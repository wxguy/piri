import json
import subprocess
import sys
from pathlib import Path

from piri.engine import ArchiveEngine
from piri.progress import Progress
from piri.policy import ExtractionPolicy


def make_tree(root: Path):
    (root / "data").mkdir(parents=True)
    for i in range(12):
        (root / "data" / f"file-{i}.txt").write_text("piri v1.5 performance\n" * 100, encoding="utf-8")


def test_operation_telemetry(tmp_path):
    src = tmp_path / "src"
    make_tree(src)
    archive = tmp_path / "x.tar.zst"
    result = ArchiveEngine().create(src, archive, jobs=2, progress=Progress(enabled=False))
    assert result.cpu_seconds >= 0
    assert result.peak_rss_kib is None or result.peak_rss_kib > 0
    assert result.output_bytes == archive.stat().st_size


def test_extract_uses_jobs_and_returns_telemetry(tmp_path):
    src = tmp_path / "src"
    make_tree(src)
    archive = tmp_path / "x.tar.zst"
    ArchiveEngine().create(src, archive, jobs=2, progress=Progress(enabled=False))
    dest = tmp_path / "out"
    result = ArchiveEngine().extract(archive, dest, jobs=2, progress=Progress(enabled=False))
    assert result.operation == "extract"
    assert (dest / "src" / "data" / "file-11.txt").exists()
    assert result.cpu_seconds >= 0


def test_atomic_extract_creates_destination_only_after_success(tmp_path):
    src = tmp_path / "src"
    make_tree(src)
    archive = tmp_path / "x.tar.zst"
    ArchiveEngine().create(src, archive, progress=Progress(enabled=False))
    dest = tmp_path / "atomic-out"
    result = ArchiveEngine().extract(archive, dest, atomic=True, progress=Progress(enabled=False))
    assert result.operation == "extract"
    assert dest.is_dir()
    assert (dest / "src" / "data" / "file-0.txt").exists()


def test_atomic_requires_new_destination(tmp_path):
    src = tmp_path / "src"
    make_tree(src)
    archive = tmp_path / "x.tar"
    ArchiveEngine().create(src, archive, progress=Progress(enabled=False))
    dest = tmp_path / "existing"
    dest.mkdir()
    try:
        ArchiveEngine().extract(archive, dest, atomic=True, progress=Progress(enabled=False))
    except FileExistsError:
        pass
    else:
        raise AssertionError("atomic extraction should reject an existing destination")


def test_cli_stats_exposes_cpu_and_rss(tmp_path):
    src = tmp_path / "src"
    make_tree(src)
    archive = tmp_path / "x.tar.zst"
    ArchiveEngine().create(src, archive, progress=Progress(enabled=False))
    proc = subprocess.run([sys.executable, "-m", "piri.cli", "--stats", "-i", str(archive)],
                          check=True, capture_output=True, text=True)
    data = json.loads(proc.stdout)
    assert data["operation"] == "extract"
    assert "cpu_seconds" in data
    assert "peak_rss_kib" in data
