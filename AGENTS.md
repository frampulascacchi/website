# AGENTS.md

Guidance agents working in this repository.

## Project shape

- This is a plain Hugo website for the Frampula Scacchi chess club.
- Main content lives in `content/`.
- Templates live in `layouts/`.
- Static assets live in `static/`.
- `public/` is generated output.
- There is one helper script in `scripts/convert_vesus_standing.py` that converts Vesus standings text files into Markdown tables.
- A `flake.nix` provides a Nix development shell and convenience apps for serving/building the site.

## Useful commands

Run the local server:

```bash
hugo server --buildDrafts --cacheDir /tmp/frampula-hugo-cache
```

Preview future-dated content too:

```bash
hugo server --buildDrafts --buildFuture --cacheDir /tmp/frampula-hugo-cache
```

Build the site:

```bash
hugo --gc --minify --cacheDir /tmp/frampula-hugo-cache
```

Build without modifying `public/`:

```bash
hugo --gc --minify --cacheDir /tmp/frampula-hugo-cache --destination /tmp/frampula-hugo-build
```

If [Nix](https://nixos.org/) is available, enter the pinned development shell:

```bash
nix develop
```

Or use the flake apps directly:

```bash
nix run .#serve
nix run .#serve-future
nix run .#build
```

The Nix workflow uses a repo-local cache directory at `./.hugo-cache`.

## Repository-specific notes

- Prefer keeping documentation and content in Italian unless the user asks otherwise.
- Do not assume `public/` should be edited by hand; it is generated.
- The GitHub Pages workflow uses Hugo extended `0.148.2`.
- The Nix flake currently tracks `nixos-unstable`, so local tool versions may differ slightly from GitHub Pages unless the flake is later pinned to the workflow's exact Hugo release.
- Local Hugo builds may fail if `--cacheDir` is omitted, because the default cache location can be outside the writable sandbox.
- Current builds emit Hugo warnings for missing taxonomy and term templates. Those warnings are existing behavior unless the task is specifically to address them.

## Editing guidance

- Be careful with uncommitted content changes. This repo is actively edited and content files may already be dirty.
- Preserve the existing visual structure in `layouts/` unless the task explicitly asks for design changes.
