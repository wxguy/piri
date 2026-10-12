$ErrorActionPreference = 'Stop'
$Root = Split-Path -Parent $PSScriptRoot
Set-Location $Root
$Version = python -c "import piri; print(piri.__version__)"
python build\build_portable.py
Remove-Item -Recurse -Force release -ErrorAction SilentlyContinue
New-Item -ItemType Directory release | Out-Null
python -m PyInstaller --noconfirm --clean --onefile --name piri piri\__main__.py
Copy-Item dist\piri.exe "release\piri-$Version-windows-x86_64.exe"
Compress-Archive -Path dist-portable\piri -DestinationPath "release\piri-$Version-windows-x86_64-portable.zip" -Force
if (Get-Command iscc -ErrorAction SilentlyContinue) {
  iscc build\piri.iss /DMyAppVersion=$Version /DSourceDir=dist-portable\piri /DOutputDir=release
}
