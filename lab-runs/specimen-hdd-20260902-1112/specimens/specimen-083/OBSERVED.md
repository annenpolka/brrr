# OBSERVED

Public golang/go#41341 (jayconrod, 2020-09-11). Failing world: Go 1.15.2, 1.14.9, and commit `03a686069191e3515c7f27f6d90b66d272e0e3a2`. `GOSUMDB=off` in the report; GOPROXY a local module proxy.

Command in a module whose `go.mod` is:

```
module m
go 1.16
require rsc.io/quote v1.5.2
```

with no `go.sum`:

```
go mod download
grep '^rsc.io/quote v1.5.2 ' go.sum
```

Expected: sums for both the `go.mod` files needed by MVS and the content of modules in the build list.

Saw: `go.sum` only contains sums for the `go.mod` files.

The unsuffixed `go.sum` line is the zip/dirhash of module source. The `version/go.mod` line is the hash of that module's go.mod only. `go mod tidy` adds or removes the zip line as needed. Pre-1.16 `go mod download` could leave a build-list module listed only as `/go.mod`.

This packet is an owned two-file fixture of those two `go.sum` identities. It does not include a local Go checkout. Do not execute untrusted checkouts on the host.
