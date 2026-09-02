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
