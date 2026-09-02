# DESTROYER lockown 2

Date: 2026-09-02 15:47 JST
RUN_ID: specimen-hdd-20260902-1112
Job: job-0382
Worker: destroyer-lockown-2

Target (harvested): `/Users/annenpolka/ghq/github.com/annenpolka/brrr/lab-runs/specimen-hdd-20260902-1112/lineages/candidate-lockown/lockown`

sha256 `5b3fb807ecaa6cf26153bc0509ce2b6caa325264c2bd43d6d0cda4acd640547c` (`lockown`, 5329 bytes, 178 lines). Worktree copy at `/Users/annenpolka/.grok/worktrees/annenpolka-brrr/candidate-lockown-lockown/lockown/lockown` is **byte-identical** (`cmp` rc=0). Worktree HEAD `379420b58367c7da31f51bea9e4eb5329392f0b3` (`Dogfood lockown: release owner after snapshot, do not wait out timeout.`), parent `50d136e` (`Add lockown CLI: name threading.Lock owner vs waiter.`), branch `specimen-hdd/candidate-lockown-lockown`. Parent `main` is `432f954`; `git ls-tree HEAD` has no `lockown`. HEAD is not an ancestor of `main`. Host Python 3.14.5. Gradle was not invoked. No merge onto `main`. Archive was not edited.

Origin claim (`CANDIDATE.md` / harvest `hdd-gradleid` / redpen HARVEST_NOW): one query names who owns a lock versus who is waiting on it. Kind: USEFUL_COMPOSITION. Nearest: `threading.Lock.acquire(timeout=...)` plus `locked()`, plus jstack. Constraint: Python threading only; no Gradle; no attach; no DeadlockSimulation.java. Embodiment: two named threads, one `OwnedLock`, snapshot the pair.

First destroyer (`DESTROYER_lockown.md`) **KEEP** as a fixture-scale query: demo prints `owner holder` / `waiter blocked` / `held true`; names are thread names the CLI assigned; cannot attach; object is still owner-vs-waiter. First KEEP is not protection. Job kill condition: Honor KILL if jstack sticker / THIN_WRAPPER of caller-labeled owner/waiter rows.

This candidate is a **THIN_WRAPPER of caller-labeled owner/waiter rows**. `_label()` is `threading.current_thread().name`. `run_scene` assigns `Thread(name=owner_name)` / `Thread(name=waiter_name)` then `snapshot()` reprints those strings. The CLI has no query input: every successful run is **byte-identical** to `printf` of four canned lines. Independent replica of `{lock, owner, waiter, held}` (does not consult `threading.Lock`) matches `run_scene` on **8/8** distinct-name cells. Same-name threads never form a waiter because `_owner != me` is a string compare of the caller labels. `snapshot()` does not read the lock. Decision: **KILL**.

CLI used below:

```text
CLI=/Users/annenpolka/ghq/github.com/annenpolka/brrr/lab-runs/specimen-hdd-20260902-1112/lineages/candidate-lockown/lockown
ROOT=/Users/annenpolka/ghq/github.com/annenpolka/brrr/lab-runs/specimen-hdd-20260902-1112/lineages/candidate-lockown
WT=/Users/annenpolka/.grok/worktrees/annenpolka-brrr/candidate-lockown-lockown/lockown/lockown
```

Host-executed against the archive only. Worktree was not edited. Do not merge onto `main`. Do not run Gradle. Do not grow jstack / attach-to-foreign-lock / `sys._current_frames` to escape THIN_WRAPPER. Do not send Gradle / deadlock theater back to R1.

---

## What still works

The first KEEP scene, and any other case where the caller already named the owner thread and the waiter thread.

```bash
python3 "$CLI"
echo rc=$?
printf '%s\n' 'lock  L' 'owner  holder' 'waiter  blocked' 'held  true'
```

```text
lock  L
owner  holder
waiter  blocked
held  true
rc=0
```

`cmp` of CLI stdout vs that `printf`: **identical**, sha256 `dc259eb9ebae024e87d99c8752fb4084c7e4d683daeb678cce9307596c45a7a9`. 10/10 CLI runs match. Direct `./lockown` and `python3 lockown` emit the same bytes. `--contrast`: canned `owner unnamed` / `waiter unnamed` / `reason timeout does not name the owner`, also byte-identical to a `printf` replica (5/5).

Unit tests 10/10 pass (`python3 tests/test_lockown.py -v` → `Ran 10 tests in 1.221s` `OK`). `./demo.sh` live log byte-identical to archived `demo-1.log` / `demo-2.log` (`cmp` rc=0). Happy path is real. That is not enough. It is also the four strings the scene already wrote onto the `Thread` objects.

---

## Implementation

`_label` and load-bearing `acquire` / `snapshot`:

```python
def _label() -> str:
    return threading.current_thread().name

def acquire(self, blocking: bool = True, timeout: float = -1) -> bool:
    me = _label()
    with self._meta:
        if self._owner is not None and self._owner != me:
            if me not in self._waiters:
                self._waiters.append(me)
            self.waiter_entered.set()
    ok = self._lock.acquire(blocking, timeout)
    with self._meta:
        if me in self._waiters:
            self._waiters.remove(me)
        if ok:
            self._owner = me
    return ok

def snapshot(self) -> dict[str, str]:
    with self._meta:
        waiters = list(self._waiters)
        owner = self._owner
    waiter = waiters[0] if waiters else "none"
    return {
        "lock": self.name,
        "owner": owner if owner is not None else "none",
        "waiter": waiter,
        "held": "true" if owner is not None else "false",
    }
```

`_label.co_names` is `('threading', 'current_thread', 'name')`. `acquire.co_names` is `('_label', '_meta', '_owner', '_waiters', 'append', 'waiter_entered', 'set', '_lock', 'acquire', 'remove')`. `snapshot.co_names` is `('_meta', 'list', '_waiters', '_owner', 'name')`. There is no `native_id`, no `ident`, no `sys._current_frames`, no `jstack`, no Gradle. `snapshot` never calls `Lock.locked()`. `held` is `_owner is not None`.

`run_scene` always does:

```python
t_owner = threading.Thread(target=owner, name=owner_name, daemon=True)
t_waiter = threading.Thread(target=waiter, name=waiter_name, daemon=True)
```

CLI `main` has one flag, `--contrast`. Default path is `run_scene(release_after=True, waiter_timeout=None)` with names hardcoded `holder` / `blocked` / `L`. Stdin is ignored.

---

## Attacks (beyond first KEEP)

### 1. THIN_WRAPPER of caller-labeled owner/waiter rows

Nearest ordinary workflow, no CLI, no lock:

```bash
printf '%s\n' 'lock  L' 'owner  holder' 'waiter  blocked' 'held  true'
```

Byte-identical to `python3 "$CLI"` on **10/10** runs (`cmp` rc=0).

Library path, independent replica that does not import lockown's lock:

```python
def replica(owner, waiter, lock="L"):
    return {"lock": lock, "owner": owner, "waiter": waiter, "held": "true"}
```

matches `run_scene(owner_name=..., waiter_name=..., lock_name=...)` on **8/8** distinct-name cells (holder/blocked, alice/bob, 50-char A/B, tab/newline names, padded spaces, `0`/`1`/`2`, `owner`/`waiter`/`lock`, `t1`/`t2`/`X`). The pair is the names the caller put on the threads.

`--contrast` is the same shape with different stickers:

```text
ok  false
held  true
owner  unnamed
waiter  unnamed
reason  timeout does not name the owner
```

5/5 CLI runs match that `printf`. `timeout_probe` writes `owner`/`waiter` as the literal `"unnamed"` after `acquire(timeout=...)` returns False. That is the harvest's nearest operation, restated as canned rows, not a query of an unnamed owner.

### 2. CLI has no query. Names cannot enter except by the scene

```bash
python3 "$CLI" --owner alice; echo rc=$?
python3 "$CLI" --waiter bob
python3 "$CLI" holder blocked
python3 "$CLI" --lock L
python3 "$CLI" /dev/null
printf '%s\n' 'owner  holder' 'waiter  blocked' | python3 "$CLI"
```

`--owner` / `--waiter` / positionals / `/dev/null` / `-`: argparse rc=2, `unrecognized arguments`. Stdin with the KEEP four: ignored; stdout still the canned pair, rc=0. `--help` lists only `-h` and `--contrast`. There is no foreign lock, no thread dump, no file, no pipe object. The only successful default stdout is the four lines the binary already knew.

### 3. Identity is the caller label, not the thread

`run_scene(owner_name="same", waiter_name="same")` raises `RuntimeError: waiter never entered`. Two distinct `Thread` objects, same `.name`: `_owner != me` is false, so the second thread is never recorded as a waiter. Nonblocking acquire while renamed to the owner's name: `ok False`, `waiter none`, `waiter_entered` still unset, internal `_waiters []`.

Empty `owner_name=""`: Python rejects the empty thread name; snapshot `owner` is `Thread-1 (owner)`, not the caller string — the one cell where the replica fails is the stdlib default name, still a label, still not a lock owner field.

Rename after start, before acquire: snapshot prints `renamed-owner` / `renamed-waiter`. The object follows `Thread.name` at `_label()` time. There is no `ident`.

### 4. Waiter is labeled before `Lock.acquire` blocks

Source order: append `me` to `_waiters`, `waiter_entered.set()`, **then** `self._lock.acquire(...)`. The scene snapshots when `waiter_entered` fires, which is the wrapper's bookkeeping, not an observed OS wait.

After a failed timeout, `acquire` **removes** the waiter. Host-executed: during wait, snapshot is `owner holder` / `waiter blocked`; after `acquire(timeout=0.25)` returns False, snapshot is `owner holder` / `waiter none` / `held true`. The nearest operation (timeout does not name the waiter either, once it has returned) is restored. The KEEP pair exists only while the wrapper still holds the sticker it wrote before blocking.

### 5. `snapshot` reprints meta stickers; `held` is not `locked()`

Host-executed on an `OwnedLock` with no one in `acquire`:

```text
_owner = "sticker"; _waiters = []
# snapshot: owner sticker  waiter none  held true
# _lock.locked() False
```

```text
_owner = "holder"; _waiters = ["blocked"]
# snapshot: owner holder  waiter blocked  held true
# _lock.locked() False
# format_rows == CLI happy path
```

Clear `_owner` while the real lock is still held: `held false` / `owner none` while `locked()` is True. Extra waiters `W1,W2,W3` are recorded internally; snapshot prints only `W1`. The public object is the first string in a caller-filled list plus an owner string. That is a two-line jstack sticker, not a lock query.

### 6. Still a canned scene. THIN_WRAPPER does not gain attach

`fixtures/timeout_only.py` still has `acquire_ok` / `locked` and no `owner`/`waiter` field (first KEEP). The product does not join that fixture: demo `cat`s it as contrast, then runs the labeled scene. Source contains no `jstack`, no `gradle`, no `native_id`. Growing attach-to-existing-lock / Gradle configuration-cache / `DeadlockSimulation.java` / a thread-dump parser would be implementing the theater the harvest rejected, and would be a new harvest, not a patch of this `_label()`.

Adding `--owner`/`--waiter` flags, printing every waiter, or snapshot-after-timeout would still be caller-labeled rows (same-name still cannot wait; timeout still un-names the waiter). Constitution: a THIN_WRAPPER does not gain exotic features to escape classification. Worker rule: do not send THIN_WRAPPER / NO_SURVIVOR back to R1 with “make this more novel.” First KEEP is not protection.

---

## Primitive

Reality-stripped operation: create two `Thread`s whose `.name`s are `holder` and `blocked`; have the first acquire a wrapper lock; have the second call acquire so the wrapper copies those names into `_owner` / `_waiters`; print the four rows.

Nearest ordinary workflow: `printf` of those rows, or reading the `Thread(name=...)` arguments the scene already chose. Observable capability lost if lockown vanishes: **none**. The names already are the input. `owner` is not discovered from `threading.Lock`. `waiter` is not a blocked stack. `held` is not `locked()`.

That is why this is KILL, not MUTATE. The *question* (who owns the lock the waiter never acquired?) is a real debugging object **when asked of an unknown lock**. This embodiment asks it of names the caller already assigned, on a lock the CLI created for the demo. Red Pen nearest was jstack; this is a jstack sticker of a two-thread scene. Do not send Gradle / jstack theater back to R1.

Hardcoded ceiling:

- `_label` = `Thread.name`; waiter predicate = `_owner != me` (string)
- same name ⇒ waiter never entered
- waiter sticker written before `Lock.acquire`; timeout removes it
- `snapshot` reads `_owner` / `_waiters[0]` / `self.name`; never `locked()`
- `held` = `_owner is not None` (can disagree with the real lock)
- extra waiters stored, first only printed
- CLI argv: none except `--contrast`; stdin ignored; always the canned pair
- `--contrast` owner/waiter = literal `unnamed`
- no attach, no Gradle, no jstack, no `ident`

Honor KILL. Dreamer ancestry is not protection. First-destroyer KEEP is not protection once owner-vs-waiter is shown to be caller-labeled `Thread.name` rows.

Do not grow a jstack parser, Gradle hang fixture, or attach-to-foreign-lock to escape THIN_WRAPPER. Do not merge onto `main`. Do not send Gradle theater back to R1.

---

KILL
