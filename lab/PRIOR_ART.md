# Prior art (clone detector for judges)

Harvested 2026-08-20 00:08 JST from an independent explore scout. Score novelty against the *primitive*, not the README.

If a candidate’s one-sentence primitive matches a row, Novelty ≤ 2 unless it changes the *object* being acted on.

## Taken verbs

Pager/TUI/colors on git → delta/tig/lazygit. Watch-and-rerun → watchexec/entr. Fixup into the right parent → git-absorb. Stacked PRs → spr/Graphite/ghstack. Pretty or structural diff → delta/difftastic. JSON/YAML query → jq/yq. Line counts / argv bench / runtime pins → tokei/hyperfine/asdf. History rewrite / shrink → filter-repo/BFG/git-sizer. AST lint / unused / hooks → semgrep/deadcode/pre-commit. Record/replay a process → rr/strace/expect.

Full table lives in the scout transcript (subagent `01a01a86-dd08-7fa3-9f53-c0f7b8673e84`).

## Gaps the scout named (verbs, not products)

1. Intent-merge
2. CI-reify
3. Hunk-to-tests
4. Recover-lost-work
5. Why-rebuild
6. Blast-radius
7. Cross-tool undo
8. Durable pin (expectation attached to a code locus that survives rename)

## How this maps onto emerging Gen-1

None of the early candidates are obvious watchexec/delta/jq clones. Several attack *ghosts* (deleted names still speaking) which is adjacent to deadcode but inverted. `unfmt` is not semgrep. `held` is not git-bisect. `winnow` is not git-bisect. `slip` is adjacent to durable-pin / blame but relocates addresses rather than attaching notes.
