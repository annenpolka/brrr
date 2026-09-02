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

npm's arborist can keep the identity of a **previous un-overridden transitive package** after a root `overrides` rule should have been a different lock object, when the path to that package crosses a `file:` / workspace Link. A Link and its target are not edge-connected. Override forwarding to the target ran while the target subtree was still unbuilt, so the guard found no matching rule and never forwarded.

On failing_ref `ae6dbeb12a6f4b313a28c99068e34ba834ae91d1`, `#buildDepStep` queues `link.target` without `link.target.updateOverridesEdgeInAdded(link.overrides)`. `#repropagateOverrides` runs after `#transplant`, before the actual tree's edges are fully resolved.

Public report (npm/cli#9659):

```
// package.json
{
  "name": "root",
  "dependencies": { "a": "file:./pkgs/a" },
  "overrides": { "brace-expansion": "2.0.1" }
}

// pkgs/a/package.json
{ "name": "a", "version": "1.0.0", "dependencies": { "glob": "7.2.0" } }
```

After `npm install`, lock/install identity is leftover `brace-expansion@1.1.15` (original), not overridden `2.0.1`. Same under hoisted and linked. The identical override works when `glob` is a direct root dependency (no Link boundary).

In-tree after the repair (not on failing_ref): forward `link.overrides` before the target subtree resolves; `#repropagateOverrides` after `calcDepFlags`; tests `overrides a nested dependency reached through a file: link`.

Case A — override path does not cross a Link (root depends on glob directly):
  lock identity is overridden 2.0.1
  not leftover original

Case B — override path crosses `file:./pkgs/a`, leftover original brace-expansion:
  leftover: 1.1.15 un-overridden identity
  nested override omitted on the Link target
  lock pins leftover original

Case C — delete node_modules + lock then install with no overrides:
  original identity is correct (not leftover of an override)

Case D — override forwarded before subtree resolve (post-repair shape, not on failing_ref):
  lock identity is 2.0.1
  not leftover original

The developer wants to know which identity case B actually left in the lock for brace-expansion: leftover original 1.1.15, overridden 2.0.1, or omitted (no brace-expansion).

# OBSERVED

Public npm/cli#9659 (closed 2026-06-26). PR 9671 squash `968e42fbd62eb3a6f446466359c9431f41d76b2b` (parent `ae6dbeb12a6f4b313a28c99068e34ba834ae91d1`). Local npm was not performed on this lab host.

Issue body: root override targeting a transitive dep is silently ignored when the path crosses a file:/workspace link; lock pins the original version; no warning.

On failing_ref, Link target is queued without forwarding OverrideSet. `#repropagateOverrides` exists for store links (#9619) but runs too early for a file: link whose subtree resolves late. Forward-before-queue is **not** on the failing revision. It is added by PR 9671.

Not this packet: specimen-004/033 optional-peer leftover (npm/cli#9876). specimen-095 nested override honored only on empty-store first install; subsequent install leftover original via addEdgeIn overwrite (npm/cli#5850). npm/cli#8986 leftover after deleting overrides (open). specimen-123/124 earthly leftover CACHE --id.

This packet does not include a local clone. Do not execute untrusted checkouts on the host.

```
# not executed on this lab host
# failing_ref ae6dbeb12a6f4b313a28c99068e34ba834ae91d1
# workspaces/arborist/lib/arborist/build-ideal-tree.js #buildDepStep
# workspaces/arborist/lib/arborist/load-actual.js #repropagateOverrides

# public shape:
# leftover brace-expansion@1.1.15 across file: link
# overrides { brace-expansion: 2.0.1 } omitted on Link target
```

Source-backed only. Do not execute untrusted checkouts on the host.

npm/cli
  workspaces/arborist/lib/arborist/build-ideal-tree.js
  workspaces/arborist/lib/arborist/load-actual.js
  workspaces/arborist/lib/override-set.js
  package-lock.json

RELEVANT MATERIAL

### build_ideal_link_failing.js

// Reduced excerpt of #buildDepStep link-target queue on failing_ref
// workspaces/arborist/lib/arborist/build-ideal-tree.js
// ae6dbeb12a6f4b313a28c99068e34ba834ae91d1
// Link target is queued. OverrideSet is not forwarded first.

          !link.target.parent &&
          !link.target.fsParent ||
          unseenLink) {
        this.addTracker('idealTree', link.target.name, link.target.location)
        this.#depsQueue.push(link.target)
      }

// load-actual.js: #repropagateOverrides runs after #transplant,
// before the actual tree's edges are fully resolved for a file: link.

### leftover_identity_split.txt

Registry / fixture:
  root overrides { brace-expansion: 2.0.1 }
  a via file:./pkgs/a depends on glob@7.2.0
  leftover lock brace-expansion@1.1.15

Case A (glob is a direct root dep, no Link):
  overridden 2.0.1
  not leftover original

Case B (path crosses file: link, leftover original):
  leftover: 1.1.15 un-overridden
  nested override omitted on Link target

Case C (no overrides field):
  original identity is correct
  not leftover of an override

Case D (OverrideSet forwarded before subtree):
  2.0.1
  not leftover original

Not this packet:
  optional-peer leftover (specimen-004/033)
  nested override subsequent-install leftover OverrideSet (specimen-095)
  leftover after deleting overrides (npm/cli#8986 open)
  earthly leftover CACHE --id (specimen-123/124)

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

        ### Field Report: Investigating npm Overrides Behavior Across `file:` Links

**Current Environment State:**
- npm version: `9.6.6` (pre-fix for npm/cli#9659)
- Reproduction case from public report (npm/cli#9659) deployed
- Directory structure initialized per Case B specification

---

### Step 1: Environment Setup Verification
```bash
# Confirm directory structure
$ tree -I node_modules
.
├── package.json
└── pkgs
    └── a
        └── package.json

# Verify package manifests
$ cat package.json
{
  "name": "root",
  "dependencies": { "a": "file:./pkgs/a" },
  "overrides": { "brace-expansion": "2.0.1" }
}

$ cat pkgs/a/package.json
{
  "name": "a",
  "version": "1.0.0",
  "dependencies": { "glob": "7.2.0" }
}
```

---

### Step 2: Install Execution (Case B)
```bash
$ npm install
added 2 packages, and audited 3 packages in 1s
found 0 vulnerabilities
```

**Installation Observations:**
- No warnings about override application failures
- No errors during dependency resolution
- `node_modules` created with expected structure:
  ```
  node_modules
  ├── a -> ./pkgs/a
  └── glob
      └── node_modules
          └── brace-expansion
  ```

---

### Step 3: Lockfile Inspection
```bash
# Extract brace-expansion lock entry
$ grep -A 10 '"brace-expansion":' package-lock.json
    "brace-expansion": {
      "version": "1.1.15",
      "resolved": "https://registry.npmjs.org/brace-expansion/-/brace-expansion-1.1.15.tgz",
      "integrity": "sha512-...",
      "dependencies": {
        "balanced-match": "^1.0.0",
        "concat-map": "0.0.1"
      },
      "engines": {
        "node": ">=0.4.0"
      }
    },
```

**Key Findings:**
1. Locked version: `1.1.15` (original transitive dependency)
2. No override metadata present in lock entry
3. No reference to overridden version `2.0.1` anywhere in lockfile

---

### Step 4: Validation Against Known Cases
**Case B Confirmation (path crosses `file:` link):**
- ✅ Lock shows original version `1.1.15`
- ✅ No override applied to transitive dependency
- ✅ Matches public report description of failure

**Contrast with Expected Fixed Behavior (Case D):**
- ⚠️ Expected overridden version `2.0.15` absent
- ⚠️ No repropagation metadata in lockfile
- ⚠️ Link boundary prevents override forwarding

---

### Step 5: Failure Isolation Test
```bash
# Remove lockfile and reinstall to confirm persistence
$ rm package-lock.json
$ npm install
# Output identical to first install
$ grep '"version":' package-lock.json | grep brace-expansion
      "version": "1.1.15",
```

**Observation:**
- Failure reproduces consistently across clean installs
- No change in behavior when reinstalling
- Override remains confined to root-level dependencies

---

### Conclusion
**For failing_ref `ae6dbeb12a6f4b313a28c99068e34ba834ae91d1` in Case B:**
1. Lockfile contains **leftover original version `1.1.15`** of `brace-expansion`
2. Override rule `2.0.1` is **silently omitted** when dependency resolution crosses `file:` link
3. No installation warnings/errors indicate override failure
4. Behavior is consistent across repeated installations

**Evidence Chain:**
- Matches public report npm/cli#9659 description
- Aligns with source analysis of missing override forwarding
- Demonstrates version pinning discrepancy versus non-link cases
- Confirms failure mode persists without environmental contamination

**Recommended Next:**
- Verify fix effectiveness in post-repair versions (≥v9.6.7) using identical test case
- Check for existence of override propagation metadata in lockfile after fix application

        # Required response

        Return only the structured JSON object described in the external-critic contract.
        Do not wrap it in a Markdown code fence.
