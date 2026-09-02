CURRENT SITUATION
A real checkout or reduced fixture exists. The following material is what is known.

# TASK

npm's arborist can keep the identity of a **previous un-overridden transitive package** after a root `overrides` rule should have been a different lock object, when the path to that package crosses a `file:` / workspace Link. A Link and its target are not edge-connected. Override forwarding to the target ran while the target subtree was still unbuilt, so the guard found no matching rule and never forwarded.

On failing_ref `ae6dbeb12a6f4b313a28c99068e34ba834ae91d1`, `#buildDepStep` queues `link.target` without `link.target.updateOverridesEdgeInAdded(link.overrides)`. `#repropagateOverrides` runs after `#transplant`, before the actual tree's edges are fully resolved.

Public report (npm/cli#9659):

```
// package.json
{
  "name": "root",
  "dependencies": { "a": "file:./pkgs/a" },
  "overrides": { "brace-expansion": "2.0.1" }
}

// pkgs/a/package.json
{ "name": "a", "version": "1.0.0", "dependencies": { "glob": "7.2.0" } }
```

After `npm install`, lock/install identity is leftover `brace-expansion@1.1.15` (original), not overridden `2.0.1`. Same under hoisted and linked. The identical override works when `glob` is a direct root dependency (no Link boundary).

In-tree after the repair (not on failing_ref): forward `link.overrides` before the target subtree resolves; `#repropagateOverrides` after `calcDepFlags`; tests `overrides a nested dependency reached through a file: link`.

Case A — override path does not cross a Link (root depends on glob directly):
  lock identity is overridden 2.0.1
  not leftover original

Case B — override path crosses `file:./pkgs/a`, leftover original brace-expansion:
  leftover: 1.1.15 un-overridden identity
  nested override omitted on the Link target
  lock pins leftover original

Case C — delete node_modules + lock then install with no overrides:
  original identity is correct (not leftover of an override)

Case D — override forwarded before subtree resolve (post-repair shape, not on failing_ref):
  lock identity is 2.0.1
  not leftover original

The developer wants to know which identity case B actually left in the lock for brace-expansion: leftover original 1.1.15, overridden 2.0.1, or omitted (no brace-expansion).

# OBSERVED

Public npm/cli#9659 (closed 2026-06-26). PR 9671 squash `968e42fbd62eb3a6f446466359c9431f41d76b2b` (parent `ae6dbeb12a6f4b313a28c99068e34ba834ae91d1`). Local npm was not performed on this lab host.

Issue body: root override targeting a transitive dep is silently ignored when the path crosses a file:/workspace link; lock pins the original version; no warning.

On failing_ref, Link target is queued without forwarding OverrideSet. `#repropagateOverrides` exists for store links (#9619) but runs too early for a file: link whose subtree resolves late. Forward-before-queue is **not** on the failing revision. It is added by PR 9671.

Not this packet: specimen-004/033 optional-peer leftover (npm/cli#9876). specimen-095 nested override honored only on empty-store first install; subsequent install leftover original via addEdgeIn overwrite (npm/cli#5850). npm/cli#8986 leftover after deleting overrides (open). specimen-123/124 earthly leftover CACHE --id.

This packet does not include a local clone. Do not execute untrusted checkouts on the host.

```
# not executed on this lab host
# failing_ref ae6dbeb12a6f4b313a28c99068e34ba834ae91d1
# workspaces/arborist/lib/arborist/build-ideal-tree.js #buildDepStep
# workspaces/arborist/lib/arborist/load-actual.js #repropagateOverrides

# public shape:
# leftover brace-expansion@1.1.15 across file: link
# overrides { brace-expansion: 2.0.1 } omitted on Link target
```

Source-backed only. Do not execute untrusted checkouts on the host.

npm/cli
  workspaces/arborist/lib/arborist/build-ideal-tree.js
  workspaces/arborist/lib/arborist/load-actual.js
  workspaces/arborist/lib/override-set.js
  package-lock.json

RELEVANT MATERIAL

### build_ideal_link_failing.js

// Reduced excerpt of #buildDepStep link-target queue on failing_ref
// workspaces/arborist/lib/arborist/build-ideal-tree.js
// ae6dbeb12a6f4b313a28c99068e34ba834ae91d1
// Link target is queued. OverrideSet is not forwarded first.

          !link.target.parent &&
          !link.target.fsParent ||
          unseenLink) {
        this.addTracker('idealTree', link.target.name, link.target.location)
        this.#depsQueue.push(link.target)
      }

// load-actual.js: #repropagateOverrides runs after #transplant,
// before the actual tree's edges are fully resolved for a file: link.

### leftover_identity_split.txt

Registry / fixture:
  root overrides { brace-expansion: 2.0.1 }
  a via file:./pkgs/a depends on glob@7.2.0
  leftover lock brace-expansion@1.1.15

Case A (glob is a direct root dep, no Link):
  overridden 2.0.1
  not leftover original

Case B (path crosses file: link, leftover original):
  leftover: 1.1.15 un-overridden
  nested override omitted on Link target

Case C (no overrides field):
  original identity is correct
  not leftover of an override

Case D (OverrideSet forwarded before subtree):
  2.0.1
  not leftover original

Not this packet:
  optional-peer leftover (specimen-004/033)
  nested override subsequent-install leftover OverrideSet (specimen-095)
  leftover after deleting overrides (npm/cli#8986 open)
  earthly leftover CACHE --id (specimen-123/124)

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
