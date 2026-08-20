import Testing

struct PresenceArbiterTests {
    struct EMASmoothing {
        @Test("初回読み取りはEMAなし（raw scoreがそのまま使われる）")
        func firstReadingNoSmoothing() {}
    }

    struct FusionLogic {
        @Test("カメラpresent + gazepresent → 総合present")
        func bothPresentResultsInPresent() {}
    }
}
