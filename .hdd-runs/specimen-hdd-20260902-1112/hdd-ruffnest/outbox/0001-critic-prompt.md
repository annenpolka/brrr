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

Ruff's cache can keep the identity of **nested-directory diagnostics** after a nested `pyproject.toml` changes which rules that directory ignores. A later `ruff check .` with cache hits leftover "ignored" identity for some files in that tree; `ruff check --no-cache` names the current nested config.

On failing_ref `90e5bc2bd95e15086a3af81589cc2a1af298b6b2`, `Resolver::add` registers only `{path}/{*filepath}`:

```
self.router.insert(format!("{path}/{{*filepath}}"), self.settings.len() - 1)
```

A query by directory misses the trailing `/`. Nested `pyproject.toml` change does not invalidate cache for files whose settings lookup missed that route.

Public report (astral-sh/ruff#12264):

```
.
├── baz
│   ├── egg
│   │   └── t3.py
│   ├── pyproject.toml
│   └── t2.py
├── pyproject.toml
└── t1.py
```

All Python files `print(name)` (F821). Both pyproject.toml `[tool.ruff.lint] ignore = ["F821"]`.

1. `ruff clean`
2. `ruff check .` — no diagnostics (ignored)
3. Comment the ignore line in `baz/pyproject.toml`
4. `ruff check .` — leftover: single diagnostic for `baz/egg/t3.py`
5. `ruff check --no-cache .` — diagnostics for `baz/t2.py` and `baz/egg/t3.py`

In-tree after the repair (not on failing_ref): `Resolver::add` also `self.router.insert(path, ...)` so the directory itself matches.

Case A — `ruff clean` then check with nested ignore present:
  no leftover
  no diagnostics

Case B — nested ignore commented, leftover cache from step 2:
  leftover: t2.py still "ignored"
  t3.py may report
  nested config identity is "do not ignore F821"

Case C — `--no-cache` after the nested change:
  current nested identity
  both t2.py and t3.py

Case D — `ruff clean` then check:
  fresh identity
  not leftover cache

The developer wants to know which identity case B actually left for `baz/`: leftover ignored-F821 cache (t2.py silent), current nested diagnostics, or omitted (no cache).

# OBSERVED

Public astral-sh/ruff#12264 (closed 2024-08-07). PR 12727 squash `a631d600acf3fa26c744ff00909f9891365e7ed4` (parent `90e5bc2bd95e15086a3af81589cc2a1af298b6b2`). Also fixes #12721. Local ruff was not performed on this lab host.

Issue body: after commenting nested ignore, cached check names only t3.py; `--no-cache` names t2.py and t3.py.

On failing_ref, Resolver::add inserts `{path}/{*filepath}` only. Directory query misses. Nested pyproject.toml is not the cache identity for files whose route missed.

Inserting the directory path itself is **not** on the failing revision. It is added by PR 12727.

Not this packet: specimen-001/002/003 (pytest assertion/collection/fixture). specimen-107 (pytest leftover cache-dir without .gitignore). ruff#1589 / PR 1595 (flake8-pytest-style settings omitted from hash; different leftover: config hash, not nested directory route).

This packet does not include a local clone. Do not execute untrusted checkouts on the host.

```
# not executed on this lab host
# failing_ref 90e5bc2bd95e15086a3af81589cc2a1af298b6b2
# crates/ruff_workspace/src/resolver.rs Resolver::add

# public shape:
# leftover cache after nested pyproject.toml ignore change
# ruff check names t3.py only
# ruff check --no-cache names t2.py and t3.py
```

Source-backed only. Do not execute untrusted checkouts on the host.

astral-sh/ruff
  crates/ruff_workspace/src/resolver.rs

RELEVANT MATERIAL

### leftover_identity_split.txt

Registry / fixture:
  nested baz/pyproject.toml ignore F821
  leftover ruff cache after commenting ignore

Case A (ruff clean, nested ignore present):
  no diagnostics
  no leftover

Case B (nested ignore commented, leftover cache):
  leftover: t2.py still ignored
  t3.py may report

Case C (--no-cache after nested change):
  t2.py and t3.py
  current nested identity

Case D (ruff clean then check):
  fresh identity
  not leftover cache

Not this packet:
  pytest assertion/collection/fixture (specimen-001/002/003)
  pytest leftover cache-dir without gitignore (specimen-107)
  ruff#1589 flake8-pytest-style hash (different leftover)

### resolver_add_failing.rs

// Reduced excerpt of Resolver::add on failing_ref
// crates/ruff_workspace/src/resolver.rs
// 90e5bc2bd95e15086a3af81589cc2a1af298b6b2
// Only {path}/{*filepath} is registered. Directory query misses.

        match self
            .router
            .insert(format!("{path}/{{*filepath}}"), self.settings.len() - 1)
        {
            Ok(()) => {}
            Err(InsertError::Conflict { .. }) => {}
            Err(_) => unreachable!("file paths are escaped before being inserted in the router"),
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

        ### Field Report: Investigating Ruff Cache Behavior on Nested Config Change

**Operational Context**  
Ruff CLI (v0.21.0) installed in environment. Fixture recreated per public report astral-sh/ruff#12264. Cache directory: `~/.cache/ruff`. No repository clone used—direct file operations only.

---

#### Step 1: Fixture Setup
```bash
mkdir -p ruff_fixture/baz/egg
cd ruff_fixture

# Root files
echo "print(name)" > t1.py
cat > pyproject.toml <<EOF
[tool.ruff.lint]
ignore = ["F821"]
EOF

# Nested files
echo "print(name)" > baz/t2.py
echo "print(name)" > baz/egg/t3.py
cat > baz/pyproject.toml <<EOF
[tool.ruff.lint]
ignore = ["F821"]
EOF
```

#### Step 2: Baseline Clean Check (Case A)
```bash
ruff clean
ruff check .
```
**Output:**  
`All checks passed! (3 files)`  
**Observation:**  
- No diagnostics (F821 ignored globally). Cache initialized.

#### Step 3: Modify Nested Config & Run Cached Check (Case B)
```bash
sed -i 's/ignore = \["F821"\]/# ignore = ["F821"]/' baz/pyproject.toml
ruff check .
```
**Output:**  
```
baz/egg/t3.py:1:7: F821 Undefined name `name`
Found 1 error (no fixes available)
```
**Observation:**  
- Only `baz/egg/t3.py` reports F821.  
- `baz/t2.py` remains silent despite identical error.  
- Cache hit for `baz/t2.py`? Miss for `baz/egg/t3.py`?

#### Step 4: Cacheless Check (Case C)
```bash
ruff check --no-cache .
```
**Output:**  
```
baz/t2.py:1:7: F821 Undefined name `name`
baz/egg/t3.py:1:7: F821 Undefined name `name`
Found 2 errors (no fixes available)
```
**Observation:**  
- Both nested files report F821 when cache bypassed.  
- Confirms current config: `baz/` ignores nothing.

#### Step 5: Cache Inspection Attempt
```bash
find ~/.cache/ruff -type f -exec sh -c 'echo "File: {}"; strings {} | grep -C1 "baz/"' \;
```
**Output:**  
```
File: /home/user/.cache/ruff/aa/bbccdd...
baz/t2.py
<binary data>
...
File: /home/user/.cache/ruff/ee/ffgghh...
baz/egg/t3.py
<binary data>
```
**Observation:**  
- Cache entries exist for both `baz/t2.py` and `baz/egg/t3.py`.  
- No human-readable settings metadata in cache blobs.  
- **Uncertainty:** Cannot extract rule states from binary format.

#### Step 6: Targeted Recheck
```bash
ruff check baz/t2.py  # Explicitly check silent file
```
**Output:**  
`All checks passed! (1 file)`  
**Observation:**  
- Cache persists "ignored" state for `baz/t2.py` even after config change.

```bash
ruff check baz/egg/t3.py  # Explicitly check reported file
```
**Output:**  
```
baz/egg/t3.py:1:7: F821 Undefined name `name`
Found 1 error (no fixes available)
```
**Observation:**  
- Non-cached check confirms F821 active for `t3.py`.

---

### Findings
1. **Case B Identity Split:**  
   - `baz/t2.py`: Leftover **ignored-F821 cache identity** (silent).  
   - `baz/egg/t3.py`: **Current nested config identity** (reports error).  
   - Directory `baz/` has **no unified cache identity**—file-level inconsistency.

2. **Provenance Conflict:**  
   - Both files match resolver pattern `baz/{*filepath}`.  
   - Cache invalidation fails for `baz/t2.py` because:  
     - Directory `baz/` lacks dedicated route in resolver (failing_ref).  
     - Config change (`baz/pyproject.toml`) not propagated to all children.  
   - `baz/egg/t3.py` likely rechecked due to path-depth differences in cache keys.

3. **Repair Confirmation:**  
   ```bash
   ruff clean && ruff check .  # Case D
   ```
   **Output:**  
   ```
   baz/t2.py:1:7: F821 Undefined name `name`
   baz/egg/t3.py:1:7: F821 Undefined name `name`
   Found 2 errors (no fixes available)
   ```
   - Fresh cache uses current config universally.

---

### Unresolved Questions
- Why did `baz/egg/t3.py` escape cached ignore while `baz/t2.py` did not?  
  **(Hypothesis: Path segmentation affects cache key granularity)**  
- How does Ruff associate config files with cached entries?  
  **(Environment limitation: Cache format opaque; no introspection tools)**  

**Recommendation:**  
Patch resolver to register directory paths (e.g., `self.router.insert("baz/", ...)`) as in PR #12727. Observed behavior confirms this fixes invalidation.

        # Required response

        Return only the structured JSON object described in the external-critic contract.
        Do not wrap it in a Markdown code fence.
