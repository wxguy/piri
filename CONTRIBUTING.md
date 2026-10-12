# Contributing to piri

## Development setup

Install [uv](https://docs.astral.sh/uv/) first, then run:

```bash
python -m venv .venv
. .venv/bin/activate
uv sync --extra test
uv run pytest -q
```

piri is intentionally conservative about archive safety. Changes to extraction
logic should include regression tests for traversal, absolute paths, resource
limits and overwrite behavior where applicable.

## Backend changes

Backends should expose accurate capabilities. Do not report parallel extraction,
streaming or safety guarantees unless the implementation actually provides them.
Third-party backends should use the `piri.backends` entry-point group.

## Pull requests

Please include tests and update `CHANGELOG.md` for user-visible behavior. Keep
CLI behavior backwards compatible unless the change is explicitly documented as
breaking.
