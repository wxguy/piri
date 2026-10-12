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

1. configures GitHub Pages and installs Node.js 22;
2. installs the locked Docusaurus dependencies;
3. builds the static site into `docs/build/`;
4. uploads that directory as a uniquely named Pages artifact; and
5. deploys that exact artifact on pushes to `main` or a manual workflow run.

In repository settings, configure **Pages → Build and deployment → Source → GitHub Actions**.

The Docusaurus configuration uses `url: https://wxguy.in` and `baseUrl: /piri/`, so the expected project site URL is:

```text
https://wxguy.in/piri/
```

Keep the `wxguy.in` custom domain configured on the account-level `wxguy.github.io` Pages site. Do not add a `CNAME` file to this project artifact, which could assign the custom domain to the project instead. The account Pages site provides the custom-domain root while piri remains under `/piri/`.

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
