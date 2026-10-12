import sys
from pathlib import Path
import zipfile

sys.path.insert(0, str(Path(__file__).parents[1]))

from piri.engine import ArchiveEngine
from piri.policy import ExtractionPolicy
from piri.security import UnsafeArchiveError, validate_zip_members


def test_engine_roundtrip(tmp_path):
    src = tmp_path / "src"
    src.mkdir()
    (src / "a.txt").write_text("hello")
    archive = tmp_path / "a.tar.gz"
    restored = tmp_path / "restored"

    engine = ArchiveEngine()
    assert engine.create(src, archive, jobs=2) == "tar.gz"
    assert engine.detect(archive).name == "tar.gz"
    engine.extract(archive, restored)
    assert (restored / "src" / "a.txt").read_text() == "hello"


def test_zip_member_limit(tmp_path):
    archive = tmp_path / "many.zip"
    with zipfile.ZipFile(archive, "w") as z:
        for i in range(5):
            z.writestr(f"{i}.txt", "x")
    with zipfile.ZipFile(archive) as z:
        try:
            validate_zip_members(z, tmp_path / "out", ExtractionPolicy(max_members=2))
        except UnsafeArchiveError:
            return
    assert False, "member limit was not enforced"


def test_policy_values():
    p = ExtractionPolicy(overwrite="skip", max_files=10, max_total_bytes=100)
    assert p.overwrite == "skip"
    assert p.max_files == 10


def test_engine_overwrite_error(tmp_path):
    src = tmp_path / "src"
    src.mkdir()
    (src / "a.txt").write_text("hello")
    archive = tmp_path / "a.tar.gz"
    out = tmp_path / "out"
    out.mkdir()
    (out / "src").mkdir()
    (out / "src" / "a.txt").write_text("existing")

    engine = ArchiveEngine()
    engine.create(src, archive)
    try:
        engine.extract(archive, out, ExtractionPolicy(overwrite="error"))
    except FileExistsError:
        return
    assert False, "overwrite=error did not reject an existing member"
