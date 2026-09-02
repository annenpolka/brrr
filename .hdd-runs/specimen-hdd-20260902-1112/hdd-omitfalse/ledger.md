# HDD Ledger

Iteration: 1

## Preserve

- An encoder can omit false while a sibling keeps the key; downstream treats missing as true
- One encoder can drop a false value so the decoded object lacks the key; another keeps "flag": false
- Downstream that treats a missing key as true inverts the omitted false

## Established

- Host two_encoders.py: A {"name":"x"} A_has_flag False; B {"flag":false,"name":"x"} B_has_flag True
- Owned two encodings: A {"name": "x"} A_has_flag False; B {"flag": false, "name": "x"} B_has_flag True

## Rejected

- Invented cli inspect/diff/probe is not installed
- Invented cli inspect/diff/probe transcripts are not installed
- Recommended encoder patch is not host evidence

## Constraints

- Owned two JSON encodings. No encoder library theater.
- No invented CLI. Owned two JSON objects. Name which encoding dropped false and whether the decoded object still has the key

## Open Questions

- (none)

## Human Pressure

- (none)

## Harvest Candidates

- which encoder dropped false, and whether the decoded object still has the key
- which encoding omitted false, and whether the decoded object still has that key

## Affordance Assessment

Classification: USEFUL_COMPOSITION
Core operation: name keys present as false in one encoding and absent in the other
Nearest existing operation: json.dumps / key membership
Observable delta: dropped_false flag; A_has no; B_has yes
Reason: join omit-false with missing-as-true; not listMapKey tagjoin
Assessed at iteration: 1

## Latest Red Pen Pressure

- (none)

## Pending

(none)
