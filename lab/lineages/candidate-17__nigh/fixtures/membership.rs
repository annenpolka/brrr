fn path_ok(kind: &str) -> bool {
    matches!(kind, "punch-through" | "ricochet" | "chain")
}

fn built() -> &'static str {
    "punch-through"
}
