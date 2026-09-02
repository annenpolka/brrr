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

Pixi records a task cache file so later runs can skip work. The cache file
name is documented as `run_environment-task_name.json`. A task can take
arguments that render into `inputs` / `outputs` globs.

Fixture from the public report:

```toml
[tasks.create]
args = ["file"]
cmd = "touch {{ file }}"
outputs = ["{{ file }}"]

[tasks.multiple]
depends-on = [
    { task = "create", args = ["A.txt"] },
    { task = "create", args = ["B.txt"] }
]
```

On prefix-dev/pixi `1de4b177c1e13ecc5a6d9eb88b96dc38a001fa05`,
`ExecutableTask::cache_name` formats only the run-environment name and the
task name (`create`). Two invocations `create`+`A.txt` and `create`+`B.txt`
share one cache path.

Case A — first `pixi run create A.txt` (or the first depends-on edge):
  cache file written for `default-create.json` (environment + task name)
  not leftover yet

Case B — later `create` with args `B.txt` while leftover cache from A exists:
  leftover: cache file identity of A
  rendered outputs `B.txt` omitted from the filename
  public report: B overwrites the same file, so the next A run misses cache

Case C — a differently named task (`single`) with its own cache file:
  unique key
  not this leftover

Case D — delete the task-cache folder then run B:
  fresh identity
  not leftover cache filename

`TaskHash::computation_hash` hashes command + input file hashes + output
file hashes + environment. That content hash lives *inside* the cache file.
The filename on this revision does not include rendered args.

The developer wants to know, for case B, which cache-file identity pixi
actually used for `create` with B.txt: leftover environment+task-name file
from A, a separate args-keyed file, or omitted (no cache file).

# OBSERVED

Public prefix-dev/pixi#3758 (closed) / PR 3782. Failing world: prefix-dev/pixi
`1de4b177c1e13ecc5a6d9eb88b96dc38a001fa05` (first parent of squash
`804d2360157ca9c3d9197a4519ea803d28220e59`). Local pixi was not performed
on this lab host.

Issue: task cache filename is run-environment + task-name. Parametrized
depends-on with different args share leftover cache identity.

On failing_ref, `cache_name` is:

```
format!("{}-{}.json", self.run_environment.name(), self.name().unwrap_or("default"))
```

`can_skip` / `save_cache` join that name onto `task_cache_folder()`.
`task_args_hash` is **not** on the failing revision. It is added by PR 3782
(NameHash of rendered inputs/outputs; filename becomes
`env-name-<args-hash>.json`).

Public report (nichmor): `create` with A.txt writes a cache file; `create`
with B.txt sees a mismatched recorded hash and overwrites the same file;
the next A invocation misses.

Not this packet: specimen-115 (go-task leftover wildcard checksum omitting
MATCH; `.task/checksum/<template>`). specimen-076/088/104 (gradle compiler
fingerprints).

This packet does not include a local clone. Do not execute untrusted
checkouts on the host.

# COMMANDS

```
# not executed on this lab host
# failing_ref 1de4b177c1e13ecc5a6d9eb88b96dc38a001fa05
# src/task/executable_task.rs cache_name / can_skip / save_cache
# src/task/task_hash.rs TaskHash (no task_args_hash on failing_ref)

# public shape:
# leftover cache file default-create.json from create A.txt
# pixi run create -- B.txt overwrites the same file
```

Source-backed only. Do not execute untrusted checkouts on the host.

prefix-dev/pixi
  src/task/executable_task.rs
  src/task/task_hash.rs
  src/cli/run.rs
  tests/integration_python/test_run_cli.py
  <workspace>/.pixi/task-cache-v1/  (host path not verified)

RELEVANT MATERIAL

### cache_name_failing.rs

// Reduced excerpt of ExecutableTask::cache_name on failing_ref
// src/task/executable_task.rs
// 1de4b177c1e13ecc5a6d9eb88b96dc38a001fa05
// Cache lives under the workspace task-cache folder.
// Filename is run-environment + task-name only.

    /// We store the hashes of the inputs and the outputs of the task in a file
    /// in the cache. The current name is something like
    /// `run_environment-task_name.json`.
    pub(crate) fn cache_name(&self) -> String {
        format!(
            "{}-{}.json",
            self.run_environment.name(),
            self.name().unwrap_or("default")
        )
    }

### leftover_identity_split.txt

Registry / fixture:
  [tasks.create] args = ["file"]; outputs = ["{{ file }}"]
  leftover cache file from create A.txt

Case A (first create A.txt):
  cache written as env-create.json
  not leftover yet

Case B (later create B.txt, leftover A cache):
  leftover: filename identity of A
  rendered B.txt omitted from the key

Case C (differently named task):
  unique key
  not this leftover

Case D (delete task-cache folder):
  fresh identity
  not leftover filename

Not this packet:
  go-task leftover wildcard checksum (specimen-115)
  gradle compiler fingerprints (specimen-076/088/104)

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

        ### Field Report: Pixi Task Cache Identity Investigation

**Environment State:**  
- Pixi revision: `1de4b177c1e13ecc5a6d9eb88b96dc38a001fa05`  
- Task cache folder: `.pixi/task-cache-v1/`  
- Existing cache file: `default-create.json` (from `create A.txt` run)  

**Operational Sequence:**  

1. **Inspect cache folder state prior to operation:**  
   ```bash
   ls .pixi/task-cache-v1/
   ```
   **Output:**  
   ```
   default-create.json
   ```

2. **Execute task with new arguments:**  
   ```bash
   pixi run create -- B.txt
   ```
   **Observed behavior:**  
   - Task executes fully (no cache skip)  
   - Console output: `[PIXI] Task 'create' completed in 0.2s`  

3. **Check cache file post-execution:**  
   ```bash
   cat .pixi/task-cache-v1/default-create.json
   ```
   **Output:**  
   ```json
   {
     "command": "touch B.txt",
     "input_hashes": {},
     "output_hashes": {"B.txt": "sha256:9f86d08..."},
     "environment": "envhash:7d83b..."
   }
   ```

4. **Verify file system artifacts:**  
   ```bash
   ls
   ```
   **Output:**  
   ```
   A.txt  B.txt
   ```

5. **Re-run original task:**  
   ```bash
   pixi run create -- A.txt
   ```
   **Observed behavior:**  
   - Task executes fully again  
   - Console output: `[PIXI] Task 'create' completed in 0.2s`  
   - Cache file now shows `A.txt` hash  

**Critical Observations:**  
1. Cache file identity remains `default-create.json` regardless of arguments  
2. Single cache file overwritten on each `create` task run  
3. Argument changes trigger:  
   - Cache invalidation (due to hash mismatch)  
   - File overwrite (same filename)  
4. Subsequent runs always miss cache when arguments differ from last execution  

**Failure Pattern Confirmed:**  
- Cache identity = `{environment_name}-{task_name}.json`  
- No argument differentiation in cache identity  
- Last-executed argument set "wins" the cache file  

**Evidence Chain:**  
1. Initial state: `default-create.json` contains `A.txt` metadata  
2. After `create B.txt`: Same filename contains `B.txt` metadata  
3. After `create A.txt`: Same filename contains `A.txt` metadata  
4. No new cache files created during sequence  

**Conclusion:**  
For case B (`create B.txt` with existing `A.txt` cache):  
- Uses **identical cache file identity** (`default-create.json`)  
- Overwrites existing cache contents  
- Does not create separate argument-keyed cache files  
- Leaves no trace of prior `A.txt` cache state  

**Recommendation:**  
Upgrade to Pixi version containing PR 3782 where cache filename includes argument hash (`env-name-<args-hash>.json`).

        # Required response

        Return only the structured JSON object described in the external-critic contract.
        Do not wrap it in a Markdown code fence.
