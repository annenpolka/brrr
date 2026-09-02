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

Cargo caches `rustc -vV` (and other rustc-info commands) in the workspace target directory as `.rustc_info.json`. The cache is keyed by a `u64` named `rustc_fingerprint`. `Cache::load` reuses the whole JSON when that field equals the fingerprint computed for the current compiler; otherwise it starts an empty cache.

`rustc_fingerprint` is computed in `src/cargo/util/rustc.rs` on rust-lang/cargo `40d6078bafd61645f13086f697104c360b25b7d3`. For each executable (the `rustc` path, optional `rustc_wrapper`, optional `rustc_workspace_wrapper`) a closure `hash_exe` hashes:

1. the resolved executable path
2. that path's mtime (`paths::mtime`)

It does not run `rustc -vV` as part of the fingerprint. Cached `-vV` stdout lives under a separate per-command map and is only consulted after the fingerprint matches.

Public report (Fedora distro rustc, shared `target/` including `.rustc_info.json`):

Two compilers, both invoked as `/usr/bin/rustc`, both `release: 1.82.0`, both `commit-hash` `f6e511eec` (2024-10-15), both mtimes clamped to `2024-10-17 00:00:00` by Fedora reproducible-builds policy.

Compiler X (`rustc -vV` if actually run):

```
rustc 1.82.0 (f6e511eec 2024-10-15) (Fedora 1.82.0-1.fc42)
```

Compiler Y:

```
rustc 1.82.0 (f6e511eec 2024-10-15) (Fedora 1.82.0-1.fc40)
```

A crate graph compiled under X leaves `target/debug/deps/libautocfg-589c41db1eea6297.rlib` plus `.rustc_info.json`. A later cargo on Y, same `target/`, surfaces:

```
error[E0514]: found crate `autocfg` compiled by an incompatible version of rustc
 --> build.rs:2:14
  |
2 |     let ac = autocfg::new();
  |              ^^^^^^^
  |
  = note: the following crate versions were found:
          crate `autocfg` compiled by rustc 1.82.0 (f6e511eec 2024-10-15) (Fedora 1.82.0-1.fc42): [...]/target/debug/deps/libautocfg-589c41db1eea6297.rlib
  = help: please recompile that crate using this compiler (rustc 1.82.0 (f6e511eec 2024-10-15) (Fedora 1.82.0-1.fc40)) (consider running `cargo clean` first)
```

Cases (distro rustc unless noted; `CARGO_CACHE_RUSTC_INFO` unset so caching is on):

Case A — X then Y, same path `/usr/bin/rustc`, same clamped mtime, shared `target/.rustc_info.json`. File lengths may differ. Creation times may differ. `rustc -vV` Fedora suffixes differ as above.

Case B — same as A, except the two binaries also have different `st_size`.

Case C — same as A, except the two binaries have the same length and the same mtime; only birth/creation time differs (and the Fedora suffix, if `-vV` were run).

Case D — rustup: `RUSTUP_HOME` and `RUSTUP_TOOLCHAIN` are set. `hash_exe` still runs on the `rustc` path (often the rustup shim). The rustup arm then also hashes the toolchain string, the home path, and `mtime` of `$RUSTUP_HOME/toolchains/$RUSTUP_TOOLCHAIN/bin/rustc`.

Case E — `CARGO_CACHE_RUSTC_INFO=0`. `load_global_rustc` passes `cache_location: None`.

Case F — `build.rustc-wrapper` set. That wrapper path is hashed with the same `hash_exe` as `rustc`.

The developer wants to know, for case A (and B/C), which identity `Cache::load` actually used for Y against X's `.rustc_info.json`: `rustc_fingerprint` equal (reuse cached `-vV` / "reusing existing rustc info cache"), unequal ("different compiler, creating new rustc info cache"), or cache disabled.

# OBSERVED

Public rust-lang/cargo#14761 (merged via bors). Failing world: `src/cargo/util/rustc.rs` at merge first parent `40d6078bafd61645f13086f697104c360b25b7d3`. Local cargo/rustc execution was not performed on this lab host.

`GlobalContext::load_global_rustc` (same revision, `src/cargo/util/context/mod.rs`) places the cache at `ws.target_dir().join(".rustc_info.json")` when a workspace is present and `CARGO_CACHE_RUSTC_INFO` is not `"0"`. The rustup-shim comparison path passed into `Rustc::new` is `$CARGO_HOME/bin/rustc`.

On the failing revision, `hash_exe` is:

```
let path = paths::resolve_executable(path)?;
path.hash(hasher);
paths::mtime(&path)?.hash(hasher);
```

`Cache::load` then:

```
if data.rustc_fingerprint == rustc_fingerprint {
    debug!("reusing existing rustc info cache");
    dirty = false;
    data
} else {
    debug!("different compiler, creating new rustc info cache");
    empty
}
```

`Rustc::new` takes `verbose_version` from `cache.cached_output(&cmd, 0)` of `rustc -vV`. A fingerprint hit therefore does not re-run `-vV`, so the Fedora suffix in verbose version is not observed at fingerprint time.

PR report: Fedora clamps mtimes (https://fedoraproject.org/wiki/Changes/ReproducibleBuildsClampMtimes). Rust 1.82 across Fedora 39–42 presents as `/usr/bin/rustc` + `2024-10-17 00:00:00`. Shared `target/` (including `.rustc_info.json`) then hits E0514 as in TASK.

No in-tree regression test landed with the PR (single-file change to `rustc.rs`).

# COMMANDS

```
# not executed on this lab host
# failing_ref 40d6078bafd61645f13086f697104c360b25b7d3
# src/cargo/util/rustc.rs rustc_fingerprint / Cache::load
# src/cargo/util/context/mod.rs load_global_rustc -> target/.rustc_info.json

# public symptom (Fedora distro rustc, shared target/):
# cargo build
# error[E0514]: found crate `autocfg` compiled by an incompatible version of rustc
#   crate compiled by Fedora 1.82.0-1.fc42
#   current compiler Fedora 1.82.0-1.fc40
```

Source-backed only. Do not execute untrusted checkouts on the host.

rust-lang/cargo
  src/cargo/util/rustc.rs
  src/cargo/util/context/mod.rs
  <workspace>/target/.rustc_info.json

RELEVANT MATERIAL

### cache_load_compare.rs

# Reduced excerpt of Cache::load on failing_ref
# src/cargo/util/rustc.rs

#[derive(Serialize, Deserialize, Debug, Default)]
struct CacheData {
    rustc_fingerprint: u64,
    outputs: HashMap<u64, Output>,
    successes: HashMap<u64, bool>,
}

// Cache::load:
//   rustc_fingerprint = rustc_fingerprint(wrapper, workspace_wrapper, rustc, rustup_rustc, gctx)
//   read cache_location as CacheData
//   if data.rustc_fingerprint == rustc_fingerprint {
//       debug!("reusing existing rustc info cache");
//       dirty = false;
//       data
//   } else {
//       debug!("different compiler, creating new rustc info cache");
//       empty  // CacheData { rustc_fingerprint, outputs: {}, successes: {} }
//   }

// Rustc::new then:
//   cmd = rustc (wrapped) -vV
//   verbose_version = cache.cached_output(&cmd, 0)?.0

### fedora_rustc_identity_split.txt

Shared workspace target dir (all cases A–C):
  <ws>/target/.rustc_info.json
  <ws>/target/debug/deps/libautocfg-589c41db1eea6297.rlib

Compiler X (Fedora 1.82.0-1.fc42):
  path: /usr/bin/rustc
  mtime: 2024-10-17 00:00:00 (clamped)
  rustc -vV release: 1.82.0
  rustc -vV commit-hash: f6e511eec (2024-10-15)
  rustc -vV host: x86_64-unknown-linux-gnu
  rustc -vV extra suffix: (Fedora 1.82.0-1.fc42)

Compiler Y (Fedora 1.82.0-1.fc40):
  path: /usr/bin/rustc
  mtime: 2024-10-17 00:00:00 (clamped)
  rustc -vV release: 1.82.0
  rustc -vV commit-hash: f6e511eec (2024-10-15)
  rustc -vV host: x86_64-unknown-linux-gnu
  rustc -vV extra suffix: (Fedora 1.82.0-1.fc40)

hash_exe inputs on failing_ref (each of rustc, wrapper, workspace_wrapper):
  resolved path
  mtime

rustup extra inputs (only if RUSTUP_HOME and RUSTUP_TOOLCHAIN are both set):
  rustup_toolchain string
  rustup_home string
  mtime of $RUSTUP_HOME/toolchains/$RUSTUP_TOOLCHAIN/bin/rustc

Cache::load decision:
  equal rustc_fingerprint -> reuse entire CacheData (including cached -vV stdout)
  unequal -> empty CacheData with the new fingerprint

### load_global_rustc.rs

# Reduced excerpt of load_global_rustc on failing_ref
# src/cargo/util/context/mod.rs

pub fn load_global_rustc(&self, ws: Option<&Workspace<'_>>) -> CargoResult<Rustc> {
    let cache_location = ws.map(|ws| {
        ws.target_dir()
            .join(".rustc_info.json")
            .into_path_unlocked()
    });
    let wrapper = self.maybe_get_tool("rustc_wrapper", &self.build_config()?.rustc_wrapper);
    let rustc_workspace_wrapper = self.maybe_get_tool(
        "rustc_workspace_wrapper",
        &self.build_config()?.rustc_workspace_wrapper,
    );

    Rustc::new(
        self.get_tool(Tool::Rustc, &self.build_config()?.rustc),
        wrapper,
        rustc_workspace_wrapper,
        &self
            .home()
            .join("bin")
            .join("rustc")
            .into_path_unlocked()
            .with_extension(env::consts::EXE_EXTENSION),
        if self.cache_rustc_info {
            cache_location
        } else {
            None
        },
        self,
    )
}

// cache_rustc_info is false only when env CARGO_CACHE_RUSTC_INFO is "0"

### rustc_fingerprint_failing.rs

# Reduced excerpt of rustc_fingerprint on failing_ref
# src/cargo/util/rustc.rs
# 40d6078bafd61645f13086f697104c360b25b7d3

fn rustc_fingerprint(
    wrapper: Option<&Path>,
    workspace_wrapper: Option<&Path>,
    rustc: &Path,
    rustup_rustc: &Path,
    gctx: &GlobalContext,
) -> CargoResult<u64> {
    let mut hasher = StableHasher::new();

    let hash_exe = |hasher: &mut _, path| -> CargoResult<()> {
        let path = paths::resolve_executable(path)?;
        path.hash(hasher);

        paths::mtime(&path)?.hash(hasher);
        Ok(())
    };

    hash_exe(&mut hasher, rustc)?;
    if let Some(wrapper) = wrapper {
        hash_exe(&mut hasher, wrapper)?;
    }
    if let Some(workspace_wrapper) = workspace_wrapper {
        hash_exe(&mut hasher, workspace_wrapper)?;
    }

    let maybe_rustup = rustup_rustc == rustc;
    match (
        maybe_rustup,
        gctx.get_env("RUSTUP_HOME"),
        gctx.get_env("RUSTUP_TOOLCHAIN"),
    ) {
        (_, Ok(rustup_home), Ok(rustup_toolchain)) => {
            rustup_toolchain.hash(&mut hasher);
            rustup_home.hash(&mut hasher);
            let real_rustc = Path::new(&rustup_home)
                .join("toolchains")
                .join(rustup_toolchain)
                .join("bin")
                .join("rustc")
                .with_extension(env::consts::EXE_EXTENSION);
            paths::mtime(&real_rustc)?.hash(&mut hasher);
        }
        (true, _, _) => anyhow::bail!("probably rustup rustc, but without rustup's env vars"),
        _ => (),
    }

    Ok(hasher.finish())
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

        ### Field Report: Investigative Session on Rustc Info Cache Behavior

#### Operational Environment
- **Tool**: Cargo build system (rust-lang/cargo@`40d6078baf`)
- **Context**: Fedora-distributed rustc 1.82.0 with clamped mtimes
- **Focus**: `rustc_fingerprint` cache behavior in shared workspace (`target/.rustc_info.json`)
- **Investigation Method**: Source analysis of cache logic at failing revision

---

### Step 1: Reproduce Cache Decision Path
**Command**: Simulate `Cache::load` for Case A (Fedora compilers X/Y)  
**Input**:  
- `rustc_path`: `/usr/bin/rustc` (identical for X/Y)  
- `mtime`: `2024-10-17 00:00:00` (clamped, identical)  
- `rustc_wrapper`: `None`  
- `rustc_workspace_wrapper`: `None`  
- `RUSTUP_HOME`/`RUSTUP_TOOLCHAIN`: Unset (non-rustup case)  

**Code Execution Path**:  
1. `hash_exe` invoked for `/usr/bin/rustc`:  
   ```rust
   path = Path::resolve_executable("/usr/bin/rustc")?; // -> /usr/bin/rustc  
   path.hash(hasher);  // Hashes "/usr/bin/rustc"  
   mtime(&path)?.hash(hasher);  // Hashes clamped mtime (0)  
   ```  
2. No wrappers → skip additional hashing  
3. Rustup check:  
   ```rust
   (maybe_rustup, RUSTUP_HOME, RUSTUP_TOOLCHAIN) = (false, _, _)  
   // Skips rustup branch → final fingerprint = hash("/usr/bin/rustc" + 0)  
   ```  

**Observation**:  
- **Fingerprint output**: Identical `u64` for X and Y  
  (Path + mtime identical → same hash)  

---

### Step 2: Cache Load Simulation  
**Command**: Simulate `Cache::load` with existing `.rustc_info.json` from Compiler X  
**Cache State**:  
```json
{
  "rustc_fingerprint": 0xAABBCCDD, // Fingerprint from X
  "outputs": { ... } // Cached -vV from X
}
```  

**Logic**:  
```rust
if current_fingerprint == cache_fingerprint { // 0xAABBCCDD == 0xAABBCCDD
  debug!("reusing existing rustc info cache");
  reuse_cache = true;
} else {
  debug!("different compiler, creating new rustc info cache");
}
```  

**Observation**:  
- **Debug log**: `"reusing existing rustc info cache"`  
- **`rustc -vV` command**: Not executed (uses cached output from X: `(Fedora 1.82.0-1.fc42)`)  
- **Actual compiler**: Y (`Fedora 1.82.0-1.fc40`)  

---

### Step 3: Impact on Build  
**Command**: Simulate crate reuse with cached compiler info  
**Result**:  
- Cargo assumes rustc identity matches cache (X)  
- Does not invalidate existing `libautocfg-*.rlib` (built with X)  
- Compiler Y links against rlib from X → **E0514 error**  
  ```
  error[E0514]: found crate `autocfg` compiled by an incompatible version of rustc
    = note: crate compiled by rustc 1.82.0 (Fedora 1.82.0-1.fc42)
    = help: recompile with current compiler (Fedora 1.82.0-1.fc40)
  ```  

**Failure Analysis**:  
- Root cause: Fingerprint collision due to:  
  1. Path/mtime-only hashing  
  2. Fedora mtime clamping  
- Cache reuse masks compiler mismatch → stale artifacts not cleaned  

---

### Case Variations  
| Case | Path | Mtime | Size | Birth Time | Fingerprint Match | Cache Reused |  
|------|------|-------|------|------------|-------------------|--------------|  
| **A** | Same | Same | - | - | ✅ | ✅ |  
| **B** | Same | Same | Diff | - | ✅ | ✅ |  
| **C** | Same | Same | Same | Diff | ✅ | ✅ |  

**Key Insight**:  
- Fingerprint **ignores size/birth time** → Collision in all cases (A/B/C)  
- `.rustc_info.json` reuse guaranteed when path/mtime identical  

---

### Conclusion  
- **Cache Behavior for Case A/B/C**:  
  - `rustc_fingerprint` **equal** → Full cache reuse  
  - Cargo reports: `"reusing existing rustc info cache"`  
- **Symptom Trigger**:  
  Cached `-vV` output (from X) masks actual compiler (Y) → linker error  

---

### Proposed Next Step  
**Investigate via Instrumented Build**:  
```bash
# On Fedora system with compilers X/Y:  
CARGO_LOG=cargo::util::rustc=debug cargo build > cargo.log 2>&1  
```  
**Expected Log Artifacts**:  
1. `DEBUG cargo::util::rustc: reusing existing rustc info cache`  
2. Mismatched crate version errors in build output  

**Rationale**:  
Confirms cache reuse precedes linker errors in real-world runtime.  

--- 

**Session End**  
No further commands executed (source analysis complete).

        # Required response

        Return only the structured JSON object described in the external-critic contract.
        Do not wrap it in a Markdown code fence.
