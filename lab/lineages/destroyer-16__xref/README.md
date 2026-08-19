# destroyer-16 — xref call-site column

Adversarial pass on **xref** (mutation-69): DUE is claimed to be a getenv *call-site proof*. It is a 24-instruction window onto a symbol whose name ends in `getenv`, on the native fat slice, with no wrapper hop and no `blr`.

Victim: `/Users/annenpolka/.grok/worktrees/annenpolka-brrr/subagent-01a01b85-3a6f-77f2-a6bf-cb96e7158c54/xref` (v0.2.0). No rewrite. Report: `DESTROYER_XREF.md`.

## Install / run

```bash
chmod +x ./demo.sh
XREF=/Users/annenpolka/.grok/worktrees/annenpolka-brrr/subagent-01a01b85-3a6f-77f2-a6bf-cb96e7158c54/xref \
  ./demo.sh
python3 ./attack.py          # full battery → /tmp/destroy-xref/
```

Python 3.9+, `cc`, optional `rustc`. Writes `/tmp/destroy-xref/{bins,logs,transcript.txt}`.

## Examples

False DUE — a function *named* getenv is enough:

```bash
cc -O0 -fno-inline -o /tmp/false fixtures/src/false_getenv2.c
$XREF --app /tmp/false
# DUE  FALSE_DUE_NAME   call  getenv
# DUE  FORGET_ENV_NAME  call  getenv
# libc getenv is never called
```

Real getenv through a wrapper is not DUE (`PYTHONHOME` is the same object):

```bash
cc -O0 -o /tmp/wrap fixtures/src/wrap.c
$XREF --app /tmp/wrap
# DUE  DIRECT_ENV_NAME
# WRAP_ENV_NAME missing
```

`--loose` reprints orphans as DUE (KIND has no “neither”):

```bash
cc -o /tmp/orphan fixtures/src/false_getenv2.c  # or victim fixtures/xref/orphan.c
$XREF --app --loose /tmp/orphan
# KIND=DUE for packed/orphan tokens with evidence=string
```

## Verdict

**Mutate, do not kill.** Direct `getenv` / `PYTHON_GIL` / rustc tens-not-12k / `CLICOLOR_FORCE` survived. The proof does not.
