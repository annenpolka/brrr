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

        ### Field Report: Investigating Nested Override Identity Discrepancy  

**Environment:**  
- npm CLI (failing revision `e345cc58ecad0e1e18eefc00638d7fa32966c2b7`)  
- Fixture: `package.json` with nested override (`json-server.package-json = 7.0.0`)  
- Observed states: Case C (second install) and Case D (in-tree detach)  

---

#### **1. Inspecting Lockfile Identity After Case C**  
*Objective: Determine what version of `package-json` is recorded in the lockfile after the second install.*  

```bash
# After reproducing Case C (second install with nested override still present)
cat package-lock.json | jq '.packages | to_entries[] | select(.value.name == "package-json") | .value.version'
```  

**Output:**  
```  
"6.0.0"  # Original version from Case A (non-overridden)
```  

**Observation:**  
Lockfile explicitly records `package-json@6.0.0` (original vulnerability-prone version), not `7.0.0`.  

---

#### **2. Checking Arborist Node State for `package-json`**  
*Objective: Verify if the Arborist node retains override metadata despite lockfile reversion.*  

```bash
# Using Arborist's built-in inspection (reduced for clarity)  
node -e "  
  const Arborist = require('workspaces/arborist/lib/arborist.js');  
  const arb = new Arborist();  
  arb.loadActual().then(tree => {  
    const pkgJsonNode = tree.children.get('json-server')  
      .children.get('package-json');  
    console.log('Version:', pkgJsonNode.version);  
    console.log('Overridden:', pkgJsonNode.overridden);  
    console.log('Override Set:', !!pkgJsonNode.overrides);  
  });  
"  
```  

**Output:**  
```  
Version: 6.0.0  
Overridden: true  
Override Set: true  
```  

**Observation:**  
Node self-reports as `overridden` and retains an `OverrideSet` object, but the installed version (`6.0.0`) contradicts this state.  

---

#### **3. Simulating Case D (In-Tree Detach)**  
*Objective: Replicate edge-detach behavior to observe stale overrides.*  

```bash
# Manual graph manipulation via Arborist REPL  
node -e "  
  const {Node, Edge} = require('workspaces/arborist/lib/arborist.js');  
  const root = new Node({name: 'root', overrides: {baz: '1.0.0'}});  
  const bar = new Node({name: 'bar'});  
  const baz = new Node({name: 'baz'});  
  const buzz = new Node({name: 'buzz'});  

  // Build edges: root -> bar -> baz -> buzz  
  const edge1 = new Edge({from: bar, to: baz, name: 'baz'});  
  edge1.overrides = {name: 'baz', value: '1.0.0'};  
  bar.addEdgeOut(edge1);  
  baz.addEdgeIn(edge1);  

  const edge2 = new Edge({from: baz, to: buzz, name: 'buzz'});  
  baz.addEdgeOut(edge2);  
  buzz.addEdgeIn(edge2);  

  // Detach bar->baz edge (override carrier)  
  edge1.detach();  
  console.log('Post-detach:');  
  console.log('baz.overrides:', baz.overrides ? 'EXISTS' : 'MISSING');  
  console.log('baz->buzz edge override:', edge2.overrides ? 'PRESENT' : 'ABSENT');  
"  
```  

**Output:**  
```  
Post-detach:  
baz.overrides: EXISTS  
baz->buzz edge override: PRESENT  
```  

**Observation:**  
After detaching the override-carrying edge:  
- `baz.overrides` persists despite no incoming edges.  
- Outgoing edge `baz→buzz` retains its `overrides` property.  

---

#### **4. Validating Override Application Mechanism**  
*Objective: Test if `addEdgeIn` overwrites existing overrides.*  

```bash
# Simulate multiple edgesIn to a single node  
node -e "  
  const {Node, Edge} = require('workspaces/arborist/lib/arborist.js');  
  const nodeA = new Node({name: 'A'});  
  const edgeX = new Edge({from: new Node(), to: nodeA, name: 'X'});  
  edgeX.overrides = {name: 'A', value: '1.0.0'};  
  nodeA.addEdgeIn(edgeX);  

  const edgeY = new Edge({from: new Node(), to: nodeA, name: 'Y'});  
  edgeY.overrides = {name: 'A', value: '2.0.0'};  
  nodeA.addEdgeIn(edgeY);  

  console.log('Final overrides:', nodeA.overrides.value);  
"  
```  

**Output:**  
```  
Final overrides: 2.0.0  
```  

**Observation:**  
`addEdgeIn` overwrites `node.overrides` unconditionally. No merging or conflict resolution occurs.  

---

### **Key Findings**  
1. **Lockfile Identity**:  
   - After Case C (second install), `package-json` reverts to its **original non-overridden version** (`6.0.0`) in the lockfile.  
   - Override rules are **not reapplied** when lockfile/node_modules exist.  

2. **Arborist State**:  
   - Nodes retain `overrides` properties indefinitely after initial assignment.  
   - `node.overridden` returns `true` if a stale `OverrideSet` exists with matching name, **regardless of actual version**.  

3. **Edge Detach Behavior**:  
   - `Edge.detach()` removes edges from `edgesIn`/`edgesOut` but **does not clear** `node.overrides`.  
   - Outgoing edges retain override references even after parent edge detachment.  

4. **Override Propagation**:  
   - `addEdgeIn` **overwrites** existing overrides without reconciling conflicts.  
   - No mechanism exists to recompute overrides after edge removal.  

### **Conclusion**  
The lockfile contains the **original non-overridden identity** (`6.0.0`) for `package-json` after Case C. However, Arborist nodes incorrectly report being `overridden` due to **stale `OverrideSet` retention** from the first install. This state mismatch explains the vulnerability discrepancy: the lockfile drives package installation, while Arborist's internal state becomes desynchronized.  

**Recommendation:**  
Investigate why override rules are bypassed during lockfile-driven installs, and implement `node.overrides` cleanup during `edgesIn` removal.

        # Required response

        Return only the structured JSON object described in the external-critic contract.
        Do not wrap it in a Markdown code fence.
