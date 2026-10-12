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

The repository's GitHub Actions workflow uploads `docs/build/` as a uniquely named Pages artifact and deploys that artifact to GitHub Pages. The workflow requires **Settings → Pages → Build and deployment → Source → GitHub Actions**.
