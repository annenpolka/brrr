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


        # What to do now

        Continue operating the same tool or environment from its current state.
        Treat the limits and corrections above as facts that have just become known inside
        the world, not as review comments. Investigate their consequences through concrete
        use. Prefer commands, observations, failures, retries, and changed behavior over a
        design essay.
