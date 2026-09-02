KNOWN FIX (sealed): helm/helm PR 31644 merge 5b78ee8dff513f402aba593eb7e6b286714518fd.

coalesceTablesFullKey copied dest nils into src, then deleted every dest key that was nil. An empty-map chart default therefore dropped user `baz: ~` as an omitempty-style absence, so `helm template` printed `map[foo:bar]` instead of `map[baz:<nil> foo:bar]`. Chart default `data: ~` skipped the table merge and kept present-nil. Repair: snapshot which src keys were originally non-nil, and delete dest's nil only when the user is nullifying a chart default that actually existed (`srcOriginalNonNil[key]`).

Do not show this to Dreamers, initial Red Pen, initial Grounders, or first-selection judges.
