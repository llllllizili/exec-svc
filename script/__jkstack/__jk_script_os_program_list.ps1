# Read registry key as product entity.

$RESULT = "["
$UninstallPaths = @(,
# For local machine.
'HKLM:\SOFTWARE\Microsoft\Windows\CurrentVersion\Uninstall',
# For current user.
'HKCU:\Software\Microsoft\Windows\CurrentVersion\Uninstall')

# For 32bit softwares that were installed on 64bit operating system.
if([Environment]::Is64BitOperatingSystem) {
    $UninstallPaths += 'HKLM:SOFTWARE\Wow6432Node\Microsoft\Windows\CurrentVersion\Uninstall'
}
$UninstallPaths | foreach {
    Get-ChildItem $_ | foreach {
        $Name =  $_.GetValue("DisplayName")
        $Publisher = $_.GetValue("Publisher")
        $Version =  $_.GetValue("DisplayVersion")
        $Install = $_.GetValue("InstallDate")
        if($Name){
            $RESULT = $RESULT + "{""name"":""$Name"",""publisher"":""$Publisher"",""version"":""$Version"",""install"":""$Install""},"
        }
    }
}
$RESULT = $RESULT.Trim(",") + "]"
$RESULT