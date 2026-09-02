# HDD Ledger

Iteration: 1

## Preserve

- A ConfigurableFileTree queried at configuration time can keep the same cache identity after a file is added under the tree

## Established

- Packet: Groovy fileTree("src").files store+load then add src/file3 still loads; named files() collection is a different identity axis
- Instrumentation of fileCollectionObserved does not cover DefaultConfigurableFileTree.getFiles in the packet

## Rejected

- Invented depscan / Gradle bytecode transcripts are not host-executed

## Constraints

- Owned two identity records: dir+pattern vs file names. No gradle.

## Open Questions

- (none)

## Human Pressure

- (none)

## Harvest Candidates

- whether a fileTree configuration-cache identity included the file names or only dir+pattern, so adding a file still loads

## Affordance Assessment

Classification: USEFUL_COMPOSITION
Core operation: name whether a fileTree cache identity omitted member file names (dir+pattern only) so an added file still hits
Nearest existing operation: print the file list and the cache hit
Observable delta: omitted-names vs names-in-identity; load-after-add vs miss
Reason: the printed files= list and the cache load are two observations; the join is which identity the tree used
Assessed at iteration: 1

## Latest Red Pen Pressure

- (none)

## Pending

(none)
