# COMMANDS

```
# not executed on this lab host (golang/go#41341 report)
# go version go1.15.2 / 1.14.9 / 03a686069191e3515c7f27f6d90b66d272e0e3a2
# GOSUMDB=off

# case A
rm -f go.sum
go mod download
grep '^rsc.io/quote v1.5.2 ' go.sum
# only rsc.io/quote v1.5.2/go.mod h1:…

# case B
go mod tidy
grep '^rsc.io/quote v1.5.2' go.sum
# rsc.io/quote v1.5.2 h1:…
# rsc.io/quote v1.5.2/go.mod h1:…
```

Owned fixtures in `files/` are the two identities, not a go toolchain run.
