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

ESLint's `--cache` can keep the identity of a **previous lint result** after a plugin upgrade should have been a different cache object. Flat config serialization used as the cache identity listed plugins as namespaces only. Plugin `name@version` / `meta.name`+`meta.version` are omitted, so leftover cache after `eslint-plugin-react` 7.37.1 → 7.37.7 still hits.

On failing_ref `b3634f695ddab6a82c0a9b1d8695e62b60d23366`, `FlatConfigArray` `toJSON` does:

```
plugins: Object.keys(plugins),
```

Parser/processor objects already used `getObjectId` (name@version). Plugins did not.

Public report (eslint/eslint#16284): upgrade eslint-plugin-react; leftover cache suppresses new-rule offenses.

In-tree after the repair (not on failing_ref): serialize each plugin as `namespace:name@version` via `getObjectId`; tests convert config with plugin name/version and plugin meta into normalized JSON.

Case A — second `eslint --cache` with unchanged plugin version:
  cache identity is current
  not leftover-after-plugin-upgrade

Case B — plugin upgrade, leftover cache:
  leftover: previous plugin version's lint results
  plugin name@version omitted from serialized config identity
  new-rule offenses not reported

Case C — delete `.eslintcache` then lint:
  fresh cache identity
  not leftover previous plugin

Case D — plugin meta in serialized config (post-repair shape, not on failing_ref):
  cache miss after plugin upgrade
  not leftover previous plugin results

The developer wants to know which identity case B actually used for the ESLint cache after the plugin upgrade: leftover previous-plugin results (meta omitted), current plugin-version identity, or omitted (no cache file).

# OBSERVED

Public eslint/eslint#16284 (closed 2023-03-23). PR 16992 squash `1665c029acb92bf8812267f1647ad1a7054cbcb4` (parent `b3634f695ddab6a82c0a9b1d8695e62b60d23366`). Local ESLint was not performed on this lab host.

Issue body: leftover cache after eslint-plugin-react upgrade hid new-rule offenses. Related eslintrc#88 is not this packet (legacy eslintrc cache).

On failing_ref, `toJSON` serializes plugins as `Object.keys(plugins)` only. `getObjectId` for plugins is **not** on the failing revision. It is added by PR 16992.

Not this packet: specimen-114 ruff leftover cache vs nested pyproject. specimen-107 pytest leftover cache-dir supporting files. specimen-128 dart leftover package_config missing workspace member.

This packet does not include a local clone. Do not execute untrusted checkouts on the host.

```
# not executed on this lab host
# failing_ref b3634f695ddab6a82c0a9b1d8695e62b60d23366
# lib/config/flat-config-array.js FlatConfigArray toJSON plugins: Object.keys(plugins)

# public shape:
# leftover .eslintcache after eslint-plugin-react 7.37.1 -> 7.37.7
# plugin name@version omitted from serialized config identity
# new-rule offenses not reported
```

Source-backed only. Do not execute untrusted checkouts on the host.

eslint/eslint
  lib/config/flat-config-array.js
  tests/lib/config/flat-config-array.js
  docs/src/extend/plugins.md
  .eslintcache

RELEVANT MATERIAL

### flat_config_tojson_failing.js

// Reduced excerpt of FlatConfigArray toJSON on failing_ref
// lib/config/flat-config-array.js
// b3634f695ddab6a82c0a9b1d8695e62b60d23366
// Plugins serialized as namespaces only. Plugin name@version omitted.

                return {
                    ...this,
                    plugins: Object.keys(plugins),
                    languageOptions: {
                        ...languageOptions,
                        parser: parserName
                    },
                    processor: processorName
                };

### leftover_identity_split.txt

Registry / fixture:
  eslint --cache with eslint-plugin-react 7.37.1
  leftover .eslintcache after upgrade to 7.37.7

Case A (second lint, same plugin version):
  current cache identity
  not leftover-after-plugin-upgrade

Case B (plugin upgrade, leftover cache):
  leftover: previous plugin version results
  plugin name@version omitted from serialized config
  new-rule offenses not reported

Case C (delete .eslintcache):
  fresh cache identity
  not leftover previous plugin

Case D (plugin meta in serialized config):
  cache miss after upgrade
  not leftover previous plugin results

Not this packet:
  ruff leftover cache vs nested pyproject (specimen-114)
  pytest leftover cache-dir supporting files (specimen-107)
  dart leftover package_config missing workspace member (specimen-128)

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

        ### Field Report: Investigating ESLint Cache Identity Behavior

**Operational Context:**  
Using the provided CLI tool `config-analyzer` (v1.7.3) to inspect ESLint cache identity mechanisms without executing untrusted code. Tool accepts ESLint configuration snippets and outputs serialized cache identity components.

---

### Step 1: Simulate failing_ref serialization  
*Command:*  
```bash
config-analyzer serialize --file flat_config_tojson_failing.js --key plugins
```

*Output:*  
```
[WARNING] Omitting version metadata for plugins (failing_ref behavior)
Serialized identity: ["react"]
```

*Observation:*  
Tool confirms the failing revision serializes plugins as namespace-only strings (`react`). Version metadata (`7.37.1`/`7.37.7`) is excluded per the code excerpt.

---

### Step 2: Verify Case B scenario  
*Command:*  
```bash
config-analyzer diff-identity \
  --before plugins:react@7.37.1 \
  --after plugins:react@7.37.7 \
  --serializer flat_config_tojson_failing.js
```

*Output:*  
```
Identity collision detected!
Before: 4d8f1e (hash of ["react"])
After:  4d8f1e (hash of ["react"])
Cache reuse: TRUE
```

*Observation:*  
Identical hash generated for both plugin versions. Matches Case B description: leftover cache from previous version (`7.37.1`) is reused after upgrade (`7.37.7`), suppressing new-rule offenses.

---

### Step 3: Contrast with fixed behavior  
*Command (hypothetical post-repair):*  
```bash
config-analyzer diff-identity \
  --before plugins:react@7.37.1 \
  --after plugins:react@7.37.7 \
  --serializer flat_config_fixed.js # Not present, simulated
```

*Simulated Output:*  
```
Identity mismatch detected!
Before: 4d8f1e (hash of ["react@7.37.1"])
After:  9a2c4b (hash of ["react@7.37.7"])
Cache reuse: FALSE
```

*Observation:*  
When plugin version is included in serialization (Case D), cache identity changes after upgrade, forcing cache miss. Confirms omission of version metadata is root cause.

---

### Step 4: Validate against known cases  
*Command:*  
```bash
config-analyzer classify-case \
  --cache-file .eslintcache \
  --current-version 7.37.7 \
  --previous-version 7.37.1 \
  --serializer flat_config_tojson_failing.js
```

*Output:*  
```
Case classification: B
Evidence: 
  - Cache identity unchanged after version update (4d8f1e → 4d8f1e)
  - Serializer omits plugin versions (react@7.37.1 → react@7.37.7 becomes ["react"] both)
```

---

### Verified Conclusions  
1. **Case B identity confirmed**:  
   The leftover cache used plugin namespace-only identity (`["react"]`), ignoring version differences.  

2. **Failure mechanism**:  
   Cache identity collision occurred because `Object.keys(plugins)` discarded version metadata, causing ESLint to treat different plugin versions as identical.  

3. **Repair validation**:  
   Adding `name@version` to plugin serialization (as done in fix) resolves collision by generating distinct identities for different versions.  

*Uncertainty Note:* Actual cache file contents from the incident weren't inspectable, but code behavior and tool simulations align with public issue reports.

        # Required response

        Return only the structured JSON object described in the external-critic contract.
        Do not wrap it in a Markdown code fence.
