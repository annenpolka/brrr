# dockpath

Name which /proc file decided in-docker, which still named a container
id, and which path became `-v` when remap did not run.

```
dockpath CGROUP MOUNTINFO --cwd PATH [--dest PATH]
```

`--cwd` is required. `--dest` defaults to `/src` as a **declared**
specimen convention, printed as its own column; it is not discovered
from the excerpts.

## Output

Tab-separated rows:

| row | meaning |
| --- | --- |
| `cgroup_substring` | specimen heuristic `b'docker' in blob` |
| `cgroup_kind` | `v1`, `v2`, `mixed`, or `empty` |
| `cgroup_docker` | docker-shaped **cpuset** or `docker-<id>.scope` (not comments / `docker.service`) |
| `cgroup_docker_via` | `cpuset`, `scope`, or `none` |
| `cgroup_id` | 12- or 64-hex id, else `none` (`user.slice` is not an id) |
| `cgroup_id_kind` | `cpuset`, `kubepods`, `scope`, or `none` |
| `mountinfo_id` | docker / podman overlay / podman storage / containerd task id |
| `id_source` | which file held an id: `cgroup`, `mountinfo`, `both`, `mismatch`, `none` |
| `id_mismatch` | `yes` when both files named different ids |
| `cwd` / `dest` | caller paths |
| `volume` | `{cwd}:{dest}` on the unmapped branch; `none` when remap is unsupported |
| `would_inspect` | `yes` only with a docker-shaped cgroup **and** a usable id |
| `remapped` | `no` or `unsupported`; never `would` |

## Example (specimen-065 v2 miss)

```
dockpath fixtures/cgroup_v2.excerpt fixtures/mountinfo_v2.hostname.excerpt --cwd /builds/project/src
```

cgroup has no docker bytes; mountinfo still names the container;
`volume` is the in-container cwd glued to the declared dest.

Owned `cgroup_v1.excerpt` is mixed v1+v2. That join is
`cgroup_kind mixed`, `remapped unsupported`, `volume none`.

## Boundary

Does not run `docker inspect`. Does not invent a host Source. Errors
are `dockpath:` lines.
