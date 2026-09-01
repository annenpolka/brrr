# Harvest: hdd-agent

origin:
  method: hdd
  trial: hdd-agent

## Core Affordance

Given a working-tree change, list obligations written elsewhere in the tree that the change appears to break, including required companion files that are absent.

## Affordance Classification

USEFUL_COMPOSITION

## Nearest Existing Operation

git diff plus rg through docs/tests; a repo-specific linter.

## Observable Delta

The missing companion artifact (a file a remaining document says MUST exist) is a first-class miss tied to the change, not only a hunk list.

## Surviving Abstractions

- Change as a set of added/removed lines
- Obligation as text already in the tree (docs, tests, comments)
- Absence of a named companion file

## Removed Magic

- CVE/GHSA/ticket oracles
- Hidden assistant transcripts
- Auto-generated rationale

## Reality Mapping

Take a diff or two snapshots. Extract identifiers and MUST/SHOULD-like requirements from remaining docs. Report: removed symbols still mentioned; required files named by remaining docs that do not exist.

## Research Boundary

Will not understand policy language beyond simple patterns. Will not know true author intent.

## Smallest Useful Artifact

CLI `owes` over fixtures: a diff that deletes a function still referenced in README, and a doc that names a missing REQUIRED file.

## Why Existing Tools Are Not Enough

git diff does not ask whether remaining text still requires something the change removed or never added.
