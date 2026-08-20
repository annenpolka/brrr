#!/usr/bin/env python3
"""Round 2: mint WHILE HEAD is V1, then advance, then dest is V2-only.

Round 1 stored V2 as a mint-time HEAD witness, so rewritten remotes / 3-hop /
ssh.github.com still matched via dest HEAD ∈ pin.witnesses. That is itself a
finding. This round isolates mint-then-advance, where dest tip is *not* in the token.
"""
from __future__ import annotations

import json
import os
import shutil
import subprocess
import textwrap
from pathlib import Path

KEEL = Path(
    "/Users/annenpolka/.grok/worktrees/annenpolka-brrr/subagent-01a01b85-3a6f-77f2-a6bf-cb0da2df3d3e/keel"
)
OUT = Path("/tmp/destroy-keel")
FIX = OUT / "r2"
KIZU = Path("/Users/annenpolka/ghq/github.com/annenpolka/kizu")
GIT_ENV = {
    **os.environ,
    "GIT_AUTHOR_NAME": "keel-destroyer",
    "GIT_AUTHOR_EMAIL": "destroyer@example.com",
    "GIT_COMMITTER_NAME": "keel-destroyer",
    "GIT_COMMITTER_EMAIL": "destroyer@example.com",
    "GIT_TERMINAL_PROMPT": "0",
}
LOG: list[str] = []
CASES: list[dict] = []

V1_BODY = textwrap.dedent(
    '''\
    def add(a, b):
        return a + b

    def helper_keep():
        return "stable helper"
    '''
)
V2_CALC = textwrap.dedent(
    '''\
    def add(a, b):
        return a + b
    '''
)
V2_OPS = V1_BODY


def log(msg: str = "") -> None:
    print(msg, flush=True)
    LOG.append(msg)


def sh(args, check=True, cwd=None):
    cp = subprocess.run(args, cwd=cwd, text=True, capture_output=True, env=GIT_ENV)
    if check and cp.returncode != 0:
        raise RuntimeError(f"{args} rc={cp.returncode}\n{cp.stdout}\n{cp.stderr}")
    return cp


def git(repo, args, check=True):
    return sh(["git", "-C", str(repo), *args], check=check)


def keel(args, check=False):
    return sh([str(KEEL), *args], check=check)


def write(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


def rec(id, title, kind, cp, note="", cmd=""):
    row = {
        "id": id,
        "title": title,
        "kind": kind,
        "rc": cp.returncode,
        "stdout": (cp.stdout or "").strip(),
        "stderr": (cp.stderr or "").strip(),
        "note": note,
        "cmd": cmd,
    }
    CASES.append(row)
    log(f"\n## {id}  [{kind}]  {title}")
    if cmd:
        log(f"$ {cmd}")
    log(f"# rc={row['rc']}")
    if row["stdout"]:
        log(row["stdout"])
    if row["stderr"]:
        log(row["stderr"])
    if note:
        log(f"# {note}")
    return row


def kid(repo, extra=None):
    cp = keel(["id", "--repo", str(repo), *(extra or [])])
    return (cp.stdout or "").strip().splitlines()[0] if cp.returncode == 0 else f"id-fail:{cp.stderr.strip()}"


def show_o(token):
    cp = keel(["show", token])
    return " | ".join(
        ln.strip()
        for ln in cp.stdout.splitlines()
        if any(k in ln for k in ("origin:", "remotes:", "witnesses:", "minted:"))
    )


def is_shallow(repo):
    return git(repo, ["rev-parse", "--is-shallow-repository"], check=False).stdout.strip() == "true"


def has_obj(repo, sha):
    return git(repo, ["cat-file", "-e", sha], check=False).returncode == 0


def clone_file(src, dest, extra=None):
    if dest.exists():
        shutil.rmtree(dest)
    sh(["git", "clone", "-q", "--depth", "1", *(extra or []), "file://" + str(src.resolve()), str(dest)])


def clone_path(src, dest):
    if dest.exists():
        shutil.rmtree(dest)
    return sh(["git", "clone", "-q", "--depth", "1", str(src.resolve()), str(dest)], check=False)


def resolve(repo, token, extra=None):
    return keel(["resolve", "--repo", str(repo), "--to", "HEAD", "--porcelain", *(extra or []), token])


def main():
    if FIX.exists():
        shutil.rmtree(FIX)
    FIX.mkdir(parents=True)

    ugly = FIX / "ugly"
    ugly.mkdir()
    git(ugly, ["init", "-q", "-b", "main"])
    git(ugly, ["remote", "add", "origin", "git@github.com:keel-lab/ugly.git"])
    write(ugly / "src/calc.py", V1_BODY)
    git(ugly, ["add", "src/calc.py"])
    git(ugly, ["commit", "-q", "-m", "v1"])
    v1 = git(ugly, ["rev-parse", "HEAD"]).stdout.strip()
    token = keel(["mint", "--repo", str(ugly), "--from", v1, "src/calc.py:4"], check=True).stdout.strip()
    log("# minted while HEAD==V1")
    log(show_o(token))
    log(f"# id at mint: {kid(ugly)}")
    assert v1[:16] in show_o(token)
    # advance
    write(ugly / "src/calc.py", V2_CALC)
    write(ugly / "src/math/ops.py", V2_OPS)
    git(ugly, ["add", "src"])
    git(ugly, ["commit", "-q", "-m", "v2 helper in math/ops"])
    v2 = git(ugly, ["rev-parse", "HEAD"]).stdout.strip()
    log(f"# V1={v1}")
    log(f"# V2={v2}")
    log(f"# id after V2: {kid(ugly)}")
    log(f"# token still: {show_o(token)}")

    foreign = FIX / "foreign"
    foreign.mkdir()
    git(foreign, ["init", "-q", "-b", "main"])
    git(foreign, ["remote", "add", "origin", "git@github.com:other/util.git"])
    write(foreign / "pkg/util.py", 'def helper_keep():\n    return "stable helper"\n')
    git(foreign, ["add", "pkg/util.py"])
    git(foreign, ["commit", "-q", "-m", "unrelated"])

    # 1-hop file:// of V2, remotes inherited — mutation's bought case for mint-then-advance
    sh1 = FIX / "sh1"
    clone_file(ugly, sh1)
    log(f"# sh1 shallow={is_shallow(sh1)} V1={has_obj(sh1, v1)} V2={has_obj(sh1, v2)} id={kid(sh1)}")
    rec(
        "R2-1hop",
        "mint-at-V1, advance V2, file:// depth-1, remotes inherited",
        "survived",
        resolve(sh1, token),
        note="dest witnesses are V2 only; V1 gone; match must be inherited github.com/keel-lab/ugly",
        cmd="mint@V1; commit V2; git clone --depth 1 file://ugly",
    )

    # remotes rewritten to fork after true shallow
    sh_fork = FIX / "sh-fork"
    clone_file(ugly, sh_fork)
    git(sh_fork, ["remote", "set-url", "origin", "https://github.com/fork/ugly.git"])
    log(f"# sh-fork id={kid(sh_fork)} remotes=\n{git(sh_fork, ['remote', '-v']).stdout}")
    rec(
        "R2-fork",
        "mint-at-V1, V2 file:// shallow, origin rewritten to fork/ugly",
        "hole",
        resolve(sh_fork, token),
        note="want fail-close: remotes are fork, dest has no V1, origin is network so not followable. dest HEAD V2 is NOT in the token.",
        cmd="file:// --depth 1 of V2; git remote set-url origin https://github.com/fork/ugly.git",
    )

    # drop origin
    sh_rm = FIX / "sh-rm"
    clone_file(ugly, sh_rm)
    git(sh_rm, ["remote", "remove", "origin"])
    log(f"# sh-rm id={kid(sh_rm)}")
    rec(
        "R2-noremote",
        "mint-at-V1, V2 file:// shallow, remote remove origin",
        "hole",
        resolve(sh_rm, token),
        note="keel1:r:github…;w:V1 vs keel1:r:;w:V2",
        cmd="file:// --depth 1; git remote remove origin",
    )

    # path --depth 1 of V2 + rewrite remotes (V1 still in dest)
    pathc = FIX / "path"
    clone_path(ugly, pathc)
    git(pathc, ["remote", "set-url", "origin", "https://github.com/fork/ugly.git"])
    log(f"# path shallow={is_shallow(pathc)} V1={has_obj(pathc, v1)} id={kid(pathc)}")
    rec(
        "R2-path-fork",
        "mint-at-V1, path --depth 1 of V2, origin rewritten to fork",
        "hole",
        resolve(pathc, token),
        note="same rewrite as R2-fork. Path clone kept V1 so object_exists matches. file:// vs path split on the hard case.",
        cmd="git clone --depth 1 $UGLY  # not file://; set-url fork",
    )

    # hops
    h1, h2, h3 = FIX / "h1", FIX / "h2", FIX / "h3"
    clone_file(ugly, h1)
    clone_file(h1, h2)
    clone_file(h2, h3)
    for n, p in [("h1", h1), ("h2", h2), ("h3", h3)]:
        log(f"# {n} shallow={is_shallow(p)} V1={has_obj(p, v1)} id={kid(p)}")
    rec("R2-h1", "1-hop file:// of V2 after mint-at-V1", "survived", resolve(h1, token))
    rec(
        "R2-h2",
        "2-hop file:// of V2 after mint-at-V1",
        "survived",
        resolve(h2, token),
        note="FOLLOW_HOPS=2 should still reach ugly's github remote / V1 objects",
    )
    rec(
        "R2-h3",
        "3-hop file:// of V2 after mint-at-V1",
        "hole",
        resolve(h3, token),
        note="FOLLOW_HOPS=2 never sees the full repo. dest HEAD is V2, not in token. Same project, fail-close.",
    )

    # host spellings on V2-only dest
    for rid, url, title in [
        ("R2-gh", "git@gh:keel-lab/ugly.git", "git@gh: SSH Host alias"),
        ("R2-sshgh", "ssh://git@ssh.github.com/keel-lab/ugly.git", "ssh.github.com"),
        ("R2-www", "https://www.github.com/keel-lab/ugly.git", "www.github.com"),
        ("R2-gitlab", "https://gitlab.com/keel-lab/ugly.git", "gitlab mirror of same path"),
    ]:
        d = FIX / rid
        clone_file(ugly, d)
        git(d, ["remote", "set-url", "origin", url])
        log(f"# {rid} id={kid(d)}")
        rec(
            rid,
            f"mint-at-V1, V2 file:// shallow, origin={url}",
            "hole",
            resolve(d, token),
            note=title + " — hostname is the project. dest has no V1.",
            cmd=f"git remote set-url origin {url}",
        )

    # same github remote spelling after shallow (CI) — should match via remotes ∩
    sh_https = FIX / "sh-https"
    clone_file(ugly, sh_https)
    git(sh_https, ["remote", "set-url", "origin", "https://github.com/keel-lab/ugly.git"])
    log(f"# sh-https id={kid(sh_https)}")
    rec(
        "R2-https",
        "mint-at-V1, V2 file:// shallow, origin set to https://github.com/keel-lab/ugly.git",
        "survived",
        resolve(sh_https, token),
        note="CI case: dest origin is the project URL, not a local hop. remotes ∩, no V1 needed.",
        cmd="set-url origin https://github.com/keel-lab/ugly.git",
    )

    # stolen witness: fetch V1 into foreign, keep foreign remotes
    graft = FIX / "graft"
    if graft.exists():
        shutil.rmtree(graft)
    sh(["git", "clone", "-q", str(foreign), str(graft)])
    git(graft, ["fetch", "--no-tags", str(ugly.resolve()), v1], check=False)
    log(f"# graft V1={has_obj(graft, v1)} id={kid(graft)}")
    rec(
        "R2-fetch",
        "foreign fetch of mint-time V1 only (no matching remote)",
        "hole",
        resolve(graft, token),
        note="object_exists(dest, V1). Token was minted before V2 existed. One fetched SHA is the project.",
        cmd=f"git -C foreign fetch ugly {v1[:12]}",
    )

    # spoof remote on foreign
    spoof = FIX / "spoof"
    if spoof.exists():
        shutil.rmtree(spoof)
    sh(["git", "clone", "-q", str(foreign), str(spoof)])
    git(spoof, ["remote", "add", "extra", "git@github.com:keel-lab/ugly.git"])
    rec(
        "R2-spoof",
        "foreign + extra remote git@github.com:keel-lab/ugly.git (mint-at-V1 token)",
        "hole",
        resolve(spoof, token),
        note="remotes ∩ does not care that dest never fetched ugly.",
        cmd="git remote add extra git@github.com:keel-lab/ugly.git",
    )

    # local origin hop
    hop = FIX / "local-origin"
    hop.mkdir()
    git(hop, ["init", "-q", "-b", "main"])
    write(hop / "pkg/util.py", 'def helper_keep():\n    return "stable helper"\n')
    git(hop, ["add", "pkg/util.py"])
    git(hop, ["commit", "-q", "-m", "poison"])
    git(hop, ["remote", "add", "origin", str(ugly.resolve())])
    rec(
        "R2-localorigin",
        "unrelated files, origin=local path to ugly (mint-at-V1 token)",
        "hole",
        resolve(hop, token),
        note="FOLLOW_HOPS: hop remotes ∩ or hop holds V1.",
        cmd="git remote add origin /path/to/ugly",
    )

    # orphan-only tree (rm files, then commit)
    orph = FIX / "orph"
    if orph.exists():
        shutil.rmtree(orph)
    sh(["git", "clone", "-q", str(ugly), str(orph)])
    git(orph, ["checkout", "--orphan", "extra-hist"])
    git(orph, ["rm", "-rf", "."], check=False)
    write(orph / "orphan-only.txt", "orphan only\n")
    git(orph, ["add", "-A"])
    git(orph, ["commit", "-q", "-m", "orphan root only"])
    orph_sha = git(orph, ["rev-parse", "HEAD"]).stdout.strip()
    log(f"# orphan-only sha={orph_sha} files={list(orph.iterdir())}")
    rec(
        "R2-orph-to-v2",
        "orphan-only commit, remotes kept, resolve --to V2",
        "survived",
        keel(["resolve", "--repo", str(orph), "--to", v2, "--porcelain", token]),
        note="same project via remotes. --to V2 still has the files. pin v0.5 died on extra root; keel should not.",
        cmd="git checkout --orphan; git rm -rf .; commit orphan-only; keel resolve --to V2",
    )
    rec(
        "R2-orph-head",
        "orphan-only HEAD resolve (no src/)",
        "survived",
        resolve(orph, token),
        note="origin should MATCH (remotes). Content then deleted. Not leftover-stub — the tree has no helper.",
        cmd="keel resolve --to HEAD  # HEAD is orphan-only.txt",
    )

    # shallow of orphan-only after stripping remotes on dest
    orph_sh = FIX / "orph-sh"
    clone_file(orph, orph_sh, extra=["--branch", "extra-hist", "--single-branch"])
    # orph still has origin pointing at ugly clone path; inherited remotes?
    log(f"# orph remotes=\n{git(orph, ['remote', '-v']).stdout}")
    log(f"# orph-sh shallow={is_shallow(orph_sh)} V1={has_obj(orph_sh, v1)} id={kid(orph_sh)}")
    rec(
        "R2-orph-sh",
        "file:// depth-1 of orphan-only branch (mint-at-V1 token)",
        "survived",
        resolve(orph_sh, token),
        note="origin may inherit via hop to orph, which hops to ugly. If remotes reach ugly, origin matches and content is deleted.",
    )
    git(orph_sh, ["remote", "remove", "origin"], check=False)
    rec(
        "R2-orph-sh-rm",
        "orphan-only file:// shallow, dest origin removed",
        "hole",
        resolve(orph_sh, token),
        note="no remotes, no V1, dest HEAD is orphan SHA. Same git family, fail-close.",
    )

    # kizu: mint-at-old, dest is file:// shallow of HEAD with remotes rewritten.
    # Token will store b4e6a5d AND current HEAD, so dest HEAD ∈ witnesses. Confirm.
    # Then: dest that is a shallow of a commit that is NEITHER witness — we cannot
    # advance kizu. Instead show that rewriting remotes on a shallow of HEAD still
    # matches *because dest HEAD is a stored witness*, i.e. tip occupancy not remotes.
    if (KIZU / ".git").exists() or (KIZU / ".git").is_file():
        seen = keel(
            ["mint", "--repo", str(KIZU), "--from", "b4e6a5d", "src/app.rs:529"], check=True
        ).stdout.strip()
        log("# kizu " + show_o(seen))
        ksh = FIX / "kizu-sh"
        clone_file(KIZU, ksh)
        git(ksh, ["remote", "set-url", "origin", "git@github.com:fork/kizu.git"])
        log(f"# kizu-sh id={kid(ksh)} b4e6a5d={has_obj(ksh, 'b4e6a5d')}")
        rec(
            "R2-kizu-fork",
            "kizu pin (witnesses=b4e6a5d+HEAD) on file:// shallow with fork remotes",
            "hole",
            resolve(ksh, seen),
            note="lands layout.rs. remotes do not overlap. dest HEAD 16-char prefix is in the token. Tip witness is the real key; remotes are optional once dest sits on a stored SHA.",
            cmd="mint --from b4e6a5d (HEAD=today); clone --depth 1 file://kizu; set-url fork",
        )

        # synthetic: a repo whose HEAD is reset to kizu HEAD SHA after fetch, files are util
        # resolve --to HEAD would then snapshot kizu's tree. Use --to-dir of util files
        # while check_root is the graft repo? --to-dir discover_repo walks from the dir.
        # Put util files inside the graft repo as untracked extra? load_snapshot --to-dir
        # uses directory files + discover_repo origin.
        steal = FIX / "steal-head"
        steal.mkdir()
        git(steal, ["init", "-q", "-b", "main"])
        git(steal, ["remote", "add", "origin", "git@github.com:other/util.git"])
        write(steal / "src/app/layout.rs", Path(KIZU / "src/app/layout.rs").read_text(encoding="utf-8", errors="replace")[:4000])
        git(steal, ["add", "src"])
        git(steal, ["commit", "-q", "-m", "copy of layout.rs, independent history"])
        kizu_head = git(KIZU, ["rev-parse", "HEAD"]).stdout.strip()
        git(steal, ["fetch", "--no-tags", str(KIZU.resolve()), kizu_head], check=False)
        log(f"# steal has kizu HEAD object? {has_obj(steal, kizu_head)} id={kid(steal)}")
        rec(
            "R2-kizu-fetch",
            "independent repo with a copy of layout.rs + fetched kizu HEAD object",
            "hole",
            resolve(steal, seen),
            note="object_exists(kizu HEAD). Origin check passes. Then fingerprint may land layout.rs at 1.000 on a stranger that copied one file and fetched one SHA.",
            cmd="git fetch kizu HEAD; files are a copied layout.rs",
        )

    log("\n\n======== R2 SUMMARY ========")
    for c in CASES:
        landed = "LAND" if c["rc"] == 0 and c["stdout"] else f"rc={c['rc']}"
        log(f"{c['id']:16} {c['kind']:9} {landed:8} {c['title']}")
    (OUT / "transcript-round2.txt").write_text("\n".join(LOG) + "\n", encoding="utf-8")
    (OUT / "cases-round2.json").write_text(json.dumps(CASES, indent=2) + "\n", encoding="utf-8")
    log(f"wrote {OUT / 'transcript-round2.txt'}")
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except Exception:
        import traceback
        traceback.print_exc()
        (OUT / "transcript-round2.txt").write_text("\n".join(LOG) + "\n" + traceback.format_exc(), encoding="utf-8")
        raise
