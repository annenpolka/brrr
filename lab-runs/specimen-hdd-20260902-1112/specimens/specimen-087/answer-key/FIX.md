KNOWN FIX (sealed): pnpm/pnpm PR 10911 commit fabf694a81b55f3a572c5a511d8f0651dcb495c8.

223b9b2 changed lockfile patchedDependencies from Record<string,{path,hash}> to Record<string,string> and stopped writing path, but convertToLockfileObject still spread rest.patchedDependencies unchanged. Reading a pre-change lockfile left leftover {path,hash} objects in LockfileObject; groupPatchedDependencies then stored that object as PatchInfo.hash; getOutdatedLockfileSetting ramda.equals compared leftover objects to current hash strings. Repair: convertToLockfileObject calls migratePatchedDependencies, which maps each value to the string itself or value.hash.

Do not show this to Dreamers, initial Red Pen, initial Grounders, or first-selection judges.
