### Field Report: Investigating Structured Attributes Variable Retention in `use_nix`

**Operational Context**:  
Examining direnv's `use_nix` behavior on failing_ref `e261bba8c9f9f32010d046a839ae5de5ae7dda0c` regarding `NIX_ATTRS_JSON_FILE` retention after shell exit. No local execution performed per security constraints.

---

#### Step 1: Inspect `values_to_restore` Map
```bash
# Extract values_to_restore definition from failing_ref
grep -A10 'local -A values_to_restore' stdlib.sh
```
**Output**:  
```
local -A values_to_restore=(
  ["NIX_BUILD_TOP"]=${NIX_BUILD_TOP:-__UNSET__}
  ["TMP"]=${TMP:-__UNSET__}
  ["TMPDIR"]=${TMPDIR:-__UNSET__}
  ["TEMP"]=${TEMP:-__UNSET__}
  ["TEMPDIR"]=${TEMPDIR:-__UNSET__}
  ["terminfo"]=${terminfo:-__UNSET__}
)
```
**Observation**:  
`NIX_ATTRS_JSON_FILE`/`NIX_ATTRS_SH_FILE` absent from restoration map. Confirmed omission matches public report.

---

#### Step 2: Trace Variable Lifecycle
**Hypothesis**:  
If structured-attrs variables persist post-shell exit, they must be:  
1. Set during `nix-shell` execution  
2. Omitted from restoration logic  
3. Left exported after `direnv_load`

**Validation via Code Path**:  
```bash
# Follow direnv_load call sequence
direnv_load nix-shell ... --run "$(join_args "$direnv" dump)"
```
**Mechanism**:  
1. `nix-shell` sets `NIX_ATTRS_*` to temporary paths  
2. `direnv dump` captures *all* exported variables  
3. Restoration loop *only* processes `values_to_restore` keys  
4. Non-listed variables (incl. `NIX_ATTRS_*`) remain set  

---

#### Step 3: Identity Analysis for Case B
**Observed State Transitions**:  
| Phase                | `NIX_ATTRS_JSON_FILE` State       |
|----------------------|-----------------------------------|
| Pre-use_nix          | Unset (Case C) or external value |
| During nix-shell     | Valid temporary path (Case A)     |
| Post-use_nix cleanup | **Leftover path** (Case B)        |

**Key Evidence**:  
- Restoration loop explicitly skips non-`values_to_restore` variables  
- No unset/export actions occur for `NIX_ATTRS_*` in failing_ref  
- Public bug confirms variables retain invalid paths post-exit  

**Conclusion for Case B Identity**:  
`NIX_ATTRS_JSON_FILE` exhibits **leftover previous-path identity** due to:  
1. Omission from restoration map  
2. Absence of explicit unset logic  
3. Persistent export state after temporary file deletion  

---

#### Failure Impact Confirmation
**Reported Symptom Verification**:  
Nested non-pure shells fail because:  
1. `NIX_ATTRS_*` point to deleted files  
2. stdenv attempts to access invalid paths  
3. Crash occurs during environment setup  

**Consistency Check**:  
Case D (post-repair) resolves this by adding:  
```bash
["NIX_ATTRS_JSON_FILE"]=${NIX_ATTRS_JSON_FILE:-__UNSET__}
["NIX_ATTRS_SH_FILE"]=${NIX_ATTRS_SH_FILE:-__UNSET__}
```
to `values_to_restore`, forcing post-exit unset.

---

**Final Determination**:  
The failing_ref behavior (Case B) uses **leftover previous-path identity** for structured attributes variables. This results from direnv's selective restoration mechanism preserving non-map variables indefinitely, regardless of path validity. The merged fix corrects this by treating `NIX_ATTRS_*` as transient session state.
