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

# OBSERVED

Public npm/cli#5850 (lukekarrys, 2022-11-12) / PR 8089. Failing world: npm@8.19.2 and later 9.x/10.x reports; pinned checkout `e345cc58ecad0e1e18eefc00638d7fa32966c2b7` (merge parent of the squash).

Issue reproduction (nested override only honored on a cold first install):

```
# package.json as in TASK (json-server ^0.17.0, nested package-json 7.0.0)
npm install                         # 0 vulnerabilities
npm install                         # 5 vulnerabilities
npm update                          # 0 vulnerabilities
rm -rf node_modules && npm install  # 5 vulnerabilities
rm package-lock.json && npm install # 5 vulnerabilities
rm -rf node_modules package-lock.json && npm install  # 0 vulnerabilities
```

Expected after every `npm install` while the nested override remains in package.json: lockfile identity of `package-json` stays `7.0.0`; audit stays at 0.

Saw: only the empty-store first install and `npm update` apply the nested rule. Any later `npm install` that can read the existing lockfile or `node_modules` returns the original `package-json` identity. Collaborator note (bnbdr): the same tree with a **top-level** `"package-json": "7.0.0"` override does apply on subsequent installs.

In-tree leftover on the failing revision (`workspaces/arborist/lib/node.js` `addEdgeIn`):

```
  addEdgeIn (edge) {
    if (edge.overrides) {
      this.overrides = edge.overrides
    }

    this.edgesIn.add(edge)
    ...
  }
```

That assignment overwrites `this.overrides` with the incoming edge's set. It does not walk `this.edgesOut`. `get overridden` is `!!(this.overrides && this.overrides.value && this.overrides.name === this.name)` — a leftover set still reports overridden.

`Edge.reload` / `detach` on the failing revision (`workspaces/arborist/lib/edge.js`):

```
    if (newTo !== this.#to) {
      if (this.#to) {
        this.#to.edgesIn.delete(this)
      }
      ...
    }
...
  detach () {
    ...
    if (this.#to) {
      this.#to.edgesIn.delete(this)
    }
    this.#from.edgesOut.delete(this.#name)
    ...
  }
```

`edgesIn.delete` does not recompute the target's OverrideSet from remaining incoming edges. After the override-carrying edge is gone, the leftover set on the node and its out-edges is unchanged.

Parent attach on the failing revision still copies `parent.overrides.getNodeRule(this)` onto the child when a parent is set. That is a different copy path from the incoming-edge leftover.

PR 8089 later added `workspaces/arborist/test/node.js` cases `updateOverridesEdgeInRemoved uses findSpecificOverrideSet for multiple edgesIn` and `should propagate the new override set to the target node`. Those names are not on the failing revision.

This packet is not optional-peer packument fetch of unmet peers (npm/cli#9876), not bun.lock leftover `packages` vs `optionalPeers` mention after `bun remove`, and not leftover overridden versions after deleting the `overrides` field from package.json (#8986, still open).

This packet does not include a local clone. Do not execute untrusted checkouts on the host.

# COMMANDS

```
# in-tree on failing_ref e345cc58ecad0e1e18eefc00638d7fa32966c2b7
# (not executed on this lab host)

# case A — never nested-overridden
# package.json dependencies: json-server ^0.17.0; no overrides
npm install
# lockfile identity of package-json is json-server's original range
# npm audit reports that original identity's vulnerabilities
# no overridden annotation for package-json

# case B — first install, empty stores, nested override present
# package.json overrides.json-server.package-json = 7.0.0
rm -rf node_modules package-lock.json
npm install
# npm audit: 0 vulnerabilities
# lockfile identity of package-json is 7.0.0

# case C — leftover original identity; nested override still in package.json
npm install
# npm audit: 5 vulnerabilities
# lockfile identity of package-json matches case A, not 7.0.0

# public #5850 variants
# npm update                          → 0 vulnerabilities
# rm -rf node_modules && npm install  → 5 vulnerabilities
# rm package-lock.json && npm install → 5 vulnerabilities

# case D — in-tree: detach the override-carrying incoming edge
# baz.overrides still the leftover set
# baz.edgesOut.get('buzz').overrides still names that set
# Edge.detach only ran edgesIn.delete

# unit tests live in workspaces/arborist/test/node.js
# production paths: workspaces/arborist/lib/node.js (addEdgeIn)
#                   workspaces/arborist/lib/edge.js (reload, detach)
```

Not executed on this lab host.

npm/cli
  workspaces/arborist/lib/node.js
  workspaces/arborist/lib/edge.js
  workspaces/arborist/lib/override-set.js
  workspaces/arborist/test/node.js

RELEVANT MATERIAL

### add_edge_in_failing.js

// Reduced excerpt of Node.addEdgeIn on failing_ref
// workspaces/arborist/lib/node.js
// e345cc58ecad0e1e18eefc00638d7fa32966c2b7
// Incoming override set overwrites this.overrides. Out-edges are not walked.

  addEdgeIn (edge) {
    if (edge.overrides) {
      this.overrides = edge.overrides
    }

    this.edgesIn.add(edge)

    // try to get metadata from the yarn.lock file
    if (this.root.meta) {
      this.root.meta.addEdge(edge)
    }
  }

### leftover_identity_split.txt

Registry / fixture:
  json-server@^0.17.0 (public #5850)
  nested override: json-server.package-json = 7.0.0
  in-tree: root overrides baz=1.0.0; bar depends on baz; baz depends on buzz

Case A (never nested-overridden):
  npm install
  package-json lockfile identity = json-server's original range
  npm audit reports that original identity
  no overridden annotation for package-json
  in-tree: baz.overrides undefined (or parent generic set with no baz value)

Case B (first install, empty stores, nested override present):
  rm -rf node_modules package-lock.json && npm install
  package-json lockfile identity = 7.0.0
  npm audit: 0 vulnerabilities
  in-tree: baz.overridden true when version is 1.0.0

Case C (second install; nested override still in package.json):
  npm install
  leftover original package-json identity (matches case A, not 7.0.0)
  npm audit: 5 vulnerabilities
  rm -rf node_modules && npm install  → still leftover (lockfile)
  rm package-lock.json && npm install → still leftover (node_modules)
  npm update                          → 7.0.0 again

Case D (in-tree detach of the override-carrying incoming edge):
  Edge.detach / reload: edgesIn.delete only
  leftover: baz.overrides still the copied set
  leftover: baz.edgesOut.get('buzz').overrides still names that set
  Node.overridden still true if name+value match

Not this packet:
  optional-peer packument fetch of unmet peers (specimen-004 / 033, npm/cli#9876)
  bun.lock leftover packages vs optionalPeers mention after bun remove (specimen-082)
  leftover overridden versions after deleting the overrides field (#8986, unfixed)
  leftover generic OverrideSet forwarded through a Link with no matching rule (#9359)
  top-level (non-nested) override, which does apply on subsequent installs

### overridden_failing.js

// Reduced excerpt of Node.overridden on failing_ref
// workspaces/arborist/lib/node.js
// e345cc58ecad0e1e18eefc00638d7fa32966c2b7
// A leftover OverrideSet with name+value still reports overridden.

  get overridden () {
    return !!(this.overrides && this.overrides.value && this.overrides.name === this.name)
  }

### reload_detach_failing.js

// Reduced excerpt of Edge.reload / detach on failing_ref
// workspaces/arborist/lib/edge.js
// e345cc58ecad0e1e18eefc00638d7fa32966c2b7
// Target OverrideSet is not recomputed when the incoming edge is dropped.

  reload (hard = false) {
    this.#explanation = null
    if (this.#from.overrides) {
      this.overrides = this.#from.overrides.getEdgeRule(this)
    } else {
      delete this.overrides
    }
    const newTo = this.#from.resolve(this.#name)
    if (newTo !== this.#to) {
      if (this.#to) {
        this.#to.edgesIn.delete(this)
      }
      this.#to = newTo
      this.#error = null
      if (this.#to) {
        this.#to.addEdgeIn(this)
      }
    } else if (hard) {
      this.#error = null
    }
  }

  detach () {
    this.#explanation = null
    if (this.#to) {
      this.#to.edgesIn.delete(this)
    }
    this.#from.edgesOut.delete(this.#name)
    this.#to = null
    this.#error = 'DETACHED'
    this.#from = null
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


        # What to do now

        Continue operating the same tool or environment from its current state.
        Treat the limits and corrections above as facts that have just become known inside
        the world, not as review comments. Investigate their consequences through concrete
        use. Prefer commands, observations, failures, retries, and changed behavior over a
        design essay.
