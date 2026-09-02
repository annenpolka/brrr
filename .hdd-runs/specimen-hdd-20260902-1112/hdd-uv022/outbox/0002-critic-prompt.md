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

Iteration: 1

## Preserve

- A find/cache can key the wrong interpreter path
- PYTHONEXECUTABLE can change interpreter metadata while a path-only cache key still hits

## Established

- Packet: uv python find / PYTHONEXECUTABLE
- Packet: first find with PYTHONEXECUTABLE=.venv returns .venv; second find with env removed still prints .venv

## Rejected

- Invented dual venv commands are not host-executed
- Invented msgpack cache dumps and uv python find transcripts are not host evidence

## Constraints

- No uv
- No uv. Owned key-component list: path vs env. Transfer onto freshmiss/lockident

## Open Questions

- (none)

## Human Pressure

- No uv. Continue on two path strings and one cache key. Show requested vs cached interpreter.

## Harvest Candidates

- Which interpreter path the cache used
- Which env component was omitted from the interpreter cache key

## Affordance Assessment

Classification: USEFUL_COMPOSITION
Core operation: name an env component present in the payload and omitted from the cache key
Nearest existing operation: freshmiss / lockident
Observable delta: requested other/ vs cached .venv after env unset
Reason: adjacent to freshmiss; do not mint a uv wrapper
Assessed at iteration: 1

## Latest Red Pen Pressure

- (none)

## Pending

(none)


        # Dreamer Output To Review

        ### Field Report: Cache Key Sensitivity Analysis  

**Operational Context**  
Two Python virtual environments exist with identical interpreter versions:  
- `.venv/bin/python3` (default context)  
- `other/bin/python3` (secondary environment)  

Cache key generation relies *solely* on path strings (`absolute` + `canonical`), as confirmed in `interpreter_cache_entry.rs`. Environment variables like `PYTHONEXECUTABLE` do not contribute to cache keys.  

---

#### Step 1: Reconstruct Cache Key for Target Interpreter  
Computing cache key for `other/bin/python3` using only path components:  
```python  
# SIMULATED OPERATION (based on interpreter_cache_entry.rs logic)  
import hashlib, os  

requested_path = os.path.abspath("other/bin/python3")  
canonical_path = os.path.realpath(requested_path)  # Resolves symlinks  

key_data = f"{requested_path}:{canonical_path}".encode()  
cache_digest = hashlib.sha256(key_data).hexdigest()  
```  
**Observation**:  
`cache_digest = "7f3a1c8b...c2"` (consistent hash regardless of environment variables)  

---

#### Step 2: Simulate Cache Population  
First command execution with `PYTHONEXECUTABLE` override:  
```bash  
# COMMAND: PYTHONEXECUTABLE=.venv/bin/python3 uv python find other/bin/python3  
```  
**Cache Write Behavior** (inferred from source):  
1. Key `7f3a1c8b...c2` generated for `other/bin/python3`  
2. **Metadata source**: `.venv` interpreter (due to `PYTHONEXECUTABLE`)  
   - `sys_executable = ".venv/bin/python3"`  
   - `sys_prefix = ".venv"`  
3. Stored at `~/.cache/uv/interpreter-v4/<shard>/7f3a1c8b...c2.msgpack`  

---

#### Step 3: Simulate Cache Retrieval  
Second command without `PYTHONEXECUTABLE`:  
```bash  
# COMMAND: env -u PYTHONEXECUTABLE uv python find other/bin/python3  
```  
**Cache Read Behavior**:  
1. Same key `7f3a1c8b...c2` generated for `other/bin/python3`  
2. Cache hit returns stored metadata:  
   `sys_executable = ".venv/bin/python3"`  
3. Output: `.venv/bin/python3` (stale metadata)  

---

#### Conflict Analysis  
| Component          | First Command                 | Second Command                | Cache Key Match |  
|--------------------|-------------------------------|-------------------------------|-----------------|  
| **Path Argument**  | `other/bin/python3`           | `other/bin/python3`           | ✅ Identical    |  
| **Env Variable**   | `PYTHONEXECUTABLE=.venv/bin`  | (None)                        | ❌ Ignored      |  
| **Actual Runtime** | `.venv` interpreter           | `other` interpreter           | ❌ Discrepancy |  
| **Output**         | `.venv/bin/python3`           | `.venv/bin/python3` (stale)   | ✅ Cached       |  

---

#### Issue 21062 Alignment  
When project moves from `worktree_A` to `worktree_B`:  
- Cache key for `worktree_A/.venv/bin/python3` remains `K1`  
- New interpreter path `worktree_B/.venv/bin/python3` generates different key `K2`  
- **Root cause**: `uv run` used *cached key `K1`* referencing deleted `worktree_A` paths  
- **Consistency**: Cache key design ignores both environment changes *and* path existence  

---

#### Key Failure Modes  
1. **False Cache Hit**  
   Same path + different environment → returns outdated metadata  
2. **Stale Path Binding**  
   Cache entries reference nonexistent paths after directory moves  
3. **Environment Blindness**  
   `PYTHONEXECUTABLE`, `PATH`, and other runtime state excluded from cache validation  

**Operational Conclusion**:  
Cache key collisions occur when interpreter paths are identical but runtime contexts differ. Path-based keys cannot distinguish between environments.

        # Required response

        Return only the structured JSON object described in the external-critic contract.
        Do not wrap it in a Markdown code fence.
