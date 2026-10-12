---
title: Environment variables
description: Environment variables and runtime controls relevant to piri deployments.
---

# Environment variables

piri can discover bundled native utilities through its runtime environment. Standalone builds may use an application-adjacent native directory.

## `PIRI_BUNDLED_BIN`

When set, piri can use the specified directory as the preferred location for bundled native executables.

Example:

```bash
export PIRI_BUNDLED_BIN=/opt/piri/native
piri --backends
```

For standalone installations, the operating-system `PATH` remains the primary mechanism for discovering native utilities.

:::tip

For reproducible automation, document the native backend versions alongside the piri version. Backend upgrades can change performance and format behaviour even when piri itself has not changed.

:::
