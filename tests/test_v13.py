import json
import subprocess
import sys
import shutil
from pathlib import Path

from piri.engine import ArchiveEngine
from piri.metadata import MetadataPolicy
from piri.policy import ExtractionPolicy
from piri.progress import Progress
from piri.results import OperationResult
from piri.selection import benchmark_candidates


def make_tree(root: Path):
    (root / "data").mkdir(parents=True)
    for i in range(6):
        p = root / "data" / f"file-{i}.txt"
        p.write_text("piri-v13\n" * (i + 1), encoding="utf-8")
        p.chmod(0o640)


def test_operation_results(tmp_path):
    src = tmp_path / "src"
    make_tree(src)
    archive = tmp_path / "x.tar.zst"
    out = tmp_path / "out"
    r1 = ArchiveEngine().create(src, archive, jobs=2, progress=Progress(enabled=False))
    assert isinstance(r1, OperationResult)
    assert r1.operation == "compress"
    r2 = ArchiveEngine().extract(archive, out, policy=ExtractionPolicy(),
                                  metadata=MetadataPolicy(), progress=Progress(enabled=False))
    assert isinstance(r2, OperationResult)
    assert r2.operation == "extract"


def test_zip_metadata_mode(tmp_path):
    src = tmp_path / "src"
    make_tree(src)
    archive = tmp_path / "x.zip"
    out = tmp_path / "out"
    ArchiveEngine().create(src, archive, progress=Progress(enabled=False))
    ArchiveEngine().extract(archive, out, policy=ExtractionPolicy(),
                            metadata=MetadataPolicy(), progress=Progress(enabled=False))
    target = out / "src" / "data" / "file-5.txt"
    assert target.exists()
    assert target.stat().st_mode & 0o777 == 0o640


def test_benchmark_has_memory_field(tmp_path):
    if not shutil.which("tar"):
        return
    src = tmp_path / "src"
    make_tree(src)
    results = benchmark_candidates(src, jobs=1, repeats=1, formats=["tar"])
    assert len(results) == 1
    assert hasattr(results[0], "rss_kib")


def test_stats_cli_returns_json(tmp_path):
    src = tmp_path / "src"
    make_tree(src)
    archive = tmp_path / "x.tar"
    proc = subprocess.run([sys.executable, "-m", "piri.cli", "--stats", "--no-progress",
                           "-i", str(src), "-o", str(archive)],
                          check=True, capture_output=True, text=True)
    data = json.loads(proc.stdout)
    assert data["operation"] == "compress"
    assert data["format"] == "tar"
    assert data["output_bytes"] > 0
