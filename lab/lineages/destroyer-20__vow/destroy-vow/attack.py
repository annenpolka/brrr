#!/usr/bin/env python3
"""Adversarial battery against vow's two-oath object. Does not rewrite vow."""
from __future__ import annotations

import json
import os
import platform
import shutil
import subprocess
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
OUT = Path(os.environ.get("DESTROY_VOW_OUT", "/tmp/destroy-vow"))
FIX = OUT / "fixtures"
VOW_ROOT = Path(
    os.environ.get(
        "VOW_ROOT",
        "/Users/annenpolka/.grok/worktrees/annenpolka-brrr/subagent-01a01b85-3a6f-77f2-a6bf-cb888759e773",
    )
)
TROTH_ROOT = Path(
    "/Users/annenpolka/.grok/worktrees/annenpolka-brrr/subagent-01a01bad-eb91-7d80-9aa0-10c17b74e5bd"
)
ONSET_ROOT = Path(
    "/Users/annenpolka/.grok/worktrees/annenpolka-brrr/subagent-01a01bd4-9291-7c63-9bf2-7de3116f0063"
)
WRIT_ROOT = Path(
    "/Users/annenpolka/.grok/worktrees/annenpolka-brrr/subagent-01a01bd4-9291-7c63-9bf2-7df33e3684b1"
)
SITBONE = Path("/Users/annenpolka/ghq/github.com/annenpolka/sitbone")
KIZU = Path("/Users/annenpolka/ghq/github.com/annenpolka/kizu")
PY = sys.executable
VOW = [PY, str(VOW_ROOT / "vow.py")]
TROTH = [PY, str(TROTH_ROOT / "troth.py")]
ONSET = [PY, str(ONSET_ROOT / "onset.py")]
WRIT = [PY, str(WRIT_ROOT / "writ.py")]

sys.path.insert(0, str(VOW_ROOT))
import vow as V  # noqa: E402

HOME = str(Path.home()).rstrip("/")
USER = os.environ.get("USER") or os.environ.get("LOGNAME") or ""
HOST = platform.node().split(".")[0]
PLAT = platform.system()

RESULTS: list[dict] = []


def write(name: str, body: str) -> Path:
    p = FIX / name
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(body, encoding="utf-8")
    return p


def sh(args: list[str], stdin: str | None = None, cwd: Path | None = None, timeout: int = 60):
    return subprocess.run(
        args,
        input=stdin,
        text=True,
        capture_output=True,
        cwd=str(cwd or VOW_ROOT),
        timeout=timeout,
    )


def rec(name: str, **kw) -> dict:
    row = {"name": name, **kw}
    RESULTS.append(row)
    flag = "HOLE" if kw.get("hole") else ("HOLD" if kw.get("hold") else "NOTE")
    print(f"[{flag}] {name}")
    for k, v in kw.items():
        if k in {"hole", "hold", "note", "pair", "status", "rc", "host", "legal", "detail"}:
            print(f"      {k}={v}")
    return row


def json_out(p: subprocess.CompletedProcess) -> dict:
    try:
        return json.loads(p.stdout or "{}")
    except json.JSONDecodeError:
        return {"_raw": p.stdout, "_err": p.stderr, "_rc": p.returncode}


def vow_file(path: Path, extra: list[str] | None = None) -> tuple[subprocess.CompletedProcess, dict]:
    p = sh(VOW + (extra or []) + ["--json", str(path)])
    return p, json_out(p)


def vow_fail(blob: str, extra: list[str] | None = None) -> tuple[subprocess.CompletedProcess, dict]:
    p = sh(VOW + ["--from-fail", "--json"] + (extra or []), stdin=blob)
    return p, json_out(p)


def troth_fail(blob: str, extra: list[str] | None = None) -> tuple[subprocess.CompletedProcess, dict]:
    p = sh(TROTH + ["--from-fail", "--json"] + (extra or []), stdin=blob, cwd=TROTH_ROOT)
    return p, json_out(p)


def status_counts(porcelain: str) -> dict[str, int]:
    counts: dict[str, int] = {}
    bound_files: list[str] = []
    for line in porcelain.splitlines():
        if line.startswith("status\t"):
            parts = line.split("\t")
            st = parts[1] if len(parts) > 1 else "?"
            counts[st] = counts.get(st, 0) + 1
            if st == "BOUND" and len(parts) > 2:
                bound_files.append(parts[2])
    counts["_bound_files"] = bound_files  # type: ignore[assignment]
    return counts


def write_fixtures() -> None:
    FIX.mkdir(parents=True, exist_ok=True)
    write(
        "ran_on_comment.py",
        "# ran on alice\n# HOME=/Users/alice\n\ndef test_spec():\n    assert 1 + 1 == 2\n",
    )
    write(
        "ran_on_trailing.py",
        "def test_spec():\n    assert 1 + 1 == 2  # ran on alice HOME=/Users/alice\n",
    )
    write(
        "ran_on_docstring.py",
        '"""ran on alice HOME=/Users/alice"""\n\ndef test_spec():\n    assert True\n',
    )
    write(
        "ran_on_swift.swift",
        "# ran on alice\nfunc test() {\n    XCTAssertEqual(1, 2)\n}\n",
    )
    write(
        "ran_on_expect_comment.txt",
        "#expect this was alice\n"
        "tests/test_add.py:3: in test_add\n"
        "    assert 1 + 1 == 3\n"
        "E   AssertionError: assert (1 + 1) == 3\n"
        "E   - 2\n"
        "E   + 3\n",
    )
    write(
        "ran_on_with_paths.txt",
        "# ran on alice\n"
        "# HOME=/Users/alice\n"
        "E   AssertionError: '/tmp/x' != '/Users/alice/Library'\n"
        "E   - /tmp/x\n"
        "E   + /Users/alice/Library\n",
    )
    write(
        "host_getenv.py",
        "import os\n\n"
        "def test_host():\n"
        "    assert os.environ['HOSTNAME'] == 'ci-mac-7'\n",
    )
    write(
        "host_gethostname.py",
        "import socket\n\n"
        "def test_host():\n"
        "    assert socket.gethostname() == 'ci-mac-7'\n",
    )
    write(
        "host_only.snap",
        "host: ci-mac-7\nhostname: ci-mac-7\nstatus: green\n",
    )
    write(
        "host_fail.txt",
        "tests/test_host.py:4: in test_host\n"
        "    assert os.environ['HOSTNAME'] == 'ci-mac-7'\n"
        "E   AssertionError: assert 'Mac' == 'ci-mac-7'\n"
        "E     - ci-mac-7\n"
        "E     + Mac\n",
    )
    write(
        "host_live_fail.txt",
        "tests/test_host.py:4: in test_host\n"
        f"    assert socket.gethostname() == '{HOST}'\n"
        f"E   AssertionError: assert 'other-box' == '{HOST}'\n"
        f"E     - {HOST}\n"
        "E     + other-box\n",
    )
    write(
        "expect_plain.swift",
        'import Testing\n@Test\nfunc userIsAlice() {\n    #expect(os.getenv("USER") == "alice")\n}\n',
    )
    write(
        "expect_generic.swift",
        "import Testing\n"
        "@Test\n"
        "func homeIsAlice() {\n"
        '    #expect(home as Optional<String> == "/Users/alice")\n'
        '    #expect(User<Host>.home == "/Users/alice")\n'
        '    #expect(foo<Bar, Baz>() == "/Users/alice/Library")\n'
        '    #expect((got as Array<String>) == ["/Users/alice"])\n'
        "}\n",
    )
    write(
        "expect_generic_noise.swift",
        "import Testing\n"
        "@Test\n"
        "func typed() {\n"
        '    #expect(value as KeyPath<User, String> == "/Users/alice")\n'
        "}\n",
    )
    write(
        "expect_closure.swift",
        "import Testing\n"
        "@Test\n"
        "func contains() {\n"
        '    #expect(items.contains(where: { $0.path == "/Users/alice" }))\n'
        "}\n",
    )
    write(
        "swift_testing_dump.txt",
        'Expectation failed: (home → "/Users/alice/Library") == "/tmp/x"\n',
    )
    write(
        "swift_testing_eq.txt",
        'Expectation failed: "/Users/alice/Library" == "/tmp/x"\n',
    )
    write(
        "wrap_message.swift",
        "func testHome() {\n"
        "    XCTAssertEqual(\n"
        "        got,\n"
        '        "/Users/alice/Library",\n'
        '        "home should be \\(NSHomeDirectory()) not \\(got)"\n'
        "    )\n"
        "}\n",
    )
    write(
        "wrap_message_path.swift",
        "func testHome() {\n"
        '    XCTAssertEqual(got, want, "/Users/alice/Library is required")\n'
        "}\n",
    )
    write(
        "wrap_py.py",
        "def test_home(self):\n"
        "    self.assertEqual(\n"
        "        got,\n"
        '        "/Users/alice/Library",\n'
        '        "expected HOME, got %s" % got,\n'
        "    )\n",
    )
    write(
        "wrap_dump.txt",
        "SitboneCoreTests.testHome: XCTAssertEqual failed: "
        '("/Users/alice/Library") is not equal to ("/tmp/x") - home should match\n',
    )
    write(
        "wrap_multiline.txt",
        "SitboneCoreTests.testHome: XCTAssertEqual failed: "
        '("/Users/alice/Library") is not equal to\n'
        '("/tmp/x")\n',
    )
    write(
        "wrap_paren.txt",
        'XCTAssertEqual failed: ("home (/Users/alice)") is not equal to ("/tmp/x")\n',
    )
    write(
        "name_follow.py",
        "import os\n"
        "from pathlib import Path\n\n"
        "def test_home():\n"
        "    home = os.environ['HOME']\n"
        "    expected = home\n"
        "    got = Path.home().as_posix()\n"
        "    assert got == expected\n",
    )
    write(
        "name_follow_literal.py",
        "def test_home():\n"
        '    expected = "/Users/annenpolka"\n'
        "    assert got == expected\n",
    )
    write(
        "name_follow_fail.txt",
        "tests/test_home.py:8: in test_home\n"
        "    assert got == expected\n"
        "E   AssertionError: assert '/tmp/x' == expected\n",
    )
    write(
        "name_follow_fail_vv.txt",
        "tests/test_home.py:8: in test_home\n"
        "    assert got == expected\n"
        "E   AssertionError: assert '/tmp/x' == '/Users/annenpolka'\n"
        "E    +  where got = '/tmp/x'\n"
        "E    +    and expected = home\n",
    )
    write(
        "name_follow_fail_diff.txt",
        "tests/test_home.py:8: in test_home\n"
        "    assert got == expected\n"
        "E   AssertionError: assert '/tmp/x' == '/Users/annenpolka'\n"
        "E   - /Users/annenpolka\n"
        "E   + /tmp/x\n",
    )
    write(
        "pytest_pm_nosrc.txt",
        "E   AssertionError: assert 'runner' == 'alice'\n",
    )
    write(
        "cargo_eq_got_left.txt",
        "assertion `left == right` failed\n"
        '  left: "/home/runner/work/proj"\n'
        ' right: "/Users/alice/proj"\n',
    )
    write(
        "portable_tmp_vs_alice.txt",
        'XCTAssertEqual failed: ("/Users/alice/Library") is not equal to ("/tmp/x")\n',
    )
    write(
        "portable_tmp_vs_me.txt",
        f'E   - /tmp/x\nE   + {HOME}/proj\n',
    )
    write(
        "alice_vs_me.txt",
        f"E   - /Users/alice/proj\nE   + {HOME}/proj\n",
    )
    write(
        "quote_assert.rs",
        "#[test]\n"
        "fn quotes() {\n"
        '    assert_eq!(shell_single_quote("/Users/John Doe/kizu"), "\'/Users/John Doe/kizu\'");\n'
        '    assert_eq!(cwd, Path::new("/home/user/project"));\n'
        "}\n",
    )
    write(
        "quote_comment.rs",
        "// kizu binary lives at `/Users/John Doe/.cargo/bin/kizu`\n"
        "// ran on alice\n"
        "fn not_a_test() {}\n",
    )
    write(
        "quote_nested.rs",
        'assert_eq!(shell_single_quote("/Users/alice/kizu"), "\'/Users/alice/kizu\'");\n',
    )
    write(
        "quote_real_home.rs",
        f'assert_eq!(shell_single_quote("{HOME}/kizu"), "\'{HOME}/kizu\'");\n',
    )
    write(
        "title_github.swift",
        "func testChromeTitle() {\n"
        "    let result = WindowTitleParser.extractSiteName(\n"
        '        from: "GitHub - annenpolka/sitbone · Pull Request #3 - Google Chrome",\n'
        '        app: "Google Chrome"\n'
        "    )\n"
        '    XCTAssertEqual(result, "GitHub")\n'
        "}\n",
    )
    write(
        "title_bare.swift",
        'XCTAssertEqual(result, "annenpolka")\n'
        'XCTAssertEqual(score("annenpolka/sitbone"), 1.0)\n',
    )


def attack_gold() -> None:
    p = sh(VOW + ["--self-test"])
    rec(
        "gold.self-test",
        hold=p.returncode == 0,
        hole=p.returncode != 0,
        rc=p.returncode,
        detail=p.stderr[-400:] if p.returncode else "ok",
    )
    for name, want_pair, exp_home, act_home in [
        ("pytest_fail.txt", "EXPECTED-BOUND vs ACTUAL-BOUND", "/Users/alice", "/home/runner"),
        ("xctest_fail.txt", "EXPECTED-OPEN vs ACTUAL-BOUND", None, "/Users/alice"),
    ]:
        blob = (VOW_ROOT / "fixtures" / name).read_text(encoding="utf-8")
        proc, data = vow_fail(blob)
        pair = data.get("pair")
        eh = (data.get("expected") or {}).get("require", {}).get("HOME")
        ah = (data.get("actual") or {}).get("require", {}).get("HOME")
        ok = pair == want_pair and ah == act_home and eh == exp_home
        rec(
            f"gold.{name}",
            hold=ok,
            hole=not ok,
            pair=pair,
            detail=f"expHOME={eh} actHOME={ah} host={data.get('host')}",
        )


def attack_ran_on() -> None:
    _, d = vow_file(FIX / "ran_on_comment.py")
    rec(
        "ran_on.file_comment_not_oath",
        hold=d.get("status") in {"OPEN", "SPEC"} and "USER" not in d.get("require", {}),
        hole=d.get("status") == "BOUND" or "USER" in d.get("require", {}),
        status=d.get("status"),
        detail=f"require={d.get('require')} silent={[s.get('value') for s in d.get('silent', [])]}",
    )
    _, d = vow_file(FIX / "ran_on_trailing.py")
    rec(
        "ran_on.trailing_comment",
        hold="USER" not in d.get("require", {}) and d.get("status") != "BOUND",
        hole=d.get("status") == "BOUND",
        status=d.get("status"),
        detail=f"require={d.get('require')} silent={d.get('silent')}",
    )
    _, d = vow_file(FIX / "ran_on_docstring.py")
    rec(
        "ran_on.docstring",
        hold=d.get("status") != "BOUND" and "USER" not in d.get("require", {}),
        hole=d.get("status") == "BOUND" or "HOME" in d.get("require", {}),
        status=d.get("status"),
        detail=f"require={d.get('require')} witnesses={d.get('witnesses')}",
    )
    _, d = vow_file(FIX / "ran_on_swift.swift")
    silent = d.get("silent") or []
    rec(
        "ran_on.swift_hash_not_comment",
        hold=d.get("status") != "BOUND",
        hole=d.get("status") == "BOUND",
        status=d.get("status"),
        note="Swift # is not a comment; ran-on line is dropped, not silent",
        detail=f"silent={silent} require={d.get('require')}",
    )
    blob = (FIX / "ran_on_expect_comment.txt").read_text(encoding="utf-8")
    _, d = vow_fail(blob)
    rec(
        "ran_on.hash_expect_in_dump",
        hold=True,
        pair=d.get("pair"),
        detail=json.dumps(
            {
                "pair": d.get("pair"),
                "source": (d.get("pairs") or [{}])[0].get("source") if d.get("pairs") else d.get("source"),
                "expected": (d.get("expected") or {}).get("require"),
                "actual": (d.get("actual") or {}).get("require"),
            }
        ),
    )
    blob = (FIX / "ran_on_with_paths.txt").read_text(encoding="utf-8")
    _, d = vow_fail(blob)
    exp_u = (d.get("expected") or {}).get("require", {}).get("USER")
    act_h = (d.get("actual") or {}).get("require", {}).get("HOME")
    rec(
        "ran_on.dump_comment_does_not_bind_but_paths_do",
        hold=exp_u is None and act_h == "/Users/alice",
        hole=exp_u == "alice" or act_h != "/Users/alice",
        pair=d.get("pair"),
        detail=f"expUSER={exp_u} actHOME={act_h} host={d.get('host')}",
    )
    gold = (VOW_ROOT / "fixtures" / "comment_in_fail.txt").read_text(encoding="utf-8")
    _, d = vow_fail(gold)
    rec(
        "ran_on.gold_comment_in_fail",
        hold="OPEN" in (d.get("pair") or "") and not (d.get("expected") or {}).get("require"),
        hole=bool((d.get("expected") or {}).get("require")),
        pair=d.get("pair"),
    )


def attack_host_soft() -> None:
    _, d = vow_file(FIX / "host_getenv.py")
    rec(
        "host.getenv_HOSTNAME_not_in_require",
        hold="HOST" not in d.get("require", {}) and d.get("status") != "BOUND",
        hole=d.get("status") == "BOUND",
        status=d.get("status"),
        detail=f"require={d.get('require')} soft={d.get('soft')} witnesses={d.get('witnesses')}",
        note="HOST is SOFT_AXES; hostname oath cannot skip",
    )
    p_apply = sh(VOW + ["--apply", str(FIX / "host_getenv.py")])
    rec(
        "host.getenv_apply_everywhere",
        hole=p_apply.returncode == 0 and d.get("soft", {}).get("HOST") == "ci-mac-7",
        hold=p_apply.returncode != 0,
        rc=p_apply.returncode,
        detail=f"status={d.get('status')} soft={d.get('soft')} apply_rc={p_apply.returncode}",
        note="ci-mac-7 HOST identity MATCH/apply on this laptop (Mac.localdomain)",
    )
    _, d = vow_file(FIX / "host_gethostname.py")
    rec(
        "host.gethostname",
        hold="HOST" not in d.get("require", {}),
        hole=d.get("status") == "BOUND",
        status=d.get("status"),
        detail=f"require={d.get('require')} soft={d.get('soft')}",
    )
    _, d = vow_file(FIX / "host_only.snap")
    rec(
        "host.snap_label",
        hold=d.get("status") != "BOUND" or "HOST" in d.get("soft", {}),
        hole=d.get("status") == "BOUND" and "HOST" in d.get("require", {}),
        status=d.get("status"),
        detail=f"require={d.get('require')} soft={d.get('soft')}",
    )
    blob = (FIX / "host_fail.txt").read_text(encoding="utf-8")
    proc, d = vow_fail(blob)
    rec(
        "host.fail_dump_cannot_name_role",
        hole=(d.get("pair") or "").count("OPEN") == 2 or d.get("host") == "NEITHER",
        hold=d.get("host") in {"EXPECTED", "ACTUAL"},
        pair=d.get("pair"),
        host=d.get("host"),
        detail=f"exp={ (d.get('expected') or {}).get('require') }/{ (d.get('expected') or {}).get('soft') } "
        f"act={ (d.get('actual') or {}).get('require') }/{ (d.get('actual') or {}).get('soft') }",
    )
    blob = (FIX / "host_live_fail.txt").read_text(encoding="utf-8")
    _, d = vow_fail(blob)
    rec(
        "host.live_hostname_dump_not_ACTUAL",
        hole=d.get("host") != "ACTUAL",
        hold=d.get("host") == "ACTUAL",
        pair=d.get("pair"),
        host=d.get("host"),
        note=f"this host HOST={HOST}; dump actual is other-box, expected is {HOST}",
        detail=f"soft_exp={(d.get('expected') or {}).get('soft')} soft_act={(d.get('actual') or {}).get('soft')}",
    )
    # HOST is recorded live but never compared
    live = V.live_axes()
    rec(
        "host.live_axes_has_HOST_unused",
        hold="HOST" in live,
        hole="HOST" not in live,
        detail=str(live),
        note="live_axes collects HOST; match_oath never reads SOFT_AXES",
    )


def attack_expect_generic() -> None:
    _, d = vow_file(FIX / "expect_plain.swift")
    rec(
        "expect.plain_USER_alice",
        hold=d.get("require", {}).get("USER") == "alice" and d.get("status") == "BOUND",
        hole=d.get("require", {}).get("USER") != "alice",
        status=d.get("status"),
        detail=f"require={d.get('require')} windows={[w.get('form') for w in d.get('windows', [])]}",
    )
    for name in ("expect_generic.swift", "expect_generic_noise.swift", "expect_closure.swift"):
        _, d = vow_file(FIX / name)
        homes = [w.get("value") for w in d.get("witnesses", []) if w.get("axis") == "HOME"]
        rec(
            f"expect.{name}",
            hole=d.get("status") != "BOUND" or "/Users/alice" not in str(d.get("require")),
            hold=d.get("status") == "BOUND" and d.get("require", {}).get("HOME") == "/Users/alice",
            status=d.get("status"),
            detail=f"require={d.get('require')} homes={homes} windows={d.get('windows')}",
        )
    blob = (FIX / "swift_testing_dump.txt").read_text(encoding="utf-8")
    _, d = vow_fail(blob)
    rec(
        "expect.swift_testing_dump_loses_actual",
        hole=(d.get("actual") or {}).get("require", {}).get("HOME") != "/Users/alice"
        or (d.get("pair") or "") != "EXPECTED-OPEN vs ACTUAL-BOUND",
        hold=(d.get("actual") or {}).get("require", {}).get("HOME") == "/Users/alice",
        pair=d.get("pair"),
        detail=f"exp={(d.get('expected') or {}).get('require')} act={(d.get('actual') or {}).get('require')} "
        f"raw_exp={d.get('expected_raw')} raw_act={d.get('actual_raw')} pairs={d.get('pairs')}",
    )
    blob = (FIX / "swift_testing_eq.txt").read_text(encoding="utf-8")
    _, d = vow_fail(blob)
    rec(
        "expect.swift_testing_eq_only_right",
        hole=True,
        pair=d.get("pair"),
        detail=f"raw_exp={d.get('expected_raw')} raw_act={d.get('actual_raw')} "
        f"exp={ (d.get('expected') or {}).get('require') } act={ (d.get('actual') or {}).get('require') }",
    )


def attack_wrap() -> None:
    _, d = vow_file(FIX / "wrap_message.swift")
    rec(
        "wrap.swift_third_arg_ignored",
        hold=d.get("require", {}).get("HOME") == "/Users/alice",
        hole=d.get("require", {}).get("HOME") != "/Users/alice",
        status=d.get("status"),
        detail=f"require={d.get('require')} windows={d.get('windows')}",
    )
    _, d = vow_file(FIX / "wrap_message_path.swift")
    rec(
        "wrap.swift_message_path_not_expected",
        hold=d.get("require", {}).get("HOME") != "/Users/alice",
        hole=d.get("require", {}).get("HOME") == "/Users/alice",
        status=d.get("status"),
        note="third-arg path is not the expected slot; name-follow hole if want is a var",
        detail=f"require={d.get('require')} windows={d.get('windows')}",
    )
    _, d = vow_file(FIX / "wrap_py.py")
    rec(
        "wrap.py_assertEqual_multiline",
        hold=d.get("require", {}).get("HOME") == "/Users/alice",
        hole=d.get("require", {}).get("HOME") != "/Users/alice",
        status=d.get("status"),
        detail=f"require={d.get('require')} windows={d.get('windows')}",
    )
    blob = (FIX / "wrap_dump.txt").read_text(encoding="utf-8")
    _, d = vow_fail(blob)
    rec(
        "wrap.dump_trailing_message",
        hole=(d.get("pair") is None and not d.get("pairs"))
        or (d.get("actual") or {}).get("require", {}).get("HOME") != "/Users/alice",
        hold=(d.get("actual") or {}).get("require", {}).get("HOME") == "/Users/alice",
        pair=d.get("pair"),
        detail=f"pairs={d.get('pairs')} status={d.get('status')} require={d.get('require')}",
        note="SWIFT_RE is $-anchored; trailing message kills the pair",
    )
    blob = (FIX / "wrap_multiline.txt").read_text(encoding="utf-8")
    _, d = vow_fail(blob)
    rec(
        "wrap.dump_multiline",
        hole=(d.get("actual") or {}).get("require", {}).get("HOME") != "/Users/alice",
        hold=(d.get("actual") or {}).get("require", {}).get("HOME") == "/Users/alice",
        pair=d.get("pair"),
        detail=f"pairs={d.get('pairs')} status={d.get('status')}",
        note="parse_fail is line-at-a-time; wrap across newline loses XCTest pair",
    )
    blob = (FIX / "wrap_paren.txt").read_text(encoding="utf-8")
    _, d = vow_fail(blob)
    rec(
        "wrap.dump_paren_in_value",
        hole=(d.get("actual") or {}).get("require", {}).get("HOME") != "/Users/alice",
        hold=(d.get("actual") or {}).get("require", {}).get("HOME") == "/Users/alice",
        pair=d.get("pair"),
        detail=f"pairs={d.get('pairs')} raw_exp={d.get('expected_raw')} raw_act={d.get('actual_raw')}",
        note="SWIFT_RE [^)]+ stops at first paren inside the value",
    )


def attack_name_follow() -> None:
    _, d = vow_file(FIX / "name_follow.py")
    rec(
        "name.expected_eq_home_assert_got",
        hole=d.get("status") != "BOUND" or "HOME" not in d.get("require", {}),
        hold=d.get("status") == "BOUND",
        status=d.get("status"),
        detail=f"require={d.get('require')} windows={d.get('windows')} witnesses={d.get('witnesses')}",
        note="does not follow expected = home; assert got == expected",
    )
    _, d = vow_file(FIX / "name_follow_literal.py")
    rec(
        "name.expected_literal_assign",
        hold=d.get("require", {}).get("HOME") == "/Users/annenpolka" or d.get("status") == "BOUND",
        hole=d.get("status") not in {"BOUND", "SPEC", "FIXTURE"},
        status=d.get("status"),
        detail=f"require={d.get('require')} witnesses={[{'role':w.get('role'),'axis':w.get('axis'),'value':w.get('value')} for w in d.get('witnesses',[])]}",
    )
    blob = (FIX / "name_follow_fail.txt").read_text(encoding="utf-8")
    _, d = vow_fail(blob)
    rec(
        "name.fail_assert_got_eq_expected_name",
        hole=(d.get("pair") or "") == "EXPECTED-OPEN vs ACTUAL-OPEN"
        or (d.get("expected_raw") == "/tmp/x"),
        hold=(d.get("expected") or {}).get("require", {}).get("HOME") == "/Users/annenpolka",
        pair=d.get("pair"),
        detail=f"raw_exp={d.get('expected_raw')} raw_act={d.get('actual_raw')} "
        f"exp={ (d.get('expected') or {}).get('require') } act={ (d.get('actual') or {}).get('require') }",
        note="pytest PM without repr: expected slot is the identifier, polarity may swap",
    )
    blob = (FIX / "name_follow_fail_vv.txt").read_text(encoding="utf-8")
    _, d = vow_fail(blob)
    rec(
        "name.fail_vv_expected_eq_home_name",
        hole=(d.get("expected") or {}).get("require", {}).get("HOME") != "/Users/annenpolka",
        hold=(d.get("expected") or {}).get("require", {}).get("HOME") == "/Users/annenpolka",
        pair=d.get("pair"),
        detail=f"raw_exp={d.get('expected_raw')} raw_act={d.get('actual_raw')} "
        f"exp={ (d.get('expected') or {}).get('require') } act={ (d.get('actual') or {}).get('require') }",
    )
    blob = (FIX / "name_follow_fail_diff.txt").read_text(encoding="utf-8")
    _, d = vow_fail(blob)
    rec(
        "name.fail_diff_saves_the_pair",
        hold=(d.get("expected") or {}).get("require", {}).get("HOME") == "/Users/annenpolka"
        and (d.get("pair") or "").startswith("EXPECTED-BOUND"),
        hole=(d.get("expected") or {}).get("require", {}).get("HOME") != "/Users/annenpolka",
        pair=d.get("pair"),
        detail=f"exp={ (d.get('expected') or {}).get('require') } act={ (d.get('actual') or {}).get('require') }",
    )
    blob = (FIX / "pytest_pm_nosrc.txt").read_text(encoding="utf-8")
    _, d = vow_fail(blob)
    rec(
        "name.pytest_pm_no_source_polarity",
        hole=(d.get("expected") or {}).get("require", {}).get("USER") == "runner"
        or (d.get("actual") or {}).get("require", {}).get("USER") == "alice",
        hold=(d.get("expected") or {}).get("require", {}).get("USER") == "alice",
        pair=d.get("pair"),
        detail=f"raw_exp={d.get('expected_raw')} raw_act={d.get('actual_raw')} "
        f"exp={ (d.get('expected') or {}).get('require') } act={ (d.get('actual') or {}).get('require') }",
        note="assert actual == expected without source/diff: PM takes left as expected",
    )
    blob = (FIX / "cargo_eq_got_left.txt").read_text(encoding="utf-8")
    _, d = vow_fail(blob)
    rec(
        "name.cargo_left_is_actual_in_rustc",
        hole=(d.get("expected") or {}).get("require", {}).get("HOME") == "/home/runner"
        or (d.get("actual") or {}).get("require", {}).get("HOME") == "/Users/alice",
        hold=(d.get("expected") or {}).get("require", {}).get("HOME") == "/Users/alice",
        pair=d.get("pair"),
        detail=f"raw_exp={d.get('expected_raw')} raw_act={d.get('actual_raw')} "
        f"exp={ (d.get('expected') or {}).get('require') } act={ (d.get('actual') or {}).get('require') }",
        note="rustc left=got actual, right=expected; vow expected=left actual=right",
    )


def attack_apply_open() -> None:
    blob = (FIX / "portable_tmp_vs_alice.txt").read_text(encoding="utf-8")
    p0 = sh(VOW + ["--from-fail", "--apply"], stdin=blob)
    p_both = sh(VOW + ["--from-fail", "--apply", "--side", "both"], stdin=blob)
    p_act = sh(VOW + ["--from-fail", "--apply", "--side", "actual"], stdin=blob)
    _, d = vow_fail(blob)
    rec(
        "apply.xctest_open_expected_default",
        hold=p0.returncode == 0,
        hole=p0.returncode != 0,
        rc=p0.returncode,
        pair=d.get("pair"),
        host=d.get("host"),
        note="OPEN expected still applies here (NEITHER); default --side expected",
    )
    rec(
        "apply.xctest_side_both_skips_portable",
        hole=p_both.returncode == 1 and p0.returncode == 0,
        hold=p_both.returncode == 0,
        rc=p_both.returncode,
        note="--side both ANDs Alice MISS into OPEN expected and skips a /tmp golden",
        detail=f"default_rc={p0.returncode} both_rc={p_both.returncode} actual_rc={p_act.returncode} host={d.get('host')}",
    )
    t0 = sh(TROTH + ["--from-fail", "--apply"], stdin=blob, cwd=TROTH_ROOT)
    t_both = sh(TROTH + ["--from-fail", "--apply", "--side", "both"], stdin=blob, cwd=TROTH_ROOT)
    rec(
        "apply.troth_peel_keeps_open",
        hold=t0.returncode == 0,
        hole=t0.returncode != 0,
        rc=t0.returncode,
        detail=t0.stdout.splitlines()[:12],
        note=f"troth --side both rc={t_both.returncode} (names AND trap, still exits 1)",
    )
    blob = (FIX / "portable_tmp_vs_me.txt").read_text(encoding="utf-8")
    p0 = sh(VOW + ["--from-fail", "--apply"], stdin=blob)
    p_act = sh(VOW + ["--from-fail", "--apply", "--side", "actual"], stdin=blob)
    _, d = vow_fail(blob)
    rec(
        "apply.tmp_vs_this_host_default_OPEN",
        hold=p0.returncode == 0 and d.get("host") == "ACTUAL",
        hole=p0.returncode != 0,
        rc=p0.returncode,
        host=d.get("host"),
        pair=d.get("pair"),
        note="host ACTUAL is named; --apply still talks to OPEN expected (rc=0). actual-side skip is a flag, not host-role.",
        detail=f"actual_apply_rc={p_act.returncode}",
    )
    t0 = sh(TROTH + ["--from-fail", "--apply"], stdin=blob, cwd=TROTH_ROOT)
    tf = sh(TROTH + ["--from-fail", "--fixture"], stdin=blob, cwd=TROTH_ROOT)
    rec(
        "apply.troth_tmp_vs_me_legal_OPEN_ACTUAL",
        hold=t0.returncode == 0 and HOME in (tf.stdout or ""),
        hole=t0.returncode != 0,
        rc=t0.returncode,
        detail=f"troth apply rc={t0.returncode} fixture={tf.stdout.strip()!r}",
    )
    blob = (FIX / "alice_vs_me.txt").read_text(encoding="utf-8")
    p0 = sh(VOW + ["--from-fail", "--apply"], stdin=blob)
    p_act = sh(VOW + ["--from-fail", "--apply", "--side", "actual"], stdin=blob)
    _, d = vow_fail(blob)
    rec(
        "apply.alice_expected_vs_me_actual",
        hole=p0.returncode == 1 and p_act.returncode == 0 and d.get("host") == "ACTUAL",
        hold=p0.returncode == 0,
        rc=p0.returncode,
        host=d.get("host"),
        pair=d.get("pair"),
        note="this host produced the fail; vow --apply skips (expected Alice MISS). --side actual would apply.",
        detail=f"actual_apply_rc={p_act.returncode}",
    )
    t0 = sh(TROTH + ["--from-fail", "--apply"], stdin=blob, cwd=TROTH_ROOT)
    rec(
        "apply.troth_alice_vs_me_applies_actual",
        hold=t0.returncode == 0,
        hole=t0.returncode != 0,
        rc=t0.returncode,
        detail=t0.stdout.splitlines()[:14],
    )


def attack_sitbone_kizu() -> None:
    p = sh(VOW + ["--scan", "-C", str(SITBONE), "--porcelain"], timeout=120)
    counts = status_counts(p.stdout)
    bound = counts.get("BOUND", 0)
    fixture = counts.get("FIXTURE", 0)
    rec(
        "dogfood.sitbone_scan",
        hold=bound == 0 and fixture >= 1,
        hole=bound > 0,
        status=str({k: v for k, v in counts.items() if not str(k).startswith("_")}),
        detail=f"BOUND files={counts.get('_bound_files')} fixture={fixture}",
        note="FIXTURE is identity-as-data, not TAINTED",
    )
    title = SITBONE / "Tests/SitboneCoreTests/WindowTitleParserTests.swift"
    _, d = vow_file(title)
    rec(
        "dogfood.sitbone_title_not_USER",
        hold="USER" not in d.get("require", {}) and d.get("status") in {"OPEN", "FIXTURE"},
        hole="USER" in d.get("require", {}) or d.get("status") == "BOUND",
        status=d.get("status"),
        detail=f"require={d.get('require')} fixture={[w for w in d.get('witnesses',[]) if w.get('role')=='fixture'][:3]}",
    )
    _, d = vow_file(FIX / "title_bare.swift")
    rec(
        "dogfood.bare_annenpolka_not_BOUND",
        hold=d.get("status") != "BOUND" and "USER" not in d.get("require", {}),
        hole=d.get("status") == "BOUND",
        status=d.get("status"),
        detail=f"require={d.get('require')} witnesses={d.get('witnesses')}",
    )
    p = sh(VOW + ["--scan", "-C", str(KIZU), "--porcelain"], timeout=180)
    counts = status_counts(p.stdout)
    bound = counts.get("BOUND", 0)
    spec = counts.get("SPEC", 0)
    rec(
        "dogfood.kizu_scan",
        hold=bound == 0 and spec >= 1,
        hole=bound > 0,
        status=str({k: v for k, v in counts.items() if not str(k).startswith("_")}),
        detail=f"BOUND files={counts.get('_bound_files')} spec={spec}",
    )
    init_tests = KIZU / "src/init/tests.rs"
    _, d = vow_file(init_tests)
    rec(
        "dogfood.kizu_init_tests_quoting",
        hold=d.get("status") in {"SPEC", "OPEN"} and "HOME" not in d.get("require", {}),
        hole="HOME" in d.get("require", {}) or d.get("status") == "BOUND",
        status=d.get("status"),
        detail=f"require={d.get('require')} silent_axes={[s.get('axis')+ '='+s.get('value','') for s in d.get('silent',[])][:6]} "
        f"payload={[w.get('value') for w in d.get('witnesses',[]) if w.get('role')=='payload'][:4]}",
    )
    attach = KIZU / "src/attach.rs"
    _, d = vow_file(attach)
    rec(
        "dogfood.kizu_attach_comment_john_doe",
        hold=d.get("status") != "BOUND" and "HOME" not in d.get("require", {}),
        hole=d.get("status") == "BOUND",
        status=d.get("status"),
        detail=f"require={d.get('require')} silent={[s.get('value') for s in d.get('silent',[])][:6]}",
    )
    _, d = vow_file(FIX / "quote_assert.rs")
    rec(
        "quote.assert_john_doe_is_SPEC",
        hold=d.get("status") in {"SPEC", "OPEN"} and "HOME" not in d.get("require", {}),
        hole=d.get("status") == "BOUND",
        status=d.get("status"),
        detail=f"require={d.get('require')} witnesses={[{'role':w.get('role'),'axis':w.get('axis'),'value':w.get('value')} for w in d.get('witnesses',[])]}",
    )
    _, d = vow_file(FIX / "quote_comment.rs")
    rec(
        "quote.comment_john_doe_silent",
        hold=d.get("status") != "BOUND" and "HOME" not in d.get("require", {}),
        hole=d.get("status") == "BOUND",
        status=d.get("status"),
        detail=f"silent={d.get('silent')} require={d.get('require')}",
    )
    _, d = vow_file(FIX / "quote_nested.rs")
    rec(
        "quote.nested_alice_callarg",
        hole=d.get("status") == "BOUND",
        hold=d.get("status") in {"SPEC", "OPEN"},
        status=d.get("status"),
        note="nested quote('/Users/alice') as actual expr; expected is quoted form — textbook alice may be SPEC",
        detail=f"require={d.get('require')} witnesses={d.get('witnesses')} windows={d.get('windows')}",
    )
    _, d = vow_file(FIX / "quote_real_home.rs")
    rec(
        "quote.nested_this_home_callarg",
        hole=d.get("status") == "BOUND",
        hold=d.get("status") != "BOUND",
        status=d.get("status"),
        note="onset: nested quote(this HOME) is not ACTUAL-BOUND. vow unary may still BOUND the expected literal.",
        detail=f"require={d.get('require')} witnesses={[{'role':w.get('role'),'axis':w.get('axis'),'value':w.get('value')} for w in d.get('witnesses',[])]}",
    )


def attack_peels() -> None:
    p = sh(ONSET + ["-C", str(SITBONE)], cwd=ONSET_ROOT, timeout=120)
    rec(
        "peel.onset_sitbone",
        hold=p.returncode == 0 and "TAINTED" not in p.stdout and "first-actual" in p.stdout,
        hole="TAINTED" in p.stdout or p.returncode != 0,
        rc=p.returncode,
        detail="\n".join(p.stdout.splitlines()[:24]),
    )
    p = sh(ONSET + ["-C", str(KIZU)], cwd=ONSET_ROOT, timeout=180)
    rec(
        "peel.onset_kizu",
        hold=p.returncode == 0 and "first-actual" in p.stdout,
        hole=p.returncode != 0,
        rc=p.returncode,
        detail="\n".join(p.stdout.splitlines()[:24]),
    )
    p = sh(WRIT + ["--list", "-C", str(SITBONE)], cwd=WRIT_ROOT, timeout=60)
    rec(
        "peel.writ_list_sitbone",
        hold=p.returncode == 0,
        hole=p.returncode != 0,
        rc=p.returncode,
        detail="\n".join(p.stdout.splitlines()[:20]),
    )
    p = sh(WRIT + ["--list", "-C", str(KIZU)], cwd=WRIT_ROOT, timeout=60)
    rec(
        "peel.writ_list_kizu",
        hold=p.returncode == 0,
        hole=p.returncode != 0,
        rc=p.returncode,
        detail="\n".join(p.stdout.splitlines()[:20]),
    )
    # onset on wrap/generic fixtures
    for name in (
        "expect_generic.swift",
        "name_follow.py",
        "host_getenv.py",
        "quote_nested.rs",
        "title_github.swift",
    ):
        p = sh(ONSET + [str(FIX / name)], cwd=ONSET_ROOT, timeout=30)
        rec(
            f"peel.onset_{name}",
            hold=True,
            rc=p.returncode,
            detail=p.stdout[:800] or p.stderr[:400],
        )


def copy_gold_fixtures() -> None:
    src = VOW_ROOT / "fixtures"
    dest = FIX / "gold"
    if dest.exists():
        shutil.rmtree(dest)
    shutil.copytree(src, dest)


def main() -> int:
    OUT.mkdir(parents=True, exist_ok=True)
    FIX.mkdir(parents=True, exist_ok=True)
    write_fixtures()
    copy_gold_fixtures()
    attack_gold()
    attack_ran_on()
    attack_host_soft()
    attack_expect_generic()
    attack_wrap()
    attack_name_follow()
    attack_apply_open()
    attack_sitbone_kizu()
    attack_peels()

    holes = [r for r in RESULTS if r.get("hole")]
    holds = [r for r in RESULTS if r.get("hold") and not r.get("hole")]
    summary = {
        "live": {"HOME": HOME, "USER": USER, "HOST": HOST, "platform": PLAT},
        "n": len(RESULTS),
        "holes": len(holes),
        "holds": len(holds),
        "hole_names": [r["name"] for r in holes],
        "hold_names": [r["name"] for r in holds],
        "results": RESULTS,
    }
    (OUT / "results.json").write_text(json.dumps(summary, indent=2, default=str), encoding="utf-8")
    lines = [
        f"destroy-vow live HOME={HOME} USER={USER} HOST={HOST} {PLAT}",
        f"n={len(RESULTS)} holes={len(holes)} holds={len(holds)}",
        "HOLES:",
    ]
    for r in holes:
        lines.append(f"  - {r['name']}: {r.get('note') or r.get('detail') or r.get('pair')}")
    lines.append("HOLDS:")
    for r in holds:
        lines.append(f"  - {r['name']}")
    (OUT / "summary.txt").write_text("\n".join(lines) + "\n", encoding="utf-8")
    print("\n======== SUMMARY ========")
    print("\n".join(lines))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
