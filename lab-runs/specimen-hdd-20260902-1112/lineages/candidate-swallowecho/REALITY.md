# Reality assessment (pre-implementation)

classification: USEFUL_COMPOSITION

## Core operation

Report a compound command whose later success hid an earlier nonzero
exit (`|| echo` / last-status lie), naming the swallowed command and
the resulting step status 0.

## Nearest existing operation

`bash -x` plus reading `$?` after the step.

## Observable delta

Names the swallowed status rather than the step's 0. `false || echo ok`
is still a green step; the query says **false** was 1.

## Reality mapping

A small shell snippet or argv list is the world. Safe commands
(`false`, `true`, `echo`, `set`) are modeled. Bazel is not executed:
`--status` records the left-hand pipeline when a green log still
contains the `|| echo` sentence (the right-hand side ran, so the left
was nonzero).

## Constraint

Observable evidence is the compound-command text plus executed or
recorded per-command statuses. GitHub Actions and Bazel are not run.

## Research boundary

Does not reconstruct protobuf generators. Does not treat `[[ a || b ]]`
test operators as command swallows once grouped. Does not call `;`
last-status or pipe-last-status the same primitive.

## Removed

Bazel stale-file logs as host-executed evidence. Workflow repair.
Fictional `fi || echo` attachment of `||` to the whole `if`.

## Smallest artifact

Python 3 stdlib CLI `swallowecho` (`hidestatus` alias).
