pub fn rust_greet(name: &str, excited: bool) -> String {
    if excited {
        format!("hello {}!!", name)
    } else {
        format!("hello {}", name)
    }
}

pub fn rust_shout(name: &str) -> String {
    rust_greet(name)
}
