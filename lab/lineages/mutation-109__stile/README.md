# stile

Inverse printf whose **proving string must be distinctive**.

weld (mutation-59) welds concat backward from a later string operand.
A 4-char suffix (`{body}abcd`) still matched every log line, and an
incomplete fence (` ```json\n{"ok":true} ` vs `"\n```"`) was a truncated
success. `stile` refuses a proving string that is only a newline, a
fence marker, or fewer than 4 distinctive static chars — unless there
are ≥2 expression holes. Incomplete fence leftovers refuse (caulk
complete operand). `response() + "\nDone."` still binds. Middle-drop
stuffing is still a miss.

## Install / run

```bash
chmod +x stile
./stile --help
./demo.sh
```

Single Python 3.9+ file. No dependencies. Exit `0` hit, `1` miss, `2` error.

```bash
rg -n --type js 'response\(\)' src | ./stile $'{"ok":true}\nDone.'
./stile --templates src/concat.go '/tmp/x: permission denied'
rg -n --type swift 'source graphemes' src | ./stile \
  'invalid original range for unit u1: 3..<8 (source graphemes: 12)'
```

Directories on `--templates` / `--files` exit 2; the tool will not walk.
`--exact` refuses leftover prefix/suffix and truncated matches.
`--complete` refuses only truncated matches (timestamp span still hits).

## Three examples

### 1. Expression-first concat still binds; a 4-char suffix does not

```bash
$ ./stile --templates fixtures/src/concat.js $'{"ok":true}\nDone.'
fixtures/src/concat.js:10:10: score=0.71 lang=js holes=1 via=full
  tmpl:  {response}\nDone.
  {response} = {"ok":true}

$ ./stile --templates fixtures/src/thin.go 'ERROR worker crashed abcd'
— no template for: ERROR worker crashed abcd   # rc=1
# not {body} = ERROR worker crashed
```

`response() + "\nDone."` is inverse-printf. `body + "abcd"` is every log
line ending in four letters. The 4-char floor is gone.

### 2. Incomplete fence leftover refuses; the full fence binds

```bash
$ ./stile --templates fixtures/src/concat.swift $'```json\n{"ok":true}\n```'
  tmpl:  ```json\n{response}\n```
  {response} = {"ok":true}

$ ./stile --templates fixtures/src/concat.swift $'```json\n{"ok":true}'
— no template for: ```json
{"ok":true}   # rc=1
# not truncated: \n```
```

The closer `"\n```"` is a proving operand. A leftover that is not that
complete operand is not inverse-printf (caulk). An unclosed
`"```json\n" + response()` does not swallow the closer into `{response}`.

### 3. Prefix-of-instance still holds; ≥2 holes keep a short proving string

```bash
$ ./stile --templates fixtures/src/concat.go 'failed read with EPERM'
— no template for: failed read with EPERM   # rc=1

$ ./stile --templates fixtures/src/thin.go --extract
thin.go:16:12: lang=go holes=2 static=1 weld {a}:{b}
# a + ":" + b is two expression holes; ":" is enough
```
