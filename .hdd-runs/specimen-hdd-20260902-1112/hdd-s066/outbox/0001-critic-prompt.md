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

A container healthcheck is configured with a short start period and a long start interval:

```
StartPeriod: 2s
StartInterval: 30s
Interval: 2s
Retries: 1
Test: ["CMD", "/bin/false"]
```

The container becomes `unhealthy` about 30s after start. Expected: unhealthy within one regular `Interval` after `StartPeriod` ends (~4s).

The developer wants to know which timer the health monitor actually armed while status was still `starting`, and when that timer fired relative to the end of the start period.

# OBSERVED

Public moby/moby#46747 / PR 52317. Failing world in `daemon/health.go` `monitor` → `getInterval`.

On the failing revision:

```
getInterval := func() time.Duration {
    if time.Since(started) >= startPeriod {
        return probeInterval
    }
    c.Lock()
    status := c.State.Health.Health.Status
    c.Unlock()

    if status == containertypes.Starting {
        return startInterval
    }
    return probeInterval
}
```

`monitor` does `intervalTimer := time.NewTimer(getInterval())` and later `intervalTimer.Reset(getInterval())`.

When `HealthStartPeriod` < `HealthStartInterval` and the container is still `starting`, `getInterval` returns the full `startInterval` (30s) even if only 2s of start period remain. The monitor sleeps past the start-period boundary, then eventually applies `probeInterval`.

Failing streak / `unhealthy` is computed in `handleProbeResult`: while status is `starting` and `timeSinceStart < startPeriod`, failures do not increment the streak. After the period, one failing probe with `Retries: 1` is enough.

This packet does not include a local clone; treat the snippets and timing as the world. Do not execute untrusted checkouts on the host.

# COMMANDS

```
# container Healthcheck:
#   StartPeriod=2s StartInterval=30s Interval=2s Retries=1 Test=CMD /bin/false
docker inspect --format '{{.State.Health.Status}}' <id>
# failing revision: unhealthy ~30s after start
# expected: unhealthy within ~Interval after StartPeriod
```

Not executed on this lab host.

moby/moby
  daemon/health.go

RELEVANT MATERIAL

### getInterval_failing.go

// Reduced excerpt of monitor/getInterval on failing_ref
// daemon/health.go

getInterval := func() time.Duration {
    if time.Since(started) >= startPeriod {
        return probeInterval
    }
    c.Lock()
    status := c.State.Health.Health.Status
    c.Unlock()

    if status == containertypes.Starting {
        return startInterval
    }
    return probeInterval
}

### repro_timing.txt

StartPeriod: 2s
StartInterval: 30s
Interval: 2s
Retries: 1
Test: CMD /bin/false
observed unhealthy: ~30s after start
expected unhealthy: within one Interval after StartPeriod (~4s)

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

        ### Field Report: Container Healthcheck Timer Investigation

#### Tool Used: `dockersim` CLI (v0.3.1)  
*Unfamiliar simulation tool pre-installed in environment. Capabilities discovered through experimentation.*

---

### Investigation Sequence

**1. Initializing simulation with observed parameters**  
```bash
dockersim init \
  --start-period=2s \
  --start-interval=30s \
  --interval=2s \
  --retries=1 \
  --test="CMD /bin/false"
```
*Output:*  
`Simulation initialized: HEALTHCHECK[StartPeriod=2s|StartInterval=30s|Interval=2s|Retries=1]`

**2. Running timer trace from t=0**  
```bash
dockersim trace-timers --from-start
```
*Output:*  
```
[  0ms] MONITOR: Armed timer=30s (STARTING_PERIOD_ACTIVE)
[ 30s] TIMER FIRED: Probe#1 executed (exit=1)
[ 30s] HEALTH STATE: starting → unhealthy (streak=1 >= retries=1)
```
*Observation:* First probe executes at 30s despite start period ending at 2s.

**3. Inspecting timer at critical boundary (t=2s)**  
```bash
dockersim checkpoint --at=2s get-timers
```
*Output:*  
```
ACTIVE TIMER @ t=2s:
- Type: start-interval
- Duration: 30s (original)
- Remaining: 28s
- Armed at: t=0ms
- Reason: status=starting
```
*Observation:* Timer armed at t=0 remains active with 28s remaining after start period ends.

**4. Simulating timer reset at period boundary**  
```bash
dockersim what-if --at=2s reset-timer
```
*Output:*  
```
HYPOTHETICAL @ t=2s:
- New interval would be: 2s (probe-interval)
- Next probe at: t=4s
- Projected state change: unhealthy @ t=4s
```

**5. Validating failure counting behavior**  
```bash
dockersim probe-history
```
*Output:*  
```
PROBE HISTORY:
[30s] Probe#1: FAIL → streak=1 (status=unhealthy)
```
*Observation:* No probes occur during start period despite configuration allowing 14 potential probes (30s/2s).

---

### Key Findings

1. **Timer arming behavior**:  
   - Single 30s timer armed at t=0 when status=`starting`  
   - Timer type persists as `start-interval` for full duration regardless of period boundary crossing

2. **Critical timing sequence**:  
   - `start-period` ends at **t=2s**  
   - Original timer fires at **t=30s**  
   - Health status changes at **t=30s** (28s after period end)

3. **Failure attribution**:  
   - First failure after period end immediately triggers `unhealthy` due to `retries=1`  
   - Zero failures counted during start period (by design)

---

### Conflict Resolution
Prior assumption: "Healthcheck should evaluate regularly during start period"  
New evidence:  
- Timer set once at start with fixed 30s duration  
- No timer adjustments occur during start period  
- Status remains `starting` until first probe completion  

Conclusion: Original timer configuration prevents boundary-adaptive behavior. Discrepancy resolved through simulation output.

---

### Uncertainty Note
Actual Docker runtime may show ±500ms variance due to goroutine scheduling (unverifiable in simulation). Core timer behavior remains consistent with provided code snippets.

        # Required response

        Return only the structured JSON object described in the external-critic contract.
        Do not wrap it in a Markdown code fence.
