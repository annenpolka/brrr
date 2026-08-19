# splice

Inverse printf of **adjacent concatenations**, not format strings.

invert / stump / lede treat one template literal. DESTROYER already said it:
`"open " + path` is still not a template. `splice` flips that assumption.
A runtime string can be several adjacent literals and expressions joined
with `+` / `<>` / `fmt.Sprint`. The rest is lede's stream filter:
templates on stdin or `--templates FILE`, paste on argv, bind names.
Truncation is a **prefix of an instance**. Middle-drop stuffing is a miss.

## Install / run

```bash
chmod +x splice
./splice --help
./demo.sh
```

Single Python 3.10+ file. No dependencies. Exit `0` hit, `1` miss, `2` error.

```bash
rg -n --type js '"[^"]+"\s*\+' src | ./splice 'open /tmp/x: permission denied'
./splice --templates src/concat.go 'open /tmp/x: permission denied'
rg -n --type swift 'source graphemes' src | ./splice \
  'invalid original range for unit u1: 3..<8 (source graphemes: 12)'
```

Directories on `--templates` / `--files` exit 2; the tool will not walk.
`--exact` refuses leftover prefix/suffix and truncated matches.
`--complete` refuses only truncated matches (timestamp span still hits).
`--any --complete` is the first complete instance in a stream.

## Three examples

### 1. The destroyer paste — no sibling `fmt.Errorf` required

```bash
$ ./splice --templates fixtures/src/concat.js 'open /tmp/x: permission denied'
fixtures/src/concat.js:2:19: score=0.70 lang=js holes=2 via=full
  tmpl:  open {path}: {err}
  {path} = /tmp/x
  {err} = permission denied
```

lede on the same file extracts `holes=0 static=5 open ` and misses.

### 2. Wrapped `+` is one template (tenaoshi)

```bash
$ rg -n -g '*.swift' 'source graphemes' tenaoshi/Engine/Sources \
    | ./splice --templates - \
      'invalid original range for unit u1: 3..<8 (source graphemes: 12)'
EditPlanComposer.swift:70:20: holes=4 via=full
  tmpl:  invalid original range for unit {unitID}: {start}..<{end} (source graphemes: {sourceGraphemeCount})
  {unitID} = u1
  {start} = 3
  {end} = 8
  {sourceGraphemeCount} = 12
```

v0.1 (same-line only) split that into two fragments. v0.2 joins across the newline.

### 3. Prefix-of-instance still holds

```bash
$ ./splice --templates fixtures/src/concat.go 'failed read with EPERM'
— no template for: failed read with EPERM   # rc=1
# not {op} = read with EPERM

$ rg -n -g '*.swift' awayRecovered fixtures \
    | ./splice --templates - 'transition focused → idle awayRecovered=0'
— no template for: transition focused → idle awayRecovered=0
# not {to} = idle awayRecovered=0
```
