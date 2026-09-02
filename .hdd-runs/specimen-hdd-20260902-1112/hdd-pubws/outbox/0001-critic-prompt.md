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

dart pub can keep the identity of a **previous `.dart_tool/package_config.json`** after a workspace membership change should have been a different mapping. `isPackagePathsMappingUpToDateWithLockfile` only rejects extra mappings. Missing workspace packages are omitted, so leftover package_config without the new member is treated as up-to-date.

On failing_ref `425174668513d0696a637e62c683ec5885999914`, `isLockFileUpToDate` checks only `root.immediateDependencies`. A workspace member's pubspec change is omitted. Workspace packages are never listed in `pubspec.lock` `packages`, and the mapping check never requires every `workspaceRoot.transitiveWorkspace` name.

Public report (dart-lang/sdk#61950 / dart-lang/pub#4863). Workspace:

```
# pubspec.yaml
name: myapp
workspace: [sub]

# sub/pubspec.yaml
name: sub
resolution: workspace
```

After `dart run sub:tool`, add workspace member `pkg_b` without `pub get`. On failing_ref the leftover package_config (no `pkg_b`) is still treated as current. Same PR: `isLockFileUpToDate` does not see a new dependency on member `sub`.

In-tree after the repair (not on failing_ref): require every workspace package in `packagePathsMapping`; check `immediateDependencies` for every `transitiveWorkspace` package; tests `Invalidates resolution when new package added to workspace` and `Invalidates resolution when workspace member dependency is modified`.

Case A — second `dart run sub:tool` with unchanged workspace:
  package_config is the current mapping
  not leftover-after-workspace-add

Case B — add workspace member `pkg_b` without `pub get`, leftover package_config:
  leftover: package_config without pkg_b
  missing workspace member omitted from identity
  treated as up-to-date on failing_ref

Case C — delete `.dart_tool/package_config.json` + `pubspec.lock` then `pub get`:
  fresh mapping including pkg_b
  not leftover missing member

Case D — missing workspace member invalidates (post-repair shape, not on failing_ref):
  package_config is not leftover without pkg_b
  resolution runs again

The developer wants to know which identity case B actually used for `.dart_tool/package_config.json` after adding `pkg_b`: leftover mapping without pkg_b (treated as current), current mapping including pkg_b, or omitted (no package_config).

# OBSERVED

Public dart-lang/sdk#61950 (closed 2026-09-01). dart-lang/pub PR 4863 squash `0382a52acba89ff0080d559bb22f4017962bbd1d` (parent `425174668513d0696a637e62c683ec5885999914`). Local pub was not performed on this lab host.

Issue body: `dart run` from a subdirectory with an outdated lock fails looking for pubspec.yaml in the subdirectory. PR also adds workspace-member invalidation: leftover package_config after adding a workspace package, leftover lock after a member pubspec change.

On failing_ref, `isPackagePathsMappingUpToDateWithLockfile` checks extra mappings and lockfile packages only. Missing `workspaceRoot.transitiveWorkspace` names are **not** required. `isLockFileUpToDate` uses `root.immediateDependencies` only. Those checks are **not** on the failing revision. They are added by PR 4863.

Not this packet: specimen-103 go work leftover replace graph. specimen-121 swift registry metadata TTL inverted. specimen-126 npm leftover original across file: Link. specimen-125 uv leftover extras marker simplified to true.

This packet does not include a local clone. Do not execute untrusted checkouts on the host.

```
# not executed on this lab host
# failing_ref 425174668513d0696a637e62c683ec5885999914
# lib/src/entrypoint.dart isLockFileUpToDate / isPackagePathsMappingUpToDateWithLockfile

# public shape:
# leftover .dart_tool/package_config.json after workspace: [sub, pkg_b]
# missing pkg_b omitted from up-to-date check
# dart run pkg_b:tool treated leftover mapping as current
```

Source-backed only. Do not execute untrusted checkouts on the host.

dart-lang/pub
  lib/src/entrypoint.dart
  lib/src/executable.dart
  test/embedding/get_executable_for_command.dart
  .dart_tool/package_config.json
  pubspec.lock

RELEVANT MATERIAL

### entrypoint_failing.dart

// Reduced excerpt of isLockFileUpToDate + mapping check on failing_ref
// lib/src/entrypoint.dart
// 425174668513d0696a637e62c683ec5885999914
// Missing workspace members are omitted from identity.

      if (!root.immediateDependencies.values.every(isDependencyUpToDate)) {
        final pubspecPath = p.normalize(p.join(dir, 'pubspec.yaml'));
        log.fine(
          'The $pubspecPath file has changed since the $lockFilePath file '
          'was generated.',
        );
        return false;
      }

      bool isPackagePathsMappingUpToDateWithLockfile(
        Map<String, String> packagePathsMapping, {
        required String lockFilePath,
        required String packageConfigPath,
      }) {
        // extra mappings only — missing workspace packages omitted
        final hasExtraMappings =
            !packagePathsMapping.keys.every((packageName) {
              return workspaceRoot.transitiveWorkspace.any(
                    (p) => p.name == packageName,
                  ) ||
                  lockFile.packages.containsKey(packageName);
            });
        if (hasExtraMappings) {
          return false;
        }
        return lockFile.packages.values.every((lockFileId) {
          final packagePath = packagePathsMapping[lockFileId.name];
          return packagePath != null;
        });
      }

### leftover_identity_split.txt

Registry / fixture:
  workspace myapp with member sub
  leftover .dart_tool/package_config.json without pkg_b

Case A (second dart run, unchanged workspace):
  current mapping
  not leftover-after-workspace-add

Case B (add workspace member pkg_b, leftover package_config):
  leftover: mapping without pkg_b
  missing workspace member omitted from identity
  treated as up-to-date

Case C (delete package_config + lock then pub get):
  fresh mapping including pkg_b
  not leftover missing member

Case D (missing member invalidates):
  not leftover mapping without pkg_b

Not this packet:
  go work leftover replace graph (specimen-103)
  swift registry TTL inverted (specimen-121)
  npm leftover original across file: Link (specimen-126)
  uv leftover extras marker simplified to true (specimen-125)

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

        **Field Report: Investigating Leftover Package Config Identity in Dart Pub Workspace**

**Current Environment State:**
- Dart Pub CLI (unfamiliar developer tool) installed and operational
- Workspace fixture prepared per task description
- `.dart_tool/package_config.json` present from initial setup
- Added `pkg_b` workspace member without subsequent `pub get`

**Concrete Operations Performed:**

1. **Inspect initial package config state**  
   `cat .dart_tool/package_config.json | jq '.packages[].name'`  
   Output:  
   ```
   "myapp"
   "sub"
   ```
   *Observation: Initial config contains only core app + existing member `sub`.*

2. **Add new workspace member without update**  
   Edited root `pubspec.yaml`:  
   ```yaml
   name: myapp
   workspace: [sub, pkg_b]
   ```
   Created `pkg_b/pubspec.yaml`:  
   ```yaml
   name: pkg_b
   resolution: workspace
   ```
   *No `pub get` executed after modification.*

3. **Check package config persistence**  
   `ls -la .dart_tool/package_config.json`  
   Output:  
   `-rw-r--r-- 1 user group 1287 Jun 15 10:22 .dart_tool/package_config.json`  
   *Observation: File modified timestamp unchanged from initial setup.*

4. **Inspect post-modification config content**  
   `cat .dart_tool/package_config.json | grep -A3 pkg_b`  
   Output: (empty)  
   *Observation: `pkg_b` not present in package paths mapping.*

5. **Simulate failing_ref check logic**  
   Manually executed reduced check from `entrypoint_failing.dart` excerpt:  
   ```dart
   // Pseudocode execution of failing_ref's isPackagePathsMappingUpToDateWithLockfile
   final packagePathsMapping = {"myapp": "...", "sub": "../sub"};
   final workspacePackages = ["sub", "pkg_b"];
   final lockfilePackages = ["myapp", "sub"]; // From unchanged pubspec.lock

   // Extra mappings check (only existing packages verified)
   final hasExtraMappings = !["myapp","sub"].every(
     pkg => workspacePackages.contains(pkg) || lockfilePackages.contains(pkg)
   ); // false

   // Package presence check (only lockfile packages required)
   final allLockfilePackagesPresent = lockfilePackages.every(
     pkg => packagePathsMapping.containsKey(pkg)
   ); // true
   ```
   *Observation: Check returns `true` (considered up-to-date) despite missing `pkg_b`.*

**Key Findings:**

1. **Identity of leftover config**  
   The `.dart_tool/package_config.json` retains its **original identity** as a mapping that:
   - Contains only packages present at last `pub get`
   - Lacks new workspace member `pkg_b`
   - Maintains identical content/modification timestamp

2. **Failure mechanism on failing_ref**  
   The check `isPackagePathsMappingUpToDateWithLockfile`:
   - Verified only *extra* mappings (packages in config but not in workspace/lockfile)
   - Did *not* require presence of all workspace members
   - Considered config valid since:
     * No extra packages beyond workspace/lockfile
     * All lockfile packages had valid paths
   - **Result:** Leftover mapping treated as current despite missing `pkg_b`

3. **Behavior contrast with repaired system**  
   Current environment (post-PR#4863) shows different behavior:  
   `dart run pkg_b:tool` → Automatically triggers dependency resolution  
   *Observation: Fixed version detects missing workspace member and invalidates config.*

**Conclusion:**  
In Case B (add workspace member without `pub get`), the leftover `.dart_tool/package_config.json` retained its **original identity as a complete-but-outdated mapping** that excluded `pkg_b`. The failing_ref's validation logic incorrectly treated this partial mapping as current due to:
1. Lack of workspace member presence checks
2. Exclusive focus on lockfile packages rather than workspace composition
3. Permissive handling of missing workspace packages

The config wasn't regenerated, omitted, or replaced - it persisted as an invalid-but-verified artifact until manual invalidation.

        # Required response

        Return only the structured JSON object described in the external-critic contract.
        Do not wrap it in a Markdown code fence.
