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

Spack `concretizer:concretization_cache` can keep the identity of a **previous spec hash** after a `package.py` change should have been a different dag_hash. The cache stores fully-finalized specs (hashes baked in). On a cache hit, `_finalize_concretization` / package-hash post-processing is omitted, so leftover `mo2ogtq` is reused after commenting `install()` in bzip2.

On failing_ref `194e0da658190ae0219bd9576bd7ce1099ce1e0b`:

```
cache_key = self._make_cache_key(problem, control_file_paths)
if conc_cache_enabled and self._conc_cache:
    result, concretization_stats = self._conc_cache.fetch(cache_key)
if not result:
    result = self._run_clingo(...)
    self._conc_cache.store(cache_key, result, self.control.statistics)
# later, on the stored Result:
root._finalize_concretization()
```

`_make_cache_key` hashes ASP problem + control files. Cached `Result.to_dict()` already has concrete hashes. Cache hit skips re-finalization.

Public report (spack/spack#51553). `spack spec -l bzip2` with cache on; edit package.py; leftover previous hash until cache disabled.

In-tree after the repair (not on failing_ref): cache write immediately after solve, before finalization; cache hits re-run `post_process_concretization_result()`.

Case A — second `spack spec` with unchanged package.py:
  cache identity is current
  not leftover-after-package-change

Case B — package.py flipped, leftover concretizer cache:
  leftover: previous dag_hash / fully-finalized spec
  package-hash recompute omitted on cache hit
  same `mo2ogtq`

Case C — cache disabled / `spack clean -m`:
  fresh hash identity
  not leftover previous spec

Case D — cache stores pre-finalization, re-finalize on hit (post-repair shape, not on failing_ref):
  cache miss / new hash after package.py change
  not leftover previous dag_hash

The developer wants to know which identity case B actually used for the spec hash after the package.py change: leftover previous-finalized results (re-finalization omitted), current package identity, or omitted (no cache).

# OBSERVED

Public spack/spack#51553 (closed 2026-06-16). PR 51931 merge `525775aa9b3e9500f661508456902c7634c23655` (parent `194e0da658190ae0219bd9576bd7ce1099ce1e0b`). Local spack was not performed on this lab host.

Issue body: concretizer cache returns previous bzip2 hash after package.py install() comment; disabling the cache yields a new hash.

On failing_ref, cache stores the Result after the solve and later finalizes hashes into that object. Cache hits reuse leftover finalized hashes. PR 51931 moves the store before finalization and re-runs post-processing on hits.

Not this packet: specimen-136 pants leftover process cache vs git hash. specimen-140 rush leftover downstream phase vs operation graph.

This packet does not include a local clone. Do not execute untrusted checkouts on the host.

```
# not executed on this lab host
# failing_ref 194e0da658190ae0219bd9576bd7ce1099ce1e0b
# lib/spack/spack/solver/asp.py PyclingoDriver cache store / _make_cache_key

# public shape:
# leftover concretizer cache after package.py change
# fully-finalized spec hashes stored; re-finalization omitted on hit
# spack spec -l bzip2 keeps previous dag_hash until cache off
```

Source-backed only. Do not execute untrusted checkouts on the host.

spack/spack
  lib/spack/spack/solver/asp.py
  repos/spack_repo/builtin/packages/bzip2/package.py

RELEVANT MATERIAL

### asp_cache_failing.py

# Reduced excerpt of PyclingoDriver solve cache on failing_ref
# lib/spack/spack/solver/asp.py
# 194e0da658190ae0219bd9576bd7ce1099ce1e0b
# Stores Result after clingo; later _finalize_concretization bakes hashes.
# Cache hit reuses leftover finalized hashes. package.py recompute omitted.

cache_key = self._make_cache_key(problem, control_file_paths)
result, concretization_stats = None, None
if conc_cache_enabled and self._conc_cache:
    result, concretization_stats = self._conc_cache.fetch(cache_key)
if not result:
    result = self._run_clingo(specs, setup, problem_repr, control_file_paths, timer)
    self._conc_cache.store(cache_key, result, self.control.statistics)
# later on Result specs:
#   root._finalize_concretization()
# cache hit skips that recompute

### leftover_identity_split.txt

Registry / fixture:
  concretizer:concretization_cache enable
  leftover spec hash after package.py change

Case A (second spack spec, same package.py):
  current cache identity
  not leftover-after-package-change

Case B (package.py flipped, leftover cache):
  leftover: previous dag_hash / fully-finalized spec
  package-hash recompute omitted on cache hit
  same mo2ogtq

Case C (cache disabled / spack clean -m):
  fresh hash identity
  not leftover previous spec

Case D (store before finalization, re-finalize on hit):
  new hash after package.py change
  not leftover previous dag_hash

Not this packet:
  pants leftover vcs_version process cache (specimen-136)
  rush leftover downstream phase cache (specimen-140)

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

        ### Field Report: Investigating Concretizer Cache Behavior

**Environment Setup and Initial State Verification**  
Confirmed the environment has the failing Spack version (commit `194e0da658190ae0219bd9576bd7ce1099ce1e0b`) via the `spack` CLI:

```bash
$ spack --version
> 0.23.0-194e0da658
```

Enabled the concretizer cache and initialized a test workspace:

```bash
$ spack config add 'concretizer:concretization_cache:true'
$ spack clean --all
$ mkdir -p ./test_env && cd ./test_env
```

---

### Step 1: Baseline Concretization of `bzip2`  
Ran initial concretization to populate the cache:

```bash
$ spack spec -l bzip2
Input spec
--------------------------------
bzip2

Concretized
--------------------------------
bzip2@1.0.8%apple-clang@15.0.0 arch=darwin-ventura-m1  mo2ogtq3k[...]
```

Recorded initial hash: `mo2ogtq`

---

### Step 2: Modify `bzip2/package.py`  
Edited `package.py` to comment out `install()` (using CLI to simulate change):

```bash
$ sed -i '' 's/def install(/& # Commented for test/' repos/spack_repo/builtin/packages/bzip2/package.py
```

Verified the modification:

```bash
$ grep -A2 'install(' repos/spack_repo/builtin/packages/bzip2/package.py
>     def install( # Commented for test
>         self, spec, prefix
>     ):
```

---

### Step 3: Re-run Concretization (Cache Hit Scenario)  
Re-ran `spack spec` without clearing the cache:

```bash
$ spack spec -l bzip2
Input spec
--------------------------------
bzip2

Concretized
--------------------------------
bzip2@1.0.8%apple-clang@15.0.0 arch=darwin-ventura-m1  mo2ogtq3k[...]
```

**Observation:** The hash remains `mo2ogtq` despite `install()` modification. Cache hit reused the previous finalized spec.

---

### Step 4: Disable Cache and Rerun  
Cleared cache and re-concretized:

```bash
$ spack clean -m
$ spack spec -l bzip2
Input spec
--------------------------------
bzip2

Concretized
--------------------------------
bzip2@1.0.8%apple-clang@15.0.0 arch=darwin-ventura-m1  xyzabcde2[...]
```

**Observation:** Fresh hash `xyzabcde` generated. Cache miss triggered full recomputation.

---

### Step 5: Verify Cache Behavior Consistency  
Re-ran with cache enabled but no package changes (Case A):

```bash
$ spack spec -l bzip2
> [...] xyzabcde2[...]  # Matches Step 4 hash
```

**Observation:** Current package identity used correctly when cache is valid.

---

### Conflict Resolution: Source Code Alignment  
Compared environment behavior against supplied `asp_cache_failing.py` excerpt. Confirmed:

1. Cache stores **post-finalization specs** (hashes baked in)
2. Cache hits skip `_finalize_concretization`
3. Package hash recomputation is omitted during hits

```python
# Excerpt validation (alignment with observed behavior):
if cache_hit:
   use_cached_finalized_spec()  # ← omits package-hash recompute
else:
   solve_and_finalize()
```

---

### Conclusion: Case B Identity Provenance  
**Answer to developer query:**  
In Case B (package.py modified, stale cache), the concretizer uses the **leftover previous-finalized spec hash** (`mo2ogtq`). This occurs because:

1. Cache returns a fully finalized spec (with pre-modification hash)
2. `_finalize_concretization` is skipped during cache hits
3. Package-specific recomputation (including new `package.py` hashes) is omitted

The identity is **not** derived from current package state or omitted—it is the literal cached artifact. This matches the public report (spack/spack#51553) and fixture's `leftover_identity_split.txt` Case B description.

**Recommendation:**  
Cache keys should incorporate package hashes or cache storage should occur pre-finalization (as implemented in post-repair versions).

        # Required response

        Return only the structured JSON object described in the external-critic contract.
        Do not wrap it in a Markdown code fence.
