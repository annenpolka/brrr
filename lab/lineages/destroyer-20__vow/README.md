# destroyer-20 — vow

Adversarial pass on **vow** (mutation-68): one failing assertion → two oaths (`EXPECTED-* vs ACTUAL-*`). Isolated worktree. Victim not rewritten. Not lees. Not visa-of-the-file.

Verdict: **mutate, do not kill.** Full report: [`DESTROYER_VOW.md`](DESTROYER_VOW.md).

## Install / run

Python 3.9+, stdlib only. Victim and peels are other worktrees; this tree only holds the report and the driver.

```bash
python3 destroy-vow/attack.py
# writes /tmp/destroy-vow/{transcript,results,fixtures,summary}
```

Or replay one hole against the victim:

```bash
VOW=/Users/annenpolka/.grok/worktrees/annenpolka-brrr/subagent-01a01b85-3a6f-77f2-a6bf-cb888759e773/vow.py
python3 "$VOW" --from-fail < /tmp/destroy-vow/fixtures/wrap_multiline.txt
python3 "$VOW" --apply --json /tmp/destroy-vow/fixtures/host_getenv.py
python3 "$VOW" --scan -C /Users/annenpolka/ghq/github.com/annenpolka/sitbone --porcelain
```

## Three examples

### 1. Same-line `# ran on` is an oath (gold own-line is not)

```bash
# gold: own-line comment stays OPEN / silent
python3 "$VOW" --json $VOW_ROOT/fixtures/comment_only.py
# status OPEN

# same-line comment becomes the expected slot
python3 "$VOW" --json /tmp/destroy-vow/followup/ran_on_sameline.py
# status BOUND  require HOME=/Users/annenpolka
```

### 2. HOST cannot name host role; `--side both` skips a portable golden

```bash
python3 "$VOW" --from-fail --apply < /tmp/destroy-vow/fixtures/host_fail.txt
# pair EXPECTED-OPEN vs ACTUAL-OPEN  host NEITHER  rc=0

python3 "$VOW" --from-fail --apply < $VOW_ROOT/fixtures/xctest_fail.txt          # rc=0
python3 "$VOW" --from-fail --apply --side both < $VOW_ROOT/fixtures/xctest_fail.txt  # rc=1
```

troth (peel) keeps `--apply` rc=0 on the XCTest dump (`legal OPEN`).

### 3. sitbone stays FIXTURE; Swift Testing dump is not a pair

```bash
python3 "$VOW" --scan -C /Users/annenpolka/ghq/github.com/annenpolka/sitbone --porcelain
# OPEN 21  FIXTURE 4  BOUND 0

python3 "$VOW" --from-fail < /tmp/destroy-vow/fixtures/swift_testing_dump.txt
# pair EXPECTED-OPEN vs ACTUAL-OPEN  actual empty
```

## Dogfood

Read-only: `/Users/annenpolka/ghq/github.com/annenpolka/{sitbone,kizu}`. Peels: troth `--apply` from host role, onset eras of ACTUAL-BOUND (sitbone/kizu `first-actual` none), writ `--list` (0 production on those trees).
