// Reduced excerpt of runSync on failing_ref
// src/cmd/go/internal/workcmd/sync.go
// a2214422293d2c26ad389050f25460b3f2f00825
// Workspace versions are mustSelect. EnterModule drops other modules' replaces.
// EditBuildList error continue leaves leftover go.mod.

		changed, err := modload.EditBuildList(moduleLoader, ctx, nil, mustSelectFor[m])
		if err != nil {
			continue
		}
		if changed {
			modload.LoadPackages(moduleLoader, ctx, modload.PackageOpts{
				Tags:                     imports.AnyTags(),
				Tidy:                     true,
				VendorModulesInGOROOTSrc: true,
				ResolveMissingImports:    false,
				LoadTests:                true,
				AllowErrors:              true,
				SilenceMissingStdImports: true,
				SilencePackageErrors:     true,
			}, "all")
			modload.WriteGoMod(moduleLoader, ctx, modload.WriteOpts{})
		}
