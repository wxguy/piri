$ErrorActionPreference = 'Stop'
$Root = Split-Path -Parent $PSScriptRoot
Set-Location $Root
$Version = python -c "import piri; print(piri.__version__)"
python build\build_portable.py
$ReleaseDir = Join-Path $Root 'release'
$BundleDir = (Resolve-Path (Join-Path $Root 'dist-portable\piri')).Path
Remove-Item -Recurse -Force $ReleaseDir -ErrorAction SilentlyContinue
New-Item -ItemType Directory $ReleaseDir | Out-Null
python -m PyInstaller --noconfirm --clean --onefile --name piri --paths . --hidden-import piri.cli --collect-submodules piri build\piri_entry.py
Copy-Item dist\piri.exe (Join-Path $ReleaseDir "piri-$Version-windows-x86_64.exe")
Compress-Archive -Path $BundleDir -DestinationPath (Join-Path $ReleaseDir "piri-$Version-windows-x86_64-portable.zip") -Force
$InnoCompiler = Get-Command iscc -ErrorAction SilentlyContinue
if (-not $InnoCompiler) {
  throw 'Inno Setup is required to build the Windows Setup installer.'
}
& $InnoCompiler.Source build\piri.iss "/DMyAppVersion=$Version" "/DSourceDir=$BundleDir" "/DOutputDir=$ReleaseDir"
if ($LASTEXITCODE -ne 0) { throw "Inno Setup failed with exit code $LASTEXITCODE" }
