# Pre-implementation Reality assessment

Copied from the harvest for hdd-empty. Not execution evidence.

origin:
  method: hdd
  trial: hdd-empty

## Core Affordance

Search a tree where zero hits is a successful empty result, distinct from a bad query and from I/O failure.

## Affordance Classification

USEFUL_COMPOSITION

## Nearest Existing Operation

rg/grep (no match → exit 1).

## Observable Delta

`hits PATTERN && next` still runs after a legitimate miss.

## Surviving Abstractions

- Empty success
- Query error
- I/O error

## Removed Magic

- Artifact indexes, scan counts, 30-day windows

## Reality Mapping

Walk files, search a substring or regex. Exit 0 if zero or more matches (print matches or "0 matches"). Exit 2 on bad pattern. Exit 3 on unreadable path.

## Smallest Useful Artifact

CLI `hits PATTERN [DIR]`

## Why Existing Tools Are Not Enough

grep/rg make empty a failing status, which breaks `set -e` pipelines that wanted "none is fine".
