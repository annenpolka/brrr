#!/usr/bin/env python3
"""R1 budget gate, ledger append, and markdown render."""
from __future__ import annotations

import json
import math
import sys
from datetime import datetime
from pathlib import Path
from zoneinfo import ZoneInfo

ROOT = Path(__file__).resolve().parents[2]
LAB = ROOT / "lab-hdd"
LEDGER = LAB / "r1-ledger.json"
BUDGET_MD = LAB / "R1_BUDGET.md"
JST = ZoneInfo("Asia/Tokyo")


def now_jst() -> str:
    return datetime.now(JST).strftime("%Y-%m-%d %H:%M:%S %Z")


def load_ledger() -> dict:
    return json.loads(LEDGER.read_text(encoding="utf-8"))


def save_ledger(ledger: dict) -> None:
    LEDGER.write_text(json.dumps(ledger, indent=2) + "\n", encoding="utf-8")


def conservative_token_estimate(text: str) -> int:
    """Overestimate tokens: 2 chars/token plus a floor."""
    if not text:
        return 0
    return max(32, math.ceil(len(text) / 2))


def estimate_cost_usd(prompt_chars: int, completion_chars: int, pricing: dict) -> dict:
    prompt_tokens = conservative_token_estimate("x" * prompt_chars if prompt_chars else "")
    # reasoning buffer: billed output may include hidden reasoning
    completion_tokens = conservative_token_estimate("x" * completion_chars if completion_chars else "")
    reasoning_buffer = 8192 if completion_chars else 0
    billed_out = completion_tokens + reasoning_buffer
    inp = pricing["input_usd_per_mtok"] * prompt_tokens / 1_000_000
    out = pricing["output_usd_per_mtok"] * billed_out / 1_000_000
    return {
        "prompt_tokens_est": prompt_tokens,
        "completion_tokens_est": completion_tokens,
        "reasoning_buffer_tokens": reasoning_buffer,
        "estimated_usd": round(inp + out, 6),
    }


def reported_spend(ledger: dict) -> float:
    """Prefer observed OpenRouter usage delta; fall back to estimates."""
    start = float(ledger["openrouter_snapshot_at_start"]["total_usage"])
    latest_obs = None
    for call in ledger.get("calls") or []:
        after = call.get("credits_after") or {}
        if "total_usage" in after:
            latest_obs = float(after["total_usage"])
    if latest_obs is not None:
        return max(0.0, latest_obs - start)
    return float(ledger.get("estimated_spend_usd") or 0.0)


def can_spend(ledger: dict, phase: str) -> tuple[bool, str]:
    spent = reported_spend(ledger)
    cap = float(ledger["effective_cap_usd"])
    remaining = cap - spent
    if spent >= float(ledger["stop_all_new_r1_usd"]):
        return False, f"hard stop: spent ${spent:.4f} >= stop_all ${ledger['stop_all_new_r1_usd']}"
    if spent >= float(ledger["stop_casual_usd"]):
        return False, f"casual stop: spent ${spent:.4f} >= ${ledger['stop_casual_usd']}"
    # 05:00 checkpoint: no broad speculative R1
    hour = datetime.now(JST).hour
    minute = datetime.now(JST).minute
    after_0500 = hour > 5 or (hour == 5 and minute >= 0 and hour >= 5)
    # After 05:00 JST on 2026-09-02 only
    d = datetime.now(JST)
    if d >= datetime(2026, 9, 2, 5, 0, tzinfo=JST):
        if phase in {"cambrian", "deepen", "jump-broad"}:
            return False, "after 05:00 JST: broad speculative R1 ended"
    if d >= datetime(2026, 9, 2, 5, 0, tzinfo=JST) and spent >= float(ledger.get("checkpoint_40_before_05") or 8):
        if phase != "exceptional-jump":
            return False, "after 05:00 and near envelope; only exceptional jumps"
    if remaining < 0.15:
        return False, f"remaining ${remaining:.4f} too small for a conservative R1 call"
    return True, f"ok remaining ${remaining:.4f} of effective cap ${cap:.2f}"


def render_budget_md(ledger: dict) -> str:
    spent = reported_spend(ledger)
    cap = float(ledger["effective_cap_usd"])
    lines = [
        "# R1 budget",
        "",
        f"Updated: {now_jst()}",
        "",
        "## Caps",
        "",
        f"- Experiment hard cap: **$50.00** (ceiling, not a target)",
        f"- OpenRouter remaining at start: **${ledger['openrouter_snapshot_at_start']['remaining']:.4f}** "
        f"(credits {ledger['openrouter_snapshot_at_start']['total_credits']} − usage "
        f"{ledger['openrouter_snapshot_at_start']['total_usage']})",
        f"- Effective cap this night: **${cap:.2f}** — {ledger['effective_cap_reason']}",
        f"- Stop casual new HDD: **${ledger['stop_casual_usd']:.2f}**",
        f"- Stop all new R1: **${ledger['stop_all_new_r1_usd']:.2f}**",
        "",
        "## Totals",
        "",
        f"- Total R1 calls: **{ledger.get('total_calls', 0)}**",
        f"- Observed spend (OpenRouter usage delta): **${spent:.6f}**",
        f"- Conservative transcript estimate (sum): **${float(ledger.get('estimated_spend_usd') or 0):.6f}**",
        f"- Remaining effective budget: **${max(0, cap - spent):.6f}**",
        f"- Remaining vs $50 experiment cap: **${50.0 - spent:.6f}**",
        "",
        "## Pricing used for estimates",
        "",
        f"- Input ${ledger['pricing']['input_usd_per_mtok']}/MTok, "
        f"output ${ledger['pricing']['output_usd_per_mtok']}/MTok",
        f"- Source: {ledger['pricing']['source']}",
        f"- Missing-metadata rule: chars/2 tokens + 8192 reasoning-token buffer per call",
        "",
        "## Calls by trial",
        "",
    ]
    by_trial: dict[str, dict] = {}
    by_phase: dict[str, dict] = {}
    for call in ledger.get("calls") or []:
        trial = call.get("trial", "?")
        phase = call.get("phase", "?")
        obs = 0.0
        if call.get("credits_before") and call.get("credits_after"):
            obs = float(call["credits_after"]["total_usage"]) - float(call["credits_before"]["total_usage"])
        est = float(call.get("estimated_usd") or 0)
        rec = by_trial.setdefault(trial, {"n": 0, "obs": 0.0, "est": 0.0})
        rec["n"] += 1
        rec["obs"] += obs
        rec["est"] += est
        prec = by_phase.setdefault(phase, {"n": 0, "obs": 0.0, "est": 0.0})
        prec["n"] += 1
        prec["obs"] += obs
        prec["est"] += est
    if not by_trial:
        lines.append("(no calls yet)")
        lines.append("")
    else:
        lines += ["| Trial | Calls | Observed USD | Estimated USD |", "| --- | ---: | ---: | ---: |"]
        for trial, rec in sorted(by_trial.items()):
            lines.append(f"| {trial} | {rec['n']} | {rec['obs']:.6f} | {rec['est']:.6f} |")
        lines.append("")
    lines += ["## Calls by experiment phase", ""]
    if not by_phase:
        lines.append("(no calls yet)")
        lines.append("")
    else:
        lines += ["| Phase | Calls | Observed USD | Estimated USD |", "| --- | ---: | ---: | ---: |"]
        for phase, rec in sorted(by_phase.items()):
            lines.append(f"| {phase} | {rec['n']} | {rec['obs']:.6f} | {rec['est']:.6f} |")
        lines.append("")
    lines += ["## Call log", ""]
    if not ledger.get("calls"):
        lines.append("(none)")
        lines.append("")
    else:
        lines += [
            "| When JST | Trial | Iter | Phase | Status | Observed USD | Estimated USD |",
            "| --- | --- | ---: | --- | --- | ---: | ---: |",
        ]
        for call in ledger["calls"]:
            obs = ""
            if call.get("credits_before") and call.get("credits_after"):
                obs = f"{float(call['credits_after']['total_usage']) - float(call['credits_before']['total_usage']):.6f}"
            lines.append(
                f"| {call.get('at_jst', '')} | {call.get('trial')} | {call.get('iteration', '')} | "
                f"{call.get('phase')} | {call.get('status')} | {obs} | {call.get('estimated_usd', '')} |"
            )
        lines.append("")
    lines += [
        "## Notes",
        "",
        "- R1 is for conceptual Dreamer mutation, not routine coding.",
        "- A Red Pen turn does not imply another R1 turn.",
        "- If OpenRouter is down, Dreaming degrades; grounding/implementation/judging continue.",
        "",
    ]
    return "\n".join(lines)


def rewrite_budget_md() -> None:
    ledger = load_ledger()
    ledger["reported_spend_usd"] = round(reported_spend(ledger), 6)
    ledger["total_calls"] = len(ledger.get("calls") or [])
    save_ledger(ledger)
    BUDGET_MD.write_text(render_budget_md(ledger), encoding="utf-8")


def main() -> None:
    cmd = sys.argv[1] if len(sys.argv) > 1 else "render"
    if cmd == "render":
        rewrite_budget_md()
        print(BUDGET_MD)
        return
    if cmd == "gate":
        phase = sys.argv[2] if len(sys.argv) > 2 else "cambrian"
        ledger = load_ledger()
        ok, reason = can_spend(ledger, phase)
        print(json.dumps({"ok": ok, "reason": reason, "spent": reported_spend(ledger)}))
        sys.exit(0 if ok else 2)
    if cmd == "spent":
        ledger = load_ledger()
        print(f"{reported_spend(ledger):.6f}")
        return
    raise SystemExit(f"unknown command {cmd}")


if __name__ == "__main__":
    main()
