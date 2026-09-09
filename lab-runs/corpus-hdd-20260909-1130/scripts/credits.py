#!/usr/bin/env python3
"""Snapshot OpenRouter credits and live model pricing without printing secrets."""
from __future__ import annotations

import json
import os
import sys
import urllib.request
from datetime import datetime
from pathlib import Path
from zoneinfo import ZoneInfo

from paths import ENV_FILE

JST = ZoneInfo("Asia/Tokyo")
CREDITS_URL = "https://openrouter.ai/api/v1/credits"
MODELS_URL = "https://openrouter.ai/api/v1/models"
R1_SLUG = "deepseek/deepseek-r1"


def load_env(env_file: Path | None = None) -> None:
    path = env_file or ENV_FILE
    if not path.exists():
        return
    for line in path.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, _, value = line.partition("=")
        key = key.strip()
        value = value.strip().strip("'").strip('"')
        os.environ.setdefault(key, value)


def _auth_headers() -> dict[str, str]:
    load_env()
    key = os.environ.get("OPENROUTER_API_KEY", "")
    if not key:
        raise SystemExit("OPENROUTER_API_KEY not set")
    return {"Authorization": f"Bearer {key}"}


def fetch_credits(env_file: Path | None = None) -> dict:
    if env_file is not None:
        load_env(env_file)
    req = urllib.request.Request(CREDITS_URL, headers=_auth_headers())
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


def public_snapshot(snap: dict) -> dict:
    return {k: v for k, v in snap.items() if k != "raw"}


def fetch_r1_pricing() -> dict:
    """Live OpenRouter list price for deepseek/deepseek-r1. Do not reuse 9/2 numbers."""
    req = urllib.request.Request(MODELS_URL, headers=_auth_headers())
    with urllib.request.urlopen(req, timeout=30) as resp:
        payload = json.loads(resp.read().decode())
    models = payload.get("data") or []
    match = next((m for m in models if m.get("id") == R1_SLUG), None)
    if match is None:
        raise SystemExit(f"{R1_SLUG} not present in live OpenRouter model list")
    pricing = match.get("pricing") or {}
    prompt = float(pricing.get("prompt") or 0)
    completion = float(pricing.get("completion") or 0)
    return {
        "model": R1_SLUG,
        "input_usd_per_mtok": round(prompt * 1_000_000, 6),
        "output_usd_per_mtok": round(completion * 1_000_000, 6),
        "prompt_per_token": prompt,
        "completion_per_token": completion,
        "source": f"live OpenRouter GET {MODELS_URL} id={R1_SLUG} at {datetime.now(JST).strftime('%Y-%m-%d %H:%M:%S %Z')}",
        "available": True,
    }


def main() -> None:
    cmd = sys.argv[1] if len(sys.argv) > 1 else "credits"
    if cmd == "credits":
        json.dump(public_snapshot(fetch_credits()), sys.stdout, indent=2)
        sys.stdout.write("\n")
        return
    if cmd == "pricing":
        json.dump(fetch_r1_pricing(), sys.stdout, indent=2)
        sys.stdout.write("\n")
        return
    raise SystemExit(f"unknown command {cmd}")


if __name__ == "__main__":
    main()
