from __future__ import annotations

import argparse
import sys
from pathlib import Path

from nigh import __version__
from nigh.extract import Corpus, extract_roots
from nigh.report import format_human, format_json, format_summary, format_tsv
from nigh.score import ACTIONABLE, classify_corpus, probe_value


HELP = """nigh — how close does this repo's own vocabulary come to each branch cut?

A gate is a comparison against a literal (kind == \"beam\", retries > 3).
A producer is a literal that constructs a value rather than testing it.

Classifications:
  CLOSED     the compared-to value is never constructed in-repo
  NIGH       no exact producer, but a near-miss (typo, case, inflection, affix)
  BRINK      a corpus number sits on an inequality cut (--brink)
  ONE-SIDED  corpus values only ever take one side of the cut (--one-sided)
  BALANCED   both sides exist (hidden unless --all)

Default report is CLOSED and NIGH — the distance field. Other statuses are opt-in.

Examples:
  nigh src tests
  nigh --nigh --closed path/
  nigh --probe beam path/
  printf 'beam\\nSuccess\\n' | nigh --probe path/
  nigh --format tsv path/ | cut -f1,2,3,6
"""


def build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(
        prog="nigh",
        description=HELP,
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    p.add_argument("paths", nargs="*", default=["."], help="files or directories (default: .)")
    p.add_argument("--format", choices=("human", "tsv", "json"), default="human")
    p.add_argument("--all", action="store_true", help="include BALANCED gates")
    p.add_argument("--closed", action="store_true", help="only CLOSED")
    p.add_argument("--nigh", action="store_true", dest="only_nigh", help="only NIGH")
    p.add_argument("--brink", action="store_true", help="only BRINK")
    p.add_argument("--one-sided", action="store_true", help="only ONE-SIDED")
    p.add_argument(
        "--probe",
        nargs="?",
        const="-",
        metavar="VALUE",
        help="sieve VALUE (or stdin lines) through gates; '-' reads stdin",
    )
    p.add_argument("--lhs", metavar="NAME", help="restrict gates to this lhs/field")
    p.add_argument("--report-only", action="store_true", help="always exit 0 after a report")
    p.add_argument("--quiet", action="store_true", help="no summary on stderr")
    p.add_argument("--version", action="version", version=f"nigh {__version__}")
    return p


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    paths = [Path(p) for p in args.paths]
    missing = [p for p in paths if not p.exists()]
    if missing:
        print(f"nigh: not found: {', '.join(str(p) for p in missing)}", file=sys.stderr)
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

    text = _render(
        args.format,
        findings,
        corpus,
        all_status=args.all or bool(args.probe) or bool(wanted),
    )
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
    if args.closed:
        wanted.add("CLOSED")
    if args.only_nigh:
        wanted.add("NIGH")
    if args.brink:
        wanted.add("BRINK")
    if args.one_sided:
        wanted.add("ONE-SIDED")
    return wanted or None


def _probe_values(probe: str) -> list[str] | None:
    if probe == "-":
        if sys.stdin.isatty():
            print("nigh: --probe - expects values on stdin", file=sys.stderr)
            return None
        return [line.strip() for line in sys.stdin if line.strip()]
    return [probe]


def _render(fmt: str, findings, corpus, *, all_status: bool) -> str:
    if fmt == "tsv":
        return format_tsv(findings, all_status=all_status)
    if fmt == "json":
        return format_json(findings, corpus, all_status=all_status)
    return format_human(findings, corpus, all_status=all_status)
