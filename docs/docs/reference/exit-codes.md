---
title: Exit codes
description: How to use piri exit status in scripts and automation.
---

# Exit codes

The most important contract for automation is simple:

- **0** — requested operation completed successfully.
- **non-zero** — the operation failed, was rejected by policy, or could not be completed.

Do not treat the presence of an output file as proof of success. Use the process exit status and, for archives, consider an explicit integrity test with `--test`.

Example:

```bash
if piri -i backup.tar.zst -o restored; then
    echo "Extraction succeeded"
else
    echo "Extraction failed" >&2
    exit 1
fi
```
