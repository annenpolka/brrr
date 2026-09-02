# Reality assessment (pre-implementation)

classification: USEFUL_COMPOSITION

## Core operation

Report an insert that returned ok while a file/dir collision remained,
including the scan start used to decide that ok.

## Nearest existing operation

Print the ordered path list, compute the insertion index by hand, look for
`name/` children, and compare that to a process that exited 0.

## Observable delta

One query treats "exit 0 plus remaining collision" as the object, not as a
successful add, and names the scan cursor. Ordinary list printing still looks
like success.

## Reality mapping

The world is an ordered list of path strings plus a name to insert. A
directory occupies `name` when an entry is `name/` or `name/...`. A file
occupies a parent when an entry equals a parent of `name`.

Git-style `has_file_name` walks forward from a cursor and **breaks** on the
first entry that does not share the name prefix. Starting that walk at 0
means any earlier sibling hides a later `name/` collision. Starting at the
real insertion position finds it. That is the scan-cursor dependence. The
list fixture is enough; a git index file is not required.

## Research boundary

Does not rebuild libgit2, parse `.git/index`, or apply a known C patch.
Does not invent dump/debug neighbors. Unsorted input makes prefix-break
meaningless as a range scan; the tool should say so rather than pretend.

## Removed

git rebuild, index dumpers, public-PR port.

## Smallest artifact

Python 3 stdlib CLI `silentadd`.

## Why existing tools are not enough

`printf` of the list plus an exit code still presents a successful add. The
join (ok, remainder, cursor) is a hand comparison.
