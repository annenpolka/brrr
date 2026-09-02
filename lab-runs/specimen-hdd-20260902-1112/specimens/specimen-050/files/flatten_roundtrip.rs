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
