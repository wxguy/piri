# Development

## Repository layout

```text
piri/
├── piri/
├── tests/
├── docs/
├── .github/
├── pyproject.toml
├── README.md
├── CHANGELOG.md
└── LICENSE
```

## Documentation

Documentation is intentionally kept as Markdown under `docs/`.

The directory is designed to be consumed directly by MkDocs.

## Testing

Run the complete suite:

```bash
pytest
```

## Build

Build the package using the project's configured Python packaging tools.

## Adding documentation

Create or update a Markdown file under `docs/` and add it to the MkDocs navigation.

Documentation should favour practical examples over theoretical descriptions.
