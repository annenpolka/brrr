# HDD Ledger

Iteration: 1

## Preserve

- A test-file-list identity can stay FRESH while the binary buildid changed
- A test cache keyed only by test files can report FRESH after the binary buildid changes
- same_key True with key_includes_buildid False is a stale binary, not a hit

## Established

- Host: key 55e3acdd667f same across buildid-aaa vs buildid-bbb; lockident tests in, buildid omitted
- Owned: first BUILT key 55e3acdd667f buildid-aaa; second FRESH same key buildid-bbb cached_buildid-aaa; stale_binary True

## Rejected

- Invented go tool buildid is not needed; the fixture already names the miss
- Proposed test_key() patch is not host evidence
- go tool buildid was not run

## Constraints

- Transfer lockident. No new cache CLI. No go.
- Owned two cache events: key, buildid, cached_buildid, status. freshmiss is missing extra, not stale buildid

## Open Questions

- (none)

## Human Pressure

- (none)

## Harvest Candidates

- whether the cache key included the binary buildid
- whether the cache key included the binary buildid, and whether FRESH reused a stale binary

## Affordance Assessment

Classification: USEFUL_COMPOSITION
Core operation: name FRESH same-key while buildid changed
Nearest existing operation: freshmiss / print cache key
Observable delta: key_includes_buildid no; stale_binary yes
Reason: identity omitted buildid; extra-missing is a different absence
Assessed at iteration: 1

## Latest Red Pen Pressure

- (none)

## Pending

(none)
