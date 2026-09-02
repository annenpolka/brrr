ACCEPT_R1

contrastiveness: high (StartPeriod 2s vs StartInterval 30s; unhealthy at ~30s vs ~4s; timer armed with startInterval while starting)
reproducibility: source-backed issue + PR + pinned merge parent/merge commit; local run not claimed
information density: high
safety: public OSS, not executed on host
nontriviality: high — two clocks (start period vs start interval) and the monitor only consults “are we past the period *now*”, not “will this sleep land past it”
ecosystem: go / moby
mechanism_family: timer-sleep-past-deadline, start-interval-vs-period, healthcheck-cadence

Packet is the failing world only. Do not assume a root cause.
