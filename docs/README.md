# piri documentation website

This directory contains the Docusaurus documentation website for piri.

## Development

Requirements: Node.js 20+.

```bash
cd docs
npm install
npm start
```

Build a production site:

```bash
npm run build
npm run serve
```

The generated site is written to `docs/build/`.

## Deployment

The `.github/workflows/docs-deploy.yml` workflow builds the site and publishes `docs/build/` to the `gh-pages` branch whenever `main` changes. In the repository's **Settings → Pages**, choose **Deploy from a branch**, select `gh-pages` and `/(root)`, then save.
