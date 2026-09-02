# DESTROYER lockident 2

Date: 2026-09-02 15:22 JST
RUN_ID: specimen-hdd-20260902-1112

Target (worktree; no `lineages/candidate-lockident/` archive):
`/Users/annenpolka/.grok/worktrees/annenpolka-brrr/lockident-lockident/lockident/lockident.py`

sha256 `694acc9041c8f7baf701647473ec0788fa1fd687ef0e83cc1e6e6e32ae54b991` (2017 bytes, 59 lines). HEAD `11736ad` (`Add lockident CLI: which blobs hashed into a freshness identity.`), branch `specimen-hdd/lockident-lockident`. Pointer: `lineages/lockident.worktree`. Parent `main` is `432f954`; `git ls-tree` has no `lockident`. No tests, no `demo.sh`, no `CANDIDATE.md` in that directory. Host Python 3.14.5. No nix (`command -v nix` empty). Not merged onto `main`. Worktree was not edited.

Origin claim (`hdd-cache-mw` / specimen-016): name which provided blobs hashed into a freshness identity and whether the live lockfile is among them. Kind: USEFUL_COMPOSITION. First destroyer (`DESTROYER_lockident.md`) **KEEP**: owned lock-omitted holds; missing `--blob` rc=2; unmatched identity `in_identity none`; empty `lock_new=` omitted; extra-output transfer “correctly reports extra omitted” when identity is the input hash. Encoding limitation (`--blob name=bytes` cannot express a JSON object identity without the caller computing `--identity`) was called acceptable. First KEEP is not protection.

This candidate is a **THIN_WRAPPER of caller-supplied `--identity` vs per-blob `sha256(bytes)[:12] == identity`**. `main` never sees FRESH/BUILT, never reads a lockfile, never reconstructs a key function. Host replica of that equality is **byte-identical** to CLI stdout on owned 016, TRANSFER_075, extra-output encodings, empty lock, and unmatched identity. `shasum -a 256 | cut -c1-12` plus `test "$d" = "$identity"` already names `in` / `omitted`. Decision: **KILL**.

CLI used below:

```text
CLI=/Users/annenpolka/.grok/worktrees/annenpolka-brrr/lockident-lockident/lockident/lockident.py
A016=/Users/annenpolka/ghq/github.com/annenpolka/brrr/lab-runs/specimen-hdd-20260902-1112/specimens/specimen-016/files/cache_lock.py
A078=/Users/annenpolka/ghq/github.com/annenpolka/brrr/lab-runs/specimen-hdd-20260902-1112/specimens/specimen-078/files/gocache_buildid.py
A011=/Users/annenpolka/ghq/github.com/annenpolka/brrr/lab-runs/specimen-hdd-20260902-1112/specimens/specimen-011/files/cache_build.py
STALE=/Users/annenpolka/ghq/github.com/annenpolka/brrr/lab-runs/specimen-hdd-20260902-1112/lineages/candidate-staleid/staleid
```

Host-executed against the worktree only. Do not merge onto `main`. Do not run nix. Do not wrap cargo / `go tool buildid` / a JSON key function to escape THIN_WRAPPER. Sibling `staleid` already owns omitted-buildid. Sibling `freshmiss` already owns extra-output. Sibling `refpin` already owns s064 (TRANSFER FAIL). unusedfp was Honor-KILLed this run for two hashes plus set difference; this object is thinner.

---

## What still works

Owned 016 and any other case where the caller already computed the 12-char identity **and** already encoded each blob as the exact bytes that identity hashed.

```bash
python3 "$A016"
python3 "$CLI" --identity 673767793f4a \
  --blob 'src=mod.rs\nfn f() {}\n' \
  --blob 'lock_new=serde = "1.0.219"\n' --live lock_new
echo rc=$?
```

```text
first BUILT key 673767793f4a artifact built-with:serde = "1.0.0"
after_lock_bump FRESH key 673767793f4a artifact built-with:serde = "1.0.0"
same_key True
lock_changed True
lock_old serde = "1.0.0"
lock_new serde = "1.0.219"

blob         digest12     membership
------------ ------------ ----------
src          673767793f4a in
lock_new     324afc7759fc omitted
identity  673767793f4a
in_identity  src
omitted  lock_new
live_lock_in_identity  false
rc=0
```

Missing `--blob`: `lockident: need at least one --blob`, rc=2. Missing `--identity`: argparse rc=2. No `=` / empty name: rc=1. Unmatched identity: `in_identity none`, rc=0. Empty `lock_new=`: `lock_new e3b0c44298fc omitted` (`sha256("")[:12]`). That is the first KEEP. It is also two `sha256` prefixes and a string compare the analog already named (`fingerprint(src)` in `cache_lock.py`).

That is the whole useful delta. Attacks below break the membership-as-identity-function claim, or show the primitive cannot grow.

---

## Implementation

Load-bearing body:

```python
def digest12(text: str) -> str:
    return hashlib.sha256(text.encode()).hexdigest()[:12]

# for each --blob name=bytes (after replace \\n → newline):
#   member = digest12(bytes) == args.identity
# live_lock_in_identity = args.live in in_id if args.live else False
```

`digest12.co_names` is `('hashlib', 'sha256', 'encode', 'hexdigest')`. `parse_blob.co_names` is `('SystemExit', 'partition', 'replace')`. Source contains no `FRESH`, `BUILT`, or `same_key`. Identity of empty bytes is `e3b0c44298fc`. Those hex strings are not cargo fingerprints.

### 1. THIN_WRAPPER of caller `--identity` vs blob-digest equality

Independent reconstruction of `digest12` + membership + `live` (no import of the module) is **byte-identical** to CLI stdout on owned 016 (`cmp` of replica vs CLI: identical), TRANSFER_075 (`identical True`), extra-output raw `src=hello`, extra-output `json.dumps({"src":"hello"})`, empty lock, unmatched `deadbeef0000`.

Nearest ordinary workflow, host-executed:

```bash
printf '%s' $'mod.rs\nfn f() {}\n' > /tmp/lockident-src
printf '%s' $'serde = "1.0.219"\n' > /tmp/lockident-lock
ident=673767793f4a
for f in src lock; do
  d=$(shasum -a 256 /tmp/lockident-$f | cut -c1-12)
  echo "$f $d $( [ "$d" = "$ident" ] && echo in || echo omitted )"
done
openssl dgst -sha256 < /tmp/lockident-src
```

```text
src 673767793f4a in
lock 324afc7759fc omitted
SHA256(stdin)= 673767793f4a…
```

`openssl dgst -sha256` of src is the analog key and the CLI `in` row. `shasum` of lock is `324afc7759fc` / omitted. The harvest said “sha256 of src and of lock are two commands; they do not join FRESH to omitted lock bytes.” This CLI still does not join FRESH. It never sees the two builds. Caller already has the key (`673767793f4a` printed by `cache_lock.py`) and already has the bytes. `live_lock_in_identity false` is `test lock_digest != identity` with a name the caller passed as `--live`.

`--identity` is required. Without it, argparse rc=2. The tool cannot ask “which of these blobs hashed into the key”; it can only ask “which of these blobs equal this hex I already have.”

### 2. Omitted buildid transfer is the analog’s JSON list, restated

TRANSFER_075 / specimen-078 analog:

```text
first BUILT key 55e3acdd667f buildid buildid-aaa
second FRESH key 55e3acdd667f buildid buildid-bbb cached_buildid buildid-aaa
same_key True
key_includes_buildid False
stale_binary True
```

`test_key` is `sha256(json.dumps(["foo_test.go"], sort_keys=True))[:12]` = `55e3acdd667f`. The transfer:

```bash
python3 "$CLI" --identity 55e3acdd667f \
  --blob 'tests=["foo_test.go"]' --blob buildid=buildid-aaa --live tests
```

```text
tests        55e3acdd667f in
buildid      5ad4c87a0014 omitted
in_identity  tests
omitted  buildid
live_lock_in_identity  true
```

`--blob tests=foo_test.go` (the filename, not the JSON list):

```text
tests        19dd3d423d43 omitted
buildid      5ad4c87a0014 omitted
in_identity  none
live_lock_in_identity  false
```

Wrong encoding ⇒ the owned join vanishes. `--live buildid` on the published transfer args: same `omitted buildid`, but `live_lock_in_identity false`. `--live tests` is true because tests is the IN blob, not because a lockfile entered the key. Point `--identity` at `sha256(b"buildid-aaa")[:12]` = `5ad4c87a0014` and membership inverts (`buildid in`, `tests omitted`, `live_lock_in_identity true` if `--live buildid`). Caller-scripted narrative.

Sibling `staleid` on two events with those keys/buildids (rc=1):

```text
same_key	yes
buildid_changed	yes
key_includes_buildid	no
stale_binary	yes
fresh_same_key	yes
```

That is the harvest. lockident does not see two events. It hashes the JSON the analog already used as the key function.

### 3. Extra-output identity is encoding, not output membership

specimen-011 analog key is `sha256(json.dumps({"src":"hello"}, sort_keys=True))[:12]` = `9280cc7e16e9`. First destroyer: extra omitted when identity is the input hash; “src membership depends on encoding.”

```bash
python3 "$CLI" --identity 9280cc7e16e9 --blob src=hello --blob extra=out.sbom
```

```text
src          2cf24dba5fb0 omitted
extra        ba526582a47d omitted
in_identity  none
omitted  src,extra
```

Both omitted. `2cf24dba5fb0` is `sha256(b"hello")[:12]`. Extra omitted here is the unmatched-identity case, not “requested output outside the key.” Compact JSON `'{"src":"hello"}'` (no space) is `2982572400eb`, also all omitted. Only the exact dumps with space after colon:

```text
inputs       9280cc7e16e9 in
extra        ba526582a47d omitted
in_identity  inputs
omitted  extra
```

Caller who already knows `json.dumps(inputs, sort_keys=True)` already knows extra was not in that object. Passing `out.bin=bin:hello` and `out.sbom=` still omits both files: they are more argv bytes, not outputs. Sibling `freshmiss` already names FRESH-but-missing `out.sbom`. This object will not.

### 4. Empty lock is `sha256("")`; missing `--blob` is argv

```bash
python3 "$CLI" --identity 673767793f4a \
  --blob 'src=mod.rs\nfn f() {}\n' --blob 'lock_new=' --live lock_new
```

```text
src          673767793f4a in
lock_new     e3b0c44298fc omitted
live_lock_in_identity  false
```

`e3b0c44298fc` is `sha256("")[:12]`. Empty lock vs nonempty src is not observed; it is hashing the empty side of `name=`. Identity of empty + `--blob lock_new=` + `--live lock_new`: `in_identity lock_new`, `live_lock_in_identity true`. A vacant blob is “the live lock” when the caller says the key is the empty digest.

No `--blob`: rc=2, stderr `lockident: need at least one --blob`. No `--identity`: argparse rc=2. Passing filesystem paths as blob values hashes the path strings (`in_identity none`). `--blob @file` is `expected name=bytes`, rc=1. Stdin is ignored.

### 5. Membership is whole-blob equality, not “entered the identity”

Concat identity `sha256(src+lock_new)[:12]` = `fd4d608b4638` with both blobs provided:

```text
src          673767793f4a omitted
lock_new     324afc7759fc omitted
in_identity  none
```

Both entered the hash. Both omitted. JSON-map identity of `{src, lock}` is `aba51aa25c48` (same as unusedfp’s all-map of those two strings); same `in_identity none`. unusedfp’s `all_first=cd6312a323ca` with `path=/app` and `idea.io.use.nio2=false`: `in_identity none`. Per-blob digest never equals a composite key. The primitive cannot name a component of an identity that is not itself the identity.

s064 (TRANSFER FAIL, already harvested as `refpin`): `--identity e374a4ebd0db` with rev/ref/narHash blobs → all omitted. `--identity` is not a git rev and not a narHash. Membership cannot name `ref` present vs absent while `rev` stayed.

### 6. `--live` is a name check; caller can lie

`--live` is `args.live in in_id`. Owned 016 `--live src`: `live_lock_in_identity true` (src is in). `--live lock_new`: false. `--live` of a name that is not a blob: false, rc=0. Omitted `--live` / `--live ''`: false. Duplicate names `src=hello` then `src=other`: `in_identity src` and `omitted src` on the same run. Two names, same bytes (`a=hello`, `b=hello`): both `in`; `--live a` is true. Uppercase identity `673767793F4A` vs lower digest: `in_identity none`. Identity `src` (the name, not a digest): none. Empty `--identity ''`: prints `identity  ` and omits everything, rc=0.

The analog’s lock-omitted fact is `--live` pointed at the omitted name. Point it at the in name and the CLI reports the live lock is in the identity.

### 7. Still two hashes. THIN_WRAPPER does not gain a key function

`demo` nearest operation was never written; `cache_lock.py` already prints the key twice and `lock_changed True`. `gocache_buildid.py` already prints `key_includes_buildid False` / `stale_binary True`. `cache_build.py` already prints `same_key True` / extra missing.

A mutation that computed identity from a named subset, ingested two cache events, or parsed Cargo.lock would be implementing the composition this artifact failed to embody — a new harvest, not a patch of equality. Constitution: a THIN_WRAPPER does not gain exotic exec features to escape classification. Worker rule: do not send THIN_WRAPPER back to R1 with “make this more novel.” Do not mutate lockident into `staleid` / `freshmiss` / `refpin` to escape.

Hardcoded ceiling:

- identity = caller hex; membership = `sha256(blob.encode())[:12] == identity`
- `--blob` is argv, `partition("=")`, `\\n` → newline only; paths are path-strings; no file ingest
- composite / JSON-map / git-rev identities ⇒ `in_identity none` even when the bytes entered
- extra-output and gocache joins require the caller to pass the analog’s dumps as a blob
- `--live` is name ∈ in-set, including `--live src` on a lock-omitted packet
- empty blob = `e3b0c44298fc`; empty identity is legal rc=0
- missing `--blob` / `--identity` are argv (rc=2), not cache misses
- case-sensitive hex; 11-char / 14-char / uppercase miss
- duplicate names can be both in and omitted
- no FRESH/BUILT; no tests; not in first selection

Honor KILL. Dreamer ancestry is not protection. First-destroyer KEEP is not protection once membership is shown to be caller hex vs `sha256[:12]`.

Do not merge onto `main`. Do not run nix. Do not execute cargo or Go to mint a remainder. Worktree stays under `~/.grok/worktrees/annenpolka-brrr/lockident-lockident/`. Pointer: `lineages/lockident.worktree`.

KILL
