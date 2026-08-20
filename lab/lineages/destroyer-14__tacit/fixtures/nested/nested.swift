public struct Thresholds {
    public init(driftDelay: Double = 15, awayDelay: Double = 90) {}
}
public struct SessionProfile {
    public init(
        name: String,
        colorHue: Double = 0.45,
        thresholds: Thresholds = Thresholds()
    ) {}
}
public struct PinProfile {
    public init(
        name: String,
        thresholds: Thresholds = Thresholds(driftDelay: 20)
    ) {}
}
public struct DotInit {
    public init(thresholds: Thresholds = .init()) {}
}
public func seed() {
    let a = SessionProfile(name: "coding")
    let b = SessionProfile(name: "x", thresholds: Thresholds())
    let c = SessionProfile(name: "y", thresholds: Thresholds(driftDelay: 15))
    let d = SessionProfile(name: "z", thresholds: Thresholds(driftDelay: 20))
    let e = PinProfile(name: "p")
    let f = PinProfile(name: "q", thresholds: Thresholds(driftDelay: 20))
    let g = DotInit()
    let t = Thresholds()
    let t2 = Thresholds(driftDelay: 15)
}
