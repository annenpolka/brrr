ACCEPT_R1

contrastiveness: high (loadgroup hangs after replace; other dist modes finish; empty runtest-some vs pending crashitem)
reproducibility: source-backed issue + PR + pinned merge parent/merge commit; local run not claimed
information density: high
safety: public OSS, not executed on host
nontriviality: high — crash recovery reintroduces finished work, then the worker waits forever on an empty unit
ecosystem: python / pytest-xdist
mechanism_family: worker-replacement, hang-after-crash, completed-work-requeued

Packet is the failing world only. Do not assume a root cause.
