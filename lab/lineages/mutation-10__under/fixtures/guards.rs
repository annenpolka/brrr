fn parse_header(bytes: &[u8]) -> Option<usize> {
    if bytes.starts_with(b"\"a/") {
        return Some(1);
    }
    if bytes.len() < 7 {
        return None;
    }
    if !bytes.starts_with(b"a/") {
        return None;
    }
    let p = (bytes.len() - 5) / 2;
    Some(p)
}
