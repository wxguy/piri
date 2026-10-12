#!/usr/bin/env bash
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT"
VERSION="$(python -c 'import piri; print(piri.__version__)')"
python build/build_portable.py
rm -rf release && mkdir -p release
TARBALL="release/piri-${VERSION}-macos-arm64.tar.gz"
tar -C dist-portable -czf "$TARBALL" piri
if command -v hdiutil >/dev/null 2>&1; then
  hdiutil create -volname "piri ${VERSION}" -srcfolder dist-portable/piri -ov -format UDZO "release/piri-${VERSION}-macos-arm64.dmg"
fi
