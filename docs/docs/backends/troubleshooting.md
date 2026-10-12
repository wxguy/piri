---
title: Backend troubleshooting
description: Diagnose missing compressors, archive utilities and native format support.
---

# Backend troubleshooting

## Format appears but cannot be created

A format can be recognised without having a writer. Check:

```bash
piri --formats
```

Look at the operation capabilities rather than only the format name.

## Native executable is installed but not detected

Check the executable from the same shell/environment used to run piri:

```bash
command -v zstd
zstd --version
piri --doctor
```

Windows:

```powershell
Get-Command 7z
7z i
piri --doctor
```

## PATH problems

A tool installed by Homebrew, a user package manager or a custom administrator path may not be visible to a service account or non-interactive shell.

Confirm:

```bash
echo "$PATH"
```

and run `piri --backends` under the same account that will perform the operation.

## Standalone build

A standalone build may contain bundled native utilities. The exact capability set is release-specific. Use:

```bash
piri --backends
piri --formats
```

Do not assume that a standalone package contains every utility found on the developer's machine.
