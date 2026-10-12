---
id: intro
title: piri documentation
sidebar_label: Overview
description: A modern, secure and benchmark-driven archive utility for Linux, macOS and Windows.
slug: /
---

# piri

> **Compress. Extract. Inspect. Benchmark. Securely.**

piri is a cross-platform command-line archive utility designed to make common archive operations simple while still exposing the capabilities, performance and safety controls expected by advanced users.

<div className="heroCommand">

```bash
curl -fsSL https://wxguy.github.io/piri/install.sh | bash
piri -i my-directory -o backup.tar.zst
piri -t backup.tar.zst
piri -i backup.tar.zst -o restored
```

</div>

## Why piri?

| | What it gives you |
|---|---|
| **One CLI** | A consistent interface for create, extract, inspect, detect and test operations. |
| **Native backends** | Uses mature operating-system tools when they provide better format coverage or performance. |
| **Security controls** | Safe extraction, path validation, resource limits and explicit overwrite policies. |
| **Benchmark-driven selection** | Measure your actual data instead of guessing which compressor is best. |
| **Broad format coverage** | Archives, compressed streams, packages, application containers and disk/filesystem images. |
| **Automation-ready** | Predictable exit codes, JSON statistics and machine-readable backend information. |

## Choose your path

### New to piri?

Start with **[Installation](/docs/getting-started/installation)** and then follow the **[Quick Start](/docs/getting-started/quickstart)**.

### Experienced command-line user?

Jump directly to the **[CLI Reference](/docs/reference/cli)**, **[Supported Formats](/docs/formats/supported-formats)** or **[Backend Architecture](/docs/backends/architecture)**.

### System administrator?

Read **[Backend Installation](/docs/getting-started/backend-installation)** and **[Security](/docs/security/security-model)**.

### Developer?

Start with **[Architecture](/docs/development/architecture)** and **[Development Setup](/docs/development/development-guide)**.

## At a glance

- **Python:** 3.10+
- **Platforms:** Linux, macOS and Windows
- **License:** MIT
- **Project:** [github.com/wxguy/piri](https://github.com/wxguy/piri)
- **Downloads:** [GitHub Releases](https://github.com/wxguy/piri/releases)

:::tip Start small

You do **not** need to install every native archive utility. Install the backends required for the formats you actually use. `piri --backends` and `piri --formats` show what is available on the current machine.

:::

## The name `piri`

*Piri* (பிரி) is a Tamil word associated with separating, splitting apart, or extracting. That meaning reflects one of the fundamental operations of this utility: extracting the contents of an archive.

Tamil is one of the world's ancient classical languages, with a rich literary and grammatical tradition extending across many centuries. The name `piri` is a respectful acknowledgement of that linguistic heritage while giving the project a short, distinctive and meaningful identity.
