$ErrorActionPreference = 'Stop'
$Root = Split-Path -Parent $PSScriptRoot
Set-Location $Root
$Version = python -c "import piri; print(piri.__version__)"
python build\build_portable.py
Remove-Item -Recurse -Force release -ErrorAction SilentlyContinue
New-Item -ItemType Directory release | Out-Null
python -m PyInstaller --noconfirm --clean --onefile --name piri --paths . build\piri_entry.py
Copy-Item dist\piri.exe "release\piri-$Version-windows-x86_64.exe"
Compress-Archive -Path dist-portable\piri -DestinationPath "release\piri-$Version-windows-x86_64-portable.zip" -Force
$InnoCompiler = Get-Command iscc -ErrorAction SilentlyContinue
if (-not $InnoCompiler) {
  throw 'Inno Setup is required to build the Windows Setup installer.'
}
& $InnoCompiler.Source build\piri.iss /DMyAppVersion=$Version /DSourceDir=dist-portable\piri /DOutputDir=release
if ($LASTEXITCODE -ne 0) { throw "Inno Setup failed with exit code $LASTEXITCODE" }
