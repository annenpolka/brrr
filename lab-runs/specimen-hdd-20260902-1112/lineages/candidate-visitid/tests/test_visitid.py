#!/usr/bin/env python3
"""pointer vs value visit sets; address reuse skips a distinct node."""

from __future__ import annotations

import importlib.machinery
import importlib.util
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CLI = ROOT / "visitid"
FIXTURES = ROOT / "fixtures"


def load_mod():
    loader = importlib.machinery.SourceFileLoader("visitid_cli", str(CLI))
    spec = importlib.util.spec_from_loader(loader.name, loader)
    assert spec is not None
    mod = importlib.util.module_from_spec(spec)
    loader.exec_module(mod)
    return mod


VI = load_mod()


def parse_rows(text: str) -> dict[str, list[str]]:
    rows: dict[str, list[str]] = {}
    for line in text.splitlines():
        if not line or "\t" not in line:
            continue
        name, *rest = line.split("\t")
        rows[name] = rest
    return rows


def run_cli(args, *, stdin: str | None = None):
    return subprocess.run(
        [sys.executable, str(CLI), *args],
        check=False,
        capture_output=True,
        text=True,
        input=stdin,
        cwd=str(ROOT),
    )


class WalkTests(unittest.TestCase):
    def test_pointer_skips_distinct_name_at_reused_addr(self):
        events = VI.parse_record(
            "visit\troot\t0x1000\nvisit\tnixpkgs\t0x2000\nvisit\thome-manager\t0x1000\n"
        )
        visited, skipped = VI.walk_pointer(events)
        self.assertEqual([e.name for e in visited], ["root", "nixpkgs"])
        self.assertEqual(len(skipped), 1)
        self.assertEqual(skipped[0].name, "home-manager")
        self.assertEqual(skipped[0].first_name, "root")
        self.assertEqual(skipped[0].kind, "address-reuse")

    def test_value_visits_distinct_names_despite_addr_reuse(self):
        events = VI.parse_record(
            "visit\troot\t0x1000\nvisit\thome-manager\t0x1000\n"
        )
        visited, skipped = VI.walk_value(events)
        self.assertEqual([e.name for e in visited], ["root", "home-manager"])
        self.assertEqual(skipped, [])

    def test_value_skips_same_name_at_new_addr(self):
        events = VI.parse_record("visit\tnixpkgs\t0x1\nvisit\tnixpkgs\t0x2\n")
        visited, skipped = VI.walk_value(events)
        self.assertEqual([e.name for e in visited], ["nixpkgs"])
        self.assertEqual(skipped[0].kind, "same-value")
        ptr_visited, ptr_skipped = VI.walk_pointer(events)
        self.assertEqual([e.name for e in ptr_visited], ["nixpkgs", "nixpkgs"])
        self.assertEqual(ptr_skipped, [])

    def test_same_pointer_same_name_is_not_reuse(self):
        events = VI.parse_record("visit\tnixpkgs\t0x1\nvisit\tnixpkgs\t0x1\n")
        visited, skipped = VI.walk_pointer(events)
        self.assertEqual([e.name for e in visited], ["nixpkgs"])
        self.assertEqual(skipped[0].kind, "same-pointer")
        self.assertEqual(VI.never_fetched(skipped), [])


class Specimen070Tests(unittest.TestCase):
    def test_owned_reuse_fixture(self):
        text = (FIXTURES / "070-reuse.rec").read_text(encoding="utf-8")
        events = VI.parse_record(text, source="070")
        result = VI.inspect(events)
        self.assertEqual(
            [e.name for e in result["events"]],
            ["root", "nixpkgs", "flake-utils", "home-manager"],
        )
        self.assertEqual(
            [e.name for e in result["pointer_visited"]],
            ["root", "nixpkgs", "flake-utils"],
        )
        self.assertEqual([s.name for s in result["pointer_skipped"]], ["home-manager"])
        self.assertEqual(result["pointer_skipped"][0].kind, "address-reuse")
        self.assertEqual(result["pointer_skipped"][0].first_name, "root")
        self.assertEqual(
            [e.name for e in result["value_visited"]],
            ["root", "nixpkgs", "flake-utils", "home-manager"],
        )
        self.assertEqual(result["never_fetched"], ["home-manager"])
        self.assertEqual(result["skip_kinds"], ["address-reuse"])
        self.assertEqual(len(result["unique_names"]), 4)
        self.assertEqual(len(result["unique_addrs"]), 3)
        self.assertEqual(VI.predicate_rc(result), 1)

    def test_cli_matches_owned_events(self):
        proc = run_cli([str(FIXTURES / "070-reuse.rec")])
        self.assertEqual(proc.returncode, 1, proc.stderr)
        rows = parse_rows(proc.stdout)
        self.assertEqual(rows["mode"], ["events"])
        self.assertEqual(rows["pointer_key"], ["id"])
        self.assertEqual(rows["value_key"], ["name"])
        self.assertNotEqual(rows["value_key"], ["caller-node"])
        self.assertNotIn("inputs", rows)
        self.assertEqual(rows["pointer_skipped"], ["home-manager"])
        self.assertEqual(rows["value_skipped"], ["-"])
        self.assertEqual(rows["skip_kind"], ["address-reuse"])
        self.assertEqual(
            rows["reuse"],
            ["0x7ffe1000", "first", "root", "later", "home-manager"],
        )
        self.assertEqual(rows["never_fetched"], ["home-manager"])
        self.assertEqual(rows["never_fetched_n"], ["1"])
        self.assertEqual(rows["unique_names"], ["4"])
        self.assertEqual(rows["unique_addrs"], ["3"])
        self.assertEqual(
            rows["names"],
            ["root", "nixpkgs", "flake-utils", "home-manager"],
        )
        self.assertEqual(rows["addrs"], ["0x7ffe1000", "0x7ffe2000", "0x7ffe3000"])
        self.assertNotIn("pointer_done", rows)
        self.assertNotIn("value_done", rows)
        self.assertIn("home-manager", rows["value_visited"])
        self.assertNotIn("home-manager", rows["pointer_visited"])

    def test_cli_python_module_matches_launcher(self):
        args = [str(FIXTURES / "070-reuse.rec")]
        via_py = subprocess.run(
            [sys.executable, str(CLI), *args],
            check=False,
            capture_output=True,
            text=True,
            cwd=str(ROOT),
        )
        via_exec = subprocess.run(
            [str(CLI), *args],
            check=False,
            capture_output=True,
            text=True,
            cwd=str(ROOT),
        )
        self.assertEqual(via_py.returncode, 1, via_py.stderr)
        self.assertEqual(via_exec.returncode, 1, via_exec.stderr)
        self.assertEqual(via_py.stdout, via_exec.stdout)
        self.assertEqual(via_py.returncode, via_exec.returncode)


class UnseenTests(unittest.TestCase):
    def test_unique_addrs_no_skip(self):
        proc = run_cli([str(FIXTURES / "unseen-unique.rec")])
        self.assertEqual(proc.returncode, 0, proc.stderr)
        rows = parse_rows(proc.stdout)
        self.assertEqual(rows["pointer_skipped"], ["-"])
        self.assertEqual(rows["value_skipped"], ["-"])
        self.assertEqual(rows["skip_kind"], ["-"])
        self.assertEqual(rows["unique_names"], ["3"])
        self.assertEqual(rows["unique_addrs"], ["3"])
        self.assertNotIn("pointer_done", rows)
        self.assertNotIn("value_done", rows)
        self.assertEqual(rows["reuse"], ["-"])
        self.assertEqual(rows["never_fetched"], ["-"])
        self.assertEqual(rows["never_fetched_n"], ["0"])

    def test_same_value_different_addr(self):
        proc = run_cli([str(FIXTURES / "unseen-same-value.rec")])
        self.assertEqual(proc.returncode, 0, proc.stderr)
        rows = parse_rows(proc.stdout)
        self.assertEqual(rows["pointer_skipped"], ["-"])
        self.assertEqual(rows["value_skipped"], ["nixpkgs"])
        self.assertEqual(rows["skip_kind"], ["same-value"])
        self.assertEqual(rows["never_fetched"], ["-"])
        self.assertEqual(rows["never_fetched_n"], ["0"])

    def test_all_digit_hex_matches_0x(self):
        proc = run_cli([], stdin="root\t1000\nnixpkgs\t0x1000\n")
        self.assertEqual(proc.returncode, 1, proc.stderr)
        rows = parse_rows(proc.stdout)
        self.assertEqual(rows["unique_addrs"], ["1"])
        self.assertEqual(rows["unique_names"], ["2"])
        self.assertEqual(rows["skip_kind"], ["address-reuse"])
        self.assertEqual(rows["never_fetched"], ["nixpkgs"])
        self.assertEqual(rows["reuse"][0], "1000")
        self.assertIn("later-token", rows["reuse"])
        self.assertIn("0x1000", rows["reuse"])

    def test_ten_and_0x10_are_the_same_pointer(self):
        proc = run_cli([], stdin="root\t10\nnixpkgs\t0x10\n")
        self.assertEqual(proc.returncode, 1, proc.stderr)
        rows = parse_rows(proc.stdout)
        self.assertEqual(rows["unique_addrs"], ["1"])
        self.assertEqual(rows["never_fetched"], ["nixpkgs"])

    def test_stdin_space_separated(self):
        proc = run_cli([], stdin="root 0x10\nnixpkgs 0x10\n")
        self.assertEqual(proc.returncode, 1, proc.stderr)
        rows = parse_rows(proc.stdout)
        self.assertEqual(rows["pointer_skipped"], ["nixpkgs"])
        self.assertEqual(rows["skip_kind"], ["address-reuse"])
        self.assertEqual(rows["never_fetched"], ["nixpkgs"])

    def test_missing_visit_is_error(self):
        proc = run_cli([], stdin="# none\n")
        self.assertEqual(proc.returncode, 1)
        self.assertIn("missing visit", proc.stderr)

    def test_bad_addr_is_error(self):
        proc = run_cli([], stdin="root\tzz\n")
        self.assertEqual(proc.returncode, 1)
        self.assertIn("bad address", proc.stderr)
        self.assertEqual(proc.stdout, "")


class LiveTests(unittest.TestCase):
    def test_retain_keeps_ids_unique(self):
        proc = run_cli(["--live", "--retain", "root", "nixpkgs", "home-manager"])
        self.assertEqual(proc.returncode, 0, proc.stderr)
        rows = parse_rows(proc.stdout)
        self.assertEqual(rows["mode"], ["cpython-slot"])
        self.assertEqual(rows["retain"], ["true"])
        self.assertEqual(rows["allocator"], ["cpython"])
        self.assertEqual(rows["pointer_key"], ["slot"])
        self.assertEqual(rows["value_key"], ["name"])
        self.assertEqual(rows["pointer_visited"], ["root", "nixpkgs", "home-manager"])
        self.assertEqual(rows["pointer_skipped"], ["-"])
        self.assertEqual(rows["value_visited"], ["root", "nixpkgs", "home-manager"])
        self.assertEqual(len(set(rows["addrs"])), 3)
        self.assertEqual(rows["addrs"], ["slot0", "slot1", "slot2"])
        for addr in rows["addrs"]:
            self.assertTrue(addr.startswith("slot"), addr)
            self.assertFalse(addr.startswith("0x"), addr)
        self.assertEqual(rows["allocator_reuse"], ["-"])
        self.assertEqual(rows["never_fetched"], ["-"])

    def test_live_drop_runs_and_names_fields(self):
        proc = run_cli(["--live", "root", "nixpkgs", "home-manager"])
        rows = parse_rows(proc.stdout)
        self.assertEqual(rows["mode"], ["cpython-slot"])
        self.assertEqual(rows["retain"], ["false"])
        self.assertEqual(rows["allocator"], ["cpython"])
        self.assertEqual(rows["pointer_key"], ["slot"])
        self.assertEqual(rows["value_key"], ["name"])
        self.assertEqual(rows["value_visited"], ["root", "nixpkgs", "home-manager"])
        for addr in rows["addrs"]:
            self.assertTrue(addr.startswith("slot"), addr)
            self.assertFalse(addr.startswith("0x"), addr)
        self.assertNotIn("0x", proc.stdout)
        if len(set(rows["addrs"])) < 3:
            self.assertEqual(proc.returncode, 1, proc.stderr)
            self.assertEqual(rows["skip_kind"], ["address-reuse"])
            self.assertNotEqual(rows["never_fetched"], ["-"])
            self.assertGreater(int(rows["never_fetched_n"][0]), 0)
            self.assertEqual(rows["allocator_reuse"][0], "ping-pong")
        else:
            self.assertEqual(proc.returncode, 0, proc.stderr)

    def test_retain_without_live_is_error(self):
        proc = run_cli(["--retain"])
        self.assertEqual(proc.returncode, 1)
        self.assertEqual(proc.stderr.strip(), "visitid: --retain requires --live")

    def test_live_events_drop_can_reuse_id(self):
        events = VI.live_events(["a", "b", "c"], retain=False)
        ids = [e.addr for e in events]
        retained = VI.live_events(["a", "b", "c"], retain=True)
        self.assertEqual(len({e.addr for e in retained}), 3)
        if len(set(ids)) < 3:
            result = VI.inspect(events)
            self.assertIn("address-reuse", result["skip_kinds"])
            self.assertTrue(result["never_fetched"])
            self.assertEqual(VI.predicate_rc(result), 1)

    def test_live_existing_file_is_not_a_name(self):
        rec = FIXTURES / "070-reuse.rec"
        proc = run_cli(["--live", str(rec)])
        self.assertEqual(proc.returncode, 1)
        self.assertIn("existing file is not a live NAME", proc.stderr)
        self.assertEqual(proc.stdout, "")

    def test_live_directory_homonym_is_a_name(self):
        with tempfile.TemporaryDirectory() as tmp:
            Path(tmp, "root").mkdir()
            proc = subprocess.run(
                [
                    sys.executable,
                    str(CLI),
                    "--live",
                    "--retain",
                    "root",
                    "nixpkgs",
                    "home-manager",
                ],
                check=False,
                capture_output=True,
                text=True,
                cwd=tmp,
            )
        self.assertEqual(proc.returncode, 0, proc.stderr)
        self.assertNotIn("existing file", proc.stderr)
        self.assertNotIn("existing path", proc.stderr)
        rows = parse_rows(proc.stdout)
        self.assertEqual(rows["value_visited"], ["root", "nixpkgs", "home-manager"])
        self.assertEqual(rows["never_fetched"], ["-"])
        self.assertEqual(rows["pointer_key"], ["slot"])
        self.assertEqual(rows["addrs"], ["slot0", "slot1", "slot2"])
        self.assertNotIn("0x", proc.stdout)

    def test_live_events_print_slot_labels(self):
        events = VI.live_events(["root", "nixpkgs", "home-manager"], retain=True)
        texts = [e.addr_text for e in events]
        self.assertEqual(texts, ["slot0", "slot1", "slot2"])
        self.assertTrue(all(e.addr_text.startswith("slot") for e in events))
        dropped = VI.live_events(["root", "nixpkgs", "home-manager"], retain=False)
        self.assertTrue(all(e.addr_text.startswith("slot") for e in dropped))
        self.assertFalse(any(e.addr_text.startswith("0x") for e in dropped))


class MutateTests(unittest.TestCase):
    def test_reuse_same_name_is_still_never_fetched(self):
        proc = run_cli(
            [],
            stdin="root\t0x1000\nhome-manager\t0x2000\nhome-manager\t0x1000\n",
        )
        self.assertEqual(proc.returncode, 1, proc.stderr)
        rows = parse_rows(proc.stdout)
        self.assertEqual(rows["unique_names"], ["2"])
        self.assertEqual(rows["unique_addrs"], ["2"])
        self.assertEqual(rows["names"], ["root", "home-manager"])
        self.assertEqual(rows["addrs"], ["0x1000", "0x2000"])
        self.assertEqual(rows["pointer_visited"], ["root", "home-manager"])
        self.assertEqual(rows["pointer_skipped"], ["home-manager"])
        self.assertEqual(rows["value_visited"], ["root", "home-manager"])
        self.assertEqual(rows["value_skipped"], ["home-manager"])
        self.assertEqual(rows["skip_kind"], ["address-reuse", "same-value"])
        self.assertEqual(
            rows["reuse"],
            ["0x1000", "first", "root", "later", "home-manager"],
        )
        self.assertEqual(rows["never_fetched"], ["home-manager"])
        self.assertEqual(rows["never_fetched_n"], ["1"])

    def test_reuse_same_name_fixture(self):
        proc = run_cli([str(FIXTURES / "reuse-same-name.rec")])
        self.assertEqual(proc.returncode, 1, proc.stderr)
        rows = parse_rows(proc.stdout)
        self.assertEqual(rows["never_fetched"], ["home-manager"])
        self.assertNotEqual(rows["never_fetched"], ["-"])

    def test_node_named_none_is_not_empty_sentinel(self):
        skipped = run_cli([], stdin="root\t0x1\nnone\t0x1\n")
        self.assertEqual(skipped.returncode, 1, skipped.stderr)
        skip_rows = parse_rows(skipped.stdout)
        self.assertEqual(skip_rows["pointer_skipped"], ["none"])
        self.assertEqual(skip_rows["never_fetched"], ["none"])
        self.assertEqual(skip_rows["never_fetched_n"], ["1"])
        self.assertEqual(skip_rows["skip_kind"], ["address-reuse"])

        visited = run_cli([], stdin="root\t0x1\nnone\t0x2\n")
        self.assertEqual(visited.returncode, 0, visited.stderr)
        vis_rows = parse_rows(visited.stdout)
        self.assertEqual(vis_rows["pointer_skipped"], ["-"])
        self.assertEqual(vis_rows["value_skipped"], ["-"])
        self.assertEqual(vis_rows["skip_kind"], ["-"])
        self.assertEqual(vis_rows["reuse"], ["-"])
        self.assertEqual(vis_rows["never_fetched"], ["-"])
        self.assertEqual(vis_rows["never_fetched_n"], ["0"])
        self.assertEqual(vis_rows["value_visited"], ["root", "none"])

    def test_empty_tab_field_is_error(self):
        proc = run_cli([], stdin="root\t\t0x10\n")
        self.assertEqual(proc.returncode, 1)
        self.assertIn("empty tab field", proc.stderr)
        self.assertEqual(proc.stdout, "")

    def test_extra_tab_field_is_error(self):
        proc = run_cli([], stdin="root\t0x1\textra\tnixpkgs\t0x2\n")
        self.assertEqual(proc.returncode, 1)
        self.assertIn("extra field", proc.stderr)
        self.assertEqual(proc.stdout, "")

    def test_padded_name_is_error(self):
        proc = run_cli([], stdin="root\t0x1\n  root  \t0x1\n")
        self.assertEqual(proc.returncode, 1)
        self.assertIn("padded name", proc.stderr)
        self.assertEqual(proc.stdout, "")

    def test_visit_as_name_without_tag(self):
        proc = run_cli([], stdin="visit\t0x1\n")
        self.assertEqual(proc.returncode, 0, proc.stderr)
        rows = parse_rows(proc.stdout)
        self.assertEqual(rows["names"], ["visit"])
        self.assertEqual(rows["never_fetched"], ["-"])

    def test_three_field_flake_input_is_extra(self):
        proc = run_cli(
            [],
            stdin="root\t0x1000\nhm1\t0x2000\thome-manager\nhm2\t0x1000\thome-manager\n",
        )
        self.assertEqual(proc.returncode, 1)
        self.assertIn("extra field", proc.stderr)
        self.assertIn("does not accept flake input names", proc.stderr)
        self.assertEqual(proc.stdout, "")

    def test_distinct_node_keys_without_input_column(self):
        proc = run_cli(
            [],
            stdin="root\t0x1000\nhm1\t0x2000\nhm2\t0x1000\n",
        )
        self.assertEqual(proc.returncode, 1, proc.stderr)
        rows = parse_rows(proc.stdout)
        self.assertEqual(rows["value_key"], ["name"])
        self.assertEqual(rows["names"], ["root", "hm1", "hm2"])
        self.assertEqual(rows["unique_names"], ["3"])
        self.assertEqual(rows["pointer_visited"], ["root", "hm1"])
        self.assertEqual(rows["pointer_skipped"], ["hm2"])
        self.assertEqual(rows["value_visited"], ["root", "hm1", "hm2"])
        self.assertEqual(rows["value_skipped"], ["-"])
        self.assertEqual(rows["never_fetched"], ["hm2"])
        self.assertNotIn("inputs", rows)

    def test_hex_without_0x_is_pointer(self):
        proc = run_cli([], stdin="root\t7ffe1000\nnixpkgs\t0x7ffe1000\n")
        self.assertEqual(proc.returncode, 1, proc.stderr)
        rows = parse_rows(proc.stdout)
        self.assertEqual(rows["unique_addrs"], ["1"])
        self.assertEqual(rows["skip_kind"], ["address-reuse"])
        self.assertEqual(rows["never_fetched"], ["nixpkgs"])
        self.assertEqual(rows["reuse"][0], "7ffe1000")

    def test_scientific_addr_is_still_bad(self):
        proc = run_cli([], stdin="root\t1e2\n")
        self.assertEqual(proc.returncode, 1)
        self.assertIn("bad address", proc.stderr)
        self.assertEqual(proc.stdout, "")

    def test_list_cap_keeps_count(self):
        lines = [f"n{i}\t0x{i:x}" for i in range(8)]
        lines += [f"later{i}\t0x{i % 8:x}" for i in range(40)]
        proc = run_cli([], stdin="\n".join(lines) + "\n")
        self.assertEqual(proc.returncode, 1, proc.stderr)
        rows = parse_rows(proc.stdout)
        self.assertEqual(rows["never_fetched_n"], ["40"])
        self.assertEqual(len(rows["never_fetched"]), 32)
        self.assertEqual(rows["pointer_skipped_n"], ["40"])
        self.assertEqual(len(rows["pointer_skipped"]), 32)
        self.assertEqual(rows["never_fetched"][0], "later0")
        self.assertIn("later31", rows["never_fetched"])
        self.assertNotIn("later32", rows["never_fetched"])

    def test_cap_unique_names_not_raw_repeats(self):
        lines = [f"n{i}\t0x{i:x}" for i in range(32)]
        lines += ["dup\t0x%x" % (i % 32) for i in range(32)]
        lines += [f"later{i}\t0x{i:x}" for i in range(8)]
        proc = run_cli([], stdin="\n".join(lines) + "\n")
        self.assertEqual(proc.returncode, 1, proc.stderr)
        rows = parse_rows(proc.stdout)
        self.assertEqual(rows["unique_names"], ["41"])
        self.assertEqual(rows["unique_addrs"], ["32"])
        self.assertEqual(rows["never_fetched_n"], ["40"])
        self.assertEqual(rows["never_fetched"][0], "dup")
        for i in range(8):
            self.assertIn(f"later{i}", rows["never_fetched"])
        self.assertEqual(len(rows["never_fetched"]), 9)
        self.assertEqual(rows["pointer_skipped"], rows["never_fetched"])
        self.assertEqual(rows["pointer_skipped_n"], ["40"])
        self.assertEqual(len(rows["names"]), 32)
        self.assertEqual(rows["names"][0], "n0")
        self.assertEqual(rows["names_n"], ["41"])
        self.assertNotIn("dup", rows["names"])
        reuse_laters = []
        for line in proc.stdout.splitlines():
            if not line.startswith("reuse\t"):
                continue
            parts = line.split("\t")
            reuse_laters.append(parts[parts.index("later") + 1])
        self.assertEqual(reuse_laters[0], "dup")
        self.assertEqual(reuse_laters[1:], [f"later{i}" for i in range(8)])

    def test_node_named_dash_is_error(self):
        proc = run_cli([], stdin="root\t0x1\n-\t0x1\n")
        self.assertEqual(proc.returncode, 1)
        self.assertIn("empty-list token", proc.stderr)
        self.assertEqual(proc.stdout, "")
        live = run_cli(["--live", "-"])
        self.assertEqual(live.returncode, 1)
        self.assertIn("empty-list token", live.stderr)

    def test_bom_in_name_is_error(self):
        proc = run_cli([], stdin="\ufeffroot\t0x1\n")
        self.assertEqual(proc.returncode, 1)
        self.assertIn("BOM", proc.stderr)
        self.assertEqual(proc.stdout, "")

    def test_double_prefix_gone(self):
        proc = run_cli(["--live"])
        self.assertEqual(proc.returncode, 1)
        self.assertEqual(proc.stderr.strip(), "visitid: --live needs at least one NAME")
        self.assertNotIn("visitid: visitid:", proc.stderr)

    def test_same_value_only_stays_rc0(self):
        proc = run_cli([], stdin="nixpkgs\t0x1\nnixpkgs\t0x2\nnixpkgs\t0x3\n")
        self.assertEqual(proc.returncode, 0, proc.stderr)
        rows = parse_rows(proc.stdout)
        self.assertEqual(rows["skip_kind"], ["same-value"])
        self.assertEqual(rows["never_fetched"], ["-"])
        self.assertEqual(rows["never_fetched_n"], ["0"])
        self.assertEqual(rows["value_key"], ["name"])
        self.assertNotIn("inputs", rows)

    def test_lock_path_and_name_are_two_keys(self):
        proc = run_cli([], stdin="root/nixpkgs\t0x1\nnixpkgs\t0x2\n")
        self.assertEqual(proc.returncode, 0, proc.stderr)
        rows = parse_rows(proc.stdout)
        self.assertEqual(rows["unique_names"], ["2"])
        self.assertEqual(rows["names"], ["root/nixpkgs", "nixpkgs"])
        self.assertEqual(rows["skip_kind"], ["-"])

    def test_help_refuses_flake_input_names(self):
        proc = subprocess.run(
            [sys.executable, str(CLI), "--help"],
            check=False,
            capture_output=True,
            text=True,
        )
        self.assertEqual(proc.returncode, 0, proc.stderr)
        self.assertIn("does not accept flake input names", proc.stdout)
        self.assertIn("slot0", proc.stdout)

    def test_event_has_no_input_field(self):
        events = VI.parse_record("root\t0x1\n")
        self.assertFalse(hasattr(events[0], "input"))


if __name__ == "__main__":
    unittest.main()
