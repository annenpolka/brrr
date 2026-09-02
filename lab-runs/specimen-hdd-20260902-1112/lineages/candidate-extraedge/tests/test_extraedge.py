#!/usr/bin/env python3
"""declared extra missing its mapped extra-edge on a reused package node."""

from __future__ import annotations

import importlib.machinery
import importlib.util
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CLI = ROOT / "extraedge"
FIX = ROOT / "fixtures"


def load_mod():
    loader = importlib.machinery.SourceFileLoader("extraedge_cli", str(CLI))
    spec = importlib.util.spec_from_loader(loader.name, loader)
    assert spec is not None
    mod = importlib.util.module_from_spec(spec)
    loader.exec_module(mod)
    return mod


EE = load_mod()


def parse_rows(text: str) -> dict[str, list[str]]:
    rows: dict[str, list[str]] = {}
    for line in text.splitlines():
        if not line or "\t" not in line:
            continue
        name, *rest = line.split("\t")
        rows[name] = rest
    return rows


def rec(*rows: tuple[str, str]) -> str:
    return "".join(f"{key}\t{value}\n" for key, value in rows)


def write_pair(dir_path: Path, a: str, b: str) -> tuple[Path, Path]:
    first = dir_path / "a.rec"
    second = dir_path / "b.rec"
    first.write_text(a, encoding="utf-8")
    second.write_text(b, encoding="utf-8")
    return first, second


def run_cli(args: list[str], stdin: str | None = None) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [sys.executable, str(CLI), *args],
        input=stdin,
        capture_output=True,
        text=True,
        check=False,
    )


class Specimen021Tests(unittest.TestCase):
    def test_edit_lock_misses_declared_extra(self):
        a = EE.parse_record((FIX / "021-edit.rec").read_text(), source="edit")
        b = EE.parse_record((FIX / "021-add.rec").read_text(), source="add")
        result = EE.inspect(a, b)
        self.assertTrue(result["same_package"])
        self.assertEqual(result["missed_first"], ["postgresql"])
        self.assertEqual(result["missed_second"], [])
        self.assertEqual(result["attached_only_second"], ["psycopg2"])
        self.assertEqual(result["extras"]["postgresql"], ["psycopg2"])

    def test_cli_owned_pair(self):
        proc = run_cli([str(FIX / "021-edit.rec"), str(FIX / "021-add.rec")])
        self.assertEqual(proc.returncode, 1, proc.stderr)
        rows = parse_rows(proc.stdout)
        self.assertEqual(rows["same_package"], ["yes"])
        self.assertEqual(rows["package_a"], ["sqlalchemy"])
        self.assertEqual(rows["package_b"], ["sqlalchemy"])
        self.assertEqual(rows["map"], ["postgresql", "psycopg2"])
        self.assertEqual(rows["missed_a"], ["postgresql"])
        self.assertEqual(rows["missed_b"], ["."])
        self.assertEqual(rows["attached_b"], ["psycopg2"])
        self.assertEqual(rows["resolved_a"], ["."])

    def test_unseen_partial_attach(self):
        proc = run_cli([str(FIX / "unseen-edit.rec"), str(FIX / "unseen-add.rec")])
        self.assertEqual(proc.returncode, 1, proc.stderr)
        rows = parse_rows(proc.stdout)
        self.assertEqual(rows["missed_a"], ["feat"])
        self.assertEqual(rows["missed_b"], ["."])
        self.assertEqual(rows["attached_b"], ["widget"])

    def test_missing_package_errors(self):
        proc = run_cli([str(FIX / "021-edit.rec"), "/dev/null"])
        self.assertEqual(proc.returncode, 1)
        self.assertEqual(proc.stdout, "")


class MappingTests(unittest.TestCase):
    def test_add_lock_as_first_is_not_a_miss(self):
        proc = run_cli([str(FIX / "021-add.rec"), str(FIX / "021-add.rec")])
        self.assertEqual(proc.returncode, 0, proc.stderr)
        rows = parse_rows(proc.stdout)
        self.assertEqual(rows["missed_a"], ["."])
        self.assertEqual(rows["missed_b"], ["."])
        self.assertEqual(rows["attached_b"], ["."])
        self.assertEqual(rows["resolved_a"], ["psycopg2"])
        self.assertEqual(rows["map"], ["postgresql", "psycopg2"])

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
        rows = parse_rows(proc.stdout)
        self.assertEqual(rows["resolved_a"], ["typing-extensions"])
        self.assertEqual(rows["missed_a"], ["postgresql"])
        self.assertEqual(rows["missed_b"], ["."])
        self.assertEqual(rows["attached_b"], ["psycopg2"])

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
        rows = parse_rows(proc.stdout)
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
        rows = parse_rows(proc.stdout)
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
        rows = parse_rows(proc.stdout)
        self.assertEqual(rows["unmapped"], ["postgresql"])
        self.assertEqual(rows["missed_a"], ["."])
        self.assertEqual(rows["attached_b"], ["."])


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
        rows = parse_rows(proc.stdout)
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
            EE.parse_record(text, source="dup")
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
            EE.parse_record(text, source="cols")
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
        rows = parse_rows(proc.stdout)
        self.assertEqual(rows["declared"], ["none"])
        self.assertEqual(rows["missed_a"], ["none"])
        self.assertEqual(rows["resolved_a"], ["."])
        self.assertEqual(rows["attached_b"], ["nonepkg"])

    def test_declared_space_is_one_name_tab_is_two(self):
        space = EE.parse_record(
            rec(
                ("package", "p"),
                ("version", "1"),
                ("declared", "my extra"),
                ("extra", "my extra\tdep"),
                ("resolved", "."),
            ),
            source="space",
        )
        self.assertEqual(space.declared, ["my extra"])
        tab = EE.parse_record(
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
        self.assertEqual(tab.declared, ["my", "extra"])

    def test_empty_declared_tab_is_empty_list(self):
        record = EE.parse_record(
            "package\tp\nversion\t1\ndeclared\t\nextra\tfeat\twidget\nresolved\t.\n",
            source="emptydecl",
        )
        self.assertEqual(record.declared, [])

    def test_dash_is_stdin(self):
        proc = run_cli(
            ["-", str(FIX / "021-add.rec")],
            stdin=(FIX / "021-edit.rec").read_text(encoding="utf-8"),
        )
        self.assertEqual(proc.returncode, 1, proc.stderr)
        rows = parse_rows(proc.stdout)
        self.assertEqual(rows["missed_a"], ["postgresql"])
        self.assertEqual(rows["attached_b"], ["psycopg2"])

    def test_swapped_021_misses_on_second(self):
        proc = run_cli([str(FIX / "021-add.rec"), str(FIX / "021-edit.rec")])
        self.assertEqual(proc.returncode, 1, proc.stderr)
        rows = parse_rows(proc.stdout)
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
        rows = parse_rows(proc.stdout)
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
            EE.parse_record(text, source="dupres")
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
            EE.parse_record(text, source="nores")
        self.assertIn("missing resolved", str(err.exception))

    def test_huge_identity_is_capped(self):
        huge = "v" * (EE.MAX_IDENTITY + 1)
        text = rec(
            ("package", "p"),
            ("version", huge),
            ("declared", "feat"),
            ("extra", "feat\twidget"),
            ("resolved", "."),
        )
        with self.assertRaises(ValueError) as err:
            EE.parse_record(text, source="huge")
        self.assertIn("exceeds", str(err.exception))


if __name__ == "__main__":
    unittest.main()
