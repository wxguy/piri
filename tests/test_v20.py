from pathlib import Path
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
