# candidate-11 — rift

## Primitive
`rift` reports identifier-level conflicts (def vs use, deleted def vs new use, split-brain defs) between two changesets that `git merge` would accept as clean.

## Why this might not exist
Git merge is textual. Semantic merge research exists, but the daily Unix verb is missing: given two refs, emit the crossed definition/use edits a clean merge would hide, with an exit code for CI. `git merge-tree` tells you about overlapping hunks, not about `parse_config`'s signature changing on one branch while a callsite changes on the other.

Privately listed four primitives; discarded the two most conventional (`because`: sibling hunks of a blame line; `skew`: def/use age gap). Not chosen: `ought` (structural holes by analogy). Implemented `rift`.

## How to run
From the worktree root:

```bash
./rift --self-test
./demo.sh
./rift -C /path/to/repo main
./rift --diffs a.diff b.diff
./rift --audit 20
```

Exit 0 = no rifts, 1 = rifts, 2 = error.

## Empirical transcript

### Before the improvement (v0.1)

Synthetic def-use, merge-tree clean:

```
$ ./rift --color never -C syn side-a side-b
rift: 6af1d46e vs 25385edb  base 3ec3142f
git merge-tree: clean
1 rift(s)

def-use  parse_config  hidden
  A  def + src/parse.rs:1  pub fn parse_config(s: &str, timeout: u64) -> Config {
  A  def - src/parse.rs:1  pub fn parse_config(s: &str) -> Config {
  B  use + src/cli.rs:2  let cfg = parse_config(raw, None);
  B  use - src/cli.rs:2  let cfg = parse_config(raw);
```

kizu `--audit` looked successful and empty, but was lying: `git log --format='%H %P %s'` parsed with `line.split(" ", 2)`, so the second parent was swallowed into the subject. Every merge was skipped with no message.

```
$ ./rift --color never -C kizu --audit 8
rift: audited merges, 0 rifts
```

sitbone dogfood (clone; extra `flush:` param vs a new callsite) produced a true hit *and* a false positive from git's Swift funcname header (the enclosing class):

```
def-use  JSONSessionStore  hidden
  A  def ~ Sources/SitboneData/JSONSessionStore.swift:40  public final class JSONSessionStore: SessionStoreProtocol, @unchecked Sendable {
  B  use + Sources/SitboneData/RiftProbe.swift:2  static func ping(_ store: JSONSessionStore) async throws {

def-use  saveCumulative  hidden
  A  def + .../JSONSessionStore.swift:40  public func saveCumulative(_ record: CumulativeRecord, flush: Bool) async throws {
  A  def - .../JSONSessionStore.swift:40  public func saveCumulative(_ record: CumulativeRecord) async throws {
  B  use + .../RiftProbe.swift:3  try await store.saveCumulative(CumulativeRecord())
```

kizu clone, `scan_scars` signature vs new callsite in `src/paths.rs` — this part already worked:

```
def-use  scan_scars  hidden
  A  def + src/hook/scan.rs:22  pub fn scan_scars(paths: &[PathBuf], timeout_ms: u64) -> Vec<ScarHit> {
  A  def - src/hook/scan.rs:22  pub fn scan_scars(paths: &[PathBuf]) -> Vec<ScarHit> {
  B  use + src/paths.rs:175  let _ = crate::hook::scan_scars(paths);
```

### After the improvement (v0.2)

Fixes: (1) parse merge parents as 40-char SHAs / tab-separated `%H%x09%P%x09%s`; (2) hunk-header defs only from callable intros (`fn`/`func`/`function`/`def`), not enclosing `class`/`struct`; (3) print the ref name next to the abbreviated SHA; (4) `--audit` summary of two-sided vs one-sided vs skipped.

sitbone, same branches — class noise gone, method remains:

```
$ ./rift --color never -C sitbone-clone rift-a rift-b
rift: rift-a (55e9967b) vs rift-b (c91090ae)  base 094769d5
git merge-tree: clean
1 rift(s)

def-use  saveCumulative  hidden
  A  def + Sources/SitboneData/JSONSessionStore.swift:40  public func saveCumulative(_ record: CumulativeRecord, flush: Bool) async throws {
  A  def - Sources/SitboneData/JSONSessionStore.swift:40  public func saveCumulative(_ record: CumulativeRecord) async throws {
  B  use + Sources/SitboneData/RiftProbe.swift:3  try await store.saveCumulative(CumulativeRecord())
```

kizu `--audit` now tells the truth:

```
$ ./rift --color never -C kizu --audit 8
rift: audited 8 merge(s): 0 two-sided, 8 one-sided, 0 skipped, 0 rift(s)
```

`--audit` on a synthetic two-sided merge finds the rift:

```
$ ./rift --color never -C syn --audit 3
rift: audited 1 merge(s): 1 two-sided, 0 one-sided, 0 skipped, 1 rift(s)
# merge 45efeebd  merge sides
rift: 45efeebd^1 (97e55ac4) vs 45efeebd^2 (f9e8e0ba)  base 6f2efac4
git merge-tree: clean
1 rift(s)

def-use  parse_config  hidden
  A  def + src/parse.rs:1  pub fn parse_config(...) timeout: u64 ...
  B  use + src/cli.rs:1  fn main() { let cfg = parse_config(raw, None); }
```

voidtrace (TypeScript) clone, `createWorldState` extra param vs new file callsite:

```
rift: rift-a (f970a085) vs rift-b (e243755a)  base ce44c93c
git merge-tree: clean
1 rift(s)

def-use  createWorldState  hidden
  A  def + packages/kernel/src/world-state.ts:34  export function createWorldState(..., epochMs = 0): WorldState {
  A  def - packages/kernel/src/world-state.ts:34  export function createWorldState(entities: Iterable<WorldEntity> = []): WorldState {
  B  use + packages/kernel/src/rift-probe.ts:1  import { createWorldState } from "./world-state.ts";
  B  use + packages/kernel/src/rift-probe.ts:2  export function riftProbe() { return createWorldState([]); }
```

`./demo.sh` — 18 checks, exit 0.

## Dogfood targets
- Synthetic git fixtures (def-use, delete-use, dup-def, ugly unicode/space filenames, lockfiles, `node_modules`, two-sided merge audit)
- `/Users/annenpolka/ghq/github.com/annenpolka/kizu` (clone + read-only `--audit`)
- `/Users/annenpolka/ghq/github.com/annenpolka/sitbone` (clone + read-only `--audit`)
- `/Users/annenpolka/ghq/github.com/annenpolka/voidtrace` (clone + read-only `--audit`)
- `/Users/annenpolka/ghq/github.com/annenpolka/tenaoshi` (read-only `--audit`: no merge commits)
- `/Users/annenpolka/ghq/github.com/annenpolka/skills` (read-only one-sided `HEAD~3 HEAD`)

## Surprises
- Every GitHub PR merge in kizu and sitbone is one-sided: parent1 equals merge-base. Historical `--audit` on those repos is structurally empty even with a correct parser.
- Git funcname headers for Swift name the *class*, not the method. Treating that as a definition change flags every type mention on the other branch.
- `git merge-tree --write-tree --name-only -z` returns the tree OID then conflicted paths; exit 1 means textual conflict, which rift uses to mark `hidden` vs `also-text`.

## Failures
- v0.1 `--audit` never saw the second parent (`split(" ", 2)`). Fixed.
- v0.1 Swift enclosing-class false positive. Fixed.
- Linear repos (voidtrace, tenaoshi, skills, and leftover feature branches that are ancestors of main) cannot exercise 3-way mode without synthetic parallel branches. Workaround: clone and create two branches, as demo.sh does.
- Language-agnostic tokenizer still misses non-ASCII identifiers and can miss a signature change that touches only a continuation line *and* has a non-callable hunk header.

## Suggested mutations
- Rename detection: `-foo` def plus `+foo2` def vs remaining uses of `foo`.
- Commute mode: would two linear commits be safe to reorder?
- Compare already-merged GitHub PRs as patches only when their pre-merge tips actually diverged from a shared base (stale-branch detection).
- Optional full-tree `git grep` on B for uses of A's deleted symbols in files B added without mentioning the ident on a changed line (already covered for new files' `+` lines).

## Kill / keep
Keep. The interaction is a missing git verb, empirically hits real signature/callsite pairs in Rust/Swift/TypeScript, and composes (`-o tsv`, `--diffs`, exit codes). GitHub-style history remains a weak `--audit` target; the useful path is `rift main...HEAD` on actually diverged branches, plus CI `-q`.
