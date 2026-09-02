# DESTROYER inprobe

Date: 2026-09-02 15:55 JST
RUN_ID: specimen-hdd-20260902-1112
Job: job-0406
Worker: destroyer-inprobe

Target (harvested): `/Users/annenpolka/ghq/github.com/annenpolka/brrr/lab-runs/specimen-hdd-20260902-1112/lineages/candidate-inprobe/inprobe`

sha256 `91044a151919af569b03c4b0e4b61919430ca2ce6dacdca25ec021fe5f856f65` (`inprobe`, 2833 bytes, 93 lines). Worktree copy at `/Users/annenpolka/.grok/worktrees/annenpolka-brrr/candidate-inprobe-inprobe/inprobe/inprobe` is **byte-identical** (`cmp` rc=0). Worktree HEAD `93c76ad090b315765bc5add634009b70211740ca` (`Add inprobe CLI from hdd-s065 harvest (isolated; not for main).`), branch `specimen-hdd/candidate-inprobe-inprobe`. Parent `main` is `432f954c0dce09f1b72084a66075051d884cba61`; `git ls-tree HEAD inprobe` empty; archive CLI is untracked in the parent tree. Host Python 3.14.5. `docker` is on PATH (`/usr/local/bin/docker`) and **was not executed**. No `/proc` read. No merge onto `main`. Archive was not edited. No prior `DESTROYER_inprobe.md`. No `MUTATE.md`.

Origin claim (`CANDIDATE.md` / harvest `hdd-s065` / redpen HARVEST_NOW / specimen-065): name which probe file decided in-docker versus which path went to `-v`. Kind: USEFUL_COMPOSITION. Removed: live docker inspect. Artifact: stdlib CLI `inprobe`. Embodiment: caller-filled TSV `cgroup` / `mountinfo` / `path_used`.

Happy path is real. Unit tests 4/4 pass (`python3 tests/test_inprobe.py -v` → `Ran 4 tests in 0.077s` `OK`; worktree 4/4 in 0.080s). `./demo.sh` twice, live logs byte-identical to each other and to archived `demo-1.log` / `demo-2.log` (`cmp` rc=0, 408 bytes). That is not enough.

This candidate is a **THIN_WRAPPER of caller-labeled probe rows**. `inspect()` is `"docker" in cgroup.lower()`, `"docker" in mount.lower() or "/containers/" in mount`, first `/containers/<12-64 hex>/`, and echo of `path_used`. `mismatch = (not cgroup_docker) and mountinfo_docker`. Independent replica (`destroyers/_inprobe_scratch/replica.py`, does not import inprobe) is **byte-identical** to CLI stdout+stderr+rc on **52/52** host cases (2 fixtures + 40 stdin records + 10 parse errors). awk of the same two membership tests matches owned 065 and unseen v1 (`cmp` rc=0). `printf` of the five canned 065 lines is byte-identical to the CLI (sha256 `0eb501650fa664a964f0e0b5d4d408301d134c4a5bdecd647b30c0b41e47a1c1`). `path_used` is a spectator: 10/10 swapped paths leave `cgroup_docker` / `mountinfo_docker` / `container` / `mismatch` unchanged. Job kill condition: Honor KILL if THIN_WRAPPER of caller-labeled probe rows. First KEEP is not protection (none exists). Decision: **KILL**.

CLI used below:

```text
CLI=/Users/annenpolka/ghq/github.com/annenpolka/brrr/lab-runs/specimen-hdd-20260902-1112/lineages/candidate-inprobe/inprobe
FIX=/Users/annenpolka/ghq/github.com/annenpolka/brrr/lab-runs/specimen-hdd-20260902-1112/lineages/candidate-inprobe/fixtures
WT=/Users/annenpolka/.grok/worktrees/annenpolka-brrr/candidate-inprobe-inprobe/inprobe/inprobe
REP=/Users/annenpolka/ghq/github.com/annenpolka/brrr/lab-runs/specimen-hdd-20260902-1112/destroyers/_inprobe_scratch/replica.py
```

Host-executed against the archive only. Worktree was not edited. Do not merge onto `main`. Do not run docker. Do not mutate into dockpath. Do not grow a live `/proc` reader or `docker inspect` to escape THIN_WRAPPER. Do not send cgroup/mountinfo theater back to R1.

---

## What still works

Owned 065 (cgroup v2 has no `docker` bytes; mountinfo still names a container path) and unseen v1 (cgroup has `/docker/<64-hex>`; mountinfo is `none`):

```bash
python3 "$CLI" "$FIX/065-cgroupv2.rec"; echo rc=$?
python3 "$CLI" "$FIX/unseen-v1.rec"; echo rc=$?
```

```text
cgroup_docker	no
mountinfo_docker	yes
container	c33988ec7651ebc867cb24755eaf637a6734088bc7eef59d5799293a9e5450f7
path_used	/workspace
mismatch	yes
rc=0
```

```text
cgroup_docker	yes
mountinfo_docker	no
container	none
path_used	/host/src
mismatch	no
rc=0
```

Stdin of the same TSV, `/dev/stdin`, comments and blank lines skipped, field order ignored, last duplicate key wins. Missing cgroup / missing path_used / unknown field / no TAB / empty file / comments-only / `/dev/null` / missing path / directory / `-` as filename / invalid UTF-8: `inprobe:` rc=1. Two positionals: argparse rc=2. Omit `mountinfo`: defaults to `""`, `mountinfo_docker no`, `mismatch no`, rc=0.

That is the harvest surface. It is also `grep -qi docker` on two caller-typed strings plus `printf` of the third.

---

## Implementation

Load-bearing body of `inspect()`:

```python
cgroup_docker = "docker" in rec["cgroup"].lower()
mount = rec["mountinfo"]
mount_docker = "docker" in mount.lower() or "/containers/" in mount
m = HEX64.search(mount)
container = m.group(1) if m else "none"
return {
    "cgroup_docker": cgroup_docker,
    "mountinfo_docker": mount_docker,
    "container": container,
    "path_used": rec["path_used"],
    "mismatch": (not cgroup_docker) and mount_docker,
}
```

`HEX64` is `r"/containers/([0-9a-f]{12,64})/"`. `inspect.co_names` is `('lower', 'HEX64', 'search', 'group')`. `inspect.co_varnames` is `('rec', 'cgroup_docker', 'mount', 'mount_docker', 'm', 'container')`. There is no `/proc`, no `subprocess`, no volume glue, no `cpuset` parser. `Path` is only `read_text`. `path_used` is required to parse and is not read again except to print.

`KNOWN` is `("cgroup", "mountinfo", "path_used")`. The `.rec` files already contain the answer as labeled rows. `demo.sh` prints “cgroup v2 has no docker bytes; mountinfo still names a container path” before invoking the CLI.

---

## Attacks

### 1. THIN_WRAPPER of caller-labeled probe rows

Nearest ordinary workflow, no CLI:

```bash
# owned 065 fields already labeled
grep -qi docker <<<"$cgroup"          # miss
grep -qi docker <<<"$mountinfo"       # hit
# or: grep -q /containers/ <<<"$mountinfo"
printf '%s\n' "$path_used"            # /workspace
```

awk of those two memberships plus the hex capture is byte-identical to `python3 "$CLI" "$FIX/065-cgroupv2.rec"` and to `"$FIX/unseen-v1.rec"` (`cmp` rc=0).

`printf` of the five canned 065 lines:

```text
cgroup_docker	no
mountinfo_docker	yes
container	c33988ec7651ebc867cb24755eaf637a6734088bc7eef59d5799293a9e5450f7
path_used	/workspace
mismatch	yes
```

matches the CLI (`cmp` rc=0, sha256 `0eb501650fa664a964f0e0b5d4d408301d134c4a5bdecd647b30c0b41e47a1c1`).

Independent replica of parse+two-greps+echo (does not import inprobe) matches CLI leftover+rc **52/52**. The `.rec` already is the probe. The CLI reprints `yes`/`no` stickers the caller could have written.

### 2. `path_used` is echo. It never joins `-v`

Same cgroup v2 + owned mountinfo, ten paths (`/workspace`, `/builds/project/src`, `/`, `relative`, `none`, `/src`, `C:\Windows`, `/tmp/has space`, `/var/lib/docker`, `hello`):

| path_used | cgroup_docker | mountinfo_docker | container | mismatch |
| --- | --- | --- | --- | --- |
| any of the ten | no | yes | c33988ec… | yes |

10/10. `path_used /workspace:/src` is echoed with the colon; there is no `volume` column and no dest. `path_used /var/lib/docker/containers/x` with `mountinfo none`: `mismatch no` — docker bytes in the path label do not vote. The claimed third question (“which path went to `-v`”) is the string the caller already typed as `path_used`.

### 3. In-docker is substring `docker`, including `notdocker`

```text
cgroup  0::/system.slice/docker.service     + owned mountinfo
# cgroup_docker yes  mismatch no

cgroup  0::/system.slice/containerd.service + owned mountinfo
# cgroup_docker no   mismatch yes     (owned 065)

cgroup  0::/system.slice/notdocker.service  + owned mountinfo
# cgroup_docker yes  mismatch no
# because "docker" in "notdocker"

cgroup  0::/system.slice/Docker.service     + mountinfo x
# cgroup_docker yes  mismatch no

cgroup  # docker is here                    + owned mountinfo
# cgroup_docker yes  mismatch no     (value, not a comment line)

# docker
cgroup  0::/system.slice/containerd.service + owned mountinfo
# comment line skipped; cgroup_docker no  mismatch yes
```

`"docker" in "notdocker"` is True. That is the failing hook’s `b'docker' in f.read()` restated on a caller string, including the false-positive the substring always had. It is not a cpuset/id parser. Mixed v1+v2 excerpt joined into one TSV value: `cgroup_docker yes` because the cpuset line still contains `docker`; `mismatch no`; container still comes only from mountinfo.

### 4. `mountinfo_docker` is two substrings. Podman overlay misses; cri-o storage hits

Under cgroup v2 (no docker bytes):

| mountinfo | mountinfo_docker | container | mismatch |
| --- | --- | --- | --- |
| owned `/var/lib/docker/containers/<64-hex>/hostname` | yes | c33988ec… | yes |
| `/foo/containers/<64-hex>/hostname` (no word `docker`) | yes | c33988ec… | yes |
| `overlay docker-root` (word, no path) | yes | none | yes |
| `storage/overlay-containers/<64-hex>/userdata/hostname` | **no** | none | **no** |
| `io.containerd.runtime.v2.task/k8s.io/<64-hex>/rootfs` | no | none | no |
| `/var/lib/containers/storage/overlay` | **yes** | none | **yes** |
| kubelet `/pods/<uuid>/volumes` | no | none | no |
| `none` / omitted | no | none | no |

`"/containers/" in "storage/overlay-containers/…"` is False (`-containers/`, not `/containers/`). `"/containers/" in "/var/lib/containers/storage/overlay"` is True. The mountinfo analog the packet named for podman does not light `mismatch`. A host cri-o storage path with no container id does. That is substring membership, not a runtime layout.

### 5. Container id is first mountinfo hex. Cgroup id is never read

```text
/containers/c33988ec7651/hostname          container c33988ec7651     (12-hex)
/containers/c33988ec765/hostname           container none            (11-hex; still mountinfo_docker yes via word docker)
/containers/<UPPER 64-hex>/hostname        container UPPERCASE       (re.I; not folded)
/containers/<65-hex>/hostname              container none
/containers/<64-hex>   (no trailing /)     container none
/containers/bbbbbbbbbbbb/a /containers/<owned>/hostname
                                           container bbbbbbbbbbbb    (first match)
```

Unseen v1 fixture has the 64-hex on the **cgroup** line and `mountinfo none`: `container none`. Wrapped specimen-065 cgroup v1 excerpt (cpuset `/docker/<id>`) plus owned mountinfo: `cgroup_docker yes`, `mismatch no`, `container` still the mountinfo capture. The tool never asks cgroup for an id. `_get_container_id`’s cpuset walk is not present.

### 6. Empty TSV values collapse under `line.strip()`

```text
cgroup\t\n          → rc=1  expected key<TAB>value
mountinfo\t\n       → rc=1  expected key<TAB>value
path_used\t\n       → rc=1  expected key<TAB>value
```

`strip()` eats the trailing tab, then the line has no tab. Empty path is not a finished echo. Omit the mountinfo **key** (not an empty value) and parse succeeds with `mountinfo ""`. The parser is a three-key sticker bag.

### 7. No live probe. Sibling dockpath already extinct

Source has no `/proc`. `docker` on PATH was not invoked. Growing `open("/proc/1/cgroup")` plus `docker inspect` would be the harvest’s rejected theater, and would be a new harvest, not a patch of these two `in` tests. Sibling `dockpath` was Honor-KILL’d (`DESTROYER_dockpath_2.md`) as two regexes plus `printf cwd:dest`; that record already named `inprobe` as the caller-filled TSV join of `mismatch = not cgroup_docker and mountinfo still looks like a container`. Extra columns would be dressing. Constitution: a THIN_WRAPPER does not gain exotic features to escape classification. Worker rule: do not send THIN_WRAPPER / NO_SURVIVOR back to R1 with “make this more novel.” First KEEP is not protection.

---

## Primitive

Reality-stripped operation: read three caller-typed TSV fields; test substring `docker` on field 1; test substring `docker` or `/containers/` on field 2; echo field 3; set `mismatch` when the first test misses and the second hits.

Nearest ordinary workflow: `grep -qi docker` on the two labeled blobs, plus `printf '%s\n' "$path_used"`. On specimen-065 that pair is: cgroup miss, mountinfo `c33988ec…`, path `/workspace`. inprobe’s load-bearing claim is that naming `mismatch` is a join those two already contain.

It is not a join. `mismatch` is the two greps. `path_used` is `printf` of a required label. `container` is a spectator capture that does not vote. Observable capability lost if inprobe vanishes: **none**. `grep -qi docker` already says the v2 excerpt is a miss. `grep /containers/` already names the id mountinfo still had. The `-v` path is the string the caller wrote as `path_used`.

That is why this is KILL, not MUTATE. The *question* (cgroup v2 said not-in-docker, mountinfo still named the container, the hook passed in-container cwd as `-v`) is a real debugging object **when asked of `/proc` plus the hook’s argv**. This embodiment asks it of rows the caller already labeled. Red Pen nearest was `cat cgroup and mountinfo`. This is those two cats with `yes`/`no` stickers. Do not send docker inspect / live `/proc` theater back to R1. Do not mutate this into dockpath.

Hardcoded ceiling:

- `cgroup_docker` ↔ `"docker" in cgroup.lower()`
- `mountinfo_docker` ↔ `"docker" in mount.lower() or "/containers/" in mount`
- `mismatch` ↔ not `cgroup_docker` and `mountinfo_docker`
- `path_used` ↔ echo
- `container` ↔ first mountinfo `/containers/<12-64 hex>/`; cgroup id never read
- `notdocker.service` is in-docker
- podman `overlay-containers` is not `mountinfo_docker`
- `/var/lib/containers/storage` is `mountinfo_docker` with `container none`
- 11-hex / 65-hex / missing trailing slash: capture none, substring may still hit
- empty TSV value after `strip` is rc=1
- excerpts only; no live `/proc`; no inspect; no volume glue

Honor KILL. Dreamer ancestry is not protection. First KEEP is not protection.

Do not merge onto `main`. Do not run docker. Archive stays under `lineages/candidate-inprobe/`.

KILL
