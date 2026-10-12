# Contributing

Contributions are welcome.

## Development setup

```bash
git clone https://github.com/wxguy/piri.git
cd piri
uv sync --extra test
```

Install [uv](https://docs.astral.sh/uv/) before running these commands.

Run tests:

```bash
uv run pytest
```

## Adding a format

A new format should include:

1. registry definition;
2. detection rule;
3. backend implementation;
4. capability declaration;
5. security/preflight handling;
6. integrity testing;
7. round-trip tests if writable;
8. documentation;
9. CLI/backend capability reporting.

Do not mark a format writable until it has a real writer and round-trip validation.

## Code quality

Keep the implementation:

- Pythonic
- explicit
- testable
- platform-aware
- conservative about security
- honest about backend capabilities

## Pull requests

Explain:

- what changed;
- why it is needed;
- supported platforms;
- native dependencies;
- test coverage;
- performance implications.
