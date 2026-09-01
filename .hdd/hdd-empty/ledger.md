# HDD Ledger

Iteration: 2

## Preserve

- A deliberate non-matching query printed 0 matches and claimed success rather than an error.
- The operator treated empty as a legitimate outcome.
- Zero matches: exit 0 with an explicit empty message.
- Invalid pattern: exit 2.
- I/O error: exit 3 with an OS error.

## Established

- query, query --context, env.
- query empty, query --context /locked_dir, query malformed glob, trace missing id.

## Rejected

- 847 artifacts, v3.1.0, 30-day index are unsupported.
- /locked_dir and service-alpha are not this machine.

## Constraints

- No hidden project index. Search real files in this tree.
- Empty, error, and unknown/unindexed must be distinguishable (message and exit code).
- Do not invent scan counts.

## Open Questions

- On a real tree, is empty-vs-error-vs-unknown a distinct contract from grep/rg?

## Human Pressure

- (none)

## Harvest Candidates

- A search whose empty result is success, with a different exit for errors and for 'this query cannot be answered here'.
- Search files with exit 0 on empty, 2 on bad query, 3 on I/O, 1 unused or matches-found as 0 with nonempty stdout.

## Affordance Assessment

Classification: USEFUL_COMPOSITION
Core operation: search a tree where zero hits is success, distinct from query errors and I/O errors
Nearest existing operation: rg/grep (empty is exit 1)
Observable delta: empty is not a failure, so `cmd && x` still runs after a legitimate miss
Reason: small contract difference; enough to ground; further dreaming is traversal lore
Assessed at iteration: 2

## Latest Red Pen Pressure

- (none)

## Pending

(none)
