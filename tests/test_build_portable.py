import importlib.util
from pathlib import Path
import subprocess
import sys


_SCRIPT = Path(__file__).parents[1] / "build" / "build_portable.py"
_SPEC = importlib.util.spec_from_file_location("piri_build_portable", _SCRIPT)
assert _SPEC and _SPEC.loader
_BUILD_PORTABLE = importlib.util.module_from_spec(_SPEC)
_SPEC.loader.exec_module(_BUILD_PORTABLE)


def test_pyinstaller_entrypoint_runs_from_source():
    entrypoint = Path(__file__).parents[1] / "build" / "piri_entry.py"

    result = subprocess.run(
        [sys.executable, str(entrypoint), "--version"],
        check=True,
        capture_output=True,
        text=True,
    )

    from piri import __version__

    assert result.stdout.strip() == __version__


def test_find_built_app_accepts_onedir_output(tmp_path: Path):
    bundle = tmp_path / "piri"
    bundle.mkdir()
    (bundle / "piri").write_bytes(b"linux executable")

    assert _BUILD_PORTABLE.find_built_app(tmp_path) == bundle


def test_find_built_app_rejects_onefile_output(tmp_path: Path):
    executable = tmp_path / "piri.exe"
    executable.write_bytes(b"windows executable")

    assert _BUILD_PORTABLE.find_built_app(tmp_path) is None


def test_copy_built_app_accepts_onefolder_output(tmp_path: Path):
    built = tmp_path / "dist" / "piri"
    built.mkdir(parents=True)
    (built / "piri").write_bytes(b"standalone executable")
    destination = tmp_path / "bundle" / "piri"

    _BUILD_PORTABLE.copy_built_app(built, destination)

    assert (destination / "piri").read_bytes() == b"standalone executable"


def test_copy_built_app_rejects_onefile_output(tmp_path: Path):
    executable = tmp_path / "piri"
    executable.write_bytes(b"one-file executable")

    try:
        _BUILD_PORTABLE.copy_built_app(executable, tmp_path / "bundle")
    except NotADirectoryError:
        pass
    else:
        raise AssertionError("one-file output must not be packaged as an onedir bundle")
