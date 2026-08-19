#!/usr/bin/env python3
"""Adversarial battery: xref DUE = getenv call-site proof."""
from __future__ import annotations

import os
import shutil
import subprocess
import sys
import time
from pathlib import Path

ROOT = Path("/tmp/destroy-xref")
SRC = ROOT / "src"
BINS = ROOT / "bins"
LOGS = ROOT / "logs"
XREF = Path(
    "/Users/annenpolka/.grok/worktrees/annenpolka-brrr/"
    "subagent-01a01b85-3a6f-77f2-a6bf-cb96e7158c54/xref"
)
KIZU = Path("/Users/annenpolka/ghq/github.com/annenpolka/kizu")
TRANSCRIPT = ROOT / "transcript.txt"

BINS.mkdir(parents=True, exist_ok=True)
LOGS.mkdir(parents=True, exist_ok=True)

lines: list[str] = []


def log(msg: str = "") -> None:
    print(msg, flush=True)
    lines.append(msg)


def run(
    argv: list[str],
    *,
    timeout: float = 60,
    cwd: Path | None = None,
) -> subprocess.CompletedProcess[str]:
    t0 = time.time()
    try:
        proc = subprocess.run(
            argv,
            text=True,
            capture_output=True,
            timeout=timeout,
            cwd=cwd,
        )
    except subprocess.TimeoutExpired as exc:
        dt = time.time() - t0
        out = (exc.stdout or "") if isinstance(exc.stdout, str) else ""
        err = (exc.stderr or "") if isinstance(exc.stderr, str) else ""
        log(f"$ {' '.join(argv)}")
        log(f"# TIMEOUT {dt:.2f}s")
        return subprocess.CompletedProcess(argv, 124, out, err)
    dt = time.time() - t0
    log(f"$ {' '.join(argv)}")
    if proc.stdout:
        body = proc.stdout.rstrip("\n")
        log(body)
    if proc.stderr:
        err = proc.stderr.rstrip("\n")
        log("# stderr:")
        log(err)
    log(f"# rc={proc.returncode}  real {dt:.2f}s")
    log()
    return proc


def cc(src: Path, dest: Path, extra: list[str] | None = None) -> bool:
    argv = ["cc", "-o", str(dest), str(src)]
    if extra:
        argv[1:1] = extra
    proc = subprocess.run(argv, text=True, capture_output=True)
    if proc.returncode != 0:
        log(f"# compile FAIL {' '.join(argv)}")
        log(proc.stderr.strip())
        return False
    log(f"# compiled {dest.name}  {' '.join(extra or [])}")
    return True


def xref(*args: str, timeout: float = 60) -> subprocess.CompletedProcess[str]:
    return run([str(XREF), *args], timeout=timeout)


def names_of(text: str) -> set[str]:
    out: set[str] = set()
    for line in text.splitlines():
        line = line.strip()
        if not line or line.startswith("KIND") or line.startswith("-"):
            continue
        if line.startswith("(no owed"):
            continue
        parts = line.split()
        if len(parts) >= 2 and parts[0] in {"DUE", "LATENT", "BOTH", "LEFT_ONLY", "RIGHT_ONLY"}:
            out.add(parts[1])
        elif parts:
            out.add(parts[0])
    return out


def kind_of(text: str, name: str) -> str | None:
    for line in text.splitlines():
        parts = line.split()
        if len(parts) >= 2 and parts[1] == name:
            return parts[0]
        if parts and parts[0] == name:
            return "NAME"
    return None


def save(name: str, text: str) -> None:
    (LOGS / name).write_text(text, encoding="utf-8")


def main() -> int:
    log("=== destroyer-16 xref: DUE=getenv call-site proof ===")
    log(f"xref={XREF}")
    log(f"host={os.uname().machine}  python={sys.version.split()[0]}")
    log()

    log("== selftest (must still pass; no rewrite) ==")
    xref("--selftest", timeout=30)
    xref("--version")

    # --- compile fixtures ---
    log("== compile fixtures ==")
    cases = {
        "direct": (SRC / "direct.c", []),
        "wrap-O0": (SRC / "wrap.c", ["-O0"]),
        "wrap-O2": (SRC / "wrap.c", ["-O2"]),
        "hop2-O0": (SRC / "hop2.c", ["-O0"]),
        "hop2-O2": (SRC / "hop2.c", ["-O2"]),
        "offset-O0": (SRC / "offset.c", ["-O0"]),
        "offset-O2": (SRC / "offset.c", ["-O2"]),
        "false-getenv": (SRC / "false_getenv.c", ["-O2"]),
        "indirect": (SRC / "indirect.c", ["-O2"]),
        "computed": (SRC / "computed.c", ["-O2"]),
        "far": (SRC / "far.c", ["-O2"]),
        "spill-O0": (SRC / "spill.c", ["-O0"]),
        "spill-O2": (SRC / "spill.c", ["-O2"]),
        "wrapx3-O0": (SRC / "wrap_x3.c", ["-O0"]),
        "wrapx3-O2": (SRC / "wrap_x3.c", ["-O2"]),
        "gpu": (SRC / "gpu_assign.c", []),
        "walk": (SRC / "environ_walk.c", []),
        "setenv": (SRC / "setenv_only.c", []),
        "docwrap-O0": (SRC / "doc_and_wrap.c", ["-O0"]),
        "docwrap-O2": (SRC / "doc_and_wrap.c", ["-O2"]),
        "fat-arm": (SRC / "fat_arm.c", ["-arch", "arm64"]),
        "fat-x86": (SRC / "fat_x86.c", ["-arch", "x86_64"]),
    }
    built: dict[str, Path] = {}
    for name, (src, extra) in cases.items():
        dest = BINS / name
        if cc(src, dest, extra):
            built[name] = dest

    blr_ok = subprocess.run(
        ["cc", "-o", str(BINS / "blr"), str(SRC / "blr.s")],
        text=True,
        capture_output=True,
    )
    if blr_ok.returncode == 0:
        built["blr"] = BINS / "blr"
        log("# compiled blr")
    else:
        log("# compile FAIL blr.s")
        log(blr_ok.stderr.strip())

    if "fat-arm" in built and "fat-x86" in built:
        lipo = subprocess.run(
            [
                "lipo",
                "-create",
                str(built["fat-arm"]),
                str(built["fat-x86"]),
                "-output",
                str(BINS / "fat"),
            ],
            text=True,
            capture_output=True,
        )
        if lipo.returncode == 0:
            built["fat"] = BINS / "fat"
            log("# lipo fat arm64+x86_64")
            run(["file", str(BINS / "fat")])
        else:
            log("# lipo FAIL")
            log(lipo.stderr.strip())

    rustc = shutil.which("rustc")
    if rustc:
        inline = BINS / "inline"
        r1 = subprocess.run(
            [
                rustc,
                "-O",
                "-C",
                "lto=thin",
                "-C",
                "codegen-units=1",
                "-C",
                "strip=symbols",
                "-o",
                str(inline),
                str(SRC / "inline.rs"),
            ],
            text=True,
            capture_output=True,
        )
        if r1.returncode == 0:
            built["inline"] = inline
            log("# rustc -O LTO inline.rs")
        else:
            log("# rustc FAIL inline.rs")
            log(r1.stderr.strip()[:400])
        optb = BINS / "option"
        r2 = subprocess.run(
            [rustc, "-O", "-o", str(optb), str(SRC / "option.rs")],
            text=True,
            capture_output=True,
        )
        if r2.returncode == 0:
            built["option"] = optb
            log("# rustc -O option.rs")
        else:
            log("# rustc FAIL option.rs")
            log(r2.stderr.strip()[:400])
        dbg = BINS / "inline-dbg"
        r3 = subprocess.run(
            [rustc, "-o", str(dbg), str(SRC / "inline.rs")],
            text=True,
            capture_output=True,
        )
        if r3.returncode == 0:
            built["inline-dbg"] = dbg
            log("# rustc (debug) inline.rs")

    log()
    log("== 0. gold still holds (do not kill because this) ==")
    if "direct" in built:
        p = xref("--app", str(built["direct"]))
        save("direct.app.txt", p.stdout)
        log(f"# DIRECT_ENV_NAME kind={kind_of(p.stdout, 'DIRECT_ENV_NAME')}")
    host_c = Path(
        "/Users/annenpolka/.grok/worktrees/annenpolka-brrr/"
        "subagent-01a01b85-3a6f-77f2-a6bf-cb96e7158c54/fixtures/split/host.c"
    )
    if host_c.is_file() and cc(host_c, BINS / "host", []):
        p = xref("--app", str(BINS / "host"))
        save("host.app.txt", p.stdout)
        p = xref("--app", "--min-evidence", "call", str(BINS / "host"))
        save("host.min-call.txt", p.stdout)
    orphan_c = Path(
        "/Users/annenpolka/.grok/worktrees/annenpolka-brrr/"
        "subagent-01a01b85-3a6f-77f2-a6bf-cb96e7158c54/fixtures/xref/orphan.c"
    )
    if orphan_c.is_file() and cc(orphan_c, BINS / "orphan", []):
        p = xref("--app", str(BINS / "orphan"))
        save("orphan.app.txt", p.stdout)
        p = xref("--app", "--loose", str(BINS / "orphan"))
        save("orphan.loose.txt", p.stdout)
        log(f"# loose KIND of ORPHAN_ENV_NAME={kind_of(p.stdout, 'ORPHAN_ENV_NAME')}")
        log(f"# loose KIND of APP_SECRET_TOKEN={kind_of(p.stdout, 'APP_SECRET_TOKEN')}")

    log("== 1. one-hop wrapper: real getenv, DUE missing ==")
    for key in ("wrap-O0", "wrap-O2", "docwrap-O0", "docwrap-O2"):
        if key not in built:
            continue
        p = xref("--app", str(built[key]))
        save(f"{key}.app.txt", p.stdout)
        p2 = xref("--calls", "--app", str(built[key]))
        save(f"{key}.calls.txt", p2.stdout)
        log(
            f"# {key} WRAP={kind_of(p.stdout, 'WRAP_ENV_NAME')} "
            f"DIRECT={kind_of(p.stdout, 'DIRECT_ENV_NAME')}"
        )

    log("== 2. second hop ==")
    for key in ("hop2-O0", "hop2-O2"):
        if key not in built:
            continue
        p = xref("--app", str(built[key]))
        save(f"{key}.app.txt", p.stdout)
        xref("--calls", "--app", str(built[key]))
        log(f"# {key} HOP2={kind_of(p.stdout, 'HOP2_ENV_NAME')}")

    log("== 3. offset +4 (CPython ENV_PYTHONHOME shape) ==")
    for key in ("offset-O0", "offset-O2"):
        if key not in built:
            continue
        p = xref("--app", str(built[key]))
        save(f"{key}.app.txt", p.stdout)
        p2 = xref("--app", "--loose", str(built[key]))
        save(f"{key}.loose.txt", p2.stdout)
        log(
            f"# {key} OFFSET_NAME={kind_of(p.stdout, 'OFFSET_NAME')} "
            f"ENV_OFFSET_NAME={kind_of(p.stdout, 'ENV_OFFSET_NAME')}"
        )

    log("== 4. false DUE: symbol suffix *getenv is not a getenv proof ==")
    if "false-getenv" in built:
        p = xref("--app", str(built["false-getenv"]))
        save("false-getenv.app.txt", p.stdout)
        p2 = xref("--calls", "--app", str(built["false-getenv"]))
        save("false-getenv.calls.txt", p2.stdout)
        log(
            f"# FALSE_DUE_NAME={kind_of(p.stdout, 'FALSE_DUE_NAME')} "
            f"FORGET_ENV_NAME={kind_of(p.stdout, 'FORGET_ENV_NAME')}"
        )
        run(["nm", str(built["false-getenv"])])

    log("== 5. indirect blr / function pointer / computed / far window / spill ==")
    for key, needle in (
        ("indirect", "INDIRECT_ENV_NAME"),
        ("computed", "COMPUTED_ENV_NAME"),
        ("far", "FAR_WINDOW_NAME"),
        ("spill-O0", "SPILL_ENV_NAME"),
        ("spill-O2", "SPILL_ENV_NAME"),
        ("wrapx3-O0", "WRAP_X3_NAME"),
        ("wrapx3-O2", "WRAP_X3_NAME"),
        ("blr", "BLR_ENV_NAME"),
        ("walk", "WALK_ENV_NAME"),
        ("setenv", "SETENV_ONLY_NAME"),
    ):
        if key not in built:
            continue
        p = xref("--app", str(built[key]))
        save(f"{key}.app.txt", p.stdout)
        xref("--calls", "--app", str(built[key]))
        log(f"# {key} {needle}={kind_of(p.stdout, needle)}")

    log("== 6. false LATENT: GPU NAME = tables ==")
    if "gpu" in built:
        p = xref("--app", str(built["gpu"]))
        save("gpu.app.txt", p.stdout)
        p2 = xref("--dump-abi", "--app", str(built["gpu"]))
        save("gpu.abi.txt", p2.stdout)
        for n in (
            "STACK_SIZE",
            "SOME_CONST",
            "AMDGPU_BUFFER_ATOMIC_ADD",
            "SQ_PGM_RESOURCES",
        ):
            log(f"# gpu {n}={kind_of(p.stdout, n)}")

    log("== 7. fat Mach-O: native slice is the proof, not the image ==")
    for key in ("fat-arm", "fat-x86", "fat"):
        if key not in built:
            continue
        p = xref("--app", str(built[key]))
        save(f"{key}.app.txt", p.stdout)
        p2 = xref("--calls", "--app", str(built[key]))
        save(f"{key}.calls.txt", p2.stdout)
        log(
            f"# {key} FAT_ARM64_NAME={kind_of(p.stdout, 'FAT_ARM64_NAME')} "
            f"FAT_X86_NAME={kind_of(p.stdout, 'FAT_X86_NAME')}"
        )
    if "fat" in built:
        run(["lipo", "-info", str(built["fat"])])

    log("== 8. rust inlined env::var (packed ptr,len) ==")
    for key in ("inline", "inline-dbg", "option"):
        if key not in built:
            continue
        p = xref("--app", str(built[key]))
        save(f"{key}.app.txt", p.stdout)
        p2 = xref("--app", "--min-evidence", "call", str(built[key]))
        save(f"{key}.min-call.txt", p2.stdout)
        p3 = xref("--calls", "--app", str(built[key]))
        save(f"{key}.calls.txt", p3.stdout)
        p4 = xref("--app", "--loose", str(built[key]))
        save(f"{key}.loose.txt", p4.stdout)
        for n in (
            "WAD_INLINE_NAME",
            "KIZU_CONFIG",
            "OPTION_ENV_NAME",
            "REAL_VAR_NAME",
        ):
            log(f"# {key} {n}={kind_of(p.stdout, n)} mincall={kind_of(p2.stdout, n)}")

    log("== 9. rust source vs image: --vs-program needle is occupancy ==")
    if "inline" in built:
        p = xref(
            "--app",
            str(SRC / "inline.rs"),
            "--vs-program",
            str(built["inline"]),
        )
        save("inline.vs-program.txt", p.stdout)
        p2 = xref("--app", "--min-evidence", "call", str(SRC / "inline.rs"))
        save("inline.rs.call.txt", p2.stdout)

    log("== 10. /bin/ls fat arm64e auth stubs ==")
    p = xref("--names", "--app", "/bin/ls")
    save("ls.names.txt", p.stdout)
    p2 = xref("--app", "/bin/ls")
    save("ls.app.txt", p2.stdout)
    p3 = xref("--calls", "--app", "/bin/ls")
    save("ls.calls.txt", p3.stdout)
    p4 = xref("--images", "/bin/ls")
    save("ls.images.txt", p4.stdout)
    log(f"# ls names={p.stdout.strip()!r}")
    log(f"# COLOR_FORCE in names={'COLOR_FORCE' in p.stdout}")
    log(f"# CLICOLOR_FORCE in names={'CLICOLOR_FORCE' in p.stdout}")

    log("== 11. xcselect / rustup shims ==")
    p = xref("--images", "/usr/bin/python3")
    save("usrpy.images.txt", p.stdout)
    p = xref("--dump-abi", "--app", "/usr/bin/python3")
    save("usrpy.abi.txt", p.stdout)
    p = xref("--app", "/usr/bin/python3")
    save("usrpy.app.txt", p.stdout)
    p = xref("--images", "rustc")
    save("rustc.path.images.txt", p.stdout)
    p = xref("--dump-abi", "--app", "--solo", "rustc")
    save("rustc.path.solo.abi.txt", p.stdout)
    p = xref("--names", "--app", "--solo", "rustc")
    save("rustc.path.solo.names.txt", p.stdout)
    log(f"# PATH rustc solo names={p.stdout.strip()!r}")

    realc_proc = subprocess.run(
        ["rustc", "--print", "sysroot"], text=True, capture_output=True
    )
    realc = None
    if realc_proc.returncode == 0:
        realc = Path(realc_proc.stdout.strip()) / "bin" / "rustc"
        log(f"# sysroot rustc={realc} exists={realc.is_file()}")
        if realc.is_file():
            p = xref("--images", str(realc))
            save("rustc.real.images.txt", p.stdout)

    log("== 12. Homebrew python3 / libpython ==")
    p = xref("--images", "python3")
    save("py.images.txt", p.stdout)
    p = xref("--dump-abi", "--app", "python3")
    save("py.app.abi.txt", p.stdout)
    p2 = xref("--calls", "--app", "python3")
    save("py.calls.txt", p2.stdout)
    p3 = xref("--names", "--app", "--solo", "python3")
    save("py.solo.names.txt", p3.stdout)
    for n in (
        "PYTHONHOME",
        "PYTHONPATH",
        "PYTHON_GIL",
        "PYTHONCASEOK",
        "PYTHONSTARTUP",
        "PYTHONHASHSEED",
        "PYTHONBREAKPOINT",
    ):
        k = None
        for line in Path(LOGS / "py.app.abi.txt").read_text(encoding="utf-8").splitlines():
            if line.startswith(n + "\t"):
                k = line.split("\t")[1]
                how = line.split("\t")[-1]
                log(f"# python3 {n} kind={k} how={how}")
                break
        if k is None:
            log(f"# python3 {n} MISSING")

    log("== 13. kizu source vs release ==")
    kizu_bin = KIZU / "target" / "release" / "kizu"
    kizu_src = KIZU / "src"
    if kizu_src.is_dir():
        p = xref("--names", "--app", "--due", str(kizu_src))
        save("kizu.src.due.txt", p.stdout)
        log(f"# kizu src --due names:\n{p.stdout.rstrip()}")
    if kizu_bin.is_file():
        p = xref("--app", "--min-evidence", "call", "--solo", str(kizu_bin))
        save("kizu.bin.min-call.txt", p.stdout)
        p2 = xref("--calls", "--app", "--solo", str(kizu_bin))
        save("kizu.bin.calls.txt", p2.stdout)
        p3 = xref("--app", "--solo", str(kizu_bin))
        save("kizu.bin.app.txt", p3.stdout)
        p4 = xref("--app", "--loose", "--solo", str(kizu_bin))
        save("kizu.bin.loose.txt", p4.stdout)
        if kizu_src.is_dir():
            p5 = xref(
                "--app",
                str(kizu_src),
                "--vs-program",
                str(kizu_bin),
            )
            save("kizu.vs-program.txt", p5.stdout)
        for n in (
            "KIZU_CONFIG",
            "KIZU_STATE_DIR",
            "KIZU_SESSION_ID",
            "KIZU_EVENT_TTL_SECS",
            "KITTY_LISTEN_ON",
            "ZELLIJ",
            "TMUX",
        ):
            log(
                f"# kizu bin {n} app={kind_of(p3.stdout, n)} "
                f"mincall={kind_of(p.stdout, n)} loose={kind_of(p4.stdout, n)}"
            )

    log("== 14. Homebrew git (cheap names) ==")
    git = shutil.which("git")
    if git:
        p = xref("--names", "--app", git)
        save("git.names.txt", p.stdout)
        log(f"# git nnames={len(p.stdout.splitlines())}")
        log(f"# GIT_DIR in names={'GIT_DIR' in p.stdout.splitlines()}")
        log(f"# ARRAY_SIZE in names={'ARRAY_SIZE' in p.stdout.splitlines()}")
        p2 = xref("--dump-abi", "--app", git)
        save("git.abi.txt", p2.stdout)
        for n in ("GIT_DIR", "ARRAY_SIZE", "GIT_AUTHOR_NAME", "GIT_CONFIG"):
            k = None
            for line in p2.stdout.splitlines():
                if line.startswith(n + "\t"):
                    k = line.split("\t")[1]
                    log(f"# git {n} kind={k} how={line.split(chr(9))[-1]}")
                    break
            if k is None:
                log(f"# git {n} MISSING")

    log("== 15. SIP / shared cache ==")
    p = xref("--images", "/usr/bin/true")
    save("true.images.txt", p.stdout)
    p = xref("--app", "/usr/bin/true")
    save("true.app.txt", p.stdout)
    p = xref("--system", "--images", "/bin/ls")
    save("ls.system.images.txt", p.stdout)
    p = xref("--app", "/bin/cat")
    save("cat.app.txt", p.stdout)

    log("== 16. sysroot rustc (may be slow; still a proof target) ==")
    if realc and realc.is_file():
        p = xref("--dump-abi", "--app", str(realc), timeout=90)
        save("rustc.real.abi.txt", p.stdout)
        n_due = n_lat = n_both = 0
        names = []
        for line in p.stdout.splitlines()[1:]:
            parts = line.split("\t")
            if len(parts) < 2:
                continue
            names.append(parts[0])
            if parts[1] == "DUE":
                n_due += 1
            elif parts[1] == "LATENT":
                n_lat += 1
            elif parts[1] == "BOTH":
                n_both += 1
        log(f"# rustc real names={len(names)} due={n_due} latent={n_lat} both={n_both}")
        for n in (
            "RUSTC_LOG",
            "RUSTC_GRAPHVIZ_FONT",
            "RUSTC_ICE",
            "STACK_SIZE",
            "AMDGPU_BUFFER_ATOMIC_ADD",
            "SESSION_GLOBALS",
            "SOME_CONST",
            "CARGO_INCREMENTAL",
        ):
            hit = next((ln for ln in p.stdout.splitlines() if ln.startswith(n + "\t")), None)
            log(f"# rustc {n}: {hit or 'MISSING'}")
        p2 = xref("--calls", "--app", str(realc), timeout=90)
        save("rustc.real.calls.txt", p2.stdout)
        log(f"# rustc --calls rows={max(0, len(p2.stdout.splitlines())-1)}")

    log("== 17. --loose KIND is DUE (search aid impersonates the proof) ==")
    # already captured on orphan

    log("== 18. source shell $VAR is DUE without getenv ==")
    sh = SRC / "doc.sh"
    sh.write_text("#!/bin/sh\necho set $DOC_SHELL_NAME to x\n", encoding="utf-8")
    p = xref("--app", str(sh))
    save("doc.sh.app.txt", p.stdout)
    log(f"# shell DOC_SHELL_NAME={kind_of(p.stdout, 'DOC_SHELL_NAME')}")

    log("== 19. option_env! source vs image ==")
    if "option" in built:
        p = xref("--app", str(SRC / "option.rs"), "--vs-program", str(built["option"]))
        save("option.vs-program.txt", p.stdout)

    TRANSCRIPT.write_text("\n".join(lines) + "\n", encoding="utf-8")
    log(f"wrote {TRANSCRIPT}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
