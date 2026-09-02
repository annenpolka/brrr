#!/usr/bin/env python3
"""completed-only work units requeue into an empty send the replacement receives."""

from __future__ import annotations

import importlib.machinery
import importlib.util
import json
import subprocess
import sys
import unittest
from collections import OrderedDict
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CLI = ROOT / "emptyunit"
FIX = ROOT / "fixtures"


def load_mod():
    loader = importlib.machinery.SourceFileLoader("emptyunit_cli", str(CLI))
    spec = importlib.util.spec_from_loader(loader.name, loader)
    assert spec is not None
    mod = importlib.util.module_from_spec(spec)
    loader.exec_module(mod)
    return mod


EU = load_mod()


def run_cli(*args: str, input_text: str | None = None) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [sys.executable, str(CLI), *args],
        input=input_text,
        capture_output=True,
        text=True,
        check=False,
    )


def parse_rows(text: str) -> dict[str, list[str]]:
    rows: dict[str, list[str]] = {}
    for line in text.splitlines():
        if not line or "\t" not in line:
            continue
        name, *rest = line.split("\t")
        rows[name] = rest
    return rows


class Specimen063Tests(unittest.TestCase):
    def test_owned_hang_is_next_assign_empty_send(self):
        rec = EU.parse_record((FIX / "063-hang.json").read_text(), source="hang")
        result = EU.inspect(rec)
        self.assertTrue(result["hang_risk"])
        self.assertEqual(result["dist"], "loadgroup")
        self.assertEqual(result["pending"], 1)
        self.assertTrue(result["requeued"])
        self.assertEqual(result["completed_only"], ["testing/test_timeout.py::test_1"])
        self.assertEqual(result["incomplete_scopes"], ["testing/test_timeout.py::test_2"])
        self.assertEqual(result["first_assigned"], "testing/test_timeout.py::test_1")
        self.assertEqual(result["would_send"], [])
        self.assertEqual(result["assigned"], ["testing/test_timeout.py::test_1"])
        self.assertFalse(result["reschedule"])
        self.assertEqual(result["hang_unit"], "testing/test_timeout.py::test_1")
        self.assertEqual(result["scopes"][0]["send"], [])
        self.assertTrue(result["scopes"][0]["empty_send"])
        self.assertEqual(result["scopes"][1]["send"], [1])

    def test_cli_owned_hang_json_rc1(self):
        proc = run_cli(str(FIX / "063-hang.json"))
        self.assertEqual(proc.returncode, 1, proc.stderr)
        rows = parse_rows(proc.stdout)
        self.assertEqual(rows["hang_risk"], ["yes"])
        self.assertEqual(rows["first_assigned"], ["testing/test_timeout.py::test_1"])
        self.assertEqual(rows["would_send"], ["()"])
        self.assertEqual(rows["assigned"], ["testing/test_timeout.py::test_1"])
        self.assertEqual(rows["reschedule"], ["no"])
        self.assertEqual(rows["hang_unit"], ["testing/test_timeout.py::test_1"])
        self.assertEqual(rows["completed_only"], ["testing/test_timeout.py::test_1"])
        self.assertEqual(rows["requeued"], ["yes"])
        self.assertEqual(rows["pending"], ["1"])
        self.assertEqual(rows["scopes_n"], ["2"])

    def test_python_workqueue_dump(self):
        proc = run_cli(str(FIX / "063-hang.dump"))
        self.assertEqual(proc.returncode, 1, proc.stderr)
        self.assertEqual(parse_rows(proc.stdout)["would_send"], ["()"])

    def test_unseen_mixed_loadscope_does_not_hang(self):
        proc = run_cli(str(FIX / "unseen-mixed.rec"))
        self.assertEqual(proc.returncode, 0, proc.stderr)
        rows = parse_rows(proc.stdout)
        self.assertEqual(rows["hang_risk"], ["no"])
        self.assertEqual(rows["dist"], ["loadscope"])
        self.assertEqual(rows["send"], ["(1,2)"])
        self.assertEqual(rows["empty_send"], ["no"])
        self.assertEqual(rows["completed_only"], ["-"])
        self.assertEqual(rows["would_send"], ["(1,2)"])

    def test_two_scopes_done_first_is_next_empty_send(self):
        proc = run_cli(str(FIX / "unseen-two-scopes.rec"))
        self.assertEqual(proc.returncode, 1, proc.stderr)
        rows = parse_rows(proc.stdout)
        self.assertEqual(rows["hang_risk"], ["yes"])
        self.assertEqual(rows["first_assigned"], ["done.py::t"])
        self.assertEqual(rows["would_send"], ["()"])
        self.assertEqual(rows["assigned"], ["done.py::t"])
        self.assertEqual(rows["reschedule"], ["no"])
        self.assertEqual(rows["hang_unit"], ["done.py::t"])
        self.assertEqual(rows["completed_only"], ["done.py::t"])
        self.assertEqual(rows["incomplete_scopes"], ["live.py::u"])

    def test_live_first_reschedule_second_empty_send_is_hang(self):
        proc = run_cli(str(FIX / "unseen-live-first.rec"))
        self.assertEqual(proc.returncode, 1, proc.stderr)
        rows = parse_rows(proc.stdout)
        self.assertEqual(rows["hang_risk"], ["yes"])
        self.assertEqual(rows["first_assigned"], ["live.py::u"])
        self.assertEqual(rows["would_send"], ["(1)"])
        self.assertEqual(rows["assigned"], ["live.py::u", "done.py::t"])
        self.assertEqual(rows["reschedule"], ["yes"])
        self.assertEqual(rows["hang_unit"], ["done.py::t"])
        self.assertEqual(rows["completed_only"], ["done.py::t"])
        self.assertEqual(rows["incomplete_scopes"], ["live.py::u"])
        self.assertEqual(rows["requeued"], ["yes"])
        self.assertEqual(rows["empty_send"], ["yes"])

    def test_pending2_then_completed_only_reschedules_empty_send(self):
        proc = run_cli(str(FIX / "unseen-pending2.rec"))
        self.assertEqual(proc.returncode, 1, proc.stderr)
        rows = parse_rows(proc.stdout)
        self.assertEqual(rows["hang_risk"], ["yes"])
        self.assertEqual(rows["first_assigned"], ["a.py"])
        self.assertEqual(rows["would_send"], ["(0,1)"])
        self.assertEqual(rows["assigned"], ["a.py", "b.py"])
        self.assertEqual(rows["reschedule"], ["yes"])
        self.assertEqual(rows["hang_unit"], ["b.py"])
        self.assertEqual(rows["pending"], ["2"])

    def test_pending3_then_completed_only_does_not_reschedule(self):
        proc = run_cli(str(FIX / "unseen-pending3.rec"))
        self.assertEqual(proc.returncode, 0, proc.stderr)
        rows = parse_rows(proc.stdout)
        self.assertEqual(rows["hang_risk"], ["no"])
        self.assertEqual(rows["first_assigned"], ["a.py"])
        self.assertEqual(rows["would_send"], ["(0,1,2)"])
        self.assertEqual(rows["assigned"], ["a.py"])
        self.assertEqual(rows["reschedule"], ["no"])
        self.assertEqual(rows["hang_unit"], ["-"])
        self.assertEqual(rows["completed_only"], ["b.py"])
        self.assertEqual(rows["empty_send"], ["yes"])
        self.assertEqual(rows["pending"], ["3"])

    def test_three_units_live_done_live_second_is_hang(self):
        text = (
            "collection\tlive1.py::u\tdone.py::t\tlive2.py::u\n"
            "dist\tloadgroup\n"
            "unit\tlive1.py::u\tlive1.py::u\topen\n"
            "unit\tdone.py::t\tdone.py::t\tdone\n"
            "unit\tlive2.py::u\tlive2.py::u\topen\n"
        )
        proc = run_cli("-", input_text=text)
        self.assertEqual(proc.returncode, 1, proc.stderr)
        rows = parse_rows(proc.stdout)
        self.assertEqual(rows["hang_risk"], ["yes"])
        self.assertEqual(rows["assigned"], ["live1.py::u", "done.py::t"])
        self.assertEqual(rows["reschedule"], ["yes"])
        self.assertEqual(rows["hang_unit"], ["done.py::t"])
        self.assertEqual(rows["would_send"], ["(0)"])

    def test_two_live_units_reschedule_is_not_hang(self):
        text = (
            "collection\tlive1.py::u\tlive2.py::u\n"
            "dist\tloadgroup\n"
            "unit\tlive1.py::u\tlive1.py::u\topen\n"
            "unit\tlive2.py::u\tlive2.py::u\topen\n"
        )
        proc = run_cli("-", input_text=text)
        self.assertEqual(proc.returncode, 0, proc.stderr)
        rows = parse_rows(proc.stdout)
        self.assertEqual(rows["hang_risk"], ["no"])
        self.assertEqual(rows["assigned"], ["live1.py::u", "live2.py::u"])
        self.assertEqual(rows["reschedule"], ["yes"])
        self.assertEqual(rows["hang_unit"], ["-"])
        self.assertEqual(rows["completed_only"], ["-"])

    def test_json_live_first_dump_is_hang(self):
        text = (
            '{"collection":["live.py::u","done.py::t"],"dist":"loadgroup",'
            '"workqueue":{"live.py::u":{"live.py::u":false},'
            '"done.py::t":{"done.py::t":true}}}'
        )
        proc = run_cli("-", input_text=text)
        self.assertEqual(proc.returncode, 1, proc.stderr)
        rows = parse_rows(proc.stdout)
        self.assertEqual(rows["hang_risk"], ["yes"])
        self.assertEqual(rows["would_send"], ["(0)"])
        self.assertEqual(rows["assigned"], ["live.py::u", "done.py::t"])
        self.assertEqual(rows["hang_unit"], ["done.py::t"])

    def test_stdin_dump_and_missing_file(self):
        proc = run_cli("-", input_text=(FIX / "063-hang.json").read_text())
        self.assertEqual(proc.returncode, 1, proc.stderr)
        self.assertIn("hang_risk\tyes", proc.stdout)
        missing = run_cli("/no/such/emptyunit.rec")
        self.assertEqual(missing.returncode, 1)
        self.assertIn("emptyunit:", missing.stderr)

    def test_handwritten_module_both_done_is_not_the_hang(self):
        proc = run_cli(str(FIX / "063-hang.rec"))
        self.assertEqual(proc.returncode, 0, proc.stderr)
        rows = parse_rows(proc.stdout)
        self.assertEqual(rows["hang_risk"], ["no"])
        self.assertEqual(rows["pending"], ["0"])
        self.assertEqual(rows["requeued"], ["no"])
        self.assertEqual(rows["dist"], ["loadgroup"])
        self.assertEqual(rows["scopes_n"], ["2"])
        self.assertNotIn("scope mismatch", proc.stderr)

    def test_hang_log_is_refused(self):
        proc = run_cli(str(FIX / "hang_log.txt"))
        self.assertEqual(proc.returncode, 1)
        self.assertIn("not a workqueue dump", proc.stderr)

    def test_loadscope_all_done_is_not_requeued(self):
        proc = run_cli(str(FIX / "loadscope-alldone.rec"))
        self.assertEqual(proc.returncode, 0, proc.stderr)
        rows = parse_rows(proc.stdout)
        self.assertEqual(rows["pending"], ["0"])
        self.assertEqual(rows["requeued"], ["no"])
        self.assertEqual(rows["hang_risk"], ["no"])
        self.assertEqual(rows["first_assigned"], ["-"])
        self.assertEqual(rows["would_send"], ["-"])
        self.assertEqual(rows["empty_send"], ["yes"])

    def test_loadscope_open_sends_remaining(self):
        proc = run_cli(str(FIX / "loadscope-open.rec"))
        self.assertEqual(proc.returncode, 0, proc.stderr)
        rows = parse_rows(proc.stdout)
        self.assertEqual(rows["hang_risk"], ["no"])
        self.assertEqual(rows["send"], ["(1)"])
        self.assertEqual(rows["would_send"], ["(1)"])
        self.assertEqual(rows["completed_only"], ["-"])


class DistSchedulerTests(unittest.TestCase):
    def test_same_tests_loadgroup_vs_loadscope_without_caller_regroup(self):
        dump = {
            "collection": ["mod.py::a", "mod.py::b"],
            "workqueue": {
                "mod.py::a": {"mod.py::a": True},
                "mod.py::b": {"mod.py::b": False},
            },
        }
        group = run_cli("-", input_text=json.dumps({**dump, "dist": "loadgroup"}))
        scope = run_cli("-", input_text=json.dumps({**dump, "dist": "loadscope"}))
        self.assertEqual(group.returncode, 1, group.stderr)
        self.assertEqual(parse_rows(group.stdout)["hang_risk"], ["yes"])
        self.assertEqual(parse_rows(group.stdout)["would_send"], ["()"])
        self.assertEqual(parse_rows(group.stdout)["first_assigned"], ["mod.py::a"])
        self.assertEqual(parse_rows(group.stdout)["scopes_n"], ["2"])
        self.assertEqual(scope.returncode, 0, scope.stderr)
        self.assertEqual(parse_rows(scope.stdout)["hang_risk"], ["no"])
        self.assertEqual(parse_rows(scope.stdout)["would_send"], ["(1)"])
        self.assertEqual(parse_rows(scope.stdout)["first_assigned"], ["mod.py"])
        self.assertEqual(parse_rows(scope.stdout)["scopes_n"], ["1"])

    def test_owned_dump_forced_loadscope_is_not_hang(self):
        rec = json.loads((FIX / "063-hang.json").read_text())
        rec["dist"] = "loadscope"
        proc = run_cli("-", input_text=json.dumps(rec))
        self.assertEqual(proc.returncode, 0, proc.stderr)
        rows = parse_rows(proc.stdout)
        self.assertEqual(rows["hang_risk"], ["no"])
        self.assertEqual(rows["first_assigned"], ["testing/test_timeout.py"])
        self.assertEqual(rows["would_send"], ["(1)"])
        self.assertEqual(rows["scopes_n"], ["1"])
        self.assertNotIn("scope mismatch", proc.stderr)

    def test_loadgroup_ignores_module_shaped_caller_keys(self):
        dump = {
            "collection": ["mod.py::a", "mod.py::b"],
            "dist": "loadgroup",
            "workqueue": {"mod.py": {"mod.py::a": True, "mod.py::b": False}},
        }
        proc = run_cli("-", input_text=json.dumps(dump))
        self.assertEqual(proc.returncode, 1, proc.stderr)
        rows = parse_rows(proc.stdout)
        self.assertEqual(rows["hang_risk"], ["yes"])
        self.assertEqual(rows["first_assigned"], ["mod.py::a"])
        self.assertEqual(rows["would_send"], ["()"])
        self.assertEqual(rows["scopes_n"], ["2"])
        self.assertNotIn("scope mismatch", proc.stderr)

    def test_loadscope_class_rsplit(self):
        dump = {
            "collection": ["m.py::T::a", "m.py::T::b"],
            "dist": "loadscope",
            "workqueue": {
                "m.py::T::a": {"m.py::T::a": True},
                "m.py::T::b": {"m.py::T::b": False},
            },
        }
        proc = run_cli("-", input_text=json.dumps(dump))
        self.assertEqual(proc.returncode, 0, proc.stderr)
        rows = parse_rows(proc.stdout)
        self.assertEqual(rows["first_assigned"], ["m.py::T"])
        self.assertEqual(rows["hang_risk"], ["no"])
        self.assertEqual(rows["would_send"], ["(1)"])

    def test_loadgroup_at_group_is_one_unit(self):
        dump = {
            "collection": ["mod.py::a[1]@g", "mod.py::b[2]@g"],
            "dist": "loadgroup",
            "workqueue": {
                "mod.py::a[1]@g": {"mod.py::a[1]@g": True},
                "mod.py::b[2]@g": {"mod.py::b[2]@g": False},
            },
        }
        proc = run_cli("-", input_text=json.dumps(dump))
        self.assertEqual(proc.returncode, 0, proc.stderr)
        rows = parse_rows(proc.stdout)
        self.assertEqual(rows["hang_risk"], ["no"])
        self.assertEqual(rows["first_assigned"], ["g"])
        self.assertEqual(rows["would_send"], ["(1)"])
        self.assertEqual(rows["scopes_n"], ["1"])


class IngestTests(unittest.TestCase):
    def test_ordereddict_print_workqueue_ingests(self):
        proc = run_cli(str(FIX / "063-hang.wq"))
        self.assertEqual(proc.returncode, 1, proc.stderr)
        rows = parse_rows(proc.stdout)
        self.assertEqual(rows["hang_risk"], ["yes"])
        self.assertEqual(rows["would_send"], ["()"])
        self.assertEqual(rows["first_assigned"], ["testing/test_timeout.py::test_1"])

    def test_collection_list_plus_ordereddict(self):
        wq = OrderedDict(
            [
                (
                    "testing/test_timeout.py::test_1",
                    OrderedDict([("testing/test_timeout.py::test_1", True)]),
                ),
                (
                    "testing/test_timeout.py::test_2",
                    OrderedDict([("testing/test_timeout.py::test_2", False)]),
                ),
            ]
        )
        text = (
            "['testing/test_timeout.py::test_1', 'testing/test_timeout.py::test_2']\n"
            + repr(wq)
        )
        proc = run_cli("-", input_text=text)
        self.assertEqual(proc.returncode, 1, proc.stderr)
        self.assertEqual(parse_rows(proc.stdout)["hang_risk"], ["yes"])
        self.assertEqual(parse_rows(proc.stdout)["would_send"], ["()"])

    def test_bare_workqueue_dict_infers_collection(self):
        text = "{'mod.py::a': {'mod.py::a': False}}"
        proc = run_cli("-", input_text=text)
        self.assertEqual(proc.returncode, 0, proc.stderr)
        rows = parse_rows(proc.stdout)
        self.assertEqual(rows["collection"], ["mod.py::a"])
        self.assertEqual(rows["hang_risk"], ["no"])
        self.assertEqual(rows["send"], ["(0)"])

    def test_empty_workqueue_does_not_shadow_assigned(self):
        dump = {
            "collection": [
                "testing/test_timeout.py::test_1",
                "testing/test_timeout.py::test_2",
            ],
            "workqueue": {},
            "assigned": {
                "testing/test_timeout.py::test_1": {
                    "testing/test_timeout.py::test_1": True
                },
                "testing/test_timeout.py::test_2": {
                    "testing/test_timeout.py::test_2": False
                },
            },
        }
        proc = run_cli("-", input_text=json.dumps(dump))
        self.assertEqual(proc.returncode, 1, proc.stderr)
        self.assertEqual(parse_rows(proc.stdout)["hang_risk"], ["yes"])
        self.assertEqual(parse_rows(proc.stdout)["would_send"], ["()"])

    def test_null_bool_int_nodeids_refused(self):
        for coll in ([None], [True], [0]):
            dump = {
                "collection": coll,
                "workqueue": {"x.py::t": {"x.py::t": False}},
            }
            proc = run_cli("-", input_text=json.dumps(dump))
            self.assertEqual(proc.returncode, 1, proc.stderr)
            self.assertIn("must be a string", proc.stderr)
            self.assertEqual(proc.stdout, "")

    def test_dash_nodeid_refused(self):
        dump = {
            "collection": ["-", "x"],
            "workqueue": {"-": {"-": True}, "x": {"x": False}},
        }
        proc = run_cli("-", input_text=json.dumps(dump))
        self.assertEqual(proc.returncode, 1, proc.stderr)
        self.assertIn("empty sentinel", proc.stderr)
        self.assertEqual(proc.stdout, "")

    def test_dist_none_is_error(self):
        dump = {
            "collection": ["a.py::t"],
            "dist": "none",
            "workqueue": {"a.py::t": {"a.py::t": False}},
        }
        proc = run_cli("-", input_text=json.dumps(dump))
        self.assertEqual(proc.returncode, 1)
        self.assertIn("dist must be loadgroup|loadscope", proc.stderr)


class MutationGuardTests(unittest.TestCase):
    def test_missing_incomplete_is_index_error_not_hang(self):
        text = (
            "collection\tmod.py::a\n"
            "dist\tloadgroup\n"
            "unit\tmod.py::a\tmod.py::a\tdone\n"
            "unit\tmod.py::b\tmod.py::b\topen\n"
        )
        proc = run_cli("-", input_text=text)
        self.assertEqual(proc.returncode, 1)
        self.assertIn("index-error", proc.stderr)
        self.assertNotIn("hang_risk", proc.stdout)

    def test_omitted_collection_infers_from_units(self):
        text = "unit\tmod.py::a\tmod.py::a\topen\n"
        proc = run_cli("-", input_text=text)
        self.assertEqual(proc.returncode, 0, proc.stderr)
        rows = parse_rows(proc.stdout)
        self.assertEqual(rows["collection"], ["mod.py::a"])
        self.assertEqual(rows["hang_risk"], ["no"])

    def test_collection_none_is_a_nodeid(self):
        text = (
            "collection\tnone\n"
            "dist\tloadgroup\n"
            "unit\tnone\tnone\topen\n"
        )
        proc = run_cli("-", input_text=text)
        self.assertEqual(proc.returncode, 0, proc.stderr)
        rows = parse_rows(proc.stdout)
        self.assertEqual(rows["collection"], ["none"])
        self.assertEqual(rows["hang_risk"], ["no"])
        self.assertEqual(rows["send"], ["(0)"])
        self.assertEqual(rows["incomplete"], ["none"])

    def test_empty_collection_row_is_empty_not_implicit(self):
        text = "collection\t\nunit\tmod.py::a\tmod.py::a\topen\n"
        proc = run_cli("-", input_text=text)
        self.assertEqual(proc.returncode, 1)
        self.assertIn("index-error", proc.stderr)

    def test_duplicate_collection_nodeid_is_error(self):
        text = (
            "collection\ta\ta\n"
            "unit\ta\ta\topen\n"
        )
        proc = run_cli("-", input_text=text)
        self.assertEqual(proc.returncode, 1)
        self.assertIn("duplicate collection nodeid", proc.stderr)

    def test_duplicate_unit_nodeid_is_error(self):
        text = (
            "collection\ta\n"
            "unit\ta\ta\topen\n"
            "unit\ta\ta\tdone\n"
        )
        proc = run_cli("-", input_text=text)
        self.assertEqual(proc.returncode, 1)
        self.assertIn("duplicate nodeid", proc.stderr)

    def test_empty_and_padded_nodeid_are_errors(self):
        empty = run_cli("-", input_text="collection\ta\nunit\ts\t\tdone\n")
        self.assertEqual(empty.returncode, 1)
        self.assertIn("empty nodeid", empty.stderr)
        padded = run_cli("-", input_text="collection\ta\nunit\t a \t a \tdone\n")
        self.assertEqual(padded.returncode, 1)
        self.assertIn("whitespace", padded.stderr)

    def test_extra_unit_column_is_error(self):
        proc = run_cli("-", input_text="collection\ta\nunit\ta\ta\tdone\textra\n")
        self.assertEqual(proc.returncode, 1)
        self.assertIn("extra unit fields", proc.stderr)

    def test_wrong_scope_column_is_ignored_and_regrouped(self):
        text = (
            "collection\tm.py::Test::t\n"
            "unit\twrong.scope\tm.py::Test::t\tdone\n"
        )
        proc = run_cli("-", input_text=text)
        self.assertEqual(proc.returncode, 0, proc.stderr)
        rows = parse_rows(proc.stdout)
        self.assertEqual(rows["hang_risk"], ["no"])
        self.assertEqual(rows["pending"], ["0"])
        self.assertEqual(rows["completed_only"], ["m.py::Test::t"])
        self.assertNotIn("scope mismatch", proc.stderr)

    def test_257_loadgroup_units_is_legal(self):
        nodeids = [f"m.py::t{i}" for i in range(257)]
        dump = {
            "collection": nodeids,
            "dist": "loadgroup",
            "workqueue": {n: {n: (i == 0)} for i, n in enumerate(nodeids)},
        }
        proc = run_cli("-", input_text=json.dumps(dump))
        self.assertEqual(proc.returncode, 1, proc.stderr)
        self.assertNotIn("exceeds cap", proc.stderr)
        rows = parse_rows(proc.stdout)
        self.assertEqual(rows["hang_risk"], ["yes"])
        self.assertEqual(rows["scopes_n"], ["257"])
        self.assertEqual(rows["first_assigned"], ["m.py::t0"])
        self.assertEqual(rows["would_send"], ["()"])
        self.assertEqual(rows["pending"], ["256"])

    def test_257_loadgroup_all_open_is_not_hang(self):
        nodeids = [f"m.py::t{i}" for i in range(257)]
        dump = {
            "collection": nodeids,
            "dist": "loadgroup",
            "workqueue": {n: {n: False} for n in nodeids},
        }
        proc = run_cli("-", input_text=json.dumps(dump))
        self.assertEqual(proc.returncode, 0, proc.stderr)
        self.assertNotIn("exceeds cap", proc.stderr)
        rows = parse_rows(proc.stdout)
        self.assertEqual(rows["hang_risk"], ["no"])
        self.assertEqual(rows["scopes_n"], ["257"])
        self.assertEqual(rows["reschedule"], ["yes"])
        self.assertEqual(rows["pending"], ["257"])


if __name__ == "__main__":
    unittest.main()
