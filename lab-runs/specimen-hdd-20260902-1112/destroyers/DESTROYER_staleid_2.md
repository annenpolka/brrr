# DESTROYER staleid 2

Date: 2026-09-02 15:47 JST
RUN_ID: specimen-hdd-20260902-1112

Target (archive, KEEP survivor):
`/Users/annenpolka/ghq/github.com/annenpolka/brrr/lab-runs/specimen-hdd-20260902-1112/lineages/candidate-staleid/staleid`

sha256 `b6c7d888f96ad11f86853dcba1704643bbb55d5e6994c23bb4b283bb48c82af1` (3927 bytes, 120 lines). Worktree copy at `/Users/annenpolka/.grok/worktrees/annenpolka-brrr/candidate-staleid-staleid/staleid/staleid` is byte-identical (`cmp` rc=0). Worktree HEAD `b6e9fbb ground staleid from hdd-gocache harvest` on `specimen-hdd/candidate-staleid-staleid`. Parent `main` is `432f954`; `git ls-tree HEAD staleid` is empty. Tests 3/3 (`python3 -m unittest discover -s tests -v` → `Ran 3 tests in 0.078s` `OK`, rc=0). `demo.sh` twice: live stdout byte-identical to archived `demo-1.log` / `demo-2.log`. Host Python 3.14.5. Host has `go` (`/opt/homebrew/bin/go`); `command -v nix` empty. No merge onto `main`. Worktree was not edited.

Origin (`CANDIDATE.md` / harvest `hdd-gocache` / specimen-078): name FRESH same-key while binary buildid changed; whether the key included buildid. Kind: USEFUL_COMPOSITION. Owned analog `gocache_buildid.py` already prints `stale_binary True` / `key_includes_buildid False`. Rejected: invented `go tool buildid` / key-function patch. Constraint: freshmiss is missing extra, not stale buildid.

First destroyer (`DESTROYER_staleid.md`) KEEP: owned analog stale_binary yes / key_includes_buildid no / rc=1; unseen same shape; key changed with buildid → includes yes, stale no, rc=0; missing file rc=1; tests 3/3; demos identical. First KEEP is not protection. This cut is caller-labeled stale identity (`cached_buildid != buildid`) vs live identity (`cached_buildid == buildid`) on records the caller already filled.

This candidate is a **THIN_WRAPPER of caller-labeled stale vs live identity**. `stale_binary` is `same_key and second.status.upper()=="FRESH" and second.cached_buildid != second.buildid`. `key_includes_buildid` is “did the two caller keys move when the two caller buildids moved.” An independent reconstruction that does not import staleid is **byte-identical** on **40/40** host cases (`stdout_eq=True`, `rc_eq=True`). awk of those four fields names the owned join. Comparing the second record to itself still prints `stale_binary yes`. Decision: **KILL**.

CLI used below:

```text
CLI=/Users/annenpolka/ghq/github.com/annenpolka/brrr/lab-runs/specimen-hdd-20260902-1112/lineages/candidate-staleid/staleid
FIX=/Users/annenpolka/ghq/github.com/annenpolka/brrr/lab-runs/specimen-hdd-20260902-1112/lineages/candidate-staleid/fixtures
WT=/Users/annenpolka/.grok/worktrees/annenpolka-brrr/candidate-staleid-staleid/staleid/staleid
A078=/Users/annenpolka/ghq/github.com/annenpolka/brrr/lab-runs/specimen-hdd-20260902-1112/specimens/specimen-078/files/gocache_buildid.py
```

Host-executed against the archive. Worktree was not edited. Do not wrap `go tool buildid` / a JSON key function / a binary hasher to escape THIN_WRAPPER. Do not send the key-function patch back to R1. Distinct field names from freshmiss are not a derived observation.

---

## What still works

The owned analog pair, the unseen token-rename pair, and any other two TSV events the caller has already filled with `status` / `key` / `buildid` / `cached_buildid`.

```bash
python3 "$CLI" "$FIX/075-first.rec" "$FIX/075-second.rec"
echo rc=$?
```

```text
key_a	55e3acdd667f
key_b	55e3acdd667f
same_key	yes
buildid_a	buildid-aaa
buildid_b	buildid-bbb
cached_buildid	buildid-aaa
first_status	BUILT
second_status	FRESH
buildid_changed	yes
key_includes_buildid	no
stale_binary	yes
fresh_same_key	yes
rc=1
```

241 bytes. Stderr empty. Unseen `aaaa1111bbbb` / `id-1`→`id-2`: same twelve rows, stale yes, includes no, rc=1. Includes fixture (different key, status BUILT, cached defaults to live): stale no, includes yes, rc=0. Missing path rc=1. Tests 3/3. Demos identical.

That is the whole useful delta. It is also what the caller already typed into `cached_buildid` vs `buildid` and `status FRESH`. `demo.sh` states it before the CLI runs:

```text
== nearest: print cache key ==
first BUILT key 55e3acdd667f buildid-aaa
second FRESH same key buildid-bbb cached_buildid-aaa
```

Host `python3 "$A078"` already prints `stale_binary True` / `key_includes_buildid False`. The CLI will not parse that log.

---

## Implementation

`inspect()` in full:

```python
def inspect(first: dict, second: dict) -> dict:
    same_key = first["key"] == second["key"]
    buildid_changed = first["buildid"] != second["buildid"]
    stale = (
        same_key
        and second["status"].upper() == "FRESH"
        and second["cached_buildid"] != second["buildid"]
    )
    includes = first["key"] == second["key"] and not buildid_changed and first["key"] != ""
    key_includes_buildid = (not same_key) and buildid_changed
    if same_key and buildid_changed:
        key_includes_buildid = False
    if same_key and not buildid_changed:
        key_includes_buildid = "unknown"
    return {
        "first": first,
        "second": second,
        "same_key": same_key,
        "buildid_changed": buildid_changed,
        "key_includes_buildid": key_includes_buildid,
        "stale_binary": stale,
        "fresh_same_key": same_key and second["status"].upper() == "FRESH",
    }
```

`inspect.co_names` is `('upper',)`. `inspect.co_varnames` is `('first', 'second', 'same_key', 'buildid_changed', 'stale', 'includes', 'key_includes_buildid')`. `includes` is assigned and never read. No `hashlib`, no `subprocess`, no `go`. `parse_event` stores first `cached_buildid` and then inspect never uses it. `cached = fields.get("cached_buildid") or fields["buildid"]` — omit the cached field and identity is live by construction. `main` is rc=1 iff `stale_binary`, else 0 on a well-formed pair.

Owned fixtures already contain the answer:

```text
# 075-first.rec
status	BUILT
key	55e3acdd667f
buildid	buildid-aaa
cached_buildid	buildid-aaa

# 075-second.rec
status	FRESH
key	55e3acdd667f
buildid	buildid-bbb
cached_buildid	buildid-aaa
```

---

## Attacks

### 1. THIN_WRAPPER of caller-labeled stale vs live identity

Same first record. Second record identical except `cached_buildid` (the cached identity vs the live identity the caller already wrote as `buildid`):

```text
# labeled STALE identity     cached_buildid	live-old   buildid	live-new
stale_binary	yes
key_includes_buildid	no
fresh_same_key	yes
buildid_changed	yes
rc=1

# labeled LIVE identity      cached_buildid	live-new   buildid	live-new
stale_binary	no
key_includes_buildid	no
fresh_same_key	yes
buildid_changed	yes
rc=0
```

FRESH, same key, buildid changed on both. Only the stale-vs-live label on the second record moves the verdict. The harvest sentence “FRESH same-key while binary buildid changed” is `fresh_same_key` plus `buildid_changed`. `stale_binary` is a third predicate: cached identity ≠ live identity. The claimed product is that third bit, and the caller typed both identities.

awk of those fields names the same pair:

```text
owned          awk_same yes  awk_inc no       awk_stale yes
labeled_stale  awk_same yes  awk_inc no       awk_stale yes
labeled_live   awk_same yes  awk_inc no       awk_stale no
includes       awk_same no   awk_inc yes      awk_stale no
```

Independent reconstruction (parse the same four keys; stale / includes / same_key as above; does not import staleid) is byte-identical stdout and rc on:

```text
owned 075                         stdout_eq=True rc_eq=True  stale yes
unseen token rename               stdout_eq=True rc_eq=True  stale yes
includes-second (diff key)        stdout_eq=True rc_eq=True  stale no includes yes
same file twice / swap / second twice
labeled_stale / labeled_live
stale_without_event_change
missing_cached_defaults_live
built / CACHED / HIT / MISS / fresh / Fresh
diffkey_fresh_stale_ids / diffkey_same_buildid / same_all_fresh
first_status_fresh_unused / first_cached_ignored
lying_labels_no_binary
ws_stripped_same
dup_cached last-wins live / last-wins stale
comments_blanks / crlf / symlink_second
unknown_field / missing_key_field / spaces_not_tabs / json
native_analog_log / utf8_bom / empty_cached / empty_key
huge_diff_key / includes_but_fresh
```

40/40. No mismatches.

| second.cached vs second.buildid | second.status | same_key | stale_binary | key_includes_buildid |
| --- | --- | --- | --- | --- |
| unequal (stale identity) | FRESH | yes | **yes** | no if buildids also moved |
| equal (live identity) | FRESH | yes | **no** | no if buildids also moved |
| unequal | BUILT / CACHED / HIT | yes | no | no |
| unequal | FRESH | no | no | **yes** if buildids moved |
| equal, buildids unchanged | FRESH | yes | no | **unknown** |

Same declared FRESH, same key. Only the stale/live identity label (and the status token next to it) change the verdict. Lying labels with no binary on disk (`key does-not-exist`, `buildid AAA`→`BBB`, `cached AAA`): stale yes, rc=1. The CLI never `stat`s a binary.

### 2. The first event is a spectator. Second vs second is already stale

`075-second.rec` against itself:

```text
buildid_a	buildid-bbb
buildid_b	buildid-bbb
cached_buildid	buildid-aaa
first_status	FRESH
second_status	FRESH
buildid_changed	no
key_includes_buildid	unknown
stale_binary	yes
fresh_same_key	yes
rc=1
```

No time axis. The second record already holds both identities. `stale_binary` does not need a first build.

True “buildid did not change between events” (first `AAA`, second live `AAA`, cached `BBB`): `buildid_changed no`, `key_includes_buildid unknown`, **`stale_binary yes`**, rc=1. Stale identity on the second record is enough.

Swap (`075-second.rec` then `075-first.rec`): second is BUILT, cached==live, stale no, rc=0. Argv order is the time axis. The CLI will not say so.

`first_status` is printed and unused. First event `FRESH` with junk `cached_buildid ZZZ`: stale still follows the second record. First `cached_buildid` is parsed, stored, never printed (`format_report` emits only `second['cached_buildid']`).

### 3. `key_includes_buildid` is key-moved-when-buildid-moved, not a key function

```text
keys differ AND buildids differ  → yes
keys same AND buildids differ    → no
keys same AND buildids same      → unknown
keys differ AND buildids same    → no
```

That is the comment in source (“only if a buildid change would have changed the key”) restated as two string inequalities. No key function is reconstructed. The dead `includes` local (`same_key and not buildid_changed and key != ""`) is the other polarity and is discarded.

Includes fixture: keys `55e3acdd667f` vs `cccc2222dddd`, buildids `buildid-aaa` vs `id-2`, status BUILT, no cached field (defaults live). `key_includes_buildid yes` because both strings moved. Status BUILT so stale no. The first KEEP treated this as “key changed with buildid.” The caller wrote a different key. Diffkey + FRESH + stale ids (`cached != live`) is still `key_includes_buildid yes` and `stale_binary no` — includes does not read cached identity.

Same key, same buildid, FRESH, live identity: `key_includes_buildid unknown`, stale no. The tool cannot ask “does this key function include buildid” of one event.

### 4. Analog already names it. Native log is refused

```bash
python3 "$A078"
```

```text
first BUILT key 55e3acdd667f buildid buildid-aaa
second FRESH key 55e3acdd667f buildid buildid-bbb cached_buildid buildid-aaa
same_key True
key_includes_buildid False
stale_binary True
```

Feed that log as a record:

```text
staleid: …/alog.rec:1: expected key<TAB>value
rc=1
```

`demo.sh` already rewrites those facts into `.rec` files. The identities the harvest “discovers” are supplied by the rewrite. `cut -f1,2` of `075-second.rec` already prints `status FRESH`, `buildid buildid-bbb`, `cached_buildid buildid-aaa`. `comm -3` of the two owned records already names BUILT vs FRESH and `buildid-aaa` vs `buildid-bbb`.

Sibling `freshmiss` on these records: `unknown field 'key'`, rc=1. Field-name mismatch is not a new primitive. lockident was Honor-KILLed this run for caller `--identity` vs `sha256[:12]`; this object is thinner (no hash).

### 5. Missing cached identity defaults live. Empty identity is unrepresentable

Omit `cached_buildid` on a FRESH same-key record whose live buildid changed:

```text
cached_buildid	live-new
stale_binary	no
rc=0
```

`fields.get("cached_buildid") or fields["buildid"]` makes a missing cached field equal the live identity. Stale is impossible unless the caller types a second identity.

`cached_buildid<TAB>` (empty value): `line.strip()` eats the trailing tab → `expected key<TAB>value`, rc=1. Same for empty `key<TAB>`. Whitespace-only values cannot be labeled. Duplicate `cached_buildid` last-wins: `live-old` then `live-new` → live, stale no; reverse order → stale yes. No error.

### 6. Status is a token. Exit 1 collides with IO

`status fresh` / `Fresh`: stale yes (`.upper()`). `FRESH` with trailing space: strip makes `FRESH`. `BUILT` / `CACHED` / `HIT` / `MISS` with stale ids: stale no, rc=0. Status is a spectator for everything except the FRESH conjunction.

stale_binary yes is rc=1. Missing path is rc=1 (`No such file or directory: '/no'`). Directory is rc=1 (`Is a directory`). `-` is rc=1 (`No such file or directory: '-'`). `/dev/null` is rc=1 (`missing status`). Native log / JSON / spaces / BOM / unknown field / invalid UTF-8 (`'utf-8' codec can't decode byte 0xff`) are rc=1. A pipe `staleid a b || echo STALE` fires on parse failure and on harvest. Fine as a printer of labels; hostile as a predicate for “this binary is stale.”

No args / one arg / extra arg: argparse rc=2. `--help` rc=0. `/dev/stdin` as FIRST works (owned harvest). Symlink to the second record matches. 200_000-char second key: rc=0, stdout 200207 bytes, `same_key no`, `key_includes_buildid yes`. No cap. Comments / blanks / CRLF: harvest.

### 7. Still two labels. THIN_WRAPPER does not gain `go tool buildid`

Host `go` exists. Source does not call it. Harvest rejected invented `go tool buildid` and the key-function patch. `inspect.co_names` is `('upper',)`.

A mutation that hashed test files, ran `go tool buildid` on a binary, or ingested `gocache_buildid.py` stdout would be implementing the composition this artifact failed to embody — a new harvest, not a patch of string inequality. Constitution: a THIN_WRAPPER does not gain exotic exec features to escape classification. Worker rule: do not send THIN_WRAPPER back to R1 with “make this more novel.” Do not mutate staleid into freshmiss / lockident / unusedfp to escape.

Hardcoded ceiling:

- stale_binary = same_key AND second FRESH AND caller cached identity ≠ caller live identity
- live identity (`cached_buildid` omitted or equal to `buildid`) ⇒ stale no even when FRESH same-key and buildid_changed
- second vs second is already stale when that record holds both identities
- key_includes_buildid = keys moved XOR not, when buildids moved; unknown when neither moved; dead `includes` unused
- first event’s status and cached_buildid are printed-or-parsed spectators
- missing cached field defaults live; empty identity is a parse error
- rc=1 on stale and on IO/parse; rc=0 on live FRESH
- native analog log is not an input; demo.sh already contains the answer
- analog already prints `stale_binary True`; awk of the `.rec` files names the join
- the CLI will not hash a key function, will not read a binary, will not run `go tool buildid`

Do not grow a buildid reader to escape THIN_WRAPPER. Do not merge this join onto `main`. Honor KILL. Dreamer ancestry is not protection. First KEEP is not protection.

---

KILL
