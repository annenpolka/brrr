# HDD Ledger

Iteration: 1

## Preserve

- A workspace member catalog: specifier can become a concrete npm range after bun update --latest while workspaces.catalog still holds the previous version

## Established

- Packet: Case B from packages/app, Tag::Catalog enters updating_packages; after install the string is a caret range; root catalog object leftover ^1.0.0
- Case A from workspace root does not rewrite member catalog: literals in this file; Case D explicit bun add is a pin not the silent leftover

## Rejected

- Invented bun update/explain transcripts are not host-executed

## Constraints

- Owned labeled member_spec vs catalog_range records. No bun.

## Open Questions

- (none)

## Human Pressure

- (none)

## Harvest Candidates

- whether the member still named catalog: or a leftover caret range while the catalog object kept the old identity

## Affordance Assessment

Classification: USEFUL_COMPOSITION
Core operation: name leftover catalog: join rewritten to a range while the catalog object still holds the old version
Nearest existing operation: grep catalog: in the member vs catalog.no-deps in the root
Observable delta: leftover_detach = member_spec != catalog: and catalog_range leftover old
Reason: grep of no-deps hits both files; the leftover is catalog: gone while the catalog object did not move
Assessed at iteration: 1

## Latest Red Pen Pressure

- (none)

## Pending

(none)
