KNOWN FIX (sealed): golang/go#41341, Go 1.16. `go mod download` should add zip sums for modules in the build list, not only go.mod sums needed by MVS. Pre-1.16 download left `rsc.io/quote v1.5.2/go.mod` without `rsc.io/quote v1.5.2`. Because sumdb is skipped for versions already in go.sum, a later go list would not fill the zip identity from the checksum database.

Do not show this to Dreamers, initial Red Pen, initial Grounders, or first-selection judges.
