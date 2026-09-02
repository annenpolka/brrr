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

sbt 2.x can keep leftover **extra zinc Analysis identity** after the analysis gz file under a cache path has switched. The leftover identity is the last-write Analysis still sitting in `MixedAnalyzingCompiler.staticCachedStore`, even though the current analysis-file identity (size + last-modified) is a different gz.

On failing_ref `c491f035f832a62843d69364b55237dc29c99e7d`, `Defaults.analysisStore` is:

```
private inline def analysisStore(inline analysisFile: TaskKey[File]): AnalysisStore =
  MixedAnalyzingCompiler.staticCachedStore(
    analysisFile = analysisFile.value.toPath,
    useTextAnalysis = false,
  )
```

That two-arg overload hard-codes `cacheLast = true`. Zinc then wraps the file store:

```
val store1 =
  if cacheLast then AnalysisStore.getCachedStore(fileStore)
  else fileStore
staticCache(analysisFile, AnalysisStore.getThreadSafeStore(store1))
```

`getCachedStore` keys only on last write through that store. It does not include file size or timestamp. sbt 2.x remote/local caching can replace the gz bytes under the same path. The extra leftover Analysis identity remains.

Public report (sbt/sbt#9195) scripted fixture `cache/discoveredMainClasses`:

```
scalaVersion := "2.13.18"
object Main { def main(args: Array[String]): Unit = () }

> checkDiscoveredMainClasses
# actual == Seq("example.Main")
$ copy-file src/main/scala/Main.scala tmp/Main.scala
$ delete src
-> checkDiscoveredMainClasses
$ copy-file tmp/Main.scala src/main/scala/Main.scala
> checkDiscoveredMainClasses
# expect success but failure
```

Workaround recorded on the issue: `cleanFull`.

Case A — first compile, analysis gz written through this store:
  last-write Analysis identity matches the file
  `discoveredMainClasses` is `Seq("example.Main")`
  no leftover extra Analysis

Case B — sbt 2.x cache restores a different gz under the same analysis path:
  leftover: extra last-write Analysis identity
  current file identity (size + mtime) is the restored gz
  last-write cache does not see the switch

Case C — delete `src`, then restore `Main.scala` (issue 9195):
  leftover extra Analysis identity from B (or from the prior write)
  `checkDiscoveredMainClasses` fails after restore
  not a missing-source case (sources are back)

Case D — `cleanFull` then compile:
  leftover Analysis cache dropped
  not this leftover (wipe, not last-write vs file identity)

The developer wants to know which identity case B/C actually used for zinc Analysis: leftover extra last-write Analysis (file identity ignored), current gz file identity (size+mtime), or omitted (no Analysis store at all).

# OBSERVED

Public sbt/sbt#9195 (closed 2026-05-11). PR 9207 merge `49f19feef1bbe41795f3d5bbfaa7b5249d4ea3ef` (parents `c491f035f832a62843d69364b55237dc29c99e7d` + `e69e23aae14240d2c6b63e2c5ff356ccc154e784`). Local sbt/zinc was not performed on this lab host.

Issue body: `discoveredMainClasses` after delete+restore of `src` expects success and fails. Notes `.triggeredBy(compile)` plus global cache. Workaround `cleanFull`.

PR body: MixedAnalyzingCompiler analysis cache caches using the last write, assuming all writing happens via it. That does not work with sbt 2.x caching where the gz file under the path can switch. Repair keys local analysis caching on file size and timestamp (caffeine), and calls zinc `staticCachedStore(..., cacheLast = false)`.

On failing_ref, `analysisStore` uses the two-arg zinc overload (`cacheLast = true`). Zinc `getCachedStore` is last-write. File size / last-modified are **not** part of that identity.

Not this packet: specimen-088 / specimen-104 (gradle configuration-cache leftover). specimen-075 (rustc incremental). specimen-078 (derived gocache). specimen-111 (tsbuildinfo leftover signature). No sbt specimen in 001-111.

This packet does not include a local clone. Do not execute untrusted checkouts on the host.

```
# not executed on this lab host
# failing_ref c491f035f832a62843d69364b55237dc29c99e7d
# main/src/main/scala/sbt/Defaults.scala analysisStore
# zinc MixedAnalyzingCompiler.staticCachedStore cacheLast=true

# public shape (sbt 2.x scripted cache/discoveredMainClasses):
# first checkDiscoveredMainClasses ok
# delete src; restore Main.scala
# leftover: extra last-write Analysis identity
# checkDiscoveredMainClasses fails
```

Source-backed only. Do not execute untrusted checkouts on the host.

sbt/sbt
  main/src/main/scala/sbt/Defaults.scala
  main/src/main/scala/sbt/internal/BuildDef.scala
sbt/zinc
  zinc/src/main/scala/sbt/internal/inc/MixedAnalyzingCompiler.scala

RELEVANT MATERIAL

### analysis_store_failing.scala

# Reduced excerpt of Defaults.analysisStore + zinc staticCachedStore on failing_ref
# sbt main/src/main/scala/sbt/Defaults.scala
# c491f035f832a62843d69364b55237dc29c99e7d
# Last-write Analysis identity is the cache. File size/mtime are omitted.

  private inline def analysisStore(inline analysisFile: TaskKey[File]): AnalysisStore =
    MixedAnalyzingCompiler.staticCachedStore(
      analysisFile = analysisFile.value.toPath,
      useTextAnalysis = false,
    )

# zinc MixedAnalyzingCompiler.scala two-arg overload (cacheLast = true):

  def staticCachedStore(analysisFile: Path, useTextAnalysis: Boolean): AnalysisStore =
    staticCachedStore(
      analysisFile = analysisFile,
      useTextAnalysis = useTextAnalysis,
      useConsistent = false,
      cacheLast = true,
      mappers = ReadWriteMappers.getEmptyMappers(),
      reproducible = true,
      parallelism = Runtime.getRuntime.availableProcessors(),
    )

    val store1 =
      if cacheLast then AnalysisStore.getCachedStore(fileStore)
      else fileStore
    staticCache(analysisFile, AnalysisStore.getThreadSafeStore(store1))

### leftover_identity_split.txt

Registry / fixture:
  sbt 2.x analysis gz path
  MixedAnalyzingCompiler.staticCachedStore cacheLast=true
  scripted cache/discoveredMainClasses

Case A (first compile, write through this store):
  last-write Analysis identity matches file
  no leftover extra Analysis

Case B (sbt 2.x cache restores a different gz under same path):
  leftover: extra last-write Analysis identity
  current file identity is size+mtime of restored gz

Case C (delete src then restore Main.scala):
  leftover extra Analysis identity
  checkDiscoveredMainClasses fails after restore

Case D (cleanFull then compile):
  leftover Analysis dropped
  not this leftover

Not this packet:
  gradle configuration-cache leftover (specimen-088 / specimen-104)
  rustc incremental (specimen-075)
  derived gocache (specimen-078)
  tsbuildinfo leftover signature (specimen-111)

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

        ### Field Report: Analysis Identity Investigation

**Operator Log**  
Using installed CLI tool `scode` (Scala Code Analyzer) to inspect analysis store behavior without executing untrusted checkouts. Tool version: `scode/3.1.4-azul`.

---

#### Step 1: Inspect analysis store initialization path  
```bash
scode trace --file analysis_store_failing.scala \
           --target "MixedAnalyzingCompiler.staticCachedStore" \
           --upstream
```
**Output:**  
```
TRACE PATH [analysis_store_failing.scala]
├── Defaults.analysisStore (line 2) 
│   └── Calls: MixedAnalyzingCompiler.staticCachedStore(Path, Boolean)
│       └── Overload resolution: staticCachedStore(Path, Boolean) [cacheLast=true]
└── MixedAnalyzingCompiler.staticCachedStore (line 9)
    └── Conditional: cacheLast=true
    └── Invokes: AnalysisStore.getCachedStore(fileStore)
    └── Stores in: staticCache(Path, AnalysisStore)
```
**Observation:**  
Confirms `cacheLast=true` flows from Defaults to `getCachedStore` wrapper. No file identity (size/mtime) appears in call chain.

---

#### Step 2: Verify store caching semantics  
```bash
scode resolve --symbol "sbt.internal.inc.AnalysisStore.getCachedStore" \
             --source zinc/src/main/scala/sbt/internal/inc/AnalysisStore.scala
```
**Output:**  
```
RESOLUTION FAILED: Source not in material. Only local excerpts available.
```
**Fallback:** Query known behavior from material:  
```bash
scode extract --file leftover_identity_split.txt --section "KNOWN FACTS"
```
**Output:**  
```
"getCachedStore keys only on last write through that store. Does not include file size or timestamp."
```
**Observation:**  
Cache identity depends solely on last write operation, not file attributes. External file changes won't invalidate cache.

---

#### Step 3: Simulate case B/C cache behavior  
```bash
scode model --scenario case_B \
           --input analysis_store_failing.scala \
           --override "fileStore=ExternalModified" \
           --method "staticCachedStore.get"
```
**Output:**  
```
MODEL EXECUTION [case_B]:
- Store state: cacheLast=true
- Store.get() called after external file change
- Cached analysis returned (last-write identity)
- File system check: SKIPPED (cacheLast condition)
- Output: Analysis(discoveredMainClasses=Seq("example.Main")) [cached]
```
**Observation:**  
Confirms cache returns last-written analysis regardless of file changes. Matches failure symptom in case C where restored sources use stale analysis.

---

#### Step 4: Validate against PR fix  
```bash
scode diff --file1 analysis_store_failing.scala \
          --file2 <(echo "cacheLast=false") \
          --impact-downstream
```
**Output:**  
```
BEHAVIOR DIFF:
- WHEN cacheLast=true: AnalysisStore.getCachedStore() wraps fileStore
- WHEN cacheLast=false: fileStore used directly
CRITICAL CHANGE: Cache bypass removes last-write identity retention
```
**Observation:**  
PR #9207 (`cacheLast=false`) avoids cached wrapper, forcing file identity check. Explains why issue resolves when cacheLast disabled.

---

#### Conclusions  

1. **Case B/C identity source**:  
   Leftover extra last-write Analysis identity used (file identity ignored). Verified through:  
   - Cache wrapper retention mechanism (`getCachedStore`)  
   - External file change simulation  
   - Cache semantics documented in material  

2. **Failure mechanism**:  
   ```mermaid
   graph LR
   A[Cache restore] --> B[File overwritten]
   B --> C[AnalysisStore.get called]
   C --> D[cacheLast=true?]
   D -->|Yes| E[Return cached analysis]
   E --> F[Stale discoveredMainClasses]
   ```

3. **Uncertainties**:  
   - Exact zinc `getCachedStore` implementation not inspectable  
   - No reproduction on local host (safety restriction)  
   - File system timestamp granularity effects unverified  

**Recommended next**:  
```bash
scode model --scenario cache_invalidation --metrics file_identity_checks
```  
To investigate alternative caching strategies if environment permits.

        # Required response

        Return only the structured JSON object described in the external-critic contract.
        Do not wrap it in a Markdown code fence.
