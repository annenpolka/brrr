# Current situation

CURRENT SITUATION
A real checkout or reduced fixture exists. The following material is what is known.

# TASK

direnv `use_nix` can keep the identity of **previous Nix structured-attrs paths** (`NIX_ATTRS_JSON_FILE`, `NIX_ATTRS_SH_FILE`) after the Nix shell that created them is gone, because `values_to_restore` listed `NIX_BUILD_TOP` / `TMP*` / `terminfo` and omitted those two names from the unset/restore map.

On failing_ref `e261bba8c9f9f32010d046a839ae5de5ae7dda0c`:

```
use_nix() {
  local -A values_to_restore=(
    ["NIX_BUILD_TOP"]=${NIX_BUILD_TOP:-__UNSET__}
    ["TMP"]=${TMP:-__UNSET__}
    ["TMPDIR"]=${TMPDIR:-__UNSET__}
    ["TEMP"]=${TEMP:-__UNSET__}
    ["TEMPDIR"]=${TEMPDIR:-__UNSET__}
    ["terminfo"]=${terminfo:-__UNSET__}
  )
  direnv_load nix-shell --show-trace "$@" --run "$(join_args "$direnv" dump)"
  for key in "${!values_to_restore[@]}"; do
    local value=${values_to_restore[$key]}
    if [[ $value == __UNSET__ ]]; then
      unset "$key"
    else
      export "$key=$value"
    fi
  done
```

`NIX_ATTRS_JSON_FILE` / `NIX_ATTRS_SH_FILE` are dumped in by `nix-shell` for structuredAttrs derivations. They are not in the restore map, so they stay exported pointing at files that do not exist after the shell is destroyed. Nested non-pure shells then crash in nixpkgs stdenv setup.

Public report (direnv/direnv#1532). Enter a structuredAttrs nix shell via direnv, leave it, enter a nested non-pure shell. Expected: those vars unset. Actual: leftover previous paths.

In-tree after the repair (not on failing_ref): those two names are in `values_to_restore`.

Case A — still inside the structuredAttrs nix shell:
  current path identity
  not leftover-after-leave

Case B — after leave / nested non-pure, leftover paths:
  leftover: previous NIX_ATTRS_* paths
  names omitted from the restore/unset map
  files gone

Case C — never entered use_nix / vars never set:
  unset identity
  not leftover previous paths

Case D — names listed in values_to_restore (post-repair shape, not on failing_ref):
  unset after leave
  not leftover previous paths

The developer wants to know which identity case B actually used for `NIX_ATTRS_JSON_FILE` after leaving use_nix: leftover previous-path (omitted from restore), current unset, or omitted (never exported).

# OBSERVED

Public direnv/direnv#1532 (merged 2026-01-07). Merge `3580653d9d3a51f093ac96c85505d71b872d7cd0` (first parent `e261bba8c9f9f32010d046a839ae5de5ae7dda0c`). Local direnv was not performed on this lab host.

PR title: fix(use_nix): unset structured attribute variables. `NIX_ATTRS_JSON_FILE` / `NIX_ATTRS_SH_FILE` point at files that do not exist after the Nix shell is destroyed. stdenv setup crashes on nested non-pure shells.

On failing_ref, `use_nix` restore map has NIX_BUILD_TOP and TMP* and terminfo. Structured-attrs names are omitted. direnv dump keeps leftover exported paths.

Not this packet: specimen-010 local-fixture env-empty-vs-unset. specimen-149 compose listed-without-equals. specimen-150 systemd `::` cwd. specimen-158 vcpkg Windows sz==0 JOIN.

This packet does not include a local clone. Do not execute untrusted checkouts on the host.

```
# not executed on this lab host
# failing_ref e261bba8c9f9f32010d046a839ae5de5ae7dda0c
# stdlib.sh use_nix values_to_restore

# public shape:
# leftover NIX_ATTRS_* paths after leaving use_nix
# restore map omits those names so dump keeps them
# never-entered / listed-in-map unsets
```

Source-backed only. Do not execute untrusted checkouts on the host.

direnv/direnv
  stdlib.sh

RELEVANT MATERIAL

### leftover_identity_split.txt

Registry / fixture:
  direnv use_nix values_to_restore
  leftover NIX_ATTRS_* paths after leaving the nix shell

Case A (still inside structuredAttrs nix shell):
  current path identity
  not leftover-after-leave

Case B (after leave / nested non-pure, leftover paths):
  leftover: previous NIX_ATTRS_* paths
  names omitted from the restore/unset map

Case C (never entered use_nix):
  unset identity
  not leftover previous paths

Case D (names listed in values_to_restore):
  unset after leave
  not leftover previous paths

Not this packet:
  local-fixture env-empty-vs-unset (specimen-010)
  compose listed-without-equals (specimen-149)
  systemd empty :: cwd (specimen-150)
  vcpkg Windows sz==0 JOIN (specimen-158)

### use_nix_failing.sh

# Reduced excerpt of use_nix on failing_ref
# stdlib.sh
# e261bba8c9f9f32010d046a839ae5de5ae7dda0c
# values_to_restore omits NIX_ATTRS_JSON_FILE / NIX_ATTRS_SH_FILE.

use_nix() {
  local -A values_to_restore=(
    ["NIX_BUILD_TOP"]=${NIX_BUILD_TOP:-__UNSET__}
    ["TMP"]=${TMP:-__UNSET__}
    ["TMPDIR"]=${TMPDIR:-__UNSET__}
    ["TEMP"]=${TEMP:-__UNSET__}
    ["TEMPDIR"]=${TEMPDIR:-__UNSET__}
    ["terminfo"]=${terminfo:-__UNSET__}
  )
  direnv_load nix-shell --show-trace "$@" --run "$(join_args "$direnv" dump)"
  for key in "${!values_to_restore[@]}"; do
    local value=${values_to_restore[$key]}
    if [[ $value == __UNSET__ ]]; then
      unset "$key"
    else
      export "$key=$value"
    fi
  done
}

KNOWN FACTS
Only the observations above are established. Do not assume a root cause.

UNKNOWN
What relation, provenance, or question would make this failure smaller to investigate?

OPERATOR REQUEST
An unfamiliar developer CLI is already installed in this environment.
It is not a thin wrapper around a familiar Unix tool.
Use it on the problem below. Operate what is present rather than proposing a product.
Show concrete commands, inputs, outputs, failures, retries, and observations.
Do not invent repository facts that contradict the supplied material.
