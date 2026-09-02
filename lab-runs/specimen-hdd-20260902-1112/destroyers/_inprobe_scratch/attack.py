#!/usr/bin/env python3
"""Host attacks against archive inprobe. Does not import inprobe."""

from __future__ import annotations

import json
import os
import subprocess
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
CLI = ROOT / "lineages" / "candidate-inprobe" / "inprobe"
FIX = ROOT / "lineages" / "candidate-inprobe" / "fixtures"
SCRATCH = Path(__file__).resolve().parent
REPLICA = SCRATCH / "replica.py"
SPEC065 = ROOT / "specimens" / "specimen-065" / "files"
DOCK = ROOT / "lineages" / "candidate-dockpath" / "fixtures"
PY = sys.executable

CID = "c33988ec7651ebc867cb24755eaf637a6734088bc7eef59d5799293a9e5450f7"
MOUNT_V2 = (
    "730 721 8:3 /var/lib/docker/containers/"
    f"{CID}/hostname /etc/hostname"
)
CG_V2 = "0::/system.slice/containerd.service"
CG_V1 = (
    "5:cpuset:/docker/"
    f"{CID}\n"
    "1:name=systemd:/docker/"
    f"{CID}\n"
    "0::/system.slice/containerd.service"
)


def rec(**fields: str) -> str:
    order = ("cgroup", "mountinfo", "path_used")
    lines = []
    for k in order:
        if k in fields:
            lines.append(f"{k}\t{fields[k]}")
    for k, v in fields.items():
        if k not in order:
            lines.append(f"{k}\t{v}")
    return "\n".join(lines) + "\n"


def run_cli(text: str | None = None, args: list[str] | None = None, path: Path | None = None):
    cmd = [PY, str(CLI)]
    if args:
        cmd.extend(args)
    elif path is not None:
        cmd.append(str(path))
    inp = None if path is not None or args else (text or "")
    return subprocess.run(cmd, input=inp, capture_output=True, text=True)


def run_replica(text: str, source: str = "<stdin>"):
    sys.path.insert(0, str(SCRATCH))
    import replica  # type: ignore

    return replica.run(text, source=source)


def cli_file(text: str, name: str = "x.rec"):
    path = SCRATCH / name
    path.write_text(text, encoding="utf-8")
    return run_cli(path=path)


def rows(stdout: str) -> dict[str, str]:
    out = {}
    for line in stdout.splitlines():
        if "\t" not in line:
            continue
        k, rest = line.split("\t", 1)
        out[k] = rest
    return out


def yn(v: bool) -> str:
    return "yes" if v else "no"


def grep_nearest(cgroup: str, mount: str, path_used: str) -> dict[str, str]:
    """Ordinary workflow: two greps + echo. No CLI."""
    cgroup_docker = "docker" in cgroup.lower()
    mount_docker = "docker" in mount.lower() or "/containers/" in mount
    import re

    m = re.search(r"/containers/([0-9a-f]{12,64})/", mount, re.I)
    container = m.group(1) if m else "none"
    mismatch = (not cgroup_docker) and mount_docker
    return {
        "cgroup_docker": yn(cgroup_docker),
        "mountinfo_docker": yn(mount_docker),
        "container": container,
        "path_used": path_used,
        "mismatch": yn(mismatch),
    }


def main() -> int:
    results: dict = {"cases": [], "errors": []}
    ok = 0
    fail = 0

    def note(name: str, **kw):
        results["cases"].append({"name": name, **kw})

    def eq(name: str, got, want):
        nonlocal ok, fail
        same = got == want
        if same:
            ok += 1
        else:
            fail += 1
            results["errors"].append({"name": name, "got": got, "want": want})
        note(name, ok=same, got=got, want=want)
        return same

    # --- owned fixtures ---
    for fx in ("065-cgroupv2.rec", "unseen-v1.rec"):
        text = (FIX / fx).read_text(encoding="utf-8")
        p = run_cli(path=FIX / fx)
        rrc, rout, rerr = run_replica(text, source=fx)
        eq(f"replica-file-{fx}-rc", (p.returncode, p.stdout, p.stderr), (rrc, rout, rerr))
        eq(f"replica-stdin-{fx}-rc", (run_cli(text).returncode, run_cli(text).stdout), (rrc, rout))

    # --- replica vs CLI on generated records ---
    cases = []
    cases.append(("owned-v2", rec(cgroup=CG_V2, mountinfo=MOUNT_V2, path_used="/workspace")))
    cases.append(("owned-v1-none-mount", rec(cgroup="12:cpuset:/docker/" + "a" * 64, mountinfo="none", path_used="/host/src")))
    cases.append(("v2-junk-mount", rec(cgroup=CG_V2, mountinfo="x", path_used="/workspace")))
    cases.append(("v2-empty-mount-omit", rec(cgroup=CG_V2, path_used="/workspace")))
    cases.append(("v2-empty-mount-field", rec(cgroup=CG_V2, mountinfo="", path_used="/workspace")))
    cases.append(("comment-docker-cgroup", rec(cgroup="# docker is here", mountinfo=MOUNT_V2, path_used="/workspace")))
    # wait: cgroup value "# docker is here" is NOT a comment line (key is cgroup)
    cases.append(("docker-service-v2", rec(cgroup="0::/system.slice/docker.service", mountinfo=MOUNT_V2, path_used="/workspace")))
    cases.append(("Docker-uppercase-cgroup", rec(cgroup="0::/system.slice/Docker.service", mountinfo="x", path_used="/x")))
    cases.append(("containers-no-docker-word", rec(cgroup=CG_V2, mountinfo=f"/foo/containers/{CID}/hostname", path_used="/x")))
    cases.append(("docker-word-no-containers", rec(cgroup=CG_V2, mountinfo="overlay docker-root", path_used="/x")))
    cases.append(("podman-overlay", rec(cgroup=CG_V2, mountinfo=f"storage/overlay-containers/{CID}/userdata/hostname", path_used="/x")))
    cases.append(("containerd-task", rec(cgroup=CG_V2, mountinfo=f"io.containerd.runtime.v2.task/k8s.io/{CID}/rootfs", path_used="/x")))
    cases.append(("kubepods", rec(cgroup="0::/kubepods/burstable/pod" + "b" * 32, mountinfo="x", path_used="/x")))
    cases.append(("hex12", rec(cgroup=CG_V2, mountinfo="/var/lib/docker/containers/c33988ec7651/hostname", path_used="/x")))
    cases.append(("hex11", rec(cgroup=CG_V2, mountinfo="/var/lib/docker/containers/c33988ec765/hostname", path_used="/x")))
    cases.append(("hex64-upper", rec(cgroup=CG_V2, mountinfo=f"/containers/{CID.upper()}/hostname", path_used="/x")))
    cases.append(("hex65", rec(cgroup=CG_V2, mountinfo="/containers/" + "a" * 65 + "/hostname", path_used="/x")))
    cases.append(("hex64-no-slash-end", rec(cgroup=CG_V2, mountinfo="/containers/" + "a" * 64, path_used="/x")))
    cases.append(("two-ids-first-wins", rec(cgroup=CG_V2, mountinfo=f"/containers/{'b'*12}/a /containers/{CID}/hostname", path_used="/x")))
    cases.append(("path-host", rec(cgroup=CG_V2, mountinfo=MOUNT_V2, path_used="/builds/project/src")))
    cases.append(("path-colon", rec(cgroup=CG_V2, mountinfo=MOUNT_V2, path_used="/workspace:/src")))
    cases.append(("path-spaces", rec(cgroup=CG_V2, mountinfo=MOUNT_V2, path_used="/tmp/has space")))
    cases.append(("path-empty", rec(cgroup=CG_V2, mountinfo=MOUNT_V2, path_used="")))
    cases.append(("both-docker", rec(cgroup="12:cpuset:/docker/" + "a" * 64, mountinfo=MOUNT_V2, path_used="/workspace")))
    cases.append(("neither", rec(cgroup=CG_V2, mountinfo="none", path_used="/host")))
    cases.append(("cgroup-memory-docker-cpuset-root", rec(cgroup="6:memory:/docker/deadbeefdead\n5:cpuset:/\n0::/", mountinfo=MOUNT_V2, path_used="/x")))
    cases.append(("mixed-v1-v2-excerpt", rec(cgroup=CG_V1.replace("\n", " "), mountinfo=MOUNT_V2, path_used="/builds/project/src")))
    cases.append(("mixed-v1-v2-multiline", rec(cgroup=CG_V1.replace("\n", " | "), mountinfo=MOUNT_V2, path_used="/builds/project/src")))
    cases.append(("cgroup-newline-stripped", rec(cgroup=CG_V2, mountinfo=MOUNT_V2, path_used="/workspace")))
    cases.append(("notdocker-scope", rec(cgroup="0::/system.slice/notdocker.service", mountinfo=MOUNT_V2, path_used="/x")))
    cases.append(("docker-in-path-used-only", rec(cgroup=CG_V2, mountinfo="none", path_used="/var/lib/docker/containers/x")))
    cases.append(("tab-in-value-split", "cgroup\t0::/x\n" + "mountinfo\tfoo\tbar\n" + "path_used\t/p\n"))
    cases.append(("last-wins-cgroup", "cgroup\t0::/nodocker\ncgroup\t0::/docker.service\nmountinfo\tx\npath_used\t/p\n"))
    cases.append(("last-wins-path", "cgroup\t0::/\npath_used\t/first\nmountinfo\tx\npath_used\t/second\n"))
    cases.append(("comments-and-blanks", "# note\n\n  \ncgroup\t0::/\n# skip docker\nmountinfo\tnone\npath_used\t/p\n"))
    cases.append(("field-order-path-first", "path_used\t/p\nmountinfo\t" + MOUNT_V2 + "\ncgroup\t" + CG_V2 + "\n"))
    cases.append(("crlf", "cgroup\t" + CG_V2 + "\r\nmountinfo\t" + MOUNT_V2 + "\r\npath_used\t/workspace\r\n"))
    cases.append(("huge-cgroup", rec(cgroup=("nodocker " * 20000) + "end", mountinfo=MOUNT_V2, path_used="/x")))
    cases.append(("huge-with-docker-tail", rec(cgroup=("x" * 50000) + "docker", mountinfo="none", path_used="/x")))
    cases.append(("pod-uuid-mount", rec(cgroup=CG_V2, mountinfo="/var/lib/kubelet/pods/aaaaaaaa-bbbb-cccc-dddd-eeeeeeeeeeee/volumes", path_used="/x")))
    cases.append(("crio-containers-storage", rec(cgroup=CG_V2, mountinfo="/var/lib/containers/storage/overlay", path_used="/x")))
    cases.append(("sysbox", rec(cgroup="0::/system.slice/sysbox.service", mountinfo=MOUNT_V2, path_used="/x")))
    cases.append(("user-slice", rec(cgroup="0::/user.slice/user-1000.slice", mountinfo="none", path_used="/home/u")))
    cases.append(("binary-looking-text", rec(cgroup="0::/\x00docker", mountinfo="x", path_used="/x")))

    replica_n = 0
    replica_ok = 0
    grep_n = 0
    grep_ok = 0
    path_swap_n = 0
    path_swap_mismatch_same = 0

    for name, text in cases:
        p = run_cli(text)
        rrc, rout, rerr = run_replica(text, source=name)
        replica_n += 1
        same = (p.returncode, p.stdout, p.stderr) == (rrc, rout, rerr)
        if same:
            replica_ok += 1
        else:
            results["errors"].append(
                {
                    "name": f"replica-{name}",
                    "cli_rc": p.returncode,
                    "cli_out": p.stdout,
                    "cli_err": p.stderr,
                    "rep_rc": rrc,
                    "rep_out": rout,
                    "rep_err": rerr,
                }
            )
        note(f"replica-{name}", ok=same, rc=p.returncode, stdout=p.stdout, stderr=p.stderr)

        if p.returncode == 0:
            r = rows(p.stdout)
            # grep nearest on parsed fields
            # Use replica parse to get fields, or split TSV ourselves for well-formed rec()
            try:
                sys.path.insert(0, str(SCRATCH))
                import replica as R  # type: ignore

                parsed = R.parse_record(text, source=name)
                g = grep_nearest(parsed["cgroup"], parsed["mountinfo"], parsed["path_used"])
                grep_n += 1
                gsame = g == r
                if gsame:
                    grep_ok += 1
                else:
                    results["errors"].append({"name": f"grep-{name}", "got": r, "want": g})
            except Exception as e:
                results["errors"].append({"name": f"grep-parse-{name}", "err": str(e)})

            # path_used swap: mismatch/container/cgroup/mount flags unchanged
            if "path_used" in r:
                swapped = rec(
                    cgroup=parsed["cgroup"],
                    mountinfo=parsed["mountinfo"],
                    path_used="/OTHER/PATH",
                )
                s = run_cli(swapped)
                sr = rows(s.stdout)
                path_swap_n += 1
                keys = ("cgroup_docker", "mountinfo_docker", "container", "mismatch")
                if all(sr.get(k) == r.get(k) for k in keys) and sr.get("path_used") == "/OTHER/PATH":
                    path_swap_mismatch_same += 1
                else:
                    results["errors"].append({"name": f"path-swap-{name}", "orig": r, "swap": sr})

    # --- parse errors ---
    err_cases = [
        ("missing-cgroup", "path_used\t/x\n"),
        ("missing-path", "cgroup\t0::/\n"),
        ("unknown-field", "cgroup\t0::/\npath_used\t/x\nfoo\tbar\n"),
        ("no-tab", "cgroup without tab\npath_used\t/x\n"),
        ("empty", ""),
        ("comments-only", "# cgroup\tdocker\n# path_used\t/x\n"),
        ("mountinfo-only", "mountinfo\tx\n"),
    ]
    err_ok = 0
    for name, text in err_cases:
        p = run_cli(text)
        rrc, rout, rerr = run_replica(text, source="<stdin>" if name != "x" else name)
        # replica uses source <input> default; CLI uses <stdin>
        rrc2, rout2, rerr2 = run_replica(text, source="<stdin>")
        same = (p.returncode, p.stdout, p.stderr) == (rrc2, rout2, rerr2)
        if same:
            err_ok += 1
        else:
            results["errors"].append(
                {
                    "name": f"err-{name}",
                    "cli": (p.returncode, p.stdout, p.stderr),
                    "rep": (rrc2, rout2, rerr2),
                }
            )
        note(f"err-{name}", ok=same, rc=p.returncode, stderr=p.stderr)

    # missing file
    p = run_cli(args=["/no/such/inprobe.rec"])
    note("missing-file", rc=p.returncode, stderr=p.stderr[:200])

    # argparse extra
    p2 = subprocess.run([PY, str(CLI), "a", "b"], capture_output=True, text=True)
    note("two-args", rc=p2.returncode, stderr=p2.stderr[:200])

    # dash as filename
    p3 = run_cli(args=["-"])
    note("dash-filename", rc=p3.returncode, stderr=p3.stderr[:200])

    # directory
    p4 = run_cli(args=[str(FIX)])
    note("directory", rc=p4.returncode, stderr=p4.stderr[:200])

    # invalid utf-8
    bad = SCRATCH / "bad-utf8.rec"
    bad.write_bytes(b"cgroup\t0::/\npath_used\t/x\nmountinfo\t\xff\xfe\n")
    p5 = subprocess.run([PY, str(CLI), str(bad)], capture_output=True, text=True)
    note("invalid-utf8", rc=p5.returncode, stderr=p5.stderr[:300])

    # /dev/null
    p6 = run_cli(args=["/dev/null"])
    note("dev-null", rc=p6.returncode, stderr=p6.stderr[:200])

    # specimen-065 excerpts wrapped as caller-labeled rows
    cg2 = (SPEC065 / "cgroup_v2.excerpt").read_text(encoding="utf-8").strip()
    mt2 = (SPEC065 / "mountinfo_v2.hostname.excerpt").read_text(encoding="utf-8").strip()
    wrapped = rec(cgroup=cg2, mountinfo=mt2, path_used="/workspace")
    p7 = run_cli(wrapped)
    rrc, rout, rerr = run_replica(wrapped, source="065-wrap")
    note(
        "specimen-065-wrap",
        ok=(p7.returncode, p7.stdout) == (rrc, rout),
        stdout=p7.stdout,
        replica=rout,
    )
    grep = grep_nearest(cg2, mt2, "/workspace")
    note("specimen-065-grep", ok=rows(p7.stdout) == grep, cli=rows(p7.stdout), grep=grep)

    # dockpath cwd as path_used
    wrapped2 = rec(cgroup=cg2, mountinfo=mt2, path_used="/builds/project/src")
    p8 = run_cli(wrapped2)
    r8 = rows(p8.stdout)
    note(
        "path-echo-not-volume",
        stdout=p8.stdout,
        has_colon_volume=":" in r8.get("path_used", "") and r8.get("path_used", "").endswith(":/src"),
        path_used=r8.get("path_used"),
        mismatch=r8.get("mismatch"),
    )

    # cgroup v1 excerpt as labeled row: docker substring yes, mismatch no
    cg1 = (SPEC065 / "cgroup_v1.excerpt").read_text(encoding="utf-8")
    # TSV value cannot hold raw newlines as extra records; put as one line
    cg1_one = " ".join(cg1.split())
    wrapped3 = rec(cgroup=cg1_one, mountinfo=mt2, path_used="/builds/project/src")
    p9 = run_cli(wrapped3)
    note("v1-excerpt-labeled", stdout=p9.stdout, rc=p9.returncode)

    # mismatch does not extract cgroup id
    note(
        "container-from-mountinfo-only",
        v1_container=rows(p9.stdout).get("container"),
        v1_cgroup_docker=rows(p9.stdout).get("cgroup_docker"),
        v1_mismatch=rows(p9.stdout).get("mismatch"),
    )

    # printf of owned 065 vs CLI
    owned = run_cli(path=FIX / "065-cgroupv2.rec")
    canned = (
        "cgroup_docker\tno\n"
        "mountinfo_docker\tyes\n"
        f"container\t{CID}\n"
        "path_used\t/workspace\n"
        "mismatch\tyes\n"
    )
    note("printf-owned-065", ok=owned.stdout == canned, cli=owned.stdout, printf=canned)

    # inspect never uses path in mismatch: 20 random paths
    paths = [
        "/workspace",
        "/builds/project/src",
        "/",
        "",
        "/var/lib/docker",
        "relative",
        "none",
        "/src",
        "C:\\Windows",
        "/tmp/\tweird",
    ]
    flags = None
    path_flag_ok = 0
    for i, path in enumerate(paths):
        # tab in path_used: rest is after first tab, so tab becomes part of value then strip
        t = rec(cgroup=CG_V2, mountinfo=MOUNT_V2, path_used=path.replace("\t", " "))
        pr = run_cli(t)
        rr = rows(pr.stdout)
        f = (rr.get("cgroup_docker"), rr.get("mountinfo_docker"), rr.get("container"), rr.get("mismatch"))
        if flags is None:
            flags = f
        if f == flags and rr.get("path_used") == path.replace("\t", " "):
            path_flag_ok += 1
    note("path-spectator-10", ok=path_flag_ok, n=len(paths), flags=list(flags) if flags else None)

    summary = {
        "replica_ok": replica_ok,
        "replica_n": replica_n,
        "grep_ok": grep_ok,
        "grep_n": grep_n,
        "err_ok": err_ok,
        "err_n": len(err_cases),
        "path_swap_ok": path_swap_mismatch_same,
        "path_swap_n": path_swap_n,
        "path_spectator_ok": path_flag_ok,
        "path_spectator_n": len(paths),
        "error_count": len(results["errors"]),
        "printf_owned": owned.stdout == canned,
        "missing_file_rc": p.returncode,
        "two_args_rc": p2.returncode,
        "dash_rc": p3.returncode,
        "dir_rc": p4.returncode,
        "utf8_rc": p5.returncode,
        "devnull_rc": p6.returncode,
        "utf8_err": p5.stderr[:300],
        "missing_err": p.stderr[:300],
        "dir_err": p4.stderr[:300],
        "dash_err": p3.stderr[:300],
        "devnull_err": p6.stderr[:200],
        "v1_excerpt": p9.stdout,
        "v2_wrap": p7.stdout,
        "path_echo": p8.stdout,
    }
    results["summary"] = summary
    outp = SCRATCH / "attack.json"
    outp.write_text(json.dumps(results, indent=2, ensure_ascii=False), encoding="utf-8")
    print(json.dumps(summary, indent=2))
    print("errors", len(results["errors"]))
    for e in results["errors"][:20]:
        print("ERR", e["name"], {k: v for k, v in e.items() if k != "name"})
    return 0 if not results["errors"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
