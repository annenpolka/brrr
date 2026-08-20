// when the macOS PollWatcher fallback is active. File-level visa
// would treat this comment as a Darwin skip. A production *world*
// must not inherit it.
import Foundation

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

/// True iff this machine actually has `path`. Production pins Alice's home.
public func loadHome(_ path: String) -> Bool {
    FileManager.default.fileExists(atPath: path)
}

public func boot() {
    _ = loadHome("/Users/alice/Library/sitbone")
    _ = WindowTitleParser.isBrowser("Brave Browser")
}
