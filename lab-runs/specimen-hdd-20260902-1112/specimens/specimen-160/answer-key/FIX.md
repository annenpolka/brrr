KNOWN FIX (sealed): crystal-lang/crystal PR 16958 squash ac82b6ba7dcdc83f72199e8827f68417d61b88c4.

failing_ref is parent c9e867a6703979d8e09abd2a3c1d9a7d55ae945d.

MultidispatchKey was (obj_type, call_signature). Second call site reused leftover dispatch chain after a new concrete type appeared.

PR repair: add sorted target_def object IDs to the key.

Do not show this to Dreamers, initial Red Pen, initial Grounders, or first-selection judges.
