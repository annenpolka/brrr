#!/usr/bin/env python3
"""Independent replica of poslayer: caller-labeled position/layer rows.

Does not import poslayer. Reconstructs:
  file_argv = replace(token, join(leftover)).split()
  override_argv = same if subst_override else override.split()
  state = literal if token in argv else expanded if token in template else absent
  entered = "file" if token in file_template; "override" if subst_override and token in override
  missed = leftover unless override substitution ran
  ran_against = last override argv word
  silent = override literal and caller exit sticker == 0
"""

from __future__ import annotations


def subst(template: str, leftover: list[str], token: str) -> str:
    return template.replace(token, " ".join(leftover))


def to_argv(command: str) -> list[str]:
    return command.split()


def token_state(template: str, argv: list[str], token: str) -> str:
    if token in argv:
        return "literal"
    if token in template:
        return "expanded"
    return "absent"


def leftover_present(leftover: list[str], argv: list[str]) -> list[str]:
    counts: dict[str, int] = {}
    for item in argv:
        counts[item] = counts.get(item, 0) + 1
    present: list[str] = []
    used: dict[str, int] = {}
    for item in leftover:
        used[item] = used.get(item, 0) + 1
        if used[item] <= counts.get(item, 0):
            present.append(item)
    return present


def inspect(
    file_template: str,
    override_template: str,
    leftover: list[str],
    token: str = "{posargs}",
    exit_code: int = 0,
    subst_override: bool = False,
) -> dict:
    file_argv = to_argv(subst(file_template, leftover, token))
    if subst_override:
        override_argv = to_argv(subst(override_template, leftover, token))
    else:
        override_argv = to_argv(override_template)
    entered: list[str] = []
    if token in file_template:
        entered.append("file")
    override_took = subst_override and token in override_template
    if override_took:
        entered.append("override")
    missed = [] if override_took else list(leftover)
    override_state = token_state(override_template, override_argv, token)
    silent = override_state == "literal" and exit_code == 0
    return {
        "token": token,
        "leftover": list(leftover),
        "file_argv": file_argv,
        "override_argv": override_argv,
        "file": token_state(file_template, file_argv, token),
        "override": override_state,
        "entered": entered,
        "in_override": leftover_present(leftover, override_argv),
        "missed": missed,
        "exit": exit_code,
        "ran_against": override_argv[-1] if override_argv else "",
        "silent": "yes" if silent else "no",
    }


def format_list(items: list[str]) -> list[str]:
    return items if items else ["-"]


def format_result(result: dict) -> str:
    lines = [
        "\t".join(["token", result["token"]]),
        "\t".join(["leftover", *format_list(result["leftover"])]),
        "\t".join(["file", result["file"], *result["file_argv"]]),
        "\t".join(["override", result["override"], *result["override_argv"]]),
        "\t".join(["entered", *format_list(result["entered"])]),
        "\t".join(["in_override", *format_list(result["in_override"])]),
        "\t".join(["missed", *format_list(result["missed"])]),
        "\t".join(["ran_against", result["ran_against"] or "-"]),
        "\t".join(["exit", str(result["exit"])]),
        "\t".join(["silent", result["silent"]]),
    ]
    return "\n".join(lines) + "\n"


def report(
    file_template: str,
    leftover: list[str],
    *,
    override: str | None = None,
    token: str = "{posargs}",
    exit_code: int = 0,
    subst_override: bool = False,
) -> str:
    override_template = file_template if override is None else override
    return format_result(
        inspect(
            file_template,
            override_template,
            leftover,
            token=token,
            exit_code=exit_code,
            subst_override=subst_override,
        )
    )
