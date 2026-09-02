# HDD Ledger

Iteration: 1

## Preserve

- While status is starting, a long StartInterval timer can be armed instead of the regular Interval

## Established

- Packet: StartPeriod 2s StartInterval 30s Interval 2s; unhealthy ~30s not ~4s

## Rejected

- Invented dockersim CLI is not installed

## Constraints

- No docker. Owned timer records: period, start_interval, interval, armed, fired_at

## Open Questions

- (none)

## Human Pressure

- (none)

## Harvest Candidates

- Which timer the monitor armed while starting, and when it fired relative to start-period end

## Affordance Assessment

Classification: USEFUL_COMPOSITION
Core operation: name the armed timer vs the timer that should fire after start period
Nearest existing operation: read StartPeriod and StartInterval
Observable delta: armed 30s during starting vs 2s after period
Reason: config dump does not name which timer was live
Assessed at iteration: 1

## Latest Red Pen Pressure

- (none)

## Pending

(none)
