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
