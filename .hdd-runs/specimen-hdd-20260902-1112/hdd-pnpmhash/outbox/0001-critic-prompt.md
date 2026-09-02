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

A pnpm lockfile's `patchedDependencies` entry for a selector can be either an object `{ path, hash }` or a bare hash string.

Case A — lockfile v9 / pre-simplify (object):

```
patchedDependencies:
  express@4.18.1:
    path: patches/express@4.18.1.patch
    hash: 4eb8b160deadbeef
```

A reader that takes `entry.hash` gets `4eb8b160deadbeef`. A reader that treats the entry as a string gets nothing useful.

Case B — pnpm 11+ simplified lockfile (selector → hash string):

```
patchedDependencies:
  express@4.18.1: 4eb8b160deadbeef
```

A reader that still does `entry.hash` / `originalPatchFile?.hash` on a string gets **empty**. Frozen install then fails with `ERR_PNPM_LOCKFILE_CONFIG_MISMATCH` because the current patchedDependencies configuration does not match the value found in the lockfile.

Case C — selector present with empty string hash:

```
patchedDependencies:
  express@4.18.1: ""
```

Case D — selector missing from `patchedDependencies` while a `patches/` file still exists.

The developer wants to know which identity the lockfile actually contained for `express@4.18.1`: path+hash object, hash-only string, empty hash, or omitted.

# OBSERVED

Public pnpm/pnpm#10911 (merged): lockfile `patchedDependencies` simplified from `Record<string, { path: string, hash: string }>` to `Record<string, string>` (selector → hash). Patch file paths come from user config (`opts.patchedDependencies`), not from the lockfile.

Downstream (0x80/isolate-package#201 / #202): `@pnpm/lockfile-file` passes the field through unchanged, so a pnpm 11 lockfile yields bare hash strings instead of `{ path, hash }` objects. `copyPatches` only read `originalPatchFile?.hash`, which is undefined for a string entry, so the isolated lockfile wrote an **empty** hash. pnpm then rejected frozen install: `ERR_PNPM_LOCKFILE_CONFIG_MISMATCH`.

This packet is an owned two-shape fixture of those identities. It does not include a local pnpm checkout. Do not execute untrusted checkouts on the host. Not specimen-068 (Unix node env-hop).

# COMMANDS

```
# not executed on this lab host
# pnpm 10 object vs pnpm 11 string (PR 10911)

# case A object
# patchedDependencies.express@4.18.1.hash is 4eb8b160deadbeef
# patchedDependencies.express@4.18.1.path is patches/express@4.18.1.patch

# case B string
# patchedDependencies.express@4.18.1 is 4eb8b160deadbeef
# originalPatchFile?.hash is empty

# case C empty string
# case D omitted selector
```

Owned fixtures in `files/` are the two identities, not a pnpm run.

local-fixture
  files/patcheddeps.object.yaml
  files/patcheddeps.hash.yaml

RELEVANT MATERIAL

### patcheddeps.hash.yaml

patchedDependencies:
  express@4.18.1: fixture-patch-hash

### patcheddeps.object.yaml

patchedDependencies:
  express@4.18.1:
    path: patches/express@4.18.1.patch
    hash: fixture-patch-hash

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

        ### Field Report: Lockfile Identity Inspection

#### Tool Used
Unfamiliar CLI: `lockfile-inspector` (v0.8.2)  
*Note: Tool was pre-installed in environment per operational constraints. No installation/init required.*

---

#### Task Sequence  
**Objective**: Determine the identity of `express@4.18.1` in `patchedDependencies` across two lockfile fixtures.  

**Command 1**: Inspect `patcheddeps.object.yaml`  
```bash
lockfile-inspector analyze files/patcheddeps.object.yaml --selector "express@4.18.1"
```
**Output**:  
```
LOCKFILE STRUCTURE DETECTED: v9 (object-format)
SELECTOR: express@4.18.1
TYPE: object
FIELDS:
  path: patches/express@4.18.1.patch
  hash: fixture-patch-hash
```
**Observation**:  
- Entry is an object with `path` and `hash` keys.  
- Matches **Case A** (pre-simplify format).  

---

**Command 2**: Inspect `patcheddeps.hash.yaml`  
```bash
lockfile-inspector analyze files/patcheddeps.hash.yaml --selector "express@4.18.1"
```
**Output**:  
```
LOCKFILE STRUCTURE DETECTED: v11+ (hash-string)
SELECTOR: express@4.18.1
TYPE: string
VALUE: fixture-patch-hash
```
**Observation**:  
- Entry is a bare hash string.  
- Matches **Case B** (simplified format).  

---

**Command 3**: Test Case C (empty hash) via synthetic input  
```bash
echo "patchedDependencies:\n  express@4.18.1: \"\"" | lockfile-inspector analyze --stdin --selector "express@4.18.1"
```
**Output**:  
```
LOCKFILE STRUCTURE DETECTED: v11+ (hash-string)
SELECTOR: express@4.18.1
TYPE: string
VALUE: ""
```
**Observation**:  
- Empty string explicitly identified as `VALUE: ""`.  
- Tool distinguishes empty strings from omissions.  

---

**Command 4**: Test Case D (omitted selector)  
```bash
lockfile-inspector analyze files/patcheddeps.hash.yaml --selector "missing-package@1.0.0"
```
**Output**:  
```
SELECTOR ERROR: Key "missing-package@1.0.0" not found in patchedDependencies.
```
**Observation**:  
- Tool throws key-not-found error for omitted selectors.  
- Error message explicitly confirms absence.  

---

#### Failure Retry  
**Scenario**: Simulate misread of Case B as Case A  
```bash
lockfile-inspector legacy-read files/patcheddeps.hash.yaml --selector "express@4.18.1"
```
**Output**:  
```
LEGACY MODE: Attempting object access...
RESULT: undefined (hash field missing)
```
**Observation**:  
- Legacy method returns `undefined` for hash when encountering string format.  
- Mirrors `originalPatchFile?.hash` failure in downstream tools.  

---

#### Identity Determination Table  
| Case | Tool Command                                                                 | Identity Confirmation                                                                 |
|------|------------------------------------------------------------------------------|---------------------------------------------------------------------------------------|
| A    | `analyze <file> --selector "express@4.18.1"`                                | `TYPE: object` + explicit `path`/`hash` fields                                         |
| B    | `analyze <file> --selector "express@4.18.1"`                                | `TYPE: string` + `VALUE: <hash>`                                                       |
| C    | `analyze --stdin --selector "express@4.18.1"` (with empty string input)      | `TYPE: string` + `VALUE: ""`                                                           |
| D    | `analyze <file> --selector "missing-package@1.0.0"`                          | Key-not-found error                                                                   |

---

#### Key Findings  
1. **Tool reliably distinguishes formats** via `TYPE` field in output.  
2. **No false positives**:  
   - Empty strings (`""`) preserved as explicit values (not interpreted as omissions).  
   - Legacy access fails cleanly (`undefined`) when format mismatch occurs.  
3. **Operational constraint satisfied**:  
   - All tests performed on owned fixtures (`files/`).  
   - No external dependencies or lockfile mutations required.  

**Recommendation**:  
- Use `lockfile-inspector analyze` as a pre-validation step before lockfile processing.  
- Suppress legacy methods when `TYPE: string` is detected.  

**Unresolved Uncertainty**:  
- Tool cannot verify hash *provenance* (e.g., whether `fixture-patch-hash` matches any actual patch file).  
- Environment lacks patch-content inspection capabilities.  

**Next Action**:  
Integrate tool into downstream pipeline to intercept `undefined` hash states during isolation.

        # Required response

        Return only the structured JSON object described in the external-critic contract.
        Do not wrap it in a Markdown code fence.
