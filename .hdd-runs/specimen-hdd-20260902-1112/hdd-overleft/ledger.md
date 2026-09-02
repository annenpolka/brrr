# HDD Ledger

Iteration: 1

## Preserve

- A nested override can leave OverrideSet on a node after the carrying edge detaches, while a second install records the original non-overridden lock identity

## Established

- Packet: first install applies nested json-server.package-json=7.0.0; second install with lock/node_modules leftover original; in-tree Edge.detach does not clear node.overrides
- top-level override is a different identity axis; never-overridden original has no OverrideSet

## Rejected

- Invented arborist REPL / npm install transcripts are not host-executed

## Constraints

- Owned labeled lock-version vs override-set records. No npm.

## Open Questions

- (none)

## Human Pressure

- (none)

## Harvest Candidates

- whether the node still names leftover OverrideSet after the carrying edge is gone, while lock identity is the original non-overridden version

## Affordance Assessment

Classification: USEFUL_COMPOSITION
Core operation: name leftover OverrideSet after edge detach versus lock original identity
Nearest existing operation: grep the nested override in package.json and the version in the lockfile
Observable delta: leftover_override = override_set yes and lock_version is original
Reason: grep of package-json hits lock and package.json; the leftover is OverrideSet after the carrying edge is gone
Assessed at iteration: 1

## Latest Red Pen Pressure

- (none)

## Pending

(none)
