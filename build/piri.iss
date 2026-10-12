#define MyAppName "piri"
#ifndef MyAppVersion
#define MyAppVersion "1.0.0"
#endif
#ifndef SourceDir
#define SourceDir "..\dist-portable\piri"
#endif
#ifndef OutputDir
#define OutputDir "..\release"
#endif
[Setup]
AppId={{C2E9E2D4-9E42-4A9B-8A35-5E0A0F2B2B01}
AppName={#MyAppName}
AppVersion={#MyAppVersion}
DefaultDirName={autopf}\piri
DefaultGroupName=piri
OutputDir={#OutputDir}
OutputBaseFilename=piri-{#MyAppVersion}-windows-x86_64-setup
Compression=lzma2
SolidCompression=yes
ArchitecturesInstallIn64BitMode=x64
ChangesEnvironment=yes
[Files]
Source: "{#SourceDir}\*"; DestDir: "{app}"; Flags: ignoreversion recursesubdirs createallsubdirs
[Icons]
Name: "{group}\piri"; Filename: "{app}\piri.exe"
Name: "{commondesktop}\piri"; Filename: "{app}\piri.exe"; Tasks: desktopicon
[Tasks]
Name: "desktopicon"; Description: "Create a desktop shortcut"; Flags: unchecked
[Code]
procedure CurStepChanged(CurStep: TSetupStep);
begin
  if (CurStep = ssPostInstall) and not WizardSilent then
    MsgBox('piri installed successfully. Open a new terminal and run: piri --version', mbInformation, MB_OK);
end;
