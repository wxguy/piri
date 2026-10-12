from __future__ import annotations

import shutil
import subprocess
from pathlib import Path

from .backend import BackendCapability
from . import backends as legacy


_FORMATS = (
    "tar", "tar.gz", "tar.zst", "tar.xz", "tar.bz2", "tar.lz4",
    "zip", "apk", "jar", "war", "ear", "aar", "7z", "cpio", "ar", "rar", "cab", "lha", "xar", "warc", "compress", "lzma", "brotli", "zstd",
)


def _version(executable: str | None) -> str | None:
    if not executable:
        return None
    try:
        proc = subprocess.run([executable, "--version"], capture_output=True, text=True, timeout=2)
        text = (proc.stdout or proc.stderr).splitlines()
        return text[0].strip()[:160] if text else None
    except (OSError, subprocess.SubprocessError):
        return None


class NativeBackend:
    """Adapter exposing piri's mature native-command implementation as a plugin backend."""

    name = "native"
    formats = _FORMATS

    def capability(self, fmt: str) -> BackendCapability:
        info = legacy.backend_info(fmt)
        spec_available = False
        try:
            from .formats import get_format
            spec = get_format(fmt)
            spec_available = bool(spec and spec.available())
            read = bool(spec and spec.read)
            write = bool(spec and spec.write)
            test = read
        except Exception:
            read = write = test = False
        executable = info.executable
        return BackendCapability(
            name=self.name,
            format=fmt,
            available=bool(spec_available and executable),
            read=read,
            write=write,
            test=test,
            parallel_compression=info.parallel_compression,
            parallel_extraction=info.parallel_extraction,
            streaming=fmt.startswith("tar.") or fmt == "tar",
            safe_preflight=fmt in {"tar", "tar.gz", "tar.zst", "tar.xz", "tar.bz2", "tar.lz4", "zip", "7z", "cpio"},
            executable=executable,
            version=_version(executable),
            reason=None if spec_available else "required native executable is unavailable",
        )

    def create(self, source: Path, destination: Path, fmt: str, jobs: int = 1, **kwargs) -> None:
        return legacy.create_archive(source, destination, fmt, jobs,
                                     progress=kwargs.get("progress"), metadata=kwargs.get("metadata"))

    def extract(self, archive: Path, destination: Path, fmt: str, jobs: int = 1, **kwargs) -> None:
        return legacy.extract_archive(archive, destination, fmt,
                                      policy=kwargs.get("policy"), progress=kwargs.get("progress"),
                                      metadata=kwargs.get("metadata"), jobs=jobs)

    def list(self, archive: Path, fmt: str, **kwargs) -> list[str]:
        return legacy.list_archive(archive, fmt)

    def test(self, archive: Path, fmt: str, **kwargs) -> int:
        return legacy.test_archive(archive, fmt)
