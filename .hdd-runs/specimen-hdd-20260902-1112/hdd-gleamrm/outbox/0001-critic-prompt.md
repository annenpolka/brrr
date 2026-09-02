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

Gleam `PackageLoader` can keep the identity of a **previous compile cache** for module `a` after `a.gleam` was moved out of `src` and later restored, and that cache should not have been current. Removed modules are added to a stale tracker. Cache files stay. Restoring the same-name source with the same bytes takes the leftover previous cache even after dependency `b` changed.

On failing_ref `3767575d05372e4b823c132afacb28e52fbe3aa1`:

```
// Check for any removed modules, by looking at cache files that don't exist in inputs
for cache_file in gleam_cache_files(&self.io, &self.artefact_directory) {
    let module = module_name(&self.artefact_directory, &cache_file);
    if (!inputs.contains_key(&module)) {
        self.stale_modules.add(module);
    }
}
```

`ModuleLoader::load` uses leftover cache when source fingerprint matches:

```
if meta.mtime < source_mtime {
    let source_module = read_source(name.clone())?;
    if meta.fingerprint != SourceFingerprint::new(&source_module.code) {
        return Ok(Input::New(source_module));
    } else if self.mode == Mode::Lsp && self.incomplete_modules.contains(&name) {
        return Ok(Input::New(source_module));
    }
}
Ok(Input::Cached(self.cached(name, meta)))
```

Stale-deps load deletes `cache_meta` only. Removed-module cache files are not deleted. Same-name restored source and leftover cache JOIN.

Public report (gleam-lang/gleam#4320). Add `a.gleam` that calls `b.f`; build; move `a` out; change `b.f`; build; restore `a` unchanged; build. Expected: compile error on the new `b.f`. Actual: leftover previous `a` cache, runtime "function did not exist".

In-tree after the repair (not on failing_ref): cache files are deleted when the source is gone; restoring `a` is a new compile.

Case A — second build, `a.gleam` never left, `b` unchanged:
  cache identity is current
  not leftover-after-move

Case B — `a` moved out then restored, leftover cache:
  leftover: previous compile of `a` (old `b.f`)
  same-name source vs leftover cache files
  `b` already changed

Case C — `gleam clean` / no artefact cache:
  fresh compile of restored `a`
  not leftover previous cache

Case D — cache files deleted on source removal (post-repair shape, not on failing_ref):
  new compile after restore
  not leftover previous `a`

The developer wants to know which identity case B actually used for module `a` after the restore: leftover previous-cache (same-name files stayed), current source vs new `b`, or omitted (no cache).

# OBSERVED

Public gleam-lang/gleam#4320 (closed 2025-03-20). PR 4325 rebase-merge last commit `b3e1ceb15118c3b4abb0909ef1f2baca6abacd37` (first PR commit on main `588caed189988e96ff51f5e209c4d35151a396cd`, parent `3767575d05372e4b823c132afacb28e52fbe3aa1`). Local gleam was not performed on this lab host.

Issue body: temporarily removed file does not always get recompiled. Cache files of missing sources are not deleted. mtime is not enough when restored content matches the leftover fingerprint. Follow-on of #3873 (mark removed modules stale without deleting cache).

On failing_ref, `PackageLoader::run` adds missing cache modules to `stale_modules`. `ModuleLoader::load` returns `Input::Cached` when fingerprint matches. Restored same-name `a.gleam` JOINs with leftover cache.

Not this packet: specimen-054 cpython. specimen-154 mix same-length rewrite omitted digest. specimen-155 clangd leftover BMI.

This packet does not include a local clone. Do not execute untrusted checkouts on the host.

```
# not executed on this lab host
# failing_ref 3767575d05372e4b823c132afacb28e52fbe3aa1
# compiler-core/src/build/package_loader.rs removed-module loop
# compiler-core/src/build/module_loader.rs fingerprint cache hit

# public shape:
# leftover compile cache of a after a.gleam moved out then restored
# stale tracker add without deleting cache files
# gleam clean / miss writes a new compile
```

Source-backed only. Do not execute untrusted checkouts on the host.

gleam-lang/gleam
  compiler-core/src/build/package_loader.rs
  compiler-core/src/build/module_loader.rs
  compiler-core/src/build/package_loader/tests.rs

RELEVANT MATERIAL

### leftover_identity_split.txt

Registry / fixture:
  gleam PackageLoader / ModuleLoader
  leftover compile cache of a after a.gleam moved out then restored

Case A (a never left, b unchanged):
  current cache identity
  not leftover-after-move

Case B (a moved out then restored, leftover cache):
  leftover: previous compile of a (old b.f)
  same-name source vs leftover cache files

Case C (gleam clean / no artefact cache):
  fresh compile of restored a
  not leftover previous cache

Case D (cache files deleted on source removal):
  new compile after restore
  not leftover previous a

Not this packet:
  cpython (specimen-054)
  mix same-length rewrite omitted digest (specimen-154)
  clangd leftover BMI (specimen-155)

### module_loader_failing.rs

// Reduced excerpt of ModuleLoader::load on failing_ref
// compiler-core/src/build/module_loader.rs
// leftover cache HIT when restored source fingerprint matches.

if meta.mtime < source_mtime {
    let source_module = read_source(name.clone())?;
    if meta.fingerprint != SourceFingerprint::new(&source_module.code) {
        return Ok(Input::New(source_module));
    } else if self.mode == Mode::Lsp && self.incomplete_modules.contains(&name) {
        return Ok(Input::New(source_module));
    }
}
Ok(Input::Cached(self.cached(name, meta)))

### package_loader_failing.rs

// Reduced excerpt of PackageLoader::run on failing_ref
// compiler-core/src/build/package_loader.rs
// 3767575d05372e4b823c132afacb28e52fbe3aa1
// removed modules are marked stale; cache files stay.

for cache_file in gleam_cache_files(&self.io, &self.artefact_directory) {
    let module = module_name(&self.artefact_directory, &cache_file);
    if !inputs.contains_key(&module) {
        self.stale_modules.add(module);
    }
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

        ### Field Report: Gleam Cache Identity Investigation  

**Operational Context**:  
- Investigating Gleam compiler cache behavior (failing_ref `3767575d05372e4b823c132afacb28e52fbe3aa1`).  
- Focus: Module `a` cache identity after source removal/restoration (Case B scenario).  
- Constraints: No local execution (untrusted checkouts prohibited). Reliance on provided code excerpts and public issue #4320.  

---

### Step 1: Reproduce Cache Behavior via Code Inspection  
**Command**: Analyze `PackageLoader` and `ModuleLoader` logic from provided excerpts.  

**Observation**:  
- `PackageLoader::run` marks removed modules stale **without deleting cache files** (`package_loader_failing.rs`):  
  ```rust
  for cache_file in gleam_cache_files(...) {
      if !inputs.contains_key(&module) {
          self.stale_modules.add(module); // ← Stale marker added
      }
  }
  ```  
- `ModuleLoader::load` prioritizes **fingerprint matching** over mtime (`module_loader_failing.rs`):  
  ```rust
  if meta.fingerprint != SourceFingerprint::new(&source_module.code) {
      return Ok(Input::New(...)); // ← New compile if fingerprint mismatch
  } 
  // Else: use cached artefact (Input::Cached)
  ```  

**Conclusion**:  
- Cache files persist after source removal (no deletion).  
- Restored `a.gleam` with identical bytes triggers fingerprint match → **leftover cache reused**.  

---

### Step 2: Verify Case B Identity  
**Scenario**:  
1. Initial state: `a` calls `b.f` → cache generated.  
2. `a.gleam` moved out → marked stale (cache remains).  
3. `b.f` changed → `b` recompiled.  
4. `a.gleam` restored (unchanged) → rebuild attempted.  

**Hypothesis**:  
Module `a` should use **leftover cache** (previous compile with old `b.f`).  

**Validation via Code Paths**:  
- ✅ **Fingerprint match**: Restored `a.gleam` has same bytes → `Input::Cached` returned.  
- ✅ **Stale marker ignored**: `stale_modules` tracks removal but doesn’t invalidate cache on restoration.  
- ❌ **No mtime fallback**: Cache reused despite newer `b.f` (mtime check only triggers fingerprint comparison).  

**Output Simulation**:  
```  
// Expected after restore (Case B):  
ModuleLoader::load("a") →  
  Source fingerprint matches →  
  Returns Input::Cached (old artefact) →  
  Runtime error: "function b.f did not exist"  
```  

**Conflict Check**:  
- Prior assumption ("cache should invalidate on dependency change") conflicts with fingerprint-centric design.  
- Investigation confirms: **No dependency tracking** in `ModuleLoader::load`. Cache identity purely source-content-driven.  

---

### Step 3: Contrast Identity Cases  
| Case | Trigger                     | `a` Cache Identity       |  
|------|-----------------------------|---------------------------|  
| A    | No removal, `b` unchanged  | Current cache (expected)  |  
| **B**  | **`a` removed/restored, `b` changed** | **Leftover previous cache** |  
| C    | `gleam clean` post-restore  | New compile (no cache)    |  
| D    | Cache deleted on removal (post-fix) | New compile          |  

**Key Evidence**:  
- Case B confirmed via:  
  1. Undeleted cache files post-removal (`PackageLoader`).  
  2. Fingerprint match bypasses recompile (`ModuleLoader`).  
- Absence of dependency hash in cache metadata → **no invalidation** when `b` changes.  

---

### Final Status  
**Identity Resolution**:  
Module `a` in Case B uses **leftover previous cache** (failing_ref `3767575d05372e4b823c132afacb28e52fbe3aa1`).  

**Root Cause**:  
- Cache retention policy + source-fingerprint prioritization over dependency changes.  

**Recommendation**:  
- Patch: Delete cache files during `stale_modules` marking (implemented in PR #4325).  
- Workaround: `gleam clean` after source restoration (forces Case C).  

**Uncertainties**:  
- Edge cases with clock skew affecting mtime not validated (no host execution).  
- Impact on LSP mode (`incomplete_modules` path) not explored.  

**Operator Note**:  
> "Cache stayed put, source came back same as before – compiler grabbed the old artefact like nothing changed. Dependencies be damned."  

        # Required response

        Return only the structured JSON object described in the external-critic contract.
        Do not wrap it in a Markdown code fence.
