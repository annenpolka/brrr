# Harvest: hdd-debug (with adjacent hdd-config)

origin:
  method: hdd
  trial: hdd-debug

## Core Affordance

Given a configuration key, show where it is declared and where the tree assigns or implies a different value.

## Affordance Classification

USEFUL_COMPOSITION

## Nearest Existing Operation

`rg` the key across config and source, then read both hits.

## Observable Delta

The result of the query is the disagreement pair (declaration site vs contradicting site), not a list of search hits to be interpreted by the user.

## Surviving Abstractions

- Declaration site (file:line)
- Contradicting assignment/implication
- Key identity as the object of inquiry

## Removed Magic

- Deploy/hotfix trackers
- Protocol version oracles
- Live runtime metrics
- Auto-repair (`config unset`)

## Reality Mapping

Scan config-like files and source for a key/identifier. Compare literal values. Report mismatches. Honest "unknown" when values cannot be compared statically.

## Research Boundary

Will not recover runtime-only values. Will not understand every config DSL. Partial file-format coverage is acceptable.

## Smallest Useful Artifact

CLI `stated <key>` over a directory of fixtures containing a config file and a contradicting source assignment.

## Why Existing Tools Are Not Enough

grep/rg return hits; they do not classify declaration vs contradiction or fail when they disagree.
