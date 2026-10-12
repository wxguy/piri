import subprocess
import sys
from pathlib import Path

from piri.engine import ArchiveEngine
from piri.errors import BackendError
from piri.policy import ExtractionPolicy
from piri.progress import Progress


def make_tree(root: Path):
    (root / "data").mkdir(parents=True)
    for i in range(4):
        (root / "data" / f"file-{i}.txt").write_text("piri integrity test\n" * (i + 1), encoding="utf-8")


def test_tar_zst_integrity(tmp_path):
    src = tmp_path / "src"
    make_tree(src)
    archive = tmp_path / "x.tar.zst"
    ArchiveEngine().create(src, archive, jobs=2, progress=Progress(enabled=False))
    result = ArchiveEngine().test(archive)
    assert result.operation == "test"
    assert result.members_processed >= 4


def test_zip_corruption_is_detected(tmp_path):
    src = tmp_path / "src"
    make_tree(src)
    archive = tmp_path / "x.zip"
    ArchiveEngine().create(src, archive, progress=Progress(enabled=False))
    data = bytearray(archive.read_bytes())
    # Flip a byte near the middle of the ZIP. testzip() should detect a CRC
    # mismatch if this lands in compressed payload; retry offsets if necessary.
    changed = False
    for offset in range(max(0, len(data) // 4), min(len(data) * 3 // 4, len(data) - 1)):
        candidate = bytearray(data)
        candidate[offset] ^= 0x01
        archive.write_bytes(candidate)
        try:
            ArchiveEngine().test(archive)
        except Exception:
            changed = True
            break
    assert changed


def test_cli_test_option(tmp_path):
    src = tmp_path / "src"
    make_tree(src)
    archive = tmp_path / "x.tar"
    ArchiveEngine().create(src, archive, progress=Progress(enabled=False))
    proc = subprocess.run([sys.executable, "-m", "piri.cli", "-t", "--no-progress", "-i", str(archive)],
                          check=True, capture_output=True, text=True)
    assert proc.returncode == 0
    assert proc.stdout.startswith("OK:")


def test_cli_test_failure_returns_nonzero(tmp_path):
    src = tmp_path / "src"
    make_tree(src)
    archive = tmp_path / "x.tar.zst"
    ArchiveEngine().create(src, archive, progress=Progress(enabled=False))
    data = bytearray(archive.read_bytes())
    data[len(data) // 2] ^= 0x01
    archive.write_bytes(data)
    proc = subprocess.run([sys.executable, "-m", "piri.cli", "-t", "-i", str(archive)],
                          capture_output=True, text=True)
    assert proc.returncode != 0
