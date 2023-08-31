@echo off
::get os data
:: wmic os get Caption,Version,SerialNumber,InstallDate /value
wmic os get Caption,Version,SerialNumber,InstallDate /value
echo ---