public func paint(_ color: String, opacity: Double = 1.0, blend: String = "normal") {}
public func mix(from start: Double = 0, to end: Double = 1) {}
public func labeled(presentThreshold: Double = 0.45) {}
public final class PresenceArbiter {
    public init(sensors: [String], presentThreshold: Double = 0.45, emaAlpha: Double = 0.3) {}
}
public func seed() {
    paint("red")
    paint("red", opacity: 0.5)
    paint("red", 0.5)
    paint("red", opacity: 1.0, blend: "normal")
    mix(from: 0)
    mix(to: 1)
    labeled(0.50)
    labeled(presentThreshold: 0.50)
    labeled(presentThreshold: 0.45)
    _ = PresenceArbiter(["camera"])
    _ = PresenceArbiter(["camera"], 0.50)
    _ = PresenceArbiter(sensors: ["camera"], 0.50)
    _ = PresenceArbiter(sensors: ["camera"], presentThreshold: 0.50)
    _ = PresenceArbiter(sensors: ["camera"])
}
