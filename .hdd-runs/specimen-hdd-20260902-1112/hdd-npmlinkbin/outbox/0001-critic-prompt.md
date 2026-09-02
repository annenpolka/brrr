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

Under npm `install-strategy=linked`, `npm uninstall <pkg>` can leave leftover **bin-shim identity** in `node_modules/.bin` after the package's top-level symlink and `.store` entry are gone. The leftover shim is a dangling link (POSIX) or a leftover `.cmd`/`.ps1` file (Windows). A later `npm install` does not heal it.

On failing_ref `696801574984ad19ffaa9a7200d7e752920a018d`, linked reify builds the actual tree for the diff from the ideal tree (`#buildLinkedActualForDiff`), so a removed dependency is never compared against disk and the diff emits no action to drop its bin shim. Post-reify `#cleanOrphanedStoreEntries` sweeps `.store` keys and top-level links. The top-level sweep **skips dot-entries**:

```
// skip npm-managed entries (.bin, .store, .package-lock.json, etc)
if (ent.name.startsWith('.')) {
    continue
}
```

There is no `#cleanStaleBinLinks`. `#cleanOrphanedStoreEntries` does not record `package.bin` names.

Public report (npm/cli#9613), `install-strategy=linked`:

```
package.json dependencies: rimraf@3.0.2, minimatch@3.0.4
npm install
ls node_modules/.bin                 # rimraf
npm uninstall rimraf
ls -l node_modules/.bin/rimraf
# node_modules/.bin/rimraf -> ../rimraf/bin.js   (dangling; ../rimraf gone)
```

Hoisted strategy removes the `.bin` entry.

In-tree after the repair (not on failing_ref): `t.test('removes stale .bin shims after uninstall, keeps surviving ones')` in `workspaces/arborist/test/arborist/reify.js`. Adds rimraf+semver linked, uninstalls rimraf, expects rimraf / rimraf.cmd / rimraf.ps1 gone and semver shims kept.

Case A — hoisted `npm uninstall rimraf` (no linked):
  diff sees the on-disk tree
  `.bin/rimraf` removed
  no leftover shim identity

Case B — linked `npm uninstall rimraf` while `semver` remains:
  top-level `rimraf` symlink and `.store` entry removed
  leftover: `.bin/rimraf` (and `.cmd`/`.ps1`) still named rimraf
  surviving `.bin/semver` should stay

Case C — linked first install (never installed rimraf):
  no leftover uninstall shim
  not this leftover

Case D — linked uninstall then `rm -rf node_modules && npm install`:
  fresh tree
  not leftover identity (wipe, not sweep)

The developer wants to know which identity case B actually left in `node_modules/.bin`: leftover rimraf shim (dangling / stale name), both shims removed, or omitted (no `.bin` directory).

# OBSERVED

Public npm/cli#9613 (closed 2026-06-24). PR 9632 merge `981e2498589c83859b3c9e8b92a2cc67562dc06b` (single parent / squash `696801574984ad19ffaa9a7200d7e752920a018d`). Part of #9608 linked-strategy leftovers. Local npm was not performed on this lab host.

PR body: under linked, uninstall removed the top-level symlink and `.store` entry but left the shim in `node_modules/.bin` as a dangling link. The leftover shim can break tools that enumerate `.bin`, shadow a later-installed binary of the same name, and is not healed by a subsequent `npm install`. Hoisted removes the `.bin` entry.

On failing_ref, `#cleanOrphanedStoreEntries` collects valid store keys and valid top-level link names, then `#cleanOrphanedTopLevelLinks` removes orphaned symlinks whose names do not start with `.`. `.bin` is skipped as an npm-managed dot-entry. No `binsByDir` / `#cleanStaleBinLinks`.

`#cleanStaleBinLinks` is **not** on the failing revision. It is added by PR 9632: while collecting valid top-level links, record `child.package.bin` names per `node_modules` dir; then remove `.bin` entries whose base name (after stripping `.cmd`/`.ps1`) is not provided by a surviving package, or which are dangling symlinks.

Not this packet: specimen-004 / specimen-033 (npm optional-peer leftover). specimen-082 (bun optional-peer leftover / Honor-KILL peerleft). specimen-095 (npm nested-override leftover / Honor-KILL overleft). specimen-089 (yarn leftover PnP build state). job-0394/0419 npm peer leftover (duplicate 004/082/095).

This packet does not include a local clone. Do not execute untrusted checkouts on the host.

```
# not executed on this lab host
# failing_ref 696801574984ad19ffaa9a7200d7e752920a018d
# workspaces/arborist/lib/arborist/reify.js #cleanOrphanedStoreEntries
# workspaces/arborist/test/arborist/reify.js linked stale .bin test (on the PR, not failing_ref)

# public shape (linked):
# npm uninstall rimraf
# leftover: node_modules/.bin/rimraf -> ../rimraf/bin.js (dangling)
# store entry and top-level symlink gone
```

Source-backed only. Do not execute untrusted checkouts on the host.

npm/cli
  workspaces/arborist/lib/arborist/reify.js
  workspaces/arborist/test/arborist/reify.js

RELEVANT MATERIAL

### leftover_identity_split.txt

Registry / fixture:
  install-strategy=linked
  deps: rimraf + semver (or minimatch)
  npm uninstall rimraf

Case A (hoisted uninstall):
  .bin/rimraf removed
  no leftover shim

Case B (linked uninstall, semver remains):
  leftover: .bin/rimraf dangling
  store + top-level rimraf gone
  .bin/semver kept

Case C (linked first install, rimraf never present):
  no leftover uninstall shim

Case D (rm -rf node_modules && npm install):
  fresh tree
  not leftover sweep

Not this packet:
  npm optional-peer leftover (specimen-004/033)
  bun optional-peer leftover (specimen-082)
  npm nested-override leftover (specimen-095)
  yarn leftover PnP build state (specimen-089)
  cargo git+ssh vs registry (job-0339: no merged PR)

### reify_clean_orphaned_failing.js

// Reduced excerpt of #cleanOrphanedStoreEntries / top-level sweep on failing_ref
// workspaces/arborist/lib/arborist/reify.js
// 696801574984ad19ffaa9a7200d7e752920a018d
// Store keys and top-level links are swept. .bin is skipped as a dot-entry.
// No binsByDir / #cleanStaleBinLinks.

  async #cleanOrphanedStoreEntries () {
    const nmDir = resolve(this.path, 'node_modules')
    const storeDir = resolve(nmDir, '.store')
    const validKeys = new Set()
    const nmDirs = new Map()
    // ... collect valid store keys and top-level link names from idealTree ...
    for (const [dir, valid] of nmDirs) {
      await this.#cleanOrphanedTopLevelLinks(dir, valid)
    }
  }

    const orphaned = []
    for (const ent of dirents) {
      // skip npm-managed entries (.bin, .store, .package-lock.json, etc)
      if (ent.name.startsWith('.')) {
        continue
      }
      // ... orphaned top-level symlink sweep ...
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

        ### Field Report: Investigating Linked Uninstall Bin Shim Leftover

**Concrete Task:** Determine exact contents of `node_modules/.bin` after linked uninstall operation (Case B scenario) using available environment tools.

**Environment Constraints Observed:**
- Cannot execute untrusted npm revisions (failing_ref blocked)
- No local repository clone available
- Must rely on installed CLI tools and source excerpts

**Operational Sequence:**

1. **Establish Baseline with Fixed npm Version (v10.5.0):**
```bash
npm --version
# > 10.5.0  (post-PR9632)
```

2. **Simulate Case B with Fixed npm (Control Test):**
```bash
mkdir test-linked-uninstall && cd test-linked-uninstall
npm init -y
npm config set install-strategy=linked
npm install rimraf@3.0.2 semver@7.5.4
ls -1 node_modules/.bin
# > rimraf
# > rimraf.cmd
# > rimraf.ps1
# > semver
# > semver.cmd
# > semver.ps1

npm uninstall rimraf
ls -1 node_modules/.bin
# > semver
# > semver.cmd
# > semver.ps1
```
**Observation:** Fixed version correctly removes all rimraf shims (.bin/rimraf, .cmd, .ps1). Semver shims remain intact.

3. **Analyze Failing Behavior via Source Inspection:**
```bash
# Extract relevant code from failing_ref
cat <<'EOF' > failing_clean_orphaned.js
const fs = require('fs/promises');
const path = require('path');

async function simulateFailingClean(nmDir) {
  const dirents = await fs.readdir(nmDir, { withFileTypes: true });
  const orphaned = [];

  for (const ent of dirents) {
    if (ent.name.startsWith('.')) {
      console.log(`Skipping dot-entry: ${ent.name}`);
      continue;
    }

    // Simplified orphan check (would check symlink target in actual impl)
    orphaned.push(ent.name);
  }

  return orphaned;
}

// Simulate node_modules structure
const fakeNM = {
  '.bin': ['rimraf', 'semver'],
  '.store': ['rimraf@3.0.2', 'semver@7.5.4'],
  'rimraf': { isSymlink: true },
  'semver': { isSymlink: true }
};

simulateFailingClean('/fake/path').then(orphans => {
  console.log('Would remove top-level links:', orphans);
});
EOF

node failing_clean_orphaned.js
# OUTPUT:
# Skipping dot-entry: .bin
# Skipping dot-entry: .store
# Would remove top-level links: [ 'rimraf', 'semver' ]
```
**Critical Observation:** Dot-entries (.bin, .store) are explicitly skipped during orphan cleanup. Bin shims never enter removal queue.

4. **Cross-Reference with PR9632 Mechanics:**
```bash
# Extract bin cleanup logic from fix
cat <<'EOF' > fixed_bin_clean.js
function cleanStaleBinLinks(binDir, survivors) {
  const shims = ['', '.cmd', '.ps1'];
  const keep = new Set(survivors.flatMap(pkg => 
    Object.keys(pkg.bin || {}).map(name => shims.map(s => name + s))
  ).flat());

  console.log('Allowed bin names:', [...keep]);

  // In actual impl: fs.readdir -> filter -> unlink
  return {
    remove: ['rimraf', 'rimraf.cmd', 'rimraf.ps1'].filter(f => !keep.has(f))
  };
}

const survivors = [
  { name: 'semver', bin: { semver: './bin/semver' } }
];

console.log(cleanStaleBinLinks('.bin', survivors));
# OUTPUT:
# Allowed bin names: [ 'semver', 'semver.cmd', 'semver.ps1' ]
# { remove: [ 'rimraf', 'rimraf.cmd', 'rimraf.ps1' ] }
EOF
```
**Key Difference:** Fixed version explicitly enumerates bin shims and cross-references with surviving packages.

**Conclusive Findings:**

1. **Case B Leftover Identity:**  
   On failing_ref (`69680157`), `npm uninstall rimraf` leaves:
   - `node_modules/.bin/rimraf` (POSIX symlink → dangling)
   - `node_modules/.bin/rimraf.cmd` (Windows batch file)
   - `node_modules/.bin/rimraf.ps1` (PowerShell script)

2. **Surviving Elements:**  
   The `.bin` directory itself remains (contains valid semver shims).  
   Semver shims (`semver`, `semver.cmd`, `semver.ps1`) are unaffected.

3. **Root Cause Verification:**  
   The `#cleanOrphanedStoreEntries` sweep:
   - Removes top-level `rimraf` symlink (non-dot entry)
   - Skips `.bin` directory (dot-entry)
   - Never inspects `.bin` contents
   - Contains zero references to `package.bin` properties

**Evidence Chain:**
- Public report #9613 confirms dangling rimraf shim
- Source excerpt shows dot-entry skip logic
- Fixed version adds explicit bin tracking
- Test case (`removes stale .bin shims`) validates fix

**Unresolved Uncertainty:**  
Windows behavior could not be physically verified without:
1. Original failing npm binary
2. Windows test environment  
*(Reliance on source analysis and reporter's Windows observations)*

        # Required response

        Return only the structured JSON object described in the external-critic contract.
        Do not wrap it in a Markdown code fence.
