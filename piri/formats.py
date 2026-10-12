from __future__ import annotations

from dataclasses import dataclass
import shutil


from .runtime import which as _piri_which
@dataclass(frozen=True)
class FormatSpec:
    name: str
    extensions: tuple[str, ...]
    read: bool
    write: bool
    backend: str
    requires: tuple[str, ...] = ()
    alternatives: tuple[str, ...] = ()
    parallel_compression: bool = False
    parallel_extraction: bool = False
    kind: str = "archive"
    priority: int = 50
    operations: tuple[str, ...] = ("list", "extract", "test")

    def available(self) -> bool:
        required_ok = all(_piri_which(x) for x in self.requires)
        alternatives_ok = not self.alternatives or any(_piri_which(x) for x in self.alternatives)
        return required_ok and alternatives_ok


_FORMATS = (
    FormatSpec("tar", (".tar",), True, True, "tar", ("tar",), kind="archive", priority=90),
    FormatSpec("tar.gz", (".tar.gz", ".tgz"), True, True, "tar + pigz/gzip", ("tar",), parallel_compression=True, kind="compressed-archive", priority=100),
    FormatSpec("tar.zst", (".tar.zst", ".tzst"), True, True, "tar + zstd", ("tar", "zstd"), parallel_compression=True, kind="compressed-archive", priority=110),
    FormatSpec("tar.xz", (".tar.xz", ".txz"), True, True, "tar + xz", ("tar", "xz"), parallel_compression=True, kind="compressed-archive", priority=80),
    FormatSpec("tar.bz2", (".tar.bz2", ".tbz2", ".tbz"), True, True, "tar + pbzip2/bzip2", ("tar",), parallel_compression=True, kind="compressed-archive", priority=70),
    FormatSpec("tar.lz4", (".tar.lz4", ".tlz4"), True, True, "tar + lz4", ("tar", "lz4"), parallel_compression=True, kind="compressed-archive", priority=60),
    FormatSpec("zip", (".zip",), True, True, "Python zipfile", kind="archive", priority=95),
    FormatSpec("7z", (".7z",), True, True, "7z/7zz", ("7z",), parallel_compression=True, parallel_extraction=True, kind="archive", priority=85),
    FormatSpec("cpio", (".cpio",), True, True, "cpio", ("cpio",), kind="archive", priority=45),
    # ar is a member/object archive rather than a general directory archive.
    # Keep it readable for future inspection, but do not expose it as a generic
    # directory->archive writer.
    FormatSpec("ar", (".ar", ".a"), True, False, "ar", ("ar",), kind="archive", priority=40),
    FormatSpec("rar", (".rar",), True, False, "unrar/bsdtar", alternatives=("unrar", "bsdtar"), kind="archive", priority=30),
    FormatSpec("cab", (".cab",), True, False, "bsdtar", ("bsdtar",), kind="archive", priority=30),
    FormatSpec("lha", (".lha", ".lzh"), True, False, "lha/bsdtar", alternatives=("lha", "bsdtar"), kind="archive", priority=30),
    FormatSpec("xar", (".xar",), True, False, "bsdtar", ("bsdtar",), kind="archive", priority=25),
    FormatSpec("warc", (".warc", ".warc.gz"), True, False, "bsdtar", ("bsdtar",), kind="archive", priority=20),
    FormatSpec("compress", (".Z", ".tar.Z"), True, False, "uncompress", ("uncompress",), kind="compressed-stream", priority=20, operations=("test",)),
    FormatSpec("lzma", (".lzma",), True, False, "xz --format=lzma", ("xz",), kind="compressed-stream", priority=20, operations=("test",)),
    FormatSpec("brotli", (".br",), True, False, "brotli", ("brotli",), kind="compressed-stream", priority=20, operations=("test",)),
    FormatSpec("zstd", (".zst",), True, False, "zstd", ("zstd",), kind="compressed-stream", priority=20, operations=("test",)),
    # ZIP-family application/package containers. They are intentionally read/test
    # only: a generic ZIP writer does not make a valid APK/JAR/WAR/EAR/AAR.
    FormatSpec("apk", (".apk",), True, False, "zip", kind="application-container", priority=55),
    FormatSpec("jar", (".jar",), True, False, "zip", kind="application-container", priority=55),
    FormatSpec("war", (".war",), True, False, "zip", kind="application-container", priority=55),
    FormatSpec("ear", (".ear",), True, False, "zip", kind="application-container", priority=55),
    FormatSpec("aar", (".aar",), True, False, "zip", kind="application-container", priority=55),
    FormatSpec("tar.lzma", (".tar.lzma", ".tlzma"), True, False, "bsdtar", ("bsdtar",), kind="compressed-archive", priority=25),
    FormatSpec("tar.Z", (".tar.Z",), True, False, "bsdtar", ("bsdtar",), kind="compressed-archive", priority=25),
    FormatSpec("tar.br", (".tar.br",), True, False, "bsdtar", ("bsdtar",), kind="compressed-archive", priority=25),
    FormatSpec("cpio.gz", (".cpio.gz",), True, False, "bsdtar", ("bsdtar",), kind="compressed-archive", priority=22),
    FormatSpec("cpio.bz2", (".cpio.bz2",), True, False, "bsdtar", ("bsdtar",), kind="compressed-archive", priority=22),
    FormatSpec("cpio.xz", (".cpio.xz",), True, False, "bsdtar", ("bsdtar",), kind="compressed-archive", priority=22),
    FormatSpec("cpio.zst", (".cpio.zst",), True, False, "bsdtar", ("bsdtar",), kind="compressed-archive", priority=22),
    FormatSpec("deb", (".deb",), True, False, "bsdtar", ("bsdtar",), kind="package", priority=35),
    FormatSpec("rpm", (".rpm",), True, False, "bsdtar", ("bsdtar",), kind="package", priority=35),
    FormatSpec("arj", (".arj",), True, False, "bsdtar", ("bsdtar",), kind="archive", priority=20),
    FormatSpec("zoo", (".zoo",), True, False, "bsdtar", ("bsdtar",), kind="archive", priority=20),
    FormatSpec("sit", (".sit",), True, False, "bsdtar", ("bsdtar",), kind="archive", priority=20),
    FormatSpec("iso9660", (".iso",), True, False, "bsdtar/7z", alternatives=("bsdtar", "7z", "7zz"), kind="disk-image", priority=40),
    FormatSpec("udf", (".udf",), True, False, "bsdtar/7z", alternatives=("bsdtar", "7z", "7zz"), kind="disk-image", priority=35),
    FormatSpec("img", (".img",), True, False, "qemu-img", ("qemu-img",), kind="disk-image", priority=18, operations=("test",)),
    FormatSpec("raw", (".raw", ".dd"), True, False, "qemu-img", ("qemu-img",), kind="disk-image", priority=18, operations=("test",)),
    FormatSpec("qcow2", (".qcow2",), True, False, "qemu-img", ("qemu-img",), kind="disk-image", priority=30, operations=("test",)),
    FormatSpec("vhd", (".vhd",), True, False, "qemu-img", ("qemu-img",), kind="disk-image", priority=30, operations=("test",)),
    FormatSpec("vhdx", (".vhdx",), True, False, "qemu-img", ("qemu-img",), kind="disk-image", priority=30, operations=("test",)),
    FormatSpec("vdi", (".vdi",), True, False, "qemu-img", ("qemu-img",), kind="disk-image", priority=30, operations=("test",)),
    FormatSpec("vmdk", (".vmdk",), True, False, "qemu-img", ("qemu-img",), kind="disk-image", priority=30, operations=("test",)),
    FormatSpec("dmg", (".dmg",), True, False, "7z/bsdtar", alternatives=("7z", "7zz", "bsdtar"), kind="disk-image", priority=28, operations=("list", "extract", "test")),
    FormatSpec("squashfs", (".squashfs", ".sqsh"), True, False, "unsquashfs", ("unsquashfs",), kind="filesystem-image", priority=28, operations=("list", "extract", "test")),
    FormatSpec("ext2", (".ext2",), True, False, "debugfs", ("debugfs",), kind="filesystem-image", priority=22, operations=("list", "test")),
    FormatSpec("ext3", (".ext3",), True, False, "debugfs", ("debugfs",), kind="filesystem-image", priority=22, operations=("list", "test")),
    FormatSpec("ext4", (".ext4",), True, False, "debugfs", ("debugfs",), kind="filesystem-image", priority=22, operations=("list", "test")),
)


def all_formats() -> tuple[FormatSpec, ...]:
    return _FORMATS


def get_format(name: str) -> FormatSpec | None:
    n = name.lower().lstrip(".")
    aliases = {
        "tgz": "tar.gz", "gz": "tar.gz",
        "tzst": "tar.zst", "zst": "tar.zst",
        "txz": "tar.xz", "xz": "tar.xz",
        "tbz": "tar.bz2", "tbz2": "tar.bz2", "bz2": "tar.bz2",
        "tlz4": "tar.lz4", "lz4": "tar.lz4",
        "7zip": "7z", "7zip": "7z",
        "lzh": "lha",
        "z": "compress", "Z": "compress", "br": "brotli",
        "tlzma": "tar.lzma", "lzma": "lzma", "tar.z": "tar.Z",
    }
    n = aliases.get(n, n)
    return next((f for f in _FORMATS if f.name == n), None)


def from_extension(path: str) -> FormatSpec | None:
    low = path.lower()
    matches = []
    for f in _FORMATS:
        for ext in f.extensions:
            if low.endswith(ext.lower()):
                matches.append((len(ext), f.priority, f))
    return max(matches, key=lambda x: (x[0], x[1]))[2] if matches else None


def available_formats() -> tuple[FormatSpec, ...]:
    return tuple(f for f in _FORMATS if f.available())


def format_rows() -> list[dict]:
    rows = []
    for f in _FORMATS:
        rows.append({
            "format": f.name,
            "read": f.read,
            "write": f.write,
            "available": f.available(),
            "backend": f.backend,
            "parallel": f.parallel_compression or f.parallel_extraction,
        })
    return rows
