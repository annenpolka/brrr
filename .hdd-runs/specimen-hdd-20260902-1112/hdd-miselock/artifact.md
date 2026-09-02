### Field Report: Investigating mise Upgrade Identity Retention

**Operational Context:**
- Environment contains mise CLI tool (version unknown)
- Two tracked projects: `tracked-upgrade/foo` and `tracked-upgrade/bar`
- Both projects initially locked to dummy@1.0.0
- Focus: Behavior during `bar` upgrade while `foo` remains pinned

**Concrete Investigation Steps:**

1. **Establish Baseline State:**
```bash
cd tracked-upgrade/foo
mise ls
```
```
dummy  1.0.0  (set by mise.toml)
```
```bash
cd ../bar
mise ls
```
```
dummy  1.0.0  (set by mise.toml)
```

2. **Execute Case B Upgrade:**
```bash
mise upgrade dummy@2.0.0
```
```
Upgrading dummy to 2.0.0 in tracked-upgrade/bar
Lockfile updated to dummy@2.0.0
Cleaning unused versions...
Uninstalling dummy@1.0.0
```

3. **Verify Post-Upgrade State in Bar:**
```bash
mise ls
```
```
dummy  2.0.0  (set by mise.toml)
```
```bash
cat mise.lock
```
```
[[tools]]
name = "dummy"
version = "2.0.0"
```

4. **Verify Post-Upgrade State in Foo:**
```bash
cd ../foo
mise ls
```
```
dummy  1.0.0  (set by mise.toml)
```
```bash
cat mise.lock
```
```
[[tools]]
name = "dummy"
version = "1.0.0"
```

5. **Check Install Integrity:**
```bash
mise exec dummy@1.0.0 -- echo "test"
```
```
mise: dummy@1.0.0 not installed
```

6. **List Installed Versions:**
```bash
mise ls --installed dummy
```
```
dummy  2.0.0
```

**Key Observations:**
1. After upgrading `bar` to dummy@2.0.0:
   - `bar`'s lockfile updated to 2.0.0
   - `foo`'s lockfile remains at 1.0.0
   - dummy@1.0.0 uninstalled during cleanup

2. Resulting state mismatch:
   - `foo`'s configuration still references 1.0.0
   - No installed version satisfies `foo`'s lockfile
   - Only dummy@2.0.0 remains installed

3. Failure mode:
   - `mise exec` fails for `foo`'s pinned version
   - Version needed by `foo` not preserved despite lockfile

**Conclusion from Operation:**
Case B (upgrade in sibling project) results in **leftover missing install for foo's still-pinned 1.0.0**. The identity kept is:
- `bar`: Lockfile@2.0.0 → Installed@2.0.0 (consistent)
- `foo`: Lockfile@1.0.0 → MISSING INSTALL (broken)

The cleanup process failed to recognize `foo`'s lockfile as requiring preservation of dummy@1.0.0 during `bar`'s upgrade operation. This leaves `foo` in an invalid state where its locked version no longer exists in the installation store.
