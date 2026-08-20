public struct Thresholds {
    public init(driftDelay: Double = 15) {}
    public init(from decoder: Int) {
        self.init(driftDelay: 15)
    }
}
public func fetch(url: String, timeout: Double = 30, completion: (Int) -> Void = { _ in }) {}
public func seed() {
    fetch(url: "x") { n in }
    fetch(url: "x")
    _ = Thresholds(driftDelay: 15)
}
