---
title: Testing
description: Test strategy for piri contributors and release builders.
---

# Testing

Run the full Python test suite before submitting changes:

```bash
python -m pytest -q
```

Compile-check the package:

```bash
python -m compileall piri
```

## What should be tested?

- format detection
- successful create/extract round trips
- integrity testing
- unsafe path rejection
- overwrite policy
- resource limits
- backend discovery
- plugin registration
- benchmark selection
- standalone runtime discovery

## Release confidence

A release should be tested on every supported operating system and Python version. Standalone artifacts should additionally be smoke-tested by executing the built binary and checking `--version`, `--formats` and a small round-trip operation.
