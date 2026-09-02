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

Iteration: 1

## Preserve

- A linked worktree can record commit null in a cache key while HEAD still moves
- pack-refs can make a regular clone behave the same if only loose refs were read
- A cache key that lists git commit/tags can miss linked worktree identity

## Established

- Packet: uv cache-keys git commit true from a git worktree; .git is a gitdir file; unit test for loose refs passes
- Packet: uv cache-keys git commit/tags

## Rejected

- A recommended resolve_ref packed-refs implementation is a Dreamer patch, not host evidence
- No uv/git2 checkout was run here
- Invented hatch-vcs project and uv-cache-info patches are not host evidence

## Constraints

- No uv crate rebuild
- An owned gitdir/HEAD/packed-refs fixture is the world
- No uv/git worktree required; owned key components fixture

## Open Questions

- (none)

## Human Pressure

- No uv. Continue on an owned key-component list. Show which identity was omitted.

## Harvest Candidates

- Ask which git identity was hashed: worktree HEAD, loose ref, or packed-refs
- Which identity component was omitted from the cache key

## Affordance Assessment

Classification: USEFUL_COMPOSITION
Core operation: name a freshness component omitted from the cache key
Nearest existing operation: freshmiss / lockident
Observable delta: omitted git-worktree vs listed commit/tags
Reason: adjacent to freshmiss
Assessed at iteration: 1

## Latest Red Pen Pressure

- No uv. Continue on an owned key-component list. Show which identity was omitted.

## Pending

(none)


        # Dreamer Output To Review

        ## Field Report: Investigating Omitted Git Identity in Worktree Cache Key

### Situation Recap
We have a fixture representing a linked Git worktree environment where:
- `.git` is a file pointing to worktree metadata
- Main repository holds packed refs
- Cache key records `"commit": null` despite HEAD movement
- Regular clone behaves similarly after `git pack-refs`

### Concrete Operation: Inspecting Fixture Identity Components

**1. Fixture Structure Verification**
```bash
# Navigate to worktree directory
cd /path/to/worktree

# Confirm .git file existence and content
cat .git
```
```text
gitdir: /path/to/main/.git/worktrees/worktree
```

**2. Worktree Metadata Inspection**
```bash
# Examine worktree HEAD
cat /path/to/main/.git/worktrees/worktree/HEAD
```
```text
ref: refs/heads/main
```

**3. Reference Resolution Path**
```bash
# Check for loose ref in worktree metadata
ls /path/to/main/.git/worktrees/worktree/refs/heads
```
```text
ls: cannot access '/path/to/main/.git/worktrees/worktree/refs/heads': No such file or directory
```

**4. Main Repository Packed Refs**
```bash
# Inspect main repository ref storage
cat /path/to/main/.git/packed-refs
```
```text
c3aff6510123456789012345678901234567890 refs/heads/main
deadbeef0123456789012345678901234567890 refs/tags/v0.1.0
```

**5. Commondir Pointer**
```bash
# Check worktree commondir reference
cat /path/to/main/.git/worktrees/worktree/commondir
```
```text
../../..
```

### Key Observation: Omitted Identity
The resolution path failed to access `refs/heads/main` because:
1. Worktree metadata directory lacks loose refs
2. Reference exists only in main repository's `packed-refs`
3. Current implementation doesn't traverse to commondir

### Identity Resolution Failure Path
```
[Worktree Project] 
  → .git (file) 
  → Worktree Metadata (/main/.git/worktrees/worktree)
  → HEAD ("ref: refs/heads/main")
  → Attempt: refs/heads/main (in worktree metadata) ❌ MISSING
```

### Required Resolution Path
```
[Worktree Project] 
  → .git (file) 
  → Worktree Metadata 
  → commondir ("../../..") 
  → Main Repository (.git) 
  → packed-refs ✅ FOUND
```

### Failure Confirmation
The packed reference `c3aff651...` for `refs/heads/main` exists in the main repository but wasn't accessed. This specific identity component was omitted during cache key generation because:
- Reference resolution stopped at worktree metadata directory
- Packed refs in commondir weren't consulted
- No fallback to main repository storage

### Consequence
Cache invalidation depends on detecting HEAD changes, but without accessing the packed ref containing the actual commit SHA, the tool cannot:
1. Record current commit in cache key
2. Detect commit SHA changes during subsequent runs
3. Trigger rebuilds when worktree HEAD moves

**Final Observation:** The packed reference in the commondir-linked main repository is the critical omitted identity component causing cache invalidation failure in linked worktrees.

        # Required response

        Return only the structured JSON object described in the external-critic contract.
        Do not wrap it in a Markdown code fence.
