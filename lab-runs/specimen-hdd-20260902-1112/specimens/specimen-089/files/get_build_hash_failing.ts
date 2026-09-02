// Reduced excerpt of getBuildHash on failing_ref
// packages/yarnpkg-core/sources/Project.ts
// Hashes locator identity plus buildLocation path strings, not unplugged contents.
// Comment on the reconstruction: remove state from packages that got removed
// (locators that left buildablePackages). Case C keeps the locator in the tree.

    const getBuildHash = (locator: Locator, buildLocations: Array<PortablePath>) => {
      const builder = createHash(`sha512`);

      builder.update(globalHash);
      builder.update(getBaseHash(locator));

      for (const location of buildLocations)
        builder.update(location);

      return builder.digest(`hex`);
    };

    // We reconstruct the build state from an empty object because we want to
    // remove the state from packages that got removed
    const nextBState = new Map<LocatorHash, string>();
