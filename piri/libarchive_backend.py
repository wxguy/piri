from __future__ import annotations

from pathlib import Path
import shutil
import re
import subprocess

from .errors import BackendError
from .security import UnsafeArchiveError
from .policy import ExtractionPolicy
from .security import validate_target


from .runtime import which as _piri_which
def executable() -> str | None:
    return _piri_which("bsdtar")


def available() -> bool:
    return executable() is not None


def list_archive(path: str | Path) -> list[str]:
    exe = executable()
    if not exe:
        raise BackendError("bsdtar is not available")
    p = subprocess.run([exe, "-tf", str(path)], check=True, capture_output=True, text=True)
    return [x for x in p.stdout.splitlines() if x]


def validate_archive(path: str | Path, root: Path, policy: ExtractionPolicy) -> list[str]:
    """Validate libarchive member names before invoking extraction."""
    names = list_archive(path)
    if len(names) > policy.max_members:
        raise UnsafeArchiveError("archive member limit exceeded")
    for name in names:
        validate_target(root, name)
        if len(name) > policy.max_path_length:
            raise UnsafeArchiveError(f"archive path is too long: {name}")
    # Use the verbose listing when possible to account for regular-file sizes
    # before extraction. The format of bsdtar -tvf is intentionally parsed
    # conservatively; if a line cannot be parsed we still retain path safety.
    total = 0
    files = 0
    try:
        verbose = subprocess.run([executable(), "-tvf", str(path)], check=True,
                                 capture_output=True, text=True).stdout.splitlines()
        for line in verbose:
            if not line or len(line) < 11:
                continue
            typechar = line[0]
            if typechar not in {"-", "l"}:
                continue
            match = re.match(r"^\S+\s+\S+\s+\S+\s+(\d+)\s+", line)
            if not match:
                continue
            files += 1
            total += int(match.group(1))
            if files > policy.max_files or total > policy.max_total_bytes:
                raise UnsafeArchiveError("archive resource limit exceeded")
    except subprocess.CalledProcessError:
        pass
    return names


def extract_archive(path: str | Path, dest: str | Path, policy: ExtractionPolicy) -> list[str]:
    exe = executable()
    if not exe:
        raise BackendError("bsdtar is not available")
    root = Path(dest)
    root.mkdir(parents=True, exist_ok=True)
    names = validate_archive(path, root, policy)
    # Extract only after the complete member-name preflight succeeds. bsdtar's
    # -safety checks are then applied by the native backend itself.
    subprocess.run([exe, "-xf", str(path), "-C", str(root), "--no-same-owner"], check=True)
    return names


def test_archive(path: str | Path) -> int:
    """Test archive readability by consuming the complete libarchive listing."""
    names = list_archive(path)
    return len(names)

class LibarchiveBackend:
    """Optional bsdtar backend for formats outside the core native writer set."""

    name = "libarchive"
    formats = (
        "rar", "cab", "lha", "xar", "warc", "deb", "rpm", "arj", "zoo", "sit",
        "iso9660", "udf", "cpio.gz", "cpio.bz2", "cpio.xz", "cpio.zst",
    )

    def capability(self, fmt: str):
        from .backend import BackendCapability
        exe = executable()
        return BackendCapability(
            self.name, fmt, bool(exe), True, False, True,
            streaming=False, safe_preflight=bool(exe), executable=exe,
            version=None, reason=None if exe else "bsdtar is unavailable",
        )

    def create(self, source, destination, fmt, jobs=1, **kwargs):
        raise BackendError(f"libarchive writer is not enabled for {fmt}")

    def list(self, archive, fmt, **kwargs):
        return list_archive(archive)

    def extract(self, archive, destination, fmt, jobs=1, **kwargs):
        names = extract_archive(archive, destination, kwargs.get("policy") or ExtractionPolicy())
        progress = kwargs.get("progress")
        if progress:
            progress.total = len(names)
            progress.update(len(names), "extract")
            progress.complete("extract")

    def test(self, archive, fmt, **kwargs):
        return test_archive(archive)
