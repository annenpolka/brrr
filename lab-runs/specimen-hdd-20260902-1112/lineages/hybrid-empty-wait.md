# Hybrid: emptyunit + waitoneshot

Date: 2026-09-02 13:56 JST

Two hang shapes, not one tool.

- emptyunit (hdd-s063): completed-only scope requeues `send ()`. hang_risk is empty send of already-done work.
- waitoneshot (hdd-k8s / specimen-056): timeout 0 + wait-for-creation aborts before visit.

Replacement empty-send waits forever on an empty index list.
Timeout-0 abort never visits the object.

Do not merge the CLIs. Keep both questions.
