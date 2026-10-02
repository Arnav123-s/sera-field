#!/usr/bin/env bash
# The fast test suite, one pytest process per file. Run from the repo root:
#   OUT=test-results/fast PY=.venv/bin/python bash scripts/runtests.sh [files...]
# Slow tests run separately, one collected node per process (including each parameter case):
#   SUITE=slow OUT=/content/tests-slow JOBS=1 SLOW_CAP=7200 PY=/content/venv-dev/bin/python bash scripts/runtests.sh [files...]
# SUITE=integration selects only the marked full-universe/end-to-end integration tests.
# Default files: tests/core and tests/sera (the legacy minds' tests in legacy/sera_v3/tests are not included).
# Fast: CAP seconds per file (default 1200), excluding slow tests. Slow/integration: SLOW_CAP seconds per node
# (default 7200, above the growth test's measured 6158 s pass in S19). Full audit budgets need fresh node timings;
# --durations=0 and the summary record them. Writes logs and summary.txt; exits 1 on failure or timeout.
set -u
PY=${PY:-python}
SUITE=${SUITE:-fast}
OUT=${OUT:-test-results/$SUITE}
CAP=${CAP:-1200}
SLOW_CAP=${SLOW_CAP:-7200}
case "$SUITE" in
  fast) MARK='not slow'; RUN_CAP=$CAP; JOBS=${JOBS:-4}; UNIT=file ;;
  slow|integration) MARK=$SUITE; RUN_CAP=$SLOW_CAP; JOBS=${JOBS:-1}; UNIT=node ;;
  *) echo "SUITE must be fast, slow, or integration" >&2; exit 2 ;;
esac
export PYTHONHASHSEED=0 PYTHONIOENCODING=utf-8 PYTHONDONTWRITEBYTECODE=1
export OMP_NUM_THREADS=1 MKL_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1 NUMBA_NUM_THREADS=1
mkdir -p "$OUT/logs"
if [ $# -gt 0 ]; then files=("$@"); else files=(tests/core/test_*.py tests/sera/test_*.py); fi

if [ "$UNIT" = node ]; then
  # A per-file cap combines several full audits; collect first so every case gets its own budget.
  timeout -k 30 "$CAP" "$PY" -m pytest --collect-only -q --color=no -p no:cacheprovider -m "$MARK" "${files[@]}" \
    > "$OUT/collection.log" 2>&1
  rc=$?
  if [ "$rc" -ne 0 ] && [ "$rc" -ne 5 ]; then
    cat "$OUT/collection.log" >&2
    printf 'FAIL | collection for %s (exit %s)\n' "$SUITE" "$rc" > "$OUT/summary.txt"
    exit 1
  fi
  mapfile -t files < <(grep -E '^[^[:space:]]+\.py::' "$OUT/collection.log")
  if [ "${#files[@]}" -eq 0 ]; then
    if [ "$rc" -eq 5 ]; then
      printf '# %s suite: no selected tests\n' "$SUITE" > "$OUT/summary.txt"
      cat "$OUT/summary.txt"
      exit 0
    fi
    echo 'FAIL | collection succeeded but no node IDs were found' > "$OUT/summary.txt"
    cat "$OUT/summary.txt" >&2
    exit 1
  fi
fi

log_name() { printf '%s' "$1" | tr -c '[:alnum:]_.-' '_'; }

one() {   # one file/node -> one status line and its log
  f=$1; name=$(log_name "$f")
  t0=$(date +%s)
  timeout -k 30 "$RUN_CAP" "$PY" -m pytest -q -p no:cacheprovider -m "$MARK" --durations=0 "$f" \
    > "$OUT/logs/$name.log" 2>&1
  rc=$?; dt=$(( $(date +%s) - t0 ))
  case $rc in 0) st=PASS ;; 5) st=EMPTY ;; 124|137) st=TIMEOUT ;; *) st=FAIL ;; esac
  last=$(grep -E "(passed|failed|error|no tests ran)" "$OUT/logs/$name.log" | tail -1)
  printf '%-7s | %5d s | %s | %s\n' "$st" "$dt" "$f" "$last" > "$OUT/logs/$name.line"
  cat "$OUT/logs/$name.line"
}
export -f one log_name; export PY OUT RUN_CAP MARK

start=$(date +%s)
printf '%s\0' "${files[@]}" | xargs -0 -P "$JOBS" -I{} bash -c 'one "$@"' _ {}
lines=()
for f in "${files[@]}"; do lines+=("$OUT/logs/$(log_name "$f").line"); done
{
  echo "# $SUITE suite, one process per $UNIT (marker: $MARK, cap ${RUN_CAP} s, ${JOBS} at a time)"
  echo "# commit $(git rev-parse --short HEAD 2>/dev/null || cat COMMIT 2>/dev/null || echo unknown), $(date -u +%Y-%m-%dT%H:%MZ)"
  cat "${lines[@]}" | sort -t'|' -k3
  n=${#files[@]}
  bad=$(cat "${lines[@]}" | grep -c -E '^(FAIL|TIMEOUT)')
  echo "${UNIT}s: $n, failed or timed out: $bad, wall: $(( $(date +%s) - start )) s"
} > "$OUT/summary.txt"
cat "$OUT/summary.txt"
grep -q -E '^(FAIL|TIMEOUT)' "$OUT/summary.txt" && exit 1 || exit 0
