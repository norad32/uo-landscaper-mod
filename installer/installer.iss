; UO Landscaper Mod Setup Script
; Requires Inno Setup (http://www.jrsoftware.org/isinfo.php)
; To build: Open this .iss in Inno Setup and compile

#define MyAppName "UO Landscaper Mod"
#define MyAppVersion "0.1.0"
#define MyAppPublisher "norad32"
#define MyAppURL "norad32.github.io/uo-landscaper-mod/"

[Setup]
; NOTE: The value of AppId uniquely identifies this application. Do not use the same AppId value in installers for other applications.
; (To generate a new GUID, click Tools | Generate GUID inside the IDE.)
AppId={{2F0EC28D-A257-4A50-92A7-6D92E26DD1BD}}
AppName={#MyAppName}
AppVersion={#MyAppVersion}
AppPublisher={#MyAppPublisher}
AppPublisherURL={#MyAppURL}
AppSupportURL={#MyAppURL}
AppUpdatesURL={#MyAppURL}
DefaultDirName={autopf}\{#MyAppName}
DefaultGroupName={#MyAppName}
AllowNoIcons=yes
LicenseFile=..\LICENSE
OutputBaseFilename=uol-mod-installer
Compression=lzma
SolidCompression=yes
WizardStyle=modern
PrivilegesRequired=admin
Uninstallable=no
DisableProgramGroupPage=yes

[Languages]
Name: "english"; MessagesFile: "compiler:Default.isl"

[Files]
Source: "../Data.xml"; DestDir: "{app}"; Flags: ignoreversion
Source: "../LICENSE"; DestDir: "{app}"; Flags: ignoreversion
Source: "../README.md"; DestDir: "{app}"; Flags: ignoreversion
Source: "../data/*"; DestDir: "{app}/data"; Flags: ignoreversion recursesubdirs createallsubdirs

[Code]
var
  OriginalDirPage: TInputDirWizardPage;

function FileExistsOrDirExists(Path: String): Boolean;
begin
  Result := FileExists(Path) or DirExists(Path);
end;

function CopyFileIfExists(const SourceFile, DestFile: String): Boolean;
begin
  if FileExists(SourceFile) then
    Result := FileCopy(SourceFile, DestFile, False)
  else
    Result := False;
end;

function ForceDirExists(Dir: string): Boolean;
begin
  if DirExists(Dir) then
    Result := False
  else
    Result := ForceDirectories(Dir);
end;

function CopyDirectoryIfExists(const Source, Dest: String): Boolean;
var
  FindRec: TFindRec;
  SourcePath, DestPath: String;
begin
  if not DirExists(Source) then
  begin
    Result := False;
    Exit;
  end;

  if not DirExists(Dest) then
    if not ForceDirExists(Dest) then
    begin
      Result := False;
      Exit;
    end;

  Result := True;
  if FindFirst(Source + '\*', FindRec) then
  begin
    try
      repeat
        if (FindRec.Name <> '.') and (FindRec.Name <> '..') then
        begin
          SourcePath := Source + '\' + FindRec.Name;
          DestPath := Dest + '\' + FindRec.Name;
          if (FindRec.Attributes and FILE_ATTRIBUTE_DIRECTORY) <> 0 then
          begin
            if not CopyDirectoryIfExists(SourcePath, DestPath) then
              Result := False;
          end
          else
          begin
            if not FileCopy(SourcePath, DestPath, False) then
              Result := False;
          end;
        end;
      until not FindNext(FindRec);
    finally
      FindClose(FindRec);
    end;
  end;
end;

procedure InitializeWizard;
begin
  // Create directory selection page
  OriginalDirPage := CreateInputDirPage(
    wpWelcome,
    'UO Landscaper Directory',
    'Please select the directory where UO Landscaper is installed.',
    'Select the folder containing your existing UO Landscaper installation:',
    True, '');
  OriginalDirPage.Add('');
  OriginalDirPage.Values[0] := 'C:\Program Files (x86)\UO_Landscaper_1.4.0\';
end;

procedure CurStepChanged(CurStep: TSetupStep);
var
  OriginalPath, DestPath: String;
  Success: Boolean;
  ErrorCode: Integer;
begin
  if CurStep = ssInstall then
  begin
    OriginalPath := OriginalDirPage.Values[0];
    if OriginalPath = '' then
    begin
      MsgBox('No UO Landscaper directory selected. Installation cannot proceed.', mbError, MB_OK);
      Abort();
    end;

    DestPath := ExpandConstant('{app}');
    
    if CompareText(OriginalPath, DestPath) = 0 then
    begin
      MsgBox('The UO Landscaper directory cannot be the same as the installation directory for the mod. Please choose a different directory.', mbError, MB_OK);
      Abort();
    end;
    
    Success := True;

    // Copy list of files
    Success := Success and CopyFileIfExists(OriginalPath + '\please_read.txt', DestPath + '\please_read.txt');
    Success := Success and CopyFileIfExists(OriginalPath + '\Altitude.dll', DestPath + '\Altitude.dll');
    Success := Success and CopyFileIfExists(OriginalPath + '\Terrain.dll', DestPath + '\Terrain.dll');
    Success := Success and CopyFileIfExists(OriginalPath + '\Logger.dll', DestPath + '\Logger.dll');
    Success := Success and CopyFileIfExists(OriginalPath + '\DataList.exe', DestPath + '\DataList.exe');
    Success := Success and CopyFileIfExists(OriginalPath + '\AltImagePrep.exe', DestPath + '\AltImagePrep.exe');
    Success := Success and CopyFileIfExists(OriginalPath + '\Transition.dll', DestPath + '\Transition.dll');
    Success := Success and CopyFileIfExists(OriginalPath + '\DataVeiwer.exe', DestPath + '\DataVeiwer.exe');
    Success := Success and CopyFileIfExists(OriginalPath + '\Mul2Bmp.exe', DestPath + '\Mul2Bmp.exe');
    Success := Success and CopyFileIfExists(OriginalPath + '\NewMapImage.exe', DestPath + '\NewMapImage.exe');
    Success := Success and CopyFileIfExists(OriginalPath + '\UOMapMake.exe', DestPath + '\UOMapMake.exe');
    Success := Success and CopyFileIfExists(OriginalPath + '\DragonConv.exe', DestPath + '\DragonConv.exe');
    Success := Success and CopyFileIfExists(OriginalPath + '\Ultima.dll', DestPath + '\Ultima.dll');
    Success := Success and CopyFileIfExists(OriginalPath + '\Twiz.exe', DestPath + '\Twiz.exe');
    Success := Success and CopyFileIfExists(OriginalPath + '\SEdit.exe', DestPath + '\SEdit.exe');
    Success := Success and CopyFileIfExists(OriginalPath + '\TEdit.exe', DestPath + '\TEdit.exe');
    Success := Success and CopyFileIfExists(OriginalPath + '\UOLandscaper.exe', DestPath + '\UOLandscaper.exe');

    // Copy directories
    Success := Success and CopyDirectoryIfExists(OriginalPath + '\Data\Import Files', DestPath + '\data\import files');
    Success := Success and CopyDirectoryIfExists(OriginalPath + '\Data\Photoshop', DestPath + '\data\photoshop');

    if not Success then
    begin
      MsgBox('Some files may not have copied successfully, but installation will continue.', mbInformation, MB_OK);
    end;
  end
  else if CurStep = ssPostInstall then
  begin
      ShellExec('', 'explorer.exe', ExpandConstant('{app}'), '', SW_SHOWNORMAL, ewNoWait, ErrorCode);
  end;
end;