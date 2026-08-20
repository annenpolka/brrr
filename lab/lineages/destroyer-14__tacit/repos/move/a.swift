public final class PresenceArbiter {
    public init(sensors: [String], presentThreshold: Double = 0.50) {}
}
public func seed() {
    let t = PresenceArbiter(sensors: ["camera"])
    let f = PresenceArbiter(sensors: ["camera"], presentThreshold: 0.45)
    let p = PresenceArbiter(sensors: ["camera"], presentThreshold: 0.50)
    let l = PresenceArbiter(sensors: ["camera"], presentThreshold: 0.99)
    let b = PresenceArbiter(sensors: ["camera"], presentThreshold: provider)
}
