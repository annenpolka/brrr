public final class PresenceArbiter {
    public init(sensors: [String], threshold: Double = 0.4, emaAlpha: Double = 0.3) {}
}
public func seed() {
    let mute = PresenceArbiter(sensors: ["camera"])
    let spoken = PresenceArbiter(sensors: ["mic"])
    let fossil = PresenceArbiter(sensors: ["radar"], threshold: 0.4)
    let pre = PresenceArbiter(sensors: ["lidar"], threshold: 0.45)
}
