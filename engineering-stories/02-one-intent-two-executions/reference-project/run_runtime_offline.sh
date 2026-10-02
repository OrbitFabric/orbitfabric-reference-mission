#!/usr/bin/env bash
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../../.." && pwd)"
PROJECT="$ROOT/engineering-stories/02-one-intent-two-executions/reference-project"
WORK="${1:-$ROOT/generated/r2-runtime-offline}"

rm -rf "$WORK"
mkdir -p "$WORK"

python "$PROJECT/scripts/runtime_preflight.py"   --output-dir "$WORK"   --execution-attempt-id offline-preflight-not-run

python -m unittest discover   -s "$PROJECT/runtime-tests"   -p 'test_*.py'   -v
