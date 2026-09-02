# FIX (sealed)

PR 38081 sets `idea.io.use.nio2` eagerly once per build tree, before the fingerprint is checked, so the value is stable across store/load. The deeper shape is: do not put unread `System.getProperties()` entries into the CC identity.

Do not leak this into Dreamer-facing files.
