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
