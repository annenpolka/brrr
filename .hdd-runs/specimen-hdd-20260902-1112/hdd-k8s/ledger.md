# HDD Ledger

Iteration: 1

## Preserve

- Documented timeout 0 means check once; a later default can abort before that check
- The abort can happen without visiting the object
- A wait with timeout 0 can fail before inspecting the object

## Established

- Packet: kubectl wait --for=jsonpath={.status.replicas} deploy/test-3 --timeout=0 errors about --wait-for-creation instead of condition met
- Packet is REAL_SOURCE_BACKED kubernetes wait

## Rejected

- No cluster was contacted; condition met / wait-for-creation=false transcripts are Dreamer-generated
- Help-text quotes beyond the packet are unverified
- Specific kubectl transcripts in this turn are not host-executed

## Constraints

- No kube API, no kubectl binary required
- A tiny owned options fixture (timeout, wait-for-creation, for=delete) is the world
- No cluster
- An owned function that errors on timeout==0 before checking a dict is the world

## Open Questions

- Can visit-vs-abort be shown from flags alone without a cluster?

## Human Pressure

- (none)

## Harvest Candidates

- Ask which default governed timeout 0 and whether the object was visited
- Ask whether wait evaluated the condition or refused before looking

## Affordance Assessment

Classification: USEFUL_COMPOSITION
Core operation: distinguish wait that inspected state from wait that failed closed before looking
Nearest existing operation: kubectl wait plus reading the error string
Observable delta: one query whose object is evaluated-vs-refused-before-look
Reason: exit status 1 conflates missing object, false condition, and policy refusal
Assessed at iteration: 1

## Latest Red Pen Pressure

- There is no cluster. Continue on a tiny wait(fixture, timeout) function. Show whether timeout 0 looked at the object.

## Pending

(none)
