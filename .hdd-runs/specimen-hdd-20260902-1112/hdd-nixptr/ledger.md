# HDD Ledger

Iteration: 1

## Preserve

- A done-set keyed by pointer address can skip a later lock node after that address is reused
- A done-set keyed by pointer can skip a distinct node that reused an address

## Established

- Packet: prefetch-inputs prints a different missing subset each run; done is std::set<const Node *>; work queued with std::bind
- Packet: flake-prefetch-inputs pointer reuse

## Rejected

- Invented nix flake prefetch-inputs --debug address logs and proposed src patches are not host evidence
- Invented %p logs and nix flake prefetch-inputs runs are not host-executed

## Constraints

- No nix. Owned events: insert(addr, name) then later worker(addr, name)
- Owned set of ids vs set of pointers fixture

## Open Questions

- (none)

## Human Pressure

- (none)

## Harvest Candidates

- Which node identities were inserted into done, whether those addresses still named the same lock nodes when the worker ran, and which inputs were never fetched
- address identity vs value identity of visited nodes

## Affordance Assessment

Classification: USEFUL_COMPOSITION
Core operation: show whether a visit set used pointer identity or value identity
Nearest existing operation: print object ids
Observable delta: skipped-because-pointer vs distinct-value
Reason: missed fetch from address reuse
Assessed at iteration: 1

## Latest Red Pen Pressure

- (none)

## Pending

(none)
