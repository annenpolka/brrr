# TASK

A Bun workspace names a dependency through the **catalog protocol** (`"lodash": "catalog:"`) while the version lives in a root `catalog` / `catalogs` object. Two identities are supposed to stay joined: the workspace member's `catalog:` literal, and the named catalog entry.

On failing_ref `b4ee407a256ac2e4f4f3a5419387b43815cf6be7`, `edit_update_no_args` walks only the four dependency groups of the **current** package.json. `dependency::Tag::Catalog` is treated like an npm range: it is inserted into `updating_packages`, and with `--latest` the string is replaced by `"latest"` before install. After install the resolved npm range is written back over that string. The root `catalog` / `catalogs` objects are never walked.

Fixture (Verdaccio `no-deps@1.0.0` and `no-deps@2.0.0`; in-tree after the repair: `test/cli/install/catalogs.test.ts` `describe("update")`):

```
// root package.json
{ "workspaces": { "packages": ["packages/*"], "catalog": { "no-deps": "^1.0.0" } } }
// packages/app/package.json
{ "dependencies": { "no-deps": "catalog:" } }
```

Case A — `bun update --latest` (or `-r --latest`) from the **workspace root**:
  current package.json is the root; it has no `catalog:` literals in dep groups
  catalog object is not a dep group, so it is not rewritten
  `catalog:` in `packages/app` is not this file
  public: catalog.no-deps stays `^1.0.0` while 2.0.0 is on the registry

Case B — `bun update --latest` from **inside** `packages/app`:
  current package.json contains `"no-deps": "catalog:"`
  Tag::Catalog is admitted into `updating_packages`
  before install the value can become `"latest"`
  after install the value is a caret range (`^2.0.0`)
  root catalog object still holds `^1.0.0`
  the live join `catalog:` is gone from the member

Case C — interactive `bun update -r -i` (already handled on this revision):
  not this leftover (interactive path already edits catalogs)

Case D — `bun add no-deps@2.0.0` inside the member:
  explicit pin; replacing `catalog:` is a requested identity change
  not the silent leftover

The developer wants to know, for case B, which identity the member package.json stored after update: leftover `catalog:` still joined to the root catalog, a rewritten npm range that left the catalog object behind, or omitted.
