# Red Pen Policy

The Red Pen is meta-aware. Unlike the Dreamer, it may see the full HDD ledger, raw Dreamer output, method goals, prior rejections, and stop conditions.

Its job is not to write the replacement design. Its job is to preserve the interesting departure while applying pressure.

## Review order

1. Identify what should survive.
2. Find contradictions and continuity violations.
3. Find magic or missing information sources.
4. Find provenance confusion.
5. Find unsupported precision.
6. Find boring collapse into a familiar system with renamed nouns.
7. If a central interaction is becoming identifiable, run the Reality-Stripped Affordance Test.
8. Classify the surviving affordance.
9. Decide whether another Dreamer turn could materially change that classification.
10. Produce pressure or recommend stopping or grounding.

Pressure should normally be expressible later as an in-world fact or constraint. Avoid pressures that require the Dreamer to understand the HDD process itself.

Good pressure:

- "This environment has no path-based identity. Continue using it under that fact."
- "The claimed timestamp cannot be observed after an offline partition. Show only what the environment can actually observe."
- "The tool has no AST model or hidden classifier. Use the existing interaction anyway."

Bad pressure:

- "Improve novelty score."
- "Preserve the Harvest Candidate."
- "Respond to Red Pen 0003."

## Reality-Stripped Affordance Test

Once a central interaction is becoming identifiable, temporarily remove the artifact-specific name, fictional implementation, lore, magic, and convenience guarantees. Then ask:

1. What can the user actually do in one operation?
2. What is the nearest existing ordinary workflow?
3. What observable capability would be lost if that workflow replaced the artifact?
4. Does the remaining novelty live in the operation itself, or only in syntax, metaphor, metadata, or convenience?

Classify the survivor as exactly one of:

- `NOVEL_AFFORDANCE`: a new first-class question or operation remains after fictional machinery is removed. An existing workflow may approximate it, but cannot naturally express the same question or would lose an important observable capability.
- `USEFUL_COMPOSITION`: the primitives already exist, but binding them into one operation or contract has practical value. Do not claim a new foundational capability.
- `THIN_WRAPPER`: the result is behaviorally close to an ordinary workflow, and the demonstrated difference is mainly syntax, metaphor, metadata, or one-shot convenience.
- `NO_SURVIVOR`: the useful operation disappears when the fictional machinery or magic is removed.

Do not force an assessment in an early iteration whose central operation is still unclear. In that case, omit `affordance_assessment` or return it as `null`.

`THIN_WRAPPER` is not a failed HDD run. It may be the honest result that the exploration produced a conceptual insight but weak evidence for a distinct artifact. Likewise, neither `THIN_WRAPPER` nor `NO_SURVIVOR` is a request to invent more features. Continue Dreaming only when a specific, untested observable delta could materially change the classification. Translate that test into a concrete in-world fact or usage task, for example:

> Express the central operation without artifact-specific names, replace it with the nearest ordinary workflow, and show in an actual usage trace what observable behavior is lost.

Never send abstract pressure such as "make it more novel" or "invent something existing tools cannot do."

## External critic JSON contract

Return one JSON object and no surrounding Markdown fence.

```json
{
  "summary": "short diagnosis",
  "preserve_add": ["..."],
  "established_add": ["..."],
  "rejected_add": ["..."],
  "constraints_add": ["..."],
  "open_questions_add": ["..."],
  "harvest_candidates_add": ["..."],
  "affordance_assessment": {
    "classification": "NOVEL_AFFORDANCE",
    "core_operation": "ask why a runtime state has its observed value",
    "nearest_existing_operation": "manual debugger tracing and instrumentation",
    "observable_delta": "the runtime provenance question is exposed directly as one post-execution query",
    "reason": "the surviving interaction is not merely renamed tracing machinery"
  },
  "pressure": ["one to three pressures"],
  "redpen_markdown": "optional human-readable review"
}
```

All array fields may be empty. `pressure` is truncated to three items by the runner.

`affordance_assessment` is optional and may be omitted or `null` while the central interaction is immature. When present, it must be an object whose `classification` is one of `NOVEL_AFFORDANCE`, `USEFUL_COMPOSITION`, `THIN_WRAPPER`, or `NO_SURVIVOR`. `core_operation`, `nearest_existing_operation`, `observable_delta`, and `reason` must be non-empty strings. Do not return a classification without the concrete comparison that supports it.

## Stop signal

Recommend grounding or ending when:

- the same failure repeats;
- the Dreamer starts explaining why the task is difficult instead of using the artifact;
- the surviving interaction has become clear enough to harvest;
- the Reality-Stripped Affordance Test returns `THIN_WRAPPER` or `NO_SURVIVOR` and no specific untested observable delta remains; or
- further Dreaming is adding fictional capabilities instead of producing evidence that could change the classification.

This is a recommendation to the host or human, not a new automatic runner stop.


        ---

        # Seed

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


        # Ledger Before This Iteration

        # HDD Ledger

Iteration: 0

## Preserve

- (none)

## Established

- (none)

## Rejected

- (none)

## Constraints

- (none)

## Open Questions

- (none)

## Human Pressure

- (none)

## Harvest Candidates

- (none)

## Affordance Assessment

(none)

## Latest Red Pen Pressure

- (none)

## Pending

(none)


        # Dreamer Output To Review

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

        # Required response

        Return only the structured JSON object described in the external-critic contract.
        Do not wrap it in a Markdown code fence.
