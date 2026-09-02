# HDD Ledger

Iteration: 1

## Preserve

- A go.sum can list a module version as go.mod-only without a zip content sum

## Established

- Packet: after go mod download with empty go.sum, grep '^rsc.io/quote v1.5.2 ' shows only the /go.mod line
- tidy (or Go 1.16+ download) has both unsuffixed zip line and /go.mod line
- sumdb is not consulted for versions already listed in go.sum

## Rejected

- Invented gosum-analyze transcripts are not host-executed

## Constraints

- Owned two go.sum fixtures. No go toolchain.

## Open Questions

- (none)

## Human Pressure

- (none)

## Harvest Candidates

- which identity go.sum contained for a module version after download: zip content sum, go.mod-only sum, both, or neither

## Affordance Assessment

Classification: USEFUL_COMPOSITION
Core operation: name go.sum identity class for a module version: zip, mod-only, both, or neither
Nearest existing operation: grep the module path in go.sum
Observable delta: mod-only vs both vs zip-only vs neither
Reason: grep of the module path hits both line types
Assessed at iteration: 1

## Latest Red Pen Pressure

- (none)

## Pending

(none)
