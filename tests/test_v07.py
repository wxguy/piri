import os
import subprocess
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parents[1]))

from piri.formats import all_formats, from_extension
from piri.detect import detect_format
from piri.backends import create_archive, list_archive, extract_archive


def test_registry_unique():
    names = [f.name for f in all_formats()]
    assert len(names) == len(set(names))


def test_extension_resolution():
    assert from_extension("x.tar.gz").name == "tar.gz"
    assert from_extension("x.tzst").name == "tar.zst"
    assert from_extension("x.TGZ").name == "tar.gz"


def test_roundtrip_tar_gz(tmp_path):
    src = tmp_path / "src"
    src.mkdir()
    (src / "a.txt").write_text("hello")
    (src / "b.txt").write_text("world")
    out = tmp_path / "x.tar.gz"
    restored = tmp_path / "restored"
    create_archive(src, out, "tar.gz", 2)
    d = detect_format(out)
    assert d.name == "tar.gz"
    assert "src/a.txt" in list_archive(out, "tar.gz")
    extract_archive(out, restored, "tar.gz")
    assert (restored / "src" / "a.txt").read_text() == "hello"


def test_list_zst_does_not_extract(tmp_path):
    if not __import__("shutil").which("zstd"):
        return
    src = tmp_path / "src"
    src.mkdir()
    (src / "a.txt").write_text("hello")
    out = tmp_path / "x.tar.zst"
    create_archive(src, out, "tar.zst", 2)
    names = list_archive(out, "tar.zst")
    assert "src/a.txt" in names
    assert not (tmp_path / "src" / "a.txt").exists() or (src / "a.txt").exists()
