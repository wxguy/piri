#!/usr/bin/env python3
from pathlib import Path
import os, shutil, subprocess

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / 'dist-portable' / 'piri'
NATIVE = ['tar','pigz','gzip','zstd','xz','bzip2','pbzip2','lz4','zip','7z','7zz','cpio','ar','unrar','bsdtar','lha','uncompress','brotli','qemu-img','debugfs','unsquashfs']

def main():
    shutil.rmtree(ROOT/'dist-portable', ignore_errors=True)
    subprocess.check_call(['pyinstaller','--noconfirm','--clean',str(ROOT/'build'/'piri.spec')], cwd=ROOT)
    # PyInstaller's one-folder output is placed in dist/piri.
    built = ROOT/'dist'/'piri'
    if not built.exists():
        raise SystemExit('PyInstaller did not produce dist/piri')
    OUT.parent.mkdir(parents=True, exist_ok=True)
    shutil.copytree(built, OUT)
    nd = OUT/'native'; nd.mkdir(exist_ok=True)
    found=[]
    for name in NATIVE:
        src = shutil.which(name)
        if src:
            dst = nd/Path(src).name
            try: shutil.copy2(src, dst); found.append(name)
            except OSError: pass
    (nd/'MANIFEST.txt').write_text('\n'.join(found)+'\n', encoding='utf-8')
    print(f'Portable bundle: {OUT}')

if __name__ == '__main__': main()
