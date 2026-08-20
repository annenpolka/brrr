from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path

from kerf import __version__
from kerf.extract import Corpus, extract_roots
from kerf.report import format_human, format_json, format_summary, format_tsv
from kerf.score import ACTIONABLE, classify_corpus, parse_probe_token, sit


HELP = """kerf — given a constructed value, emit the cuts it sits on

A gate is a comparison against a literal bound (retries > 3, phase == "done",
status != "unknown", code in 200..<300). kerf inverts the join: the value is
the query, the tree is a haystack of predicates, the rows are the cuts that
value sits on.

  HIT       the value is the compared-to (statusCode == 401 with 401)
  BRINK     exclusive/inclusive numeric bound (n > 3 with 3)
  OFFBY     equality one step away (401 vs 400)
  SENTINEL  0 / -1 / "unknown" sitting on the excluded or domain edge
  NEIGHBOR  adjacent enum variant (phase == "done" with "running")

Default: VALUE [paths], TSV on stdout, no header, no summary.
Stdin supplies values when VALUE is omitted (or VALUE is '-').
--scan is the ancestor corpus join (tree's own literals vs its cuts).

Examples:
  kerf 3 src/
  kerf 400 Engine/
  kerf statusCode=400 Engine/
  printf '3\\n401\\nunknown\\n' | kerf src/
  kerf 3 src/ | awk -F'\\t' '$2=="BRINK"'
  kerf --scan --format human src/
"""


class _Parser(argparse.ArgumentParser):
    """Keep -1 / -0.5 as VALUES, not unknown options."""

    def _parse_optional(self, arg_string):
        if arg_string is not None and re.fullmatch(r"-\d+(?:\.\d+)?", arg_string):
            return None
        return super()._parse_optional(arg_string)


def build_parser() -> argparse.ArgumentParser:
    p = _Parser(
        prog="kerf",
        description=HELP,
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    p.add_argument(
        "args",
        nargs="*",
        help="VALUE [paths...]  (or paths with --scan / stdin)",
    )
    p.add_argument(
        "--probe",
        metavar="VALUE",
        help="explicit value; '-' reads stdin (default: first positional or stdin)",
    )
    p.add_argument(
        "--scan",
        action="store_true",
        help="corpus join: which of this tree's own literals sit on its cuts",
    )
    p.add_argument("--format", choices=("tsv", "human", "json"), default="tsv")
    p.add_argument("--header", action="store_true", help="TSV header row")
    p.add_argument("--brink", action="store_true", help="only BRINK")
    p.add_argument("--offby", action="store_true", help="only OFFBY")
    p.add_argument("--sentinel", action="store_true", help="only SENTINEL")
    p.add_argument("--neighbor", action="store_true", help="only NEIGHBOR")
    p.add_argument("--hit", action="store_true", help="only HIT")
    p.add_argument("--lhs", metavar="NAME", help="restrict gates to this lhs/field")
    p.add_argument("--report-only", action="store_true", help="always exit 0 after a report")
    p.add_argument("--summary", action="store_true", help="corpus counts on stderr")
    p.add_argument("--quiet", action="store_true", help="no summary (default)")
    p.add_argument("--version", action="version", version=f"kerf {__version__}")
    return p


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    mode, values, paths, err = _resolve(args)
    if err is not None:
        print(f"kerf: {err}", file=sys.stderr)
        return 2

    missing = [p for p in paths if not p.exists()]
    if missing:
        print(f"kerf: not found: {', '.join(str(p) for p in missing)}", file=sys.stderr)
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

    wanted = _wanted_status(args)
    all_findings = []
    wrote = False

    if mode == "scan":
        findings = classify_corpus(corpus)
        if wanted:
            findings = [f for f in findings if f.status in wanted]
        all_findings = findings
        text = _render(args.format, findings, corpus, header=args.header)
        if text:
            sys.stdout.write(text)
            if args.format != "tsv" and not text.endswith("\n"):
                sys.stdout.write("\n")
            wrote = bool(text.strip())
    else:
        for token in values:
            field, value = parse_probe_token(token)
            if field is None and args.lhs:
                field = args.lhs
            findings = sit(value, corpus, field=field)
            if wanted:
                findings = [f for f in findings if f.status in wanted]
            all_findings.extend(findings)
            text = _render(args.format, findings, corpus, header=args.header and not wrote)
            if text:
                sys.stdout.write(text)
                sys.stdout.flush()
                wrote = True

    if args.summary and not args.quiet:
        print(format_summary(all_findings, corpus), file=sys.stderr)

    if args.report_only:
        return 0
    if mode == "scan":
        if any(f.status in ACTIONABLE for f in all_findings):
            return 1
        return 0
    return 0 if all_findings else 1


def _resolve(args) -> tuple[str, list[str], list[Path], str | None]:
    positionals = list(args.args)
    if args.scan:
        paths = [Path(p) for p in positionals] or [Path(".")]
        return "scan", [], paths, None

    if args.probe is not None:
        values = _probe_values(args.probe)
        if values is None:
            return "probe", [], [], "need VALUE on argv or stdin"
        paths = [Path(p) for p in positionals] or [Path(".")]
        return "probe", values, paths, None

    piped = not sys.stdin.isatty()
    if positionals:
        first_is_path = Path(positionals[0]).exists()
        if piped and first_is_path:
            values = _probe_values("-") or []
            paths = [Path(p) for p in positionals]
            return "probe", values, paths, None
        values = [positionals[0]]
        paths = [Path(p) for p in positionals[1:]] or [Path(".")]
        return "probe", values, paths, None

    if piped:
        values = _probe_values("-") or []
        return "probe", values, [Path(".")], None
    return "probe", [], [], "need VALUE, stdin, or --scan"


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
    if args.hit:
        wanted.add("HIT")
    return wanted or None


def _probe_values(probe: str) -> list[str] | None:
    if probe != "-":
        return [probe]
    raw = sys.stdin.buffer.read()
    if not raw:
        return []
    text = raw.decode("utf-8", "replace")
    return [line.strip() for line in text.splitlines() if line.strip()]


def _render(fmt: str, findings, corpus, *, header: bool) -> str:
    if fmt == "tsv":
        return format_tsv(findings, header=header)
    if fmt == "json":
        return format_json(findings, corpus)
    return format_human(findings, corpus)
