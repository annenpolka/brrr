# HDD Ledger

Iteration: 1

## Preserve

- Flatten deserialize can accept a unit variant as a map key with null value
- Flatten serialize can reject that same unit variant
- Flatten of a unit-like variant can be untested while other flatten shapes pass

## Established

- Packet: de of {"Unit":null} passes; ser panics can only flatten structs and maps (got an enum)
- Packet: serde flatten unit variant

## Rejected

- serde-tokens is not installed; token traces are Dreamer-generated
- In-tree cargo test transcripts were not produced on this host
- cargo test transcripts are Dreamer-generated

## Constraints

- No serde checkout, no cargo
- The user snippet and the packet error string are the world
- No cargo/serde checkout

## Open Questions

- (none)

## Human Pressure

- (none)

## Harvest Candidates

- Ask which direction of the format boundary accepted the unit variant and which rejected it
- Ask which flatten shape has no roundtrip

## Affordance Assessment

Classification: USEFUL_COMPOSITION
Core operation: name which flattened variant shape does not roundtrip
Nearest existing operation: write one more unit test
Observable delta: one query that lists missing flatten shapes vs passing ones
Reason: test pass/fail on other variants hides the missing unit case
Assessed at iteration: 1

## Latest Red Pen Pressure

- No crate checkout. Continue on a tiny flatten roundtrip table with a missing unit shape.

## Pending

(none)
