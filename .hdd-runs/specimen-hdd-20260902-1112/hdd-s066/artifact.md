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
