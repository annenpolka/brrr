# Current situation

CURRENT SITUATION
A real checkout or reduced fixture exists. The following material is what is known.

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

local-fixture
  files/go.sum.download
  files/go.sum.tidy

RELEVANT MATERIAL

### go.sum.download

rsc.io/quote v1.5.2/go.mod h1:fixture-quote-mod-only=
rsc.io/sampler v1.3.0/go.mod h1:fixture-sampler-mod-only=
golang.org/x/text v0.0.0-20170915032832-14c0d48ead0c/go.mod h1:fixture-text-mod-only=

### go.sum.tidy

golang.org/x/text v0.0.0-20170915032832-14c0d48ead0c h1:fixture-text-zip=
golang.org/x/text v0.0.0-20170915032832-14c0d48ead0c/go.mod h1:fixture-text-mod-only=
rsc.io/quote v1.5.2 h1:fixture-quote-zip=
rsc.io/quote v1.5.2/go.mod h1:fixture-quote-mod-only=
rsc.io/sampler v1.3.0 h1:fixture-sampler-zip=
rsc.io/sampler v1.3.0/go.mod h1:fixture-sampler-mod-only=

KNOWN FACTS
Only the observations above are established. Do not assume a root cause.

UNKNOWN
What relation, provenance, or question would make this failure smaller to investigate?

OPERATOR REQUEST
An unfamiliar developer CLI is already installed in this environment.
It is not a thin wrapper around a familiar Unix tool.
Use it on the problem below. Operate what is present rather than proposing a product.
Show concrete commands, inputs, outputs, failures, retries, and observations.
Do not invent repository facts that contradict the supplied material.
