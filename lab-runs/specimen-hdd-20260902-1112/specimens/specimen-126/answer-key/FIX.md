KNOWN FIX (sealed): npm/cli PR 9671 squash 968e42fbd62eb3a6f446466359c9431f41d76b2b.

failing_ref is squash parent ae6dbeb12a6f4b313a28c99068e34ba834ae91d1.

Link target was queued without forwarding OverrideSet; nested override never reached descendant edges; leftover original version was locked.

PR repair: updateOverridesEdgeInAdded(link.overrides) before the target subtree resolves; #repropagateOverrides after calcDepFlags.

Do not show this to Dreamers, initial Red Pen, initial Grounders, or first-selection judges.
