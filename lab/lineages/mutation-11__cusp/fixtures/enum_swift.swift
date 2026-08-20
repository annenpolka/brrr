enum PresenceStatus {
    case present
    case absent
    case unknown
    case none
}

func leave(previous: PresenceStatus) -> PresenceStatus {
    switch previous {
    case .present:
        return .present
    case .absent, .unknown, .none:
        return .absent
    }
}

func missing() -> PresenceStatus {
    return .unknown
}
