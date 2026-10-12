from __future__ import annotations

from pathlib import Path
import hashlib
import json
import os
import random


def create_benchmark_corpus(root: str | Path, *, size_mb: int = 64, seed: int = 12345) -> dict:
    """Create a deterministic mixed corpus for archive benchmarking.

    The corpus intentionally mixes highly compressible text, moderately
    compressible structured data, and incompressible binary data.  It is
    deterministic for reproducible benchmark comparisons.
    """
    if size_mb < 1:
        raise ValueError("size_mb must be >= 1")
    root = Path(root)
    if root.exists() and any(root.iterdir()):
        raise ValueError(f"benchmark corpus destination is not empty: {root}")
    root.mkdir(parents=True, exist_ok=True)
    rng = random.Random(seed)

    text_target = max(1, size_mb * 1024 * 1024 // 3)
    binary_target = max(1, size_mb * 1024 * 1024 // 3)
    structured_target = size_mb * 1024 * 1024 - text_target - binary_target

    text = root / "text"; text.mkdir()
    structured = root / "structured"; structured.mkdir()
    binary = root / "binary"; binary.mkdir()

    def write_repeated(path: Path, target: int, block: bytes) -> int:
        written = 0
        with path.open("wb") as f:
            while written < target:
                chunk = block[: min(len(block), target - written)]
                f.write(chunk)
                written += len(chunk)
        return written

    text_block = ("piri benchmark corpus: practical archive performance testing\n" * 128).encode()
    write_repeated(text / "documentation.txt", text_target, text_block)

    structured_written = 0
    with (structured / "records.jsonl").open("w", encoding="utf-8") as f:
        while structured_written < structured_target:
            row = {
                "id": rng.randrange(1_000_000_000),
                "name": "record",
                "value": round(rng.random() * 10000, 6),
                "category": rng.choice(["metoc", "weather", "ocean", "archive"]),
            }
            line = json.dumps(row, sort_keys=True) + "\n"
            f.write(line)
            structured_written += len(line.encode())

    binary_bytes = bytearray(binary_target)
    for i in range(binary_target):
        binary_bytes[i] = rng.randrange(256)
    (binary / "random.bin").write_bytes(binary_bytes)

    files = [p for p in root.rglob("*") if p.is_file()]
    total = sum(p.stat().st_size for p in files)
    digest = hashlib.sha256()
    for p in sorted(files):
        digest.update(p.relative_to(root).as_posix().encode())
        digest.update(b"\0")
        digest.update(hashlib.sha256(p.read_bytes()).digest())
    return {"path": str(root), "files": len(files), "bytes": total, "sha256": digest.hexdigest(), "seed": seed}
