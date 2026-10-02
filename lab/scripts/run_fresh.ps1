# ccops5 lab | visible run: ball world version 2, FRESH seeds 21-30, run once, then the read-only audit.
# Nothing may be changed after this runs: the results are reported as they come.
$ErrorActionPreference = 'Continue'
[Console]::OutputEncoding = [System.Text.Encoding]::UTF8
$host.UI.RawUI.WindowTitle = 'ccops5 ball v2 - FRESH seeds 21-30 (run once) + read-only audit'
Set-Location (Split-Path $PSScriptRoot -Parent)   # the repo root (main or a worktree)
$env:PYTHONDONTWRITEBYTECODE = '1'
$env:PYTHONIOENCODING = 'utf-8'
$py = 'D:\ai\labs\sera-field\.venv\Scripts\python.exe'
function Tee-Utf8([string]$Path) { process { $line = "$_"; $line; Add-Content -LiteralPath $Path -Value $line -Encoding UTF8 } }
if (Test-Path 'legacy\ball\ball-fresh2') { Write-Host 'legacy\ball\ball-fresh2 already exists: fresh seeds are run once only. Stopping.' -ForegroundColor Red; Set-Content -LiteralPath 'scratch\fresh_done.txt' -Value 'refused: legacy\ball\ball-fresh2 exists' -Encoding ASCII; return }
New-Item -ItemType Directory -Path 'legacy\ball\ball-fresh2' | Out-Null
Write-Host '== ccops5 ball v2: FRESH seeds 21-30, learners concept / per_place / baseline, 4 workers ==' -ForegroundColor Cyan
& $py -u legacy\ball\ball_run.py --seeds 21 22 23 24 25 26 27 28 29 30 --results ball-fresh2 --workers 4 2>&1 | Tee-Utf8 'legacy\ball\ball-fresh2\run.log'
$run = $LASTEXITCODE
Write-Host '== read-only audit: python legacy\ball\ball_check.py --results ball-fresh2 --read-only ==' -ForegroundColor Cyan
& $py -u legacy\ball\ball_check.py --results ball-fresh2 --read-only 2>&1 | Tee-Utf8 'legacy\ball\ball-fresh2\check.log'
$check = $LASTEXITCODE
Set-Content -LiteralPath 'scratch\fresh_done.txt' -Value "run=$run check=$check" -Encoding ASCII
Write-Host "== done: run exit $run, audit exit $check. This window stays open; close it when you like. ==" -ForegroundColor Green
