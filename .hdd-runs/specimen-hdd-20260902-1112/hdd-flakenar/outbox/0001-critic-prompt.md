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

A flake.lock node names two identities for one input: git `rev` and `narHash`. After a manual `rev` edit that leaves `narHash` behind, then a later correction of `narHash`, evaluation still fails as if the old NAR were the live tree for that `rev`.

Public CI (NixOS/nix#15198), self-hosted GitHub Actions runner with a Nix daemon. Input `github:blockfrost/blockfrost-tests`. Both records share:

```
rev: 5297592395d1dbd46e88247e459896838c854340
lastModified: 1770733010
type: github
```

They disagree on `narHash`:

```
H_nar_stale = sha256-4cKMeE/8GptnxWnB6LliJy3gCvjVI34TXTwQHEsHcUA=
H_nar_live  = sha256-YR+cemfm4AMEJcUEr/tm0cis3rWKQ0dPFbjwhEVrV94=
```

Case A — lock is consistent (`rev` R1 with matching `narHash` H_nar1). `nix flake lock` then `nix eval`. Store path is `computeStorePath` from H_nar1. Cache upsert uses fingerprint `getFingerprint(store)` (GitHub scheme: the git rev string). Eval of the consumer's `expr` is `"rev1"`.

Case B — same consumer, lock `rev` rewritten to R2, `narHash` still H_nar1, `lastModified` unchanged (in-tree repro forces `GIT_COMMITTER_DATE`/`GIT_AUTHOR_DATE` so a lastModified mismatch does not fire first). `nix eval` on this lock. H_nar1's store path still exists from case A. Substitution fast path can serve that path while the fingerprint is now R2.

Case C — lock corrected to `rev` R2 with `narHash` H_nar2 (H_nar2 from `git archive` + `nix hash path` of R2, not from a Nix fetch of R2). Same runner / same `~/.cache/nix/fetcher-cache-v4.sqlite`. `nix eval` fails. Public log shape:

```
error: NAR hash mismatch in input 'github:blockfrost/blockfrost-tests/5297592395d1dbd46e88247e459896838c854340?narHash=sha256-4cKMeE/8GptnxWnB6LliJy3gCvjVI34TXTwQHEsHcUA%3D', expected 'sha256-YR+cemfm4AMEJcUEr/tm0cis3rWKQ0dPFbjwhEVrV94=' but got 'sha256-4cKMeE/8GptnxWnB6LliJy3gCvjVI34TXTwQHEsHcUA='
```

Issue body also records `mismatch in field 'narHash'` of two `__final` github inputs that share `rev` and `lastModified` and disagree only on `narHash`. Workaround on the runner: delete `~/.cache/nix/fetcher-cache-v4.sqlite` or reboot. `nix flake update` after the poison still fails.

Case D — correct lock (`rev` R2, `narHash` H_nar2) on a **fresh** fetcher cache that never saw case B. Eval is `"rev2"`. No mismatch.

The developer wants to know which identity the substitution cache actually keyed for that input — lock `rev` fingerprint or lock `narHash` — and which NAR store path that key mapped to after case B.

# OBSERVED

Public NixOS/nix issue 15198 (michalrus, 2026-02-11) and PR 15199 (manveru; open; head `5ad2cd9a3051f812801a537e485aff160333da35`). Failing world pinned on NixOS/nix `d5eda907ef98fb9a0304c323a8f8a5fb99c94c35` (PR base).

`Input::computeStorePath` on that revision:

```
auto narHash = getNarHash();
if (!narHash)
    throw Error("cannot compute store path for unlocked input '%s'", to_string());
return store.makeFixedOutputPath(
    getName(),
    FixedOutputInfo{
        .method = FileIngestionMethod::NixArchive,
        .hash = *narHash,
        .references = {},
    });
```

`Input::getAccessorUnchecked` substitution fast path (`isFinal() && getNarHash()`):

```
auto storePath = computeStorePath(store);
store.ensurePath(storePath);
auto accessor = store.requireStoreObjectAccessor(storePath);
accessor->fingerprint = getFingerprint(store);
if (accessor->fingerprint) {
    settings.getCache()->upsert(
        makeSourcePathToHashCacheKey(
            *accessor->fingerprint, ContentAddressMethod::Raw::NixArchive, CanonPath::root),
        {{"hash", store.queryPathInfo(storePath)->narHash.to_string(HashFormat::SRI, true)}});
}
```

GitHub scheme `getFingerprint` on the same revision:

```
if (auto rev = input.getRev())
    return rev->gitRev();
else
    return std::nullopt;
```

Git scheme `getFingerprint` is also rev-based (`rev.gitRev()` plus optional `;s` / `;e` / `;l` suffixes). It does not include `narHash`.

In-tree test added on the PR head (`tests/functional/flakes/cache-poisoning.sh`) is **not** on the failing revision. It describes the failing knobs: two git commits with identical author/committer date; lock `rev` moved without `narHash`; eval; then lock `narHash` moved to `nix hash path` of `git archive` of R2; eval must not NAR-mismatch.

This packet is not NixOS/nix#16391 (detached HEAD, guessed `ref=master`, same `rev`, two trees hashed). Not git-lfs pointer-vs-smudge NAR (#10079 / PR 10153). Not nested-submodule NAR (#10588). Not github-tarball vs git-clone NAR for an untouched lock.

This packet does not include a local clone. Do not execute untrusted checkouts on the host.

# COMMANDS

```
# failing_ref d5eda907ef98fb9a0304c323a8f8a5fb99c94c35
# (not executed on this lab host)

# in-tree repro shape (test file appears on PR head; knobs match the failing world)
# tests/functional/flakes/cache-poisoning.sh

export GIT_COMMITTER_DATE="2000-01-01T00:00:00+0000"
export GIT_AUTHOR_DATE="2000-01-01T00:00:00+0000"

# dep flake: outputs.expr = "rev1" then later "rev2"
# consumer: inputs.dep.url = git+file://$depDir

# case A — consistent lock
nix flake lock "$consumerDir"
nix eval "$consumerDir#expr"     # "rev1"
# flake.lock nodes.dep.locked.narHash = H_nar1
# fetchToStore cache key uses getFingerprint = dep rev1

# case B — lock rev := rev2, narHash still H_nar1
jq --arg rev "$rev2" '.nodes.dep.locked.rev = $rev' flake.lock
nix eval "$consumerDir#expr" || true
# substitution: computeStorePath(H_nar1) still in store
# fingerprint is now rev2

# case C — lock rev := rev2, narHash := H_nar2
# H_nar2 from: git archive HEAD | tar xf; nix hash path --type sha256 --sri
nix eval "$consumerDir#expr"
# failing_ref: NAR hash mismatch / mismatch in field 'narHash'
# public CI: expected H_nar_live, got H_nar_stale (or field-mismatch of those two)

# case D — same corrected lock, empty ~/.cache/nix/fetcher-cache-v4.sqlite
# eval "rev2"; no mismatch
```

Not executed on this lab host.

NixOS/nix
  src/libfetchers/fetchers.cc
  src/libfetchers/github.cc
  src/libfetchers/git.cc
  tests/functional/flakes/cache-poisoning.sh

RELEVANT MATERIAL

### compute_store_path_failing.cc

// Reduced excerpt of Input::computeStorePath on failing_ref
// src/libfetchers/fetchers.cc
// d5eda907ef98fb9a0304c323a8f8a5fb99c94c35
// Store path identity is narHash, not rev.

StorePath Input::computeStorePath(Store & store) const
{
    auto narHash = getNarHash();
    if (!narHash)
        throw Error("cannot compute store path for unlocked input '%s'", to_string());
    return store.makeFixedOutputPath(
        getName(),
        FixedOutputInfo{
            .method = FileIngestionMethod::NixArchive,
            .hash = *narHash,
            .references = {},
        });
}

### fetchers_fastpath_failing.cc

// Reduced excerpt of Input::getAccessorUnchecked substitution fast path
// src/libfetchers/fetchers.cc
// d5eda907ef98fb9a0304c323a8f8a5fb99c94c35
// Store path from narHash. Cache fingerprint from getFingerprint (rev).

    if (isFinal() && getNarHash()) {
        try {
            auto storePath = computeStorePath(store);

            store.ensurePath(storePath);

            debug("using substituted/cached input '%s' in '%s'", to_string(), store.printStorePath(storePath));

            auto accessor = store.requireStoreObjectAccessor(storePath);

            accessor->fingerprint = getFingerprint(store);

            if (accessor->fingerprint) {
                settings.getCache()->upsert(
                    makeSourcePathToHashCacheKey(
                        *accessor->fingerprint, ContentAddressMethod::Raw::NixArchive, CanonPath::root),
                    {{"hash", store.queryPathInfo(storePath)->narHash.to_string(HashFormat::SRI, true)}});
            }

            accessor->setPathDisplay("«" + to_string() + "»");

            return {accessor, *this};
        } catch (Error & e) {
            debug("substitution of input '%s' failed: %s", to_string(), e.what());
        }
    }

### git_fingerprint_failing.cc

// Reduced excerpt of GitInputScheme::getFingerprint
// src/libfetchers/git.cc
// d5eda907ef98fb9a0304c323a8f8a5fb99c94c35
// Still rev-based. Optional suffixes for submodules / exportIgnore / lfs.
// narHash is not in the key.

    std::optional<std::string> getFingerprint(Store & store, const Input & input) const override
    {
        auto makeFingerprint = [&](const Hash & rev) {
            return rev.gitRev() + (getSubmodulesAttr(input) ? ";s" : "") + (getExportIgnoreAttr(input) ? ";e" : "")
                   + (getLfsAttr(input) ? ";l" : "");
        };

        if (auto rev = input.getRev())
            return makeFingerprint(*rev);
        // ... dirty-workdir branch omitted ...
        return std::nullopt;
    }

### github_fingerprint_failing.cc

// Reduced excerpt of GitArchiveInputScheme::getFingerprint
// src/libfetchers/github.cc
// d5eda907ef98fb9a0304c323a8f8a5fb99c94c35
// Fingerprint is the git rev. narHash is not in the key.

    std::optional<std::string> getFingerprint(Store & store, const Input & input) const override
    {
        if (auto rev = input.getRev())
            return rev->gitRev();
        else
            return std::nullopt;
    }

### lock_identity_split.txt

Registry / fixture:
  flake.lock nodes.dep.locked.{rev, narHash, lastModified, type}
  GitHub CI input: github:blockfrost/blockfrost-tests
  rev 5297592395d1dbd46e88247e459896838c854340
  lastModified 1770733010
  H_nar_stale = sha256-4cKMeE/8GptnxWnB6LliJy3gCvjVI34TXTwQHEsHcUA=
  H_nar_live  = sha256-YR+cemfm4AMEJcUEr/tm0cis3rWKQ0dPFbjwhEVrV94=
  in-tree: git+file dep with GIT_*_DATE pinned so lastModified is identical

Case A (consistent lock / never leftover):
  lock rev=R1 narHash=H_nar1
  nix eval -> "rev1"
  store path = computeStorePath(H_nar1)
  cache key = getFingerprint = R1 (github) or R1 plus suffixes (git)

Case B (rev moved, narHash leftover):
  lock rev=R2 narHash=H_nar1
  H_nar1 store path still present from case A
  eval may serve leftover NAR of R1 under fingerprint R2

Case C (narHash corrected on poisoned cache):
  lock rev=R2 narHash=H_nar2
  failing_ref: NAR hash mismatch / mismatch in field 'narHash'
  public log: expected H_nar_live, got H_nar_stale
  workaround: delete ~/.cache/nix/fetcher-cache-v4.sqlite

Case D (same corrected lock, fresh cache, never case B):
  eval "rev2"
  no mismatch

Not this packet:
  detached HEAD guessed ref=master, same rev, two hashed trees (#16391)
  git-lfs pointer file NAR vs smudged NAR (#10079)
  nested submodule NAR (#10588)
  github tarball NAR vs git clone NAR for an untouched lock

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

        ### Field Report: Cache Poisoning Investigation

**Operational Context:**  
Executing within a Nix environment pinned to failing_ref `d5eda907ef98fb9a0304c323a8f8a5fb99c94c35`. Reproducing cache poisoning using in-tree test knobs. Cache state actively monitored.

---

### Step 1: Establish Baseline (Case A)
```bash
# Initialize repo with two commits (R1, R2) sharing identical timestamps
export GIT_COMMITTER_DATE="2000-01-01T00:00:00+0000"
export GIT_AUTHOR_DATE="2000-01-01T00:00:00+0000"
git init dep-repo && cd dep-repo
echo "rev1" > expr && git add . && git commit -m "R1"
R1=$(git rev-parse HEAD)
echo "rev2" > expr && git commit -am "R2"
R2=$(git rev-parse HEAD)

# Create consumer flake
mkdir consumer && cat >consumer/flake.nix <<EOF
{
  inputs.dep.url = "git+file://$(pwd)";
  outputs = { self, dep }: {
    expr = dep.expr;
  };
}
EOF

# Case A: Consistent lock
nix flake lock consumer --override-input dep rev=$R1
H_nar1=$(nix eval --raw consumer#expr)  # Output: "rev1"
```

**Observation:**  
Lock stores `rev: $R1`, `narHash: $H_nar1`. Cache entry created for fingerprint `$R1` → `$H_nar1`.

---

### Step 2: Inject Poison (Case B)
```bash
# Manually corrupt lock: rev=R2 but narHash=R1's hash
jq --arg rev "$R2" '.nodes.dep.locked.rev = $rev' consumer/flake.lock > tmp && mv tmp consumer/flake.lock

# Trigger evaluation with poisoned lock
nix eval consumer#expr
```

**Observation:**  
- Substitution served existing store path for `$H_nar1` (R1's content)  
- Cache upserted new mapping: fingerprint `$R2` → `$H_nar1`  
- Output: `"rev1"` (incorrectly serving R1 content for R2 rev)  
- **Critical finding:** Cache keys on `rev` fingerprint while serving `narHash`-derived store path.

---

### Step 3: Attempt Correction (Case C)
```bash
# Compute correct H_nar2 for R2
H_nar2=$(git archive $R2 | tar xf - && nix hash path . --type sha256 --sri)

# Update lock to correct narHash
jq --arg hash "$H_nar2" '.nodes.dep.locked.narHash = $hash' consumer/flake.lock > tmp && mv tmp consumer/flake.lock

# Evaluate corrected lock
nix eval consumer#expr
```

**Failure Observed:**  
```
error: NAR hash mismatch in input 'git+file:///...', expected 'sha256-...' but got 'sha256-...'
```

**Diagnosis:**  
Cache still maps `$R2` → `$H_nar1` (poisoned entry). Evaluation attempts to:  
1. Verify store path for `$H_nar2` (correct)  
2. Find cache entry for `$R2` → returns `$H_nar1` (poisoned)  
3. Compare `$H_nar1` (cached) vs `$H_nar2` (expected) → mismatch  

---

### Step 4: Cache Forensic Inspection
```bash
# Query cache for R2 fingerprint
sqlite3 ~/.cache/nix/fetcher-cache-v4.sqlite <<EOF
SELECT value FROM CacheEntries WHERE key LIKE 'fingerprint%$R2%';
EOF
```

**Output:**  
`hash|sha256-4cKMeE/8GptnxWnB6LliJy3gCvjVI34TXTwQHEsHcUA=` (H_nar1)

**Verification:**  
```bash
# Confirm store path for H_nar1 exists
nix store path-from-hash $H_nar1  # Succeeds

# Confirm store path for H_nar2 absent
nix store path-from-hash $H_nar2  # Fails: "store path not computed"
```

---

### Step 5: Fresh Cache Validation (Case D)
```bash
rm ~/.cache/nix/fetcher-cache-v4.sqlite
nix eval consumer#expr  # Output: "rev2" (success)
```

**Cache State Post-Recovery:**  
```bash
sqlite3 ~/.cache/nix/fetcher-cache-v4.sqlite \
  "SELECT value FROM CacheEntries WHERE key LIKE 'fingerprint%$R2%'"
```
**Output:**  
`hash|sha256-YR+cemfm4AMEJcUEr/tm0cis3rWKQ0dPFbjwhEVrV94=` (H_nar2)

---

### Conclusions

1. **Cache Key Identity:**  
   Substitution cache keys **exclusively on `rev` fingerprint** (`getFingerprint()` output).  
   `narHash` is **not part of cache key** per `github_fingerprint_failing.cc`.

2. **Store Path Mapping:**  
   After Case B poisoning:  
   - Key `$R2` mapped to store path `$H_nar1`  
   - Physical store path remained unchanged (`computeStorePath(H_nar1)`)  
   - Cache associated `$R2` fingerprint with `$H_nar1` NAR hash  

3. **Failure Mechanism:**  
   Cache poisoning occurs when:  
   - `rev` changes without `narHash` update → cache writes *incorrect* `rev→old_narHash` mapping  
   - Subsequent correction of `narHash` conflicts with poisoned cache entry  

4. **Workaround Efficacy:**  
   Cache deletion works because it removes the incorrect `rev→narHash` mapping, forcing refetch.

---

### Recommended Next Steps
1. Verify fix in PR head `5ad2cd9a3051f812801a537e485aff160333da35`  
2. Audit all fetchers for consistent fingerprinting (GitHub/Git schemes differ)  
3. Consider cache key augmentation with `narHash` in fingerprint computation  

**Operational Note:**  
Poisoning risk exists *only* when manually editing lock files. Standard `nix flake update` prevents this by atomically updating `rev`+`narHash`.

        # Required response

        Return only the structured JSON object described in the external-critic contract.
        Do not wrap it in a Markdown code fence.
