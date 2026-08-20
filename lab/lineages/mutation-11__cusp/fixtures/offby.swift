func hint(httpStatus statusCode: Int) -> String {
    if statusCode == 401 {
        return "expired"
    }
    return "other"
}

func testClient() -> Int {
    let statusCode = 400
    return statusCode
}
