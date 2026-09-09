# github-pilot expansion screen (host; not Dreamer-facing)

Reviewer: agent. Not human. HOLD is not converted to PASS to fill a quota.

Source corpus: `.brrr-corpus/pilot-expand-20260909` collection `a9328ef43806b624ae4b461fea9d53947e459228bc24bd2fe1fb90773d4ff216`.
This run does not re-init that collection; it resumes and screens. 1130 already screened 13755/13784/13885/14048/14971 as HOLD.

## Newly screened complete issues (read bodies)

| Issue | Quality | Why |
| --- | --- | --- |
| 14608 nested addoption | HOLD | Directory sketch only; no file bytes; no command transcript. |
| 13913 conftest load vs custom CLI | HOLD | Reproducer is `git clone sqlalchemy` plus xdist; not a sealed mini bundle. |
| 14635 order-dependent fixture closure | HOLD | Requires Home Assistant tree; reporter says no standalone conftest. Causal/AI diagnosis must not go to a Dreamer. |
| 13479 class fixture + freezegun | HOLD | Mini snippet exists but depends on third-party `freezegun`. Host 実機 pytest 8.4.1 and 9.1.1 + freezegun 1.5.2: `fixture 'ff' not found`. No View. |
| 14591 indirect parametrize override | HOLD | Complete single-file example + 9.0.3 vs 9.1.0 transcripts. Bisect SHA is 正解 and stays off the consumer. Host 実機: 9.0.3 4 passed; 9.1.0 collection error `duplicate parametrization of 'myfixture'`; 9.1.1 4 passed (regression gone). No View/export. |
| 14011 class-scoped inherited fixture | HOLD | Complete snippet + pip list + pytest 9.0.1. Host 実機: 9.0.1 both tests fail (`self.variable is None`). No View staged. |

Reconfirmed 1130 HOLD 13885: pytest 8.4.1 and 9.0.1 autouse `assert 0` still runs under `@skipIf(True, ...)`; pytest 9.1.1 skips (rc=0). Still HOLD; no View. 14011 still fails on 9.1.1 (`self.variable is None`).

| 12689 | HOLD | No sealed mini bundle. HOLD. |
| 13699 | HOLD | Host CPython 3.14 + asynctest 0.13.0: `asyncio.coroutine` AttributeError; importorskip does not skip. No View. |
| 13724 | HOLD | PR. Repair/feature. HOLD. |
| 13727 | HOLD | PR. Repair/feature. HOLD. |
| 13754 | HOLD | Has a snippet but no sealed View/export. HOLD. |
| 13755 session heavy_fixture | HOLD | Host public snippet: 4 unique params, 10 setups on 8.4.1/9.0.1/9.1.1. Same as reporter. No View. |
| 13778 | HOLD | PR. Repair/feature. HOLD. |
| 13796 | HOLD | PR. Repair/feature. HOLD. |
| 13834 | HOLD | No sealed mini bundle. HOLD. |

| 13875 | HOLD | PR. HOLD. |
| 13910 | HOLD | No sealed mini bundle. HOLD. |
| 13922 | HOLD | PR. HOLD. |
| 13927 | HOLD | PR. HOLD. |
| 13957 | HOLD | Host collect-only nodeids 8.4.1/9.0.1/9.1.1 all `[cpu-half-ip-1-1-True]`. No 8/9 swap. Not original IDs. No View. |
| 13970 | HOLD | PR. HOLD. |
| 13976 | HOLD | PR. HOLD. |
| 13985 | HOLD | Host `[tool.pytest] addopts="-q"`: 8.4.1 ignores table; 9.0.1/9.1.1 TypeError expects list. List form `["-q"]` pass 9.x. SchemaStore not run. No View. |
| 13993 | HOLD | PR. HOLD. |
| 13998 | HOLD | PR. HOLD. |

| 14700 | HOLD | No sealed mini bundle. HOLD. |
| 14444 | HOLD | No sealed mini bundle. HOLD. |

## Batch2 bodies + host 実機 (18:08–18:17 JST)

Reviewer: agent. HOLD not converted to PASS. Expand collect `a9328ef4` is `NO_RUNNABLE_JOB` unfinished 0; do not resume.

| Issue | Quality | Why |
| --- | --- | --- |
| 14775 class fixture -Werror | HOLD | Complete snippet. Host: 8.4.1/9.0.1 2 pass; 9.1.1 rc=1 `_finalizers` AssertionError. No View. |
| 13925 empty-string discovery | HOLD | Two-file layout. Host: 8.4.1 `pytest -q '' a/` 1 pass; 9.0.1/9.1.1 collect `1/0`. No View. |
| 14253 log_cli_level int | HOLD | Public pyproject. Host 9.0.1/9.1.1 rc=3 TypeError string vs int. No View. |
| 14092 tmp_path_retention_count int | HOLD | Public pyproject. Host 9.0.1/9.1.1 rc=3 TypeError. No View. |
| 14650 strict_parametrization_ids | HOLD | Public test_strict.py. Host 9.1.0/9.1.1 rc=2 duplicate IDs `1-2`. No View. |
| 14094 Monkeypatch delitem | HOLD | As-written `pytest.Monkeypatch` is not public API. Host 9.0.1/9.1.1 AttributeError. No View. |
| 14095 scoped fixture override | HOLD | Host 9.0.1/9.1.1 rc=1; class `a` does not rebuild module `b`. No View. |
| 13882 class fixtures vs subclasses | HOLD | Mocked Chrome/login e2e, not a sealed mini. |
| 14560 custom class parametrize | HOLD | Host dict-wrapper `__getattr__` KeyError `__name__` on collect 8.4.1/9.0.1/9.1.1. Not original file. No View. |
| 13965 unittest subTest blowup | HOLD | N=1 host 9.0.1/9.1.1 rc=0; stress microbenchmark not a View. |
| 14412 subtest times | HOLD | Host 9.1.1 rc=0 (sleep shortened). No View. |
| 14800 fixture_setup finalizers | HOLD | Host 9.1.1 rc=1; needs plugin hook. No View. |
| 14640 CLI path order | HOLD | Public tree. Host CASE1 interleaved: 8.4.1/9.0.1 3 pass; 9.1.1 `shared` missing on test_b. CASE2 sorted 3 pass. No `_matchfactories` patch. No View. |
| 14004 testpaths sibling leak | HOLD | Host 9.1.1 nested autouse rc=0. No View. |
| 14808 _getini_ini string type | HOLD | Host: `[tool.pytest.ini_options]` array getini returns list; `[tool.pytest]` TypeError; pytest.ini scalar pass. No View. |
| 14683 doctest_namespace | HOLD | Host stripped `ANSWER=42` doctest 8.4.1/9.0.1/9.1.1 pass. Needs nimbus/xarray for reporter. No View. |
| 14436 caplog KeyError | HOLD | Host minis: happy caplog pass; session ScopeMismatch; `-p no:logging` fixture missing. Tavern KeyError not reproduced. No View. |
| 14514 dotted filenames | HOLD | Feature. Host collect foo.test.py rc=2. |
| 14101 subtest xfail | HOLD | Feature request. |
| 14762 3.15b4 SEGFAULT | HOLD | CI crash; no mini. |
| 14431 cache efficiency | HOLD | Host add() rc=0; not a cache bug. |

## Batch6 leftover complete pytest roots (18:27–18:30 JST)

Reviewer: agent. HOLD not converted to PASS. Expand collect remains `NO_RUNNABLE_JOB` unfinished 0; not resumed.

| Issue | Quality | Why |
| --- | --- | --- |
| 2043 indirect override | HOLD | Host 8.4.1 collect error; 9.0.1 4 pass; 9.1.0 duplicate parametrization; 9.1.1 4 pass. No View. |
| 5203 fixture override | HOLD | Host 8.4.1/9.0.1/9.1.1 rc=1 TestB assert 8==6. Same family as 14095. No View. |
| 9298 pycache_prefix | HOLD | Windows CI only; no portable mini. |
| 13784 capteesys -s | HOLD | Host 8.4.1 `capteesys`+`-s` stdout doubled; without capteesys once; 9.1.1 once. No View. |
| 14048 --pyargs tox | HOLD | Host `--pyargs amodule.tests` 8.4.1/9.1.1 rc=4 missing `__init__.py`. No tox tree. No View. |
| 14148 config.cache | HOLD | Host `-p no:cacheprovider` AttributeError on 8.4.1/9.1.1; default cache 9.1.1 pass. No View. |
| 14445 walrus rewrite | HOLD | Host 8.4.1/9.0.1/9.0.3/9.1.1 rc=1 (`1 != 1`, count 6). 9.1.1 `--assert=plain` 2 pass. No View. |
| 14446 / 14453 / 14476 / 14488 | HOLD | PR or no sealed files. |
| 14593 / 14622 / 14624 | HOLD | PR or feature; no View. |
| 14613 PYTEST_CACHE_DIR_BASE | HOLD | Feature request; no failing mini. |
| 14670 / 14694 / 14696 | HOLD | Repair PRs. 正解 risk. |
| 14691 classmethod fixture | HOLD | Host `@classmethod` fixture not found; without classmethod or `@staticmethod` 1 pass. No View. |
| 14702 / 14750 / 14777 | HOLD | PR. 正解 risk. |
| 14737 package pytestmark | HOLD | Host skip in `__init__.py`/`conftest.py` does not apply; module-level pytestmark skips. No View. |
| 14807 / 14811 / 14812 | HOLD | PR. 正解 risk. |
| 14819 chained compare | HOLD | Host 8.4.1/9.0.1/9.1.1 rc=1 (ZeroDivisionError + boom called). No View. |
| 14820 rebind operand | HOLD | Host 8.4.1/9.0.1/9.1.1 rc=1 (`99 == 0`). 9.1.1 `--assert=plain` 2 pass. No View. |
| 14821 / 14850 | HOLD | PR. 正解 risk. |
| 14841 pytester sys.modules | HOLD | Host public snippet 8.4.1/9.1.1 rc=1, 1 failed/3 passed; deferred-import-fail `resource_tracker` on stderr. No View. |
| 14877 plugin scan | HOLD | Profiler numbers; no failing input. |
| 14389 raises match chaining | HOLD | Host `raises(..., match="nope")`: 8.4.1/9.0.1 print `During handling`; 9.1.1 omits it. No `from exc` implemented. No View. |
| 14921 | HOLD | PR. 正解 risk. |
| 14935 tmp_path user-scoped | HOLD | Host 8.4.1/9.1.1 two-project runs share `pytest-of-<user>/`; proj-a scratch evicted; no `.origin`. Design, no View. |
| 14971 nested conftest | HOLD | Host 9.1.1 interleaved file args miss nested fixture; sorted args and `pytest tests` 3 pass. No View. |
| 14964 interleaved autouse | HOLD | Host CASE1 `tests/a.py test_x.py tests/b.py`: 8.4.1/9.0.1 both tests ERROR guard; 9.1.1 test_b PASSES. Sorted orders both ERROR. No View. |
| 14608 nested addoption | HOLD | Host `pytest --from-b A` unrecognized on 8.4.1 and 9.1.1; `A B` and cwd=A `../B` pass. No 8/9 delta. No View. |
| 14973 | HOLD | PR. 正解 risk. |

## 19:44 vacancy tick host 実機 (HOLD not PASS)

| Issue | Quality | Why |
| --- | --- | --- |
| 14696 file-valued option | HOLD | Mini: `--write-idents idents.txt` unrecognized 8.4.1–9.1.1; missing filename loads except 9.1.0. No sqlalchemy tree. No View. |
| 14841 pytester+mp | HOLD | Public snippet: deferred-import-fail resource_tracker KeyError on 8.4.1–9.1.1. No View. |
| 14448 rewrite display | HOLD | Subscript/IfExp fail as `assert 1 == 99` / `assert 0 == 99`; no `where` line. PR not applied. No View. |
| 14323 Popen DEVNULL | HOLD | Comment snippet: all capture modes pass on macOS 3.14. No View. |
| 14488 caplog handler | HOLD | After stash del: opaque StashKey KeyError 8.4.1–9.1.1; happy handler pass. PR not applied. No View. |

## 19:59 vacancy tick host 実機 (HOLD not PASS)

| Issue | Quality | Why |
| --- | --- | --- |
| 14635 fixture closure order | HOLD | Reduced mini (no HA clone) collects and runs on 8.4.1–9.1.1. Does not reproduce `function uses no argument`. No View. |
| 14694 rootdir conftest doctest | HOLD | `--rootdir` testing/ + parent `--doctest-modules`: pass 8.4.1–9.0.3; NameError on 9.1.0/9.1.1. PR not applied. No View. |
| 14807 / 14921 / 14118 | HOLD | PRs. 正解 risk. No new View. |

## 20:04 vacancy host 実機 (HOLD not PASS)

| Issue | Quality | Why |
| --- | --- | --- |
| 14973 addModuleCleanup | HOLD | stdlib unittest writes flag; pytest 8.4.1–9.1.1 does not. PR not applied. No View. |
| 14812 caplog teardown report | HOLD | INTERNALERROR StashKey KeyError on 8.4.1–9.1.1. PR not applied. No View. |
| 14702 fixture doctest | HOLD | CPython 3.14 `--doctest-modules` 2 pass 1 skip; no INTERNALERROR. No jaraco. No View. |

## 20:14 vacancy host 実機 (HOLD not PASS)

| Issue | Quality | Why |
| --- | --- | --- |
| 14807 custom TOML `[pytest]` | HOLD | `-c` `[pytest]` ignored 8.4.1–9.1.1; `-c` ini_options works; named `pytest.toml` from 9.0.1. PR not applied. No View. |
| 14514 python_files workaround | HOLD | `*.test.py` still `ModuleNotFoundError: pkg.foo`. No View. |
| 14255 quoted log level | HOLD | `"INFO"` pass on 9.x native table; int 10 TypeError. Docs PR not applied. No View. |

## 20:15 occupy host 実機 (HOLD not PASS)

| Issue | Quality | Why |
| --- | --- | --- |
| 14807 both tables / pyproject `[pytest]` | HOLD | Both tables: no UsageError, ini_options wins. pyproject `[pytest]` ignored. No View. |
| 14514 importlib | HOLD | `--import-mode=importlib` collect rc=0; default import still ImportError. No View. |

## 20:28 leftover host 実機 (HOLD not PASS)

| Issue | Quality | Why |
| --- | --- | --- |
| 13913 testpaths + idents.txt | HOLD | `--db --write-idents idents.txt` rc=0 on 8.4.1; unrecognized on pytest 9. Explicit `tests/` always rc=0. No sqlalchemy. No View. |
| 14700 skipped fixture doctest | HOLD | 3.14 `pkg/git.py` 1 skipped; no `line is not None`. No jaraco. No View. |
| 14762 3.15b4 SEGFAULT | HOLD | Host 3.14.5 collect rc=0. No crash. No View. |
| 9298 pycache_prefix | HOLD | macOS prefix writes rewritten pyc. Windows missing-pyc not reproduced. No View. |

None exported. No quality PASS. HDD consumer still has 1 discovery case. **小規模試行**. Not holdout.

## 20:49 vacancy host 実機 (HOLD not PASS)

| Issue | Quality | Why |
| --- | --- | --- |
| 13699 asynctest importorskip | HOLD | AttributeError `asyncio.coroutine` on 8.4.1–9.1.1; importorskip does not skip. 3.14 third-party, not 8/9 delta. No View. |
| 14094 MonkeyPatch spelling | HOLD | Correct `MonkeyPatch`: existing delitem restores; missing delitem/delattr leave `{1:3}` / `prop=3` on 8.4.1–9.1.1. As-written `Monkeypatch` is AttributeError. No View. |
| 11502 `--config-file=/dev/null` | HOLD | `rootdir: /dev` 8.4.1–9.1.1; collect walks from `/dev`. No PytestCacheWarning on macOS 3.14. No View. |
| 14705 custom TOML python_files | HOLD | `-c` `[pytest]` ignored (collects `test_normal`); `-c` `[tool.pytest]` from 9.0.1 collects `bench_add`. Same as #14807. No View. |
| 14447 walrus rewrite plain | HOLD | 9.1.1 `--assert=plain` 3 passed (rewrite still 3 failed 8.4.1–9.1.1). No View. |
| 14048 --pyargs noinit extra | HOLD | 9.0.3/9.1.0 without `tests/__init__.py` rc=4 same as 8.4.1/9.0.1/9.1.1. No View. |

## 20:57 occupy host 実機 (HOLD not PASS)

| Issue | Quality | Why |
| --- | --- | --- |
| 14445 walrus rewrite extra | HOLD | 9.1.0 rewrite still `1 != 1` / `6 == 3`; `--assert=plain` 2 pass 8.4.1–9.1.1. No View. |
| 14819 chained compare plain | HOLD | `--assert=plain` short-circuit AssertionError on 8.4.1–9.1.1; rewrite still ZeroDivision+boom. No View. |
| 14820 rebind operand plain | HOLD | `--assert=plain` 2 pass 8.4.1–9.1.1; rewrite still `99 == 0`. No View. |
| 14101 xfail_strict extra | HOLD | 9.0.3/9.1.0 same XPASS + `xfail=True` still runs `assert False`. Feature. No View. |
| 14431 default collect | HOLD | `test.py` skipped on 8.4.1–9.1.1 (rc=5); explicit `test.py` 1 pass. Not a cache bug. No View. |
| 14608 extra layouts | HOLD | `cd A && pytest --from-b` unrecognized 8.4.1–9.1.1; parent ini from root 2 pass. No 8/9 delta. No View. |
| leftover PRs | HOLD | 14446/14453/14593/14622/14624/14670/14750/14777/14821/14850/14921 repair/tooling. 正解 off Dreamer. |
| 14608c invocation-dir tests/ | HOLD | `--db-url` with no file args: pass 8.4.1–9.0.3; unrecognized 9.1.0; pass 9.1.1. Explicit path args pass 9.1.0. PR not applied. No View. |

None exported. No quality PASS. HDD consumer still has 1 discovery case. **小規模試行**. Not holdout.

## 21:07 occupy host 実機 (HOLD not PASS)

| Issue | Quality | Why |
| --- | --- | --- |
| 14817 method-call rewrite | HOLD | All 8.4.1–9.1.1 show bound-method intermediates (`where 42 = compute()`), not changelog `Obj().compute()`. Plain bare AssertionError. No View. |
| 14816 IfExp rewrite | HOLD | `assert 0 == 99`; no `where 0 = (... if True else ...)`. Same as 14448. No View. |
| 14815 subscript rewrite | HOLD | `assert 1 == 99`; no `where 1 = {'a': 1, 'b': 2}['a']`. Same as 14448. No View. |
| 14608c testpaths | HOLD | `testpaths=tests` does not rescue 9.1.0 (`--db-url` still unrecognized). Missing `testpaths=other` still 9.1.0 unrecognized; other versions fallback-pass. No View. |
| 14608c root vs nested | HOLD | Invocation-dir `conftest.py` pass on 9.1.0. Nested `tests/unit/conftest.py` unrecognized 8.4.1–9.1.1. 9.1.0-only miss is a direct `test*` child. No View. |
| 14817 instance | HOLD | `obj.compute()` still bound-method intermediates on 8.4.1/9.1.0/9.1.1. No View. |
| 14813 | HOLD | Coverage-matrix PR, test-only, no public failing mini. 正解 off Dreamer. |
| 14104 session gap | HOLD | Comment mini 3 pass 8.4.1–9.1.1 including `getfixturevalue`. No call-phase teardown fail. No View. |
| 14608c name glob | HOLD | `test-foo`/`testdir`/`testfoo` 9.1.0-only miss. `_tests`/`Tests` unrecognized all versions. No View. |
| 13976 comment | HOLD | Duplicate of 14591 indirect override. Already reconstituted. 正解 off Dreamer. |
| 14271 monkeypatch comment | HOLD | delattr raising=False then setattr; hasattr True 8.4.1–9.1.1. PR not applied. No View. |
| 14476 `-k foo` extra | HOLD | Mark `foo` and name `test_foo` both collected 8.4.1–9.1.1. No View. |
| 14104 setup-show | HOLD | Session `foo[1]` carried across gap; teardown at end. getfixturevalue then new unparametrized foo. No View. |
| 13957b comment MRE | HOLD | 8.4.1 `test[b1-a1]`; pytest 9 `test[a1-b1]`. Swap `test(B_C, A_B_C)` restores b-first on 9. Original knn mini did not show this. No View. |
| 13755b further-min | HOLD | Session `fix_once` torn down after test_a; test_b ERROR `param not in seen` 8.4.1–9.1.1. No View. |
| 14271 delitem extra | HOLD | delitem raising=False then assign; key remains 8.4.1–9.1.1. No View. |
| 13976 fixture override | HOLD | Comment mini 2 pass 8.4.1–9.0.3; duplicate `target` on 9.1.0; 2 pass 9.1.1. Same family as 14591. No View. |
| 13957b `-v` | HOLD | Run nodeids match collect-only (`b1-a1` vs `a1-b1`). 4 pass. No View. |
| 9703b same-named | HOLD | `-c config/` collapses `test_same`; `--lf` reruns both. `--rootdir=.` unique. No View. |
| 13976 conftest + generate_tests | HOLD | Conftest layout same 9.1.0 duplicate. generate_tests workaround 5 pass including 9.1.0. Not a product. No View. |
| 14608c confcutdir | HOLD | `confcutdir=.` does not rescue 9.1.0 `--db-url`. No View. |
| 14650b no-strict | HOLD | Isolated tree auto-suffixes `1-2_0`/`1-2_1` 2 pass 8.4.1–9.1.1. Nested dir still inherits parent pyproject. No View. |
| 13976 ids= | HOLD | `ids=["A","B"]` still duplicate on 9.1.0. No View. |
| 14800 setup-show | HOLD | `_finalizers` from 9.1.0 (9.0.3 still 2 pass 1 skip). No View. |
| 14650c ini tables | HOLD | `pytest.ini` `[pytest]` and `ini_options` both ERROR on 9.x; 8.4.1 unknown-option + auto-suffix. No View. |
| 13976 pytest.param | HOLD | `pytest.param` still duplicate on 9.1.0. No View. |
| 14608c pythonpath | HOLD | `pythonpath` / `-o pythonpath` / ini_options do not rescue 9.1.0 `--db-url`. `addopts=tests` rescues (root rc=5; inside tests/ 1 pass). `--noconftest` unrecognized 8.4.1–9.1.1. `confcutdir=tests` / `norecursedirs=tests` no rescue. No View. |
| 14431 python_files | HOLD | `python_files=test.py` default collect 1 pass 8.4.1–9.1.1. No View. |
| 14800 setup-plan | HOLD | `--setup-show` 9.0.1 still 2 pass 1 skip. `--setup-plan` no tests ran 8.4.1–9.1.1 (`_finalizers` is execute-only). No View. |
| 14694 pythonpath | HOLD | `pythonpath=src/pkg/testing` still NameError on 9.1.0/9.1.1. No View. |
| 14004b testpaths leak | HOLD | `sdk/` + `testpaths=../tests/sdk` inner autouse leak 8.4.1–9.0.3; gone 9.1.0; explicit path no leak. pythonpath does not change the leak. No View. |
| 13913 pythonpath | HOLD | `pythonpath=["tests"]` still pytest 9 unrecognized `--db --write-idents` with existing file. No View. |
| 14514 pythonpath | HOLD | `pythonpath=pkg` still `foo.test` ModuleNotFound; importlib 1 pass. No View. |
| 14696 pythonpath | HOLD | `pythonpath=tests` still existing `idents.txt` unrecognized `--write-idents` 8.4.1–9.1.1; missing file still 9.1.0-only miss. No View. |
| 14807 extras | HOLD | pyproject `[tool.pytest]` list from 9.0.1; string TypeError on 9.x. `pytest.toml` only `[pytest]` from 9.0.1 (ini_options/native ignored). `-c` INI `[pytest]` all versions. native+ini_options UsageError on pytest 9. tox.ini/setup.cfg/pytest.ini all versions. No View. |
| leftover pytest 正解 PRs | HOLD | 14446..14921 screens fences=0 except 14821 (is 14820) and 14921 tooling. Do not apply. No View. |
| leftover uv PRs | HOLD | 16139/18406/18979/19114/19330/19370/19613/21265 fences=0 snippet_len=0. No View. |
| 13925 reverse empty | HOLD | `a/ ''` same 8.4.1 1 pass / pytest 9 ZeroDivision. `-- a/` 1 pass all. No View. |
| 14807 setup.cfg [pytest] | HOLD | Failed all versions; change to `[tool:pytest]`. ini_options string python_files works 8.4.1–9.1.1. pytest.toml `[pytest]` string TypeError on 9. No View. |
| 12083 two files | HOLD | Distinct file args n=2 all versions. `--keep-duplicates` reverse n=3 all. Overlap-dir drop is 8.4.1-only. No View. |
| 14608c PYTEST_ADDOPTS | HOLD | `PYTEST_ADDOPTS=tests` rescues 9.1.0 `--db-url` like CLI/ini path args. No View. |
| 13925 a/ . | HOLD | `a/ .` and `. a/` same 8.4.1 1 pass / pytest 9 ZeroDivision. Overlapping cwd drop on 8.4.1. No View. |
| 14807 tox [tool:pytest] | HOLD | tox.ini `[tool:pytest]` ignored; pytest.ini `[tool:pytest]` ignored. setup.cfg wants `[tool:pytest]`. No View. |
| 14412 ini_options times | HOLD | 8.4.1 reads times as whole-test ms (no subtest us). Pytest 9 later 0.000us. No View. |
| 14640 reverse interleaved | HOLD | Later assignment after resume gap misses `shared` from 9.1.0. 8.4.1 re-SETUP after TEARDOWN. No View. |
| 14148 cache_on 8.4.1 | HOLD | Default cache 1 pass. AttributeError only `-p no:cacheprovider`. No View. |
| 14971 reverse/setup-show | HOLD | Reverse interleaved same 9.1.0 miss on later services test. `--setup-show` 8.4.1/9.0.3 re-SETUP nested_fixture; 9.1.0 does not. Family of 14640. No View. |
| 14964 reverse/setup-show | HOLD | Reverse CASE1 later test_a passes on 9.1.0 (guard missed). `--setup-show` 9.1.0 SETUP guard only for first tests/ file. No View. |
| 13704 keep-duplicates | HOLD | `--keep-duplicates tests/ tests/test_it.py` n=3 all versions. Same file twice n=2 all. No View. |
| 14640/14971 dir collect | HOLD | `pytest tests` / `tests/services` pass all versions including 9.1.0. Miss needs interleaved file args with a gap. No View. |
| 14964 no-gap | HOLD | `a.py b.py` both ERROR guard all versions. `pytest tests` rc=5. python_files=*.py dir both ERROR. No View. |
| 14104 setup-show extra | HOLD | 9.0.1/9.0.3 session `foo[1]` carried across gap like 8.4.1/9.1.x. No View. |
| 14640 assignment-only | HOLD | `tests/woo/assignment` 2 pass all versions. Miss needs resume gap. No View. |
| 14971 one-services+gap | HOLD | `test_a.py test_top.py` and `test_top.py test_b.py` 2 pass all. Miss needs two same-conftest files with gap between. No View. |
| 14964 one-file+gap | HOLD | `a.py test_x.py` / `test_x.py b.py` still 1 error guard all versions. Miss needs two tests/ files with gap between. No View. |
| 5203 setup-show | HOLD | `b` built from first module `a` all versions. Same as 14095. No View. |
| 13885 setup-show | HOLD | Autouse fires 8.4.1–9.0.3; `_unittest_skip_fixture_Foo` from 9.1.0. No View. |
| 14095 setup-show | HOLD | Same as 5203: `b` from first module `a` all versions. No View. |
| 13755 setup-show extra | HOLD | 9.0.1/9.0.3/9.1.0 10 SETUP S / 10 TEARDOWN S. No 8/9 delta. No View. |
| 13704b keep-duplicates | HOLD | `a/b a/` n=4 all (`test_b` twice). Restores overlapping parent on 8.4.1. No View. |
| 7777 a/b collect | HOLD | `a/b` n=3; `a/b/c` n=2 all versions. Nested Dir c still collects. No View. |
| 14964d reverse | HOLD | Reverse gap same 9.1.0 miss (later test_a PASSES). 9.0.1 both ERROR. No View. |

## 21:00 vacancy host 実機 (HOLD not PASS)

| Issue | Quality | Why |
| --- | --- | --- |
| 14716 `-c` invalid paths | HOLD | Wrong ext silent rc=0 (`configfile` reported even if missing). Missing `.ini` raw FileNotFoundError rc=1. Same 8.4.1–9.1.1. No View. |
| 14916 rewrite gaps | HOLD | Lists show index diff; `f()` shows `where 42 = f()`. Not the PR's `<function ...>` claim. No View. |
| 14814 walrus/starred | HOLD | Starred rewrite `(9, [9]) == (1, [9])`; plain/native pass. Parenthesized walrus-tuple rewrite pass. No View. |
| 11502 run `/dev/null` | HOLD | Collect-only no warning; running tests PytestCacheWarning on 8.4.1–9.1.1. No View. |
| 14705 custom ini_options | HOLD | Custom `-c` `[tool.pytest.ini_options]` collected on 8.4.1 (unlike `[tool.pytest]`). No View. |

None exported. No quality PASS. HDD consumer still has 1 discovery case. **小規模試行**. Not holdout.

## 21:15 vacancy host 実機 (HOLD not PASS)

| Issue | Quality | Why |
| --- | --- | --- |
| 9703 `-c config/` autouse | HOLD | Explicit files: `rootdir: config/` + `config::` nodeids 8.4.1–9.1.1. Autouse leak on file2 through 9.0.3; gone 9.1.0. No View. |
| 13246 sibling fixtures | HOLD | `-c config/pytest.ini` `test2` sees `value=1` (`FAILED config::test2`) 8.4.1–9.1.1. `--rootdir=.` 2 pass. No View. |
| 14814 bare walrus | HOLD | `collect(x := 1, identity(x := 2))` rewrite/plain/native all pass. No View. |
| 14716 missing toml/cfg | HOLD | Missing `.toml`/`.cfg` FileNotFoundError rc=1 like `.ini`. Wrong `.in` still silent. No View. |
| 11502 nocache | HOLD | `-p no:cacheprovider` still `rootdir: /dev`; no PytestCacheWarning. No View. |

None exported. No quality PASS. HDD consumer still has 1 discovery case. **小規模試行**. Not holdout.

## 21:30 vacancy host 実機 (HOLD not PASS)

| Issue | Quality | Why |
| --- | --- | --- |
| 9703b same-named `test_same` | HOLD | `-c config/` both displayed `config::test_same` 8.4.1–9.1.1. `--lf` reruns both (no deselected). `--rootdir=.` unique ids. No View. |
| 9703 `--rootdir=.` | HOLD | Unique `tests/test_file*.py` nodeids; autouse only file1 on 8.4.1/9.1.1. No View. |
| 13246 subdir invoke | HOLD | From `subdir/` `-c ../config/pytest.ini` still `FAILED ../config::test2`. No View. |

None exported. No quality PASS. HDD consumer still has 1 discovery case. **小規模試行**. Not holdout.

## 21:44 vacancy host 実機 (HOLD not PASS)

| Issue | Quality | Why |
| --- | --- | --- |
| 14004b testpaths outside rootdir | HOLD | `cd sdk && pytest -s`: inner autouse leaks onto outer tests 8.4.1–9.0.3; gone 9.1.0. Explicit `../tests/sdk` never leaks. No View. |
| 9703b `--rootdir=. --lf` | HOLD | After fail file1, `--lf` reruns only the failed test. Unique nodeids restore lastfailed. No View. |

None exported. No quality PASS. HDD consumer still has 1 discovery case. **小規模試行**. Not holdout.

## 21:59 vacancy host 実機 (HOLD not PASS)

| Issue | Quality | Why |
| --- | --- | --- |
| 12083 overlapping args | HOLD | `tests/test_one.py tests` collect 1 on 8.4.1 (subdir dropped), 2 on pytest 9. `--keep-duplicates` 3 all versions. No View. |
| 13925 empty/dot alone | HOLD | `pytest ''` and `pytest .` ZeroDivision all versions; `a/` 1 pass. 8/9 delta is `'' a/` together. No View. |
| 14004b `--rootdir` | HOLD | `--rootdir=.` from sdk still leak 8.4.1–9.0.3. `--rootdir=..` rc=5 no tests. No View. |

None exported. No quality PASS. HDD consumer still has 1 discovery case. **小規模試行**. Not holdout.

## 22:15 vacancy host 実機 (HOLD not PASS)

| Issue | Quality | Why |
| --- | --- | --- |
| 13704 dir/file overlap | HOLD | `tests/ tests/test_it.py` collect 1 on 8.4.1 / 2 on pytest 9. Same file twice: 2 on 8.4.1 / 1 on pytest 9. No View. |
| 12083 overlap run | HOLD | `tests/test_one.py tests` run 1 pass on 8.4.1 / 2 on pytest 9. `--keep-duplicates` run 3 pass. No View. |
| 13925 collect-only `'' a/` | HOLD | 8.4.1 1 collected; 9.1.1 1 collected + ERROR test_root ZeroDivision. Same split as run. No View. |

None exported. No quality PASS. HDD consumer still has 1 discovery case. **小規模試行**. Not holdout.

## 22:30 vacancy host 実機 (HOLD not PASS)

| Issue | Quality | Why |
| --- | --- | --- |
| 7777 nested packages | HOLD | `--collect-only a/` 5 nested items 8.4.1–9.1.1. `--keep-duplicates` still 5 (pytest-6 11-item duplication gone). No View. |
| 13704b `a/b a/` order | HOLD | 8.4.1 n=1 (parent dropped). pytest 9 n=3 equivalent to `a/`; `a/a` before `a/b`. No View. |
| 14964d `test_*.py` names | HOLD | Dir/no-gap both ERROR all versions. Interleaved gap still 9.1.0 miss (test_b PASSES). No View. |

None exported. No quality PASS. HDD consumer still has 1 discovery case. **小規模試行**. Not holdout.

## 22:48 leftover host 実機 (HOLD not PASS)

| Issue | Quality | Why |
| --- | --- | --- |
| 7777 overlap run | HOLD | `a/b a/` 8.4.1 3 pass / pytest 9 5 pass. `--keep-duplicates` run 8 all. No View. |
| 13925 keep-duplicates cwd | HOLD | `--keep-duplicates '' a/` and `a/ .` ZeroDivision on 8.4.1 too (restores dropped cwd). No View. |
| 12083 keep-duplicates `tests .` | HOLD | n=4 all versions (cwd duplicates tests/). Without flag n=2 unique. No View. |
| 14775 -Werror | HOLD | `_finalizers` from 9.1.0 when warning is an error. Without `-Werror`, 9.1.1 2 pass 1 warning. No View. |
| 13885 setup-plan | HOLD | 9.1.0 plan still lists autouse `something`; execute skip fixture does not fire it. No View. |
| 14608c `-o addopts=tests` | HOLD | Rescues 9.1.0. `alt_inside` 1 pass including 9.1.0. No View. |

None exported. No quality PASS. HDD consumer still has 1 discovery case. **小規模試行**. Not holdout.

## 22:50 vacancy host 実機 (HOLD not PASS)

| Issue | Quality | Why |
| --- | --- | --- |
| 3062 setup.cfg log_format | HOLD | pytest 8.4.1–9.1.1 getini raw `%(filename)s...` and live-log applies it. Stock ConfigParser interpolation InterpolationMissingOptionError. No View. |
| 7777b package-scoped fixtures | HOLD | `--setup-show a/` 3 pass 8.4.1–9.1.1. `pkg_a` once; `pkg_b` only around `test_b1`. No 8/9 delta. No View. |
| 14807 setup.cfg `[tool:pytest] addopts=-q` | HOLD | collect-only 1 test 8.4.1–9.1.1. Table is read (unlike `[pytest]` Failed). No View. |

None exported. No quality PASS. HDD consumer still has 1 discovery case. **小規模試行**. Not holdout.

## 23:00 vacancy host 実機 (HOLD not PASS)

| Issue | Quality | Why |
| --- | --- | --- |
| 13704b `a/a a/` | HOLD | 8.4.1 n=1 parent dropped; pytest 9 n=3. keep-duplicates n=4. Same family as `a/b a/`. No View. |
| 7777 `a/b2 a/` | HOLD | 8.4.1 n=1; pytest 9 n=5. keep-duplicates run 6. Sibling overlap same 8.4.1 parent-drop. No View. |
| 13925 `'' .` | HOLD | ZeroDivision all versions (both args are cwd). No View. |
| 3062 escaped `%%` | HOLD | ConfigParser InterpolationSyntaxError; pytest getini keeps literal `%%`. No View. |
| 14737 setup-show | HOLD | `--setup-show skippedpkg` still 1 fail; skip not applied. No View. |

None exported. No quality PASS. HDD consumer still has 1 discovery case. **小規模試行**. Not holdout.

## 23:14 vacancy host 実機 (HOLD not PASS)

| Issue | Quality | Why |
| --- | --- | --- |
| 13704b sibling / same-dir | HOLD | `a/a a/b` n=2 all (parent-drop is parent-only). `a/ a/` n=3 unique / keep-duplicates 6. No View. |
| 13704 same-dir twice | HOLD | `tests/ tests/` n=2 unique all; keep-duplicates n=4. Same-file twice stays 2 vs 1. No View. |
| 7777 sibling / same-dir | HOLD | `a/b a/b2` n=4 all. `a/ a/` n=5 unique / keep-duplicates 10. No View. |
| 12083 same-dir twice | HOLD | `tests tests` n=2 unique all; keep-duplicates n=4. No View. |
| 13925 keep-duplicates `'' .` | HOLD | ZeroDivision all versions. `a/ a/` n=1 unique / keep-duplicates 2. No View. |
| 3062 ini/full-escaped | HOLD | pytest.ini `%%` InterpolationSyntaxError. Fully escaped ConfigParser succeeds; pytest getini keeps `%%`. No View. |
| 14807 named native+pytest | HOLD | pytest.toml `[pytest]`+native: 8.4.1 unread; pytest 9 `[pytest]` wins; no UsageError. No View. |
| 14737 setup-plan | HOLD | `--setup-plan skippedpkg` lists Function, no tests ran. Skip not applied. No View. |

None exported. No quality PASS. HDD consumer still has 1 discovery case. **小規模試行**. Not holdout.

## 23:45 vacancy host 実機 (HOLD not PASS)

| Issue | Quality | Why |
| --- | --- | --- |
| 13704b file-vs-parent | HOLD | `a/a/test_aa.py a/` 8.4.1 n=1 / pytest 9 n=3; keep-duplicates 4. File-vs-sibling-dir n=2 all. No View. |
| 7777 nested ancestor | HOLD | `a/b/c a/` 8.4.1 n=2 / pytest 9 n=5; keep-duplicates 7. Mid-parent 2 vs 3. Nested sibling n=3 all. No View. |
| 12083 same-subdir twice | HOLD | `tests/subdirectory` twice n=1 unique / keep-duplicates 2. No View. |
| 13925 `'' ''` | HOLD | ZeroDivision all versions (both empty args are cwd). No View. |
| 14807 both-tables leftover | HOLD | pytest.ini `[pytest]` wins. `-c` TOML `[pytest]`+native: 8.4.1 unread / pytest 9 native wins; no UsageError. No View. |
| 3062 tox.ini | HOLD | `[pytest]` raw getini + 1 pass. ConfigParser InterpolationMissingOptionError. No View. |

None exported. No quality PASS. HDD consumer still has 1 discovery case. **小規模試行**. Not holdout.

## 00:00 vacancy host 実機 (HOLD not PASS)

| Issue | Quality | Why |
| --- | --- | --- |
| 7777 deepest nested | HOLD | `a/b/c/d a/` 8.4.1 n=1 / pytest 9 n=5; keep-duplicates 6. Mid 1 vs 3. Vs Dir c 1 vs 2. Sibling n=2 all. No View. |
| 13704b file-in-parent | HOLD | `a/test_a.py a/` 8.4.1 n=1 / pytest 9 n=3; keep-duplicates 4. Two files n=2 all. No View. |
| 13925 `. .` | HOLD | ZeroDivision all. keep-duplicates 2 errors. No View. |
| 14964 keep-duplicates CASE1 | HOLD | still 9.1.0 later miss. Collect-only n=3 all (execute-only). No View. |
| 3062 pyproject `%%` | HOLD | getini keeps literal `%%` 1 pass all. No View. |

None exported. No quality PASS. HDD consumer still has 1 discovery case. **小規模試行**. Not holdout.

## 00:15 vacancy host 実機 (HOLD not PASS)

| Issue | Quality | Why |
| --- | --- | --- |
| 7777 nested file vs ancestor | HOLD | `a/b/c/d/test_d.py a/` 8.4.1 n=1 / pytest 9 n=5; keep-duplicates 6. Same vs cwd. No View. |
| 13704b `a/a .` | HOLD | child-dir vs cwd 8.4.1 n=1 / pytest 9 n=3; keep-duplicates 4. No View. |
| 14964 setup-plan | HOLD | CASE1 lists guard for later test through 9.0.3 only; miss visible at plan. No View. |
| 14964d keep-duplicates | HOLD | still 9.1.0 later miss; collect-only n=3 all. No View. |
| 14737 tb=short | HOLD | still 1 fail assert False all versions. No View. |
| 3062 escaped live-log | HOLD | prints literal `%(filename)s:3` (logging treats `%%` as percent). No View. |

None exported. No quality PASS. HDD consumer still has 1 discovery case. **小規模試行**. Not holdout.

## 00:31 vacancy host 実機 (HOLD not PASS)

| Issue | Quality | Why |
| --- | --- | --- |
| 14971/14640 setup-plan gap | HOLD | 8.4.1–9.0.3 fixture for both; 9.1.0/9.1.1 later ERROR not found (rc=1). No-gap OK. Requested-fixture miss errors at plan. No View. |
| 14964 --lf / reverse plan | HOLD | `--lf` 8.4.1 both errors; 9.1.0 only test_a (later miss not last-failed). Reverse plan later test without guard from 9.1.0. No View. |
| 7777 nested file vs sibling | HOLD | `a/b/c/d/test_d.py a/b2` n=2 all. No View. |
| 3062 full-escaped live-log | HOLD | ValueError unsupported format character `W` 8.4.1–9.1.1. No View. |

None exported. No quality PASS. HDD consumer still has 1 discovery case. **小規模試行**. Not holdout.

## 00:41 vacancy host 実機 (HOLD not PASS)

| Issue | Quality | Why |
| --- | --- | --- |
| 14971/14640 --lf/--ff after gap | HOLD | 9.1.0 later ERROR is last-failed (`--lf` reruns test_b). `--ff` still shows later miss. 8.4.1 `--lf` 3 pass. No View. |
| 14964 --ff/--maxfail=1 | HOLD | `--ff` still later PASS. `--maxfail=1` stops at test_a (hides later miss). No View. |
| 14964d --lf | HOLD | 8.4.1 both errors; 9.1.0 only test_a. No View. |
| 7777 file vs containing dir | HOLD | `test_d.py a/b/c/d` n=1 all; keep-duplicates 2. Two files n=2. No View. |
| 13704b file vs containing dir | HOLD | `test_aa.py a/a` n=1 all; keep 2. Parent-file vs child-dir n=2. No View. |
| 14807 ini+toml / tox+toml | HOLD | 8.4.1 ini/tox wins; pytest 9 named pytest.toml wins. No View. |

None exported. No quality PASS. HDD consumer still has 1 discovery case. **小規模試行**. Not holdout.

## 01:02 vacancy host 実機 (HOLD not PASS)

| Issue | Quality | Why |
| --- | --- | --- |
| 14807 ini vs pyproject | HOLD | pytest.ini beats native/ini_options all versions. Named pytest.toml still beats setup.cfg from 9.0.1. No View. |
| 14807 ini+tox / ini+scfg | HOLD | pytest.ini wins all versions. No View. |
| 14964 --nf | HOLD | later miss still visible (unlike --lf). No View. |
| 14971/14640 --maxfail=1 | HOLD | later miss still visible (`..E`). Unlike 14964 --maxfail=1. No View. |
| 14737 --lf | HOLD | still 1 fail assert False. No View. |

None exported. No quality PASS. HDD consumer still has 1 discovery case. **小規模試行**. Not holdout.

## 01:15 vacancy host 実機 (HOLD not PASS)

| Issue | Quality | Why |
| --- | --- | --- |
| 14807 ini+pyboth | HOLD | 8.4.1 pytest.ini; pytest 9 UsageError dual pyproject tables. No View. |
| 14807 toml+pyproject | HOLD | pytest 9 toml wins; 8.4.1 toml unread. No View. |
| 14807 scfg+native | HOLD | 8.4.1 setup.cfg; pytest 9 native beats setup.cfg. No View. |
| 14964 --sw | HOLD | stuck on first error; hides later miss. No View. |
| 14971/14640 --nf | HOLD | later miss still visible. No View. |

None exported. No quality PASS. HDD consumer still has 1 discovery case. **小規模試行**. Not holdout.

## 01:30 vacancy host 実機 (HOLD not PASS)

| Issue | Quality | Why |
| --- | --- | --- |
| 14807 tox+pyproject | HOLD | 8.4.1 tox.ini; pytest 9 native beats tox.ini. No View. |
| 14807 -c toml displaces ini | HOLD | `-c` unread `[pytest]` still drops cwd pytest.ini. No View. |
| 14971/14640 --sw | HOLD | later miss visible then stuck on later ERROR. Unlike 14964 --sw. No View. |

None exported. No quality PASS. HDD consumer still has 1 discovery case. **小規模試行**. Not holdout.

## 01:45 vacancy host 実機 (HOLD not PASS)

| Issue | Quality | Why |
| --- | --- | --- |
| 14807 -c ini displaces native | HOLD | `-c custom.ini` only_cini even vs pyproject native on pytest 9. No View. |
| 14807 -c toml native vs named toml | HOLD | `-c` native displaces pytest.toml on pytest 9. No View. |

None exported. No quality PASS. HDD consumer still has 1 discovery case. **小規模試行**. Not holdout.

## 02:01 vacancy host 実機 (HOLD not PASS)

| Issue | Quality | Why |
| --- | --- | --- |
| 14807 -c toml unread displaces native | HOLD | unread `[pytest]` `-c` drops pyproject native on pytest 9 (defaults). No View. |
| 14807 -c ini vs tox/ini_options | HOLD | `-c custom.ini` only_cini displaces tox.ini and ini_options. No View. |

None exported. No quality PASS. HDD consumer still has 1 discovery case. **小規模試行**. Not holdout.

32113 public files remain discovery. Related PRs in mini-followup remain 正解 and stay off the consumer.

## Acquisition vs eligibility

Fetching can succeed while eligibility for HDD stays quality+漏洩 PASS bound to a View hash. This screen does not mint PASS.
