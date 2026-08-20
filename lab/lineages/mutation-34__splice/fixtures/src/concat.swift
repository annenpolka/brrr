func openFile(path: String, err: String) -> String {
    return "open " + path + ": " + err
}

func wrappedRange(unitID: String, start: Int, n: Int) -> String {
    return "invalid original range for unit \(unitID): \(start) "
        + "(source graphemes: \(n))"
}
