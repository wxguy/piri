# Supported Formats

piri separates formats into archives, compressed streams, packages/application containers and disk/filesystem images.

Availability depends on native programs installed on the host.

## Archives

- TAR
- TAR.GZ
- TAR.ZST
- TAR.XZ
- TAR.BZ2
- TAR.LZ4
- TAR.LZMA
- TAR.Z
- TAR.BR
- ZIP
- 7z
- CPIO
- CPIO.GZ
- CPIO.BZ2
- CPIO.XZ
- CPIO.ZST
- AR

## Legacy/optional archives

- RAR
- CAB
- LHA/LZH
- XAR
- WARC
- ARJ
- ZOO
- SIT

## Compression streams

- compress / `.Z`
- LZMA
- Brotli
- Zstandard

## Packages and application containers

- DEB
- RPM
- APK
- JAR
- WAR
- EAR
- AAR

APK/JAR/WAR/EAR/AAR are ZIP-family containers but are represented separately so piri can expose their application/container identity.

## Disk and filesystem images

- ISO9660
- UDF
- IMG
- RAW
- QCOW2
- VHD
- VHDX
- VDI
- VMDK
- DMG
- SquashFS
- EXT2
- EXT3
- EXT4

Disk images are deliberately not treated as ordinary archives.

## Check local availability

```bash
piri --formats
```

For backend details:

```bash
piri --backends
```

The output tells you whether each format is readable, writable, testable and whether the required backend is available.
