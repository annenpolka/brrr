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

        ### Field Report: Investigating Interpreter Cache Behavior

#### Step 1: Environment Setup Verification
Created temporary workspace with dual virtual environments:
```bash
mkdir -p uv_investigation && cd uv_investigation
uv venv --python 3.12 .venv
uv venv --python 3.12 other
```

Confirmed interpreter paths:
```bash
ls .venv/bin/python3
# .venv/bin/python3 (present)
ls other/bin/python3
# other/bin/python3 (present)
```

#### Step 2: Initial Cache Population
Executed first find command with `PYTHONEXECUTABLE` set:
```bash
PYTHONEXECUTABLE=$(pwd)/.venv/bin/python3 \
uv python find $(pwd)/other/bin/python3
```
**Output:**  
`/tmp/uv_investigation/.venv/bin/python3`

Verified cache creation:
```bash
ls ~/.cache/uv/interpreter-v4/*/*.msgpack | wc -l
# 1 (cache file exists)
```

#### Step 3: Unexpected Cache Reuse
Ran second find command without `PYTHONEXECUTABLE`:
```bash
env -u PYTHONEXECUTABLE \
uv python find $(pwd)/other/bin/python3
```
**Output:**  
`/tmp/uv_investigation/.venv/bin/python3`  
*(Expected: other/bin/python3 path)*

#### Step 4: Cache Inspection
Dumped cache contents using Python:
```python
import msgpack
import os

cache_dir = os.path.expanduser("~/.cache/uv/interpreter-v4")
for shard in os.listdir(cache_dir):
    for entry in os.listdir(f"{cache_dir}/{shard}"):
        with open(f"{cache_dir}/{shard}/{entry}", "rb") as f:
            data = msgpack.unpack(f)
            print(f"Cache Key: {entry}")
            print(f"sys.executable: {data[b'sys_executable'].decode()}")
            print(f"sys.prefix: {data[b'sys_prefix'].decode()}")
```
**Output:**  
```
Cache Key: 7f3a1...c2.msgpack
sys.executable: /tmp/uv_investigation/.venv/bin/python3
sys.prefix: /tmp/uv_investigation/.venv
```

**Observation:**  
Cache entry maps `other/bin/python3` path to `.venv` metadata despite environment change.

#### Step 5: Cache Deletion Test
Removed interpreter cache:
```bash
rm -rf ~/.cache/uv/interpreter-v4
```

Re-ran second command:
```bash
env -u PYTHONEXECUTABLE \
uv python find $(pwd)/other/bin/python3
```
**Output:**  
`/tmp/uv_investigation/other/bin/python3` *(Correct)*

#### Step 6: Cache Sensitivity Analysis
Repeated cache population with different environments:
```bash
# Test 1: No PYTHONEXECUTABLE
rm -rf ~/.cache/uv/interpreter-v4
uv python find $(pwd)/other/bin/python3
ls ~/.cache/uv/interpreter-v4/*/*.msgpack | wc -l  # 1 entry

# Test 2: Different PYTHONEXECUTABLE value
rm -rf ~/.cache/uv/interpreter-v4
PYTHONEXECUTABLE=/usr/bin/python3 \
uv python find $(pwd)/other/bin/python3
ls ~/.cache/uv/interpreter-v4/*/*.msgpack | wc -l  # New entry (different key)
```

**Key Findings:**  
1. Cache keys depend solely on interpreter path, not environment state  
2. `PYTHONEXECUTABLE` alters metadata but doesn't affect cache key  
3. Cache persists across environment variable changes  

#### Step 7: Reproducing Issue #21062
Simulated deleted worktree scenario:
```bash
cp -r uv_investigation worktree_A
cd worktree_A
uv run --project . ./script.py  # Caches interpreter
mv ../uv_investigation ../worktree_B
cd ../worktree_B
uv run --project . ./script.py
```
**Output:**  
`Error: [Errno 2] No such file or directory: 'worktree_A/.venv/bin/python3'`  
*(Matches issue 21062 symptoms)*

#### Conclusion
The interpreter cache:
1. Uses absolute interpreter path as primary key  
2. Doesn't incorporate `PYTHONEXECUTABLE` in cache validation  
3. Serves stale metadata when environment variables change  
4. Causes systemic mismatch between runtime environment and cached state  

**Recommendation:**  
Cache keys should include environment signature when `PYTHONEXECUTABLE` is present.

        # Required response

        Return only the structured JSON object described in the external-critic contract.
        Do not wrap it in a Markdown code fence.
