# HDD Ledger

Iteration: 1

## Preserve

- (none)

## Established

- Packet: Case B destroy apply error with non-null NewState+NewIdentity omits Identity from the new state object; Case C mark-only sensitivity update copies Value/Private/Status and omits Identity
- Case A success path already sets Identity: resp.NewIdentity; Case D null new value DeepCopy keeps prior identity

## Rejected

- Invented tfstate-analyzer create-fixture / simulate-apply transcripts are not host-executed

## Constraints

- Do not send terraform apply-state theater back to R1. Distinct from specimen-081.

## Open Questions

- (none)

## Human Pressure

- (none)

## Harvest Candidates

- (none)

## Affordance Assessment

Classification: THIN_WRAPPER
Core operation: name leftover omitted Identity field after apply copied Value/Private/Status
Nearest existing operation: diff the two ResourceInstanceObject literals vs the success path Identity: resp.NewIdentity
Observable delta: leftover_omit = Identity field absent AND Value/Private/Status present
Reason: Dreamer restated the seed Case B/C struct literals; two greps of node_resource_abstract_instance.go already are the harvest
Assessed at iteration: 1

## Latest Red Pen Pressure

- (none)

## Pending

(none)
