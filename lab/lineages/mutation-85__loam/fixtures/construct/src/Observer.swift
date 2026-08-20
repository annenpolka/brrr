public final class SiteObserver {
    public init() {}
    public func record(site: String, duration: Double) {
        _ = (site, duration)
    }
}

public func tickObserver() {
    SiteObserver().record(site: "prod", duration: 1)
}
