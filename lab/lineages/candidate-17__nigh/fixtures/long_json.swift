func load() {
    let json = #"{"default_provider":"codex","default_model":"claude-haiku-4-5","escalation_model":"claude-opus-5"}"#
    _ = json
}

func check(model: String) -> Bool {
    return model == "claude-haiku-4-5"
}
