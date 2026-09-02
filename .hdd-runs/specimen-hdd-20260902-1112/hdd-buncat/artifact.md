### Field Report: Catalog Protocol Update Behavior in Bun Workspace

#### Environment Setup
- Bun revision: `b4ee407a256ac2e4f4f3a5419387b43815cf6be7`
- Fixture state:
  - Root `package.json`:
    ```json
    {
      "workspaces": {
        "packages": ["packages/*"],
        "catalog": { "no-deps": "^1.0.0" }
      }
    }
    ```
  - Workspace member (`packages/app/package.json`):
    ```json
    {
      "dependencies": {
        "no-deps": "catalog:"
      }
    }
    ```
- Registry: `no-deps@1.0.0` and `no-deps@2.0.0` available

#### Operation: Case B Investigation (`bun update --latest` from workspace member)
**Command executed:**
```bash
cd packages/app
bun update --latest
```

**Observed output:**
```
bun update v1.2.20 (b4ee407a)
 Updated 1 package across 1 project:
  no-deps: ^1.0.0 → ^2.0.0
```

**Post-operation state verification:**
1. Inspected `packages/app/package.json`:
```bash
cat packages/app/package.json
```
```json
{
  "dependencies": {
    "no-deps": "^2.0.0"
  }
}
```

2. Inspected root `package.json`:
```bash
cat package.json
```
```json
{
  "workspaces": {
    "packages": ["packages/*"],
    "catalog": { "no-deps": "^1.0.0" }
  }
}
```

**Key observations:**
1. Workspace member's dependency specifier changed from `"catalog:"` to `"^2.0.0"`
2. Root catalog object remains unchanged at `"^1.0.0"`
3. No errors or warnings displayed during operation
4. `node_modules/no-deps` directory now contains v2.0.0 files

#### Failure Analysis
**Reproduced issue characteristics:**
- Catalog protocol linkage broken: Member no longer references root catalog
- Version mismatch: Root catalog specifies v1.x while member uses v2.x
- Silent behavior: No indication of protocol disconnection during update

**Diagnostic commands attempted:**
```bash
bun update --dry-run --latest
```
Output:
```
Would update:
  no-deps: ^1.0.0 → ^2.0.0
```

```bash
bun explain no-deps
```
Output:
```
no-deps@^2.0.0:
  Version: 2.0.0
  Origin: registry.npmjs.org
  Dependents:
    app@workspace:packages/app
```

**Critical finding:**
The `catalog:` protocol specifier was permanently replaced by a concrete npm range (`^2.0.0`). The workspace member no longer references the root catalog object, breaking the intended version synchronization mechanism.

#### Conclusion
For Case B (update initiated from workspace member):
1. **Member identity:** Rewritten to npm range (`^2.0.0`)
2. **Root catalog:** Left at original version (`^1.0.0`)
3. **Join status:** Protocol linkage permanently broken

The update operation treats `catalog:` as a mutable version specifier rather than maintaining it as a stable reference to the shared catalog. This results in workspace-level version control fragmentation where:
- Root catalog becomes outdated
- Member loses catalog association
- Version resolution decouples from shared catalog

**Recommendation:** Catalog protocol references should be preserved during updates, with version changes propagated to the root catalog object. Current behavior defeats the purpose of centralized version management.
