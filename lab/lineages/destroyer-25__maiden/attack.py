#!/usr/bin/env python3
"""Adversarial battery against maiden (never-red). Do not rewrite maiden."""
from __future__ import annotations

import json
import os
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

M = Path(
    os.environ.get(
        "MAIDEN",
        "/Users/annenpolka/.grok/worktrees/annenpolka-brrr/subagent-01a01bd4-9291-7c63-9bf2-7e115d7932c1/maiden",
    )
)
ROOT = Path("/tmp/destroy-maiden")
FIX = ROOT / "fixtures"
LOG = ROOT / "logs"
LED = ROOT / "ledger"
OUT = ROOT / "transcript.txt"

FIX.mkdir(parents=True, exist_ok=True)
LOG.mkdir(parents=True, exist_ok=True)
LED.mkdir(parents=True, exist_ok=True)

records: list[str] = []


def note(title: str) -> None:
    bar = "=" * 72
    records.append(f"\n{bar}\n# {title}\n{bar}")
    print(f"\n### {title}", flush=True)


def run(args: list[str], stdin: str | None = None, cwd: Path | None = None, env: dict | None = None) -> subprocess.CompletedProcess:
    e = os.environ.copy()
    if env:
        e.update(env)
    p = subprocess.run(
        args,
        input=stdin,
        text=True,
        capture_output=True,
        cwd=str(cwd) if cwd else None,
        env=e,
    )
    cmd = " ".join(args)
    rec = (
        f"$ {cmd}\n"
        f"# rc={p.returncode}\n"
        f"{p.stdout}"
    )
    if p.stderr.strip():
        rec += f"--- stderr ---\n{p.stderr}"
    records.append(rec)
    print(rec, end="" if rec.endswith("\n") else "\n", flush=True)
    return p


def maiden(*args: str, stdin: str | None = None, cwd: Path | None = None) -> subprocess.CompletedProcess:
    return run([str(M), "--no-ledger", *args], stdin=stdin, cwd=cwd)


def write(rel: str, text: str) -> Path:
    p = FIX / rel
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(text, encoding="utf-8")
    return p


# ---------------------------------------------------------------------------
# fixtures
# ---------------------------------------------------------------------------

GOLD_2019 = write(
    "junit/run-2019-fail.xml",
    Path(
        "/Users/annenpolka/.grok/worktrees/annenpolka-brrr/subagent-01a01bd4-9291-7c63-9bf2-7e115d7932c1/fixtures/junit/run-2019-fail.xml"
    ).read_text(),
)
GOLD_2024 = write(
    "junit/run-2024-green.xml",
    Path(
        "/Users/annenpolka/.grok/worktrees/annenpolka-brrr/subagent-01a01bd4-9291-7c63-9bf2-7e115d7932c1/fixtures/junit/run-2024-green.xml"
    ).read_text(),
)

write(
    "junit/status-attr-failed.xml",
    """<?xml version="1.0"?>
<testsuite name="pkg" tests="2" failures="1" timestamp="2019-06-01T12:00:00">
  <testcase classname="pkg.T" name="alpha" status="failed"/>
  <testcase classname="pkg.T" name="beta" status="passed"/>
</testsuite>
""",
)

write(
    "junit/status-attr-then-green.xml",
    """<?xml version="1.0"?>
<testsuite name="pkg" tests="2" failures="0" timestamp="2024-08-01T12:00:00">
  <testcase classname="pkg.T" name="alpha" status="passed"/>
  <testcase classname="pkg.T" name="beta" status="passed"/>
</testsuite>
""",
)

write(
    "junit/flaky-then-green.xml",
    """<?xml version="1.0"?>
<testsuite name="pkg" tests="2" failures="0" timestamp="2024-08-01T12:00:00">
  <testcase classname="pkg.T" name="alpha">
    <flakyFailure message="boom">java.lang.AssertionError: boom</flakyFailure>
  </testcase>
  <testcase classname="pkg.T" name="beta"/>
</testsuite>
""",
)

write(
    "junit/rerun-failure.xml",
    """<?xml version="1.0"?>
<testsuite name="pkg" tests="1" failures="0" timestamp="2024-08-01T12:00:00">
  <testcase classname="pkg.T" name="alpha">
    <rerunFailure message="boom">first try failed</rerunFailure>
  </testcase>
</testsuite>
""",
)

write(
    "junit/same-name-fail-then-pass.xml",
    """<?xml version="1.0"?>
<testsuite name="pkg" tests="2" timestamp="2024-08-01T12:00:00">
  <testcase classname="pkg.T" name="alpha"><failure message="boom">boom</failure></testcase>
  <testcase classname="pkg.T" name="alpha"/>
</testsuite>
""",
)

write(
    "junit/no-timestamp-fail.xml",
    """<?xml version="1.0"?>
<testsuite name="pkg" tests="1" failures="1">
  <testcase classname="pkg.T" name="alpha"><failure message="boom">boom</failure></testcase>
</testsuite>
""",
)

write(
    "junit/no-timestamp-green.xml",
    """<?xml version="1.0"?>
<testsuite name="pkg" tests="1" failures="0">
  <testcase classname="pkg.T" name="alpha"/>
</testsuite>
""",
)

write(
    "junit/classname-changed-fail.xml",
    """<?xml version="1.0"?>
<testsuite name="pkg" timestamp="2019-06-01T12:00:00">
  <testcase classname="pkg.Old" name="alpha"><failure>boom</failure></testcase>
</testsuite>
""",
)

write(
    "junit/classname-changed-pass.xml",
    """<?xml version="1.0"?>
<testsuite name="pkg" timestamp="2024-08-01T12:00:00">
  <testcase classname="pkg.New" name="alpha"/>
</testsuite>
""",
)

write(
    "junit/rename-fail.xml",
    """<?xml version="1.0"?>
<testsuite name="pkg" timestamp="2019-06-01T12:00:00">
  <testcase classname="pkg.T" name="compute_diff"><failure>boom</failure></testcase>
</testsuite>
""",
)

write(
    "junit/rename-pass.xml",
    """<?xml version="1.0"?>
<testsuite name="pkg" timestamp="2024-08-01T12:00:00">
  <testcase classname="pkg.T" name="compute_operation_diff"/>
</testsuite>
""",
)

write(
    "junit/skip-only.xml",
    """<?xml version="1.0"?>
<testsuite name="pkg" timestamp="2020-01-01T00:00:00">
  <testcase classname="pkg.T" name="never"><skipped/></testcase>
</testsuite>
""",
)

write(
    "junit/skip-then-pass.xml",
    """<?xml version="1.0"?>
<testsuite name="pkg" timestamp="2024-08-01T12:00:00">
  <testcase classname="pkg.T" name="never"/>
</testsuite>
""",
)

write(
    "junit/xunit-error.xml",
    """<?xml version="1.0"?>
<testsuite name="pkg" timestamp="2019-06-01T12:00:00">
  <testcase classname="pkg.T" name="alpha"><error message="boom">NPE</error></testcase>
</testsuite>
""",
)

write(
    "ledger/honest.jsonl",
    '{"id":"pkg.T::alpha","status":"fail","t":"2019-06-01T12:00:00Z","src":"ci.xml","run":"2019"}\n'
    '{"id":"pkg.T::alpha","status":"pass","t":"2024-08-01T12:00:00Z","src":"ci.xml","run":"2024"}\n'
    '{"id":"pkg.T::beta","status":"pass","t":"2024-08-01T12:00:00Z","src":"ci.xml","run":"2024"}\n',
)

write(
    "ledger/status-red.jsonl",
    '{"id":"pkg.T::alpha","status":"red","t":"2019-06-01T12:00:00Z","src":"ci.xml","run":"2019"}\n'
    '{"id":"pkg.T::alpha","status":"pass","t":"2024-08-01T12:00:00Z","src":"ci.xml","run":"2024"}\n',
)

write(
    "ledger/status-failure-word.jsonl",
    '{"id":"pkg.T::alpha","status":"failure","t":"2019-06-01T12:00:00Z","src":"ci.xml","run":"2019"}\n'
    '{"id":"pkg.T::alpha","status":"pass","t":"2024-08-01T12:00:00Z","src":"ci.xml","run":"2024"}\n',
)

write(
    "ledger/corrupt-mixed.jsonl",
    '{"id":"pkg.T::alpha","status":"fail","t":"2019-06-01T12:00:00Z","src":"ci.xml","run":"2019"}\n'
    'NOT JSON this line is a fail that should scar beta: test beta ... FAILED\n'
    '{"id":"pkg.T::beta","status":"pass","t":"2024-08-01T12:00:00Z"}\n'
    '{"kind":"source","src":"x","sha256":"abc"}\n'
    '{"id":"pkg.T::gamma"}\n'
    '{"status":"fail","t":"2019-01-01T00:00:00Z"}\n',
)

write(
    "ledger/looks-like-ledger-but-swallows-cargo.jsonl",
    '{"id":"note","status":"seen","t":null,"src":"header"}\n'
    "test kizu::scar::undo ... FAILED\n"
    "test kizu::hook::parse ... ok\n",
)

write(
    "ci/go-fail.txt",
    """=== RUN   TestAlpha
    alpha_test.go:10: boom
--- FAIL: TestAlpha (0.00s)
=== RUN   TestBeta
--- PASS: TestBeta (0.00s)
FAIL
""",
)

write(
    "ci/bun-fail.txt",
    """bun test v1.2.0
tests/e2e/smoke.test.ts:
✓ launches against a clean repo [12.00ms]
✗ shows a modified file in the scroll view [20.00ms]
  ^ error: expect(view).toContain("auth.rs")
1 pass
1 fail
 10 expect() calls
Ran 2 tests across 1 file. [40.00ms]
""",
)

write(
    "ci/nextest-fail.txt",
    """    Starting 2 tests across 1 binary
        FAIL [   0.010s] kizu app::tests::alpha
        PASS [   0.001s] kizu app::tests::beta
────────────
     Summary [   0.012s] 2 tests run: 1 passed, 1 failed
""",
)

write(
    "ci/cargo-failures-section.txt",
    """running 2 tests
test app::tests::alpha ... FAILED
test app::tests::beta ... ok

failures:

---- app::tests::alpha stdout ----
assertion failed

failures:
    app::tests::alpha

test result: FAILED. 1 passed; 1 failed; 0 ignored
""",
)

write(
    "ci/wrong-suite-gha.txt",
    """ubuntu-latest / e2e\tbun test\t2026-04-16T06:40:47.000Z  bun test v1.2.0
ubuntu-latest / e2e\tbun test\t2026-04-16T06:40:47.010Z  ✗ shows a modified file [20ms]
ubuntu-latest / unit\tcargo test\t2026-04-16T06:41:12.000Z  test kizu::hook::parse ... ok
ubuntu-latest / unit\tcargo test\t2026-04-16T06:41:12.100Z  test kizu::scar::undo ... ok
# later the e2e job also printed a cargo-looking line in a captured fixture:
ubuntu-latest / e2e\tbun test\t2026-04-16T06:41:20.000Z  captured: test kizu::scar::undo ... FAILED
""",
)

write(
    "ci/pytest-captured-cargo.txt",
    """tests/test_parse.py::test_reads_cargo_log PASSED
tests/test_parse.py::test_mentions_failure PASSED
""",
)

write(
    "ci/pytest-xfail.txt",
    """tests/test_old.py::test_known_bug XFAIL
tests/test_old.py::test_flaky XPASS
tests/test_old.py::test_ok PASSED
""",
)

write(
    "ci/swift-unrecognized.txt",
    """Test Suite 'SitbonePackageTests.xctest' started at 2026-04-10 02:53:56.000
Test Suite 'SitboneCoreTests' started at 2026-04-10 02:53:56.001
Test Case '-[SitboneCoreTests.FocusStateMachineTests testFlowStaysWhenIdleBelowT1]' failed (0.010 seconds).
Executed 1 test, with 1 failure (0 unexpected) in 0.010 (0.011) seconds
""",
)

write(
    "ci/rg-pass-junit.xml",
    """<?xml version="1.0"?>
<testsuite name="pkg" timestamp="2024-08-01T12:00:00">
  <testcase classname="pkg.T" name="alpha"/>
  <testcase classname="pkg.T" name="beta"/>
  <testcase classname="pkg.T" name="gamma"><skipped/></testcase>
  <testcase classname="pkg.T" name="delta"/>
</testsuite>
""",
)

write(
    "roster/cargo-list.txt",
    "app::tests::alpha: test\n"
    "app::tests::beta: test\n"
    "app::tests::newborn: test\n",
)

write(
    "roster/swift-list.txt",
    Path(
        "/Users/annenpolka/.grok/worktrees/annenpolka-brrr/subagent-01a01bd4-9291-7c63-9bf2-7e115d7932c1/fixtures/swift/list.txt"
    ).read_text(),
)

write(
    "swift/ambiguous/Tests/ModA/A.swift",
    'import Testing\nstruct A {\n    @Test("same")\n    func foo() {}\n}\n',
)
write(
    "swift/ambiguous/Tests/ModB/B.swift",
    'import Testing\nstruct B {\n    @Test("same")\n    func bar() {}\n}\n',
)

write(
    "swift/ambiguous/log.txt",
    '✔ Test "same" passed after 0.001 seconds.\n',
)

write(
    "swift/rename/Tests/Mod/Old.swift",
    'import Testing\nstruct Old {\n    @Test("display")\n    func oldName() {}\n}\n',
)

# cargo parametrized identity
write(
    "cargo/param-fail.txt",
    "test app::tests::cases::add::case_1 ... FAILED\n"
    "test app::tests::cases::add::case_2 ... ok\n",
)
write(
    "cargo/param-list.txt",
    "app::tests::cases::add: test\n"
    "app::tests::cases::add::case_1: test\n"
    "app::tests::cases::add::case_2: test\n",
)

# xcresult-shaped dir
xc = FIX / "xcresult" / "Missing.xcresult"
xc.mkdir(parents=True, exist_ok=True)
(xc / "Info.plist").write_text(
    '<?xml version="1.0"?><plist><dict><key>rootId</key><string>0</string></dict></plist>\n'
)

# app bundle with Info.plist (sitbone-shaped)
app = FIX / "app" / "Sitbone.app" / "Contents"
app.mkdir(parents=True, exist_ok=True)
(app / "Info.plist").write_text(
    '<?xml version="1.0"?><plist><dict><key>CFBundleName</key><string>Sitbone</string></dict></plist>\n'
)

# libtest json
write(
    "cargo/libtest.jsonl",
    '{"type":"suite","event":"started","test_count":2}\n'
    '{"type":"test","event":"started","name":"app::tests::alpha"}\n'
    '{"type":"test","name":"app::tests::alpha","event":"failed"}\n'
    '{"type":"test","name":"app::tests::beta","event":"ok"}\n'
    '{"type":"suite","event":"failed","passed":1,"failed":1}\n',
)

write(
    "cargo/libtest-ok-field.jsonl",
    '{"type":"test","name":"app::tests::alpha","ok":false}\n'
    '{"type":"test","name":"app::tests::beta","ok":true}\n',
)

# empty / garbage
write("empty/empty.txt", "")
write("empty/whitespace.txt", "\n\n   \n")
write("empty/garbage.txt", "hello world this is not a test log\njust prose\n")
write("empty/markdown.md", "# Tests\n\nAll tests PASS.\n\n`test foo ... FAILED` is an example.\n")

# ---------------------------------------------------------------------------
# attacks
# ---------------------------------------------------------------------------

note("0. gold path — never-red is not rg PASS")
maiden("--header", str(GOLD_2019), str(GOLD_2024))
maiden("--latest", "--counts", str(GOLD_2019), str(GOLD_2024))
maiden("--skeptic", "--header", str(GOLD_2019), str(GOLD_2024))
maiden("--counts", str(GOLD_2019))
maiden("--only", "SKIPPED", str(GOLD_2019))

note("1. no-records UNKNOWN vs never-red")
maiden("--counts")
maiden("--roster", "--counts", str(FIX / "roster/cargo-list.txt"))
maiden("--roster", "--counts", str(FIX / "roster/swift-list.txt"))
maiden("--counts", str(FIX / "empty/empty.txt"))
maiden("--counts", str(FIX / "empty/garbage.txt"))
maiden("--counts", str(FIX / "empty/markdown.md"))
p = maiden("--header", str(FIX / "ci/go-fail.txt"))
p = maiden("--header", str(FIX / "ci/bun-fail.txt"))
p = maiden("--header", str(FIX / "ci/nextest-fail.txt"))

note("2. SKIP-only claimed maiden")
maiden("--header", str(FIX / "junit/skip-only.xml"))
maiden("--header", str(FIX / "junit/skip-only.xml"), str(FIX / "junit/skip-then-pass.xml"))
maiden("--header", str(FIX / "ci/pytest-xfail.txt"))

note("3. latest-green ∩ historical-fail (--skeptic)")
maiden("--skeptic", "--header", str(GOLD_2019), str(GOLD_2024))
maiden("--latest", "--skeptic", "--header", str(GOLD_2019), str(GOLD_2024))
maiden("--skeptic", "--check", "SKEPTIC", str(GOLD_2019), str(GOLD_2024))
print(f"# --skeptic --check rc printed above (expect 1)")
maiden("--skeptic", "--header", str(FIX / "junit/same-name-fail-then-pass.xml"))
maiden("--header", str(FIX / "junit/same-name-fail-then-pass.xml"))
maiden("--latest", "--header", str(FIX / "junit/same-name-fail-then-pass.xml"))

note("3b. timestamp-less junit: mtime is the clock")
# invert mtimes: fail file newer than green
fail_nt = FIX / "junit/no-timestamp-fail.xml"
green_nt = FIX / "junit/no-timestamp-green.xml"
os.utime(green_nt, (1_000_000_000, 1_000_000_000))  # 2001
os.utime(fail_nt, (1_800_000_000, 1_800_000_000))  # 2027 — fail looks latest
maiden("--header", str(fail_nt), str(green_nt))
maiden("--latest", "--header", str(fail_nt), str(green_nt))
maiden("--skeptic", "--header", str(fail_nt), str(green_nt))
# opposite: green newer
os.utime(fail_nt, (1_000_000_000, 1_000_000_000))
os.utime(green_nt, (1_800_000_000, 1_800_000_000))
maiden("--header", str(fail_nt), str(green_nt))
maiden("--latest", "--header", str(fail_nt), str(green_nt))
maiden("--skeptic", "--header", str(fail_nt), str(green_nt))

note("4. renamed tests launder a scar")
maiden("--header", str(FIX / "junit/rename-fail.xml"), str(FIX / "junit/rename-pass.xml"))
maiden("--skeptic", "--header", str(FIX / "junit/rename-fail.xml"), str(FIX / "junit/rename-pass.xml"))
maiden("--header", str(FIX / "junit/classname-changed-fail.xml"), str(FIX / "junit/classname-changed-pass.xml"))
maiden("--skeptic", str(FIX / "junit/classname-changed-fail.xml"), str(FIX / "junit/classname-changed-pass.xml"))

note("5. ledger format lies")
maiden("--header", str(FIX / "ledger/honest.jsonl"))
maiden("--skeptic", "--header", str(FIX / "ledger/honest.jsonl"))
maiden("--header", str(FIX / "ledger/status-red.jsonl"))
maiden("--header", str(FIX / "ledger/status-failure-word.jsonl"))
maiden("--header", str(FIX / "ledger/corrupt-mixed.jsonl"))
maiden("--header", str(FIX / "ledger/looks-like-ledger-but-swallows-cargo.jsonl"))

# ingest sha skip + --run
led = LED / "dup.jsonl"
if led.exists():
    led.unlink()
run([str(M), "--ledger", str(led), "ingest", "--run", "r1", str(GOLD_2019)])
run([str(M), "--ledger", str(led), "ingest", "--run", "r2", str(GOLD_2019)])  # same bytes, sha skip
run([str(M), "--ledger", str(led), "ingest", "--run", "r3", str(GOLD_2024)])
run([str(M), "--ledger", str(led), "--header"])

note("6. junit flaky then green")
maiden("--header", str(FIX / "junit/flaky-then-green.xml"))
maiden("--header", str(FIX / "junit/rerun-failure.xml"))
maiden("--header", str(FIX / "junit/status-attr-failed.xml"))
maiden(
    "--header",
    str(FIX / "junit/status-attr-failed.xml"),
    str(FIX / "junit/status-attr-then-green.xml"),
)
maiden(
    "--skeptic",
    "--header",
    str(FIX / "junit/status-attr-failed.xml"),
    str(FIX / "junit/status-attr-then-green.xml"),
)
maiden("--header", str(FIX / "junit/xunit-error.xml"), str(GOLD_2024))

note("7. xcresult missing / Info.plist trap")
maiden("--header", str(FIX / "xcresult/Missing.xcresult"))
maiden("--counts", str(FIX / "app/Sitbone.app"))
# sitbone real app bundle
sit_app = Path("/Users/annenpolka/ghq/github.com/annenpolka/sitbone/.build/Sitbone.app")
if sit_app.exists():
    maiden("--counts", str(sit_app))
    maiden("--header", str(sit_app / "Contents"))

note("8. CI log parse of the wrong suite")
maiden("--header", str(FIX / "ci/wrong-suite-gha.txt"))
maiden("--skeptic", "--header", str(FIX / "ci/wrong-suite-gha.txt"))
maiden("--header", str(FIX / "ci/cargo-failures-section.txt"))
maiden("--header", str(FIX / "ci/pytest-captured-cargo.txt"))
maiden("--header", str(FIX / "ci/swift-unrecognized.txt"))
maiden("--header", str(FIX / "cargo/libtest.jsonl"))
maiden("--header", str(FIX / "cargo/libtest-ok-field.jsonl"))

note("9. rg PASS skeptic pipeline")
# naive rg PASS on latest junit
p = run(["grep", "-c", "testcase ", str(GOLD_2024)])
maiden("--latest", "--only", "MAIDEN", "--header", str(GOLD_2019), str(GOLD_2024))
maiden("--only", "MAIDEN", "--header", str(GOLD_2019), str(GOLD_2024))
# pipe a grepped PASS-looking cargo log
rg_like = "test app::tests::alpha ... ok\ntest app::tests::beta ... ok\n"
maiden("--header", stdin=rg_like)
# --check MAIDEN on latest-only (the TDD gate on a lie)
maiden("--latest", "--check", "MAIDEN", str(GOLD_2019), str(GOLD_2024))
maiden("--check", "MAIDEN", str(GOLD_2019), str(GOLD_2024))

note("10. census vs specifier; ambiguous @Test; param cargo")
tree = Path(
    "/Users/annenpolka/.grok/worktrees/annenpolka-brrr/subagent-01a01bd4-9291-7c63-9bf2-7e115d7932c1/fixtures/tree"
)
swift_log = Path(
    "/Users/annenpolka/.grok/worktrees/annenpolka-brrr/subagent-01a01bd4-9291-7c63-9bf2-7e115d7932c1/fixtures/swift/testing.txt"
)
swift_list = Path(
    "/Users/annenpolka/.grok/worktrees/annenpolka-brrr/subagent-01a01bd4-9291-7c63-9bf2-7e115d7932c1/fixtures/swift/list.txt"
)
maiden("-C", str(tree), "--census", "--counts", str(swift_log))
maiden("-C", str(tree), "--census", "--header", str(swift_log))
maiden("-C", str(tree), "--roster", "--header", str(swift_list), str(swift_log))
maiden(
    "-C",
    str(FIX / "swift/ambiguous"),
    "--header",
    str(FIX / "swift/ambiguous/log.txt"),
)
maiden("--roster", "--header", str(FIX / "cargo/param-list.txt"), str(FIX / "cargo/param-fail.txt"))

note("11. xfail/xpass mapping")
maiden("--header", str(FIX / "ci/pytest-xfail.txt"))

note("12. why on missing / scarred")
maiden("why", "pkg.T::alpha")  # no ledger, no files
# classify why via --why
maiden("--why", "pkg.T::alpha", str(GOLD_2019), str(GOLD_2024))

# persist
OUT.write_text("\n".join(records) + "\n", encoding="utf-8")
print(f"\n# wrote {OUT}  lines={len(OUT.read_text().splitlines())}", flush=True)
