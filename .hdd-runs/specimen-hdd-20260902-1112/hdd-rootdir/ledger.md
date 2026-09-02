# HDD Ledger

Iteration: 2

## Preserve

- rootdir in a subdirectory plus collection from a parent can drop names the rootdir conftest meant to inject
- A conftest can load globally and still not bind to the collected item

## Established

- Packet: pytest 9.0.3 pass vs 9.1.1 NameError on the reporter invocation
- Packet: pytest 9.0.3 pass vs 9.1.1 NameError; specimen-055 owned parent/tests vs proj/conftest layout

## Rejected

- Specific xclim indicator NameError and --trace-config plugin lists are Dreamer-generated
- pytest --trace-config / --debug transcripts are Dreamer-generated
- Citations of public issue numbers are not specimen observations

## Constraints

- No xclim checkout
- A tiny directory layout with rootdir-subdir vs parent collection is the world
- No pytest 9.1 checkout required
- The owned two-directory fixture is the world

## Open Questions

- Can the tool list which conftest objects apply to each collected item without pytest internals dumps?

## Human Pressure

- There is no xclim tree. Continue using a two-directory fixture: conftest in a subdirectory rootdir, items collected from a parent path. Show which config applied to which item.

## Harvest Candidates

- Ask which configuration objects apply to items collected outside the rootdir

## Affordance Assessment

Classification: USEFUL_COMPOSITION
Core operation: for each collected item, show which conftest/config objects actually apply
Nearest existing operation: pytest --collect-only plus reading conftest files
Observable delta: one query that shows a visibility hole when collection path is not a descendant of rootdir
Reason: collect-only lists items but not which conftest identity they bound
Assessed at iteration: 2

## Latest Red Pen Pressure

- There is no xclim tree. Use the two-directory fixture only.

## Pending

(none)
