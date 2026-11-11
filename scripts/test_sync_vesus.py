from datetime import datetime, timedelta, timezone

from sync_vesus import PAST_HEADING, UPCOMING_HEADING, build_index, format_label


now = datetime.now(timezone.utc)
tournaments = [
    {"shortKey": "future_key", "name": "Vesus name", "start": now + timedelta(days=10), "end": now + timedelta(days=10, hours=1)},
    {"shortKey": "past-key", "name": "Vesus name", "start": now - timedelta(days=10), "end": now - timedelta(days=9)},
]
text = f"""Intro

{UPCOMING_HEADING}

- [Curated future - 1 gennaio 2000](https://vesus.org/tournament/future_key)

{PAST_HEADING}

- [Curated past - 1 gennaio 2000](/tornei/past/)
"""
slugs = {"past-key": "past"}
updated, upcoming, past = build_index(text, tournaments, slugs)
assert (upcoming, past) == (1, 1)
assert format_label(tournaments[0], "Curated future") in updated
assert format_label(tournaments[1], "Curated past") in updated
assert "1 gennaio 2000" not in updated
assert build_index(updated, tournaments, slugs)[0] == updated
