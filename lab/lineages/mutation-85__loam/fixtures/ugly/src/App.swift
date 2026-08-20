public enum WindowTitleParser {
    private static let browsers: Set<String> = [
        "Chrome", "Safari", "Brave Browser", "Microsoft Edge"
    ]
    public static func isBrowser(_ appName: String) -> Bool {
        if appName == "Chrome" { return true }
        if appName == "Safari" { return true }
        return browsers.contains(appName)
    }

    public static func extractSiteName(from title: String, app: String) -> String? {
        guard isBrowser(app) else { return nil }
        return title
    }
}

public func tick(app: String) {
    _ = WindowTitleParser.isBrowser(app)
}
