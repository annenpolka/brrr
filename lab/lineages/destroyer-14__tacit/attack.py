#!/usr/bin/env python3
"""Adversarial battery against tacit TACIT/SHADOW/OVERRIDE/BOUND/BLAST/FOSSIL.

Does not rewrite tacit. Writes fixtures, runs the victim, records transcripts.
"""
from __future__ import annotations

import importlib.util
import os
import shutil
import subprocess
import sys
import textwrap
from pathlib import Path

ROOT = Path("/tmp/destroy-tacit")
FIX = ROOT / "fixtures"
LOG = ROOT / "logs"
REPOS = ROOT / "repos"
TACIT = Path(
    "/Users/annenpolka/.grok/worktrees/annenpolka-brrr/"
    "subagent-01a01b83-5900-7902-9188-72c70d715bf7/tacit"
)

for d in (FIX, LOG, REPOS):
    d.mkdir(parents=True, exist_ok=True)


def write(path: Path, body: str) -> Path:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(textwrap.dedent(body).lstrip("\n"))
    return path


def run(args: list[str], cwd: Path | None = None) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        args,
        cwd=str(cwd) if cwd else None,
        text=True,
        capture_output=True,
    )


def tacit(*args: str, cwd: Path | None = None) -> subprocess.CompletedProcess[str]:
    return run([str(TACIT), *args], cwd=cwd)


def banner(title: str) -> None:
    print()
    print("=" * 72)
    print(title)
    print("=" * 72)


def show(name: str, proc: subprocess.CompletedProcess[str]) -> str:
    out = proc.stdout.rstrip("\n")
    err = proc.stderr.rstrip("\n")
    print(f"--- {name}  rc={proc.returncode} ---")
    if out:
        print(out)
    if err:
        print("STDERR:", err)
    return out


def git_init(repo: Path) -> None:
    if repo.exists():
        shutil.rmtree(repo)
    repo.mkdir(parents=True)
    run(["git", "init", "-q", "-b", "main"], cwd=repo)
    run(["git", "config", "user.name", "destroyer"], cwd=repo)
    run(["git", "config", "user.email", "d@x"], cwd=repo)
    run(["git", "config", "commit.gpgsign", "false"], cwd=repo)


def git_commit(repo: Path, msg: str) -> None:
    run(["git", "add", "-A"], cwd=repo)
    run(["git", "commit", "-q", "-m", msg], cwd=repo)


def load_tacit():
    import importlib.machinery

    loader = importlib.machinery.SourceFileLoader("tacit_mod", str(TACIT))
    spec = importlib.util.spec_from_loader("tacit_mod", loader)
    mod = importlib.util.module_from_spec(spec)
    sys.modules["tacit_mod"] = mod
    loader.exec_module(mod)
    return mod


# ---------------------------------------------------------------------------
# 1. keyword vs positional
# ---------------------------------------------------------------------------
write(
    FIX / "kwpos" / "kwpos.py",
    """
    def f(a=1, b=2, c=3):
        pass

    def splat(*args, timeout=30):
        pass

    def kwargs(timeout=30, **kw):
        pass

    def kwonly(*, timeout=30):
        pass

    def posonly(a, /, timeout=30):
        pass

    def greet(name, greeting="hi", times=1):
        pass

    def use():
        f()
        f(1)
        f(1, 2)
        f(b=2)
        f(1, c=3)
        f(c=3, a=9)
        splat()
        splat(1)
        splat(1, 2, 3)
        kwargs()
        kwargs(timeout=30)
        kwargs(**{"timeout": 30})
        kwonly()
        kwonly(timeout=30)
        posonly(1)
        posonly(1, 30)
        greet("x")
        greet("x", "yo")
        greet("x", times=2)
        greet("x", greeting="hi", times=1)
        greet("yo")  # name positional, greeting TACIT
    """,
)

write(
    FIX / "kwpos" / "unlabeled.swift",
    """
    public func paint(_ color: String, opacity: Double = 1.0, blend: String = "normal") {}
    public func mix(from start: Double = 0, to end: Double = 1) {}
    public func labeled(presentThreshold: Double = 0.45) {}
    public final class PresenceArbiter {
        public init(sensors: [String], presentThreshold: Double = 0.45, emaAlpha: Double = 0.3) {}
    }
    public func seed() {
        paint("red")
        paint("red", opacity: 0.5)
        paint("red", 0.5)
        paint("red", opacity: 1.0, blend: "normal")
        mix(from: 0)
        mix(to: 1)
        labeled(0.50)
        labeled(presentThreshold: 0.50)
        labeled(presentThreshold: 0.45)
        _ = PresenceArbiter(["camera"])
        _ = PresenceArbiter(["camera"], 0.50)
        _ = PresenceArbiter(sensors: ["camera"], 0.50)
        _ = PresenceArbiter(sensors: ["camera"], presentThreshold: 0.50)
        _ = PresenceArbiter(sensors: ["camera"])
    }
    """,
)

write(
    FIX / "kwpos" / "retry.ts",
    """
    export function retry(fn: Function, attempts: number = 3, delay: number = 100) {
      return fn();
    }
    retry(() => 1);
    retry(() => 1, 3);
    retry(() => 1, 5);
    retry(() => 1, 5, 200);
    retry(() => 1, delay = 200);
    """,
)


# ---------------------------------------------------------------------------
# 2. multiline calls
# ---------------------------------------------------------------------------
write(
    FIX / "multiline" / "multi.swift",
    """
    public final class PresenceArbiter {
        public init(
            sensors: [String],
            presentThreshold: Double = 0.45,
            absentThreshold: Double = 0.35,
            emaAlpha: Double = 0.3
        ) {}
    }
    public func seed() {
        let a = PresenceArbiter(
            sensors: ["camera"],
            presentThreshold: 0.45
        )
        let b = PresenceArbiter(
            sensors: ["camera"],
            presentThreshold: // the documented default
                0.45
        )
        let c = PresenceArbiter(
            sensors: ["camera"]
            // presentThreshold: 0.45
        )
        let d = PresenceArbiter(
            sensors: ["camera"],
            presentThreshold:
            0.50
        )
        let e = PresenceArbiter(
            sensors: ["camera"],
            emaAlpha: 1.0,
        )
    }
    """,
)

write(
    FIX / "multiline" / "multi.py",
    """
    def greet(name, greeting="hi", times=1):
        pass

    greet(
        "x",
        "yo",
    )
    greet(
        "x",
        # greeting="yo"
    )
    greet(
        "x",
        greeting=  # restated default
            "hi",
    )
    """,
)


# ---------------------------------------------------------------------------
# 3. comments that look like args
# ---------------------------------------------------------------------------
write(
    FIX / "comments" / "residue.swift",
    """
    public final class PresenceArbiter {
        public init(sensors: [String], presentThreshold: Double = 0.45) {}
    }
    // comment residue must not be a call: PresenceArbiter(SitboneCore)
    // PresenceArbiter(sensors: ["camera"], presentThreshold: 0.50)
    public func seed() {
        let a = PresenceArbiter(sensors: ["camera"]) // presentThreshold: 0.45
        let b = PresenceArbiter(/* presentThreshold: 0.45 */ sensors: ["camera"])
        let c = PresenceArbiter(sensors: ["camera"] /* presentThreshold: 0.50 */)
        let s = "PresenceArbiter(sensors: [\\"x\\"], presentThreshold: 0.99)"
    }
    """,
)

write(
    FIX / "comments" / "residue.py",
    """
    def greet(name, greeting="hi", times=1):
        pass

    # greet("x", greeting="yo")
    greet("x")  # greeting="hi"
    greet("x", greeting="hi")  # restated
    s = 'greet("z", greeting="yo")'
    """,
)


# ---------------------------------------------------------------------------
# 4. nested Thresholds()
# ---------------------------------------------------------------------------
write(
    FIX / "nested" / "nested.swift",
    """
    public struct Thresholds {
        public init(driftDelay: Double = 15, awayDelay: Double = 90) {}
    }
    public struct SessionProfile {
        public init(
            name: String,
            colorHue: Double = 0.45,
            thresholds: Thresholds = Thresholds()
        ) {}
    }
    public struct PinProfile {
        public init(
            name: String,
            thresholds: Thresholds = Thresholds(driftDelay: 20)
        ) {}
    }
    public struct DotInit {
        public init(thresholds: Thresholds = .init()) {}
    }
    public func seed() {
        let a = SessionProfile(name: "coding")
        let b = SessionProfile(name: "x", thresholds: Thresholds())
        let c = SessionProfile(name: "y", thresholds: Thresholds(driftDelay: 15))
        let d = SessionProfile(name: "z", thresholds: Thresholds(driftDelay: 20))
        let e = PinProfile(name: "p")
        let f = PinProfile(name: "q", thresholds: Thresholds(driftDelay: 20))
        let g = DotInit()
        let t = Thresholds()
        let t2 = Thresholds(driftDelay: 15)
    }
    """,
)


# ---------------------------------------------------------------------------
# 5. clap flags
# ---------------------------------------------------------------------------
write(
    FIX / "clap" / "cli.rs",
    r'''
    use clap::{Parser, Subcommand};

    #[derive(Subcommand, Debug)]
    enum Command {
        HookPostTool {
            #[arg(long, default_value = "claude-code")]
            agent: String,
        },
        HookStop {
            #[arg(long, default_value = "claude-code")]
            agent: String,
        },
        HookNamed {
            #[arg(long = "agent-id", default_value = "claude-code")]
            agent: String,
        },
        Timeout {
            #[arg(long, default_value_t = 30)]
            timeout: u32,
        },
    }

    fn examples() {
        let a = "kizu hook-post-tool --agent claude-code";
        let b = "kizu hook-post-tool --agent=claude-code";
        let c = "kizu hook-post-tool --agent \"claude-code\"";
        let d = "kizu hook-post-tool --agent 'claude-code'";
        let e = "kizu hook-post-tool";
        let f = "please run hook-post-tool later";
        let g = "command: hook-post-tool";
        let h = "$ hook-post-tool";
        let i = "kizu hook-post-tool \
            --agent claude-code";
        let j = format!("hook-post-tool --agent {agent_arg}");
        let k = "kizu hook-stop --agent cursor";
        let l = "kizu hook-named --agent-id claude-code";
        let m = "kizu hook-named --agent claude-code";
        let n = "kizu timeout --timeout 30";
        let o = "kizu hook-post-tool --agent cline\n";
        // comment: kizu hook-post-tool rides the default
        let p = "older kizu install of hook-post-tool";
    }
    ''',
)


# ---------------------------------------------------------------------------
# 6. overloads + default merge
# ---------------------------------------------------------------------------
write(
    FIX / "overload" / "box.swift",
    """
    public struct Box {
        public init(width: Double = 10) {}
        public init(width: String = "10") {}
    }
    public func seed() {
        _ = Box()
        _ = Box(width: 10)
        _ = Box(width: "10")
        _ = Box(width: 20)
    }
    """,
)


# ---------------------------------------------------------------------------
# 7. default-moving diffs + FOSSIL (git repos)
# ---------------------------------------------------------------------------
def build_git_repos() -> None:
    # same-name move 0.45 -> 0.50 with tacit / fossil / pre / lock / bound
    repo = REPOS / "move"
    git_init(repo)
    write(
        repo / "a.swift",
        """
        public final class PresenceArbiter {
            public init(sensors: [String], presentThreshold: Double = 0.45) {}
        }
        public func seed() {
            let t = PresenceArbiter(sensors: ["camera"])
            let f = PresenceArbiter(sensors: ["camera"], presentThreshold: 0.45)
            let p = PresenceArbiter(sensors: ["camera"], presentThreshold: 0.50)
            let l = PresenceArbiter(sensors: ["camera"], presentThreshold: 0.99)
            let b = PresenceArbiter(sensors: ["camera"], presentThreshold: provider)
        }
        """,
    )
    git_commit(repo, "old 0.45")
    write(
        repo / "a.swift",
        """
        public final class PresenceArbiter {
            public init(sensors: [String], presentThreshold: Double = 0.50) {}
        }
        public func seed() {
            let t = PresenceArbiter(sensors: ["camera"])
            let f = PresenceArbiter(sensors: ["camera"], presentThreshold: 0.45)
            let p = PresenceArbiter(sensors: ["camera"], presentThreshold: 0.50)
            let l = PresenceArbiter(sensors: ["camera"], presentThreshold: 0.99)
            let b = PresenceArbiter(sensors: ["camera"], presentThreshold: provider)
        }
        """,
    )
    git_commit(repo, "new 0.50")

    # rename at same index (fixture gold)
    repo = REPOS / "rename"
    git_init(repo)
    write(
        repo / "a.swift",
        """
        public final class PresenceArbiter {
            public init(sensors: [String], threshold: Double = 0.4, emaAlpha: Double = 0.3) {}
        }
        public func seed() {
            let a = PresenceArbiter(sensors: ["camera"])
            let b = PresenceArbiter(sensors: ["camera"], threshold: 0.4)
        }
        """,
    )
    git_commit(repo, "threshold 0.4")
    write(
        repo / "a.swift",
        """
        public final class PresenceArbiter {
            public init(sensors: [String], presentThreshold: Double = 0.45, emaAlpha: Double = 0.3) {}
        }
        public func seed() {
            let a = PresenceArbiter(sensors: ["camera"])
            let b = PresenceArbiter(sensors: ["camera"], presentThreshold: 0.4)
        }
        """,
    )
    git_commit(repo, "rename presentThreshold 0.45")

    # insert a slot at index 1 so pairing should break
    repo = REPOS / "shift"
    git_init(repo)
    write(
        repo / "a.swift",
        """
        public final class PresenceArbiter {
            public init(sensors: [String], threshold: Double = 0.4) {}
        }
        public func seed() {
            let a = PresenceArbiter(sensors: ["camera"])
            let b = PresenceArbiter(sensors: ["camera"], threshold: 0.4)
            let c = PresenceArbiter(sensors: ["camera"], threshold: 0.45)
        }
        """,
    )
    git_commit(repo, "threshold 0.4")
    write(
        repo / "a.swift",
        """
        public final class PresenceArbiter {
            public init(sensors: [String], absentThreshold: Double = 0.35, presentThreshold: Double = 0.45) {}
        }
        public func seed() {
            let a = PresenceArbiter(sensors: ["camera"])
            let b = PresenceArbiter(sensors: ["camera"], presentThreshold: 0.4)
            let c = PresenceArbiter(sensors: ["camera"], presentThreshold: 0.45)
        }
        """,
    )
    git_commit(repo, "insert absent, rename present")

    # born-only (no rename): name-only join still BLAST?
    repo = REPOS / "born"
    git_init(repo)
    write(
        repo / "a.swift",
        """
        public final class PresenceArbiter {
            public init(sensors: [String]) {}
        }
        public func seed() {
            let a = PresenceArbiter(sensors: ["camera"])
        }
        """,
    )
    git_commit(repo, "no default")
    write(
        repo / "a.swift",
        """
        public final class PresenceArbiter {
            public init(sensors: [String], presentThreshold: Double = 0.45) {}
        }
        public func seed() {
            let a = PresenceArbiter(sensors: ["camera"])
            let b = PresenceArbiter(sensors: ["camera"], presentThreshold: 0.45)
        }
        """,
    )
    git_commit(repo, "born presentThreshold")

    # float-equal 0.45 -> 0.450 should be stable
    repo = REPOS / "float"
    git_init(repo)
    write(
        repo / "a.swift",
        """
        public final class PresenceArbiter {
            public init(sensors: [String], presentThreshold: Double = 0.45) {}
        }
        public func seed() {
            let a = PresenceArbiter(sensors: ["camera"])
            let b = PresenceArbiter(sensors: ["camera"], presentThreshold: 0.45)
        }
        """,
    )
    git_commit(repo, "0.45")
    write(
        repo / "a.swift",
        """
        public final class PresenceArbiter {
            public init(sensors: [String], presentThreshold: Double = 0.450) {}
        }
        public func seed() {
            let a = PresenceArbiter(sensors: ["camera"])
            let b = PresenceArbiter(sensors: ["camera"], presentThreshold: 0.45)
        }
        """,
    )
    git_commit(repo, "0.450")

    # clap default move
    repo = REPOS / "clapmove"
    git_init(repo)
    write(
        repo / "cli.rs",
        r'''
        enum Command {
            HookPostTool {
                #[arg(long, default_value = "claude-code")]
                agent: String,
            },
        }
        fn examples() {
            let a = "kizu hook-post-tool --agent claude-code";
            let b = "kizu hook-post-tool --agent cursor";
            let c = "kizu hook-post-tool";
        }
        ''',
    )
    git_commit(repo, "claude-code")
    write(
        repo / "cli.rs",
        r'''
        enum Command {
            HookPostTool {
                #[arg(long, default_value = "cursor")]
                agent: String,
            },
        }
        fn examples() {
            let a = "kizu hook-post-tool --agent claude-code";
            let b = "kizu hook-post-tool --agent cursor";
            let c = "kizu hook-post-tool";
        }
        ''',
    )
    git_commit(repo, "cursor default")

    # quote-style "hi" -> 'hi' python
    repo = REPOS / "quotes"
    git_init(repo)
    write(
        repo / "g.py",
        """
        def greet(name, greeting="hi"):
            pass
        greet("x")
        greet("x", "hi")
        greet("x", 'hi')
        """,
    )
    git_commit(repo, "dquote hi")
    write(
        repo / "g.py",
        """
        def greet(name, greeting='hi'):
            pass
        greet("x")
        greet("x", "hi")
        greet("x", 'hi')
        """,
    )
    git_commit(repo, "squote hi")


# ---------------------------------------------------------------------------
# run
# ---------------------------------------------------------------------------
def main() -> int:
    build_git_repos()
    t = load_tacit()
    transcript: list[str] = []

    def rec(s: str) -> None:
        print(s)
        transcript.append(s)

    banner("1. KEYWORD vs POSITIONAL  (python)")
    p = tacit("-C", str(FIX / "kwpos"), "--all", "--header", "f", "splat", "kwargs", "kwonly", "posonly", "greet")
    show("kwpos.py", p)
    rec(p.stdout)

    banner("1b. SWIFT UNLABELED / LABELS")
    p = tacit("-C", str(FIX / "kwpos"), "--all", "--header")
    # filter to swift by running on just the swift file via a tiny tree? scan includes both
    show("kwpos all", p)

    banner("1c. TS positional + keyword mix")
    p = tacit("-C", str(FIX / "kwpos"), "--all", "--header", "retry")
    show("retry.ts", p)

    banner("2. MULTILINE")
    p = tacit("-C", str(FIX / "multiline"), "--all", "--header")
    show("multiline", p)

    banner("3. COMMENTS THAT LOOK LIKE ARGS")
    p = tacit("-C", str(FIX / "comments"), "--all", "--header")
    show("comments", p)

    banner("4. NESTED Thresholds()")
    p = tacit("-C", str(FIX / "nested"), "--all", "--header")
    show("nested", p)
    p = tacit("-C", str(FIX / "nested"), "--all", "--summary")
    show("nested summary", p)

    banner("5. CLAP FLAGS")
    p = tacit("-C", str(FIX / "clap"), "--all", "--header")
    show("clap", p)
    p = tacit("-C", str(FIX / "clap"), "--all", "--summary")
    show("clap summary", p)

    banner("6. OVERLOAD MERGE")
    p = tacit("-C", str(FIX / "overload"), "--all", "--header")
    show("overload", p)

    banner("7. DEFAULT-MOVING DIFFS")
    for name in ("move", "rename", "shift", "born", "float", "clapmove", "quotes"):
        repo = REPOS / name
        p = tacit("-C", str(repo), "--git", "HEAD^", "HEAD", "--header", "--all")
        show(f"git {name}", p)

    banner("8. e9b0f75 PAIRING LIE (import pair_renames on / off)")
    sit = "/Users/annenpolka/ghq/github.com/annenpolka/sitbone"
    old_h = t.harvest_rev(sit, "e9b0f75^")
    new_h = t.harvest_rev(sit, "e9b0f75")
    paired = t.diff_rows(old_h, new_h, unfold=True)
    paired_pa = [
        r
        for r in paired
        if r.callee == "PresenceArbiter" and r.param in {"presentThreshold", "absentThreshold"}
    ]
    rec(
        f"paired e9b0f75 PresenceArbiter rows={len(paired_pa)} "
        f"BLAST={sum(1 for r in paired_pa if r.why=='BLAST')} "
        f"FOSSIL={sum(1 for r in paired_pa if r.why=='FOSSIL')}"
    )
    rec("paired default samples: " + ", ".join(sorted({r.default for r in paired_pa})))

    orig = t.pair_renames

    def name_only(old, new):
        mapping = {}
        old_names = {p.name for p in old}
        for p in new:
            if p.name in old_names:
                mapping[p.name] = p.name
        return mapping

    t.pair_renames = name_only
    nopair = t.diff_rows(old_h, new_h, unfold=True)
    nopair_pa = [
        r
        for r in nopair
        if r.callee == "PresenceArbiter" and r.param in {"presentThreshold", "absentThreshold"}
    ]
    rec(
        f"name-only e9b0f75 PresenceArbiter rows={len(nopair_pa)} "
        f"BLAST={sum(1 for r in nopair_pa if r.why=='BLAST')} "
        f"FOSSIL={sum(1 for r in nopair_pa if r.why=='FOSSIL')}"
    )
    rec("name-only default samples: " + ", ".join(sorted({r.default for r in nopair_pa})))
    t.pair_renames = orig

    # fixture rename with/without pairing — FOSSIL is the pairing-sensitive object
    old_src = (REPOS / "rename" / "a.swift").read_text()  # this is NEW; get from git
    old_txt = subprocess.check_output(
        ["git", "-C", str(REPOS / "rename"), "show", "HEAD^:a.swift"], text=True
    )
    new_txt = subprocess.check_output(
        ["git", "-C", str(REPOS / "rename"), "show", "HEAD:a.swift"], text=True
    )
    old_h = t.harvest_texts([("a.swift", old_txt, "swift")])
    new_h = t.harvest_texts([("a.swift", new_txt, "swift")])
    d_pair = t.diff_rows(old_h, new_h, unfold=True)
    rec("fixture rename WITH pairing:")
    for r in d_pair:
        rec(f"  {r.why}\t{r.verdict}\t{r.param}\t{r.default}\t{r.passed}")
    t.pair_renames = name_only
    d_nop = t.diff_rows(old_h, new_h, unfold=True)
    rec("fixture rename NAME-ONLY:")
    for r in d_nop:
        rec(f"  {r.why}\t{r.verdict}\t{r.param}\t{r.default}\t{r.passed}")
    t.pair_renames = orig

    banner("9. values_equal / is_literal")
    cases = [
        ("0.45", "0.450"),
        ("0.45", ".45"),
        ("15", "15.0"),
        ("0.4", "0.40"),
        ('"hi"', "'hi'"),
        ('"claude-code"', "claude-code"),
        ("True", "true"),
        ("None", "nil"),
        ("Thresholds()", "Thresholds()"),
        ("Thresholds(driftDelay: 15)", "Thresholds()"),
        ("[]", "[ ]"),
    ]
    for a, b in cases:
        rec(f"values_equal({a!r}, {b!r}) = {t.values_equal(a, b)}")
    lits = [
        "0.45",
        "Thresholds()",
        "Thresholds(driftDelay: 15)",
        ".init()",
        "provider",
        '["camera"]',
        "**{'timeout': 30}",
        "()",
        "[]",
        "{}",
        ".present",
        "nil",
    ]
    for s in lits:
        rec(f"is_literal({s!r}) = {t.is_literal(s)}")

    banner("10. SITBONE / KIZU / TENAOSHI gold recheck")
    sit = "/Users/annenpolka/ghq/github.com/annenpolka/sitbone"
    kiz = "/Users/annenpolka/ghq/github.com/annenpolka/kizu"
    ten = "/Users/annenpolka/ghq/github.com/annenpolka/tenaoshi"
    p = tacit("-C", sit, "--all", "--summary", "presentThreshold")
    show("sitbone presentThreshold", p)
    p = tacit("-C", sit, "--git", "e9b0f75^", "e9b0f75", "--summary", "PresenceArbiter")
    show("sitbone e9b0f75", p)
    p = tacit("-C", kiz, "--all", "--header", "--only", "tacit", "agent")
    show("kizu TACIT agent", p)
    p = tacit("-C", ten, "--all", "--header", "reopenUnit")
    show("tenaoshi reopenUnit", p)

    banner("11. signature-skip wrapper (tenaoshi-shaped)")
    write(
        FIX / "wrapper" / "wrap.swift",
        """
        public struct Review {
            public mutating func reopenUnit(id: String, returningToFinal: Bool = true) {}
        }
        public struct Panel {
            func reopenUnit(id: String) {
                review?.reopenUnit(id: id)
            }
            var review: Review?
        }
        public func seed(r: inout Review) {
            r.reopenUnit(id: "x")
            r.reopenUnit(id: "x", returningToFinal: true)
        }
        """,
    )
    p = tacit("-C", str(FIX / "wrapper"), "--all", "--header")
    show("wrapper", p)

    banner("12. self.init / trailing closure / default expr")
    write(
        FIX / "swiftmore" / "more.swift",
        """
        public struct Thresholds {
            public init(driftDelay: Double = 15) {}
            public init(from decoder: Int) {
                self.init(driftDelay: 15)
            }
        }
        public func fetch(url: String, timeout: Double = 30, completion: (Int) -> Void = { _ in }) {}
        public func seed() {
            fetch(url: "x") { n in }
            fetch(url: "x")
            _ = Thresholds(driftDelay: 15)
        }
        """,
    )
    p = tacit("-C", str(FIX / "swiftmore"), "--all", "--header")
    show("swiftmore", p)

    (LOG / "attack-notes.txt").write_text("\n".join(transcript) + "\n")
    print("\nWrote", LOG / "attack-notes.txt")
    return 0


if __name__ == "__main__":
    sys.exit(main())
