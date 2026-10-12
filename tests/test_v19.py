from pathlib import Path

from piri.detect import detect_format
from piri.formats import all_formats, from_extension, get_format


def test_v19_registry_has_expanded_formats():
    names = {f.name for f in all_formats()}
    expected = {
        "lzma", "brotli", "zstd", "tar.lzma", "tar.Z", "tar.br",
        "cpio.gz", "cpio.bz2", "cpio.xz", "cpio.zst",
        "deb", "rpm", "arj", "zoo", "sit",
        "iso9660", "udf", "img", "raw", "qcow2", "vhd", "vhdx", "vdi", "vmdk",
    }
    assert expected <= names


def test_v19_extension_resolution():
    assert get_format("tar.z") is not None
    assert from_extension("sample.tar.Z").name == "tar.Z"
    assert from_extension("sample.qcow2").name == "qcow2"
    assert from_extension("sample.img").name == "img"


def test_v19_iso_signature_detection(tmp_path: Path):
    image = tmp_path / "disk.bin"
    with image.open("wb") as f:
        f.write(b"\0" * 32769)
        f.write(b"CD001")
    assert detect_format(image).name == "iso9660"


def test_v19_raw_image_formats_are_test_only():
    for name in ("img", "raw", "qcow2", "vhd", "vhdx", "vdi", "vmdk"):
        spec = get_format(name)
        assert spec is not None
        assert spec.write is False
        assert spec.operations == ("test",)
