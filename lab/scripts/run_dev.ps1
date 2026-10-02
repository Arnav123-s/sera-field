# ccops5 lab | visible run: ball world version 2, dev seeds 1-10 (3 learners), then the full audit.
$ErrorActionPreference = 'Continue'
[Console]::OutputEncoding = [System.Text.Encoding]::UTF8
$host.UI.RawUI.WindowTitle = 'ccops5 ball v2 - dev seeds 1-10 + audit'
Set-Location (Split-Path $PSScriptRoot -Parent)   # the repo root (main or a worktree)
$env:PYTHONDONTWRITEBYTECODE = '1'
$env:PYTHONIOENCODING = 'utf-8'
$py = 'D:\ai\labs\sera-field\.venv\Scripts\python.exe'
function Tee-Utf8([string]$Path) { process { $line = "$_"; $line; Add-Content -LiteralPath $Path -Value $line -Encoding UTF8 } }
Remove-Item -LiteralPath 'scratch\dev_done.txt', 'legacy\ball\ball-results\run.log', 'legacy\ball\ball-results\check.log' -ErrorAction SilentlyContinue
Write-Host '== ccops5 ball v2: dev seeds 1-10, learners concept / per_place / baseline, 4 workers ==' -ForegroundColor Cyan
& $py -u legacy\ball\ball_run.py --workers 4 2>&1 | Tee-Utf8 'legacy\ball\ball-results\run.log'
$run = $LASTEXITCODE
Write-Host '== full audit: python legacy\ball\ball_check.py (A-H) ==' -ForegroundColor Cyan
& $py -u legacy\ball\ball_check.py 2>&1 | Tee-Utf8 'legacy\ball\ball-results\check.log'
$check = $LASTEXITCODE
Set-Content -LiteralPath 'scratch\dev_done.txt' -Value "run=$run check=$check" -Encoding ASCII
Write-Host "== done: run exit $run, audit exit $check. This window stays open; close it when you like. ==" -ForegroundColor Green
