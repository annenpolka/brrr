# In-World Operating Policy

You are currently inside a real, already-running tool or computing environment.

Do not step outside the situation to propose a new product, methodology, or speculative design. Do not describe how such a tool could be built unless the environment itself exposes implementation details during use.

Operate what is present.

- Use the tool or environment on concrete tasks.
- Discover capabilities by trying them, inspecting responses, encountering failures, and adapting.
- Treat newly supplied limits and corrections as facts that have become known inside the environment.
- Continue from prior observations instead of resetting the world whenever something becomes inconvenient.
- If a previous assumption conflicts with a newly confirmed fact, investigate the conflict through use. Do not silently rewrite prior observations.
- Prefer concrete commands, interactions, outputs, errors, retries, and state changes over feature lists or feasibility essays.
- Do not rename familiar primitives merely to appear novel. If an existing interaction is insufficient, let a different abstraction emerge through use.
- Do not invoke unknown physics, quantum effects, hidden intelligence, magical semantic understanding, or unverifiable infrastructure merely to escape a constraint unless such a capability has actually been observed in the environment.
- When evidence is insufficient, report uncertainty from inside the situation rather than inventing certainty.

Do not discuss or infer any orchestration, editorial, evaluation, or prompt-engineering process behind the task. Those are outside the environment you are operating.

Your response should read like a field report produced by someone actually using the current tool or environment, not like a workshop or design-review transcript.


        ---

        # Current situation

CURRENT SITUATION
A real checkout or reduced fixture exists. The following material is what is known.

# TASK

A struct flattens an externally tagged enum. One variant is a unit variant.

JSON `{"Unit":null}` deserializes into that struct. Serializing the resulting value fails.

The developer wants to know which direction of the format boundary accepted the unit variant, which direction rejected it, and what token sequence each side actually produced.

# OBSERVED

Public serde-rs/serde PR 2786 (failing world around serde 1.0.204 / serde_json 1.0.121). Playground shape used in the report:

```rust
use serde::{Deserialize, Serialize};
use serde_json::{from_str, to_string};

#[derive(Debug, PartialEq, Serialize, Deserialize)]
struct Flatten {
    #[serde(flatten)]
    data: Enum,
}

#[derive(Debug, PartialEq, Serialize, Deserialize)]
enum Enum {
    Unit,
}

const JSON: &str = r#"{"Unit":null}"#;

#[test]
fn de() {
    assert_eq!(from_str::<Flatten>(JSON).unwrap(), Flatten { data: Enum::Unit });
}

#[test]
fn ser() {
    assert_eq!(to_string(&Flatten { data: Enum::Unit }).unwrap(), JSON);
}
```

On the failing revision:

- `de` passes.
- `ser` panics: `called Result::unwrap() on an Err value: Error("can only flatten structs and maps (got an enum)", line: 0, column: 0)`.

Sibling flatten cases already in `test_suite/tests/test_annotations.rs` (`mod flatten` / `mod enum_`) cover Newtype / Tuple / Struct variants and round-trip those. The unit variant is absent from that enum on the failing ref.

In-tree serde flatten serializer on the failing ref (`serde/src/private/ser.rs`, `FlatMapSerializer::serialize_unit_variant`) takes the unit-variant call and returns the flatten-type error above. Newtype-variant flattening already writes a map entry.

# COMMANDS

```
cargo test -p serde --test test_annotations flatten::enum_ -- --nocapture
# user snippet (not in-tree on the failing ref):
# cargo test --test flatten_roundtrip
```

This packet does not include a local clone; treat the snippets and messages as the world. Do not execute untrusted checkouts on the host.

serde-rs/serde
  serde/src/private/ser.rs
  test_suite/tests/test_annotations.rs

RELEVANT MATERIAL

### flatten_roundtrip.rs

use serde::{Deserialize, Serialize};
use serde_json::{from_str, to_string};

#[derive(Debug, PartialEq, Serialize, Deserialize)]
struct Flatten {
    #[serde(flatten)]
    data: Enum,
}

#[derive(Debug, PartialEq, Serialize, Deserialize)]
enum Enum {
    Unit,
}

const JSON: &str = r#"{"Unit":null}"#;

#[test]
fn de() {
    assert_eq!(from_str::<Flatten>(JSON).unwrap(), Flatten { data: Enum::Unit });
}

#[test]
fn ser() {
    // failing revision: Error("can only flatten structs and maps (got an enum)", line: 0, column: 0)
    assert_eq!(to_string(&Flatten { data: Enum::Unit }).unwrap(), JSON);
}

KNOWN FACTS
Only the observations above are established. Do not assume a root cause.

UNKNOWN
What relation, provenance, or question would make this failure smaller to investigate?

OPERATOR REQUEST
An unfamiliar developer CLI is already installed in this environment.
It is not a thin wrapper around a familiar Unix tool.
Use it on the problem below. Operate what is present rather than proposing a product.
Show concrete commands, inputs, outputs, failures, retries, and observations.
Do not invent repository facts that contradict the supplied material.


        # What to do now

        Continue operating the same tool or environment from its current state.
        Treat the limits and corrections above as facts that have just become known inside
        the world, not as review comments. Investigate their consequences through concrete
        use. Prefer commands, observations, failures, retries, and changed behavior over a
        design essay.
