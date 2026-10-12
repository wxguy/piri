---
title: Format compatibility matrix
description: Understand detection, reading, writing and testing capabilities across piri formats.
---

# Format compatibility matrix

The registry is authoritative at runtime. The matrix below is a conceptual guide; always confirm the installed build with `piri --formats`.

| Family | Examples | Typical backend | Notes |
|---|---|---|---|
| TAR | `tar`, `tar.gz`, `tar.zst`, `tar.xz` | tar + compressor | General-purpose archive workflows |
| ZIP | `zip` | Python/native ZIP tooling | Broad interoperability |
| 7-Zip | `7z` | `7z`/`7zz` | Requires a compatible 7-Zip backend |
| CPIO | `cpio`, compressed CPIO | cpio + compressor | Common in Unix/Linux tooling |
| Legacy | RAR, CAB, LHA, ARJ, ZOO, SIT | Native tools where available | Often read/inspect oriented |
| Packages | DEB, RPM | ar/tar/native tooling | Package containers are not generic application archives |
| Java/Android | APK, JAR, WAR, EAR, AAR | ZIP-family handling | Treated as application containers |
| Compressed streams | Z, LZMA, Brotli, Zstd | Native compressors | A stream is not itself a directory archive |
| Optical images | ISO9660, UDF | image/archive readers | Images are kept distinct from ordinary archives |
| Virtual disks | QCOW2, VHD, VHDX, VDI, VMDK | qemu-img / image tooling | Inspection/conversion semantics differ from extraction |
| Filesystems | SquashFS, ext2/3/4 | filesystem utilities | Not interchangeable with ordinary archive extraction |

## Read vs write

A format being recognised does not mean piri will create it. This is intentional. Generic writers can corrupt formats that require application-specific metadata or filesystem semantics.

## Query the authoritative matrix

```bash
piri --formats
```

For programmatic use:

```bash
piri --backends-json
```
