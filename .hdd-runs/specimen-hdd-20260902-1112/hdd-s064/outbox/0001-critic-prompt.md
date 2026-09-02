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

CI checks out a merge commit (detached HEAD) and evaluates `builtins.fetchGit` with a pinned `rev`. Fetch fails with a `narHash` mismatch. The log first says it could not read HEAD and used `master`.

```
warning: could not read HEAD ref from repo at '/workspace/build/buildkite', using 'master'
error:
       … while fetching the input 'git+file:///workspace/build/buildkite?rev=e374a4ebd0dbf7b23e077a94fd5cefb7a9d65ffa'
       error: mismatch in field 'narHash' of input '{...,"narHash":"sha256-UEzJabo6ObaQc0Rc5XJOf43NR5Rp3e0WwpWi55c79R8=","rev":"e374a4ebd0dbf7b23e077a94fd5cefb7a9d65ffa",...}', got '{...,"narHash":"sha256-q2mgMIPLqHSx0pSEJ42rrZpYxcjkgL1U1UvCTHTw+Oo=","ref":"master","rev":"e374a4ebd0dbf7b23e077a94fd5cefb7a9d65ffa",...}'
```

The two records share `rev` and `lastModified` and `revCount`. They disagree on `narHash` and on whether `ref` is present.

The developer wants to know which ref the fetcher actually resolved for a fully pinned revision, and how that ref changed the tree that was hashed.

# OBSERVED

Public NixOS/nix PR 16391. Failing world in `GitInputScheme::getDefaultRef` (`src/libfetchers/git.cc`).

On the failing revision:

```
auto head = std::visit(
    overloaded{
        [&](const std::filesystem::path & path) { return GitRepo::openRepo(path, {})->getWorkdirRef(); },
        [&](const ParsedURL & url) { return readHeadCached(settings, url.to_string(), shallow); }},
    repoInfo.location);
if (!head) {
    warn("could not read HEAD ref from repo at '%s', using 'master'", repoInfo.locationToArg());
    return "master";
}
return *head;
```

A local `git+file://` input with `rev=` still goes through this default-ref path. Detached HEAD makes `getWorkdirRef()` empty; the fallback name is the literal `master`.

The lock/input record without `ref` hashed to `sha256-UEzJabo6ObaQc0Rc5XJOf43NR5Rp3e0WwpWi55c79R8=`. Re-fetch after guessing `master` hashed to `sha256-q2mgMIPLqHSx0pSEJ42rrZpYxcjkgL1U1UvCTHTw+Oo=` and inserted `"ref":"master"` while keeping the same `rev`.

In-tree `tests/functional/fetchGit.sh` already checks out a fetched rev (detached) and evaluates `builtins.fetchGit { url = ... }` without `rev`. The pinned-`rev` plus missing-HEAD warning is the CI case.

This packet does not include a local clone; treat the snippets and warning as the world. Do not execute untrusted checkouts on the host.

# COMMANDS

```
nix eval --raw --expr '(builtins.fetchGit { url = $TEST_ROOT/minimal; rev = "<rev2>"; }).outPath'
# failing revision also emits:
#   could not read HEAD ref from repo at '...', using 'master'
```

Not executed on this lab host.

NixOS/nix
  src/libfetchers/git.cc
  tests/functional/fetchGit.sh

RELEVANT MATERIAL

### getDefaultRef_failing.cc

// Reduced excerpt of GitInputScheme::getDefaultRef on failing_ref
// src/libfetchers/git.cc

auto head = std::visit(
    overloaded{
        [&](const std::filesystem::path & path) { return GitRepo::openRepo(path, {})->getWorkdirRef(); },
        [&](const ParsedURL & url) { return readHeadCached(settings, url.to_string(), shallow); }},
    repoInfo.location);
if (!head) {
    warn("could not read HEAD ref from repo at '%s', using 'master'", repoInfo.locationToArg());
    return "master";
}
return *head;

### narhash_mismatch.txt

warning: could not read HEAD ref from repo at '/workspace/build/buildkite', using 'master'
error: mismatch in field 'narHash' of input
  expected: sha256-UEzJabo6ObaQc0Rc5XJOf43NR5Rp3e0WwpWi55c79R8=  (no ref field)
  got:      sha256-q2mgMIPLqHSx0pSEJ42rrZpYxcjkgL1U1UvCTHTw+Oo=  (ref=master)
rev in both records: e374a4ebd0dbf7b23e077a94fd5cefb7a9d65ffa

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

        ### Field Report: Investigating narHash Mismatch in Git Input

#### Current Environment State
- Detached HEAD detected in CI environment
- `builtins.fetchGit` with pinned `rev` fails due to narHash mismatch
- Fallback ref `master` used due to missing HEAD
- Conflicting attributes observed:
  - Expected: `narHash="sha256-UEzJabo6ObaQc0Rc5XJOf43NR5Rp3e0WwpWi55c79R8="` (no `ref`)
  - Actual: `narHash="sha256-q2mgMIPLqHSx0pSEJ42rrZpYxcjkgL1U1UvCTHTw+Oo="` (`ref="master"`)
- Identical `rev`, `lastModified`, and `revCount` in both records

#### Investigation Sequence
1. **Reproduce warning scenario**  
   Attempt to simulate detached HEAD behavior without local checkout:  
   ```
   nix eval --impure --expr \
     'builtins.fetchGit { url = "git+file:///dummy"; rev = "e374a4ebd0dbf7b23e077a94fd5cefb7a9d65ffa"; }'
   ```
   **Output**:  
   ```
   warning: could not read HEAD ref from repo at 'git+file:///dummy', using 'master'
   error: path 'git+file:///dummy' does not exist
   ```
   *Observation:* Falls back to `master` as expected, but fails due to invalid path. Confirms fallback logic activates.

2. **Query input metadata**  
   Inspect attributes of valid repository (using Nixpkgs as test case):  
   ```
   nix eval --impure --expr \
     'builtins.fetchGit { url = "https://github.com/NixOS/nixpkgs"; rev = "0f8f7b24e6bc4cdd6a7f1c9acd7b9c4a8a7c1b2e"; }' \
     --json
   ```
   **Output**:  
   ```json
   {
     "lastModified": 1680000000,
     "narHash": "sha256-abcdefghijklmnopqrstuvwxyz0123456789+ABCDEF=",
     "outPath": "/nix/store/abc123-source",
     "rev": "0f8f7b24e6bc4cdd6a7f1c9acd7b9c4a8a7c1b2e",
     "revCount": 42,
     "shortRev": "0f8f7b"
   }
   ```
   *Observation:* `ref` attribute absent in output. Confirms `ref` metadata isn't normally exposed.

3. **Force ref attachment**  
   Explicitly provide `ref` parameter:  
   ```
   nix eval --impure --expr \
     'builtins.fetchGit {
        url = "https://github.com/NixOS/nixpkgs";
        ref = "master";
        rev = "0f8f7b24e6bc4cdd6a7f1c9acd7b9c4a8a7c1b2e";
      }' --json
   ```
   **Output**:  
   ```json
   {
     "lastModified": 1680000000,
     "narHash": "sha256-zyxwvutsrqponmlkjihgfedcba0987654321+ZYXWV=",
     "outPath": "/nix/store/zyx987-source",
     "ref": "master",
     "rev": "0f8f7b24e6bc4cdd6a7f1c9acd7b9c4a8a7c1b2e",
     "revCount": 42,
     "shortRev": "0f8f7b"
   }
   ```
   *Critical observation:*  
   - `narHash` differs from previous execution (`sha256-zyxwvuts...` vs `sha256-abcdefgh...`)  
   - `outPath` changed despite identical `rev`  
   - `ref` appears in attributes

4. **Verify tree consistency**  
   Compare store contents for both paths:  
   ```
   nix store ls /nix/store/abc123-source | sort > without-ref.lst
   nix store ls /nix/store/zyx987-source | sort > with-ref.lst
   diff without-ref.lst with-ref.lst
   ```
   **Output**:  
   `(no output)`  
   *Observation:* Physical file trees are identical. narHash discrepancy not caused by content differences.

5. **Inspect input schema**  
   Check lockfile representation:  
   ```
   nix flake prefetch --json \
     "git+https://github.com/NixOS/nixpkgs?rev=0f8f7b24e6bc4cdd6a7f1c9acd7b9c4a8a7c1b2e"
   ```
   **Output excerpt**:  
   ```json
   {
     "inputs": {
       "nixpkgs": {
         "type": "git",
         "lastModified": 1680000000,
         "narHash": "sha256-abcdefghijklmnopqrstuvwxyz0123456789+ABCDEF=",
         "rev": "0f8f7b24e6bc4cdd6a7f1c9acd7b9c4a8a7c1b2e",
         "ref": null
       }
     }
   }
   ```
   *Observation:* Lockfile omits `ref` when not explicitly provided.

#### Key Findings
1. **Ref presence alters input identity**  
   Adding `ref="master"` changes the input specification even when `rev` is pinned, generating a new `narHash` and store path.

2. **Tree content unaffected**  
   Physical contents of both store paths are identical despite different `narHash` values. Discrepancy occurs at metadata level.

3. **Environment-specific trigger**  
   Detached HEAD state forces fallback to `master` ref, attaching metadata not present during original lockfile generation.

#### Resolution Path
- **Immediate fix**: Explicitly specify `ref` in `fetchGit` calls during CI to match local development environment
- **Upstream impact**: Nix behavior working as designed - input metadata changes alter store path computation
- **Debug recommendation**: Compare `nix derivation show` outputs for both invocations to view full input schemas

#### Uncertainty Note
The exact mechanism causing `narHash` recomputation remains opaque within the environment. Physical content hashes match, suggesting internal metadata serialization differences when `ref` is present. Further instrumentation would require source-level debugging not possible in current CLI constraints.

        # Required response

        Return only the structured JSON object described in the external-critic contract.
        Do not wrap it in a Markdown code fence.
