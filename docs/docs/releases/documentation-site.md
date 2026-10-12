---
title: Documentation site development and deployment
description: Maintain, preview and deploy the piri Docusaurus documentation site.
---

# Documentation site development and deployment

The documentation website lives under `docs/` and is independent of the Python package build.

## Requirements

Docusaurus 3.10 requires Node.js 20 or newer. Check the installed version with:

```bash
node --version
npm --version
```

## Run locally

```bash
cd docs
npm install
npm start
```

The development server normally opens at `http://localhost:3000/piri/`.

## Production build

```bash
cd docs
npm run build
npm run serve
```

The generated static site is placed in `docs/build/`.

## GitHub Pages

The repository contains `.github/workflows/docs.yml`. It:

1. installs Node.js 20;
2. installs the Docusaurus dependencies;
3. builds the static site;
4. uploads the build as a GitHub Pages artifact; and
5. deploys the artifact on pushes to `main` or a manual workflow run.

In repository settings, configure **Pages → Build and deployment → Source → GitHub Actions**.

The current project configuration targets:

```text
https://wxguy.github.io/piri/
```

If the repository is moved, update `url`, `baseUrl`, `organizationName` and `projectName` in `docusaurus.config.js`.

## Content guidelines

Write documentation for the reader's task, not for the source tree. Prefer:

- copy-ready commands;
- one concept at a time;
- platform tabs where commands differ;
- warnings for destructive or security-sensitive operations;
- links to the next logical task;
- explicit statements when a capability depends on a native backend.

Avoid duplicating the same technical table in several pages. Put authoritative information in one location and link to it.
