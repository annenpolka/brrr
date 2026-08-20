import Testing

@Test
func userIsAlice() {
    #expect(os.getenv("USER") == "alice")
}
