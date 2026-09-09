# Host 実機 index (not Dreamer-facing)

| Case | Result | Consumer |
| --- | --- | --- |
| Deno 32113 public files | Deno 2.8.1: run1 foo+deno.lock rc0; run2 '@.' rc1 | discovery only; not 未知holdout |
| pytest#14011 | 9.0.1 both tests fail (variable None); 9.1.1 rc=1 | HOLD no View |
| pytest#14591 | 9.0.3 4 pass; 9.1.0 duplicate parametrization; 9.1.1 4 pass | HOLD no View |
| pytest#13479 | 8.4.1+freezegun: fixture ff not found; 9.1.1 rc=1 | HOLD no View |
| pytest#13885 | 8.4.1/9.0.1 autouse assert 0 under skipIf; 9.1.1 rc=0 | HOLD no View |
| pytest#13754 | setup-plan 8.4.1/9.0.1/9.1.1 rc=0 | HOLD no View |
| pytest#14095 | 9.0.1/9.1.1 rc=1 class fixture a does not rebuild module b | HOLD no View |
| pytest#13965 | N=1 9.0.1/9.1.1 rc=0 | HOLD no View |
| pytest#14775 | 8.4.1/9.0.1 -Werror 2 pass; 9.1.1 rc=1 `_finalizers` AssertionError | HOLD no View |
| pytest#13925 | `pytest -q '' a/`: 8.4.1 1 pass; 9.0.1/9.1.1 collect ZeroDivisionError | HOLD no View |
| pytest#14253 | 9.0.1/9.1.1 rc=3 log_cli_level int TypeError | HOLD no View |
| pytest#14092 | 9.0.1/9.1.1 rc=3 tmp_path_retention_count int TypeError | HOLD no View |
| pytest#14650 | 9.1.0/9.1.1 rc=2 duplicate parametrization IDs | HOLD no View |
| pytest#14094 | 9.0.1/9.1.1 rc=1 `pytest.Monkeypatch` AttributeError | HOLD no View |
| pytest#14412 | 9.1.1 rc=0 (sleep shortened) | HOLD no View |
| pytest#14431 | 9.1.1 rc=0 add() not a cache bug | HOLD no View |
| pytest#14514 | foo.test.py collect rc=2 | HOLD no View |
| pytest#14004 | 9.1.1 rc=0 nested autouse | HOLD no View |
| pytest#14800 | 8.4.1/9.0.1 2 pass 1 skip; 9.1.0/9.1.1 `_finalizers` | HOLD no View |
| pytest#14447 | 9.0.1/9.1.1 rc=1 walrus rewrite | HOLD no View |
| pytest#13882 | 9.1.1 2 passed; does not reproduce reporter | HOLD no View |
| pytest#14819 | rewrite ZeroDivision+boom 8.4.1–9.1.1; `--assert=plain` short-circuit all versions | HOLD no View |
| pytest#14820 | rewrite `99==0` 8.4.1–9.1.1; `--assert=plain` 2 pass all versions | HOLD no View |
| pytest#14971 | 8.4.1/9.0.1 3 pass; 9.1.1 nested fixture missing | HOLD no View |
| pytest#14691 | 8.4.1/9.0.1/9.1.1 fixture sample not found | HOLD no View |
| pytest#14445 | 8.4.1–9.1.1 walrus double-eval; `--assert=plain` 2 pass all versions | HOLD no View |
| pytest#13784 | 8.4.1 -s stdout doubled; 9.1.1 once | HOLD no View |
| pytest#5203 | 8.4.1/9.0.1/9.1.1 rc=1 TestB b=8 not 6 | HOLD no View |
| pytest#2043 | 8.4.1 collect error; 9.0.1 4 pass; 9.1.0 dup param; 9.1.1 4 pass | HOLD no View |
| pytest#14640 | 9.1.1 interleaved CLI missing `shared`; sorted 3 pass | HOLD no View |
| pytest#14737 | 8.4.1/9.0.1/9.1.1 skip in `__init__.py` does not apply | HOLD no View |
| pytest#14048 | 8.4.1/9.1.1 `--pyargs` rc=4 missing `__init__.py` | HOLD no View |
| pytest#14964 | 9.1.1 interleaved `a.py test_x.py b.py` test_b misses autouse; 8.4.1/9.0.1 both error | HOLD no View |
| pytest#14101 | 9.0.1/9.0.3/9.1.0/9.1.1 xfail_strict XPASS; 8.4.1 no subtests plugin | HOLD feature |
| pytest#14148 | `-p no:cacheprovider` AttributeError cache; default pass | HOLD no View |
| pytest#14608 | `pytest A --from-b` unrecognized 8.4.1 and 9.1.1; `A B` pass | HOLD no View |
| pytest#14412 | 9.0.1/9.1.0/9.1.1 later subtests `0.000us`; 8.4.1 no times | HOLD no View |
| pytest#14095 | 8.4.1/9.0.1/9.1.1 class a does not rebuild module b | HOLD no View |
| pytest#13965 | N=1 8.4.1/9.0.1/9.1.1 pass | HOLD no View |
| pytest#14935 | user-scoped `pytest-of-<user>/`; proj-a scratch evicted; no `.origin` | HOLD design |
| pytest#14640 | 9.1.0/9.1.1 interleaved `shared` missing; sorted 3 pass | HOLD no View |
| pytest#14808 | ini_options array getini returns list; `[tool.pytest]` TypeError | HOLD no View |
| pytest#14560 | dict-wrapper parametrize collect KeyError `__name__` | HOLD no View |
| pytest#14613 | `-o cache_dir` per-project trees; no `PYTEST_CACHE_DIR_BASE` | HOLD feature |
| pytest#14683 | stripped doctest_namespace 8.4.1/9.0.1/9.1.1 pass; no nimbus | HOLD no View |
| pytest#13957 | collect-only IDs `[cpu-half-ip-1-1-True]` all versions; no swap | HOLD no View |
| pytest#14051 | pytest.main space and equals both pass; no sigstore importError | HOLD no View |
| pytest#14476 | `-k "baidu and not logo"` collects search only | HOLD no View |
| pytest#14444 | `pytest_load_initial_conftests` cannot force capture=sys; `pytest_configure` can | HOLD feature |
| pytest#14392 | `is_fully_escaped(r"\\.")` True on 8.4.1/9.0.1, False on 9.1.1 | HOLD no View |
| pytest#14436 | happy caplog pass; session ScopeMismatch; no:logging fixture missing | HOLD no View |
| pytest#13699 | asynctest 0.13.0 on 3.14 AttributeError coroutine; importorskip fails | HOLD no View |
| pytest#14696 | existing file as `--write-idents` value: unrecognized 8.4.1–9.1.1; missing file loads except 9.1.0 | HOLD no View |
| pytest#14841 | pytester+mp deferred-import-fail: resource_tracker KeyError 8.4.1–9.1.1 (1 fail / 3 pass) | HOLD no View |
| pytest#14448 | rewrite `assert 1 == 99` / `assert 0 == 99`; no `where` subscript/IfExp line | HOLD no View |
| pytest#14323 | Popen DEVNULL default/fd/sys/-s all pass on macOS 3.14 | HOLD no View |
| pytest#14488 | `caplog.handler` after stash del: opaque StashKey KeyError 8.4.1–9.1.1 | HOLD no View |
| pytest#14635 | HA-pattern mini collects/runs 8.4.1–9.1.1; no `function uses no argument`; HA not cloned | HOLD no View |
| pytest#14694 | `--rootdir` testing/ + parent doctest: pass 8.4.1–9.0.3; NameError 9.1.0/9.1.1 | HOLD no View |
| pytest#14877 | default 32 plugins; dir() sum 1609–1701; not a timed A/B | HOLD no View |
| pytest#14973 | `addModuleCleanup` flag written by unittest, missing under pytest 8.4.1–9.1.1 | HOLD no View |
| pytest#14812 | teardown makereport `caplog.text` INTERNALERROR StashKey KeyError 8.4.1–9.1.1 | HOLD no View |
| pytest#14702 | fixture doctest on 3.14: 2 pass 1 skip; no INTERNALERROR; no jaraco | HOLD no View |
| pytest#13985 | `[tool.pytest] addopts="-q"` TypeError on 9.x; list form pass; 8.4.1 ignores table | HOLD no View |
| pytest#13922 | extra positional rc=4 file-not-found; no `Do not expect file_or_dir` UserWarning on 3.14 | HOLD no View |
| pytest#14807 | `-c` `[pytest]` ignored; both tables no UsageError (ini_options wins); `pytest.toml` from 9.0.1; pyproject `[pytest]` ignored | HOLD no View |
| pytest#14514b | default import `pkg.foo` ImportError; `--import-mode=importlib` collect rc=0 | HOLD no View |
| pytest#14255 | quoted `log_cli_level="INFO"` pass on 9.x; native int 10 TypeError | HOLD no View |
| pytest#14389 | raises match-fail: `During handling` on 8.4.1/9.0.1/9.0.3; omitted from 9.1.0 | HOLD no View |
| pytest#13913 | testpaths+idents.txt: 8.4.1 pass; pytest 9 unrecognized `--db --write-idents`; explicit `tests/` always pass | HOLD no View |
| pytest#14700 | 3.14 skipped fixture doctest 1 skip; no `line is not None`; no jaraco | HOLD no View |
| pytest#14762 | host 3.14.5 collect rc=0; 3.15b4 SEGFAULT not reproduced | HOLD no View |
| pytest#9298 | macOS PYTHONPYCACHEPREFIX writes rewritten test_foo pyc; Windows missing-pyc not reproduced | HOLD no View |
| pytest#14811 | list-as-string getini AssertionError; no PytestRemovedIn10Warning on 8.4.1–9.1.1 | HOLD no View |
| pytest#13755 | session `heavy_fixture` 4 params / 10 setups on 8.4.1–9.1.1 | HOLD no View |
| pytest#14084 | `--pyargs` from subdir needs PYTHONPATH=..; PYTHONPATH=. rc=4 same 8.4/9.x | HOLD no View |
| pytest#14514c | top-level `foo.test.py`: default `No module named 'foo'`; importlib 1 pass 8.4.1–9.1.1 | HOLD no View |
| pytest#13699 extra | importorskip AttributeError on 8.4.1–9.1.1; import asynctest rc=1 | HOLD no View |
| pytest#14094b | MonkeyPatch spelling: 1 pass 2 fail restore-missing on 8.4.1–9.1.1 | HOLD no View |
| pytest#11502 | `--config-file=/dev/null` `rootdir: /dev`; collect-only no warning; run PytestCacheWarning; nocache no warning | HOLD no View |
| pytest#14705 | `-c` `[pytest]` ignored; `[tool.pytest]` from 9.0.1; custom ini_options read on 8.4.1 | HOLD no View |
| pytest#14716 | `-c` wrong ext silent; missing `.ini` FileNotFoundError traceback | HOLD no View |
| pytest#14916 | rewrite lists index-diff; `f()` `where 42 = f()` not `<function>` | HOLD no View |
| pytest#14814 | starred rewrite `(9,[9])`; walrus-tuple rewrite pass; plain pass | HOLD no View |
| pytest#14431 | default collect skips `test.py` 8.4.1–9.1.1; explicit `test.py` 1 pass | HOLD no View |
| pytest#14608 extra | `cd A && pytest --from-b` unrecognized 8.4.1–9.1.1; ini root 2 pass | HOLD no View |
| pytest#14608c | no-args `--db-url` 9.1.0-only miss on direct `test*` (`tests`/`test-foo`/`testdir`/`testfoo`); `_tests`/`Tests` never initial | HOLD no View |
| pytest#14104 | session-fixture gap 3 pass; `--setup-show` carries `foo[1]` across gap | HOLD no View |
| pytest#14271 | monkeypatch delattr/delitem raising=False then assign; hasattr/`in` True 8.4.1–9.1.1 | HOLD no View |
| pytest#13957b | comment MRE nodeids `b1-a1` on 8.4.1 vs `a1-b1` on pytest 9; run 4 pass; swap args restores | HOLD no View |
| pytest#13755b | further-minimized session `fix_once` torn down after test_a; test_b ERROR; 4 SETUP S | HOLD no View |
| pytest#13976 | fixture params override 9.1.0-only duplicate; ids= does not rescue; generate_tests 5 pass on 9.1.0 | HOLD no View |
| pytest#14650b | no strict ini: auto-suffix `1-2_0`/`1-2_1` 2 pass 8.4.1–9.1.1 | HOLD no View |
| pytest#14650c | pytest.ini `[pytest]` and `ini_options` strict: 8.4.1 unknown+suffix; 9.x duplicate ERROR | HOLD no View |
| pytest#9703b | `-c config/` same-named tests collapse to `config::test_same`; `--lf` reruns both | HOLD no View |
| pytest#13246 | `-c config/pytest.ini` sibling fixture shadow; `--rootdir=.` 2 pass | HOLD no View |
| pytest#9703 | `-c config/` collapsed `config::` nodeids; autouse leak gone from 9.1.0 | HOLD no View |
| pytest#14817 | method-call rewrite: `where 42 = compute()` + bound method; not `Obj().compute()` | HOLD no View |
| pytest#14816 | IfExp rewrite `assert 0 == 99`; no `where (... if True else ...)` | HOLD no View |
| pytest#14815 | subscript rewrite `assert 1 == 99`; no `where {'a': 1}['a']` | HOLD no View |
| leftover PRs 14446/14453/14593/14622/14624/14670/14750/14777/14821/14850/14921 | repair/tooling; symptoms already reconstituted | HOLD no View |
| pytest#9703 | `-c config/` `config::` nodeids; autouse leak 8.4.1–9.0.3 gone 9.1.0 | HOLD no View |
| pytest#13246 | sibling `value` shadow `FAILED config::test2`; `--rootdir=.` 2 pass; subdir invoke same | HOLD no View |
| pytest#9703b | same-named `test_same` both `config::test_same`; `--lf` reruns both; `--rootdir=. --lf` only failed | HOLD no View |
| pytest#14004b | `sdk/` testpaths leak inner autouse 8.4.1–9.0.3; gone 9.1.0; explicit path no leak | HOLD no View |
| pytest#14608c pythonpath | pythonpath / `-o` / ini_options do not rescue 9.1.0; `addopts=tests` does; `--noconftest` unrecognized all | HOLD no View |
| pytest#14431 python_files | `python_files=test.py` default collect 1 pass 8.4.1–9.1.1 | HOLD no View |
| pytest#14800 setup-plan | `--setup-show` 9.0.1 still 2 pass 1 skip; `--setup-plan` no tests ran 8.4.1–9.1.1 | HOLD no View |
| pytest#14694 pythonpath | `pythonpath=src/pkg/testing` still NameError 9.1.0/9.1.1 | HOLD no View |
| pytest#13913 pythonpath | `pythonpath=["tests"]` still pytest 9 unrecognized `--db --write-idents` | HOLD no View |
| pytest#14514 pythonpath | `pythonpath=pkg` still `foo.test` ModuleNotFound; importlib 1 pass | HOLD no View |
| pytest#14696 pythonpath | `pythonpath=tests` still existing-file unrecognized all; missing file 9.1.0-only | HOLD no View |
| pytest#14807 extras | pyproject `[tool.pytest]` list from 9.0.1; string TypeError 9.x; pytest.toml only `[pytest]`; native+ini_options UsageError on 9; setup.cfg `[pytest]` Failed; ini_options string works | HOLD no View |
| pytest#13925 reverse | `a/ ''` same 8/9 split; `-- a/` 1 pass all | HOLD no View |
| pytest#12083 two files | distinct files n=2 all versions; keep-duplicates reverse n=3 all | HOLD no View |
| pytest#14608c PYTEST_ADDOPTS | env path arg rescues 9.1.0 like addopts=tests | HOLD no View |
| pytest#13925 a/ . | overlapping cwd `.` dropped on 8.4.1 when `a/` also given | HOLD no View |
| pytest#14412 ini_options times | 8.4.1 whole-test ms no subtest us; pytest 9 later 0.000us | HOLD no View |
| pytest#14640 reverse | later assignment after gap misses shared from 9.1.0; 8.4.1 re-SETUP | HOLD no View |
| pytest#14148 cache_on 8.4.1 | default 1 pass; AttributeError only no:cacheprovider | HOLD no View |
| pytest#14971 reverse/setup-show | 9.1.0 no re-SETUP nested_fixture after gap; later services miss | HOLD no View |
| pytest#14964 reverse/setup-show | 9.1.0 drops autouse guard after gap; later test_a passes | HOLD no View |
| pytest#13704 keep-duplicates | dir/file n=3 all; same-file twice n=2 all | HOLD no View |
| pytest#14640/14971 dir collect | directory collect pass all versions including 9.1.0 | HOLD no View |
| pytest#14964 no-gap | a.py b.py both ERROR all; tests/ rc=5; miss needs gap | HOLD no View |
| pytest#14640 assignment-only | no resume gap 2 pass all versions | HOLD no View |
| pytest#14971 one-services+gap | 2 pass all; miss needs two same-conftest files with gap between | HOLD no View |
| pytest#14964 one-file+gap | still guard all versions; miss needs two tests/ files with gap between | HOLD no View |
| pytest#5203 setup-show | b built from first module a all versions | HOLD no View |
| pytest#13885 setup-show | autouse fires 8.4.1–9.0.3; skip fixture from 9.1.0 | HOLD no View |
| pytest#14095 setup-show | same as 5203: b from first module a all versions | HOLD no View |
| pytest#13755 setup-show extra | 9.0.1/9.0.3/9.1.0 10 SETUP S | HOLD no View |
| pytest#13704b keep-duplicates | a/b a/ n=4 all (test_b twice) | HOLD no View |
| pytest#7777 a/b collect | a/b n=3; a/b/c n=2 all versions | HOLD no View |
| pytest#14964d reverse | reverse gap same 9.1.0 miss | HOLD no View |
| pytest#12083 | overlap `test_one.py tests` collect 1 on 8.4.1 / 2 on pytest 9; keep-duplicates 3 | HOLD no View |
| pytest#13704 | `tests/ tests/test_it.py` 1 vs 2; same file twice 2 vs 1 (8.4.1 vs pytest 9) | HOLD no View |
| pytest#7777 | nested packages collect 5; keep-duplicates still 5 (no pytest-6 dupes) | HOLD no View |
| pytest#13704b | `a/b a/` 1 on 8.4.1 / 3 on pytest 9; `a/a` before `a/b` | HOLD no View |
| pytest#14964d | `test_*.py` names: dir/no-gap both ERROR; interleaved gap still 9.1.0 miss | HOLD no View |
| pytest#7777 overlap run | `a/b a/` 8.4.1 3 pass / pytest 9 5 pass; keep-duplicates run 8 all | HOLD no View |
| pytest#13925 keep-duplicates | `--keep-duplicates '' a/` / `a/ .` ZeroDivision on 8.4.1 too | HOLD no View |
| pytest#12083 keep-duplicates cwd | `tests .` n=4 all (cwd duplicates tests/) | HOLD no View |
| pytest#14775 -Werror | `_finalizers` from 9.1.0 when warning is an error; without -Werror 9.1.1 2 pass 1 warning | HOLD no View |
| pytest#13885 setup-plan | 9.1.0 plan still lists autouse `something`; execute skip fixture does not fire it | HOLD no View |
| pytest#14608c -o addopts | `-o addopts=tests` rescues 9.1.0; alt_inside 1 pass | HOLD no View |
| pytest#3062 | setup.cfg `log_format=%(filename)s` pytest getini raw + live-log 8.4.1–9.1.1; stock ConfigParser interpolation InterpolationMissingOptionError | HOLD no View |
| pytest#7777b | package-scoped `pkg_a`/`pkg_b` `--setup-show` 3 pass all versions; inner teardown does not drop outer | HOLD no View |
| pytest#14807 scfg-tool | setup.cfg `[tool:pytest] addopts=-q` collect 1 test 8.4.1–9.1.1 | HOLD no View |
| pytest#13784 setup-show | `--setup-show -svv test.py` same doubling through 9.0.3 | HOLD no View |
| pytest#13976 setup-show | `--setup-show test_override.py` same 9.1.0 duplicate | HOLD no View |
| pytest#14650 collect-only | `test_strict.py` 8.4.1 auto-suffix 2 / pytest 9 duplicate IDs | HOLD no View |
| pytest#14104 dir collect | both gap layouts 6 pass all; session carry not a gap miss | HOLD no View |
| pytest#13704b a/a overlap | `a/a a/` 8.4.1 n=1 / pytest 9 n=3; keep-duplicates n=4 | HOLD no View |
| pytest#7777 a/b2 overlap | `a/b2 a/` 8.4.1 n=1 / pytest 9 n=5; keep-duplicates run 6 | HOLD no View |
| pytest#13925 empty-dot | `'' .` / `. ''` ZeroDivision all versions | HOLD no View |
| pytest#3062 escaped | `%%(filename)s` ConfigParser InterpolationSyntaxError; pytest getini keeps literal `%%` | HOLD no View |
| pytest#14011 setup-show | class `fix` per subclass; `self.variable` still None | HOLD no View |
| pytest#14691 setup-show | classmethod `sample` not found; no_cm 9.0.1/9.0.3/9.1.0 1 pass | HOLD no View |
| pytest#14048 pyargs collect | `--pyargs` with `__init__.py` 1 collected all | HOLD no View |
| pytest#13479 setup-show | `ff` not found all versions | HOLD no View |
| pytest#14737 collect-only | package pytestmark still Function not skipped | HOLD no View |
| pytest#14447 setup-show | still 3 fail all versions | HOLD no View |
| pytest#14084 collect-only | subdir PYTHONPATH=. rc=4; PYTHONPATH=.. 1 collected | HOLD no View |
| pytest#14392 extra | even-count `r"\\."` False from 9.1.0; `r"\."` True all | HOLD no View |
| pytest#14444 CLI capture | `--capture=sys` 1 pass all; hook append still fd | HOLD no View |
| pytest#13704b sibling | `a/a a/b` n=2 all; parent-drop is parent-only | HOLD no View |
| pytest#13704 same-dir twice | `tests/ tests/` n=2 unique / keep-duplicates 4 | HOLD no View |
| pytest#7777 sibling | `a/b a/b2` n=4 all; same-dir twice 5 / keep-duplicates 10 | HOLD no View |
| pytest#12083 same-dir twice | `tests tests` n=2 unique / keep-duplicates 4 | HOLD no View |
| pytest#13925 keep-duplicates empty-dot | `--keep-duplicates '' .` ZeroDivision all; `a/ a/` 1 / 2 | HOLD no View |
| pytest#3062 ini/full-escaped | pytest.ini `%%` InterpolationSyntaxError; full-escaped ConfigParser ok / pytest literal `%%` | HOLD no View |
| pytest#14807 named native+pytest | pytest.toml `[pytest]`+native: 8.4.1 unread / pytest 9 `[pytest]` wins; no UsageError | HOLD no View |
| pytest#14737 setup-plan | `--setup-plan skippedpkg` lists Function, no tests ran | HOLD no View |
| pytest#13704b file-vs-parent | `a/a/test_aa.py a/` 8.4.1 n=1 / pytest 9 n=3; keep-duplicates 4 | HOLD no View |
| pytest#7777 nested ancestor | `a/b/c a/` 8.4.1 n=2 / pytest 9 n=5; keep-duplicates 7; mid-parent 2 vs 3 | HOLD no View |
| pytest#12083 same-subdir twice | `tests/subdirectory` twice n=1 / keep-duplicates 2 | HOLD no View |
| pytest#13925 same-empty twice | `'' ''` ZeroDivision all | HOLD no View |
| pytest#14807 both-tables leftover | pytest.ini `[pytest]` wins; `-c` TOML native wins on 9; no UsageError | HOLD no View |
| pytest#3062 tox.ini | `[pytest]` raw getini; ConfigParser InterpolationMissingOptionError | HOLD no View |
| pytest#14935 leftover extras | unique `--basetemp` keeps from-a; shared overwrites; count=10 keeps; policy=all still last 3 | HOLD design |
| pytest#12083 subdirectory vs cwd | `tests/subdirectory .` 8.4.1 n=1 / pytest 9 n=2; keep-duplicates 3 | HOLD no View |
| pytest#13704 file-vs-parent other | `tests/test_other.py tests/` 8.4.1 n=1 / pytest 9 n=2; keep-duplicates 3 | HOLD no View |
| pytest#14608c collect/toml/native | collect-only still 9.1.0 miss; pytest.toml list/native addopts rescue | HOLD no View |
| pytest#14807 pairing leftover | `-c` INI `[tool:pytest]` ignored; tox.ini both `[pytest]` wins; setup.cfg both no Failed | HOLD no View |
| pytest#7777 deepest nested | `a/b/c/d a/` 8.4.1 n=1 / pytest 9 n=5; keep-duplicates 6 | HOLD no View |
| pytest#13704b file-in-parent | `a/test_a.py a/` 8.4.1 n=1 / pytest 9 n=3; keep-duplicates 4 | HOLD no View |
| pytest#13925 same-dot twice | `. .` ZeroDivision all; keep-duplicates 2 errors | HOLD no View |
| pytest#14964 keep-duplicates CASE1 | still 9.1.0 later miss; collect-only n=3 all | HOLD no View |
| pytest#3062 pyproject escaped | getini keeps literal `%%` 1 pass all | HOLD no View |
| pytest#12083 three-way | file+subdir+cwd n=2 all; three dirs 1 vs 2 keep-duplicates 5 | HOLD no View |
| pytest#7777 cwd-as-parent | `a/b/c .` same as `a/b/c a/` 2 vs 5 keep-duplicates 7 | HOLD no View |
| pytest#13704b cwd-as-parent | `a/b .` same as `a/b a/` 1 vs 3 keep-duplicates 4 | HOLD no View |
| pytest#14431 collect-only | default rc=5; explicit `test.py` 1 collected | HOLD no View |
| pytest#14800 tb=short | still `_finalizers` from 9.1.0; plain same | HOLD no View |
| pytest#14694 setup-show | 9.1.0 drops SETUP F `add_answer`; NameError | HOLD no View |
| pytest#13704 three-way | both files n=2 all; `test_it.py tests .` 1 vs 2 | HOLD no View |
| pytest#14101 tb=short | still XPASS on pytest 9 | HOLD feature |
| pytest#14775 tb=short | no `-Werror` 2 pass 1 warning from 9.1.0; `-Werror` 2 errors | HOLD no View |
| pytest#13885 tb=short | autouse ERROR through 9.0.3; skip from 9.1.0 | HOLD no View |
| pytest#14971/14640 collect-only gap | n=3 all including 9.1.0 (miss is execute) | HOLD no View |
| pytest#12083/13704/7777 file-vs-cwd | 8.4.1 drops cwd; pytest 9 unique-union; keep-duplicates restores | HOLD no View |
| pytest#13965 collect-only | default rc=5; explicit `test.py` 1 collected | HOLD no View |
| pytest#13754 collect-only | 4 collected all versions | HOLD no View |
| pytest#14591/2043 tb=short | same collect split as run | HOLD no View |
| pytest#14808 setup-show | ini_options list fail all; native TypeError on 9; pytest.ini pass | HOLD no View |
| pytest#14011 collect/tb | collect-only 2; `--tb=short` still None | HOLD no View |
| pytest#5203/14095 collect-only | 2 collected; miss is execute | HOLD no View |
| pytest#13976/14650 tb=short | same collect split as run | HOLD no View |
| pytest#14051 setup-show | 1 pass all | HOLD no View |
| pytest#14476 -k foo collect | both tests 8.4.1–9.1.1 | HOLD no View |
| pytest#7777 nested file vs ancestor | `a/b/c/d/test_d.py a/` 8.4.1 n=1 / pytest 9 n=5; keep-duplicates 6 | HOLD no View |
| pytest#13704b a/a vs cwd | `a/a .` 8.4.1 n=1 / pytest 9 n=3; keep-duplicates 4 | HOLD no View |
| pytest#14964 setup-plan | CASE1 lists guard for later test through 9.0.3 only | HOLD no View |
| pytest#14964d keep-duplicates | still 9.1.0 later miss; collect-only n=3 | HOLD no View |
| pytest#14737 tb=short | still 1 fail assert False all | HOLD no View |
| pytest#3062 escaped live-log | prints literal `%(filename)s:3` | HOLD no View |
| pytest#14971/14640 setup-plan gap | later ERROR not found from 9.1.0; no-gap OK | HOLD no View |
| pytest#14964 --lf | 8.4.1 both errors; 9.1.0 only test_a (later miss hidden) | HOLD no View |
| pytest#7777 nested file vs sibling | `a/b/c/d/test_d.py a/b2` n=2 all | HOLD no View |
| pytest#3062 full-escaped live-log | ValueError `%W` 8.4.1–9.1.1 | HOLD no View |
| pytest#14412 alt collect-only | isolated alt_ini/alt_iniopt 1 UnitTestCase all (times is execute) | HOLD no View |
| pytest#14696 iso_miss | isolated existing **and** missing `--write-idents` both 9.1.0-only unrecognized | HOLD no View |
| pytest#14048 setup-show pyargs | no PYTHONPATH rc=4; `PYTHONPATH=.` 1 pass all | HOLD no View |
| pytest#13965 setup-show | 1 pass all; pytest 9 reports 1000 subtests | HOLD no View |
| pytest#14004b collect-only sdk | **3 collected all** (not 4); leak is execute | HOLD no View |
| pytest#13755b collect-only | 4 collected all | HOLD no View |
| pytest#9703b collect-only | 2 `::test_same` all | HOLD no View |
| pytest#14800/14101/14775 collect-only | 3/2/2 collected; `_finalizers`/XPASS is execute | HOLD no View |
| pytest#13882/14683/14700/14635/14323 collect-only | 2/1/1/4/1 collected; miss is execute | HOLD no View |
| pytest#14971/14640 --lf after gap | 9.1.0 later ERROR is last-failed (reruns test_b); 8.4.1 `--lf` 3 pass | HOLD no View |
| pytest#14971/14640 --ff after gap | 9.1.0 `E..` later miss still visible | HOLD no View |
| pytest#14964 --ff/--maxfail=1 | `--ff` still shows later PASS; `--maxfail=1` hides later miss | HOLD no View |
| pytest#14964d --lf | 8.4.1 both errors; 9.1.0 only test_a | HOLD no View |
| pytest#7777 file vs containing dir | `test_d.py a/b/c/d` n=1 all; keep-duplicates 2 | HOLD no View |
| pytest#13704b file vs containing dir | `test_aa.py a/a` n=1 all; keep 2; parent-file vs child-dir n=2 | HOLD no View |
| pytest#14807 ini+toml / tox+toml | 8.4.1 ini/tox wins; pytest 9 named pytest.toml wins | HOLD no View |
| pytest#14640/14971 --lf rerun | later ERROR last-failed then **1 passed** (gap skipped) | HOLD no View |
| pytest#14004b setup-plan sdk | inner_fixture on outer tests through 9.0.3; gone 9.1.0 | HOLD no View |
| pytest#9703 setup-plan | autouse both files through 9.0.3; file2 none from 9.1.0 | HOLD no View |
| pytest#13755 setup-plan | 10 SETUP S / 10 TEARDOWN S all | HOLD no View |
| pytest#14104 setup-plan | session `foo[1]` carry at plan all | HOLD no View |
| pytest#7777b file-vs-cwd | `a/test_a.py .` / `a/b .` 8.4.1 n=1 / pytest 9 n=3; keep 4 | HOLD no View |
| pytest#14694/14812/14973/14702/13246/14814 collect-only | miss is execute | HOLD no View |
| pytest#13699 tb=short PYTHONPATH | still AttributeError coroutine | HOLD no View |
| pytest#14696 iso_miss setup-show | missing 9.1.0-only; existing unrecognized **all** | HOLD no View |
| pytest#13976/14591/2043 setup-plan | same collect split as run (9.1.0 duplicate) | HOLD no View |
| pytest#14650 setup-plan | 8.4.1 auto-suffix; pytest 9 duplicate IDs | HOLD no View |
| pytest#14148 cache-show | nodeids printed; no:cacheprovider unrecognized `--cache-show` | HOLD no View |
| pytest#14608c override-ini | `addopts=tests` rescues 9.1.0 on alt_inside; file addopts unrecognized all | HOLD no View |
| pytest#14412 durations=0 | not per-subtest us; pytest 9 still 3 subtests | HOLD no View |
| pytest#13784 tb=short -s | still doubling through 9.0.3 | HOLD no View |
| pytest#14817 setup-show | still bound-method intermediates | HOLD no View |
| pytest#14800 --lf | hides `_finalizers` (rerun 2 pass) | HOLD no View |
| pytest#14775 --lf -Werror | still 2 errors | HOLD no View |
| pytest#12083/13704/7777 setup-plan overlap | same drop as collect (8.4.1 1/1/3; pytest 9 2/2/5) | HOLD no View |
| pytest#13925 setup-plan empty | 8.4.1 drops cwd; pytest 9 ZeroDivision | HOLD no View |
| pytest#14444 setup-plan | hides capture fd vs sys | HOLD no View |
| pytest#14762 setup-show | 1 pass; no segfault | HOLD no View |
| pytest#13922 setup-show extra | rc=4; no UserWarning | HOLD no View |
| pytest#13885 --lf | 8.4.1–9.0.3 still ERROR; 9.1.0 skip no last-failed | HOLD no View |
| pytest#5203/14095 setup-plan | `b` from first module `a` all versions | HOLD no View |
| pytest#14011 setup-plan | class `fix` per subclass; None is execute | HOLD no View |
| pytest#14691 setup-plan | `sample` not found at plan all | HOLD no View |
| pytest#14444 collect-only | 2 collected; capture is execute | HOLD no View |
| pytest#13479 setup-plan | `ff` not found at plan all | HOLD no View |
| pytest#12083 reverse/keep plan | reverse 1 vs 2; keep-duplicates n=3 | HOLD no View |
| pytest#13704b setup-plan overlap | 8.4.1 n=1 / pytest 9 n=3; keep 4 | HOLD no View |
| pytest#7777b setup-plan overlap | 8.4.1 n=1 / pytest 9 n=3 | HOLD no View |
| pytest#14800 --ff | hides `_finalizers` (2 pass 1 skip) | HOLD no View |
| pytest#14775 --ff -Werror | still 2 errors | HOLD no View |
| pytest#13885 --ff | still 8/9 skip-vs-fire | HOLD no View |
| pytest#14101 --lf | XPASS not last-failed | HOLD feature |
| pytest#14613 cache-show after run | nodeids `p1/test_a.py::test_a` | HOLD no View |
| pytest#14148 nocache --cache-clear | unrecognized `--cache-clear` | HOLD no View |
| pytest#14650b setup-plan | 2 all (no-strict) | HOLD no View |
| pytest#14650c setup-plan | pytest 9 duplicate IDs | HOLD no View |
| pytest#14608c override-ini db-url | 1 pass including 9.1.0 | HOLD no View |
| pytest#14807 ini vs pyproject | pytest.ini beats native/ini_options all versions | HOLD no View |
| pytest#14807 scfg+toml | 8.4.1 setup.cfg; pytest 9 named pytest.toml | HOLD no View |
| pytest#14807 ini+tox / ini+scfg | pytest.ini wins all versions | HOLD no View |
| pytest#14964 --nf | later miss still visible (unlike --lf) | HOLD no View |
| pytest#14971/14640 --maxfail=1 | later miss still visible (`..E`); unlike 14964 | HOLD no View |
| pytest#14737 --lf | still 1 fail assert False; skip not applied | HOLD no View |
| pytest#13704 reverse/same-file plan | reverse 1 vs 2 keep 3; same file 2 vs 1 | HOLD no View |
| pytest#7777 reverse/file-cwd plan | reverse 3 vs 5 keep 8; file-vs-cwd 1 vs 5 | HOLD no View |
| pytest#13925 . a/ plan | 8.4.1 drop cwd / pytest 9 ZeroDivision | HOLD no View |
| pytest#14101 --ff | still XPASS | HOLD feature |
| pytest#13784 plain -s | still doubling through 9.0.3 | HOLD no View |
| pytest#14389 --tb=line | During handling gone 8.4.1 and 9.1.0+ | HOLD no View |
| pytest#13699 --assert=plain | still AttributeError coroutine | HOLD no View |
| pytest#14808/14448/14255 tb | list isinstance / no where / TypeError on 9 | HOLD no View |
| pytest#12083 subdir vs cwd plan | 8.4.1 n=1 / pytest 9 n=2 | HOLD no View |
| pytest#14694 tb=short doctest | NameError from 9.1.0 | HOLD no View |
| pytest#14841 setup-show | still resource_tracker | HOLD no View |
| pytest#13913 tb=short tests/ | 1 pass including 9.1.0 | HOLD no View |
| pytest#11502 tb=short | 1 pass nocache | HOLD no View |
| pytest#same-dir twice plan | unique 2/2/5/1; keep 4/4 | HOLD no View |
| pytest#14800/14775 --maxfail=1 | hides second error from 9.1.0 | HOLD no View |
| pytest#14964d --ff | later also ERROR (unlike --lf) | HOLD no View |
| pytest#14591/13976/2043/14650 --lf | collect-error is not last-failed | HOLD no View |
| pytest#13885 --maxfail=1 | still 8/9 skip-vs-fire | HOLD no View |
| pytest#14101 --maxfail=1 | still XPASS | HOLD feature |
| pytest#14817 --assert=plain | no bound-method `where` | HOLD no View |
| pytest#14608c --noconftest | unrecognized `--db-url` all | HOLD no View |
| pytest#14444 --capture=sys | 2 pass no_hook | HOLD no View |
| pytest#14807 ini+pyboth | 8.4.1 ini; pytest 9 UsageError dual pyproject tables | HOLD no View |
| pytest#14807 toml+pyproject | pytest 9 toml wins; 8.4.1 toml unread | HOLD no View |
| pytest#14807 scfg+native | 8.4.1 setup.cfg; pytest 9 native beats setup.cfg | HOLD no View |
| pytest#14964 --sw | stuck on first error; hides later miss | HOLD no View |
| pytest#14971/14640 --nf | later miss still visible | HOLD no View |
| pytest#14775 --nf -Werror | still 2 errors (does not hide `_finalizers`) | HOLD no View |
| pytest#13885 --nf | still 8/9 skip-vs-fire | HOLD no View |
| pytest#14101 --nf | still XPASS | HOLD feature |
| pytest#14964d --maxfail=1 | 1 error all (first ERROR stops) | HOLD no View |
| pytest#14591/2043 --ff | collect-error is not last-failed | HOLD no View |
| pytest#14815/14816 --assert=plain | no changelog `where` | HOLD no View |
| pytest#7777b reverse plan | 8.4.1 n=1 / pytest 9 n=3 | HOLD no View |
| pytest#12083 subdir vs parent plan | 8.4.1 n=1 / pytest 9 n=2 | HOLD no View |
| pytest#14814 --assert=plain | 3 pass (starred fail is rewrite-only) | HOLD no View |
| pytest#14444 with_hook --capture=sys | 2 pass | HOLD no View |
| pytest#14650 --ff | collect-error is not last-failed | HOLD no View |
| pytest#14148 cache-show after run | nodeids `test_cache.py::test_function` | HOLD no View |
| pytest#13246 setup-plan | SETUP `value` for both; shadow is execute | HOLD no View |
| pytest#9703 --ff | 2 pass no last-failed | HOLD no View |
| pytest#14807 tox+pyproject | 8.4.1 tox; pytest 9 native beats tox.ini | HOLD no View |
| pytest#14807 -c toml displaces ini | `-c` unread [pytest] still drops cwd pytest.ini | HOLD no View |
| pytest#14971/14640 --sw | later miss visible then stuck on later ERROR | HOLD no View |
| pytest#13704b same-dir unique plan | n=3 all | HOLD no View |
| pytest#7777b a/b2 a/ plan | 8.4.1 n=1 / pytest 9 n=3; keep n=4 | HOLD no View |
| pytest#13925 -- a/ plan | n=1 all | HOLD no View |
| pytest#13885 --sw | still 8/9 skip-vs-fire | HOLD no View |
| pytest#14101 --sw | XPASS is not stepwise-failed | HOLD no View |
| pytest#13913 no-path plan | 8.4.1 n=1 / pytest 9 unrecognized | HOLD no View |
| pytest#14808 pytest_ini tb | 1 pass all | HOLD no View |
| pytest#11502 setup-plan | 1 collected all | HOLD no View |
| pytest#14650b --lf | 2 pass no last-failed | HOLD no View |
| pytest#12083 three-way plan | n=2 all (file hides 8/9) | HOLD no View |
| pytest#13704 three-way plan | 8.4.1 n=1 / pytest 9 n=2 | HOLD no View |
| pytest#14964d --sw | stuck on first ERROR; hides later miss | HOLD no View |
| pytest#14737 --ff/--sw | still 1 fail; skip not applied | HOLD no View |
| pytest#13755b --lf | hides session-teardown miss (2 pass) | HOLD no View |
| pytest#13784 --tb=line -s | still doubling through 9.0.3 | HOLD no View |
| pytest#14650c --lf | collect-error is not last-failed | HOLD no View |
| pytest#14812 --assert=plain | still INTERNALERROR StashKey | HOLD no View |
| pytest#7777 keep a/b2 plan | n=6 all | HOLD no View |
| pytest#12083 keep three-way plan | n=4 all | HOLD no View |
| pytest#13704 keep three-way plan | n=5 all | HOLD no View |
| pytest#13755b --ff/--sw/--nf | --ff swaps miss onto test_a; --sw hides remaining; --nf still 2 errors | HOLD no View |
| pytest#5203/14095 --lf | hides rebuild miss (1 pass 1 deselected) | HOLD no View |
| pytest#14011 --lf | still 2 fail None | HOLD no View |
| pytest#14691 --lf | still sample not found | HOLD no View |
| pytest#14820/14445 --tb=line | still rewrite miss | HOLD no View |
| pytest#14255 int_native plan | TypeError on pytest 9 | HOLD no View |
| pytest#14807 -c ini displaces native | `-c custom.ini` only_cini even vs pyproject native on 9 | HOLD no View |
| pytest#14807 -c toml native vs named toml | `-c` native displaces pytest.toml on 9 | HOLD no View |
| pytest#5203/14095 --ff/--sw/--nf | --ff swaps miss; --sw hides; --nf still original | HOLD no View |
| pytest#13246 --lf/--ff/--nf/--sw | still sibling shadow; --sw stuck on first fail | HOLD no View |
| pytest#14011 --sw/--maxfail=1 | hides Test2 | HOLD no View |
| pytest#13479 --ff/--sw | still ff missing | HOLD no View |
| pytest#14812 --lf | still INTERNALERROR after pass | HOLD no View |
| pytest#14447 --lf | still 3 walrus fail | HOLD no View |
| pytest#14841 --lf | reruns resource_tracker fail | HOLD no View |
| pytest#14560 --lf | collect-error is not last-failed | HOLD no View |
| pytest#14807 -c toml unread displaces native | `-c` unread `[pytest]` drops pyproject native on 9 (defaults) | HOLD no View |
| pytest#14807 -c ini vs tox/ini_options | `-c custom.ini` only_cini displaces tox.ini and ini_options | HOLD no View |
| pytest#14819 --nf/--maxfail=1/--assert=plain | --nf still 2 fail; --maxfail=1 hides boom; plain 1 fail 1 pass | HOLD no View |
| pytest#14445 --assert=plain | 2 pass (walrus miss is rewrite-only) | HOLD no View |
| pytest#14800 --assert=plain | still `_finalizers` from 9.1.0; --lf/--ff/--sw hide it | HOLD no View |
| pytest#14775 -Werror --assert=plain | still 2 errors on 9.1.0; --sw hides second | HOLD no View |
| pytest#13755b --assert=plain --lf | still hides session-teardown miss | HOLD no View |
| pytest#11502 no:cacheprovider --nf/--sw | unrecognized; cacheprovider kept 1 pass | HOLD no View |
| pytest#14808 tool.pytest --lf | 8.4.1 pass; pytest 9 TypeError still last-failed | HOLD no View |
| pytest#14255 int_native --lf | pytest 9 configure TypeError is not last-failed | HOLD no View |
| pytest#14650c --nf/--sw | collect-error is not last-failed | HOLD no View |
| pytest#14253/14092 parent --lf | 8.4.1 leftover dummy collision; pytest 9 TypeError not last-failed | HOLD no View |
| pytest#14253/14092 isolated ini_options --lf/--ff/--nf/--sw | 1 pass all (TypeError is native table) | HOLD no View |
| pytest#14808 ini_options --lf/--ff/--nf/--sw | still list AssertionError; --sw stuck on it | HOLD no View |
| pytest#14808 tool_pytest --nf | 8.4.1 pass; pytest 9 TypeError still last-failed | HOLD no View |
| pytest#14560 --nf/--maxfail=1 | collect-error KeyError is not last-failed | HOLD no View |
| pytest#14807 pytest.cfg pairings | pytest.cfg ignored; native/toml from 9.0.1; ini/tox/setup.cfg/ini_options win; tox.ini beats setup.cfg; -c INI only_cini | HOLD no View |
| pytest#14807 setup.cfg [pytest] pairings | 8.4.1 sibling ini/tox suppress Failed; pytest 9 Failed always; native/toml Failed all | HOLD no View |
| pytest#14807 leftover-0347 | pytest.cfg does not suppress Failed; -c INI/TOML suppress all versions; ini_options 8.4.1 only; pytest.ini [tool:pytest] displaces pyproject | HOLD no View |
| pytest#14807 leftover-0371 PYTEST_ADDOPTS | -o python_files replaces tox/ini/cfg/native/toml; does not suppress setup.cfg [pytest] Failed | HOLD no View |
| pytest#14608c alt_lo_base --lf/--ff/--nf/--sw | 9.1.0 unrecognized both runs (not last-failed); other versions 1 pass | HOLD no View |
| pytest#14514c importlib --lf/--ff/--sw/--nf | 1 pass; default import collect ImportError not last-failed | HOLD no View |
| pytest#13913 tests/ --lf/--ff/--sw/--nf | 1 pass including 9.1.0 (path rescues) | HOLD no View |
| pytest#14148 --nf | 1 pass all | HOLD no View |
| pytest#13985 list/ini_options --ff/--nf/--sw | 1 pass; string --nf TypeError on 9 not last-failed | HOLD no View |
| pytest#14705 --lf/--ff/--nf/--sw | 1 pass no last-failed | HOLD no View |
| pytest#14255 quoted --ff/--nf | 1 pass all | HOLD no View |
| pytest#14048 PYTHONPATH --sw/--nf --pyargs | 1 pass all | HOLD no View |
| pytest#14412 isolated --lf/--ff | 1 pass (8.4.1 whole-test / pytest 9 3 subtests) | HOLD no View |
| pytest#14004b --ff/--nf/--sw from sdk | 3 pass; leak is not last-failed | HOLD no View |
| pytest#14808 pytest_ini --nf | 1 pass all | HOLD no View |
| pytest#14650c --maxfail=1 | 8.4.1 2 pass; pytest 9 collect-error not last-failed | HOLD no View |
| pytest#13985/14255 --maxfail=1 | pytest 9 configure TypeError is not last-failed | HOLD no View |
| pytest#11502 --cache-show after /dev/null run | lists `::test_a` (rootdir /dev) | HOLD no View |
| pytest#14608c alt_inside --lf/--ff/--sw | 1 pass including 9.1.0 (addopts=tests rescue) | HOLD no View |
| pytest#14650c ini_options --lf/--ff/--nf/--sw | 8.4.1 2 pass; pytest 9 collect-error not last-failed | HOLD no View |
| pytest#13913 no-path --ff/--sw | 8.4.1 1 pass; pytest 9 unrecognized `--db --write-idents` | HOLD no View |
| pytest#11502 --cache-clear | 1 pass all | HOLD no View |
| pytest#14048 --maxfail=1 --pyargs | 1 pass all | HOLD no View |
| pytest#14608c alt_lo_base --lf/--ff/--nf/--sw | 9.1.0 unrecognized both runs (not last-failed) | HOLD no View |
| pytest#13913 tests/ --ff/--sw | 1 pass all (path rescues option) | HOLD no View |
| pytest#14514c importlib --lf/--ff/--sw | 1 pass all | HOLD no View |
| pytest#13922 --lf/--ff/--sw | 1 pass all | HOLD no View |
| pytest#14431 alt_pyfiles --lf/--ff/--sw | 1 pass all | HOLD no View |
| pytest#14084 PYTHONPATH --lf/--ff --pyargs | 1 pass all | HOLD no View |
| pytest#14514c default --lf/--ff/--sw | collect ImportError is not last-failed | HOLD no View |
| pytest#14608c alt_lo_base --maxfail=1 | 9.1.0 unrecognized both runs | HOLD no View |
| pytest#13913 tests/ --lf/--nf | 1 pass all | HOLD no View |
| pytest#13922 -- extra --lf/--sw | rc=4 file-not-found not last-failed | HOLD no View |
| pytest#14084 --nf/--sw --pyargs | 1 pass all | HOLD no View |
| pytest#14094 --lf/--ff/--nf/--sw | still 2 Monkeypatch fail; --sw hides later | HOLD no View |
| pytest#14916 --lf/--ff/--nf/--sw | still 2 rewrite fail; --sw hides later | HOLD no View |
| pytest#14094b --lf/--ff/--sw | --lf reruns 2 fail; --sw hides later | HOLD no View |
| pytest#14811 parent --nf/--sw | 1 pass (getini fail is implicit/) | HOLD no View |
| pytest#14436 happy/nolog --lf/--ff/--sw | 1 pass all | HOLD no View |
| pytest#14436 session_fix --lf/--sw | still ScopeMismatch | HOLD no View |
| pytest#14094/14916 --maxfail=1 | hides later fail | HOLD no View |
| pytest#14811 implicit --ff | still 1 fail getini list | HOLD no View |
| pytest#14436 session_fix --ff/--nf/--maxfail=1 | still ScopeMismatch | HOLD no View |
| pytest#14488 --nf/--sw/--maxfail=1 | --nf still StashKey; --sw hides later pass | HOLD no View |
| pytest#14841 --nf/--sw | 8.4.1 still resource_tracker fail; --sw hides later | HOLD no View |
| pytest#14812 --maxfail=1 | still INTERNALERROR after pass (rc=3) | HOLD no View |
| pytest#13699 --maxfail=1 | still AttributeError | HOLD no View |
| pytest#14973 --nf/--sw/--maxfail=1 | 2 pass (cleanup miss not last-failed) | HOLD no View |
| pytest#14702 --nf/--sw/--maxfail=1 | 2 pass 1 skip | HOLD no View |
| pytest#14323/14762/14051 --nf/--sw/--maxfail=1 | 1 pass all | HOLD no View |
| pytest#14807 setup.cfg [pytest] vs pytest.cfg | Failed all (pytest.cfg does not suppress) | HOLD no View |
| pytest#14807 setup.cfg [pytest] vs ini_options | 8.4.1 only_iniopt; pytest 9 Failed | HOLD no View |
| pytest#14807 pytest.ini [tool:pytest] vs pyproject | test_default all (filename displaces native/ini_options) | HOLD no View |
| pytest#14807 --config-file=/dev/null | displaces cwd pytest.ini/native/setup.cfg | HOLD no View |
| pytest#3062 --log-cli | unrecognized rc=4 all | HOLD no View |
| pytest#3062 pytest.ini/pyproject live-log | even `-s -o log_cli=true` no live-log print; setup.cfg `[tool:pytest]` prints | HOLD no View |
| pytest#14807 -o python_files | replaces cwd python_files; rc=5 if that file is absent | HOLD no View |
| pytest#14807 PYTEST_ADDOPTS python_files | same replace as CLI -o; beats pytest.ini+native; CLI/override-ini win over env | HOLD no View |
| pytest#14807 python_files=test_*.py restore | test_default vs cwd pytest.ini/setup.cfg/tox/native | HOLD no View |
| pytest#14807 env vs -c / /dev/null | PYTEST_ADDOPTS python_files still applies with --config-file=/dev/null and beats -c custom.ini | HOLD no View |
| pytest#14807 -o addopts=-q | additive quiet; does not replace python_files | HOLD no View |
| pytest#3062 --log-cli-format / -o log_format | overrides setup.cfg live-log; pytest.ini/pyproject still no live-log | HOLD no View |
| pytest#3062 --log-file | setup.cfg writes live-log line; pytest.ini/pyproject empty even at DEBUG | HOLD no View |
| pytest#3062 asctime+date-format | prints HH:MM:SS when asctime is in the format | HOLD no View |
| pytest#14807 -o minversion=99 | 8.4.1 still collects; pytest 9 rc=4 citing active config (None: / /dev/null / custom.ini) | HOLD no View |
| pytest#14807 -o minversion=9.1 | 8.4.1 still collects; 9.0.1–9.0.3 rc=4; 9.1.0+ pass | HOLD no View |
| pytest#14807 -o minversion=9.0.2 / 9.1.1 | 9.0.2 is 9.0.1-only rc=4; 9.1.1 only 9.1.1 pass; last -o wins; CLI beats env | HOLD no View |
| pytest#14807 minversion error path | pytest.cfg None:; /dev/null /dev/null:; -c custom.ini; 8.4.1 never enforces | HOLD no View |
| pytest#14807 named pytest.toml minversion | 9.0.1 8.4.1 test_default / pytest9 only_pytest_toml; 9.1.1 only 9.1.1; 99 cites pytest.toml | HOLD no View |
| pytest#14807 minversion vs setup.cfg [pytest] | Failed first all versions; `-o minversion` does not suppress Failed | HOLD no View |
| pytest#14807 minversion vs tox.ini | 9.0.1 only_tox all; 9.0.3 9.0.1 rc=4 citing tox.ini | HOLD no View |
| pytest#14101 -o xfail_strict=true | 8.4.1 1 xfailed 1 error (no subtests); pytest 9 XPASS(strict) fail | HOLD no View |
| pytest#14807 --strict-config -o verbosity=2 | 8.4.1 rc=0; pytest 9 rc=4 unknown verbosity | HOLD no View |
| pytest#14807 --strict-config vs named toml/Failed | verbosity 8.4.1 collect / pytest9 rc=4; setup.cfg [pytest] Failed first; python_files only_pytest_toml all | HOLD no View |
| pytest#14807 -o addopts=--strict-config -o verbosity=2 | 8.4.1/9.0.1/9.0.3 rc=0; 9.1.0+ rc=4 | HOLD no View |
| pytest#3062 -o log_file vs pytest.ini | still empty (same split as --log-file) | HOLD no View |
| pytest#3062 -c /dev/null --log-file | default WARNING format (displaces cwd log_format); --log-file-format FILE:hello-log | HOLD no View |
| pytest#14807 addopts=--strict-config vs tox/setup.cfg | 8.4.1/9.0.1/9.0.3 rc=0; 9.1.0+ rc=4 | HOLD no View |
| pytest#3062 --strict-config log_cli | pytest.ini still no live-log; setup.cfg still prints | HOLD no View |
| pytest#14807 --strict-config python_files=test_*.py | restores test_default vs pytest.ini/setup.cfg/native/tox | HOLD no View |
| pytest#14807 Failed vs -o/--strict-config | setup.cfg [pytest] Failed not suppressed by -o/env/--strict-config; -c and /dev/null displace | HOLD no View |
| pytest#14807 env -c vs Failed with only_cini | PYTEST_ADDOPTS=-c custom.ini only_cini all; -c+verbosity Failed suppressed then pytest9 unknown | HOLD no View |
| pytest#14807 -c /dev/null vs Failed | same as --config-file=/dev/null: test_default; + only_cfg.py collects only_cfg; --override-ini still Failed | HOLD no View |
| pytest#14807 -c /dev/null vs dual cwd | pytest.ini+native / setup.cfg+native / ini+tox / tox+native / ini+setup.cfg / tox+setup.cfg: test_default all | HOLD no View |
| pytest#14807 -c /dev/null vs pyboth | displaces pytest 9 UsageError (test_default); + only_native.py collects only_native | HOLD no View |
| pytest#14807 addopts=--strict-config -c /dev/null verbosity | 8.4.1 rc=0 / 9.0.1-9.0.3 warning / 9.1.0+ rc=4; Failed displaced | HOLD no View |

| pytest#11502 leftover-0719 --cache-show /dev/null | after normal run cache empty at /dev/.pytest_cache | HOLD no View |
| pytest#14048 leftover-0710 /dev/null --pyargs | PYTHONPATH=. 1 pass all; without PYTHONPATH rc=4 missing __init__.py | HOLD no View |
| pytest#13913 leftover-0701 /dev/null | tests/ rescue survives /dev/null 1 pass including 9.1.0; no-path pytest 9 unrecognized; 8.4.1 parent leftover dummy --db collisions | HOLD no View |
| pytest#14608c leftover-0692 /dev/null + addopts=tests | alt_inside leftover-0251 rescue survives /dev/null (1 pass including 9.1.0); alt_lo_base rc=5; leftover-0566 /dev/null --db-url still 9.1.0 unrecognized | HOLD no View |
HOLD is not converted to PASS. These bytes stay off the Dreamer channel.
