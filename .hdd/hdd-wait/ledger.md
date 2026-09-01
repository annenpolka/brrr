# HDD Ledger

Iteration: 2

## Preserve

- The object of inquiry was a waiting process, not a log file.
- trace output named a blocking external condition rather than only CPU.
- The Dreamer used ps wchan and /proc/fd rather than a mock-service.

## Established

- list, trace, resume, mock-service, logs --follow.
- attach PID, trace, resume refused to inject into a kernel pipe.

## Rejected

- Session IDs, correlation IDs, 300s timeout, and a mock that completes the wait are unverified.
- PID 4712, inode 19388407, 128 bytes, and 5m17s blocked were not observations of this machine.

## Constraints

- There is no mock-service injector and no hidden session table.
- The CLI may only observe real OS state (process, fds, syscalls it can actually see).
- Operate on a real waiting process in this environment.

## Open Questions

- Without mocking, can one command say what a given PID is blocked on?

## Human Pressure

- (none)

## Harvest Candidates

- Ask what a process is waiting for, as a first-class query over observable OS state.

## Affordance Assessment

Classification: THIN_WRAPPER
Core operation: report a process's wait channel and blocking file descriptor
Nearest existing operation: ps -o wchan, lsof -p, /proc/PID/fd
Observable delta: bundled wording; no new query object after removing invented session lore
Reason: capability removal left ordinary process inspection; no untested delta that would change the class
Assessed at iteration: 2

## Latest Red Pen Pressure

- (none)

## Pending

(none)
