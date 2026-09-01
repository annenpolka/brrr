#!/usr/bin/env python3
"""Drive the shipped hits CLI. Empty is success; bad query and I/O are not."""

import os
import stat
import subprocess
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
HITS = ROOT / "hits"
HAS = ROOT / "fixtures" / "has"
MISS = ROOT / "fixtures" / "miss"
REGEX = ROOT / "fixtures" / "regex"
MIXED = ROOT / "fixtures" / "mixed"


def run(*args, cwd=None):
    return subprocess.run(
        [str(HITS), *args],
        cwd=cwd,
        capture_output=True,
        text=True,
    )


class HitsCLITest(unittest.TestCase):
    def test_executable(self):
        self.assertTrue(HITS.is_file())
        self.assertTrue(os.access(HITS, os.X_OK))

    def test_hit_prints_file_line_text_and_exits_0(self):
        r = run("needle", str(HAS))
        self.assertEqual(r.returncode, 0, r.stderr)
        lines = [ln for ln in r.stdout.splitlines() if ln]
        self.assertEqual(len(lines), 2)
        self.assertIn("hello.txt:1:hello needle world", lines[0])
        self.assertIn("more.txt:1:another needle here", lines[1])
        self.assertNotIn("0 matches", r.stdout)

    def test_miss_prints_zero_matches_and_exits_0(self):
        r = run("needle", str(MISS))
        self.assertEqual(r.returncode, 0, r.stderr)
        self.assertEqual(r.stdout, "0 matches\n")

    def test_miss_is_success_in_shell_and(self):
        """The primitive: hits PAT && next still runs after a legitimate miss."""
        r = subprocess.run(
            f'"{HITS}" needle "{MISS}" && echo still-running',
            shell=True,
            capture_output=True,
            text=True,
        )
        self.assertEqual(r.returncode, 0, r.stderr)
        self.assertIn("0 matches", r.stdout)
        self.assertIn("still-running", r.stdout)

    def test_literal_is_not_regex(self):
        r = run("n.edle", str(REGEX))
        self.assertEqual(r.returncode, 0, r.stderr)
        self.assertEqual(r.stdout, "0 matches\n")

    def test_regex_match(self):
        r = run("--regex", "n.edle", str(REGEX))
        self.assertEqual(r.returncode, 0, r.stderr)
        self.assertIn("sample.txt:1:needle", r.stdout)
        self.assertNotIn("nXXdle", r.stdout)

    def test_bad_regex_exits_2(self):
        r = run("--regex", "[", str(HAS))
        self.assertEqual(r.returncode, 2)
        self.assertIn("bad regex", r.stderr)
        self.assertEqual(r.stdout, "")

    def test_usage_missing_pattern_exits_1(self):
        r = run()
        self.assertEqual(r.returncode, 1)
        self.assertIn("usage:", r.stderr)

    def test_usage_unknown_option_exits_1(self):
        r = run("--nope", "needle", str(HAS))
        self.assertEqual(r.returncode, 1)
        self.assertIn("unknown option", r.stderr)

    def test_missing_dir_exits_3(self):
        r = run("needle", str(ROOT / "fixtures" / "no-such-dir"))
        self.assertEqual(r.returncode, 3)
        self.assertIn("unreadable directory", r.stderr)

    def test_file_as_dir_exits_3(self):
        r = run("needle", str(HAS / "hello.txt"))
        self.assertEqual(r.returncode, 3)
        self.assertIn("unreadable directory", r.stderr)

    def test_unreadable_dir_exits_3(self):
        tmp = tempfile.mkdtemp(prefix="hits-unreadable-")
        try:
            os.chmod(tmp, 0)
            r = run("needle", tmp)
            self.assertEqual(r.returncode, 3)
            self.assertIn("unreadable directory", r.stderr)
        finally:
            os.chmod(tmp, stat.S_IRWXU)
            os.rmdir(tmp)

    def test_skips_dot_git(self):
        tmp = tempfile.mkdtemp(prefix="hits-git-")
        try:
            root = Path(tmp)
            (root / "visible.txt").write_text("nope\n", encoding="utf-8")
            git = root / ".git"
            git.mkdir()
            (git / "config").write_text("needle hidden in git\n", encoding="utf-8")
            r = run("needle", str(root))
            self.assertEqual(r.returncode, 0, r.stderr)
            self.assertEqual(r.stdout, "0 matches\n")
        finally:
            (Path(tmp) / ".git" / "config").unlink()
            (Path(tmp) / ".git").rmdir()
            (Path(tmp) / "visible.txt").unlink()
            os.rmdir(tmp)

    def test_default_dir_is_cwd(self):
        r = run("needle", cwd=str(HAS))
        self.assertEqual(r.returncode, 0, r.stderr)
        self.assertIn("hello.txt:1:hello needle world", r.stdout)
        self.assertIn("more.txt:1:another needle here", r.stdout)

    def test_skips_binary_but_keeps_text(self):
        r = run("needle", str(MIXED))
        self.assertEqual(r.returncode, 0, r.stderr)
        self.assertIn("note.txt:1:text needle in notes", r.stdout)
        self.assertNotIn("blob.bin", r.stdout)
        self.assertNotIn("0 matches", r.stdout)

    def test_binary_only_tree_is_empty_success(self):
        tmp = tempfile.mkdtemp(prefix="hits-bin-")
        try:
            blob = Path(tmp) / "only.bin"
            blob.write_bytes(b"\x00needle\x00")
            r = run("needle", tmp)
            self.assertEqual(r.returncode, 0, r.stderr)
            self.assertEqual(r.stdout, "0 matches\n")
        finally:
            blob.unlink()
            os.rmdir(tmp)

    def test_glob_limits_paths(self):
        r = run("--glob", "*.txt", "needle", str(MIXED))
        self.assertEqual(r.returncode, 0, r.stderr)
        self.assertIn("note.txt:1:text needle in notes", r.stdout)
        self.assertNotIn("blob.bin", r.stdout)

    def test_glob_miss_is_empty_success(self):
        r = run("--glob", "*.md", "needle", str(MIXED))
        self.assertEqual(r.returncode, 0, r.stderr)
        self.assertEqual(r.stdout, "0 matches\n")

    def test_glob_requires_pattern(self):
        r = run("--glob")
        self.assertEqual(r.returncode, 1)
        self.assertIn("--glob", r.stderr)

    def test_nested_unreadable_dir_exits_3(self):
        tmp = tempfile.mkdtemp(prefix="hits-nested-eacces-")
        try:
            root = Path(tmp)
            (root / "open").mkdir()
            (root / "secret").mkdir()
            (root / "open" / "a.txt").write_text("nothing\n", encoding="utf-8")
            (root / "secret" / "hidden.txt").write_text("needle hidden\n", encoding="utf-8")
            os.chmod(root / "secret", 0)
            r = run("needle", str(root))
            self.assertEqual(r.returncode, 3)
            self.assertIn("unreadable", r.stderr)
            self.assertNotEqual(r.stdout, "0 matches\n")
        finally:
            os.chmod(Path(tmp) / "secret", stat.S_IRWXU)
            (Path(tmp) / "secret" / "hidden.txt").unlink()
            (Path(tmp) / "secret").rmdir()
            (Path(tmp) / "open" / "a.txt").unlink()
            (Path(tmp) / "open").rmdir()
            os.rmdir(tmp)


if __name__ == "__main__":
    unittest.main()
