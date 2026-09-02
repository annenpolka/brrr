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

BuildKit's git source cache key for a checkout can be only the commit SHA (plus `.git` when `keepGitDir` is true). Two identifiers that name the **same commit through different refs** then share one snapshot. With `keepGitDir`, the program later resolves the user-provided ref inside that snapshot's `.git`. The first fetch may have stored a `.git` that does not contain the second ref.

In-tree after the repair: `TestMultipleTagAccessKeepGitDir` (`source/git/source_test.go`). Repo has tags `a/v1.2.3` and `a/v1.2.3-same` on the same initial commit. First identifier uses Ref `a/v1.2.3`; second uses `a/v1.2.3-same`. Same remote. `KeepGitDir` true vs false.

On failing_ref `bc6f7be35057d15f8384c91ed500a610ab7e2a87`, `shaToCacheKey` is:

```
func (gs *gitSourceHandler) shaToCacheKey(sha string) string {
	key := sha
	if gs.src.KeepGitDir {
		key += ".git"
	}
	if gs.src.Subdir != "" {
		key += ":" + gs.src.Subdir
	}
	return key
}
```

`CacheKey` after resolving ls-remote always calls `shaToCacheKey(sha)` with no ref. A commit-SHA identifier also keys only on the SHA.

Case A — `KeepGitDir` false, two tags on one commit (`a/v1.2.3` then `a/v1.2.3-same`):
  tree content is identical
  cache keys are equal (SHA only, length 40)
  no leftover `.git` identity (there is no `.git` in the snapshot)

Case B — `KeepGitDir` true, same two tags, same commit:
  pin (resolved SHA) is equal
  failing_ref cache keys are equal (`sha + ".git"`)
  second snapshot can reuse the first keep-git-dir checkout
  that `.git` was fetched for `a/v1.2.3`; `git rev-parse a/v1.2.3-same` inside it can miss the second ref

Case C — `KeepGitDir` true, identifier is a raw 40-char commit SHA (no named ref):
  `shaToCacheKey` still SHA + `.git`
  no named ref is requested in `.git` beyond the SHA fetch
  not the two-tag leftover

Case D — `KeepGitDir` true, two different commits (different SHAs):
  keys differ because SHA differs
  not a leftover-ref problem

The developer wants to know, for case B, which identity `shaToCacheKey` stored: leftover SHA-only (plus `.git`) so two refs collide, SHA#ref so they split, or omitted (no keep-git-dir key).

# OBSERVED

Public moby/buildkit PR 5444 (tonistiigi, merged 2024-10-28, merge `94f0ff8a0c85f4491ce7fd5ffc942e7f58a01ff9`). Related discussion: #4446 (keep-git-dir detached HEAD / missing refs). Failing world pinned on merge first parent `bc6f7be35057d15f8384c91ed500a610ab7e2a87`. Local BuildKit execution was not performed on this lab host.

PR body: when keep-git-dir is true, a Git commit accessed through different refs (or a ref added after the commit was already pulled) reused a cache key that was only the git commit. The previous `.git` directory can be reused without the later ref inside. keep-git-dir false is unchanged: two refs at one commit yield identical tree content. A raw SHA identifier still does not add a named ref to the key.

In-tree test added on the PR (`TestMultipleTagAccessKeepGitDir`): two tags on the same commit; keep-git-dir true requires `key1 != key2` while `pin1 == pin2`; keep-git-dir false requires `key1 == key2`. That test is **not** on the failing revision.

`CacheKey` on failing_ref: if `gs.src.Ref` is already a commit SHA, `shaToCacheKey(ref)` (no extra ref). Otherwise `git ls-remote origin <ref> <ref>^{}` picks a SHA from HEAD/tag/partial lines, then `shaToCacheKey(sha)` with no usedRef.

Not this packet: specimen-066 (moby healthcheck StartPeriod vs StartInterval). specimen-007 (libgit2). specimen-091 (cargo git checkout PathBuf `..`). cargo#17289 (checkout short-id vs core.abbrev).

This packet does not include a local clone. Do not execute untrusted checkouts on the host.

```
# not executed on this lab host
# failing_ref bc6f7be35057d15f8384c91ed500a610ab7e2a87
# source/git/source.go shaToCacheKey / CacheKey
# source/git/source_test.go TestMultipleTagAccessKeepGitDir (on the PR, not failing_ref)

# public shape (keepGitDir, two tags, one commit):
# GitIdentifier{Remote, KeepGitDir: true, Ref: "a/v1.2.3"}
# GitIdentifier{Remote, KeepGitDir: true, Ref: "a/v1.2.3-same"}
# failing: CacheKey equal (sha+".git"); Snapshot 2 can reuse Snapshot 1 .git
# intended: pin equal, key unequal when keepGitDir
```

Source-backed only. Do not execute untrusted checkouts on the host.

moby/buildkit
  source/git/source.go
  source/git/source_test.go

RELEVANT MATERIAL

### cache_key_failing.go

// Reduced excerpt of CacheKey on failing_ref
// source/git/source.go
// After ls-remote picks a SHA, key is shaToCacheKey(sha) with no usedRef.
// Commit-SHA identifier also keys only on the SHA.

	if ref := gs.src.Ref; ref != "" && gitutil.IsCommitSHA(ref) {
		cacheKey := gs.shaToCacheKey(ref)
		gs.cacheKey = cacheKey
		return cacheKey, ref, nil, true, nil
	}
	// ...
	cacheKey := gs.shaToCacheKey(sha)
	gs.cacheKey = cacheKey
	return cacheKey, sha, nil, true, nil

### leftover_identity_split.txt

Registry / fixture:
  two tags on one commit: a/v1.2.3 and a/v1.2.3-same
  GitIdentifier.Remote shared
  pin = resolved commit SHA (40 hex)

Case A (KeepGitDir false, two tags, one commit):
  tree bytes identical
  cache key = SHA (len 40)
  keys equal
  no .git in snapshot

Case B (KeepGitDir true, two tags, one commit):
  pin equal
  failing_ref key = SHA + ".git" for both (keys equal)
  second snapshot can reuse first .git
  leftover: named ref omitted from key; .git may lack a/v1.2.3-same

Case C (KeepGitDir true, identifier is raw commit SHA):
  key = SHA + ".git"
  no named ref requested
  not the two-tag leftover

Case D (KeepGitDir true, two different commits):
  SHA differs so keys differ
  not leftover-ref

Not this packet:
  moby healthcheck StartPeriod vs StartInterval (specimen-066)
  libgit2 (specimen-007)
  cargo git checkout PathBuf with .. (specimen-091)

### sha_to_cache_key_failing.go

// Reduced excerpt of shaToCacheKey on failing_ref
// source/git/source.go
// bc6f7be35057d15f8384c91ed500a610ab7e2a87
// Key is commit SHA. KeepGitDir adds ".git". Named ref is not in the key.

func (gs *gitSourceHandler) shaToCacheKey(sha string) string {
	key := sha
	if gs.src.KeepGitDir {
		key += ".git"
	}
	if gs.src.Subdir != "" {
		key += ":" + gs.src.Subdir
	}
	return key
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

        ### Field Report: BuildKit Git Source Cache Key Analysis  

**Operational Context**  
Executing within a constrained BuildKit analysis environment. No local Git operations permitted; relying solely on provided code excerpts and established facts. Focus is on `source/git/source.go` at failing commit `bc6f7be`.  

---

#### **Concrete Investigation Steps**  

1. **Confirm Cache Key Composition**  
   Inspected `shaToCacheKey` implementation at failing_ref:  
   ```go  
   func (gs *gitSourceHandler) shaToCacheKey(sha string) string {  
       key := sha  // Base key = raw SHA  
       if gs.src.KeepGitDir {  
           key += ".git"  // Append ".git" only if KeepGitDir=true  
       }  
       if gs.src.Subdir != "" {  
           key += ":" + gs.src.Subdir  
       }  
       return key  
   }  
   ```  
   → **Observation**: No named ref (`a/v1.2.3`, `a/v1.2.3-same`) appears in key construction.  

2. **Trace Cache Key Generation for Tags**  
   Examined `CacheKey` logic handling non-SHA refs (tags):  
   ```go  
   // For non-SHA ref (e.g. tag):  
   cacheKey := gs.shaToCacheKey(sha) // sha = resolved commit  
   return cacheKey, sha, nil, true, nil  
   ```  
   → **Observation**:  
   - Input `Ref="a/v1.2.3"` → Resolves to SHA `abc123` → Cache key = `abc123.git`  
   - Input `Ref="a/v1.2.3-same"` → Resolves to **same SHA `abc123`** → Cache key = `abc123.git`  

3. **Verify Key Collision in Case B**  
   Cross-referenced with `leftover_identity_split.txt`:  
   ```  
   Case B (KeepGitDir true, two tags, one commit):  
     failing_ref key = SHA + ".git" for both (keys equal)  
   ```  
   → **Confirmed**: Both tags produce identical cache key `abc123.git`.  

4. **Test Intended Behavior via PR Test**  
   Analyzed `TestMultipleTagAccessKeepGitDir` (from merged PR, not failing_ref):  
   ```go  
   // Expected post-fix behavior:  
   require.Equal(t, key1 != key2, true) // Keys differ for same SHA  
   require.Equal(t, pin1, pin2)        // Pins identical  
   ```  
   → **Contrast**: Failing_ref does **not** include ref in key, while fixed version does.  

---

#### **Key Findings**  

- **Cache Key Identity for Case B**:  
  `shaToCacheKey` stored **SHA-only + ".git"** (e.g., `abc123.git`).  
  - Named refs (`a/v1.2.3`, `a/v1.2.3-same`) were **omitted** from key.  
  - Result: Two refs sharing a commit **collided** under one cache key.  

- **Root Cause**:  
  Cache reuse allowed Snapshot 2 to inherit Snapshot 1's `.git` directory, which lacked `a/v1.2.3-same` ref.  

- **How Failure Manifested**:  
  Subsequent `git rev-parse a/v1.2.3-same` in reused `.git` directory failed (ref missing).  

---

#### **Unresolved Uncertainty**  
- **Why was ref excluded from key?**  
  Code suggests intentional design for raw SHA inputs (Case C), but no guard for named refs.  
- **Mitigation in Fix**:  
  PR #5444 modified key generation to include ref when `KeepGitDir=true` and ref is **not** a raw SHA.  

---

**Conclusion**  
For Case B at failing_ref, `shaToCacheKey` stored a **SHA-only + ".git"** identity. This caused two refs to share a cache entry despite referring to the same commit, resulting in missing ref errors during reuse. The fix introduced ref-aware key splitting for non-SHA identifiers.  

**No further commands executed** – constraints prohibit Git operations or BuildKit runtime. Analysis complete per available artifacts.

        # Required response

        Return only the structured JSON object described in the external-critic contract.
        Do not wrap it in a Markdown code fence.
