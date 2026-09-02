#!/usr/bin/env python3
"""Independent replica of armtimer inspect. Does not import the CLI."""
from __future__ import annotations


def yn(v: bool) -> str:
    return "yes" if v else "no"


def format_num(v: float) -> str:
    if v == int(v):
        return str(int(v))
    return str(v)


def inspect(rec: dict) -> dict:
    remaining = rec["start_period"] - rec["elapsed"]
    starting = rec["status"] == "starting" and rec["elapsed"] < rec["start_period"]
    armed = rec["start_interval"] if starting else rec["interval"]
    return {
        "armed": armed,
        "during": "starting" if starting else rec["status"],
        "period_end": rec["start_period"],
        "remaining": remaining,
        "expected_after_period": rec["interval"],
        "late": (armed > remaining and remaining >= 0) if starting else False,
    }


def format_report(result: dict) -> str:
    return (
        f"armed\t{format_num(result['armed'])}\n"
        f"during\t{result['during']}\n"
        f"period_end\t{format_num(result['period_end'])}\n"
        f"remaining\t{format_num(result['remaining'])}\n"
        f"expected_after_period\t{format_num(result['expected_after_period'])}\n"
        f"late\t{yn(result['late'])}\n"
    )
