#!/usr/bin/env bash
# Run tagjoin on omitempty vs listMapKey fixtures (specimen-052 shape + unseen).
set -euo pipefail

ROOT="$(cd "$(dirname "$0")" && pwd)"
CLI="$ROOT/tagjoin"

candidate_roots() {
  local top common parent abs
  top="$(git -C "$1" rev-parse --show-toplevel 2>/dev/null || true)"
  [ -n "$top" ] && printf '%s\n' "$top"
  common="$(git -C "$1" rev-parse --git-common-dir 2>/dev/null || true)"
  if [ -n "$common" ]; then
    case "$common" in
      /*) abs="$common" ;;
      *) abs="$(cd "$1" && cd "$common" && pwd)" ;;
    esac
    parent="$(cd "$abs/.." && pwd)"
    printf '%s\n' "$parent"
  fi
}

find_specimen() {
  if [ -n "${SPECIMEN:-}" ] && [ -f "$SPECIMEN/files/types_excerpt.go" ]; then
    printf '%s\n' "$SPECIMEN"
    return 0
  fi
  local root cand
  while IFS= read -r root; do
    [ -z "$root" ] && continue
    cand="$root/lab-runs/specimen-hdd-20260902-1112/specimens/specimen-052"
    if [ -f "$cand/files/types_excerpt.go" ]; then
      printf '%s\n' "$cand"
      return 0
    fi
  done < <(candidate_roots "$ROOT"; candidate_roots "$(pwd)")
  return 1
}

SPECIMEN="$(find_specimen || true)"
EXCERPT="$ROOT/fixtures/excerpt.go"
if [ -n "${SPECIMEN:-}" ] && [ -f "$SPECIMEN/files/types_excerpt.go" ]; then
  EXCERPT="$SPECIMEN/files/types_excerpt.go"
fi

if [ ! -x "$CLI" ]; then
  chmod +x "$CLI"
fi
if [ ! -f "$CLI" ]; then
  echo "demo.sh: missing CLI at $CLI" >&2
  exit 1
fi

echo "== nearest existing: grep omitempty / listMapKey / +optional =="
grep -nE 'omitempty|listMapKey|\+optional' "$ROOT/fixtures/052-types.go" || true
echo "(hits both tags; does not name which identity key is optional)"
echo

echo "== tagjoin owned wrapped fixture (specimen-052 shape) =="
python3 "$CLI" "$ROOT/fixtures/052-types.go"
echo

echo "== tagjoin excerpt $EXCERPT =="
python3 "$CLI" "$EXCERPT"
echo

echo "== tagjoin unseen Ports / containerPort =="
python3 "$CLI" "$ROOT/fixtures/unseen-ports.go"
echo

echo "== tagjoin agree (required name key, list still omitempty) =="
python3 "$CLI" "$ROOT/fixtures/agree-name.go"
echo

echo "== tagjoin json empty name omitempty (not agree) =="
python3 "$CLI" "$ROOT/fixtures/empty-json-name.go"
echo

echo "== tagjoin json address vs listMapKey=ip (missing, not HostAlias.IP) =="
python3 "$CLI" "$ROOT/fixtures/wrong-wire.go"
echo

echo "== tagjoin duplicate +listMapKey (disagree_n 1) =="
python3 "$CLI" "$ROOT/fixtures/dup-listmapkey.go"
echo

echo "== tagjoin YAML OpenAPI-ish x-kubernetes-list-map-keys =="
python3 "$CLI" "$ROOT/fixtures/crd-list-map.yaml"
echo

echo "== tagjoin YAML description |- then list-map keys =="
python3 "$CLI" "$ROOT/fixtures/crd-block-scalar.yaml"
echo

echo "== tagjoin YAML versions: sequence CRD =="
python3 "$CLI" "$ROOT/fixtures/crd-versions.yaml"
echo

echo "== tagjoin JSON OpenAPI list-map keys =="
python3 "$CLI" "$ROOT/fixtures/crd-list-map.json"
echo

echo "== tagjoin FILE.go FILE.yaml (documented order) =="
python3 "$CLI" "$ROOT/fixtures/052-types.go" "$ROOT/fixtures/crd-list-map.yaml"
echo

echo "== tagjoin spaces around +listMapKey = =="
python3 "$CLI" "$ROOT/fixtures/spaces-eq.go"
echo

echo "== tagjoin json:,inline embed (HostAlias.IP, not missing) =="
python3 "$CLI" "$ROOT/fixtures/embed-inline.go"
echo

echo "== tagjoin untagged list field =="
python3 "$CLI" "$ROOT/fixtures/untagged-list.go"
echo

echo "== tagjoin duplicate type HostAlias (collision, not last-wins) =="
python3 "$CLI" "$ROOT/fixtures/dup-type.go"
echo

echo "== tagjoin UTF-8 BOM (agree Item.Name, not join none) =="
python3 "$CLI" "$ROOT/fixtures/bom.go"
echo

echo "== tagjoin --check owned fixture (disagree → rc 1) =="
rc=0
python3 "$CLI" --check "$ROOT/fixtures/052-types.go" || rc=$?
echo "rc=$rc"
