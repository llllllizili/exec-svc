$PowerShellVersion=$psversiontable.PSVersion.ToString()

$OS = Get-WmiObject -Class Win32_OperatingSystem
$OSCaption = $OS.Caption
$OSVersion = $OS.Version
$OSSerialNumber = $OS.SerialNumber
$OSInstallDate = $OS.InstallDate
$NetworkData = Get-WmiObject -Class Win32_NetworkAdapterConfiguration -Filter IPEnabled=$true
$Computer = Get-WmiObject -Class Win32_ComputerSystem
$ComputerName = $Computer.Name
$CPUInfo = Get-WmiObject -Class Win32_Processor
$LogicalProcessorCount = (Get-WmiObject -class Win32_processor -Property NumberOfLogicalProcessors).NumberOfLogicalProcessors
if($LogicalProcessorCount -eq $null)
{
    $LogicalProcessorCount = (Get-WmiObject -class Win32_processor -Property NumberOfLogicalProcessors)[0].NumberOfLogicalProcessors

}
$LogicalProcessorCountSum = 0
foreach ( $LogicalProcessorCountVariable  in  $LogicalProcessorCount){
        $LogicalProcessorCountSum+=$LogicalProcessorCountVariable
}

$LogicalProcessorLoad = (Get-WmiObject win32_processor  -Property LoadPercentage).LoadPercentage
if($LogicalProcessorLoad -eq $null)
{
    $LogicalProcessorLoad = (Get-WmiObject win32_processor  -Property LoadPercentage)[0].LoadPercentage
}
$PhysicalProcessorCount = @($CPUInfo).Count
$PhysicalDiskInfo = Get-WmiObject -Class Win32_DiskDrive
$LogicalDiskInfo = Get-WmiObject -Class Win32_LogicalDisk -filter "DriveType=3"
$LogicalDiskCount = $LogicalDiskInfo.Count
$PhysicalDiskCount = ($PhysicalDiskInfo.Caption).Count
$MemTotal = $OS.TotalVisibleMemorySize
$MemFree = $OS.FreePhysicalMemory
$MemUsePercent = ("{0:N2}" -f (($MemTotal - $MemFree)/$MemTotal*100))+"%"

if ($PhysicalDiskCount -eq $null)
{
    $PhysicalDiskCount = $PhysicalDiskInfo.Count
}

$RESULT="{""powershellVersion"":""$PowerShellVersion"",""os"":{""osCaption"":""$OSCaption"",""osVersion"":""$OSVersion"",""serialNumber"":""$OSSerialNumber"",""osInstallTime"":""$OSInstallDate""},""system"":{""computerName"":""$ComputerName"",""physicalCPUNum"":""$PhysicalProcessorCount"",""logicalCPUNum"":""$LogicalProcessorCountSum"",""cpuUse"":""$LogicalProcessorLoad%"",""memorySizeTotal"":""$MemTotal"",""memoryUse"":""$MemUsePercent""},""cpu"":["
$count=0
foreach ($CPU in $CPUInfo)
{
    $CPUName = $CPU.Name
    $DeviceID = $CPU.DeviceID
    $RESULT=$RESULT+"{""cpuName"":""$CPUName"",""deviceID"":""$DeviceID""}"
    $count++
    if($count -lt $PhysicalProcessorCount)
    {
        $RESULT=$RESULT+","
    }
    elseif($count -eq $PhysicalProcessorCount)
    {
        $RESULT=$RESULT+"],""ip"":["
    }
    else
    {
        $RESULT=$RESULT+"],""ip"":["
    }
}
$count=0
foreach ($Network in $NetworkData)
{
    $DefaultIPGateway = $Network.DefaultIPGateway
    $NetworkAdapter = $Network.Description
    $IPAddress = $Network.IPAddress[0]
    $IPV6Address = $Network.IPAddress[1]
    $IPSubnet = $Network.IPSubnet[0]
    $MACAddress = $Network.MACAddress
    $RESULT=$RESULT+"{""defaultIPGateway"":""$DefaultIPGateway"",""networkAdapter"":""$NetworkAdapter"",""ipAddress"":""$IPAddress"",""ipV6Address"":""$IPV6Address"",""subnetMask"":""$IPSubnet"",""macAddress"":""$MACAddress""}"
    $count++
    if($count -lt $NetworkData.count)
    {
        $RESULT=$RESULT+","
    }
    elseif($count -eq $NetworkData.count)
    {
        $RESULT=$RESULT+"],""physicalDisk"":["
    }
    else
    {
        $RESULT=$RESULT+"],""physicalDisk"":["
    }
}

$count=0
foreach ($Disk in $PhysicalDiskInfo)
{
    $SerialNumber = $Disk.SerialNumber
    $DeviceID = $Disk.DeviceID.Remove(0,4)
    $DiskSize = $Disk.Size/1KB
    $RESULT=$RESULT+"{""serialNumber"":""$SerialNumber"",""deviceID"":""$DeviceID"",""diskSize"":""$DiskSize""}"
    $count++
    if($count -lt $PhysicalDiskCount)
    {
        $RESULT=$RESULT+","
    }
    elseif($count -eq $PhysicalDiskCount)
    {
        $RESULT=$RESULT+"],""logicalDisk"":["
    }
    else
    {
        $RESULT=$RESULT+"],""logicalDisk"":["
    }
}
$count=0
foreach ($Disk in $LogicalDiskInfo)
{
    $SerialNumber = $Disk.VolumeSerialNumber
    $DeviceID = $Disk.DeviceID
    $DiskSize = $Disk.Size/1KB
    $DiskFreeSpace = $Disk.FreeSpace/1KB
    $RESULT=$RESULT+"{""deviceID"":""$DeviceID"",""volumeSerialNumber"":""$SerialNumber"",""diskSize"":""$DiskSize"",""diskFreeSpace"":""$DiskFreeSpace""}"
    $count++
    if($count -lt $LogicalDiskCount)
    {
        $RESULT=$RESULT+","
    }
    elseif($count -eq $LogicalDiskCount)
    {
        $RESULT=$RESULT+"]}"
    }
    else
    {
        $RESULT=$RESULT+"]}"
    }
}
echo $RESULT