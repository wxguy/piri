from __future__ import annotations

import os
import shutil
import subprocess
import tarfile
import zipfile
from dataclasses import dataclass
from pathlib import Path

from .errors import BackendError
from .formats import get_format
from .policy import ExtractionPolicy
from .progress import Progress
from .security import validate_tar_members, validate_zip_members, validate_target, UnsafeArchiveError
from .metadata import MetadataPolicy, restore_zip_metadata


from .runtime import which as _piri_which
@dataclass(frozen=True)
class BackendInfo:
    format: str
    compressor: str
    executable: str | None
    parallel_compression: bool
    parallel_extraction: bool


def _which(*names):
    for n in names:
        p = _piri_which(n)
        if p:
            return p
    return None


def backend_info(fmt: str) -> BackendInfo:
    if fmt == "tar":
        return BackendInfo(fmt, "tar", _which("tar"), False, False)
    if fmt == "tar.gz":
        exe = _which("pigz", "gzip")
        return BackendInfo(fmt, os.path.basename(exe) if exe else "unavailable", exe,
                           bool(exe and os.path.basename(exe) == "pigz"), False)
    if fmt == "tar.zst":
        exe = _which("zstd")
        return BackendInfo(fmt, "zstd", exe, bool(exe), False)
    if fmt == "tar.xz":
        exe = _which("xz")
        return BackendInfo(fmt, "xz", exe, bool(exe), False)
    if fmt == "tar.bz2":
        exe = _which("pbzip2", "bzip2")
        return BackendInfo(fmt, os.path.basename(exe) if exe else "unavailable", exe,
                           bool(exe and os.path.basename(exe) == "pbzip2"), False)
    if fmt == "tar.lz4":
        exe = _which("lz4")
        return BackendInfo(fmt, "lz4", exe, bool(exe), False)
    if fmt == "zip":
        exe = _which("zip")
        return BackendInfo(fmt, "zip", exe, False, False)
    if fmt == "7z":
        exe = _which("7z", "7zz")
        return BackendInfo(fmt, "7z/7zz", exe, bool(exe), bool(exe))
    if fmt == "cpio":
        return BackendInfo(fmt, "cpio", _which("cpio"), False, False)
    if fmt == "ar":
        return BackendInfo(fmt, "ar", _which("ar"), False, False)
    if fmt == "rar":
        return BackendInfo(fmt, "unrar/bsdtar", _which("unrar", "bsdtar"), False, False)
    if fmt in {"cab", "xar", "warc"}:
        return BackendInfo(fmt, "bsdtar", _which("bsdtar"), False, False)
    if fmt == "lha":
        return BackendInfo(fmt, "lha/bsdtar", _which("lha", "bsdtar"), False, False)
    if fmt == "compress":
        return BackendInfo(fmt, "uncompress", _which("uncompress"), False, False)
    if fmt == "lzma":
        return BackendInfo(fmt, "xz --format=lzma", _which("xz"), False, False)
    if fmt == "brotli":
        return BackendInfo(fmt, "brotli", _which("brotli"), False, False)
    if fmt == "zstd":
        return BackendInfo(fmt, "zstd", _which("zstd"), True, True)
    return BackendInfo(fmt, "unknown", None, False, False)


def _run(cmd, **kwargs):
    return subprocess.run(cmd, check=True, **kwargs)


def _tar_create(src: Path, out: Path, fmt: str, jobs: int):
    parent, name = src.parent, src.name
    if fmt == "tar":
        _run(["tar", "-cf", str(out), "-C", str(parent), name])
        return
    if fmt == "tar.zst":
        compressor = ["zstd", f"-T{max(1, jobs)}", "-q", "-f", "-o", str(out), "-"]
    elif fmt == "tar.gz":
        compressor = ["pigz", "-p", str(max(1, jobs))] if _piri_which("pigz") else ["gzip"]
    elif fmt == "tar.xz":
        compressor = ["xz", "-T", str(max(1, jobs))]
    elif fmt == "tar.bz2":
        compressor = ["pbzip2", "-p", str(max(1, jobs))] if _piri_which("pbzip2") else ["bzip2"]
    elif fmt == "tar.lz4":
        compressor = ["lz4", "-q"]
    else:
        raise ValueError(fmt)

    tarp = subprocess.Popen(["tar", "-cf", "-", "-C", str(parent), name], stdout=subprocess.PIPE)
    assert tarp.stdout is not None
    try:
        if fmt == "tar.zst":
            proc = subprocess.Popen(compressor, stdin=tarp.stdout)
        else:
            with out.open("wb") as fo:
                proc = subprocess.Popen(compressor, stdin=tarp.stdout, stdout=fo)
        tarp.stdout.close()
        rc = proc.wait()
        trc = tarp.wait()
        if rc or trc:
            raise BackendError(f"compression backend failed for {fmt}")
    finally:
        if tarp.poll() is None:
            tarp.kill()


def _decompress_stream(src: Path, fmt: str, jobs: int = 1):
    if fmt == "tar.gz":
        cmd = (["pigz", "-p", str(max(1, jobs)), "-dc", str(src)] if _piri_which("pigz") else ["gzip", "-dc", str(src)])
    elif fmt == "tar.zst":
        cmd = ["zstd", "-dc", str(src)]
    elif fmt == "tar.xz":
        cmd = ["xz", "-T", str(max(1, jobs)), "-dc", str(src)]
    elif fmt == "tar.bz2":
        cmd = (["pbzip2", "-p", str(max(1, jobs)), "-dc", str(src)] if _piri_which("pbzip2") else ["bzip2", "-dc", str(src)])
    elif fmt == "tar.lz4":
        cmd = ["lz4", "-T", str(max(1, jobs)), "-dc", str(src)]
    else:
        raise ValueError(fmt)
    return subprocess.Popen(cmd, stdout=subprocess.PIPE)


def _list_stream_tar(path: Path, fmt: str, jobs: int = 1) -> list[str]:
    proc = _decompress_stream(path, fmt, jobs)
    assert proc.stdout is not None
    names: list[str] = []
    try:
        with tarfile.open(fileobj=proc.stdout, mode="r|") as tf:
            for member in tf:
                names.append(member.name)
        rc = proc.wait()
        if rc:
            raise BackendError(f"decompression backend failed for {fmt}")
        return names
    finally:
        if proc.poll() is None:
            proc.kill()


def list_archive(path: str | Path, fmt: str) -> list[str]:
    p = Path(path)
    if fmt in {"rar", "cab", "lha", "xar", "warc"}:
        from .libarchive_backend import list_archive as la
        return la(p)
    if fmt == "tar":
        with tarfile.open(p, "r:") as tf:
            return tf.getnames()
    if fmt in {"zip", "apk", "jar", "war", "ear", "aar"}:
        with zipfile.ZipFile(p) as zf:
            return zf.namelist()
    if fmt in {"tar.gz", "tar.zst", "tar.xz", "tar.bz2", "tar.lz4"}:
        return _list_stream_tar(p, fmt)
    if fmt == "7z":
        exe = _which("7z", "7zz")
        if not exe:
            raise BackendError("7z/7zz is not installed")
        r = subprocess.run([exe, "l", "-slt", str(p)], check=True, capture_output=True, text=True)
        return [line.split(" = ", 1)[1] for line in r.stdout.splitlines() if line.startswith("Path = ")][1:]
    if fmt == "ar":
        r = subprocess.run(["ar", "t", str(p)], check=True, capture_output=True, text=True)
        return r.stdout.splitlines()
    if fmt == "cpio":
        r = subprocess.run(["cpio", "-it", "-F", str(p)], check=True, capture_output=True, text=True)
        return [x for x in r.stdout.splitlines() if x]
    raise BackendError(f"listing backend not implemented for {fmt}")


def _validate_stream_tar(path: Path, fmt: str, root: Path, policy: ExtractionPolicy, jobs: int = 1) -> int:
    proc = _decompress_stream(path, fmt, jobs)
    assert proc.stdout is not None
    count = 0
    total = 0
    try:
        with tarfile.open(fileobj=proc.stdout, mode="r|") as tf:
            for m in tf:
                validate_target(root, m.name)
                if len(m.name) > policy.max_path_length:
                    raise UnsafeArchiveError(f"archive path is too long: {m.name}")
                count += 1
                if count > policy.max_members:
                    raise UnsafeArchiveError("archive member limit exceeded")
                if m.isfile():
                    if m.size < 0:
                        raise UnsafeArchiveError(f"invalid member size: {m.name}")
                    total += m.size
                    if count > policy.max_files or total > policy.max_total_bytes:
                        raise UnsafeArchiveError("archive resource limit exceeded")
                if m.isdev() or m.isfifo():
                    raise UnsafeArchiveError(f"unsafe TAR special file: {m.name}")
                if m.issym() or m.islnk():
                    validate_target(root, m.linkname)
        rc = proc.wait()
        if rc:
            raise BackendError(f"decompression backend failed for {fmt}")
        return count
    finally:
        if proc.poll() is None:
            proc.kill()


def _extract_stream_tar(path: Path, fmt: str, root: Path, policy: ExtractionPolicy, progress: Progress, jobs: int = 1) -> None:
    # First pass validates the complete stream. Second pass performs extraction.
    count = _validate_stream_tar(path, fmt, root, policy, jobs)
    progress.total = count
    proc = _decompress_stream(path, fmt, jobs)
    assert proc.stdout is not None
    try:
        with tarfile.open(fileobj=proc.stdout, mode="r|") as tf:
            for m in tf:
                tf.extract(m, root, filter="data")
                progress.update(label="extract")
        rc = proc.wait()
        if rc:
            raise BackendError(f"decompression backend failed for {fmt}")
        progress.complete("extract")
    finally:
        if proc.poll() is None:
            proc.kill()


def extract_archive(path: str | Path, dest: str | Path, fmt: str,
                    policy: ExtractionPolicy | None = None,
                    progress: Progress | None = None,
                    metadata: MetadataPolicy | None = None,
                    jobs: int = 1):
    p, root = Path(path), Path(dest)
    policy = policy or ExtractionPolicy()
    root.mkdir(parents=True, exist_ok=True)
    progress = progress or Progress(enabled=False)
    if jobs < 1:
        raise ValueError("jobs must be >= 1")

    if fmt in {"rar", "cab", "lha", "xar", "warc"}:
        from .libarchive_backend import extract_archive as ea
        names = ea(p, root, policy)
        progress.total = len(names)
        progress.update(len(names), "extract")
        progress.complete("extract")
        return
    if fmt == "tar":
        with tarfile.open(p, "r:") as tf:
            validate_tar_members(tf, root, policy)
            members = tf.getmembers()
            progress.total = len(members)
            for m in members:
                tf.extract(m, root, filter="data")
                progress.update(label="extract")
            progress.complete("extract")
        return
    if fmt in {"zip", "apk", "jar", "war", "ear", "aar"}:
        with zipfile.ZipFile(p) as zf:
            validate_zip_members(zf, root, policy)
            infos = zf.infolist()
            progress.total = len(infos)
            for info in infos:
                zf.extract(info, root)
                if metadata:
                    restore_zip_metadata(root, info, metadata)
                progress.update(label="extract")
            progress.complete("extract")
        return
    if fmt in {"tar.gz", "tar.zst", "tar.xz", "tar.bz2", "tar.lz4"}:
        _extract_stream_tar(p, fmt, root, policy, progress, jobs)
        return
    if fmt == "7z":
        exe = _which("7z", "7zz")
        if not exe:
            raise BackendError("7z/7zz is not installed")
        names = list_archive(p, fmt)
        if len(names) > policy.max_members:
            raise UnsafeArchiveError("archive member limit exceeded")
        for name in names:
            validate_target(root, name)
            if len(name) > policy.max_path_length:
                raise UnsafeArchiveError(f"archive path is too long: {name}")
        subprocess.run([exe, "x", str(p), f"-o{root}", "-y", f"-mmt={max(1, jobs)}"], check=True)
        progress.total = len(names)
        progress.update(progress.total, "extract")
        progress.complete("extract")
        return
    if fmt == "cpio":
        names = list_archive(p, fmt)
        if len(names) > policy.max_members:
            raise UnsafeArchiveError("archive member limit exceeded")
        for name in names:
            validate_target(root, name)
            if len(name) > policy.max_path_length:
                raise UnsafeArchiveError(f"archive path is too long: {name}")
        cmd = ["cpio", "-id", "--no-absolute-filenames", "-F", str(p)]
        if policy.overwrite == "replace":
            cmd.insert(2, "-u")
        subprocess.run(cmd, check=True, cwd=root, capture_output=True, text=True)
        progress.total = len(names)
        progress.update(len(names), "extract")
        progress.complete("extract")
        return
    if fmt == "ar":
        subprocess.run(["ar", "x", str(p)], check=True, cwd=root)
        return
    raise BackendError(f"extraction backend not implemented for {fmt}")



def test_archive(path: str | Path, fmt: str) -> int:
    """Read an archive completely enough to validate its container integrity.

    Returns the number of members successfully tested.  For formats with
    embedded payload checksums (for example ZIP), the backend also verifies
    those checksums.  TAR itself has no payload checksum, so a plain TAR can
    only be validated structurally; compressed TAR formats additionally have
    their compression stream validated through EOF.
    """
    p = Path(path)
    if fmt in {"rar", "cab", "lha", "xar", "warc"}:
        from .libarchive_backend import test_archive as ta
        return ta(p)
    if fmt == "tar":
        count = 0
        with tarfile.open(p, "r:") as tf:
            for member in tf:
                # Reading regular files forces tarfile to consume the member
                # payload. TAR has no payload checksum, but truncation and
                # malformed records are detected while reading to EOF.
                if member.isfile():
                    f = tf.extractfile(member)
                    if f is not None:
                        while f.read(1024 * 1024):
                            pass
                count += 1
        return count
    if fmt in {"zip", "apk", "jar", "war", "ear", "aar"}:
        with zipfile.ZipFile(p) as zf:
            bad = zf.testzip()
            if bad is not None:
                raise BackendError(f"ZIP integrity check failed: {bad}")
            return len(zf.infolist())
    if fmt in {"tar.gz", "tar.zst", "tar.xz", "tar.bz2", "tar.lz4"}:
        # The validator walks the entire decompressed stream.  Reading every
        # regular-file payload additionally exercises TAR extraction parsing.
        proc = _decompress_stream(p, fmt)
        assert proc.stdout is not None
        count = 0
        try:
            with tarfile.open(fileobj=proc.stdout, mode="r|") as tf:
                for member in tf:
                    if member.isfile():
                        f = tf.extractfile(member)
                        if f is not None:
                            while f.read(1024 * 1024):
                                pass
                    count += 1
            rc = proc.wait()
            if rc:
                raise BackendError(f"compression stream integrity check failed for {fmt}")
            return count
        finally:
            if proc.poll() is None:
                proc.kill()
    if fmt == "7z":
        exe = _which("7z", "7zz")
        if not exe:
            raise BackendError("7z/7zz is not installed")
        subprocess.run([exe, "t", str(p)], check=True, capture_output=True, text=True)
        return len(list_archive(p, fmt))
    if fmt == "cpio":
        # cpio must consume the archive to enumerate its complete member
        # stream.  Errors such as truncated input are returned by cpio.
        r = subprocess.run(["cpio", "-it", "-F", str(p)], check=True,
                           capture_output=True, text=True)
        return len([x for x in r.stdout.splitlines() if x])
    if fmt == "ar":
        subprocess.run(["ar", "t", str(p)], check=True, capture_output=True, text=True)
        return len(list_archive(p, fmt))
    if fmt == "compress":
        subprocess.run(["uncompress", "-c", str(p)], check=True,
                       stdout=subprocess.DEVNULL, stderr=subprocess.PIPE)
        return 1
    if fmt == "lzma":
        subprocess.run(["xz", "--format=lzma", "-t", str(p)], check=True,
                       stdout=subprocess.DEVNULL, stderr=subprocess.PIPE)
        return 1
    if fmt == "brotli":
        subprocess.run(["brotli", "-t", str(p)], check=True,
                       stdout=subprocess.DEVNULL, stderr=subprocess.PIPE)
        return 1
    if fmt == "zstd":
        subprocess.run(["zstd", "-t", str(p)], check=True,
                       stdout=subprocess.DEVNULL, stderr=subprocess.PIPE)
        return 1
    raise BackendError(f"integrity test backend not implemented for {fmt}")

def _source_file_count(src: Path) -> int:
    return sum(1 for p in src.rglob("*") if p.is_file())


def create_archive(src: str | Path, out: str | Path, fmt: str, jobs: int,
                   progress: Progress | None = None, metadata: MetadataPolicy | None = None):
    src, out = Path(src), Path(out)
    out.parent.mkdir(parents=True, exist_ok=True)
    progress = progress or Progress(enabled=False)
    progress.total = _source_file_count(src)
    if fmt == "tar" or fmt.startswith("tar."):
        _tar_create(src, out, fmt, jobs)
    elif fmt == "zip":
        _run(["zip", "-rq", str(out), src.name], cwd=src.parent)
    elif fmt == "cpio":
        # GNU cpio accepts a NUL-delimited file list, so names are never
        # reparsed through a shell. find supplies the list without loading it
        # into Python memory.
        finder = subprocess.Popen(["find", src.name, "-print0"], cwd=src.parent, stdout=subprocess.PIPE)
        assert finder.stdout is not None
        try:
            with out.open("wb") as fo:
                proc = subprocess.Popen(["cpio", "-0", "-o", "-H", "newc"], cwd=src.parent, stdin=finder.stdout, stdout=fo, stderr=subprocess.PIPE)
                finder.stdout.close()
                _, err = proc.communicate()
            frc = finder.wait()
            if proc.returncode or frc:
                raise BackendError(f"cpio creation failed: {err.decode(errors='replace')}")
        finally:
            if finder.poll() is None:
                finder.kill()
    elif fmt == "7z":
        exe = _which("7z", "7zz")
        if not exe:
            raise BackendError("7z/7zz is not installed")
        _run([exe, "a", f"-mmt={max(1,jobs)}", str(out), src.name], cwd=src.parent)
    else:
        raise BackendError(f"creation backend not implemented for {fmt}")
    progress.update(progress.total, "compress")
    progress.complete("compress")
