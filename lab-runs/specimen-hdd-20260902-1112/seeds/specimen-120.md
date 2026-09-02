CURRENT SITUATION
A real checkout or reduced fixture exists. The following material is what is known.

# TASK

Pixi's task cache can keep the identity of **one parametrized invocation** after a later invocation of the same task name with different arguments should be a different cache object. The cache filename is `run-environment-task-name.json`. Task arguments that render `inputs` / `outputs` are omitted from that filename.

On failing_ref `1de4b177c1e13ecc5a6d9eb88b96dc38a001fa05`, `ExecutableTask::cache_name` is:

```
pub(crate) fn cache_name(&self) -> String {
    format!(
        "{}-{}.json",
        self.run_environment.name(),
        self.name().unwrap_or("default")
    )
}
```

`can_skip` and `save_cache` both join that name under the task-cache folder. Two `create` invocations with `A.txt` then `B.txt` share one file. The second overwrites the first; the next `A.txt` misses.

Public report (prefix-dev/pixi#3758):

```
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

```
pixi run multiple   # touch A.txt; touch B.txt
pixi run multiple   # touch A.txt; touch B.txt  — no cache hit
```

A single parametrized depend (`create` with `single.txt`) does hit. Two non-parametrized tasks (`create1` / `create2`) each have their own filename and hit.

In-tree after the repair (not on failing_ref): `cache_name` takes a `NameHash` of rendered inputs/outputs; tests `test_task_caching_with_multiple_outputs_args` / `test_task_caching_with_multiple_inputs_args`.

Case A — first `pixi run multiple` (A then B):
  cache file written for env+name
  B overwrites A's hash
  not leftover reuse yet (both ran)

Case B — second `pixi run multiple` with leftover env+name file from B:
  leftover: B's computation hash under `default-create.json`
  A omitted from the filename
  both run again (no cache hit)

Case C — `pixi run single` (one parametrized depend):
  unique env+name file matches that one arg-set
  cache hit
  not this leftover (only one instantiation)

Case D — delete the task-cache folder then `pixi run multiple`:
  fresh identity
  not leftover filename

The developer wants to know which identity case B actually left in the task-cache folder: leftover B hash reused as A's filename, split files per rendered args, or omitted (no cache file).

# OBSERVED

Public prefix-dev/pixi#3758 (closed 2025-05-20). PR 3782 squash `804d2360157ca9c3d9197a4519ea803d28220e59` (parent `1de4b177c1e13ecc5a6d9eb88b96dc38a001fa05`). Local pixi was not performed on this lab host.

Issue body: `pixi run multiple` never reports cache hit; `pixi run single` and `pixi run create-all` (two distinct task names) do.

On failing_ref, cache filename is run-environment + task-name. Rendered inputs/outputs and ArgValues are not that filename. `TaskHash::computation_hash` still hashes file contents inside the file; the *name* of the file is the leftover identity.

`NameHash` / `task_args_hash` are **not** on the failing revision. They are added by PR 3782.

Not this packet: specimen-115 (go-task leftover wildcard fingerprint omitting MATCH; template name `build-*` vs MATCH instantiation). Pixi leftover is one named task with two argument instantiations sharing `env-name.json`.

This packet does not include a local clone. Do not execute untrusted checkouts on the host.

```
# not executed on this lab host
# failing_ref 1de4b177c1e13ecc5a6d9eb88b96dc38a001fa05
# src/task/executable_task.rs cache_name / can_skip / save_cache

# public shape:
# leftover default-create.json from create args=B.txt
# pixi run multiple with create args=A.txt then B.txt: no cache hit
```

Source-backed only. Do not execute untrusted checkouts on the host.

prefix-dev/pixi
  src/task/executable_task.rs
  src/task/task_hash.rs
  tests/integration_python/test_run_cli.py

RELEVANT MATERIAL

### cache_name_failing.rs

// Reduced excerpt of ExecutableTask::cache_name on failing_ref
// src/task/executable_task.rs
// 1de4b177c1e13ecc5a6d9eb88b96dc38a001fa05
// Filename identity is run-environment + task-name.
// ArgValues / rendered inputs/outputs are omitted from the filename.

    pub(crate) fn cache_name(&self) -> String {
        format!(
            "{}-{}.json",
            self.run_environment.name(),
            self.name().unwrap_or("default")
        )
    }

    pub(crate) async fn can_skip(&self, lock_file: &LockFile) -> Result<CanSkip, std::io::Error> {
        let cache_name = self.cache_name();
        let cache_file = self.project().task_cache_folder().join(cache_name);
        // ...
    }

### leftover_identity_split.txt

Registry / fixture:
  tasks.create args=["file"] outputs=["{{ file }}"]
  tasks.multiple depends-on create A.txt then create B.txt
  leftover task-cache default-create.json

Case A (first pixi run multiple):
  A writes default-create.json
  B overwrites same filename
  both ran

Case B (second pixi run multiple, leftover B file):
  leftover: B computation hash under env+name
  A omitted from filename
  no cache hit

Case C (single parametrized depend):
  one instantiation
  cache hit
  not this leftover

Case D (delete task-cache folder):
  fresh identity
  not leftover filename

Not this packet:
  go-task leftover wildcard fingerprint omitting MATCH (specimen-115)

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
