# weld

Inverse printf of **concatenations that may start at an expression**.

splice (mutation-34) splices `"lit" + expr + "lit"` from a leading string.
It misses `response() + "\nDone."` because the chain starts at an
expression; a later string operand is what proves concat. `weld` binds
named holes on those chains. Truncation is a **prefix of an instance**.
Middle-drop stuffing is a miss.

## Install / run

```bash
chmod +x weld
./weld --help
./demo.sh
```

Single Python 3.9+ file. No dependencies. Exit `0` hit, `1` miss, `2` error.

```bash
rg -n --type js 'response\(\)' src | ./weld $'{"ok":true}\nDone.'
./weld --templates src/concat.go '/tmp/x: permission denied'
rg -n --type swift 'source graphemes' src | ./weld \
  'invalid original range for unit u1: 3..<8 (source graphemes: 12)'
```

Directories on `--templates` / `--files` exit 2; the tool will not walk.
`--exact` refuses leftover prefix/suffix and truncated matches.
`--complete` refuses only truncated matches (timestamp span still hits).
`--any --complete` is the first complete instance in a stream.

## Three examples

### 1. Expression-first concat — splice misses, weld binds

```bash
$ ./weld --templates fixtures/src/concat.js $'{"ok":true}\nDone.'
fixtures/src/concat.js:10:10: score=0.71 lang=js holes=1 via=full
  tmpl:  {response}\nDone.
  {response} = {"ok":true}
```

Source is `response() + "\nDone."`. splice extracts the suffix literal
`\nDone.` with holes=0 and misses the paste.

### 2. Wrapped `+` is still one template (tenaoshi)

```bash
$ rg -n -g '*.swift' 'source graphemes' tenaoshi/Engine/Sources \
    | ./weld --templates - \
      'invalid original range for unit u1: 3..<8 (source graphemes: 12)'
EditPlanComposer.swift:70:20: holes=4 via=full
  tmpl:  invalid original range for unit {unitID}: {start}..<{end} (source graphemes: {sourceGraphemeCount})
  {unitID} = u1
  {start} = 3
  {end} = 8
  {sourceGraphemeCount} = 12
```

The wrap is a gap, not a stop. A one-line no-bindings guard would hide it.

### 3. Prefix-of-instance still holds

```bash
$ ./weld --templates fixtures/src/concat.go 'failed read with EPERM'
— no template for: failed read with EPERM   # rc=1
# not {op} = read with EPERM

$ rg -n -g '*.swift' awayRecovered fixtures \
    | ./weld --templates - 'transition focused → idle awayRecovered=0'
— no template for: transition focused → idle awayRecovered=0
# not {to} = idle awayRecovered=0
```
