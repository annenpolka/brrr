# HDD Ledger

Iteration: 1

## Preserve

- Leftover identity JSON against a nil identity schema does not yield a usable identity

## Established

- Packet: Decode takes IdentityJSON != nil then schema.Identity.ImpliedType(); nil receiver EmptyObject
- Case B with identity schema decodes {id: foo}; case C nil JSON skips identity branch

## Rejected

- Invented terraform Decode transcripts are not host-executed

## Constraints

- Owned schema/json records. No terraform.

## Open Questions

- (none)

## Human Pressure

- (none)

## Harvest Candidates

- which decode class leftover IdentityJSON produced when current schema had no identity: object, typed-null, omitted, or unsupported-attribute error

## Affordance Assessment

Classification: USEFUL_COMPOSITION
Core operation: name decode class of leftover identity JSON against nil vs present schema
Nearest existing operation: print IdentityJSON and Identity: nil
Observable delta: error vs object vs omitted
Reason: the leftover bytes look like identity; decode class is the miss
Assessed at iteration: 1

## Latest Red Pen Pressure

- (none)

## Pending

(none)
