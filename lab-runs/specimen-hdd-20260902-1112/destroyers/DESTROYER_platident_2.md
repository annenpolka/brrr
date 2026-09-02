# DESTROYER platident 2

Date: 2026-09-02 14:51 JST
RUN_ID: specimen-hdd-20260902-1112

Target (archive, KEEP survivor):
`/Users/annenpolka/ghq/github.com/annenpolka/brrr/lab-runs/specimen-hdd-20260902-1112/lineages/candidate-platident/platident`

CLI sha256 `7a2caaaf8fb5b7e1e32d920409e8b32e29df5a3510cb461e09907581b48bb774` (4030 bytes). Worktree copy at `/Users/annenpolka/.grok/worktrees/annenpolka-brrr/candidate-platident-platident/platident/platident` is byte-identical (branch `specimen-hdd/candidate-platident-platident`, HEAD `5fdb719 ground platident from hdd-s074 harvest`). Parent `main` is `432f954`; `platident` is not in that tree. Tests: `python3 -m unittest discover -s …/tests -v` → 3/3 OK, rc=0. `demo.sh` twice to temp logs: byte-identical, matches archived `demo-1.log` / `demo-2.log`. Host Python 3.14.5. No poetry (`command -v poetry` empty). No nix. No merge onto `main`.

Origin: specimen-074 / hdd-s074. Frozen `bundle install` exit 0 materializes `nokogiri-1.18.10` (Gem::Platform::RUBY) while `Bundler.setup` misses locked `nokogiri-1.18.10-x86_64-linux`. Classification: USEFUL_COMPOSITION. Primitive claimed: `hidden_by_exit0` when install ruby-platform exit 0 and setup misses locked linux identity. First destroyer (`DESTROYER_platident.md`) KEEP: owned 074 harvests, unseen sorbet-static same shape, agree not hidden, missing file rc=1. Bakeoff prefers this object over `platid` until a later destroyer. This is that destroyer.

CLI used below:

```text
CLI=/Users/annenpolka/ghq/github.com/annenpolka/brrr/lab-runs/specimen-hdd-20260902-1112/lineages/candidate-platident/platident
FIX=/Users/annenpolka/ghq/github.com/annenpolka/brrr/lab-runs/specimen-hdd-20260902-1112/lineages/candidate-platident/fixtures
```

Host-executed against the archive only. Worktree was not edited. This candidate is a **THIN_WRAPPER of string inequality** of two caller-written ids, with `install_exit`/`lookup_status` defaulting to harvest-true. `same_name_version` is a spectator. Independent reconstruction of full stdout is IDENTICAL 11/11. awk of `a != b` plus the two membership tests matches the load-bearing columns on owned/unseen/agree. Decision: **KILL**.

---

## What still works

Owned 074, unseen sorbet-static, agree, missing path, empty file, `/dev/null`, directory, no args. stdin `-` / `/dev/stdin` / FIFO / process substitution / symlink / filename with a space / CRLF / comments: harvest. That is the first KEEP. It is also `test "$install_id" != "$lookup_id"`.

```bash
python3 "$CLI" "$FIX/074-nokogiri.rec"; echo rc=$?
```

```text
install_id	nokogiri-1.18.10
lookup_id	nokogiri-1.18.10-x86_64-linux
install_platform	ruby
lookup_platform	x86_64-linux
same_name_version	yes
identity_mismatch	yes
install_ok	yes
lookup_miss	yes
hidden_by_exit0	yes
rc=0
```

```bash
python3 "$CLI" "$FIX/agree.rec"; echo rc=$?
# hidden_by_exit0	no
# identity_mismatch	no
# rc=0
```

Missing `/no/such/platident`: empty stdout, `platident: [Errno 2] No such file or directory`, rc=1. `/dev/null` / empty file: `missing install_id or lookup_id`, rc=1. Directory: `Is a directory`, rc=1. No args / extra arg: argparse rc=2. `--help` rc=0.

Sibling `platid` on the same owned pair prints the same harvest name and **rc=1**. platident harvests at **rc=0**.

That is the whole useful delta. Attacks below show `hidden_by_exit0` does not require same name+version, does not require `install_exit` to be present, and does not care which id is install vs lookup.

---

## Implementation

Load-bearing body of `inspect()`:

```python
mismatch = inst != look
install_ok = rec.get("install_exit", "0") in {"0", "ok", "success"}
lookup_miss = rec.get("lookup_status", "miss") in {"miss", "missing", "fail", "1"}
hidden = install_ok and lookup_miss and mismatch
```

`same_nv = iname == lname and iver == lver` is computed from `split_id` and written as `same_name_version`. It is not in `hidden`. `inspect.co_names` is `('split_id', 'get')`. `format_report` never prints name or version, only the two platforms and the spectator boolean.

`demo.sh` already names the nearest operation: `print both gem full names` / `install nokogiri-1.18.10  setup nokogiri-1.18.10-x86_64-linux  install exit 0`.

### 1. THIN_WRAPPER of string inequality

Independent reconstruction of `inspect()` + `format_report` (exec of the archive file, no import of a package) is **byte-identical** to CLI stdout on 11/11 host cases: owned, unseen, agree, ids-only (no exit fields), swapped owned, different name+version, `nokogiri-1.18.10` vs `nokogiri-1.18.10-ruby`, `0mq-1.0.0` vs `0mq-1.0.0-java`, hyphen prerelease, `install_exit 1`, `lookup_status ok`.

awk of the four load-bearing columns, without `split_id`:

```awk
BEGIN{FS="\t"}
$1=="install_id"{i=$2}
$1=="lookup_id"{l=$2}
$1=="install_exit"{e=$2}
$1=="lookup_status"{s=$2}
END{
  if(e=="") e="0"
  if(s=="") s="miss"
  ok=(e=="0"||e=="ok"||e=="success")
  miss=(s=="miss"||s=="missing"||s=="fail"||s=="1")
  mm=(i!=l)
  hidden=(ok && miss && mm)
  printf "identity_mismatch\t%s\n", mm?"yes":"no"
  printf "install_ok\t%s\n", ok?"yes":"no"
  printf "lookup_miss\t%s\n", miss?"yes":"no"
  printf "hidden_by_exit0\t%s\n", hidden?"yes":"no"
}
```

`074-nokogiri.rec` / `unseen-sorbet.rec` / `agree.rec`: awk == CLI those four rows. IDENTICAL.

Harvest fires when the two id strings differ, even when `same_name_version` is `no`:

```bash
printf 'install_id\taaa-1.0.0\nlookup_id\tbbb-9.9.9-x86_64-linux\ninstall_exit\t0\nlookup_status\tmiss\n' | python3 "$CLI" -
```

```text
same_name_version	no
identity_mismatch	yes
hidden_by_exit0	yes
rc=0
```

Same for different version, same platform (`nokogiri-1.18.10-x86_64-linux` vs `nokogiri-1.18.11-x86_64-linux`): `same_name_version no`, `hidden_by_exit0 yes`. The claimed primitive is “name+version match and platform does not.” The predicate is `inst != look`.

Constitution: a THIN_WRAPPER does not gain extra TSV rows (`install_platform`, `same_name_version`) to escape classification. Those rows are `split_id` labels. They do not vote.

### 2. Missing `install_exit` / `lookup_status` default to harvest-true

`rec.get("install_exit", "0")` and `rec.get("lookup_status", "miss")`. Omit both fields; keep the owned ids:

```bash
printf 'install_id\tnokogiri-1.18.10\nlookup_id\tnokogiri-1.18.10-x86_64-linux\n' | python3 "$CLI" -
```

```text
install_ok	yes
lookup_miss	yes
hidden_by_exit0	yes
rc=0
```

The exit-0 that names the harvest is not in the record. Omit only `install_exit`, or only `lookup_status`: still harvest. Two different ids are sufficient.

Same ids, no exit fields: `identity_mismatch no`, `lookup_miss yes` (default miss), `hidden_by_exit0 no`. Default miss does not harvest an agree; default success does harvest a mismatch.

Present fields that are not in the token sets:

| field | value | install_ok / lookup_miss | hidden |
| --- | --- | --- | --- |
| `install_exit` | `0` / `ok` / `success` | yes / (miss) | yes |
| `install_exit` | `1` / `fail` / `false` / `00` | no | no |
| `lookup_status` | `miss` / `missing` / `fail` / `1` | (ok) / yes | yes |
| `lookup_status` | `ok` / `found` / `0` | (ok) / no | no |

`00` is not success. `lookup_status 0` is not a miss (install uses `0` as ok; lookup uses `1` as miss). Empty `install_exit<TAB>` with no value: `expected key<TAB>value`, rc=1 — omit the key, do not blank it.

The harvest name is `hidden_by_exit0`. The exit can be absent.

### 3. `split_id` is a hyphen heuristic, not `Gem::Specification#full_name`

`split_id` splits on `-`, takes the first token whose first character is a digit as version, and treats `rest[1:]` as platform. Empty platform prints `ruby`. Comment in source: “Last two hyphen runs are not reliable.” Host tuples:

```text
nokogiri-1.18.10                  -> ('nokogiri', '1.18.10', '')
nokogiri-1.18.10-x86_64-linux     -> ('nokogiri', '1.18.10', 'x86_64-linux')
nokogiri-1.18.10-ruby             -> ('nokogiri', '1.18.10', 'ruby')
foo-1.0.0-rc1                     -> ('foo', '1.0.0', 'rc1')
foo-1.0.0-rc1-x86_64-linux        -> ('foo', '1.0.0', 'rc1-x86_64-linux')
0mq-1.0.0                         -> ('0mq', '1.0.0', '')
0mq-1.0.0-java                    -> ('0mq', '1.0.0-java', '')
foo-2-1.0.0                       -> ('foo', '2', '1.0.0')
foo-2-1.0.0-java                  -> ('foo', '2', '1.0.0-java')
1.18.10-x86_64-linux              -> ('1.18.10', 'x86_64-linux', '')
nokogiri-1.18.10-                 -> ('nokogiri', '1.18.10', '')
```

Hyphen prerelease (`foo-1.0.0-rc1` vs `foo-1.0.0-rc1-x86_64-linux`): `same_name_version yes`, platforms `rc1` vs `rc1-x86_64-linux`, `hidden_by_exit0 yes`. Version is not `1.0.0-rc1`. Platform is not `x86_64-linux`. Dot prerelease (`1.0.0.pre.1`) splits as a real gem version; the hyphen form does not.

Digit-leading name (`0mq-1.0.0` vs `0mq-1.0.0-java`): because `idx == 0`, the java platform is swallowed into version. Both platforms print `ruby`. `same_name_version no`. `hidden_by_exit0 yes`. The spectator column lies; the harvest still fires on string inequality.

Name with a digit token (`foo-2-1.0.0`): name `foo`, version `2`, platform `1.0.0`. If the gem is `foo-2` version `1.0.0`, the parse is the wrong split. `hidden_by_exit0` still yes against the java form.

`Gem::Platform::RUBY` spelling: empty suffix vs explicit `-ruby` are the same platform after default, and a harvest:

```bash
printf 'install_id\tnokogiri-1.18.10\nlookup_id\tnokogiri-1.18.10-ruby\ninstall_exit\t0\nlookup_status\tmiss\n' | python3 "$CLI" -
```

```text
install_platform	ruby
lookup_platform	ruby
same_name_version	yes
identity_mismatch	yes
hidden_by_exit0	yes
rc=0
```

Reverse (`-ruby` then empty suffix): same false harvest. Both sides spelled `-ruby`: `identity_mismatch no`, `hidden_by_exit0 no`. The mismatch is the suffix spelling, not the identity. Owned 074 is the empty-suffix form; the CLI will also harvest the same ruby gem written two ways.

Trailing hyphen `nokogiri-1.18.10-` vs owned linux: platform still `ruby` vs `x86_64-linux`, `same_name_version yes`, harvest. Lockfile line `nokogiri (1.18.10-x86_64-linux)` is `expected key<TAB>value`, rc=1 — no lock ingest. `mingw` / `musl` / `gnu` / `arm64-darwin` hyphen platforms split as owned does; they are still `a != b`.

`split_id` is dressing. It does not decide `hidden_by_exit0`. When it lies, the harvest bit still follows the raw strings.

### 4. Swapped ids still harvest

Owned pair with install/lookup reversed:

```bash
printf 'install_id\tnokogiri-1.18.10-x86_64-linux\nlookup_id\tnokogiri-1.18.10\ninstall_exit\t0\nlookup_status\tmiss\n' | python3 "$CLI" -
```

```text
install_id	nokogiri-1.18.10-x86_64-linux
lookup_id	nokogiri-1.18.10
install_platform	x86_64-linux
lookup_platform	ruby
same_name_version	yes
identity_mismatch	yes
hidden_by_exit0	yes
rc=0
```

Ids-only swap (no exit fields): same harvest. Unseen sorbet-static swap: same. platid’s unseen shape (`ffi-1.17.0-arm64-darwin` installed, `ffi-1.17.0` lookup): `hidden_by_exit0 yes`.

Specimen-074 is install of the ruby gem, setup miss of the locked linux gem. The swap is the other bug (platform gem on disk, ruby lookup). This CLI names both `hidden_by_exit0`. There is no time axis. `identity_mismatch` is commutative. Duplicate `install_id` last-wins can even collapse a mismatch into an agree (`hidden_by_exit0 no`) without error.

### 5. stdin — `-` holds; BOM / empty / extra arg do not

`-` FIRST (only arg): owned harvest, agree not hidden. `/dev/stdin`: harvest. FIFO with a writer: harvest. Process substitution: harvest. Symlink, space in filename, CRLF, comments: harvest.

Empty stdin: `platident: <stdin>: missing install_id or lookup_id`, rc=1. UTF-8 BOM: `unknown field '\ufeffinstall_id'`, rc=1. `python3 "$CLI" - -`: argparse `unrecognized arguments: -`, rc=2 (one positional). Invalid UTF-8: codec error, rc=1. JSON object / spaces instead of tabs / unknown field: parse error, rc=1, empty stdout.

stdin is not the kill. The harvest on `-` is the same `a != b` as the file path.

Extra tab in `install_id` (`nokogiri-1.18.10<TAB>extra`): value keeps the extra field, `same_name_version no`, `hidden_by_exit0 yes`, rc=0. NUL in `lookup_status` (`miss\x00`): token not in the miss set, `lookup_miss no`, `hidden_by_exit0 no`, rc=0 — silent not-harvest, not an error. Huge 5000-char name / version: harvest, ~10k stdout, no cap.

### 6. Harvest rc=0; lockfile is not ingest

Owned hidden: rc=0. Agree: rc=0. Ids-only hidden: rc=0. `install_exit 1`: `hidden_by_exit0 no`, still rc=0. Distinction is the `hidden_by_exit0` row, not grep-on-exit. Sibling `platid` after its destroyer MUTATE returns rc=1 on the same owned pair.

A real lockfile snippet (`    nokogiri (1.18.10-x86_64-linux)`) is `expected key<TAB>value`. The caller must already have typed `install_id` / `lookup_id`. No `Gemfile.lock`, no `gem specification`, no bundler.

---

## Primitive

Reality-stripped operation: parse a TSV map of two caller-written full names; `identity_mismatch = install_id != lookup_id`; `install_ok` defaults missing `install_exit` to `"0"`; `lookup_miss` defaults missing `lookup_status` to `"miss"`; `hidden_by_exit0 = install_ok and lookup_miss and mismatch`; print empty-suffix as `ruby`; exit 0 if the map parsed.

Nearest ordinary workflow (owned packet, also `demo.sh`):

```text
echo "install nokogiri-1.18.10  setup nokogiri-1.18.10-x86_64-linux  install exit 0"
test "nokogiri-1.18.10" != "nokogiri-1.18.10-x86_64-linux"
awk of the four membership rows above
```

On specimen-074 that pair is: ruby full_name vs linux full_name, install exit 0, setup miss. platident’s load-bearing claim is that naming `hidden_by_exit0` is a join those two strings plus two statuses do not already contain.

It is not. The statuses are optional and default to the harvest. `same_name_version` does not vote. Swap is the same bit. `split_id` is a hyphen split whose lies do not change `hidden`. Mounting a lockfile / running bundler is out of scope and refused.

Observable capability lost if platident vanishes: **none**. The caller already wrote both identities. `test a != b` already says mismatch. `printf` of the two names already is the demo. Defaulting missing exit to 0 is not evidence of exit 0. Wrapping `bundle install` / `Bundler.setup` to capture the two full names and the two exits would be a new harvest (live bundler, out of scope). Sibling `platid` already prints `hidden_by_exit0` from structured name/version/platform fields and returns rc=1 on mismatch. Do not mutate platident into platid to escape THIN_WRAPPER. Do not send it back to R1 to “make this more novel.”

That is why this is KILL, not MUTATE. The *question* (install materialized the ruby gem, setup searched for the locked linux gem, exit 0 hid the miss) is a real debugging object. This embodiment does not ask it of a lock, a gem index, or even of name+version+platform. It asks whether two strings the caller typed are unequal, and treats absent exit fields as the specimen. First-destroyer KEEP is not protection once that KEEP is shown to be labels on `a != b`.

Hardcoded ceiling:

- `hidden_by_exit0` ↔ `install_id != lookup_id` and two default-true flags
- `same_name_version` is a spectator; different name or version still harvests
- missing `install_exit` is success; missing `lookup_status` is miss
- swapped ids harvest the same bit; no install-vs-setup axis
- empty suffix and `-ruby` are both platform `ruby` and a harvest when the strings differ
- `0mq-1.0.0-java` platform prints `ruby`; hyphen prerelease platform is `rc1`
- harvest rc=0 (platid rc=1 on the same pair)
- lockfile / JSON / BOM / empty stdin refuse; extra tab in an id harvests
- `NUL` in `lookup_status` silently not-miss
- no bundler, no gem index, no lock ingest

Honor KILL. Dreamer ancestry is not protection. First KEEP is not protection. Do not grow a bundler runner to escape THIN_WRAPPER. Do not merge platident onto `platid` or onto `main`.

Archive stays under `lineages/candidate-platident/`.

KILL
