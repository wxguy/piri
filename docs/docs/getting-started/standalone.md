# Standalone Installers and Release Artifacts

piri provides standalone installers for end users and a source checkout for development workflows.

## 1. Recommended: standalone installation

```bash
curl -fsSL https://wxguy.github.io/piri/install.sh | bash
```

On Linux x86_64 and Apple Silicon macOS, this downloads the latest standalone release from GitHub. Windows users can download the Setup installer from the [latest release](https://github.com/wxguy/piri/releases/latest). No separate Python setup is needed on the target machine.

## Standalone release files

Standalone releases bundle the Python runtime and the native utilities staged for that platform.

### Windows

```text
piri-<version>-windows-x86_64.exe
piri-<version>-windows-x86_64-setup.exe
piri-<version>-windows-x86_64-portable.zip
```

The Setup installer installs the PyInstaller onedir bundle on the host. Its runtime files stay installed alongside the executable, avoiding the temporary extraction performed by the one-file executable. The portable ZIP contains the same onedir bundle without installing it.

### Linux

```text
piri-<version>-linux-x86_64.run
piri-<version>-linux-x86_64.img
piri-<version>-linux-x86_64.tar.gz
```

The `.run` file installs the PyInstaller onedir bundle on the host. The `.img` file is a raw ext4 filesystem image containing the complete bundle. It is **not a bootable operating system image**.

### macOS

```text
piri-<version>-macos-arm64.dmg
piri-<version>-macos.tar.gz
```

The DMG and tarball contain the PyInstaller onedir bundle, so its runtime files remain on disk between launches.

## Native backend policy

The standalone build bundles native utilities that can be legally and technically redistributed by the project and that are available in the release build environment.

A standalone build includes its Python runtime, but it cannot guarantee that every optional archive/image backend is present on every platform.

Run:

```bash
piri --formats
piri --backends
```

to see the exact capabilities of the installed build.

## Why not one `.img` for every operating system?

`.img` is not a universal application installer format. Windows uses executable installers/binaries, macOS uses DMG/app bundles, and Linux commonly uses AppImage, self-extracting installers or packages. piri publishes the native format for each platform while also providing the Linux `.img` requested for portable filesystem-image distribution.
