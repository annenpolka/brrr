#!/usr/bin/env python3
"""Report whether timeout 0 visits the object or aborts on wait-for-creation."""
from __future__ import annotations

import argparse
import sys


def decide(timeout: float, wait_for_creation: bool, for_cond: str, exists: bool) -> dict:
    oneshot = timeout == 0
    if oneshot and wait_for_creation and for_cond != "delete":
        return {
            "visited": "false",
            "oneshot": "false",
            "abort": "wait-for-creation-requires-timeout",
            "reason": "creation-wait default aborts before lookup when timeout is 0",
        }
    if not exists and wait_for_creation and for_cond != "delete" and timeout > 0:
        return {
            "visited": "false",
            "oneshot": "false",
            "abort": "none",
            "reason": "would wait for creation (not executed here)",
        }
    return {
        "visited": "true" if exists or for_cond == "delete" else "false",
        "oneshot": "true" if oneshot else "false",
        "abort": "none",
        "reason": "one-shot check" if oneshot else "wait path",
    }


def main(argv: list[str] | None = None) -> int:
    p = argparse.ArgumentParser(prog="waitoneshot")
    p.add_argument("--timeout", type=float, required=True)
    p.add_argument("--wait-for-creation", choices=("true", "false"), default="true")
    p.add_argument("--for", dest="for_cond", default="jsonpath")
    p.add_argument("--object-exists", choices=("true", "false"), default="true")
    args = p.parse_args(argv)
    rec = decide(
        args.timeout,
        args.wait_for_creation == "true",
        args.for_cond,
        args.object_exists == "true",
    )
    print(f"timeout  {args.timeout}")
    print(f"wait_for_creation  {args.wait_for_creation}")
    print(f"for  {args.for_cond}")
    print(f"object_exists  {args.object_exists}")
    for key in ("visited", "oneshot", "abort", "reason"):
        print(f"{key}  {rec[key]}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
