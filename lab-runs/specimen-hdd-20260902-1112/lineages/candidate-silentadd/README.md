# silentadd

Report an insert that returned ok while a file/dir collision remained,
including the scan start used to decide that ok.

An ordered path index can reject adding `blobtree` when `blobtree/` already
exists. A collision scan that starts at 0 and **breaks** on the first
non-prefix entry misses that later directory if any sibling sorts earlier.
The add returns success. The colliding entry is still there.

`ls` of the list plus exit 0 still looks like a successful add. This command
prints the join: add result, remaining collision, scan cursor.

This is a path-list fixture, not git and not libgit2.

## Usage

```
silentadd [--scan START] NAME ENTRY [ENTRY ...]
silentadd [--scan START] NAME --file PATH
silentadd [--scan START] NAME < entries.txt
```

| argument | meaning |
| --- | --- |
| `NAME` | path being inserted |
| `ENTRY...` | current ordered index (paths) |
| `--file PATH` | entries, one per line (`#` comments and blanks skipped) |
| `--scan START` | collision scan start: integer, or `pos` for the insertion position. Default `0` |

## Output

Tab-separated rows.

```
name	blobtree
index	aaa	blobtree/	zzz
insert_pos	1
scan_start	0
ordered	yes
add	ok
collision	present
remain	blobtree/	dir
hide	aaa
scan0	miss
scan_pos	hit
silent	yes
```

| row | meaning |
| --- | --- |
| `insert_pos` | where `NAME` would be inserted in sort order |
| `scan_start` | cursor used for the directory-prefix walk that decided `add` |
| `ordered` | whether the list is sorted (`prefix-break` is a range scan only then) |
| `add` | `ok` if that walk missed and no same-path/parent-file collision |
| `collision` | `present` if any remaining file/dir collision exists in the list |
| `remain` | colliding entry and kind (`dir` = `NAME/` child; `file` = parent or same path as file) |
| `hide` | first non-prefix entry that aborted the walk; `none` if the walk found a dir |
| `scan0` / `scan_pos` | directory-prefix walk from 0 vs from `insert_pos` (`hit`/`miss`) |
| `silent` | `yes` when add is `ok` and a collision remains |

Default `--scan 0` is the lying cursor. `--scan pos` is the insertion
position, which finds a later `NAME/` child on a sorted list.

## Example (specimen-014)

```
silentadd blobtree aaa 'blobtree/' zzz
```

`aaa` sorts before `blobtree`. Scan start 0 hits `aaa`, prefix-breaks, misses
`blobtree/`. `add` is `ok`. `remain` is `blobtree/`. `hide` is `aaa`.
`scan0` is `miss`, `scan_pos` is `hit`. `silent` is `yes`.

```
silentadd --scan pos blobtree aaa 'blobtree/' zzz
```

Scan starts at insert position 1, finds `blobtree/`, `add` is `fail`.

A list with only the colliding directory (insertion position 0) is found
even from scan start 0. That is why tests that seed a single prior entry
never catch the miss.

## Boundary

Does not read a git index, rebuild libgit2, or replace entries.
Prefix-break assumes a sorted list. Same-path and parent-file collisions
are listed regardless of scan start.
