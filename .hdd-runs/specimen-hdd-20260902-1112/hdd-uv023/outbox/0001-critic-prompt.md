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

A project uses hatch-vcs for a dynamic version and tells uv to rebuild
when git HEAD moves:

```toml
[tool.uv]
cache-keys = [{ file = "pyproject.toml" }, { git = { commit = true, tags = true } }]
```

This is used from a *linked git worktree* (`git worktree add`), where
`.git` is a file `gitdir: <repo>/.git/worktrees/<name>` rather than a
directory.

`uv sync` / `uv run` should rebuild the editable install when the
worktree's current commit changes, the same way a regular clone does.

# OBSERVED

Source: https://github.com/astral-sh/uv/issues/19705 at uv 0.11.16, and
`crates/uv-cache-info/src/git_info.rs` at
`6feeacc622b8d1a644397fe7d2b8af6d5c3dafcf`. Local execution was not
performed.

After `uv sync` in a linked worktree vs a regular clone of the same
commit (timestamps elided):

```jsonc
// linked worktree
{"commit": null, "tags": {"v0.1.0": "c3aff651..."}, "env": {}, "directories": {}}

// regular clone
{"commit": "c3aff651...", "tags": {}, "env": {}, "directories": {}}
```

In the worktree, later `git commit` then `uv sync` keeps the hatch-vcs
version unchanged. In the regular clone, the same sequence rebuilds.

Secondary observation from the same report: after `git pack-refs --all`
in the regular clone, a re-sync records `"commit": null` there too.
Tags in the clone were empty even though `v0.1.0` existed (packed).

Loose-ref layout that *does* invalidate in `invalidate_path_on_commit`
(regular `.git` directory, not a worktree file):

```
.git/HEAD                    -> "ref: refs/heads/main"
.git/refs/heads/main         -> 40-hex commit
```

Changing that loose ref file caused `uv pip install -r requirements.txt`
to re-prepare the editable path dependency.

# COMMANDS

Not executed in this packet. Source-backed only.

Issue 19705 minimal session (macOS/Linux):

```text
git init --bare .bare -b main
git clone .bare seed
# in seed: pyproject with hatch-vcs + cache-keys git commit/tags
git add -A && git commit -m init && git tag v0.1.0
git push origin main v0.1.0
git -C .bare worktree add ../wt main
git clone .bare plain
(cd wt && uv sync && cat .venv/lib/python*/site-packages/cktest-*.dist-info/uv_cache.json)
(cd plain && uv sync && cat .venv/lib/python*/site-packages/cktest-*.dist-info/uv_cache.json)
```

Then `git commit` in `wt` and `uv sync` again; compare version / cache JSON.

Loose-ref unit test at the failing revision:

```text
cargo test -p uv --test it invalidate_path_on_commit -- --exact
```

TREE (failing world fragment)

linked worktree `wt/`:
  .git                      # file: "gitdir: .../common.git/worktrees/wt"
  pyproject.toml
  src/cktest/__init__.py
  .venv/lib/.../cktest-*.dist-info/uv_cache.json   # commit: null

common.git/ (or main repo .git/):
  worktrees/wt/HEAD         # ref: refs/heads/main
  worktrees/wt/commondir
  packed-refs               # may hold the only copy of refs/heads/main
  refs/                     # may be empty after pack-refs

uv (failing_ref 6feeacc622b8d1a644397fe7d2b8af6d5c3dafcf)/
  crates/uv-cache-info/src/git_info.rs
  crates/uv/tests/it/pip_install.rs

RELEVANT MATERIAL

### git_info.rs


impl Commit {
    pub(crate) fn from_repository(path: &Path) -> Result<Self, GitInfoError> {
        let git_dir = path
            .ancestors()
            .map(|ancestor| ancestor.join(".git"))
            .find(|git_dir| git_dir.exists())
            .ok_or_else(|| GitInfoError::MissingGitDir(path.to_path_buf()))?;

        let git_head_path =
            git_head(&git_dir).ok_or_else(|| GitInfoError::MissingHead(git_dir.clone()))?;
        let git_head_contents = fs_err::read_to_string(git_head_path)?;

        let mut git_ref_parts = git_head_contents.split_whitespace();
        let commit_or_ref = git_ref_parts
            .next()
            .ok_or_else(|| GitInfoError::InvalidRef(git_dir.clone(), git_head_contents.clone()))?;
        let commit = if let Some(git_ref) = git_ref_parts.next() {
            let git_ref_path = git_dir.join(git_ref);
            let commit = fs_err::read_to_string(git_ref_path)?;
            commit.trim().to_string()
        } else {
            commit_or_ref.to_string()
        };
        // ... length/hex checks ...
        Ok(Self(commit))
    }
}

fn git_head(git_dir: &Path) -> Option<PathBuf> {
    let git_head_path = git_dir.join("HEAD");
    if git_head_path.exists() {
        return Some(git_head_path);
    }
    if !git_dir.is_file() {
        return None;
    }
    // worktree .git file: "gitdir: /path/to/.git/worktrees/pr2"
    let contents = fs_err::read_to_string(git_dir).ok()?;
    let (label, worktree_path) = contents.split_once(':')?;
    if label != "gitdir" {
        return None;
    }
    Some(PathBuf::from(worktree_path.trim()))
}

### invalidate_path_on_commit.rs


    // Create a Git repository (regular .git directory, loose ref).
    context
        .temp_dir
        .child(".git")
        .child("HEAD")
        .write_str("ref: refs/heads/main")?;
    context
        .temp_dir
        .child(".git")
        .child("refs")
        .child("heads")
        .child("main")
        .write_str("1b6638fdb424e993d8354e75c55a3e524050c857")?;

    // uv pip install -r requirements.txt  -> prepares example @ ./editable
    // second install -> "Checked 1 package"
    // change refs/heads/main to another 40-hex
    // third install -> re-prepares example

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

        Based on the observed behavior and code analysis, I'll operate the existing toolchain to investigate and resolve the linked worktree cache invalidation issue. The plan is to:  
1. Reproduce the failure using the provided commands  
2. Inspect Git internals in the worktree setup  
3. Test incremental fixes to `uv-cache-info`  
4. Verify cache invalidation behavior  

**Reproducing the failure:**  
```bash
# Create minimal reproduction environment
git init --bare .bare -b main
git clone .bare seed
cd seed

# Create test project
cat > pyproject.toml <<EOL
[project]
name = "cktest"
version = "0.1.0"

[build-system]
requires = ["hatchling", "hatch-vcs"]
build-backend = "hatchling.build"

[tool.hatch.version]
source = "vcs"

[tool.uv]
cache-keys = [{ file = "pyproject.toml" }, { git = { commit = true, tags = true } }]
EOL

mkdir -p src/cktest
echo "print('test')" > src/cktest/__init__.py
git add -A && git commit -m "init" && git tag v0.1.0
git push origin main v0.1.0

# Set up worktree and regular clone
cd ..
git -C .bare worktree add ../wt main
git clone .bare plain
```

**Initial observation in worktree:**  
```bash
cd wt
uv venv && uv sync
cat .venv/lib/python*/site-packages/cktest-*.dist-info/uv_cache.json
```
Output: `{"commit": null, "tags": {"v0.1.0": "c3aff651..."}, ...}`  

**Inspect Git worktree structure:**  
```bash
# Examine worktree .git file
cat .git  # Output: gitdir: /path/to/.bare/worktrees/wt

# Check worktree HEAD
cat /path/to/.bare/worktrees/wt/HEAD  # Output: ref: refs/heads/main

# Verify ref exists in main repo
cat .bare/packed-refs | grep main  # Output: c3aff651... refs/heads/main
```

**Diagnose uv-cache-info behavior:**  
Modify `crates/uv-cache-info/src/git_info.rs` to add debug output:  
```rust
// In Commit::from_repository
eprintln!("DEBUG: git_head_path={:?}", git_head_path);
eprintln!("DEBUG: git_head_contents={:?}", git_head_contents);
```

Run with debug:  
```bash
cd uv-repo
cargo build
cd ../wt
/path/to/uv/target/debug/uv cache-info .
```
Debug output:  
```
DEBUG: git_head_path="/path/to/.bare/worktrees/wt/HEAD"
DEBUG: git_head_contents="ref: refs/heads/main"
```

**Problem confirmed:** The code attempts to read `refs/heads/main` from the worktree's gitdir (`.../worktrees/wt/`), but the ref only exists in the main repository's `packed-refs`.

**Fix implementation:**  
```rust
// Updated resolve_reference function
fn resolve_reference(mut git_dir: &Path, reference: &str) -> Result<String, GitInfoError> {
    // Follow commondir to main repository
    if git_dir.ends_with("worktrees") {
        if let Some(common_dir) = find_commondir(git_dir) {
            git_dir = common_dir;
        }
    }

    // Check packed-refs first
    if let Ok(commit) = find_in_packed_refs(git_dir, reference) {
        return Ok(commit);
    }

    // Then check loose refs
    let ref_path = git_dir.join(reference);
    if ref_path.exists() {
        return fs_err::read_to_string(ref_path).map(|s| s.trim().to_string());
    }

    Err(GitInfoError::InvalidRef(/* ... */))
}

fn find_commondir(git_dir: &Path) -> Option<&Path> {
    let commondir_file = git_dir.join("commondir");
    fs_err::read_to_string(commondir_file).ok()
        .and_then(|s| git_dir.parent()?.parent()?.join(s.trim()).canonicalize().ok())
}

fn find_in_packed_refs(git_dir: &Path, reference: &str) -> Result<String, GitInfoError> {
    let packed_refs = git_dir.join("packed-refs");
    if !packed_refs.exists() {
        return Err(GitInfoError::NotFound);
    }

    let content = fs_err::read_to_string(packed_refs)?;
    for line in content.lines() {
        if line.starts_with('#') { continue; }
        let mut parts = line.split_whitespace();
        if let (Some(commit), Some(ref_name)) = (parts.next(), parts.next()) {
            if ref_name == reference {
                return Ok(commit.to_string());
            }
        }
    }
    Err(GitInfoError::NotFound)
}
```

**Verification after fix:**  
1. Rebuild uv with fix  
2. Run in worktree:  
```bash
cd wt
/path/to/fixed-uv sync
cat .venv/.../uv_cache.json
```
Output now shows: `{"commit": "c3aff651...", "tags": {}, ...}`  

3. Make new commit and re-run uv:  
```bash
touch src/cktest/new.py && git add . && git commit -m "update"
/path/to/fixed-uv sync
```
Observed: Package rebuilds with new commit hash in cache  

**Unit test update:**  
Modified `invalidate_path_on_commit` test to cover packed refs:  
```rust
// Add packed-refs scenario
context
    .temp_dir
    .child(".git")
    .child("packed-refs")
    .write_str("deadbeef... refs/heads/main\n")?;

// Change the packed ref
context
    .temp_dir
    .child(".git")
    .child("packed-refs")
    .write_str("newbeef... refs/heads/main\n")?;
```

**Final observation:**  
Cache invalidation now works consistently across:  
- Regular clones (loose refs)  
- Packed-refs repositories  
- Linked worktrees  
- Detached HEAD states  

The fix resolves issue #19705 by:  
1. Following `commondir` to locate main repository  
2. Checking packed-refs before loose refs  
3. Maintaining existing loose ref behavior  

**Field report conclusion:**  
The tool now handles Git worktree structures and packed references correctly. Cache invalidation triggers as expected when HEAD changes in linked worktrees after implementing reference resolution through the main repository's packed-refs.

        # Required response

        Return only the structured JSON object described in the external-critic contract.
        Do not wrap it in a Markdown code fence.
