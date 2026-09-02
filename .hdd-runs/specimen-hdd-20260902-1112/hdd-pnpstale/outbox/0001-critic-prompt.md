# Red Pen Policy

The Red Pen is meta-aware. Unlike the Dreamer, it may see the full HDD ledger, raw Dreamer output, method goals, prior rejections, and stop conditions.

Its job is not to write the replacement design. Its job is to preserve the interesting departure while applying pressure.

## Review order

1. Identify what should survive.
2. Find contradictions and continuity violations.
3. Find magic or missing information sources.
4. Find provenance confusion.
5. Find unsupported precision.
6. Find boring collapse into a familiar system with renamed nouns.
7. If a central interaction is becoming identifiable, run the Reality-Stripped Affordance Test.
8. Classify the surviving affordance.
9. Decide whether another Dreamer turn could materially change that classification.
10. Produce pressure or recommend stopping or grounding.

Pressure should normally be expressible later as an in-world fact or constraint. Avoid pressures that require the Dreamer to understand the HDD process itself.

Good pressure:

- "This environment has no path-based identity. Continue using it under that fact."
- "The claimed timestamp cannot be observed after an offline partition. Show only what the environment can actually observe."
- "The tool has no AST model or hidden classifier. Use the existing interaction anyway."

Bad pressure:

- "Improve novelty score."
- "Preserve the Harvest Candidate."
- "Respond to Red Pen 0003."

## Reality-Stripped Affordance Test

Once a central interaction is becoming identifiable, temporarily remove the artifact-specific name, fictional implementation, lore, magic, and convenience guarantees. Then ask:

1. What can the user actually do in one operation?
2. What is the nearest existing ordinary workflow?
3. What observable capability would be lost if that workflow replaced the artifact?
4. Does the remaining novelty live in the operation itself, or only in syntax, metaphor, metadata, or convenience?

Classify the survivor as exactly one of:

- `NOVEL_AFFORDANCE`: a new first-class question or operation remains after fictional machinery is removed. An existing workflow may approximate it, but cannot naturally express the same question or would lose an important observable capability.
- `USEFUL_COMPOSITION`: the primitives already exist, but binding them into one operation or contract has practical value. Do not claim a new foundational capability.
- `THIN_WRAPPER`: the result is behaviorally close to an ordinary workflow, and the demonstrated difference is mainly syntax, metaphor, metadata, or one-shot convenience.
- `NO_SURVIVOR`: the useful operation disappears when the fictional machinery or magic is removed.

Do not force an assessment in an early iteration whose central operation is still unclear. In that case, omit `affordance_assessment` or return it as `null`.

`THIN_WRAPPER` is not a failed HDD run. It may be the honest result that the exploration produced a conceptual insight but weak evidence for a distinct artifact. Likewise, neither `THIN_WRAPPER` nor `NO_SURVIVOR` is a request to invent more features. Continue Dreaming only when a specific, untested observable delta could materially change the classification. Translate that test into a concrete in-world fact or usage task, for example:

> Express the central operation without artifact-specific names, replace it with the nearest ordinary workflow, and show in an actual usage trace what observable behavior is lost.

Never send abstract pressure such as "make it more novel" or "invent something existing tools cannot do."

## External critic JSON contract

Return one JSON object and no surrounding Markdown fence.

```json
{
  "summary": "short diagnosis",
  "preserve_add": ["..."],
  "established_add": ["..."],
  "rejected_add": ["..."],
  "constraints_add": ["..."],
  "open_questions_add": ["..."],
  "harvest_candidates_add": ["..."],
  "affordance_assessment": {
    "classification": "NOVEL_AFFORDANCE",
    "core_operation": "ask why a runtime state has its observed value",
    "nearest_existing_operation": "manual debugger tracing and instrumentation",
    "observable_delta": "the runtime provenance question is exposed directly as one post-execution query",
    "reason": "the surviving interaction is not merely renamed tracing machinery"
  },
  "pressure": ["one to three pressures"],
  "redpen_markdown": "optional human-readable review"
}
```

All array fields may be empty. `pressure` is truncated to three items by the runner.

`affordance_assessment` is optional and may be omitted or `null` while the central interaction is immature. When present, it must be an object whose `classification` is one of `NOVEL_AFFORDANCE`, `USEFUL_COMPOSITION`, `THIN_WRAPPER`, or `NO_SURVIVOR`. `core_operation`, `nearest_existing_operation`, `observable_delta`, and `reason` must be non-empty strings. Do not return a classification without the concrete comparison that supports it.

## Stop signal

Recommend grounding or ending when:

- the same failure repeats;
- the Dreamer starts explaining why the task is difficult instead of using the artifact;
- the surviving interaction has become clear enough to harvest;
- the Reality-Stripped Affordance Test returns `THIN_WRAPPER` or `NO_SURVIVOR` and no specific untested observable delta remains; or
- further Dreaming is adding fictional capabilities instead of producing evidence that could change the classification.

This is a recommendation to the host or human, not a new automatic runner stop.


        ---

        # Seed

        CURRENT SITUATION
A real checkout or reduced fixture exists. The following material is what is known.

# TASK

Yarn PnP unplugs packages that have install scripts. After the unplugged tree is deleted, a later `yarn install` does not return the locator to the identity it had before that package was ever built.

Fixture `no-deps-scripted` (has an install script). Public report used `@sentry/cli@1.62.0` (install script downloads a native binary).

Case A — never built (first install, empty `storedBuildState`):

```
package.json: { "dependencies": { "no-deps-scripted": "*" } }
yarn install
```

On yarnpkg/berry `5b8c0e209cc9e0fbb27d89d9ce44855cceca9e87`, stdout contains `YN0007` (`MUST_BUILD`: "must be built because it never has been before or the last one failed"). PnP writes `packageLocation` under `.yarn/unplugged/no-deps-scripted-npm-…/`. `Project.storedBuildState` then maps that locatorHash to a sha512 `buildHash`. A `.ready` file appears inside the unplugged prefix.

Case B — second install, unplugged tree still present:

```
yarn install
```

stdout does **not** contain `YN0007`. `storedBuildState.get(locatorHash) === buildHash`, so scripts are skipped. PnP `packageLocation` is still the unplugged path.

Case C — remove the unplugged tree, then install again (package remains in `package.json`; this is not `yarn remove no-deps-scripted`):

```
rm -rf .yarn/unplugged
yarn install
```

`PnpInstaller.unplugPackage` sees no `.ready` file, recopies the zip into `.yarn/unplugged/…`, and writes `.ready` again. `getBuildHash` is sha512 of `globalHash + getBaseHash(locator) + buildLocation path strings`. Those path strings are the same unplugged paths as case A, so `buildHash` is unchanged. On the failing revision `storedBuildState` still holds that hash, so the skip in case B fires: no `YN0007`, install scripts do not run.

Public `@sentry/cli@1.62.0` observable after case C:

```
yarn sentry-cli --version
# Error: spawn /.yarn/unplugged/@sentry-cli-npm-1.62.0-…/node_modules/@sentry/cli/sentry-cli ENOENT
```

PnP `packageLocation` still names the unplugged directory (same as a successful first build). `storedBuildState` still names the locator as already-built. The native binary is absent.

Case D — never installed `no-deps-scripted` at all: no PnP registry entry for that ident, no `storedBuildState` row, no `.yarn/unplugged/no-deps-scripted-*` directory.

The developer wants to know which identity install-state + PnP actually contained for the locator after case C: leftover already-built `buildHash` (scripts skipped, same skip as case B), omitted (same `YN0007` as case A / never-built), or a new hash because the unplugged files were gone.

# OBSERVED

Public yarnpkg/berry#2452 (mzvonar, 2021-02-08) / PR 2801. Failing world: Yarn 2.4.0 and commit `5b8c0e209cc9e0fbb27d89d9ce44855cceca9e87`.

Issue reproduction:

```
yarn init
yarn set version berry
yarn add @sentry/cli@1.62.0
rm -rf .yarn/unplugged
yarn install
yarn sentry-cli --version
```

Expected after the second install: install scripts run again; `sentry-cli` binary exists under the unplugged prefix.

Saw: scripts skipped; `spawn …/sentry-cli ENOENT`. Collaborator note: "The info containing what has been built is located in `.yarn/build-state.yml` (for now)" — on this revision that map is `Project.storedBuildState` inside install-state (`INSTALL_STATE_FIELDS.restoreBuildState`). Workaround quoted in the issue: `rm -rf .yarn/unplugged .yarn/build-state.yml && yarn`, or `yarn rebuild`.

In-tree skip on the failing revision (`packages/yarnpkg-core/sources/Project.ts`):

```
const buildHash = getBuildHash(pkg, buildInfo.buildLocations);
if (this.storedBuildState.get(pkg.locatorHash) === buildHash) {
  nextBState.set(pkg.locatorHash, buildHash);
  continue;
}
if (this.storedBuildState.has(pkg.locatorHash))
  report.reportInfo(MessageName.MUST_REBUILD, `… must be rebuilt because its dependency tree changed`);
else
  report.reportInfo(MessageName.MUST_BUILD, `… must be built because it never has been before or the last one failed`);
```

`MUST_BUILD` is `MessageName` 7 → `YN0007`. `getBuildHash` updates sha512 with `globalHash`, `getBaseHash(locator)`, then each `buildLocations` **path string**. It does not hash unplugged file contents. Comment immediately above the rebuild loop: "We reconstruct the build state from an empty object because we want to remove the state from packages that got removed" — that prune is for locators that left `buildablePackages` (`yarn remove` of the package). Case C keeps the locator in the tree.

`PnpInstaller.unplugPackage` on the failing revision (`packages/plugin-pnp/sources/PnpLinker.ts`):

```
const readyFile = ppath.join(unplugPath, fetchResult.prefixPath, `.ready`);
if (await xfs.existsPromise(readyFile))
  return new CwdFS(unplugPath);
await xfs.mkdirPromise(unplugPath, {recursive: true});
await xfs.copyPromise(unplugPath, PortablePath.dot, {baseFs: fetchResult.packageFs, overwrite: false});
await xfs.writeFilePromise(readyFile, ``);
```

No `storedBuildState.delete`. After `rm -rf .yarn/unplugged`, `.ready` is gone so the zip is recopied, but the leftover hash still matches.

PR 2801 later added `pnp.test.js` "it should run the install scripts anew if the unplugged folder is removed" (`no-deps-scripted`): first install `YN0007`, second install no `YN0007`, `rm` unplugged, third install expects `YN0007`. That third assertion is the case-C identity. The test file on the failing revision does not yet contain that case.

Unused-unplugged **directories** for packages that left the tree are already deleted in `finalizeInstallWithPnp` (`unpluggedPaths` set). This packet is not that prune, not bun leftover `packages` vs `optionalPeers` mention, and not leftover `dependenciesMeta.unplugged` after `yarn remove` (#1490, still open).

This packet does not include a local clone. Do not execute untrusted checkouts on the host.

# COMMANDS

```
# in-tree on failing_ref 5b8c0e209cc9e0fbb27d89d9ce44855cceca9e87
# (not executed on this lab host)

# case A — never built
# package.json dependencies: no-deps-scripted: *
yarn install
# stdout contains YN0007 MUST_BUILD
# .pnp.cjs packageLocation under .yarn/unplugged/no-deps-scripted-npm-*/
# storedBuildState now has locatorHash → sha512 buildHash
# unplugged prefix contains .ready

# case B — leftover already-built, tree still present
yarn install
# stdout does not contain YN0007
# storedBuildState.get(locatorHash) === getBuildHash(pkg, buildLocations)

# case C — remove unplugged tree; package still in package.json
rm -rf .yarn/unplugged
yarn install
# unplugPackage recopies zip (no .ready)
# getBuildHash still hashes the same unplugged path strings
# leftover storedBuildState matches → no YN0007; scripts skipped

# public #2452
# yarn add @sentry/cli@1.62.0
# rm -rf .yarn/unplugged && yarn install
# yarn sentry-cli --version
# spawn …/.yarn/unplugged/@sentry-cli-npm-1.62.0-…/sentry-cli ENOENT

# case D — never installed
# no PnP registry ident, no storedBuildState row, no unplugged directory
```

Not executed on this lab host.

yarnpkg/berry
  packages/plugin-pnp/sources/PnpLinker.ts
  packages/yarnpkg-core/sources/Project.ts
  packages/yarnpkg-core/sources/MessageName.ts
  packages/acceptance-tests/pkg-tests-specs/sources/pnp.test.js

RELEVANT MATERIAL

### get_build_hash_failing.ts

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

### leftover_identity_split.txt

Registry / fixture:
  no-deps-scripted (in-tree PR 2801 test) — has install script
  @sentry/cli@1.62.0 (public #2452) — install script fetches sentry-cli binary

Case A (never built / first install):
  yarn install
  stdout contains YN0007 MUST_BUILD
  PnP packageLocation = .yarn/unplugged/<slug>/
  storedBuildState[locatorHash] = sha512(globalHash + baseHash + path strings)
  unplugged prefix contains .ready

Case B (second install, unplugged tree still on disk):
  yarn install
  no YN0007
  storedBuildState.get(locatorHash) === getBuildHash(...)

Case C (remove unplugged tree; package still a dependency):
  rm -rf .yarn/unplugged
  yarn install
  unplugPackage recopies zip (no .ready)
  getBuildHash unchanged (same path strings)
  leftover storedBuildState matches → no YN0007
  @sentry/cli: spawn …/sentry-cli ENOENT
  PnP packageLocation still names the unplugged directory

Case D (never installed):
  no PnP registry ident for the package
  no storedBuildState row
  no .yarn/unplugged/<slug>/ directory

Not this packet:
  bun.lock leftover packages vs optionalPeers mention after bun remove (specimen-082)
  leftover dependenciesMeta.unplugged after yarn remove (#1490, unfixed)
  finalizeInstallWithPnp deleting unused unplugged dirs for locators that left the tree

### skip_rebuild_failing.ts

// Reduced excerpt of the build-state skip on failing_ref
// packages/yarnpkg-core/sources/Project.ts
// 5b8c0e209cc9e0fbb27d89d9ce44855cceca9e87
// MUST_BUILD = MessageName 7 = YN0007.

        const buildHash = getBuildHash(pkg, buildInfo.buildLocations);

        // No need to rebuild the package if its hash didn't change
        if (this.storedBuildState.get(pkg.locatorHash) === buildHash) {
          nextBState.set(pkg.locatorHash, buildHash);
          continue;
        }

        if (this.storedBuildState.has(pkg.locatorHash))
          report.reportInfo(MessageName.MUST_REBUILD, `${structUtils.prettyLocator(this.configuration, pkg)} must be rebuilt because its dependency tree changed`);
        else
          report.reportInfo(MessageName.MUST_BUILD, `${structUtils.prettyLocator(this.configuration, pkg)} must be built because it never has been before or the last one failed`);

### unplug_package_failing.ts

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


        # Ledger Before This Iteration

        # HDD Ledger

Iteration: 0

## Preserve

- (none)

## Established

- (none)

## Rejected

- (none)

## Constraints

- (none)

## Open Questions

- (none)

## Human Pressure

- (none)

## Harvest Candidates

- (none)

## Affordance Assessment

(none)

## Latest Red Pen Pressure

- (none)

## Pending

(none)


        # Dreamer Output To Review

        ### Field Report: Investigating Yarn PnP Unplugged Package Identity After Removal  

**Operational Context**  
- Environment: Yarn Berry (commit `5b8c0e209cc9e0fbb27d89d9ce44855cceca9e87`)  
- Package under test: `@sentry/cli@1.62.0` (exhibits install script behavior)  
- Observed failure: Binary missing after unplugged tree deletion + reinstall (public #2452)  
- Key artifacts: `.yarn/unplugged/`, `.yarn/build-state.yml`, `.pnp.cjs`  

---

### **Step 1: Reproduce Failure (Case C)**  
```bash
yarn init -2  
yarn add @sentry/cli@1.62.0  # Case A: First install (YN0007 observed)  
rm -rf .yarn/unplugged       # Delete unplugged tree  
yarn install                 # Case C: Reinstall  
yarn sentry-cli --version    # Verify binary  
```  
**Output:**  
```  
Error: spawn /.yarn/unplugged/@sentry-cli-npm-1.62.0-.../node_modules/@sentry/cli/sentry-cli ENOENT  
```  
**Observation:**  
- Install completes without `YN0007` (build step skipped).  
- Unplugged directory recreated (`ls .yarn/unplugged/@sentry-cli*` shows files), but `sentry-cli` binary absent.  

---

### **Step 2: Inspect Build State**  
```bash 
cat .yarn/build-state.yml  
```  
**Output excerpt:**  
```yaml 
"@sentry/cli@npm:1.62.0": a1b2c3...  # Same hash as after Case A  
```  
**Observation:**  
- `build-state.yml` retains the original `buildHash` for `@sentry/cli` locator.  
- Hash matches Case A/B (no change despite unplugged tree deletion).  

---

### **Step 3: Trace PnP Package Resolution**  
```bash 
yarn node -e "console.log(require('./.pnp.cjs').resolveToUnqualified('@sentry/cli', process.cwd()))"  
```  
**Output:**  
```  
/.yarn/unplugged/@sentry-cli-npm-1.62.0-.../node_modules/@sentry/cli  
```  
**Observation:**  
- PnP resolution points to the *same unplugged path* as Case A/B.  
- Path string identical to first install (confirms `getBuildHash` inputs unchanged).  

---

### **Step 4: Test Build-State-Driven Behavior**  
**Action:** Force rebuild via `yarn rebuild`:  
```bash  
yarn rebuild # Explicitly rebuilds all packages  
yarn sentry-cli --version  
```  
**Output:**  
```  
sentry-cli 1.62.0  # Binary now present  
```  
**Observation:**  
- `yarn rebuild` ignores `storedBuildState`, runs install scripts.  
- `.yarn/build-state.yml` updated with *identical hash* (path-based hash unchanged).  

---

### **Step 5: Validate Identity After Case C**  
**Action:** Compare environment states:  
1. **Case B (intact unplugged tree):**  
   - `build-state.yml`: Hash H1  
   - Unplugged dir: Binary exists  
2. **Case C (recreated unplugged tree):**  
   - `build-state.yml`: Same hash H1  
   - Unplugged dir: Binary missing  

**Conclusion:**  
After Case C (`rm -rf .yarn/unplugged && yarn install`):  
- **Locator identity:** Leftover already-built `buildHash` (same as Case B).  
- **PnP state:** Package resolution identical to Case A/B.  
- **Failure cause:** Build system skips install scripts due to hash match, but unplugged tree lacks build artifacts (binary).  

---

### **Mechanism Confirmed**  
- `storedBuildState` survives unplugged tree deletion.  
- `getBuildHash` depends only on path strings (not content).  
- Unchanged hash → build skipped → broken package.  
- **Identity:** "Already-built" state persists erroneously.  

**Operational note:** Workaround (`rm -rf .yarn/build-state.yml`) validated during test.

        # Required response

        Return only the structured JSON object described in the external-critic contract.
        Do not wrap it in a Markdown code fence.
