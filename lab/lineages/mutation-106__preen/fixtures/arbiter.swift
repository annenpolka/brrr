public struct Thresholds {
    public init(
        driftDelay: Double = 15,
        awayDelay: Double = 90
    ) {
        self.driftDelay = driftDelay
        self.awayDelay = awayDelay
    }
    public let driftDelay: Double
    public let awayDelay: Double
}

public final class PresenceArbiter {
    public init(
        sensors: [String],
        presentThreshold: Double = 0.45,
        absentThreshold: Double = 0.35,
        emaAlpha: Double = 0.3,
        frameProvider: String? = nil
    ) {}
}

// comment residue must not be a call: PresenceArbiter(SitboneCore)
public func seed() {
    let a = PresenceArbiter(sensors: ["camera"])
    let b = PresenceArbiter(sensors: ["camera"], presentThreshold: 0.45)
    let c = PresenceArbiter(sensors: ["camera"], presentThreshold: 0.50, emaAlpha: 1.0)
    let d = PresenceArbiter(sensors: list, frameProvider: provider)
    let t = Thresholds()
    let t2 = Thresholds(driftDelay: 15)
    let t3 = Thresholds(driftDelay: 20)
}

public struct SessionProfile {
    public init(
        name: String,
        colorHue: Double = 0.45,
        thresholds: Thresholds = Thresholds()
    ) {}
}

public func profiles() {
    let p = SessionProfile(name: "coding")
    let q = SessionProfile(name: "default", colorHue: 0.45)
    let b = SessionProfile(name: "x", thresholds: Thresholds())
    let c = SessionProfile(name: "y", thresholds: Thresholds(driftDelay: 15))
    let d = SessionProfile(name: "z", thresholds: Thresholds(driftDelay: 20))
}

public struct PinProfile {
    public init(name: String, thresholds: Thresholds = Thresholds(driftDelay: 20)) {}
}

public struct DotInit {
    public init(name: String, thresholds: Thresholds = .init()) {}
}

public func nested() {
    let e = PinProfile(name: "p")
    let f = DotInit(name: "d")
}
