# DESTROYER platid

Date: 2026-09-02 14:12 JST

Target: lineages/candidate-platid/platid

Owned 074: mismatch yes, same_name/version yes, platforms ruby vs x86_64-linux. Unseen darwin vs ruby same shape. Missing file rc=1.

## Implementation

Harvest was exit-0 install hiding the setup miss. platid prints mismatch yes and still **rc=0**. There is no hidden_by_exit0 / install_ok / lookup_miss. Printing two full names still leaves “install succeeded” as a hand join.

## Decision

MUTATE. rc=1 on mismatch. Name whether install_ok hid lookup_miss.
