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


        # What to do now

        Continue operating the same tool or environment from its current state.
        Treat the limits and corrections above as facts that have just become known inside
        the world, not as review comments. Investigate their consequences through concrete
        use. Prefer commands, observations, failures, retries, and changed behavior over a
        design essay.
