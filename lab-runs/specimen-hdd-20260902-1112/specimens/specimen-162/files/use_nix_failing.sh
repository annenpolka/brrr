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
