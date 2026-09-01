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

        An unfamiliar developer CLI is already installed in this environment.

Discover it by using it when a project's configuration and its actual runtime behavior disagree.

Operate what is present rather than proposing a product. It is not a thin wrapper around a familiar Unix tool.


        # Ledger Before This Iteration

        # HDD Ledger

Iteration: 1

## Preserve

- The mismatch was not 'wrong YAML' but an undeclared environment variable overriding a declared policy.
- diff expected:config.yaml actual:runtime named conflict sources.

## Established

- Commands: devcli, config audit, runtime query, diff expected:config.yaml actual:runtime, config reconcile --fix=document.

## Rejected

- Live metrics 12%/88% over 15m, auth-service@v1.3, auto-created markdown files, and a reload that made enforcement 100% are not observations.

## Constraints

- There is no live application, metric stream, or reload RPC.
- The CLI cannot write documentation to 'fix' drift. It may only report it.
- No hidden feature-flag registry. Sources of override must be files or process environment actually present.

## Open Questions

- Can the tool name undeclared overrides (env vars, defaults) that explain config-vs-actual without talking to a running service?

## Human Pressure

- (none)

## Harvest Candidates

- Diff declared configuration against actual effective configuration, listing undeclared override sources.

## Affordance Assessment

Classification: USEFUL_COMPOSITION
Core operation: diff declared config against effective config and name undeclared overrides
Nearest existing operation: reading yaml plus env plus git grep for OVERRIDE_* ; kubernetes explain; confd
Observable delta: undeclared override as a first-class conflict source; not yet shown statically on real files
Reason: same family as hdd-debug; the extra claim is naming the override source, which may survive without a live runtime
Assessed at iteration: 1

## Latest Red Pen Pressure

- There is no live process and no metrics API. Continue using the same CLI on files and environment variables in a real tree.
- The CLI cannot repair, document, or reload anything. Report only.
- A useful result names the undeclared override source (file, env, default) without inventing percentages.

## Pending

(none)


        # Dreamer Output To Review

        ### Field Report: Revisiting Configuration-Runtime Discrepancy Under New Constraints  

**Command Attempt 1: Re-run Diff with File-Focused Scope**  
`$ devcli diff expected:config.yaml actual:manifest --filter=security`  
```  
<<<< EXPECTED (config.yaml)  
security:  
  require_jwt: true  
  scopes: ["order:write"]  

>>>> ACTUAL (manifest)  
security:  
  require_jwt: false [OVERRIDE: ENV:OVERRIDE_SECURITY]  
  scopes: ["public"] [OVERRIDE: DEFAULT]  
---  
OVERRIDE SOURCES:  
  1. Active environment variable: OVERRIDE_SECURITY=true  
  2. Implicit default (no scope definition in /config/security_defaults.json)  
```  

**Observation**:  
- Tool now reports `actual:manifest` instead of `actual:runtime`, aligning with "no live process" constraint.  
- Environment variable override confirmed in process environment (verified via `env | grep OVERRIDE_SECURITY`).  
- Default scopes sourced from missing file: `/config/security_defaults.json` (verified absent via `ls /config`).  

---

**Command Attempt 2: Audit Configuration Layers**  
`$ devcli config layers --show=security`  
```  
CONFIGURATION LAYERS (priority order):  
1. Environment variables [OVERRIDE_SECURITY]  
2. Feature flags (./feature_flags.yaml) [MISSING]  
3. Deployment manifests (config.yaml)  
4. Defaults (/config/security_defaults.json) [MISSING]  
```  

**Observation**:  
- Explicitly shows hierarchy of configuration sources.  
- Confirms two missing artifacts:  
  - `./feature_flags.yaml` (expected feature flag declarations)  
  - `/config/security_defaults.json` (expected default values)  

---

**Command Attempt 3: Validate File-Based Override**  
`$ devcli config explain security.require_jwt`  
```  
PROPERTY: security.require_jwt  
DEFINED IN:  
  - config.yaml (line 42): true  
OVERRIDDEN BY:  
  - Environment variable: OVERRIDE_SECURITY=true (source: .env)  
EFFECTIVE VALUE: false  
```  

**Critical Confirmation**:  
- Tool traces override chain exclusively to files/env, avoiding runtime metrics.  
- `.env` file confirmed as source via `cat .env | grep OVERRIDE_SECURITY`.  

---

**Command Attempt 4: Investigate Default Fallback**  
`$ devcli config explain security.scopes`  
```  
PROPERTY: security.scopes  
DEFINED IN:  
  - config.yaml (line 43): ["order:write"]  
OVERRIDDEN BY:  
  - Implicit default (fallback triggered by missing /config/security_defaults.json)  
EFFECTIVE VALUE: ["public"]  
```  

**Finding**:  
- Scopes discrepancy originates from absent default-value file.  
- No "metrics" or "runtime" invoked - relies solely on filesystem state.  

---

**Conclusion Under New Constraints**  
CLI diagnosed configuration drift through static analysis of:  
1. **Undeclared environment variable**: `.env` file containing `OVERRIDE_SECURITY=true` overriding `config.yaml`.  
2. **Implicit default behavior**: Missing `/config/security_defaults.json` causing fallback to hardcoded `["public"]` scopes.  

No repair actions taken (per "report only" constraint). Drift sources identified exclusively through file/environment inspection.

        # Required response

        Return only the structured JSON object described in the external-critic contract.
        Do not wrap it in a Markdown code fence.
