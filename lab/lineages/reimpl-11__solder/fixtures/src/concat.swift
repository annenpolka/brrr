func openFile(path: String, err: String) -> String {
    return "open " + path + ": " + err
}

func wrappedRange(unitID: String, start: Int, n: Int) -> String {
    return "invalid original range for unit \(unitID): \(start) "
        + "(source graphemes: \(n))"
}

func done(response: () -> String) -> String {
    return response() + "\nDone."
}

func fence(response: () -> String) -> String {
    return "```json\n" + response() + "\n```"
}

func wrappedLead(body: String) -> String {
    return body
        + "\nDone."
}
