# HDD Ledger

Iteration: 1

## Preserve

- An outer ignore-unknown setting can fail to apply inside a packed Any JSON object
- The inner parse can be a different writer instance with different options
- A flag that ignores unknown fields may not apply inside a nested Any-like envelope

## Established

- Packet: C++ Cannot find field. on unknown age inside Any while Go/Python accept; outer ignore_unknown_fields true
- Packet: nested Any + ignore_unknown_fields

## Rejected

- protostream_objectwriter.cc greps and line-precise constructors are not host evidence
- A recommended TypeInfo constructor that copies parent options is a Dreamer patch, not a specimen observation
- json_util_test.cc transcripts are Dreamer-generated

## Constraints

- No protobuf checkout, no C++ rebuild
- A tiny owned nested-options fixture (outer ignore vs inner defaults) is the world
- No protobuf/bazel
- A nested dict parser fixture is the world

## Open Questions

- Can the inner vs outer options be shown without the C++ sources?

## Human Pressure

- (none)

## Harvest Candidates

- Ask which parser instance saw the nested object and which options that instance actually had
- Ask which nested envelope did not inherit ignore-unknown

## Affordance Assessment

Classification: USEFUL_COMPOSITION
Core operation: show whether an ignore-unknown policy applied inside a nested envelope
Nearest existing operation: read the parser options and the nested type
Observable delta: one query naming the layer where the flag stopped
Reason: a single error string does not name the layer
Assessed at iteration: 1

## Latest Red Pen Pressure

- No protobuf tree. Continue on a nested JSON-like fixture with an ignore-unknown flag that does not enter an Any envelope.

## Pending

(none)
