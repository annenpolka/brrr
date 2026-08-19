# destroyer-16 — xref

## Primitive

DUE-as-getenv-call-site-proof is a 24-insn window onto a `*getenv` / `*3env3var*` symbol in the native fat slice. An isolated cstring with a `bl` to `not_a_getenv` is DUE. A real `getenv` through `_wrap_dup` / `_env_to_dict` is not.

## Why this might not exist

DESTROYER_ASSAY asked for Mach-O xref so DUE would stop being an env-shaped token. xref did that and killed rustc’s 12k LLVM flood. The leftover is the proof itself: name-match, no hop, no `blr`, `kind_of` else-DUE, native slice only. lash/wad/prove peeled wrappers and CString; this pass is the column.

## How to run

```
XREF=/Users/annenpolka/.grok/worktrees/annenpolka-brrr/subagent-01a01b85-3a6f-77f2-a6bf-cb96e7158c54/xref ./demo.sh
python3 ./attack.py
```

## Empirical transcript

See `DESTROYER_XREF.md` and `/tmp/destroy-xref/transcript.txt`.

Gold still holds: compiled `getenv("ASSAY_GETENV_ONLY")` DUE; orphan default empty; `PYTHON_GIL` DUE; rustc due=38; `/bin/ls` `CLICOLOR_FORCE`.

Holes: `FALSE_DUE_NAME` DUE with no libc getenv; `WRAP_ENV_NAME` missing at `-O0`; `PYTHONHOME` LATENT; kizu release `--calls` empty / `--vs-program` occupancy BOTH; fat `FAT_X86_NAME` unaskable; `blr` miss; `--loose` KIND=DUE; GPU `STACK_SIZE` LATENT.

## Dogfood targets

- Homebrew python3 / libpython 3.14
- `/usr/bin/python3` (SIP xcselect)
- `/bin/ls` (fat arm64e)
- PATH rustc (rustup) and `$(rustc --print sysroot)/bin/rustc`
- kizu `src/` + `target/release/kizu`
- Homebrew git
- Compiled fixtures under `fixtures/src/`

## Surprises

- `-O2` inlines wrappers into DUE; `-O0` is the hole. CPython is compiled like `-O2` for `PYTHON_GIL` and like a wrapper for `PYTHONHOME`.
- `kind_of` has no neither: `--loose` is assay with a getenv badge.
- `--calls` on `not_a_getenv` prints `how=getenv`.

## Failures

- Did not inject DYLD (SIP + malloc reentry, already discarded).
- Did not re-run DESTROYER_ASSAY’s 12k flood as the object.
- `COLOR_FORCE ⊂ CLICOLOR_FORCE` substring check in an early script was a false alarm; `--names` on `/bin/ls` does not emit `COLOR_FORCE`.

## Suggested mutations

See DESTROYER_XREF.md kill/keep table: libc-getenv allowlist, one-hop wrappers, CString inlining, neither-KIND, fat slices, `blr`/SP, shim role, env-ish LATENT.

## Kill / keep

**Keep. Mutate.** Not `strings(1)`. DUE-as-proof has conceptual holes.
