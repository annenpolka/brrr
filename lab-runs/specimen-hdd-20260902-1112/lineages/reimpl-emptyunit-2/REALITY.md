# Reality assessment

classification: USEFUL_COMPOSITION

Core operation: flatten a workqueue dump to nodeids, partition by dist,
then name whether any unit in the replacement burst (FIFO first, plus one
more if that partition’s pending is 1 or 2) would send an empty collection
index list.

Nearest: print the workqueue dict. Delta: same tests change hang_risk
under loadgroup vs loadscope; first_assigned vs assigned vs would_send
`()` vs hang_unit vs hang_risk. Missing indexes are errors. No pytest-xdist.

Second style vs `candidate-emptyunit`: collection-index partitions rather
than a named-dict walk of caller-grouped keys. Same leftover-identity
question. Not the Honor-KILL first-dict empty-list / dist sticker (live-first
hangs; loadscope on the same tests does not).
