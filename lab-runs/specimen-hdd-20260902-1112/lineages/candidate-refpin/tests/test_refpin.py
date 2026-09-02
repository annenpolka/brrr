#!/usr/bin/env python3
"""default ref attached to a pinned rev changes narHash identity."""

from __future__ import annotations

import importlib.machinery
import importlib.util
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CLI = ROOT / "refpin"
FIX = ROOT / "fixtures"

REV = "e374a4ebd0dbf7b23e077a94fd5cefb7a9d65ffa"
HASH_A = "sha256-UEzJabo6ObaQc0Rc5XJOf43NR5Rp3e0WwpWi55c79R8="
HASH_B = "sha256-q2mgMIPLqHSx0pSEJ42rrZpYxcjkgL1U1UvCTHTw+Oo="
HARVEST = "pinned-rev-default-ref-changed-hash"


def load_mod():
    loader = importlib.machinery.SourceFileLoader("refpin_cli", str(CLI))
    spec = importlib.util.spec_from_loader(loader.name, loader)
    assert spec is not None
    mod = importlib.util.module_from_spec(spec)
    sys.modules[loader.name] = mod
    loader.exec_module(mod)
    return mod


RP = load_mod()


def parse_rows(text: str) -> dict[str, list[str]]:
    rows: dict[str, list[str]] = {}
    for line in text.splitlines():
        if not line or "\t" not in line:
            continue
        name, *rest = line.split("\t")
        rows[name] = rest
    return rows


def run_cli(args, *, stdin=None):
    return subprocess.run(
        [sys.executable, str(CLI), *args],
        capture_output=True,
        text=True,
        check=False,
        input=stdin,
    )


def rec(*lines: str) -> str:
    return "\n".join(lines) + "\n"


def write_pair(td: Path, a: str, b: str) -> tuple[Path, Path]:
    pa = td / "a.rec"
    pb = td / "b.rec"
    pa.write_text(a, encoding="utf-8")
    pb.write_text(b, encoding="utf-8")
    return pa, pb


class Specimen064Tests(unittest.TestCase):
    def test_owned_pair_is_the_harvest_and(self):
        a = RP.parse_record((FIX / "064-expected.rec").read_text(), source="expected")
        b = RP.parse_record((FIX / "064-got.rec").read_text(), source="got")
        self.assertFalse(a.ref.present)
        self.assertTrue(b.ref.present)
        self.assertEqual(b.ref.value, "master")
        result = RP.inspect(a, b)
        self.assertTrue(result["same_rev"])
        self.assertTrue(result["identity_changed"])
        self.assertEqual(result["ref_attached"], "attached")
        self.assertEqual(result["verdict"], HARVEST)
        self.assertEqual(result["attached_ref"], "master")
        self.assertIn("narHash", result["diverged"])
        self.assertNotIn("ref", result["diverged"])
        self.assertEqual(result["present_only_b"], ["ref"])
        self.assertIn("rev", result["equal"])
        self.assertIn("lastModified", result["equal"])
        self.assertIn("revCount", result["equal"])

    def test_cli_owned_pair(self):
        proc = run_cli([str(FIX / "064-expected.rec"), str(FIX / "064-got.rec")])
        self.assertEqual(proc.returncode, 1, proc.stderr)
        rows = parse_rows(proc.stdout)
        self.assertEqual(rows["verdict"], [HARVEST])
        self.assertEqual(rows["same_rev"], ["yes"])
        self.assertEqual(rows["ref_present_a"], ["no"])
        self.assertEqual(rows["ref_present_b"], ["yes"])
        self.assertEqual(rows["ref_a"], ["-"])
        self.assertEqual(rows["ref_b"], ["master"])
        self.assertEqual(rows["ref_attached"], ["attached"])
        self.assertEqual(rows["attached_ref"], ["master"])
        self.assertEqual(rows["identity_changed"], ["yes"])
        self.assertEqual(rows["time_axis"], ["FIRST=earlier SECOND=later"])
        self.assertIn("lastModified", rows["equal"])
        self.assertIn("revCount", rows["equal"])

    def test_unseen_identical_records(self):
        proc = run_cli([str(FIX / "unseen-same.rec"), str(FIX / "unseen-same-b.rec")])
        self.assertEqual(proc.returncode, 0, proc.stderr)
        rows = parse_rows(proc.stdout)
        self.assertEqual(rows["verdict"], ["identical"])
        self.assertEqual(rows["identity_changed"], ["no"])
        self.assertEqual(rows["ref_attached"], ["none"])
        self.assertEqual(rows["ref_present_a"], ["no"])
        self.assertEqual(rows["ref_present_b"], ["no"])
        self.assertEqual(rows["diverged"], ["-"])

    def test_missing_file_errors(self):
        proc = run_cli([str(FIX / "064-expected.rec"), "/dev/null"])
        self.assertEqual(proc.returncode, 1)
        self.assertIn("not a lock record", proc.stderr)


class JoinAndPresenceTests(unittest.TestCase):
    def test_same_hash_different_ref_is_not_harvest(self):
        with tempfile.TemporaryDirectory() as tmp:
            td = Path(tmp)
            a, b = write_pair(
                td,
                rec(f"rev\t{REV}", f"narHash\t{HASH_A}", "ref\tmain"),
                rec(f"rev\t{REV}", f"narHash\t{HASH_A}", "ref\tmaster"),
            )
            proc = run_cli([str(a), str(b)])
        self.assertEqual(proc.returncode, 1, proc.stderr)
        rows = parse_rows(proc.stdout)
        self.assertEqual(rows["verdict"], ["both-disagree"])
        self.assertEqual(rows["identity_changed"], ["no"])
        self.assertNotEqual(rows["verdict"], [HARVEST])

    def test_one_sided_attach_same_hash_is_not_harvest(self):
        with tempfile.TemporaryDirectory() as tmp:
            td = Path(tmp)
            a, b = write_pair(
                td,
                rec(f"rev\t{REV}", f"narHash\t{HASH_A}"),
                rec(f"rev\t{REV}", f"narHash\t{HASH_A}", "ref\tmaster"),
            )
            proc = run_cli([str(a), str(b)])
        self.assertEqual(proc.returncode, 1, proc.stderr)
        rows = parse_rows(proc.stdout)
        self.assertEqual(rows["verdict"], ["ref-attached-same-hash"])
        self.assertEqual(rows["ref_attached"], ["attached"])
        self.assertEqual(rows["identity_changed"], ["no"])

    def test_different_rev_same_hash_prints_both_revs(self):
        other = "bbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbb"
        with tempfile.TemporaryDirectory() as tmp:
            td = Path(tmp)
            a, b = write_pair(
                td,
                rec(f"rev\t{REV}", f"narHash\t{HASH_A}", "ref\tmaster"),
                rec(f"rev\t{other}", f"narHash\t{HASH_A}", "ref\tmaster"),
            )
            proc = run_cli([str(a), str(b)])
        self.assertEqual(proc.returncode, 1, proc.stderr)
        rows = parse_rows(proc.stdout)
        self.assertEqual(rows["verdict"], ["rev-diverged"])
        self.assertEqual(rows["same_rev"], ["no"])
        self.assertEqual(rows["rev_a"], [REV])
        self.assertEqual(rows["rev_b"], [other])
        self.assertNotIn("rev", rows)

    def test_lastModified_value_only(self):
        with tempfile.TemporaryDirectory() as tmp:
            td = Path(tmp)
            a, b = write_pair(
                td,
                rec(f"rev\t{REV}", f"narHash\t{HASH_A}", "ref\tmaster", "lastModified\t100", "revCount\t1"),
                rec(f"rev\t{REV}", f"narHash\t{HASH_A}", "ref\tmaster", "lastModified\t200", "revCount\t2"),
            )
            proc = run_cli([str(a), str(b)])
        self.assertEqual(proc.returncode, 0, proc.stderr)
        rows = parse_rows(proc.stdout)
        self.assertEqual(rows["verdict"], ["lastModified-only"])
        self.assertEqual(rows["identity_changed"], ["no"])
        self.assertEqual(rows["diverged"], ["lastModified", "revCount"])

    def test_lastModified_presence_is_not_value_inequality(self):
        with tempfile.TemporaryDirectory() as tmp:
            td = Path(tmp)
            a, b = write_pair(
                td,
                rec(f"rev\t{REV}", f"narHash\t{HASH_A}", "lastModified\t100"),
                rec(f"rev\t{REV}", f"narHash\t{HASH_A}"),
            )
            proc = run_cli([str(a), str(b)])
        self.assertEqual(proc.returncode, 0, proc.stderr)
        rows = parse_rows(proc.stdout)
        self.assertEqual(rows["verdict"], ["metadata-presence"])
        self.assertEqual(rows["present_only_a"], ["lastModified"])
        self.assertEqual(rows["diverged"], ["-"])
        self.assertEqual(rows["identity_changed"], ["no"])

    def test_missing_rev(self):
        with tempfile.TemporaryDirectory() as tmp:
            td = Path(tmp)
            a, b = write_pair(
                td,
                rec(f"narHash\t{HASH_A}"),
                rec(f"rev\t{REV}", f"narHash\t{HASH_A}"),
            )
            proc = run_cli([str(a), str(b)])
        self.assertEqual(proc.returncode, 1)
        self.assertEqual(proc.stdout, "")
        self.assertIn("missing rev", proc.stderr)

    def test_empty_vs_omitted_vs_none_vs_NONE(self):
        with tempfile.TemporaryDirectory() as tmp:
            td = Path(tmp)
            omitted = rec(f"rev\t{REV}", f"narHash\t{HASH_A}")
            empty = rec(f"rev\t{REV}", f"narHash\t{HASH_A}", "ref\t")
            none = rec(f"rev\t{REV}", f"narHash\t{HASH_A}", "ref\tnone")
            none_upper = rec(f"rev\t{REV}", f"narHash\t{HASH_A}", "ref\tNONE")
            cases = [
                (omitted, none, "attached", "none", "yes"),
                (none, omitted, "ref_removed", "-", "no"),
                (omitted, empty, "attached", "", "yes"),
                (none, none_upper, "both-disagree", "NONE", "yes"),
            ]
            for first, second, attached, ref_b, present_b in cases:
                a, b = write_pair(td, first, second)
                proc = run_cli([str(a), str(b)])
                rows = parse_rows(proc.stdout)
                self.assertEqual(rows["ref_attached"], [attached], proc.stdout)
                self.assertEqual(rows["ref_b"], [ref_b], proc.stdout)
                self.assertEqual(rows["ref_present_b"], [present_b], proc.stdout)
                self.assertNotEqual(rows["verdict"], [HARVEST], proc.stdout)

    def test_branch_named_none_is_a_ref(self):
        rec_none = rec(f"rev\t{REV}", f"narHash\t{HASH_B}", "ref\tnone")
        rec_omit = rec(f"rev\t{REV}", f"narHash\t{HASH_A}")
        with tempfile.TemporaryDirectory() as tmp:
            td = Path(tmp)
            a, b = write_pair(td, rec_omit, rec_none)
            proc = run_cli([str(a), str(b)])
        rows = parse_rows(proc.stdout)
        self.assertEqual(rows["verdict"], [HARVEST])
        self.assertEqual(rows["ref_b"], ["none"])
        self.assertEqual(rows["ref_present_b"], ["yes"])
        self.assertEqual(rows["attached_ref"], ["none"])

    def test_swapped_owned_pair_is_ref_removed(self):
        proc = run_cli([str(FIX / "064-got.rec"), str(FIX / "064-expected.rec")])
        self.assertEqual(proc.returncode, 1, proc.stderr)
        rows = parse_rows(proc.stdout)
        self.assertEqual(rows["verdict"], ["pinned-rev-default-ref-removed-hash"])
        self.assertEqual(rows["ref_attached"], ["ref_removed"])
        self.assertEqual(rows["removed_ref"], ["master"])
        self.assertEqual(rows["attached_ref"], ["-"])
        self.assertNotEqual(rows["verdict"], [HARVEST])
        self.assertNotEqual(rows["ref_attached"], ["attached"])

    def test_hash_changed_no_ref_is_not_harvest(self):
        with tempfile.TemporaryDirectory() as tmp:
            td = Path(tmp)
            a, b = write_pair(
                td,
                rec(f"rev\t{REV}", f"narHash\t{HASH_A}"),
                rec(f"rev\t{REV}", f"narHash\t{HASH_B}"),
            )
            proc = run_cli([str(a), str(b)])
        self.assertEqual(proc.returncode, 1, proc.stderr)
        rows = parse_rows(proc.stdout)
        self.assertEqual(rows["verdict"], ["hash-changed-no-ref"])
        self.assertEqual(rows["ref_attached"], ["none"])
        self.assertEqual(rows["identity_changed"], ["yes"])
        self.assertNotEqual(rows["verdict"], [HARVEST])

    def test_dash_is_stdin(self):
        proc = run_cli(
            ["-", str(FIX / "064-got.rec")],
            stdin=(FIX / "064-expected.rec").read_text(),
        )
        self.assertEqual(proc.returncode, 1, proc.stderr)
        rows = parse_rows(proc.stdout)
        self.assertEqual(rows["verdict"], [HARVEST])
        self.assertEqual(rows["source_a"], ["tsv"])

    def test_url_and_type_are_ignored(self):
        with tempfile.TemporaryDirectory() as tmp:
            td = Path(tmp)
            a, b = write_pair(
                td,
                rec(
                    f"rev\t{REV}",
                    f"narHash\t{HASH_A}",
                    "url\tgit+file:///x",
                    "type\tgit",
                    "lastModified\t1",
                    "revCount\t1",
                ),
                rec(
                    f"rev\t{REV}",
                    f"narHash\t{HASH_B}",
                    "ref\tmaster",
                    "url\tgit+file:///x",
                    "type\tgit",
                    "lastModified\t1",
                    "revCount\t1",
                ),
            )
            proc = run_cli([str(a), str(b)])
        self.assertEqual(proc.returncode, 1, proc.stderr)
        rows = parse_rows(proc.stdout)
        self.assertEqual(rows["verdict"], [HARVEST])
        self.assertNotIn("unknown field", proc.stderr)

    def test_both_refs_different_with_hash_change(self):
        with tempfile.TemporaryDirectory() as tmp:
            td = Path(tmp)
            a, b = write_pair(
                td,
                rec(f"rev\t{REV}", f"narHash\t{HASH_A}", "ref\tmain"),
                rec(f"rev\t{REV}", f"narHash\t{HASH_B}", "ref\tmaster"),
            )
            proc = run_cli([str(a), str(b)])
        self.assertEqual(proc.returncode, 1, proc.stderr)
        rows = parse_rows(proc.stdout)
        self.assertEqual(rows["verdict"], ["both-disagree"])
        self.assertEqual(rows["ref_attached"], ["both-disagree"])
        self.assertNotEqual(rows["verdict"], [HARVEST])

    def test_extra_tab_is_error_not_identity(self):
        with tempfile.TemporaryDirectory() as tmp:
            td = Path(tmp)
            a, b = write_pair(
                td,
                rec(f"rev\t{REV}", f"narHash\t{HASH_A}\tEXTRA"),
                rec(f"rev\t{REV}", f"narHash\t{HASH_B}", "ref\tmaster"),
            )
            proc = run_cli([str(a), str(b)])
        self.assertEqual(proc.returncode, 1)
        self.assertEqual(proc.stdout, "")
        self.assertIn("extra tab in value", proc.stderr)

    def test_duplicate_field_is_error(self):
        with tempfile.TemporaryDirectory() as tmp:
            td = Path(tmp)
            a, b = write_pair(
                td,
                rec(f"rev\t{REV}", "rev\tlater", f"narHash\t{HASH_A}"),
                rec(f"rev\t{REV}", f"narHash\t{HASH_A}"),
            )
            proc = run_cli([str(a), str(b)])
        self.assertEqual(proc.returncode, 1)
        self.assertEqual(proc.stdout, "")
        self.assertIn("duplicate field 'rev'", proc.stderr)

    def test_native_mismatch_log(self):
        proc = run_cli([str(FIX / "narhash_mismatch.txt")])
        self.assertEqual(proc.returncode, 1, proc.stderr)
        rows = parse_rows(proc.stdout)
        self.assertEqual(rows["verdict"], [HARVEST])
        self.assertEqual(rows["ref_b"], ["master"])
        self.assertEqual(rows["attached_ref"], ["master"])
        self.assertEqual(rows["source_a"], ["mismatch-log"])
        self.assertEqual(rows["source_b"], ["mismatch-log"])
        self.assertEqual(rows["rev"], [REV])

    def test_native_nix_error_json_blobs(self):
        proc = run_cli([str(FIX / "nix-error.txt")])
        self.assertEqual(proc.returncode, 1, proc.stderr)
        rows = parse_rows(proc.stdout)
        self.assertEqual(rows["verdict"], [HARVEST])
        self.assertEqual(rows["ref_b"], ["master"])
        self.assertEqual(rows["narHash_b"], [HASH_B])

    def test_json_lock_objects(self):
        proc = run_cli([str(FIX / "064-expected.json"), str(FIX / "064-got.json")])
        self.assertEqual(proc.returncode, 1, proc.stderr)
        rows = parse_rows(proc.stdout)
        self.assertEqual(rows["verdict"], [HARVEST])
        self.assertEqual(rows["source_a"], ["json"])
        self.assertEqual(rows["source_b"], ["json"])
        self.assertEqual(rows["ref_b"], ["master"])
        self.assertIn("lastModified", rows["equal"])

    def test_flake_lock_single_node(self):
        proc = run_cli([str(FIX / "064-expected.json"), str(FIX / "064-got.lock")])
        self.assertEqual(proc.returncode, 1, proc.stderr)
        rows = parse_rows(proc.stdout)
        self.assertEqual(rows["verdict"], [HARVEST])
        self.assertEqual(rows["source_b"], ["json"])

    def test_json_without_rev_is_not_a_lock_record(self):
        with tempfile.TemporaryDirectory() as tmp:
            td = Path(tmp)
            bad = td / "bad.json"
            bad.write_text('{"foo": 1, "url": "x", "type": "git"}\n', encoding="utf-8")
            proc = run_cli([str(bad), str(FIX / "064-got.json")])
        self.assertEqual(proc.returncode, 1)
        self.assertEqual(proc.stdout, "")
        self.assertIn("not a lock record", proc.stderr)

    def test_prose_is_not_a_lock_record(self):
        with tempfile.TemporaryDirectory() as tmp:
            td = Path(tmp)
            prose = td / "note.txt"
            prose.write_text("this is not a lock\n", encoding="utf-8")
            proc = run_cli([str(prose), str(FIX / "064-got.rec")])
        self.assertEqual(proc.returncode, 1)
        self.assertIn("not a lock record", proc.stderr)

    def test_huge_narhash_is_capped(self):
        huge_a = "sha256-" + ("A" * 400)
        huge_b = "sha256-" + ("B" * 400)
        with tempfile.TemporaryDirectory() as tmp:
            td = Path(tmp)
            a, b = write_pair(
                td,
                rec(f"rev\t{REV}", f"narHash\t{huge_a}"),
                rec(f"rev\t{REV}", f"narHash\t{huge_b}"),
            )
            proc = run_cli([str(a), str(b)])
        self.assertEqual(proc.returncode, 1, proc.stderr)
        rows = parse_rows(proc.stdout)
        self.assertEqual(rows["verdict"], ["hash-changed-no-ref"])
        self.assertEqual(rows["narHash_capped"], ["yes"])
        self.assertLess(len(rows["narHash_a"][0]), 120)
        self.assertTrue(rows["narHash_a"][0].endswith("…"))

    def test_no_args_is_usage(self):
        proc = run_cli([])
        self.assertEqual(proc.returncode, 2)

    def test_stdin_twice_is_error(self):
        proc = run_cli(["-", "-"], stdin=(FIX / "064-expected.rec").read_text())
        self.assertEqual(proc.returncode, 1)
        self.assertIn("cannot read stdin twice", proc.stderr)


if __name__ == "__main__":
    unittest.main()
