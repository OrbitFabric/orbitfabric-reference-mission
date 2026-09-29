#!/usr/bin/env bash
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
SCENARIO="$ROOT/scenario/r2_g0_health_check.yaml"
DEFINITION="$ROOT/fixtures/experiment-definition.synthetic.json"
TOOL="$ROOT/scripts/g0_contracts.py"

if ! command -v orbitfabric >/dev/null 2>&1; then
  echo "orbitfabric CLI is required; install the repository-pinned Core baseline first" >&2
  exit 2
fi

tmpdir="$(mktemp -d)"
trap 'rm -rf "$tmpdir"' EXIT

declaration="$tmpdir/scenario-declaration.json"
materialized="$tmpdir/experiment-definition.synthetic.json"

orbitfabric export scenario-declaration "$SCENARIO" --json "$declaration"
python "$TOOL" materialize-definition \
  --scenario-declaration "$declaration" \
  --output "$materialized"

cmp "$materialized" "$DEFINITION"

python "$TOOL" verify-all \
  --scenario-declaration "$declaration" \
  --definition "$DEFINITION"

python -m unittest discover \
  -s "$ROOT/tests" \
  -p 'test_*.py' \
  -v

echo "[r2-g0] offline contract / identity proof PASS"
