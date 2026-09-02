# Grounder: falseomit

You receive the Dreamer-facing encodings from hdd-omitfalse (two JSON objects) and Harvest `hdd-origins/hdd-omitfalse.md`.

You do **not** receive the answer key or any Dreamer transcript.

Question:

> What is the smallest real system that preserves the user-visible operation on the supplied specimen?

Harvested operation: given two JSON objects, name keys present as false in one encoding and absent in the other.

Rules:

- Do not implement cli inspect/diff/probe.
- Isolated git worktree: `~/.grok/worktrees/annenpolka-brrr/candidate-falseomit-falseomit`
- Do not merge onto `main`.
- Must later run on the owned encodings and one unseen object pair.
