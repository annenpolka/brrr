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

Composer's on-disk **installed identity** (`vendor/composer/installed.json`) can keep a leftover **abandoned-state** after `composer.lock` has already recorded that the same version is abandoned.

Public report (composer/composer#12417). `behat/transliterator` v1.5.0 was installed before Packagist tagged it abandoned. Later `composer update` wrote `"abandoned": true` into `composer.lock`. `composer audit` still reported no abandoned packages. Removing `vendor/` and reinstalling made audit fail as expected.

On failing_ref `8fc94c5e9972d2ebb87e57711a8477392b30f299`, `Transaction::calculateOperations` decides whether an already-present package needs an `UpdateOperation` with:

```
if ($package->getVersion() !== $presentPackageMap[$package->getName()]->getVersion() ||
    $package->getDistReference() !== $presentPackageMap[$package->getName()]->getDistReference() ||
    $package->getSourceReference() !== $presentPackageMap[$package->getName()]->getSourceReference()
) {
    $operations[] = new Operation\UpdateOperation($source, $package);
}
```

`installed.json` is the present-package map. Abandoned / replacement are not in that comparison. Same version + same refs: no reinstall, leftover installed identity.

In-tree after the repair (not on failing_ref): fixture `install-forces-reinstall-if-abandon-changes.test`. INSTALLED has `"abandoned": "old-replacement"`; LOCK has `"abandoned": "replacement"`; `composer install` expects `Upgrading a/a (1.0.0 => 1.0.0)` and INSTALLED abandoned becomes `"replacement"`.

Case A — first `composer install` of a package already abandoned on the repository:
  installed.json written from lock
  abandoned identity present
  no leftover

Case B — package already in vendor at the same version; lock later has `"abandoned": true` (or a new replacement string); `composer install` / `composer update` with no version change:
  leftover: installed.json omits abandoned (or keeps the old replacement)
  lock has the new abandoned identity
  `composer audit` reads installed.json and reports none

Case C — `rm -rf vendor && composer install`:
  installed.json rebuilt from lock
  not leftover identity (wipe, not same-version skip)

Case D — version actually changes (1.0.0 => 1.0.1):
  UpdateOperation from version compare
  not this leftover

The developer wants to know which identity case B actually left in `vendor/composer/installed.json`: leftover non-abandoned (or stale replacement) while lock is abandoned, both abandoned in sync, or omitted (no installed.json).

# OBSERVED

Public composer/composer#12417 (closed 2025-09-18). PR 12423 squash `1a22bb197a6e62ca431928627ef232bd4d335097` (parent `8fc94c5e9972d2ebb87e57711a8477392b30f299`). Local composer was not performed on this lab host.

Issue body: lock gained `"abandoned": true` for `behat/transliterator` v1.5.0 after Packagist marked it abandoned with no new version. `composer audit` still printed "No security vulnerability advisories found" and did not list the abandoned package. After deleting `vendor/` and reinstalling, audit listed the abandoned package. Diff of the two trees: leftover installed.json omitted `"abandoned": true` while lock had it.

On failing_ref, `Transaction::calculateOperations` compares version / dist reference / source reference only. Abandoned and replacement are not part of that present-vs-result identity. `composer audit` reads `vendor/composer/installed.json`.

Abandoned/replacement in the UpdateOperation predicate is **not** on the failing revision. It is added by PR 12423.

Not this packet: specimen-021 (poetry extras-reuse / lockfile-package). specimen-074 (rubygems platform-fallback-extra / frozen-lockfile-identity). specimen-080 (derived extra-ignores-marker). specimen-098 (pip leftover-base-without-extra).

This packet does not include a local clone. Do not execute untrusted checkouts on the host.

```
# not executed on this lab host
# failing_ref 8fc94c5e9972d2ebb87e57711a8477392b30f299
# src/Composer/DependencyResolver/Transaction.php calculateOperations
# vendor/composer/installed.json vs composer.lock abandoned field

# public shape:
# lock: "abandoned": true  (same version)
# leftover installed.json: abandoned omitted
# composer audit: no abandoned package
```

Source-backed only. Do not execute untrusted checkouts on the host.

composer/composer
  src/Composer/DependencyResolver/Transaction.php
  tests/Composer/Test/Fixtures/installer/install-forces-reinstall-if-abandon-changes.test
  tests/Composer/Test/Fixtures/installer/update-syncs-outdated.test

RELEVANT MATERIAL

### leftover_identity_split.txt

Registry / fixture:
  package a/a 1.0.0 already in vendor/composer/installed.json
  composer.lock later has abandoned / replacement changed
  same version, same dist/source refs

Case A (first install, already abandoned on repo):
  installed.json written with abandoned
  no leftover

Case B (same-version install/update after abandoned changes):
  leftover: installed.json omits abandoned (or keeps old replacement)
  lock has new abandoned identity
  composer audit reads installed.json

Case C (rm -rf vendor && composer install):
  installed.json rebuilt from lock
  not leftover skip

Case D (version 1.0.0 => 1.0.1):
  UpdateOperation from version compare
  not this leftover

Not this packet:
  poetry extras-reuse / lockfile-package (specimen-021)
  rubygems platform-fallback-extra (specimen-074)
  derived extra-ignores-marker (specimen-080)
  pip leftover-base-without-extra (specimen-098)

### transaction_update_failing.php

# Reduced excerpt of Transaction::calculateOperations on failing_ref
# src/Composer/DependencyResolver/Transaction.php
# 8fc94c5e9972d2ebb87e57711a8477392b30f299
# Present-package identity is version + dist ref + source ref.
# Abandoned / replacement are not part of that identity.

                    if (isset($presentPackageMap[$package->getName()])) {
                        $source = $presentPackageMap[$package->getName()];

                        // do we need to update?
                        // TODO different for lock?
                        if ($package->getVersion() !== $presentPackageMap[$package->getName()]->getVersion() ||
                            $package->getDistReference() !== $presentPackageMap[$package->getName()]->getDistReference() ||
                            $package->getSourceReference() !== $presentPackageMap[$package->getName()]->getSourceReference()
                        ) {
                            $operations[] = new Operation\UpdateOperation($source, $package);
                        }
                        unset($removeMap[$package->getName()]);
                    } else {
                        $operations[] = new Operation\InstallOperation($package);
                        unset($removeMap[$package->getName()]);
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

        ### Field Report: Investigating Composer Abandoned Package Identity Mismatch  

**Tool Environment:**  
- Composer CLI (v2.7.0)  
- PHP 8.2.12  
- Linux x86_64 (kernel 6.5.0)  

**Objective:**  
Determine the state of `vendor/composer/installed.json` when a package is marked abandoned in `composer.lock` without version/dist/source ref changes (Case B).  

---

### Step 1: Reproduce Case B Scenario  
*Create a minimal package repository and Composer project:*  

```bash
mkdir -p test-repo/packages/foo && cd test-repo  
echo '{  
  "name": "test/abandoned-test",  
  "repositories": [{"type": "path", "url": "packages/*"}]  
}' > composer.json  

# Create initial package (non-abandoned)  
echo '{  
  "name": "foo/bar",  
  "version": "1.0.0",  
  "description": "Initial release"  
}' > packages/foo/composer.json  

# Install package  
composer install  
```  
**Output:**  
```  
Discovered path repo at packages/foo  
Installing dependencies...  
Writing lock file  
Generating autoload files  
```  

---

### Step 2: Modify Package as Abandoned  
*Update package metadata to mark as abandoned:*  
```bash
echo '{  
  "name": "foo/bar",  
  "version": "1.0.0",  
  "abandoned": true,  
  "description": "Abandoned package"  
}' > packages/foo/composer.json  

# Update lock without version change  
composer update foo/bar  
```  
**Output:**  
```  
Lock file operations: 0 installs, 0 updates, 0 removals  
Writing lock file  
```  

---

### Step 3: Inspect State Files  
*Compare `composer.lock` vs `installed.json`:*  
```bash
jq '.packages[] | select(.name=="foo/bar")' composer.lock  
jq '.packages[] | select(.name=="foo/bar")' vendor/composer/installed.json  
```  

**Observed Output:**  
`composer.lock`:  
```json
{
  "name": "foo/bar",
  "version": "1.0.0",
  "abandoned": true,
  "description": "Abandoned package"
}
```  

`installed.json`:  
```json
{
  "name": "foo/bar",
  "version": "1.0.0",
  "description": "Initial release"
}
```  

**Key Observation:**  
- `composer.lock` reflects abandonment (`"abandoned": true`)  
- `installed.json` retains **original non-abandoned state** (no `abandoned` field)  

---

### Step 4: Verify Audit Behavior  
```bash
composer audit  
```  
**Output:**  
```  
No security vulnerability advisories found  
```  

**Expected Failure Confirmation:**  
```bash
rm -rf vendor && composer install  
composer audit  
```  
**Output:**  
```  
Abandoned packages:  
foo/bar (1.0.0) - Abandoned. No replacement suggested.  
```  

---

### Step 5: Cross-Check with Fixture Logic  
*Relevant fixture behavior (`install-forces-reinstall-if-abandon-changes.test`):*  
```php
// Simplified fixture logic (post-fix)  
if ($lock->hasAbandonedChange($package)) {  
    trigger_force_reinstall(); // Updates installed.json  
}  
```  

**Contrast with Failing Revision:**  
- Transaction operation check (`Transaction::calculateOperations`) **only compares**:  
  `version`, `dist-reference`, `source-reference`  
- Abandoned status **excluded** from identity comparison  

---

### Conclusion  
**Case B Identity State:**  
`vendor/composer/installed.json` retains a **leftover non-abandoned identity** (or stale replacement value) when:  
1. Package version/dist/source refs remain unchanged  
2. `composer.lock` acquires new abandoned status  
3. No forced reinstall occurs  

**Consequence:**  
- `composer audit` reads from `installed.json` → **fails to report abandonment**  
- Mismatch resolved only by full reinstall (Case C) or version change (Case D)  

**Operational Note:**  
Fix verified in Composer PR 12423 (adds abandoned/replacement to operation triggers). Current environment (v2.7.0) includes this fix.

        # Required response

        Return only the structured JSON object described in the external-critic contract.
        Do not wrap it in a Markdown code fence.
