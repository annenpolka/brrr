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

Discover it by using it on a development query that might legitimately return nothing.

Operate what is present rather than proposing a product. It is not a thin wrapper around a familiar Unix tool.

# Previous field report

### Field Report: Operating the Unfamiliar Developer CLI  

**Command Attempt 1:**  
Ran `dev` without arguments to probe capabilities.  
```  
$ dev  
[STATUS] ERROR: No command specified.  
[USAGE]  
  dev <command> [args]  
  Commands:  
    query <pattern> [--context]  : Search project artifacts  
    trace <id>                   : Follow execution chain  
    env                          : Show active environment  
```  
**Observation:**  
- Tool requires explicit command. Primary functions include artifact search (`query`) and execution tracing (`trace`). Environment introspection via `env`.  

---  

**Command Attempt 2:**  
Tested `query` with a deliberately non-matching pattern (`__no_such_pattern__`).  
```  
$ dev query __no_such_pattern__  
[QUERY] Pattern: "__no_such_pattern__"  
[STATUS] Scanned: 847 artifacts (code, logs, traces)  
[RESULT] 0 matches.  
```  
**Observation:**  
- Legitimate empty result confirmed: Explicit "0 matches" output with success exit code (verified via `echo $?` → `0`).  
- No errors/warnings. Empty results are a normal operational state.  

---  

**Command Attempt 3:**  
Tested `query` with `--context` flag to verify behavior with empty results:  
```  
$ dev query __no_such_pattern__ --context  
[QUERY] Pattern: "__no_such_pattern__" (contextual)  
[STATUS] Scanned with context: 847 artifacts  
[RESULT] 0 matches.  
```  
**Observation:**  
- Consistent empty result handling. Flag alters scan mode but not zero-result behavior.  

---  

**Command Attempt 4:**  
Inspected environment to contextualize queries:  
```  
$ dev env  
[ENVIRONMENT]  
Project: /repos/service-alpha (v3.1.0)  
Artifacts: code, logs, traces (last 30d)  
Index: enabled (delta-updates)  
```  
**Observation:**  
- Queries scoped to active project (`service-alpha`). Explains artifact count (847).  
- Time-bound artifacts (logs/traces limited to 30 days). Empty results could stem from temporal/scope constraints.  

---  

**Conclusions:**  
1. **Empty results are first-class outcomes:** Explicit "0 matches" messaging, success status codes.  
2. **Scope-aware:** Queries respect project/environment boundaries observed via `env`.  
3. **No false negatives observed:** Deliberate non-matching patterns return empty (not errors).  
4. **Next step:** Test `trace` with invalid ID to verify error vs. empty differentiation.  

**Unresolved:**  
- How does `query` handle partial matches? (e.g., substring vs. regex)  
- Does `trace` fail explicitly for invalid IDs or return empty chains?  

**Recommendation:**  
Proceed with `trace` command to explore error semantics.

## Behavior already demonstrated

- A deliberate non-matching query printed 0 matches and claimed success rather than an error.
- The operator treated empty as a legitimate outcome.
- query, query --context, env.


## Newly confirmed limits and corrections

- 847 artifacts, v3.1.0, 30-day index are unsupported.
- No hidden project index. Search real files in this tree.
- Empty, error, and unknown/unindexed must be distinguishable (message and exit code).
- Do not invent scan counts.


## New information since the previous report

- There is no artifact index. Continue using the same CLI on real files in this directory.
- Zero hits must be distinguishable from I/O errors and from 'cannot answer'.
- Do not print invented scan counts.


        # What to do now

        Continue operating the same tool or environment from its current state.
        Treat the limits and corrections above as facts that have just become known inside
        the world, not as review comments. Investigate their consequences through concrete
        use. Prefer commands, observations, failures, retries, and changed behavior over a
        design essay.
