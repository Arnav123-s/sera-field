# Runs one SERA v3 job in this visible window: .venv (CPU torch), every cache on D:, log tee'd (every line kept even while
# others read it), done marker at the end. Arguments after -Script go to the script as one string (-ArgLine).
#   Start-Process powershell -ArgumentList '-NoExit','-ExecutionPolicy','Bypass','-File','<this file>','-Name','imagine-v0','-Script','scripts\sera_train.py','-ArgLine','"--name imagine-v0 --steps 40000"'
param(
    [Parameter(Mandatory)][string]$Name,
    [Parameter(Mandatory)][string]$Script,
    [string]$ArgLine = ''
)
. (Join-Path $PSScriptRoot 'sera_env.ps1')
$root = Split-Path $PSScriptRoot -Parent
$runs = 'D:\ai\labs\ccops5-sera-lab\sera-runs'
New-Item -ItemType Directory -Force $runs | Out-Null
$log = Join-Path $runs "$Name.log"
$py = 'D:\ai\labs\ccops5-sera-lab\.venv\Scripts\python.exe'
$Host.UI.RawUI.WindowTitle = "SERA $Name"
$commit = (git -C $root rev-parse --short HEAD)
$fs = [System.IO.File]::Open($log, 'Append', 'Write', 'ReadWrite')
$w = New-Object System.IO.StreamWriter($fs, [Text.Encoding]::UTF8)
$w.AutoFlush = $true
$w.WriteLine("name=$Name commit=$commit script=$Script args=$ArgLine started=$(Get-Date -Format s)")
$started = Get-Date
$argList = @('-u', (Join-Path $root $Script)) + ($ArgLine -split ' ' | Where-Object { $_ })
& $py @argList 2>&1 | ForEach-Object { $line = "$_"; Write-Host $line; $w.WriteLine($line) }
$code = $LASTEXITCODE
$w.WriteLine("exit=$code minutes=$([math]::Round(((Get-Date) - $started).TotalMinutes, 1)) finished=$(Get-Date -Format s)")
$w.Close()
"exit=$code finished=$(Get-Date -Format s)" | Set-Content (Join-Path $runs "$Name.done") -Encoding utf8
