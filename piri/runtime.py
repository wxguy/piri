from __future__ import annotations

import os
import shutil
import sys
from pathlib import Path


def bundled_bin_dir() -> Path | None:
    value = os.environ.get("PIRI_BUNDLED_BIN")
    if value:
        path = Path(value)
        if path.is_dir():
            return path

    # PyInstaller one-folder/one-file extraction directory.
    candidates = []
    if getattr(sys, "frozen", False):
        base = Path(getattr(sys, "_MEIPASS", Path(sys.executable).resolve().parent))
        candidates.append(base / "native")
        candidates.append(base / "bin")
        candidates.append(Path(sys.executable).resolve().parent / "native")
        candidates.append(Path(sys.executable).resolve().parent / "bin")

    for path in candidates:
        if path.is_dir():
            return path
    return None


def which(*names: str) -> str | None:
    """Find a native utility, preferring piri-bundled utilities."""
    bundle = bundled_bin_dir()
    suffixes = [""]
    if os.name == "nt":
        suffixes = ["", ".exe", ".cmd", ".bat"]

    if bundle:
        for name in names:
            for suffix in suffixes:
                candidate = bundle / f"{name}{suffix}"
                if candidate.is_file():
                    return str(candidate)

    for name in names:
        found = shutil.which(name)
        if found:
            return found
    return None
