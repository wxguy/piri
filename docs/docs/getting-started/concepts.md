---
title: Core concepts
description: Understand how piri thinks about archives, formats, backends and policies.
---

# Core concepts

piri separates several ideas that are often mixed together by traditional archive commands.

## Format

A **format** describes the structure of data, such as TAR, ZIP, 7z, ISO9660 or QCOW2.

## Backend

A **backend** is an implementation used by piri to perform an operation. It may be Python code, a native executable or a plugin.

## Capability

A format can be detected without necessarily being writable. A backend may support read, write, list, test or safe-preflight operations independently.

## Operation

The main operations are:

- create an archive from a directory
- extract an archive into a directory
- list archive contents
- test archive integrity
- detect an unknown file
- benchmark candidate formats/backends

## Policy

Policies control safety and resource usage: overwrite behaviour, maximum member count, maximum extracted bytes and path constraints.

This separation is why `piri --formats` is more useful than a simple list of file extensions.
