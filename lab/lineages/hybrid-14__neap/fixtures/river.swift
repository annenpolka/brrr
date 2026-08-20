struct AppRiverRow {
    var flowScore: Double
    var barColor: Int {
        if app.flowScore > 0.2 {
            return 1
        } else if app.flowScore < -0.2 {
            return -1
        }
        return 0
    }
    var stored = 1
}
