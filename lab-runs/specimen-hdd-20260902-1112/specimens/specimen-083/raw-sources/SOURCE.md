repository: golang/go (derived fixture)
issue: https://github.com/golang/go/issues/41341
failing_world: Go 1.15.2 / 1.14.9 / 03a686069191e3515c7f27f6d90b66d272e0e3a2
fixed_world: Go 1.16 go mod download records zip sums of build-list modules
scout_note: not specimen-078 / hdd-gocache (testcache omits buildid). Distinct: go.sum zip-content identity vs go.mod-only identity after download.
