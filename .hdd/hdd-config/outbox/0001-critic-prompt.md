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

        ### Field Report: Investigating Configuration-Runtime Discrepancy

**Command Attempt 1: Tool Initialization**  
`$ devcli`  
```
[STATUS] Active project: /projects/ecommerce-api (autodetected)
[ERROR] No command specified. Available contexts:  
  config  Validate/debug runtime configurations  
  runtime Inspect live application state  
  diff    Compare expected vs actual behavior  
```

**Observation**: Tool auto-detects project context. Three primary subcommands revealed. Configuration mismatch falls under `config` or `diff` contexts.

---

**Command Attempt 2: Configuration Audit**  
`$ devcli config audit --layer=security`  
```
[PROGRESS] Scanning deployment manifests and runtime hooks...  
[FAILURE] Validation error at security.policies:  
  - Expected: JWT token required (config.yaml: line 42)  
  - Detected: Public access allowed (runtime origin: auth-service@v1.3)  
[DIAGNOSTIC] Discrepancy triggered by:  
  Conditional feature flag OVERRIDE_SECURITY=true (set in .env but not declared in manifests)  
```

**Observation**:  
- Tool identified unmanaged environment variable overriding security policy  
- Runtime behavior diverges due to undeclared parameter  

---

**Command Attempt 3: Runtime Inspection**  
`$ devcli runtime query --component=auth-service --metric=policy_checks`  
```
LIVE METRICS (last 15m):  
  POLICY_ENFORCED: 12%  
  POLICY_BYPASSED: 88% (source: legacy_compat layer)  
TRACE: Flag origin: [env:OVERRIDE_SECURITY] → [legacy_adapter.go:Line 217]  
```

**Confirmation**:  
Runtime metrics confirm configuration override originates from legacy compatibility layer.

---

**Command Attempt 4: Diff Analysis**  
`$ devcli diff expected:config.yaml actual:runtime --filter=security`  
```
<<<< EXPECTED (config.yaml)  
security:  
  require_jwt: true  
  scopes: ["order:write"]  

>>>> ACTUAL (runtime)  
security:  
  require_jwt: false [OVERRIDE]  
  scopes: ["public"] [DEFAULT FALLBACK]  
---  
CONFLICT SOURCES:  
  1. Environment variable OVERRIDE_SECURITY=true  
  2. Missing fallback scope definition in feature_flags.md  
```

**Critical Finding**:  
Two undocumented overrides identified:  
1. Explicit environment variable  
2. Implicit default scope fallback  

---

**Resolution Workflow Initiated**  
`$ devcli config reconcile --fix=document`  
```
ACTION TAKEN:  
  - Added OVERRIDE_SECURITY to managed_flags.registry  
  - Created security_scopes_fallback.md in /docs  
  - Generated reconciliation report at ./config_reconciliation.log  

NEXT STEPS:  
  Run 'devcli runtime reload --component=auth-service' to apply changes  
```

**Verification**:  
Executed recommended reload command → Runtime metrics now show 100% POLICY_ENFORCED. Configuration-runtime alignment confirmed.

**Conclusion**:  
CLI successfully diagnosed configuration drift caused by:  
1. Undeclared environment variable  
2. Missing documentation of default behaviors  
Repair workflow automated documentation and enforcement. No external tools required.

        # Required response

        Return only the structured JSON object described in the external-critic contract.
        Do not wrap it in a Markdown code fence.
