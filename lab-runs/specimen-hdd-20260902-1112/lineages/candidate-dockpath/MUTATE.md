# MUTATE dockpath

CLI sha256 before: `ad249638464a917c7a3c95f1ca8fb9b63710afc3f19c6c7a295cd4fa110b5e5e` (3451 bytes, DESTROYER_dockpath.md)
CLI sha256 after:  `ec012938bdc9243b46a68e685a7b2bd0da807c166fdfc694534fde747bd0e661` (9702 bytes)

Date: 2026-09-02. Worktree: `/Users/annenpolka/.grok/worktrees/annenpolka-brrr/candidate-dockpath-dockpath` (branch `specimen-hdd/candidate-dockpath-dockpath`, commit `5d914c5`). Not merged to `main`. Binary name still `dockpath`. No docker.

From DESTROYER_dockpath.md: keep the object (for one cgroup excerpt and one mountinfo excerpt, which probe decided in-docker, which still named a container id, and which path was used as `-v` **when remap did not run**). Do not keep a calculator that glues `:/src` onto `--cwd` and labels the v1 branch `would`.

## What changed

1. **`remapped` is `no` | `unsupported`, never `would`.** Inspect is out of scope, so a docker-shaped cgroup with a usable id is `would_inspect yes` / `remapped unsupported` / `volume none`. The unmapped path is not printed as `-v`. Owned v1 (mixed) no longer claims `volume /builds/project/src:/src` on the inspect branch.
2. **`id_source` is which file held an id.** `cgroup_id` present ⇒ source is not `none`. `cgroup_id none` and a mountinfo hit ⇒ `mountinfo` even if the blob contains `docker`. Matching ids are `both`. Disagreeing ids are `id_source mismatch` plus `id_mismatch yes`. `user.slice` is not an id (`HEX64` / `HEX12`).
3. **In-docker is not `b"docker" in blob` as a remap predicate.** That heuristic is the named `cgroup_substring` bit. `cgroup_docker` is a docker-shaped **cpuset** path or `docker-<id>.scope`. Comments, `docker.service`, memory-controller `/docker/<id>` with cpuset `/`, and binary `docker` bytes are `cgroup_substring yes` / `cgroup_docker no` / `would_inspect no`.
4. **Owned `cgroup_v1.excerpt` is mixed.** Trailing `0::/system.slice/containerd.service` is named `cgroup_kind mixed`; the docker decision is `cgroup_docker_via cpuset`.
5. **Volume dest is declared.** `--dest` (default `/src`) is a column. Volume is `{cwd}:{dest}` only on `remapped no`. `--cwd` is required (no GitLab default). Empty / tab / newline / colon cwd is rc=1. Spaces are a quoted `-v` token.
6. **Ids mountinfo still named are findable.** 12-hex docker dirs, uppercase 64-hex, podman `storage/overlay-containers/<id>/userdata/hostname`, containerd `io.containerd.runtime.v2.task/.../<id>/`. Kubepods basename is `id_source cgroup`.
7. **Errors are `dockpath:` lines.** `UnicodeDecodeError` on a cpuset id is not a traceback. Empty both files is not a finished volume.

## Tests / demo

`python3 tests/test_dockpath.py` twice: 31 OK.

`./demo.sh` twice: byte-identical (`demo-1.log` / `demo-2.log`).

Owned v2 miss (remap did not run):

```
cgroup_substring	no
cgroup_kind	v2
cgroup_docker	no
cgroup_id	none
mountinfo_id	c33988ec7651ebc867cb24755eaf637a6734088bc7eef59d5799293a9e5450f7
id_source	mountinfo
cwd	/builds/project/src
dest	/src
volume	/builds/project/src:/src
would_inspect	no
remapped	no
```

Owned mixed v1+v2:

```
cgroup_kind	mixed
cgroup_docker_via	cpuset
id_source	both
volume	none
would_inspect	yes
remapped	unsupported
```

## Remaining failures (not faked)

- There is still no host Source. Research boundary (no live inspect) was correct. `remapped unsupported` is the honest ceiling; a later mutation that prints `remapped would` with `{cwd}:/src` should KILL.
- dest default remains `/src` as a declared specimen convention (`--dest` / `dest` column). It is not read from mountinfo or a command.
- 63-hex and 65-hex docker path components are still `mountinfo_id none` (ids are 12 or 64).
- kubelet `/pods/<uuid>/` is a pod, not a container id.
- cri-o / nerdctl / sysbox / other runtime layouts are not extracted unless they match the four mountinfo regexes.
- v1 docker only on an unrelated controller (memory) is substring, not in-docker. That is declared.
- Sibling harvest `inprobe` still exists as a caller-filled TSV join.
- Volume quoting is a token formatter, not `docker run`.
- Excerpts only; does not read live `/proc`.
