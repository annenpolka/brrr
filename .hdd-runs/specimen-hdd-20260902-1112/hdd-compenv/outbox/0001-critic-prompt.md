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

Compose-go `Normalize` can keep the identity of a **previous image ENV default** after the compose file listed `FOO` (no equals, no value) and that listing should have meant unset-in-container. `resolve` drops a listed-without-equals name when the user environment has no matching entry. The service environment map then omits `FOO`. The leftover identity is the image `ENV FOO=not_empty` default, not unset.

On failing_ref `65600cee45d45771a1faa6ddaf87b23ca4d2400c`:

```
func resolve(a any, fn func(s string) (string, bool)) (any, bool) {
    switch v := a.(type) {
    case []any:
        var resolved []any
        for _, val := range v {
            if r, ok := resolve(val, fn); ok {
                resolved = append(resolved, r)
            }
        }
        return resolved, true
    case map[string]any:
        resolved := map[string]any{}
        for key, val := range v {
            if val != nil {
                resolved[key] = val
                continue
            }
            if s, ok := fn(key); ok {
                resolved[key] = s
            }
        }
        return resolved, true
    case string:
        if !strings.Contains(v, "=") {
            if val, ok := fn(v); ok {
                return fmt.Sprintf("%s=%s", v, val), true
            }
            return "", false
        }
        return v, true
    default:
        return v, false
    }
}
```

`service["environment"]` and `build["args"]` both call the same `resolve`. Listed-without-equals `FOO` with no user-env match returns `("", false)` and is dropped. `FOO=` (equals, empty) is a different identity and is kept. Image `ENV EMPTY=not_empty` then supplies leftover `not_empty`.

Public report (docker/compose#11962). Image `ENV EMPTY=not_empty`; compose lists `- EMPTY`; `echo "=$EMPTY="` prints `=not_empty=` (leftover image default) instead of `==` (unset). `FOO=` empty string is `==` with empty. User-env `EMPTY=hello` is `=hello=`.

In-tree after the repair (not on failing_ref): `resolve(a, fn, keepEmpty bool)`; environment uses `keepEmpty=true` and keeps listed-without-equals as `nil` / the bare name. Build args stay `keepEmpty=false`.

Case A — listed `FOO`, user env has `FOO=bar`:
  current resolved identity `FOO=bar`
  not leftover-after-drop

Case B — listed `FOO` (no equals), user env has no `FOO`, leftover drop:
  leftover: previous image ENV default / omitted from service environment
  listed-without-equals dropped (`"", false`)
  container still has image default

Case C — listed `FOO=` (equals, empty string):
  empty-string identity
  not unset; not leftover image default

Case D — environment keepEmpty (post-repair shape, not on failing_ref):
  listed-without-equals kept as nil / bare name
  container unsets; not leftover image default

The developer wants to know which identity case B actually used for `FOO` after the listing: leftover previous-image default (listed-without-equals dropped), current unset, empty string, or omitted (no env map).

# OBSERVED

Public docker/compose#11962 (closed 2024-07-10). compose-spec/compose-go PR 654 squash `6adefd584b8088e0c6817bf54f5715595dd41301` (parent `65600cee45d45771a1faa6ddaf87b23ca4d2400c`). docker/compose PR 11965 bumps compose-go and adds e2e `TestUnsetEnv`. Local compose-go was not performed on this lab host.

Issue body: image `ENV VAR "default"`; compose `environment: - VAR` (no value). Before v2.24.7 the variable was unset from the container. After, leftover image default stayed. `VAR=` (equals, empty) is empty in the container on both sides.

On failing_ref, `Normalize` calls `resolve` for environment and build args with one signature. Listed-without-equals and no user-env match is dropped. Build args are supposed to keep Dockerfile defaults; environment listed-without-equals is supposed to unset.

Not this packet: specimen-010 local-fixture env-empty-vs-unset. specimen-031 pip empty user `proxy =` vs global proxy. specimen-079 helm null vs omitempty.

This packet does not include a local clone. Do not execute untrusted checkouts on the host.

```
# not executed on this lab host
# failing_ref 65600cee45d45771a1faa6ddaf87b23ca4d2400c
# loader/normalize.go resolve / service["environment"]

# public shape:
# leftover image ENV default after listed-without-equals dropped
# FOO= empty string is a different identity
# user-env match yields current FOO=value
```

Source-backed only. Do not execute untrusted checkouts on the host.

compose-spec/compose-go
  loader/normalize.go
  loader/normalize_test.go

RELEVANT MATERIAL

### leftover_identity_split.txt

Registry / fixture:
  compose-go Normalize environment resolve
  leftover image ENV default after listed-without-equals dropped

Case A (listed FOO, user env FOO=bar):
  current resolved identity
  not leftover-after-drop

Case B (listed FOO, no user env, leftover drop):
  leftover: previous image ENV default
  listed-without-equals omitted from service environment
  container still has image default

Case C (listed FOO= empty string):
  empty-string identity
  not unset; not leftover image default

Case D (environment keepEmpty):
  listed-without-equals kept as nil / bare name
  container unsets
  not leftover image default

Not this packet:
  local-fixture env-empty-vs-unset (specimen-010)
  pip empty user proxy vs global (specimen-031)
  helm null vs omitempty (specimen-079)

### resolve_failing.go

// Reduced excerpt of resolve on failing_ref
// loader/normalize.go
// 65600cee45d45771a1faa6ddaf87b23ca4d2400c
// listed-without-equals with no user-env match returns "", false and is dropped.
// leftover identity is the image ENV default.

func resolve(a any, fn func(s string) (string, bool)) (any, bool) {
    switch v := a.(type) {
    case string:
        if !strings.Contains(v, "=") {
            if val, ok := fn(v); ok {
                return fmt.Sprintf("%s=%s", v, val), true
            }
            return "", false
        }
        return v, true
    default:
        return v, false
    }
}

// service["environment"] and build["args"] share this resolve

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

        ### Field Report: Investigating Environment Variable Resolution in compose-go

**Operational Context:**  
Working within the constraints of the provided compose-go source code (failing_ref `65600cee45d45771a1faa6ddaf87b23ca4d2400c`). No local execution performed per security constraints. Analysis conducted through direct code inspection and scenario testing against the `resolve` function.

---

#### Investigation Sequence

**1. Reproducing Case B Behavior**  
Executed code path simulation for `resolve("FOO", envLookup)` where `envLookup` returns `("", false)` for "FOO":

```go
// Input: "FOO" (no equals, no value)
// Code path: string case -> !strings.Contains("FOO", "=") -> true
// envLookup("FOO") returns ("", false) -> returns ("", false)
result, ok := resolve("FOO", func(s string) (string, bool) {
    return "", false  // Simulates no user-env match
})
fmt.Printf("Result: %#v, Ok: %v\n", result, ok)
```

**Output Observation:**  
`Result: "", Ok: false`  
→ Variable is dropped from environment map (not included in service config)

**2. Container Runtime Implications**  
When compose-go omits `FOO` from the service environment map:  
- Container inherits image's `ENV FOO=not_empty` as leftover default  
- Verified via public report (docker/compose#11962): `echo "=$FOO="` outputs `=not_empty=`  

**3. Contrasting Case C (Empty String)**  
Tested `resolve("FOO=", envLookup)` path:

```go
// Input: "FOO=" (equals present)
// Code path: strings.Contains("FOO=", "=") -> true
// Returns original string without lookup
result, ok := resolve("FOO=", func(s string) (string, bool) {
    return "SHOULD_NOT_BE_CALLED", true
})
fmt.Printf("Result: %#v, Ok: %v\n", result, ok)
```

**Output Observation:**  
`Result: "FOO=", Ok: true`  
→ Variable explicitly set to empty string in container (`echo "=$FOO="` outputs `==`)

**4. Key Behavior Matrix**

| Case | Compose Entry | User Env Match | `resolve()` Output | Container State |
|------|---------------|----------------|--------------------|-----------------|
| **A** | `- FOO`       | `FOO=bar`      | `"FOO=bar", true`  | `bar` (explicit) |
| **B** | `- FOO`       | No match       | `"", false`        | `not_empty` (image default) |
| **C** | `- FOO=`      | Any            | `"FOO=", true`     | Empty string |

---

#### Confirmed Identity for Case B
**FOO's post-resolution identity:**  
`Leftover image ENV default`  
- Proven by `resolve()` outputting `("", false)` → variable omission  
- Container behavior shows image default persists  
- Distinct from unset (Case D repair) and empty string (Case C)

**Conflict Resolution:**  
Prior assumption that `- FOO` should unset conflicts with observed behavior. The `resolve()` function actively drops unmatched variables, leaving image defaults intact. This matches public issue docker/compose#11962 where v2.24.7 changed behavior from unset to image-default retention.

**Smallest Verification Path:**  
1. Confirm `resolve()` returns `("", false)` for unmatched no-equals entries  
2. Check service environment map omits the variable  
3. Validate container uses image ENV value  

No further instrumentation required - the code path and outputs are deterministic.

**Operational Conclusion:**  
The failing_ref behavior is consistent: Case B uses leftover image defaults. Repair requires modifying `resolve()` to preserve unset intent (as implemented in later keepEmpty flag).

        # Required response

        Return only the structured JSON object described in the external-critic contract.
        Do not wrap it in a Markdown code fence.
