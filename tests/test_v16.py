import json
import subprocess
import sys
from pathlib import Path

from piri.engine import ArchiveEngine
from piri.registry import BackendRegistry, default_registry


def make_tree(root: Path):
    (root / "data").mkdir(parents=True)
    (root / "data" / "a.txt").write_text("piri backend registry\n" * 20, encoding="utf-8")


def test_default_registry_has_native_backend():
    registry = default_registry()
    registration = registry.get("native")
    assert registration.name == "native"
    assert "tar.zst" in registration.formats


def test_registry_resolves_native_backend_for_formats():
    engine = ArchiveEngine()
    for fmt in ("tar", "tar.gz", "tar.zst", "zip", "cpio"):
        registration = engine.registry.registration_for_format(fmt)
        assert registration is not None
        assert registration.name == "native"


def test_capability_matrix_is_structured():
    rows = ArchiveEngine().backend_capabilities()
    assert rows
    row = next(r for r in rows if r["format"] == "tar.zst")
    assert row["backend"] == "native"
    assert "parallel_compression" in row
    assert "streaming" in row
    assert "safe_preflight" in row


def test_cli_backends_json(tmp_path):
    proc = subprocess.run([sys.executable, "-m", "piri.cli", "--backends-json"],
                          check=True, capture_output=True, text=True)
    data = json.loads(proc.stdout)
    assert "backends" in data
    assert any(row["backend"] == "native" for row in data["backends"])


def test_cli_backends_text(tmp_path):
    proc = subprocess.run([sys.executable, "-m", "piri.cli", "--backends"],
                          check=True, capture_output=True, text=True)
    assert "Backend" in proc.stdout
    assert "native" in proc.stdout


def test_engine_uses_registry_for_round_trip(tmp_path):
    src = tmp_path / "src"
    make_tree(src)
    archive = tmp_path / "x.tar.zst"
    engine = ArchiveEngine()
    engine.create(src, archive)
    dest = tmp_path / "out"
    result = engine.extract(archive, dest)
    assert result.format == "tar.zst"
    assert (dest / "src" / "data" / "a.txt").exists()


def test_plugin_registration_can_override_native_priority():
    class Dummy:
        name = "dummy"
        formats = ("tar",)
        def capability(self, fmt):
            from piri.backend import BackendCapability
            return BackendCapability("dummy", fmt, True, True, True)
        def create(self, *args, **kwargs): pass
        def extract(self, *args, **kwargs): pass
        def list(self, *args, **kwargs): return []
        def test(self, *args, **kwargs): return 0

    registry = default_registry()
    registry.register(Dummy(), source="test", priority=300)
    assert registry.registration_for_format("tar").name == "dummy"


def test_benchmark_corpus_is_deterministic(tmp_path):
    from piri.corpus import create_benchmark_corpus
    a = tmp_path / "a"
    b = tmp_path / "b"
    ma = create_benchmark_corpus(a, size_mb=1, seed=7)
    mb = create_benchmark_corpus(b, size_mb=1, seed=7)
    assert ma["sha256"] == mb["sha256"]
    assert ma["files"] == 3


def test_cli_can_create_benchmark_corpus(tmp_path):
    corpus = tmp_path / "corpus"
    proc = subprocess.run(
        [sys.executable, "-m", "piri.cli", "--make-benchmark-corpus", str(corpus), "--benchmark-size-mb", "1"],
        check=True, capture_output=True, text=True,
    )
    data = json.loads(proc.stdout)
    assert data["files"] == 3
    assert corpus.is_dir()


def test_formats_output_exposes_separate_parallel_capabilities():
    proc = subprocess.run([sys.executable, "-m", "piri.cli", "--formats"], check=True, capture_output=True, text=True)
    assert "C-Par" in proc.stdout
    assert "E-Par" in proc.stdout


def test_benchmark_corpus_runs_through_selection(tmp_path):
    from piri.corpus import create_benchmark_corpus
    from piri.selection import benchmark_candidates
    corpus = tmp_path / "corpus"
    create_benchmark_corpus(corpus, size_mb=1, seed=11)
    results = benchmark_candidates(corpus, jobs=1, repeats=1, formats=["tar"])
    assert len(results) == 1
    assert results[0].status == "PASS"
    assert results[0].integrity is True
    assert results[0].compression_seconds >= 0


def test_benchmark_json_contains_telemetry_fields(tmp_path):
    from piri.corpus import create_benchmark_corpus
    from piri.selection import benchmark_candidates, result_dicts
    corpus = tmp_path / "corpus"
    create_benchmark_corpus(corpus, size_mb=1, seed=12)
    result = result_dicts(benchmark_candidates(corpus, jobs=1, repeats=1, formats=["tar"]))[0]
    assert "cpu_seconds" in result
    assert "rss_kib" in result
