---
title: Architecture
description: High-level architecture of piri and its format/backend selection model.
---

# Architecture

piri is organised around a separation between the command-line interface, operation engine, format registry, policy/security layer and backend implementations.

```text
CLI
 │
 ▼
Engine ──────────────── Policy / Security
 │
 ├── Detection
 ├── Format Registry
 ├── Selection
 │
 └── Backend Registry
       ├── Python backends
       ├── Native backends
       └── Plugins
```

## Design goals

- keep the CLI predictable
- make format knowledge authoritative and centralised
- make backend capabilities explicit
- validate unsafe extraction before writing
- allow native performance without making native tools mandatory
- make benchmark results useful for real selection

## Why a registry?

A registry prevents format knowledge from being scattered across the CLI and individual backend implementations. It also allows `--formats`, detection and selection to share the same source of truth.

## Why policies are separate

Security and resource constraints should apply regardless of which backend eventually performs an operation. Keeping them above the backend layer reduces the risk that a new backend accidentally bypasses core extraction policy.
