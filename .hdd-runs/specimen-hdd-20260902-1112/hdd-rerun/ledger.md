# HDD Ledger

Iteration: 2

## Preserve

- A rerun can reuse the same test class instance that the failing attempt mutated
- Fixture cleanup can run while the instance identity stays the same
- A rerun may reuse the same instance so state on self leaks into the next attempt
- A rerun can reuse the same test class instance the failing attempt mutated
- Distinct test items can still get new instances

## Established

- Packet mechanism: leaked instance on rerun (pytest-rerunfailures, failing_ref 0440e2158c98187a6ccd283e9c0b65475d1cd620)
- Public pytest-rerunfailures #340: create a fresh test class instance for each rerun
- Packet mechanism: leaked instance on rerun; pytest-rerunfailures failing_ref 0440e215

## Rejected

- Numeric object ids, ITEM INSTANCE debug prints, and sed-into-plugin transcripts are not host evidence
- A recommended _reset_test_instance helper is a Dreamer patch, not a specimen observation
- Specific memory ids and SETUP/TEST counts in this transcript are unverified
- Numeric object ids and pytest -s transcripts were not captured on this host
- Direct recursion of test_flaky is not the rerun protocol

## Constraints

- No plugin source checkout, no in-place sed of third-party code
- A tiny owned class with an autouse fixture and a rerun loop is the world if a clone is absent
- Do not install pytest-rerunfailures on the host
- An owned class with a counter on self is enough
- No plugin checkout
- An owned loop that reuses one instance across attempts is the world

## Open Questions

- Can instance identity across attempts be shown from user-visible prints of id(self) on an owned fixture?
- Can the tool show same vs new id(self) across attempts using a tiny fixture?

## Human Pressure

- (none)

## Harvest Candidates

- Ask whether a rerun used a new instance or the leftover one, and which attributes survived
- Ask whether a retry reused the failed instance

## Affordance Assessment

Classification: USEFUL_COMPOSITION
Core operation: for a rerun, report whether the test class instance was reused and what attributes leaked
Nearest existing operation: print id(self) in setup/call/teardown
Observable delta: one query whose object is leftover instance identity across attempts
Reason: ordinary rerun output shows pass/fail; it does not name instance reuse
Assessed at iteration: 2

## Latest Red Pen Pressure

- Do not recurse the test method. Use an owned attempt loop over one instance.

## Pending

(none)
