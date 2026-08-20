import Testing
@Test
func home() {
    #expect(home as Optional<String> == "/Users/annenpolka")
    #expect(User<Host>.home == "/Users/annenpolka/Library")
    #expect(items.contains(where: { $0.path == "/Users/annenpolka" }))
}
