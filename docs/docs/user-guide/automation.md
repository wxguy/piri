---
title: Automation and CI/CD
description: Use piri reliably from shell scripts, scheduled jobs and continuous integration.
---

# Automation and CI/CD

piri is designed to be usable from scripts without requiring interactive prompts.

## Recommended pattern

```bash
set -euo pipefail

piri --overwrite error -i ./build-output -o ./artifacts/build.tar.zst
piri --test ./artifacts/build.tar.zst
```

The test step gives the pipeline an explicit integrity gate before the artifact is published.

## Discover capabilities in CI

```bash
piri --backends-json
```

Use the structured output when the pipeline needs to select a backend based on capability rather than parsing human-readable output.

## Record operation statistics

```bash
piri --stats -i ./dataset -o ./dataset.tar.zst
```

Keep the statistics alongside benchmark or release artifacts when reproducibility matters.

## Container images

For minimal containers, install only the native tools needed by the formats used by the application. A Python-only piri installation is deliberately small; native backend availability is environment-dependent.

## Failure handling

Treat a non-zero piri exit code as a failed operation. In production automation, do not infer success from the existence of an output file alone.
