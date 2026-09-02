# OBSERVED

Public dart-lang/sdk#61950 (closed 2026-09-01). dart-lang/pub PR 4863 squash `0382a52acba89ff0080d559bb22f4017962bbd1d` (parent `425174668513d0696a637e62c683ec5885999914`). Local pub was not performed on this lab host.

Issue body: `dart run` from a subdirectory with an outdated lock fails looking for pubspec.yaml in the subdirectory. PR also adds workspace-member invalidation: leftover package_config after adding a workspace package, leftover lock after a member pubspec change.

On failing_ref, `isPackagePathsMappingUpToDateWithLockfile` checks extra mappings and lockfile packages only. Missing `workspaceRoot.transitiveWorkspace` names are **not** required. `isLockFileUpToDate` uses `root.immediateDependencies` only. Those checks are **not** on the failing revision. They are added by PR 4863.

Not this packet: specimen-103 go work leftover replace graph. specimen-121 swift registry metadata TTL inverted. specimen-126 npm leftover original across file: Link. specimen-125 uv leftover extras marker simplified to true.

This packet does not include a local clone. Do not execute untrusted checkouts on the host.
