# DESTROYER narleftover

Date: 2026-09-02 15:59 JST
RUN_ID: specimen-hdd-20260902-1112
Job: job-0413 (worker destroyer-narleftover)

Target (harvested): `/Users/annenpolka/ghq/github.com/annenpolka/brrr/lab-runs/specimen-hdd-20260902-1112/lineages/candidate-narleftover/narleftover`

sha256 `8b42c8af7d14ba63d12d787b34be84396f330b7da5b6b4e0508206aadd04b4d1` (2629 bytes, 88 lines). No `narleftover` worktree under `lab-runs/.../worktrees` or `~/.grok/worktrees`. Parent `main` is `432f954`; `git ls-tree main -- narleftover` empty; archive untracked (`?? lineages/candidate-narleftover/`) and was not merged. Host Python 3.14.5. `command -v nix` **ABSENT**; nix **was not executed**. No sqlite. No flake.lock parse.

Origin claim (`CANDIDATE.md` / harvest `hdd-flakenar` / specimen-092): name leftover fetcher-cache NAR for a rev fingerprint versus the lock narHash after correction. rc=1 when `leftover_stale_nar`. Kind: USEFUL_COMPOSITION. Red Pen `hdd-flakenar-0001.json`: NEXT_ACTION=HARVEST_NOW; `observable_delta` already **`leftover_stale_nar = cache_nar != lock_nar for same rev`**; nearest existing operation already **`diff flake.lock narHash vs sqlite cache value for that rev`**. Rejected: invented nix eval/sqlite transcripts. Constraint: owned labeled rev/narHash records. No nix daemon. Distinct from Honor-KILLed lockident (caller `--identity` vs `sha256[:12]`).

Happy path is real. Unit tests 3/3 pass (`python3 -m unittest discover -s tests -v` → `Ran 3 tests in 0.076s` `OK`, rc=0). `demo.sh` twice, live logs byte-identical to each other and to archived `demo-1.log` / `demo-2.log`. That is not enough.

This candidate is a **THIN_WRAPPER of two-string inequality**. `inspect()` is `leftover = cache != lock`. It never opens `fetcher-cache-v4.sqlite`, never parses `flake.lock`, never computes a NAR, never joins two events, never checks that `rev` is the cache fingerprint. Host replica of that inequality plus the four TSV rows is **byte-identical** to CLI stdout+rc on both owned fixtures (`cmp` rc=0, 191 / 190 bytes) and on **15/15** host records plus a 10k-char pair (20050-byte stdout). `awk` of `lock_nar` vs `cache_nar` matches `leftover_stale_nar` on both owned files. `test "$cache" != "$lock"` matches both. `demo.sh` already prints `leftover is cache_nar != lock_nar for the same rev fingerprint`. Decision: **KILL**.

CLI used below:

```text
CLI=/Users/annenpolka/ghq/github.com/annenpolka/brrr/lab-runs/specimen-hdd-20260902-1112/lineages/candidate-narleftover/narleftover
FIX=/Users/annenpolka/ghq/github.com/annenpolka/brrr/lab-runs/specimen-hdd-20260902-1112/lineages/candidate-narleftover/fixtures
S092=/Users/annenpolka/ghq/github.com/annenpolka/brrr/lab-runs/specimen-hdd-20260902-1112/specimens/specimen-092
```

Host-executed against the archive only. Do not merge onto `main`. Do not run nix. Do not wrap sqlite / `nix hash path` / a fetcher-cache reader to escape THIN_WRAPPER. Job kill_condition: `thin two-hash inequality`. First HARVEST is not protection.

Scratch: `destroyers/_narleftover_scratch/` (`attack.py` plus host records). Isolation: RUN_DIR writes only.

---

## What still works

Owned poison (case C: lock H_nar2, cache still H_nar1) and owned fresh (case D: same SRI twice), **when the caller already labeled both NAR strings**.

```bash
python3 "$CLI" "$FIX/092-poison.rec"; echo rc=$?
python3 "$CLI" "$FIX/092-fresh.rec"; echo rc=$?
```

```text
rev	5297592395d1dbd46e88247e459896838c854340
lock_nar	sha256-YR+cemfm4AMEJcUEr/tm0cis3rWKQ0dPFbjwhEVrV94=
cache_nar	sha256-4cKMeE/8GptnxWnB6LliJy3gCvjVI34TXTwQHEsHcUA=
leftover_stale_nar	yes
rc=1

rev	5297592395d1dbd46e88247e459896838c854340
lock_nar	sha256-YR+cemfm4AMEJcUEr/tm0cis3rWKQ0dPFbjwhEVrV94=
cache_nar	sha256-YR+cemfm4AMEJcUEr/tm0cis3rWKQ0dPFbjwhEVrV94=
leftover_stale_nar	no
rc=0
```

191 / 190 bytes. Stderr empty. Two hashes only (`rev	-`, `lock_nar	A`, `cache_nar	B`): leftover yes, rc=1. Unicode hashes, inner tab in the cache value, symlink, process substitution, filename with a space, CRLF, stdin `-`, `/dev/stdin`, pipe: leftover is still `cache != lock`. Missing path / directory / empty file / comments-only / `/dev/null` / unknown field / spaces instead of tabs / BOM / invalid UTF-8 / empty `cache_nar<TAB>`: `narleftover: …` rc=1. No args / extra positional: argparse rc=2. `-h` rc=0.

That is the whole useful surface. It is also what `test "$cache_nar" != "$lock_nar"` already does. Attacks below break the “which NAR the substitution cache keyed for that rev” claim, or show the primitive cannot grow.

---

## Implementation

`inspect()` in full:

```python
def inspect(fields: dict[str, str]) -> dict:
    lock = fields["lock_nar"]
    cache = fields["cache_nar"]
    leftover = cache != lock
    return {
        "rev": fields["rev"],
        "lock_nar": lock,
        "cache_nar": cache,
        "leftover_stale_nar": leftover,
    }
```

`inspect.__code__.co_names` is `()`. `parse_record.co_names` is `('enumerate', 'splitlines', 'strip', 'startswith', 'ValueError', 'split', 'KNOWN')`. Source contains no `hashlib`, no `sha256`, no `sqlite`, no `flake`, no `nix`. `KNOWN` is `('rev', 'lock_nar', 'cache_nar')`. The load-bearing operator is Python `!=` on two stripped strings the caller wrote.

### 1. THIN_WRAPPER of two caller-labeled hashes

Independent reconstruction (no import of `inspect`): parse the three TSV keys; `leftover = cache_nar != lock_nar`; print the four rows. Byte-identical to CLI stdout+rc on owned poison (`cmp` identical, 191 bytes), owned fresh (190 bytes), 15/15 host sweep records, and a 10000-char pair.

Nearest ordinary workflow, host-executed:

```bash
awk 'BEGIN{FS="\t"} $1=="lock_nar"{l=$2} $1=="cache_nar"{c=$2} END{print (c!=l)?"yes":"no"}' \
  "$FIX/092-poison.rec" "$FIX/092-fresh.rec"
```

```text
yes
no
```

Shell `test`:

```bash
# poison
test "sha256-4cKMeE/8GptnxWnB6LliJy3gCvjVI34TXTwQHEsHcUA=" \
  != "sha256-YR+cemfm4AMEJcUEr/tm0cis3rWKQ0dPFbjwhEVrV94=" && echo yes
# fresh
test "sha256-YR+cemfm4AMEJcUEr/tm0cis3rWKQ0dPFbjwhEVrV94=" \
  != "sha256-YR+cemfm4AMEJcUEr/tm0cis3rWKQ0dPFbjwhEVrV94=" && echo yes || echo no
```

```text
yes
no
```

IDENTICAL to `leftover_stale_nar`. The harvest records already *are* the input. The CLI reprints the two SRI strings the caller wrote, compares them, and exits 1. Concatenating the two owned reports does not discover a fetcher-cache mapping. It reprints H_nar2 vs H_nar1.

Red Pen already named this inequality as the delta and named `diff flake.lock narHash vs sqlite cache value` as the analog. Grounding on “owned labeled records” turned the analog into the product: the operator still supplies both sides.

Constitution: a THIN_WRAPPER does not gain extra TSV rows (`rev`) to escape classification. `rev` is echo. It does not vote. Worker rule: do not send THIN_WRAPPER back to R1 with “make this more novel.” First HARVEST is not protection. Same extinction class as Honor-KILLed unusedfp (two hashes plus set difference; this is thinner: no hash) and Honor-KILLed lockident (caller hex vs `sha256[:12]`; this never hashes). Distinct object: two NAR SRI strings, not blob-digest membership.

### 2. Spectator `rev`: “same rev fingerprint” is not checked

Poison hashes with a different 40-hex rev (`DEADBEEF…` / `1111…` / `-`):

```text
rev	DEADBEEFDEADBEEFDEADBEEFDEADBEEFDEADBEEF
lock_nar	sha256-YR+cemfm4AMEJcUEr/tm0cis3rWKQ0dPFbjwhEVrV94=
cache_nar	sha256-4cKMeE/8GptnxWnB6LliJy3gCvjVI34TXTwQHEsHcUA=
leftover_stale_nar	yes
rc=1
```

Leftover column and rc are byte-identical to owned poison except the echoed `rev` line (`stdout_differs_only_rev True`). Owned rev with *matching* hashes is leftover no, rc=0 — that is case D’s stickers, not a fresh sqlite. The CLI cannot ask whether the cache key was R2. It never sees a key.

A record that claims case C (`rev` R2) while the two NAR fields are equal reports leftover no. A record that claims case D while the two NAR fields differ reports leftover yes. The stickers decide.

### 3. Encoding is string inequality, not a NAR identity

Same live hash as SRI vs decoded hex `611f9c7a67e6e0030425c504affb66d1c8acdeb58a43474f15b8f084456b57de`: leftover **yes**, rc=1. Same SRI vs the base64 without `sha256-` prefix: leftover **yes**, rc=1. Quoted SRI vs bare SRI: leftover yes. `SHA256-…` vs `sha256-…`: leftover yes. Leading space on `lock_nar` is `rest.strip()`’d, so padded live SRI vs live SRI is leftover **no** — strip, not NAR semantics.

Last-wins: poison `cache_nar` then a second `cache_nar` equal to lock → leftover no, rc=0. Duplicate keys are a last assignment, not two cache stores.

Empty `cache_nar	-` vs live lock: leftover yes (the token `-` is a string). Empty `cache_nar<TAB>` after strip has no tab → `expected key<TAB>value`, rc=1, no TSV. That is parse, not “cache miss.”

The two owned SRIs decode to different sha256s (`611f9c7a…` vs `e1c28c78…`). The CLI never decodes them. `base64` / `openssl dgst` are not in the product.

### 4. Origin packet cannot enter

```bash
python3 "$CLI" "$S092/files/lock_identity_split.txt"; echo rc=$?
python3 "$CLI" "$S092/files/github_fingerprint_failing.cc"; echo rc=$?
python3 "$CLI" "$S092/files/fetchers_fastpath_failing.cc"; echo rc=$?
```

```text
narleftover: …/lock_identity_split.txt:1: expected key<TAB>value
rc=1
narleftover: …/github_fingerprint_failing.cc:1: expected key<TAB>value
rc=1
narleftover: …/fetchers_fastpath_failing.cc:1: expected key<TAB>value
rc=1
```

`compute_store_path_failing.cc`, `TASK.md`, and a flake.lock JSON fragment (`{"nodes":{"dep":{"locked":{"rev":…,"narHash":…}}}}`) are the same parse error. The failing `getFingerprint` / substitution-upsert excerpts are not records. The owned fixtures are already the harvest sentence, typed as TSV. Dreamer nix/sqlite transcripts were rejected; this is that inspect, reduced to `!=`.

### 5. Parse / IO / stdin

| input | rc | note |
| --- | --- | --- |
| missing path | 1 | `No such file or directory` |
| directory | 1 | `Is a directory` |
| empty / comments-only / `/dev/null` | 1 | `need rev, lock_nar, cache_nar` |
| unknown field / `narHash` | 1 | `unknown field` |
| spaces instead of tabs | 1 | `expected key<TAB>value` |
| UTF-8 BOM | 1 | `unknown field '\ufeffrev'` |
| invalid UTF-8 | 1 | codec error |
| CRLF | 1 | `splitlines`, owned leftover yes |
| stdin `-` / pipe / `/dev/stdin` | 1 | owned leftover (dash *is* stdin) |
| argv-less | 2 | argparse |
| process substitution / symlink / space in filename | 1 | leftover still `!=` |
| 10000-char hashes | 1 | 20050-byte stdout, leftover yes |
| empty `cache_nar` token | 1 | `line.strip()` eats the tab |
| no args / extra positional | 2 | argparse |
| `-h` | 0 | help |

Leftover-yes and parse/IO share rc=1. A pipe cannot tell “stale NAR” from “forgot `cache_nar`.” Tests never hit spectator rev, SRI-vs-hex, last-wins, stdin, BOM, or origin files. Three tests: owned poison, owned fresh, missing path (rc=1 only).

### 6. Distinct from Honor-KILLed lockident; not a refpin remainder

lockident (`~/.grok/worktrees/annenpolka-brrr/lockident-lockident/lockident/lockident.py`, sha256 `694acc90…`, 2017 bytes) is caller `--identity` vs per-blob `sha256(bytes)[:12]`. It hashes. This object does not. Passing narleftover’s two SRI strings as lockident blobs would membership-test them against a 12-char hex the caller also supplied — a different thin wrapper, already Honor-KILLed. Do not mutate narleftover into lockident.

Sibling `refpin` (KEEP, 617 lines, specimen-064) joins two fetch events: default-ref attach AND changed narHash while rev stayed. narleftover has one record, no `ref`, no FIRST/SECOND, no mismatch-log ingest. Do not mutate narleftover into refpin to escape. unusedfp was Honor-KILLed this run for two hashes plus set difference; this object is thinner.

---

## Primitive

Reality-stripped operation: parse a TSV of caller-labeled `rev` / `lock_nar` / `cache_nar`; print `leftover_stale_nar` as `cache_nar != lock_nar`; echo `rev` as a label; rc=1 iff that inequality (or parse/IO).

Nearest ordinary workflow: `test "$cache" != "$lock"`, or awk of the two caller-written fields, or reading the two owned records by eye. `demo.sh` already says that. Observable capability lost if narleftover vanishes: **none**. The harvest records already are the input. The join is still a hand comparison after the TSV. The fetcher cache is never read. The lockfile is never read. The rev is never used as a key.

That is why this is KILL, not MUTATE. The *question* (after a poisoned lock then a narHash correction, does `fetcher-cache-v4.sqlite` still map git-rev fingerprint R2 to H_nar1 while the lock names H_nar2) is a real debugging object. This embodiment does not ask it of a cache, a lock, or a store path. It asks two caller strings. Adding sqlite / `nix hash path` / `computeStorePath` would be implementing the nix theater the harvest rejected, and would be a new harvest, not a patch of this 88-line `!=`. Constitution: a THIN_WRAPPER does not gain exotic features to escape classification. Worker rule: do not send THIN_WRAPPER back to R1 with “make this more novel.” First HARVEST is not protection. Dreamer ancestry is not protection.

Hardcoded ceiling:

- leftover iff stripped `cache_nar != lock_nar`
- `rev` is a spectator; disk / sqlite / flake.lock are never read
- SRI vs hex vs noprefix vs quoted vs case are leftover (string form)
- leading space is stripped; empty token is unparseable
- last-wins overwrites; no two-event join
- leftover-yes and parse/IO share rc=1
- no hashlib; no nix; not in first selection

Honor KILL. Do not merge onto `main`. Do not run nix. Do not execute a Nix daemon or sqlite to mint a remainder. Archive stays under `lineages/candidate-narleftover/`. Do not mutate into lockident / refpin / unusedfp. Reimpl of this primitive is not a survivor.

KILL
