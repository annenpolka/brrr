KNOWN FIX (sealed): hashicorp/terraform PR 37396 squash 28cb1307393a2a6a0d1600955e17cd585e1aa7b8.

failing_ref is squash parent dcb0486c44ea05f1b5661d8b4fb6d0dd258880a3.

Mark-only update copied previous state and set only Value, omitting Identity. Destroy/apply error with non-null newVal built a new object without Identity even when the provider returned NewIdentity.

PR repair: mark-only path sets Identity: change.AfterIdentity. Error non-null path sets Identity: resp.NewIdentity. testDiffFn copies PriorIdentity to PlannedIdentity.

Do not show this to Dreamers, initial Red Pen, initial Grounders, or first-selection judges.
