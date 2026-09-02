// Reduced excerpt of PnpInstaller.unplugPackage on failing_ref
// packages/plugin-pnp/sources/PnpLinker.ts
// 5b8c0e209cc9e0fbb27d89d9ce44855cceca9e87
// After rm -rf .yarn/unplugged, .ready is missing so the zip is recopied.
// storedBuildState is not cleared.

  private async unplugPackage(locator: Locator, fetchResult: FetchResult) {
    const unplugPath = pnpUtils.getUnpluggedPath(locator, {configuration: this.opts.project.configuration});
    this.unpluggedPaths.add(unplugPath);

    const readyFile = ppath.join(unplugPath, fetchResult.prefixPath, `.ready` as Filename);
    if (await xfs.existsPromise(readyFile))
      return new CwdFS(unplugPath);

    await xfs.mkdirPromise(unplugPath, {recursive: true});
    await xfs.copyPromise(unplugPath, PortablePath.dot, {baseFs: fetchResult.packageFs, overwrite: false});

    await xfs.writeFilePromise(readyFile, ``);

    return new CwdFS(unplugPath);
  }
