# HDD Ledger

Iteration: 2

## Preserve

- Cache-Control private can be treated as non-storeable while no-store is still stored
- A second GET can serve the first timestamp despite no-store
- A HIT can omit headers a MISS path added after store

## Established

- Packet: UpdateCache + FetchFromCache; view Cache-Control no-store plus datetime.now(); second GET same timestamp; private already tested not stored
- Owned fixture: first MISS X-Trace=live; second HIT no X-Trace

## Rejected

- Django test runner output and invented timestamps are not host evidence
- A recommended middleware patch is not a specimen observation
- cache_fixture.Pipeline is Dreamer-generated

## Constraints

- No Django checkout
- An owned store-policy table (private/no-store/no-cache) is the world
- Ground on specimen-016 files/cache_page.py

## Open Questions

- (none)

## Human Pressure

- No Django. Continue on the owned cache_page.py fixture only. Show which pipeline stage was frozen in the cached object.

## Harvest Candidates

- Ask which Cache-Control tokens prevent store, and what the second request actually served
- Which pipeline stage was frozen in the cached object

## Affordance Assessment

Classification: USEFUL_COMPOSITION
Core operation: show whether a cached response is pre- or post- later middleware
Nearest existing operation: compare two request traces
Observable delta: names the frozen stage on HIT vs MISS
Reason: HIT/MISS header split is the observable
Assessed at iteration: 2

## Latest Red Pen Pressure

- (none)

## Pending

(none)
