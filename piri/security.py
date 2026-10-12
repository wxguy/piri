from __future__ import annotations

from pathlib import Path, PurePosixPath
from .policy import ExtractionPolicy
import os
import zipfile
import tarfile


class UnsafeArchiveError(ValueError):
    pass


def _safe_member_path(name: str) -> PurePosixPath:
    if not name:
        raise UnsafeArchiveError("archive contains an empty member name")
    name = name.replace("\\", "/")
    p = PurePosixPath(name)
    if p.is_absolute():
        raise UnsafeArchiveError(f"absolute archive path is not allowed: {name}")
    if any(part == ".." for part in p.parts):
        raise UnsafeArchiveError(f"path traversal is not allowed: {name}")
    return p


def validate_target(root: Path, member_name: str) -> Path:
    p = _safe_member_path(member_name)
    root = root.resolve()
    target = (root / Path(*p.parts)).resolve()
    try:
        target.relative_to(root)
    except ValueError as exc:
        raise UnsafeArchiveError(f"archive path escapes extraction root: {member_name}") from exc
    return target


def validate_zip_members(zf: zipfile.ZipFile, root: Path, policy: ExtractionPolicy | None = None) -> None:
    policy = policy or ExtractionPolicy()
    infos = zf.infolist()
    if len(infos) > policy.max_members:
        raise UnsafeArchiveError("archive member limit exceeded")
    total = 0
    files = 0
    for info in infos:
        validate_target(root, info.filename)
        if len(info.filename) > policy.max_path_length:
            raise UnsafeArchiveError(f"archive path is too long: {info.filename}")
        if not info.is_dir():
            files += 1
            total += info.file_size
        if files > policy.max_files or total > policy.max_total_bytes:
            raise UnsafeArchiveError("archive resource limit exceeded")
        mode = (info.external_attr >> 16) & 0o170000
        if mode in (0o020000, 0o060000, 0o140000):
            raise UnsafeArchiveError(f"unsafe ZIP special file: {info.filename}")


def validate_tar_members(tf: tarfile.TarFile, root: Path, policy: ExtractionPolicy | None = None) -> None:
    policy = policy or ExtractionPolicy()
    members = tf.getmembers()
    if len(members) > policy.max_members:
        raise UnsafeArchiveError("archive member limit exceeded")
    total = 0
    files = 0
    for m in members:
        validate_target(root, m.name)
        if len(m.name) > policy.max_path_length:
            raise UnsafeArchiveError(f"archive path is too long: {m.name}")
        if m.isfile():
            files += 1
            total += max(0, m.size)
        if files > policy.max_files or total > policy.max_total_bytes:
            raise UnsafeArchiveError("archive resource limit exceeded")
        if m.isdev() or m.isfifo():
            raise UnsafeArchiveError(f"unsafe TAR special file: {m.name}")
        if m.issym() or m.islnk():
            validate_target(root, m.name)
            validate_target(root, m.linkname)
