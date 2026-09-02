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
