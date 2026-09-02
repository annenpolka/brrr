KNOWN FIX (sealed): dart-lang/pub PR 4863 squash 0382a52acba89ff0080d559bb22f4017962bbd1d.

failing_ref is parent 425174668513d0696a637e62c683ec5885999914.

isPackagePathsMappingUpToDateWithLockfile omitted missing workspace packages, so leftover package_config without a newly added member was treated as current. isLockFileUpToDate checked only root.immediateDependencies.

PR repair: require every transitiveWorkspace name in packagePathsMapping; check immediateDependencies for every workspace package; construct Entrypoint from workspace root.

Do not show this to Dreamers, initial Red Pen, initial Grounders, or first-selection judges.
