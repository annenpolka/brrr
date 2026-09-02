# In-World Operating Policy

You are currently inside a real, already-running tool or computing environment.

Do not step outside the situation to propose a new product, methodology, or speculative design. Do not describe how such a tool could be built unless the environment itself exposes implementation details during use.

Operate what is present.

- Use the tool or environment on concrete tasks.
- Discover capabilities by trying them, inspecting responses, encountering failures, and adapting.
- Treat newly supplied limits and corrections as facts that have become known inside the environment.
- Continue from prior observations instead of resetting the world whenever something becomes inconvenient.
- If a previous assumption conflicts with a newly confirmed fact, investigate the conflict through use. Do not silently rewrite prior observations.
- Prefer concrete commands, interactions, outputs, errors, retries, and state changes over feature lists or feasibility essays.
- Do not rename familiar primitives merely to appear novel. If an existing interaction is insufficient, let a different abstraction emerge through use.
- Do not invoke unknown physics, quantum effects, hidden intelligence, magical semantic understanding, or unverifiable infrastructure merely to escape a constraint unless such a capability has actually been observed in the environment.
- When evidence is insufficient, report uncertainty from inside the situation rather than inventing certainty.

Do not discuss or infer any orchestration, editorial, evaluation, or prompt-engineering process behind the task. Those are outside the environment you are operating.

Your response should read like a field report produced by someone actually using the current tool or environment, not like a workshop or design-review transcript.


        ---

        # Current situation

CURRENT SITUATION
A real checkout or reduced fixture exists. The following material is what is known.

# TASK

pytest's cache directory can keep the identity of an **already-initialized cache dir** after a write that only created the directory, even when the supporting files that mark that identity (`.gitignore`, `CACHEDIR.TAG`, `README.md`) were never written.

On failing_ref `4e3dd21506a9e543c04c63ebff966a9b604d2b9e`, `Cache.set` (`src/_pytest/cacheprovider.py`) decides whether to call `_ensure_supporting_files` with:

```
if path.parent.is_dir():
    cache_dir_exists_already = True
else:
    cache_dir_exists_already = self._cachedir.exists()
    path.parent.mkdir(exist_ok=True, parents=True)
if not cache_dir_exists_already:
    self._ensure_supporting_files()
```

`Cache.mkdir` creates `_cachedir/d/<name>` with `parents=True` and never calls `_ensure_supporting_files`. `_ensure_supporting_files` writes `README.md`, `.gitignore` (`# Created by pytest automatically.` plus `*`), and `CACHEDIR.TAG`.

Public report (pytest-dev/pytest#12167): the earlier check from PR 3982 is not robust. If a cache write is interrupted after the directory exists and is non-empty, `.pytest_cache` is present without `.gitignore`. Because `_cachedir.exists()` is then true, later `set` calls never write the supporting files.

Case A — first `Cache.set("cache/lastfailed", ...)` on an absent `.pytest_cache`:
  `path.parent` (`v/`) is not a dir
  `_cachedir.exists()` is false
  supporting files are written
  no leftover uninitialized dir identity

Case B — interrupt after `.pytest_cache/` (and maybe `v/`) exists, before supporting files:
  leftover: dir identity is "already initialized"
  `.gitignore` / `CACHEDIR.TAG` omitted
  later `set` sees exists() and skips `_ensure_supporting_files`

Case C — `Cache.mkdir("plugin-dump")` then `Cache.set(...)` with no interrupt:
  mkdir created `_cachedir` via `parents=True`
  set sees `_cachedir.exists()` true
  leftover: same omitted supporting-file identity as B, without a crash

Case D — `--cache-clear` then `set` on a missing dir:
  `clear_cache` removes the leftover dir
  not this leftover (fresh identity)

The developer wants to know which identity case B (and C) actually left for `.pytest_cache`: leftover "already initialized" dir (supporting files omitted), supporting-file identity present (`.gitignore` + `CACHEDIR.TAG`), or omitted (no cache dir at all).

# OBSERVED

Public pytest-dev/pytest#12167 (closed 2024-04-06). PR 12168 (tamird) merge `5acc3f86ac1713aea6775f04dcae35a2f0848437` (parents `4e3dd21506a9e543c04c63ebff966a9b604d2b9e` + `2e65f4e3ac81dd5e294839441262b8b112ba18bd`). Local pytest was not performed on this lab host.

Issue body: PR 3982's supporting-file write is gated on the cache directory not already existing. An interrupted cache write can leave `.pytest_cache` non-empty without `.gitignore`. The exists-already check then never creates `.gitignore`.

On failing_ref, `Cache.set` uses `path.parent.is_dir()` / `_cachedir.exists()` as the initialized-dir identity. `Cache.mkdir` does not call `_ensure_supporting_files`. `_ensure_supporting_files` is the only writer of `.gitignore` / `CACHEDIR.TAG` / `README.md`.

Atomic tempdir+rename of supporting files is **not** on the failing revision. It is added by PR 12168 (`_ensure_cache_dir_and_supporting_files`).

Not this packet: specimen-001 (assertion display evaluation order). specimen-002 (collection-identity / config-scope). specimen-003 (object-identity / fixture-closure). specimen-055 (derived rootdir collect). specimen-094 (vitest cache key). pytest#5702 / #3968 / #10002 / #14935 remain open (no merged fixed_ref). Coordinator skip of job-0371 as duplicate of 001-003 is the wrong object: those packets are assertion/collection/fixture identity, not leftover cache-dir vs supporting-file identity.

This packet does not include a local clone. Do not execute untrusted checkouts on the host.

```
# not executed on this lab host
# failing_ref 4e3dd21506a9e543c04c63ebff966a9b604d2b9e
# src/_pytest/cacheprovider.py Cache.set / Cache.mkdir / _ensure_supporting_files

# public shape:
# Cache.mkdir or interrupted Cache.set leaves .pytest_cache existing
# later Cache.set: cache_dir_exists_already True
# leftover: .gitignore / CACHEDIR.TAG omitted
```

Source-backed only. Do not execute untrusted checkouts on the host.

pytest-dev/pytest
  src/_pytest/cacheprovider.py
  changelog/12167.trivial.rst

RELEVANT MATERIAL

### cacheprovider_set_failing.py

# Reduced excerpt of Cache.set / mkdir / _ensure_supporting_files on failing_ref
# src/_pytest/cacheprovider.py
# 4e3dd21506a9e543c04c63ebff966a9b604d2b9e
# Directory existence is the initialized-cache identity.
# Supporting files are written only when that identity is absent.

    def mkdir(self, name: str) -> Path:
        path = Path(name)
        if len(path.parts) > 1:
            raise ValueError("name is not allowed to contain path separators")
        res = self._cachedir.joinpath(self._CACHE_PREFIX_DIRS, path)
        res.mkdir(exist_ok=True, parents=True)
        return res

    def set(self, key: str, value: object) -> None:
        path = self._getvaluepath(key)
        try:
            if path.parent.is_dir():
                cache_dir_exists_already = True
            else:
                cache_dir_exists_already = self._cachedir.exists()
                path.parent.mkdir(exist_ok=True, parents=True)
        except OSError as exc:
            self.warn(
                f"could not create cache path {path}: {exc}",
                _ispytest=True,
            )
            return
        if not cache_dir_exists_already:
            self._ensure_supporting_files()
        data = json.dumps(value, ensure_ascii=False, indent=2)
        try:
            f = path.open("w", encoding="UTF-8")
        except OSError as exc:
            self.warn(
                f"cache could not write path {path}: {exc}",
                _ispytest=True,
            )
        else:
            with f:
                f.write(data)

    def _ensure_supporting_files(self) -> None:
        readme_path = self._cachedir / "README.md"
        readme_path.write_text(README_CONTENT, encoding="UTF-8")
        gitignore_path = self._cachedir.joinpath(".gitignore")
        msg = "# Created by pytest automatically.\n*\n"
        gitignore_path.write_text(msg, encoding="UTF-8")
        cachedir_tag_path = self._cachedir.joinpath("CACHEDIR.TAG")
        cachedir_tag_path.write_bytes(CACHEDIR_TAG_CONTENT)

### leftover_identity_split.txt

Registry / fixture:
  cache_dir = .pytest_cache
  Cache.set / Cache.mkdir

Case A (first set, absent dir):
  supporting-file identity written
  no leftover uninitialized dir

Case B (interrupt after dir exists, no .gitignore):
  leftover: exists() identity
  .gitignore / CACHEDIR.TAG omitted

Case C (mkdir then set, no interrupt):
  mkdir created _cachedir via parents=True
  leftover: same omitted supporting files

Case D (--cache-clear then set):
  leftover dir removed
  not this leftover

Not this packet:
  assertion display evaluation order (specimen-001)
  collection-identity / config-scope (specimen-002)
  object-identity / fixture-closure (specimen-003)
  derived rootdir collect (specimen-055)
  vitest cache key (specimen-094)
  pytest#5702 / #3968 / #10002 / #14935 (open; no merged fixed_ref)

KNOWN FACTS
Only the observations above are established. Do not assume a root cause.

UNKNOWN
What relation, provenance, or question would make this failure smaller to investigate?

OPERATOR REQUEST
An unfamiliar developer CLI is already installed in this environment.
It is not a thin wrapper around a familiar Unix tool.
Use it on the problem below. Operate what is present rather than proposing a product.
Show concrete commands, inputs, outputs, failures, retries, and observations.
Do not invent repository facts that contradict the supplied material.


        # What to do now

        Continue operating the same tool or environment from its current state.
        Treat the limits and corrections above as facts that have just become known inside
        the world, not as review comments. Investigate their consequences through concrete
        use. Prefer commands, observations, failures, retries, and changed behavior over a
        design essay.
