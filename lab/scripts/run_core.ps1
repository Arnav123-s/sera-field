# Runs a long SERA job (core_check.py or any lab script) in this visible window, from a given folder (usually a
# snapshot worktree of the commit under test), logging (UTF-8) to core-results\<Name>.log in the lab and writing a
# done marker.
#   Start-Process powershell -ArgumentList '-NoExit','-ExecutionPolicy','Bypass','-File','scripts\run_core.ps1','-Name','m1a-seed1','-From','<dir>','-Cmd','core_check.py --seed 1 --twice'
param([Parameter(Mandatory)][string]$Name, [string]$From = '', [Parameter(Mandatory)][string]$Cmd)
$lab = Split-Path $PSScriptRoot -Parent
if (-not $From) { $From = $lab }
$out = Join-Path $lab 'core-results'
New-Item -ItemType Directory -Force $out | Out-Null
$log = Join-Path $out "$Name.log"
$py = 'D:\ai\labs\ccops5-sera-lab\.venv\Scripts\python.exe'
$env:PYTHONHASHSEED = '0'; $env:PYTHONDONTWRITEBYTECODE = '1'; $env:PYTHONIOENCODING = 'utf-8'
[Console]::OutputEncoding = [Text.Encoding]::UTF8
$Host.UI.RawUI.WindowTitle = "SERA $Name"
Set-Location $From
$commit = git rev-parse --short HEAD
# One writer for the whole run, shared for reading and writing: Add-Content per line silently lost lines whenever
# another program (tail, the command center) had the log open (probe, 2026-09-24: 3 of 25 lines kept).
$stream = [IO.File]::Open($log, [IO.FileMode]::Create, [IO.FileAccess]::Write, [IO.FileShare]::ReadWrite)
$writer = New-Object IO.StreamWriter($stream, (New-Object Text.UTF8Encoding($false)))
$writer.AutoFlush = $true
function Say($s) { Write-Host $s; $writer.WriteLine($s) }
Say "name=$Name from=$From commit=$commit cmd=$Cmd started=$(Get-Date -Format s)"
$started = Get-Date
& $py @($Cmd -split ' ') 2>&1 | ForEach-Object { Say "$_" }
$code = $LASTEXITCODE
$minutes = [math]::Round(((Get-Date) - $started).TotalMinutes, 1)
Say "exit=$code minutes=$minutes finished=$(Get-Date -Format s)"
$writer.Close()
[IO.File]::WriteAllText((Join-Path $out "$Name.done"), "exit=$code minutes=$minutes commit=$commit finished=$(Get-Date -Format s)`n")
