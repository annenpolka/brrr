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
