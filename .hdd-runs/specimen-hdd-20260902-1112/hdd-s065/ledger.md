# HDD Ledger

Iteration: 1

## Preserve

- cgroup v2 can lack the docker string while mountinfo still names a docker container path

## Established

- Packet: _is_in_docker reads /proc/1/cgroup for b'docker'; cgroup v2 is 0::/system.slice/containerd.service

## Rejected

- Invented live docker inspect of this host is not the packet world

## Constraints

- No docker. Owned probe records: cgroup text, mountinfo docker path, path used in -v

## Open Questions

- (none)

## Human Pressure

- (none)

## Harvest Candidates

- Which /proc file decided in-docker, which container id if any, which path ended up in -v

## Affordance Assessment

Classification: USEFUL_COMPOSITION
Core operation: name the probe file that said not-in-docker while another file still named a container path
Nearest existing operation: cat cgroup plus grep mountinfo
Observable delta: cgroup miss vs mountinfo hit vs path used
Reason: two files, one decision; the join is the object
Assessed at iteration: 1

## Latest Red Pen Pressure

- (none)

## Pending

(none)
