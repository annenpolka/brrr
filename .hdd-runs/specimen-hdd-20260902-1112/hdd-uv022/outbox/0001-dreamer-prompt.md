# In-World Operating Policy

You are currently inside a real, already-running tool or computing environment.

Do not step outside the situation to propose a new product, methodology, or speculative design. Do not describe how such a tool could be built unless the environment itself exposes implementation details during use.

Operate what is present.

- Use the tool or environment on concrete tasks.
- Discover capabilities by trying them, inspecting responses, encountering failures, and adapting.
- Treat newly supplied limits and corrections as facts that have become known inside the environment.
- Continue from prior observations instead of resetting the world whenever something becomes inconvenient.
- If a previous assumption conflicts with a newly confirmed fact, investigate the conflict through use. Do not silently rewrite prior observations.
- Prefer concrete commands, interactions, outputs, errors, retries, and state changes over feature lists or feasibility essays.
- Do not rename familiar primitives merely to appear novel. If an existing interaction is insufficient, let a different abstraction emerge through use.
- Do not invoke unknown physics, quantum effects, hidden intelligence, magical semantic understanding, or unverifiable infrastructure merely to escape a constraint unless such a capability has actually been observed in the environment.
- When evidence is insufficient, report uncertainty from inside the situation rather than inventing certainty.

Do not discuss or infer any orchestration, editorial, evaluation, or prompt-engineering process behind the task. Those are outside the environment you are operating.

Your response should read like a field report produced by someone actually using the current tool or environment, not like a workshop or design-review transcript.


        ---

        # Current situation

CURRENT SITUATION
A real checkout or reduced fixture exists. The following material is what is known.

# TASK

Two virtual environments exist:

- `.venv` — the test context default
- `other/` — a second venv created with the same Python version

`uv python find` is asked for `other/bin/python3`.

First invocation sets `PYTHONEXECUTABLE` to `.venv/bin/python3`. The
requested interpreter, under that environment variable, reports the
`.venv` executable.

Second invocation asks for the same `other/bin/python3` path with
`PYTHONEXECUTABLE` *removed*. The developer wants this to print
`other/bin/python3`, not the default `.venv`.

# OBSERVED

Source: test `python_find_cached_launcher_override` at
`c5d8a25374a5b3c98178ebcb440c8c25f65b803e`, plus issue 21062. Local
execution was not performed.

Harness snapshot (failing revision):

```
# with PYTHONEXECUTABLE=<.venv>/bin/python3
uv python find <other>/bin/python3
----- stdout -----
[VENV]/bin/python3

# PYTHONEXECUTABLE removed
uv python find <other>/bin/python3
----- stdout -----
[VENV]/bin/python3
```

The second command's comment in the test says it should return `other`,
not the cached `.venv`. The recorded stdout is still `[VENV]/bin/python3`.

Issue 21062 (related field report): `uv run --project slack-watcher
<console-script>` executed a binary under a *deleted* worktree path
`A/slack-watcher/.venv/bin/...` while the live project was at `B`.
`uv run --no-cache` was correct. Deleting only
`~/.cache/uv/interpreter-v4` also corrected subsequent runs. Decoding
`.msgpack` entries showed `sys_prefix` / `sys_executable` pointing at
the deleted worktree `A`.

# COMMANDS

Not executed in this packet. Source-backed only.

Reduced session:

```text
uv venv --python 3.12 other
# PYTHONEXECUTABLE points at the default .venv interpreter
PYTHONEXECUTABLE=.venv/bin/python3 uv python find other/bin/python3
env -u PYTHONEXECUTABLE uv python find other/bin/python3
```

Upstream test at the failing revision:

```text
cargo test -p uv --test python python_find_cached_launcher_override -- --exact --nocapture
```

Issue 21062 also used `uv run --no-cache --project <dir> <script>` as a
contrast that avoided the stale interpreter metadata.

TREE (failing world fragment)

[TEMP_DIR]/
  .venv/bin/python3          # default context venv
  other/bin/python3          # requested interpreter

~/.cache/uv/interpreter-v4/
  <shard>/
    <digest>.msgpack         # CachedByTimestamp<Interpreter>

uv (failing_ref c5d8a25374a5b3c98178ebcb440c8c25f65b803e)/
  crates/uv-python/src/interpreter.rs
  crates/uv/tests/python/python_find.rs

RELEVANT MATERIAL

### interpreter_cache_entry.rs


        let canonical = canonicalize_executable(&absolute).map_err(handle_io_error)?;

        let cache_entry = cache.entry(
            CacheBucket::Interpreter,
            cache_digest(&(
                ARCH,
                uv_platform::OsType::from_env()
                    .map(|os_type| os_type.to_string())
                    .unwrap_or_default(),
                uv_platform::OsRelease::from_env()
                    .map(|os_release| os_release.to_string())
                    .unwrap_or_default(),
            )),
            // We use the absolute path for the cache entry to avoid cache collisions for relative
            // paths. ... We include the canonical path in the cache entry as well ...
            format!("{}.msgpack", cache_digest(&(&absolute, &canonical))),
        );

### python_find_cached_launcher_override.rs


fn python_find_cached_launcher_override() {
    let context = uv_test::test_context!("3.12");
    let other_venv = context.temp_dir.child("other");

    context
        .venv()
        .arg("--python")
        .arg("3.12")
        .arg(other_venv.path())
        .assert()
        .success();

    let requested_python = venv_bin_path(&other_venv).join("python3");
    let override_python = venv_bin_path(&context.venv).join("python3");

    // `PYTHONEXECUTABLE` makes the requested `other` interpreter report `.venv`.
    uv_snapshot!(context.filters(), context.python_find()
        .arg(&requested_python)
        .env("PYTHONEXECUTABLE", &override_python), @"
    exit_code: 0 (success)
    ----- stdout -----
    [VENV]/bin/python3
    ");

    // Without `PYTHONEXECUTABLE`, this should return `other`, not the cached `.venv`.
    uv_snapshot!(context.filters(), context.python_find()
        .arg(&requested_python)
        .env_remove("PYTHONEXECUTABLE"), @"
    exit_code: 0 (success)
    ----- stdout -----
    [VENV]/bin/python3
    ");
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


        # What to do now

        Continue operating the same tool or environment from its current state.
        Treat the limits and corrections above as facts that have just become known inside
        the world, not as review comments. Investigate their consequences through concrete
        use. Prefer commands, observations, failures, retries, and changed behavior over a
        design essay.
