# HDD Ledger

Iteration: 2

## Preserve

- A field can be omitempty/optional in tags while a list-map-key treats it as required identity
- A field can be omitempty while a listMapKey treats it as identity

## Established

- Packet: CRD generation / HostAlias
- Dreamer wrote a tiny IdentityItem fixture; still invented the analyzer

## Rejected

- k8s-field-analyzer output is Dreamer-generated
- k8s-field-analyzer is not installed

## Constraints

- No k8s codegen; owned struct tags
- Ground by parsing struct tags only

## Open Questions

- (none)

## Human Pressure

- No CRD generator. Continue on a tiny struct-tag fixture. Show omitempty vs identity marker.

## Harvest Candidates

- Which tag said optional while another marker used the field as identity
- omitempty vs identity marker join

## Affordance Assessment

Classification: USEFUL_COMPOSITION
Core operation: name a field whose optionality tags disagree with identity markers
Nearest existing operation: read struct tags
Observable delta: one query joining omitempty vs listMapKey
Reason: grep hits both without joining
Assessed at iteration: 2

## Latest Red Pen Pressure

- (none)

## Pending

(none)
