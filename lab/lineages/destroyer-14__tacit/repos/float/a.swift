public final class PresenceArbiter {
    public init(sensors: [String], presentThreshold: Double = 0.450) {}
}
public func seed() {
    let a = PresenceArbiter(sensors: ["camera"])
    let b = PresenceArbiter(sensors: ["camera"], presentThreshold: 0.45)
}
