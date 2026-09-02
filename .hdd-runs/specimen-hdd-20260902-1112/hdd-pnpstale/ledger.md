# HDD Ledger

Iteration: 1

## Preserve

- storedBuildState can still name a locator as already-built after .yarn/unplugged is deleted

## Established

- Packet: after rm -rf .yarn/unplugged, yarn install skips YN0007 because buildHash is path-string based and the leftover hash remains
- Never-built has no storedBuildState row; intact unplugged has hash and .ready

## Rejected

- Invented yarn add/install/rebuild transcripts are not host-executed

## Constraints

- Owned labeled excerpts: stored_hash vs unplugged_ready. No yarn.

## Open Questions

- (none)

## Human Pressure

- (none)

## Harvest Candidates

- whether install-state identity after unplug-delete is leftover already-built hash, omitted never-built, or a new content hash

## Affordance Assessment

Classification: USEFUL_COMPOSITION
Core operation: name leftover already-built storedBuildState after unplugged tree is gone
Nearest existing operation: grep the locator in build-state.yml and ls .yarn/unplugged
Observable delta: leftover_built = stored_hash and not ready
Reason: grep of the locator hits build-state; the miss is the absent .ready/binary
Assessed at iteration: 1

## Latest Red Pen Pressure

- (none)

## Pending

(none)
