# TASK

Incremental compile with `-Znext-solver`. Same crate, two revisions, same incremental directory.

Revision cfail1:

```rust
pub trait Future {
    type Error;
    fn poll() -> Self::Error;
}

struct S;
impl Future for S {
    type Error = Error;
    fn poll() -> Self::Error { todo!() }
}

pub struct Error(());
```

Revision cfail2 changes only the struct shape:

```rust
pub struct Error();
```

`fn poll` still returns `Self::Error`, which normalizes to `Error`. The field of `Error` is gone.

The second session ICEs while decoding a DefId that no longer exists. The typeck query for `fn poll` was not marked red.

The developer wants to know which query identity the second session treated as still green, and which first-run dependency that identity did not record.
