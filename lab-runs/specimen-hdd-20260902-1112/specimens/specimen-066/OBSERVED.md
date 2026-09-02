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
