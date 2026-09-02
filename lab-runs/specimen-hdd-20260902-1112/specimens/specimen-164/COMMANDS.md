```
# not executed on this lab host
# failing_ref 8100bd18a42c29740e2d30d21b5f68be67f27d1b
# lib/zeitwerk/loader.rb autoload_path_set_by_me_for?
# lib/zeitwerk/registry.rb inception?

# public shape:
# leftover gem inception of MyGem after app added MyGem::Foo
# Registry.inception?(cpath) drops which loader registered it
# reload of app-added same-name constants fails
```

Source-backed only. Do not execute untrusted checkouts on the host.
