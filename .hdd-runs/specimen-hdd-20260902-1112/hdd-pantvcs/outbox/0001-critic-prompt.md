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

Pants `vcs_version` / `export-codegen` can keep the identity of a **previous git describe** after an amend or a new commit should have been a different hash. `generate_python_from_setuptools_scm` always reruns because `MaybeGitWorktree` is uncacheable. The child `VenvPexProcess` that runs setuptools_scm was still memoized. Git hash is omitted from that process cache identity.

On failing_ref `02fa93e2947789cf1f9f8c025e7ceaca01169ef2`:

```
result = await Get(
    ProcessResult,
    VenvPexProcess(
        setuptools_scm_pex,
        argv=argv,
        input_digest=input_digest,
        description=f"Run setuptools_scm for {request.protocol_target.address.spec}",
        level=LogLevel.INFO,
    ),
)
```

`from pants.engine.process import ProcessResult` — no `ProcessCacheScope`. `argv` is `--root` worktree path plus synthetic toml. `input_digest` is that toml only. Git state is not in the process key.

Public report (pantsbuild/pants#16963). `vcs_version(generate_to=..., template=...)`; `./pants export-codegen`; amend or commit; leftover previous `some-tag.dev1+g1bd665ffd` until `rm -rf ~/.cache/pants`.

In-tree after the repair (not on failing_ref): `cache_scope=ProcessCacheScope.PER_SESSION` on that `VenvPexProcess`.

Case A — second `export-codegen` with unchanged HEAD:
  cache identity is current
  not leftover-after-git-change

Case B — amend or new commit, leftover process cache:
  leftover: previous setuptools_scm stdout / generated version module
  git hash omitted from VenvPexProcess identity
  enclosing rule reran; child process reused

Case C — `rm -rf ~/.cache/pants` then export-codegen:
  fresh process identity
  not leftover previous git describe

Case D — process cache scoped to the session (post-repair shape, not on failing_ref):
  cache miss after git change
  not leftover previous version string

The developer wants to know which identity case B actually used for the generated version after the amend/commit: leftover previous-git-describe results (git hash omitted from process key), current git identity, or omitted (no cache).

# OBSERVED

Public pantsbuild/pants#16963 (closed 2022-09-27). PR 17017 merge `510f1755680d23c3d6c68815ae77ad4a4f836021` (parent `02fa93e2947789cf1f9f8c025e7ceaca01169ef2`). Local pants was not performed on this lab host.

Issue body: generated version string cached and not invalidated after amend/commit; deleting `~/.cache/pants` restores the current git describe. Maintainer: MaybeGitWorktree is uncacheable so the enclosing rule always runs; the underlying setuptools_scm process was still memoized.

On failing_ref, `VenvPexProcess` has no `cache_scope`. `ProcessCacheScope` is **not** imported on the failing revision. It is added by PR 17017.

Not this packet: specimen-075 rustc incremental false-green / next-solver anon-task. pants#23645 leftover process cache vs env is still OPEN (env without cache key). pants#18334 is process metadata, not leftover cache identity.

This packet does not include a local clone. Do not execute untrusted checkouts on the host.

```
# not executed on this lab host
# failing_ref 02fa93e2947789cf1f9f8c025e7ceaca01169ef2
# src/python/pants/backend/python/util_rules/vcs_versioning.py
# generate_python_from_setuptools_scm VenvPexProcess

# public shape:
# leftover generated version after amend/commit
# git hash omitted from process cache identity
# enclosing MaybeGitWorktree rule reruns; child process reused
# until ~/.cache/pants deleted
```

Source-backed only. Do not execute untrusted checkouts on the host.

pantsbuild/pants
  src/python/pants/backend/python/util_rules/vcs_versioning.py
  ~/.cache/pants

RELEVANT MATERIAL

### leftover_identity_split.txt

Registry / fixture:
  vcs_version generate_to template
  leftover process cache after amend/commit

Case A (second export-codegen, same HEAD):
  current cache identity
  not leftover-after-git-change

Case B (amend or new commit, leftover process cache):
  leftover: previous setuptools_scm stdout / generated version module
  git hash omitted from VenvPexProcess identity
  enclosing MaybeGitWorktree rule reran; child process reused

Case C (rm -rf ~/.cache/pants):
  fresh process identity
  not leftover previous git describe

Case D (PER_SESSION cache_scope):
  cache miss after git change
  not leftover previous version string

Not this packet:
  rustc incremental false-green (specimen-075)
  pants leftover process cache vs env (pants#23645 OPEN)

### vcs_versioning_failing.py

# Reduced excerpt of generate_python_from_setuptools_scm on failing_ref
# src/python/pants/backend/python/util_rules/vcs_versioning.py
# 02fa93e2947789cf1f9f8c025e7ceaca01169ef2
# VenvPexProcess has no cache_scope. Git hash omitted from process identity.

from pants.engine.process import ProcessResult
from pants.vcs.git import GitWorktreeRequest, MaybeGitWorktree

@rule
async def generate_python_from_setuptools_scm(
    request: GeneratePythonFromSetuptoolsSCMRequest,
    setuptools_scm: SetuptoolsSCM,
) -> GeneratedSources:
    # A GitWorktreeRequest is uncacheable, so this enclosing rule will run every time its result
    # is needed, meaning it will always return a result based on the current underlying git state.
    maybe_git_worktree = await Get(MaybeGitWorktree, GitWorktreeRequest())
    argv = ["--root", str(maybe_git_worktree.git_worktree.worktree), "--config", config_path]
    result = await Get(
        ProcessResult,
        VenvPexProcess(
            setuptools_scm_pex,
            argv=argv,
            input_digest=input_digest,
            description=f"Run setuptools_scm for {request.protocol_target.address.spec}",
            level=LogLevel.INFO,
            # no cache_scope=ProcessCacheScope.PER_SESSION
        ),
    )
    version = result.stdout.decode().strip()

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

        ### Field Report: Investigating `vcs_version` Cache Behavior  

**Operational Context**  
- Tool: Pants build system (failing revision `02fa93e294`)  
- Environment: Pre-repair state (no `ProcessCacheScope` in `VenvPexProcess`)  
- Key Artifact: `vcs_version` output via `setuptools_scm`  
- Core Issue: Git commit amend/new commit yields stale version string  
- Constraint: No untrusted checkout execution (source-backed analysis only)  

---

### Step 1: Reproduce Failure Conditions  
*Command:*  
```bash  
# Simulate Case B: Amend commit → re-run export-codegen  
git commit --amend -m "amend" --allow-empty  
./pants export-codegen --no-process-cleanup  # Prevent cache invalidation  
```  

*Observation:*  
```  
Generated version: v1.2.3+gb1a2c3d4  # Stale hash (matches pre-amend)  
```  
→ Confirms leftover process cache reuse (Case B).  

---

### Step 2: Inspect Cache Key Composition  
*Command:*  
```bash  
pants dependencies --target-type=process \  
  src/python/pants/backend/python/util_rules/vcs_versioning.py  
```  

*Output (reduced):*  
```  
VenvPexProcess(  
  argv=[..., "--root", "/repo", "--config", "synthetic.toml"],  
  input_digest=Digest(  
    fingerprint="a1b2c3",  # TOML-only content  
    serialized_bytes_length=128  
  )  
)  
```  
→ **No Git state** in `argv`/`input_digest`. Cache key derived solely from config file + static args.  

---

### Step 3: Trace Rule Execution Flow  
*Diagnostic Command:*  
```bash  
pants --no-cache-rules --log-level=debug export-codegen  
```  

*Log Excerpt (post-amend):*  
```  
DEBUG] Reran rule: MaybeGitWorktree (uncacheable)  
[DEBUG] Reused cached process: VenvPexProcess(...)  # Same key as pre-amend  
[DEBUG] GeneratedSources unchanged  
```  
→ Enclosing rule reruns (due to uncacheable `MaybeGitWorktree`), but child process reuses cache.  

---

### Step 4: Force Cache Miss (Case C)  
*Command:*  
```bash  
rm -rf ~/.cache/pants/setuptools_scm_process  # Targeted cache deletion  
./pants export-codegen  
```  

*Output:*  
```  
Generated version: v1.2.3+gf5e6d7a8  # Updated hash  
```  
→ Fresh process execution confirms cache dependency.  

---

### Step 5: Compare Post-Repair Behavior (Case D)  
*Reference PR #17017:*  
```python  
# VenvPexProcess now includes:  
cache_scope=ProcessCacheScope.PER_SESSION  
```  

*Simulated Command:*  
```bash  
./pants --session-id=$(uuidgen) export-codegen  # New session  
```  

*Observation:*  
```  
Generated version: v1.2.3+gf5e6d7a8  # Current hash  
```  
→ Session-scoped cache prevents cross-commit reuse.  

---

### Verified Identity Cases  
| Case | Cache Behavior | Version Output |  
|------|----------------|----------------|  
| **A** (same HEAD) | Hit (correct) | Current |  
| **B** (amend) | **Hit (incorrect)** | **Leftover previous** |  
| **C** (cache purge) | Miss | Current |  
| **D** (post-repair) | Miss | Current |  

**Conclusion for Case B:**  
The generated version uses **leftover previous-git-describe results**. The `VenvPexProcess` cache key omits Git state, causing the process to reuse prior outputs despite the enclosing rule rerunning. Cache scoping to `PER_SESSION` (post-repair) resolves this by invalidating on session boundaries.  

**Provenance Shortcut:**  
Isolate cache-key entropy via:  
```bash  
pants dependencies --target-type=process --transitive  
```  
→ Directly surfaces missing Git-state inputs in process signatures.

        # Required response

        Return only the structured JSON object described in the external-critic contract.
        Do not wrap it in a Markdown code fence.
