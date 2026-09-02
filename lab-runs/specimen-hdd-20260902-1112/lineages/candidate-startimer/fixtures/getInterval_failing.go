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
