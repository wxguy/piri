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

The repository's GitHub Actions workflow builds this site and deploys it to GitHub Pages.
