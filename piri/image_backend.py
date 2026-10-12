from __future__ import annotations

import shutil
import subprocess
from pathlib import Path

from .backend import BackendCapability
from .errors import BackendError


from .runtime import which as _piri_which
IMAGE_FORMATS = (
    "iso9660", "udf", "img", "raw", "qcow2", "vhd", "vhdx", "vdi", "vmdk",
    "dmg", "squashfs", "ext2", "ext3", "ext4",
)


def _which(*names: str) -> str | None:
    for name in names:
        path = _piri_which(name)
        if path:
            return path
    return None


def _version(exe: str | None) -> str | None:
    if not exe:
        return None
    try:
        r = subprocess.run([exe, "--version"], capture_output=True, text=True, timeout=2)
        text = (r.stdout or r.stderr).splitlines()
        return text[0].strip()[:160] if text else None
    except Exception:
        return None


class ImageBackend:
    """Read/test disk and filesystem images without treating raw disks as archives."""

    name = "image"
    formats = IMAGE_FORMATS

    def capability(self, fmt: str) -> BackendCapability:
        if fmt in {"iso9660", "udf", "dmg"}:
            exe = _which("bsdtar", "7z", "7zz")
            return BackendCapability(
                self.name, fmt, bool(exe), True, False, True,
                streaming=False, safe_preflight=bool(exe), executable=exe,
                version=_version(exe), reason=None if exe else "bsdtar or 7z/7zz is unavailable",
            )
        if fmt == "squashfs":
            exe = _which("unsquashfs")
        elif fmt in {"ext2", "ext3", "ext4"}:
            exe = _which("debugfs")
        else:
            exe = _which("qemu-img")
        return BackendCapability(
            self.name, fmt, bool(exe), True, False, True,
            streaming=False, safe_preflight=True, executable=exe,
            version=_version(exe), reason=None if exe else "required image/filesystem utility is unavailable",
        )

    def create(self, source: Path, destination: Path, fmt: str, jobs: int = 1, **kwargs) -> None:
        raise BackendError(f"image writer is intentionally not provided for {fmt}")

    def list(self, archive: Path, fmt: str, **kwargs) -> list[str]:
        if fmt in {"iso9660", "udf", "dmg"}:
            exe = _which("bsdtar", "7z", "7zz")
            if not exe:
                raise BackendError("no ISO/UDF reader is installed")
            if Path(exe).name in {"bsdtar", "tar"}:
                return [x for x in subprocess.run([exe, "-tf", str(archive)], check=True,
                                                   capture_output=True, text=True).stdout.splitlines() if x]
            r = subprocess.run([exe, "l", str(archive)], check=True, capture_output=True, text=True)
            return [x for x in r.stdout.splitlines() if x.strip()]
        if fmt == "squashfs":
            exe = _which("unsquashfs")
            if not exe:
                raise BackendError("unsquashfs is unavailable")
            r = subprocess.run([exe, "-ll", str(archive)], check=True, capture_output=True, text=True)
            return [line.split(maxsplit=8)[-1] for line in r.stdout.splitlines() if line.strip()]
        if fmt in {"ext2", "ext3", "ext4"}:
            exe = _which("debugfs")
            if not exe:
                raise BackendError("debugfs is unavailable")
            r = subprocess.run([exe, "-R", "ls -p", str(archive)], check=True, capture_output=True, text=True)
            return [line.strip() for line in r.stdout.splitlines() if line.strip() and not line.startswith("debugfs") and not line.startswith("debugfs ")]
        raise BackendError(f"listing is not supported for raw disk image format: {fmt}")

    def extract(self, archive: Path, destination: Path, fmt: str, jobs: int = 1, **kwargs) -> None:
        if fmt in {"squashfs"}:
            exe = _which("unsquashfs")
            if not exe:
                raise BackendError("unsquashfs is unavailable")
            destination.mkdir(parents=True, exist_ok=True)
            subprocess.run([exe, "-d", str(destination), str(archive)], check=True)
            return
        if fmt not in {"iso9660", "udf", "dmg"}:
            raise BackendError(f"raw disk/filesystem image extraction is intentionally disabled: {fmt}")
        exe = _which("bsdtar", "7z", "7zz")
        if not exe:
            raise BackendError("no ISO/UDF reader is installed")
        destination.mkdir(parents=True, exist_ok=True)
        if Path(exe).name in {"bsdtar", "tar"}:
            subprocess.run([exe, "-xf", str(archive), "-C", str(destination), "--no-same-owner"], check=True)
        else:
            subprocess.run([exe, "x", str(archive), f"-o{destination}", "-y"], check=True)

    def test(self, archive: Path, fmt: str, **kwargs) -> int:
        if fmt in {"iso9660", "udf"}:
            names = self.list(archive, fmt)
            return len(names)
        if fmt == "squashfs":
            exe = _which("unsquashfs")
            if not exe:
                raise BackendError("unsquashfs is unavailable")
            subprocess.run([exe, "-stat", str(archive)], check=True, capture_output=True, text=True)
            return 1
        if fmt in {"ext2", "ext3", "ext4"}:
            exe = _which("debugfs")
            if not exe:
                raise BackendError("debugfs is unavailable")
            subprocess.run([exe, "-R", "stats", str(archive)], check=True, capture_output=True, text=True)
            return 1
        exe = _which("qemu-img")
        if not exe:
            raise BackendError("qemu-img is unavailable")
        subprocess.run([exe, "check", "--force-share", str(archive)], check=True, capture_output=True, text=True)
        return 1
