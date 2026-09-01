# Harvest: hdd-merge

origin:
  method: hdd
  trial: hdd-merge

## Core Affordance

Resolve textual merge conflict markers by requiring every contested span to be tagged with the parent it came from, and emit that parentage as a first-class report.

## Affordance Classification

USEFUL_COMPOSITION

## Nearest Existing Operation

git mergetool; manually editing `<<<<<<<` markers; `git checkout --ours/--theirs`.

## Observable Delta

Ordinary merge tools produce a new blob and forget which parent supplied each contested token. This operation keeps per-span parent provenance.

## Surviving Abstractions

- Two-parent conflict regions
- Explicit parent tags on kept text
- Provenance report (not only the resolved file)

## Removed Magic

- Semantic understanding of JS/YAML
- Interactive TUI/dashboard
- Hidden AI merge

## Reality Mapping

Parse `<<<<<<< / ======= / >>>>>>>` regions. Accept a mapping of tagged choices (CLI flags, a sidecar, or tagged stdin). Write resolved text. Write a provenance list. Refuse unmarked mixed text.

## Research Boundary

Does not solve true semantic merge, binary files, or three-or-more parents beyond git's usual two-stage merge.

## Smallest Useful Artifact

A one-shot CLI, e.g. `whence resolve <file>`, plus `whence report`, stdlib only, fixtures with real conflict markers.

## Why Existing Tools Are Not Enough

`git mergetool` and marker editing do not emit parentage of the kept spans. `--ours/--theirs` is whole-region, not per-token, and records nothing.
