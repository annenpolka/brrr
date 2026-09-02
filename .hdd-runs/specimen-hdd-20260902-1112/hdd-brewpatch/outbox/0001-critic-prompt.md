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

Homebrew test-bot bottle cache can keep the identity of a **previous bottle** after a local patch file has changed. `no_diff?` diffs only the formula path against the bottle's `tap_git_revision`. Patch files listed on the formula are omitted from that identity.

On failing_ref `4f6e4df964fa22f12591ca4b27e9b52df34b9494`, `artifact_cache_valid?` is:

```
sha = local_bottle_hash(formula.name, bottle_dir: artifact_cache)
        &.dig(formula.name, "formula", "tap_git_revision")
return false if sha.blank?
return false unless no_diff?(formula, sha)
```

and `no_diff?` is:

```
relative_formula_path = formula.path.relative_path_from(repository)
!!system(git, "-C", repository, "diff", "--no-ext-diff", "--quiet", git_ref, "--",
         relative_formula_path.to_s)
```

Public report (Homebrew/brew#23588). CI for homebrew-core gcc:

```
==> brew install artifact-cache/gcc--16.2.0.tahoe.bottle.tar.gz
Notice: Bottle for gcc built at 7df12339119 (Merge e5a39e93eb ... into 860ea91cd8 ...)
```

The formula file itself was unmodified. The local patch the formula refers to changed between runs. Leftover bottle from the previous patch identity was installed.

Case A — first bottle, formula and local patch match `tap_git_revision`:
  cache valid
  not leftover after patch change

Case B — local `patches/foo.diff` edited, formula.rb unchanged, leftover bottle in artifact-cache:
  leftover: previous bottle identity
  current patch identity is the new diff
  `no_diff?` is true (formula path only)
  leftover bottle reused

Case C — formula.rb itself edited:
  `no_diff?` is false
  cache invalid
  not this leftover (formula path is the identity)

Case D — delete artifact-cache bottle then fetch:
  fresh bottle
  not leftover cache identity

The developer wants to know which identity case B actually installed: leftover previous bottle (old patch), current bottle rebuilt for the new patch, or omitted (no bottle).

# OBSERVED

Public Homebrew/brew#23588 (closed 2026-08-20; PR merged 2026-08-21). PR 23597 merge `b62af44bc2d4173d113d07648eb78a9facb73fcf` (first parent `4f6e4df964fa22f12591ca4b27e9b52df34b9494`). Local brew was not performed on this lab host.

Issue body: test-bot used a bottle from cache even though a local patch file changed without modifying the formula.

On failing_ref, `no_diff?` only passes `formula.path`. `formula.patchlist.grep(LocalPatch)` is **not** part of the cache identity.

Not this packet: Homebrew#20936 formula_auditor revision/compatibility_version (job-0539 skip axis). Distinct leftover: bottle cache identity omits local patch files so leftover previous bottle is reused after patch change.

This packet does not include a local clone. Do not execute untrusted checkouts on the host.

```
# not executed on this lab host
# failing_ref 4f6e4df964fa22f12591ca4b27e9b52df34b9494
# Library/Homebrew/test_bot/test_formulae.rb no_diff? / artifact_cache_valid?

# public shape:
# leftover artifact-cache/gcc--*.bottle.tar.gz
# formula.rb unchanged; patches/foo.diff changed
# brew install leftover bottle
```

Source-backed only. Do not execute untrusted checkouts on the host.

Homebrew/brew
  Library/Homebrew/test_bot/test_formulae.rb
  Library/Homebrew/test/test_bot/test_formulae_spec.rb
  artifact-cache/<formula>--*.bottle.tar.gz
  <tap>/patches/*.diff

RELEVANT MATERIAL

### leftover_identity_split.txt

Registry / fixture:
  artifact-cache leftover bottle
  formula.rb unchanged
  patches/foo.diff old then new
  tap_git_revision of previous bottle

Case A (formula+patch match bottle revision):
  cache valid
  not leftover after patch change

Case B (patch edited, leftover bottle):
  leftover: previous bottle identity
  no_diff? true (formula path only)
  leftover bottle installed

Case C (formula.rb edited):
  no_diff? false
  cache invalid
  not this leftover

Case D (delete artifact-cache bottle):
  fresh bottle
  not leftover cache identity

Not this packet:
  Homebrew#20936 formula_auditor revision (job-0539 skip axis)

### no_diff_failing.rb

# Reduced excerpt of no_diff? / artifact_cache_valid? on failing_ref
# Library/Homebrew/test_bot/test_formulae.rb
# 4f6e4df964fa22f12591ca4b27e9b52df34b9494
# Cache identity is formula path vs tap_git_revision. Local patches omitted.

      def no_diff?(formula, git_ref)
        return false unless repository.directory?
        @fetched_refs ||= T.let([], T.nilable(T::Array[String]))
        if @fetched_refs.exclude?(git_ref)
          test git.to_s, "-C", repository.to_s, "fetch", "origin", git_ref, ignore_failures: true
          @fetched_refs << git_ref if steps.fetch(-1).passed?
        end

        relative_formula_path = formula.path.relative_path_from(repository)
        !!system(git.to_s, "-C", repository.to_s, "diff", "--no-ext-diff", "--quiet", git_ref, "--",
                 relative_formula_path.to_s)
      end

      def artifact_cache_valid?(formula, formulae_dependents: false)
        sha = local_bottle_hash(formula.name, bottle_dir: artifact_cache)
          &.dig(formula.name, "formula", "tap_git_revision")
        return false if sha.blank?
        return false unless no_diff?(formula, sha)
        # ...
      end

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

        ### Field Report: Bottle Cache Identity Investigation  

**Operational Context**  
- Environment: Homebrew test-bot artifact cache system  
- Tool: `brew test-bot` infrastructure (existing fixture state)  
- Focus: Case B behavior (patch change, formula unchanged, leftover bottle)  

---

#### Step 1: Verify Bottle Identity via Metadata  
**Command:**  
```bash  
tar -xOf artifact-cache/gcc--16.2.0.tahoe.bottle.tar.gz \  
    gcc/16.2.0/.brew/gcc.bottle.json | jq '.formula.tap_git_revision'  
```  
**Output:**  
`"7df12339119e5a39e93eb860ea91cd8"` (bottle's recorded `tap_git_revision`)  

**Observation:**  
Bottle metadata confirms it was built at the *previous* revision (Merge `e5a39e93eb...`).  

---

#### Step 2: Cross-Reference Patch Provenance  
**Command:**  
```bash  
# Check current patch state (not in git diff)  
sha256sum patches/foo.diff  
```  
**Output:**  
`d3b07384d113edec49eaa6238ad5ff00  patches/foo.diff` (new hash)  

**Command:**  
```bash  
# Reconstruct previous patch state from bottle's git revision  
git -C repository show 7df12339119e5a39e93eb860ea91cd8:patches/foo.diff | sha256sum  
```  
**Output:**  
`c157a79031e1c40f85931829bc5fc552  -` (old hash)  

**Observation:**  
- Bottle expects patch hash `c157a7...` (matches *previous* patch).  
- Current patch is `d3b073...` (changed).  

---

#### Step 3: Simulate `artifact_cache_valid?` Check  
**Replay `no_diff?` Logic:**  
```bash  
git -C repository diff --no-ext-diff --quiet \  
    7df12339119e5a39e93eb860ea91cd8 -- Formula/gcc.rb  
echo $?  
```  
**Output:**  
`0` (success = no formula diff)  

**Observation:**  
Cache validation passes (`no_diff?` true) because:  
- Formula file (`gcc.rb`) unchanged → ignores patch mismatch.  
- System returns exit code `0` (no diff detected).  

---

#### Step 4: Confirm Installed Artifact  
**Command:**  
```bash  
brew install artifact-cache/gcc--16.2.0.tahoe.bottle.tar.gz  
brew ls --verbose gcc | grep 'patches/foo.diff'  
```  
**Output:**  
```  
/opt/homebrew/lib/patches/foo.diff (c157a79031e1c40f85931829bc5fc552)  
```  

**Observation:**  
Installed bottle contains the *old patch* (`c157a7...`), proving:  
- Leftover bottle reused verbatim.  
- Patch change did not trigger rebuild.  

---

#### Conclusion: Case B Identity  
- **Installed artifact:** Leftover previous bottle (old patch).  
- **Root cause:** Cache identity (`tap_git_revision` + formula path) excludes local patches.  
- **Failure mode:** `no_diff?` only validates formula file, not dependencies.  

**Evidence Chain:**  
1. Bottle metadata links to old git revision (`7df123...`).  
2. Old revision’s patch ≠ current patch (hash mismatch).  
3. Cache validation passed (formula unchanged).  
4. Installed files reflect old patch.  

**Next Step:**  
Patch files require inclusion in cache identity (e.g., via recursive hash of `patches/`).  

---  
**Status:** Case B resolved (leftover bottle reused).

        # Required response

        Return only the structured JSON object described in the external-critic contract.
        Do not wrap it in a Markdown code fence.
