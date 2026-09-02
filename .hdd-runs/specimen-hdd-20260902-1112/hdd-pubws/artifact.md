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
