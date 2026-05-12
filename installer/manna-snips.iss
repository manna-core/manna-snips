#define AppName "Manna Snips"
#ifndef AppVersion
  #define AppVersion "0.1.1"
#endif
#ifndef SourceDir
  #define SourceDir "..\dist\installer-staging\MannaSnips"
#endif
#ifndef OutputDir
  #define OutputDir "..\dist\installer"
#endif

[Setup]
AppId={{3B0F7455-878A-4E60-B54D-BD83FD4202AF}
AppName={#AppName}
AppVersion={#AppVersion}
AppPublisher=Manna
DefaultDirName={autopf}\{#AppName}
DefaultGroupName={#AppName}
AllowNoIcons=yes
DisableWelcomePage=no
DisableDirPage=no
DisableProgramGroupPage=yes
OutputDir={#OutputDir}
OutputBaseFilename=MannaSnips-{#AppVersion}-Setup
Compression=lzma
SolidCompression=yes
WizardStyle=modern
ArchitecturesAllowed=x64compatible
ArchitecturesInstallIn64BitMode=x64compatible
UninstallDisplayIcon={app}\assets\icons\manna-snips.ico
SetupIconFile=..\assets\icons\manna-snips.ico

[Languages]
Name: "english"; MessagesFile: "compiler:Default.isl"

[Tasks]
Name: "desktopicon"; Description: "Create a desktop shortcut"; GroupDescription: "Additional shortcuts:"; Flags: unchecked

[Files]
Source: "{#SourceDir}\*"; DestDir: "{app}"; Flags: ignoreversion recursesubdirs createallsubdirs

[Registry]
Root: HKCU; Subkey: "Software\Microsoft\Windows\CurrentVersion\Run"; ValueType: string; ValueName: "MannaSnips"; ValueData: """{app}\python-runtime\pythonw.exe"" ""{app}\scripts\manna_snips_app.pyw"" --minimized"; Flags: uninsdeletevalue; Check: StartOnBootSelected

[Icons]
Name: "{autoprograms}\{#AppName}"; Filename: "{app}\python-runtime\pythonw.exe"; Parameters: """{app}\scripts\manna_snips_app.pyw"""; WorkingDir: "{app}"; IconFilename: "{app}\assets\icons\manna-snips.ico"
Name: "{autodesktop}\{#AppName}"; Filename: "{app}\python-runtime\pythonw.exe"; Parameters: """{app}\scripts\manna_snips_app.pyw"""; WorkingDir: "{app}"; Tasks: desktopicon; IconFilename: "{app}\assets\icons\manna-snips.ico"

[Run]
Filename: "{app}\python-runtime\pythonw.exe"; Parameters: """{app}\scripts\manna_snips_app.pyw"""; WorkingDir: "{app}"; Description: "Launch {#AppName}"; Flags: nowait postinstall skipifsilent unchecked

[Code]
var
  StartOnBootCheckBox: TNewCheckBox;

function StartOnBootSelected: Boolean;
begin
  Result := Assigned(StartOnBootCheckBox) and StartOnBootCheckBox.Checked;
end;

procedure InitializeWizard;
begin
  StartOnBootCheckBox := TNewCheckBox.Create(WizardForm);
  StartOnBootCheckBox.Parent := WizardForm.WelcomePage;
  StartOnBootCheckBox.Left := WizardForm.WelcomeLabel2.Left;
  StartOnBootCheckBox.Top := WizardForm.WelcomeLabel2.Top + WizardForm.WelcomeLabel2.Height + ScaleY(18);
  StartOnBootCheckBox.Width := WizardForm.WelcomeLabel2.Width;
  StartOnBootCheckBox.Height := ScaleY(32);
  StartOnBootCheckBox.Caption := 'Start with Windows after install';
  StartOnBootCheckBox.Checked := False;
end;
