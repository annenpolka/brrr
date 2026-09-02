# HDD Ledger

Iteration: 1

## Preserve

- An empty-map chart default can drop a user YAML-null key that a null chart default keeps

## Established

- Packet: default data:{} + user baz:~ → map[foo:bar]; default data:~ + same user → map[baz:<nil> foo:bar]; v3.19.3 kept present-nil for empty-map default

## Rejected

- Invented helm template runs and coalesce.go traces are not host-executed

## Constraints

- Owned two coalesce records. No helm.

## Open Questions

- (none)

## Human Pressure

- (none)

## Harvest Candidates

- whether user null survived given chart default empty-map vs null

## Affordance Assessment

Classification: USEFUL_COMPOSITION
Core operation: name a user-null key dropped by empty-map default coalesce and kept by null default
Nearest existing operation: print both maps
Observable delta: kept no vs kept yes for baz
Reason: two quoted maps still leave the default-shape join as a hand comparison
Assessed at iteration: 1

## Latest Red Pen Pressure

- (none)

## Pending

(none)
