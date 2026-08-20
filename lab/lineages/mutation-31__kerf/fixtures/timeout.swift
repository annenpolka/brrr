// Negative: HTTP range must not sit on a timeout of 300.
let timeout: TimeInterval = 300

func success(http: HTTPURLResponse) -> Bool {
    return (200..<300).contains(http.statusCode)
}
