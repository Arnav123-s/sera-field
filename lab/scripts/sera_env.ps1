# SERA v3 run environment: keep every cache and temp file on D: (C: is full). Dot-source it: . .\scripts\sera_env.ps1
$d = 'D:\ai\tools'
foreach ($p in 'tmp','pip-cache','cuda-cache','numba-cache','torch-home','xdg-cache','mpl') { New-Item -ItemType Directory -Force (Join-Path $d $p) | Out-Null }
$env:TEMP = "$d\tmp"; $env:TMP = "$d\tmp"
$env:PIP_CACHE_DIR = "$d\pip-cache"
$env:CUDA_CACHE_PATH = "$d\cuda-cache"
$env:NUMBA_CACHE_DIR = "$d\numba-cache"
$env:TORCH_HOME = "$d\torch-home"
$env:XDG_CACHE_HOME = "$d\xdg-cache"
$env:MPLCONFIGDIR = "$d\mpl"
$env:PYTHONHASHSEED = '0'
$env:PYTHONIOENCODING = 'utf-8'
$env:PYTHONPATH = (Resolve-Path (Join-Path $PSScriptRoot '..')).Path
