---
title: Backend development
description: Guide for implementing and registering piri backends.
---

# Backend development

Backends should be treated as capability providers rather than arbitrary command wrappers.

A backend should clearly state what it can do:

- detect
- list
- read/extract
- create/write
- test
- stream
- preflight safely
- execute in parallel

## Development principles

1. Never silently claim a capability that is not implemented.
2. Preserve piri policy checks before writing to disk.
3. Validate paths and special files during extraction.
4. Return useful, structured errors.
5. Add round-trip tests where a writer exists.
6. Document external executable and licensing assumptions.

Third-party Python plugins can register through the `piri.backends` entry-point group.
