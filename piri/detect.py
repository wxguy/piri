from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
import gzip
import bz2
import lzma
import zipfile
import tarfile
import subprocess
import shutil

from .formats import from_extension


from .runtime import which as _piri_which
@dataclass(frozen=True)
class DetectedFormat:
    name: str
    confidence: str
    reason: str


MAGICS = (
    (b"\x1f\x8b", "gzip"),
    (b"BZh", "bzip2"),
    (b"\xfd7zXZ\x00", "xz"),
    (b"\x28\xb5\x2f\xfd", "zstd"),
    (b"PK\x03\x04", "zip"),
    (b"PK\x05\x06", "zip"),
    (b"PK\x07\x08", "zip"),
    (b"7z\xbc\xaf\x27\x1c", "7z"),
    (b"!<arch>\n", "ar"),
    (b"070701", "cpio"),
    (b"070702", "cpio"),
    (b"QFI\xfb", "qcow2"),
    (b"KDMV", "vmdk"),
    (b"hsqs", "squashfs"),
    (b"\x7fELF", "raw"),
)


class _Reader:
    def __init__(self, f):
        self.f = f
    def read(self, n=-1):
        return self.f.read(n)
    def readable(self):
        return True


def _compressed_tar(path: Path, kind: str) -> bool:
    try:
        if kind == "gzip":
            with gzip.open(path, "rb") as f:
                with tarfile.open(fileobj=_Reader(f), mode="r|") as tf:
                    return tf.next() is not None
        if kind == "bzip2":
            with bz2.open(path, "rb") as f:
                with tarfile.open(fileobj=_Reader(f), mode="r|") as tf:
                    return tf.next() is not None
        if kind == "xz":
            with lzma.open(path, "rb") as f:
                with tarfile.open(fileobj=_Reader(f), mode="r|") as tf:
                    return tf.next() is not None
        if kind == "zstd" and _piri_which("zstd"):
            proc = subprocess.Popen(["zstd", "-dc", str(path)], stdout=subprocess.PIPE)
            try:
                with tarfile.open(fileobj=proc.stdout, mode="r|") as tf:
                    result = tf.next() is not None
                return result
            finally:
                if proc.stdout:
                    proc.stdout.close()
                proc.wait()
    except Exception:
        return False
    return False


def detect_format(path: str | Path) -> DetectedFormat:
    p = Path(path)
    with p.open("rb") as fh:
        data = fh.read(16)
        fh.seek(32769)
        iso_magic = fh.read(5)
        fh.seek(0)
        vdi_magic = fh.read(72)
        fh.seek(max(0, p.stat().st_size - 512))
        vhd_footer = fh.read(8)

    if iso_magic == b"CD001":
        return DetectedFormat("iso9660", "high", "ISO9660 volume descriptor")
    if vhd_footer == b"conectix":
        return DetectedFormat("vhd", "high", "VHD footer signature")
    if vdi_magic[64:68] == b"\x7f\x10\xda\xbe":
        return DetectedFormat("vdi", "high", "VDI signature")
    # ext2/3/4 superblock magic at offset 1024 + 56.
    try:
        with p.open("rb") as fh:
            fh.seek(1080)
            if fh.read(2) == b"\x53\xef":
                # Feature flags distinguish the ext family. ext2 has no
                # incompat feature flags; ext3/4 commonly do.
                fh.seek(1144)
                incompat = int.from_bytes(fh.read(4), "little")
                if incompat & 0x40:
                    return DetectedFormat("ext4", "high", "EXT superblock with ext4 incompat feature")
                if incompat:
                    return DetectedFormat("ext3", "high", "EXT superblock with incompat feature")
                return DetectedFormat("ext2", "high", "EXT filesystem superblock")
    except OSError:
        pass

    for magic, kind in MAGICS:
        if data.startswith(magic):
            if kind in {"gzip", "bzip2", "xz", "zstd"} and _compressed_tar(p, kind):
                suffix = {"gzip": "gz", "bzip2": "bz2", "xz": "xz", "zstd": "zst"}[kind]
                return DetectedFormat(f"tar.{suffix}", "high", f"{kind} stream contains TAR")
            if kind == "zip":
                ext = from_extension(str(p))
                if ext and ext.name in {"apk", "jar", "war", "ear", "aar"}:
                    return DetectedFormat(ext.name, "high", f"ZIP signature with {ext.name} extension")
            if kind == "ar":
                ext = from_extension(str(p))
                if ext and ext.name == "deb":
                    return DetectedFormat("deb", "high", "ar signature with Debian package extension")
            mapped = {
                "gzip": "gzip", "bzip2": "bzip2", "xz": "xz",
                "zstd": "zstd", "zip": "zip", "7z": "7z",
                "ar": "ar", "cpio": "cpio", "squashfs": "squashfs",
            }[kind]
            return DetectedFormat(mapped, "high", f"magic signature: {kind}")

    try:
        if zipfile.is_zipfile(p):
            return DetectedFormat("zip", "high", "ZIP structural validation")
    except Exception:
        pass
    try:
        if tarfile.is_tarfile(p):
            return DetectedFormat("tar", "high", "TAR structural validation")
    except Exception:
        pass

    ext = from_extension(str(p))
    if ext:
        return DetectedFormat(ext.name, "medium", f"filename extension: {ext.name}")

    return DetectedFormat("unknown", "low", "no known signature or extension")
