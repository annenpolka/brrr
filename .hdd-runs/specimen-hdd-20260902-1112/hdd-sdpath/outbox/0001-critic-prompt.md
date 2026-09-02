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

systemd `get_paths_from_environ` can keep the identity of the **current working directory** as a unit search path after `SYSTEMD_UNIT_PATH` listed an empty `::` component and that listing should not have been a path. Unset, empty `""`, trailing `:`, and middle `::` are different identities. Empty components other than a trailing `:` are split into leftover `""` entries; `path_split_and_make_absolute` turns those into leftover cwd `.`.

On failing_ref `cad2c455ec1acff29a81421c58adbe0ffc191f65`:

```
static int get_paths_from_environ(const char *var, char ***ret) {
        const char *e;
        int r;

        e = getenv(var);
        if (!e) {
                *ret = NULL;
                return 0;
        }

        bool append = endswith(e, ":"); /* Whether to append the normal search paths after what's obtained
                                           from envvar */

        /* FIXME: empty components in other places should be rejected. */

        r = path_split_and_make_absolute(e, ret);
        if (r < 0)
                return r;

        return append;
}
```

`getenv` missing (`!e`) is unset. `e` pointing at `""` is empty-string. Trailing `:` means append built-in defaults. Middle `::` is not trailing-append. The FIXME is unenforced. Empty components become leftover cwd search-path identity.

Public PR (systemd/systemd#43355). Tests after the repair: unset → default search path; `""` → empty search path; `:` → same as unset (append defaults); `:foo` and `/foo::/bar` → EINVAL; trailing `/foo:` → `/foo` plus defaults.

In-tree after the repair (not on failing_ref): `path_is_valid_search_path` requires `isempty(path) || (isempty(startswith(path, ":")) && !strstr(path, "::"))`. Leading/middle empty is `-EINVAL`. Generator path parse errors propagate instead of becoming leftover empty generator paths.

Case A — `SYSTEMD_UNIT_PATH` unset:
  default search-path identity
  not leftover-cwd

Case B — `SYSTEMD_UNIT_PATH=/foo::/bar`, leftover empty component:
  leftover: cwd `.` as a search path
  empty `::` component split then made absolute
  same process lookup

Case C — `SYSTEMD_UNIT_PATH=""` (set, empty string):
  empty search path
  not leftover cwd; not default path

Case D — `SYSTEMD_UNIT_PATH=/foo:` (trailing colon):
  `/foo` plus built-in defaults
  not leftover cwd

Case E — leading/middle empty rejected (post-repair shape, not on failing_ref):
  EINVAL
  not leftover cwd search path

The developer wants to know which identity case B actually used for the unit search path after `::`: leftover cwd `.` (empty component made absolute), current listed directories only, empty search path, or omitted (defaults).

# OBSERVED

Public systemd/systemd#43355 (merged 2026-08-13). Squash `f4284e9cebac67ad7af3bc27b736cf1107b88127` (parent `cad2c455ec1acff29a81421c58adbe0ffc191f65`). Follow-up for `cf7d80a5fe549d4db11800015e02220dccec3096` (SYSTEMD_UNIT_PATH colon-separated prepend/append). Local systemd was not performed on this lab host.

PR title: path-lookup: reject empty env path components. Only trailing empty components have special meaning: they request appending the built-in defaults. Share validation between path lookup and systemd-analyze verify.

On failing_ref, `get_paths_from_environ` documents the FIXME and still splits empty components. Unset vs empty `""` vs `:` vs `::` are different getenv identities; empty components become leftover cwd.

Not this packet: specimen-010 local-fixture env-empty-vs-unset. specimen-031 pip empty-override. compose leftover listed-without-equals vs image ENV (packed this tick as leftover empty-vs-unset environment, not PATH cwd).

This packet does not include a local clone. Do not execute untrusted checkouts on the host.

```
# not executed on this lab host
# failing_ref cad2c455ec1acff29a81421c58adbe0ffc191f65
# src/libsystemd/sd-path/path-lookup.c get_paths_from_environ

# public shape:
# leftover cwd search path after SYSTEMD_UNIT_PATH=/foo::/bar
# unset is default path; "" is empty path; trailing : appends defaults
# new process / EINVAL after repair does not keep leftover cwd
```

Source-backed only. Do not execute untrusted checkouts on the host.

systemd/systemd
  src/libsystemd/sd-path/path-lookup.c
  src/test/test-path-lookup.c
  src/analyze/analyze-verify-util.c

RELEVANT MATERIAL

### leftover_identity_split.txt

Registry / fixture:
  systemd get_paths_from_environ SYSTEMD_UNIT_PATH
  leftover cwd search path after empty :: component

Case A (unset SYSTEMD_UNIT_PATH):
  default search-path identity
  not leftover-cwd

Case B (/foo::/bar, leftover empty component):
  leftover: cwd . as a search path
  empty :: split then made absolute

Case C ("" empty string):
  empty search path
  not leftover cwd; not default path

Case D (/foo: trailing colon):
  /foo plus built-in defaults
  not leftover cwd

Case E (leading/middle empty rejected):
  EINVAL
  not leftover cwd search path

Not this packet:
  local-fixture env-empty-vs-unset (specimen-010)
  pip empty user proxy vs global (specimen-031)
  compose leftover listed-without-equals vs image ENV (this-tick compose packet)

### path_lookup_failing.c

/* Reduced excerpt of get_paths_from_environ on failing_ref
 * src/libsystemd/sd-path/path-lookup.c
 * cad2c455ec1acff29a81421c58adbe0ffc191f65
 * empty :: components are split then made absolute as leftover cwd.
 */

static int get_paths_from_environ(const char *var, char ***ret) {
        const char *e;
        int r;

        e = getenv(var);
        if (!e) {
                *ret = NULL;
                return 0;
        }

        bool append = endswith(e, ":");

        /* FIXME: empty components in other places should be rejected. */

        r = path_split_and_make_absolute(e, ret);
        if (r < 0)
                return r;

        return append;
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

        ### Field Report: Investigating SYSTEMD_UNIT_PATH Identity Case B  

**Tool:** `path-behavior-analyzer` (v0.8.3) – Pre-installed CLI for environment variable path resolution diagnostics.  

---

#### **Step 1: Initialize analysis context**  
```bash
$ path-behavior-analyzer init --ref=cad2c455ec1acff29a81421c58adbe0ffc191f65 --function=get_paths_from_environ  
[✓] Context loaded:  
    - Target: libsystemd/sd-path/path-lookup.c  
    - Failing_ref: cad2c455ec1acff29a81421c58adbe0ffc191f65  
    - Known constraint: Empty non-trailing components become absolute cwd (.)  
```

#### **Step 2: Simulate Case B (`/foo::/bar`)**  
```bash
$ path-behavior-analyzer simulate-env SYSTEMD_UNIT_PATH=/foo::/bar --phase=split  
[OUTPUT]  
● getenv("SYSTEMD_UNIT_PATH") → "/foo::/bar"  
● endswith(e, ":") → false (no append)  
● path_split_and_make_absolute("/foo::/bar") → ["/foo", ".", "/bar"]  
  │  
  └── Empty component "" → resolved to cwd "." (via path_split_and_make_absolute)  
```

#### **Step 3: Verify path resolution identity**  
```bash
$ path-behavior-analyzer resolve-identity . --context=search_path  
[OUTPUT]  
● Identity type: leftover_cwd  
● Provenance: Empty component in envvar (non-trailing)  
● Absolute path: /proc/self/cwd/. (symbolic → current working directory)  
● Search path effect: Units searched in:  
   [0]: /foo  
   [1]: . (cwd)  
   [2]: /bar  
```

#### **Step 4: Contrast with other cases**  
```bash
$ path-behavior-analyzer compare --cases=unset,empty,trailing  
[OUTPUT]  
┌──────────┬──────────────┬──────────────────────┬─────────────────────────────┐  
│ Case     │ Env Value    │ Search Path          │ Identity                   │  
├──────────┼──────────────┼──────────────────────┼─────────────────────────────┤  
│ unset    │ (null)       │ ["/lib/systemd", ...]│ default                    │  
│ empty    │ ""           │ []                   │ explicit_empty             │  
│ trailing │ "/foo:"      │ ["/foo"] + defaults  │ append_defaults            │  
│ B (::)   │ "/foo::/bar" │ ["/foo", ".", "/bar"]│ leftover_cwd (non-trailing)│  
└──────────┴──────────────┴──────────────────────┴─────────────────────────────┘  
```

#### **Step 5: Validate against FIXME annotation**  
```bash
$ path-behavior-analyzer annotate --line=fixme  
[OUTPUT]  
● src/libsystemd/sd-path/path-lookup.c:14  
  /* FIXME: empty components in other places should be rejected. */  
● Current behavior (failing_ref):  
  - Empty components permitted → resolve to cwd "."  
  - Conflict: Trailing ":" triggers append, middle "::" triggers leftover cwd  
● Post-repair (PR#43355): Middle "::" → EINVAL (no cwd resolution)  
```

---

### **Observed Conclusions**  
1. **Case B Identity** (`SYSTEMD_UNIT_PATH=/foo::/bar`):  
   - Empty `::` component resolves to **leftover cwd `.`**  
   - Mechanism: `path_split_and_make_absolute` converts `""` → absolute cwd path  
   - Search path: Explicit list `["/foo", ".", "/bar"]` (no defaults appended)  

2. **Key Conflict**:  
   - Trailing `:` (e.g., `/foo:`) → *appends* defaults  
   - Middle `::` → *inserts* cwd as path entry  
   - Root cause: `endswith(":", e)` check only handles *terminals*, not intermediates  

3. **Unrepaired Behavior**:  
   - `get_paths_from_environ` treats unset, `""`, `:`, and `::` as 4 distinct states  
   - Empty components leak cwd into search path (violates path sanitation)  

---

### **Recommended Next Action**  
```bash  
$ path-behavior-analyzer generate-test --case=mid_empty_component  
[✓] Test case emitted:  
    test_get_paths_from_environ_middle_empty() {  
        assert_env SYSTEMD_UNIT_PATH=/foo::/bar → search_path == ["/foo", ".", "/bar"];  
        assert_env SYSTEMD_UNIT_PATH=:: → search_path == [".", "."];  
    }  
```  
**Rationale**: Confirms pre-repair behavior where middle `::` always materializes as cwd `.` entries.

        # Required response

        Return only the structured JSON object described in the external-critic contract.
        Do not wrap it in a Markdown code fence.
