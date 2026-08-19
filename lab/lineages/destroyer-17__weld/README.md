# destroyer-17 — weld

Adversarial pass on **weld** (mutation-59, expr-first concat). Does not rewrite the victim. Does not implement a second inverse-printf walker.

Verdict: **mutate, do not kill.** Full writeup: `DESTROYER_WELD.md` (also `lab/judges/DESTROYER_WELD.md`). Transcript: `/tmp/destroy-weld/transcript.txt`.

## Primitive under attack

Inverse printf as a stream filter whose concat template may start at an expression. A later string operand proves the chain. Truncation is a prefix of an instance. Middle-drop stuffing is a miss.

## How to run

```bash
WELD=/Users/annenpolka/.grok/worktrees/annenpolka-brrr/subagent-01a01b85-3a6f-77f2-a6bf-caff208a0972/weld
chmod +x "$WELD"
"$WELD" --selftest          # still ok after the battery
python3 /tmp/destroy-weld/attack.py
./demo.sh                   # a few money-shot probes
```

Victim worktree is isolated. This worktree never merges to main.

## Three examples

### 1. Leftover proving string is not a fresh line (`cleaned + "\n"`)

```bash
$ rg -n -g '*.rs' 'cleaned \+' kizu | "$WELD" --templates - $'keep\n'
— no template for: keep   # rc=1

$ "$WELD" --templates concat.js $'\nDone.'
— no template for: Done.  # normalize_query stripped the proving newline
```

rime/caulk peel leftover. Lowering weld’s `visible < 4` would match every log line.

### 2. Middle-drop stuffing on sitbone siblings (fixture 7-hole still misses)

```bash
$ rg -n -g '*.swift' awayRecovered sitbone \
    | "$WELD" --templates - 'transition focused → idle awayRecovered=0'
  tmpl:  transition {oldPhase.rawValue} → {newPhase.rawValue} reason=… duration=…
  {newPhase.rawValue} = idle awayRecovered=0    # stuffed; rc=0
```

The 7-hole line honestly misses (`awayRecovered=` is a later witness). The duration=/site= siblings share the prefix and do not.

### 3. `fmt.Sprint` is not `+`

```bash
# Go runtime: fmt.Sprint(1, 2, " items") == "1 2 items"
$ "$WELD" --templates sprint.go '1 2 items'
  tmpl:  {n}{m} items
  {n} = 1 2 items
  unbound: {m}
```

Sprint spaces between non-strings never appear in the template. Adjacent empty parts collapse to one greedy hole.

## Dogfood

tenaoshi, kizu, sitbone. Full fence and `response() + "\nDone."` still bind. rustc locators still refuse. `MAX_FILE_BYTES` still omits a 2.1 MB godfile with no warning.
