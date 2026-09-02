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

bazel-contrib `rules_distroless` apt extension can keep the identity of **previous snapshot facts / packages** after the snapshot URL was upgraded and the package index should have been different. The facts cache key is `dist/component/architecture/Packages` (and Contents). Snapshot URLs are not part of that key. Upgrading the snapshot while leaving dist/component/arch the same still returns leftover previous integrity facts and stale packages.

On failing_ref `42dd9a20c5c761e4131325a2cf594a753ffffa2d`:

```
pkg_fact_key = dist + "/" + component + "/" + architecture + "/Packages"
cnt_fact_key = dist + "/" + component + "/" + architecture + "/Contents"
```

`mctx.facts` then serves `glock.facts().get(pkg_fact_key)` as the integrity for a cache HIT. The URL of the snapshot is not in the key.

Public report (bazel-contrib/rules_distroless#237). Same dist/component/arch; snapshot URL flipped from `.../20251001T023456Z` to `.../20240210T223313Z`; leftover previous facts and stale packages. Rolling suites were already filtered; snapshot suites reused the omitted-URL key.

In-tree after the repair (not on failing_ref): `util.index_fact_key(dist, component, architecture, index_type, urls)` appends a sorted-deduplicated URL token; unused previous-URL facts are pruned.

Case A — second fetch, same snapshot URLs, same dist/component/arch:
  cache identity is current
  not leftover-after-upgrade

Case B — snapshot URL upgraded, leftover facts hit:
  leftover: previous integrity / stale packages
  snapshot URL omitted from fact key
  same dist/component/arch

Case C — facts empty / first fetch / rolling suite not cached:
  fresh index identity
  not leftover previous facts

Case D — snapshot URLs in the fact key (post-repair shape, not on failing_ref):
  new facts after snapshot upgrade
  not leftover previous packages

The developer wants to know which identity case B actually used for the package index after the snapshot URL change: leftover previous-facts packages (URL omitted), current snapshot index, or omitted (no facts cache).

# OBSERVED

Public bazel-contrib/rules_distroless#237 (merged 2026-07-28). Squash `52a250a1135cd35440a3ff6616fc4f6ebd4819a0` (parent `42dd9a20c5c761e4131325a2cf594a753ffffa2d`). Local rules_distroless was not performed on this lab host.

PR body: the URL of the snapshot was not part of the cache key for facts. Upgrading the snapshot (everything else the same) yielded stale facts and stale packages. Repair bakes snapshot source URLs into the facts key and prunes facts from unused URLs.

On failing_ref, `_fetch_and_parse_sources` builds `pkg_fact_key` from dist/component/architecture only, then `glock.facts().get(pkg_fact_key)` on snapshot suites.

Not this packet: bazel#29298 `env_inherit` action cache local vs remote (SKIP unfixed). specimen-064/070 nix leftover. specimen-136 pants leftover vcs_version.

This packet does not include a local clone. Do not execute untrusted checkouts on the host.

```
# not executed on this lab host
# failing_ref 42dd9a20c5c761e4131325a2cf594a753ffffa2d
# apt/extensions.bzl pkg_fact_key / mctx.facts

# public shape:
# leftover snapshot facts after snapshot URL upgrade
# fact key is dist/component/arch/Packages; URL omitted
# empty facts / URL in key yields the new index
```

Source-backed only. Do not execute untrusted checkouts on the host.

bazel-contrib/rules_distroless
  apt/extensions.bzl
  apt/private/util.bzl

RELEVANT MATERIAL

### facts_failing.bzl

# Reduced excerpt of apt facts key on failing_ref
# apt/extensions.bzl
# 42dd9a20c5c761e4131325a2cf594a753ffffa2d
# pkg_fact_key is dist/component/arch/Packages. snapshot URL omitted.
# leftover previous integrity after snapshot URL upgrade.

pkg_fact_key = dist + "/" + component + "/" + architecture + "/Packages"
cnt_fact_key = dist + "/" + component + "/" + architecture + "/Contents"
cached_pkg_format = formats.get(pkg_fact_key)
# glock.facts().get(pkg_fact_key) is the leftover integrity on HIT

### leftover_identity_split.txt

Registry / fixture:
  rules_distroless apt mctx.facts
  leftover snapshot facts after URL upgrade

Case A (second fetch, same snapshot URLs):
  current cache identity
  not leftover-after-upgrade

Case B (snapshot URL upgraded, leftover facts hit):
  leftover: previous integrity / stale packages
  snapshot URL omitted from fact key
  same dist/component/arch

Case C (facts empty / rolling suite):
  fresh index identity
  not leftover previous facts

Case D (snapshot URLs in the fact key):
  new facts after snapshot upgrade
  not leftover previous packages

Not this packet:
  bazel#29298 env_inherit local vs remote (SKIP unfixed)
  nix leftover (specimen-064/070)
  pants leftover vcs_version (specimen-136)

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

        ### Field Report: Investigating `rules_distroless` Apt Fact Cache Behavior  

**Operational Context**  
Using the installed `cachekey-analyzer` CLI tool (v3.1.0) to inspect fact-key construction for apt indices. The tool accepts structured inputs (dist/component/arch) and outputs cache keys, validity flags, and identity classifications aligned with the known cases (A/B/C/D).  

---

#### Step 1: Recreate failing_ref cache key construction  
*Command:*  
```bash
cachekey-analyzer generate \
  --dist "bullseye" \
  --component "main" \
  --arch "amd64" \
  --index-type "Packages" \
  --behavior omit-url
```  

*Output:*  
```
KEY: bullseye/main/amd64/Packages  
CASE: B (URL OMITTED)  
WARNING: Key excludes URL(s). Stale hits possible if URL changes.  
```  

**Observation:**  
- Key matches failing_ref structure (`dist/component/architecture/Packages`).  
- Tool explicitly classifies this as **Case B** (URL upgrade → stale hit risk).  

---

#### Step 2: Simulate snapshot URL upgrade  
*Scenario:* Same dist/component/arch, but snapshot URL changes from `old-snapshot` → `new-snapshot`.  

*Command (with URL change):*  
```bash
cachekey-analyzer generate \
  --dist "bullseye" \
  --component "main" \
  --arch "amd64" \
  --index-type "Packages" \
  --behavior omit-url \
  --urls "https://snapshot.debian.org/archive/debian/20251001T023456Z" \
  --urls "https://snapshot.debian.org/archive/debian/20240210T223313Z"
```  

*Output:*  
```
KEY: bullseye/main/amd64/Packages  
CASE: B (URL OMITTED)  
WARNING: Key unchanged despite URL change. Previous facts remain valid.  
```  

**Observation:**  
- Key **unchanged** despite different URLs → cache hit on prior facts.  
- Tool confirms stale packages would persist (Case B).  

---

#### Step 3: Contrast with repaired behavior (Case D)  
*Command (include URLs in key):*  
```bash
cachekey-analyzer generate \
  --dist "bullseye" \
  --component "main" \
  --arch "amd64" \
  --index-type "Packages" \
  --behavior hash-urls \
  --urls "https://snapshot.debian.org/archive/debian/20240210T223313Z"
```  

*Output:*  
```
KEY: bullseye/main/amd64/Packages/urlsha256:6d4f123...b7a  
CASE: D (URLS INCLUDED)  
NOTE: Key changes if URLs change. Forces cache miss on snapshot upgrade.  
```  

**Observation:**  
- Key now includes URL-derived token → triggers cache miss when URLs change (Case D).  
- Differs from failing_ref (Case B) where URL absence caused stale hits.  

---

#### Step 4: Verify Case C (no prior facts)  
*Command (force empty cache):*  
```bash
cachekey-analyzer generate \
  --dist "bullseye" \
  --component "main" \
  --arch "amd64" \
  --index-type "Packages" \
  --cache-state empty
```  

*Output:*  
```
KEY: bullseye/main/amd64/Packages  
CASE: C (NO PRIOR FACTS)  
ACTION: Cache miss. Fresh fetch required.  
```  

**Observation:**  
- Same key as Case B but no prior facts → fresh fetch (Case C).  
- Confirms **only Case B** reuses stale facts when URLs change.  

---

### Conclusion  
For **Case B (snapshot URL upgrade)**:  
- The environment used **leftover previous-facts packages** (identity from prior snapshot).  
- Root cause: Cache key (`dist/component/architecture/Packages`) **excluded URLs** → unchanged key reused stale facts.  
- Provenance: Failing_ref's key design caused cache hits to ignore URL changes.  

**Next step**: Apply URL-including keys (Case D) to prevent recurrence.  

---

> **Operator Note**:  
> All commands executed against `cachekey-analyzer`’s built-in fixture matching `rules_distroless` failing_ref behavior. No untrusted checkouts performed. Tool available for further case validation via `cachekey-analyzer verify --case <A|B|C|D>`.

        # Required response

        Return only the structured JSON object described in the external-critic contract.
        Do not wrap it in a Markdown code fence.
