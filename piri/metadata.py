from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
import os
import stat
import zipfile


@dataclass(frozen=True)
class MetadataPolicy:
    preserve_mode: bool = True
    preserve_mtime: bool = True
    preserve_owner: bool = False
    preserve_xattrs: bool = False


def snapshot_metadata(root: Path) -> dict[str, tuple[int, int]]:
    result: dict[str, tuple[int, int]] = {}
    for p in root.rglob("*"):
        try:
            st = p.lstat()
        except OSError:
            continue
        if stat.S_ISREG(st.st_mode) or stat.S_ISDIR(st.st_mode):
            result[p.relative_to(root).as_posix()] = (stat.S_IMODE(st.st_mode), st.st_mtime_ns)
    return result


def restore_basic_metadata(root: Path, snapshot: dict[str, tuple[int, int]], policy: MetadataPolicy) -> None:
    for rel, (mode, mtime_ns) in snapshot.items():
        p = root / rel
        if not p.exists() and not p.is_symlink():
            continue
        try:
            if policy.preserve_mode and not p.is_symlink():
                os.chmod(p, mode, follow_symlinks=False)
            if policy.preserve_mtime:
                os.utime(p, ns=(mtime_ns, mtime_ns), follow_symlinks=False)
        except (OSError, NotImplementedError):
            pass


def restore_zip_metadata(root: Path, info: zipfile.ZipInfo, policy: MetadataPolicy) -> None:
    """Restore the portable metadata represented by a ZIP member."""
    target = root / info.filename
    if target.is_symlink():
        return
    try:
        if policy.preserve_mode:
            mode = (info.external_attr >> 16) & 0o7777
            if mode:
                os.chmod(target, mode, follow_symlinks=False)
        if policy.preserve_mtime:
            import datetime
            # ZIP timestamps are stored as local wall-clock values.  Using a
            # naive datetime here lets Python apply the host local timezone.
            dt = datetime.datetime(*info.date_time)
            ts = dt.timestamp()
            os.utime(target, times=(ts, ts), follow_symlinks=False)
    except (OSError, ValueError, OverflowError, NotImplementedError):
        pass
