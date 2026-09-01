# Harvest: hdd-ci

origin:
  method: hdd
  trial: hdd-ci

## Core Affordance

Snapshot two execution environments (files + env) as named captures and diff them; optionally run a command with one capture's environment variables.

## Affordance Classification

USEFUL_COMPOSITION

## Nearest Existing Operation

diff -ru; env; direnv; docker; act.

## Observable Delta

The compared object is a labeled environment capture, not an ad hoc pair of dumps the user has to remember.

## Surviving Abstractions

- Named capture
- Env-var delta vs file delta
- Replay as apply-env-and-exec (not service resurrection)

## Removed Magic

- CI tarball import
- Vaults
- Auto-started daemons
- Invented test success

## Reality Mapping

Serialize cwd env files (.env) and a file list/hashes. Diff two captures. For replay: export captured env and exec a command in a directory.

## Smallest Useful Artifact

CLI `capdiff capture|diff|replay`.

## Why Existing Tools Are Not Enough

diff and env exist; a named capture pair with env-vs-file sections is the composition worth keeping.
