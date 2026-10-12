---
title: Frequently asked questions
description: Common questions about installing and using piri.
---

# Frequently asked questions

## Does the standalone installer include every native tool?

No. Standalone releases include the native utilities staged for their build platform, but some tools remain optional. `piri --backends` shows which tools are available in the installed build.

## Why does piri recognise a format but not create it?

Recognition, reading and writing are separate capabilities. Some formats contain application-specific or filesystem-specific semantics and are intentionally not advertised as generic writers.

## Do I need Python for the standalone release?

No. Standalone builds package the Python runtime. Native backend availability still depends on what was included in that release build.

## Why is the Windows Setup installer faster than the single-file EXE?

A one-file executable normally has to unpack its embedded application payload before starting. The installed one-folder build keeps those files already extracted on disk, so startup avoids that repeated extraction step.

## Is `--test` the same as a cryptographic checksum?

No. `--test` validates the archive using the integrity mechanisms available to the format/backend. It does not automatically prove authenticity or provide a cryptographic digest of the original directory.

## Is piri a replacement for every feature of tar or 7-Zip?

No. piri provides a consistent higher-level interface and backend selection layer. Specialist tools may still expose format-specific features that piri does not.

## How do I know what my installation supports?

```bash
piri --doctor
piri --backends
piri --formats
```
