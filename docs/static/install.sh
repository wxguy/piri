#!/usr/bin/env bash
set -euo pipefail

REPOSITORY='wxguy/piri'
INSTALL_DIR="${PIRI_INSTALL_DIR:-$HOME/.local/opt/piri}"
BIN_DIR="$HOME/.local/bin"

fail() {
  printf 'piri installer: %s\n' "$1" >&2
  exit 1
}

command -v curl >/dev/null 2>&1 || fail 'curl is required.'
command -v tar >/dev/null 2>&1 || fail 'tar is required.'

OS="$(uname -s)"
ARCH="$(uname -m)"
case "$OS/$ARCH" in
  Linux/x86_64|Linux/amd64)
    ASSET_SUFFIX='linux-x86_64'
    ;;
  Darwin/arm64|Darwin/aarch64)
    ASSET_SUFFIX='macos-arm64'
    ;;
  Darwin/x86_64)
    fail 'Intel macOS builds are not currently published. See the GitHub releases page.'
    ;;
  *)
    fail "unsupported platform: $OS/$ARCH. See the GitHub releases page for available builds."
    ;;
esac

LATEST_URL="https://github.com/${REPOSITORY}/releases/latest"
RELEASE_URL="$(curl -fsSL -o /dev/null -w '%{url_effective}' "$LATEST_URL")" || fail 'could not find the latest GitHub release.'
VERSION="${RELEASE_URL##*/tag/}"
VERSION="${VERSION#v}"
[[ "$VERSION" =~ ^[0-9]+\.[0-9]+\.[0-9]+([.-][A-Za-z0-9.-]+)?$ ]] || fail 'could not determine a valid release version.'

BASE_URL="https://github.com/${REPOSITORY}/releases/download/v${VERSION}"
WORK_DIR="$(mktemp -d)"
trap 'rm -rf "$WORK_DIR"' EXIT

mkdir -p "$INSTALL_DIR" "$BIN_DIR"
if [[ "$ASSET_SUFFIX" == 'linux-x86_64' ]]; then
  ASSET="piri-${VERSION}-${ASSET_SUFFIX}"
  curl -fsSL "$BASE_URL/${ASSET}.run" -o "$WORK_DIR/${ASSET}.run" || fail 'could not download the Linux installer.'
  curl -fsSL "$BASE_URL/${ASSET}.tar.gz" -o "$WORK_DIR/${ASSET}.tar.gz" || fail 'could not download the Linux application archive.'
  chmod +x "$WORK_DIR/${ASSET}.run"
  PIRI_INSTALL_DIR="$INSTALL_DIR" HOME="$HOME" "$WORK_DIR/${ASSET}.run"
else
  ASSET="piri-${VERSION}-${ASSET_SUFFIX}"
  curl -fsSL "$BASE_URL/${ASSET}.tar.gz" -o "$WORK_DIR/${ASSET}.tar.gz" || fail 'could not download the macOS application archive.'
  tar -xzf "$WORK_DIR/${ASSET}.tar.gz" -C "$WORK_DIR"
  [[ -d "$WORK_DIR/piri" ]] || fail 'the downloaded archive has an unexpected layout.'
  mkdir -p "$INSTALL_DIR"
  cp -R "$WORK_DIR/piri/." "$INSTALL_DIR/"
  ln -sfn "$INSTALL_DIR/piri" "$BIN_DIR/piri"
  printf 'Installed piri %s to %s\n' "$VERSION" "$INSTALL_DIR"
fi

PATH_LINE='case ":$PATH:" in *:"$HOME/.local/bin:"*) ;; *) export PATH="$HOME/.local/bin:$PATH" ;; esac'
for PROFILE in "$HOME/.profile" "$HOME/.bash_profile" "$HOME/.bashrc" "$HOME/.zprofile" "$HOME/.zshrc"; do
  if [[ -f "$PROFILE" ]] || [[ "$PROFILE" == "$HOME/.profile" ]]; then
    touch "$PROFILE"
    if ! grep -Fqx "$PATH_LINE" "$PROFILE"; then
      printf '\n# Added by the piri installer\n%s\n' "$PATH_LINE" >> "$PROFILE"
    fi
  fi
done

printf 'Run: %s/piri --version\n' "$BIN_DIR"
case ":$PATH:" in
  *":$BIN_DIR:"*) ;;
  *) printf 'The installer added %s to your shell startup files. Open a new terminal for PATH changes to take effect.\n' "$BIN_DIR" ;;
esac
