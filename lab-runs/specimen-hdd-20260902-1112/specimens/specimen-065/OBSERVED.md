# OBSERVED

Public pre-commit/pre-commit PR 3535. Failing world in `pre_commit/languages/docker.py`.

On the failing revision:

```
def _is_in_docker() -> bool:
    try:
        with open('/proc/1/cgroup', 'rb') as f:
            return b'docker' in f.read()
    except FileNotFoundError:
        return False

def _get_container_id() -> str:
    with open('/proc/1/cgroup', 'rb') as f:
        for line in f.readlines():
            if line.split(b':')[1] == b'cpuset':
                return os.path.basename(line.split(b':')[2]).strip().decode()
    raise RuntimeError('Failed to find the container ID in /proc/1/cgroup.')
```

`_get_docker_path` returns the original path unless `_is_in_docker()` is true, then inspects that id and rewrites cwd through matching Mounts.

cgroup v1 `/proc/1/cgroup` (reduced) contains `docker/<64-hex>` on many controllers, including `cpuset`.

cgroup v2 `/proc/1/cgroup` is typically a single line, e.g.:

```
0::/system.slice/containerd.service
```

That line has no `docker` bytes and no `cpuset` controller field. `_is_in_docker()` is False; `_get_container_id` is not reached. `docker_cmd` therefore emits `-v <container-cwd>:/src`.

`/proc/1/mountinfo` on the same cgroup v2 container still shows a host bind of `/var/lib/docker/containers/<64-hex>/hostname` onto `/etc/hostname` (and podman overlay-containers analog).

This packet does not include a local clone; treat the snippets as the world. Do not execute untrusted checkouts on the host.
