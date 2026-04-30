## Frampula Scacchi

Source code for the website of the chess club [Frampula Scacchi](https://maps.app.goo.gl/kRrFoXhyx2ZavTcA7).

## Requirements

- [Hugo extended](https://gohugo.io/installation/) installed locally

The GitHub Pages workflow currently builds the site with Hugo extended `0.148.2`.

## Nix

If you use [Nix](https://nixos.org/), this repo includes a `flake.nix` with a lightweight development shell.

Enter the shell:

```bash
nix develop
```

From there you can run Hugo directly, or use the convenience apps:

```bash
nix run .#serve
nix run .#serve-future
nix run .#build
```

The Nix shell sets `HUGO_CACHEDIR` to a repo-local absolute path at `./.hugo-cache`.

## Development

Start a local development server:

```bash
hugo server --buildDrafts --cacheDir /tmp/frampula-hugo-cache
```

The site will be available at `http://localhost:1313/`.

If you need to preview future-dated content as well, use:

```bash
hugo server --buildDrafts --buildFuture --cacheDir /tmp/frampula-hugo-cache
```

## Build

Build the production site locally:

```bash
hugo --gc --minify --cacheDir /tmp/frampula-hugo-cache
```

The generated site is written to `public/`.

If you want to avoid touching the checked-in `public/` directory while testing a build, use a temporary destination:

```bash
hugo --gc --minify --cacheDir /tmp/frampula-hugo-cache --destination /tmp/frampula-hugo-build
```

## Deployment

Deployment is handled by GitHub Actions through [`.github/workflows/gh-pages-deploy.yml`](.github/workflows/gh-pages-deploy.yml). A push to `main` builds and publishes the site to GitHub Pages.
