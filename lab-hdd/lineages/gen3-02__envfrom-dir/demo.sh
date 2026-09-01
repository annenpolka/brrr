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

echo
echo "=== --dir reads that tree, not cwd ==="
WORKDIR="$(mktemp -d)"
mkdir "$WORKDIR/here" "$WORKDIR/there"
printf 'FOO=from-here\n' > "$WORKDIR/here/.env"
printf 'FOO=from-there\n' > "$WORKDIR/there/.env"
(cd "$WORKDIR/here" && python3 "$ENVFROM" FOO)
(cd "$WORKDIR/here" && python3 "$ENVFROM" --dir "$WORKDIR/there" FOO)
rm -rf "$WORKDIR"

echo
echo "=== missing --dir (expect exit 1, not SOURCE: env) ==="
set +e
python3 "$ENVFROM" --dir /no/such/envfrom-dir PATH
echo "exit=$?"
set -e

echo
echo "=== UTF-8 BOM keeps FOO; invalid UTF-8 exits 1 without traceback ==="
BOMDIR="$(mktemp -d)"
printf '\xef\xbb\xbfFOO=bom\r\nexport BAR\r\nBAZ=ok\r\n' > "$BOMDIR/.env"
python3 "$ENVFROM" --dir "$BOMDIR" FOO BAR BAZ
printf 'FOO=ok\nBAR=\xff\xfe\x00notutf8\nBAZ=1\n' > "$BOMDIR/.env"
set +e
python3 "$ENVFROM" --dir "$BOMDIR" FOO
echo "exit=$?"
set -e
rm -rf "$BOMDIR"
