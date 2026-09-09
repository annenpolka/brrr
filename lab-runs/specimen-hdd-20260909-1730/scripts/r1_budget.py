#!/usr/bin/env python3
"""R1 budget gate, ledger append, and markdown render for specimen-hdd-20260909-1730 only."""
from __future__ import annotations

import json
import math
import sys
from datetime import datetime
from pathlib import Path
from zoneinfo import ZoneInfo

from clock_gate import GATES, HARD_STOP, PRESERVE_START
from paths import BUDGET_MD, DAY_MAX_R1_CALLS, LEDGER_JSON, LEDGER_JSONL, USER_CAP_USD

JST = ZoneInfo("Asia/Tokyo")
BROAD_FREEZE = GATES["broad_end"]
HARD_END = HARD_STOP
SAVE_START = PRESERVE_START

CASUAL_PHASES = {"cambrian", "deepen", "jump-broad", "first-turn", "wild", "explore"}
HIGH_VALUE_PHASES = {"counterexample", "jump", "exceptional-jump", "transfer", "follow-up"}


def now_jst(now: datetime | None = None) -> str:
    return (now or datetime.now(JST)).strftime("%Y-%m-%d %H:%M:%S %Z")


def compute_effective_cap(
    available_credit: float,
    user_cap: float = USER_CAP_USD,
    reserve: float = 1.50,
) -> float:
    """effective_cap = max(0, min(user_cap, available_credit - reserve)). No auto top-up."""
    return max(0.0, min(float(user_cap), float(available_credit) - float(reserve)))


def load_ledger(path: Path | None = None) -> dict:
    ledger_path = path or LEDGER_JSON
    text = ledger_path.read_text(encoding="utf-8")
    try:
        return json.loads(text)
    except json.JSONDecodeError:
        obj, _end = json.JSONDecoder().raw_decode(text)
        return obj


def save_ledger(ledger: dict, path: Path | None = None) -> None:
    ledger_path = path or LEDGER_JSON
    ledger_path.parent.mkdir(parents=True, exist_ok=True)
    tmp = ledger_path.with_suffix(".json.tmp")
    tmp.write_text(json.dumps(ledger, indent=2) + "\n", encoding="utf-8")
    tmp.replace(ledger_path)


def conservative_token_estimate(text: str) -> int:
    if not text:
        return 0
    return max(32, math.ceil(len(text) / 2))


def estimate_cost_usd(prompt_chars: int, completion_chars: int, pricing: dict) -> dict:
    prompt_tokens = conservative_token_estimate("x" * prompt_chars if prompt_chars else "")
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
    start = float(ledger["openrouter_snapshot_at_start"]["total_usage"])
    latest_obs = None
    for call in ledger.get("calls") or []:
        after = call.get("credits_after") or {}
        if "total_usage" in after:
            latest_obs = float(after["total_usage"])
    if latest_obs is not None:
        return max(0.0, latest_obs - start)
    return float(ledger.get("estimated_spend_usd") or 0.0)


def conservative_spend(ledger: dict) -> float:
    observed = reported_spend(ledger)
    estimated = float(ledger.get("estimated_spend_usd") or 0.0)
    return max(observed, estimated)


def in_flight_reserve(ledger: dict) -> float:
    return float(ledger.get("in_flight_reserve_usd") or 0.0)


def remaining_usd(ledger: dict) -> float:
    return float(ledger["effective_cap_usd"]) - conservative_spend(ledger) - in_flight_reserve(ledger)


def can_spend(
    ledger: dict,
    phase: str,
    now: datetime | None = None,
    extra_reserve_usd: float = 0.0,
) -> tuple[bool, str]:
    """Refuse new R1 at 100% of effective cap; refuse casual first-turn expansion at 80%."""
    spent = conservative_spend(ledger)
    reserved = in_flight_reserve(ledger) + float(extra_reserve_usd or 0.0)
    cap = float(ledger["effective_cap_usd"])
    remaining = cap - spent - reserved
    hard = float(ledger.get("hard_cap_usd") or USER_CAP_USD)
    stop_all = float(ledger.get("stop_all_new_r1_usd") or cap)
    stop_casual = float(ledger.get("stop_casual_usd") or (0.8 * cap))
    now = now or datetime.now(JST)
    calls = len(ledger.get("calls") or [])
    day_max = int(ledger.get("day_max_r1_calls") or DAY_MAX_R1_CALLS)
    broad_freeze = GATES["broad_end"]

    if cap <= 0:
        return False, "effective_cap is 0: no R1"
    if now >= HARD_END:
        return False, f"hard end {HARD_END.isoformat()}: no new R1"
    if now >= SAVE_START and phase in CASUAL_PHASES:
        return False, f"after {SAVE_START.strftime('%H:%M')} JST: save window; no new exploratory R1"
    if spent >= hard:
        return False, f"hard cap: spent ${spent:.4f} >= ${hard:.2f}"
    if spent + reserved >= stop_all or remaining <= 0:
        return False, (
            f"hard stop: spent ${spent:.4f} + reserve ${reserved:.4f} "
            f">= stop_all ${stop_all:.2f} (100% of effective cap)"
        )
    if remaining < 0.15:
        return False, f"remaining ${remaining:.4f} too small for a conservative R1 call"
    if calls >= day_max:
        return False, f"day max R1 calls: {calls} >= {day_max}"
    if now >= broad_freeze and phase not in {"exceptional-jump"}:
        return False, (
            f"after {broad_freeze.strftime('%H:%M')} JST: broad R1 frozen; only exceptional-jump allowed"
        )
    casual = phase in CASUAL_PHASES or phase not in HIGH_VALUE_PHASES
    if casual and spent + reserved >= stop_casual:
        return False, (
            f"casual stop: spent ${spent:.4f} + reserve ${reserved:.4f} "
            f">= ${stop_casual:.2f} (80% of effective cap); high-value phases still allowed"
        )
    return True, f"ok remaining ${remaining:.4f} of effective cap ${cap:.2f}"


def append_jsonl(record: dict, path: Path | None = None) -> None:
    jsonl = path or LEDGER_JSONL
    jsonl.parent.mkdir(parents=True, exist_ok=True)
    with jsonl.open("a", encoding="utf-8") as fh:
        fh.write(json.dumps(record, ensure_ascii=False) + "\n")


def render_budget_md(ledger: dict) -> str:
    spent = reported_spend(ledger)
    conservative = conservative_spend(ledger)
    cap = float(ledger["effective_cap_usd"])
    start = ledger["openrouter_snapshot_at_start"]
    lines = [
        "# R1 budget",
        "",
        f"Updated: {now_jst()}",
        "",
        "## Caps",
        "",
        f"- User-specified daily cap: **${float(ledger.get('hard_cap_usd') or USER_CAP_USD):.2f}** (ceiling, not a target)",
        f"- OpenRouter remaining at start: **${start['remaining']:.4f}** "
        f"(credits {start['total_credits']} − usage {start['total_usage']})",
        f"- Account reserve: **$1.50** (no auto top-up)",
        f"- Effective cap this run: **${cap:.2f}** — {ledger.get('effective_cap_reason', '')}",
        f"- Stop casual new HDD (80%): **${float(ledger['stop_casual_usd']):.2f}**",
        f"- Stop all new R1 (100%): **${float(ledger['stop_all_new_r1_usd']):.2f}**",
        f"- Day max R1 calls: **{int(ledger.get('day_max_r1_calls') or DAY_MAX_R1_CALLS)}**",
        f"- Broad freeze: **{GATES['broad_end'].strftime('%Y-%m-%d %H:%M:%S %Z')}** (exceptional-jump only after)",
        f"- Preservation start: **{SAVE_START.strftime('%Y-%m-%d %H:%M:%S %Z')}**",
        f"- Hard end: **{HARD_END.strftime('%Y-%m-%d %H:%M:%S %Z')}** (not extended)",
        "",
        "## Totals",
        "",
        f"- Total R1 calls: **{ledger.get('total_calls', 0)}**",
        f"- Observed spend (OpenRouter usage delta): **${spent:.6f}**",
        f"- Conservative transcript estimate (sum): **${float(ledger.get('estimated_spend_usd') or 0):.6f}**",
        f"- Gate spend (max observed, estimate) + in-flight reserve: "
        f"**${conservative:.6f}** + **${in_flight_reserve(ledger):.6f}**",
        f"- Remaining effective budget: **${max(0.0, remaining_usd(ledger)):.6f}**",
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
            "| When JST | Trial | Iter | Phase | Status | HTTP | Tool | Observed USD | Estimated USD |",
            "| --- | --- | ---: | --- | --- | --- | --- | ---: | ---: |",
        ]
        for call in ledger["calls"]:
            obs = ""
            if call.get("credits_before") and call.get("credits_after"):
                obs = f"{float(call['credits_after']['total_usage']) - float(call['credits_before']['total_usage']):.6f}"
            http_ok = call.get("http_success")
            tool_ok = call.get("tool_success", False)
            lines.append(
                f"| {call.get('at_jst', '')} | {call.get('trial')} | {call.get('iteration', '')} | "
                f"{call.get('phase')} | {call.get('status')} | {http_ok} | {tool_ok} | {obs} | {call.get('estimated_usd', '')} |"
            )
        lines.append("")
    lines += [
        "## Notes",
        "",
        "- Dreamer is `deepseek/deepseek-r1` only; no silent substitute.",
        "- An R1 HTTP success is design material, not tool success.",
        "- Host Red Pen does not count against this cap.",
        "- Codex usage is not counted against this cap.",
        "- This ledger lives under the current run dir; closed `lab-hdd/` and the 9/2 and 1130 runs are not written.",
        "- No auto top-up.",
        "",
    ]
    return "\n".join(lines)


def rewrite_budget_md(ledger_path: Path | None = None, md_path: Path | None = None) -> None:
    ledger = load_ledger(ledger_path)
    ledger["reported_spend_usd"] = round(reported_spend(ledger), 6)
    ledger["total_calls"] = len(ledger.get("calls") or [])
    save_ledger(ledger, ledger_path)
    (md_path or BUDGET_MD).write_text(render_budget_md(ledger), encoding="utf-8")


def main() -> None:
    cmd = sys.argv[1] if len(sys.argv) > 1 else "render"
    if cmd == "render":
        rewrite_budget_md()
        print(BUDGET_MD)
        return
    if cmd == "gate":
        phase = sys.argv[2] if len(sys.argv) > 2 else "first-turn"
        ledger = load_ledger()
        ok, reason = can_spend(ledger, phase)
        print(json.dumps({"ok": ok, "reason": reason, "spent": conservative_spend(ledger),
                          "in_flight": in_flight_reserve(ledger), "remaining": remaining_usd(ledger)}))
        sys.exit(0 if ok else 2)
    if cmd == "spent":
        ledger = load_ledger()
        print(f"{reported_spend(ledger):.6f}")
        return
    raise SystemExit(f"unknown command {cmd}")


if __name__ == "__main__":
    main()
