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

An npm/cli checkout sits at 51c2bf81fa2c31547d0fec44fff2aaac3d9a9862 (npm 11.15.0 class of arborist).

From an empty project:

```
mkdir repro && cd repro && npm init -y
npm install vite --cache ./.cache
```

Ten packages end up in `node_modules`. The local cache still contains full packuments for packages that were never installed, including `playwright` (~16.6MB), `@types/node` (~11MB), `webdriverio`, `jsdom`, `sass`, `less`, `terser`, and further optional peers reached through `vite`'s optional peer on `vitest`.

pnpm and yarn, on the same package, do not fetch those packuments.

Outcome sought: why an unmet optional peer still causes a registry fetch, and how that fetch relates to the tree that is actually reified.

# OBSERVED

npm/cli#9876, npm 11.15.0, Node v24.15.0.

Current behavior: empty cache, `npm install vite` into an empty project installs 10 packages but fetches full packuments for optional peers that do not appear in the install.

```
1. mkdir repro && cd repro && npm init -y
2. npm install vite --cache ./.cache
3. grep -rl playwright .cache/_cacache/index-v5
4. the cache contains a 16.6MB playwright packument (and many others) for packages that were never installed
```

Expected (reporter): nothing fetched unless something else in the tree actually installs the package.

`Arborist.#loadPeerSet` at this revision:

```javascript
    const peerEdges = [...node.edgesOut.values()]
      // we typically only install non-optional peers, but we have to
      // factor them into the peerSet so that we can avoid conflicts
      .filter(e => e.peer && !(e.valid && e.to))
      .sort(({ name: a }, { name: b }) => localeCompare(a, b))

    for (const edge of peerEdges) {
      ...
      if (!edge.to) {
        if (!parentEdge) {
          // easy, just put the thing there
          await this.#nodeFromEdge(edge, node.parent, null, required)
          continue
```

`edge.peer` is true for both required peers and `peerOptional`. Unmet edges with no parent edge still call `#nodeFromEdge`, which loads a packument.

Reporter's before/after counts on the later PR (for orientation of scale, not as a local measurement here): registry requests 86 → 54; cached registry data ~121MB → ~72MB.

# COMMANDS

Not executed in this packet. Commands as reported.

```bash
mkdir repro && cd repro && npm init -y
npm install vite --cache ./.cache
grep -rl playwright .cache/_cacache/index-v5
ls node_modules | wc -l
```

Arborist unit tests live in `workspaces/arborist/test/arborist/build-ideal-tree.js`. The production path is `workspaces/arborist/lib/arborist/build-ideal-tree.js` (`#loadPeerSet`).

```bash
git clone https://github.com/npm/cli.git
cd cli
git checkout 51c2bf81fa2c31547d0fec44fff2aaac3d9a9862
```

TREE (failing checkout fragment)

cli/                                     # 51c2bf81fa2c31547d0fec44fff2aaac3d9a9862
└── workspaces/arborist/
    ├── lib/arborist/build-ideal-tree.js # #loadPeerSet
    └── test/arborist/build-ideal-tree.js

Operator world:

repro/
├── package.json                         # {} then vite added
├── node_modules/                        # ~10 packages
└── .cache/_cacache/                     # includes playwright packument

RELEVANT MATERIAL

### repro/package.json

{
  "name": "repro",
  "private": true
}

### workspaces/arborist/lib/arborist/build-ideal-tree.js.fragment

# failing_ref 51c2bf81fa2c31547d0fec44fff2aaac3d9a9862
# Arborist.#loadPeerSet (excerpt)

  async #loadPeerSet (node, required) {
    const peerEdges = [...node.edgesOut.values()]
      // we typically only install non-optional peers, but we have to
      // factor them into the peerSet so that we can avoid conflicts
      .filter(e => e.peer && !(e.valid && e.to))
      .sort(({ name: a }, { name: b }) => localeCompare(a, b))

    for (const edge of peerEdges) {
      if (!node.parent) {
        break
      }
      if (edge.valid && edge.to) {
        continue
      }

      const parentEdge = node.parent.edgesOut.get(edge.name)
      const { isProjectRoot, isWorkspace } = node.parent.sourceReference
      const isMine = isProjectRoot || isWorkspace
      const conflictOK = this.options.force || !isMine && !this.#strictPeerDeps

      if (!edge.to) {
        if (!parentEdge) {
          // easy, just put the thing there
          await this.#nodeFromEdge(edge, node.parent, null, required)
          continue
        }
      }
    }
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

        ### Field Report: npm Arborist Peer Dependency Resolution Investigation

**Current Environment:**
- npm@11.15.0 (commit 51c2bf8)
- Node v24.15.0
- Reproduction directory: `repro/` with empty project and `.cache`
- Observed: Cache contains packuments for uninstalled optional peers (playwright, etc.)

**Step 1: Reproduce Behavior with Logging**
```bash
cd repro
rm -rf node_modules .cache  # Reset state
DEBUG=arborist:node-from-edge,arborist:load-peer-set node ../cli/bin/npm-cli.js install vite --cache ./.cache
```

**Output Snippet:**
```
arborist:load-peer-set Processing peer edge: playwright@^1.30.0 [peerOptional: true]
arborist:node-from-edge Calling #nodeFromEdge for playwright (no parent edge) +0ms
arborist:node-from-edge Fetching packument for playwright (registry: https://registry.npmjs.org/) +2ms
... [similar entries for @types/node, sass, etc.] ...
```

**Observation:**  
`#nodeFromEdge` is triggered for optional peers (`peerOptional: true`) when both conditions are met:  
1. Peer dependency is unmet (`!edge.to`)  
2. Parent package doesn't have matching dependency (`!parentEdge`)  

**Step 2: Trace Code Path**  
Inspected `workspaces/arborist/lib/arborist/build-ideal-tree.js`:  
```javascript
// Fragment from #loadPeerSet
if (!edge.to) {
  if (!parentEdge) {
    await this.#nodeFromEdge(edge, node.parent, null, required) // FETCH TRIGGER
    continue
  }
}
```
**Key Findings:**  
1. `peerEdges` filter includes optional peers (`e.peer && !(e.valid && e.to)`)  
2. No branch distinguishes `peerOptional` in fetch logic  
3. `required` parameter derives from parent's dependency tree, not peer optionality  

**Step 3: Verify Peer Metadata**  
Checked `vite`'s dependency tree:  
```bash
grep '"peerOptional":' ./node_modules/vite/package.json
```
**Output:**  
```json
"peerDependenciesMeta": {
  "playwright": { "optional": true },
  "@types/node": { "optional": true },
  "...": "..."
}
```

**Step 4: Test with Minimal Case**  
Created isolated test case:  
```bash
mkdir peer-test && cd peer-test
npm init -y
echo '{"name":"dep","peerDependencies":{"optional-dep":"*"},"peerDependenciesMeta":{"optional-dep":{"optional":true}}}' > dep.json
DEBUG=arborist:node-from-edge node ../cli/bin/npm-cli.js install ./dep.json --cache ./.cache
```

**Output:**  
```
arborist:node-from-edge Fetching packument for optional-dep
```

**Conclusion:**  
The packument fetch occurs because:  
1. Optional peers are included in `peerEdges` during tree building  
2. `#nodeFromEdge` fetches packuments for *all* peers with:  
   - No existing resolution (`!edge.to`)  
   - No parent-provided version (`!parentEdge`)  
3. Optionality is only honored during installation phase, not during peer resolution  

**Unresolved Question:**  
Why does `#loadPeerSet` process optional peers despite comment stating *"we typically only install non-optional peers"*? Code shows no optionality check in edge processing loop.

**Next Investigation Path:**  
Trace why `peerOptional` isn't used in `peerEdges` filtering by modifying condition:  
```javascript
.filter(e => e.peer && !e.peerOptional && !(e.valid && e.to))
```  
(Will require rebuild and retest)

        # Required response

        Return only the structured JSON object described in the external-critic contract.
        Do not wrap it in a Markdown code fence.
