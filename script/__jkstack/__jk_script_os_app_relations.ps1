$TCPConnections=netstat -ano | Select-String "TCP" | Select-String "ESTABLISHED"

$RESULT="["
$count=0
foreach ($Con in $TCPConnections)
{
    $Entry=$Con -Split "\s+"
    $Protocol=$Entry[1]
    $Local_addr=$Entry[2].Split(":")[0]
    $Local_port=$Entry[2].Split(":")[1]
    $Foreign_addr=$Entry[3].Split(":")[0]
    $Foreign_port=$Entry[3].Split(":")[1]
    $State=$Entry[4]
    $AppPid=$Entry[5]
    $APP=(Get-Process -Id $Entry[5]).ProcessName
    $RESULT=$RESULT+"{""protocol"":""$Protocol"",""local_addr"":""$Local_addr"",""local_port"":""$Local_port"",
        ""foreign_addr"":""$Foreign_addr"",""foreign_port"":""$Foreign_port"",""state"":""$State"",""app"":""$APP"",""pid"":""$AppPid""}"
    $count++
    if($count -lt $TCPConnections.Count)
    {
        $RESULT=$RESULT+","
    }
    elseif($count -eq $TCPConnections.Count)
    {
        $RESULT=$RESULT+"]"
    }
}
echo $RESULT