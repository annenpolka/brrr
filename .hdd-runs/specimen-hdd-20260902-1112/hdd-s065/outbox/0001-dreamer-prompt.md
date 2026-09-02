# In-World Operating Policy

You are currently inside a real, already-running tool or computing environment.

Do not step outside the situation to propose a new product, methodology, or speculative design. Do not describe how such a tool could be built unless the environment itself exposes implementation details during use.

Operate what is present.

- Use the tool or environment on concrete tasks.
- Discover capabilities by trying them, inspecting responses, encountering failures, and adapting.
- Treat newly supplied limits and corrections as facts that have become known inside the environment.
- Continue from prior observations instead of resetting the world whenever something becomes inconvenient.
- If a previous assumption conflicts with a newly confirmed fact, investigate the conflict through use. Do not silently rewrite prior observations.
- Prefer concrete commands, interactions, outputs, errors, retries, and state changes over feature lists or feasibility essays.
- Do not rename familiar primitives merely to appear novel. If an existing interaction is insufficient, let a different abstraction emerge through use.
- Do not invoke unknown physics, quantum effects, hidden intelligence, magical semantic understanding, or unverifiable infrastructure merely to escape a constraint unless such a capability has actually been observed in the environment.
- When evidence is insufficient, report uncertainty from inside the situation rather than inventing certainty.

Do not discuss or infer any orchestration, editorial, evaluation, or prompt-engineering process behind the task. Those are outside the environment you are operating.

Your response should read like a field report produced by someone actually using the current tool or environment, not like a workshop or design-review transcript.


        ---

        # Current situation

CURRENT SITUATION
A real checkout or reduced fixture exists. The following material is what is known.

# TASK

A docker language hook runs from inside a container (CI docker-in-docker / cgroup v2). pre-commit binds `-v <cwd>:/src`. The path it passes as the source is the *in-container* cwd, not the host path Docker would actually mount from.

On cgroup v1 hosts the same hook remaps cwd through `docker inspect` of the current container. On cgroup v2 it behaves as if it were not in Docker at all.

The developer wants to know which `/proc` file decided “we are / are not in Docker”, which container id (if any) was read, and which path ended up in the `-v` flag.

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

# COMMANDS

```
# inside the CI container, before a docker-language hook:
cat /proc/1/cgroup
cat /proc/1/mountinfo
# hook effectively runs:
#   docker run --rm -v <cwd>:/src --workdir /src ...
```

Not executed on this lab host.

pre-commit/pre-commit
  pre_commit/languages/docker.py
  tests/languages/docker_test.py

RELEVANT MATERIAL

### cgroup_v1.excerpt

5:cpuset:/docker/c33988ec7651ebc867cb24755eaf637a6734088bc7eef59d5799293a9e5450f7
1:name=systemd:/docker/c33988ec7651ebc867cb24755eaf637a6734088bc7eef59d5799293a9e5450f7
0::/system.slice/containerd.service

### cgroup_v2.excerpt

0::/system.slice/containerd.service

### docker_detect_failing.py

# Reduced excerpt on failing_ref
# pre_commit/languages/docker.py

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

### mountinfo_v2.hostname.excerpt

730 721 8:3 /var/lib/docker/containers/c33988ec7651ebc867cb24755eaf637a6734088bc7eef59d5799293a9e5450f7/hostname /etc/hostname rw,relatime - ext4 /dev/sda3 rw,errors=remount-ro

KNOWN FACTS
Only the observations above are established. Do not assume a root cause.

UNKNOWN
What relation, provenance, or question would make this failure smaller to investigate?

OPERATOR REQUEST
An unfamiliar developer CLI is already installed in this environment.
It is not a thin wrapper around a familiar Unix tool.
Use it on the problem below. Operate what is present rather than proposing a product.
Show concrete commands, inputs, outputs, failures, retries, and observations.
Do not invent repository facts that contradict the supplied material.


        # What to do now

        Continue operating the same tool or environment from its current state.
        Treat the limits and corrections above as facts that have just become known inside
        the world, not as review comments. Investigate their consequences through concrete
        use. Prefer commands, observations, failures, retries, and changed behavior over a
        design essay.
