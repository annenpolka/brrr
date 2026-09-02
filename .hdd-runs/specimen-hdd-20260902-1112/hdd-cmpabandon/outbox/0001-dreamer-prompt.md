# In-World Operating Policy

You are currently inside a real, already-running tool or computing environment.

Do not step outside the situation to propose a new product, methodology, or speculative design. Do not describe how such a tool could be built unless the environment itself exposes implementation details during use.

Operate what is present.

- Use the tool or environment on concrete tasks.
- Discover capabilities by trying them, inspecting responses, encountering failures, and adapting.
- Treat newly supplied limits and corrections as facts that have become known inside the environment.
- Continue from prior observations instead of resetting the world whenever something becomes inconvenient.
- If a previous assumption conflicts with a newly confirmed fact, investigate the conflict through use. Do not silently rewrite prior observations.
- Prefer concrete commands, interactions, outputs, errors, retries, and state changes over feature lists or feasibility essays.
- Do not rename familiar primitives merely to appear novel. If an existing interaction is insufficient, let a different abstraction emerge through use.
- Do not invoke unknown physics, quantum effects, hidden intelligence, magical semantic understanding, or unverifiable infrastructure merely to escape a constraint unless such a capability has actually been observed in the environment.
- When evidence is insufficient, report uncertainty from inside the situation rather than inventing certainty.

Do not discuss or infer any orchestration, editorial, evaluation, or prompt-engineering process behind the task. Those are outside the environment you are operating.

Your response should read like a field report produced by someone actually using the current tool or environment, not like a workshop or design-review transcript.


        ---

        # Current situation

CURRENT SITUATION
A real checkout or reduced fixture exists. The following material is what is known.

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

# OBSERVED

Public composer/composer#12417 (closed 2025-09-18). PR 12423 squash `1a22bb197a6e62ca431928627ef232bd4d335097` (parent `8fc94c5e9972d2ebb87e57711a8477392b30f299`). Local composer was not performed on this lab host.

Issue body: lock gained `"abandoned": true` for `behat/transliterator` v1.5.0 after Packagist marked it abandoned with no new version. `composer audit` still printed "No security vulnerability advisories found" and did not list the abandoned package. After deleting `vendor/` and reinstalling, audit listed the abandoned package. Diff of the two trees: leftover installed.json omitted `"abandoned": true` while lock had it.

On failing_ref, `Transaction::calculateOperations` compares version / dist reference / source reference only. Abandoned and replacement are not part of that present-vs-result identity. `composer audit` reads `vendor/composer/installed.json`.

Abandoned/replacement in the UpdateOperation predicate is **not** on the failing revision. It is added by PR 12423.

Not this packet: specimen-021 (poetry extras-reuse / lockfile-package). specimen-074 (rubygems platform-fallback-extra / frozen-lockfile-identity). specimen-080 (derived extra-ignores-marker). specimen-098 (pip leftover-base-without-extra).

This packet does not include a local clone. Do not execute untrusted checkouts on the host.

```
# not executed on this lab host
# failing_ref 8fc94c5e9972d2ebb87e57711a8477392b30f299
# src/Composer/DependencyResolver/Transaction.php calculateOperations
# vendor/composer/installed.json vs composer.lock abandoned field

# public shape:
# lock: "abandoned": true  (same version)
# leftover installed.json: abandoned omitted
# composer audit: no abandoned package
```

Source-backed only. Do not execute untrusted checkouts on the host.

composer/composer
  src/Composer/DependencyResolver/Transaction.php
  tests/Composer/Test/Fixtures/installer/install-forces-reinstall-if-abandon-changes.test
  tests/Composer/Test/Fixtures/installer/update-syncs-outdated.test

RELEVANT MATERIAL

### leftover_identity_split.txt

Registry / fixture:
  package a/a 1.0.0 already in vendor/composer/installed.json
  composer.lock later has abandoned / replacement changed
  same version, same dist/source refs

Case A (first install, already abandoned on repo):
  installed.json written with abandoned
  no leftover

Case B (same-version install/update after abandoned changes):
  leftover: installed.json omits abandoned (or keeps old replacement)
  lock has new abandoned identity
  composer audit reads installed.json

Case C (rm -rf vendor && composer install):
  installed.json rebuilt from lock
  not leftover skip

Case D (version 1.0.0 => 1.0.1):
  UpdateOperation from version compare
  not this leftover

Not this packet:
  poetry extras-reuse / lockfile-package (specimen-021)
  rubygems platform-fallback-extra (specimen-074)
  derived extra-ignores-marker (specimen-080)
  pip leftover-base-without-extra (specimen-098)

### transaction_update_failing.php

# Reduced excerpt of Transaction::calculateOperations on failing_ref
# src/Composer/DependencyResolver/Transaction.php
# 8fc94c5e9972d2ebb87e57711a8477392b30f299
# Present-package identity is version + dist ref + source ref.
# Abandoned / replacement are not part of that identity.

                    if (isset($presentPackageMap[$package->getName()])) {
                        $source = $presentPackageMap[$package->getName()];

                        // do we need to update?
                        // TODO different for lock?
                        if ($package->getVersion() !== $presentPackageMap[$package->getName()]->getVersion() ||
                            $package->getDistReference() !== $presentPackageMap[$package->getName()]->getDistReference() ||
                            $package->getSourceReference() !== $presentPackageMap[$package->getName()]->getSourceReference()
                        ) {
                            $operations[] = new Operation\UpdateOperation($source, $package);
                        }
                        unset($removeMap[$package->getName()]);
                    } else {
                        $operations[] = new Operation\InstallOperation($package);
                        unset($removeMap[$package->getName()]);
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


        # What to do now

        Continue operating the same tool or environment from its current state.
        Treat the limits and corrections above as facts that have just become known inside
        the world, not as review comments. Investigate their consequences through concrete
        use. Prefer commands, observations, failures, retries, and changed behavior over a
        design essay.
