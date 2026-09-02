CURRENT SITUATION
A real checkout or reduced fixture exists. The following material is what is known.

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

# OBSERVED

Public composer/composer#12417 (closed 2025-09-18). PR 12423 squash `1a22bb197a6e62ca431928627ef232bd4d335097` (parent `aa2a468cd2f9d75ff1c9103e2cbe2d03d982c4e8`). Local composer was not performed on this lab host.

Issue body: lock gained `"abandoned": true` after Packagist tagged the already-installed package. installed.json omitted abandoned. audit read installed.json and reported none. Wipe vendor + install healed it.

On failing_ref, calculateOperations compares version / dist-ref / source-ref only. Abandoned and replacement-package are not that identity. Same-version leftover vendor is not an UpdateOperation.

`isAbandoned()` / `getReplacementPackage()` on CompletePackageInterface are **not** on the failing revision's update predicate. They are added by PR 12423.

Not this packet: specimen-074 (rubygems platform-fallback extra). specimen-021 (poetry lock leftover). specimen-086 (cargo rustc-fingerprint metadata). emit_086 composer classmap leftover was not the claimed 086 packet (086 is cargo). job-0458 hunt was installed.json vs lock, not classmap.

This packet does not include a local clone. Do not execute untrusted checkouts on the host.

```
# not executed on this lab host
# failing_ref aa2a468cd2f9d75ff1c9103e2cbe2d03d982c4e8
# src/Composer/DependencyResolver/Transaction.php calculateOperations

# public shape:
# leftover vendor installed.json omitted abandoned
# composer.lock has abandoned
# composer audit reports none
```

Source-backed only. Do not execute untrusted checkouts on the host.

composer/composer
  src/Composer/DependencyResolver/Transaction.php
  tests/Composer/Test/Fixtures/installer/install-forces-reinstall-if-abandon-changes.test

RELEVANT MATERIAL

### leftover_identity_split.txt

Registry / fixture:
  leftover vendor/composer/installed.json
  composer.lock already has abandoned
  same version

Case A (fresh install, empty vendor):
  installed.json written with abandoned
  no leftover omitted-abandoned

Case B (leftover vendor from before abandon tag):
  leftover: installed.json omitted abandoned
  lock has abandoned
  audit reports none

Case C (rm -rf vendor && composer install):
  fresh identity
  not leftover sweep

Case D (version bump UpdateOperation):
  reinstall for version identity
  not this leftover

Not this packet:
  rubygems platform-fallback extra (specimen-074)
  poetry lock leftover (specimen-021)
  cargo rustc-fingerprint metadata (specimen-086)

### transaction_update_predicate_failing.php

# Reduced excerpt of Transaction::calculateOperations on failing_ref
# src/Composer/DependencyResolver/Transaction.php
# aa2a468cd2f9d75ff1c9103e2cbe2d03d982c4e8
# Version / dist-ref / source-ref are the installed identity.
# Abandoned / replacement-package are not that identity.

                        if ($package->getVersion() !== $presentPackageMap[$package->getName()]->getVersion() ||
                            $package->getDistReference() !== $presentPackageMap[$package->getName()]->getDistReference() ||
                            $package->getSourceReference() !== $presentPackageMap[$package->getName()]->getSourceReference()
                        ) {
                            $operations[] = new Operation\UpdateOperation($source, $package);
                        }

KNOWN FACTS
Only the observations above are established. Do not assume a root cause.

UNKNOWN
What relation, provenance, or question would make this failure smaller to investigate?

OPERATOR REQUEST
An unfamiliar developer CLI is already installed in this environment.
It is not a thin wrapper around a familiar Unix tool.
Use it on the problem below. Operate what is present rather than proposing a product.
Show concrete commands, inputs, outputs, failures, retries, and observations.
Do not invent repository facts that contradict the supplied material.
