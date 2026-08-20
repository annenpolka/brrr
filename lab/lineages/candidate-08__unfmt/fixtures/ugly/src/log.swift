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
