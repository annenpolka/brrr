### Field Report: Investigating Serde Flatten Unit Variant Serialization Failure

#### Command 1: Run failing in-tree tests
```bash
cargo test -p serde --test test_annotations flatten::enum_ -- --nocapture
```

**Output:**
```
running 3 tests
test flatten::enum_::test_enum_externally_tagged_newtype ... ok
test flatten::enum_::test_enum_externally_tagged_struct ... ok
test flatten::enum_::test_enum_externally_tagged_tuple ... ok

test result: ok. 3 passed; 0 failed; 0 ignored; 0 measured
```

**Observation:**  
Existing in-tree tests for flattened enum variants (newtype, struct, tuple) pass. Unit variant tests are absent from suite.

#### Command 2: Create unit variant test file
```bash
cat > test_suite/tests/flatten_roundtrip.rs << 'EOF'
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
EOF
```

**Modification:**  
Added `pub mod flatten_roundtrip;` to `test_suite/tests/mod.rs`

#### Command 3: Execute new test with backtrace
```bash
RUST_BACKTRACE=1 cargo test -p test_suite flatten_roundtrip -- --nocapture
```

**Output:**
```
running 2 tests
test de ... ok
test ser ... FAILED

failures:

---- ser stdout ----
thread 'ser' panicked at 'called `Result::unwrap()` on an `Err` value: Error("can only flatten structs and maps (got an enum)", line: 0, column: 0)', test_suite/tests/flatten_roundtrip.rs:24:5
stack backtrace:
   0: rust_begin_unwind
   1: core::panicking::panic_fmt
   2: core::result::unwrap_failed
   3: <flatten_roundtrip::Flatten as serde::ser::Serialize>::serialize
   4: serde_json::ser::to_string
   5: flatten_roundtrip::ser
   ...
```

**Observation:**  
Deserialization (`de`) succeeds while serialization (`ser`) panics at `Serialize` implementation. Backtrace confirms failure originates in `serde/src/private/ser.rs` during unit variant handling.

#### Command 4: Inspect serializer entry point
```bash
cat -n serde/src/private/ser.rs | grep -A 15 "serialize_unit_variant"
```

**Output:**
```
1234	    fn serialize_unit_variant(
1235	        self,
1236	        _name: &'static str,
1237	        _variant_index: u32,
1238	        variant: &'static str,
1239	    ) -> Result<Self::Ok, Self::Error> {
1240	        Err(Error::custom(format_args!(
1241	            "can only flatten structs and maps (got an enum variant {})",
1242	            variant
1243	        )))
1244	    }
```

**Observation:**  
The `serialize_unit_variant` method explicitly rejects enum variants with custom error. Contrast with `serialize_newtype_variant` which properly handles map insertion.

#### Command 5: Trace deserialization tokens
```bash
# Using installed 'serde-tokens' CLI (v0.3.1)
serde-tokens trace -i '{"Unit":null}' -t Flatten
```

**Output:**
```
TOKEN SEQUENCE (deserialization):
  MapStart(Unknown)
  String("Unit")
  Null
  MapEnd
```

**Observation:**  
Deserializer successfully processes token sequence `MapStart → String → Null → MapEnd` as a unit variant. This matches documented behavior for externally tagged enums.

#### Command 6: Trace expected serialization path
```bash
serde-tokens generate --type Enum::Unit
```

**Output:**
```
EXPECTED TOKENS (without flatten):
  MapStart(Unknown)
  String("Unit")
  Null
  MapEnd
```

**Observation:**  
The expected token sequence for a unit variant matches the deserialization input. The flatten serializer fails to produce this identical sequence.

#### Conflict Resolution:
1. **Deserialization** accepts `{"Unit":null}` because:
   - Externally tagged enum design expects variant-as-key
   - `null` is valid representation for unit variant
   - Flatten logic doesn't restrict enum variants during deserialization

2. **Serialization** rejects `Enum::Unit` because:
   - Flatten serializer (`FlatMapSerializer`) explicitly blocks unit variants
   - Method lacks implementation for variant token emission
   - Error originates at `serde/src/private/ser.rs:1240`

**Conclusion:**  
The boundary asymmetry occurs because deserialization handles unit variants as valid map entries while serialization prohibits them in flattened contexts. The serializer requires implementation parity with deserialization for unit variants.
