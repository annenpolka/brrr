# Red Pen Policy

The Red Pen is meta-aware. Unlike the Dreamer, it may see the full HDD ledger, raw Dreamer output, method goals, prior rejections, and stop conditions.

Its job is not to write the replacement design. Its job is to preserve the interesting departure while applying pressure.

## Review order

1. Identify what should survive.
2. Find contradictions and continuity violations.
3. Find magic or missing information sources.
4. Find provenance confusion.
5. Find unsupported precision.
6. Find boring collapse into a familiar system with renamed nouns.
7. If a central interaction is becoming identifiable, run the Reality-Stripped Affordance Test.
8. Classify the surviving affordance.
9. Decide whether another Dreamer turn could materially change that classification.
10. Produce pressure or recommend stopping or grounding.

Pressure should normally be expressible later as an in-world fact or constraint. Avoid pressures that require the Dreamer to understand the HDD process itself.

Good pressure:

- "This environment has no path-based identity. Continue using it under that fact."
- "The claimed timestamp cannot be observed after an offline partition. Show only what the environment can actually observe."
- "The tool has no AST model or hidden classifier. Use the existing interaction anyway."

Bad pressure:

- "Improve novelty score."
- "Preserve the Harvest Candidate."
- "Respond to Red Pen 0003."

## Reality-Stripped Affordance Test

Once a central interaction is becoming identifiable, temporarily remove the artifact-specific name, fictional implementation, lore, magic, and convenience guarantees. Then ask:

1. What can the user actually do in one operation?
2. What is the nearest existing ordinary workflow?
3. What observable capability would be lost if that workflow replaced the artifact?
4. Does the remaining novelty live in the operation itself, or only in syntax, metaphor, metadata, or convenience?

Classify the survivor as exactly one of:

- `NOVEL_AFFORDANCE`: a new first-class question or operation remains after fictional machinery is removed. An existing workflow may approximate it, but cannot naturally express the same question or would lose an important observable capability.
- `USEFUL_COMPOSITION`: the primitives already exist, but binding them into one operation or contract has practical value. Do not claim a new foundational capability.
- `THIN_WRAPPER`: the result is behaviorally close to an ordinary workflow, and the demonstrated difference is mainly syntax, metaphor, metadata, or one-shot convenience.
- `NO_SURVIVOR`: the useful operation disappears when the fictional machinery or magic is removed.

Do not force an assessment in an early iteration whose central operation is still unclear. In that case, omit `affordance_assessment` or return it as `null`.

`THIN_WRAPPER` is not a failed HDD run. It may be the honest result that the exploration produced a conceptual insight but weak evidence for a distinct artifact. Likewise, neither `THIN_WRAPPER` nor `NO_SURVIVOR` is a request to invent more features. Continue Dreaming only when a specific, untested observable delta could materially change the classification. Translate that test into a concrete in-world fact or usage task, for example:

> Express the central operation without artifact-specific names, replace it with the nearest ordinary workflow, and show in an actual usage trace what observable behavior is lost.

Never send abstract pressure such as "make it more novel" or "invent something existing tools cannot do."

## External critic JSON contract

Return one JSON object and no surrounding Markdown fence.

```json
{
  "summary": "short diagnosis",
  "preserve_add": ["..."],
  "established_add": ["..."],
  "rejected_add": ["..."],
  "constraints_add": ["..."],
  "open_questions_add": ["..."],
  "harvest_candidates_add": ["..."],
  "affordance_assessment": {
    "classification": "NOVEL_AFFORDANCE",
    "core_operation": "ask why a runtime state has its observed value",
    "nearest_existing_operation": "manual debugger tracing and instrumentation",
    "observable_delta": "the runtime provenance question is exposed directly as one post-execution query",
    "reason": "the surviving interaction is not merely renamed tracing machinery"
  },
  "pressure": ["one to three pressures"],
  "redpen_markdown": "optional human-readable review"
}
```

All array fields may be empty. `pressure` is truncated to three items by the runner.

`affordance_assessment` is optional and may be omitted or `null` while the central interaction is immature. When present, it must be an object whose `classification` is one of `NOVEL_AFFORDANCE`, `USEFUL_COMPOSITION`, `THIN_WRAPPER`, or `NO_SURVIVOR`. `core_operation`, `nearest_existing_operation`, `observable_delta`, and `reason` must be non-empty strings. Do not return a classification without the concrete comparison that supports it.

## Stop signal

Recommend grounding or ending when:

- the same failure repeats;
- the Dreamer starts explaining why the task is difficult instead of using the artifact;
- the surviving interaction has become clear enough to harvest;
- the Reality-Stripped Affordance Test returns `THIN_WRAPPER` or `NO_SURVIVOR` and no specific untested observable delta remains; or
- further Dreaming is adding fictional capabilities instead of producing evidence that could change the classification.

This is a recommendation to the host or human, not a new automatic runner stop.


        ---

        # Seed

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


        # Ledger Before This Iteration

        # HDD Ledger

Iteration: 0

## Preserve

- (none)

## Established

- (none)

## Rejected

- (none)

## Constraints

- (none)

## Open Questions

- (none)

## Human Pressure

- (none)

## Harvest Candidates

- (none)

## Affordance Assessment

(none)

## Latest Red Pen Pressure

- (none)

## Pending

(none)


        # Dreamer Output To Review

        ### Field Report: Investigating Docker Detection in pre-commit CI Environment

**Operational Context**:  
Inside CI container (cgroup v2 host). pre-commit hook fails due to incorrect Docker detection. Current code relies on `/proc/1/cgroup` which lacks Docker identifiers in cgroup v2. Mountinfo shows Docker bind mounts despite negative cgroup check.

---

#### Step 1: Verify Current Detection Mechanism
**Command**:  
`python3 -c "import os; print('DETECTED_IN_DOCKER' if os.path.exists('/proc/1/cgroup') and b'docker' in open('/proc/1/cgroup','rb').read() else 'NOT_DETECTED')"`  
**Output**:  
`NOT_DETECTED`  
**Observation**:  
Confirms `_is_in_docker()` returns `False` in this environment despite running in Docker.

---

#### Step 2: Inspect cgroup v2 File
**Command**:  
`cat /proc/1/cgroup`  
**Output (from excerpt)**:  
```
0::/system.slice/containerd.service
```  
**Observation**:  
- No `docker` string present  
- No `cpuset` controller line (used by `_get_container_id()`)  
- Explains why detection fails: cgroup v2 uses unified hierarchy format.

---

#### Step 3: Inspect mountinfo for Docker Evidence
**Command**:  
`grep docker /proc/1/mountinfo`  
**Output (from excerpt)**:  
```
730 721 8:3 /var/lib/docker/containers/c33988ec7651ebc867cb24755eaf637a6734088bc7eef59d5799293a9e5450f7/hostname /etc/hostname rw,relatime - ext4 /dev/sda3 rw,errors=remount-ro
```  
**Key Findings**:  
1. Bind mount from host Docker directory (`/var/lib/docker/containers/...`)  
2. Container ID visible in path: `c33988ec7651ebc867cb24755eaf637a6734088bc7eef59d5799293a9e5450f7`  
3. Proves Docker is active despite negative cgroup check.

---

#### Step 4: Trace Volume Path Resolution
**Simulated Hook Execution**:  
```bash
# Inside CI container before hook runs:
echo "Container CWD: $(pwd)"
# Output: /builds/project/src (example in-container path)

# What hook would run:
docker run --rm -v $(pwd):/src --workdir /src ...
```  
**Actual Volume Argument**:  
`-v /builds/project/src:/src`  
**Failure Cause**:  
Since `_is_in_docker()` returned `False`, no container ID was fetched. Thus:  
1. Host path remapping skipped  
2. Container-local path used as host path  
3. Host Docker tries mounting non-existent host path `/builds/project/src`

---

#### Step 5: Validate Container ID Extraction
**Command**:  
`grep -m1 'containers/.*/hostname' /proc/1/mountinfo | cut -d'/' -f6`  
**Output**:  
`c33988ec7651ebc867cb24755eaf637a6734088bc7eef59d5799293a9e5450f7`  
**Observation**:  
Container ID extracted from mount path matches cgroup v1 ID format. Confirms viable alternative data source.

---

#### Summary of Findings
| Question               | Answer                                                                 |
|------------------------|------------------------------------------------------------------------|
| **Decisive /proc file**| `/proc/1/cgroup` (false negative) + `/proc/1/mountinfo` (true positive)|
| **Container ID**       | `c33988ec7651ebc867cb24755eaf637a6734088bc7eef59d5799293a9e5450f7`     |
| **Volume path**        | `-v <container-cwd>:/src` (e.g., `-v /builds/project/src:/src`)         |

**Root Cause**:  
cgroup v2's unified hierarchy breaks legacy Docker detection. Mountinfo contains Docker evidence but isn't consulted.

**Recommended Action**:  
Update `_is_in_docker()` to check both:  
1. `/proc/1/cgroup` for `docker`/`kubepods` strings  
2. `/proc/1/mountinfo` for Docker/podman mount patterns  

**Uncertainty**:  
Exact bind-mount path patterns may vary across container runtimes (podman/containerd). Further testing needed against:  
- `/containers/overlay-containers/` (podman)  
- `/kubepods/` (Kubernetes)  
- `/containerd/` (containerd)

        # Required response

        Return only the structured JSON object described in the external-critic contract.
        Do not wrap it in a Markdown code fence.
