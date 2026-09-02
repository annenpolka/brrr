#!/usr/bin/env python3
"""owned false_green, unrelated green, invalidation, incomplete, cap."""

from __future__ import annotations

import importlib.machinery
import importlib.util
import subprocess
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CLI = ROOT / "greendep"
FIX = ROOT / "fixtures"


def load_mod():
    loader = importlib.machinery.SourceFileLoader("greendep_cli", str(CLI))
    spec = importlib.util.spec_from_loader(loader.name, loader)
    assert spec is not None
    mod = importlib.util.module_from_spec(spec)
    loader.exec_module(mod)
    return mod


GD = load_mod()


def run_cli(args: list[str], stdin: str | None = None) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [sys.executable, str(CLI), *args],
        input=stdin,
        capture_output=True,
        text=True,
        check=False,
    )


def last_row(text: str, key: str) -> list[str]:
    found: list[str] | None = None
    for line in text.splitlines():
        if not line or "\t" not in line:
            continue
        name, *rest = line.split("\t")
        if name == key:
            found = rest
    if found is None:
        raise AssertionError(f"missing {key!r} in\n{text}")
    return found


def pair_rows(text: str, key: str) -> list[tuple[str, str]]:
    pairs: list[tuple[str, str]] = []
    for line in text.splitlines():
        if not line.startswith(key + "\t"):
            continue
        rest = line.split("\t")[1:]
        if rest == ["-"]:
            return []
        if len(rest) != 4 or rest[0] != "query" or rest[2] != "dep":
            raise AssertionError(f"bad {key} row {line!r}")
        pairs.append((rest[1], rest[3]))
    return pairs


class Owned075(unittest.TestCase):
    def test_poll_false_green_unrecorded_error(self):
        proc = run_cli([str(FIX / "075-poll.rec")])
        self.assertEqual(proc.returncode, 1, proc.stderr + proc.stdout)
        self.assertEqual(last_row(proc.stdout, "false_green"), ["typeck_of(S::poll)"])
        self.assertEqual(last_row(proc.stdout, "false_green_n"), ["1"])
        self.assertEqual(last_row(proc.stdout, "green"), ["typeck_of(S::poll)"])
        self.assertEqual(
            pair_rows(proc.stdout, "unrecorded_changed"),
            [("typeck_of(S::poll)", "type_of(Error)")],
        )
        self.assertEqual(pair_rows(proc.stdout, "invalidation"), [])
        self.assertEqual(last_row(proc.stdout, "invalidation"), ["-"])
        self.assertEqual(last_row(proc.stdout, "incomplete"), ["no"])
        self.assertNotIn("->", proc.stdout.split("unrecorded_changed", 1)[1])

    def test_green_fixture_same_join_other_spelling(self):
        proc = run_cli([str(FIX / "075-green.rec")])
        self.assertEqual(proc.returncode, 1, proc.stderr)
        self.assertEqual(last_row(proc.stdout, "false_green"), ["typeck_of(poll)"])
        self.assertEqual(
            pair_rows(proc.stdout, "unrecorded_changed"),
            [("typeck_of(poll)", "type_of(Error)")],
        )
        self.assertEqual(pair_rows(proc.stdout, "changed"), [("typeck_of(poll)", "type_of(Error)")])

    def test_stdin(self):
        proc = run_cli(["-"], stdin=(FIX / "075-poll.rec").read_text())
        self.assertEqual(proc.returncode, 1, proc.stderr)
        self.assertEqual(last_row(proc.stdout, "false_green"), ["typeck_of(S::poll)"])

    def test_missing(self):
        proc = run_cli(["/no"])
        self.assertEqual(proc.returncode, 1)
        self.assertIn("greendep:", proc.stderr)


class UnrelatedGreen(unittest.TestCase):
    def test_only_owner_is_false_green(self):
        proc = run_cli([str(FIX / "unrelated.rec")])
        self.assertEqual(proc.returncode, 1, proc.stderr + proc.stdout)
        self.assertEqual(last_row(proc.stdout, "false_green"), ["typeck_of(S::poll)"])
        self.assertEqual(
            last_row(proc.stdout, "green"),
            ["typeck_of(S::poll)", "typeck_of(unrelated)"],
        )
        self.assertEqual(
            pair_rows(proc.stdout, "unrecorded_changed"),
            [("typeck_of(S::poll)", "type_of(Error)")],
        )
        self.assertNotIn("typeck_of(unrelated)", "\t".join(last_row(proc.stdout, "false_green")))

    def test_shorthand_changed_with_two_greens_is_error(self):
        rec = (
            "query\ttypeck_of(S::poll)\tgreen\n"
            "query\ttypeck_of(unrelated)\tgreen\n"
            "dep\ttypeck_of(S::poll)\ttrait_def\n"
            "changed\ttype_of(Error)\n"
        )
        proc = run_cli(["-"], stdin=rec)
        self.assertEqual(proc.returncode, 1)
        self.assertEqual(proc.stdout, "")
        self.assertIn("exactly one green", proc.stderr)

    def test_global_changed_list_is_error(self):
        rec = (
            "query\ttypeck_of(S::poll)\tgreen\n"
            "changed\ttype_of(Error)\tadt_def\ttrait_def\n"
        )
        proc = run_cli(["-"], stdin=rec)
        self.assertEqual(proc.returncode, 1)
        self.assertIn("not a global list", proc.stderr)


class Invalidation(unittest.TestCase):
    def test_agree_red_is_not_invalidation(self):
        proc = run_cli([str(FIX / "agree.rec")])
        self.assertEqual(proc.returncode, 0, proc.stderr + proc.stdout)
        self.assertEqual(last_row(proc.stdout, "false_green"), ["-"])
        self.assertEqual(last_row(proc.stdout, "false_green_n"), ["0"])
        self.assertEqual(pair_rows(proc.stdout, "invalidation"), [])
        self.assertEqual(pair_rows(proc.stdout, "unrecorded_changed"), [])

    def test_recorded_changed_green_is_invalidation(self):
        proc = run_cli([str(FIX / "unseen-recorded.rec")])
        self.assertEqual(proc.returncode, 1, proc.stderr + proc.stdout)
        self.assertEqual(last_row(proc.stdout, "false_green"), ["-"])
        self.assertEqual(last_row(proc.stdout, "false_green_n"), ["0"])
        self.assertEqual(
            pair_rows(proc.stdout, "invalidation"),
            [("typeck_of(poll)", "type_of(Error)")],
        )
        self.assertEqual(last_row(proc.stdout, "invalidation_n"), ["1"])
        self.assertEqual(pair_rows(proc.stdout, "unrecorded_changed"), [])
        self.assertEqual(last_row(proc.stdout, "incomplete"), ["no"])

    def test_both_kinds_print(self):
        proc = run_cli([str(FIX / "both.rec")])
        self.assertEqual(proc.returncode, 1, proc.stderr + proc.stdout)
        self.assertEqual(last_row(proc.stdout, "false_green"), ["typeck_of(S::poll)"])
        self.assertEqual(
            pair_rows(proc.stdout, "unrecorded_changed"),
            [("typeck_of(S::poll)", "adt_def")],
        )
        self.assertEqual(
            pair_rows(proc.stdout, "invalidation"),
            [("typeck_of(S::poll)", "type_of(Error)")],
        )

    def test_other_query_changed_does_not_invalidate(self):
        rec = (
            "query\ttypeck_of(S::poll)\tgreen\n"
            "query\ttypeck_of(unrelated)\tgreen\n"
            "dep\ttypeck_of(S::poll)\ttype_of(Error)\n"
            "changed\ttypeck_of(unrelated)\ttype_of(Error)\n"
        )
        proc = run_cli(["-"], stdin=rec)
        self.assertEqual(proc.returncode, 1, proc.stderr + proc.stdout)
        self.assertEqual(last_row(proc.stdout, "false_green"), ["typeck_of(unrelated)"])
        self.assertEqual(pair_rows(proc.stdout, "invalidation"), [])
        self.assertEqual(last_row(proc.stdout, "incomplete"), ["no"])


class PairEncoding(unittest.TestCase):
    def test_arrow_names_are_opaque_tsv_fields(self):
        proc = run_cli([str(FIX / "arrows.rec")])
        self.assertEqual(proc.returncode, 1, proc.stderr)
        self.assertEqual(pair_rows(proc.stdout, "unrecorded_changed"), [("a->b", "e->f")])
        self.assertNotIn("a->b->e->f", proc.stdout)
        self.assertIn("unrecorded_changed\tquery\ta->b\tdep\te->f\n", proc.stdout)

    def test_rustc_dump_refused(self):
        proc = run_cli(["-"], stdin="typeck_of(S::poll) -> type_of(Error)\n")
        self.assertEqual(proc.returncode, 1)
        self.assertEqual(proc.stdout, "")
        self.assertIn("rustc-shaped q -> d dump is not an input", proc.stderr)
        self.assertIn("query/dep/changed TSV", proc.stderr)

    def test_dep_arrow_without_tabs_is_not_an_edge(self):
        proc = run_cli(["-"], stdin="query\tq\tgreen\ndep\tq->d\nchanged\td\n")
        self.assertEqual(proc.returncode, 1)
        self.assertIn("dep needs query and dep name", proc.stderr)

    def test_inspect_is_own_set_difference(self):
        rec = GD.parse_record(
            "query\tpoll\tgreen\nquery\tunrelated\tgreen\n"
            "dep\tpoll\ttrait_def\nchanged\tpoll\tError\n",
            source="t",
        )
        result = GD.inspect(rec)
        self.assertEqual(result["false_green"], ["poll"])
        self.assertEqual(result["unrecorded_changed"], [("poll", "Error")])
        self.assertEqual(result["invalidation"], [])
        self.assertFalse(result["incomplete"])


class UnseenConst(unittest.TestCase):
    def test_eval_const_unrecorded_inner(self):
        proc = run_cli([str(FIX / "unseen-const.rec")])
        self.assertEqual(proc.returncode, 1, proc.stderr)
        self.assertEqual(last_row(proc.stdout, "false_green"), ["eval_const(N)"])
        self.assertEqual(
            pair_rows(proc.stdout, "unrecorded_changed"),
            [("eval_const(N)", "type_of(Inner)")],
        )


class Incomplete(unittest.TestCase):
    def test_green_plus_dep_without_changed_is_incomplete(self):
        proc = run_cli([str(FIX / "incomplete.rec")])
        self.assertEqual(proc.returncode, 2, proc.stderr + proc.stdout)
        self.assertEqual(last_row(proc.stdout, "incomplete"), ["yes"])
        self.assertEqual(last_row(proc.stdout, "false_green"), ["-"])
        self.assertEqual(last_row(proc.stdout, "false_green_n"), ["0"])
        self.assertEqual(pair_rows(proc.stdout, "changed"), [])

    def test_green_only_is_incomplete(self):
        proc = run_cli(["-"], stdin="query\ta\tgreen\n")
        self.assertEqual(proc.returncode, 2, proc.stderr + proc.stdout)
        self.assertEqual(last_row(proc.stdout, "incomplete"), ["yes"])
        self.assertEqual(last_row(proc.stdout, "false_green"), ["-"])

    def test_harvest_colors_without_changed_is_incomplete(self):
        rec = (
            "query\ttypeck_of(poll)\tgreen\n"
            "query\ttype_of(Error)\tred\n"
            "dep\ttypeck_of(poll)\ttrait_def\n"
        )
        proc = run_cli(["-"], stdin=rec)
        self.assertEqual(proc.returncode, 2, proc.stderr + proc.stdout)
        self.assertEqual(last_row(proc.stdout, "incomplete"), ["yes"])
        self.assertEqual(last_row(proc.stdout, "false_green"), ["-"])

    def test_changed_tab_only_is_empty_changed_not_parse_error(self):
        proc = run_cli(["-"], stdin="query\ta\tgreen\nchanged\t\n")
        self.assertEqual(proc.returncode, 2, proc.stderr + proc.stdout)
        self.assertEqual(proc.stderr, "")
        self.assertEqual(last_row(proc.stdout, "incomplete"), ["yes"])
        self.assertEqual(pair_rows(proc.stdout, "changed"), [])

    def test_red_only_without_changed_is_complete(self):
        proc = run_cli(["-"], stdin="query\ta\tred\n")
        self.assertEqual(proc.returncode, 0, proc.stderr + proc.stdout)
        self.assertEqual(last_row(proc.stdout, "incomplete"), ["no"])
        self.assertEqual(last_row(proc.stdout, "green"), ["-"])


class NamesAndColors(unittest.TestCase):
    def test_minus_query_is_not_a_legal_name(self):
        proc = run_cli(["-"], stdin="query\t-\tgreen\nchanged\tq\tD\n")
        self.assertEqual(proc.returncode, 1)
        self.assertEqual(proc.stdout, "")
        self.assertIn("not a legal NAME", proc.stderr)

    def test_minus_changed_dep_is_not_a_legal_name(self):
        proc = run_cli(["-"], stdin="query\tq\tgreen\nchanged\tq\t-\n")
        self.assertEqual(proc.returncode, 1)
        self.assertEqual(proc.stdout, "")
        self.assertIn("not a legal NAME", proc.stderr)

    def test_empty_false_green_sentinel_is_count_zero(self):
        proc = run_cli([str(FIX / "unseen-recorded.rec")])
        self.assertEqual(last_row(proc.stdout, "false_green"), ["-"])
        self.assertEqual(last_row(proc.stdout, "false_green_n"), ["0"])
        self.assertIn("false_green\t-\n", proc.stdout)
        self.assertNotIn("query\t-\t", proc.stdout)

    def test_true_is_not_green(self):
        proc = run_cli(["-"], stdin="query\ta\ttrue\nchanged\ta\tx\n")
        self.assertEqual(proc.returncode, 1)
        self.assertEqual(proc.stdout, "")
        self.assertIn("not green or red", proc.stderr)


class Cap(unittest.TestCase):
    def test_two_thousand_own_changed_greens_are_capped(self):
        lines = []
        for i in range(2000):
            lines.append(f"query\tg{i}\tgreen")
            lines.append(f"changed\tg{i}\tD{i}")
        proc = run_cli(["-"], stdin="\n".join(lines) + "\n")
        self.assertEqual(proc.returncode, 1, proc.stderr)
        self.assertEqual(last_row(proc.stdout, "false_green_n"), ["2000"])
        self.assertEqual(last_row(proc.stdout, "unrecorded_changed_n"), ["2000"])
        self.assertEqual(last_row(proc.stdout, "green_n"), ["2000"])
        shown = last_row(proc.stdout, "false_green")
        self.assertEqual(len(shown), GD.LIST_CAP)
        self.assertEqual(shown, [f"g{i}" for i in range(GD.LIST_CAP)])
        self.assertEqual(len(pair_rows(proc.stdout, "unrecorded_changed")), GD.LIST_CAP)
        self.assertNotIn("g1999", proc.stdout)
        self.assertLess(len(proc.stdout), 50_000)
        self.assertEqual(last_row(proc.stdout, "incomplete"), ["no"])

    def test_two_thousand_greens_one_changed_is_still_per_query(self):
        lines = [f"query\tg{i}\tgreen" for i in range(2000)]
        lines.append("changed\tg0\tD")
        proc = run_cli(["-"], stdin="\n".join(lines) + "\n")
        self.assertEqual(proc.returncode, 1, proc.stderr)
        self.assertEqual(last_row(proc.stdout, "false_green"), ["g0"])
        self.assertEqual(last_row(proc.stdout, "false_green_n"), ["1"])
        self.assertNotIn("g1", "\t".join(last_row(proc.stdout, "false_green")))

    def test_huge_name_is_truncated_in_stdout(self):
        name = "N" * 200_000
        rec = f"query\t{name}\tgreen\nchanged\t{name}\tD\n"
        proc = run_cli(["-"], stdin=rec)
        self.assertEqual(proc.returncode, 1, proc.stderr)
        self.assertEqual(last_row(proc.stdout, "false_green_n"), ["1"])
        shown = last_row(proc.stdout, "false_green")[0]
        self.assertEqual(shown, "N" * GD.NAME_CAP + "...")
        self.assertNotIn(name, proc.stdout)
        self.assertLess(len(proc.stdout), 10_000)


if __name__ == "__main__":
    unittest.main()
