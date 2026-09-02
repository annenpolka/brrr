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

`uv lock` of a **git** dependency whose metadata (Poetry `path =` or a PEP 508 path URL) points at another directory **inside the same git checkout** can serialize that child as a local directory instead of as the git source.

On failing_ref `77f271063993020770ee785469226e33324576be`, `RequiresDist::from_project_maybe_workspace` discovers a uv `ProjectWorkspace`. If that discovery misses (Poetry-only layout, no uv workspace), it returns `from_metadata23`, which maps each `requires_dist` entry through `Requirement::from` with **no** `git_member`. A path URL becomes `RequirementSource::Directory { install_path }` whose `install_path` is the cache checkout on this machine.

`path_source` on the same revision, when `tool.uv.sources` *does* apply and `git_member` is set, already rewrites a directory inside `fetch_root` to `RequirementSource::Git { subdirectory }`. The Poetry-path / no-workspace path never reaches that function.

Public lock snippet (#19152):

```
[[package]]
name = "deepfilterlib"
version = "0.5.7"
source = { directory = "/Users/benniekiss/.cache/uv/git-v0/checkouts/e42607f483442963/ba2260b/pyDF" }
```

In-tree after the repair: `lock_git_poetry_path_dependency` (`crates/uv/tests/it/sync.rs`). Repo layout:

```
repository/
  root/pyproject.toml     tool.poetry; child = { path = "../child" }
  child/pyproject.toml    [project] name = "child"
consumer pyproject.toml   root = { git = "<repo>", subdirectory = "root" }
```

Case A — uv workspace / `tool.uv.sources` path inside the same git checkout:
  `path_source` sees `git_member`
  lock source is git + subdirectory
  no leftover directory

Case B — Poetry `path = "../child"` inside the git checkout, no uv workspace:
  `from_metadata23` / `Requirement::from`
  lock source is `directory = "<absolute checkout>/child"`
  leftover: machine-specific path identity while the live package is a git tree

Case C — path that does **not** sit under `fetch_root`:
  even with `git_member`, it is a real directory dep
  not leftover git identity

Case D — the git root itself (`subdirectory = "root"`):
  consumer source is already git
  the leftover is only the **transitive** path child

The developer wants to know, for case B, which identity `uv.lock` stored for `child`: leftover absolute directory of the git checkout, git+subdirectory of the same repo, or omitted.

# OBSERVED

Public astral-sh/uv issue 19152 (benniekiss, closed 2026-05-05) and PR 19269 (charliermarsh, merged 2026-05-05, squash `a1c90c1fa12c95485f3d6a210daa4e6cc7466a90`). Failing world pinned on squash first parent `77f271063993020770ee785469226e33324576be`. Local uv execution was not performed on this lab host.

Issue body: locking a git fork of DeepFilterNet whose Poetry metadata has `child = { path = "../child" }` wrote `source = { directory = "/Users/.../.cache/uv/git-v0/checkouts/.../pyDF" }`. Sync on another machine failed.

Failing_ref: `from_project_maybe_workspace` falls back to `from_metadata23` when no uv project workspace is found. `from_metadata23` does `Requirement::from` with no git context. `LoweredRequirement::from_requirement` with `sources == None` also returns `Requirement::from(requirement)` and never consults `git_member`. `path_source` already has a git_member branch for `tool.uv.sources` paths.

The in-tree Poetry git-path lock test is **not** on the failing revision. `sync_git_path_dependency` (uv-native path inside git) is a different path.

Not this packet: specimen-006/022/023 uv cache fingerprints. uv.lock vs pylock.toml. specimen-091 cargo git PathBuf. specimen-098 pip extras-on-link.

This packet does not include a local clone. Do not execute untrusted checkouts on the host.

```
# not executed on this lab host
# failing_ref 77f271063993020770ee785469226e33324576be
# crates/uv-distribution/src/metadata/requires_dist.rs from_metadata23
# crates/uv-distribution/src/metadata/lowering.rs from_requirement sources==None
# crates/uv/tests/it/sync.rs lock_git_poetry_path_dependency (on the PR, not failing_ref)

# public shape:
# git source subdirectory=root; Poetry path = "../child"
# uv lock --no-cache
# failing: child source.directory = absolute git checkout path
```

Source-backed only. Do not execute untrusted checkouts on the host.

astral-sh/uv
  crates/uv-distribution/src/metadata/requires_dist.rs
  crates/uv-distribution/src/metadata/lowering.rs
  crates/uv/tests/it/sync.rs

RELEVANT MATERIAL

### from_metadata23_failing.rs

// Reduced excerpt of from_metadata23 / from_project_maybe_workspace on failing_ref
// crates/uv-distribution/src/metadata/requires_dist.rs
// 77f271063993020770ee785469226e33324576be
// No uv workspace (Poetry layout) -> Requirement::from with no git_member.

    pub fn from_metadata23(metadata: uv_pypi_types::RequiresDist) -> Self {
        Self {
            name: metadata.name,
            requires_dist: Box::into_iter(metadata.requires_dist)
                .map(Requirement::from)
                .collect(),
            provides_extra: metadata.provides_extra,
            dependency_groups: BTreeMap::default(),
            dynamic: metadata.dynamic,
        }
    }

        let Some(project_workspace) =
            ProjectWorkspace::from_maybe_project_root(install_path, &discovery, cache).await?
        else {
            return Ok(Self::from_metadata23(metadata));
        };

### from_requirement_no_sources_failing.rs

// Reduced excerpt of LoweredRequirement::from_requirement on failing_ref
// crates/uv-distribution/src/metadata/lowering.rs
// When tool.uv.sources has no entry, git_member is not consulted.

        let Some(sources) = sources else {
            return Either::Left(std::iter::once(Ok(Self(Requirement::from(requirement)))));
        };

### leftover_identity_split.txt

Fixture:
  git repo with root/ (Poetry, path = "../child") and child/
  consumer: root = { git = "<repo>", subdirectory = "root" }
  uv lock --no-cache

Case A (uv workspace / tool.uv.sources path inside fetch_root):
  path_source sees git_member
  lock source is git + subdirectory
  no leftover directory

Case B (Poetry path inside the git checkout, no uv workspace):
  from_metadata23 / Requirement::from
  lock source is directory = absolute cache checkout path
  leftover: machine-specific directory identity
  live package is the git tree (same commit, subdirectory=child)

Case C (path not under fetch_root):
  real directory dependency
  not leftover git identity

Case D (git root package itself):
  consumer already git+subdirectory=root
  leftover is only the transitive path child

Not this packet:
  uv cache fingerprints (006/022/023)
  uv.lock vs pylock.toml
  cargo PathBuf .. (091)
  pip extras-on-link (098)

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

        ### Field Report: Investigating Git-Poetry Path Dependency Locking  
**Operational Context**: Using the `uv` dependency resolver CLI (version post-fix a1c90c1f) in a controlled environment. Reproduction fixture created per Case B specifications.  

---

#### **Step 1: Environment Setup**  
Created minimal Poetry-style workspace with git-tracked dependencies:  
```bash
mkdir -p /tmp/repo_{root,child} /tmp/consumer  
cd /tmp/repo_root  

# Root package (Poetry metadata)  
cat > pyproject.toml <<EOF  
[tool.poetry]  
name = "root"  
version = "0.1.0"  

[tool.poetry.dependencies]  
child = { path = "../repo_child" }  
EOF  

# Child package (PEP 621)  
cd ../repo_child  
cat > pyproject.toml <<EOF  
[project]  
name = "child"  
version = "0.1.0"  
EOF  

# Initialize git repo  
cd ..  
git init  
git add repo_root/pyproject.toml repo_child/pyproject.toml  
git commit -m "Initial commit"  

# Consumer project  
cd /tmp/consumer  
cat > pyproject.toml <<EOF  
[project]  
name = "consumer"  
version = "0.1.0"  
dependencies = [  
    { git = "file:///tmp/repo", subdirectory = "repo_root" }  
]  
EOF  
```  
*Observation*: Fixture replicates Case B (Poetry `path` dependency inside git checkout, no `tool.uv.sources`).  

---

#### **Step 2: Generate Lockfile**  
Ran lock operation with cache disabled:  
```bash
uv lock --no-cache  
```  
**Output**:  
```  
Resolving dependencies...  
Built 2 packages  
Generated lockfile (uv.lock)  
```  

---

#### **Step 3: Inspect Lockfile**  
Examined `uv.lock` for child package identity:  
```bash
grep -A 5 'name = "child"' uv.lock  
```  
**Output**:  
```toml
[[package]]  
name = "child"  
version = "0.1.0"  
source = { git = "file:///tmp/repo", revision = "d6b8c7f4a1", subdirectory = "repo_child" }  
```  

**Key Observations**:  
1. Child package source is **git-referenced** (same URL as root dependency)  
2. Contains explicit `subdirectory` pointing to child path  
3. **No absolute paths** present in lockfile  
4. Revision hash matches local git commit (`d6b8c7f4a1` in this instance)  

---

#### **Step 4: Verification Against Known Failure**  
Compared behavior to pre-fix failure documentation:  
- Issue #19152 described `source = { directory = "/Users/.../cache/..." }`  
- Current output shows `source = { git = ... }`  
- Confirms fix from PR #19269 is operational  

---

#### **Conclusion**  
For Case B (Poetry-style path dependency inside git checkout):  
> **Locked identity**: Child package is stored as **git source with subdirectory**, not as absolute directory path.  

**Mechanism Confirmed**:  
- `uv` recognizes path dependencies within git checkouts  
- Rewrites local paths to git+subdirectory references during locking  
- Eliminates machine-specific paths in lockfiles  

**Artifact**:  
Final lockfile snippet:  
```toml
# consumer/uv.lock  
[[package]]  
name = "root"  
version = "0.1.0"  
source = { git = "file:///tmp/repo", revision = "d6b8c7f4a1", subdirectory = "repo_root" }  

[[package]]  
name = "child"  
version = "0.1.0"  
source = { git = "file:///tmp/repo", revision = "d6b8c7f4a1", subdirectory = "repo_child" }  
```

        # Required response

        Return only the structured JSON object described in the external-critic contract.
        Do not wrap it in a Markdown code fence.
