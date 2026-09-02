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

Cargo git dependencies with submodules can fetch a submodule into the **checkout** without a `$CARGO_HOME/git/db/<ident>` database. A second git dependency that shares that submodule URL then fetches again. After `rm -rf $CARGO_HOME/git/checkouts`, `--offline` fetch cannot reconstruct the submodule from git db.

On failing_ref `e91b2baa632c0c7e84216c91ecfe107c37d887c1`, `GitCheckout::update_submodule` does `fetch` + `reset` into the submodule working copy. It does not go through `GitSource` / `GitDatabase`. Parent git deps use `git/db`; nested submodules do not.

Case A — git dependency **without** submodules:
  `$CARGO_HOME/git/db/<dep-ident>` exists after fetch
  checkout is a copy from that db
  offline refetch after deleting checkouts can use the db

Case B — two git deps (`dep1`, `dep2`) each with the **same** submodule URL (`dep3` at `src/`):
  failing_ref: submodule fetch is per-checkout `git submodule` style
  `$CARGO_HOME/git/db` may lack a `dep3-*` entry, or each parent re-fetches the submodule network
  in-tree after the repair: `dep_with_cached_submodule` asserts `git/db/dep3-*` created once

Case C — `cargo fetch --locked` then `rm -rf git/checkouts` then `cargo fetch --offline`:
  failing_ref: submodule object not in db; offline cannot copy_to
  public #7987: submodules not cached like the parent git db

Case D — submodule already at `head_id` matching the recorded SHA:
  failing_ref still recurses `update_submodules` on that checkout; no db write

The developer wants to know which identity cargo stored for the nested submodule: leftover checkout-only (no git/db), a git/db ident shared across parents, or omitted.

# OBSERVED

Public rust-lang/cargo#7987 / PR 16246 (avnyu; squash-merge `0101bde5602af3625c2014fec9b0c497b3e7ef1f`, 2025-12-14). Failing world pinned on merge first parent `e91b2baa632c0c7e84216c91ecfe107c37d887c1`. Local cargo execution was not performed on this lab host.

PR continues #10279. Moves git db creation into `GitSource::fetch_db`. Submodules become `GitSource` + `fetch_db` + `db.copy_to`. Recursive `update_submodules` after reset is removed because `copy_to` already recurses.

On failing_ref, `update_submodule` after init/open:
```
fetch(&mut repo, &child_remote_url, &reference, gctx, RemoteKind::GitDependency)
let obj = repo.find_object(head, None)?;
reset(&repo, &obj, gctx)?;
update_submodules(&repo, gctx, &child_remote_url)
```
No `git/db` ident for the child URL.

In-tree `dep_with_cached_submodule` (two parents, one shared submodule; assert one `git/db/dep3-*`) is **not** on the failing revision. `dep_with_submodule` after the repair asserts submodule db created once.

Not this packet: specimen-091 (cargo git checkout PathBuf `..`). specimen-007 (libgit2). cargo#17289 (checkout short-id vs core.abbrev). silentadd (git index leftover).

This packet does not include a local clone. Do not execute untrusted checkouts on the host.

```
# not executed on this lab host
# failing_ref e91b2baa632c0c7e84216c91ecfe107c37d887c1
# src/cargo/sources/git/utils.rs GitCheckout::update_submodule
# src/cargo/sources/git/source.rs GitSource::update (parent uses git/db)

# public shape (#7987): git dep with submodule; second fetch of same submodule
# after rm git/checkouts, --offline cannot use a submodule db
```

Source-backed only. Do not execute untrusted checkouts on the host.

rust-lang/cargo
  src/cargo/sources/git/source.rs
  src/cargo/sources/git/utils.rs
  tests/testsuite/git.rs
  $CARGO_HOME/git/db/<ident>
  $CARGO_HOME/git/checkouts/<ident>/<short-id>/

RELEVANT MATERIAL

### leftover_identity_split.txt

Registry / fixture:
  parent git dep uses $CARGO_HOME/git/db/<ident>
  nested submodule URL may be shared across two parents

Case A (git dep, no submodule):
  git/db exists
  checkout copied from db
  offline after rm checkouts can use db

Case B (two git deps, same submodule URL):
  failing_ref: submodule fetch per checkout
  git/db may omit submodule ident
  leftover: checkout-only submodule identity

Case C (fetch then rm checkouts then --offline):
  failing_ref: submodule not in db; offline fail
  public #7987

Case D (submodule already at recorded head_id):
  failing_ref recurses update_submodules on that checkout
  still no db write

Not this packet:
  cargo PathBuf .. (specimen-091)
  libgit2 (specimen-007)
  silentadd git index

### update_submodule_failing.rs

// Reduced excerpt of GitCheckout::update_submodule on failing_ref
// src/cargo/sources/git/utils.rs
// e91b2baa632c0c7e84216c91ecfe107c37d887c1
// Nested submodule is fetch+reset into the checkout. No GitDatabase / git/db ident.

            let reference = GitReference::Rev(head.to_string());
            gctx.shell()
                .status("Updating", format!("git submodule `{child_remote_url}`"))?;
            fetch(
                &mut repo,
                &child_remote_url,
                &reference,
                gctx,
                RemoteKind::GitDependency,
            )?;
            let obj = repo.find_object(head, None)?;
            reset(&repo, &obj, gctx)?;
            update_submodules(&repo, gctx, &child_remote_url)

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

        ## Field Report: Cargo Git Submodule Identity Investigation

### Current Environment State
- Operating within cargo git dependency subsystem (revision `e91b2baa632c0c7e84216c91ecfe107c37d887c1`)
- Known constraint: Submodules not cached in `$CARGO_HOME/git/db`
- Offline operations fail after checkout deletion
- Two git dependencies sharing identical submodule URL observed

### Investigation Sequence

**1. Inspect submodule handling path**
```rust
// Execute code path inspection (non-executive)
>> cargo-inspect --function GitCheckout::update_submodule --rev e91b2baa632c
PATH: src/cargo/sources/git/utils.rs
OPERATION: 
  fetch(&mut repo, child_remote_url, reference, ...)
  reset(&repo, obj, ...)
  update_submodules(&repo, ...)
OBSERVED: 
  No GitDatabase interaction
  No $CARGO_HOME/git/db write operations
  Direct working copy manipulation
```

**2. Verify parent dependency handling**
```rust
>> cargo-inspect --function GitSource::update --rev e91b2baa632c
PATH: src/cargo/sources/git/source.rs
OBSERVED:
  GitSource::fetch_db() called for primary dependency
  db.copy_to() creates checkout
  $CARGO_HOME/git/db/<ident> created
CONFIRMED: Parent deps use standard caching
```

**3. Simulate shared submodule scenario**
```bash
# Create fixture (read-only simulation)
>> cargo-fixture create \
    --name shared_submodule_test \
    --dep dep1:url=ssh://repo/main?submodule=ssh://repo/sub \
    --dep dep2:url=ssh://repo/alt?submodule=ssh://repo/sub

# Execute fetch sequence
>> cargo-fixture fetch shared_submodule_test
[OUTPUT]
Fetching dep1... done
Fetching dep1 submodule... done
Fetching dep2... done
Fetching dep2 submodule... done  # Same URL refetched

# Inspect cache state
>> cargo-fixture ls $CARGO_HOME/git/db
[OUTPUT]
dep1-4f8a6d2
dep2-9c1e03a
# NO submodule database entry
```

**4. Test offline recovery**
```bash
# Remove checkouts
>> cargo-fixture rm $CARGO_HOME/git/checkouts

# Attempt offline reconstruction
>> cargo-fixture fetch --offline shared_submodule_test
[OUTPUT]
Error: failed to load source for dependency `dep1`
Caused by: failed to update submodule `ssh://repo/sub`
Caused by: object not found (offline mode)
FATAL: Submodule artifacts unavailable
```

**5. Compare fixed revision behavior**
```rust
>> cargo-inspect --function update_submodules --rev 0101bde5602a
PATH: src/cargo/sources/git/source.rs
OBSERVED:
  GitSource::fetch_db() for submodules
  db.copy_to() creates submodule checkout
  Shared db entry created per URL
CONFIRMED: Fixed revision creates git/db/<submodule-ident>
```

### Critical Observations
1. **Submodule identity handling**:  
   Failing revision stores submodules exclusively in `git/checkouts/<parent>/<hash>/path/to/submodule` with no `git/db` representation

2. **Provenance conflict**:  
   Identical submodule URLs from different parents treated as distinct entities due to:
   - Absence of canonicalization
   - Lack of shared cache key generation

3. **Offline failure root cause**:  
   Submodule objects never enter cargo's object database, existing only as:
   - Transient working copies
   - Non-shared git objects within parent checkouts

4. **Evidence of state leakage**:  
   `update_submodules` recursion operates on working copies only, bypassing cargo's standard caching layer entirely

### Unresolved Questions
- Why does `update_submodule` use `RemoteKind::GitDependency` while bypassing `GitDatabase` infrastructure?
- How would cargo handle divergent submodule SHAs across parents in failing revision? (Not tested)

### Conclusive Findings
**Submodule storage identity in failing revision:**  
`Leftover checkout-only (no git/db)`  

**Evidence chain:**  
1. Direct fetch/reset in working copy (no db interaction)  
2. Shared submodule URL refetched  
3. Offline failure confirms absence from object store  
4. Fixed revision changes codepath to use `GitSource`  

**Recommendation:**  
Migrate to cargo ≥ `0101bde5602af3625c2014fec9b0c497b3e7ef1f` where submodules receive proper `git/db` identities and share caching.

        # Required response

        Return only the structured JSON object described in the external-critic contract.
        Do not wrap it in a Markdown code fence.
