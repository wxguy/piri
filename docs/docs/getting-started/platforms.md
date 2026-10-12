---
title: Platform installation guides
description: Platform-specific installation guidance for piri and its optional native backends.
---

# Platform installation guides

piri is distributed as standalone platform builds. Native utilities are optional and are detected at runtime.

## Windows

For most users, use the **Setup installer** from the GitHub release. It installs the normal one-folder application and avoids the repeated startup extraction associated with a single-file executable.

Portable alternatives are also available for users who do not want an installation.

See [Standalone Installers](./standalone).

## Ubuntu / Debian

Install piri with the hosted installer:

```bash
curl -fsSL https://wxguy.github.io/piri/install.sh | bash
```

Useful native backends:

```bash
sudo apt update
sudo apt install tar gzip pigz zstd xz-utils bzip2 pbzip2 lz4 zip p7zip-full cpio libarchive-tools qemu-utils e2fsprogs squashfs-tools
```

## Fedora / RHEL / Rocky / AlmaLinux

```bash
sudo dnf install tar gzip pigz zstd xz bzip2 pbzip2 lz4 zip p7zip p7zip-plugins cpio libarchive qemu-img e2fsprogs squashfs-tools
```

Package names vary by RHEL-compatible release and enabled repositories. Check availability with your distribution's package manager before scripting installation.

## Arch Linux / Manjaro

```bash
sudo pacman -S tar gzip pigz zstd xz bzip2 pbzip2 lz4 zip 7zip cpio libarchive qemu-img e2fsprogs squashfs-tools
```

## openSUSE

```bash
sudo zypper install tar gzip pigz zstd xz bzip2 lz4 zip 7zip cpio libarchive-tools qemu-tools e2fsprogs squashfs-tools
```

Exact package names can differ between Leap and Tumbleweed.

## Alpine Linux

```bash
sudo apk add tar gzip pigz zstd xz bzip2 lz4 zip 7zip cpio libarchive qemu-img e2fsprogs squashfs-tools
```

## macOS

Homebrew is the simplest way to install optional native backends:

```bash
brew install zstd xz bzip2 lz4 pigz p7zip libarchive
```

Install piri with the hosted installer:

```sh
curl -fsSL https://wxguy.github.io/piri/install.sh | bash
```

## Verify the installation

Run all three commands after installing piri:

```bash
piri --version
piri --backends
piri --formats
```

`--backends` answers **which engines are available**. `--formats` answers **which format capabilities piri can currently expose**.
