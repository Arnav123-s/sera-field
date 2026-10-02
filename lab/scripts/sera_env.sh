# SERA v3 run environment for Git Bash: keep every cache and temp file on D: (C: is full). Source it: . scripts/sera_env.sh
D='D:\ai\tools'
for p in tmp pip-cache cuda-cache numba-cache torch-home xdg-cache mpl; do mkdir -p "/d/ai/tools/$p"; done
export OMP_NUM_THREADS=1 MKL_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1 NUMBA_NUM_THREADS=1
export TEMP="$D\tmp" TMP="$D\tmp" PIP_CACHE_DIR="$D\pip-cache" CUDA_CACHE_PATH="$D\cuda-cache" NUMBA_CACHE_DIR="$D\numba-cache"
export TORCH_HOME="$D\torch-home" XDG_CACHE_HOME="$D\xdg-cache" MPLCONFIGDIR="$D\mpl" PYTHONHASHSEED=0 PYTHONIOENCODING=utf-8
export PYTHONPATH="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd -W)"
export SERA_PY=/d/ai/labs/ccops5-sera-lab/.venv/Scripts/python.exe   # CPU torch (the CUDA build wakes the GPU to P0, 19 W)
