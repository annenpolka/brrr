#!/usr/bin/env python3
"""DESTROYER keel — origin is remotes + tip witnesses, not root SHAs.

Do not rewrite keel. Do not re-run leftover-stub / extract-and-keep attacks.
Empirical holes in origin-as-project.
"""
from __future__ import annotations

import base64
import json
import os
import shutil
import subprocess
import sys
import textwrap
import zlib
from dataclasses import dataclass, field
from pathlib import Path

KEEL = Path(
    "/Users/annenpolka/.grok/worktrees/annenpolka-brrr/subagent-01a01b85-3a6f-77f2-a6bf-cb0da2df3d3e/keel"
)
OUT = Path("/tmp/destroy-keel")
FIX = OUT / "fixtures"
KIZU = Path("/Users/annenpolka/ghq/github.com/annenpolka/kizu")
VOID = Path("/Users/annenpolka/ghq/github.com/annenpolka/voidtrace")
SKILLS = Path("/Users/annenpolka/ghq/github.com/annenpolka/skills")

GIT_ENV = {
    **os.environ,
    "GIT_AUTHOR_NAME": "keel-destroyer",
    "GIT_AUTHOR_EMAIL": "destroyer@example.com",
    "GIT_COMMITTER_NAME": "keel-destroyer",
    "GIT_COMMITTER_EMAIL": "destroyer@example.com",
    "GIT_TERMINAL_PROMPT": "0",
}

HELPER_BODY = textwrap.dedent(
    '''\
    def add(a, b):
        return a + b

    def helper_keep():
        return "stable helper"
    '''
)

HELPER_V2 = textwrap.dedent(
    '''\
    def add(a, b):
        return a + b

    def helper_keep():
        return "stable helper"
    # later
    '''
)

FOREIGN_HELPER = textwrap.dedent(
    '''\
    def helper_keep():
        return "stable helper"
    '''
)

ROWS: list[dict] = []
LOG: list[str] = []


def log(msg: str = "") -> None:
    print(msg, flush=True)
    LOG.append(msg)


def sh(
    args: list[str],
    *,
    cwd: Path | None = None,
    check: bool = True,
    env: dict | None = None,
) -> subprocess.CompletedProcess[str]:
    cp = subprocess.run(
        args,
        cwd=str(cwd) if cwd else None,
        text=True,
        capture_output=True,
        env=env or GIT_ENV,
    )
    if check and cp.returncode != 0:
        raise RuntimeError(
            f"cmd failed rc={cp.returncode}: {args}\nstdout={cp.stdout}\nstderr={cp.stderr}"
        )
    return cp


def git(repo: Path, args: list[str], check: bool = True) -> subprocess.CompletedProcess[str]:
    return sh(["git", "-C", str(repo), *args], check=check)


def keel(args: list[str], check: bool = False) -> subprocess.CompletedProcess[str]:
    return sh([str(KEEL), *args], check=check)


def write(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


def init_repo(path: Path, remote: str | None = None) -> Path:
    if path.exists():
        shutil.rmtree(path)
    path.mkdir(parents=True)
    git(path, ["init", "-q", "-b", "main"])
    if remote:
        git(path, ["remote", "add", "origin", remote])
    return path


def commit_file(repo: Path, rel: str, body: str, msg: str) -> str:
    write(repo / rel, body)
    git(repo, ["add", rel])
    git(repo, ["commit", "-q", "-m", msg])
    return git(repo, ["rev-parse", "HEAD"]).stdout.strip()


def forge_v1(path: str, line: int, text: str) -> str:
    payload = {"v": 1, "n": line, "p": path, "t": text}
    raw = json.dumps(payload, ensure_ascii=False, separators=(",", ":"), sort_keys=True).encode(
        "utf-8"
    )
    packed = zlib.compress(raw, 9)
    return "keel1." + base64.urlsafe_b64encode(packed).decode("ascii").rstrip("=")


def strip_origin(token: str) -> str:
    body = token[len("keel1.") :]
    pad = "=" * (-len(body) % 4)
    raw = json.loads(zlib.decompress(base64.urlsafe_b64decode(body + pad)))
    raw.pop("o", None)
    packed = zlib.compress(
        json.dumps(raw, ensure_ascii=False, separators=(",", ":"), sort_keys=True).encode("utf-8"),
        9,
    )
    return "keel1." + base64.urlsafe_b64encode(packed).decode("ascii").rstrip("=")


@dataclass
class Case:
    id: str
    title: str
    kind: str  # hole | survived | claimed | sanity
    cmd: str
    rc: int
    stdout: str
    stderr: str
    note: str = ""


CASES: list[Case] = []


def record(
    id: str,
    title: str,
    kind: str,
    cp: subprocess.CompletedProcess[str],
    note: str = "",
    cmd: str = "",
) -> Case:
    c = Case(
        id=id,
        title=title,
        kind=kind,
        cmd=cmd,
        rc=cp.returncode,
        stdout=(cp.stdout or "").strip(),
        stderr=(cp.stderr or "").strip(),
        note=note,
    )
    CASES.append(c)
    log(f"\n## {id}  [{kind}]  {title}")
    if cmd:
        log(f"$ {cmd}")
    log(f"# rc={c.rc}")
    if c.stdout:
        log(c.stdout)
    if c.stderr:
        log(c.stderr)
    if note:
        log(f"# {note}")
    return c


def resolve(repo: Path | None, token: str, extra: list[str] | None = None) -> subprocess.CompletedProcess[str]:
    args = ["resolve", "--porcelain"]
    if repo is not None:
        args += ["--repo", str(repo), "--to", "HEAD"]
    args += extra or []
    args.append(token)
    return keel(args)


def show_origin(token: str) -> str:
    cp = keel(["show", token])
    lines = [ln.strip() for ln in cp.stdout.splitlines() if "origin:" in ln or "remotes:" in ln or "witnesses:" in ln]
    return " | ".join(lines) if lines else cp.stdout.strip()


def kid(repo: Path, extra: list[str] | None = None) -> str:
    cp = keel(["id", "--repo", str(repo), *(extra or [])])
    return (cp.stdout or "").strip().splitlines()[0] if cp.returncode == 0 else f"id-fail:{cp.stderr.strip()}"


def is_shallow(repo: Path) -> bool:
    cp = git(repo, ["rev-parse", "--is-shallow-repository"], check=False)
    return cp.stdout.strip() == "true"


def has_object(repo: Path, sha: str) -> bool:
    return git(repo, ["cat-file", "-e", sha], check=False).returncode == 0


def roots(repo: Path) -> list[str]:
    cp = git(repo, ["rev-list", "--max-parents=0", "--all"], check=False)
    return [ln.strip() for ln in cp.stdout.splitlines() if ln.strip()]


def clone_file_depth1(src: Path, dest: Path, extra: list[str] | None = None) -> None:
    if dest.exists():
        shutil.rmtree(dest)
    args = ["git", "clone", "-q", "--depth", "1", *(extra or []), "file://" + str(src.resolve()), str(dest)]
    sh(args)


def clone_path_depth1(src: Path, dest: Path) -> subprocess.CompletedProcess[str]:
    if dest.exists():
        shutil.rmtree(dest)
    return sh(
        ["git", "clone", "-q", "--depth", "1", str(src.resolve()), str(dest)],
        check=False,
    )


def setup_ugly() -> tuple[Path, str, str, str]:
    repo = FIX / "ugly"
    init_repo(repo, remote="git@github.com:keel-lab/ugly.git")
    v1 = commit_file(repo, "src/calc.py", HELPER_BODY, "v1")
    v2 = commit_file(repo, "src/math/ops.py", HELPER_BODY, "v2 extract")
    # keep origin path as leftover stub? NO — this destroyer does not attack leftover.
    # v2 still has the helper at src/calc.py AND a copy. Origin-body identity is out of scope.
    # For origin tests we only need a unique landing. Overwrite origin to a comment so the
    # locus is clearly in math/ops? That would look like leftover. Keep both files with
    # identical helper — resolve may be ambiguous. Better: move body only in v2 by deleting
    # the function from calc.py without making a leftover stub attack.
    write(
        repo / "src/calc.py",
        textwrap.dedent(
            '''\
            def add(a, b):
                return a + b
            '''
        ),
    )
    git(repo, ["add", "src/calc.py", "src/math/ops.py"])
    git(repo, ["commit", "-q", "-m", "v2: helper lives in math/ops"])
    v2 = git(repo, ["rev-parse", "HEAD"]).stdout.strip()
    token = keel(["mint", "--repo", str(repo), "--from", v1, "src/calc.py:4"], check=True).stdout.strip()
    return repo, v1, v2, token


def setup_foreign() -> Path:
    repo = FIX / "foreign"
    init_repo(repo, remote="git@github.com:other/util.git")
    commit_file(repo, "pkg/util.py", FOREIGN_HELPER, "unrelated helper")
    return repo


def setup_bare() -> tuple[Path, str, str]:
    repo = FIX / "bare"
    init_repo(repo, remote=None)
    v1 = commit_file(repo, "src/calc.py", FOREIGN_HELPER, "bare-v1")
    token = keel(["mint", "--repo", str(repo), "--from", v1, "src/calc.py:1"], check=True).stdout.strip()
    v2 = commit_file(repo, "src/calc.py", FOREIGN_HELPER + "# later\n", "bare-v2")
    return repo, v1, token


def main() -> int:
    if FIX.exists():
        shutil.rmtree(FIX)
    FIX.mkdir(parents=True)
    log(f"keel binary: {KEEL}")
    log(f"keel version: {keel(['--version']).stdout.strip() or keel(['--help']).stdout.splitlines()[0]}")
    st = keel(["--selftest"])
    log(f"selftest rc={st.returncode} {st.stdout.strip()}")
    if st.returncode != 0:
        return 1

    ugly, v1, v2, helper = setup_ugly()
    foreign = setup_foreign()
    bare, bare_v1, barepin = setup_bare()
    log("\n# minted helper")
    log(show_origin(helper))
    log(f"# ugly id: {kid(ugly, ['--from', v1])}")
    log(f"# ugly HEAD: {v2}")
    log(f"# V1: {v1}")
    log(f"# foreign id: {kid(foreign)}")
    log("# bare token " + show_origin(barepin))

    # ------------------------------------------------------------------
    # 0. Sanity: claims the mutation bought
    # ------------------------------------------------------------------
    cp = resolve(foreign, helper)
    record(
        "0a",
        "foreign git root fail-closes",
        "survived",
        cp,
        note="want rc=1, no result row",
        cmd=f"keel resolve --repo foreign --to HEAD $HELPER",
    )

    cp = keel(["resolve", "--repo", str(foreign), "--to", "HEAD", "--any-repo", "--porcelain", helper])
    record(
        "0b",
        "--any-repo papers a stranger at 1.000",
        "hole",
        cp,
        note="same flag that would save a fork also lands an unrelated helper",
        cmd="keel resolve --repo foreign --to HEAD --any-repo $HELPER",
    )

    cp = keel(["resolve", "--to-dir", str(foreign / "pkg"), "--porcelain", helper])
    record(
        "0c",
        "--to-dir of foreign git subdirectory inherit-refuses",
        "survived",
        cp,
        note="claimed closed vs pin v0.5; dest is still inside other/util",
        cmd="keel resolve --to-dir foreign/pkg $HELPER",
    )

    shal = FIX / "ugly-file-shallow"
    clone_file_depth1(ugly, shal)
    log(f"# file:// shallow? {is_shallow(shal)}  V1 in dest? {has_object(shal, v1)}")
    log(f"# file:// roots={roots(shal)} full roots={roots(ugly)}")
    log(f"# file:// id: {kid(shal)}")
    cp = resolve(shal, helper)
    record(
        "0d",
        "file:// --depth 1 of same project resolves (inherited remotes)",
        "survived",
        cp,
        note="the mutation's bought case; dest roots != full roots",
        cmd="git clone --depth 1 file://$UGLY && keel resolve --to HEAD $HELPER",
    )

    pathc = FIX / "ugly-path-depth1"
    path_cp = clone_path_depth1(ugly, pathc)
    log(f"# path --depth 1 stderr: {(path_cp.stderr or '').strip()}")
    log(f"# path shallow? {is_shallow(pathc)}  V1 in dest? {has_object(pathc, v1)}")
    log(f"# path roots={roots(pathc)}")
    cp = resolve(pathc, helper)
    record(
        "0e",
        "path --depth 1 is NOT a graft (git ignores --depth)",
        "claimed",
        cp,
        note="CANDIDATE already named this; dest still holds V1 so witnesses would match even without remotes",
        cmd="git clone --depth 1 $UGLY  # not file://",
    )

    orph = FIX / "ugly-orphan"
    if orph.exists():
        shutil.rmtree(orph)
    sh(["git", "clone", "-q", str(ugly), str(orph)])
    git(orph, ["checkout", "--orphan", "extra-hist"])
    write(orph / "orphan-only.txt", "orphan only\n")
    git(orph, ["add", "orphan-only.txt"])
    git(orph, ["commit", "-q", "-m", "orphan root"])
    main_ref = git(orph, ["rev-parse", "--abbrev-ref", "HEAD"], check=False).stdout.strip()
    # still on orphan; resolve --to the original V2 commit (pin v0.5 died here on roots)
    cp = keel(["resolve", "--repo", str(orph), "--to", v2, "--porcelain", helper])
    record(
        "0f",
        "orphan extra root, still on orphan, resolve --to original V2",
        "survived",
        cp,
        note="pin v0.5 fail-closed on extra root SHA; keel remotes still overlap",
        cmd="git checkout --orphan extra-hist && commit && keel resolve --to $V2",
    )
    git(orph, ["checkout", "-q", v2])
    cp = resolve(orph, helper)
    record(
        "0g",
        "orphan extra root then checkout original, resolve HEAD",
        "survived",
        cp,
        note="demo 25 shape",
        cmd="checkout main after orphan; keel resolve --to HEAD",
    )
    log(f"# orphan roots: {roots(orph)}")

    # ------------------------------------------------------------------
    # 1. Remote URL is config, not proof — spoof origin
    # ------------------------------------------------------------------
    spoof = FIX / "foreign-spoof"
    if spoof.exists():
        shutil.rmtree(spoof)
    sh(["git", "clone", "-q", str(foreign), str(spoof)])
    git(spoof, ["remote", "add", "extra", "git@github.com:keel-lab/ugly.git"])
    log(f"# spoof remotes:\n{git(spoof, ['remote', '-v']).stdout}")
    log(f"# spoof id: {kid(spoof)}")
    cp = resolve(spoof, helper)
    record(
        "1a",
        "foreign repo + extra remote spelled like the pin's project",
        "hole",
        cp,
        note="git remote add extra git@github.com:keel-lab/ugly.git with no fetch. remotes ∩ is True. Stranger lands.",
        cmd="git -C foreign remote add extra git@github.com:keel-lab/ugly.git && keel resolve",
    )

    # rewrite dest remotes to the pin's URL (replace, not extra)
    spoof2 = FIX / "foreign-seturl"
    if spoof2.exists():
        shutil.rmtree(spoof2)
    sh(["git", "clone", "-q", str(foreign), str(spoof2)])
    git(spoof2, ["remote", "set-url", "origin", "https://github.com/keel-lab/ugly.git"])
    cp = resolve(spoof2, helper)
    record(
        "1b",
        "foreign repo origin rewritten to pin's https URL",
        "hole",
        cp,
        note="ssh vs https of the *claimed* host/path is the same project. Rewriting origin is enough.",
        cmd="git remote set-url origin https://github.com/keel-lab/ugly.git",
    )

    # ------------------------------------------------------------------
    # 2. Shared graft / fetched witness — objects, not project
    # ------------------------------------------------------------------
    graft = FIX / "foreign-fetch"
    if graft.exists():
        shutil.rmtree(graft)
    sh(["git", "clone", "-q", str(foreign), str(graft)])
    # fetch the pin's V1 object; do not add a matching network remote
    fetch = git(graft, ["fetch", "--no-tags", str(ugly.resolve()), v1], check=False)
    log(f"# fetch rc={fetch.returncode} stderr={fetch.stderr.strip()[:400]}")
    log(f"# V1 now in foreign-fetch? {has_object(graft, v1)}")
    log(f"# foreign-fetch remotes:\n{git(graft, ['remote', '-v']).stdout}")
    log(f"# foreign-fetch id: {kid(graft)}")
    cp = resolve(graft, helper)
    record(
        "2a",
        "foreign repo that has fetched the pin's commit (no matching remote)",
        "hole",
        cp,
        note="object_exists(dest, pin.witness) short-circuits project identity. A fetch of one SHA is enough.",
        cmd=f"git -C foreign fetch $UGLY {v1[:12]} && keel resolve",
    )

    alt = FIX / "foreign-alternates"
    if alt.exists():
        shutil.rmtree(alt)
    sh(["git", "clone", "-q", str(foreign), str(alt)])
    alt_file = alt / ".git" / "objects" / "info" / "alternates"
    alt_file.parent.mkdir(parents=True, exist_ok=True)
    alt_file.write_text(str((ugly / ".git" / "objects").resolve()) + "\n", encoding="utf-8")
    log(f"# alternates V1 visible? {has_object(alt, v1)}")
    cp = resolve(alt, helper)
    record(
        "2b",
        "foreign repo with objects/info/alternates → victim object store",
        "hole",
        cp,
        note="clone --shared / alternates / graft: dest can see pin witnesses without being the project",
        cmd="echo $UGLY/.git/objects > foreign/.git/objects/info/alternates",
    )

    # local origin hop to a *different* project that happens to hold the objects
    hop_poison = FIX / "hop-poison"
    init_repo(hop_poison, remote=None)
    commit_file(hop_poison, "pkg/util.py", FOREIGN_HELPER, "poison")
    git(hop_poison, ["remote", "add", "origin", str(ugly.resolve())])
    log(f"# hop-poison id: {kid(hop_poison)}")
    cp = resolve(hop_poison, helper)
    record(
        "2c",
        "unrelated repo whose origin is a local path to the victim",
        "hole",
        cp,
        note="FOLLOW_HOPS walks local origin; hop remotes ∩ pin remotes, or hop object_exists(witness). Any local remote to the victim is the victim.",
        cmd="git remote add origin /path/to/ugly   # dest is other/util files",
    )

    # ------------------------------------------------------------------
    # 3. --to-dir: git subdir vs gitless copy vs containing stranger
    # ------------------------------------------------------------------
    gitless_pkg = FIX / "gitless-pkg"
    if gitless_pkg.exists():
        shutil.rmtree(gitless_pkg)
    shutil.copytree(foreign / "pkg", gitless_pkg)
    cp = keel(["resolve", "--to-dir", str(gitless_pkg), "--porcelain", helper])
    record(
        "3a",
        "--to-dir gitless copy of foreign subdirectory",
        "hole",
        cp,
        note="origins_match(pin, None) is True. pin v0.5 subdir hole is closed only when discover_repo finds a .git. A copy of pkg/ is a landing.",
        cmd="cp -R foreign/pkg /tmp/pkg && keel resolve --to-dir /tmp/pkg",
    )

    # copy files into a *different* git repo's subdirectory
    nest = FIX / "nest-stranger"
    init_repo(nest, remote="git@github.com:stranger/mono.git")
    commit_file(nest, "README.md", "mono\n", "seed")
    shutil.copytree(foreign / "pkg", nest / "vendor" / "ugly-pkg")
    git(nest, ["add", "vendor"])
    git(nest, ["commit", "-q", "-m", "vendor copy"])
    cp = keel(["resolve", "--to-dir", str(nest / "vendor" / "ugly-pkg"), "--porcelain", helper])
    record(
        "3b",
        "--to-dir of files sitting inside an unrelated git repo",
        "hole",
        cp,
        note="discover_repo walks up to stranger/mono. Dest origin is the container, not the files. Same bytes as 3a, opposite refuse.",
        cmd="keel resolve --to-dir stranger-mono/vendor/ugly-pkg",
    )

    # gitless --from-dir mint has no origin
    srcdir = FIX / "gitless-src"
    if srcdir.exists():
        shutil.rmtree(srcdir)
    write(srcdir / "src/calc.py", HELPER_BODY)
    gitless_token = keel(
        ["mint", "--from-dir", str(srcdir), "src/calc.py:4"], check=True
    ).stdout.strip()
    log("# gitless mint " + show_origin(gitless_token))
    cp = keel(["resolve", "--repo", str(foreign), "--to", "HEAD", "--porcelain", gitless_token])
    record(
        "3c",
        "gitless --from-dir mint resolves onto a foreign git repo",
        "hole",
        cp,
        note="missing pin origin is allowed. A directory mint is a universal token.",
        cmd="keel mint --from-dir DIR src/calc.py:4 && keel resolve --repo foreign",
    )

    # ------------------------------------------------------------------
    # 4. v1 / missing origin
    # ------------------------------------------------------------------
    # minted text from show
    shown = keel(["show", helper]).stdout
    minted_text = ""
    for ln in shown.splitlines():
        if ln.strip().startswith("text:"):
            minted_text = ln.split("text:", 1)[1].strip()
            break
    v1tok = forge_v1("src/calc.py", 4, minted_text or '    return "stable helper"')
    log(f"# v1 forged show:\n{keel(['show', v1tok]).stdout}")
    cp = keel(["resolve", "--repo", str(foreign), "--to", "HEAD", "--porcelain", v1tok])
    record(
        "4a",
        "forged v1 payload (no origin) lands on foreign repo",
        "hole",
        cp,
        note="CANDIDATE listed this. origins_match(None, dest) is True. Origin-as-project is optional on the token.",
        cmd="keel resolve --repo foreign  keel1.<v1-no-o>",
    )

    stripped = strip_origin(helper)
    log(f"# stripped-o show:\n{keel(['show', stripped]).stdout}")
    cp = keel(["resolve", "--repo", str(foreign), "--to", "HEAD", "--porcelain", stripped])
    record(
        "4b",
        "v3 token with origin field deleted",
        "hole",
        cp,
        note="same fail-open as v1. Dropping o is enough; no need to change version.",
        cmd="decode, pop o, re-encode",
    )

    # ------------------------------------------------------------------
    # 5. Remotes rewritten after a true shallow — same project looks foreign
    # ------------------------------------------------------------------
    sh_rw = FIX / "ugly-shallow-rewritten"
    clone_file_depth1(ugly, sh_rw)
    assert is_shallow(sh_rw) and not has_object(sh_rw, v1)
    git(sh_rw, ["remote", "set-url", "origin", "https://github.com/fork/ugly.git"])
    log(f"# rewritten shallow remotes:\n{git(sh_rw, ['remote', '-v']).stdout}")
    log(f"# rewritten shallow id: {kid(sh_rw)}")
    cp = resolve(sh_rw, helper)
    record(
        "5a",
        "file:// shallow then origin rewritten to a fork network URL",
        "hole",
        cp,
        note="dest remotes are fork/ugly; dest has no V1; local origin is no longer followable. Same project, fail-close. Path clones still have V1 and would pass.",
        cmd="git clone --depth 1 file://$UGLY && git remote set-url origin https://github.com/fork/ugly.git",
    )

    sh_rm = FIX / "ugly-shallow-noremote"
    clone_file_depth1(ugly, sh_rm)
    git(sh_rm, ["remote", "remove", "origin"])
    log(f"# noremote shallow id: {kid(sh_rm)}")
    cp = resolve(sh_rm, helper)
    record(
        "5b",
        "file:// shallow then git remote remove origin",
        "hole",
        cp,
        note="CI checkout without origin, or a copied .git/shallow. No remotes, no V1, nowhere to hop. Same project, fail-close.",
        cmd="git clone --depth 1 file://$UGLY && git remote remove origin",
    )

    # path clone --depth 1 (full objects) + rewrite remotes: still matches via object_exists
    path_rw = FIX / "ugly-path-rewritten"
    clone_path_depth1(ugly, path_rw)
    git(path_rw, ["remote", "set-url", "origin", "https://github.com/fork/ugly.git"])
    git(path_rw, ["remote", "remove", "origin"], check=False)
    # re-add fork only
    git(path_rw, ["remote", "add", "origin", "https://github.com/fork/ugly.git"], check=False)
    log(f"# path-rewritten shallow? {is_shallow(path_rw)} V1? {has_object(path_rw, v1)}")
    log(f"# path-rewritten id: {kid(path_rw)}")
    cp = resolve(path_rw, helper)
    record(
        "5c",
        "path --depth 1 + remotes rewritten to fork still resolves",
        "hole",
        cp,
        note="file:// vs path split: the same argv --depth 1, after the same remote rewrite, disagrees because path clones silently keep V1. Origin is still object-store occupancy, not project.",
        cmd="git clone --depth 1 $UGLY && git remote set-url origin fork; keel resolve",
    )

    # ------------------------------------------------------------------
    # 6. mint-then-advance-then-shallow, hops, origin gone
    # ------------------------------------------------------------------
    log(f"# bare V1 in full? {has_object(bare, bare_v1)}")
    baresh = FIX / "bare-shallow"
    clone_file_depth1(bare, baresh)
    log(f"# 24b-shape: shallow? {is_shallow(baresh)} V1 in dest? {has_object(baresh, bare_v1)}")
    log(f"# baresh id: {kid(baresh)}")
    cp = resolve(baresh, barepin)
    record(
        "6a",
        "remotes-less mint-then-advance-then-file:// shallow (follow origin)",
        "survived",
        cp,
        note="demo 24b. dest origin is file:// full, which still holds V1.",
        cmd="mint at V1; commit V2; git clone --depth 1 file://bare",
    )

    baresh2 = FIX / "bare-shallow-noremote"
    clone_file_depth1(bare, baresh2)
    git(baresh2, ["remote", "remove", "origin"])
    cp = resolve(baresh2, barepin)
    record(
        "6b",
        "mint-then-advance-then-shallow, then drop dest origin",
        "hole",
        cp,
        note="Lost clause made empirical. Token origin is keel1:r:;w:<V1> only. Dest cannot prove identity.",
        cmd="24b then git remote remove origin",
    )

    # 3-hop file:// of ugly (has remotes on the root, none on the hops)
    h1 = FIX / "hop1"
    h2 = FIX / "hop2"
    h3 = FIX / "hop3"
    clone_file_depth1(ugly, h1)
    clone_file_depth1(h1, h2)
    clone_file_depth1(h2, h3)
    for name, p in [("h1", h1), ("h2", h2), ("h3", h3)]:
        log(f"# {name} shallow={is_shallow(p)} V1={has_object(p, v1)} id={kid(p)}")
    cp = resolve(h1, helper)
    record("6c", "1-hop file:// shallow inherits remotes", "survived", cp, cmd="clone file://ugly")
    cp = resolve(h2, helper)
    record(
        "6d",
        "2-hop file:// shallow of a shallow",
        "survived" if cp.returncode == 0 and "\t" in (cp.stdout or "") else "hole",
        cp,
        note="FOLLOW_HOPS=2 should still reach the github remote / V1 objects",
        cmd="clone file://h1",
    )
    cp = resolve(h3, helper)
    record(
        "6e",
        "3-hop file:// shallow of a shallow of a shallow",
        "hole",
        cp,
        note="FOLLOW_HOPS=2 never walks to the full repo. Same project, fail-close. Nested CI caches / clone-of-clone-of-clone.",
        cmd="clone file://h2  # third graft",
    )

    # ------------------------------------------------------------------
    # 7. Host spelling is the project
    # ------------------------------------------------------------------
    alias = FIX / "ugly-ssh-alias"
    if alias.exists():
        shutil.rmtree(alias)
    sh(["git", "clone", "-q", str(ugly), str(alias)])
    git(alias, ["remote", "set-url", "origin", "git@gh:keel-lab/ugly.git"])
    log(f"# ssh-alias id: {kid(alias)}")
    # full clone still has V1 objects, so this may still MATCH via witnesses even with different remotes
    cp = resolve(alias, helper)
    record(
        "7a",
        "full clone origin rewritten to git@gh: alias (SSH config Host)",
        "survived" if cp.returncode == 0 else "hole",
        cp,
        note="remotes no longer overlap (gh/keel-lab/ugly vs github.com/keel-lab/ugly). Full clone still has V1, so object_exists saves it.",
        cmd="git remote set-url origin git@gh:keel-lab/ugly.git",
    )

    alias_sh = FIX / "ugly-alias-shallow"
    clone_file_depth1(ugly, alias_sh)
    git(alias_sh, ["remote", "set-url", "origin", "git@gh:keel-lab/ugly.git"])
    log(f"# alias-shallow id: {kid(alias_sh)}")
    cp = resolve(alias_sh, helper)
    record(
        "7b",
        "file:// shallow + origin rewritten to git@gh: alias",
        "hole",
        cp,
        note="same repo as 7a. Without V1 in dest, SSH Host aliases are a different project. CI machines with Host gh are foreign to tokens minted with github.com.",
        cmd="file:// --depth 1 then git@gh:",
    )

    sshgh = FIX / "ugly-sshgithub"
    clone_file_depth1(ugly, sshgh)
    git(sshgh, ["remote", "set-url", "origin", "ssh://git@ssh.github.com/keel-lab/ugly.git"])
    log(f"# ssh.github.com id: {kid(sshgh)}")
    cp = resolve(sshgh, helper)
    record(
        "7c",
        "file:// shallow + origin rewritten to ssh.github.com",
        "hole",
        cp,
        note="GitHub's SSH hostname is not github.com. normalize_remote keeps the host. Same project, fail-close.",
        cmd="git remote set-url origin ssh://git@ssh.github.com/keel-lab/ugly.git",
    )

    www = FIX / "ugly-www"
    clone_file_depth1(ugly, www)
    git(www, ["remote", "set-url", "origin", "https://www.github.com/keel-lab/ugly.git"])
    log(f"# www.github.com id: {kid(www)}")
    cp = resolve(www, helper)
    record(
        "7d",
        "file:// shallow + www.github.com",
        "hole",
        cp,
        note="www.github.com ≠ github.com after hostname lowercasing.",
        cmd="https://www.github.com/keel-lab/ugly.git",
    )

    # ------------------------------------------------------------------
    # 8. Fork remotes (PR CI) vs --any-repo papering
    # ------------------------------------------------------------------
    fork = FIX / "ugly-fork"
    init_repo(fork, remote="git@github.com:alice/ugly.git")
    # copy history by fetching objects? that's graft. Instead copy files as independent history.
    write(fork / "src/math/ops.py", HELPER_BODY)
    write(
        fork / "src/calc.py",
        textwrap.dedent(
            '''\
            def add(a, b):
                return a + b
            '''
        ),
    )
    git(fork, ["add", "src"])
    git(fork, ["commit", "-q", "-m", "forked files, independent history"])
    log(f"# fork id: {kid(fork)}")
    cp = resolve(fork, helper)
    record(
        "8a",
        "independent fork (different remotes, no shared objects)",
        "claimed",
        cp,
        note="CANDIDATE Lost: two forks with different remotes look foreign. Want --any-repo. That is also the stranger flag (0b).",
        cmd="keel resolve --repo alice/ugly $HELPER_from_upstream",
    )
    cp = keel(["resolve", "--repo", str(fork), "--to", "HEAD", "--any-repo", "--porcelain", helper])
    record(
        "8b",
        "--any-repo on the fork lands (and on the stranger, 0b)",
        "hole",
        cp,
        note="one flag papers 'same project, remotes drifted' and 'any tree, any project'. There is no --same-project-anyway.",
        cmd="keel resolve --any-repo",
    )

    # ------------------------------------------------------------------
    # 9. Orphan-only dest / remotes stripped
    # ------------------------------------------------------------------
    orph2 = FIX / "orphan-stripped"
    if orph2.exists():
        shutil.rmtree(orph2)
    sh(["git", "clone", "-q", str(ugly), str(orph2)])
    git(orph2, ["checkout", "--orphan", "extra-hist"])
    write(orph2 / "orphan-only.txt", "orphan only\n")
    git(orph2, ["add", "-A"])
    git(orph2, ["commit", "-q", "-m", "orphan root"])
    git(orph2, ["remote", "remove", "origin"])
    # still a full object store until we prune. V2 may still exist.
    log(f"# orphan-stripped V2 present? {has_object(orph2, v2)} remotes={git(orph2, ['remote', '-v']).stdout!r}")
    cp = keel(["resolve", "--repo", str(orph2), "--to", v2, "--porcelain", helper])
    record(
        "9a",
        "orphan HEAD, remotes stripped, resolve --to original V2 (objects remain)",
        "survived" if cp.returncode == 0 else "hole",
        cp,
        note="without remotes, --to V2 is a dest witness and V2 is still in the store. Roots no longer matter; occupancy of the SHA does.",
        cmd="checkout --orphan; remote remove origin; keel resolve --to $V2",
    )

    orph_sh = FIX / "orphan-shallow"
    # shallow clone of only the orphan branch from orph (which still has origin)
    orph_src = FIX / "ugly-orphan"  # from 0f/0g, currently on v2 with extra-hist branch
    git(orph_src, ["remote", "remove", "origin"], check=False)
    git(orph_src, ["remote", "add", "origin", "git@github.com:keel-lab/ugly.git"], check=False)
    if orph_sh.exists():
        shutil.rmtree(orph_sh)
    sh(
        [
            "git",
            "clone",
            "-q",
            "--depth",
            "1",
            "--branch",
            "extra-hist",
            "--single-branch",
            "file://" + str(orph_src.resolve()),
            str(orph_sh),
        ]
    )
    log(f"# orphan-shallow shallow={is_shallow(orph_sh)} V2={has_object(orph_sh, v2)} files={list(orph_sh.iterdir())}")
    log(f"# orphan-shallow id: {kid(orph_sh)}")
    cp = resolve(orph_sh, helper)
    record(
        "9b",
        "file:// depth-1 of the orphan branch only (inherited remotes)",
        "survived" if cp.returncode == 0 else "hole",
        cp,
        note="dest tree is orphan-only.txt; remotes still say keel-lab/ugly so origin matches. Landing is then a content question (likely deleted). Origin-as-project treats orphan-only graft as the project — which is the mutation. Record whether it fail-opens origin and then deletes.",
        cmd="git clone --depth 1 --branch extra-hist file://$ORPH",
    )

    # ------------------------------------------------------------------
    # 10. bundle of later tip, remotes-less
    # ------------------------------------------------------------------
    bundle = FIX / "later.bundle"
    git(bare, ["bundle", "create", str(bundle), "HEAD"])
    bundled = FIX / "from-bundle"
    if bundled.exists():
        shutil.rmtree(bundled)
    sh(["git", "clone", "-q", str(bundle), str(bundled)])
    log(f"# bundle remotes:\n{git(bundled, ['remote', '-v']).stdout}")
    log(f"# bundle id: {kid(bundled)}")
    log(f"# bundle has V1? {has_object(bundled, bare_v1)}")
    cp = resolve(bundled, barepin)
    record(
        "10a",
        "git clone of a bundle of the later tip (remotes-less mint)",
        "hole" if cp.returncode != 0 else "survived",
        cp,
        note="origin is the bundle path (local, not a project remote). If the clone is full it still has V1; git clone bundle is typically full history of the bundled refs. If V1 was not in the bundle, dest cannot follow a .bundle file as a git dir.",
        cmd="git bundle create later.bundle HEAD && git clone later.bundle",
    )

    # bundle only HEAD of bare (V2). git bundle HEAD includes ancestors unless -- since.
    bundle2 = FIX / "v2-only.bundle"
    git(bare, ["bundle", "create", str(bundle2), "HEAD", "--", "."], check=False)
    # try shallow-ish: pack only V2 with git bundle create --since
    bundle3 = FIX / "since.bundle"
    git(bare, ["bundle", "create", str(bundle3), "HEAD", "^" + bare_v1], check=False)
    bundled3 = FIX / "from-since-bundle"
    if bundled3.exists():
        shutil.rmtree(bundled3)
    clone3 = sh(["git", "clone", "-q", str(bundle3), str(bundled3)], check=False)
    log(f"# since-bundle clone rc={clone3.returncode} {clone3.stderr.strip()[:300]}")
    if clone3.returncode == 0:
        log(f"# since-bundle has V1? {has_object(bundled3, bare_v1)} id={kid(bundled3)}")
        cp = resolve(bundled3, barepin)
        record(
            "10b",
            "clone of a bundle that excludes V1 (remotes-less token)",
            "hole",
            cp,
            note="mint-then-advance then ship a V2-only bundle. No network remotes, no V1, origin is a file that is not a git dir to follow.",
            cmd="git bundle create v2.bundle HEAD ^V1 && git clone v2.bundle",
        )

    # ------------------------------------------------------------------
    # 11. kizu dogfood
    # ------------------------------------------------------------------
    if (KIZU / ".git").exists() or (KIZU / ".git").is_file():
        seen = keel(
            ["mint", "--repo", str(KIZU), "--from", "b4e6a5d", "src/app.rs:529"], check=True
        ).stdout.strip()
        log("# kizu token " + show_origin(seen))
        log(f"# kizu id: {kid(KIZU, ['--from', 'b4e6a5d'])}")
        cp = keel(["resolve", "--repo", str(KIZU), "--to", "HEAD", "--porcelain", seen])
        record(
            "11a",
            "kizu src/app.rs:529@b4e6a5d → layout.rs on full clone",
            "survived",
            cp,
            note="unique kizu pin still lands the godfile split. Do not kill because of this.",
            cmd="keel mint --from b4e6a5d src/app.rs:529 && keel resolve --to HEAD",
        )
        kizu_sh = FIX / "kizu-file-shallow"
        log("# cloning kizu file:// --depth 1 (may take a few seconds)")
        clone_file_depth1(KIZU, kizu_sh)
        log(f"# kizu shallow={is_shallow(kizu_sh)} b4e6a5d in dest? {has_object(kizu_sh, 'b4e6a5d')}")
        log(f"# kizu shallow id: {kid(kizu_sh)}")
        cp = keel(["resolve", "--repo", str(kizu_sh), "--to", "HEAD", "--porcelain", seen])
        record(
            "11b",
            "kizu pin on file:// --depth 1 of today's kizu",
            "survived" if cp.returncode == 0 and "layout.rs" in (cp.stdout or "") else "hole",
            cp,
            note="mint-time parent b4e6a5d is gone on a true graft. Remotes should inherit github.com/annenpolka/kizu.",
            cmd="git clone --depth 1 file://$KIZU && keel resolve $SEEN",
        )
        git(kizu_sh, ["remote", "set-url", "origin", "https://github.com/other/kizu.git"])
        log(f"# kizu rewritten id: {kid(kizu_sh)}")
        cp = keel(["resolve", "--repo", str(kizu_sh), "--to", "HEAD", "--porcelain", seen])
        record(
            "11c",
            "kizu file:// shallow + origin rewritten to other/kizu",
            "hole",
            cp,
            note="same tree as 11b. Fork remote + missing b4e6a5d → foreign. The pin that just landed the godfile split is now a different repository.",
            cmd="git remote set-url origin https://github.com/other/kizu.git",
        )
        # spoof kizu remote on foreign helper repo
        git(foreign, ["remote", "add", "kizu", "git@github.com:annenpolka/kizu.git"], check=False)
        cp = keel(["resolve", "--repo", str(foreign), "--to", "HEAD", "--porcelain", seen])
        record(
            "11d",
            "kizu pin on unrelated util after git remote add kizu git@github.com:annenpolka/kizu.git",
            "hole",
            cp,
            note="origin check passes because remotes ∩. Content may then miss layout.rs and report deleted/unresolved — the refuse that was supposed to be 'different repository' never fired.",
            cmd="git -C foreign remote add kizu git@github.com:annenpolka/kizu.git && keel resolve $SEEN",
        )
        # gitless copy of kizu src/app
        kizu_gitless = FIX / "kizu-gitless-src"
        if kizu_gitless.exists():
            shutil.rmtree(kizu_gitless)
        app = KIZU / "src" / "app"
        if app.is_dir():
            shutil.copytree(app, kizu_gitless / "src" / "app")
            cp = keel(["resolve", "--to-dir", str(kizu_gitless), "--porcelain", seen])
            record(
                "11e",
                "kizu pin --to-dir gitless copy of src/app",
                "hole",
                cp,
                note="no .git → dest origin None → origins_match True. A tarball of src/app is the project.",
                cmd="cp -R kizu/src/app /tmp/app && keel resolve --to-dir /tmp/app",
            )
    else:
        log("SKIP kizu (missing)")

    if (VOID / ".git").exists() or (VOID / ".git").is_file():
        evaluate = "packages/kernel/src/evaluate.ts"
        vp = keel(["mint", "--repo", str(VOID), "--from", "HEAD", f"{evaluate}:1"], check=True).stdout.strip()
        log("# void token " + show_origin(vp))
        cp = keel(["resolve", "--repo", str(VOID), "--to", "HEAD", "--porcelain", vp])
        record("12a", "voidtrace HEAD identity (sanity)", "survived", cp)
        # spoof void remote on foreign
        git(foreign, ["remote", "add", "void", "git@github.com:annenpolka/voidtrace.git"], check=False)
        cp = keel(["resolve", "--repo", str(foreign), "--to", "HEAD", "--porcelain", vp])
        record(
            "12b",
            "voidtrace pin on foreign after spoofing voidtrace remote",
            "hole",
            cp,
            note="same remotes∩ hole as 11d, different project name in the token.",
        )

    if (SKILLS / ".git").exists() or (SKILLS / ".git").is_file():
        log(f"# skills id: {kid(SKILLS)}")

    # ------------------------------------------------------------------
    # summary
    # ------------------------------------------------------------------
    log("\n\n======== SUMMARY ========")
    holes = [c for c in CASES if c.kind == "hole"]
    survived = [c for c in CASES if c.kind == "survived"]
    claimed = [c for c in CASES if c.kind == "claimed"]
    log(f"cases={len(CASES)} hole={len(holes)} survived={len(survived)} claimed={len(claimed)}")
    for c in CASES:
        landed = "LAND" if c.rc == 0 and c.stdout and not c.stdout.startswith("keel") else f"rc={c.rc}"
        log(f"{c.id:4} {c.kind:9} {landed:8} {c.title}")

    (OUT / "transcript.txt").write_text("\n".join(LOG) + "\n", encoding="utf-8")
    (OUT / "cases.json").write_text(
        json.dumps(
            [
                {
                    "id": c.id,
                    "title": c.title,
                    "kind": c.kind,
                    "rc": c.rc,
                    "stdout": c.stdout,
                    "stderr": c.stderr,
                    "note": c.note,
                    "cmd": c.cmd,
                }
                for c in CASES
            ],
            indent=2,
        )
        + "\n",
        encoding="utf-8",
    )
    log(f"\nwrote {OUT / 'transcript.txt'} and {OUT / 'cases.json'}")
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except Exception:
        import traceback

        traceback.print_exc()
        Path("/tmp/destroy-keel/transcript.txt").write_text(
            "\n".join(LOG) + "\n\n" + traceback.format_exc(), encoding="utf-8"
        )
        raise
