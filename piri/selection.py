from __future__ import annotations

from dataclasses import dataclass, asdict
from pathlib import Path
import hashlib
import statistics
import tempfile
import time
import os

from .backends import create_archive, extract_archive
from .formats import all_formats
from .telemetry import PeakRSSMonitor, cpu_times


@dataclass
class CandidateResult:
    format: str
    status: str
    original_bytes: int = 0
    archive_bytes: int = 0
    ratio: float = 0.0
    compression_seconds: float = 0.0
    extraction_seconds: float = 0.0
    compression_mib_s: float = 0.0
    extraction_mib_s: float = 0.0
    integrity: bool = False
    score: float | None = None
    rank: int | None = None
    error: str = ""
    rss_kib: int | None = None
    cpu_seconds: float = 0.0


def _files_digest(root: Path) -> str:
    h = hashlib.sha256()
    for p in sorted(x for x in root.rglob("*") if x.is_file()):
        rel = p.relative_to(root).as_posix().encode()
        h.update(rel)
        h.update(b"\0")
        with p.open("rb") as f:
            while True:
                b = f.read(1024 * 1024)
                if not b:
                    break
                h.update(b)
    return h.hexdigest()


def _dataset_bytes(root: Path) -> int:
    return sum(p.stat().st_size for p in root.rglob("*") if p.is_file())


def candidate_formats() -> list:
    # Only generic directory archive writers belong in --best.
    names = {"tar", "tar.gz", "tar.zst", "tar.xz", "tar.bz2", "tar.lz4", "zip", "7z"}
    return [f for f in all_formats() if f.write and f.read and f.available() and f.name in names]


def benchmark_candidates(src: str | Path, jobs: int = 1, repeats: int = 3,
                         formats: list[str] | None = None) -> list[CandidateResult]:
    src = Path(src)
    selected = candidate_formats()
    if formats:
        wanted = set(formats)
        selected = [f for f in selected if f.name in wanted]

    original = _dataset_bytes(src)
    source_digest = _files_digest(src)
    results = []

    for spec in selected:
        runs = []
        # One warm-up pass reduces first-execution effects on small datasets.
        with tempfile.TemporaryDirectory(prefix="piri-warmup-") as td:
            try:
                warm_archive = Path(td) / ("warm" + spec.extensions[0])
                warm_restored = Path(td) / "restored"
                create_archive(src, warm_archive, spec.name, jobs)
                extract_archive(warm_archive, warm_restored, spec.name)
            except Exception:
                pass

        for _ in range(max(1, repeats)):
            with tempfile.TemporaryDirectory(prefix="piri-select-") as td:
                td = Path(td)
                archive = td / ("archive" + spec.extensions[0])
                restored = td / "restored"
                t0 = time.perf_counter()
                cpu0 = cpu_times()
                try:
                    with PeakRSSMonitor() as monitor:
                        create_archive(src, archive, spec.name, jobs)
                        ctime = time.perf_counter() - t0
                        t1 = time.perf_counter()
                        extract_archive(archive, restored, spec.name)
                        etime = time.perf_counter() - t1
                    digest_ok = _files_digest(restored / src.name) == source_digest
                    size = archive.stat().st_size
                    cpu1 = cpu_times()
                    cpu = max(0.0, sum(cpu1) - sum(cpu0))
                    runs.append((size, ctime, etime, digest_ok, monitor.peak_kib, cpu))
                except Exception as exc:
                    runs.append(("ERROR", 0.0, 0.0, False, str(exc)))

        errors = [r for r in runs if r[0] == "ERROR"]
        if errors:
            results.append(CandidateResult(spec.name, "FAIL",
                                           original_bytes=original,
                                           error=errors[0][-1]))
            continue

        size = int(statistics.median(r[0] for r in runs))
        ctime = statistics.median(r[1] for r in runs)
        etime = statistics.median(r[2] for r in runs)
        ok = all(r[3] for r in runs)
        rss_values = [r[4] for r in runs if len(r) > 4 and r[4] is not None]
        cpu_values = [r[5] for r in runs if len(r) > 5]
        results.append(CandidateResult(
            format=spec.name,
            status="PASS" if ok else "FAIL",
            original_bytes=original,
            archive_bytes=size,
            ratio=(original / size) if size else 0.0,
            compression_seconds=ctime,
            extraction_seconds=etime,
            compression_mib_s=(original / 1048576 / ctime) if ctime else 0.0,
            extraction_mib_s=(original / 1048576 / etime) if etime else 0.0,
            integrity=ok,
            rss_kib=max(rss_values) if rss_values else None,
            cpu_seconds=(statistics.median(cpu_values) if cpu_values else 0.0),
        ))
    return results


def _rank(results: list[CandidateResult], mode: str):
    good = [r for r in results if r.status == "PASS" and r.integrity]
    if not good:
        raise RuntimeError("no benchmark candidate completed successfully")

    min_size = min(r.archive_bytes for r in good)
    min_comp = min(r.compression_seconds for r in good)
    min_ext = min(r.extraction_seconds for r in good)

    def score(r):
        if mode == "smallest":
            return r.archive_bytes / min_size
        if mode == "fastest":
            return r.compression_seconds / min_comp
        if mode == "extract-fast":
            return r.extraction_seconds / min_ext
        if mode == "balanced":
            return 0.5 * (r.archive_bytes / min_size) + 0.5 * (r.compression_seconds / min_comp)
        raise ValueError(f"unknown selection mode: {mode}")

    ranked = sorted(good, key=lambda r: (score(r), r.archive_bytes, r.format))
    for i, r in enumerate(ranked, 1):
        r.score = score(r)
        r.rank = i
    return ranked


def choose_result(results: list[CandidateResult], mode: str) -> CandidateResult:
    return _rank(results, mode)[0]


def rank_results(results: list[CandidateResult], mode: str) -> list[CandidateResult]:
    return _rank(results, mode)


def result_dicts(results):
    return [asdict(r) for r in results]
