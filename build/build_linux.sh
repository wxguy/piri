#!/usr/bin/env bash
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT"
VERSION="$(python -c 'import piri; print(piri.__version__)')"
python build/build_portable.py
rm -rf release && mkdir -p release
TARBALL="release/piri-${VERSION}-linux-x86_64.tar.gz"
tar -C dist-portable -czf "$TARBALL" piri
cat > "release/piri-${VERSION}-linux-x86_64.run" <<'RUNEOF'
#!/usr/bin/env bash
set -euo pipefail
SELF="$(readlink -f "$0")"
ARCHIVE="${SELF%.run}.tar.gz"
if [[ ! -f "$ARCHIVE" ]]; then echo "Missing adjacent archive: $ARCHIVE" >&2; exit 1; fi
DEST="${PIRI_INSTALL_DIR:-$HOME/.local/opt/piri}"
mkdir -p "$DEST" "$HOME/.local/bin"
tar -xzf "$ARCHIVE" -C "$DEST" --strip-components=1
ln -sf "$DEST/piri" "$HOME/.local/bin/piri"
echo "Installed piri to $DEST"
RUNEOF
chmod +x "release/piri-${VERSION}-linux-x86_64.run"
# Keep a filesystem image as a distribution image; it is not bootable. Size it
# from the onedir bundle so included backends and future runtime growth fit.
IMG="release/piri-${VERSION}-linux-x86_64.img"
BUNDLE_MB="$(du -sm dist-portable/piri | cut -f1)"
IMAGE_MB="$((BUNDLE_MB + BUNDLE_MB / 2 + 64))"
truncate -s "${IMAGE_MB}M" "$IMG"
# Populate the ext4 image with the complete portable bundle.
mke2fs -q -t ext4 -d dist-portable/piri "$IMG"
