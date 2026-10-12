from pathlib import Path
import tarfile
import zipfile

from piri.detect import detect_format
from piri.formats import get_format, all_formats
from piri.engine import ArchiveEngine


def test_v20_application_container_registry():
    names = {"apk", "jar", "war", "ear", "aar"}
    assert names.issubset({f.name for f in all_formats()})
    for name in names:
        f = get_format(name)
        assert f and f.read and not f.write and f.kind == "application-container"


def test_v20_application_container_detection(tmp_path: Path):
    for ext, expected in ((".apk", "apk"), (".jar", "jar"), (".war", "war"),
                          (".ear", "ear"), (".aar", "aar")):
        p = tmp_path / f"x{ext}"
        with zipfile.ZipFile(p, "w") as zf:
            zf.writestr("META-INF/test", b"ok")
        assert detect_format(p).name == expected


def test_v20_application_container_integrity(tmp_path: Path):
    p = tmp_path / "app.jar"
    with zipfile.ZipFile(p, "w") as zf:
        zf.writestr("META-INF/test", b"hello")
    result = ArchiveEngine().test(p)
    assert result.members_processed == 1


def test_v20_deb_extension_detection(tmp_path: Path):
    p = tmp_path / "pkg.deb"
    p.write_bytes(b"!<arch>\n")
    assert detect_format(p).name == "deb"


def test_v20_squashfs_detection(tmp_path: Path):
    p = tmp_path / "root.squashfs"
    p.write_bytes(b"hsqs" + b"\0" * 64)
    assert detect_format(p).name == "squashfs"


def test_v20_ext2_detection(tmp_path: Path):
    p = tmp_path / "disk.ext2"
    data = bytearray(2048)
    data[1080:1082] = b"\x53\xef"
    p.write_bytes(data)
    assert detect_format(p).name == "ext2"


def test_v20_ext4_detection(tmp_path: Path):
    p = tmp_path / "disk.ext4"
    data = bytearray(2048)
    data[1080:1082] = b"\x53\xef"
    data[1144:1148] = (0x40).to_bytes(4, "little")
    p.write_bytes(data)
    assert detect_format(p).name == "ext4"


def test_v20_disk_formats_registered():
    names = {"dmg", "squashfs", "ext2", "ext3", "ext4"}
    assert names.issubset({f.name for f in all_formats()})


def test_v20_zip_family_not_generic_writer():
    for name in ("apk", "jar", "war", "ear", "aar"):
        assert not get_format(name).write


def test_v20_count_is_at_least_50():
    assert len(all_formats()) >= 50


def test_v20_python_module_entrypoint_exists():
    import piri.__main__  # noqa: F401


def test_v20_existing_zip_detection_unchanged(tmp_path: Path):
    p = tmp_path / "plain.zip"
    with zipfile.ZipFile(p, "w") as zf:
        zf.writestr("x.txt", b"x")
    assert detect_format(p).name == "zip"


def test_zip_create_works_without_system_zip(monkeypatch, tmp_path: Path):
    from piri import backends

    monkeypatch.setattr(backends, "_which", lambda *names: None)
    src = tmp_path / "src"
    src.mkdir()
    (src / "hello.txt").write_text("hello", encoding="utf-8")
    archive = tmp_path / "archive.zip"

    ArchiveEngine().create(src, archive)

    with zipfile.ZipFile(archive) as zf:
        assert zf.read("src/hello.txt") == b"hello"


def test_tar_extract_fallback_sanitizes_metadata(tmp_path: Path):
    from piri.backends import _extract_tar_member

    class LegacyTarFile:
        def extract(self, member, path):
            self.member = member

    member = tarfile.TarInfo("safe.txt")
    member.mode = 0o4755
    member.uid = 123
    member.gid = 456
    tf = LegacyTarFile()

    _extract_tar_member(tf, member, tmp_path)

    assert tf.member.mode == 0o755
    assert tf.member.uid is None
    assert tf.member.gid is None
