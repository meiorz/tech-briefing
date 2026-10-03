if (-not (Test-NetConnection 127.0.0.1 -Port 10000 -InformationLevel Quiet -WarningAction SilentlyContinue)) {
    Write-Host "Azurite is not running. Start it first: azurite --location .azurite --silent" -ForegroundColor Red
    return
}
. "$PSScriptRoot\.venv\Scripts\Activate.ps1"
$env:Path = ($env:Path -split ';' | Where-Object { $_ -notlike 'C:\msys64\*' }) -join ';'
Write-Host "python : $((Get-Command python.exe).Source)"
Write-Host "python3: $((Get-Command python3.exe -ErrorAction SilentlyContinue).Source ?? 'not found (good)')"
func start
