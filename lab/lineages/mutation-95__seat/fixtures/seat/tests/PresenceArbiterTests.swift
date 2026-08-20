import Testing

struct PresenceArbiterTests {
    @Test func defaultTimeout() {
        let arbiter = PresenceArbiter(sensors: [])
        _ = arbiter.detect(timeout: 30)
    }
}
