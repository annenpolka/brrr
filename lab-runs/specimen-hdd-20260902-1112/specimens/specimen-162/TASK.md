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
