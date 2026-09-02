# DESTROYER patchident

Date: 2026-09-02 15:20 JST
RUN_ID: specimen-hdd-20260902-1112
Target: `lineages/candidate-patchident/patchident`

Worktree `specimen-hdd/candidate-patchident-patchident` HEAD `c35f800`. Parent `main`. pnpm not invoked. No merge onto `main`.

Origin: harvest `hdd-pnpmhash` / specimen-085. Name patchedDependencies identity: object, hash-only, empty, omitted. `legacy_dot_hash` empty on a string.

Tests 6/6. Demos identical. Owned object → rc=0, hash=legacy. Hash-only → rc=1, `legacy_dot_hash -`. Empty string `empty`. Omitted selector `omitted`. Stdin object works.

Holes: parser is a tiny YAML subset (indented path/hash vs same-line string). No full YAML. Selector grep still hits both files. Hash bytes are never compared to a patch file.

Decision: **KEEP**. Load-bearing delta is naming object vs hash-only vs the `.hash`-on-string miss on owned 085 shapes. Later destroyer may KILL if it is still two greps plus a sticker. Do not add pnpm. Do not merge onto `main`.

KEEP
