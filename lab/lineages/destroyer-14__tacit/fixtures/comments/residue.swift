public final class PresenceArbiter {
    public init(sensors: [String], presentThreshold: Double = 0.45) {}
}
// comment residue must not be a call: PresenceArbiter(SitboneCore)
// PresenceArbiter(sensors: ["camera"], presentThreshold: 0.50)
public func seed() {
    let a = PresenceArbiter(sensors: ["camera"]) // presentThreshold: 0.45
    let b = PresenceArbiter(/* presentThreshold: 0.45 */ sensors: ["camera"])
    let c = PresenceArbiter(sensors: ["camera"] /* presentThreshold: 0.50 */)
    let s = "PresenceArbiter(sensors: [\"x\"], presentThreshold: 0.99)"
}
