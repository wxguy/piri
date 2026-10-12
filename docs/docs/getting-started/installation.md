# Installation

## Linux and macOS

```bash
curl -fsSL https://wxguy.github.io/piri/install.sh | bash
```

The installer downloads the latest standalone build from GitHub and installs it under `~/.local/opt/piri`, with a command link in `~/.local/bin`. Linux x86_64 and Apple Silicon macOS are currently supported. Set `PIRI_INSTALL_DIR` before running the command to choose a different application location.

The installer requires `curl` and `tar`. It adds `~/.local/bin` to common Bash and Zsh startup files so piri is available on `PATH` in new terminals. Because an installer started through `curl | bash` cannot change the calling shell, open a new terminal after installation.

## Windows

Download and run the Setup installer from the [latest GitHub release](https://github.com/wxguy/piri/releases/latest). Portable executable and ZIP downloads are also available there.

## Verify

```bash
piri --version
```

To upgrade, run the install command again. It installs the latest published release.

## Development installation

Install [uv](https://docs.astral.sh/uv/), then clone the repository and sync its development dependencies:

```bash
git clone https://github.com/wxguy/piri.git
cd piri
uv sync --extra test
```

## Optional native tools

piri uses native programs when available. Examples include:

- `tar`
- `pigz`
- `gzip`
- `zstd`
- `xz`
- `bzip2`
- `pbzip2`
- `lz4`
- `zip`
- `7z` / `7zz`
- `bsdtar`
- `qemu-img`
- `debugfs`
- `unsquashfs`

The exact set of available formats depends on the tools installed on the host.

Use:

```bash
piri --formats
piri --backends
```

to inspect the local capabilities.
