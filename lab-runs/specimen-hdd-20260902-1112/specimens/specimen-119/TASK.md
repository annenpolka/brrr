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
