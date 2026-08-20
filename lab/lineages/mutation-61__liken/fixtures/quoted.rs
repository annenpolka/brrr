fn parse_diff_git_header(rest: &str) -> Option<PathBuf> {
    let bytes = rest.as_bytes();

    if bytes.starts_with(b"\"a/") {
        // Quoted form: nested checks, then a total return.
        let (_a_decoded, after_a) = parse_quoted_token(bytes)?;
        let after_space = after_a.strip_prefix(b" ")?;
        let (b_decoded, _tail) = parse_quoted_token(after_space)?;
        if !b_decoded.starts_with(b"b/") {
            return None;
        }
        return Some(bytes_to_path(&b_decoded[2..]));
    }

    let len = bytes.len();
    if len < 5 + 2 {
        return None;
    }
    let inner = len.checked_sub(5)?;
    if !inner.is_multiple_of(2) {
        return None;
    }
    let p = inner / 2;
    if !bytes.starts_with(b"a/") {
        return None;
    }
    let a_side = &bytes[2..2 + p];
    let b_prefix_start = 2 + p;
    if bytes.get(b_prefix_start..b_prefix_start + 3) != Some(b" b/") {
        return None;
    }
    let b_side = &bytes[b_prefix_start + 3..];
    if a_side != b_side {
        return None;
    }
    Some(bytes_to_path(a_side))
}
