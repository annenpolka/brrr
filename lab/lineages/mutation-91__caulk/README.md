# caulk

Inverse printf of a leftover remainder that is a **complete concat
operand**.

rime (mutation-79) reconstructs the next concat from a partial bind
(what already matched + prefix leftover / remainder). It still binds a
truncated proving string (`\nDon` of `\nDone.`). A leftover that is not
a complete operand is not inverse-printf.

`caulk` takes the same partial bind and emits the next concat only when
leftover equals a concat operand. Names bind. Middle-drop stuffing is a
miss. `cleaned + "\n"` after a contentful leftover still only hits when
leftover is the complete `\n` operand.

## Install / run

```bash
chmod +x caulk
./caulk --help
./demo.sh
```

Single Python 3.9+ file. No dependencies. Exit `0` hit, `1` miss, `2` error.

```bash
./caulk --templates src.js --matched '{"ok":true}' --remainder $'\nDone.'
./caulk --complete --templates src.js --matched '{"ok":true}' --remainder $'\nDon'
./caulk --templates src.js --matched '{"ok":true}' --prefix $'```json\n' --remainder $'\n```'
rg -n --type rust 'cleaned \+' src | ./caulk --matched 'keep' --remainder $'\n'
weld --templates src $'ts ERROR failed to spawn `git`' | ./caulk --templates src
```

Leftover mode is `--complete` by default. `--complete` also refuses
truncated fresh-line matches. Directories on `--templates` / `--files`
exit 2; the tool will not walk.

## Three examples

### 1. Truncated leftover is a miss; complete leftover binds

Source is `body + "\nDone."`. Complete remainder is the operand:

```bash
$ ./caulk --templates fixtures/src/leftover.js \
    --matched '{"ok":true}' --remainder $'\nDone.'
leftover.js:6:10: via=leftover
  prior: {"ok":true}
  rem:    \nDone.
  tmpl:  {body}\nDone.
  {body} = {"ok":true}
```

A prefix of that operand is not inverse-printf:

```bash
$ ./caulk --templates fixtures/src/leftover.js \
    --matched '{"ok":true}' --remainder $'\nDon'
— leftover is not a complete operand: \nDon  (of \nDone.)
```

rime still binds the truncated leftover, and prints both leftover remainder and rest-of-operand. Piped into caulk, leftover is `\nDon`, not `e.`:

```bash
$ rime --templates fixtures/src/leftover.js \
    --matched '{"ok":true}' --remainder $'\nDon'
  tmpl:  {body}\nDone.
  rem:    \nDon
  truncated: e.

$ rime ... --remainder $'\nDon' | ./caulk --templates leftover.js
— leftover is not a complete operand: \nDon  (of \nDone.)
```

### 2. Prefix leftover + remainder reconstruct a wrap when both operands are complete

```bash
$ ./caulk --templates fixtures/src/leftover.js \
    --matched '{"ok":true}' --prefix $'```json\n' --remainder $'\n```'
leftover.js:18:10: via=wrap
  tmpl:  ```json\n{response}\n```
  {response} = {"ok":true}
```

Truncated wrap remainder of the closing fence operand is a miss.
Truncated wrap prefix leftover of `"```json\n"` is a miss. Neither
leftover alone is a template query.

### 3. Newline-only suffix after a contentful leftover — only when leftover is complete

```bash
$ rg -n --type rust 'cleaned \+' kizu | ./caulk --templates - \
    --matched $'#!/bin/sh\necho keep' --remainder $'\n'
teardown.rs:86:52: via=leftover
  tmpl:  {cleaned}\n
  {cleaned} = #!/bin/sh
echo keep
```

`cleaned + "\n"` is leftover-only. Remainder `\n` is the complete
operand. Remainder `\nDon` is a truncated proving string of a longer
concat and does not steal `{cleaned}\n`. The same template against a
fresh line is a miss: a one-hole newline is not inverse-printf.
