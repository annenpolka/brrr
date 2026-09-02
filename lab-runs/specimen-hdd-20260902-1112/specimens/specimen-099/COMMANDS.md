```
# not executed on this lab host
# failing_ref e91b2baa632c0c7e84216c91ecfe107c37d887c1
# src/cargo/sources/git/utils.rs GitCheckout::update_submodule
# src/cargo/sources/git/source.rs GitSource::update (parent uses git/db)

# public shape (#7987): git dep with submodule; second fetch of same submodule
# after rm git/checkouts, --offline cannot use a submodule db
```

Source-backed only. Do not execute untrusted checkouts on the host.
