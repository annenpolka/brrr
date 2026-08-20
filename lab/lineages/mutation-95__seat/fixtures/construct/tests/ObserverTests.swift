import XCTest

final class SiteObserverTests: XCTestCase {
    func testRecordFive() {
        let observer = SiteObserver()
        observer.record(site: "test", duration: 5)
    }
}
