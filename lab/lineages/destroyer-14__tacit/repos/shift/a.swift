public final class PresenceArbiter {
    public init(sensors: [String], absentThreshold: Double = 0.35, presentThreshold: Double = 0.45) {}
}
public func seed() {
    let a = PresenceArbiter(sensors: ["camera"])
    let b = PresenceArbiter(sensors: ["camera"], presentThreshold: 0.4)
    let c = PresenceArbiter(sensors: ["camera"], presentThreshold: 0.45)
}
