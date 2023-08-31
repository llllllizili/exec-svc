$Key = 'HKEY_LOCAL_MACHINE\SOFTWARE\Microsoft\Windows NT\CurrentVersion'
$Name = 'ProductId'
 
$result = (Get-ItemProperty -Path "Registry::$Key" -ErrorAction Stop).$Name
 
 
"$result"