from pathlib import Path


def test_bundled_runtime_precedes_system(monkeypatch, tmp_path):
    from piri import runtime

    bundle = tmp_path / "native"
    bundle.mkdir()
    tool = bundle / "zstd"
    tool.write_text("placeholder")
    monkeypatch.setenv("PIRI_BUNDLED_BIN", str(bundle))
    monkeypatch.setattr(runtime.shutil, "which", lambda name: "/system/zstd")
    assert runtime.which("zstd") == str(tool)
