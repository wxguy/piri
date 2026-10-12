# Backend Architecture

piri uses a backend registry to separate the archive engine from native tools and optional implementations.

## Why backends?

Different formats have different optimal tools.

Examples:

- TAR + gzip → `pigz` when available
- TAR + Zstandard → `zstd`
- TAR + bzip2 → `pbzip2` when available
- 7z → `7z` or `7zz`
- disk images → `qemu-img`
- filesystem images → specialised readers such as `debugfs` or `unsquashfs`

piri should use the best available implementation rather than reimplement every compression algorithm in Python.

## Capabilities

A backend can report:

- read
- write
- test
- streaming
- parallel compression
- parallel extraction
- safe preflight
- executable
- backend version

## Plugin architecture

Third-party Python backends can register through the `piri.backends` entry-point group.

A backend should expose the operations required by the registry and provide accurate capability information.

## Capability principle

Never claim a capability that the underlying backend does not actually provide.

In particular, parallel decompression does not automatically mean parallel archive extraction.
