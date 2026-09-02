#!/usr/bin/env python3
"""Independent replica of startimer inspect. Does not import the CLI."""
from __future__ import annotations


def fmt_dur(seconds: float) -> str:
    if abs(seconds - round(seconds)) < 1e-9:
        return f"{int(round(seconds))}s"
    return f"{seconds:.3f}s".rstrip("0").rstrip(".") + "s"


def inspect(start_period: float, start_interval: float, interval: float, retries: int) -> dict:
    armed = start_interval
    period_end = start_period
    first_probe = armed
    first_counted = first_probe if first_probe >= period_end else period_end
    unhealthy_at = first_counted + (retries - 1) * interval
    expected_unhealthy = period_end + interval + (retries - 1) * interval
    return {
        "armed_at": 0.0,
        "armed_kind": "start-interval",
        "armed": armed,
        "period_end": period_end,
        "remaining_at_period_end": max(armed - period_end, 0.0),
        "reset_at_period_end": False,
        "first_probe": first_probe,
        "first_counted": first_counted,
        "unhealthy_at": unhealthy_at,
        "expected_unhealthy": expected_unhealthy,
        "gap": unhealthy_at - expected_unhealthy,
        "retries": retries,
    }


def format_report(result: dict) -> str:
    lines = [
        f"armed_at\t{fmt_dur(result['armed_at'])}",
        f"armed\t{result['armed_kind']}\t{fmt_dur(result['armed'])}",
        f"period_end\t{fmt_dur(result['period_end'])}",
        f"remaining_at_period_end\t{fmt_dur(result['remaining_at_period_end'])}",
        f"reset_at_period_end\t{'yes' if result['reset_at_period_end'] else 'no'}",
        f"first_probe\t{fmt_dur(result['first_probe'])}",
        f"first_counted\t{fmt_dur(result['first_counted'])}",
        f"unhealthy_at\t{fmt_dur(result['unhealthy_at'])}",
        f"expected_unhealthy\t{fmt_dur(result['expected_unhealthy'])}",
        f"gap\t{fmt_dur(result['gap'])}",
        f"retries\t{result['retries']}",
    ]
    return "\n".join(lines) + "\n"
