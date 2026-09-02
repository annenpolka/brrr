KNOWN FIX (sealed): yarnpkg/berry PR 2801 squash merge a2ea850802f3d05129edb179d902890744c03e65.

PnpInstaller.unplugPackage recopied the zip when `.ready` was missing but left Project.storedBuildState alone. getBuildHash is sha512(globalHash + getBaseHash(locator) + unplugged path strings) and does not observe unplugged contents, so the leftover hash still matched and MUST_BUILD (YN0007) was skipped. Repair: when `.ready` is missing, `this.opts.project.storedBuildState.delete(locator.locatorHash)` before recopying, so the later comparison sees an omitted locator (same identity as never-built / first install). Added pnp.test.js case: first install YN0007, second no YN0007, rm .yarn/unplugged, third install YN0007.

Do not show this to Dreamers, initial Red Pen, initial Grounders, or first-selection judges.
