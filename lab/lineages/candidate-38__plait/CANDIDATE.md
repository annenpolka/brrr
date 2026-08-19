# candidate-38 — plait

## Primitive

A review suggestion is a strand (span + before→after). **plait is the composition algebra of those strands with each other** (COMMUTE / STACK / ECHO / SPLIT / SUBSUME / JAM), not occupancy against a tree and not GitHub "outdated".

## Four primitives considered

1. **plait** — suggestion strands as a patch algebra; apply schedules are witnesses. **Implemented.**
2. **vow** — the author's last utterance ("done"/"fixed") is a speech-act the tree must occupy. **Discarded:** without a suggestion it is NLP; with one it is plea occupancy plus a regex.
3. **rejoin** — an edge from a review comment to the commit that answered it. **Discarded:** occupancy-in-disguise plus fuzzy matching; GitHub already has Resolve.
4. **foil** — contrary comments on one locus as UNISON / ECHO / SPLIT. **Kept as verdicts inside plait** (ECHO / SPLIT), not a second tool.

## Why this might not exist

plea/sate/lodge occupy each claim against a *tree*. GitHub outdated is line-identity. `git apply --check` is a boolean per patch. Reviewers still click "Commit suggestion" one-by-one and discover the third fails because the second shifted lines, or that two nits on the same line are two after-images, or that a later-round comment only applies after an earlier suggestion.

Nobody ships a Unix verb whose object is **the composition of the comments**, with a schedule (`line` / `time` / `topo`) as a witness. Spans are only comparable inside one `original_commit_id`; across commits the images are the object (STACK, not false JAM).

## How to run

From the worktree root:

```bash
chmod +x ./plait ./demo.sh
./plait --help
./plait --selftest
./demo.sh
./plait fixtures/cli-pr7.json
./plait --remarks fixtures/cli-cli-comments.json
./plait -C /tmp/tree fixtures/stack.jsonl
gh api repos/cli/cli/pulls/7/comments | ./plait
```

Python 3.10+, stdlib. Exit 0 composable, 1 SPLIT, 2 JAMMED, 3 error.

## Empirical transcript

### v1 (span algebra + apply witnesses; DISJOINT as a pair)

`./plait --selftest` → 21 passed (reconstruction of truncated cli/cli hunk 333030758 included).

**cli/cli PR #7** (2 suggestions on `command/pr.go:347` and `:400`):

```
COMMUTE  command/pr.go  #333030758@347  #333031216@400
plaits: two PARALLEL singletons
```

Correct pair, **wrong plait**: two commuting strands on one file were two components. You could not see "apply both".

**cli/cli last 100 review comments** (3 suggestions on `command/pr.go`): three PARALLEL singletons. `--remarks` exploded into **COVER on reply-to-remark** plus thousands of DISJOINT pairs — unreadable, and COVER was the wrong object (vilmibm's 👍 is a THREAD, not coverage of an edit).

**kizu `src/git.rs`**: two distant export nits COMMUTE and apply; adding an overlapping rewrite JAMS and apply fails.

### v2 (one improvement, from that dogfood)

1. **COMMUTE joins same-path edits** into one PARALLEL plait. PR #7 becomes `#333030758,#333031216  independent; compose in any order`. The 100-comment stream's 3 suggestions become **one PARALLEL plait**.
2. **COVER is remark×suggestion only.** Remark×remark with `in_reply_to` (or the same locus) is **THREAD**. DISJOINT pairs are hidden unless `--all-pairs`.

`--remarks` on 100 comments: 33 THREAD clusters, 17 PARALLEL leftovers, 4880 DISJOINT hidden, the 3-suggestion PARALLEL plait intact, zero COVER-on-replies.

Apply witnesses (already in v1, still hold):

| fixture | line | time | topo | same-tree |
| --- | --- | --- | --- | --- |
| commute (alpha/gamma) | ok | ok | ok | yes |
| shift (insert at L1, edit L4) | ok | ok | ok | yes (time *shifts*) |
| stack (beta→beta2→beta3, inverted created_at) | fail | fail | ok | no |
| jam overlap | fail | fail | fail | — |

`./demo.sh` **35 passed, 0 failed**.

## Dogfood targets

- Synthetic algebra: `fixtures/{commute,stack,split,jam,echo,subsume,shift,stream.md}`
- Real GitHub: `fixtures/cli-pr7.json` (PR #7, 7 comments / 2 suggestions); `fixtures/cli-cli-comments.json` (100 recent review comments on cli/cli, 3 suggestions)
- Real file: `~/ghq/github.com/annenpolka/kizu/src/git.rs` (export nits commute; overlapping rewrite jams)

## Surprises

- GitHub truncates `diff_hunk` at the commented line. original_line 347 *is* the last `+` line of a `+342,11` hunk — range reconstruction works if you count new-side lines, not if you take "the last context line".
- STACK in the wild is **cross-commit** (after of round 1 = before of round 2). Same-commit overlapping spans are JAM or SPLIT, never STACK. Treating spans as comparable across `original_commit_id` would false-JAM the 100-comment stream (`:347` vs `:23` on different SHAs).
- Most of a 100-comment review stream is **THREAD**, not edits. The algebra of suggestions is a sparse subgraph.

## Failures

- No live tree for cli/cli, so PR #7 has no apply witness (images only). kizu supplies the real-file apply.
- Remarks that are not replies and sit on different lines of the same hunk stay PARALLEL singletons; they are not a thread.
- `in_reply_to` of a *suggestion* is not modeled as THREAD-on-edit (rare in the 100-comment sample).
- Apply still requires a unique before-image when spans have shifted past recovery; ambiguous duplicates fail closed.

## Suggested mutations

- `--apply` write the topo result as a patch / worktree (the schedule becomes an action).
- Fuse with plea: occupy the *composed* after-image against HEAD (one occupancy, not N).
- Multi-file STACK (suggestion A creates the path B edits).
- `gh api …/threads` as a first-class THREAD ingest so `--remarks` does not need to reconstruct from `in_reply_to`.

## Kill / keep

**Keep.** The object is not occupancy and not leftover names. Dogfood changed the clustering rule. A developer about to click through five GitHub suggestions has a verb that says PARALLEL / SERIES / SPLIT / JAMMED *before* the third click fails.
