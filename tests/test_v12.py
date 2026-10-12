import os
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parents[1]))

from piri.engine import ArchiveEngine
from piri.policy import ExtractionPolicy
from piri.progress import Progress


def make_tree(root: Path):
    (root / "data").mkdir(parents=True)
    for i in range(8):
        (root / "data" / f"file-{i}.txt").write_text(("piri-v12\n" * (i + 1)), encoding="utf-8")


def test_real_progress_for_compress_and_extract(tmp_path):
    src = tmp_path / "src"
    make_tree(src)
    archive = tmp_path / "data.tar.zst"
    restored = tmp_path / "restored"

    pc = Progress(enabled=False)
    ArchiveEngine().create(src, archive, jobs=2, progress=pc)
    assert pc.done == pc.total
    assert pc.total == 8

    pe = Progress(enabled=False)
    ArchiveEngine().extract(archive, restored, policy=ExtractionPolicy(), progress=pe)
    assert pe.done == pe.total
    assert pe.total > 0
    assert (restored / "src" / "data" / "file-7.txt").read_text(encoding="utf-8")


def test_skip_merges_nested_tree(tmp_path):
    src = tmp_path / "src"
    make_tree(src)
    archive = tmp_path / "data.tar"
    ArchiveEngine().create(src, archive, progress=Progress(enabled=False))

    dest = tmp_path / "out"
    (dest / "src" / "data").mkdir(parents=True)
    existing = dest / "src" / "data" / "file-0.txt"
    existing.write_text("KEEP", encoding="utf-8")

    ArchiveEngine().extract(archive, dest, policy=ExtractionPolicy(overwrite="skip"),
                            progress=Progress(enabled=False))
    assert existing.read_text(encoding="utf-8") == "KEEP"
    assert (dest / "src" / "data" / "file-7.txt").exists()


def test_max_members_is_enforced(tmp_path):
    src = tmp_path / "src"
    make_tree(src)
    archive = tmp_path / "data.tar"
    ArchiveEngine().create(src, archive, progress=Progress(enabled=False))
    dest = tmp_path / "out"
    try:
        ArchiveEngine().extract(archive, dest,
                                policy=ExtractionPolicy(max_members=2),
                                progress=Progress(enabled=False))
    except Exception as exc:
        assert "member limit" in str(exc).lower()
    else:
        raise AssertionError("member limit was not enforced")


def test_cpio_roundtrip_when_available(tmp_path):
    import shutil
    if not shutil.which("cpio"):
        return
    src = tmp_path / "src"
    make_tree(src)
    archive = tmp_path / "data.cpio"
    restored = tmp_path / "restored"
    engine = ArchiveEngine()
    engine.create(src, archive, progress=Progress(enabled=False))
    engine.extract(archive, restored, progress=Progress(enabled=False))
    assert (restored / "src" / "data" / "file-7.txt").exists()
