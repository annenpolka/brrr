public func detect() async -> PresenceReading {
    guard isEnabled else {
        return PresenceReading(status: .unknown, confidence: 0)
    }

    let readings = await readAllSensors()
    let active = readings.filter { $0.reading.isPresent != nil }

    guard !active.isEmpty else {
        recordObservation(status: .unknown, emaScore: 0)
        return PresenceReading(status: .unknown, confidence: 0)
    }

    let rawScore = calculateWeightedScore(active: active)
    if rawScore < absentThreshold {
        return PresenceReading(status: .absent, confidence: rawScore)
    } else if rawScore >= presentThreshold {
        return PresenceReading(status: .present, confidence: rawScore)
    } else {
        return PresenceReading(status: .unknown, confidence: rawScore)
    }
}
