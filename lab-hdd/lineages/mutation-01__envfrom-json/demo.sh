#!/usr/bin/env bash
# Real demo: file empty override vs inherited process env.
set -euo pipefail
ROOT="$(cd "$(dirname "$0")" && pwd)"
ENVFROM="$ROOT/envfrom"
FIX="$ROOT/fixtures/empty-override"

export LIBRARY_PATH="/usr/local/lib:/usr/lib"
export APP_ENV="from-shell"

echo "=== envfrom LIBRARY_PATH APP_ENV PATH NOT_A_REAL_VAR ==="
python3 "$ENVFROM" --dir "$FIX" LIBRARY_PATH APP_ENV PATH NOT_A_REAL_VAR

echo
echo "=== --fail-empty LIBRARY_PATH (expect exit 2) ==="
set +e
python3 "$ENVFROM" --dir "$FIX" --fail-empty LIBRARY_PATH
echo "exit=$?"
set -e

echo
echo "=== --run without --load: child keeps inherited LIBRARY_PATH ==="
python3 "$ENVFROM" --dir "$FIX" --run -- python3 -c 'import os; print("child LIBRARY_PATH=" + os.environ.get("LIBRARY_PATH", "(unset)"))'

echo
echo "=== --run --load: child sees file empty override ==="
python3 "$ENVFROM" --dir "$FIX" --run --load -- python3 -c 'import os; print("child LIBRARY_PATH=" + repr(os.environ.get("LIBRARY_PATH"))); print("child APP_ENV=" + os.environ.get("APP_ENV", "(unset)"))'

echo
echo "=== --json LIBRARY_PATH APP_ENV NOT_A_REAL_VAR ==="
python3 "$ENVFROM" --json --dir "$FIX" LIBRARY_PATH APP_ENV NOT_A_REAL_VAR

QUOTE="$ROOT/fixtures/quoted-export"
echo
echo "=== quoted values, inline comments, export PREFIX ==="
python3 "$ENVFROM" --dir "$QUOTE" PREFIX GREETING NAME COLOR EMPTY_QUOTED HASH_IN_QUOTES

echo
echo "=== --json quoted-export ==="
python3 "$ENVFROM" --json --dir "$QUOTE" PREFIX GREETING NAME COLOR EMPTY_QUOTED HASH_IN_QUOTES
