# TASK

`go mod download` in a module that has no `go.sum` writes checksum lines for `go.mod` files needed by MVS, and does not write checksum lines for the zip content of modules in the build list.

Two identities for `rsc.io/quote v1.5.2`:

```
rsc.io/quote v1.5.2/go.mod h1:…   # go.mod-only
rsc.io/quote v1.5.2 h1:…          # zip content
```

Case A — after `go mod download` with empty `go.sum` (Go 1.15.2 / 1.14.9 / 03a6860):

```
grep '^rsc.io/quote v1.5.2 ' go.sum
```

prints only the `/go.mod` line (or prints nothing for the unsuffixed zip line).

Case B — after `go mod tidy` (or Go 1.16+ `go mod download` that also records zip sums):

```
grep '^rsc.io/quote v1.5.2' go.sum
```

contains both the unsuffixed zip line and the `/go.mod` line.

The checksum database is not consulted for module versions already listed in `go.sum`. A `go.sum` that only has the `/go.mod` identity will not fetch the zip identity from sumdb on a later `go list`.

The developer wants to know which identity `go.sum` actually contained after download: zip content sum, go.mod-only sum, both, or neither.
