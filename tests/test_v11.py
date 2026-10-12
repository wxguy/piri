import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parents[1]))

from piri.progress import Progress
from piri.metadata import MetadataPolicy, snapshot_metadata
from piri.formats import all_formats


def test_progress_disabled():
    p = Progress(total=10, enabled=False)
    p.update()
    p.finish()
    assert p.done == 1


def test_metadata_snapshot(tmp_path):
    f = tmp_path / "a.txt"
    f.write_text("hello")
    snap = snapshot_metadata(tmp_path)
    assert "a.txt" in snap
    assert snap["a.txt"][0] > 0


def test_optional_formats_registered():
    names = {f.name for f in all_formats()}
    assert {"rar", "cab", "lha", "xar"} <= names
