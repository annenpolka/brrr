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
