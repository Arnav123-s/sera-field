# ccops5 lab | visible run: do the committed results reproduce under the lab's own .venv?
# Re-runs seed 1 of every world into scratch\repro and compares value by value (only `seconds` ignored),
# then re-runs the ball checks, whose report files are committed, so `git diff` shows any change.
$ErrorActionPreference = 'Continue'
[Console]::OutputEncoding = [System.Text.Encoding]::UTF8
$host.UI.RawUI.WindowTitle = 'ccops5 reproduction check under the lab venv (seed 1 of every world)'
Set-Location (Split-Path $PSScriptRoot -Parent)   # the repo root (main or a worktree)
$env:PYTHONDONTWRITEBYTECODE = '1'
$env:PYTHONIOENCODING = 'utf-8'
$py = 'D:\ai\labs\ccops5-sera-lab\.venv\Scripts\python.exe'
$R = Join-Path (Get-Location) 'scratch\repro'   # absolute: the runners resolve --results from their own folder
function Tee-Utf8([string]$Path) { process { $line = "$_"; $line; Add-Content -LiteralPath $Path -Value $line -Encoding UTF8 } }
Remove-Item -LiteralPath $R -Recurse -Force -ErrorAction SilentlyContinue
New-Item -ItemType Directory -Path $R | Out-Null
$log = "$R\repro.log"
& $py -c "import sys, numpy, scipy, torch; print('python', sys.version.split()[0], '| numpy', numpy.__version__, '| scipy', scipy.__version__, '| torch', torch.__version__)" 2>&1 | Tee-Utf8 $log
$steps = @(
    @('main lab, seed 1', @('legacy\nursery\run.py', '--seeds', '1', '--results', "$R\main", '--workers', '4'), 'legacy\nursery\results', "$R\main"),
    @('school, seed 1', @('legacy\school\school_run.py', '--seeds', '1', '--results', "$R\school", '--workers', '4'), 'legacy\school\school-results', "$R\school"),
    @('relentless, seed 1', @('legacy\relentless\relentless_run.py', '--seeds', '1', '--results', "$R\relentless", '--workers', '4', '--others'), 'legacy\relentless\relentless-results', "$R\relentless"),
    @('inventor, seed 1', @('legacy\inventor\inventor_run.py', '--seeds', '1', '--results', "$R\inventor", '--workers', '4'), 'legacy\inventor\inventor-results', "$R\inventor"),
    @('ball, seed 1', @('legacy\ball\ball_run.py', '--seeds', '1', '--results', "$R\ball", '--workers', '4'), 'legacy\ball\ball-results', "$R\ball")
)
$summary = @()
foreach ($s in $steps) {
    Write-Host "== $($s[0]) ==" -ForegroundColor Cyan
    "== $($s[0]) ==" | Tee-Utf8 $log | Out-Null
    & $py -u @($s[1]) 2>&1 | Tee-Utf8 $log | Out-Null
    & $py scripts\compare_results.py $s[2] $s[3] 2>&1 | Tee-Utf8 $log
    $summary += "$($s[0]): compare exit $LASTEXITCODE"
}
Write-Host '== ball checks: live invariants on seed 1, and the read-only audit of fresh seeds 21-30 ==' -ForegroundColor Cyan
& $py -u legacy\ball\ball_check.py --seed 1 2>&1 | Tee-Utf8 $log | Out-Null
$summary += "ball_check --seed 1: exit $LASTEXITCODE"
& $py -u legacy\ball\ball_check.py --results ball-fresh2 --read-only 2>&1 | Tee-Utf8 $log | Out-Null
$summary += "ball_check --results ball-fresh2 --read-only: exit $LASTEXITCODE"
$summary | Tee-Utf8 $log
Set-Content -LiteralPath "$R\done.txt" -Value ($summary -join "`n") -Encoding ASCII
Write-Host '== done. Committed report files changed by this run (INVENTOR.md is expected to change and is restored during development):' -ForegroundColor Green
git status --short
