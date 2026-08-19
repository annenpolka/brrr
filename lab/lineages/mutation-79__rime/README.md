# rime

Inverse printf of a **leftover remainder**, not a fresh log line.

weld (mutation-59) binds concat that starts at an expression
(`response() + "\nDone."`). It still fails when the proving string is a
leftover *suffix* of a previous match or a `truncated:` remainder: the
query is treated as a new log line, `normalize` strips `\nDone.` to
`Done.`, and a one-hole `expr + "\n"` is rejected because it would
match every line.

`rime` takes a **partial bind** (what already matched + prefix leftover /
remainder) and emits the next concat template that consumes that leftover.
Names bind. Middle-drop stuffing is a miss. A one-hole `expr + "\n"` that
matches every log line is not a template.

## Install / run

```bash
chmod +x rime
./rime --help
./demo.sh
```

Single Python 3.9+ file. No dependencies. Exit `0` hit, `1` miss, `2` error.

```bash
./rime --templates src.js --matched '{"ok":true}' --remainder $'\nDone.'
./rime --templates src.js --matched '{"ok":true}' --prefix $'```json\n' --remainder $'\n```'
rg -n --type rust 'cleaned \+' src | ./rime --matched 'keep' --remainder $'\n'
weld --templates src $'ts ERROR failed to spawn `git`' | ./rime --templates src
```

Directories on `--templates` / `--files` exit 2; the tool will not walk.

## Three examples

### 1. Leftover suffix is the proving string — weld misses, rime binds

```bash
$ ./rime --templates fixtures/src/leftover.js \
    --matched '{"ok":true}' --remainder $'\nDone.'
leftover.js:6:10: via=leftover
  prior: {"ok":true}
  rem:    \nDone.
  tmpl:  {body}\nDone.
  {body} = {"ok":true}
```

Source is `body + "\nDone."`. weld on the leftover remainder:

```bash
$ weld --templates fixtures/src/leftover.js $'\nDone.'
— no template for: Done.    # rc=1
```

The remainder is not a fresh log line.

### 2. Prefix leftover + truncated remainder reconstruct a wrap

```bash
$ ./rime --templates fixtures/src/leftover.js \
    --matched '{"ok":true}' --prefix $'```json\n' --remainder $'\n```'
leftover.js:18:10: via=wrap
  tmpl:  ```json\n{response}\n```
  {response} = {"ok":true}
```

The two leftovers are the proving strings of
`"```json\n" + response() + "\n```"`. Neither leftover alone is a
template query.

### 3. Newline-only suffix after a contentful leftover

```bash
$ rg -n --type rust 'cleaned \+' kizu | ./rime --templates - \
    --matched $'#!/bin/sh\necho keep' --remainder $'\n'
teardown.rs:86:52: via=leftover
  tmpl:  {cleaned}\n
  {cleaned} = #!/bin/sh
echo keep
```

`cleaned + "\n"` is leftover-only. The same template against a fresh
line is a miss: a one-hole newline is not inverse-printf.
