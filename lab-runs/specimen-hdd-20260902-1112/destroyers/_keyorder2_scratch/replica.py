#!/usr/bin/env python3
"""Independent replica of keyorder inspect: key-order diff on caller objects.

Does not import the CLI. Primitive:

    keys = tuple(mapping)
    sk = tuple(sorted(mapping))
    obj_keys = tuple(obj) if obj is not None else None
    label = sorted-keys if keys==sk else insertion-order if obj is None or keys==obj_keys else other
    disagree = len(set(tuple(m) for m in displays)) > 1
    reordered = names whose keys == sk and keys != obj_keys
    faithful = names whose keys == obj_keys
"""
from __future__ import annotations

import ast
import json
import re
import subprocess
import sys
import tempfile
from pathlib import Path

RUN = Path("/Users/annenpolka/ghq/github.com/annenpolka/brrr/lab-runs/specimen-hdd-20260902-1112")
CLI = RUN / "lineages/candidate-keyorder/keyorder"
FX = RUN / "lineages/candidate-keyorder/fixtures"
SCRATCH = Path(__file__).resolve().parent
ASSIGN_RE = re.compile(r"^(?:[A-Za-z_][A-Za-z0-9_]*)\s*=\s*")


def strip_prefix(text: str) -> str:
    raw = text.strip()
    while True:
        match = ASSIGN_RE.match(raw)
        if not match:
            break
        rest = raw[match.end() :]
        if rest.startswith("{"):
            raw = rest
            continue
        break
    if raw.endswith(",") and raw.startswith("{"):
        candidate = raw[:-1].rstrip()
        if candidate.endswith("}"):
            raw = candidate
    return raw


def parse_mapping(text: str) -> dict:
    raw = strip_prefix(text)
    obj = ast.literal_eval(raw)
    if not isinstance(obj, dict):
        raise ValueError(f"not a mapping: {text!r}")
    return obj


def fmt(mapping: dict) -> str:
    inner = ", ".join(f"{k!r}: {v!r}" for k, v in mapping.items())
    return "{" + inner + "}"


def classify(mapping: dict, obj: dict | None) -> str:
    keys = tuple(mapping)
    try:
        sk = tuple(sorted(mapping))
    except TypeError:
        if obj is not None and keys == tuple(obj):
            return "insertion-order"
        return "unsortable"
    is_sorted = keys == sk
    if obj is None:
        return "sorted-keys" if is_sorted else "insertion-order"
    if is_sorted:
        return "sorted-keys"
    if keys == tuple(obj):
        return "insertion-order"
    return "other"


def inspect(displays: list[tuple[str, dict]], obj: dict | None = None) -> str:
    rows: list[tuple] = []
    if obj is not None:
        rows.append(("obj", fmt(obj)))
        rows.append(("obj_keys", *(repr(k) for k in obj)))
        try:
            sk = tuple(sorted(obj))
            rows.append(("sorted_keys", *(repr(k) for k in sk)))
        except TypeError:
            rows.append(("sorted_keys", "unsortable"))
    for name, mapping in displays:
        rows.append(("display", name, fmt(mapping), classify(mapping, obj)))
    try:
        item_sets = [frozenset(m.items()) for _, m in displays]
        if obj is not None:
            item_sets.append(frozenset(obj.items()))
        same = bool(item_sets) and all(s == item_sets[0] for s in item_sets)
    except TypeError:
        same = False
    rows.append(("same_items", "yes" if same else "no"))
    orders = [tuple(m) for _, m in displays]
    disagree = len(set(orders)) > 1
    rows.append(("disagree", "yes" if disagree else "no"))
    if same and displays:
        obj_keys = tuple(obj) if obj is not None else None
        if obj_keys is None:
            unsorted = []
            for _, mapping in displays:
                keys = tuple(mapping)
                try:
                    sk = tuple(sorted(mapping))
                except TypeError:
                    unsorted.append(keys)
                    continue
                if keys != sk:
                    unsorted.append(keys)
            uniq = list(dict.fromkeys(unsorted))
            if len(uniq) == 1:
                obj_keys = uniq[0]
        if obj_keys is not None:
            try:
                sk = tuple(sorted(dict(displays[0][1])))
            except TypeError:
                sk = None
            reordered: list[str] = []
            faithful: list[str] = []
            for name, mapping in displays:
                keys = tuple(mapping)
                if keys == obj_keys:
                    faithful.append(name)
                elif sk is not None and keys == sk:
                    reordered.append(name)
            rows.append(("reordered", *(reordered if reordered else ("none",))))
            rows.append(("faithful", *(faithful if faithful else ("none",))))
    return "\n".join("\t".join(str(p) for p in row) for row in rows) + "\n"


def parse_file_text(text: str) -> tuple[str | None, list[tuple[str, str]]]:
    obj_text = None
    displays: list[tuple[str, str]] = []
    anon = 0
    for line in text.splitlines():
        stripped = line.strip()
        if not stripped or stripped.startswith("#"):
            continue
        if "\t" in line:
            name, mapping = line.split("\t", 1)
            name = name.strip()
            mapping = mapping.strip()
            if name == "obj":
                obj_text = mapping
                continue
            displays.append((name, mapping))
        else:
            displays.append((str(anon), stripped))
            anon += 1
    return obj_text, displays


def replica_cli(argv: list[str]) -> tuple[str, str, int]:
    """Minimal argv interpreter matching keyorder's inspect path (no import)."""
    obj_text = None
    displays: list[tuple[str, str]] = []
    fixture = False
    file_path = None
    positionals: list[str] = []
    i = 0
    while i < len(argv):
        a = argv[i]
        if a == "--fixture":
            fixture = True
        elif a == "--obj":
            i += 1
            obj_text = argv[i]
        elif a == "--file":
            i += 1
            file_path = argv[i]
        else:
            positionals.append(a)
        i += 1
    if fixture:
        owned = {1: 0, 0: 0}
        obj_text = fmt(owned)
        displays.append(("pretty", "{" + ", ".join(f"{k!r}: {owned[k]!r}" for k in sorted(owned)) + "}"))
        displays.append(("repr", fmt(owned)))
    if file_path is not None:
        if file_path == "-":
            text = sys.stdin.read()
        else:
            try:
                text = Path(file_path).read_text(encoding="utf-8")
            except FileNotFoundError:
                return "", f"keyorder: file not found: {file_path}\n", 1
        file_obj, file_displays = parse_file_text(text)
        if file_obj is not None and obj_text is None:
            obj_text = file_obj
        displays.extend(file_displays)
    for n, item in enumerate(positionals):
        displays.append((str(n), item))
    if not displays:
        return "", "keyorder: need a mapping display, --file, or --fixture\n", 2
    try:
        obj = parse_mapping(obj_text) if obj_text is not None else None
        parsed = [(name, parse_mapping(text)) for name, text in displays]
    except (ValueError, SyntaxError) as err:
        msg = str(err)
        if not msg.startswith("not a mapping"):
            msg = f"not a mapping literal: {err}"
        return "", f"keyorder: {err}\n", 2
    return inspect(parsed, obj=obj), "", 0


def run_cli(args: list[str], stdin_text: str | None = None) -> tuple[str, str, int]:
    proc = subprocess.run(
        [sys.executable, str(CLI), *args],
        check=False,
        capture_output=True,
        text=True,
        input=stdin_text,
    )
    return proc.stdout, proc.stderr, proc.returncode


def json_label(obj_text: str, display_text: str) -> str:
    obj = json.loads(obj_text)
    d = json.loads(display_text)
    keys = list(d)
    sk = sorted(d)
    if keys == sk:
        return "sorted-keys"
    if keys == list(obj):
        return "insertion-order"
    return "other"


def main() -> None:
    cases: list[tuple[str, list[str], str | None]] = [
        ("fixture", ["--fixture"], None),
        ("two_prints_file", ["--obj", "{1: 0, 0: 0}", "--file", str(FX / "two_prints.txt")], None),
        ("two_prints_obj_row", ["--file", str(FX / "two_prints_obj.txt")], None),
        ("agree", ["--obj", "{0: 0, 1: 0}", "--file", str(FX / "agree.txt")], None),
        ("three_views", ["--file", str(FX / "three_views.txt")], None),
        ("positional_owned", ["--obj", "{1: 0, 0: 0}", "{0: 0, 1: 0}", "{1: 0, 0: 0}"], None),
        ("infer_no_obj", ["{0: 0, 1: 0}", "{1: 0, 0: 0}"], None),
        ("spacing", ["--obj", "{1:0,0:0}", "{0:0,1:0}", "{1:0,0:0}"], None),
        ("prefixed", ["--obj", "{1: 0, 0: 0}", "d = {0: 0, 1: 0}", "d={1: 0, 0: 0}"], None),
        ("different_items", ["--obj", "{1: 0, 0: 0}", "{0: 1, 1: 1}"], None),
        ("one_sorted_vs_obj", ["--obj", "{1: 0, 0: 0}", "{0: 0, 1: 0}"], None),
        ("two_unsorted", ["{2: 0, 0: 0, 1: 0}", "{1: 0, 0: 0, 2: 0}", "{0: 0, 1: 0, 2: 0}"], None),
        ("other_permutation", ["--obj", "{1: 0, 0: 0, 2: 0}", "{2: 0, 1: 0, 0: 0}", "{1: 0, 0: 0, 2: 0}"], None),
        ("wrong_obj_sorted", ["--obj", "{0: 0, 1: 0}", "{1: 0, 0: 0}", "{0: 0, 1: 0}"], None),
        ("lone_unsorted", ["{1: 0, 0: 0}"], None),
        ("json_string_keys", ["--obj", '{"b": 1, "a": 0}', '{"a": 0, "b": 1}', '{"b": 1, "a": 0}'], None),
        ("json_sorted_obj", ["--obj", '{"a": 0, "b": 1}', '{"a": 0, "b": 1}', '{"b": 1, "a": 0}'], None),
        ("json_three_perm", ['{"c": 0, "a": 0, "b": 0}', '{"b": 0, "a": 0, "c": 0}', '{"a": 0, "b": 0, "c": 0}'], None),
        ("json_dumps_pair", None, None),  # filled below
        ("true_vs_1", ["--obj", "{1: 0, 0: 0}", "{True: 0, 0: 0}"], None),
        ("float_vs_int", ["--obj", "{1: 0, 0: 0}", "{1.0: 0, 0: 0}"], None),
        ("false_zero_collapse", ["{False: 1, 0: 2}", "{0: 2}"], None),
        ("tuple_keys", ["--obj", "{(1, 0): 0, (0, 1): 0}", "{(0, 1): 0, (1, 0): 0}", "{(1, 0): 0, (0, 1): 0}"], None),
        ("bytes_keys", ["--obj", "{b'b': 0, b'a': 0}", "{b'a': 0, b'b': 0}", "{b'b': 0, b'a': 0}"], None),
        ("unicode_keys", ["--obj", "{'箱': 0, 'a': 0}", "{'a': 0, '箱': 0}", "{'箱': 0, 'a': 0}"], None),
        ("numeric_string", ["--obj", "{'10': 0, '2': 0}", "{'10': 0, '2': 0}", "{'2': 0, '10': 0}"], None),
        ("empty_dicts", ["--obj", "{}", "{}", "{}"], None),
        ("single_key", ["--obj", "{1: 0}", "{1: 0}"], None),
        ("three_int_pprint", ["--obj", "{3: 0, 1: 0, 2: 0}", "{1: 0, 2: 0, 3: 0}", "{3: 0, 1: 0, 2: 0}"], None),
    ]

    # json.dumps pair as caller JSON texts
    obj_js = json.dumps({"b": 1, "a": 0}, separators=(", ", ": "))
    sorted_js = json.dumps({"b": 1, "a": 0}, sort_keys=True, separators=(", ", ": "))
    cases[18] = ("json_dumps_pair", ["--obj", obj_js, sorted_js, obj_js], None)

    results = []
    n_ok = 0
    n_fail = 0
    for name, args, stdin_text in cases:
        cli_out, cli_err, cli_rc = run_cli(args, stdin_text)
        # replica inspect path only for rc=0 parseable cases
        try:
            rec_out, rec_err, rec_rc = replica_cli(args)
        except Exception as exc:  # noqa: BLE001
            rec_out, rec_err, rec_rc = "", f"replica-exc: {exc}\n", 99
        same = cli_out == rec_out and cli_rc == rec_rc
        if same:
            n_ok += 1
            status = "IDENTICAL"
        else:
            n_fail += 1
            status = "DIFF"
        results.append((name, status, cli_rc, rec_rc, len(cli_out), same))
        if not same:
            (SCRATCH / f"diff-{name}.cli.out").write_text(cli_out)
            (SCRATCH / f"diff-{name}.rec.out").write_text(rec_out)
            (SCRATCH / f"diff-{name}.cli.err").write_text(cli_err)
            (SCRATCH / f"diff-{name}.rec.err").write_text(rec_err)
            print(f"DIFF {name} cli_rc={cli_rc} rec_rc={rec_rc}")
            print("--- cli ---")
            print(cli_out)
            print("--- rec ---")
            print(rec_out)
        else:
            print(f"IDENTICAL {name} rc={cli_rc} bytes={len(cli_out)}")

    print(f"REPLICA {n_ok}/{n_ok + n_fail} identical")

    # JSON-only one-liner vs CLI labels
    json_cases = [
        ("json_string_keys", '{"b": 1, "a": 0}', ['{"a": 0, "b": 1}', '{"b": 1, "a": 0}']),
        ("json_dumps", obj_js, [sorted_js, obj_js]),
        ("json_agree", '{"a": 0, "b": 1}', ['{"a": 0, "b": 1}']),
        ("json_three", '{"c": 0, "a": 0, "b": 0}', ['{"a": 0, "b": 0, "c": 0}', '{"c": 0, "a": 0, "b": 0}']),
    ]
    json_ok = 0
    json_n = 0
    for name, obj_text, displays in json_cases:
        cli_out, _, cli_rc = run_cli(["--obj", obj_text, *displays])
        labels = []
        for line in cli_out.splitlines():
            parts = line.split("\t")
            if parts[:1] == ["display"] and len(parts) >= 4:
                labels.append(parts[3])
        predicted = [json_label(obj_text, d) for d in displays]
        json_n += 1
        match = labels == predicted and cli_rc == 0
        if match:
            json_ok += 1
        print(f"JSON_LABEL {name} cli={labels} json.loads={predicted} match={match} rc={cli_rc}")
    print(f"JSON_LABEL {json_ok}/{json_n}")

    # mutation leftover attacks
    attacks = []

    def attack(name, args, stdin_text=None):
        out, err, rc = run_cli(args, stdin_text)
        attacks.append((name, rc, out, err))
        print(f"ATTACK {name} rc={rc}")
        if out:
            print(out, end="" if out.endswith("\n") else "\n")
        if err:
            print("STDERR", err, end="" if err.endswith("\n") else "\n")

    attack("nested_crash", ["--obj", "{1: {0: 1, 1: 0}}", "{1: {1: 0, 0: 1}}", "{1: {0: 1, 1: 0}}"])
    attack("list_values", ["{1: [0], 0: [1]}"])
    attack("list_d_refused", ["--obj", "{1: 0, 0: 0}", "[1, 0]", "{0: 0, 1: 0}"])
    attack("disagree_skips_obj", ["--obj", "{1: 0, 0: 0}", "{0: 0, 1: 0}"])
    attack("reordered_none_other", ["--obj", "{1: 0, 0: 0, 2: 0}", "{2: 0, 1: 0, 0: 0}", "{1: 0, 0: 0, 2: 0}"])
    attack("json_true_literal", ["--obj", '{"ok": true}', '{"ok": true}'])
    attack("json_null", ['{"a": null}'])
    attack("empty_file", ["--file", "/dev/null"])
    attack("dump_blob", ["--file", str(RUN / "specimens/specimen-034/OBSERVED.md")])

    # jq analog
    print("=== jq keys vs keys_unsorted ===")
    jq_obj = '{"b": 1, "a": 0}'
    for label, filt in [("unsorted", "keys_unsorted"), ("sorted", "keys")]:
        proc = subprocess.run(
            ["jq", "-r", f'{filt} | join(" ")'],
            input=jq_obj,
            text=True,
            capture_output=True,
            check=False,
        )
        print(f"jq {label} rc={proc.returncode} out={proc.stdout!r}")

    print("=== python json.dumps sort_keys vs insertion ===")
    d = {"b": 1, "a": 0}
    print("insertion", json.dumps(d, separators=(", ", ": ")))
    print("sort_keys", json.dumps(d, sort_keys=True, separators=(", ", ": ")))
    print("list", list(d), "sorted", sorted(d))

    print("=== python one-liner owned pair ===")
    print(
        subprocess.run(
            [
                sys.executable,
                "-c",
                "import ast\n"
                "obj=ast.literal_eval('{1: 0, 0: 0}')\n"
                "for s in ['{0: 0, 1: 0}','{1: 0, 0: 0}']:\n"
                " d=ast.literal_eval(s)\n"
                " print(list(d), 'sorted' if list(d)==sorted(d) else 'not-sorted',"
                " 'matches_obj' if list(d)==list(obj) else 'differs')\n",
            ],
            capture_output=True,
            text=True,
            check=False,
        ).stdout,
        end="",
    )


if __name__ == "__main__":
    main()
