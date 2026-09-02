# DESTROYER cssleft

Date: 2026-09-02 15:49 JST
RUN_ID: specimen-hdd-20260902-1112
Target (harvested): `/Users/annenpolka/ghq/github.com/annenpolka/brrr/lab-runs/specimen-hdd-20260902-1112/lineages/candidate-cssleft/cssleft`

sha256 `f22cb1af76ad1949b1554fe66ca96290f69fe787c291624e87a061a9616e7b6c` (3114 bytes, 98 lines). No `cssleft` worktree under `~/.grok/worktrees`. Parent `main` is `432f954`; the archive is untracked (`?? lineages/candidate-cssleft/`) and was not merged. Host Python 3.14.5. `webpack` is **not on PATH**. `npx` and `node` are on PATH (`/opt/homebrew/bin/npx`, `/opt/homebrew/bin/node`) and **were not executed**.

Origin claim (`CANDIDATE.md` / harvest `hdd-csshash` / specimen-090 leftover CSS `[contenthash]` / stale css-url after referenced PNG identity moved): leftover_url = `url_in_css != png_emitted`; leftover_css_hash = `css_name == prev_css_name`; leftover = either. Kind: USEFUL_COMPOSITION. Owned packet: Case C PNG bytes moved, CSS source still step-1, CSS name leftover `H_css1`, rendered CSS may still contain `H_png0`. Rejected: invented dep-analyzer / webpack watch transcripts. Constraint: owned labeled identity records. No webpack.

Happy path is real. Unit tests 4/4 pass (`python3 -m unittest discover -s tests -v` → `Ran 4 tests in 0.107s` `OK`, rc=0). `demo.sh` twice, live logs byte-identical to each other and to archived `demo-1.log` / `demo-2.log` (`cmp` rc=0, 625 bytes). That is not enough.

This candidate is a **THIN_WRAPPER** of two string comparisons on caller-typed names: `url != png` OR (`bool(prev)` AND `css == prev`). `inspect()` never reads a CSS file, never greps `url()`, never diffs `STATS_JSON` assets, never hashes a module, never looks at `[contenthash]`. Host replica of `inspect` + `format_report` is **byte-identical** to the CLI on leftover+rc for **27/27** parse-success host cases (`stdout_eq=True`). A python one-liner of those two comparisons matches leftover+rc on the three harvest shapes plus url-only / css-hash-only / hyphen-collision / same-name / omit-prev. awk of the four TSV keys matches the three load-bearing leftover columns on **12/12**. Non-empty token grid (`-`,`A`,`B`,`0`)⁴: **256/256** replica+thin. Decision: **KILL**.

CLI used below:

```text
CLI=/Users/annenpolka/ghq/github.com/annenpolka/brrr/lab-runs/specimen-hdd-20260902-1112/lineages/candidate-cssleft/cssleft
FIX=/Users/annenpolka/ghq/github.com/annenpolka/brrr/lab-runs/specimen-hdd-20260902-1112/lineages/candidate-cssleft/fixtures
S090=/Users/annenpolka/ghq/github.com/annenpolka/brrr/lab-runs/specimen-hdd-20260902-1112/specimens/specimen-090
```

No merge onto `main`. No webpack. Do not grow a webpack runner, a `STATS_JSON` walker, or a `url()` / `[contenthash]` parser to escape THIN_WRAPPER. Do not send webpack theater back to R1. First HARVEST is not protection. Same shape as Honor-KILLed peerleft / pnpbuilt / fingerid: leftover = two caller-typed string comparisons.

---

## What still works

Owned leftover, owned fresh, owned css-moved-url-ok, unseen `W_css1` copies of leftover, and any other TSV whose rows are already `css_name` / `url_in_css` / `png_emitted` / optional `prev_css_name`, **when the question is only whether two caller strings differ and/or two other caller strings are equal**.

```bash
python3 "$CLI" "$FIX/090-leftover.rec"
echo rc=$?
```

```text
css_name	H_css1
url_in_css	H_png0
png_emitted	H_png1
prev_css_name	H_css1
leftover_url	yes
leftover_css_hash	yes
leftover	yes
rc=1
```

126 bytes. Stderr empty. Owned fresh: `url_in_css	H_png0` / `png_emitted	H_png0` / `prev_css_name	-` / leftover no, rc=0, 118 bytes. Owned css-only (case B): `css_name	H_css1` / `prev_css_name	H_css0` / urls both `H_png0` / leftover no, rc=0, 123 bytes. Unseen `W_css1` leftover: same seven rows with those tokens, leftover yes, rc=1.

Symlink, FIFO (writer concurrent), process substitution, filename with a space, CRLF, Unicode names `依存1` / `画像0`: leftover yes, rc=1. 10000 comment lines plus leftover names: leftover yes, rc=1, stdout **126** bytes, ~0.030s. Same 10000 plus fresh names: leftover no, rc=0, 118 bytes, ~0.027s. Missing path / directory / invalid UTF-8 / BOM / binary NUL / unknown field / origin split / JSON / CSS source / STATS_JSON: `cssleft: …` rc=1. No args / extra positional: argparse rc=2.

That is the whole useful surface. It is also what `test "$url" != "$png" || { test -n "$prev" && test "$css" = "$prev"; }` already does on four caller-typed strings.

---

## Implementation

`inspect()` in full:

```python
def inspect(fields: dict[str, str]) -> dict:
    css = fields["css_name"]
    url = fields["url_in_css"]
    png = fields["png_emitted"]
    prev = fields.get("prev_css_name") or ""
    leftover_url = url != png
    leftover_css = bool(prev) and css == prev
    leftover = leftover_url or leftover_css
    return {
        "css_name": css,
        "url_in_css": url,
        "png_emitted": png,
        "prev_css_name": prev or "-",
        "leftover_url": leftover_url,
        "leftover_css_hash": leftover_css,
        "leftover": leftover,
    }
```

`inspect.co_names` is `('get', 'bool')`. `inspect.co_varnames` is `('fields', 'css', 'url', 'png', 'prev', 'leftover_url', 'leftover_css', 'leftover')`. `inspect.co_consts` includes `'css_name'`, `'url_in_css'`, `'png_emitted'`, `'prev_css_name'`, `''`, `'-'`. dis: `COMPARE_OP (!=)` of url vs png, then `bool(prev)` AND `COMPARE_OP (==)` of css vs prev, then OR. There is no prefix, no `url()`, no contenthash, no STATS_JSON, no webpack, no PNG bytes, no CSS source.

`parse_record` accepts keys `css_name` / `url_in_css` / `png_emitted` / `prev_css_name` only. First tab splits key/value; `rest.strip()` is the value. Unknown keys raise. `css_name`, `url_in_css`, `png_emitted` are required. leftover never reads a file except those four strings. `prev_css_name` omitted prints as `-`; leftover_css uses `""`.

`demo.sh` already names the nearest operation: `leftover is url_in_css != png_emitted and/or css_name == prev_css_name`.

Tests never hit leftover_url-only, leftover_css-hash-only, same-name both sides, hyphen collision, omit-prev, extra tabs, origin bytes, stdin, or the token grid. Four tests: owned leftover, owned fresh, owned case B, missing file.

---

## Attacks

### 1. THIN_WRAPPER of `url != png` OR `css == prev`

Host replica of `inspect` + `format_report` (exec of the archive file, no package import) is byte-identical to CLI stdout on the harvest shapes:

| case | cli_rc | replica_rc | stdout_eq | leftover_thin | leftover_url | leftover_css_hash |
| --- | ---: | ---: | --- | --- | --- | --- |
| owned leftover (C) | 1 | 1 | True | True | yes | yes |
| owned fresh (A) | 0 | 0 | True | False | no | no |
| owned css-only (B) | 0 | 0 | True | False | no | no |
| unseen widget leftover | 1 | 1 | True | True | yes | yes |
| stdin leftover | 1 | 1 | True | True | yes | yes |

Python one-liner, no `inspect` import, labeled names only:

```bash
python3 -c '
import sys
fields={}
for raw in open(sys.argv[1], encoding="utf-8"):
    line=raw.strip()
    if not line or line.startswith("#") or "\t" not in line: continue
    k,r=line.split("\t",1)
    fields[k.strip()]=r.strip()
css=fields["css_name"]; url=fields["url_in_css"]; png=fields["png_emitted"]
prev=fields.get("prev_css_name") or ""
print("leftover_url", url != png)
print("leftover_css_hash", bool(prev) and css == prev)
print("leftover", (url != png) or (bool(prev) and css == prev))
' "$FIX/090-leftover.rec"
```

```text
leftover_url True
leftover_css_hash True
leftover True
```

Same two comparisons vs the CLI leftover rows and rc: owned leftover / fresh / css-only / url-only / css-hash-only / hyphen-collision / same-name / omit-prev all match. Non-empty token grid of four names: **256/256**. Empty-field pairs are `expected key<TAB>value` because `line.strip()` eats a trailing tab (`css_name\t` becomes `css_name`). That is not a webpack walker.

awk of the three load-bearing leftover columns:

```awk
BEGIN{FS="\t"}
/^#/ {next}
NF<2 {next}
{
  k=$1; v=$2
  gsub(/^[ \t]+|[ \t]+$/, "", k)
  gsub(/^[ \t]+|[ \t]+$/, "", v)
  f[k]=v
}
END{
  leftover_url = (f["url_in_css"] != f["png_emitted"])
  leftover_css = (f["prev_css_name"] != "" && f["css_name"] == f["prev_css_name"])
  leftover = leftover_url || leftover_css
  printf "leftover_url\t%s\n", leftover_url?"yes":"no"
  printf "leftover_css_hash\t%s\n", leftover_css?"yes":"no"
  printf "leftover\t%s\n", leftover?"yes":"no"
}
```

owned leftover / fresh / css-only / url-only / css-hash-only / omit-prev / hyphen-collision / unseen / unicode / same-name / prev-zero / huge: `awk_eq_cli_loadbearing=True` **12/12**. The echoed name columns are not in the leftover bits. They do not vote.

Nearest ordinary workflow, host-executed:

```bash
grep -n H_css1 "$FIX/090-leftover.rec"; echo leftover_css_rc=$?
grep -n H_png0 "$FIX/090-leftover.rec"
grep -n H_css1 "$FIX/090-fresh.rec"; echo fresh_css_rc=$?
grep -n H_png0 "$FIX/090-fresh.rec"
```

```text
2:css_name	H_css1
5:prev_css_name	H_css1
leftover_css_rc=0
1:# Case C: PNG bytes moved; CSS source still step-1; url leftover H_png0
3:url_in_css	H_png0
fresh_css_rc=1
3:url_in_css	H_png0
4:png_emitted	H_png0
```

`demo.sh` says “diff STATS_JSON names; grep url() in CSS”. There is no STATS_JSON and no CSS file in the fixtures. grep of `H_css1` hits leftover because the caller wrote that token twice (`css_name` and `prev_css_name`). grep of `H_png0` hits leftover because the caller wrote it as `url_in_css` and in a comment. leftover is whether they also typed two different strings for url vs png, and/or the same string for css vs prev.

Shell of the owned leftover pair:

```bash
test "$url" != "$png" || { test -n "$prev" && test "$css" = "$prev"; }
# leftover yes; rc=1
```

Owned fresh (`prev` is `-`, urls equal, css `H_css0` ≠ `-`): leftover no, rc=0.

Constitution: a THIN_WRAPPER does not gain extra TSV rows (`css_name`, `url_in_css`, `png_emitted`, `prev_css_name` reprints) to escape classification. Those rows are the inputs. leftover does not hash them.

### 2. leftover_url-only; leftover_css_hash-only; OR is the harvest bit

Host-executed, urls disagree, css ≠ prev:

```text
css_name	H_css1
url_in_css	H_png0
png_emitted	H_png1
prev_css_name	H_css0
leftover_url	yes
leftover_css_hash	no
leftover	yes
rc=1
```

Urls agree, css == prev:

```text
css_name	H_css1
url_in_css	H_png1
png_emitted	H_png1
prev_css_name	H_css1
leftover_url	no
leftover_css_hash	yes
leftover	yes
rc=1
```

Owned Case C is both bits yes. Either bit alone is leftover yes, rc=1. The harvest sentence “leftover = leftover_url or leftover_css_hash” is the CLI. Tests never hit the split. Swap of url vs png (`H_png1` in css, `H_png0` emitted) is leftover_url yes: inequality, not “stale vs new.”

### 3. leftover_css_hash is “typed the same nonempty prev”

Host-executed, urls match, css_name equals prev_css_name `H_css0` (nothing “moved”):

```text
css_name	H_css0
url_in_css	H_png0
png_emitted	H_png0
prev_css_name	H_css0
leftover_url	no
leftover_css_hash	yes
leftover	yes
rc=1
```

Same leftover yes for `css_name	0` / `prev_css_name	0` with matching urls, and for `css_name	X` / `url_in_css	X` / `png_emitted	X` / `prev_css_name	X`. leftover_css_hash fires because the caller typed the same nonempty string twice. It is not a compile delta.

Omit `prev_css_name` with leftover urls:

```text
css_name	H_css1
url_in_css	H_png0
png_emitted	H_png1
prev_css_name	-
leftover_url	yes
leftover_css_hash	no
leftover	yes
rc=1
```

`prev` printed `-` is the format default for `""`. leftover_css uses `""`, so leftover_css_hash is no. Omit prev with matching urls: leftover no, rc=0. The previous-compile name can be absent and leftover_url still harvests.

Hyphen collision: `css_name	-` / `prev_css_name	-` / matching urls:

```text
css_name	-
url_in_css	H_png0
png_emitted	H_png0
prev_css_name	-
leftover_url	no
leftover_css_hash	yes
leftover	yes
rc=1
```

`bool("-")` is true and `css == prev`. Format’s missing-prev sticker `-` is a leftover_css_hash hit if the caller also types `-` as the CSS name. Owned fresh is leftover no only because `H_css0 != "-"`.

Owned case B is leftover_css_hash no because the caller typed `H_css1` vs `H_css0`. The CLI does not know CSS source moved.

Duplicate `prev_css_name` last-wins: `H_css0` then `H_css1` against `css_name	H_css1` and matching urls → leftover_css_hash yes, rc=1.

### 4. Extra tabs; empty field

`parse_record` takes `rest.strip()` after the first tab. Extra columns after the name stay in the value: `url_in_css	H_png0	extra` → token `H_png0\textra` ≠ `H_png1` → leftover_url yes, rc=1. Replica `stdout_eq=True`. The leftover bit still follows `!=`.

An extra tab **before** the value (`url_in_css\t\tH_png0`): `strip()` eats the leading tab; token is `H_png0`; leftover_url vs `H_png1` still yes, rc=1. Empty value (`prev_css_name\t\n`): `line.strip()` eats the trailing tab; `expected key<TAB>value`, rc=1, no TSV. Empty `css_name	` is the same parse error.

Spaces instead of a tab: `expected key<TAB>value`, rc=1, no TSV.

### 5. Stdin

`-` is stdin. Owned leftover body on the pipe: leftover TSV, rc=1, replica `stdout_eq=True`. Empty stdin: `cssleft: <stdin>: need css_name, url_in_css, png_emitted`, rc=1. `/dev/stdin` leftover: leftover yes, rc=1. Process substitution `<(cat leftover.rec)`: leftover yes, rc=1. Fine as a one-file tool. The bit is still two caller-typed comparisons.

Argv-less / extra positional: argparse rc=2, pipe ignored.

### 6. Origin bytes refuse; webpack artifacts are not parsed

Specimen `leftover_identity_split.txt` as record: `expected key<TAB>value`, rc=1. JSON `{"css_name":"H_css1",…}`: same parse error, rc=1. CSS source `.a { background: url("./logo.png"); }`: same. STATS_JSON `{"assets":[{"name":"H_css1"},{"name":"H_png1"}]}`: same. `contenthash	H_css1`: `unknown field 'contenthash'`, rc=1. `Css_name	H_css1`: `unknown field 'Css_name'`, rc=1. Missing `png_emitted`: `need css_name, url_in_css, png_emitted`, rc=1. Comments-only: same need-fields, rc=1. UTF-8 BOM: `unknown field '\ufeffcss_name'`, rc=1. Embedded NUL: `unknown field '\x00url_in_css'`, rc=1. Invalid UTF-8: codec error, no leftover TSV, rc=1.

The harvest presence test is “diff two STATS_JSON asset names and grep url() in the CSS file.” Host-executed, those origin bytes are not TSV. leftover no (no TSV). The caller must already have split `H_css1` / `H_png0` / `H_png1` into labeled rows. That split is the product. The CLI reprints it.

`url_in_css	url(H_png0)` vs `png_emitted	H_png1`: leftover_url yes because the strings differ. The `url()` wrapper is not parsed. Hashed filenames `style.abc.css` / `logo.old.png` / `logo.new.png` leftover the same way any other four strings leftover.

### 7. Huge dump; still two comparisons

10000 `#` lines plus leftover names: leftover yes, rc=1, stdout **126** bytes, 0.030s. Same 10000 plus fresh names: leftover no, rc=0, 118 bytes, 0.027s. No cap. No CSS dumped. The useful bit is still `url != png or css == prev`.

Missing path: `No such file or directory`, rc=1. Directory: `Is a directory`, rc=1. Duplicate `css_name` last-wins (`H_css0` then `H_css1` on owned leftover urls → leftover_css_hash yes). Tests never hit duplicates, origin, stdin, extra tabs, leftover_url-only, leftover_css-hash-only, hyphen collision, or omit-prev.

---

## Primitive

Reality-stripped operation: parse one TSV file of `css_name` / `url_in_css` / `png_emitted` plus optional `prev_css_name`; leftover_url iff url ≠ png; leftover_css_hash iff prev is nonempty and css == prev; leftover iff either; print seven TSV rows; rc=1 iff leftover. The four name columns are echoed inputs. Missing prev prints as `-` and does not vote.

Nearest ordinary workflow: `test "$url" != "$png"` and `test "$css" = "$prev"` on the names the caller already labeled, or `python3 -c 'print((url!=png) or (prev and css==prev))'`, or the awk above. Observable capability lost if cssleft vanishes: **none**. The excerpt already is the input. The leftover-vs-moved-PNG join is still a hand comparison after the caller typed `H_png0` vs `H_png1` and `H_css1` vs `H_css1`. grep of the CSS filename hits both compiles because the fixtures contain that token on both `css_name` and `prev_css_name`.

That is why this is KILL, not MUTATE. The *question* (after a referenced PNG `[contenthash]` moved, does the CSS chunk still name `H_css1` and/or does `url()` still name `H_png0` — grep of the CSS filename hits both compiles; the miss is url vs emitted PNG) is a real debugging object. This embodiment does not ask it of webpack, STATS_JSON, or a CSS file. It asks `url != png or css == prev` on caller-labeled tokens. Adding a webpack watch runner, a `CssUrlDependency.updateHash` walk, or ingesting `data.url["css-url"]` vs `assetPath`, would be implementing the webpack theater the harvest rejected, and would be a new harvest, not a patch of this 98-line `!=` / `==`. Constitution: a THIN_WRAPPER does not gain exotic features to escape classification. Worker rule: do not send THIN_WRAPPER back to R1 with “make this more novel.” First HARVEST is not protection. Honor-KILLed peerleft is leftover = in B not in A on two caller-labeled regions. Honor-KILLed pnpbuilt is leftover = flag A and not flag B. Honor-KILLed fingerid is leftover = three string equalities. This is leftover = two string comparisons on caller-typed names.

Hardcoded ceiling:

- leftover iff url ≠ png OR (prev nonempty AND css == prev); echoed names do not vote
- leftover yes with leftover_url-only (css ≠ prev) or leftover_css_hash-only (urls equal)
- leftover yes with omitted prev when urls disagree; leftover_css_hash no, prev printed `-`
- leftover_css_hash yes when the caller types the same nonempty string twice (same-name, `0`/`0`, `X`/`X`)
- hyphen collision: css `-` and prev `-` is leftover_css_hash yes even with matching urls
- owned fresh is leftover no because `H_css0 != "-"` and urls equal
- owned case B is leftover no because the caller typed different css vs prev
- url vs png swap is leftover_url yes (inequality, not stale-vs-new)
- `url(H_png0)` is a different string, not a parsed `url()`
- extra tab after the value stays in the token; extra tab before the value is `strip()`ped
- empty field after strip is `expected key<TAB>value`
- `-` is stdin; empty stdin is `need css_name, url_in_css, png_emitted`
- origin split / JSON / CSS source / STATS_JSON / `contenthash` / `Css_name` / BOM / NUL refuse
- 10k-comment leftover still 126-byte sticker, ~0.030s
- rc=1 on leftover **or** parse/IO; argparse rc=2 on missing argv
- Dreamer webpack watch was rejected; this is that leftover, reduced to the harvest sentence as `!=` / `==`

Honor KILL. Dreamer ancestry is not protection.

Do not grow a webpack runner, a `STATS_JSON` walker, or a `url()` / `[contenthash]` parser to escape THIN_WRAPPER. Do not merge this join onto `main`. No webpack. Do not send webpack theater back to R1.

---

KILL
