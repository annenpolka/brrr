public final class PresenceArbiter {
    public init(sensors: [String]) {}
    public func detect(timeout: Double = 30) -> Double { timeout }
}

public func tickArbiter() {
    _ = PresenceArbiter(sensors: []).detect(timeout: 0)
}
