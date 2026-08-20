from __future__ import annotations

import argparse
import sys
from pathlib import Path
from typing import Iterator, Optional, TextIO

from .diffio import (
    LINE_ONLY_RE,
    Locator,
    PrefixedStream,
    bind_seed_spec,
    git_diff,
    git_repo_root,
    parse_colon_target,
    parse_grep_lines,
    parse_locator_line,
    parse_unified_diff,
    pin_text,
    recover_file_from_pins,
    SourceBag,
)
from .model import Locus, Query
from .query import query_file
from .render import render
from .rhyme import Hit
from .scan import (
    filter_loci,
    is_noise,
    scan_file,
    scan_paths,
)


def _looks_like_diff(text: str) -> bool:
    return (
        text.startswith("diff --git ")
        or text.startswith("--- ")
        or text.startswith("+++ ")
        or "\n@@ " in text[:4000]
        or text.startswith("@@ ")
    )


def _mode(args: argparse.Namespace, *, from_stream: bool, n: Optional[int] = None) -> str:
    if args.json:
        return "json"
    if args.group:
        return "group"
    if args.explain:
        return "explain"
    if args.tsv:
        return "tsv"
    if from_stream:
        return "tsv"
    if sys.stdout.isatty() and n is not None and n <= 8:
        return "explain"
    return "tsv"


class AmbiguousSeed(Exception):
    """Locators named more than one path-condition stack."""

    def __init__(self, reps: list[Locus]):
        self.reps = reps
        n = len(reps)
        shown: list[str] = []
        for loc in reps[:8]:
            frames = loc.effective_cond_frames()
            pred = frames[-1].render() if frames else ""
            shown.append(f"  {loc.file}:{loc.line}  {pred}".rstrip())
        extra = f"\n  … {n - 8} more" if n > 8 else ""
        body = ("\n" + "\n".join(shown) + extra) if shown else ""
        super().__init__(
            "seed: locators name "
            f"{n} stacks; pass --same-as FILE:LINE or :LINE or --first"
            + body
        )


def build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(
        prog="seed",
        description=(
            "Control-flow rhyme from a content pin: locators recover a file "
            "(stripped LINE:text identity, every pin) and seed only if they "
            "name one stack. A bag of early returns is not a seed. Not a tree walk."
        ),
        epilog=(
            "Hybrid of peal(1): the seed is a content pin, not the first rg "
            "locator. Invert of chime(1) as a Unix filter. Not a snippet (ambit)."
        ),
    )
    p.add_argument(
        "target",
        nargs="?",
        help="FILE:LINE seed (optional when stdin locators carry a line)",
    )
    p.add_argument(
        "paths",
        nargs="*",
        help="FILE to scan (DIR only with --walk). Default: files named on stdin",
    )
    p.add_argument(
        "--same-as",
        metavar="FILE:LINE",
        help="seed locus (FILE:LINE, or :LINE on the recovered file)",
    )
    p.add_argument(
        "--first",
        action="store_true",
        help="seed from the first locator (peal's default); off: refuse a bag of stacks",
    )
    p.add_argument(
        "--exact",
        action="store_true",
        help="only identical stacks; drop deeper (superset) nests",
    )
    p.add_argument(
        "--any-fn",
        action="store_true",
        help="rhyme across functions (default: same function as the seed)",
    )
    p.add_argument(
        "--eval",
        dest="include_eval",
        action="store_true",
        help="include eval frames in the stack key (the if-line itself)",
    )
    p.add_argument("--all", action="store_true", help="every matching line, no span collapse")
    p.add_argument(
        "--braces",
        action="store_true",
        help="keep blank / `{` / `}` lines (default: drop them as span noise)",
    )
    p.add_argument(
        "--others",
        action="store_true",
        help="omit the seed line from the hits",
    )
    p.add_argument(
        "--hits",
        action="store_true",
        help="keep only stdin locator lines (filter), do not scan their files",
    )
    p.add_argument(
        "--walk",
        action="store_true",
        help="scan DIR operands (and cwd if none); off by default",
    )
    p.add_argument("--git", action="store_true", help="filter git diff of the working tree")
    p.add_argument("--diff", metavar="PATCH", help="filter a unified diff file ('-' = stdin)")
    p.add_argument("--json", action="store_true", help="NDJSON")
    p.add_argument("--tsv", action="store_true", help="force TSV even on a tty")
    p.add_argument("--explain", action="store_true", help="multi-line human output")
    p.add_argument("--group", action="store_true", help="cluster by same vs deeper")
    p.add_argument("--repo", default=None, help="repo root (default: cwd / git toplevel)")
    p.add_argument("--old", default="HEAD", help="revision for deleted diff lines")
    p.add_argument("-q", "--quiet", action="store_true", help="no output; only exit status")
    return p


def _want_stdin(args: argparse.Namespace, stdin: Optional[TextIO]) -> bool:
    if stdin is not None:
        return True
    if args.diff == "-":
        return True
    try:
        return not sys.stdin.isatty()
    except Exception:
        return False


def _split_target(args: argparse.Namespace) -> tuple[Optional[str], list[Path]]:
    """FILE:LINE is a seed; a bare existing path is a scan file."""
    seed_spec = args.same_as
    paths = [Path(p) for p in args.paths]
    if not args.target:
        return seed_spec, paths
    if LINE_ONLY_RE.match(args.target) and seed_spec is None:
        return args.target, paths
    q = parse_colon_target(args.target)
    as_path = Path(args.target)
    if q is not None and (seed_spec is None):
        # FILE:LINE seed. A real file named "foo.py:12" is vanishingly rare.
        return args.target, paths
    if as_path.exists():
        return seed_spec, [as_path, *paths]
    if q is not None:
        return args.target if seed_spec is None else seed_spec, paths
    # Not a locus, not a path — keep it as a scan operand so the walker
    # (or the missing-file error) can speak.
    return seed_spec, [as_path, *paths]


def _kw(args: argparse.Namespace) -> dict:
    return dict(
        exact=args.exact,
        include_eval=args.include_eval,
        any_fn=args.any_fn,
        collapse=not args.all,
        payload=True,
        braces=args.braces,
    )


def _query_seed(spec: str, default_file: Optional[str] = None) -> Locus:
    bound = bind_seed_spec(spec, default_file)
    q = parse_colon_target(bound)
    if q is None:
        if LINE_ONLY_RE.match(spec):
            raise SystemExit(
                "seed: :LINE needs a recovered file, a FILE operand, or --same-as FILE:LINE"
            )
        raise SystemExit(f"seed: expected FILE:LINE, got {spec!r}")
    loc = query_file(q.file, q.line)
    if loc.error:
        raise SystemExit(f"seed: {q.file}:{q.line}: {loc.error}")
    return loc


def _stack_key(loc: Locus, *, include_eval: bool, any_fn: bool) -> tuple:
    key = loc.cond_key(include_eval=include_eval)
    if any_fn:
        return ("", key)
    return (loc.fn_ident(), key)


def _seed_from_locators(
    locators: list[Locator],
    *,
    include_eval: bool,
    bag: SourceBag,
    first: bool = False,
    any_fn: bool = False,
) -> Optional[Locus]:
    """Content pin of a unique path-condition, not the first rg locator.

    Skip noise / eval-only. `--first` restores peal's first-locator seed.
    """
    pairs: list[tuple[Locator, Locus]] = []
    for loc in locators:
        if loc.line is None or not loc.file:
            continue
        q = bag.resolve_query(Query(file=loc.file, line=loc.line, here=loc.here or None))
        if q.error:
            continue
        if not q.cond_key(include_eval=include_eval):
            continue
        if is_noise(q):
            continue
        pairs.append((loc, q))
    if not pairs:
        return None
    if first:
        return pairs[0][1]
    groups: dict[tuple, list[tuple[Locator, Locus]]] = {}
    order: list[tuple] = []
    for loc, q in pairs:
        key = _stack_key(q, include_eval=include_eval, any_fn=any_fn)
        if key not in groups:
            order.append(key)
            groups[key] = []
        groups[key].append((loc, q))
    if len(groups) > 1:
        reps: list[Locus] = []
        for key in order:
            members = sorted(groups[key], key=lambda p: (p[1].file, p[1].line))
            reps.append(members[0][1])
        raise AmbiguousSeed(reps)
    members = groups[order[0]]
    identity = [
        q
        for loc, q in members
        if pin_text(loc.here) and pin_text(loc.here) == pin_text(q.here)
    ]
    if identity:
        identity.sort(key=lambda q: (q.file, q.line))
        return identity[0]
    members_q = sorted((q for _, q in members), key=lambda q: (q.file, q.line))
    return members_q[0]


def _finish(hits: list[Hit], args: argparse.Namespace, *, from_stream: bool) -> int:
    if args.others:
        hits = [h for h in hits if not h.seed]
    if args.quiet:
        return 0 if hits else 1
    mode = _mode(args, from_stream=from_stream, n=len(hits))
    text = render(hits, mode=mode)
    if text:
        sys.stdout.write(text)
        if not text.endswith("\n"):
            sys.stdout.write("\n")
    return 0 if hits else 1


def _scan_named(
    files: Iterator[Path],
    seed,
    args: argparse.Namespace,
    *,
    from_stream: bool,
) -> int:
    kw = _kw(args)
    hits: list[Hit] = []
    any_file = False
    for fp in files:
        any_file = True
        hits.extend(scan_file(fp, seed, **kw))
    if not any_file:
        print("seed: no files to scan", file=sys.stderr)
        return 2
    return _finish(hits, args, from_stream=from_stream)


def _file_key(p: Path) -> str:
    try:
        if p.exists():
            return str(p.resolve())
    except OSError:
        pass
    return str(p)


def _unique_files(
    locators,
    file_targets: list[Path],
    repo: Optional[Path],
) -> list[Path]:
    """Files stdin named. Bare LINE:text recovers a unique git-listed file."""
    files: list[Path] = []
    seen: set[str] = set()
    bare = []
    for loc in locators:
        if loc.file:
            p = Path(loc.file)
            key = _file_key(p)
            if key in seen:
                continue
            seen.add(key)
            files.append(p)
        elif loc.line is not None:
            bare.append(loc)
    if files:
        return files
    if not bare:
        return []
    recovered = recover_file_from_pins(bare, extra_files=file_targets, repo=repo)
    if recovered is None:
        return []
    rec = str(recovered)
    for loc in locators:
        if not loc.file:
            loc.file = rec
    return [recovered]


def main(argv: Optional[list[str]] = None, stdin: Optional[TextIO] = None) -> int:
    args = build_parser().parse_args(argv)
    try:
        seed_spec, paths = _split_target(args)
    except SystemExit as e:
        if e.code and isinstance(e.code, str):
            print(e.code, file=sys.stderr)
            return 2
        raise

    repo = Path(args.repo).resolve() if args.repo else (git_repo_root() or Path.cwd())
    bag = SourceBag(repo=repo)
    file_targets = [p for p in paths if p.is_file()]
    dir_targets = [p for p in paths if p.is_dir()]
    default_file = str(file_targets[0]) if len(file_targets) == 1 else None
    if default_file is None and seed_spec:
        q = parse_colon_target(seed_spec)
        if q is not None:
            default_file = q.file

    want_stdin = _want_stdin(args, stdin)
    src: Optional[TextIO] = None
    if want_stdin:
        src = stdin if stdin is not None else sys.stdin

    try:
        return _dispatch(
            args,
            seed_spec,
            paths,
            file_targets,
            dir_targets,
            default_file,
            bag,
            src,
        )
    except BrokenPipeError:
        return 0
    except SystemExit as e:
        if e.code and isinstance(e.code, str):
            print(e.code, file=sys.stderr)
            return 2
        raise


def _dispatch(
    args: argparse.Namespace,
    seed_spec: Optional[str],
    paths: list[Path],
    file_targets: list[Path],
    dir_targets: list[Path],
    default_file: Optional[str],
    bag: SourceBag,
    src: Optional[TextIO],
) -> int:
    prefixed: Optional[PrefixedStream] = None
    if src is not None:
        prefixed = PrefixedStream(src)
        if args.diff or args.git or _looks_like_diff(prefixed.head):
            return _run_diff(args, seed_spec, bag, prefixed)
        return _run_stream(
            args, seed_spec, file_targets, dir_targets, default_file, bag, prefixed
        )
    return _run_args_only(args, seed_spec, paths, file_targets, dir_targets)


def _require_seed(
    seed_spec: Optional[str],
    locators,
    args,
    bag,
    default_file: Optional[str] = None,
) -> Locus:
    if seed_spec:
        return _query_seed(seed_spec, default_file=default_file)
    try:
        seed = _seed_from_locators(
            locators,
            include_eval=args.include_eval,
            bag=bag,
            first=args.first,
            any_fn=args.any_fn,
        )
    except AmbiguousSeed as e:
        raise SystemExit(str(e))
    if seed is not None:
        return seed
    raise SystemExit(
        "seed: name a locus (FILE:LINE, --same-as, or rg -n locators with a path-condition)"
    )


def _run_diff(
    args: argparse.Namespace,
    seed_spec: Optional[str],
    bag: SourceBag,
    prefixed: PrefixedStream,
) -> int:
    if args.diff and args.diff != "-":
        text = Path(args.diff).read_text(encoding="utf-8", errors="replace")
    elif args.git:
        repo = Path(args.repo).resolve() if args.repo else (git_repo_root() or Path.cwd())
        if git_repo_root(repo) is None:
            print("seed: not a git repository", file=sys.stderr)
            return 3
        text = git_diff(repo, [])
    else:
        text = prefixed.remainder_text()
    loci = [bag.resolve_hit(hit, old_rev=args.old) for hit in parse_unified_diff(text)]
    # A diff is locators. Seed still has to be named.
    if not seed_spec:
        print(
            "seed: --diff needs a seed locus (FILE:LINE or --same-as)",
            file=sys.stderr,
        )
        return 2
    seed = _query_seed(seed_spec)
    if not seed.cond_key(include_eval=args.include_eval):
        print(
            f"seed: {seed.file}:{seed.line}: no path-condition "
            "(top-level / function preamble)",
            file=sys.stderr,
        )
        return 1
    hits = filter_loci(loci, seed, **_kw(args))
    return _finish(hits, args, from_stream=True)


def _bound_file(
    default_file: Optional[str],
    files: list[Path],
    file_targets: Optional[list[Path]] = None,
) -> Optional[str]:
    if default_file:
        return default_file
    if len(files) == 1:
        return str(files[0])
    extras = file_targets or []
    if len(extras) == 1:
        return str(extras[0])
    return None


def _run_stream(
    args: argparse.Namespace,
    seed_spec: Optional[str],
    file_targets: list[Path],
    dir_targets: list[Path],
    default_file: Optional[str],
    bag: SourceBag,
    prefixed: PrefixedStream,
) -> int:
    lines = list(prefixed.lines())
    locators = [parse_locator_line(raw, default_file=default_file) for raw in lines]
    locators = [p for p in locators if p is not None]
    nonempty = any(raw.strip() for raw in lines)
    if not locators:
        if nonempty:
            print(
                "seed: stdin is not a diff or file:line stream "
                "(pass FILE:LINE, or rg -nH / rg -l)",
                file=sys.stderr,
            )
            return 2
        return _run_args_only(args, seed_spec, file_targets + dir_targets, file_targets, dir_targets)

    files = _unique_files(locators, file_targets, repo=bag.repo)
    if not files and default_file:
        files = [Path(default_file)]
        for loc in locators:
            if not loc.file:
                loc.file = default_file

    if not files:
        print(
            "seed: LINE:text locators need a FILE operand, rg -nH, or a unique "
            "match in this git tree (cd to the repo rg searched, or --repo)",
            file=sys.stderr,
        )
        return 2

    bound = _bound_file(default_file, files, file_targets)
    seed = _require_seed(seed_spec, locators, args, bag, default_file=bound)
    if not seed.cond_key(include_eval=args.include_eval):
        print(
            f"seed: {seed.file}:{seed.line}: no path-condition "
            "(top-level / function preamble)",
            file=sys.stderr,
        )
        return 1

    if args.hits:
        bound = default_file or (str(files[0]) if len(files) == 1 else None)
        queries = parse_grep_lines("".join(lines), default_file=bound)
        queries = [q for q in queries if q.file]
        if not queries:
            print(
                "seed: --hits needs line locators (rg -n), not a file list",
                file=sys.stderr,
            )
            return 2
        loci = [bag.resolve_query(q) for q in queries]
        hits = filter_loci(loci, seed, **_kw(args))
        return _finish(hits, args, from_stream=True)

    if dir_targets and not args.walk:
        print(
            f"seed: will not walk {dir_targets[0]} (pipe rg locators, pass FILE, or --walk)",
            file=sys.stderr,
        )
        return 2

    return _scan_named(iter(files), seed, args, from_stream=True)


def _run_args_only(
    args: argparse.Namespace,
    seed_spec: Optional[str],
    paths: list[Path],
    file_targets: list[Path],
    dir_targets: list[Path],
) -> int:
    if not seed_spec:
        print(
            "seed: name a locus (FILE:LINE, --same-as, or pipe rg locators). No cwd walk.",
            file=sys.stderr,
        )
        return 2
    bound = _bound_file(None, [], file_targets)
    seed = _query_seed(seed_spec, default_file=bound)
    if not seed.cond_key(include_eval=args.include_eval):
        print(
            f"seed: {seed.file}:{seed.line}: no path-condition "
            "(top-level / function preamble)",
            file=sys.stderr,
        )
        return 1
    if dir_targets and not args.walk:
        shown = dir_targets[0]
        print(
            f"seed: will not walk {shown} (pipe rg locators, pass FILE, or --walk)",
            file=sys.stderr,
        )
        return 2
    if file_targets and not args.walk:
        return _scan_named(iter(file_targets), seed, args, from_stream=False)
    if args.walk:
        roots = paths or [Path.cwd()]
        hits = scan_paths(roots, seed, **_kw(args))
        return _finish(hits, args, from_stream=False)
    # Seed names its own file — scan that file only, not the tree around it.
    seed_path = Path(seed.file)
    if seed_path.is_file() or seed_path.exists():
        return _scan_named(iter([seed_path]), seed, args, from_stream=False)
    print(
        "seed: name files on argv or pipe locators (rg -nH / rg -l). No cwd walk.",
        file=sys.stderr,
    )
    return 2


if __name__ == "__main__":
    sys.exit(main())
