function Get-SystemInfo
{
  param($ComputerName = $env:COMPUTERNAME)
  $header = 'Hostname','OSfinger','OSVersion','OSManufacturer','OSConfiguration','OS Build Type','RegisteredOwner','RegisteredOrganization','Product ID','Original Install Date','System Boot Time','System Manufacturer','System Model','System Type','Processor(s)','BIOS Version','Windows Directory','System Directory','Boot Device','System Locale','Input Locale','Time Zone','Total Physical Memory','Available Physical Memory','Virtual Memory: Max Size','Virtual Memory: Available','Virtual Memory: In Use','Page File Location(s)','Domain','Logon Server','Hotfix(s)','Network Card(s)'

  systeminfo.exe /FO CSV /S $ComputerName |
    Select-Object -Skip 1 |
    ConvertFrom-CSV -Header $header
}

$info = GET-SystemInfo

function GET-interfaces
{
  $length = (GET-NetIPaddress | select InterfaceAlias).Count

  for($i=1;$i -lt $length;$i++)
  {
     $IPaddr = (GET-NetIPaddress | select IPaddress)[$i] -split(":")[0]
     $Interfaces = (GET-NetIPaddress | select InterfaceAlias)[$i] -split(":")[0]
      $RESULT = "{""$IPaddr"",""$Interfaces""}"
      $RESULTS+=$RESULT+","
  }
  $RESULTS
}

$GETinterface = GET-interfaces
$OSfinger = $info | select OSfinger
$results = "[""$OSfinger""`n""$GETinterface""]"
$results