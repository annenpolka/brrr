# pathnode

Name whether the same path is still the same collection object, and which
fixture is bound to which node.

A parent directory can appear more than once in CLI args. Fixtures
registered against the first directory node miss on a later node for the
same path. Printing collect output still looks like one `dir1`.

This is a collection-event fixture, not pytest.

## Usage

```
pathnode RECORD
pathnode < RECORD
```

Event fields (tab-separated):

| field | meaning |
| --- | --- |
| `collect PATH NODE` | a directory was collected as NODE |
| `register FIXTURE NODE` | fixture definition bound to NODE |
| `lookup FIXTURE NODE found\|missing` | lookup against NODE |

## Output

```
paths	dir1	dir2	dir1
nodes	n1	n2	n3
dup_path	dir1	nodes	n1	n3	same_node	no
miss	shared_fixture	lookup	n3	bound_to	n1	found	no
```

`same_node yes` means the path was collected twice as the same node id
(repaired identity). `miss none` means every lookup found.

## Example (specimen-003)

`pathnode fixtures/003-collect.rec`: dir1 is n1 and n3, `same_node no`,
`shared_fixture` bound to n1, lookup on n3 missing.
