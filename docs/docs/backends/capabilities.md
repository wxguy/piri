---
title: Backend capabilities
description: Learn how piri reports and selects native and Python backend capabilities.
---

# Backend capabilities

Every backend advertises capabilities such as read, write, list, test, streaming, safe preflight and parallel execution.

## Inspect backends

```bash
piri --backends
```

For automation:

```bash
piri --backends-json
```

## Backend selection

When multiple implementations can perform an operation, piri can use explicit selection or benchmark-driven selection. The selection layer considers format compatibility, backend availability and operation requirements.

## Native backends

Native tools are useful when they provide mature format support or better performance. They are discovered at runtime rather than being mandatory Python dependencies.

## Plugins

Third-party Python backends can register through the `piri.backends` entry-point group. Plugin authors should expose only capabilities they can perform safely and should integrate with piri's validation and policy model.
