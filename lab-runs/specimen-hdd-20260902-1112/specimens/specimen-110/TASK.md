# TASK

Composer's on-disk **installed identity** (`vendor/composer/installed.json`) can keep a leftover **abandoned-state** after `composer.lock` has already recorded that the same version is abandoned.

Public report (composer/composer#12417). `behat/transliterator` v1.5.0 was installed before Packagist tagged it abandoned. Later `composer update` wrote `"abandoned": true` into `composer.lock`. `composer audit` still reported no abandoned packages. Removing `vendor/` and reinstalling made audit fail as expected.

On failing_ref `8fc94c5e9972d2ebb87e57711a8477392b30f299`, `Transaction::calculateOperations` decides whether an already-present package needs an `UpdateOperation` with:

```
if ($package->getVersion() !== $presentPackageMap[$package->getName()]->getVersion() ||
    $package->getDistReference() !== $presentPackageMap[$package->getName()]->getDistReference() ||
    $package->getSourceReference() !== $presentPackageMap[$package->getName()]->getSourceReference()
) {
    $operations[] = new Operation\UpdateOperation($source, $package);
}
```

`installed.json` is the present-package map. Abandoned / replacement are not in that comparison. Same version + same refs: no reinstall, leftover installed identity.

In-tree after the repair (not on failing_ref): fixture `install-forces-reinstall-if-abandon-changes.test`. INSTALLED has `"abandoned": "old-replacement"`; LOCK has `"abandoned": "replacement"`; `composer install` expects `Upgrading a/a (1.0.0 => 1.0.0)` and INSTALLED abandoned becomes `"replacement"`.

Case A — first `composer install` of a package already abandoned on the repository:
  installed.json written from lock
  abandoned identity present
  no leftover

Case B — package already in vendor at the same version; lock later has `"abandoned": true` (or a new replacement string); `composer install` / `composer update` with no version change:
  leftover: installed.json omits abandoned (or keeps the old replacement)
  lock has the new abandoned identity
  `composer audit` reads installed.json and reports none

Case C — `rm -rf vendor && composer install`:
  installed.json rebuilt from lock
  not leftover identity (wipe, not same-version skip)

Case D — version actually changes (1.0.0 => 1.0.1):
  UpdateOperation from version compare
  not this leftover

The developer wants to know which identity case B actually left in `vendor/composer/installed.json`: leftover non-abandoned (or stale replacement) while lock is abandoned, both abandoned in sync, or omitted (no installed.json).
