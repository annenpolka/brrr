# Hybrid: emptyunit × waitoneshot

Date: 2026-09-02
Job: job-0175 (`hybrid-emptywait`)

Verdict: **NON-JOIN / thin concat**. No binary.

Proposed join: name whether a waiter never finished because (a) it was
sent an empty remaining set after completed-only requeue, or (b) it
aborted before visiting because a creation-wait default refused timeout
0. One query, two reasons.

That is two parent reports glued under the English word "waiter". It is
not a relation unavailable from concatenating parent outputs
(Constitution 13.5). Kill condition on the job was "thin concat of two
CLIs".

## Parents (host-executed)

`emptyunit` on `fixtures/063-hang.rec` (specimen-063 owned hang):

```
completed_only	testing/test_timeout.py
send	()
empty_send	yes
hang_risk	yes
```

Replacement worker is sent `()` because every unit in the scope is
already done. That is reason (a). Mixed incomplete
(`unseen-mixed.rec`) is `hang_risk no` / `send (1,2)`.

`waitoneshot` on specimen-056 flags (`timeout=0 wait_for_creation=true
for=jsonpath exists=true`):

```
visited  false
oneshot  false
abort  wait-for-creation-requires-timeout
reason  creation-wait default aborts before lookup when timeout is 0
```

Timeout 0 + wait-for-creation false is a oneshot visit. `for=delete` is
oneshot even when wait-for-creation is true. That is reason (b). Tests:
emptyunit 5/5 OK; waitoneshot 15/15 OK. Each `demo.sh` twice, logs
identical.

## Concat already names both reasons

```
python3 emptyunit fixtures/063-hang.rec
# hang_risk yes / empty_send yes / send ()

waitoneshot --timeout 0 --wait-for-creation true --for jsonpath --object-exists true
# visited false / abort wait-for-creation-requires-timeout
```

A wrapper that prints `why empty-send` vs `why abort-before-visit` is
`uniq(parent claims)`. The exclusive class reconstructs from those two
stdout blocks. Pairing a workqueue table with kubectl wait flags is
caller-invented: no owned event is both.

## No shared object

| | emptyunit | waitoneshot |
| --- | --- | --- |
| domain | pytest-xdist workqueue | kubectl wait flags |
| input | TSV collection + unit rows | `--timeout` / `--wait-for-creation` / `--for` / `--object-exists` |
| waiter | replacement worker | `kubectl wait` |
| unfinished | hang on empty send | immediate abort before lookup |
| existence | remaining indexes empty | abort still happens when `object_exists=true` |

The analogical map (empty remaining ≈ missing object) fails on the
owned abort row: waitoneshot does not consult existence on the
timeout-0 creation-wait path. emptyunit has no timeout. waitoneshot has
no workqueue. There is no remaining-set-plus-wait-policy fixture.

This is the same mashup shape as `hybrid-zerowhy` (XOR of independent
parent claims). That embodiment was already attacked this run as a
calculator over concatenated stdout. Do not mint another one.

## What was not done

Did not run `scripts/make_worktree.sh hybrid-emptywait emptywait`.
Did not invent pytest-xdist or kubectl. Did not merge onto main.

Keep the parents. Archive this note only.
