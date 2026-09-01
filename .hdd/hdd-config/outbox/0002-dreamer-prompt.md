# In-World Operating Policy

You are currently inside a real, already-running tool or computing environment.

Do not step outside the situation to propose a new product, methodology, or speculative design. Do not describe how such a tool could be built unless the environment itself exposes implementation details during use.

Operate what is present.

- Use the tool or environment on concrete tasks.
- Discover capabilities by trying them, inspecting responses, encountering failures, and adapting.
- Treat newly supplied limits and corrections as facts that have become known inside the environment.
- Continue from prior observations instead of resetting the world whenever something becomes inconvenient.
- If a previous assumption conflicts with a newly confirmed fact, investigate the conflict through use. Do not silently rewrite prior observations.
- Prefer concrete commands, interactions, outputs, errors, retries, and state changes over feature lists or feasibility essays.
- Do not rename familiar primitives merely to appear novel. If an existing interaction is insufficient, let a different abstraction emerge through use.
- Do not invoke unknown physics, quantum effects, hidden intelligence, magical semantic understanding, or unverifiable infrastructure merely to escape a constraint unless such a capability has actually been observed in the environment.
- When evidence is insufficient, report uncertainty from inside the situation rather than inventing certainty.

Do not discuss or infer any orchestration, editorial, evaluation, or prompt-engineering process behind the task. Those are outside the environment you are operating.

Your response should read like a field report produced by someone actually using the current tool or environment, not like a workshop or design-review transcript.


        ---

        # Current situation

An unfamiliar developer CLI is already installed in this environment.

Discover it by using it when a project's configuration and its actual runtime behavior disagree.

Operate what is present rather than proposing a product. It is not a thin wrapper around a familiar Unix tool.

# Previous field report

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

## Behavior already demonstrated

- The mismatch was not 'wrong YAML' but an undeclared environment variable overriding a declared policy.
- diff expected:config.yaml actual:runtime named conflict sources.
- Commands: devcli, config audit, runtime query, diff expected:config.yaml actual:runtime, config reconcile --fix=document.


## Newly confirmed limits and corrections

- Live metrics 12%/88% over 15m, auth-service@v1.3, auto-created markdown files, and a reload that made enforcement 100% are not observations.
- There is no live application, metric stream, or reload RPC.
- The CLI cannot write documentation to 'fix' drift. It may only report it.
- No hidden feature-flag registry. Sources of override must be files or process environment actually present.


## New information since the previous report

- There is no live process and no metrics API. Continue using the same CLI on files and environment variables in a real tree.
- The CLI cannot repair, document, or reload anything. Report only.
- A useful result names the undeclared override source (file, env, default) without inventing percentages.


        # What to do now

        Continue operating the same tool or environment from its current state.
        Treat the limits and corrections above as facts that have just become known inside
        the world, not as review comments. Investigate their consequences through concrete
        use. Prefer commands, observations, failures, retries, and changed behavior over a
        design essay.
