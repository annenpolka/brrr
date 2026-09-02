# Harvest: hdd-silent-add → fossil silentadd

- Core Affordance: Report an insert that returned ok while a file/dir collision remained, including scan start.
- Affordance Classification: USEFUL_COMPOSITION at Red Pen; THIN_WRAPPER at destroyer.
- Nearest Existing Operation: print the ordered path list before and after insert plus the process exit
- Observable Delta: one query that treats exit 0 plus remaining collision as the object, not a successful add, and names the scan cursor
- Surviving Abstractions: silent-success remainder; scan-cursor dependence
- Removed Magic: git/libgit2 rebuild, invented index dumpers, adopting a known C patch
- Reality Mapping: an ordered path-list fixture of the same collision; prefix-break forward scan vs insertion-position scan
- Research Boundary: does not rebuild libgit2 or parse a real git index; the list is the world
- Smallest Useful Artifact: CLI that, given a name and an ordered entry list, prints add ok/fail, remaining colliding entries, and scan start
- Why Existing Tools Are or Are Not Enough: `ls` of the list plus exit 0 still looks like a successful add; the join (ok + remainder + cursor) is a hand comparison
- Source Specimens: specimen-014 (original), specimen-017 (counterexample: extras/requires, not a path index)
- Origin trial: hdd-silent-add
- Embodiment: `lineages/candidate-silentadd/silentadd`
- Destroyer: DESTROYER_silentadd_2.md Honor-KILL (prefix-walk / scan-0 plus remainder membership). First KEEP is not protection. Mutate-silentadd was a no-op.
