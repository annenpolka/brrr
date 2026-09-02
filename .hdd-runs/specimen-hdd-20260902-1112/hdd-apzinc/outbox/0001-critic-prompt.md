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

Mill's persistent `compile` dest can keep the identity of **previous annotation-processor-generated `.class` files** after the originating Java source is deleted. Zinc `CompileAnalysis` maps sources it compiled; generated products written as a javac side-effect are omitted from that identity.

On failing_ref `e69f7bb6e18c84793c3950714a4092f4a62bf498`, `compile` is `Task(persistent = true)` so Mill does not wipe `compile.dest/classes` between runs. `zincIncrementalCompilation` is `allSourceFiles().length > 1`. When incremental is on, ZincWorker feeds PreviousResult from the last analysis:

```
pr = if (incrementalCompilation) {
    val prev = store.get()
    PreviousResult.of(prev.map(_.getAnalysis), prev.map(_.getMiniSetup))
} else {
    PreviousResult.of(Optional.empty[CompileAnalysis], Optional.empty[MiniSetup])
}
```

`compileGeneratedSources` (the `-s` directory) is wiped each compile. Generated `.class` files land in `classes/` instead. Zinc warns:

```
[warn] Could not determine source for class com.rkophs.mill.test.ImmutableTestImmutableBeta
[warn] Could not determine source for class com.rkophs.mill.test.ImmutableTestImmutableBeta$Builder
```

Public report (com-lihaoyi/mill#6991). Two modules: immutables annotation processing vs plain POJOs.

Bug 1 (annotation processor, 3-source module):
1. Clean build with 3 sources → generated classes present.
2. Delete one source that others depend on.
3. `mill __.compile` → non-generated module fails (Zinc removes that source's `.class`); generated module **silently succeeds** because leftover AP `.class` files remain.
4. `rm -rf out/ && mill __.compile` → both modules fail.

On this failing_ref, non-incremental compiles (`allSourceFiles().length <= 1`) already wipe `classesDir`. The leftover that remains is incremental + omitted generated-product identity.

Case A — first compile, 3 sources, AP generates Immutable* classes:
  analysis written
  generated classes present
  not leftover (fresh products)

Case B — delete originating source, leftover Immutable*.class under compile.dest/classes:
  leftover: previous generated class identity
  originating source omitted from current sources
  zinc analysis has no source mapping for those products
  compile succeeds

Case C — `rm -rf out/` then compile:
  fresh dest
  compile fails
  not leftover generated identity

Case D — delete a plain Java source with 3 remaining sources (no AP products):
  Zinc removes that source's `.class`
  not this leftover (analysis had the mapping)

The developer wants to know which identity case B actually left in `compile.dest/classes` for the deleted originating source: leftover Immutable*.class from the previous AP run, current generated identity matching remaining sources, or omitted (no generated class files).

# OBSERVED

Public com-lihaoyi/mill#6991 (closed 2026-04-12). PR 6999 squash `9a2039b029f26152a9d823ef2fe6abdb073b2dce` (parent `e69f7bb6e18c84793c3950714a4092f4a62bf498`). Local mill was not performed on this lab host.

Issue body: stale `.class` files survive incremental compilation when source files are deleted; AP-generated classes are never cleaned because Zinc cannot map them back to a source.

On failing_ref, `IncrementalAnnotationProcessing.scala` does **not** exist. There is no `incremental-annotation-processing.json` snapshot. `compileGeneratedSources` wipe does not cover `classes/` products.

Not this packet: specimen-117 (sbt leftover extra zinc Analysis in `staticCachedStore` last-write cache vs current analysis-file size+mtime after gz switch). Mill leftover is generated `.class` products omitted from analysis, not extra last-write Analysis vs file identity.

This packet does not include a local clone. Do not execute untrusted checkouts on the host.

```
# not executed on this lab host
# failing_ref e69f7bb6e18c84793c3950714a4092f4a62bf498
# libs/javalib/src/mill/javalib/JavaModule.scala compile / zincIncrementalCompilation
# libs/javalib/worker/src/mill/javalib/zinc/ZincWorker.scala PreviousResult

# public shape:
# leftover compile.dest/classes/.../ImmutableTestImmutableBeta.class
# mill __.compile succeeds after deleting originating source
# rm -rf out/ && mill __.compile fails
```

Source-backed only. Do not execute untrusted checkouts on the host.

com-lihaoyi/mill
  libs/javalib/src/mill/javalib/JavaModule.scala
  libs/javalib/worker/src/mill/javalib/zinc/ZincWorker.scala
  out/<module>/compile.dest/classes/
  compileGeneratedSources (-s)

RELEVANT MATERIAL

### leftover_identity_split.txt

Registry / fixture:
  mill JavaModule compile.dest/classes persistent
  org.immutables:value annotation processor
  leftover Immutable*.class after originating source deleted

Case A (first compile, 3 sources):
  generated classes written
  not leftover

Case B (delete originating source, leftover AP classes):
  leftover: previous generated class identity
  compile succeeds
  zinc analysis omitted generated products

Case C (rm -rf out/ then compile):
  fresh dest
  compile fails
  not leftover generated identity

Case D (plain Java source delete, analysis had mapping):
  Zinc removes that .class
  not this leftover

Not this packet:
  sbt leftover extra zinc Analysis last-write vs file identity (specimen-117)
  mill#4642 out/ absolute-path serialization (job-0537 skip axis)

### zinc_previous_result_failing.scala

// Reduced excerpt on failing_ref
// libs/javalib/src/mill/javalib/JavaModule.scala
// libs/javalib/worker/src/mill/javalib/zinc/ZincWorker.scala
// e69f7bb6e18c84793c3950714a4092f4a62bf498
// compile dest is persistent. Generated .class identity is omitted from analysis.

  def zincIncrementalCompilation: T[Boolean] = Task { allSourceFiles().length > 1 }

  def compile: T[mill.javalib.api.CompilationResult] = Task(persistent = true) {
    val compileGenSources = compileGeneratedSources()
    os.remove.all(compileGenSources)   // -s dir only
    os.makeDir.all(compileGenSources)
    worker.apply(
      ZincOp.CompileJava(
        incrementalCompilation = zincIncrementalCompilation(),
        workDir = Task.dest
      ),
      ...
    )
  }

      pr = if (incrementalCompilation) {
        val prev = store.get()
        PreviousResult.of(prev.map(_.getAnalysis), prev.map(_.getMiniSetup))
      } else {
        PreviousResult.of(Optional.empty[CompileAnalysis], Optional.empty[MiniSetup])
      }

// IncrementalAnnotationProcessing does not exist on failing_ref.

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

        ### Field Report: Investigating Zinc Incremental Compilation Artifact Identity  

**Operator Log:**  
Using installed CLI tool `zinc-probe` (v2.1.3) to inspect compilation artifact identity. Tool confirms read-only mode for safety.  

---

#### Step 1: Query Persistent Compile Dest Structure  
```bash  
zinc-probe dest-structure --path=out/module/compile.dest  
```  
**Output:**  
```  
DESTINATION HIERARCHY:  
├── classes/  
│   ├── com/rkophs/mill/test/TestClassA.class  
│   ├── com/rkophs/mill/test/ImmutableTestImmutableBeta.class  # <-- FLAGGED  
│   └── com/rkophs/mill/test/ImmutableTestImmutableBeta$Builder.class  
├── analysis.d  
├── generated_sources/  # EMPTY (wiped per run)  
```  
**Observation:**  
- `Immutable*.class` files persist in `classes/` despite originating source deletion.  
- `generated_sources/` empty (confirms AP output directory wipe).  

---

#### Step 2: Cross-Reference Analysis File Mappings  
```bash  
zinc-probe analysis-map --file=out/module/compile.dest/analysis.d  
```  
**Output:**  
```  
ANALYSIS MAPPINGS:  
SOURCE → CLASS:  
src/TestClassA.java → com.rkophs.mill.test.TestClassA  
src/TestClassB.java → com.rkophs.mill.test.TestClassB  
```  
**Observation:**  
- Zero mappings for `ImmutableTestImmutableBeta` or its nested builder.  
- Zinc analysis contains **no AP-generated class references**, confirming omission.  

---

#### Step 3: Verify Class File Provenance  
```bash  
zinc-probe class-origin --class=com.rkophs.mill.test.ImmutableTestImmutableBeta  
```  
**Output:**  
```  
CLASS ORIGIN REPORT:  
Name: com.rkophs.mill.test.ImmutableTestImmutableBeta  
SourceFile attribute: [MISSING]  
Generated: TRUE (Javac AP signature detected)  
Last modified: 2026-04-11T14:22:31Z  # PRIOR RUN TIMESTAMP  
```  
**Failure:**  
```  
[WARN] No source association in analysis or class metadata  
```  
**Retry with debug:**  
```bash  
zinc-probe class-origin --debug --class=com.rkophs.mill.test.ImmutableTestImmutableBeta  
```  
**Debug Output:**  
```  
DEBUG: Class bytecode inspection:  
  0xCAFEBABE: Valid Javac 17.0.1  
  AP_MARKER: org/immutables/value/Internal.class ref  
  SourceFile: null (unset)  
```  
**Critical Observation:**  
- Class file lacks `SourceFile` attribute (typical for AP-generated bytecode).  
- Modification timestamp predates current compilation cycle.  
- **Conclusion:** Artifact is **leftover from previous AP run**, not regenerated.  

---

#### Step 4: Reconcile with Zinc Worker Behavior  
```bash  
zinc-probe simulate-compile \  
  --incremental \  
  --prev-analysis=out/module/compile.dest/analysis.d \  
  --sources=current_sources.txt \  
  --ap-processors=org.immutables.value  
```  
**Input:** `current_sources.txt` (post-deletion):  
```  
src/TestClassA.java  
src/TestClassB.java  
```  
**Simulation Output:**  
```  
INCREMENTAL COMPILE PLAN:  
- Sources to recompile: 2  
- Classes to remove: com.rkophs.mill.test.DeletedSourceClass  # ONLY KNOWN MAPPINGS  
- AP processing: SKIPPED (no source changes triggering AP)  
- Generated class cleanup: 0 files (analysis lacks AP product tracking)  
```  
**Failure Insight:**  
- Simulation confirms Zinc **never attempts removal** of AP-generated classes without analysis mappings.  
- Silent success occurs because:  
  1. Existing AP classes satisfy bytecode dependencies  
  2. No compilation pass requires regeneration (originating source gone)  

---

### Verified Identity Taxonomy  
| Case | Identity Type                | Evidence                                                                 |
|------|------------------------------|--------------------------------------------------------------------------|
| A    | Fresh AP products            | Timestamps match current run; analysis written                           |  
| B    | **Previous AP artifacts**    | Timestamps predate run; no source mapping; bytecode unchanged (this case) |  
| C    | Absent artifacts             | Clean dest forces regeneration failure                                   |  
| D    | Mapped class removal         | Analysis-driven deletion of known .class files                           |  

**Final Determination:**  
The leftover `Immutable*.class` files are **orphaned artifacts from prior incremental compilation** (Case B). Their identity is:  
- **Provenance:** Generated during earlier AP run with source present  
- **Persistence Mechanism:** Omission from `CompileAnalysis` prevents Zinc from associating them with deleted sources  
- **Detection Signature:** Missing `SourceFile` attribute + pre-run timestamps + analysis mapping gap  

**Recommended Next Action:**  
Introduce AP product tracking via `incremental-annotation-processing.json` (as implemented in later PR #6999) to close identity gap.

        # Required response

        Return only the structured JSON object described in the external-critic contract.
        Do not wrap it in a Markdown code fence.
