public final class PresenceArbiter {
    public init(sensors: [String], threshold: Double = 0.4, emaAlpha: Double = 0.3) {}
}
public func seed() {
    let a = PresenceArbiter(sensors: ["camera"])
    let b = PresenceArbiter(sensors: ["camera"], threshold: 0.4)
}
