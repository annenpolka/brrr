import Foundation

func checkThresholds(presentThreshold: Double, absentThreshold: Double) {
    precondition(
        presentThreshold > absentThreshold,
        "presentThreshold must be greater than absentThreshold (got \(presentThreshold) vs \(absentThreshold))"
    )
}

func logSession(name: String) {
    print("session started profile=\(name, privacy: .private)")
}

func logCamera(enabled: Bool) {
    print("camera presence \(enabled ? "enabled" : "disabled", privacy: .public)")
}

func logTransition(from: String, to: String, reason: String, idle: Int) {
    print("""
        transition \(from, privacy: .public) → \(to, privacy: .public) \
        reason=\(reason, privacy: .public) idle=\(idle, privacy: .public)s
        """)
}
