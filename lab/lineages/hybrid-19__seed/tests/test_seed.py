#!/usr/bin/env python3
from __future__ import annotations

import io
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from seedline.cli import main
from seedline.diffio import file_matches_pins, parse_locator_line, recover_file_from_pins
from seedline.query import query_file
from seedline.rhyme import relation
from seedline.scan import collapse_hits, drop_noise, hits_in_file


def _git(files: dict[str, str]) -> Path:
    d = Path(tempfile.mkdtemp(prefix="seed-"))
    subprocess.run(["git", "init"], cwd=d, check=True, capture_output=True)
    for name, content in files.items():
        p = d / name
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_text(content)
    subprocess.run(["git", "add", "-A"], cwd=d, check=True, capture_output=True)
    return d


class NestedRhymeTests(unittest.TestCase):
    def setUp(self) -> None:
        self.path = ROOT / "fixtures" / "nested.py"
        self.seed13 = query_file(self.path, 13)
        self.seed8 = query_file(self.path, 8)
        self.seed10 = query_file(self.path, 10)

    def test_denied_is_exact_only_itself(self) -> None:
        hits = hits_in_file(self.path, self.seed13, exact=True)
        lines = {h.loc.line for h in hits}
        self.assertEqual(lines, {13})
        self.assertTrue(all(h.relation == "same" for h in hits))

    def test_denied_does_not_rhyme_with_drained(self) -> None:
        hits = hits_in_file(self.path, self.seed13)
        lines = {h.loc.line for h in hits}
        self.assertIn(13, lines)
        self.assertNotIn(34, lines)
        self.assertNotIn(6, lines)

    def test_after_none_guard_is_superset_of_locked_and_pending(self) -> None:
        hits = hits_in_file(self.path, self.seed8)
        lines = {h.loc.line for h in hits}
        self.assertIn(8, lines)
        self.assertIn(13, lines)
        self.assertIn(34, lines)
        self.assertNotIn(6, lines)
        self.assertNotIn(45, lines)

    def test_try_body_does_not_include_except(self) -> None:
        hits = hits_in_file(self.path, self.seed10)
        lines = {h.loc.line for h in hits}
        self.assertIn(10, lines)
        self.assertIn(13, lines)
        self.assertNotIn(17, lines)
        self.assertNotIn(19, lines)
        exact = hits_in_file(self.path, self.seed10, exact=True)
        exact_lines = {h.loc.line for h in exact}
        self.assertNotIn(13, exact_lines)

    def test_relation_prefix(self) -> None:
        loc8 = query_file(self.path, 8)
        loc13 = query_file(self.path, 13)
        loc6 = query_file(self.path, 6)
        self.assertEqual(relation(loc8, loc13), "deeper")
        self.assertEqual(relation(loc13, loc13), "same")
        self.assertIsNone(relation(loc13, loc8))
        self.assertIsNone(relation(loc8, loc6))


class BraceRhymeTests(unittest.TestCase):
    def test_rust_fallthrough_not_early_return(self) -> None:
        path = ROOT / "fixtures" / "guards.rs"
        seed = query_file(path, 11)
        hits = hits_in_file(path, seed)
        lines = {h.loc.line for h in hits}
        self.assertIn(11, lines)
        self.assertNotIn(3, lines)
        self.assertNotIn(6, lines)
        self.assertNotIn(9, lines)

    def test_swift_guard_body_not_else(self) -> None:
        path = ROOT / "fixtures" / "sample.swift"
        seed = query_file(path, 6)
        hits = hits_in_file(path, seed)
        lines = {h.loc.line for h in hits}
        self.assertIn(6, lines)
        self.assertNotIn(3, lines)
        self.assertIn(10, lines)


class CollapseTests(unittest.TestCase):
    def test_collapse_contiguous(self) -> None:
        path = ROOT / "fixtures" / "nested.py"
        seed = query_file(path, 8)
        raw = hits_in_file(path, seed)
        collapsed = collapse_hits(raw)
        self.assertLess(len(collapsed), len(raw))

    def test_noise_drop_prefers_let_not_brace(self) -> None:
        path = ROOT / "fixtures" / "guards.rs"
        seed = query_file(path, 11)
        raw = hits_in_file(path, seed, exact=True)
        cleaned = drop_noise(raw)
        collapsed = collapse_hits(cleaned)
        self.assertTrue(collapsed)
        heres = {h.loc.here.strip() for h in collapsed}
        self.assertTrue(any("let p" in h or "Some(p)" in h for h in heres))
        self.assertNotIn("}", heres)


class LocatorParseTests(unittest.TestCase):
    def test_rg_nh(self) -> None:
        loc = parse_locator_line(
            'fixtures/guards.rs:8:        if !bytes.starts_with(b"a/") {'
        )
        assert loc is not None
        self.assertEqual(loc.file, "fixtures/guards.rs")
        self.assertEqual(loc.line, 8)

    def test_rg_l(self) -> None:
        loc = parse_locator_line(str(ROOT / "fixtures" / "guards.rs"))
        assert loc is not None
        self.assertIsNone(loc.line)

    def test_bare_line_keeps_pin_without_file(self) -> None:
        loc = parse_locator_line('13:    return "denied"')
        assert loc is not None
        self.assertEqual(loc.file, "")
        self.assertEqual(loc.line, 13)

    def test_file_line_only(self) -> None:
        loc = parse_locator_line("parse.rs:60")
        assert loc is not None
        self.assertEqual(loc.file, "parse.rs")
        self.assertEqual(loc.line, 60)


class PinIdentityTests(unittest.TestCase):
    def test_substring_is_not_a_match(self) -> None:
        d = _git(
            {
                "real.py": 'def f(x):\n    if x:\n        return 1\n',
                "decoy.py": 'def f(x):\n    if x:\n        note = "return None is mentioned here"\n',
            }
        )
        pins = [(3, "return None")]
        self.assertFalse(file_matches_pins(d / "decoy.py", pins))
        self.assertFalse(file_matches_pins(d / "real.py", pins))

    def test_stripped_line_is_a_match(self) -> None:
        d = _git({"real.py": 'def f(x):\n    if x:\n        return None\n'})
        self.assertTrue(file_matches_pins(d / "real.py", [(3, "return None")]))

    def test_substring_decoy_refuses_recovery(self) -> None:
        d = _git(
            {
                "real.py": 'def f(x):\n    if x:\n        return 1\n',
                "decoy.py": 'def f(x):\n    if x:\n        note = "return None is mentioned here"\n',
            }
        )
        from seedline.diffio import Locator

        got = recover_file_from_pins(
            [Locator(file="", line=3, here="return None")],
            repo=d,
        )
        self.assertIsNone(got)

    def test_all_pins_not_capped_at_16(self) -> None:
        shared = "\n".join(f"        let shared_{i} = {i};" for i in range(1, 17))
        real = (
            "fn f() {\n    if true {\n"
            + shared
            + "\n        let UNIQUE_REAL = 1;\n    }\n}\n"
        )
        decoy = (
            "fn f() {\n    if true {\n"
            + shared
            + "\n        let UNIQUE_DECOY = 2;\n    }\n}\n"
        )
        d = _git({"real.rs": real, "decoy.rs": decoy})
        from seedline.diffio import Locator

        shared_pins = [
            Locator(file="", line=2 + i, here=f"let shared_{i} = {i};")
            for i in range(1, 17)
        ]
        # 16 shared pins match both files → refuse
        self.assertIsNone(recover_file_from_pins(shared_pins, repo=d))
        # 17th pin distinguishes
        all_pins = shared_pins + [
            Locator(file="", line=19, here="let UNIQUE_REAL = 1;")
        ]
        got = recover_file_from_pins(all_pins, repo=d)
        self.assertIsNotNone(got)
        self.assertEqual(got.name, "real.rs")


class CliTests(unittest.TestCase):
    def _run(self, argv, stdin: str | None = None) -> tuple[int, str, str]:
        out = io.StringIO()
        err = io.StringIO()
        old_out, old_err = sys.stdout, sys.stderr
        sys.stdout, sys.stderr = out, err
        try:
            rc = main(argv, stdin=io.StringIO(stdin if stdin is not None else ""))
        finally:
            sys.stdout, sys.stderr = old_out, old_err
        return rc, out.getvalue(), err.getvalue()

    def test_explain_denied_exact(self) -> None:
        rc, out, _ = self._run(
            [f"{ROOT / 'fixtures' / 'nested.py'}:13", "--exact", "--explain"]
        )
        self.assertEqual(rc, 0)
        self.assertIn("denied", out)
        self.assertNotIn("drained", out)

    def test_try_exact_is_flush_and_return_not_except(self) -> None:
        rc, out, _ = self._run(
            [f"{ROOT / 'fixtures' / 'nested.py'}:10", "--exact", "--explain"]
        )
        self.assertEqual(rc, 0)
        self.assertIn("db.flush()", out)
        self.assertIn("return None", out)
        self.assertNotIn("except", out)
        self.assertNotIn("denied", out)

    def test_same_as_flag(self) -> None:
        rc, out, _ = self._run(
            [
                "--same-as",
                f"{ROOT / 'fixtures' / 'nested.py'}:13",
                "--exact",
                "--tsv",
            ]
        )
        self.assertEqual(rc, 0)
        self.assertIn("denied", out)

    def test_missing_locus(self) -> None:
        rc, _, err = self._run([])
        self.assertEqual(rc, 2)
        self.assertIn("No cwd walk", err)

    def test_refuses_dir_walk(self) -> None:
        rc, _, err = self._run(
            [f"{ROOT / 'fixtures' / 'nested.py'}:13", str(ROOT / "fixtures")]
        )
        self.assertEqual(rc, 2)
        self.assertIn("will not walk", err)

    def test_guards_here_is_payload(self) -> None:
        rc, out, _ = self._run(
            [f"{ROOT / 'fixtures' / 'guards.rs'}:11", "--exact", "--explain"]
        )
        self.assertEqual(rc, 0)
        self.assertIn("let p", out)
        self.assertNotIn("here   }", out)

    def test_stdin_locators_scan_the_file_not_the_lines(self) -> None:
        guards = ROOT / "fixtures" / "guards.rs"
        stdin = f"{guards}:11:    let p = (bytes.len() - 5) / 2;\n"
        rc, out, err = self._run(["--tsv"], stdin=stdin)
        self.assertEqual(rc, 0, err)
        self.assertIn("let p", out)
        self.assertIn("11-12", out)
        self.assertNotIn("return None", out)

    def test_rg_l_needs_a_seed(self) -> None:
        nested = ROOT / "fixtures" / "nested.py"
        rc, _, err = self._run(["--tsv"], stdin=f"{nested}\n")
        self.assertEqual(rc, 2)
        self.assertIn("locus", err)

    def test_rg_l_plus_same_as_scans_named_file(self) -> None:
        nested = ROOT / "fixtures" / "nested.py"
        rc, out, _ = self._run(
            ["--same-as", f"{nested}:13", "--exact", "--tsv"],
            stdin=f"{nested}\n",
        )
        self.assertEqual(rc, 0)
        self.assertIn("denied", out)
        self.assertNotIn("drained", out)

    def test_hits_filters_locator_lines(self) -> None:
        nested = ROOT / "fixtures" / "nested.py"
        rc, out, _ = self._run(
            [f"{nested}:8", "--hits", "--tsv"],
            stdin='13:    return "denied"\n6:        audit.warn("missing")\n',
        )
        self.assertEqual(rc, 0)
        self.assertIn(":13", out)
        self.assertNotIn(":6", out)

    def test_bare_unique_pin_recovers_and_seeds(self) -> None:
        nested = (ROOT / "fixtures" / "nested.py").read_text()
        d = _git({"nested.py": nested})
        rc, out, err = self._run(
            ["--exact", "--tsv", "--repo", str(d)],
            stdin='13:    return "denied"\n',
        )
        self.assertEqual(rc, 0, err)
        self.assertIn("denied", out)
        self.assertNotIn("drained", out)

    def test_bag_of_stacks_refuses(self) -> None:
        nested = (ROOT / "fixtures" / "nested.py").read_text()
        d = _git({"nested.py": nested})
        rc, out, err = self._run(
            ["--exact", "--tsv", "--repo", str(d)],
            stdin='13:    return "denied"\n34:            return "drained"\n',
        )
        self.assertEqual(rc, 2, out)
        self.assertIn("stacks", err)
        self.assertNotIn("denied", out)
        self.assertNotIn("drained", out)

    def test_first_restores_locator_order(self) -> None:
        nested = (ROOT / "fixtures" / "nested.py").read_text()
        d = _git({"nested.py": nested})
        rc, out, err = self._run(
            ["--first", "--exact", "--tsv", "--repo", str(d)],
            stdin='13:    return "denied"\n34:            return "drained"\n',
        )
        self.assertEqual(rc, 0, err)
        self.assertIn("denied", out)
        self.assertNotIn("drained", out)

    def test_same_as_overrides_bag(self) -> None:
        nested = ROOT / "fixtures" / "nested.py"
        d = _git({"nested.py": nested.read_text()})
        rc, out, err = self._run(
            [
                "--same-as",
                f"{d / 'nested.py'}:13",
                "--exact",
                "--tsv",
                "--repo",
                str(d),
            ],
            stdin='13:    return "denied"\n34:            return "drained"\n',
        )
        self.assertEqual(rc, 0, err)
        self.assertIn("denied", out)
        self.assertNotIn("drained", out)

    def test_same_as_colon_line_binds_recovered_file(self) -> None:
        nested = (ROOT / "fixtures" / "nested.py").read_text()
        d = _git({"nested.py": nested})
        rc, out, err = self._run(
            ["--same-as", ":13", "--exact", "--tsv", "--repo", str(d)],
            stdin='13:    return "denied"\n34:            return "drained"\n',
        )
        self.assertEqual(rc, 0, err)
        self.assertIn("denied", out)
        self.assertNotIn("drained", out)

    def test_same_as_colon_line_needs_a_file(self) -> None:
        rc, _, err = self._run(["--same-as", ":13", "--tsv"])
        self.assertEqual(rc, 2)
        self.assertIn(":LINE", err)

    def test_argv_colon_line_plus_file(self) -> None:
        nested = ROOT / "fixtures" / "nested.py"
        rc, out, err = self._run([":13", "--exact", "--tsv", str(nested)])
        self.assertEqual(rc, 0, err)
        self.assertIn("denied", out)
        self.assertNotIn("drained", out)

    def test_bag_fixture_refuses(self) -> None:
        bag = ROOT / "fixtures" / "bag.py"
        stdin = (
            f"{bag}:6:        return None\n"
            f"{bag}:8:        return None\n"
        )
        rc, out, err = self._run(["--explain"], stdin=stdin)
        self.assertEqual(rc, 2, out)
        self.assertIn("2 stacks", err)
        self.assertIn(":6", err)
        self.assertIn(":8", err)

    def test_same_stack_two_pins_is_not_a_bag(self) -> None:
        guards = ROOT / "fixtures" / "guards.rs"
        stdin = (
            f"{guards}:12:    Some(p)\n"
            f"{guards}:11:    let p = (bytes.len() - 5) / 2;\n"
        )
        rc, out, err = self._run(["--exact", "--tsv"], stdin=stdin)
        self.assertEqual(rc, 0, err)
        self.assertIn("let p", out)
        self.assertIn("11-12", out)

    def test_bare_line_unknown_pins_refuse(self) -> None:
        rc, _, err = self._run(
            ["--tsv"],
            stdin="9999:    this-line-does-not-exist-xyzzy\n",
        )
        self.assertEqual(rc, 2)
        self.assertIn("LINE:text", err)

    def test_bare_line_plus_file_operand_scans(self) -> None:
        nested = ROOT / "fixtures" / "nested.py"
        rc, out, _ = self._run(
            ["--tsv", str(nested)],
            stdin='13:    return "denied"\n',
        )
        self.assertEqual(rc, 0)
        self.assertIn("denied", out)
        self.assertNotIn("drained", out)
        self.assertEqual(out.count("denied"), 1)

    def test_seventeenth_pin_recovers_via_cli(self) -> None:
        shared = "\n".join(f"        let shared_{i} = {i};" for i in range(1, 17))
        real = (
            "fn f() {\n    if true {\n"
            + shared
            + "\n        let UNIQUE_REAL = 1;\n    }\n}\n"
        )
        decoy = (
            "fn f() {\n    if true {\n"
            + shared
            + "\n        let UNIQUE_DECOY = 2;\n    }\n}\n"
        )
        d = _git({"real.rs": real, "decoy.rs": decoy})
        lines = [f"{2 + i}:        let shared_{i} = {i};" for i in range(1, 17)]
        lines.append("19:        let UNIQUE_REAL = 1;")
        rc, out, err = self._run(
            ["--explain", "--repo", str(d)],
            stdin="\n".join(lines) + "\n",
        )
        self.assertEqual(rc, 0, err)
        self.assertIn("real.rs", out)
        self.assertIn("2-19", out)
        self.assertNotIn("UNIQUE_DECOY", out)
        self.assertNotIn("decoy.rs", out)

    def test_sixteen_shared_pins_refuse(self) -> None:
        shared = "\n".join(f"        let shared_{i} = {i};" for i in range(1, 17))
        real = (
            "fn f() {\n    if true {\n"
            + shared
            + "\n        let UNIQUE_REAL = 1;\n    }\n}\n"
        )
        decoy = (
            "fn f() {\n    if true {\n"
            + shared
            + "\n        let UNIQUE_DECOY = 2;\n    }\n}\n"
        )
        d = _git({"real.rs": real, "decoy.rs": decoy})
        lines = [f"{2 + i}:        let shared_{i} = {i};" for i in range(1, 17)]
        rc, _, err = self._run(
            ["--explain", "--repo", str(d)],
            stdin="\n".join(lines) + "\n",
        )
        self.assertEqual(rc, 2)
        self.assertIn("LINE:text", err)


if __name__ == "__main__":
    unittest.main()
