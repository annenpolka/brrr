# dockpath

origin.method: hdd
origin.trial: hdd-s065
specimens: [specimen-065]

classification: USEFUL_COMPOSITION

## Primitive

Name which /proc file decided in-docker, which still named a container id,
and which path became `-v` when remap did not run.

## Why this might not exist

`cat cgroup` plus `grep docker mountinfo` both hit or miss independently.
The miss is the join: detection used cgroup (no docker bytes) so the volume
source is the in-container cwd, while mountinfo still names the container.

## Core operation

Replay `_is_in_docker` as a named `cgroup_substring` bit (`b'docker' in
cgroup`). In-docker itself is a docker-shaped cpuset or `docker-<id>.scope`,
not the blob substring. Name cgroup ids with HEX12/HEX64 (cpuset, kubepods
basename, v2 scope). Parse mountinfo for docker, podman overlay, podman
`storage/overlay-containers`, and containerd task paths. Print dest as a
declared column. `remapped` is `no` or `unsupported`; never `would`.

## Observable delta

One query names cgroup miss vs mountinfo hit vs path used. Two cats do not.
Mixed v1+v2 is a kind, not a silent docker-blob win. Disagreeing ids are a
row.

## Reality mapping

Owned excerpts from specimen-065. No docker inspect.

## Removed

Live docker, invented CI cwd listings, default `--cwd /builds/project/src`,
`remapped would`.

## Smallest artifact

Python 3 stdlib CLI `dockpath`.

## How to run

From this directory:

```
python3 tests/test_dockpath.py
./demo.sh
```

`--cwd` is required.
