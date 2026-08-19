#!/usr/bin/env python3
"""DESTROYER battery for beck — first pipeline stage that produced this byte.

No victim rewrites. Writes /tmp/destroy-beck/{transcript.txt,fixtures/,logs/}.
"""
from __future__ import annotations

import json
import os
import subprocess
import sys
import time
from pathlib import Path

BECK = os.environ.get(
    "BECK",
    "/Users/annenpolka/.grok/worktrees/annenpolka-brrr/subagent-01a01bad-eb91-7d80-9aa0-1108ac34ccbe/beck",
)
FACET = os.environ.get(
    "FACET",
    "/Users/annenpolka/.grok/worktrees/annenpolka-brrr/subagent-01a01bd4-9291-7c63-9bf2-7d8a55cd1699/facet",
)
ROOT = Path(os.environ.get("DESTROY_ROOT", "/tmp/destroy-beck"))
FIX = ROOT / "fixtures"
LOGS = ROOT / "logs"
KIZU = os.environ.get("KIZU", "/Users/annenpolka/ghq/github.com/annenpolka/kizu")
SIT = os.environ.get("SITBONE", "/Users/annenpolka/ghq/github.com/annenpolka/sitbone")
CARGO = FIX / "kizu-cargo.json"

transcript: list[str] = []


def log(msg: str = "") -> None:
    print(msg, flush=True)
    transcript.append(msg)


def banner(title: str) -> None:
    log()
    log("=" * 72)
    log(title)
    log("=" * 72)


def ensure_dirs() -> None:
    FIX.mkdir(parents=True, exist_ok=True)
    LOGS.mkdir(parents=True, exist_ok=True)


def ensure_cargo() -> Path:
    if CARGO.is_file() and CARGO.stat().st_size > 1000:
        return CARGO
    manifest = Path(KIZU) / "Cargo.toml"
    p = subprocess.run(
        ["cargo", "metadata", "--format-version", "1", "--offline", "--manifest-path", str(manifest)],
        capture_output=True,
        timeout=60,
    )
    if p.returncode != 0:
        log("cargo metadata failed: " + p.stderr.decode("utf-8", "replace")[:400])
        raise SystemExit(2)
    CARGO.write_bytes(p.stdout)
    return CARGO


def run_beck(
    args: list[str],
    *,
    stdin: bytes | None = None,
    timeout: float = 30.0,
    env: dict[str, str] | None = None,
) -> tuple[int, str, str, float]:
    cmd = [BECK, *args]
    t0 = time.perf_counter()
    try:
        p = subprocess.run(
            cmd,
            input=stdin,
            capture_output=True,
            timeout=timeout,
            env=env,
        )
        elapsed = time.perf_counter() - t0
        out = p.stdout.decode("utf-8", errors="replace")
        err = p.stderr.decode("utf-8", errors="replace")
        return p.returncode, out, err, elapsed
    except subprocess.TimeoutExpired as e:
        elapsed = time.perf_counter() - t0
        out = (e.stdout or b"").decode("utf-8", errors="replace")
        err = (e.stderr or b"").decode("utf-8", errors="replace") + f"\nTIMEOUT after {timeout}s"
        return 124, out, err, elapsed


def run_facet(args: list[str], stdin: bytes | None = None, timeout: float = 30.0) -> tuple[int, str, str, float]:
    t0 = time.perf_counter()
    p = subprocess.run([FACET, *args], input=stdin, capture_output=True, timeout=timeout)
    elapsed = time.perf_counter() - t0
    return (
        p.returncode,
        p.stdout.decode("utf-8", errors="replace"),
        p.stderr.decode("utf-8", errors="replace"),
        elapsed,
    )


def show(name: str, rc: int, out: str, err: str, elapsed: float, cap: int = 40) -> None:
    log(f"$ {name}")
    body = out.rstrip("\n")
    if body:
        lines = body.splitlines()
        for ln in lines[:cap]:
            log(ln)
        if len(lines) > cap:
            log(f"  … and {len(lines) - cap} more stdout lines")
    if err.strip():
        elines = err.rstrip("\n").splitlines()
        for ln in elines[:16]:
            log("stderr: " + ln)
        if len(elines) > 16:
            log(f"  … and {len(elines) - 16} more stderr lines")
    log(f"# rc={rc}  elapsed={elapsed:.3f}s")


def show_json(name: str, rc: int, out: str, err: str, elapsed: float) -> dict | None:
    show(name, rc, out, err, elapsed, cap=80)
    try:
        return json.loads(out)
    except json.JSONDecodeError:
        log("(stdout not json)")
        return None


def save(name: str, text: str | bytes) -> Path:
    p = FIX / name
    p.parent.mkdir(parents=True, exist_ok=True)
    if isinstance(text, bytes):
        p.write_bytes(text)
    else:
        p.write_text(text if text.endswith("\n") else text + "\n", encoding="utf-8")
    return p


def split_probe() -> None:
    ns: dict = {}
    src = Path(BECK).read_text(encoding="utf-8")
    exec(compile(src, BECK, "exec"), ns)
    split = ns["split_pipeline"]
    cases = [
        "echo $(foo | bar) | baz",
        "{ echo a | cat; } | wc",
        "{ printf kizu | tr k K; } | cat",
        "echo a | | cat",
        "echo a |",
        "| echo a",
        "echo a || echo b | cat",
        "git status 2>&1 | cat",
        "git 2>&1 status | cat",
        "git -C /tmp 2>&1 status | cat",
        "cd /tmp && echo a | cat",
        "bash -c \"echo a | sed s/a/b/\" | cat",
        "cat <(echo a | tr a b) | cat",
        "printf hi |& cat",
        "foo | bar |",
        "",
    ]
    for s in cases:
        try:
            st = split(s)
            log(f"split OK  {s!r} => {st}")
        except Exception as e:
            log(f"split ERR {s!r} => {type(e).__name__}: {e}")


def naive_tee_git() -> None:
    tee0 = FIX / "tee0.out"
    tee1 = FIX / "tee1.out"
    p = subprocess.run(
        f"git -C /tmp status | tee {tee0} | cat > {tee1}",
        shell=True,
        capture_output=True,
    )
    b0 = tee0.read_bytes() if tee0.exists() else b""
    b1 = tee1.read_bytes() if tee1.exists() else b""
    g0 = b"fatal: not a git repository" in b0
    g1 = b"fatal: not a git repository" in b1
    log(f"naive tee git -C /tmp status | tee s0 | cat")
    log(f"  shell_stderr {p.stderr.decode('utf-8','replace').rstrip()!r}")
    log(f"  tee0_bytes={len(b0)} tee1_bytes={len(b1)} grep0={g0} grep1={g1}")
    log("  NAIVE_TEE_MISS" if not (g0 or g1) else "  NAIVE_TEE_HIT")


def write_trace_dirs() -> None:
    d = FIX / "tee-dir"
    d.mkdir(exist_ok=True)
    (d / "0.argv").write_text("git -C /tmp status\n")
    (d / "0.stdout").write_bytes(b"")
    (d / "1.argv").write_text("cat\n")
    (d / "1.stdout").write_bytes(b"")
    (d / "pipeline.txt").write_text("git -C /tmp status | cat\n")
    d2 = FIX / "tee-stderr-dir"
    d2.mkdir(exist_ok=True)
    (d2 / "0.argv").write_text("git -C /tmp status\n")
    (d2 / "0.stdout").write_bytes(b"")
    (d2 / "0.stderr").write_text(
        "fatal: not a git repository (or any of the parent directories): /tmp\n"
    )
    (d2 / "1.argv").write_text("cat\n")
    (d2 / "1.stdout").write_bytes(b"")


def main() -> int:
    ensure_dirs()
    cargo = ensure_cargo()
    log(f"beck={BECK}")
    log(f"facet={FACET}")
    log(f"cargo_bytes={cargo.stat().st_size}")
    raw = cargo.read_bytes()
    log(f"kizu@0.7.0 count={raw.count(b'kizu@0.7.0')} first={raw.find(b'kizu@0.7.0')}")
    log(
        "notify-debouncer-full@0.7.0 count="
        f"{raw.count(b'notify-debouncer-full@0.7.0')} first={raw.find(b'notify-debouncer-full@0.7.0')}"
    )
    log(f"0.7.0 count={raw.count(b'0.7.0')} first={raw.find(b'0.7.0')}")
    log(f"kizu first={raw.find(b'kizu')}")

    banner("0. victim still green")
    rc, out, err, el = run_beck(["--selftest"], timeout=20)
    show("beck --selftest", rc, out, err, el)
    rc, out, err, el = run_beck(["--version"])
    show("beck --version", rc, out, err, el)

    banner("1. git fatal never enters the pipe + tee|grep skeptic")
    naive_tee_git()
    rc, out, err, el = run_beck(
        ["--quiet", "--json", "--needle", "fatal: not a git repository", "--sh", "git -C /tmp status | cat | cat"]
    )
    doc = show_json("beck --quiet --json --needle fatal --sh 'git -C /tmp status | cat | cat'", rc, out, err, el)
    save("git-fatal.json", out)
    rc, out, err, el = run_beck(
        ["--quiet", "--needle", "fatal: not a git repository", "--sh", "git -C /tmp status | cat | cat"]
    )
    show("beck human git fatal", rc, out, err, el)

    banner("2. wrap: sed prefix vs tee exact (gold)")
    rc, out, err, el = run_beck(
        [
            "--quiet",
            "--json",
            "--needle",
            "fatal: not a git repository",
            "--sh",
            "printf '%s\\n' 'not a git repository' | sed 's/^/fatal: /' | cat",
        ]
    )
    show_json("beck wrap sed", rc, out, err, el)
    save("wrap-sed.json", out)

    banner("3. fd confusion")
    rc, out, err, el = run_beck(
        ["--quiet", "--json", "--needle", "fatal: not a git repository", "--sh", "git -C /tmp status 2>&1 | cat"]
    )
    show_json("trailing 2>&1", rc, out, err, el)
    rc, out, err, el = run_beck(
        ["--quiet", "--json", "--needle", "fatal: not a git repository", "--sh", "git -C /tmp status |& cat"]
    )
    show_json("|& merge", rc, out, err, el)
    rc, out, err, el = run_beck(
        ["--quiet", "--json", "--needle", "fatal: not a git repository", "--sh", "git -C /tmp 2>&1 status | cat"]
    )
    show_json("mid-command 2>&1 (not trailing peel)", rc, out, err, el)
    save("mid-2gt1.json", out)
    both = r'python3 -c "import sys; sys.stdout.write(\"fatal: not a git repository\n\"); sys.stderr.write(\"fatal: not a git repository\n\")" | cat'
    rc, out, err, el = run_beck(["--quiet", "--json", "--needle", "fatal: not a git repository", "--sh", both])
    show_json("same needle on stdout AND stderr of stage 0", rc, out, err, el)
    rc, out, err, el = run_beck(
        [
            "--quiet",
            "--json",
            "--needle",
            "boom",
            "--sh",
            r'true | python3 -c "import sys; sys.stderr.write(\"boom\n\")" | cat',
        ]
    )
    show_json("later-stage unpiped stderr", rc, out, err, el)

    banner("4. $() / bash -c / {} / process-substitution wrappers")
    split_probe()
    rc, out, err, el = run_beck(
        ["--quiet", "--json", "--needle", "Kizu", "--sh", "echo $(printf kizu | tr k K) | cat"]
    )
    show_json("$() inner pipeline is one outer stage", rc, out, err, el)
    save("dollar.json", out)
    rc, out, err, el = run_beck(
        ["--quiet", "--json", "--needle", "b", "--sh", "bash -c 'printf a | sed s/a/b/' | cat"]
    )
    show_json("bash -c inner pipeline not walked", rc, out, err, el)
    rc, out, err, el = run_beck(
        ["--quiet", "--json", "--needle", "Kizu", "--sh", "{ printf kizu | tr k K; } | cat"]
    )
    show_json("{ printf kizu | tr k K; } claimed one outer stage", rc, out, err, el)
    save("brace.json", out)
    rc, out, err, el = run_beck(
        ["--quiet", "--json", "--needle", "b", "--sh", "cat <(printf a | tr a b) | cat"]
    )
    show_json("process substitution inner not walked", rc, out, err, el)

    banner("5. binary needles")
    bin_sh = r'python3 -c "import sys; sys.stdout.buffer.write(b\"aaa\x00bbb\xffccc\")" | cat'
    rc, out, err, el = run_beck(["--quiet", "--json", "--span", "3:7", "--sh", bin_sh])
    show_json("--span 3:7 of NUL+bbb", rc, out, err, el)
    save("binary-span.json", out)
    rc, out, err, el = run_beck(["--quiet", "--span", "3:7", "--sh", bin_sh])
    show("human --span binary", rc, out, err, el)
    # CLI --needle cannot carry NUL (C argv). Span is the door.
    rc, out, err, el = run_beck(["--quiet", "--save", str(FIX / "bin.json"), "--span", "3:7", "--sh", bin_sh])
    show("save binary trace", rc, out, err, el)
    rc, out, err, el = run_beck(["--quiet", "--span", "3:7", "--trace", str(FIX / "bin.json")])
    show("replay binary trace", rc, out, err, el)
    live = (FIX / "bin-live.txt")
    # compare encodings
    doc = json.loads((FIX / "bin.json").read_text())
    log(f"trace stdout encoding: {doc['stages'][0]['stdout']}")

    banner("6. overlapping stages (carry lie / remint)")
    rc, out, err, el = run_beck(["--quiet", "--json", "--needle", "hi", "--sh", "printf hi | echo hi"])
    show_json("printf hi | echo hi  (echo remints; later claims carry)", rc, out, err, el)
    save("echo-remint.json", out)
    rc, out, err, el = run_beck(["--quiet", "--json", "--needle", "hi", "--sh", "true | echo hi"])
    show_json("true | echo hi  (honest later mint)", rc, out, err, el)
    rc, out, err, el = run_beck(
        [
            "--quiet",
            "--json",
            "--needle",
            "kizu@0.7.0",
            "--sh",
            'printf kizu | python3 -c "import sys; print(sys.stdin.read().strip()); print(\\"0.7.0\\")" | python3 -c "import sys; a=sys.stdin.read().split(); print(a[0]+\\"@\\"+a[1])"',
        ]
    )
    show_json("pieces from two earlier stages + glue @", rc, out, err, el)
    rc, out, err, el = run_beck(["--quiet", "--json", "--needle", "aaaa", "--sh", "printf aaa | sed 's/aaa/aaaa/'"])
    show_json("greedy overlap aaa -> aaaa", rc, out, err, el)

    banner("7. JSON coincidence kizu@0.7.0 vs notify-debouncer-full (facet hole)")
    sh = f"cat {cargo} | jq -r '.packages[] | select(.name==\"kizu\") | .name + \"@\" + .version'"
    rc, out, err, el = run_beck(["--quiet", "--timeout", "30", "--json", "--needle", "kizu@0.7.0", "--sh", sh], timeout=40)
    doc = show_json("beck cargo|jq construct kizu@0.7.0", rc, out, err, el)
    save("kizu-at.json", out)
    if doc:
        log("pieces:")
        for p in doc.get("pieces") or []:
            log(f"  {p}")
        pl = doc.get("payload")
        log(f"payload (longest piece): {pl}")
    rc, out, err, el = run_beck(
        [
            "--quiet",
            "--timeout",
            "30",
            "--json",
            "--needle",
            "0.7.0",
            "--sh",
            f"cat {cargo} | jq -r '.packages[] | select(.name==\"kizu\") | .version'",
        ],
        timeout=40,
    )
    show_json("beck cargo|jq extract 0.7.0 (first find)", rc, out, err, el)
    rc, out, err, el = run_beck(
        ["--quiet", "--timeout", "30", "--json", "--needle", "notify-debouncer-full@0.7.0", "--sh", f"cat {cargo} | cat"],
        timeout=40,
    )
    show_json("beck exact notify-debouncer-full@0.7.0 already in cargo .id", rc, out, err, el)
    rc, out, err, el = run_beck(
        ["--quiet", "--timeout", "30", "--json", "--min-payload", "8", "--needle", "kizu@0.7.0", "--sh", sh],
        timeout=40,
    )
    show_json("--min-payload 8 turns wrap into mint (no piece >= 8)", rc, out, err, el)
    save("kizu-at-min8.json", out)

    if Path(FACET).is_file():
        cargo_bytes = cargo.read_bytes()
        rc, out, err, el = run_facet(["--quiet", "-n", "kizu@0.7.0"], stdin=cargo_bytes, timeout=20)
        show("facet -n kizu@0.7.0 < cargo", rc, out, err, el)
        save("facet-kizu.txt", out)
        rc, out, err, el = run_facet(["--quiet", "-n", "notify-debouncer-full@0.7.0"], stdin=cargo_bytes, timeout=20)
        show("facet -n notify-debouncer-full@0.7.0", rc, out, err, el)
        rc, out, err, el = run_facet(["--quiet", "-n", "0.7.0"], stdin=cargo_bytes, timeout=20)
        show("facet -n 0.7.0 occupancy", rc, out, err, el)

    tiny = 'printf "%s\\n" "{\\"name\\":\\"kizu\\",\\"version\\":\\"0.7.0\\"}" | jq -r ".name + \\"@\\" + .version"'
    rc, out, err, el = run_beck(["--quiet", "--json", "--line", "1", "--sh", tiny])
    show_json("tiny JSON (no sibling crate) — glue @ is honest", rc, out, err, el)
    save("tiny-jq.json", out)
    for m in (1, 4, 8):
        rc, out, err, el = run_beck(["--quiet", "--json", "--min-payload", str(m), "--line", "1", "--sh", tiny])
        doc = json.loads(out) if rc in (0, 1) and out.strip().startswith("{") else {}
        kind = (doc.get("producer") or {}).get("kind")
        pieces = [(p["kind"], p["text"]) for p in doc.get("pieces") or []]
        log(f"tiny min-payload={m} kind={kind} pieces={pieces} rc={rc}")

    banner("8. empty stages")
    rc, out, err, el = run_beck(["--quiet", "--needle", "x", "--sh", "echo a | | cat"])
    show("empty mid stage  echo a | | cat", rc, out, err, el)
    rc, out, err, el = run_beck(["--quiet", "--json", "--needle", "hi", "--sh", "printf hi |"])
    show_json("trailing pipe silently dropped", rc, out, err, el)
    rc, out, err, el = run_beck(["--quiet", "--needle", "x", "--sh", "| echo a"])
    show("leading pipe", rc, out, err, el)
    rc, out, err, el = run_beck(["--quiet", "--needle", "x", "--sh", ""])
    show("empty --sh '' is usage (falsy), not empty-pipeline", rc, out, err, el)
    rc, out, err, el = run_beck(["--quiet", "--json", "--needle", "hi", "--sh", "true | true"])
    show_json("true | true needle miss", rc, out, err, el)
    rc, out, err, el = run_beck(["--quiet", "--span", "0:0", "--sh", "printf hi | cat"])
    show("empty span 0:0", rc, out, err, el)

    banner("9. --run vs recorded trace")
    rc, out, err, el = run_beck(
        ["--quiet", "--save", str(FIX / "fatal.json"), "--needle", "fatal: not a git repository", "--sh", "git -C /tmp status | cat"]
    )
    save("fatal-live.txt", out)
    show("save live fatal", rc, out, err, el)
    rc, out, err, el = run_beck(["--quiet", "--needle", "fatal: not a git repository", "--trace", str(FIX / "fatal.json")])
    save("fatal-replay.txt", out)
    show("replay fatal json", rc, out, err, el)
    live_t = (FIX / "fatal-live.txt").read_text()
    replay_t = (FIX / "fatal-replay.txt").read_text()
    log("json trace MATCH" if live_t == replay_t else "json trace DIFF")
    write_trace_dirs()
    rc, out, err, el = run_beck(
        ["--quiet", "--json", "--needle", "fatal: not a git repository", "--trace", str(FIX / "tee-dir")]
    )
    show_json("trace dir of tee dumps (no stderr files) = skeptic miss", rc, out, err, el)
    rc, out, err, el = run_beck(
        ["--quiet", "--json", "--needle", "fatal: not a git repository", "--trace", str(FIX / "tee-stderr-dir")]
    )
    show_json("trace dir with 0.stderr present", rc, out, err, el)
    rc, out, err, el = run_beck(["--quiet", "--json", "--needle", "hello world", "--run", "--", "printf", "%s\\n", "hello world", "+", "cat"])
    show_json("--run + strips quotes: printf %s\\n hello world", rc, out, err, el)
    save("run-plus-quotes.json", out)
    rc, out, err, el = run_beck(["--quiet", "--json", "--needle", "hello world", "--sh", "printf '%s\\n' 'hello world' | cat"])
    show_json("--sh keeps quotes, mints 'hello world'", rc, out, err, el)
    # unquoted pipe: the *shell* steals | ; recreate via bash -c
    p = subprocess.run(
        [BECK, "--quiet", "--json", "--needle", "hi", "--run", "--", "printf", "hi", "|", "cat"],
        capture_output=True,
        timeout=15,
    )
    log("$ beck --run -- printf hi | cat   # as argv with literal | (not shell-split)")
    log(p.stdout.decode("utf-8", "replace").rstrip())
    if p.stderr:
        log("stderr: " + p.stderr.decode("utf-8", "replace")[:400])
    log(f"# rc={p.returncode}")
    p = subprocess.run(
        f"{BECK} --quiet --json --needle hi --run -- printf hi | cat",
        shell=True,
        capture_output=True,
        timeout=15,
    )
    log("$ sh -c 'beck --run -- printf hi | cat'  # shell owns the pipe")
    log("stdout (after cat): " + p.stdout.decode("utf-8", "replace").rstrip()[:500])
    log(f"# rc={p.returncode}  (beck recorded one stage; cat ate the report)")
    rc, out, err, el = run_beck(
        ["--quiet", "--json", "--needle", "fatal: not a git repository", "--run", "--", "git -C /tmp status | cat"]
    )
    show_json("--run -- 'git … | cat' as one rest arg ≡ --sh", rc, out, err, el)

    banner("10. dogfood kizu / sitbone / stdin / prefix / ANSI")
    if (Path(KIZU) / ".git").is_dir():
        rc, out, err, el = run_beck(
            ["--quiet", "--cwd", KIZU, "--json", "--needle", "release: v0.7.0", "--sh", "git log --oneline | rg release | head -5"],
            timeout=20,
        )
        show_json("kizu git log | rg release | head", rc, out, err, el)
        save("kizu-log.json", out)
    if (Path(SIT) / ".git").is_dir():
        rc, out, err, el = run_beck(
            ["--quiet", "--cwd", SIT, "--json", "--needle", "dual-threshold hysteresis", "--sh", "git log --oneline | rg hysteresis | cat"],
            timeout=20,
        )
        show_json("sitbone git log | rg hysteresis", rc, out, err, el)
        save("sitbone.json", out)
    rc, out, err, el = run_beck(
        ["--quiet", "--json", "--stdin", "--needle", "hello-from-outside", "--sh", "cat | cat"],
        stdin=b"hello-from-outside\n",
    )
    show_json("stdin carry", rc, out, err, el)
    rc, out, err, el = run_beck(
        ["--quiet", "--json", "--prefix", "--needle", "fatal:", "--sh", "git -C /tmp status | cat"]
    )
    show_json("--prefix fatal:", rc, out, err, el)
    rc, out, err, el = run_beck(
        [
            "--quiet",
            "--json",
            "--needle",
            "hello",
            "--sh",
            r'python3 -c "import sys; sys.stdout.buffer.write(b\"hel\x1b[31mlo\n\")" | cat',
        ]
    )
    show_json("ANSI inserted inside needle -> MISS", rc, out, err, el)
    rc, out, err, el = run_beck(
        [
            "--quiet",
            "--json",
            "--line",
            "1",
            "--sh",
            r'printf "%s\n" "9349dc5 release: v0.7.0" | rg --color=always release',
        ]
    )
    show_json("--line 1 on rg --color=always (ANSI glue wrap)", rc, out, err, el)
    save("ansi-line.json", out)

    banner("11. follow-up: victim unpatched")
    rc, out, err, el = run_beck(["--selftest"], timeout=20)
    show("beck --selftest after battery", rc, out, err, el)

    text = "\n".join(transcript) + "\n"
    (ROOT / "transcript.txt").write_text(text, encoding="utf-8")
    (ROOT / "followup.txt").write_text(
        "Victim not rewritten. selftest still 14/14 after the battery.\n"
        "Gold: unpiped git stderr, tiny JSON wrap glue @, trailing 2>&1 fd, kizu git log mint.\n"
        "Holes: brace-group split, $() inner, facet JSON coincidence, --run quote strip, later=carry remint, min-payload 8 mint, tee-dir miss.\n",
        encoding="utf-8",
    )
    log()
    log(f"wrote {ROOT / 'transcript.txt'}")
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except KeyboardInterrupt:
        raise SystemExit(130)
