# DESTROYER dockpath 2

Date: 2026-09-02 14:18 JST
RUN_ID: specimen-hdd-20260902-1112

Target (archive, post-MUTATE remapped-unsupported):
`/Users/annenpolka/ghq/github.com/annenpolka/brrr/lab-runs/specimen-hdd-20260902-1112/lineages/candidate-dockpath/dockpath`

CLI sha256 `ec012938bdc9243b46a68e685a7b2bd0da807c166fdfc694534fde747bd0e661` (9702 bytes). Matches `lineages/candidate-dockpath/MUTATE.md` after. First record: `destroyers/DESTROYER_dockpath.md`. Tests: `python3 tests/test_dockpath.py` → 31 OK. No docker. Not merged to `main`.

Origin claim after mutation: name which /proc file decided in-docker, which still named a container id, and which path became `-v` **when remap did not run**. `remapped` is `no` | `unsupported`, never `would`. Kind: USEFUL_COMPOSITION. Owned: specimen-065 cgroup v2 miss + mixed v1+v2 excerpt.

Happy path is still real. That is not enough.

This candidate is a **THIN_WRAPPER of two regexes** plus `printf '%s:%s\n' --cwd --dest`. `inspect()` never reads mountinfo when it decides `remapped` or `volume`. `id_source` is string equality of two captures. Decision: **KILL**.

```text
CLI=/Users/annenpolka/ghq/github.com/annenpolka/brrr/lab-runs/specimen-hdd-20260902-1112/lineages/candidate-dockpath/dockpath
FIX=/Users/annenpolka/ghq/github.com/annenpolka/brrr/lab-runs/specimen-hdd-20260902-1112/lineages/candidate-dockpath/fixtures
CWD=/builds/project/src
CID=c33988ec7651ebc867cb24755eaf637a6734088bc7eef59d5799293a9e5450f7
```

Host-executed against the archive only. Worktree
`/Users/annenpolka/.grok/worktrees/annenpolka-brrr/candidate-dockpath-dockpath`
was not edited. Parent `main` stays coordinator-only.

---

## What still works

Owned v2 miss (remap did not run):

```text
cgroup_docker	no
mountinfo_id	c33988ec7651ebc867cb24755eaf637a6734088bc7eef59d5799293a9e5450f7
id_source	mountinfo
volume	/builds/project/src:/src
remapped	no
```

Owned mixed v1+v2: `cgroup_kind mixed`, `cgroup_docker_via cpuset`, `id_source both`, `volume none`, `remapped unsupported`, not `would`. Unseen podman overlay: `mountinfo_id aaaa…`, `remapped no`. `--cwd` omitted: argparse rc=2. Empty cwd / colon / tab: `dockpath:` rc=1. Both files empty: rc=1. Uppercase 64-hex mountinfo still folds (first destroyer item 1). `docker.service` / comment `docker` stay substring-not-inspect.

---

## Implementation

### 1. `remapped` is `cgroup_docker` restated; mountinfo never joins the `-v` path

Code:

```python
if docker:
    remapped = "unsupported"
    volume = "none"
    would_inspect = usable
else:
    remapped = "no"
    volume = format_volume(cwd, dest)
    would_inspect = False
```

`docker` comes only from `cgroup_docker_info`. `mids = mountinfo_ids(mountinfo)` is not in that branch.

Swap mountinfo under the same cgroup (14 cases, dest `/src` and `/app`): **bijection_failures 0**.

| case | cgroup_docker | remapped | volume | id_source |
| --- | --- | --- | --- | --- |
| v2 + owned mountinfo | no | no | `/builds/project/src:/src` | mountinfo |
| v2 + junk `x` | no | no | `/builds/project/src:/src` | none |
| v2 + other 64-hex | no | no | `/builds/project/src:/src` | mountinfo |
| mixed + owned | yes | unsupported | none | both |
| mixed + junk | yes | unsupported | none | cgroup |
| mixed + other 64-hex | yes | unsupported | none | mismatch |
| mixed + podman overlay | yes | unsupported | none | mismatch |

`id_source` moves. `remapped` and `volume` do not. The claimed third question (“which path became `-v`”) is `--cwd`/`--dest` echoed when a cgroup regex misses. It is not a join.

`--dest /app` on mixed: `dest /app`, `volume none`. Dest is a declared column the volume row does not use on the inspect branch.

### 2. Mixed v1+v2 is a label, not the remap predicate

Owned `cgroup_v1.excerpt` is mixed because of a trailing `0::/system.slice/containerd.service`. Strip that line (pure v1 docker cpuset + owned mountinfo):

```text
cgroup_kind	v1
cgroup_docker	yes
remapped	unsupported
volume	none
```

Same remap as mixed. Hybrid empty controllers `0::/` + `5:cpuset:/` is `cgroup_kind mixed` and `remapped no` / `volume /x:/src`. Mixed-ness does not decide anything load-bearing.

Docker only on memory (`5:memory:/docker/not-an-id` + `0::/`): `cgroup_kind mixed`, `cgroup_docker no`, `volume /x:/src`. Declared, and it is the same “not cpuset / not scope ⇒ echo cwd” rule.

Mixed cpuset `CID` plus v2 `docker-OTHER.scope`: `cgroup_docker_via scope` (first scope return) while `cgroup_id_kind cpuset` (cpuset wins the id). Two columns, two winners, one blob.

### 3. `--cwd` required; dest is specimen glue

```text
python3 "$CLI" "$FIX/cgroup_v2.excerpt" "$FIX/mountinfo_v2.hostname.excerpt"
# rc=2; "the following arguments are required: --cwd"
# --dest /app without --cwd: still rc=2
```

`--cwd` empty / tab / colon: rc=1, stdout empty. `--dest` empty / colon: rc=1. Relative `src` is accepted: `volume src:/src`. dest is never read from mountinfo `/etc/hostname`. Default `/src` is still the specimen convention the first destroyer already named.

### 4. `id_source mismatch` is string inequality of two greps

64-hex vs 64-hex different: `id_source mismatch`, `id_mismatch yes`, **and** `remapped unsupported` / `volume none` because cgroup was docker-shaped. Mismatch does not change the path.

12-hex prefix of the owned 64-hex vs the 64-hex (same Docker short id):

```text
cgroup_id	c33988ec7651
mountinfo_id	c33988ec7651ebc867cb24755eaf637a6734088bc7eef59d5799293a9e5450f7
id_source	mismatch
id_mismatch	yes
```

Reverse (64 vs 12) is the same mismatch. Docker treats the 12-char form as that container. This tool compares normalized strings.

cgroup `CID` plus mountinfo `CID` **and** another 64-hex: `mountinfo_id` is two tab fields, `id_source both`, `id_mismatch no`. Extra id is not a mismatch if any listed id equals cgroup. TSV column count breaks.

kubepods OTHER vs docker mountinfo CID (not docker-shaped): `id_source mismatch`, `remapped no`, `volume /app:/src`. Disagreeing ids still glue cwd to dest.

cri-containerd-OTHER.scope vs docker mountinfo CID: `cgroup_docker no`, `cgroup_id_kind scope`, `id_source mismatch`, `volume /x:/src`. CRI_SCOPE fills an id; it never sets docker.

### 5. Still grep-shaped. THIN_WRAPPER of two regexes

Demo.sh already names the nearest operation: `cat cgroup plus grep mountinfo`.

Owned v2:

```text
grep -a docker "$FIX/cgroup_v2.excerpt"   # rc=1, no bytes
grep -aoE '/var/lib/docker/containers/[0-9a-fA-F]{12,64}/' "$FIX/mountinfo_v2.hostname.excerpt"
# /var/lib/docker/containers/c33988ec…/
printf '%s:/src\n' "$CWD"
# /builds/project/src:/src
```

Two-regex reconstruction of the load-bearing columns (cgroup docker-shaped `cpuset:.*/docker/<hex>` or `docker-<hex>.scope`; mountinfo `/var/lib/docker/containers/<hex>/`; else `printf cwd:dest`):

```text
v2    MATCH remapped/volume/mid True
mixed MATCH remapped/volume/mid True
```

```text
# v2 two-regex
remapped	no
volume	/builds/project/src:/src
mountinfo_id	c33988ec7651ebc867cb24755eaf637a6734088bc7eef59d5799293a9e5450f7

# mixed two-regex
remapped	unsupported
volume	none
mountinfo_id	c33988ec7651ebc867cb24755eaf637a6734088bc7eef59d5799293a9e5450f7
```

Byte-identical to dockpath on those three fields. Podman overlay is a third regex on the unseen fixture; it still does not feed `remapped`. Full-column replay of `inspect()` is also byte-identical to owned v2 / mixed / podman stdout — it is the same predicates with labels (`cgroup_kind`, `cgroup_docker_via`, `would_inspect`, `dest`, `id_mismatch`). Constitution: a THIN_WRAPPER does not gain extra TSV rows to escape classification. First mutation added those rows.

`DOCKER_SCOPE` is still unanchored `docker-<hex>.scope`. First destroyer asked for a path token, not a substring.

```text
# 0::/system.slice/notdocker-<CID>.scope
cgroup_docker	yes
cgroup_docker_via	scope
cgroup_id	c33988ec…
remapped	unsupported
volume	none
would_inspect	yes
```

`mynotdocker-<CID>.scope` plus owned mountinfo: `id_source both`, `remapped unsupported`. Same class as the pre-mutate `notdocker.slice` blob hit.

13/32/63-hex `/docker/<hex>`: `cgroup_docker yes` (capture `{12,64}`) but `cgroup_id none` / `mountinfo_id none` (normalize is 12 or 64 only). `remapped unsupported`, `volume none`, no id. 11-hex: docker no, `volume /x:/src`. Overlay2 `<id>/diff` is not a containers path: `mountinfo_id none`. The same id in overlay `lowerdir=/var/lib/docker/containers/<id>/lower` **is** extracted (blob search, not a mount column).

### 6. kubepods

Typical cpuset `/kubepods/burstable/pod<uuid>/<CID>` plus kubelet `/pods/<uuid>/etc-hosts`:

```text
cgroup_docker	no
cgroup_id	c33988ec…
cgroup_id_kind	kubepods
mountinfo_id	none
id_source	cgroup
volume	/app:/src
remapped	no
would_inspect	no
```

Kubelet pod UUID is not a container id (declared). Volume is still cwd:dest glue. Same CID plus owned docker mountinfo: `id_source both`, **still** `remapped no` / `volume /app:/src` — mountinfo identity does not remap.

Put `/docker/` in the kubepods path (`…/podUUID/docker/<CID>`): `cgroup_docker yes` via cpuset, `cgroup_id_kind kubepods`, `remapped unsupported`. False docker-shaped.

cri-containerd scope + containerd task mountinfo: `cgroup_docker no`, `id_source both`, `volume /app:/src`. kubepods.slice with no hex basename, and a dashed pod UUID as basename: `cgroup_id none`, `volume /app:/src`.

### 7. Empty files

```text
both empty / both whitespace / /dev/null /dev/null
# rc=1  dockpath: empty cgroup and mountinfo

empty cgroup + junk mountinfo          volume /x:/src   remapped no   kind empty
v2 cgroup + empty mountinfo            volume /x:/src   remapped no
comment-only `# docker` + empty mount  substring yes, docker no, volume /x:/src
empty cgroup + owned mountinfo         id_source mountinfo, volume cwd:/src
```

One empty file is a finished volume whenever the other file is non-blank. The empty-both guard does not save the echo.

### 8. Binary garbage

```text
\x00\x01\xff\xfe garbage / \x00\xff\xfe     rc=0  remapped no  volume /x:/src
garbage\x00\x01docker\xff\xfe / x           substring yes, docker no, volume /x:/src
5:cpuset:/docker/\x80\xffid                 rc=1  dockpath: invalid utf-8 in cgroup id
NUL after a 64-hex cpuset id                docker no (regex wants / or $), volume /x:/src
junk around a valid containers/<CID>/ path  mountinfo_id CID, remapped no, volume /x:/src
```

Invalid utf-8 is a `dockpath:` line (mutation item 7). Binary that does not match the two regexes still prints a `-v`. That is the unmapped branch by construction.

---

## Primitive

Reality-stripped operation: search cgroup for `cpuset:/docker/<hex>` or `docker-<hex>.scope`; search mountinfo for four path regexes; if the first search hits, print `remapped unsupported` / `volume none`; else print `--cwd` and `--dest` glued with `:`. Name whether the two captures are equal.

Nearest ordinary workflow (owned packet, also demo.sh):

```text
cat cgroup | grep docker
grep docker/containers mountinfo
printf '%s:/src\n' "$cwd"
```

On specimen-065 that pair is: cgroup miss, mountinfo `c33988ec…`, volume `/builds/project/src:/src`. dockpath’s load-bearing claim is that naming `id_source` / `remapped` is a join those two already contain.

It is not. `remapped` is the first regex. `volume` is `printf` of argv when that regex misses. `id_source` is whether capture A equals capture B (`both` / `mismatch` / `cgroup` / `mountinfo` / `none`) — the same extinction class as envhop’s `dropped_invalid` = intersection. Mountinfo never votes on in-docker. The hook in `docker_detect_failing.py` also never reads mountinfo; the tool’s “which file decided” is always cgroup. `--cwd` is required because the path is not discovered.

Observable capability lost if dockpath vanishes: **none**. `grep -a docker` already says the v2 excerpt is a miss. `grep containers/<hex>` already names the id mountinfo still had. `printf '%s:/src\n'` already names the unmapped `-v`. Wrapping `docker inspect` to print a host Source would be a new harvest (live inspect, out of scope). MUTATE.md already set that ceiling: a later mutation that prints `remapped would` with `{cwd}:/src` should KILL. This embodiment is the other lie: `remapped unsupported` as a synonym of the cgroup regex, with mountinfo as a spectator column.

That is why this is KILL, not MUTATE. The *question* (cgroup v2 said not-in-docker, mountinfo still named the container, the hook passed in-container cwd as `-v`) is a real debugging object. This embodiment does not join it. It asks regex A then echoes argv, and regex B for a label. First destroyer MUTATE fixed `would` + glued `:/src` on the inspect branch. The remainder after that honesty pass is still two regexes. Extra columns (`cgroup_kind`, `cgroup_docker_via`, `dest`, `would_inspect`, `id_mismatch`) are the mutation’s dressing. Sibling `inprobe` already names `mismatch = not cgroup_docker and mountinfo still looks like a container` with caller-filled `path_used`. Do not mutate dockpath into that name to escape THIN_WRAPPER. Do not send it back to R1 to “make this more novel.”

Hardcoded ceiling:

- `remapped` ↔ `cgroup_docker`; `volume` ↔ not `cgroup_docker`
- mountinfo identity never changes `-v`
- 12-hex vs 64-hex prefix of the same id is `mismatch`
- extra mountinfo ids are extra TSV fields and can hide mismatch
- `notdocker-<id>.scope` is in-docker
- 13–63 hex is docker-shaped with no id
- kubepods basename is an id; kubelet `/pods/<uuid>/` is not; volume stays cwd:dest
- empty-one / binary-miss still finish a volume
- dest default `/src` is a declared convention
- excerpts only; no live `/proc`; no inspect

Honor KILL. Dreamer ancestry is not protection. First-destroyer MUTATE is not protection once the mutation has been shown to be labels on the same two greps.

Do not merge onto `main`. Do not run docker. Archive stays under `lineages/candidate-dockpath/`.

KILL
