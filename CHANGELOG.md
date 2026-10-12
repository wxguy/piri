# Changelog

## Unreleased

- Make GitHub standalone releases the user installation path, with a hosted Linux/macOS installer script and Windows release downloads.
- Publish standalone releases through GitHub Releases.
- Fix CPIO extraction with the BSD cpio implementation used by macOS.

## 1.0.0

- Project renamed to `piri`; the name reflects the Tamil word *piri* (பிரி), associated with separating or extracting.
- Expanded registry to 50 format IDs.
- Added APK, JAR, WAR, EAR and AAR container recognition/testing.
- Added DEB/RPM package classification.
- Added ARJ, ZOO and SIT registry entries.
- Added DMG, SquashFS and EXT2/3/4 filesystem-image handling where native tools exist.
- Added ZIP-family extension-aware detection.
- Added filesystem image signature detection.
- Preserved strict distinction between archives, compressed streams, packages and disk images.

## 0.0.6

- Expanded format registry with compressed streams, additional TAR/CPIO combinations, package/archive formats, and disk-image formats.
- Added optional ISO9660/UDF image reading and integrity testing.
- Added qemu-img based integrity testing for IMG/raw/QCOW2/VHD/VHDX/VDI/VMDK when qemu-img is installed.
- Added LZMA, Brotli and Zstandard stream integrity testing.
- Kept image writers disabled until a real, tested image writer is available.

## 0.0.5 - Benchmark and portability validation

- Added deterministic mixed benchmark corpus generation.
- Added benchmark CPU-time and peak-RSS telemetry.
- Improved format capability display with separate compression/extraction parallelism.
- Added benchmark corpus CLI options.
- Prepared the benchmark workflow for cross-platform CI validation.

## 0.0.4 - Release engineering

- Added production-oriented package metadata and project URLs.
- Added optional test/build dependency groups.
- Added GitHub Actions CI for supported Python versions on Linux, macOS and Windows.
- Added a release workflow for tagged distribution publishing.
- Added contributor, security and release documentation.
- Refreshed the project README for the then-current release series.

## 0.0.3 - Backend architecture

- Added formal backend registry and plugin entry-point architecture.
- Added backend capability reporting and JSON output.
- Improved alternative native-reader discovery.

## 0.0.2 - Performance and reliability

- Added CPU/RSS telemetry and structured statistics.
- Added processor control during supported extraction.
- Added atomic extraction.

## 0.0.1 - Integrity testing

- Added `-t` / `--test` archive integrity testing.
