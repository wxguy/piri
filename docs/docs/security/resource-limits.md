---
title: Resource limits
description: Control archive expansion, member counts and path-related resource usage.
---

# Resource limits

Archive extraction can consume far more resources than the compressed file size suggests. piri therefore exposes policies for limiting members, bytes and path characteristics.

Use the CLI reference to see the exact options supported by your installed release.

## Recommended approach for untrusted archives

1. Inspect the archive before extraction.
2. Test the archive where possible.
3. Use conservative resource limits.
4. Extract into a disposable destination.
5. Avoid running extraction as root unless necessary.
6. Use `--atomic` when you want a failed extraction to avoid publishing a partial destination.

:::warning

No archive tool can make an untrusted file inherently safe. Resource limits reduce risk; they do not replace malware scanning, sandboxing or operating-system security controls.

:::
