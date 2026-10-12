# piri

**A modern, secure and benchmark-driven archive and extraction utility for Linux, macOS and Windows.**

piri provides one consistent command-line interface for creating, inspecting, testing and extracting archives while selecting appropriate native backends available on the system.

## Quick start

```bash
curl -fsSL https://wxguy.github.io/piri/install.sh | bash
piri -i my-directory -o backup.tar.zst
piri -t backup.tar.zst
piri -i backup.tar.zst -o restored
```

## Why piri?

- Simple CLI for everyday archive operations.
- Broad archive, compression, package and image-format coverage.
- Native high-performance backends where available.
- Safe extraction with path and resource policies.
- Integrity testing with `-t` / `--test`.
- Benchmark-driven format and backend selection.
- Structured statistics for automation.
- Extensible backend architecture.
- Standalone releases for Linux, macOS and Windows.

## Documentation

The complete documentation website is maintained separately under `docs/` and built with Docusaurus.

**Documentation:** https://wxguy.github.io/piri/

Useful starting points in the repository:

- [Installation](docs/docs/getting-started/installation.md)
- [Backend Installation](docs/docs/getting-started/backend-installation.md)
- [Quick Start](docs/docs/getting-started/quickstart.md)
- [Supported Formats](docs/docs/formats/supported-formats.md)
- [CLI Reference](docs/docs/reference/cli.md)
- [Security](docs/docs/security/security-model.md)
- [Development](docs/docs/development/development-guide.md)

## Supported formats

piri distinguishes archives, compressed streams, application/package containers, and disk/filesystem images. The authoritative capability matrix is available from:

```bash
piri --formats
piri --backends
piri --doctor
```

Availability and read/write/test capabilities depend on the installed backend tools and the platform.

## Benchmarking

Benchmark your actual dataset instead of guessing:

```bash
piri --benchmark-select -i DATASET
piri --best smallest -i DATASET
piri --best fastest -i DATASET
piri --best extract-fast -i DATASET
piri --best balanced -i DATASET
```

Create a deterministic benchmark corpus when reproducibility is important:

```bash
piri --make-benchmark-corpus ./piri-bench --benchmark-size-mb 1024
```

## Development

Install [uv](https://docs.astral.sh/uv/) first, then run:

```bash
python -m venv .venv
. .venv/bin/activate
uv sync --extra test
uv run pytest -q
```

Build Python distribution artifacts with:

```bash
python -m build
python -m twine check dist/*
```

The documentation site has its own Node.js environment under `docs/`:

```bash
cd docs
npm install
npm start
```

## Standalone releases

Users who do not want Python can use platform-specific standalone releases published with each GitHub release:

- **Windows:** Setup installer, one-file `.exe`, and portable `.zip`.
- **Linux:** `.run`, `.tar.gz`, and filesystem `.img` distributions.
- **macOS:** `.dmg` and portable `.tar.gz` distributions.

Standalone builds bundle the Python runtime and selected native utilities; exact backend availability is release-specific.

## Project

- GitHub: https://github.com/wxguy/piri
- Issues: https://github.com/wxguy/piri/issues
- Releases: https://github.com/wxguy/piri/releases

## License

MIT. See [LICENSE](LICENSE).
