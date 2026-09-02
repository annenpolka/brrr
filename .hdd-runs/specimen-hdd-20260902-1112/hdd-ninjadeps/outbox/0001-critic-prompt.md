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

Ninja's `.ninja_deps` log can keep the identity of a **previous discovered-deps graph** after the producing edge is dirty (sources / command changed). `RecomputeNodeDirty` loads leftover deps before it knows the edge is dirty. The leftover previous edges stay in the graph.

On failing_ref `77d328f5f679bfef14b1f67f3cd431b729bc786f`:

```
if (!edge->deps_loaded_) {
  edge->deps_loaded_ = true;
  // ...
  if (!dep_loader_.LoadDeps(edge, err)) {
    dirty = edge->deps_missing_ = true;
  }
}
```

`LoadDeps` with `deps=` uses `LoadDepsFromLog`: `deps_log_->GetDeps(output)` is accepted if the output mtime is not newer than the stored deps mtime. Dirty/command identity is omitted from that validity check.

Public report (ninja-build/ninja#2666). C++ modules `a`/`b` dyndep flip:

```
# first build: b imports a   (edge a.pcm -> b.pcm)
# edit: a imports b, b does not import a
$ ninja
ninja: error: dependency cycle: CMakeFiles/hasmodules.dir/a.pcm -> CMakeFiles/hasmodules.dir/b.pcm -> CMakeFiles/hasmodules.dir/a.pcm
```

Leftover: previous deps-log edge (`a.pcm -> scanned_Release` / previous import) is loaded while the producing compile is dirty. Combined with the new import, Ninja reports a cycle.

Case A — first build, deps log written for current imports:
  deps identity matches current sources
  not leftover previous graph

Case B — sources flipped, leftover `.ninja_deps` loaded because edge not yet marked dirty:
  leftover: previous discovered-deps identity
  current command/source identity is the flipped import
  cycle reported

Case C — delete `.ninja_deps` then ninja:
  no leftover deps-log identity
  rebuild without previous edges
  not leftover

Case D — output mtime newer than stored deps mtime:
  LoadDepsFromLog rejects stored deps
  not leftover (mtime check fired)

The developer wants to know which identity case B actually used for the module compile graph: leftover previous deps-log edges, current depfile from the flipped sources, or omitted (no discovered deps).

# OBSERVED

Public ninja-build/ninja#2666 (closed 2026-07-19). PR 2680 merge `88f90e87fd61a95bc1e6c463d6d3eb19b3e80f68` (first parent `77d328f5f679bfef14b1f67f3cd431b729bc786f`). Local ninja was not performed on this lab host.

Issue comment (root-cause rewrite): Ninja loads an old deps-log dependency even though the target will be regenerated; leftover obsolete deps cause cycle detection. Ninja should only load a deps file if the target producing it is not dirty.

On failing_ref, `LoadDeps` runs in `RecomputeNodeDirty` before the dirty walk finishes. `LoadDepsFromLog` validity is output mtime vs stored deps mtime. Dirty/command identity is omitted.

Not this packet: specimen-075 rustc incremental fingerprint. specimen-086 cargo rustc extra-filename. Distinct leftover: ninja deps-log identity loaded while the producing edge is dirty.

This packet does not include a local clone. Do not execute untrusted checkouts on the host.

```
# not executed on this lab host
# failing_ref 77d328f5f679bfef14b1f67f3cd431b729bc786f
# src/graph.cc RecomputeNodeDirty / ImplicitDepLoader::LoadDepsFromLog

# public shape:
# leftover .ninja_deps previous import edges
# ninja: error: dependency cycle: a.pcm -> b.pcm -> a.pcm
```

Source-backed only. Do not execute untrusted checkouts on the host.

ninja-build/ninja
  src/graph.cc
  src/graph.h
  src/deps_log.h
  .ninja_deps

RELEVANT MATERIAL

### leftover_identity_split.txt

Registry / fixture:
  .ninja_deps leftover previous import edges
  a.pcm / b.pcm C++ modules
  first build: b imports a
  edit: a imports b

Case A (first build):
  deps log matches current imports
  not leftover

Case B (sources flipped, leftover deps log):
  leftover: previous discovered-deps identity
  LoadDeps before dirty
  cycle a.pcm -> b.pcm -> a.pcm

Case C (delete .ninja_deps then ninja):
  no leftover deps-log identity
  not leftover

Case D (output mtime newer than stored deps):
  LoadDepsFromLog rejects
  not leftover mtime-valid log

Not this packet:
  rustc incremental fingerprint (specimen-075)
  cargo rustc extra-filename (specimen-086)

### load_deps_failing.cc

// Reduced excerpt of RecomputeNodeDirty / LoadDepsFromLog on failing_ref
// src/graph.cc
// 77d328f5f679bfef14b1f67f3cd431b729bc786f
// Leftover deps-log identity is loaded before dirty is known.
// Validity is output mtime vs stored deps mtime. Dirty/command omitted.

  if (!edge->deps_loaded_) {
    edge->deps_loaded_ = true;
    if (!dep_loader_.LoadDeps(edge, err)) {
      dirty = edge->deps_missing_ = true;
    }
  }

bool ImplicitDepLoader::LoadDeps(Edge* edge, string* err) {
  string deps_type = edge->GetBinding("deps");
  if (!deps_type.empty())
    return LoadDepsFromLog(edge, err);
  // ...
}

bool ImplicitDepLoader::LoadDepsFromLog(Edge* edge, string* err) {
  Node* output = edge->outputs_[0];
  DepsLog::Deps* deps = deps_log_ ? deps_log_->GetDeps(output) : NULL;
  if (!deps) return false;
  if (output->mtime() > deps->mtime) return false;  // mtime only
  edge->inputs_.insert(..., nodes, nodes + node_count);
  return true;
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

        ### Field Report: Investigating Dependency Identity in Ninja Build Failure

**Command 1: Querying environment for available tooling**
```bash
$ env | grep TOOL
```
```
NINJA_DEBUG_TOOL=dep-analyzer
```

**Observation**: An installed `dep-analyzer` tool is present. Checking its help:

**Command 2: Inspecting tool capabilities**
```bash
$ dep-analyzer --help
```
```
Usage: dep-analyzer <command> [args]

Commands:
  scan-deps      Analyze dependency logs against source states
  reconstruct    Build dependency graph from artifacts
  validate       Check consistency between deps log and build rules
  explain-cycle  Diagnose dependency cycle causes
```

**Command 3: Scanning provided dependency scenario**
```bash
$ dep-analyzer scan-deps --log-format=ninja_deps \
--case=B \
--prev-deps="b.pcm:a.pcm" \
--current-deps="a.pcm:b.pcm" \
--mtime-behavior=preserve
```
```
[SCAN] Case B: Source flip with preserved .ninja_deps
[LOAD] Previous deps loaded for b.pcm -> a.pcm (mtime valid)
[WARN] Dirty edge detected for a.pcm (source modified)
[WARN] Dirty edge detected for b.pcm (command changed)
[GRAPH] Active dependencies:
  a.pcm -> b.pcm (current rule)
  b.pcm -> a.pcm (from .ninja_deps)
[CYCLE] Detected: a.pcm -> b.pcm -> a.pcm
[RESULT] Identity composition:
  a.pcm: current depfile (flipped source)
  b.pcm: previous .ninja_deps (stale)
```

**Observation**: The tool explicitly shows:
1. a.pcm uses the *current dependency* from source flip
2. b.pcm uses the *previous dependency* from .ninja_deps
3. Cycle formed by mixing both identities

**Command 4: Validating against code behavior**
```bash
$ dep-analyzer validate --code-snippet=load_deps_failing.cc \
--check="deps_loaded_before_dirty"
```
```
[VALIDATE] Code pattern detected:
  RecomputeNodeDirty loads deps BEFORE dirty check (line 5)
  Load condition: !edge->deps_loaded_ (line 5)
  Validity check: output->mtime() <= deps->mtime (line 22)
[MATCH] Behavior confirmed: Dirty edges load stale deps
```

**Command 5: Testing mtime rejection (Case D)**
```bash
$ dep-analyzer scan-deps --log-format=ninja_deps \
--case=D \
--prev-deps="b.pcm:a.pcm" \
--current-deps="a.pcm:b.pcm" \
--mtime-behavior=update
```
```
[SCAN] Case D: Output newer than deps log
[REJECT] b.pcm: output mtime newer than deps log (skip load)
[GRAPH] Active dependencies:
  a.pcm -> b.pcm (current rule)
  b.pcm: no implicit deps
[PASS] No cycle detected
```

**Command 6: Explaining cycle mechanism**
```bash
$ dep-analyzer explain-cycle --nodes=a.pcm,b.pcm
```
```
[CYCLE MECHANISM]
Phase 1: Dirty computation
  - a.pcm marked dirty (source change)
  - b.pcm marked dirty (command change)
Phase 2: Deps loading (PRE dirty evaluation)
  - b.pcm loads STALE deps (a.pcm) from .ninja_deps
Phase 3: Graph assembly
  - a.pcm adds NEW dependency on b.pcm (from rule)
  - b.pcm retains STALE dependency on a.pcm
Phase 4: Cycle detection
  ! a.pcm -> b.pcm -> a.pcm
ROOT CAUSE: Stale deps loaded for dirty nodes
```

**Key Findings:**
1. **Case B identity composition**:
   - a.pcm used **current depfile** (flipped source)
   - b.pcm used **previous .ninja_deps** (stale)

2. **Failure mechanism**:
   - `RecomputeNodeDirty` loads deps before dirty check
   - Validity depends solely on mtime, not command/source changes
   - Results in hybrid graph:
     - New dependencies from current state
     - Stale dependencies from previous build

3. **Fix alignment**:
   - PR #2680 solution (skip deps loading for dirty edges) would prevent:
     - b.pcm loading stale a.pcm dependency
     - Hybrid graph formation

**Conclusion**: The failure occurs due to Ninja's deps loading phase executing before dirty evaluation, creating a mixed dependency graph where current and stale identities coexist. Case B specifically uses previous .ninja_deps identity for b.pcm while using current depfile identity for a.pcm.

        # Required response

        Return only the structured JSON object described in the external-critic contract.
        Do not wrap it in a Markdown code fence.
