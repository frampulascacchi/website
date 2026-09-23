#!/usr/bin/env python3
"""
Sync the tournament calendar in content/tornei/_index.md with vesus.org.

Fetches the tournaments created by the club account through the Vesus GraphQL
API and rewrites the "Prossimi tornei" / "Tornei passati" lists:

- upcoming tournaments are listed with their vesus.org registration link;
- played tournaments move to the past list, linking the local page when a
  tournament page (content/tornei/*.md) contains the matching vesus shortKey,
  otherwise linking vesus.org.

Existing entry labels are preserved, so manually curated names are not lost.
See docs/vesus-data.md for the API details.
"""

import json
import re
import sys
import urllib.request
from datetime import datetime, timezone
from pathlib import Path
from zoneinfo import ZoneInfo

ROOT = Path(__file__).resolve().parent.parent
INDEX = ROOT / "content/tornei/_index.md"
PAGES_DIR = ROOT / "content/tornei"

API_URL = "https://api.vesus.org/graphql"
USERNAME = "frampulascacchi"
DOC_ID = "30126cc9b73b521cef13aaeae83f0a85"
OPERATION = "UserEventsCreatorQuery"

UPCOMING_HEADING = "### Prossimi tornei in programma 🔜 {#in-programma}"
PAST_HEADING = "### Tornei passati 🔙 {#passati}"

ROME = ZoneInfo("Europe/Rome")
MONTHS = [
    "gennaio", "febbraio", "marzo", "aprile", "maggio", "giugno",
    "luglio", "agosto", "settembre", "ottobre", "novembre", "dicembre",
]

ITEM_RE = re.compile(r"^- \[(.+)\]\((.+)\)$")
VESUS_KEY_RE = re.compile(r"vesus\.org/tournament/([A-Za-z0-9]+)")
LOCAL_SLUG_RE = re.compile(r"^/tornei/([^/]+)/?$")


def fetch_tournaments():
    body = json.dumps({
        "docId": DOC_ID,
        "operationName": OPERATION,
        "variables": {"username": USERNAME, "count": 100, "cursor": None},
    }).encode()
    request = urllib.request.Request(API_URL, data=body, headers={
        "Content-Type": "application/json",
        "Origin": "https://vesus.org",
        "User-Agent": "frampula-website-sync",
    })
    with urllib.request.urlopen(request, timeout=30) as response:
        payload = json.load(response)

    edges = payload["data"]["user"]["events"]["creator"]["edges"]
    tournaments = []
    for edge in edges:
        event = edge["node"]
        for tournament in event.get("tournaments") or []:
            short_key = tournament.get("shortKey")
            if not short_key:
                continue
            start = tournament.get("start") or event.get("start")
            end = tournament.get("end") or event.get("end") or start
            tournaments.append({
                "shortKey": short_key,
                "name": event.get("name") or tournament.get("name") or "Torneo",
                "start": datetime.fromisoformat(start.replace("Z", "+00:00")),
                "end": datetime.fromisoformat(end.replace("Z", "+00:00")),
            })
    return tournaments


def local_page_slugs():
    """shortKey -> page slug, from the vesus links inside tournament pages."""
    slugs = {}
    for page in PAGES_DIR.glob("*.md"):
        if page.name == "_index.md":
            continue
        for short_key in VESUS_KEY_RE.findall(page.read_text(encoding="utf-8")):
            slugs.setdefault(short_key, page.stem)
    return slugs


def format_label(tournament):
    date = tournament["start"].astimezone(ROME)
    return f"{tournament['name']} - {date.day} {MONTHS[date.month - 1]} {date.year}"


def parse_block(block):
    entries = []
    extra = []
    for line in block.splitlines():
        stripped = line.strip()
        match = ITEM_RE.match(stripped)
        if match:
            entries.append((match.group(1), match.group(2)))
        elif stripped:
            extra.append(stripped)
    return entries, "\n".join(extra)


def entry_key(url):
    match = VESUS_KEY_RE.search(url)
    return match.group(1) if match else None


def entry_slug(url):
    match = LOCAL_SLUG_RE.match(url)
    return match.group(1) if match else None


def build_index(text, tournaments, slugs):
    start_upcoming = text.index(UPCOMING_HEADING)
    start_past = text.index(PAST_HEADING)

    intro = text[:start_upcoming].rstrip("\n")
    upcoming_entries, _ = parse_block(
        text[start_upcoming + len(UPCOMING_HEADING):start_past]
    )
    past_entries, outro = parse_block(text[start_past + len(PAST_HEADING):])

    key_by_slug = {slug: key for key, slug in slugs.items()}
    labels = {}
    for label, url in upcoming_entries:
        key = entry_key(url)
        if key:
            labels.setdefault(key, label)
    for label, url in past_entries:
        key = entry_key(url) or key_by_slug.get(entry_slug(url) or "")
        if key:
            labels.setdefault(key, label)

    now = datetime.now(timezone.utc)
    upcoming = sorted(
        (t for t in tournaments if t["end"] > now), key=lambda t: t["start"]
    )
    played = sorted(
        (t for t in tournaments if t["end"] <= now),
        key=lambda t: t["start"],
        reverse=True,
    )

    upcoming_lines = []
    for tournament in upcoming:
        key = tournament["shortKey"]
        label = labels.get(key) or format_label(tournament)
        url = f"https://vesus.org/tournament/{key}?selectedTab=tournament.registration"
        upcoming_lines.append(f"- [{label}]({url})")

    api_keys = {t["shortKey"] for t in tournaments}
    past_lines = []
    represented = set()
    for tournament in played:
        key = tournament["shortKey"]
        slug = slugs.get(key)
        label = labels.get(key) or format_label(tournament)
        url = f"/tornei/{slug}/" if slug else f"https://vesus.org/tournament/{key}"
        past_lines.append(f"- [{label}]({url})")
        represented.add(key)

    # Keep archive entries that no longer exist on vesus.
    for label, url in past_entries:
        key = entry_key(url) or key_by_slug.get(entry_slug(url) or "")
        if key in represented:
            continue
        if key and key in api_keys:
            continue
        past_lines.append(f"- [{label}]({url})")

    lines = [intro, "", UPCOMING_HEADING, "", *upcoming_lines, "", PAST_HEADING, "", *past_lines]
    if outro:
        lines += ["", outro]
    return "\n".join(lines) + "\n", len(upcoming_lines), len(past_lines)


def main():
    text = INDEX.read_text(encoding="utf-8")
    tournaments = fetch_tournaments()
    slugs = local_page_slugs()
    updated, upcoming_count, past_count = build_index(text, tournaments, slugs)
    print(f"vesus tournaments: {upcoming_count} upcoming, {past_count} played")

    if "--dry-run" in sys.argv:
        sys.stdout.write(updated)
        return

    if updated != text:
        INDEX.write_text(updated, encoding="utf-8")
        print(f"updated {INDEX.relative_to(ROOT)}")
    else:
        print("no changes")


if __name__ == "__main__":
    main()
