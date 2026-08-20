import json
import unittest
from io import StringIO
from pathlib import Path

from dirgepkg.cli import run
from dirgepkg.overlay import overlay_diff
from dirgepkg.stacks import dirge_from_images, stacks_in_source

ROOT = Path(__file__).resolve().parents[1]


def _run(argv, stdin_text=None):
    stdin = StringIO(stdin_text) if stdin_text is not None else StringIO("")
    stdin.isatty = lambda: False  # type: ignore[method-assign]
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


class TestOverlayObituaries(unittest.TestCase):
    def test_island_one_obituary_not_two_sibling_rows(self):
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
        self.assertEqual(len(data["dirge"]), 1, data["dirge"])
        obit = data["dirge"][0]
        self.assertGreaterEqual(obit["arm_n"], 2)
        labels = " ".join(obit["label"] for obit in data["dirge"])
        arm_labels = " ".join(a["label"] for a in obit["arms"])
        self.assertIn("flow_score", labels + " " + arm_labels)
        self.assertNotIn("unique_mod", labels + " " + arm_labels)
        self.assertGreater(data["born"], 0)
        self.assertNotEqual(data["deaths"], data["born"])

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

    def test_seq_clusters_elif_and_sequential(self):
        rc, out, _ = _run(
            [
                "--base",
                ":wt",
                "--diff",
                str(ROOT / "fixtures/seq.diff"),
                "--json",
                "-C",
                str(ROOT),
            ]
        )
        self.assertEqual(rc, 0, out)
        data = json.loads(out)
        self.assertEqual(len(data["dirge"]), 1, json.dumps(data["dirge"], indent=2))
        self.assertGreaterEqual(data["dirge"][0]["arm_n"], 3)
        self.assertEqual(data["dirge"][0]["label"], "if app.flowScore > 0.2")
        self.assertTrue(
            data["dirge"][0]["pin"].endswith(":4")
            or "flowScore > 0.2" in data["dirge"][0]["label"],
            data["dirge"][0]["pin"],
        )
        joined = " ".join(a["label"] for a in data["dirge"][0]["arms"])
        self.assertIn("flowScore", joined)
        self.assertNotIn("stored", joined)
        self.assertFalse(data["dirge"][0]["label"].startswith("given"))

    def test_twochain_stays_two_obituaries(self):
        rc, out, _ = _run(
            [
                "--base",
                ":wt",
                "--diff",
                str(ROOT / "fixtures/twochain.diff"),
                "--json",
                "-C",
                str(ROOT),
            ]
        )
        self.assertEqual(rc, 0, out)
        data = json.loads(out)
        self.assertEqual(len(data["dirge"]), 2, json.dumps(data["dirge"], indent=2))
        self.assertTrue(all(o["arm_n"] == 2 for o in data["dirge"]))

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
        self.assertEqual(data["dirge"], [])
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
        self.assertEqual(data["dirge"], [])
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
        labels = " ".join(p["label"] for p in data["dirge"])
        arms = " ".join(a["label"] for p in data["dirge"] for a in p.get("arms", []))
        self.assertNotIn("flow_score > 0.2", labels + " " + arms)
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
        self.assertEqual(data["dirge"], [])
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
        labels = " ".join(p["label"] for p in data2["dirge"])
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
        report = dirge_from_images(images)
        death_keys = {s.key for o in report.covering for s in o.members}
        self.assertTrue(death_keys)
        self.assertNotEqual(death_keys, head_only)
        keep_labels = {" | ".join(f"{k} {p}".strip() for k, p in key) for key in keep_keys}
        covering = {s.label for o in report.covering for s in o.members}
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
        labels = [" | ".join(f"{k} {p}".strip() for k, p in key) for key in hits]
        self.assertTrue(any("flowScore > 0.2" in lab for lab in labels), labels)
        self.assertFalse(any("stored" in lab for lab in labels), labels)

    def test_wrap_is_not_a_death(self):
        images = overlay_diff(
            (ROOT / "fixtures/newif.diff").read_text(),
            ROOT,
            base=":wt",
        )
        report = dirge_from_images(images, also_changed=True)
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
