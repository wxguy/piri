from PyInstaller.utils.hooks import collect_submodules

hiddenimports = collect_submodules('piri')

block_cipher = None

a = Analysis(
    ['../piri/__main__.py'],
    pathex=['..'],
    binaries=[],
    datas=[],
    hiddenimports=hiddenimports,
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    noarchive=False,
)
pyz = PYZ(a.pure)
exe = EXE(pyz, a.scripts, [], exclude_binaries=True, name='piri', debug=False,
          bootloader_ignore_signals=False, strip=False, upx=True, console=True)
coll = COLLECT(exe, a.binaries, a.datas, strip=False, upx=True,
               upx_exclude=[], name='piri')
