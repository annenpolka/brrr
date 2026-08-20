let result = WindowTitleParser.extractSiteName(
    from: "GitHub - annenpolka/sitbone · Pull Request #3 - Google Chrome",
    app: "Google Chrome"
)
XCTAssertEqual(result, "GitHub")
