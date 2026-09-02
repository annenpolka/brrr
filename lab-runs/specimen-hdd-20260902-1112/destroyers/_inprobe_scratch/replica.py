#!/usr/bin/env python3
"""Independent replica of inprobe: two greps + echo of caller path_used.

Does not import inprobe. Reconstructs the labeled-row join:
  cgroup_docker     = "docker" in cgroup.lower()
  mountinfo_docker  = "docker" in mount.lower() or "/containers/" in mount
  container         = first /containers/<12-64 hex>/
  path_used         = echoed
  mismatch          = (not cgroup_docker) and mountinfo_docker
"""

from __future__ import annotations

import re
import sys
from pathlib import Path

KNOWN = ("cgroup", "mountinfo", "path_used")
HEX64 = re.compile(r"/containers/([0-9a-f]{12,64})/", re.I)


def parse_record(text: str, *, source: str = "<input>") -> dict:
    cgroup = None
    mountinfo = None
    path_used = None
    for lineno, raw in enumerate(text.splitlines(), 1):
        line = raw.strip()
        if not line or line.startswith("#"):
            continue
        if "\t" not in line:
            raise ValueError(f"{source}:{lineno}: expected key<TAB>value")
        key, rest = line.split("\t", 1)
        key, rest = key.strip(), rest.strip()
        if key not in KNOWN:
            raise ValueError(f"{source}:{lineno}: unknown field {key!r}")
        if key == "cgroup":
            cgroup = rest
        elif key == "mountinfo":
            mountinfo = rest
        elif key == "path_used":
            path_used = rest
    if cgroup is None:
        raise ValueError(f"{source}: missing cgroup")
    if path_used is None:
        raise ValueError(f"{source}: missing path_used")
    return {"cgroup": cgroup, "mountinfo": mountinfo or "", "path_used": path_used}


def inspect(rec: dict) -> dict:
    cgroup_docker = "docker" in rec["cgroup"].lower()
    mount = rec["mountinfo"]
    mount_docker = "docker" in mount.lower() or "/containers/" in mount
    m = HEX64.search(mount)
    container = m.group(1) if m else "none"
    return {
        "cgroup_docker": cgroup_docker,
        "mountinfo_docker": mount_docker,
        "container": container,
        "path_used": rec["path_used"],
        "mismatch": (not cgroup_docker) and mount_docker,
    }


def yn(v: bool) -> str:
    return "yes" if v else "no"


def format_report(result: dict) -> str:
    return (
        f"cgroup_docker\t{yn(result['cgroup_docker'])}\n"
        f"mountinfo_docker\t{yn(result['mountinfo_docker'])}\n"
        f"container\t{result['container']}\n"
        f"path_used\t{result['path_used']}\n"
        f"mismatch\t{yn(result['mismatch'])}\n"
    )


def run(text: str, *, source: str = "<input>") -> tuple[int, str, str]:
    try:
        rec = parse_record(text, source=source)
    except ValueError as err:
        return 1, "", f"inprobe: {err}\n"
    return 0, format_report(inspect(rec)), ""


def main(argv=None) -> int:
    argv = list(sys.argv[1:] if argv is None else argv)
    if argv:
        path = argv[0]
        try:
            text = Path(path).read_text(encoding="utf-8")
        except OSError as err:
            sys.stderr.write(f"inprobe: {err}\n")
            return 1
        source = path
    else:
        text = sys.stdin.read()
        source = "<stdin>"
    rc, out, err = run(text, source=source)
    if err:
        sys.stderr.write(err)
    sys.stdout.write(out)
    return rc


if __name__ == "__main__":
    raise SystemExit(main())
