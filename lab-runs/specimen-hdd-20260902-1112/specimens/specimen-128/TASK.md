# TASK

dart pub can keep the identity of a **previous `.dart_tool/package_config.json`** after a workspace membership change should have been a different mapping. `isPackagePathsMappingUpToDateWithLockfile` only rejects extra mappings. Missing workspace packages are omitted, so leftover package_config without the new member is treated as up-to-date.

On failing_ref `425174668513d0696a637e62c683ec5885999914`, `isLockFileUpToDate` checks only `root.immediateDependencies`. A workspace member's pubspec change is omitted. Workspace packages are never listed in `pubspec.lock` `packages`, and the mapping check never requires every `workspaceRoot.transitiveWorkspace` name.

Public report (dart-lang/sdk#61950 / dart-lang/pub#4863). Workspace:

```
# pubspec.yaml
name: myapp
workspace: [sub]

# sub/pubspec.yaml
name: sub
resolution: workspace
```

After `dart run sub:tool`, add workspace member `pkg_b` without `pub get`. On failing_ref the leftover package_config (no `pkg_b`) is still treated as current. Same PR: `isLockFileUpToDate` does not see a new dependency on member `sub`.

In-tree after the repair (not on failing_ref): require every workspace package in `packagePathsMapping`; check `immediateDependencies` for every `transitiveWorkspace` package; tests `Invalidates resolution when new package added to workspace` and `Invalidates resolution when workspace member dependency is modified`.

Case A — second `dart run sub:tool` with unchanged workspace:
  package_config is the current mapping
  not leftover-after-workspace-add

Case B — add workspace member `pkg_b` without `pub get`, leftover package_config:
  leftover: package_config without pkg_b
  missing workspace member omitted from identity
  treated as up-to-date on failing_ref

Case C — delete `.dart_tool/package_config.json` + `pubspec.lock` then `pub get`:
  fresh mapping including pkg_b
  not leftover missing member

Case D — missing workspace member invalidates (post-repair shape, not on failing_ref):
  package_config is not leftover without pkg_b
  resolution runs again

The developer wants to know which identity case B actually used for `.dart_tool/package_config.json` after adding `pkg_b`: leftover mapping without pkg_b (treated as current), current mapping including pkg_b, or omitted (no package_config).
