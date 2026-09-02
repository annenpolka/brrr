# HDD Ledger

Iteration: 1

## Preserve

- Class attribute mutation can leak between tests while module globals look unchanged

## Established

- Host: ordleak names Box.bucket; leakorder leaked=none on specimen-060

## Rejected

- state-inspector is not installed

## Constraints

- Do not mint a third leak CLI; mutate leakorder isolation

## Open Questions

- (none)

## Human Pressure

- (none)

## Harvest Candidates

- Include class attributes in leak identity

## Affordance Assessment

Classification: USEFUL_COMPOSITION
Core operation: name a class-attribute leak that only appears when test order changes
Nearest existing operation: ordleak on specimen-060
Observable delta: Box.bucket vs leaked=none
Reason: module snapshot is the wrong object
Assessed at iteration: 1

## Latest Red Pen Pressure

- (none)

## Pending

(none)
