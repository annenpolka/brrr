from __future__ import annotations

import argparse
import sys
from pathlib import Path

from cusp import __version__
from cusp.extract import Corpus, extract_roots
from cusp.report import format_human, format_json, format_summary, format_tsv
from cusp.score import ACTIONABLE, classify_corpus, probe_value


HELP = """cusp — which constructed values sit on a numeric or enum cut?

A gate is a comparison against a literal bound (retries > 3, phase == "done",
status != "unknown", code in 200..<300). A producer is a literal that
constructs a value rather than testing it.

cusp reports only the brink: values that sit on the cut.

  BRINK     exclusive/inclusive numeric bound (n > 3 with 3; n >= 4 with 4)
  OFFBY     numeric equality one step away on the same field (401 vs 400)
  SENTINEL  0 / -1 / "unknown" / "none" sitting on the excluded or domain edge
  NEIGHBOR  constructed enum variant adjacent to the compared-to set

String-edit near-misses (typo / case / inflection) are out of scope.

Examples:
  cusp src tests
  cusp --offby --brink path/
  cusp --probe 3 path/
  cusp --probe unknown path/
  cusp --format tsv path/ | cut -f1,2,3,6,10
"""


def build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(
        prog="cusp",
        description=HELP,
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    p.add_argument("paths", nargs="*", default=["."], help="files or directories (default: .)")
    p.add_argument("--format", choices=("human", "tsv", "json"), default="human")
    p.add_argument("--brink", action="store_true", help="only BRINK")
    p.add_argument("--offby", action="store_true", help="only OFFBY")
    p.add_argument("--sentinel", action="store_true", help="only SENTINEL")
    p.add_argument("--neighbor", action="store_true", help="only NEIGHBOR")
    p.add_argument(
        "--probe",
        nargs="?",
        const="-",
        metavar="VALUE",
        help="which cuts does VALUE sit on? '-' reads stdin",
    )
    p.add_argument("--lhs", metavar="NAME", help="restrict gates to this lhs/field")
    p.add_argument("--report-only", action="store_true", help="always exit 0 after a report")
    p.add_argument("--quiet", action="store_true", help="no summary on stderr")
    p.add_argument("--version", action="version", version=f"cusp {__version__}")
    return p


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    paths = [Path(p) for p in args.paths]
    missing = [p for p in paths if not p.exists()]
    if missing:
        print(f"cusp: not found: {', '.join(str(p) for p in missing)}", file=sys.stderr)
        return 2

    try:
        corpus = extract_roots(paths)
    except KeyboardInterrupt:
        return 130

    if args.lhs:
        needle = args.lhs.lower()
        corpus = Corpus(
            producers=corpus.producers,
            gates=[
                g
                for g in corpus.gates
                if needle in g.lhs.lower() or needle == g.field.lower()
            ],
            enums=corpus.enums,
            files=corpus.files,
            skipped=corpus.skipped,
        )

    if args.probe is not None:
        values = _probe_values(args.probe)
        if values is None:
            return 2
        findings = []
        for value in values:
            findings.extend(probe_value(value, corpus))
    else:
        findings = classify_corpus(corpus)

    wanted = _wanted_status(args)
    if wanted:
        findings = [f for f in findings if f.status in wanted]

    text = _render(args.format, findings, corpus)
    if text:
        sys.stdout.write(text)
        if args.format == "human" and not text.endswith("\n"):
            sys.stdout.write("\n")

    if not args.quiet:
        print(format_summary(findings, corpus), file=sys.stderr)

    if args.report_only:
        return 0
    if any(f.status in ACTIONABLE for f in findings):
        return 1
    return 0


def _wanted_status(args) -> set[str] | None:
    wanted: set[str] = set()
    if args.brink:
        wanted.add("BRINK")
    if args.offby:
        wanted.add("OFFBY")
    if args.sentinel:
        wanted.add("SENTINEL")
    if args.neighbor:
        wanted.add("NEIGHBOR")
    return wanted or None


def _probe_values(probe: str) -> list[str] | None:
    if probe == "-":
        if sys.stdin.isatty():
            print("cusp: --probe - expects values on stdin", file=sys.stderr)
            return None
        return [line.strip() for line in sys.stdin if line.strip()]
    return [probe]


def _render(fmt: str, findings, corpus) -> str:
    if fmt == "tsv":
        return format_tsv(findings, all_status=True)
    if fmt == "json":
        return format_json(findings, corpus, all_status=True)
    return format_human(findings, corpus, all_status=True)
