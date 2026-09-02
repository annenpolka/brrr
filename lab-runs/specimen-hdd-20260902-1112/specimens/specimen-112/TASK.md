# TASK

Composer's `vendor/composer/installed.json` can keep the identity of a package **as not abandoned** after `composer.lock` already records `"abandoned": true` (or a replacement name) for the same version. `composer audit` reads installed.json, so leftover omitted-abandoned identity makes audit report none.

On failing_ref `aa2a468cd2f9d75ff1c9103e2cbe2d03d982c4e8`, `Transaction::calculateOperations` decides whether a present package is an update with only version / dist-ref / source-ref:

```
if ($package->getVersion() !== $presentPackageMap[$package->getName()]->getVersion() ||
    $package->getDistReference() !== $presentPackageMap[$package->getName()]->getDistReference() ||
    $package->getSourceReference() !== $presentPackageMap[$package->getName()]->getSourceReference()
) {
    $operations[] = new Operation\UpdateOperation($source, $package);
}
```

Abandoned / replacement-package are not in that identity. Same version + same refs → no reinstall → installed.json leftover.

Public report (composer/composer#12417): `behat/transliterator` was installed before Packagist tagged it abandoned. Later `composer update` wrote `"abandoned": true` into `composer.lock`. `composer audit` still reported no abandoned package. `vendor/composer/installed.json` omitted `"abandoned"`. `rm -rf vendor && composer install` wrote abandoned into installed.json and audit failed as expected.

In-tree after the repair (not on failing_ref): `tests/Composer/Test/Fixtures/installer/install-forces-reinstall-if-abandon-changes.test`. INSTALLED has `"abandoned": "old-replacement"`, LOCK has `"abandoned": "replacement"`, same `1.0.0`. Expect `Upgrading a/a (1.0.0 => 1.0.0)` and installed.json replacement.

Case A — fresh `composer install` with lock already abandoned, empty vendor:
  installed.json written with abandoned
  no leftover omitted-abandoned identity

Case B — leftover vendor from before the abandon tag; lock now has abandoned; same version:
  leftover: installed.json omitted abandoned
  lock has abandoned
  audit reports none

Case C — `rm -rf vendor && composer install`:
  fresh identity
  not leftover sweep

Case D — version bump that is already an UpdateOperation:
  reinstall happens for version identity
  not this leftover (same-version omit)

The developer wants to know which identity case B actually left in `vendor/composer/installed.json`: leftover omitted-abandoned (lock has abandoned, installed does not), abandoned present, or omitted (no installed.json).
