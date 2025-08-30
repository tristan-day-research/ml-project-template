#!/usr/bin/env bash
set -euo pipefail

# End-to-end sanity for ml-project-template
# - Scenario A: No mlcore (template runs standalone)
# - Scenario B: With local mlcore path

ROOT_DIR=$(cd "$(dirname "$0")/.." && pwd)
SANDBOX="$ROOT_DIR/.sandbox"
SAMPLE_A="$SANDBOX/sample_no_mlcore"
SAMPLE_B="$SANDBOX/sample_with_mlcore"

echo "[info] Using sandbox: $SANDBOX"
rm -rf "$SANDBOX"
mkdir -p "$SANDBOX"

have_uv=0
if command -v uv >/dev/null 2>&1; then
  have_uv=1
  echo "[info] Detected uv"
else
  echo "[info] uv not found; falling back to pip"
fi

install_project () {
  local proj_dir=$1
  pushd "$proj_dir" >/dev/null
  python -m pip install --upgrade pip >/dev/null
  if [ $have_uv -eq 1 ]; then
    uv pip install -e .
    uv pip install pytest
  else
    python -m pip install -e .
    python -m pip install pytest
  fi
  popd >/dev/null
}

run_tests () {
  local proj_dir=$1
  pushd "$proj_dir" >/dev/null
  pytest -q || { echo "[error] pytest failed"; exit 1; }
  popd >/dev/null
}

run_flow () {
  local proj_dir=$1
  pushd "$proj_dir" >/dev/null
  python - <<'PY'
import importlib.util
import os
from pathlib import Path

# Resolve package name from folder name
pkg = Path('.').resolve().name.replace('-', '_')

print('[info] Python:', os.sys.executable)
print('[info] Package:', pkg)

spec = importlib.util.find_spec('mlcore')
print('[info] mlcore found:', bool(spec))
if spec:
    print('[info] mlcore file:', spec.origin)

flow_mod = __import__(f"{pkg}.flows.train_eval", fromlist=['train_eval_flow'])
result = flow_mod.train_eval_flow()
print('[info] flow result:', result)
PY
  popd >/dev/null
}

echo "\n=== Scenario A: Generate without mlcore ==="
copier copy --defaults \
  --data project_name="Sample A" \
  --data use_prefect=true \
  --data use_pandera=false \
  --data python_version="3.11" \
  . "$SAMPLE_A"

install_project "$SAMPLE_A"
run_tests "$SAMPLE_A"
run_flow "$SAMPLE_A"

echo "\n=== Scenario B: Generate with local mlcore ==="
export MLCORE_LOCAL_PATH="$ROOT_DIR/ci/dummy-mlcore"
copier copy --defaults \
  --data project_name="Sample B" \
  --data use_prefect=true \
  --data use_pandera=false \
  --data python_version="3.11" \
  . "$SAMPLE_B"

install_project "$SAMPLE_B"
run_tests "$SAMPLE_B"
run_flow "$SAMPLE_B"

echo "\n[success] E2E sanity completed. See outputs above."

