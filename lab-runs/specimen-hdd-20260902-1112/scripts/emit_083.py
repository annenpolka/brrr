#!/usr/bin/env python3
"""Emit sealed DERIVED_VERIFIED packet specimen-083 (go.sum zip vs go.mod-only).

Derived from golang/go#41341. Not specimen-078 / hdd-gocache (testcache omits
buildid). Packet already on disk; this script refuses to overwrite.
"""
from __future__ import annotations

from emit_specimen import emit
from compile_seed import write_seed
from paths import SPECIMENS
from update_index import main as update_index

SPEC_ID = "specimen-083"


packet = dict(
    id=SPEC_ID,
    manifest="""
id: specimen-083
kind: DERIVED_VERIFIED
repository: local-fixture
failing_ref: fixture-gosum-mod-only
fixed_ref: fixture-gosum-zip-and-mod
source_issue: https://github.com/golang/go/issues/41341
source_pr: none
mechanism_tags:
  - gosum-zip-hash
  - gosum-mod-only
  - download-omits-content-sum
ecosystem: go
reproduction_status: verified
safety_status: owned-fixture
packet_tokens_estimate: 1800
answer_key_sealed: true
parent_specimens: []
mutations: []
""",
    task="""# TASK

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
""",
    observed="""# OBSERVED

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
""",
    commands="""# COMMANDS

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
""",
    tree="""local-fixture
  files/go.sum.download
  files/go.sum.tidy
""",
    source="""repository: golang/go (derived fixture)
issue: https://github.com/golang/go/issues/41341
failing_world: Go 1.15.2 / 1.14.9 / 03a686069191e3515c7f27f6d90b66d272e0e3a2
fixed_world: Go 1.16 go mod download records zip sums of build-list modules
scout_note: not specimen-078 / hdd-gocache (testcache omits buildid). Distinct: go.sum zip-content identity vs go.mod-only identity after download.
""",
    answer_key="""KNOWN FIX (sealed): golang/go#41341, Go 1.16. `go mod download` should add zip sums for modules in the build list, not only go.mod sums needed by MVS. Pre-1.16 download left `rsc.io/quote v1.5.2/go.mod` without `rsc.io/quote v1.5.2`. Because sumdb is skipped for versions already in go.sum, a later go list would not fill the zip identity from the checksum database.

Do not show this to Dreamers, initial Red Pen, initial Grounders, or first-selection judges.
""",
    curation="""ACCEPT_R1

contrastiveness: high (go.mod-only sum vs zip+mod sums; download vs tidy; sumdb skipped for versions already listed)
reproducibility: derived from public issue + owned two-file fixture; local go run not claimed
information density: high
safety: owned-fixture
nontriviality: two go.sum identities for one module version; substring grep on the module path hits both
""",
    files={
        "go.sum.download": """rsc.io/quote v1.5.2/go.mod h1:fixture-quote-mod-only=
rsc.io/sampler v1.3.0/go.mod h1:fixture-sampler-mod-only=
golang.org/x/text v0.0.0-20170915032832-14c0d48ead0c/go.mod h1:fixture-text-mod-only=
""",
        "go.sum.tidy": """golang.org/x/text v0.0.0-20170915032832-14c0d48ead0c h1:fixture-text-zip=
golang.org/x/text v0.0.0-20170915032832-14c0d48ead0c/go.mod h1:fixture-text-mod-only=
rsc.io/quote v1.5.2 h1:fixture-quote-zip=
rsc.io/quote v1.5.2/go.mod h1:fixture-quote-mod-only=
rsc.io/sampler v1.3.0 h1:fixture-sampler-zip=
rsc.io/sampler v1.3.0/go.mod h1:fixture-sampler-mod-only=
""",
    },
)


if __name__ == "__main__":
    dest = SPECIMENS / SPEC_ID
    if dest.exists():
        raise SystemExit(f"{dest} already exists; refusing to overwrite")
    path = emit(packet)
    seed = write_seed(SPECIMENS / SPEC_ID)
    print(path)
    print(seed)
    update_index()
