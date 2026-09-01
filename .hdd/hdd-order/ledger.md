# HDD Ledger

Iteration: 1

## Preserve

- The operator asked whether one development event could have caused another.
- resolve refused to answer before traces existed, which is at least an honesty gesture inside the fiction.

## Established

- Commands: inspect, trace, list, resolve.

## Rejected

- Event IDs, timestamps, and parent-child links were generated, not observed.

## Constraints

- There is no event database and no trace cache.
- The CLI may only look at files, git history, and logs that actually exist in this tree.
- Do not invent identifiers.

## Open Questions

- On two real git commits or two log lines, can the tool say more than 'A is earlier than B'?

## Human Pressure

- (none)

## Harvest Candidates

- Ask whether change A could have caused observation B using only in-tree evidence.

## Affordance Assessment

Classification: THIN_WRAPPER
Core operation: query a causality graph for whether event A is an ancestor of event B
Nearest existing operation: distributed tracing, journalctl, git log --follow
Observable delta: not yet shown without a fictional event store
Reason: current session is a renamed tracer; one more turn on real git/logs could change this
Assessed at iteration: 1

## Latest Red Pen Pressure

- There is no event ID store. Continue using the same CLI on two real items in this repository (commits, test failures, or log files).
- Do not invent identifiers or parent links. If evidence is insufficient, say so.
- A useful answer is more than timestamp order.

## Pending

(none)
