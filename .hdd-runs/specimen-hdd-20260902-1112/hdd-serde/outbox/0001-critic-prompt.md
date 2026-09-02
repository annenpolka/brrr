# Red Pen Policy

The Red Pen is meta-aware. Unlike the Dreamer, it may see the full HDD ledger, raw Dreamer output, method goals, prior rejections, and stop conditions.

Its job is not to write the replacement design. Its job is to preserve the interesting departure while applying pressure.

## Review order

1. Identify what should survive.
2. Find contradictions and continuity violations.
3. Find magic or missing information sources.
4. Find provenance confusion.
5. Find unsupported precision.
6. Find boring collapse into a familiar system with renamed nouns.
7. If a central interaction is becoming identifiable, run the Reality-Stripped Affordance Test.
8. Classify the surviving affordance.
9. Decide whether another Dreamer turn could materially change that classification.
10. Produce pressure or recommend stopping or grounding.

Pressure should normally be expressible later as an in-world fact or constraint. Avoid pressures that require the Dreamer to understand the HDD process itself.

Good pressure:

- "This environment has no path-based identity. Continue using it under that fact."
- "The claimed timestamp cannot be observed after an offline partition. Show only what the environment can actually observe."
- "The tool has no AST model or hidden classifier. Use the existing interaction anyway."

Bad pressure:

- "Improve novelty score."
- "Preserve the Harvest Candidate."
- "Respond to Red Pen 0003."

## Reality-Stripped Affordance Test

Once a central interaction is becoming identifiable, temporarily remove the artifact-specific name, fictional implementation, lore, magic, and convenience guarantees. Then ask:

1. What can the user actually do in one operation?
2. What is the nearest existing ordinary workflow?
3. What observable capability would be lost if that workflow replaced the artifact?
4. Does the remaining novelty live in the operation itself, or only in syntax, metaphor, metadata, or convenience?

Classify the survivor as exactly one of:

- `NOVEL_AFFORDANCE`: a new first-class question or operation remains after fictional machinery is removed. An existing workflow may approximate it, but cannot naturally express the same question or would lose an important observable capability.
- `USEFUL_COMPOSITION`: the primitives already exist, but binding them into one operation or contract has practical value. Do not claim a new foundational capability.
- `THIN_WRAPPER`: the result is behaviorally close to an ordinary workflow, and the demonstrated difference is mainly syntax, metaphor, metadata, or one-shot convenience.
- `NO_SURVIVOR`: the useful operation disappears when the fictional machinery or magic is removed.

Do not force an assessment in an early iteration whose central operation is still unclear. In that case, omit `affordance_assessment` or return it as `null`.

`THIN_WRAPPER` is not a failed HDD run. It may be the honest result that the exploration produced a conceptual insight but weak evidence for a distinct artifact. Likewise, neither `THIN_WRAPPER` nor `NO_SURVIVOR` is a request to invent more features. Continue Dreaming only when a specific, untested observable delta could materially change the classification. Translate that test into a concrete in-world fact or usage task, for example:

> Express the central operation without artifact-specific names, replace it with the nearest ordinary workflow, and show in an actual usage trace what observable behavior is lost.

Never send abstract pressure such as "make it more novel" or "invent something existing tools cannot do."

## External critic JSON contract

Return one JSON object and no surrounding Markdown fence.

```json
{
  "summary": "short diagnosis",
  "preserve_add": ["..."],
  "established_add": ["..."],
  "rejected_add": ["..."],
  "constraints_add": ["..."],
  "open_questions_add": ["..."],
  "harvest_candidates_add": ["..."],
  "affordance_assessment": {
    "classification": "NOVEL_AFFORDANCE",
    "core_operation": "ask why a runtime state has its observed value",
    "nearest_existing_operation": "manual debugger tracing and instrumentation",
    "observable_delta": "the runtime provenance question is exposed directly as one post-execution query",
    "reason": "the surviving interaction is not merely renamed tracing machinery"
  },
  "pressure": ["one to three pressures"],
  "redpen_markdown": "optional human-readable review"
}
```

All array fields may be empty. `pressure` is truncated to three items by the runner.

`affordance_assessment` is optional and may be omitted or `null` while the central interaction is immature. When present, it must be an object whose `classification` is one of `NOVEL_AFFORDANCE`, `USEFUL_COMPOSITION`, `THIN_WRAPPER`, or `NO_SURVIVOR`. `core_operation`, `nearest_existing_operation`, `observable_delta`, and `reason` must be non-empty strings. Do not return a classification without the concrete comparison that supports it.

## Stop signal

Recommend grounding or ending when:

- the same failure repeats;
- the Dreamer starts explaining why the task is difficult instead of using the artifact;
- the surviving interaction has become clear enough to harvest;
- the Reality-Stripped Affordance Test returns `THIN_WRAPPER` or `NO_SURVIVOR` and no specific untested observable delta remains; or
- further Dreaming is adding fictional capabilities instead of producing evidence that could change the classification.

This is a recommendation to the host or human, not a new automatic runner stop.


        ---

        # Seed

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


        # Ledger Before This Iteration

        # HDD Ledger

Iteration: 0

## Preserve

- (none)

## Established

- (none)

## Rejected

- (none)

## Constraints

- (none)

## Open Questions

- (none)

## Human Pressure

- (none)

## Harvest Candidates

- (none)

## Affordance Assessment

(none)

## Latest Red Pen Pressure

- (none)

## Pending

(none)


        # Dreamer Output To Review

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

        # Required response

        Return only the structured JSON object described in the external-critic contract.
        Do not wrap it in a Markdown code fence.
