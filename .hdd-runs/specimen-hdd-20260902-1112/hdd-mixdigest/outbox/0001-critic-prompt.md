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

Mix `Mix.Compilers.Elixir` can keep the identity of a **previous BEAM compile** after a same-length source rewrite and the modules should have been different. The source record stores `size` not a content digest. Stale detection is `size != last_size` or `Mix.Utils.stale?([last_mtime | times], [modified])`. A same-length rewrite whose mtime is reset (future-mtime warning) keeps leftover previous modules.

On failing_ref `a677d3c9efb32fe435d8fd102eb8f90272e14da1`:

```
defrecord :source,
  source: nil,
  size: 0,
  compile_references: [],
  ...

changed =
  for source(source: source, external: external, size: size, modules: modules) <-
        all_sources,
      {last_mtime, last_size} = Map.fetch!(sources_stats, source),
      times = Enum.map(external, &(sources_stats |> Map.fetch!(&1) |> elem(0))),
      size != last_size or Mix.Utils.stale?([last_mtime | times], [modified]) or
        Enum.any?(modules, &Map.has_key?(modules_to_recompile, &1)),
      do: source
```

Source identity is size+mtime, not bytes. Future mtimes are reset to now; then last_mtime is not stale vs the compile timestamp and size still matches.

Public report (elixir-lang/elixir#11080). Same-length rewrite (`A` → `Z`); leftover previous compile. In-tree after the repair: source record has `digest`; same-length content change recompiles; identical files with bumped mtime do not.

Case A — second compile, same bytes, same size:
  cache identity is current
  not leftover-after-rewrite

Case B — same-length rewrite, leftover BEAM:
  leftover: previous modules
  digest omitted; size matches
  future-mtime reset defeats mtime check

Case C — mix clean / forced compile:
  fresh module identity
  not leftover previous BEAM

Case D — digest on the source record (post-repair shape, not on failing_ref):
  new compile after same-length rewrite
  not leftover previous modules

The developer wants to know which identity case B actually used for the compile after the rewrite: leftover previous-BEAM (digest omitted), current source bytes, or omitted (no compile cache).

# OBSERVED

Public elixir-lang/elixir#11080 (merged 2021-06-28). Squash `350a909eb195ab1c0bc5ad29b7573c36ebd98377` (parent `a677d3c9efb32fe435d8fd102eb8f90272e14da1`). Local elixir/mix was not performed on this lab host.

PR body: hashing content is the right check; tests were added for same-length content change vs identical files with bumped mtime.

On failing_ref, the source record has size not digest. Stale detection is size inequality or Mix.Utils.stale? on mtimes. Same-length rewrite can keep leftover previous modules.

Not this packet: specimen-054 cpython generated-header drift. specimen-086 cargo rustc fingerprint clamped mtime. specimen-147 CDK truncated mtime fingerprint.

This packet does not include a local clone. Do not execute untrusted checkouts on the host.

```
# not executed on this lab host
# failing_ref a677d3c9efb32fe435d8fd102eb8f90272e14da1
# lib/mix/lib/mix/compilers/elixir.ex source record / changed

# public shape:
# leftover BEAM after same-length source rewrite
# source record has size not digest
# mix clean / digest in record yields the new modules
```

Source-backed only. Do not execute untrusted checkouts on the host.

elixir-lang/elixir
  lib/mix/lib/mix/compilers/elixir.ex

RELEVANT MATERIAL

### elixir_compile_failing.ex

# Reduced excerpt of Mix.Compilers.Elixir stale check on failing_ref
# lib/mix/lib/mix/compilers/elixir.ex
# a677d3c9efb32fe435d8fd102eb8f90272e14da1
# source record has size not digest.

defrecord :source, source: nil, size: 0, modules: []

changed =
  for source(source: source, size: size, modules: modules) <- all_sources,
      {last_mtime, last_size} = Map.fetch!(sources_stats, source),
      size != last_size or Mix.Utils.stale?([last_mtime | times], [modified]) or
        Enum.any?(modules, &Map.has_key?(modules_to_recompile, &1)),
      do: source
# leftover previous BEAM after same-length rewrite

### leftover_identity_split.txt

Registry / fixture:
  Mix.Compilers.Elixir source record
  leftover BEAM after same-length rewrite

Case A (second compile, same bytes):
  current cache identity
  not leftover-after-rewrite

Case B (same-length rewrite, leftover BEAM):
  leftover: previous modules
  digest omitted; size matches
  future-mtime reset defeats mtime check

Case C (mix clean):
  fresh module identity
  not leftover previous BEAM

Case D (digest on source record):
  new compile after same-length rewrite
  not leftover previous modules

Not this packet:
  cpython generated-header drift (specimen-054)
  cargo rustc fingerprint clamped mtime (specimen-086)

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

        ### Field Report: Investigating Elixir Compiler Identity Case B  

**Tool Environment:**  
- Active CLI: `mix_analyzer` (version 1.3.2)  
- Mode: Static code analysis (no execution of untrusted checkouts)  
- Loaded artifacts:  
  - `elixir_compile_failing.ex` (excerpt from failing_ref)  
  - `leftover_identity_split.txt` (case definitions)  

---

#### Step 1: Inspect Stale Detection Logic  
**Command:**  
```bash  
mix_analyzer parse-condition --file elixir_compile_failing.ex --line 5  
```  
**Output:**  
```  
Condition:  
  (size != last_size)  
  OR Mix.Utils.stale?([last_mtime | times], [modified])  
  OR Enum.any?(modules, &Map.has_key?(modules_to_recompile, &1))  
```  
**Observation:**  
The condition depends on three mutually reinforcing checks:  
1. Source `size` change  
2. File mtime freshness  
3. Dependency recompilation flags  

---

#### Step 2: Simulate Case B Parameters  
**Command:**  
```bash  
mix_analyzer simulate-case \  
  --case B \  
  --size 100 \  
  --last_size 100 \  
  --last_mtime "2021-06-01T10:00:00Z" \  
  --modified "2021-06-01T10:00:00Z" \  # Reset future mtime → now  
  --modules_to_recompile "[]"  
```  
**Output:**  
```  
[OUTCOME]  
- Size check: MATCH (100 == 100) → false  
- Mtime check: Mix.Utils.stale?([2021-06-01T10:00:00Z], [2021-06-01T10:00:00Z]) → false  
- Module recompilation check: false  
→ Source marked UNCHANGED. No recompile triggered.  
```  
**Failure:**  
Output lacks BEAM identity metadata. Need deeper artifact inspection.  

---

#### Step 3: Query BEAM Provenance Mechanism  
**Command:**  
```bash  
mix_analyzer beam-provenance \  
  --case B \  
  --assume_unchanged \  
  --previous_beam_hash "sha256:9f86d081"  
```  
**Output:**  
```  
[PROVENANCE TRACE]  
- Module loader: BEAM identity derived SOLELY from:  
  1. File path (/build/lib/module.beam)  
  2. Embedded {:source, size, mtime} metadata (size=100, mtime=2021-06-01T10:00:00Z)  
- NO content digest check performed.  
- NO invalidation of previous BEAM (hash: sha256:9f86d081).  
```  
**Observation:**  
After same-length rewrite (Case B):  
- Compiler uses **leftover previous BEAM** (identified by path + stale metadata).  
- Source bytes are **not consulted** (no digest exists in source record).  
- Compile cache is **omitted** (no recompilation occurred).  

---

#### Step 4: Verify Against Repaired Implementation  
**Command:**  
```bash  
mix_analyzer compare-case \  
  --case B \  
  --case D \  
  --diff-field source.digest  
```  
**Output:**  
```  
[DIFF]  
- Case B (failing_ref): source record → {size, mtime}  
- Case D (repaired): source record → {digest, mtime}  

[EFFECT]  
Case B: BEAM identity = f(path, last_size, last_mtime) → STALE after rewrite  
Case D: BEAM identity = f(path, content_digest) → INVALIDATED after rewrite  
```  

---

#### Conclusion: Case B Identity  
- **Leftover previous BEAM** was used post-rewrite.  
- Root cause: Identity binding relied on `{path, size, mtime}` tuple, which became stale when:  
  - Size remained constant  
  - Mtime reset masked timestamp changes  
- Mitigation (confirmed in public report): Digest-based content checking replaces size.  

**Unresolved Uncertainty:**  
Tool cannot verify if BEAM loader *always* ignores source bytes in Case B without live `:code` inspection.  

**Recommendation:**  
Cross-verify with `mix_analyzer beam-loader-trace` on trusted fixture (not present in environment).

        # Required response

        Return only the structured JSON object described in the external-critic contract.
        Do not wrap it in a Markdown code fence.
