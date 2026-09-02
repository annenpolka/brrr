# HDD Ledger

Iteration: 1

## Preserve

- An extra annotation-processor GAV listed only on annotationProcessorPaths can fail like a missing artifact even when the reactor sibling exists, because resolveProcessorPathEntries uses local+remote only

## Established

- Packet: Case B reactor sibling not on consumer compile classpath, process-test-classes does not install; Case A published local-repo jar works; Case C missing GAV fails the same wrap
- compile classpath is reactor-aware; processorpath ArtifactResolutionRequest is not

## Rejected

- Invented mvn help / source-cat transcripts are not host-executed

## Constraints

- Owned labeled reactor/local-repo/processorpath records. No maven.

## Open Questions

- (none)

## Human Pressure

- (none)

## Harvest Candidates

- whether extra processorpath identity was local-repo jar, omitted/fail like missing GAV, reactor sibling path, or compile-classpath

## Affordance Assessment

Classification: USEFUL_COMPOSITION
Core operation: name extra processorpath identity: local-repo hit vs omitted/fail while reactor sibling exists
Nearest existing operation: grep the GAV in processorpath vs ls reactor target/classes vs ~/.m2
Observable delta: omitted_fail = reactor_present and not local_repo and processorpath fail
Reason: grep of the GAV hits the pom; the miss is processorpath vs reactor vs local repo
Assessed at iteration: 1

## Latest Red Pen Pressure

- (none)

## Pending

(none)
