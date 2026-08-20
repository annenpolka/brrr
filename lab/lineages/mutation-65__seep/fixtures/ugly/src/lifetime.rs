pub struct SelectState<'a> {
    pub prompt: &'a str,
}

impl<'a> SelectState<'a> {
    pub fn new(prompt: &'a str, items: &'a [&'a str], default: usize) -> Self {
        let _ = (prompt, items, default);
        Self { prompt }
    }

    pub fn later(x: i32) -> i32 {
        x
    }
}

pub fn boot(s: &str) {
    let _ = SelectState::new(s, &[s], 0);
    later(1);
}

#[cfg(test)]
mod tests {
    use super::*;
    #[test]
    fn later_zero() {
        later(0);
    }
}
