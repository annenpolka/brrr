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


        # What to do now

        Continue operating the same tool or environment from its current state.
        Treat the limits and corrections above as facts that have just become known inside
        the world, not as review comments. Investigate their consequences through concrete
        use. Prefer commands, observations, failures, retries, and changed behavior over a
        design essay.
