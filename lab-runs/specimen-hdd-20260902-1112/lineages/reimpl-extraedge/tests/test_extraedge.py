#!/usr/bin/env python3
"""Two-pass attach graph: mapped extra-edge missing is a miss."""

from __future__ import annotations

import importlib.machinery
import importlib.util
import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CLI = ROOT / "extraedge"
FIX = ROOT / "fixtures"


def load_cli():
    loader = importlib.machinery.SourceFileLoader("extraedge2_cli", str(CLI))
    spec = importlib.util.spec_from_loader(loader.name, loader)
    assert spec is not None
    mod = importlib.util.module_from_spec(spec)
    sys.modules[loader.name] = mod
    loader.exec_module(mod)
    return mod


MOD = load_cli()


def run_cli(args: list[str], stdin: str | None = None) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [sys.executable, str(CLI), *args],
        input=stdin,
        capture_output=True,
        text=True,
        check=False,
    )


def rows_of(text: str) -> dict[str, list[str]]:
    rows: dict[str, list[str]] = {}
    for line in text.splitlines():
        if not line or "\t" not in line:
            continue
        key, *rest = line.split("\t")
        rows[key] = rest
    return rows


def rec(*pairs: tuple[str, str]) -> str:
    return "".join(f"{key}\t{value}\n" for key, value in pairs)


def write_pair(dir_path: Path, a: str, b: str) -> tuple[Path, Path]:
    first = dir_path / "a.rec"
    second = dir_path / "b.rec"
    first.write_text(a, encoding="utf-8")
    second.write_text(b, encoding="utf-8")
    return first, second


class GraphTwoPassTests(unittest.TestCase):
    def test_ingest_then_walk_names_miss_and_later_attach(self):
        first = MOD.load_document((FIX / "021-edit.rec").read_text(), source="edit")
        second = MOD.load_document((FIX / "021-add.rec").read_text(), source="add")
        graph = MOD.AttachGraph()
        graph.ingest("a", first)
        self.assertEqual(graph.out["postgresql"], ["psycopg2"])
        self.assertEqual(graph.edges["psycopg2"].attached, set())
        graph.ingest("b", second)
        self.assertEqual(graph.edges["psycopg2"].attached, {"b"})
        result = graph.walk()
        self.assertTrue(result["same_package"])
        self.assertEqual(result["missed_a"], ["postgresql"])
        self.assertEqual(result["missed_b"], [])
        self.assertEqual(result["attached_b"], ["psycopg2"])
        ops = [ev["op"] for ev in graph.trace]
        self.assertIn("map", ops)
        self.assertIn("attach", ops)
        self.assertIn("miss", ops)
        self.assertIn("only_b", ops)

    def test_json_edges_compile_to_the_same_document_shape(self):
        rec_doc = MOD.load_document((FIX / "021-edit.rec").read_text(), source="rec")
        json_doc = MOD.load_document((FIX / "021-edit.json").read_text(), source="json")
        for key in ("package", "version", "declared", "resolved"):
            self.assertEqual(rec_doc[key], json_doc[key], key)
        self.assertEqual(rec_doc["extras"], json_doc["extras"])


class FixtureCliTests(unittest.TestCase):
    def test_owned_021_pair(self):
        proc = run_cli([str(FIX / "021-edit.rec"), str(FIX / "021-add.rec")])
        self.assertEqual(proc.returncode, 1, proc.stderr)
        rows = rows_of(proc.stdout)
        self.assertEqual(rows["same_package"], ["yes"])
        self.assertEqual(rows["package_a"], ["sqlalchemy"])
        self.assertEqual(rows["package_b"], ["sqlalchemy"])
        self.assertEqual(rows["map"], ["postgresql", "psycopg2"])
        self.assertEqual(rows["missed_a"], ["postgresql"])
        self.assertEqual(rows["missed_b"], ["."])
        self.assertEqual(rows["attached_b"], ["psycopg2"])
        self.assertEqual(rows["resolved_a"], ["."])

    def test_json_021_matches_tsv(self):
        tsv = run_cli([str(FIX / "021-edit.rec"), str(FIX / "021-add.rec")])
        js = run_cli([str(FIX / "021-edit.json"), str(FIX / "021-add.json")])
        self.assertEqual(tsv.returncode, js.returncode)
        self.assertEqual(tsv.stdout, js.stdout)

    def test_add_lock_as_first_is_not_a_miss(self):
        proc = run_cli([str(FIX / "021-add.rec"), str(FIX / "021-add.rec")])
        self.assertEqual(proc.returncode, 0, proc.stderr)
        rows = rows_of(proc.stdout)
        self.assertEqual(rows["missed_a"], ["."])
        self.assertEqual(rows["missed_b"], ["."])
        self.assertEqual(rows["attached_b"], ["."])
        self.assertEqual(rows["resolved_a"], ["psycopg2"])
        self.assertEqual(rows["map"], ["postgresql", "psycopg2"])

    def test_unseen_partial_attach(self):
        proc = run_cli([str(FIX / "unseen-edit.rec"), str(FIX / "unseen-add.rec")])
        self.assertEqual(proc.returncode, 1, proc.stderr)
        rows = rows_of(proc.stdout)
        self.assertEqual(rows["missed_a"], ["feat"])
        self.assertEqual(rows["missed_b"], ["."])
        self.assertEqual(rows["attached_b"], ["widget"])

    def test_missing_package_errors(self):
        proc = run_cli([str(FIX / "021-edit.rec"), "/dev/null"])
        self.assertEqual(proc.returncode, 1)
        self.assertEqual(proc.stdout, "")
        self.assertIn("missing package", proc.stderr)


class MappingTests(unittest.TestCase):
    def test_honest_021_typing_extensions_is_a_miss(self):
        with tempfile.TemporaryDirectory() as tmp:
            first, second = write_pair(
                Path(tmp),
                rec(
                    ("package", "sqlalchemy"),
                    ("version", "2.1.0b1.dev0"),
                    ("declared", "postgresql"),
                    ("extra", "postgresql\tpsycopg2"),
                    ("resolved", "typing-extensions"),
                ),
                rec(
                    ("package", "sqlalchemy"),
                    ("version", "2.1.0b1.dev0"),
                    ("declared", "postgresql"),
                    ("extra", "postgresql\tpsycopg2"),
                    ("resolved", "psycopg2"),
                ),
            )
            proc = run_cli([str(first), str(second)])
        self.assertEqual(proc.returncode, 1, proc.stderr)
        rows = rows_of(proc.stdout)
        self.assertEqual(rows["resolved_a"], ["typing-extensions"])
        self.assertEqual(rows["missed_a"], ["postgresql"])
        self.assertEqual(rows["missed_b"], ["."])
        self.assertEqual(rows["attached_b"], ["psycopg2"])
        self.assertNotIn("typing-extensions", rows["attached_b"])

    def test_two_extras_one_attach_names_the_miss(self):
        with tempfile.TemporaryDirectory() as tmp:
            first, second = write_pair(
                Path(tmp),
                rec(
                    ("package", "sqlalchemy"),
                    ("version", "2.1.0b1.dev0"),
                    ("declared", "postgresql\tmysql"),
                    ("extra", "postgresql\tpsycopg2"),
                    ("extra", "mysql\tmysqlclient"),
                    ("resolved", "psycopg2"),
                ),
                rec(
                    ("package", "sqlalchemy"),
                    ("version", "2.1.0b1.dev0"),
                    ("declared", "postgresql\tmysql"),
                    ("extra", "postgresql\tpsycopg2"),
                    ("extra", "mysql\tmysqlclient"),
                    ("resolved", "psycopg2\tmysqlclient"),
                ),
            )
            proc = run_cli([str(first), str(second)])
        self.assertEqual(proc.returncode, 1, proc.stderr)
        rows = rows_of(proc.stdout)
        self.assertEqual(rows["missed_a"], ["mysql"])
        self.assertEqual(rows["missed_b"], ["."])
        self.assertEqual(rows["attached_b"], ["mysqlclient"])

    def test_empty_resolved_is_all_mapped_miss(self):
        with tempfile.TemporaryDirectory() as tmp:
            first, second = write_pair(
                Path(tmp),
                rec(
                    ("package", "sqlalchemy"),
                    ("version", "2.1.0b1.dev0"),
                    ("declared", "postgresql\tmysql"),
                    ("extra", "postgresql\tpsycopg2"),
                    ("extra", "mysql\tmysqlclient"),
                    ("resolved", "."),
                ),
                rec(
                    ("package", "sqlalchemy"),
                    ("version", "2.1.0b1.dev0"),
                    ("declared", "postgresql\tmysql"),
                    ("extra", "postgresql\tpsycopg2"),
                    ("extra", "mysql\tmysqlclient"),
                    ("resolved", "psycopg2"),
                ),
            )
            proc = run_cli([str(first), str(second)])
        self.assertEqual(proc.returncode, 1, proc.stderr)
        rows = rows_of(proc.stdout)
        self.assertEqual(rows["missed_a"], ["postgresql", "mysql"])
        self.assertEqual(rows["attached_b"], ["psycopg2"])

    def test_unmapped_extra_is_refused(self):
        with tempfile.TemporaryDirectory() as tmp:
            first, second = write_pair(
                Path(tmp),
                rec(
                    ("package", "sqlalchemy"),
                    ("version", "2.1.0b1.dev0"),
                    ("declared", "postgresql"),
                    ("resolved", "typing-extensions"),
                ),
                rec(
                    ("package", "sqlalchemy"),
                    ("version", "2.1.0b1.dev0"),
                    ("declared", "postgresql"),
                    ("resolved", "psycopg2"),
                ),
            )
            proc = run_cli([str(first), str(second)])
        self.assertEqual(proc.returncode, 1, proc.stderr)
        rows = rows_of(proc.stdout)
        self.assertEqual(rows["unmapped"], ["postgresql"])
        self.assertEqual(rows["missed_a"], ["."])
        self.assertEqual(rows["attached_b"], ["."])

    def test_one_of_two_targets_present_is_not_a_miss(self):
        body = {
            "package": "p",
            "version": "1",
            "declared": ["feat"],
            "edges": [
                {"extra": "feat", "target": "alpha"},
                {"extra": "feat", "target": "beta"},
            ],
            "resolved": ["beta"],
        }
        proc = run_cli(["-", "-"], stdin="")  # sanity: both stdin refused
        self.assertEqual(proc.returncode, 1)
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "both.json"
            path.write_text(json.dumps(body), encoding="utf-8")
            proc = run_cli([str(path), str(path)])
        self.assertEqual(proc.returncode, 0, proc.stderr)
        rows = rows_of(proc.stdout)
        self.assertEqual(rows["missed_a"], ["."])
        self.assertEqual(rows["map"], ["feat", "alpha", "beta"])


class IdentityTests(unittest.TestCase):
    def test_different_package_does_not_fill_attached(self):
        with tempfile.TemporaryDirectory() as tmp:
            other = rec(
                ("package", "notsqlalchemy"),
                ("version", "2.1.0b1.dev0"),
                ("declared", "postgresql"),
                ("extra", "postgresql\tpsycopg2"),
                ("resolved", "psycopg2"),
            )
            path = Path(tmp) / "other.rec"
            path.write_text(other, encoding="utf-8")
            proc = run_cli([str(FIX / "021-edit.rec"), str(path)])
        self.assertEqual(proc.returncode, 1, proc.stderr)
        rows = rows_of(proc.stdout)
        self.assertEqual(rows["package_a"], ["sqlalchemy"])
        self.assertEqual(rows["package_b"], ["notsqlalchemy"])
        self.assertEqual(rows["version_a"], ["2.1.0b1.dev0"])
        self.assertEqual(rows["version_b"], ["2.1.0b1.dev0"])
        self.assertEqual(rows["same_package"], ["no"])
        self.assertEqual(rows["identity"], ["mismatch"])
        self.assertEqual(rows["missed_a"], ["."])
        self.assertEqual(rows["attached_b"], ["."])
        self.assertNotIn("psycopg2", proc.stdout)

    def test_duplicate_package_line_is_error(self):
        text = (
            "package\tp1\n"
            "package\tp2\n"
            "version\t1\n"
            "declared\tfeat\n"
            "extra\tfeat\twidget\n"
            "resolved\t.\n"
        )
        with self.assertRaises(ValueError) as err:
            MOD.load_document(text, source="dup")
        self.assertIn("duplicate package", str(err.exception))

    def test_extra_columns_on_package_are_error(self):
        text = (
            "package\tsqlalchemy\textra\n"
            "version\t1\n"
            "declared\tpostgresql\n"
            "extra\tpostgresql\tpsycopg2\n"
            "resolved\t.\n"
        )
        with self.assertRaises(ValueError) as err:
            MOD.load_document(text, source="cols")
        self.assertIn("extra columns on package", str(err.exception))


class LexerTests(unittest.TestCase):
    def test_extra_named_none_survives(self):
        with tempfile.TemporaryDirectory() as tmp:
            first, second = write_pair(
                Path(tmp),
                rec(
                    ("package", "p"),
                    ("version", "1"),
                    ("declared", "none"),
                    ("extra", "none\tnonepkg"),
                    ("resolved", "."),
                ),
                rec(
                    ("package", "p"),
                    ("version", "1"),
                    ("declared", "none"),
                    ("extra", "none\tnonepkg"),
                    ("resolved", "nonepkg"),
                ),
            )
            proc = run_cli([str(first), str(second)])
        self.assertEqual(proc.returncode, 1, proc.stderr)
        rows = rows_of(proc.stdout)
        self.assertEqual(rows["declared"], ["none"])
        self.assertEqual(rows["missed_a"], ["none"])
        self.assertEqual(rows["resolved_a"], ["."])
        self.assertEqual(rows["attached_b"], ["nonepkg"])

    def test_declared_space_is_one_name_tab_is_two(self):
        space = MOD.load_document(
            rec(
                ("package", "p"),
                ("version", "1"),
                ("declared", "my extra"),
                ("extra", "my extra\tdep"),
                ("resolved", "."),
            ),
            source="space",
        )
        self.assertEqual(space["declared"], ["my extra"])
        tab = MOD.load_document(
            rec(
                ("package", "p"),
                ("version", "1"),
                ("declared", "my\textra"),
                ("extra", "my\tdep1"),
                ("extra", "extra\tdep2"),
                ("resolved", "."),
            ),
            source="tab",
        )
        self.assertEqual(tab["declared"], ["my", "extra"])

    def test_empty_declared_tab_is_empty_list(self):
        record = MOD.load_document(
            "package\tp\nversion\t1\ndeclared\t\nextra\tfeat\twidget\nresolved\t.\n",
            source="emptydecl",
        )
        self.assertEqual(record["declared"], [])

    def test_dash_is_stdin(self):
        proc = run_cli(
            ["-", str(FIX / "021-add.rec")],
            stdin=(FIX / "021-edit.rec").read_text(encoding="utf-8"),
        )
        self.assertEqual(proc.returncode, 1, proc.stderr)
        rows = rows_of(proc.stdout)
        self.assertEqual(rows["missed_a"], ["postgresql"])
        self.assertEqual(rows["attached_b"], ["psycopg2"])

    def test_swapped_021_misses_on_second(self):
        proc = run_cli([str(FIX / "021-add.rec"), str(FIX / "021-edit.rec")])
        self.assertEqual(proc.returncode, 1, proc.stderr)
        rows = rows_of(proc.stdout)
        self.assertEqual(rows["missed_a"], ["."])
        self.assertEqual(rows["missed_b"], ["postgresql"])
        self.assertEqual(rows["attached_b"], ["."])
        self.assertEqual(rows["resolved_b"], ["."])

    def test_postgresql_case_is_distinct(self):
        with tempfile.TemporaryDirectory() as tmp:
            body = (
                "package\tsqlalchemy\n"
                "version\t2.1.0b1.dev0\n"
                "declared\tPostgreSQL\tpostgresql\n"
                "extra\tpostgresql\tpsycopg2\n"
                "extra\tPostgreSQL\tPsycopg2\n"
                "resolved\tpsycopg2\n"
            )
            first, second = write_pair(Path(tmp), body, body)
            proc = run_cli([str(first), str(second)])
        self.assertEqual(proc.returncode, 1, proc.stderr)
        rows = rows_of(proc.stdout)
        self.assertEqual(rows["declared"], ["PostgreSQL", "postgresql"])
        self.assertEqual(rows["missed_a"], ["PostgreSQL"])
        self.assertEqual(rows["missed_b"], ["PostgreSQL"])
        self.assertEqual(rows["attached_b"], ["."])

    def test_duplicate_resolved_is_error(self):
        text = (
            "package\tp\n"
            "version\t1\n"
            "declared\tfeat\n"
            "extra\tfeat\twidget\n"
            "resolved\tnone\n"
            "resolved\twidget\n"
        )
        with self.assertRaises(ValueError) as err:
            MOD.load_document(text, source="dupres")
        self.assertIn("duplicate resolved", str(err.exception))
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "dup.rec"
            path.write_text(text, encoding="utf-8")
            other = Path(tmp) / "ok.rec"
            other.write_text(
                rec(
                    ("package", "p"),
                    ("version", "1"),
                    ("declared", "feat"),
                    ("extra", "feat\twidget"),
                    ("resolved", "widget"),
                ),
                encoding="utf-8",
            )
            proc = run_cli([str(path), str(other)])
        self.assertEqual(proc.returncode, 1)
        self.assertEqual(proc.stdout, "")
        self.assertIn("duplicate resolved", proc.stderr)

    def test_forgotten_resolved_is_error(self):
        text = (
            "package\tsqlalchemy\n"
            "version\t2.1.0b1.dev0\n"
            "declared\tpostgresql\n"
            "extra\tpostgresql\tpsycopg2\n"
        )
        with self.assertRaises(ValueError) as err:
            MOD.load_document(text, source="nores")
        self.assertIn("missing resolved", str(err.exception))

    def test_huge_identity_is_capped(self):
        huge = "v" * (MOD.MAX_IDENTITY + 1)
        text = rec(
            ("package", "p"),
            ("version", huge),
            ("declared", "feat"),
            ("extra", "feat\twidget"),
            ("resolved", "."),
        )
        with self.assertRaises(ValueError) as err:
            MOD.load_document(text, source="huge")
        self.assertIn("exceeds", str(err.exception))

    def test_json_stdin_matches_owned_pair(self):
        proc = run_cli(
            ["-", str(FIX / "021-add.json")],
            stdin=(FIX / "021-edit.json").read_text(encoding="utf-8"),
        )
        self.assertEqual(proc.returncode, 1, proc.stderr)
        rows = rows_of(proc.stdout)
        self.assertEqual(rows["missed_a"], ["postgresql"])
        self.assertEqual(rows["attached_b"], ["psycopg2"])
        self.assertEqual(rows["same_package"], ["yes"])


if __name__ == "__main__":
    unittest.main()
