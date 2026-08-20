import json
import unittest
from io import StringIO
from pathlib import Path

from neappkg.cli import run
from neappkg.overlay import overlay_diff
from neappkg.stacks import neap_from_images, stacks_in_source

ROOT = Path(__file__).resolve().parents[1]


def _run(argv, stdin_text=None):
    stdin = StringIO(stdin_text) if stdin_text is not None else StringIO("")
    stdin.isatty = lambda: False  # type: ignore[method-assign]
    # capture stdout
    import sys
    from io import StringIO as S

    out, err = S(), S()
    old_out, old_err = sys.stdout, sys.stderr
    try:
        sys.stdout, sys.stderr = out, err
        rc = run(argv, stdin=stdin)
    finally:
        sys.stdout, sys.stderr = old_out, old_err
    return rc, out.getvalue(), err.getvalue()


class TestOverlayDeaths(unittest.TestCase):
    def test_island_names_flow_not_births(self):
        rc, out, _ = _run(
            [
                "--base",
                ":wt",
                "--diff",
                str(ROOT / "fixtures/island.diff"),
                "--json",
                "-C",
                str(ROOT),
            ]
        )
        self.assertEqual(rc, 0, out)
        data = json.loads(out)
        labels = " ".join(p["label"] for p in data["neap"])
        self.assertIn("flow_score", labels)
        self.assertNotIn("unique_mod", labels)
        self.assertGreater(data["born"], 0)
        self.assertNotEqual(data["deaths"], data["born"])
        self.assertGreaterEqual(len(data["neap"]), 1)

    def test_island_does_not_write_mods(self):
        for i in range(3):
            self.assertFalse((ROOT / f"fixtures/mod{i}.py").exists())
        _run(
            [
                "--base",
                ":wt",
                "--diff",
                str(ROOT / "fixtures/island.diff"),
                "-q",
                "-C",
                str(ROOT),
            ]
        )
        for i in range(3):
            self.assertFalse((ROOT / f"fixtures/mod{i}.py").exists())
        self.assertTrue((ROOT / "fixtures/river.py").exists())

    def test_birth_only_newif_is_silent(self):
        rc, out, _ = _run(
            [
                "--base",
                ":wt",
                "--diff",
                str(ROOT / "fixtures/newif.diff"),
                "--json",
                "-C",
                str(ROOT),
            ]
        )
        self.assertEqual(rc, 1, out)
        data = json.loads(out)
        self.assertEqual(data["neap"], [])
        self.assertGreater(data["born"], 0)

    def test_move_is_silent(self):
        rc, out, _ = _run(
            [
                "--base",
                ":wt",
                "--diff",
                str(ROOT / "fixtures/move.diff"),
                "--json",
                "-C",
                str(ROOT),
            ]
        )
        self.assertEqual(rc, 1, out)
        data = json.loads(out)
        self.assertEqual(data["neap"], [])
        self.assertGreater(data["moves"], 0)
        self.assertFalse((ROOT / "fixtures/parse_moved.py").exists())

    def test_copied_stack_is_not_a_death(self):
        rc, out, _ = _run(
            [
                "--base",
                ":wt",
                "--diff",
                str(ROOT / "fixtures/copyguard.diff"),
                "--json",
                "-C",
                str(ROOT),
            ]
        )
        data = json.loads(out)
        labels = " ".join(p["label"] for p in data["neap"])
        # if flow_score > 0.2 is copied into site.py — AB, not exclusive-A
        self.assertNotIn("flow_score > 0.2", labels)
        self.assertFalse((ROOT / "fixtures/site.py").exists())

    def test_strip_guard_default_silent_also_changed_names_it(self):
        rc, out, _ = _run(
            [
                "--base",
                ":wt",
                "--diff",
                str(ROOT / "fixtures/strip.diff"),
                "--json",
                "-C",
                str(ROOT),
            ]
        )
        self.assertEqual(rc, 1, out)
        data = json.loads(out)
        self.assertEqual(data["neap"], [])
        rc2, out2, _ = _run(
            [
                "--base",
                ":wt",
                "--diff",
                str(ROOT / "fixtures/strip.diff"),
                "--also-changed",
                "--json",
                "-C",
                str(ROOT),
            ]
        )
        self.assertEqual(rc2, 0, out2)
        data2 = json.loads(out2)
        labels = " ".join(p["label"] for p in data2["neap"])
        self.assertTrue("ready" in labels, labels)

    def test_head_only_is_not_overlay_deaths(self):
        keep = (ROOT / "fixtures/keep.py").read_text()
        river = (ROOT / "fixtures/river.py").read_text()
        keep_keys = set(stacks_in_source(keep, "fixtures/keep.py"))
        river_keys = set(stacks_in_source(river, "fixtures/river.py"))
        head_only = keep_keys | river_keys
        images = overlay_diff(
            (ROOT / "fixtures/island.diff").read_text(),
            ROOT,
            base=":wt",
        )
        report = neap_from_images(images)
        death_keys = {s.key for s in report.covering}
        self.assertTrue(death_keys)
        self.assertNotEqual(death_keys, head_only)
        # keep_flag lives on HEAD and is not in the overlay deaths
        keep_labels = {" | ".join(f"{k} {p}".strip() for k, p in key) for key in keep_keys}
        covering = {s.label for s in report.covering}
        self.assertTrue(any("keep" in lab for lab in keep_labels))
        self.assertFalse(any("keep" in lab for lab in covering))

    def test_no_diff_is_usage(self):
        import sys
        from io import StringIO as S

        err = S()
        old = sys.stderr
        fake = StringIO("")
        fake.isatty = lambda: True  # type: ignore[method-assign]
        try:
            sys.stderr = err
            rc = run([], stdin=fake)
        finally:
            sys.stderr = old
        self.assertEqual(rc, 2)

    def test_computed_var_if_is_a_stack(self):
        src = (ROOT / "fixtures/river.swift").read_text()
        hits = stacks_in_source(src, "fixtures/river.swift")
        labels = [ " | ".join(f"{k} {p}".strip() for k, p in key) for key in hits ]
        self.assertTrue(any("flowScore > 0.2" in lab for lab in labels), labels)
        self.assertFalse(any("stored" in lab for lab in labels), labels)

    def test_wrap_is_not_a_death(self):
        images = overlay_diff(
            (ROOT / "fixtures/newif.diff").read_text(),
            ROOT,
            base=":wt",
        )
        report = neap_from_images(images, also_changed=True)
        self.assertEqual(report.deaths, [])
        self.assertGreater(report.born_n, 0)

    def test_directory_operand_refused(self):
        rc, _, err = _run(
            [
                "--base",
                ":wt",
                "--diff",
                str(ROOT / "fixtures/island.diff"),
                str(ROOT / "fixtures"),
                "-C",
                str(ROOT),
            ]
        )
        self.assertEqual(rc, 2)
        self.assertIn("refusing to walk", err)


if __name__ == "__main__":
    unittest.main()
