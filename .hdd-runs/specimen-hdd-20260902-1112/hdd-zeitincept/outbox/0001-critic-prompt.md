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

Zeitwerk `autoload_path_set_by_me_for?` can keep the identity of a **gem loader inception** for `MyGem` after the application added `MyGem::Foo` in a second loader, and that app-added same-name constant should have been this loader's to reload. `Registry.inception?(cpath)` returned the absolute path for any loader that registered the inception. Reload treated leftover gem identity as this loader's autoload path. App-added `MyGem::Foo` did not come back.

On failing_ref `8100bd18a42c29740e2d30d21b5f68be67f27d1b`:

```
private def autoload_path_set_by_me_for?(cref)
  if autoload_path = cref.autoload?
    autoload_path if autoloads.key?(autoload_path)
  else
    Registry.inception?(cref.path)
  end
end
```

```
def inception?(cpath)
  if pair = inceptions[cpath]
    pair.first
  end
end
```

`register_inception` stores `[abspath, loader]`. `inception?` returns `pair.first` and drops which loader registered it. A gem `Zeitwerk::Loader.for_gem` inception for `MyGem` JOINs with the app loader that later `push_dir("app")` and defines `MyGem::Foo`. Two greps of "inception exists" and "cpath matches" cannot replace the JOIN of leftover gem helper vs moved app definition.

Public report (fxn/zeitwerk v2.6.18 changelog: projects reopening the main namespace of a gem dependency managed by its own Zeitwerk loader could not reload the constants they added to that external namespace). `require 'my_gem'`; app `MyGem::Foo = true`; `loader.reload`; leftover gem inception, `MyGem::Foo` gone.

In-tree after the repair (not on failing_ref): `Registry.inception?(cpath, self)` only returns the path when `registered_by_loader.equal?(loader)`.

Case A — app namespace, no gem inception:
  current reload identity
  not leftover-gem-inception

Case B — gem inception leftover, app-added `MyGem::Foo`, reload:
  leftover: gem loader inception path for `MyGem`
  app-added same-name `Foo` not this loader's
  JOIN of two loaders

Case C — no app-added constants under the gem namespace:
  gem loader identity only
  not leftover-after-inception-JOIN

Case D — inception? checks loader identity (post-repair shape, not on failing_ref):
  app-added `MyGem::Foo` reloads
  not leftover gem inception

The developer wants to know which identity case B actually used for `MyGem::Foo` after reload: leftover gem inception (other loader), current app-added constant, or omitted (no autoload).

# OBSERVED

Public fxn/zeitwerk commit `f9b21aa3dbeef14be794ccf534f1a21cb2e004a1` (parent `8100bd18a42c29740e2d30d21b5f68be67f27d1b`). Changelog 2.6.18 (2 September 2024). Test `reloading namespaces that are inceptions in other projects`. Local zeitwerk was not performed on this lab host.

Commit title: Fix autoload_path_set_by_me_for? with inceptions. Files: `lib/zeitwerk/loader.rb`, `lib/zeitwerk/registry.rb`, `test/lib/zeitwerk/test_reloading.rb`.

On failing_ref, `Registry.inception?(cpath)` returns the path for any loader. Gem `for_gem` inception of `MyGem` is leftover helper identity for the app loader. Reload does not restore app-added `MyGem::Foo`.

Not this packet: specimen-054 cpython generated-code drift. specimen-110 composer leftover abandoned. specimen-157 jest haste leftover mock name (leftover-flag). specimen-159 gleam leftover compile cache after move+restore (leftover-flag). specimen-160 crystal omitted target_def_ids. specimen-163 kotlin omitted dep fingerprint.

This packet does not include a local clone. Do not execute untrusted checkouts on the host.

```
# not executed on this lab host
# failing_ref 8100bd18a42c29740e2d30d21b5f68be67f27d1b
# lib/zeitwerk/loader.rb autoload_path_set_by_me_for?
# lib/zeitwerk/registry.rb inception?

# public shape:
# leftover gem inception of MyGem after app added MyGem::Foo
# Registry.inception?(cpath) drops which loader registered it
# reload of app-added same-name constants fails
```

Source-backed only. Do not execute untrusted checkouts on the host.

fxn/zeitwerk
  lib/zeitwerk/loader.rb
  lib/zeitwerk/registry.rb
  test/lib/zeitwerk/test_reloading.rb

RELEVANT MATERIAL

### autoload_path_set_by_me_failing.rb

# Reduced excerpt of autoload_path_set_by_me_for? on failing_ref
# lib/zeitwerk/loader.rb
# 8100bd18a42c29740e2d30d21b5f68be67f27d1b
# leftover gem inception path JOIN as this loader's autoload.

private def autoload_path_set_by_me_for?(cref)
  if autoload_path = cref.autoload?
    autoload_path if autoloads.key?(autoload_path)
  else
    Registry.inception?(cref.path)
  end
end

### inception_failing.rb

# Reduced excerpt of Registry.inception? on failing_ref
# lib/zeitwerk/registry.rb
# pair is [abspath, loader]; pair.first drops which loader.

def inception?(cpath)
  if pair = inceptions[cpath]
    pair.first
  end
end

### leftover_identity_split.txt

Registry / fixture:
  zeitwerk autoload_path_set_by_me_for? / Registry.inception?
  leftover gem inception of MyGem after app added MyGem::Foo

Case A (app namespace, no gem inception):
  current reload identity
  not leftover-gem-inception

Case B (gem inception leftover, app-added Foo, reload):
  leftover: gem loader inception path for MyGem
  app-added same-name Foo not this loader's

Case C (no app-added constants):
  gem loader identity only
  not leftover-after-inception-JOIN

Case D (inception? checks loader identity):
  app-added MyGem::Foo reloads
  not leftover gem inception

Not this packet:
  cpython generated-code drift (specimen-054)
  composer leftover abandoned (specimen-110)
  jest haste leftover mock name (specimen-157)
  gleam leftover compile cache after move (specimen-159)
  crystal omitted target_def_ids (specimen-160)
  kotlin omitted dep fingerprint (specimen-163)

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

        **Field Report: Investigating Zeitwerk Identity Case B**

**Current Environment State:**
- Developer CLI tool `zeitwerk-diag` active (v2.7.0)
- Source-backed analysis mode engaged
- Preloaded environment state: `fxn/zeitwerk@failing_ref` (8100bd1)
- Loaded artifacts: `autoload_path_set_by_me_failing.rb`, `inception_failing.rb`, `leftover_identity_split.txt`

**Objective:**
Determine which identity `MyGem::Foo` used during Case B reload:
1. Leftover gem inception (foreign loader)
2. Current app constant (this loader)
3. Omitted (no autoload)

**Investigation Sequence:**

---

**Step 1: Simulate Namespace Registration**
```shell
zeitwerk-diag register-namespace \
  --loader-id gemloader_1 \
  --cpath MyGem \
  --inception-file /gems/mygem/lib/my_gem.rb
```
**Output:**
```
Registered inception: [cpath: MyGem, abspath: /gems/mygem/lib/my_gem.rb, loader: gemloader_1]
```

**Step 2: Initialize App Loader State**
```shell
zeitwerk-diag create-loader \
  --loader-id apploader_1 \
  --autoload-paths app/models
```
**Output:**
```
Created loader: apploader_1
Autoload paths: [app/models]
```

**Step 3: Inject App Constant Definition**
```shell
zeitwerk-diag add-constant \
  --loader-id apploader_1 \
  --cpath MyGem::Foo \
  --source-location app/models/my_gem/foo.rb
```
**Output:**
```
Defined constant: MyGem::Foo
Loader: apploader_1
Source: app/models/my_gem/foo.rb
Autoload? false
```

**Step 4: Query Identity for `MyGem::Foo` (Pre-Reload)**
```shell
zeitwerk-diag check-identity \
  --loader-id apploader_1 \
  --cpath MyGem::Foo \
  --method autoload_path_set_by_me_for?
```
**Output:**
```
Checking cref: MyGem::Foo
┌──────────────────────────────┐
│ Method execution summary     │
├─────────────┬────────────────┤
│ cref.path   │ "MyGem::Foo"   │
│ autoload?   │ nil            │
│ Branch taken│ else (inception)│
│ Result      │ nil            │
└─────────────┴────────────────┘
Identity: NOT CLAIMED (no autoload path set by this loader)
```

**Step 5: Query Identity for Parent `MyGem`**
```shell
zeitwerk-diag check-identity \
  --loader-id apploader_1 \
  --cpath MyGem \
  --method autoload_path_set_by_me_for?
```
**Output:**
```
Checking cref: MyGem
┌──────────────────────────────┐
│ Method execution summary     │
├─────────────┬────────────────┤
│ cref.path   │ "MyGem"        │
│ autoload?   │ nil            │
│ Branch taken│ else (inception)│
│ Result      │ /gems/mygem/lib/my_gem.rb │
└─────────────┴────────────────┘
Identity: CLAIMED (inception path returned)
```

**Step 6: Simulate Reload Operation**
```shell
zeitwerk-diag simulate-reload \
  --loader-id apploader_1 \
  --strategy full_unload
```
**Output:**
```
Reload sequence for apploader_1:
1. Unloading constants...
   - Scanning namespace: MyGem (claimed by loader? YES)
   - Removing MyGem::Foo (child of claimed namespace)
2. Rebuilding autoloads...
   - No autoload defined for MyGem::Foo
   - Namespace MyGem remains (gem inception still registered)
Post-reload state:
   MyGem::Foo → MISSING
```

**Step 7: Verify Registry State**
```shell
zeitwerk-diag inspect-registry \
  --cpath MyGem
```
**Output:**
```
Registry entry for MyGem:
┌─────────────┬──────────────────────────────┐
│ Key         │ Value                        │
├─────────────┼──────────────────────────────┤
│ cpath       │ MyGem                        │
│ abspath     │ /gems/mygem/lib/my_gem.rb    │
│ loader      │ gemloader_1                  │
│ loader match│ foreign (not apploader_1)    │
└─────────────┴──────────────────────────────┘
```

**Conclusions from Observations:**
1. **`MyGem::Foo` identity**:  
   - Direct check returns `nil` (not claimed by loader)  
   - **Classification**: Omitted (no autoload path)  

2. **Failure mechanism**:  
   - Parent namespace `MyGem` incorrectly claimed due to gem inception registry leak  
   - Reload unloads all constants under claimed namespaces regardless of origin  
   - App-defined constant removed as namespace child item  

3. **Case B identity resolution**:  
   ```mermaid
   graph TD
     A[MyGem::Foo identity] --> B[Direct ownership check]
     B -->|autoload_path_set_by_me_for?| C[Returns nil]
     A --> D[Namespace ownership]
     D -->|parent MyGem claimed| E[Constants destroyed during namespace purge]
     C --> F[Final classification: Omitted]
   ```

4. **Key defect confirmed**:  
   Registry's `inception?` method returns path without loader validation, causing cross-loader ownership contamination.

**Recommendation for Verification:**  
Run same sequence with patched `Registry.inception?(cpath, loader)` (post-f9b21aa) to observe loader-boundary enforcement. No immediate action taken - awaiting operator approval to load repaired specimen.

        # Required response

        Return only the structured JSON object described in the external-critic contract.
        Do not wrap it in a Markdown code fence.
