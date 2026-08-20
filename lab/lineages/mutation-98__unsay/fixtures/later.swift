public final class PresenceArbiter {
    public init(sensors: [String], presentThreshold: Double = 0.45, emaAlpha: Double = 0.3) {}
}
public func seed() {
    let mute = PresenceArbiter(sensors: ["camera"])
    let spoken = PresenceArbiter(sensors: ["mic"], presentThreshold: 0.45)
    let fossil = PresenceArbiter(sensors: ["radar"], presentThreshold: 0.4)
    let pre = PresenceArbiter(sensors: ["lidar"], presentThreshold: 0.45)
    let late = PresenceArbiter(sensors: ["new"], presentThreshold: 0.45)
}
