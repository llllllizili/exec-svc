$process = Get-Process |  Sort PM -Descending  | select ID, Name, Description, MainWindowTitle, StartTime, CPU, WS
$RESULT = "["
$count = 0
foreach ($item in $process){
    $name = $item.Name
    $id = $item.ID
    $cpu = $item.CPU
    $mem = $item.WS
    $start = $item.StartTime
    $desc = $item.Description
    $title = $item.MainWindowTitle
    $RESULT = $RESULT + "{""name"":""$name"",""id"":""$id"",""cpu"":""$cpu (s)"",""memory"":""$mem"",""start"":""$start"",""desc"":""$desc"",""title"":""$title""}"
    $count++
    if($count -lt $process.Count)
    {
        $RESULT=$RESULT+","
    }
    elseif($count -eq $process.Count)
    {
        $RESULT=$RESULT+"]"
    }
}

echo $RESULT.Replace('\','/')