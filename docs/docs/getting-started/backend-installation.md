---
title: Installing native backends
description: Complete guide to the optional native utilities used by piri across major operating systems.
---

# Installing native backends

piri deliberately does not make every compression and archive utility a mandatory Python dependency. Instead, it discovers mature native programs when they are installed.

This gives users a small base installation while allowing administrators to add only the capabilities they need.

## Backend map

| Utility | Typical role |
|---|---|
| `tar` | TAR archive creation and extraction |
| `gzip`, `pigz` | gzip compression; `pigz` adds parallel compression |
| `zstd` | Zstandard compression |
| `xz` | XZ/LZMA2 compression |
| `bzip2`, `pbzip2` | bzip2 compression; `pbzip2` adds parallel compression |
| `lz4` | LZ4 compression |
| `zip` | ZIP creation |
| `7z`, `7zz` | 7-Zip and broad archive reading |
| `cpio` | CPIO archives |
| `bsdtar` | libarchive-backed archive operations |
| `ar` | Unix archive containers, including package internals |
| `unrar` | RAR extraction/inspection where available |
| `lha` | LHA/LZH formats |
| `brotli` | Brotli streams |
| `qemu-img` | Virtual disk image inspection/conversion capabilities |
| `debugfs` | ext filesystem inspection |
| `unsquashfs` | SquashFS extraction/inspection |

:::note

The presence of a utility does not automatically mean every format operation is writable. piri reports the actual capabilities exposed by each backend.

:::

## Debian and Ubuntu

```bash
sudo apt update
sudo apt install tar gzip pigz zstd xz-utils bzip2 pbzip2 lz4 zip p7zip-full cpio libarchive-tools qemu-utils e2fsprogs squashfs-tools
```

Check individual programs:

```bash
command -v zstd
command -v 7z
command -v bsdtar
```

## Fedora, RHEL, Rocky and AlmaLinux

```bash
sudo dnf install tar gzip pigz zstd xz bzip2 pbzip2 lz4 zip p7zip p7zip-plugins cpio libarchive qemu-img e2fsprogs squashfs-tools
```

Some packages, especially proprietary or restricted RAR tooling, may require an additional repository. Do not add third-party repositories solely because piri reports an optional backend as unavailable unless you understand and trust that repository.

## Arch Linux and Manjaro

```bash
sudo pacman -S tar gzip pigz zstd xz bzip2 pbzip2 lz4 zip 7zip cpio libarchive qemu-img e2fsprogs squashfs-tools
```

## openSUSE

```bash
sudo zypper install tar gzip pigz zstd xz bzip2 lz4 zip 7zip cpio libarchive-tools qemu-tools e2fsprogs squashfs-tools
```

## Alpine Linux

```bash
sudo apk add tar gzip pigz zstd xz bzip2 lz4 zip 7zip cpio libarchive qemu-img e2fsprogs squashfs-tools
```

## macOS

```bash
brew install zstd xz bzip2 lz4 pigz p7zip libarchive
```

macOS already provides several base utilities. Homebrew fills in tools that are not normally present or provides newer versions.

## Windows

For the standalone Windows release, the project bundles selected native utilities with the application where redistribution is appropriate.

For a Python installation, install native tools independently. `winget` and Chocolatey are convenient options:

```powershell
winget search 7zip
winget install 7zip.7zip
```

or:

```powershell
choco install 7zip -y
```

Then reopen the terminal and verify:

```powershell
piri --backends
piri --formats
```

## Why does piri not install these automatically?

There are several reasons:

1. Native utilities are maintained by their own projects and distributions.
2. Package names differ across operating systems.
3. Some utilities have licensing or redistribution considerations.
4. Users may already have a preferred version installed.
5. Installing every backend would make a normal Python installation unnecessarily large.

For standalone releases, piri can bundle a controlled set of tools during the release build.

## Diagnose missing capabilities

Start with:

```bash
piri --doctor
piri --backends
piri --formats
```

Then check the expected executable directly:

```bash
command -v zstd
zstd --version
```

On Windows:

```powershell
Get-Command 7z
7z i
```

See [Backend Troubleshooting](../backends/troubleshooting) for common failures.
