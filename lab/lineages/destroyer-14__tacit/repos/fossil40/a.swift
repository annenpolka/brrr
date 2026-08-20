public final class PresenceArbiter {
    public init(sensors: [String], presentThreshold: Double = 0.45) {}
}
public func seed() {
    let a = PresenceArbiter(sensors: ["camera"], presentThreshold: 0.40)
}
