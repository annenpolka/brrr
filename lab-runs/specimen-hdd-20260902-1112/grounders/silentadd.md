# Grounder: silentadd

You receive the Dreamer-facing packet for specimen-014 (TASK, OBSERVED, COMMANDS, files/index_scan.py) and Harvest `hdd-origins/hdd-silent-add.md`.

You do **not** receive the answer key or any Dreamer transcript.

Question:

> What is the smallest real system that preserves the user-visible operation on the supplied specimen?

Harvested operation: report an insert that returned ok while a file/dir collision remained, including scan start.

Rules:

- Do not rebuild git/libgit2 or adopt a known C patch.
- A small ordered path list of the same collision is the world.
- Isolated git worktree: `~/.grok/worktrees/annenpolka-brrr/candidate-silentadd-silentadd`
- Do not merge onto `main`.
- Must later run on specimen-014 and specimen-017 (017 is extras/requires, not a path index).
