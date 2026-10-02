#!/usr/bin/env bash
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../../.." && pwd)"
PROJECT="$ROOT/engineering-stories/02-one-intent-two-executions/reference-project"
WORK="${1:-$ROOT/generated/r2-g1}"

rm -rf "$WORK"
mkdir -p "$WORK/iiss" "$WORK/out"

orbitfabric export integration-input-set "$ROOT/mission" --output-dir "$WORK/iiss"
orbitfabric export scenario-declaration   "$PROJECT/scenario/r2_g0_health_check.yaml"   --json "$WORK/scenario_declaration.json"

python "$PROJECT/scripts/g1_projection.py"   --iiss-dir "$WORK/iiss"   --scenario-declaration "$WORK/scenario_declaration.json"   --output-dir "$WORK/out"   --verify-retained

python -m unittest discover   -s "$PROJECT/tests"   -p 'test_g1_projection.py'   -v
