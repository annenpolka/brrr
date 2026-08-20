public final class PresenceArbiter {
    public init(sensors: [String], presentThreshold: Double = 0.45, emaAlpha: Double = 0.3) {}
}
public func seed() {
    let a = PresenceArbiter(sensors: ["camera"])
    let b = PresenceArbiter(sensors: ["camera"], presentThreshold: 0.4)
}
