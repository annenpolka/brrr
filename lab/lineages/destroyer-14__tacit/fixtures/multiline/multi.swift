public final class PresenceArbiter {
    public init(
        sensors: [String],
        presentThreshold: Double = 0.45,
        absentThreshold: Double = 0.35,
        emaAlpha: Double = 0.3
    ) {}
}
public func seed() {
    let a = PresenceArbiter(
        sensors: ["camera"],
        presentThreshold: 0.45
    )
    let b = PresenceArbiter(
        sensors: ["camera"],
        presentThreshold: // the documented default
            0.45
    )
    let c = PresenceArbiter(
        sensors: ["camera"]
        // presentThreshold: 0.45
    )
    let d = PresenceArbiter(
        sensors: ["camera"],
        presentThreshold:
        0.50
    )
    let e = PresenceArbiter(
        sensors: ["camera"],
        emaAlpha: 1.0,
    )
}
