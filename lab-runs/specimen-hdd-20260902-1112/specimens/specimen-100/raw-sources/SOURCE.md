repository: oven-sh/bun
issue: https://github.com/oven-sh/bun/issues/21852
pr: https://github.com/oven-sh/bun/pull/36304
failing_ref (squash first parent): b4ee407a256ac2e4f4f3a5419387b43815cf6be7
fixed_ref (squash merge): 079d1d345fd1e9fc54b4e0bd36a0ce57fdcf0a48
pr_head: 75bcb995cb3a62ee2da0cdd5e0a55fe5442a3427
merged_at: 2026-07-29T11:32:43Z
merged_by: Jarred-Sumner
pr_author: robobun
changed_files: src/install/PackageManager.rs, src/install/PackageManager/PackageJSONEditor.rs, src/install/PackageManager/updatePackageJSONAndInstall.rs, test/cli/install/catalogs.test.ts, test/harness.ts
pr_title: install: update catalog definitions on non-interactive bun update
related_issue: https://github.com/oven-sh/bun/issues/23739
scout_note: not specimen-082 optional-peer lockfile leftover. Distinct leftover: catalog: protocol identity rewritten to a caret range while the root catalog object kept the old version.
