# hybrid-04 — sinter

## Primitive

A generated file both *claims* a parent (receipt) and *belongs* to a firing lot (recipe). sinter fuses those two witnesses into one object, then reports **RAGGED / STALE / CLEAN** with a typed why: **content**, **clock**, or **dirty-parent**.

## Why this might not exist

kiln reconstructs lots from headers, generator recipes, and pkl imports, then asks whether the claim still holds (DATED/SPLIT/BLIND/CLOCK/…). clutch reads the colophon a file already carries and asks whether siblings that cite the same parent were re-laid together (RAGGED/COLD/NOW/…). Developers who have both still have two reports.

The recurring annoyance is one question: *is this firing still one true firing, and if not, is that because the world moved, the clock lied, or a regen is in flight?* `ninja -d explain` needs a graph nobody wrote. `just spec-check` regenerates. `ls -l` lies after checkout. Git is silent when unit oracles last moved on 2026-07-20 and the spec on 2026-07-28.

Discarded as concatenation: `kiln | clutch`, or kiln's tag bag plus clutch's stamp-join. The object changed: membership is the join of testimony and recipe; the verb collapses the assay to three verdicts and three whys.

## How to run

From the worktree root:

```bash
./sinter --help
./sinter --selftest
./demo.sh
./sinter -C /Users/annenpolka/ghq/github.com/annenpolka/relico
./sinter -C /Users/annenpolka/ghq/github.com/annenpolka/relico why tests/unit/oracles_generated.test.ts
./sinter -C /Users/annenpolka/ghq/github.com/annenpolka/voidtrace --tsv
./sinter -C /Users/annenpolka/ghq/github.com/annenpolka/tenaoshi
```

Python 3.10+, stdlib only. `./sinter` is the CLI. Exit 0 on scan; `--check` exits 1 on RAGGED/STALE; usage errors exit 2.

## Empirical transcript

### Before the improvement (v0.1)

Fixture selftest held: partial regen → lot **RAGGED why=content**; headerless `extra/EPC-001.json` joined via=recipe; dirty parent left members CLEAN and the lot RAGGED why=dirty-parent; CLOCK vs clustered mtimes; 正本; stamp-join; justfile/AGENTS/Cargo.lock skipped.

kiln's claim still held on real trees: lots recovered from headers + recipes + pkl imports, and the claim was either true or not. clutch's claim still held: receipts grouped siblings git never recorded.

Real repos, first pass:

**relico** — the money shot, already one firing not two reports:

```
[RAGGED why=content] specs/notifier.pkl  5 files  fire 2026-07-20 19:43 .. 2026-07-28 10:18  ages 0–4
  via      both=5
  imports  specs/patterns.pkl
  STALE  content  tests/unit/oracles_generated.test.ts     fired 2026-07-20
  STALE  content  tests/e2e/oracles_generated.e2e.ts       fired 2026-07-20
  STALE  content  src-tauri/tests/oracles_generated.rs     fired 2026-07-28 08:28
  CLEAN  -        tests/renderer/oracles_generated.spec.ts fired 2026-07-28
  CLEAN  -        docs/SPEC.md                             fired 2026-07-28
```

Git is clean. Tests pass. Unit/e2e oracles are eight days behind the spec. `why` names `specs/notifier.pkl`, undeclared `specs/patterns.pkl`, and `tools/spec-gen.ts`. via=both: every member both testified and was listed by the recipe. kiln would have said DATED+SPLIT+BLIND. clutch would have said RAGGED ages 0–4. sinter answers the joint question: **RAGGED why=content**.

**tenaoshi** — 1 firing, **39** members, via both=3 recipe=36. Parent dirty. Members CLEAN. Lot **RAGGED why=dirty-parent**. Recipe pulled `contracts/testcases/*.json` (no colophon). clutch never sees those 36 files; kiln does; sinter assays the joined lot without painting members STALE (clutch v0.2 lesson).

Noise that drowned it:

- **-v dumped 36 identical JSON cases**, each repeating the same three dirty-parent reasons.
- **voidtrace dumped 59 pkl content reasons per member** (import closure), plus generator `*.test.ts` as if they were the source world. `tools/spec-gen/src/render.ts` showed up as a *reason* (correct) and drowned the 0-vs-29 rag under a wall of paths.
- Untracked recipe JSON printed as `fired -  dirty`.

### After the improvement (v0.2)

Forced by that first dogfood, not by a feature list:

1. **Reason grain.** Parent/declared sources named; generator files collapsed to one line; undeclared imports summarized (`56 undeclared import(s) (e.g. specs/rules/model.pkl)`). CLOCK stays a member why on top of content dating; the *firing* why prefers content.
2. **Recipe-only collapse.** More than two `via=recipe` siblings with the same verdict become `36 via=recipe under contracts/testcases/, 36 untracked`. The join is still visible. The flood is not.
3. **Dirty-parent wording.** If the member is itself dirty, say so (`member also dirty`) instead of lying `artifact not rewritten`.
4. **Generator tests are not the world.** `*.test.ts` under `tools/spec-gen/` no longer date every artifact.

Re-runs:

- **relico**: unchanged money shot. 5 members, all via=both, RAGGED why=content, patterns.pkl in the unit-oracle why. No CLOCK. No justfile.
- **tenaoshi**: 39 members, both=3 recipe=36, RAGGED why=dirty-parent, three testimony files + one recipe summary line. Oracle dirty and parent dirty, members not STALE.
- **voidtrace**: 27 members, via both=10 generated-md=2 recipe=13 stamp-join=2. **RAGGED why=content**, ages 0–29. `AI_UX.md` STALE (2026-07-29); `SPEC.md` / `ids.generated.ts` / stamp-joined `capabilities.generated.json` CLEAN (2026-08-20). 59 undeclared imports summarized, not dumped. `render.ts` is not a member. kizu/sitbone: 0 firings.

`./sinter why tests/unit/oracles_generated.test.ts` (relico):

```
STALE  tests/unit/oracles_generated.test.ts  why=content
  firing   RAGGED why=content  specs/notifier.pkl
  via      both  how=generated-by-from
  parent   specs/notifier.pkl
  recipe   tools/spec-gen.ts
  fired    2026-07-20 19:43  11d3ef841599
  imports  1  specs/patterns.pkl
  why:
    content specs/notifier.pkl  bytes changed since fire
    content tools/spec-gen.ts  bytes changed since fire
    content 1 undeclared import(s) (e.g. specs/patterns.pkl)
  siblings:
    STALE  content  src-tauri/tests/oracles_generated.rs     fired 2026-07-28 08:28
    STALE  content  tests/e2e/oracles_generated.e2e.ts       fired 2026-07-20 19:43
    CLEAN  -        docs/SPEC.md                             fired 2026-07-28 10:18
    CLEAN  -        tests/renderer/oracles_generated.spec.ts fired 2026-07-28 10:18
```

`./demo.sh` → 38 passed, 0 failed.

## Dogfood targets

- `/Users/annenpolka/ghq/github.com/annenpolka/relico` — split oracle firing
- `/Users/annenpolka/ghq/github.com/annenpolka/tenaoshi` — dirty regen + headerless recipe JSON
- `/Users/annenpolka/ghq/github.com/annenpolka/voidtrace` — deep pkl import world + receipts + stamp-join
- `/Users/annenpolka/ghq/github.com/annenpolka/kizu` — empty (negative)
- `/Users/annenpolka/ghq/github.com/annenpolka/sitbone` — empty (negative)
- `--selftest` fixture (partial regen, recipe-only member, dirty-parent, clock vs clustered mtimes, 正本, stamp-join)

## Surprises

- kiln's claim still holds after the join: the world is the import closure, and a *content-identical* regen does not move git last-commit. Relico unit oracles are STALE why=content even though a later spec-gen run rewrote them with the same bytes. clutch's COLD≠STALE distinction is the same fact, told as age; sinter tells it as why=content plus a CLEAN sibling.
- Headers name one pkl. The live world is `import "patterns.pkl"` (relico/tenaoshi) or fifty files under `specs/` (voidtrace). Undeclared imports are the default, not an edge case — but they are a *why*, not a verdict. BLIND is gone as a tag; it survives as `content 56 undeclared import(s)`.
- Dirty parent on tenaoshi is in-flight regen *and* a dirty oracle. v0.1 said `artifact not rewritten` while the member line said `dirty`. The two witnesses disagreed about the member; v0.2 makes the reason honest.
- `via=recipe` is the proof this is not clutch. tenaoshi's 36 JSON cases have no colophon and still belong. `via=both` on relico is the proof the two witnesses agreed.

## Failures

- CLOCK can still fire on a touched artifact whose world mtimes were backdated; checkout clusters drop out. Same residual as kiln: not a proof of "would make rebuild."
- Untracked recipe outputs have no fire commit. They join (the point) but age/content reasons fall back to dirty-parent.
- VoidTrace JSON schemas join via recipe (`package.json` is a slightly greasy first example). `*.schema.json` still carry no receipt.
- Does not re-run the generator. INERT (regen would be a no-op) vs STALE (regen would change bytes) is not distinguished without invoking `just spec-gen`.
- Conflicted generated files (voidtrace SPEC.md during a merge) are dirty members; multiple `sourceFingerprint` values in conflict markers are ignored for die election. Correct, a bit blunt.

## Suggested mutations

- `--repair`: emit a `just spec-gen` / per-projection command for STALE members only.
- Store/compare `sourceFingerprint` against a hash of the import closure without running pkl (voidtrace already stamps `sha256:` in JSON; currency=die vs byte is already detected).
- Watch mode: re-scan after `just spec-gen` and show the firing collapsing from RAGGED to CLEAN.
- Cross-projection clause-id skew as a firing column (relico unit tests ICN-* only; rust tests 80 clauses).

## Kill / keep

**Keep.** The object changed. kiln still reconstructs a firing from claims+recipes+imports (that claim holds). clutch still reads receipts as testimony (siblings with the same parent are one unrecorded generation event). sinter is the missing verb between them: one firing, witnessed two ways, assayed as RAGGED/STALE/CLEAN with why=content|clock|dirty-parent. Relico's eight-day split, tenaoshi's headerless JSON lot, and VoidTrace's 29-commit cold sibling are one command, and v0.2 came from a real dump of 59 pkl paths, not from concatenating flags.
