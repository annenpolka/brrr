# HDD Ledger

Iteration: 1

## Preserve

- Frozen install can materialize a ruby-platform gem while setup still searches the locked platform identity

## Established

- Packet: lock has nokogiri (1.18.10-x86_64-linux); install fetches/installs nokogiri 1.18.10 exit 0; setup cannot find nokogiri-1.18.10-x86_64-linux

## Rejected

- Invented bundle info, bundle platform, and inline Bundler patches are not host-executed

## Constraints

- Owned two identity records. No bundler.

## Open Questions

- (none)

## Human Pressure

- (none)

## Harvest Candidates

- which identity install materialized versus which identity setup searched for

## Affordance Assessment

Classification: USEFUL_COMPOSITION
Core operation: name materialized identity vs lookup identity when name+version match and platform does not
Nearest existing operation: print both gem full names
Observable delta: install ruby-platform vs setup locked linux platform
Reason: exit 0 install hides the identity that setup will miss
Assessed at iteration: 1

## Latest Red Pen Pressure

- (none)

## Pending

(none)
