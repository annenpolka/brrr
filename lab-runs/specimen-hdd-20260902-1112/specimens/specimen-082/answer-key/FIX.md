KNOWN FIX (sealed): oven-sh/bun PR 35681 squash merge bbe3f6a2629adf808adbd0da199ae8c94a3c0d47.

Package::clone copied every resolution slot, including optional-peer slots hoist had filled, so a package that had once satisfied an optional peer stayed reachable through clean_with_logger after the only non-peer edge was removed. Fresh resolve never populated those slots independently (enqueue_dependency_with_main_and_success_fn returns Ok(()) for is_optional_peer). Repair: in Package::clone, write invalid_package_id to an optional-peer resolution slot instead of mapping/enqueuing the old target; Cloner::flush re-runs resolve()/hoist(), which re-binds the slot only when some non-optional-peer edge still keeps the target alive. Added bun-lock.test.ts cases expect bun.lock after remove to be byte-identical to the never-installed state.

Do not show this to Dreamers, initial Red Pen, initial Grounders, or first-selection judges.
