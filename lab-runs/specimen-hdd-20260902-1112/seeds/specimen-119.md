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
