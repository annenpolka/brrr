import XCTest

final class WindowTitleParserTests: XCTestCase {
    func testChrome() {
        _ = WindowTitleParser.isBrowser("Chrome")
        _ = WindowTitleParser.isBrowser("Safari")
        _ = WindowTitleParser.isBrowser("VS Code")
    }
}
