#!/usr/bin/env python3
"""Emit leftover-identity REAL_SOURCE_BACKED packets 142-144.

Packed (unique vs 001-141; 075 not overwritten; not bazel#29298):
1) job-0615 ansible-collections/community.general#9710 / PR 9760:
   leftover proxmox inventory cache file after meta:refresh_inventory
   because cache_key is inventory *file* identity (get_cache_key(path))
   and the plugin has only use_cache, not "refetch and persist".
2) job-0616 GoogleContainerTools/skaffold#9248/#9279 / PR 9278:
   leftover remote artifact identity after input/digest change because
   lookupRemote returned found whenever RemoteDigest(tag) succeeded,
   without comparing cached vs remote digest.
3) job-0617 gruntwork-io/terragrunt#764 / PR 774:
   leftover previous source files in .terragrunt-cache after source
   change; encodeSourceName omits ref from cache-path identity;
   CopyFolderContents had no manifest so stale.tf survived.

SKIP:
- job-0618 sccache leftover CPATH: mozilla/sccache#2798 still OPEN,
  PR 2799 OPEN. not inventing refs.
"""
from __future__ import annotations

import os

from compile_seed import write_seed
from emit_specimen import emit
from paths import SPECIMENS
from scheduler import complete, enqueue, now_jst, with_state
from update_index import main as update_index

START_N = 142
WORKER = "scout-coord-2020"
SKIP_JOBS = {
    "job-0618": (
        "skip sccache leftover object vs CPATH identity: sccache#2798 still "
        "OPEN, PR 2799 OPEN. not inventing refs; not 075/086"
    ),
}
PACK_JOBS = {
    "job-0615": None,  # filled after claim
    "job-0616": None,
    "job-0617": None,
}
NEXT_SCOUTS = [
    (
        "public OSS: pulumi leftover checkpoint vs stack identity not 081/118",
        "unique pulumi leftover if pinned",
    ),
    (
        "public OSS: packer leftover cache vs template identity not 001-144",
        "unique packer leftover if pinned",
    ),
    (
        "public OSS: opentofu leftover state serial vs identity not 081/118",
        "unique tofu leftover if pinned",
    ),
    (
        "public OSS: sccache leftover CPATH identity if #2798 merges",
        "unique sccache leftover if pinned",
    ),
]


def _claim_id(start: int = START_N) -> str:
    SPECIMENS.mkdir(parents=True, exist_ok=True)
    for n in range(start, 180):
        spec_id = f"specimen-{n:03d}"
        dest = SPECIMENS / spec_id
        try:
            os.mkdir(dest)
            return spec_id
        except FileExistsError:
            continue
    raise SystemExit("no free specimen id")


def packet_ansible(spec_id: str) -> dict:
    return dict(
        id=spec_id,
        manifest=f"""
id: {spec_id}
kind: REAL_SOURCE_BACKED
repository: ansible-collections/community.general
failing_ref: 94e1511005e621f56002f3b057d03b46f7639fb3
fixed_ref: d696bb7b8992bfc6535c5e51dd37a00b9b4e22df
source_issue: https://github.com/ansible-collections/community.general/issues/9710
source_pr: https://github.com/ansible-collections/community.general/pull/9760
mechanism_tags:
  - leftover-inventory-cache
  - cache-keyed-by-file-path
  - refresh-omits-cache-persist
ecosystem: ansible
reproduction_status: source-backed
safety_status: not-executed-on-host
packet_tokens_estimate: 7600
answer_key_sealed: true
parent_specimens: []
mutations: []
""",
        task="""# TASK

Ansible `community.general.proxmox` inventory with `cache: true` can keep the identity of a **previous inventory JSON** after the Proxmox world changed (new LXC) and `meta: refresh_inventory` should have been a different host set. The cache key is inventory **file** identity (`get_cache_key(path)`). The plugin has only `use_cache = cache and get_option('cache')`. On refresh, `cache=False` so it refetches in memory, but it does not persist a new cache file. The next playbook run hits leftover previous hosts.

On failing_ref `94e1511005e621f56002f3b057d03b46f7639fb3`:

```
self.cache_key = self.get_cache_key(path)
self.use_cache = cache and self.get_option('cache')
# _get_json:
if not self.use_cache or url not in self._cache.get(self.cache_key, {}):
    ...
    self._cache[self.cache_key][url] = data
return make_unsafe(self._cache[self.cache_key][url])
self._populate()
```

`get_cache_key(path)` is the inventory yaml path, not the remote host set. Nested writes into an existing `_cache[self.cache_key]` dict do not replace the cache file after refresh.

Public report (ansible-collections/community.general#9710). Create LXC; `meta: refresh_inventory`; in-memory inventory has the new host; cache file timestamp/content unchanged; second run without handler uses leftover previous inventory until the cache dir is deleted.

In-tree after the repair (not on failing_ref): `update_cache = not cache and get_option('cache')`; results collected in `_results`; `self._cache[self.cache_key] = self._results` written in one go.

Case A — second inventory load, Proxmox unchanged, cache on:
  cache identity is current
  not leftover-after-world-change

Case B — new LXC then leftover cache file (refresh did not persist):
  leftover: previous proxmox inventory JSON / missing new hostname
  cache keyed by inventory file path
  same `.cache` jsonfile

Case C — cache plugin off / cache dir deleted:
  fresh inventory identity
  not leftover previous hosts

Case D — refresh writes `_cache[cache_key] = results` (post-repair shape, not on failing_ref):
  cache miss / new host present on second run
  not leftover previous inventory

The developer wants to know which identity case B actually used for the inventory after the new LXC: leftover previous-file-keyed cache (refresh omitted persist), current Proxmox identity, or omitted (no cache).
""",
        observed="""# OBSERVED

Public ansible-collections/community.general#9710 (closed 2025-02-17). PR 9760 squash `d696bb7b8992bfc6535c5e51dd37a00b9b4e22df` (parent `94e1511005e621f56002f3b057d03b46f7639fb3`). Local ansible/proxmox was not performed on this lab host.

Issue body: proxmox inventory cache enabled; create LXC; `meta: refresh_inventory` updates in-memory inventory; cache file under `.cache` does not change; second play fails `hostvars['debian-t']` undefined until cache deleted.

On failing_ref, `_get_json` keys cache by inventory file path. Refresh sets `cache=False` so `use_cache` is false and the plugin refetches, but there is no separate persist path. Nested assignment into an existing cache dict leaves the previous jsonfile.

Not this packet: specimen-136 pants leftover process cache vs git hash. ansible-core#73699 leftover inventory vs `--flush-cache` (core manager, not proxmox file-keyed jsonfile).

This packet does not include a local clone. Do not execute untrusted checkouts on the host.
""",
        commands="""```
# not executed on this lab host
# failing_ref 94e1511005e621f56002f3b057d03b46f7639fb3
# plugins/inventory/proxmox.py parse / _get_json / get_cache_key(path)

# public shape:
# leftover inventory cache file after meta:refresh_inventory
# cache keyed by inventory yaml path; new LXC omitted on second run
# until cache dir deleted
```

Source-backed only. Do not execute untrusted checkouts on the host.
""",
        tree="""ansible-collections/community.general
  plugins/inventory/proxmox.py
""",
        source="""repository: ansible-collections/community.general
issue: https://github.com/ansible-collections/community.general/issues/9710
pr: https://github.com/ansible-collections/community.general/pull/9760
failing_ref (parent of squash on main): 94e1511005e621f56002f3b057d03b46f7639fb3
fixed_ref (refresh persists _results as cache file): d696bb7b8992bfc6535c5e51dd37a00b9b4e22df
merged_at: 2025-02-17T17:45:31Z
pr_author: iqt4
merged_by: felixfontein
changed_files: plugins/inventory/proxmox.py, changelogs/fragments/9760-proxmox-inventory.yml
pr_title: proxmox inventory: proposal for #9710 (caching)
scout_note: not 136 pants process cache. leftover inventory jsonfile keyed by inventory file path after world change. unique vs 001-141.
""",
        answer_key="""KNOWN FIX (sealed): ansible-collections/community.general PR 9760 squash d696bb7b8992bfc6535c5e51dd37a00b9b4e22df.

failing_ref is parent 94e1511005e621f56002f3b057d03b46f7639fb3.

Proxmox inventory cache was keyed by inventory file path and had only a use_cache knob. meta:refresh_inventory refetched in memory but leftover previous jsonfile stayed current for the next run.

PR repair: update_cache when cache=False but plugin cache enabled; assign self._cache[self.cache_key] = self._results in one go.

Do not show this to Dreamers, initial Red Pen, initial Grounders, or first-selection judges.
""",
        curation="""ACCEPT_R1

contrastiveness: high (unchanged world vs leftover cache after new LXC vs cache off vs persist-on-refresh)
reproducibility: source-backed issue+PR + pinned parent/squash; local run not claimed
information density: high
safety: public OSS, not executed on host
nontriviality: high — inventory file path and remote host-set are different identities; leftover jsonfile stayed current
ecosystem: ansible / proxmox inventory cache
mechanism_family: leftover-inventory-cache, cache-keyed-by-file-path, refresh-omits-cache-persist

Packet is the failing world only. Do not assume a root cause.
""",
        files={
            "proxmox_cache_failing.py": """# Reduced excerpt of proxmox inventory cache on failing_ref
# plugins/inventory/proxmox.py
# 94e1511005e621f56002f3b057d03b46f7639fb3
# cache_key is inventory file path. Nested write into existing dict.
# refresh (cache=False) refetches in memory; leftover jsonfile stays.

self.cache_key = self.get_cache_key(path)
self.use_cache = cache and self.get_option('cache')

def _get_json(self, url, ignore_errors=None):
    if not self.use_cache or url not in self._cache.get(self.cache_key, {}):
        if self.cache_key not in self._cache:
            self._cache[self.cache_key] = {'url': ''}
        data = []
        # ... HTTP GET into data ...
        self._cache[self.cache_key][url] = data
    return make_unsafe(self._cache[self.cache_key][url])

self._populate()
""",
            "leftover_identity_split.txt": """Registry / fixture:
  community.general.proxmox cache: true
  leftover inventory jsonfile after new LXC + refresh_inventory

Case A (second load, Proxmox unchanged):
  current cache identity
  not leftover-after-world-change

Case B (new LXC, leftover cache file):
  leftover: previous proxmox inventory JSON
  cache keyed by inventory file path
  new hostname omitted on second run

Case C (cache off / cache dir deleted):
  fresh inventory identity
  not leftover previous hosts

Case D (refresh writes _cache[key] = results):
  new host present on second run
  not leftover previous inventory

Not this packet:
  pants leftover vcs_version process cache (specimen-136)
  ansible-core leftover inventory vs --flush-cache (#73699)
""",
        },
    )


def packet_skaffold(spec_id: str) -> dict:
    return dict(
        id=spec_id,
        manifest=f"""
id: {spec_id}
kind: REAL_SOURCE_BACKED
repository: GoogleContainerTools/skaffold
failing_ref: 6ea9aeb818b8e371a4386bf044479f86a0a6e885
fixed_ref: 9ff4546df8c0d891fde32c24e0d0ef93a8c7404b
source_issue: https://github.com/GoogleContainerTools/skaffold/issues/9248
source_pr: https://github.com/GoogleContainerTools/skaffold/pull/9278
mechanism_tags:
  - leftover-remote-artifact
  - omitted-digest-compare
  - tag-reuse-cache-hit
ecosystem: skaffold
reproduction_status: source-backed
safety_status: not-executed-on-host
packet_tokens_estimate: 7600
answer_key_sealed: true
parent_specimens: []
mutations: []
""",
        task="""# TASK

Skaffold artifact cache `lookupRemote` can keep the identity of a **previous remote image** after build inputs changed and the digest should have been different. If `RemoteDigest(tag)` succeeds, the failing world returns `found` immediately. It overwrites `artifactCache[hash]` with that digest and does **not** compare the cached digest to the remote one. Reusing the same tag (git sha tag, `:tag1`) after a Dockerfile/dep change still prints `Found Remotely` and skips the rebuild.

On failing_ref `6ea9aeb818b8e371a4386bf044479f86a0a6e885`:

```
func (c *cache) lookupRemote(ctx context.Context, hash, tag string, platforms []specs.Platform) cacheDetails {
	var cacheHit bool
	entry := ImageDetails{}
	if digest, err := docker.RemoteDigest(tag, c.cfg, nil); err == nil {
		log.Entry(ctx).Debugf("Found %s remote", tag)
		entry.Digest = digest
		c.artifactCache[hash] = entry
		return found{hash: hash}
	}
	// ... cacheHit path compares tag@digest only after RemoteDigest(tag) failed ...
	return needsBuilding{hash: hash}
}
```

`hash` is the current input digest. `tag` is the image tag. Remote tag lookup is not the input identity.

Public reports: GoogleContainerTools/skaffold#9248 (lookupRemote always found when the same tag is reused) and #9279 (skaffold build retrieves the same image from cache even when input files change; `Found Remotely` after Dockerfile edit). `--cache-artifacts=false` updates hashes.

In-tree after the repair (not on failing_ref): `found` only when cacheHit **and** remoteDigest == cachedEntry.Digest.

Case A — second build, same inputs, same remote digest:
  cache identity is current
  not leftover-after-input-change

Case B — inputs flipped, same tag, leftover remote lookup:
  leftover: previous image digest under that tag
  digest compare omitted
  `Found Remotely` / no rebuild

Case C — `--cache-artifacts=false`:
  fresh build identity
  not leftover previous digest

Case D — found only if cacheHit and digests equal (post-repair shape, not on failing_ref):
  cache miss / rebuild after input change
  not leftover previous remote image

The developer wants to know which identity case B actually used for the artifact after the input change: leftover previous-tag remote digest (digest compare omitted), current input hash, or omitted (no cache).
""",
        observed="""# OBSERVED

Public GoogleContainerTools/skaffold#9248 (closed 2024-01-31) and #9279 (closed as the same lookupRemote leftover). PR 9278 squash `9ff4546df8c0d891fde32c24e0d0ef93a8c7404b` (parent `6ea9aeb818b8e371a4386bf044479f86a0a6e885`). Local skaffold was not performed on this lab host.

Issue #9279: bazel/docker artifacts; input files change; `skaffold build` still returns the previous image; `Found Remotely` after Dockerfile `RUN ls`; `--cache-artifacts=false` updates hashes.

On failing_ref, lookupRemote treats a live remote tag as a cache hit for the current input hash without comparing digests.

Not this packet: specimen-097 buildkit leftover git-dir cache key omitting ref. specimen-136 pants leftover process cache vs git hash.

This packet does not include a local clone. Do not execute untrusted checkouts on the host.
""",
        commands="""```
# not executed on this lab host
# failing_ref 6ea9aeb818b8e371a4386bf044479f86a0a6e885
# pkg/skaffold/build/cache/lookup.go lookupRemote

# public shape:
# leftover Found Remotely after Dockerfile/input change
# RemoteDigest(tag) success returns found; digest compare omitted
# --cache-artifacts=false yields a new hash
```

Source-backed only. Do not execute untrusted checkouts on the host.
""",
        tree="""GoogleContainerTools/skaffold
  pkg/skaffold/build/cache/lookup.go
  pkg/skaffold/build/cache/cache.go
""",
        source="""repository: GoogleContainerTools/skaffold
issue: https://github.com/GoogleContainerTools/skaffold/issues/9248
related_issue: https://github.com/GoogleContainerTools/skaffold/issues/9279
pr: https://github.com/GoogleContainerTools/skaffold/pull/9278
failing_ref (parent of squash on main): 6ea9aeb818b8e371a4386bf044479f86a0a6e885
fixed_ref (lookupRemote compares remote vs cached digest): 9ff4546df8c0d891fde32c24e0d0ef93a8c7404b
merged_at: 2024-01-31T13:29:23Z
pr_author: idsulik
merged_by: ericzzzzzzz
changed_files: pkg/skaffold/build/cache/lookup.go, cache.go, retrieve_test.go, pkg/skaffold/runner/new.go
pr_title: fix(lookupRemote): fixed lookup.go lookupRemote to compare remote and cached digests
scout_note: not 097 buildkit keep-git-dir omitted-ref. leftover remote tag identity after input digest change. unique vs 001-141.
""",
        answer_key="""KNOWN FIX (sealed): GoogleContainerTools/skaffold PR 9278 squash 9ff4546df8c0d891fde32c24e0d0ef93a8c7404b.

failing_ref is parent 6ea9aeb818b8e371a4386bf044479f86a0a6e885.

lookupRemote returned found whenever RemoteDigest(tag) succeeded, so leftover previous image identity after the same tag was reused with a different input digest.

PR repair: return found only when cacheHit and remoteDigest == cachedEntry.Digest.

Do not show this to Dreamers, initial Red Pen, initial Grounders, or first-selection judges.
""",
        curation="""ACCEPT_R1

contrastiveness: high (unchanged inputs vs leftover Found Remotely after edit vs cache off vs digest-equal found)
reproducibility: source-backed issue+PR + pinned parent/squash; local run not claimed
information density: high
safety: public OSS, not executed on host
nontriviality: high — input hash and remote tag are different identities; leftover tag digest stayed current
ecosystem: skaffold / artifact cache
mechanism_family: leftover-remote-artifact, omitted-digest-compare, tag-reuse-cache-hit

Packet is the failing world only. Do not assume a root cause.
""",
        files={
            "lookup_remote_failing.go": """// Reduced excerpt of lookupRemote on failing_ref
// pkg/skaffold/build/cache/lookup.go
// 6ea9aeb818b8e371a4386bf044479f86a0a6e885
// RemoteDigest(tag) success => found. digest compare omitted.

func (c *cache) lookupRemote(ctx context.Context, hash, tag string, platforms []specs.Platform) cacheDetails {
	entry := ImageDetails{}
	if digest, err := docker.RemoteDigest(tag, c.cfg, nil); err == nil {
		log.Entry(ctx).Debugf("Found %s remote", tag)
		entry.Digest = digest
		c.artifactCache[hash] = entry
		return found{hash: hash}
	}
	return needsBuilding{hash: hash}
}
""",
            "leftover_identity_split.txt": """Registry / fixture:
  skaffold artifact cache / lookupRemote
  leftover Found Remotely after input change

Case A (second build, same inputs, same digest):
  current cache identity
  not leftover-after-input-change

Case B (Dockerfile/deps flipped, same tag, leftover remote):
  leftover: previous image digest under that tag
  digest compare omitted
  Found Remotely

Case C (--cache-artifacts=false):
  fresh build identity
  not leftover previous digest

Case D (found only if cacheHit and digests equal):
  rebuild after input change
  not leftover previous remote image

Not this packet:
  buildkit leftover git-dir cache key omitting ref (specimen-097)
  pants leftover vcs_version process cache (specimen-136)
""",
        },
    )


def packet_terragrunt(spec_id: str) -> dict:
    return dict(
        id=spec_id,
        manifest=f"""
id: {spec_id}
kind: REAL_SOURCE_BACKED
repository: gruntwork-io/terragrunt
failing_ref: 17004093f058bfe45c59ab6e34fe3c46da86dbf8
fixed_ref: 85f63b2bbde2fc8d9b207799e6891c171e6527ee
source_issue: https://github.com/gruntwork-io/terragrunt/issues/764
source_pr: https://github.com/gruntwork-io/terragrunt/pull/774
mechanism_tags:
  - leftover-source-copy
  - omitted-ref-from-cache-path
  - no-copy-manifest
ecosystem: terragrunt
reproduction_status: source-backed
safety_status: not-executed-on-host
packet_tokens_estimate: 7800
answer_key_sealed: true
parent_specimens: []
mutations: []
""",
        task="""# TASK

Terragrunt `.terragrunt-cache` can keep the identity of a **previous source tree** after `terraform { source = "...?ref=..." }` changed. Two leftovers share one download folder:

1. `encodeSourceName` hashes the source URL **without the query string**. Different `ref=` values reuse `QM1-63WWHsRnztH6ooxLgsdRMGg/tieM-yGmC7c1rfHpXzt3T9uRVsA`. Version lives only in `.terragrunt-source-version`.
2. `CopyFolderContents` copies into that folder with **no manifest**. After source update, leftover `stale.tf` from the previous tree stays. `cleanupDownloadDir` then deletes leftover dest contents including `.git`, so go-getter `git pull` fails (`pathspec 'master' did not match`).

On failing_ref `17004093f058bfe45c59ab6e34fe3c46da86dbf8`:

```
func encodeSourceName(sourceUrl *url.URL) (string, error) {
	sourceUrlNoQuery, err := parseSourceUrl(sourceUrl.String())
	sourceUrlNoQuery.RawQuery = ""
	return util.EncodeBase64Sha1(sourceUrlNoQuery.String()), nil
}
func CopyFolderContents(source string, destination string) error {
	return CopyFolderContentsWithFilter(source, destination, func(path string) bool {
		return !PathContainsHiddenFileOrFolder(path)
	})
}
```

Public report (gruntwork-io/terragrunt#764). Change `?ref=` from `6e30e8a` to `c7f82af`; same cache path; leftover dest; delete `.terragrunt-cache` to get the new commit. In-tree test after the repair: `test-stale-file-exists` then `test-stale-file-doesnt-exist-after-source-update`.

In-tree after the repair (not on failing_ref): `.terragrunt-module-manifest` / `.terragrunt-source-manifest`; `CopyFolderContents(..., manifestFile)` Clean() previous copies; `cleanupDownloadDir` removed.

Case A — second run, same `source` / same files:
  cache identity is current
  not leftover-after-source-change

Case B — `ref=` or local files flipped, leftover dest:
  leftover: previous `stale.tf` / previous clone path
  ref omitted from cache-path identity
  same encoded folder

Case C — `rm -rf .terragrunt-cache` / `--terragrunt-source-update`:
  fresh source identity
  not leftover previous tree

Case D — copy manifest Clean() before recopy (post-repair shape, not on failing_ref):
  stale.tf gone after source update
  not leftover previous files

The developer wants to know which identity case B actually used for the working dir after the source change: leftover previous-copy (no manifest; ref omitted from path), current source identity, or omitted (no cache).
""",
        observed="""# OBSERVED

Public gruntwork-io/terragrunt#764 (closed 2019-07-31). PR 774 merge `85f63b2bbde2fc8d9b207799e6891c171e6527ee` (first parent `17004093f058bfe45c59ab6e34fe3c46da86dbf8`). Local terragrunt was not performed on this lab host.

Issue body: changing `...?ref=` keeps the same `.terragrunt-cache` hash subdirs; leftover dest; `git pull` fails after cleanup deleted `.git`; deleting the cache folder pulls the new commit.

On failing_ref, encodeSourceName omits query/ref from the cache path. CopyFolderContents has no list of previously copied files, so leftover `stale.tf` survives a source update. PR 774 tests `test-stale-file-doesnt-exist-after-source-update`.

Not this packet: specimen-118 terraform leftover identity omitted from apply state. terragrunt#6468 leftover deleted git-module files still OPEN (not this merged pair). PR 4781 catalog `ref != ""` one-line flip is THIN_WRAPPER, not packed.

This packet does not include a local clone. Do not execute untrusted checkouts on the host.
""",
        commands="""```
# not executed on this lab host
# failing_ref 17004093f058bfe45c59ab6e34fe3c46da86dbf8
# cli/download_source.go encodeSourceName / CopyFolderContents / cleanupDownloadDir

# public shape:
# leftover .terragrunt-cache path after ?ref= change
# encodeSourceName omits query; leftover stale.tf; leftover dest without .git
# rm -rf .terragrunt-cache yields the new source
```

Source-backed only. Do not execute untrusted checkouts on the host.
""",
        tree="""gruntwork-io/terragrunt
  cli/download_source.go
  util/file.go
""",
        source="""repository: gruntwork-io/terragrunt
issue: https://github.com/gruntwork-io/terragrunt/issues/764
pr: https://github.com/gruntwork-io/terragrunt/pull/774
failing_ref (first parent of merge on master): 17004093f058bfe45c59ab6e34fe3c46da86dbf8
fixed_ref (copy manifest Clean previous files): 85f63b2bbde2fc8d9b207799e6891c171e6527ee
merged_at: 2019-07-31T12:21:17Z
pr_author: ekini
merged_by: brikis98
changed_files: cli/download_source.go, util/file.go, cli/file_copy_getter.go, tests/fixtures
pr_title: For local file copy create a manifest with a list of files.
scout_note: not 118 terraform omitted apply identity. leftover previous source copy after ref/files change. unique vs 001-141. #6468 still OPEN not used.
""",
        answer_key="""KNOWN FIX (sealed): gruntwork-io/terragrunt PR 774 merge 85f63b2bbde2fc8d9b207799e6891c171e6527ee.

failing_ref is first parent 17004093f058bfe45c59ab6e34fe3c46da86dbf8.

.encodeSourceName omitted ref from cache-path identity so leftover dest was reused. CopyFolderContents had no manifest, so leftover previous files (stale.tf) stayed after source change. cleanupDownloadDir wiped .git in that leftover dest.

PR repair: fileManifest Clean() of previously copied paths; CopyFolderContents takes manifestFile; cleanupDownloadDir removed.

Do not show this to Dreamers, initial Red Pen, initial Grounders, or first-selection judges.
""",
        curation="""ACCEPT_R1

contrastiveness: high (unchanged source vs leftover dest after ref/files change vs cache wipe vs copy-manifest Clean)
reproducibility: source-backed issue+PR + pinned parent/merge; local run not claimed
information density: high
safety: public OSS, not executed on host
nontriviality: high — cache-path identity and source version/query are different; leftover previous copy stayed current
ecosystem: terragrunt / source cache
mechanism_family: leftover-source-copy, omitted-ref-from-cache-path, no-copy-manifest

Packet is the failing world only. Do not assume a root cause.
""",
        files={
            "encode_source_failing.go": """// Reduced excerpt of cache-path identity + copy on failing_ref
// cli/download_source.go / util/file.go
// 17004093f058bfe45c59ab6e34fe3c46da86dbf8
// encodeSourceName omits query/ref. CopyFolderContents has no manifest.

func encodeSourceName(sourceUrl *url.URL) (string, error) {
	sourceUrlNoQuery, err := parseSourceUrl(sourceUrl.String())
	sourceUrlNoQuery.RawQuery = ""
	return util.EncodeBase64Sha1(sourceUrlNoQuery.String()), nil
}

func CopyFolderContents(source string, destination string) error {
	return CopyFolderContentsWithFilter(source, destination, func(path string) bool {
		return !PathContainsHiddenFileOrFolder(path)
	})
}
// leftover previous files in destination after source change
""",
            "leftover_identity_split.txt": """Registry / fixture:
  .terragrunt-cache download dir
  leftover previous source after ?ref= / file change

Case A (second run, same source):
  current cache identity
  not leftover-after-source-change

Case B (ref= or files flipped, leftover dest):
  leftover: previous stale.tf / previous clone path
  ref omitted from encodeSourceName
  same encoded folder

Case C (rm -rf .terragrunt-cache / --terragrunt-source-update):
  fresh source identity
  not leftover previous tree

Case D (copy manifest Clean before recopy):
  stale.tf gone after source update
  not leftover previous files

Not this packet:
  terraform leftover identity omitted from apply state (specimen-118)
  terragrunt#6468 leftover deleted git-module files (OPEN)
""",
        },
    )


PACKETS = [
    ("job-0615", "hdd-pveinv", packet_ansible,
     "ansible leftover proxmox inventory jsonfile keyed by file path; not 136"),
    ("job-0616", "hdd-skafdig", packet_skaffold,
     "skaffold leftover remote tag identity omits digest compare; not 097"),
    ("job-0617", "hdd-tgcopy", packet_terragrunt,
     "terragrunt leftover source copy omits ref from cache path; not 118"),
]


def _claim_job(state, job_id: str, worker: str) -> None:
    job = next((j for j in state.get("ready_jobs") or [] if j.get("id") == job_id), None)
    if job is None:
        return
    if job.get("status") == "READY":
        job["status"] = "CLAIMED"
        job["claimed_at"] = now_jst()
        job["worker"] = worker
        workers = state.setdefault("workers", [])
        rec = next((w for w in workers if w.get("id") == worker), None)
        if rec is None:
            workers.append({"id": worker, "status": "active", "job": job_id})
        else:
            rec["status"] = "active"
            rec["job"] = job_id
    elif job.get("status") == "CLAIMED":
        old = job.get("worker")
        if old not in {None, worker} and not str(old).startswith("scout-coord-"):
            raise SystemExit(f"{job_id} status=CLAIMED worker={old}")
        job["worker"] = worker
    elif job.get("status") in {"DONE", "SKIP"}:
        pass
    else:
        raise SystemExit(f"{job_id} status={job.get('status')}")


def _claim_all() -> None:
    def fn(state):
        for jid in list(PACK_JOBS) + list(SKIP_JOBS):
            _claim_job(state, jid, WORKER)
        return True

    with_state(fn)


def _complete_and_enqueue(packed: list[tuple[str, str, str, str]]) -> str:
    note = {"reason": ""}

    def fn(state):
        for jid, artifact in SKIP_JOBS.items():
            job = next((j for j in state.get("ready_jobs") or [] if j.get("id") == jid), None)
            if job is None:
                continue
            if job.get("status") in {"READY", "CLAIMED"}:
                if job.get("status") == "READY":
                    _claim_job(state, jid, WORKER)
                old = job.get("worker")
                if old in {None, WORKER} or str(old).startswith("scout-coord-"):
                    complete(state, jid, result="skip", artifact=artifact)
        ids = {s.get("id") for s in state.get("specimens") or []}
        reasons = []
        for job_id, spec_id, trial, priority_reason in packed:
            if spec_id not in ids:
                state.setdefault("specimens", []).append({"id": spec_id})
                ids.add(spec_id)
            job = next((j for j in state.get("ready_jobs") or [] if j.get("id") == job_id), None)
            if job is not None and job.get("status") in {"READY", "CLAIMED"}:
                if job.get("status") == "READY":
                    _claim_job(state, job_id, WORKER)
                complete(state, job_id, result="ok", artifact=f"specimens/{spec_id}")
            already = any(
                j.get("queue") == "READY_R1_DREAM"
                and j.get("specimen") == spec_id
                and j.get("status") in {"READY", "CLAIMED"}
                for j in state.get("ready_jobs") or []
            )
            if not already:
                enqueue(
                    state,
                    "READY_R1_DREAM",
                    input_ref=f"seeds/{spec_id}.md trial={trial}",
                    expected_output="0001-dreamer.md",
                    kill_condition="15m",
                    estimated_cost="r1",
                    priority_reason=priority_reason,
                    specimen=spec_id,
                    lineage=trial,
                    phase="cambrian",
                    extra={"trial": trial},
                )
            reasons.append(f"READY_R1_DREAM trial={trial} specimen={spec_id}")
        existing_inputs = {
            j.get("input")
            for j in state.get("ready_jobs") or []
            if j.get("queue") == "READY_SPECIMEN_SCOUT"
        }
        for input_ref, reason in NEXT_SCOUTS:
            if input_ref in existing_inputs:
                continue
            enqueue(
                state,
                "READY_SPECIMEN_SCOUT",
                input_ref=input_ref,
                expected_output="specimens/specimen-NNN leftover-identity packet",
                kill_condition="25m no unique leftover-identity pair; skip bazel#29298; never overwrite 075",
                estimated_cost="low",
                priority_reason=reason,
                phase="cambrian",
            )
        note["reason"] = "; ".join(reasons)
        return True

    with_state(fn)
    return note["reason"]


def main() -> None:
    _claim_all()
    claimed: list[str] = []
    packed: list[tuple[str, str, str, str]] = []
    try:
        for job_id, trial, builder, priority_reason in PACKETS:
            spec_id = _claim_id()
            claimed.append(spec_id)
            emit(builder(spec_id))
            write_seed(SPECIMENS / spec_id)
            packed.append((job_id, spec_id, trial, priority_reason))
        update_index()
        launch_note = _complete_and_enqueue(packed)
        for job_id, spec_id, trial, _ in packed:
            print(SPECIMENS / spec_id)
            print(f"seed=seeds/{spec_id}.md trial={trial} job={job_id}")
        print(launch_note)
        print(f"ids={[p[1] for p in packed]} worker={WORKER} at={now_jst()}")
    except Exception:
        for spec_id in claimed:
            dest = SPECIMENS / spec_id
            if dest.is_dir() and not (dest / "manifest.yaml").exists():
                try:
                    dest.rmdir()
                except OSError:
                    pass
        raise


if __name__ == "__main__":
    main()
