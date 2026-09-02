# MUTATE pathnode (applied 2026-09-02 13:28 JST)

From DESTROYER_pathnode.md:

1. A `found` lookup whose fixture was never registered on that node is a miss
   (`unbound yes`), not `miss none`.
2. Report `shared_node` when one node id names more than one path.
3. Tests: unbound-found; two-paths-one-node.

Happy path (specimen-003) unchanged: dir1 as n1/n3, fixture miss found=no.
