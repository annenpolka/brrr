func startSession(name: String) {
    Logger.coreSession.info("session started profile=\(name, privacy: .private)")
    Logger.sensorsCamera.warning("device init failed")
}

func saveFail(path: String, err: String) {
    Logger.dataStore.error("""
        cumulative save failed path=\(path) \
        error=\(err)
        """)
}

func logCamera(enabled: Bool) {
    Logger.coreSession.info(
        "camera presence \(enabled ? "enabled" : "disabled", privacy: .public)"
    )
}

func logTransition(from: String, to: String, reason: String, idle: Int) {
    Logger.coreState.info("""
        transition \(from, privacy: .public) → \(to, privacy: .public) \
        reason=\(reason, privacy: .public) idle=\(idle, privacy: .public)s \
        deserted=\(0, privacy: .public) \
        driftRecovered=\(0, privacy: .public) \
        awayRecovered=\(0, privacy: .public)
        """)
}
