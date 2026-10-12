from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True)
class ExtractionPolicy:
    overwrite: str = "error"          # error | replace | skip
    max_files: int = 1_000_000
    max_total_bytes: int = 100 * 1024**3
    max_path_length: int = 4096
    max_members: int = 1_000_000


def check_destination(root: Path, policy: ExtractionPolicy) -> None:
    if policy.overwrite not in {"error", "replace", "skip"}:
        raise ValueError("overwrite must be error, replace or skip")
    root.mkdir(parents=True, exist_ok=True)
    if not root.is_dir():
        raise ValueError(f"destination is not a directory: {root}")


def should_write(path: Path, policy: ExtractionPolicy) -> bool:
    if not path.exists():
        return True
    if policy.overwrite == "replace":
        return True
    if policy.overwrite == "skip":
        return False
    raise FileExistsError(f"destination already exists: {path}")
