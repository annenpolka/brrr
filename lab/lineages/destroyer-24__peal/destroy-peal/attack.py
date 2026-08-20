#!/usr/bin/env python3
"""Adversarial battery against peal(1). Records /tmp/destroy-peal/transcript.txt.

Does not rewrite peal. Invokes the victim as a subprocess.
"""
from __future__ import annotations

import os
import shutil
import subprocess
import sys
import time
from pathlib import Path

ROOT = Path("/tmp/destroy-peal")
FIX = ROOT / "fixtures"
LOG = ROOT / "logs"
TRANSCRIPT = ROOT / "transcript.txt"

PEAL = Path(
    "/Users/annenpolka/.grok/worktrees/annenpolka-brrr/subagent-01a01b6a-b1f0-7600-ae0c-3b73b8f2249f/peal"
)
CHIME = Path(
    "/Users/annenpolka/.grok/worktrees/annenpolka-brrr/subagent-01a01ad1-c9bc-75e2-8872-cc3cdc8f2abf/chime"
)
AMBIT = Path(
    "/Users/annenpolka/.grok/worktrees/annenpolka-brrr/subagent-01a01b56-ac5a-7b03-a99f-434e97f8bd56/ambit"
)
PEAL_WT = PEAL.parent
KIZU = Path("/Users/annenpolka/ghq/github.com/annenpolka/kizu")
SIT = Path("/Users/annenpolka/ghq/github.com/annenpolka/sitbone")
PARSE = KIZU / "src/git/parse.rs"
ARB = SIT / "Sources/SitboneCore/PresenceArbiter.swift"

cases: list[dict] = []


def rec(
    name: str,
    cmd: list[str] | str,
    *,
    cwd: Path | None = None,
    stdin: str | bytes | None = None,
    timeout: float = 30,
    env: dict | None = None,
    note: str = "",
) -> dict:
    cwd = cwd or Path.cwd()
    t0 = time.perf_counter()
    kw: dict = dict(cwd=str(cwd), capture_output=True, timeout=timeout)
    if env:
        kw["env"] = {**os.environ, **env}
    try:
        if isinstance(stdin, bytes):
            kw["input"] = stdin
            r = subprocess.run(cmd if isinstance(cmd, list) else cmd, shell=isinstance(cmd, str), **kw)
            out, err = r.stdout, r.stderr
            # decode for transcript; keep bytes len
            out_s = out.decode("utf-8", errors="replace") if isinstance(out, (bytes, bytearray)) else str(out)
            err_s = err.decode("utf-8", errors="replace") if isinstance(err, (bytes, bytearray)) else str(err)
            rc = r.returncode
        else:
            kw["text"] = True
            kw["input"] = stdin if stdin is not None else None
            r = subprocess.run(cmd if isinstance(cmd, list) else cmd, shell=isinstance(cmd, str), **kw)
            out_s, err_s, rc = r.stdout or "", r.stderr or "", r.returncode
        crashed = False
    except subprocess.TimeoutExpired as e:
        out_s = (e.stdout or b"" if isinstance(e.stdout, (bytes, bytearray)) else (e.stdout or ""))
        err_s = (e.stderr or b"" if isinstance(e.stderr, (bytes, bytearray)) else (e.stderr or ""))
        if isinstance(out_s, (bytes, bytearray)):
            out_s = out_s.decode("utf-8", errors="replace")
        if isinstance(err_s, (bytes, bytearray)):
            err_s = err_s.decode("utf-8", errors="replace")
        rc = 124
        crashed = True
    except Exception as e:
        out_s, err_s, rc, crashed = "", f"{type(e).__name__}: {e}", 99, True
    elapsed = time.perf_counter() - t0
    row = {
        "name": name,
        "cmd": cmd if isinstance(cmd, str) else " ".join(cmd),
        "cwd": str(cwd),
        "rc": rc,
        "elapsed": round(elapsed, 4),
        "stdout": out_s,
        "stderr": err_s,
        "crashed": crashed,
        "note": note,
        "stdin_preview": (
            stdin[:200].decode("utf-8", errors="replace")
            if isinstance(stdin, (bytes, bytearray))
            else (stdin[:200] if isinstance(stdin, str) else "")
        ),
        "stdin_bytes": len(stdin) if isinstance(stdin, (bytes, bytearray, str)) else 0,
    }
    cases.append(row)
    return row


def sh(cmd: str, cwd: Path, **kw):
    return rec(kw.pop("name", cmd), cmd, cwd=cwd, **kw)


def write_transcript() -> None:
    lines = []
    lines.append("# destroy-peal transcript")
    lines.append(f"# cases={len(cases)}")
    lines.append("")
    for i, c in enumerate(cases, 1):
        lines.append("=" * 72)
        lines.append(f"CASE {i}: {c['name']}")
        if c["note"]:
            lines.append(f"NOTE: {c['note']}")
        lines.append(f"cwd: {c['cwd']}")
        lines.append(f"$ {c['cmd']}")
        if c["stdin_bytes"]:
            lines.append(f"stdin_bytes={c['stdin_bytes']}")
            pv = c["stdin_preview"].replace("\n", "\\n")
            lines.append(f"stdin_preview: {pv}")
        lines.append(f"rc={c['rc']} elapsed={c['elapsed']}s crashed={c['crashed']}")
        if c["stderr"]:
            err = c["stderr"]
            if len(err) > 4000:
                err = err[:2000] + "\n…\n" + err[-800:]
            lines.append("--- stderr ---")
            lines.append(err.rstrip())
        out = c["stdout"]
        if len(out) > 6000:
            out = out[:3000] + "\n…\n" + out[-1200:]
        lines.append("--- stdout ---")
        lines.append(out.rstrip())
        lines.append("")
    TRANSCRIPT.write_text("\n".join(lines), encoding="utf-8")


def git_init(path: Path) -> None:
    if path.exists():
        shutil.rmtree(path)
    path.mkdir(parents=True)
    subprocess.run(["git", "init", "-q"], cwd=path, check=True)
    subprocess.run(["git", "config", "user.email", "d@x"], cwd=path, check=True)
    subprocess.run(["git", "config", "user.name", "d"], cwd=path, check=True)


def git_commit(path: Path, msg: str = "x") -> None:
    subprocess.run(["git", "add", "-A"], cwd=path, check=True)
    subprocess.run(["git", "commit", "-q", "-m", msg], cwd=path, check=True)


NESTED = '''"""Ugly nested control flow for when(1)."""


def delete_user(user, db, audit):
    if user is None:
        audit.warn("missing")
        return None
    if user.locked:
        try:
            db.flush()
            if user.role == "admin":
                if not user.can_delete:
                    return "denied"
                raise RuntimeError("admin locked")
            return None
        except RuntimeError as exc:
            audit.error(exc)
            if getattr(exc, "retry", False):
                return "retry"
            return "fail"
        else:
            audit.ok("unlocked path")
        finally:
            db.release()
    elif user.pending:
        for item in user.queue:
            if item.kind == "invite":
                continue
            try:
                db.apply(item)
            except ValueError:
                return "bad-item"
        else:
            return "drained"
    else:
        match user.status:
            case "active" if user.age > 18:
                return db.delete(user)
            case "active":
                return "minor"
            case "gone":
                return None
            case _:
                return "unknown"
    return "fallthrough"
'''


def setup_fixtures() -> None:
    if FIX.exists():
        shutil.rmtree(FIX)
    FIX.mkdir(parents=True)
    LOG.mkdir(parents=True, exist_ok=True)

    # --- ambiguous: two files, identical (line, text) at 13 ---
    amb = FIX / "ambiguous"
    git_init(amb)
    (amb / "a.py").write_text(NESTED, encoding="utf-8")
    (amb / "b.py").write_text(NESTED, encoding="utf-8")
    git_commit(amb, "twin nested")

    # --- substring decoy: short pin "return None" matches comment ---
    sub = FIX / "substring"
    git_init(sub)
    (sub / "real.py").write_text(
        "def f(x):\n"
        "    if x:\n"
        "        return None\n"
        "    return 1\n",
        encoding="utf-8",
    )
    (sub / "decoy.py").write_text(
        "def f(x):\n"
        "    if x:\n"
        "        # note: return None is mentioned here\n"
        "        return 1\n",
        encoding="utf-8",
    )
    git_commit(sub, "substring")

    # --- pins[:16]: first 16 (line,text) shared; unique pin at 17 ---
    p16 = FIX / "pins16"
    git_init(p16)
    real_lines = [f"    let x{i} = {i};" for i in range(1, 17)]
    real_lines.append("    let UNIQUE_REAL = 1;")
    decoy_lines = [f"    let x{i} = {i};" for i in range(1, 17)]
    decoy_lines.append("    let UNIQUE_DECOY = 2;")
    (p16 / "real.rs").write_text(
        "fn f() {\n" + "\n".join(real_lines) + "\n}\n", encoding="utf-8"
    )
    (p16 / "decoy.rs").write_text(
        "fn f() {\n" + "\n".join(decoy_lines) + "\n}\n", encoding="utf-8"
    )
    git_commit(p16, "pins16")

    # --- v2 recover: move + drift + extract-and-keep ---
    v1 = FIX / "v1"
    git_init(v1)
    (v1 / "src").mkdir()
    body = (
        "fn parse_header(bytes: &[u8]) -> Option<usize> {\n"
        "    if bytes.starts_with(b\"\\\"a/\") {\n"
        "        return Some(1);\n"
        "    }\n"
        "    if bytes.len() < 7 {\n"
        "        return None;\n"
        "    }\n"
        "    if !bytes.starts_with(b\"a/\") {\n"
        "        return None;\n"
        "    }\n"
        "    let p = (bytes.len() - 5) / 2;\n"
        "    Some(p)\n"
        "}\n"
    )
    (v1 / "src/parse.rs").write_text(body, encoding="utf-8")
    git_commit(v1, "v1")

    v2move = FIX / "v2move"
    if v2move.exists():
        shutil.rmtree(v2move)
    shutil.copytree(v1, v2move)
    (v2move / "src/git").mkdir(parents=True, exist_ok=True)
    shutil.move(str(v2move / "src/parse.rs"), str(v2move / "src/git/parse.rs"))
    git_commit(v2move, "move to src/git/parse.rs")

    v2drift = FIX / "v2drift"
    if v2drift.exists():
        shutil.rmtree(v2drift)
    shutil.copytree(v1, v2drift)
    drifted = "// preamble\n" * 20 + body
    (v2drift / "src/parse.rs").write_text(drifted, encoding="utf-8")
    git_commit(v2drift, "line drift +20")

    v2keep = FIX / "v2keep"
    if v2keep.exists():
        shutil.rmtree(v2keep)
    shutil.copytree(v1, v2keep)
    (v2keep / "src/git").mkdir(parents=True, exist_ok=True)
    (v2keep / "src/git/parse.rs").write_text(body, encoding="utf-8")
    # leftover stub at old path still has the same line-11 payload
    git_commit(v2keep, "extract-and-keep")

    # --- empty / preamble seed ---
    pre = FIX / "preamble"
    git_init(pre)
    (pre / "mod.py").write_text("X = 1\n\ndef f():\n    return 2\n", encoding="utf-8")
    git_commit(pre, "preamble")

    # --- colon in filename ---
    colon = FIX / "colon"
    git_init(colon)
    (colon / "foo:bar.py").write_text(
        "def f(x):\n    if x:\n        return 'denied'\n", encoding="utf-8"
    )
    git_commit(colon, "colon name")

    # --- binary named as source ---
    bdir = FIX / "binsrc"
    git_init(bdir)
    (bdir / "blob.rs").write_bytes(b"fn f() {\n    let x = 1;\n}\n\x00\xffsecret\n")
    git_commit(bdir, "binary rs")

    # --- huge listed tree for pin-recovery timing ---
    huge = FIX / "hugelist"
    git_init(huge)
    (huge / "src").mkdir()
    for i in range(80):
        (huge / "src" / f"f{i:03d}.rs").write_text(
            f"fn f{i}() {{\n    if true {{\n        let x = {i};\n        return;\n    }}\n}}\n",
            encoding="utf-8",
        )
    (huge / "src" / "target.rs").write_text(
        "fn parse() {\n"
        + "\n".join(f"    let pad_{i} = {i};" for i in range(40))
        + "\n    let b_side = 1;\n    Some(b_side)\n}\n",
        encoding="utf-8",
    )
    git_commit(huge, "80 files")

    # --- two-file different stacks ---
    two = FIX / "twostack"
    git_init(two)
    (two / "alpha.py").write_text(
        "def a(user):\n    if user.locked:\n        return 'denied'\n    return 'ok'\n",
        encoding="utf-8",
    )
    (two / "beta.py").write_text(
        "def b(item):\n    if item.kind == 'invite':\n        return 'skip'\n    return 'go'\n",
        encoding="utf-8",
    )
    git_commit(two, "two stacks")

    # --- identical helper at same line in two files (sitbone-shaped Logging) ---
    ident = FIX / "identline"
    git_init(ident)
    for name in ("A.swift", "B.swift"):
        (ident / name).write_text(
            "import Foundation\n"
            "func log() {\n"
            "    guard isEnabled else {\n"
            "        return\n"
            "    }\n"
            "    print(\"x\")\n"
            "}\n",
            encoding="utf-8",
        )
    git_commit(ident, "identical swift")

    # huge locator stream files
    stream = FIX / "huge_stream.txt"
    rows = [f"src/f{i%80:03d}.rs:{3}:        let x = {i%80};" for i in range(50000)]
    stream.write_text("\n".join(rows) + "\n", encoding="utf-8")

    line_stream = FIX / "huge_linetext.txt"
    rows2 = [f"{(i % 40) + 2}:    let pad_{i%40} = {i%40};" for i in range(20000)]
    line_stream.write_text("\n".join(rows2) + "\n", encoding="utf-8")

    (FIX / "not_locator.txt").write_text("hello world\nthis is not a locator\n", encoding="utf-8")
    (FIX / "json_rg.txt").write_text(
        '{"type":"match","data":{"path":{"text":"src/git/parse.rs"},'
        '"lines":{"text":"    let b_side = 1;\\n"},"line_number":60}}\n',
        encoding="utf-8",
    )
    (FIX / "vimgrep.txt").write_text("src/git/parse.rs:60:5:    let b_side = 1;\n", encoding="utf-8")
    (FIX / "rustc.txt").write_text(
        "error[E0425]: cannot find value `b_side` in this scope\n"
        "  --> src/git/parse.rs:60:9\n"
        "   |\n"
        "60 |     let b_side = &bytes[b_prefix_start + 3..];\n",
        encoding="utf-8",
    )
    (FIX / "context_rg.txt").write_text(
        "src/git/parse.rs-59-    let b_prefix_start = 2 + p;\n"
        "src/git/parse.rs:60:    let b_side = &bytes[b_prefix_start + 3..];\n"
        "src/git/parse.rs-61-    if a_side != b_side {\n",
        encoding="utf-8",
    )
    ansi = (
        "\x1b[35msrc/git/parse.rs\x1b[0m:\x1b[32m60\x1b[0m:"
        "    let b_side = &bytes[b_prefix_start + 3..];\n"
    )
    (FIX / "ansi.txt").write_bytes(ansi.encode())
    (FIX / "bare_line_only.txt").write_text("60:\n", encoding="utf-8")
    (FIX / "file_line_only.txt").write_text("parse.rs:60\n", encoding="utf-8")
    (FIX / "url.txt").write_text("example.com:8080:not-a-file\n", encoding="utf-8")
    (FIX / "windows.txt").write_text("C:\\Users\\x\\parse.rs:60:    let b_side\n", encoding="utf-8")
    (FIX / "mixed.txt").write_text(
        "unrelated.py:1: print(1)\n60:    let b_side = &bytes[b_prefix_start + 3..];\n",
        encoding="utf-8",
    )


def main() -> int:
    setup_fixtures()
    peal = str(PEAL)
    chime = str(CHIME)

    # ============================================================
    # 0. Baseline: victim still green
    # ============================================================
    rec(
        "baseline unittest",
        [sys.executable, "-m", "unittest", "tests.test_peal", "-q"],
        cwd=PEAL_WT,
        timeout=60,
        note="victim tests must still pass",
    )
    rec(
        "baseline --help",
        [peal, "--help"],
        cwd=PEAL_WT,
    )

    # ============================================================
    # 1. Gold kizu: advertised pipe vs chime FILE:LINE
    # ============================================================
    rg_bside = subprocess.run(
        ["rg", "-n", "let b_side", "src/git/parse.rs"],
        cwd=KIZU,
        capture_output=True,
        text=True,
    )
    rec(
        "kizu rg -n let b_side (raw)",
        ["rg", "-n", "let b_side", "src/git/parse.rs"],
        cwd=KIZU,
        note="single-file rg omits path; producer for advertised pipe",
    )
    rec(
        "kizu peal from rg -n let b_side",
        [peal, "--explain"],
        cwd=KIZU,
        stdin=rg_bside.stdout,
        note="advertised invert: recover FILE, scan, emit Some(bytes_to_path)",
    )
    rec(
        "kizu chime parse.rs:60",
        [chime, str(PARSE) + ":60", "--explain"],
        cwd=KIZU,
        note="chime names the locus; should rhyme with peal scan",
    )
    rec(
        "kizu peal argv parse.rs:60",
        [peal, str(PARSE) + ":60", "--explain"],
        cwd=KIZU,
    )
    rec(
        "kizu peal LINE:text from peal worktree no --repo",
        [peal, "--explain"],
        cwd=PEAL_WT,
        stdin=rg_bside.stdout,
        note="cwd is the wrong git; pin recovery should refuse",
    )
    rec(
        "kizu peal LINE:text --repo $KIZU from peal worktree",
        [peal, "--explain", "--repo", str(KIZU)],
        cwd=PEAL_WT,
        stdin=rg_bside.stdout,
    )
    rec(
        "kizu rg -nH let b_side | peal",
        [peal, "--explain"],
        cwd=KIZU,
        stdin=subprocess.run(
            ["rg", "-nH", "let b_side", "src/git/parse.rs"],
            cwd=KIZU,
            capture_output=True,
            text=True,
        ).stdout,
    )

    # first-locator seed: return None bag
    rg_none = subprocess.run(
        ["rg", "-n", "return None;", "src/git/parse.rs"],
        cwd=KIZU,
        capture_output=True,
        text=True,
    )
    rec(
        "kizu rg -n return None; (raw)",
        ["rg", "-n", "return None;", "src/git/parse.rs"],
        cwd=KIZU,
    )
    rec(
        "kizu peal from rg -n return None;",
        [peal, "--explain"],
        cwd=KIZU,
        stdin=rg_none.stdout,
        note="first locator is quoted-form :34, not unquoted :60",
    )
    rec(
        "kizu chime :60 filters return None stream",
        [chime, str(PARSE) + ":60", "--tsv"],
        cwd=KIZU,
        stdin=rg_none.stdout,
        note="chime FILTERS grep hits to the :60 stack",
    )
    rec(
        "kizu peal --hits on return None stream",
        [peal, "--hits", "--tsv"],
        cwd=KIZU,
        stdin=rg_none.stdout,
        note="--hits + first-locator seed = quoted arm filter, not :60",
    )
    rec(
        "kizu peal --same-as :60 on return None stream",
        [peal, "--same-as", str(PARSE) + ":60", "--explain"],
        cwd=KIZU,
        stdin=rg_none.stdout,
        note="--same-as overrides first locator; should scan like chime :60",
    )
    rec(
        "kizu peal --hits --same-as :60",
        [peal, "--same-as", str(PARSE) + ":60", "--hits", "--tsv"],
        cwd=KIZU,
        stdin=rg_none.stdout,
    )
    rec(
        "kizu peal :54 prefix (argv)",
        [peal, str(PARSE) + ":54", "--explain"],
        cwd=KIZU,
        note="shallower seed lists :60/:64 as deeper",
    )
    rec(
        "kizu peal :25 quoted exact",
        [peal, str(PARSE) + ":25", "--exact", "--explain"],
        cwd=KIZU,
    )

    # ============================================================
    # 2. sitbone dogfood
    # ============================================================
    rec(
        "sitbone peal argv PresenceArbiter:76",
        [peal, str(ARB) + ":76", "--explain"],
        cwd=SIT,
        note="guard isEnabled else arm vs body",
    )
    rec(
        "sitbone peal argv PresenceArbiter:80 (after guard)",
        [peal, str(ARB) + ":80", "--explain"],
        cwd=SIT,
    )
    rg_guard = subprocess.run(
        ["rg", "-n", "guard isEnabled", str(ARB)],
        cwd=SIT,
        capture_output=True,
        text=True,
    )
    rec(
        "sitbone rg -n guard isEnabled | peal",
        [peal, "--explain"],
        cwd=SIT,
        stdin=rg_guard.stdout,
    )
    rec(
        "sitbone chime :80",
        [chime, str(ARB) + ":80", "--explain"],
        cwd=SIT,
    )
    rec(
        "sitbone rg -n return PresenceReading | peal",
        [peal, "--explain"],
        cwd=SIT,
        stdin=subprocess.run(
            ["rg", "-n", "return PresenceReading", "Sources/SitboneCore/PresenceArbiter.swift"],
            cwd=SIT,
            capture_output=True,
            text=True,
        ).stdout,
        note="multiple returns; first locator is the seed",
    )
    rec(
        "sitbone rg -nH Logger.sensorsPresence | peal from sitbone root",
        [peal, "--explain"],
        cwd=SIT,
        stdin=subprocess.run(
            ["rg", "-nH", "Logger.sensorsPresence", "Sources"],
            cwd=SIT,
            capture_output=True,
            text=True,
        ).stdout,
    )

    # Logging.swift exists in four modules — same-ish lines?
    rec(
        "sitbone rg -n import Foundation Logging.swift",
        ["rg", "-n", "import Foundation", "Sources"],
        cwd=SIT,
    )

    # ============================================================
    # 3. Ambiguous FILE from LINE:text pins
    # ============================================================
    pin_denied = '13:    return "denied"\n'
    rec(
        "ambiguous twin nested.py LINE:text",
        [peal, "--exact", "--tsv"],
        cwd=FIX / "ambiguous",
        stdin=pin_denied,
        note="two files, same text at line 13 → must refuse, not guess",
    )
    rec(
        "ambiguous + FILE operand a.py",
        [peal, "--exact", "--tsv", str(FIX / "ambiguous/a.py")],
        cwd=FIX / "ambiguous",
        stdin=pin_denied,
        note="FILE operand should bind the pin",
    )
    rec(
        "unique nested in peal worktree LINE:text",
        [peal, "--exact", "--tsv"],
        cwd=PEAL_WT,
        stdin=pin_denied,
        note="claimed unique recovery of fixtures/nested.py",
    )
    rec(
        "identical swift guard LINE:text",
        [peal, "--explain"],
        cwd=FIX / "identline",
        stdin="3:    guard isEnabled else {\n4:        return\n",
        note="A.swift and B.swift identical",
    )

    # substring pin: "return None" is in the comment on decoy line 3
    rec(
        "substring pin return None at line 3",
        [peal, "--explain"],
        cwd=FIX / "substring",
        stdin="3:        return None\n",
        note="real.py has `return None`; decoy.py has it in a comment. substring `in` match.",
    )
    rec(
        "substring pin full unique line",
        [peal, "--explain"],
        cwd=FIX / "substring",
        stdin="3:        return None\n",
    )

    # ============================================================
    # 4. v2 recover FILE
    # ============================================================
    pin_v1 = "11:    let p = (bytes.len() - 5) / 2;\n"
    rec(
        "v1 pin recover src/parse.rs",
        [peal, "--explain"],
        cwd=FIX / "v1",
        stdin=pin_v1,
    )
    rec(
        "v2move pin recover after git mv",
        [peal, "--explain"],
        cwd=FIX / "v2move",
        stdin=pin_v1,
        note="file moved; (line,text) still unique at new path",
    )
    rec(
        "v2drift pin recover after +20 lines",
        [peal, "--explain"],
        cwd=FIX / "v2drift",
        stdin=pin_v1,
        note="same text now at line 31; pin still says 11 → should refuse",
    )
    rec(
        "v2keep extract-and-keep ambiguous",
        [peal, "--explain"],
        cwd=FIX / "v2keep",
        stdin=pin_v1,
        note="stub + extract both hold line 11",
    )
    rec(
        "v2drift with updated line number 31",
        [peal, "--explain"],
        cwd=FIX / "v2drift",
        stdin="31:    let p = (bytes.len() - 5) / 2;\n",
        note="human updated the pin; should recover",
    )

    # ============================================================
    # 5. seeds that match two files
    # ============================================================
    rec(
        "twostack rg -nH return | peal first seed",
        [peal, "--explain"],
        cwd=FIX / "twostack",
        stdin=subprocess.run(
            ["rg", "-nH", "return", "."],
            cwd=FIX / "twostack",
            capture_output=True,
            text=True,
        ).stdout,
        note="first locator seed; both files scanned",
    )
    rec(
        "twostack rg -l | peal --same-as alpha:3",
        [peal, "--same-as", str(FIX / "twostack/alpha.py") + ":3", "--explain"],
        cwd=FIX / "twostack",
        stdin="alpha.py\nbeta.py\n",
    )
    rec(
        "kizu rg -nH return None; across src/git | peal",
        [peal, "--explain"],
        cwd=KIZU,
        stdin=subprocess.run(
            ["rg", "-nH", "return None;", "src/git"],
            cwd=KIZU,
            capture_output=True,
            text=True,
        ).stdout,
        note="multi-file named locators; first seed; scan every named file",
    )

    # ============================================================
    # 6. empty stdin
    # ============================================================
    rec("empty stdin no argv", [peal], cwd=PEAL_WT, stdin="", note="piped empty")
    rec("newline stdin no argv", [peal], cwd=PEAL_WT, stdin="\n")
    rec("whitespace stdin", [peal], cwd=PEAL_WT, stdin="   \n\n")
    rec(
        "empty stdin with FILE:LINE argv",
        [peal, str(PEAL_WT / "fixtures/nested.py") + ":13", "--exact", "--tsv"],
        cwd=PEAL_WT,
        stdin="",
        note="piped empty but argv seed; want_stdin true",
    )
    rec(
        "no stdin tty-like (we always pipe in this harness)",
        [peal, str(PEAL_WT / "fixtures/nested.py") + ":13", "--exact", "--tsv"],
        cwd=PEAL_WT,
        stdin=None,
        note="subprocess stdin is not a tty either unless DEVNULL? None still closes",
    )
    rec(
        "argv seed stdin from /dev/null via empty bytes",
        [peal, str(PEAL_WT / "fixtures/nested.py") + ":13", "--exact", "--tsv"],
        cwd=PEAL_WT,
        stdin=b"",
    )

    # ============================================================
    # 7. binary
    # ============================================================
    rec(
        "binary stdin NUL+0xff",
        [peal, "--explain"],
        cwd=PEAL_WT,
        stdin=b"\x00\xffsecret\n",
        note="text-mode stdin decode",
    )
    rec(
        "binary stdin urandom 64",
        [peal],
        cwd=PEAL_WT,
        stdin=os.urandom(64),
    )
    rec(
        "NUL inside otherwise valid locator",
        [peal, "--explain"],
        cwd=KIZU,
        stdin=b"60:    let b_side\x00hidden\n",
    )
    rec(
        "binary .rs named as FILE operand",
        [peal, str(FIX / "binsrc/blob.rs") + ":2", "--explain"],
        cwd=FIX / "binsrc",
        note="errors=replace on file read",
    )
    rec(
        "binary .rs LINE:text pin recover",
        [peal, "--explain"],
        cwd=FIX / "binsrc",
        stdin="2:    let x = 1;\n",
    )

    # ============================================================
    # 8. huge rg streams
    # ============================================================
    huge_named = (FIX / "huge_stream.txt").read_text(encoding="utf-8")
    rec(
        "huge named locators 50k FILE:LINE",
        [peal, "--tsv"],
        cwd=FIX / "hugelist",
        stdin=huge_named,
        timeout=60,
        note="cli collects the whole stream then scans unique files",
    )
    huge_bare = (FIX / "huge_linetext.txt").read_text(encoding="utf-8")
    rec(
        "huge LINE:text 20k pins (pins[:16] recovery)",
        [peal, "--tsv"],
        cwd=FIX / "hugelist",
        stdin=huge_bare,
        timeout=60,
        note="recovery uses only first 16 pins; then scans recovered file",
    )
    rec(
        "pins16 truncated uniqueness: 17 unique pins, first 16 shared",
        [peal, "--explain"],
        cwd=FIX / "pins16",
        stdin="".join(
            [f"{i+1}:    let x{i} = {i};\n" for i in range(1, 17)]
            + ["18:    let UNIQUE_REAL = 1;\n"]
        ),
        note="line numbers: file is fn f(){ line1, then let x1 at line 2 ... UNIQUE at line 18",
    )
    # correct line mapping: line 1 = fn f() {, lines 2-17 = let x1..x16, line 18 = UNIQUE
    rec(
        "pins16 first 16 shared without unique pin",
        [peal, "--explain"],
        cwd=FIX / "pins16",
        stdin="".join(f"{i+1}:    let x{i} = {i};\n" for i in range(1, 17)),
        note="pins 2-17 are shared; ambiguous",
    )
    rec(
        "pins16 include UNIQUE_REAL as pin 17 (beyond [:16] if 16 shared first)",
        [peal, "--explain"],
        cwd=FIX / "pins16",
        stdin="".join(f"{i+1}:    let x{i} = {i};\n" for i in range(1, 17))
        + "18:    let UNIQUE_REAL = 1;\n",
        note="17th pin is unique but pins[:16] drops it → still ambiguous",
    )
    rec(
        "pins16 only UNIQUE_REAL pin",
        [peal, "--explain"],
        cwd=FIX / "pins16",
        stdin="18:    let UNIQUE_REAL = 1;\n",
    )

    # time pin recovery against kizu tree (many files)
    t0 = time.perf_counter()
    rec(
        "kizu pin-recovery timing let b_side",
        [peal, "--tsv"],
        cwd=KIZU,
        stdin=rg_bside.stdout,
        timeout=60,
        note="reads every git-listed source to match pins",
    )

    # ============================================================
    # 9. pins that are not LINE:text
    # ============================================================
    rec(
        "rg --json stdin",
        [peal, "--explain"],
        cwd=KIZU,
        stdin=(FIX / "json_rg.txt").read_text(),
        note="no JSON parser",
    )
    rec(
        "real rg --json starts_with | peal",
        [peal, "--explain"],
        cwd=KIZU,
        stdin=subprocess.run(
            ["rg", "--json", "starts_with", "src/git/parse.rs"],
            cwd=KIZU,
            capture_output=True,
            text=True,
        ).stdout,
    )
    rec(
        "vimgrep file:line:col:text",
        [peal, "--explain"],
        cwd=KIZU,
        stdin=(FIX / "vimgrep.txt").read_text(),
        note="GREP_RE accepts col; file is relative parse.rs path vs src/git/parse.rs",
    )
    rec(
        "rustc diagnostic arrow",
        [peal, "--explain"],
        cwd=KIZU,
        stdin=(FIX / "rustc.txt").read_text(),
    )
    rec(
        "rg -C context lines mixed with match",
        [peal, "--explain"],
        cwd=KIZU,
        stdin=(FIX / "context_rg.txt").read_text(),
        note="context uses dash; match uses colon",
    )
    rec(
        "ANSI color rg",
        [peal, "--explain"],
        cwd=KIZU,
        stdin=(FIX / "ansi.txt").read_bytes(),
    )
    rec(
        "bare LINE with empty text `60:`",
        [peal, "--explain"],
        cwd=KIZU,
        stdin="60:\n",
        note="empty here → any file with >=60 lines matches",
    )
    rec(
        "FILE:LINE only parse.rs:60 from kizu root",
        [peal, "--explain"],
        cwd=KIZU,
        stdin="parse.rs:60\n",
        note="basename does not resolve against repo root",
    )
    rec(
        "FILE:LINE only src/git/parse.rs:60",
        [peal, "--explain"],
        cwd=KIZU,
        stdin="src/git/parse.rs:60\n",
    )
    rec(
        "FILE:LINE only from kizu/src/git cwd",
        [peal, "--explain"],
        cwd=KIZU / "src/git",
        stdin="parse.rs:60\n",
    )
    rec(
        "url-shaped locator",
        [peal, "--explain"],
        cwd=PEAL_WT,
        stdin=(FIX / "url.txt").read_text(),
    )
    rec(
        "windows path locator",
        [peal, "--explain"],
        cwd=PEAL_WT,
        stdin=(FIX / "windows.txt").read_text(),
    )
    rec(
        "prose not a locator",
        [peal],
        cwd=PEAL_WT,
        stdin=(FIX / "not_locator.txt").read_text(),
    )
    rec(
        "mixed FILE:LINE + bare LINE:text",
        [peal, "--explain"],
        cwd=KIZU,
        stdin=(FIX / "mixed.txt").read_text(),
        note="any named file skips pin recovery; bare pin never gets a file",
    )
    rec(
        "rg -l parse.rs | peal no seed",
        [peal, "--explain"],
        cwd=KIZU,
        stdin="src/git/parse.rs\n",
    )
    rec(
        "colon in filename foo:bar.py:3",
        [peal, "--explain"],
        cwd=FIX / "colon",
        stdin="foo:bar.py:3:        return 'denied'\n",
    )
    rec(
        "CRLF locators",
        [peal, "--exact", "--tsv"],
        cwd=PEAL_WT,
        stdin='13:    return "denied"\r\n',
    )
    rec(
        "rg -n --column let b_side",
        [peal, "--explain"],
        cwd=KIZU,
        stdin=subprocess.run(
            ["rg", "-n", "--column", "let b_side", "src/git/parse.rs"],
            cwd=KIZU,
            capture_output=True,
            text=True,
        ).stdout,
    )

    # ============================================================
    # 10. chime vs peal on nested fixture (filter vs scan)
    # ============================================================
    nested = PEAL_WT / "fixtures/nested.py"
    rg_return = subprocess.run(
        ["rg", "-n", "return", str(nested)],
        cwd=PEAL_WT,
        capture_output=True,
        text=True,
    )
    rec(
        "fixture rg -n return nested.py (raw)",
        ["rg", "-n", "return", str(nested)],
        cwd=PEAL_WT,
    )
    rec(
        "chime FILE:LINE filters rg return stream",
        [chime, f"{nested}:8", "--tsv"],
        cwd=PEAL_WT,
        stdin=rg_return.stdout,
        note="chime default stdin = filter",
    )
    rec(
        "peal LINE:text from same rg (scan, not filter)",
        [peal, "--tsv"],
        cwd=PEAL_WT,
        stdin=rg_return.stdout,
        note="first return is None-arm :7; seed is that stack",
    )
    rec(
        "peal --hits same stream with --same-as :8",
        [peal, "--same-as", f"{nested}:8", "--hits", "--tsv"],
        cwd=PEAL_WT,
        stdin=rg_return.stdout,
    )
    rec(
        "peal scan --same-as :8 on rg -l nested",
        [peal, "--same-as", f"{nested}:8", "--tsv"],
        cwd=PEAL_WT,
        stdin=f"{nested}\n",
    )
    rec(
        "chime :8 scans the file (no stdin)",
        [chime, f"{nested}:8", "--tsv"],
        cwd=PEAL_WT,
    )
    rec(
        "peal :8 scans the file (no useful stdin)",
        [peal, f"{nested}:8", "--tsv"],
        cwd=PEAL_WT,
    )

    # guards.rs:11 gold
    rec(
        "guards.rs:11 argv peal",
        [peal, str(PEAL_WT / "fixtures/guards.rs") + ":11", "--exact", "--explain"],
        cwd=PEAL_WT,
    )
    rec(
        "guards LINE:text from peal wt",
        [peal, "--exact", "--explain"],
        cwd=PEAL_WT,
        stdin="11:    let p = (bytes.len() - 5) / 2;\n",
    )

    # ============================================================
    # 11. cwd walk refuse / --walk
    # ============================================================
    rec("no args no stdin (closed)", [peal], cwd=PEAL_WT, stdin="")
    rec(
        "DIR operand without --walk",
        [peal, str(PEAL_WT / "fixtures/nested.py") + ":13", str(PEAL_WT / "fixtures")],
        cwd=PEAL_WT,
    )
    rec(
        "--walk fixtures",
        [peal, str(PEAL_WT / "fixtures/nested.py") + ":13", "--walk", str(PEAL_WT / "fixtures"), "--exact", "--tsv"],
        cwd=PEAL_WT,
    )
    rec(
        "DIR as --repo for pins still no walk of DIR operand",
        [peal, "--repo", str(KIZU), "--explain"],
        cwd=PEAL_WT,
        stdin=rg_bside.stdout,
    )

    # preamble / empty cond_key
    rec(
        "preamble line 1 no path-condition",
        [peal, str(FIX / "preamble/mod.py") + ":1", "--explain"],
        cwd=FIX / "preamble",
    )

    # --diff without seed
    rec(
        "--diff stdin without seed",
        [peal, "--diff", "-"],
        cwd=PEAL_WT,
        stdin="diff --git a/x b/x\n--- a/x\n+++ b/x\n@@ -1 +1 @@\n-a\n+b\n",
    )

    write_transcript()

    # compact index
    idx = []
    for i, c in enumerate(cases, 1):
        tb = "TRACE" if ("Traceback" in (c["stderr"] or "") or "Error" in (c["stderr"] or "")[:80] and c["rc"] not in (0, 1, 2, 3)) else ""
        idx.append(
            f"{i:03d} rc={c['rc']:<3} {c['elapsed']:<7} {c['name']} {tb}"
        )
    (ROOT / "index.txt").write_text("\n".join(idx) + "\n", encoding="utf-8")
    print(f"wrote {TRANSCRIPT} cases={len(cases)}")
    print("\n".join(idx))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
