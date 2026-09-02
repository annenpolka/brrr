repository: yarnpkg/berry
issue: https://github.com/yarnpkg/berry/issues/2452
pr: https://github.com/yarnpkg/berry/pull/2801
failing_ref (PR base / merge parent): 5b8c0e209cc9e0fbb27d89d9ce44855cceca9e87
fixed_ref (squash merge commit): a2ea850802f3d05129edb179d902890744c03e65
head_sha: 0d6f061e93e6978606b83c96545a1dd1eee97521
merged_at: 2021-04-24T18:35:42Z
merged_by: arcanis
changed_files: packages/plugin-pnp/sources/PnpLinker.ts, packages/acceptance-tests/pkg-tests-specs/sources/pnp.test.js, CHANGELOG.md
pr_title: fix(plugin-pnp): delete stale build state when unplugged folder is missing
scout_note: not specimen-082/peerleft (bun.lock leftover packages vs optionalPeers mention after bun remove). not #1490 leftover dependenciesMeta.unplugged after yarn remove (open, no fixed_ref). not specimen-087 leftover pnpm path field. Distinct leftover: storedBuildState buildHash after .yarn/unplugged is removed vs never-built YN0007; PnP packageLocation still names the unplugged path. getBuildHash hashes path strings, not unplugged contents. yarn remove of the package already rebuilds storedBuildState from remaining buildablePackages.
