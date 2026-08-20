fn render<'a>(x: &'a str) -> Line<'static> {
    x == "keep-me"
}

struct Line<'static> {}

fn built() -> &'static str {
    "keep-me"
}
