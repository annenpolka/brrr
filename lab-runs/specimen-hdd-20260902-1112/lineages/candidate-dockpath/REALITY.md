# Reality assessment

classification: USEFUL_COMPOSITION

Core operation: name the probe file that said not-in-docker while another
file still named a container path, and which path went to `-v` when remap
did not run.

Nearest: cat cgroup plus grep mountinfo plus `printf '%s:/src\n'`. Delta on
the owned v2 miss: `cgroup_docker no`, `mountinfo_id` present, `remapped no`,
`volume` is cwd plus declared dest. Mixed v1+v2 is `cgroup_kind mixed` and
`remapped unsupported` (no host Source). No docker.
