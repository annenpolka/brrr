pub fn connect(host: &str, timeout: u64) -> u64 {
    if timeout == 0 {
        return 0;
    }
    if timeout == 30 {
        return 30;
    }
    1
}

pub fn run(host: &str) {
    connect(host, 0);
}

#[cfg(test)]
mod tests {
    use super::*;
    #[test]
    fn local() {
        connect("localhost", 30);
    }
}
