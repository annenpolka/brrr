#!/usr/bin/env python3
"""Assert fields on a knot JSON report.

  assert_report.py REPORT.json knot.comm=sleep conversation.kinds=pipe-empty
"""
from __future__ import annotations

import json
import sys


def walk(obj, path: str):
    cur = obj
    for part in path.split("."):
        if part == "kinds" and isinstance(cur, list):
            return sorted({(e or {}).get("kind") for e in cur if isinstance(e, dict)})
        if isinstance(cur, list):
            cur = cur[int(part)]
        elif isinstance(cur, dict):
            cur = cur[part]
        else:
            raise KeyError(path)
    return cur


def main() -> int:
    if len(sys.argv) < 3:
        print("usage: assert_report.py REPORT.json path=expect ...", file=sys.stderr)
        return 2
    with open(sys.argv[1], encoding="utf-8") as fh:
        report = json.load(fh)
    failed = 0
    for spec in sys.argv[2:]:
        if "=" not in spec:
            print(f"bad spec {spec!r}", file=sys.stderr)
            failed += 1
            continue
        path, expect = spec.split("=", 1)
        try:
            if path == "conversation.kinds":
                kinds = {(e or {}).get("kind") for e in (report.get("conversation") or [])}
                kinds |= {(e or {}).get("kind") for e in (report.get("graph") or [])}
                got = sorted(k for k in kinds if k)
                ok = expect in got
                if ok:
                    print(f"ok   {path} contains {expect}  (saw {got})")
                    continue
                print(f"FAIL {path}: {expect!r} not in {got}", file=sys.stderr)
                failed += 1
                continue
            got = walk(report, path)
        except (KeyError, IndexError, ValueError, TypeError) as exc:
            print(f"FAIL {path}: missing ({exc})", file=sys.stderr)
            failed += 1
            continue
        got_s = str(got)
        if expect in {got_s, json.dumps(got)} or (isinstance(got, str) and expect in got):
            print(f"ok   {path}={got_s}")
            continue
        try:
            if abs(float(got) - float(expect)) <= 1e-6:
                print(f"ok   {path}={got_s}")
                continue
        except (TypeError, ValueError):
            pass
        print(f"FAIL {path}: got {got_s!r} want {expect!r}", file=sys.stderr)
        failed += 1
    return 1 if failed else 0


if __name__ == "__main__":
    raise SystemExit(main())
