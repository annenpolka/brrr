# Experiment state

- Start: 2026-08-19 23:45 JST
- Hard end: 2026-08-20 09:00 JST
- Clock: 2026-08-20 00:23 JST
- Phase: Generation 1 — Cambrian explosion (until 01:15), then dogfood (01:15–03:00)
- Parent role: coordinator only
- Heartbeat scheduler: `01a01a85796e` every 15m, durable, foreground

## Active workers

| ID | subagent_id | tool / assignment | status |
| --- | --- | --- | --- |
| candidate-01 | 01a01a85-796e-78d2-bfe0-dde59d683b37 | akin | running |
| candidate-03 | 01a01a85-796f-76d0-988f-5bc4aa5c81e4 | wisp | running |
| candidate-10 | 01a01a85-796f-76d0-988f-5c354be4601c | also | running |
| candidate-11 | 01a01a85-796f-76d0-988f-5c49cc5231d5 | rift | running |
| candidate-12 | 01a01a85-796f-76d0-988f-5c5b40ae9b40 | wraith | running |
| candidate-14 | 01a01a85-7970-76f3-9304-ba467290f2a9 | unseen | running |
| candidate-15 | 01a01a85-bf36-7370-8d54-8bed7c40c0c8 | winnow | running |
| mutation-01 | 01a01a9f-346a-7601-9e43-6388555c1aa4 | aka → wire-keys only | running |
| mutation-02 | 01a01a9f-346a-7601-9e43-6391a0670b24 | unfmt → stdin templates | running |
| mutation-03 | 01a01a9f-346a-7601-9e43-63a8f9fbdf45 | held → emit predicates | running |
| mutation-04 | 01a01a9f-346b-78e2-88a2-feeb66b194f6 | slip → gitless stream | running |
| mutation-05 | 01a01a9f-346c-7dc0-92e1-7d0b51eef919 | rift → uncommitted vs history | running |
| candidate-17 | 01a01a9f-346c-7dc0-92e1-7d1a6e398700 | new (anti-ghost) | running |
| candidate-18 | 01a01a9f-346c-7dc0-92e1-7d29b9b85e35 | new (anti-ghost) | running |
| candidate-19 | 01a01a9f-346c-7dc0-92e1-7d332e733f0b | new (anti-ghost) | running |
| candidate-20 | 01a01a9f-346c-7dc0-92e1-7d477ee4266d | new (anti-ghost) | running |

## Completed (Gen 1 ships)

| ID | tool | primitive | worktree |
| --- | --- | --- | --- |
| candidate-02 | aka | identifier inflection classes + one-sided patch check | .../ddfe15c70cd6 |
| candidate-04 | reverb | preimage of a diff as a search query | .../5bd55fb413f6 |
| candidate-05 | haunt | inverse dead-code: dead names still speaking | .../5bee2235e3dc |
| candidate-06 | deja | RELAPSE / UNDOFIX / RESURRECT vs history | .../5bf60a115585 |
| candidate-07 | zanei | leftover claims a diff just made false | .../5c00e96ceb84 |
| candidate-08 | unfmt | inverse printf against a tree | .../5c1f75800762 |
| candidate-09 | held | history eras where a predicate holds | .../5c2c16399eaa |
| candidate-13 | unfmt | independent inverse-printf (convergent) | .../ba3259b5566f |
| candidate-16 | slip | relocate file:line by fingerprint | .../8bf9fdfd09da |

## Decisions

- 2026-08-19 23:53 JST — Same broad challenge to all Gen-1 candidates. Isolated worktrees.
- 2026-08-19 23:56 JST — Saturated at 16 inventors.
- 2026-08-20 00:23 JST — Nine ships. Refilled with 5 one-assumption mutations + 4 new candidates steered off the ghost-name cluster. Independent `unfmt` convergence preserved (both lineages kept).
