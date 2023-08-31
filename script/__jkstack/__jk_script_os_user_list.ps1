$UserAccount = Get-WmiObject -Class Win32_UserAccount
$UserAccountCount = $UserAccount.count
$RESULT="["

$count = 0
foreach ($Account in $UserAccount)
{
    $count++
    $Caption = ""
    $Domain = ""
    $AccountType = $Account.AccountType
    $Caption = $Account.Caption
    $Domain = $Account.Domain
    $SID = $Account.SID
    $FullName = $Account.FullName
    $Name = $Account.Name
    $RESULT = $RESULT + "{""accountType"":""$AccountType"",""caption"":""$Caption"",""domain"":""$Domain"",""sid"":""$SID"",""fullName"":""$FullName"",""name"":""$Name""}"
    if($count -lt $UserAccountCount)
    {
        $RESULT = $RESULT + ","
    }
    else
    {
        $RESULT = $RESULT + "]"
    }
}
$RESULT = $RESULT.Replace("\","/")

echo $RESULT