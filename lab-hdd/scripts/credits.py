#!/usr/bin/env python3
"""Snapshot OpenRouter credits without printing secrets."""
from __future__ import annotations

import json
import os
import sys
import urllib.request
from datetime import datetime
from pathlib import Path
from zoneinfo import ZoneInfo

ROOT = Path(__file__).resolve().parents[2]
ENV_FILE = ROOT / ".env.hdd"
JST = ZoneInfo("Asia/Tokyo")


def load_env() -> None:
    if not ENV_FILE.exists():
        return
    for line in ENV_FILE.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, _, value = line.partition("=")
        key = key.strip()
        value = value.strip().strip("'").strip('"')
        os.environ.setdefault(key, value)


def fetch_credits() -> dict:
    load_env()
    key = os.environ.get("OPENROUTER_API_KEY", "")
    if not key:
        raise SystemExit("OPENROUTER_API_KEY not set")
    req = urllib.request.Request(
        "https://openrouter.ai/api/v1/credits",
        headers={"Authorization": f"Bearer {key}"},
    )
    with urllib.request.urlopen(req, timeout=30) as resp:
        payload = json.loads(resp.read().decode())
    data = payload.get("data") or {}
    credits = float(data.get("total_credits") or 0)
    usage = float(data.get("total_usage") or 0)
    return {
        "at_jst": datetime.now(JST).strftime("%Y-%m-%d %H:%M:%S %Z"),
        "total_credits": credits,
        "total_usage": usage,
        "remaining": credits - usage,
        "raw": payload,
    }


def main() -> None:
    snap = fetch_credits()
    out = {k: v for k, v in snap.items() if k != "raw"}
    json.dump(out, sys.stdout, indent=2)
    sys.stdout.write("\n")


if __name__ == "__main__":
    main()
