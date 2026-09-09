# Pending snippet reconstitutions (host; not Dreamer)

Tree-only leftovers:

- 14635 Home Assistant core not cloned. A reduced fixture-closure mini was reconstituted and does **not** reproduce the collection error (8.4.1–9.1.1 collect/run pass). Still HOLD.

14436 happy-caplog minis reconstituted (no tavern KeyError). 14841 public pytester+mp snippet reconstituted (deferred-import-fail resource_tracker). Both HOLD.

14683 stripped doctest mini was reconstituted as HOLD (does not match nimbus/xarray reporter).

14101 feature snippet was reconstituted as HOLD (not a View).

Leftover complete pytest PRs without hv dirs (14446/14453/14593/14622/14624/14670/14750/14777/14821/14850/14921) are repair/tooling HOLD; symptoms already reconstituted. Do not apply PRs.

14608 invocation-dir `tests/` `--db-url` reconstituted as pytest-14608c: 9.1.0-only unrecognized. `testpaths=tests` does not rescue 9.1.0. Still HOLD; no View.

14817/14816/14815 rewrite-display minis reconstituted (bound-method / missing `where` lines). 14813 coverage PR is test-only HOLD. Do not apply PRs.

14104 session-fixture gap reconstituted: 3 pass all versions; `--setup-show` carries session fixture across the gap. 13976 comment is 14591 duplicate HOLD. 13246/9703 `-c config/` reconstituted HOLD.

14271 monkeypatch comment mini reconstituted (hasattr True; delitem True). 14476 leftover `-k foo` collects mark+name.

13957b comment MRE reconstituted: 8/9 nodeid swap; `-v` run matches collect. 13755b further-minimized session teardown ERROR all versions. Still HOLD; no View.

13976 fixture-params override reconstituted: 9.1.0-only duplicate parametrization (same family as 14591). Conftest layout same miss. `ids=` / `pytest.param` do not rescue. `pytest_generate_tests` workaround 5 pass on 9.1.0 (not a product). 14650b isolated no-strict auto-suffixes IDs. 14650c pytest.ini and ini_options both ERROR on 9.x. 14800 `--setup-show` `_finalizers` from 9.1.0 not 9.0.3. 9703b same-named tests under `-c config/` reconstituted HOLD. 14608c `confcutdir=.` does not rescue 9.1.0.

All leftover complete pytest/uv roots from expand `a9328ef4` are screened HOLD. Do not mint PASS.

11502 `/dev/null` and 14705 custom TOML minis reconstituted as HOLD (no View). 14094b MonkeyPatch spelling is a host control, not a Dreamer packet.

14716 `-c` invalid paths, 14916 rewrite gaps, and 14814 starred/walrus minis reconstituted as HOLD (no View).

9703/13246 `-c config/pytest.ini` public layouts reconstituted as HOLD (no View). Do not apply PR 14837.

9703b same-named `test_same` collapse + `--lf` reconstituted as HOLD. Do not apply PRs 14571/14579/14454.

14004b public `sdk/` + `testpaths=../tests/sdk` leak reconstituted as HOLD (gone from 9.1.0). Do not apply PRs 14098/14118.

14608c leftover pythonpath / `-o pythonpath` / ini_options pythonpath / `norecursedirs=tests` / `confcutdir=tests` / `collect_ignore=tests` / pythonpath-with-test-inside-tests do **not** rescue 9.1.0. `addopts = tests` does (ini path arg). `--noconftest` unrecognized on all versions. Still HOLD; no View.

14004b leftover pythonpath next to testpaths: still leak 8.4.1–9.0.3, gone 9.1.0. pythonpath does not change the leak.

14431 leftover `python_files = test.py` default-collects 1 pass 8.4.1–9.1.1. 14800 leftover `--setup-show` 9.0.1 still 2 pass 1 skip; `--setup-plan` no tests ran all versions. 14694 leftover pythonpath still NameError 9.1.0/9.1.1.

13913 leftover pythonpath still pytest 9 unrecognized `--db --write-idents`. 14514 leftover pythonpath still `foo.test` ModuleNotFound; importlib 1 pass. 14696 leftover pythonpath still existing-file unrecognized all versions; missing file still 9.1.0-only.

14807 leftover extras reconstituted: pyproject `[tool.pytest]` list from 9.0.1; string TypeError on 9.x; `pytest.toml` only `[pytest]` from 9.0.1; native+ini_options UsageError on pytest 9; `pytest.cfg` ignored all versions. Still HOLD; no View.

Leftover pytest 正解 PRs re-screened 22:03 JST (14821 snippet is 14820). uv leftover 8 still fences=0 HOLD. Do not apply PRs.

12083 overlapping collection args reconstituted as HOLD (8.4.1 drops subdirectory; pytest 9 collects both). Reverse args same split. Two distinct file args n=2 all versions. `--keep-duplicates` reverse n=3 all. 13925 `''`/`.` alone ZeroDivision all versions; reverse `a/ ''` same 8/9; `-- a/` 1 pass all. 14004b `--rootdir=.` still leak; `--rootdir=..` rc=5.

13704 `tests/ tests/test_it.py` reconstituted as HOLD (8.4.1 n=1 / pytest 9 n=2). Same file twice: 2 on 8.4.1 / 1 on pytest 9. Do not apply PR 13704.

7777 nested package tree reconstituted as HOLD (5 nested items; keep-duplicates still 5). 13704b `a/b a/` 1 on 8.4.1 / 3 on pytest 9 with `a/a` before `a/b`. 14964d `test_*.py` names still 9.1.0 interleaved-gap miss.

14807 leftover: setup.cfg `[pytest]` Failed all versions; ini_options string python_files works all; pytest.toml `[pytest]` string TypeError on 9. tox.ini `[tool:pytest]` ignored; pytest.ini `[tool:pytest]` ignored.

14608c leftover `PYTEST_ADDOPTS=tests` rescues 9.1.0 like ini/CLI path args. 13925 leftover `a/ .` / `. a/` same 8/9 cwd-overlap drop as `'' a/` and 12083.

14412 leftover ini_options/pytest.ini times: 8.4.1 whole-test ms, no per-subtest us; pytest 9 later 0.000us regardless of table. 14640 leftover reverse interleaved same 9.1.0 miss; `--setup-show` 8.4.1 re-SETUP after gap, 9.1.0 does not. 14148 leftover default cache 8.4.1 1 pass.

14971 leftover reverse/setup-show: same 9.1.0 no re-SETUP of nested_fixture after gap (family of 14640). 14964 leftover reverse/setup-show: 9.1.0 drops autouse guard after gap (later test passes). 13704 leftover `--keep-duplicates` dir/file n=3 all; same-file twice n=2 all.

14640/14971 leftover directory collect pass all versions. 14964 leftover `pytest tests` rc=5 (`a.py`/`b.py` not test_*); no-gap `a.py b.py` both ERROR all versions; python_files=*.py dir collect both ERROR all. The 9.1.0 miss needs interleaved file args **with a gap**. 14104 leftover setup-show 9.0.1/9.0.3 session carry.

14640 leftover assignment-only 2 pass all. 14971 leftover one-services+gap 2 pass all (miss needs **two** same-conftest files with a gap between). 14964 leftover one-file+gap still guard all versions (miss needs two tests/ files with a gap between). 5203 leftover setup-show `b` from first module `a` all versions. 13885 leftover setup-show autouse fires 8.4.1–9.0.3, skip fixture from 9.1.0.

14095 leftover setup-show same as 5203. 13755 leftover setup-show 9.0.1/9.0.3/9.1.0 10 SETUP S. 13704b leftover `--keep-duplicates a/b a/` n=4 all. 7777 leftover `a/b` n=3 / `a/b/c` n=2 all. 14964d leftover reverse gap same 9.1.0 miss.

2043 leftover `--collect-only`/`--setup-show` same 8.4.1 no-fixture / 9.1.0 duplicate / others 4. 7777 leftover overlap **run** 8.4.1 3 pass / pytest 9 5 pass; `--keep-duplicates` run 8 all. 13704b leftover run reverse 1 vs 3; keep-duplicates run 4 all. 14964d leftover `--setup-show` reverse same 9.1.0 miss; dir/no-gap both ERROR all.

13925 leftover `--keep-duplicates '' a/` and `a/ .`: ZeroDivision on **8.4.1 too** (restores dropped overlapping cwd). 12083 leftover `--keep-duplicates tests .` n=4 all (cwd duplicates tests/). 13704 leftover `--keep-duplicates tests/test_it.py tests/` n=3 / 3 passed all.

14640/14971 leftover `--setup-show` directory still re-SETUP `shared`/`nested_fixture` on 9.1.0 (no gap). 14775 leftover `-Werror` `_finalizers` from 9.1.0; `--setup-show` without `-Werror` 2 pass 1 warning on 9.1.0/9.1.1. 13885 leftover `--setup-plan` still lists autouse `something` on 9.1.0 (execute skip fixture does not fire it). 14608c leftover `-o addopts=tests` rescues 9.1.0; `alt_inside` 1 pass including 9.1.0. 14591 leftover collect-only/setup-show same 9.1.0 duplicate.

13784 leftover `--setup-show -svv test.py` same doubling 8.4.1–9.0.3 / once from 9.1.0. 13976 leftover `--setup-show test_override.py` same 9.1.0 duplicate. 14650 leftover `--collect-only test_strict.py` 8.4.1 auto-suffix 2 / pytest 9 duplicate IDs. 14104 leftover directory collect 6 pass all (session carry is not an interleaved-gap miss).

14011 leftover `--setup-show`: class `fix` SETUP per subclass; `self.variable` still None. 14691 leftover `--setup-show`: `sample` not found (no SETUP); no_cm 9.0.1/9.0.3/9.1.0 1 pass. 14048 leftover `--collect-only --pyargs` with `__init__.py` 1 collected all. 13479 leftover `--setup-show` `ff` not found all. 14737 leftover collect-only lists Function not skipped; conftest pytestmark 9.0.1/9.1.0 still fail; module pytestmark 8.4.1/9.0.1/9.1.0 skip. 14447 leftover `--setup-show` still 3 fail.

14084 leftover `subdir/` `PYTHONPATH=.` rc=4 on 9.0.3/9.1.0; `--collect-only --pyargs` matches run. 14392 leftover even-count `r"\\."` / `r"\\\\."` False from 9.1.0; `r"\."` True all. 14444 leftover CLI `--capture=sys` 1 pass all.

13754 leftover `--setup-show test.py` shared module same 8/9, 4 pass. 13965 leftover `-o python_files=test.py` 1 pass all.

14389 leftover `--assert=plain` drops `During handling` on 8.4.1 only; 9.0.1/9.0.3 still print it. 14819 leftover `--tb=short` still 2 fail all.

14820 leftover `--tb=short` still 1 fail 1 pass. 14445 leftover `--tb=short` still 2 fail (`1 != 1`; `6 == 3`). 14816/14815 leftover `--tb=short` still no changelog `where` line.

3062 leftover setup.cfg `log_format=%(filename)s`: pytest getini raw + live-log 8.4.1–9.1.1; stock ConfigParser interpolation InterpolationMissingOptionError. 7777 leftover package-scoped `pkg_a`/`pkg_b` `--setup-show` 3 pass all. 14807 leftover `setup.cfg` `[tool:pytest] addopts=-q` collect 1 all versions.

13704b leftover `a/a a/` 8.4.1 n=1 / pytest 9 n=3; keep-duplicates n=4. 7777 leftover `a/b2 a/` 8.4.1 n=1 / pytest 9 n=5; keep-duplicates run 6. 13925 leftover `'' .` ZeroDivision all. 3062 leftover escaped `%%(filename)s` ConfigParser InterpolationSyntaxError; pytest getini keeps `%%`. 14737 leftover `--setup-show` still 1 fail.

13755b leftover `--setup-plan` 4 SETUP S / 4 TEARDOWN S all. 13957b leftover `--setup-show` still 8/9 id swap. 14101 leftover `--setup-show` still XPASS. 14808 leftover collect-only 1 per layout. 14812 leftover `--tb=short` still INTERNALERROR. 14973 leftover `--setup-show` 2 pass cleanup missing. 14448 leftover `--tb=short` no `where`; `--assert=plain` bare AssertionError. 14814 leftover `--tb=short` starred still `(9,[9])`.

9703 leftover `--setup-show` explicit files autouse twice through 9.0.3, once from 9.1.0. 13985 leftover collect-only string addopts TypeError on pytest 9. 14253/14092 leftover collect-only TypeError int native table on pytest 9. 14650b leftover collect/show auto-suffix 2 pass. 14488 leftover `--tb=short` still StashKey. 14841 leftover `--tb=short` still resource_tracker on pytest 9.

14702 leftover `--setup-show --doctest-modules` 2 pass 1 skip. 13246 leftover `--setup-show` still sibling `value` shadow. 14613 leftover `-p no:cacheprovider -o cache_dir` pytest 9 unknown-option warning still 2 pass. 14004 leftover `--setup-show` 4 pass (no leak). 14004b leftover `--setup-show` from `sdk/` inner 3 through 9.0.3 / 1 from 9.1.0.

14560 leftover `--tb=short` still collect KeyError. 14051 leftover `--collect-only` 1. 14323 leftover `--setup-show` 1 pass.

14811 leftover `--collect-only` 1. 14255 leftover int native `--collect-only` TypeError on pytest 9; quoted 1 all. 14916 leftover `--tb=short` still introspects. 14705 leftover `--collect-only -c` same `[pytest]` vs `[tool.pytest]` split. 7777b leftover `a/b a/` 1 vs 3; keep-duplicates 4. 9703b leftover `--setup-show` both `test_same`. 14716 leftover `--setup-show -c config.ini` 1 pass; missing `.toml`/`.cfg` FileNotFoundError. 14094b leftover `--tb=short` still 2 fail 1 pass. 14608 leftover `--collect-only --from-b A` rc=4 / `A B` n=2. 13922 leftover `--collect-only -- extra` rc=4 no UserWarning.

14635 leftover `--setup-show` 4 pass. 14700 leftover `--setup-show` 1 skip. 13882 leftover `--setup-show` 2 pass. 14514b leftover `--collect-only` ImportError / importlib 1. 11502 leftover `--setup-show --config-file=/dev/null` nocache 1 pass.

14514c leftover `--collect-only` dir rc=5; explicit `foo.test.py` ImportError; importlib 1 collected. 14683 leftover `--setup-show --doctest-modules` 1 pass.

14094 leftover `--tb=short` Monkeypatch AttributeError. 13957 leftover `--setup-show` 1 pass no swap. 14148 leftover `--setup-show` cache off AttributeError / default 1 pass. 14650c leftover `--collect-only` 8.4.1 auto-suffix / pytest 9 ERROR. 13699 leftover without tree skip; with asynctest PYTHONPATH AttributeError. 14877 leftover plugin count 32. 14762 leftover `--collect-only` 1 no segfault. 9298 leftover `--setup-show` 1 pass.

13913 leftover `--collect-only --db sqlite --write-idents idents.txt` 8.4.1 1 collected / pytest 9 unrecognized. 14431 leftover `--setup-show test.py` 1 pass all.

14935 leftover extras: unique `--basetemp` keeps from-a; shared `--basetemp` overwrites `test_mark0`; `tmp_path_retention_count=10` keeps proj-a; count=0 / policy=none empty; policy=all still last 3 (`pytest-2,3,4`). `--collect-only` creates no tmp dirs. Still HOLD design; no View.

12083 leftover `tests/subdirectory .` / `. tests/subdirectory` / `tests/subdirectory ''`: 8.4.1 n=1 / pytest 9 n=2; `--keep-duplicates` n=3. Cwd-as-parent split that `tests .` did not show.

13704 leftover `tests/test_other.py tests/`: 8.4.1 n=1 / pytest 9 n=2; keep-duplicates 3. Two files n=2 all.

14608c leftover `--collect-only` still 9.1.0 unrecognized. CLI `--confcutdir` / importlib / `--rootdir` / `python_files` do not rescue. pytest.toml string addopts TypeError on 9; list/native addopts rescue (rc=5 at root / 1 pass inside tests/).

14807 leftover `-c custom.ini [tool:pytest]` ignored. tox.ini both `[pytest]` wins. setup.cfg both `[tool:pytest]` wins **no Failed**.

12083 leftover three-way `tests/subdirectory tests/test_one.py .`: n=2 all (file hides 8.4.1 cwd drop). Three dirs `tests/subdirectory tests .`: 8.4.1 n=1 / pytest 9 n=2; keep-duplicates n=5. 7777 `a/b/c .` same as `a/b/c a/`. 13704b `a/b .` same as `a/b a/`. 13925 `. .` ZeroDivision all; keep-duplicates 2 errors. 14431 `--collect-only` default rc=5 / explicit 1 collected.

14800 leftover `--tb=short`/`--assert=plain` still `_finalizers` from 9.1.0. 14694 leftover `--setup-show`: 9.1.0 drops SETUP F `add_answer` (NameError). 13704 leftover three-way both files n=2 all; `tests/test_it.py tests .` 1 vs 2. 14101 leftover `--tb=short` still XPASS.

14775 leftover `--tb=short` without `-Werror`: 2 pass 1 warning from 9.1.0. With `-Werror`: 2 errors. 13885 leftover `--tb=short` still skip from 9.1.0. 14971/14640 leftover `--collect-only` interleaved gap n=3 all (miss is execute).

12083/13704/7777/13704b leftover file-vs-cwd: 8.4.1 drops cwd. 13965 leftover `--collect-only` default rc=5 / explicit 1. 13754 leftover collect-only 4 all. 14591/2043 leftover `--tb=short` same collect split. 14808 leftover `--setup-show` surfaces getini (collect-only hid it). First R1 Dream 0001–0003 already on disk; no 0004.

14011 leftover collect-only 2; `--tb=short` still None. 5203/14095 leftover collect-only 2 (miss is execute). 13976 leftover `--tb=short` still 9.1.0 duplicate. 14650 leftover `--tb=short` 8.4.1 2 pass / pytest 9 duplicate IDs. 14051 leftover `--setup-show` 1 pass. 14476 leftover `--collect-only -k foo` both tests.

7777 leftover nested file `a/b/c/d/test_d.py a/` 8.4.1 n=1 / pytest 9 n=5; keep-duplicates 6. Same vs cwd. 13704b leftover `a/a .` 1 vs 3 / keep 4. 14964 leftover `--setup-plan` CASE1 lists guard for later test through 9.0.3 only. 14964d leftover keep-duplicates gap still 9.1.0 later miss; collect-only n=3. 14737 leftover `--tb=short` still 1 fail. 3062 leftover escaped live-log prints literal `%(filename)s:3`.

14971/14640 leftover `--setup-plan` gap: 8.4.1–9.0.3 fixture for both; 9.1.0/9.1.1 later ERROR not found. No-gap plan OK all. 14964 leftover `--lf` after CASE1: 8.4.1 both errors; 9.1.0 only test_a (later miss not last-failed). 7777 leftover nested file vs sibling n=2 all. 3062 leftover fully escaped live-log ValueError `%W`.

13704b leftover sibling `a/a a/b` n=2 all (parent-drop is parent-only). Same-dir twice `a/ a/` n=3 unique / keep-duplicates 6. 13704 leftover `tests/ tests/` n=2 unique / keep-duplicates 4. 7777 leftover sibling `a/b a/b2` n=4 all; same-dir twice n=5 / keep-duplicates 10. 12083 leftover `tests tests` n=2 / keep-duplicates 4. 13925 leftover `--keep-duplicates '' .` still ZeroDivision all; `a/ a/` n=1 / keep-duplicates 2. 3062 leftover pytest.ini `%%` InterpolationSyntaxError; fully escaped ConfigParser succeeds, pytest getini keeps `%%`. 14807 leftover named pytest.toml `[pytest]`+native: 8.4.1 unread / pytest 9 `[pytest]` wins, no UsageError. 14737 leftover `--setup-plan` lists Function, no tests ran.

13704b leftover file-vs-parent `a/a/test_aa.py a/` 8.4.1 n=1 / pytest 9 n=3; keep-duplicates 4. File-vs-sibling-dir n=2 all. 7777 leftover nested ancestor `a/b/c a/` 8.4.1 n=2 / pytest 9 n=5; keep-duplicates 7. Mid-parent `a/b/c a/b` 2 vs 3. Nested sibling `a/b/c a/b2` n=3 all. 12083 leftover same-subdir twice n=1 / keep-duplicates 2. 13925 leftover `'' ''` ZeroDivision all. 14807 leftover pytest.ini both tables `[pytest]` wins; `-c` TOML `[pytest]`+native 8.4.1 unread / pytest 9 native wins, no UsageError. 3062 leftover tox.ini `[pytest]` raw getini; ConfigParser InterpolationMissingOptionError.

7777 leftover deepest `a/b/c/d a/` 8.4.1 n=1 / pytest 9 n=5; keep-duplicates 6. `a/b/c/d a/b` 1 vs 3; `a/b/c/d a/b/c` 1 vs 2; sibling `a/b/c/d a/b2` n=2 all. 13704b leftover file-in-parent `a/test_a.py a/` 8.4.1 n=1 / pytest 9 n=3; keep-duplicates 4. Two files n=2 all. 13925 leftover `. .` ZeroDivision all; keep-duplicates 2 errors. 14964 leftover keep-duplicates CASE1 still 9.1.0 later miss; collect-only n=3 all. 3062 leftover pyproject `%%` getini keeps literal `%%`.

14971/14640 leftover `--lf` after gap: 8.4.1–9.0.3 3 pass; 9.1.0/9.1.1 reruns **only later ERROR** (requested-fixture miss is last-failed). `--ff` still shows later miss (`E..`). `--lf --lfnf none` after all-pass: rc=5 deselected. 14964 leftover `--ff` still later PASS; `--maxfail=1` stops at first error (hides later miss). 14964d leftover `--lf` same as 14964. 7777 leftover file vs containing dir n=1 all / keep 2. Two files n=2 all. 13704b leftover file vs containing dir n=1 all / keep 2; parent-file vs child-dir n=2 all. 14807 leftover pytest.ini+pytest.toml: 8.4.1 `only_ini.py` / pytest 9 `only_pytest_toml.py`. tox.ini+pytest.toml: 8.4.1 `only_tox.py` / pytest 9 toml. Bare `--lfnf` without `--lf` UsageError rc=4.

14412 leftover isolated `alt_ini/`/`alt_iniopt/` `--collect-only`: 1 UnitTestCase all (times split is execute). 14696 leftover isolated `iso_miss/`: collect-only existing+missing both 9.1.0-only; `--setup-show` existing `idents.txt` unrecognized **all versions**; missing 9.1.0-only. Parent existing unrecognized all; parent missing hits leftover `alt_pp/` collisions. 14048 leftover `--setup-show --pyargs` without PYTHONPATH rc=4 even with `__init__.py`; `PYTHONPATH=.` 1 pass all. 13965 leftover `--setup-show test.py` 1 pass all; pytest 9 reports 1000 subtests. 14004b leftover `--collect-only` from `sdk/` 3 collected all (not 4). 13755b leftover collect-only 4. 9703b leftover collect-only 2 `::test_same`. 14800/14101/14775 leftover collect-only 3/2/2 (`_finalizers`/XPASS is execute). 13882/14683/14700/14635/14323 leftover collect-only 2/1/1/4/1.

14640/14971 leftover `--lf` later ERROR last-failed then **1 passed** (gap skipped; miss not reproduced). 14004b leftover `--setup-plan` from `sdk/` inner_fixture on outer tests through 9.0.3, gone 9.1.0. 9703 leftover `--setup-plan` autouse both through 9.0.3, file2 none from 9.1.0. 13755 leftover `--setup-plan` 10S/10T all. 14104 leftover `--setup-plan` session carry all. 7777b leftover file-vs-cwd 8.4.1 n=1 / pytest 9 n=3; keep-duplicates 4. 14694/14812/14973/14702/13246/14814 leftover collect-only (miss is execute). 13699 leftover `--tb=short` PYTHONPATH still AttributeError.

13976/14591 leftover `--setup-plan` same 9.1.0-only duplicate collect. 2043 leftover `--setup-plan test_ab.py` same 8.4.1 no-fixture / 9.1.0 duplicate / others 4. 14650 leftover `--setup-plan` 8.4.1 auto-suffix / pytest 9 duplicate IDs. 14148 leftover `--cache-show` prints nodeids; `-p no:cacheprovider --cache-show` unrecognized all. 14613 leftover `--cache-show -o cache_dir` empty. 14608c leftover `--override-ini addopts=tests` on `alt_inside/` rescues 9.1.0; `alt_lo_base/` `addopts=tests` rc=5; `addopts=test_it.py` unrecognized all. 14412 leftover `--durations=0` not per-subtest us. 13784 leftover `--tb=short -s` still doubling through 9.0.3. 14817 leftover `--setup-show` still bound-method. 14800 leftover `--lf` hides `_finalizers` (rerun 2 pass). 14775 leftover `--lf -Werror` still 2 errors.

12083/13704/7777 leftover `--setup-plan` overlap same drop as collect. 13925 leftover `--setup-plan '' a/` 8.4.1 n=1 (cwd dropped) / pytest 9 ZeroDivision. 14444 leftover `--setup-plan` hides capture. 14762 leftover `--setup-show` 1 pass. 13922 leftover `--setup-show -- extra` rc=4. 13885 leftover `--lf` 8.4.1–9.0.3 still ERROR / 9.1.0 skip no last-failed.

5203/14095 leftover `--setup-plan` `b` from first module `a` all. 14011 leftover `--setup-plan` class `fix` per subclass. 14691 leftover `--setup-plan` `sample` not found at plan. 14444 leftover `--collect-only` 2. 13479 leftover `--setup-plan` `ff` not found at plan.

12083 leftover reverse `--setup-plan` 1 vs 2 keep 3; `tests/subdirectory .` plan 1 vs 2. 13704 leftover reverse plan 1 vs 2 keep 3; same-file twice 2 vs 1. 13704b leftover plan `a/b a/` 1 vs 3 keep 4. 7777 leftover reverse 3 vs 5 keep 8; file-vs-cwd 1 vs 5. 7777b leftover plan overlap 1 vs 3. 14800 leftover `--ff` hides `_finalizers`. 14775 leftover `--ff -Werror` still 2 errors. 13885 leftover `--ff` still 8/9. 14101 leftover `--lf`/`--ff` XPASS not last-failed. 14613 leftover `--cache-show` after run has nodeids. 14148 leftover nocache `--cache-clear` unrecognized. 14650b leftover plan 2 all; 14650c leftover plan pytest 9 duplicate. 14608c leftover `--override-ini addopts=tests --db-url scheme://host/db` 1 pass including 9.1.0. 13925 leftover `. a/` plan 8.4.1 drop cwd / pytest 9 ZeroDivision. 13784 leftover `--assert=plain -s` still doubling. 14389 leftover `--tb=line` omits During handling on 8.4.1 and 9.1.0+. 13699 leftover `--assert=plain` still AttributeError. 14808 leftover `--tb=short` still list isinstance. 14448 leftover `--tb=native` no `where`. 14255 leftover int_native `--tb=short` TypeError on 9. 14694 leftover `--tb=short` NameError from 9.1.0. 14841 leftover `--setup-show` still resource_tracker. 13913 leftover `--tb=short tests/` 1 pass. 11502 leftover `--tb=short` 1 pass.

14807 leftover pytest.ini + pyproject native/ini_options: **only_ini.py** all versions (pytest.ini beats pyproject). pytest.ini + tox.ini / setup.cfg: only_ini.py all. setup.cfg + named pytest.toml: 8.4.1 only_cfg.py / pytest 9 only_pytest_toml.py. 14964 leftover `--nf` later miss still visible. 14971/14640 leftover `--maxfail=1` later miss still visible (`..E`). 14737 leftover `--lf` still 1 fail assert False.

14807 leftover pytest.ini + pyproject both tables: 8.4.1 only_ini.py; pytest 9 UsageError (ini does not suppress). pytest.toml + pyproject native: 8.4.1 test_default; pytest 9 toml. pytest.toml + ini_options: 8.4.1 ini_options / pytest 9 toml. setup.cfg + native: 8.4.1 cfg / pytest 9 native. setup.cfg + ini_options: ini_options all. 14964 leftover `--sw` stuck on first error. 14971/14640 leftover `--nf` later miss still visible.

14807 leftover tox.ini + pyproject native: 8.4.1 only_tox / pytest 9 native. tox.ini + ini_options: only_iniopt all. pytest.toml + tox.ini: 8.4.1 tox / pytest 9 toml. `-c custom.toml` `[pytest]` with cwd pytest.ini: test_default all (`-c` displaces ini). `-c` native: 8.4.1 default / pytest 9 native. 14971/14640 leftover `--sw` later miss visible then stuck on later ERROR.

13704b leftover `--setup-plan a/ a/` unique n=**3** all; keep n=6. 7777b leftover `--setup-plan a/b2 a/` 8.4.1 n=**1** / pytest 9 n=**3**; `--keep-duplicates` n=**4**. 13925 leftover `--setup-plan -- a/` n=**1** all. 13885 leftover `--sw` still 8/9 skip-vs-fire. 14101 leftover `--sw` XPASS is not stepwise-failed. 13913 leftover no-path `--setup-plan` 8.4.1 1 / pytest 9 unrecognized. 14808 leftover `pytest_ini/` `--tb=short` 1 pass all. 11502 leftover `--setup-plan` 1 collected all. 14650b leftover `--lf` 2 pass no last-failed.

12083 leftover three-way `--setup-plan tests/subdirectory tests/test_one.py .` n=**2** all (file hides 8/9). 13704 leftover `--setup-plan tests/test_it.py tests .` 8.4.1 n=**1** / pytest 9 n=**2**. 14964d leftover `--sw` stuck on first ERROR (hides later miss, same as #14964). 14737 leftover `--ff`/`--sw` still 1 fail. 14004b leftover `--lf` from `sdk/` 3 pass no last-failed. 13755b leftover `--lf` reruns errors then **2 passed** (hides session-teardown miss). 9703 leftover `--nf` 2 pass. 13784 leftover `--tb=line -s` still doubling through 9.0.3 / once from 9.1.0. 14650c leftover `--lf` collect-error is not last-failed. 13754 leftover `--setup-plan` 4. 13965 leftover `--setup-plan` 1. 14431 leftover `--setup-plan test.py` 1. 14514c leftover `--setup-plan foo.test.py` ImportError. 14812 leftover `--assert=plain` still INTERNALERROR StashKey. 14808 leftover `pytest_ini/` `--setup-plan` 1.

7777 leftover `--setup-plan --keep-duplicates a/b2 a/` n=**6** all. 12083 leftover keep three-way plan n=**4**. 13704 leftover keep three-way plan n=**5**. 13755b leftover `--ff` swaps miss onto `test_a`; `--sw` 2nd run 2 pass; `--nf` still 2 errors; `--maxfail=1` 2 pass 1 error. 5203/14095 leftover `--lf` **1 passed** (hides rebuild miss). 14011 leftover `--lf` still 2 fail. 14691 leftover `--lf` still sample not found. 14811 leftover `--lf` still getini fail. 14820/14445 leftover `--tb=line` still rewrite miss. 14255 leftover quoted plan 1; int_native plan TypeError on pytest 9. 3062 leftover `--setup-plan` 1. 14716 leftover missing toml FileNotFoundError. 14048 leftover `--pyargs --setup-plan` 1 collected with or without PYTHONPATH. 13913 leftover no-path `--lf` 8.4.1 1 pass / pytest 9 unrecognized.

5203/14095 leftover `--ff` swaps the rebuild miss onto the earlier test; `--sw` hides it (2nd run 1 pass); `--nf` still original fail; `--maxfail=1` miss still visible. 13246 leftover `--lf`/`--ff`/`--nf` still sibling shadow; `--sw` stuck on first fail. 14011 leftover `--sw`/`--maxfail=1` hides Test2. 13479 leftover `--ff`/`--sw` still `ff` missing. 14811 leftover `--nf`/`--sw` still getini fail. 14737 leftover `--nf` still 1 fail. 14104 leftover `--ff` 6 pass no last-failed. 14004 leftover `--lf` 4 pass no last-failed.

14807 leftover `-c custom.ini` `[pytest]`: **only_cini.py** all vs pyproject native / named pytest.toml / pytest.ini / setup.cfg (`-c` INI displaces them). Without `-c`, custom.ini is not a cwd config. Leftover `-c custom.toml` native vs named pytest.toml: 8.4.1 default (toml displaced, native unread); pytest 9 **only_native.py** (`-c` native displaces named toml).

14807 leftover `-c custom.toml` unread `[pytest]` vs pyproject native: with `-c`, **test_default.py** all including pytest 9 (displaces native). Same vs ini_options. `-c` native vs setup.cfg: 8.4.1 default / pytest 9 native. `-c custom.ini` vs tox.ini / ini_options: **only_cini.py** all.

14807 leftover `pytest.cfg` `[pytest]` is **not** a cwd config. vs native: 8.4.1 default / pytest 9 native. vs pytest.ini **only_ini.py** all. vs tox.ini **only_tox.py** all. vs setup.cfg **only_cfg.py** all. vs named pytest.toml: 8.4.1 default / pytest 9 toml. vs ini_options **only_iniopt.py** all. `-c custom.ini` vs pytest.cfg: without `-c` default / with `-c` **only_cini.py**. `-c` unread TOML vs pytest.cfg: default all. tox.ini vs setup.cfg: **only_tox.py** all.

14807 leftover `setup.cfg` `[pytest]` Failed: 8.4.1 suppressed by sibling pytest.ini/tox.ini (those win); pytest 9 Failed always. Native/toml do not suppress. pytest.ini `[tool:pytest]` ignored still displaces tox.ini (default files). `-c` TOML native vs pytest.cfg: 8.4.1 default / pytest 9 native. `-c` INI `[tool:pytest]` ignored.

14807 leftover `setup.cfg` `[pytest]` vs `pytest.cfg`: Failed all. `-c` INI/unread TOML/native suppress Failed. pytest.ini `[tool:pytest]` vs pyproject native/ini_options: **test_default** all (filename displaces pyproject). setup.cfg `[pytest]` vs ini_options: 8.4.1 only_iniopt / pytest 9 Failed. `--config-file=/dev/null` displaces cwd pytest.ini/native/setup.cfg. `-o python_files` replaces cwd python_files (rc=5 if that file is absent).

3062 leftover `--log-cli` unrecognized. pytest.ini/pyproject `log_cli=true` even with `-s -o log_cli=true --log-cli-level=WARNING` does not print live log. setup.cfg `[tool:pytest] log_cli=true` does. Fully escaped setup.cfg live-log still ValueError `%W`.

14807 leftover-0368/0374–0398: `PYTEST_ADDOPTS`/`--override-ini`/`-o python_files` replace cwd python_files (same as leftover-0365). CLI `-o` and `--override-ini` win over env. `python_files=test_*.py` restores **test_default**. Env still applies with `--config-file=/dev/null` and **beats** `-c custom.ini`. `-o addopts=-q` is additive quiet and does **not** replace python_files.

3062 leftover-0377–0398: `--log-cli-format` / `-o log_format` / `-o log_cli_format` override setup.cfg live-log. pytest.ini/pyproject `--log-file` empty and still no live-log **on assert-True-only tests**. Isolated `logging.warning` trees do print/write. asctime + `--log-cli-date-format` / `-o log_date_format` prints **HH:MM:SS**. Date-format without asctime does not add a timestamp.

3062 leftover-0626: `-c /dev/null --log-file-format=FILE:%(message)s` vs pytest.ini writes **FILE:hello-log** (cwd format displaced, no live-log). env/`--strict-config` `-c /dev/null --log-file` writes default **WARNING  hdd3062:test_log.py:3 hello-log**. setup.cfg `-c /dev/null --log-file` same default WARNING. Isolated setup.cfg `--log-cli-format` **CLI:test_log.py:3 hello-log**.

14807 leftover-0413–0560: `-o minversion=99` is **not enforced on 8.4.1**. setup.cfg `[pytest]` **Failed** is not suppressed by `-o`/`--override-ini`/`PYTEST_ADDOPTS python_files`/`--strict-config`/`--noconftest`. `-c` and `-c /dev/null` / `--config-file=/dev/null` **do** displace Failed and cwd python_files (dual cwd too: pytest.ini+native, setup.cfg+native, ini+tox, tox+native, ini+setup.cfg, tox+setup.cfg → **test_default**). `-c /dev/null -o python_files=only_*.py` collects that file. 14101 `--strict-config xfail_strict` same 8.4.1 xE / pytest 9 XPASS-as-fail.

14807 leftover-0563: `--strict-config -c /dev/null` vs more dual cwd (ini+toml / toml+native / toml+tox / scfg+native / ini+iniopt / scfg+iniopt) **test_default**. `-c /dev/null` **displaces pytest.ini+pyproject both-tables UsageError** on pytest 9. `-o python_files=only_native.py` after `/dev/null` vs pyboth **only_native**.

14807 leftover-0665: `-o addopts=--strict-config -c /dev/null -o verbosity=2` vs tox/named toml/Failed/native/ignored table is **8.4.1 rc=0 / 9.0.1–9.0.3 warning / 9.1.0+ rc=4**. Failed displaced. leftover-0476 weaker split survives `/dev/null`.

14807 leftover-0668/0671/0674: `--strict-config -c /dev/null -o minversion=99` vs pytest.ini/native/Failed/tox/named toml/ignored table/pytest.cfg/setup.cfg `[tool:pytest]` is **8.4.1 test_default** / pytest 9 **rc=4 citing `/dev/null:`**. `--strict-config -c /dev/null -o minversion=9.1` is **8.4.1 test_default** / **9.0.1–9.0.3 rc=4 citing `/dev/null:`** / **9.1.0+ test_default**. leftover-0422 split **survives `/dev/null`**. Failed displaced. env `PYTEST_ADDOPTS='-o minversion=99'` / `9.1`, `--override-ini minversion=99`, `--config-file=/dev/null` **same as CLI**.

14807 leftover-0677: `--strict-config -c /dev/null -o minversion=9.1.1` is **8.4.1 test_default** / **9.0.1–9.1.0 rc=4 citing `/dev/null:`** / **only 9.1.1 test_default**. `minversion=9.0.2` is **9.0.1-only rc=4 citing `/dev/null:`**. leftover-0473/0428 splits **survive `/dev/null`**. `-o addopts=--strict-config -c /dev/null -o minversion=9.1`/`99` is **same as CLI `--strict-config`** (leftover-0476 weaker split does **not** apply to known minversion). Failed displaced.

14807 leftover-0680/0683: leftover-0665 `-o addopts=--strict-config -c /dev/null -o verbosity=2` vs pytest.ini / pytest.cfg / setup.cfg `[tool:pytest]` / dual cwd (ini+native, ini+toml, ini+pyboth, scfg+native, toml+native, ini+scfg, tox+native, toml+tox, scfg+toml) is **leftover-0476 weaker split**. pyboth UsageError **displaced**. env vs named toml/ini/pytest.cfg/Failed same. `minversion=8.0`/`9.0`/`9.0.1` after `/dev/null` **all test_default including 8.4.1**. `minversion=9.1.0` leftover-0422 split. `minversion=9.0.3` is **9.0.1-only rc=4 citing `/dev/null:`**. Dual cwd `minversion=9.1`/`99` same. Failed displaced.

14807 leftover-0686: leftover-0665 addopts verbosity after `/dev/null` vs ini+iniopt / scfg+iniopt / toml+iniopt / tox+iniopt is **leftover-0476 weaker split**. `--config-file=/dev/null` **same as `-c`**. `--override-ini verbosity=2` same weaker split. leftover-14101 `--strict-config -c /dev/null -o xfail_strict=true` is **8.4.1 subtests missing** / pytest 9 **XPASS(strict)** (leftover-0470 survives `/dev/null`). leftover-3062 iso-log leftover-0476 weaker split.

14807 leftover-0689: leftover-14101 `-o addopts=--strict-config -c /dev/null -o xfail_strict=true` is **same as CLI `--strict-config`** (pytest 9 all XPASS(strict); leftover-0476 weaker split does **not** apply to known xfail_strict). leftover-0476 verbosity execute: 8.4.1 subtests missing; **9.0.x warning still runs**; **9.1.0+ rc=4 hides XPASS**. CLI `--strict-config -o verbosity=2` **pytest 9 all rc=4** hides XPASS.

14608c leftover-0692/0695/0698: leftover-0251 `--override-ini addopts=tests --db-url` **survives `/dev/null`** on `alt_inside/` (1 pass including 9.1.0). Later `-o addopts=--strict-config` **overwrites** that rescue (**9.1.0 unrecognized --db-url**). Later `--override-ini addopts=tests` or later `-o addopts=tests` **wins**. env `PYTEST_ADDOPTS='-o addopts=tests'` **survives `/dev/null`**. cwd pytest.ini `addopts=tests` is **displaced** (leftover-0566 split). leftover-0251 + `-o verbosity=2` without `--strict-config` **1 pass all** with pytest 9 warning.

13913 leftover-0701/0704/0707: `tests/` `--db --write-idents` **survives `/dev/null`**. Isolated no-path `-c /dev/null`: **8.4.1 1 pass** / pytest 9 **unrecognized** (leftover-0701 8.4.1 rc=2 was leftover-dir `--db` collisions). leftover-0251 `--override-ini addopts=tests` / env `addopts=tests` **1 pass all**. Later `-o addopts=--strict-config` loses rescue. leftover-0476 + `tests/` **9.1.0+ rc=4 hides rescue**. `tests/` + `-o verbosity=2` without `--strict-config` **1 pass all** with pytest 9 warning.

14048 leftover-0710/0713: `PYTHONPATH=. --pyargs amodule.tests` **survives `/dev/null`**. leftover-0476 **hides that rescue on 9.1.0+**. `-o`/`--override-ini pythonpath=.` **does not rescue --pyargs**. leftover-0476 verbosity without `--strict-config` **1 pass all**. leftover-14084 leftover-0713/0716: `PYTHONPATH=.` and subdir `PYTHONPATH=..` **survive `/dev/null`**; leftover-0476 **hides them on 9.1.0+**.

11502 leftover-0719/0722: leftover-0719 `--cache-show leftover-0719 -c /dev/null` after a normal run is **cache empty** at `/dev/.pytest_cache`. leftover-0476 / leftover-0470 `--strict-config verbosity` **do not apply** to leftover-0719 `--cache-show` (rc=0 all including 9.1.0+). leftover-0719 `--cache-show` without `/dev/null` lists `tests/test_a.py::test_a`. leftover-14148 leftover-0725: leftover-14148 leftover-14148 `-p no:cacheprovider leftover-0719 -c /dev/null` **AttributeError all**; leftover-0476 **hides it on 9.1.0+**. leftover-11502 leftover-14148 no:cacheprovider leftover-0719 `--cache-show` **unrecognized `--cache-show`**. leftover-0728 not started: 保全 08:00.

14807 leftover-0533: `PYTEST_ADDOPTS=-c custom.ini` vs Failed with `only_cini.py` present is **only_cini all**. `--strict-config -c custom.ini -o verbosity=2` suppresses Failed then pytest 9 unknown verbosity. `-c` + `--override-ini python_files=test_*.py` restores **test_default**. `-c` unread TOML vs Failed **test_default**; native TOML 8.4.1 default / pytest 9 **only_native**.

14807 leftover-0488: `--strict-config -o verbosity=2` vs named `pytest.toml` / ignored pytest.ini / `-c custom.ini` is 8.4.1 collect / pytest 9 rc=4 unknown verbosity. setup.cfg `[pytest]` **Failed first**. `--override-ini verbosity=2` same as CLI. Env `--strict-config` vs named toml pytest 9 rc=4. `--strict-config -o minversion=99` vs named toml 8.4.1 test_default / pytest 9 citing `pytest.toml`. `--strict-config -o python_files` **only_pytest_toml all including 8.4.1**.

14807 leftover-0473: named `pytest.toml` `-o minversion` cites **`pytest.toml`**. `9.0.1` 8.4.1 test_default / pytest 9 only_pytest_toml; `9.1.1` only 9.1.1 pass; `99` pytest 9 rc=4. setup.cfg `[pytest]` **Failed first** vs `-o minversion` (does **not** suppress Failed). tox.ini `9.0.1` only_tox all; `9.0.3` 9.0.1 rc=4 citing tox.ini. pytest.ini `[tool:pytest]` `minversion=99` still cites **`pytest.ini`**. Env vs named toml same as CLI.

14807 leftover-0347: pytest.cfg does **not** suppress setup.cfg `[pytest]` Failed. `-c` INI/TOML **does** suppress Failed on 8.4.1–9.1.1 (`-c` INI only_cini; unread TOML default; native TOML 8.4.1 default / pytest 9 native). ini_options suppresses Failed on 8.4.1 only. pytest.ini `[tool:pytest]` displaces pyproject native/ini_options (default files). tox.ini `[tool:pytest]` loses to pytest.ini `[pytest]`.

14807 leftover-0371: `PYTEST_ADDOPTS='-o python_files=only_native.py'` replaces tox/ini/cfg/native/toml python_files (only_native even when native/toml unread on 8.4.1). Env does **not** suppress setup.cfg `[pytest]` Failed (unlike `-c`).

14253/14092 leftover parent `--lf`: 8.4.1 leftover dummy-name collision; pytest 9 configure TypeError (not last-failed). Isolated `ini_options/` `--lf`/`--ff`/`--nf`/`--sw` **1 pass** all. TypeError is native `[tool.pytest]`, not ini_options.

14808 leftover `ini_options/` `--lf`/`--ff`/`--nf`/`--sw`: still 1 failed `isinstance(['not','a','string'], str)`; `--sw` stuck on it. Leftover `tool_pytest/` `--nf`: 8.4.1 1 pass (unread); pytest 9 TypeError still last-failed.

14560 leftover `--nf`/`--maxfail=1`: still collect-error `KeyError: '__name__'` (not last-failed). 14148 leftover `--nf`: 1 pass all. 13985 leftover list/ini_options `--ff`/`--nf`/`--sw`: 1 pass; string `--nf` TypeError on pytest 9 is not last-failed. 14705 leftover `--lf`/`--ff`/`--nf`/`--sw` `benchmarks/test_normal.py`: 1 pass all. 14255 leftover quoted `--ff`/`--nf`: 1 pass. 14048 leftover PYTHONPATH `--sw`/`--nf --pyargs`: 1 pass all.

14412 leftover isolated `alt_ini/`/`alt_iniopt/` `--lf`/`--ff`: 1 pass all (pytest 9 3 subtests). 14004b leftover `--ff`/`--nf`/`--sw` from `sdk/`: 3 pass (leak is not last-failed). 14808 leftover `pytest_ini/` `--nf`: 1 pass. 14650c leftover `--maxfail=1`: 8.4.1 2 pass; pytest 9 collect-error not last-failed. 13985/14255 leftover `--maxfail=1`: pytest 9 configure TypeError not last-failed. 11502 leftover `--cache-show` after `/dev/null` run lists `::test_a`. 14608c leftover `alt_inside/` `--lf`/`--ff`/`--sw` with `--override-ini addopts=tests --db-url scheme://host/db`: 1 pass including 9.1.0.

14608c leftover `alt_lo_base/` `--lf`/`--ff`/`--nf`/`--sw --db-url`: 9.1.0 unrecognized both runs (not last-failed); other versions 1 pass. 13913 leftover `tests/` `--ff`/`--sw`: 1 pass including 9.1.0. 14514c leftover importlib `--lf`/`--ff`/`--sw`: 1 pass. 13922 leftover `--lf`/`--ff`/`--sw`: 1 pass. 14431 leftover `alt_pyfiles/` `--lf`/`--ff`/`--sw`: 1 pass. 14084 leftover PYTHONPATH `--lf`/`--ff --pyargs`: 1 pass.
Leftover-0692 14608c: leftover-0251 `--override-ini addopts=tests --db-url` on `alt_inside/` **survives** `-c /dev/null` / `--config-file=/dev/null` (**1 pass including 9.1.0**). leftover-0566 `alt_lo_base/` `-c /dev/null --db-url` still **9.1.0 unrecognized**. `alt_lo_base/` `addopts=tests` + `/dev/null` is **rc=5** (option recognized, no tests).
Leftover-0701 13913: explicit `tests/` `--db --write-idents` **survives** `-c /dev/null` / `--config-file=/dev/null` (**1 pass including 9.1.0**). No-path after `/dev/null` is pytest 9 unrecognized; 8.4.1 hits parent leftover dummy `--db` collisions because `testpaths` is displaced.
Leftover-0710 14048: `PYTHONPATH=. --pyargs amodule.tests` **survives** `-c /dev/null` / `--config-file=/dev/null` (**1 pass all**). Without PYTHONPATH still rc=4 missing `__init__.py`.
Leftover-0719 11502: `--cache-show -c /dev/null` after a normal run is **empty** (`cachedir: /dev/.pytest_cache`). leftover-0251 `--cache-show` after a `/dev/null` run listed collapsed `::test_a`.

