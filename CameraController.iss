[Setup]
AppName=CameraController
AppVersion=1.5
WizardStyle=modern
DefaultDirName={autopf}\CameraController
DefaultGroupName=CameraController
UninstallDisplayIcon={app}\CameraController.exe
Compression=lzma2
SolidCompression=yes
DisableWelcomePage=no
UserInfoPage=no
DisableDirPage=no
DisableProgramGroupPage=no
OutputBaseFilename=CameraController

[Files]
Source: "main.pyw"; DestDir: "{app}"
Source: "requirements.txt"; DestDir: "{app}"
Source: "ico.ico"; DestDir: "{app}"
Source: "start.bat"; DestDir: "{app}";
Source: "start"; DestDir: "{app}"; 
Source: "python-3.9.7.exe"; DestDir: "{app}"; Flags: deleteafterinstall;  

[Icons]
Name: "{commondesktop}\CameraController"; Filename: "{app}\main.pyw"; IconFilename: "{app}\ico.ico"; 

[Tasks]
Name: python_task; Description: "Install python(recommended)"; GroupDescription: "Additional tasks:";

[Run]
Filename: "{app}\python-3.9.7.exe"; \
Parameters: "/passive InstallAllUsers=1 PrependPath=1"; \
WorkingDir: "{app}"; Flags: 32bit; Check: install_python
Filename: "pip.exe"; Parameters: "install -r {app}\requirements.txt"; StatusMsg: "Installing requirements...";


[Code]
function install_python() : Boolean;
var 
  key : string;
begin     

  if IsTaskSelected('python_task') then    
  begin 
      Result := true;
  end;
end;



function python_is_installed() : Boolean;
var
  key : string;
begin
   { check registry }
   key := 'software\Python\Python-3.9.7\InstallPath';
   Result := not RegValueExists(HKEY_LOCAL_MACHINE, Key, '');  
end;



var
  OutputProgressWizardPage: TOutputProgressWizardPage;
  OutputMarqueeProgressWizardPage: TOutputMarqueeProgressWizardPage;
  OutputProgressWizardPagesAfterID: Integer;

procedure InitializeWizard;
var
  InputQueryWizardPage: TInputQueryWizardPage;
  InputOptionWizardPage: TInputOptionWizardPage;
  InputDirWizardPage: TInputDirWizardPage;
  InputFileWizardPage: TInputFileWizardPage;
  OutputMsgWizardPage: TOutputMsgWizardPage;
  OutputMsgMemoWizardPage: TOutputMsgMemoWizardPage;
  AfterID: Integer;
begin



end;

 


