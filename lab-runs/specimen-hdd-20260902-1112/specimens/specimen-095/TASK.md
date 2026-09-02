# TASK

A nested npm `overrides` rule is honored on a first install and ignored on the next install against the same tree. The lockfile identity of the overridden package does not return to the identity it had on the first install, and it also does not match a tree that never declared the nested override.

Public fixture (npm/cli#5850, npm@8.19.2 class; same shape still reported on npm 9/10):

```
{
  "name": "test",
  "version": "1.0.0",
  "engines": { "npm": ">=8.3.0" },
  "dependencies": { "json-server": "^0.17.0" },
  "overrides": {
    "json-server": {
      "package-json": "7.0.0"
    }
  }
}
```

`json-server` declares a dependency on `package-json`. The override is nested under `json-server`, not a top-level `"package-json": "7.0.0"`.

Case A — never nested-overridden (same `json-server` range, no `overrides` field):

```
npm install
```

`package-lock.json` records whatever `package-json` `json-server` actually asked for. `npm audit` reports the vulnerabilities of that original identity. There is no `"overridden"` annotation for `package-json`.

Case B — first install with the nested override, empty stores:

```
rm -rf node_modules package-lock.json
npm install
```

On npm/cli `e345cc58ecad0e1e18eefc00638d7fa32966c2b7`, this is the only install that honors the nested rule. `npm audit` reports 0 vulnerabilities. The lockfile identity of `package-json` is `7.0.0`.

Case C — second `npm install` with lockfile and `node_modules` still present (package.json still contains the nested override; this is not deleting the `overrides` field):

```
npm install
```

`npm audit` reports 5 vulnerabilities. The lockfile identity of `package-json` is no longer `7.0.0`; it matches the original (case A) identity, not case B.

Related public observations on the same failing world:

```
npm update                          # 0 vulnerabilities (override applied again)
rm -rf node_modules && npm install  # 5 vulnerabilities (lockfile leftover)
rm package-lock.json && npm install # 5 vulnerabilities (node_modules leftover)
```

A top-level (non-nested) override `"package-json": "7.0.0"` does **not** show this second-install leftover; only the nested form does.

Case D — in-tree Arborist graph, no registry. Root has `overrides: { baz: "1.0.0" }`, child `bar` depends on `baz`, `baz` depends on `buzz`. After the `bar → baz` edge is detached (the override-carrying incoming edge is gone; `baz` remains in the tree via another path, or is about to be re-linked):

On the failing revision, `baz.overrides` is still the rule copied from that edge (`addEdgeIn` did `this.overrides = edge.overrides`). `Edge.detach` / `reload` only run `this.#to.edgesIn.delete(this)`. `baz.edgesOut.get("buzz").overrides` still names the leftover rule.

The developer wants to know which identity the lockfile / Arborist node actually contained for `package-json` (public) or `baz` (in-tree) after case C / the detach: leftover original / leftover OverrideSet (same as case A, or the stale nested rule), omitted (never-overridden), or the first-install overridden identity (`7.0.0` / `baz@1.0.0`).
