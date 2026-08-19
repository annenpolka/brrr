#!/usr/bin/env python3
"""DESTROYER battery for woof — --only prose is class-not-path.

DESTROYER_WEFT already named the docs/** glob. Do not re-run that pass.
This battery attacks woof's claim that --only prose is comment+text tokens
regardless of path. Cite snag --forbid number; do not clone it.
tally --chg is the fence-flood peel — contrast, not a rewrite of woof.
"""
from __future__ import annotations

import os
import subprocess
import sys
import time
from pathlib import Path

WOOF = os.environ.get(
    "WOOF",
    "/Users/annenpolka/.grok/worktrees/annenpolka-brrr/subagent-01a01bad-eb91-7d80-9aa0-10d91539263d/woof",
)
TALLY = os.environ.get(
    "TALLY",
    "/Users/annenpolka/.grok/worktrees/annenpolka-brrr/subagent-01a01bd4-9291-7c63-9bf2-7db4d4bb2bf3/tally",
)
WEFT = os.environ.get(
    "WEFT",
    "/Users/annenpolka/.grok/worktrees/annenpolka-brrr/subagent-01a01b68-3200-7781-bf46-49a3c771f5ff/weft",
)
SNAG = os.environ.get(
    "SNAG",
    "/Users/annenpolka/.grok/worktrees/annenpolka-brrr/subagent-01a01b83-58ff-7043-bd7c-ca791fbb8e0c/snag",
)
ROOT = Path(os.environ.get("DESTROY_ROOT", "/tmp/destroy-woof"))
FIX = ROOT / "fixtures"
LOG = ROOT / "transcript.txt"
FOLLOW = ROOT / "followup.txt"
os.makedirs(FIX, exist_ok=True)

SB = "/Users/annenpolka/ghq/github.com/annenpolka/sitbone"
KZ = "/Users/annenpolka/ghq/github.com/annenpolka/kizu"
VT = "/Users/annenpolka/ghq/github.com/annenpolka/voidtrace"
WOOF_FIX = Path(
    "/Users/annenpolka/.grok/worktrees/annenpolka-brrr/subagent-01a01bad-eb91-7d80-9aa0-10d91539263d/fixtures"
)
TALLY_FIX = Path(
    "/Users/annenpolka/.grok/worktrees/annenpolka-brrr/subagent-01a01bd4-9291-7c63-9bf2-7db4d4bb2bf3/fixtures"
)

transcript: list[str] = []


def log(msg: str = "") -> None:
    print(msg, flush=True)
    transcript.append(msg)


def write(path: Path, text: str) -> Path:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")
    return path


def banner(title: str) -> None:
    log()
    log("=" * 72)
    log(title)
    log("=" * 72)


def run_bin(
    bin_path: str,
    args: list[str],
    stdin: bytes | str | None = None,
    timeout: float = 30.0,
) -> tuple[int, str, str, float]:
    cmd = [bin_path, *args]
    if stdin is None:
        data = None
    elif isinstance(stdin, bytes):
        data = stdin
    else:
        data = stdin.encode("utf-8")
    t0 = time.perf_counter()
    try:
        p = subprocess.run(cmd, input=data, capture_output=True, timeout=timeout)
        elapsed = time.perf_counter() - t0
        out = p.stdout.decode("utf-8", errors="replace")
        err = p.stderr.decode("utf-8", errors="replace")
        return p.returncode, out, err, elapsed
    except subprocess.TimeoutExpired as e:
        elapsed = time.perf_counter() - t0
        out = (e.stdout or b"").decode("utf-8", errors="replace")
        err = (e.stderr or b"").decode("utf-8", errors="replace") + f"\nTIMEOUT after {timeout}s"
        return 124, out, err, elapsed


def woof(args: list[str], stdin: bytes | str | None = None) -> tuple[int, str, str, float]:
    return run_bin(WOOF, args, stdin)


def tally(args: list[str], stdin: bytes | str | None = None) -> tuple[int, str, str, float]:
    return run_bin(TALLY, args, stdin)


def weft(args: list[str], stdin: bytes | str | None = None) -> tuple[int, str, str, float]:
    return run_bin(WEFT, args, stdin)


def snag(args: list[str], stdin: bytes | str | None = None) -> tuple[int, str, str, float]:
    return run_bin(SNAG, args, stdin)


def show(name: str, rc: int, out: str, err: str, elapsed: float, cap: int = 24) -> None:
    log(f"$ {name}")
    body = out.rstrip("\n")
    if body:
        lines = body.splitlines()
        for ln in lines[:cap]:
            log(ln)
        if len(lines) > cap:
            log(f"  … and {len(lines) - cap} more stdout lines")
    if err.strip():
        elines = err.rstrip("\n").splitlines()
        for ln in elines[:12]:
            log("stderr: " + ln)
        if len(elines) > 12:
            log(f"  … and {len(elines) - 12} more stderr lines")
    log(f"# rc={rc}  elapsed={elapsed:.3f}s")


def git_diff(repo: str, spec: str) -> bytes:
    return subprocess.check_output(
        ["git", "-C", repo, "diff", "--no-color", "--no-ext-diff", spec],
        stderr=subprocess.DEVNULL,
    )


def save_diff(name: str, text: str) -> Path:
    return write(FIX / name, text if text.endswith("\n") else text + "\n")


def copy_known(name: str, src: Path) -> str:
    text = src.read_text(encoding="utf-8")
    save_diff(name, text)
    return text


# ---------------------------------------------------------------------------
# fixtures (class-not-path; not the DESTROYER_WEFT glob battery)
# ---------------------------------------------------------------------------

FENCE = r"""diff --git a/README.md b/README.md
--- a/README.md
+++ b/README.md
@@ -1,8 +1,8 @@
 # demo
 Copy this into src:
 
 ```rust
-let timeout = 30;
+let timeout = 60;
 fn retry() {}
 ```
"""

MIXED_MONEY = r"""--- a/src.rs
+++ b/src.rs
@@ -1,3 +1,3 @@
 fn main() {
-    let timeout = 30; // seconds
+    let timeout = 60; // secs
 }
"""

COMMENT_NUMBER = r"""diff --git a/src.rs b/src.rs
--- a/src.rs
+++ b/src.rs
@@ -1 +1 @@
-    let timeout = 30; // timeout 30
+    let timeout = 30; // timeout 60
"""

CJK_README = """diff --git a/README.md b/README.md
--- a/README.md
+++ b/README.md
@@ -1 +1 @@
-契約は蒸留
+契約は資産
"""

CJK_IDENT = r"""diff --git a/src.rs b/src.rs
--- a/src.rs
+++ b/src.rs
@@ -1,3 +1,3 @@
-fn 契約() {
+fn 資産() {
     let timeout = 30;
 }
"""

CJK_MIXED = r"""diff --git a/src.rs b/src.rs
--- a/src.rs
+++ b/src.rs
@@ -1,3 +1,3 @@
-fn timeout_秒() { let x = 1; }
+fn delay_秒() { let x = 1; }
"""

CJK_FULLWIDTH = r"""diff --git a/src.rs b/src.rs
--- a/src.rs
+++ b/src.rs
@@ -1 +1 @@
-let timeout = ３０;
+let timeout = ６０;
"""

CJK_COMMENT = r"""diff --git a/src.rs b/src.rs
--- a/src.rs
+++ b/src.rs
@@ -1 +1 @@
-let timeout = 30; // 秒
+let timeout = 30; // タイムアウト
"""

CJK_INDENTED = r"""diff --git a/README.md b/README.md
--- a/README.md
+++ b/README.md
@@ -1,3 +1,3 @@
 # demo
-    fn 契約() {}
+    fn 資産() {}
"""

CJK_TXT = r"""diff --git a/notes.txt b/notes.txt
--- a/notes.txt
+++ b/notes.txt
@@ -1 +1 @@
-fn 契約() {}
+fn 資産() {}
"""

CJK_CHANGELOG = r"""diff --git a/CHANGELOG b/CHANGELOG
--- a/CHANGELOG
+++ b/CHANGELOG
@@ -1 +1 @@
-fn 契約()
+fn 資産()
"""

CJK_FENCE = r"""diff --git a/README.md b/README.md
--- a/README.md
+++ b/README.md
@@ -1,6 +1,6 @@
 # demo
 ```rust
-fn 契約() {}
+fn 資産() {}
 ```
"""

INDENTED_IDENT = r"""diff --git a/README.md b/README.md
--- a/README.md
+++ b/README.md
@@ -1,3 +1,3 @@
 # demo
-    fn fetch_user() {}
+    fn fetch_account() {}
"""

INDENTED_BOTH = r"""diff --git a/README.md b/README.md
--- a/README.md
+++ b/README.md
@@ -1,5 +1,5 @@
 # demo
 
-    fn fetch_user() { let timeout = 30; }
+    fn fetch_account() { let timeout = 60; }
"""

RST_CODEBLOCK = r"""diff --git a/guide.rst b/guide.rst
--- a/guide.rst
+++ b/guide.rst
@@ -1,6 +1,6 @@
 title
 .. code-block:: rust
-    fn fetch_user() { let timeout = 30; }
+    fn fetch_account() { let timeout = 60; }
"""

SHA_DIGIT = r"""diff --git a/README.md b/README.md
--- a/README.md
+++ b/README.md
@@ -1 +1 @@
-see commit 77df1da
+see commit 98a8009
"""

SHA_MIXED_PREFIX = r"""diff --git a/docs/adr/0019.md b/docs/adr/0019.md
--- a/docs/adr/0019.md
+++ b/docs/adr/0019.md
@@ -1,3 +1,3 @@
 # adr
-implements 557c76f
+implements e9b0f75
"""

SHA_LETTER = r"""diff --git a/README.md b/README.md
--- a/README.md
+++ b/README.md
@@ -1 +1 @@
-see e9b0f75
+see ce44c93
"""

SHA_CODE_UNQUOTED = r"""diff --git a/src.rs b/src.rs
--- a/src.rs
+++ b/src.rs
@@ -1 +1 @@
-let rev = 77df1da;
+let rev = 98a8009;
"""

SHA_CODE_STRING = r"""diff --git a/src.rs b/src.rs
--- a/src.rs
+++ b/src.rs
@@ -1 +1 @@
-const REV: &str = "77df1da";
+const REV: &str = "98a8009";
"""

INLINE_TICK_NUMBER = r"""diff --git a/README.md b/README.md
--- a/README.md
+++ b/README.md
@@ -1 +1 @@
-set timeout to `30`
+set timeout to `60`
"""

FENCE_BODY_SWAP = r"""diff --git a/README.md b/README.md
--- a/README.md
+++ b/README.md
@@ -1,8 +1,8 @@
 # demo
-The old timeout was 60.
+The old timeout was 30.
 
 ```rust
-let timeout = 30;
+let timeout = 60;
 ```
"""

UNTITLED_FENCE = r"""diff --git a/README.md b/README.md
--- a/README.md
+++ b/README.md
@@ -1,6 +1,6 @@
 # demo
 ```
-let timeout = 30;
+let timeout = 60;
 ```
"""

HTML_COMMENT_MD = r"""diff --git a/README.md b/README.md
--- a/README.md
+++ b/README.md
@@ -1 +1 @@
-<!-- timeout 30 -->
+<!-- timeout 60 -->
"""

HTML_COMMENT_RS = r"""diff --git a/src.rs b/src.rs
--- a/src.rs
+++ b/src.rs
@@ -1 +1 @@
-<!-- timeout 30 -->
+<!-- timeout 60 -->
"""

RENAME_ONLY = r"""diff --git a/src/foo.rs b/src/bar.rs
similarity index 100%
rename from src/foo.rs
rename to src/bar.rs
"""

MODE_ONLY = r"""diff --git a/src/run.sh b/src/run.sh
old mode 100644
new mode 100755
"""

EMPTY_ADD = r"""diff --git a/notes.txt b/notes.txt
new file mode 100644
--- /dev/null
+++ b/notes.txt
"""

BINARY_SRC = """diff --git a/src/secret.bin b/src/secret.bin
index 1111111..2222222 100644
Binary files a/src/secret.bin and b/src/secret.bin differ
"""

BINARY_GIF = """diff --git a/docs/media/demo.gif b/docs/media/demo.gif
index 1111111..2222222 100644
Binary files a/docs/media/demo.gif and b/docs/media/demo.gif differ
"""

GIT_BINARY_PATCH = """diff --git a/src/blob.bin b/src/blob.bin
GIT binary patch
delta 12
zcmZQz
literal 0
HcmV?d00001
"""

LOCK_ONLY = r"""diff --git a/Cargo.lock b/Cargo.lock
--- a/Cargo.lock
+++ b/Cargo.lock
@@ -1,3 +1,3 @@
 [[package]]
 name = "kizu"
-version = "0.6.0"
+version = "0.7.0"
"""

HEX_0X = r"""diff --git a/README.md b/README.md
--- a/README.md
+++ b/README.md
@@ -1 +1 @@
-hash 0xdeadbeef
+hash 0xcafebabe
"""

MOVE_IDENT = r"""diff --git a/src.rs b/src.rs
--- a/src.rs
+++ b/src.rs
@@ -1,3 +1,3 @@
-fn fetch_user() {}
+fn other() {}
 fn keep() {}
+fn fetch_user() {}
"""


def main() -> int:
    os.chmod(WOOF, 0o755)
    if os.path.exists(TALLY):
        os.chmod(TALLY, 0o755)
    if os.path.exists(WEFT):
        os.chmod(WEFT, 0o755)
    if os.path.exists(SNAG):
        os.chmod(SNAG, 0o755)

    banner("0. baseline (woof 0.2; do not rewrite)")
    rc, out, err, el = woof(["--selftest"])
    show("./woof --selftest", rc, out, err, el)
    rc, out, err, el = woof(["--version"])
    show("./woof --version", rc, out, err, el)
    if os.path.exists(TALLY):
        rc, out, err, el = tally(["--version"])
        show("./tally --version", rc, out, err, el)
    if os.path.exists(WEFT):
        rc, out, err, el = weft(["--version"])
        show("./weft --version", rc, out, err, el)

    # ------------------------------------------------------------------
    banner("1. gold that must survive (mixed-line, comment-interior, CJK split, fence number)")
    mixed = copy_known("mixed-money.diff", WOOF_FIX / "mixed-money.diff") if (WOOF_FIX / "mixed-money.diff").exists() else MIXED_MONEY
    if not (WOOF_FIX / "mixed-money.diff").exists():
        save_diff("mixed-money.diff", mixed)
    rc, out, err, el = woof(["--only", "prose"], mixed)
    show("./woof --only prose  < mixed-money.diff", rc, out, err, el)
    rc, out, err, el = woof(["--only", "prose", "--emit"], mixed)
    show("./woof --only prose --emit  < mixed-money.diff", rc, out, err, el)

    interior = copy_known("comment-number.diff", WOOF_FIX / "comment-number.diff") if (WOOF_FIX / "comment-number.diff").exists() else COMMENT_NUMBER
    if not (WOOF_FIX / "comment-number.diff").exists():
        save_diff("comment-number.diff", interior)
    rc, out, err, el = woof(["--only", "prose"], interior)
    show("./woof --only prose  < comment-number.diff  (interior 30→60)", rc, out, err, el)
    if os.path.exists(SNAG):
        rc, out, err, el = snag(["--forbid", "number"], interior)
        show("./snag --forbid number  < comment-number.diff  (cited, not cloned)", rc, out, err, el)
    if os.path.exists(WEFT):
        rc, out, err, el = weft(["--only", "docs"], interior)
        show("./weft --only docs  < comment-number.diff", rc, out, err, el)

    save_diff("cjk-readme.diff", CJK_README)
    save_diff("cjk-ident.diff", CJK_IDENT)
    rc, out, err, el = woof(["--only", "prose"], CJK_README)
    show("./woof --only prose  < cjk-readme.diff", rc, out, err, el)
    rc, out, err, el = woof(["--only", "comments"], CJK_README)
    show("./woof --only comments  < cjk-readme.diff", rc, out, err, el)
    rc, out, err, el = woof(["--only", "prose"], CJK_IDENT)
    show("./woof --only prose  < cjk-ident.diff  (fn 契約 on src.rs)", rc, out, err, el)

    fence = copy_known("fence-number.md.diff", WOOF_FIX / "fence-number.md.diff") if (WOOF_FIX / "fence-number.md.diff").exists() else FENCE
    if not (WOOF_FIX / "fence-number.md.diff").exists():
        save_diff("fence-number.md.diff", fence)
    rc, out, err, el = woof(["--only", "prose"], fence)
    show("./woof --only prose  < fence-number.md.diff  (v0.2 number ply)", rc, out, err, el)
    if os.path.exists(WEFT):
        rc, out, err, el = weft(["--only", "docs"], fence)
        show("./weft --only docs  < fence-number.md.diff  (DESTROYER_WEFT glob+swallow; cite, do not re-run)", rc, out, err, el)
    if os.path.exists(TALLY):
        rc, out, err, el = tally(["--only", "prose", "--chg"], fence)
        show("./tally --only prose --chg  < fence-number.md.diff", rc, out, err, el)

    gen = ""
    if (WOOF_FIX / "docs-generated-api.rs.diff").exists():
        gen = copy_known("docs-generated-api.rs.diff", WOOF_FIX / "docs-generated-api.rs.diff")
        rc, out, err, el = woof(["--only", "prose"], gen)
        show("./woof --only prose  < docs-generated-api.rs.diff  (class-not-path; DESTROYER_WEFT glob is closed here)", rc, out, err, el)
        if os.path.exists(WEFT):
            rc, out, err, el = weft(["--only", "docs"], gen)
            show("./weft --only docs  < docs-generated-api.rs.diff  (path glob still frees it)", rc, out, err, el)

    # ------------------------------------------------------------------
    banner("2. new bash sample is 114 ident inserts (sitbone 77df1da; tally --chg contrast)")
    if (TALLY_FIX / "fence-new-sample.md.diff").exists():
        newsamp = copy_known("fence-new-sample.md.diff", TALLY_FIX / "fence-new-sample.md.diff")
        rc, out, err, el = woof(["--only", "prose"], newsamp)
        show("./woof --only prose  < fence-new-sample.md.diff", rc, out, err, el)
        if os.path.exists(TALLY):
            rc, out, err, el = tally(["--only", "prose", "--chg"], newsamp)
            show("./tally --only prose --chg  < fence-new-sample.md.diff", rc, out, err, el)
    if (TALLY_FIX / "fence-ident-flood.md.diff").exists():
        flood = copy_known("fence-ident-flood.md.diff", TALLY_FIX / "fence-ident-flood.md.diff")
        rc, out, err, el = woof(["--only", "prose"], flood)
        show("./woof --only prose  < fence-ident-flood.md.diff  (openssl sample + 2048 inserts)", rc, out, err, el)
        if os.path.exists(TALLY):
            rc, out, err, el = tally(["--only", "prose", "--chg"], flood)
            show("./tally --only prose --chg  < fence-ident-flood.md.diff", rc, out, err, el)

    if os.path.isdir(os.path.join(SB, ".git")):
        diff77 = git_diff(SB, "77df1da^..77df1da")
        write(FIX / "sitbone-77df1da.diff", diff77.decode("utf-8", errors="replace"))
        rc, out, err, el = woof(["--only", "prose"], diff77)
        show("git diff sitbone 77df1da | woof --only prose", rc, out, err, el, cap=12)
        rc, out, err, el = woof(["--only", "prose", "--emit"], diff77)
        show("git diff sitbone 77df1da | woof --only prose --emit  (class counts)", rc, out, err, el, cap=0)
        # class × path counts
        counts: dict[str, int] = {}
        for ln in out.splitlines()[1:]:
            cols = ln.split("\t")
            if len(cols) >= 4:
                key = f"{cols[0]} {cols[2]} {cols[3]}"
                counts[key] = counts.get(key, 0) + 1
        log("emit counts (path class op):")
        for k, n in sorted(counts.items(), key=lambda kv: (-kv[1], kv[0])):
            log(f"  {n}  {k}")
        if os.path.exists(TALLY):
            rc, out, err, el = tally(["--only", "prose", "--chg"], diff77)
            show("git diff sitbone 77df1da | tally --only prose --chg", rc, out, err, el, cap=10)
        if os.path.exists(WEFT):
            rc, out, err, el = weft(["--only", "docs"], diff77)
            show("git diff sitbone 77df1da | weft --only docs  (Makefile only; README free — DESTROYER_WEFT gold)", rc, out, err, el, cap=6)

    # ------------------------------------------------------------------
    banner("3. hex/hash tokens — ADR SHAs are not one ident")
    save_diff("sha-digit.md.diff", SHA_DIGIT)
    save_diff("sha-mixed-prefix.md.diff", SHA_MIXED_PREFIX)
    save_diff("sha-letter.md.diff", SHA_LETTER)
    save_diff("sha-code-unquoted.diff", SHA_CODE_UNQUOTED)
    save_diff("sha-code-string.diff", SHA_CODE_STRING)
    save_diff("hex-0x.md.diff", HEX_0X)
    rc, out, err, el = woof(["--only", "prose"], SHA_DIGIT)
    show("./woof --only prose  < sha-digit.md.diff  (77df1da → 98a8009)", rc, out, err, el)
    rc, out, err, el = woof(["--only", "prose", "--emit"], SHA_DIGIT)
    show("./woof --only prose --emit  < sha-digit.md.diff", rc, out, err, el)
    rc, out, err, el = woof(["--only", "prose"], SHA_MIXED_PREFIX)
    show("./woof --only prose  < sha-mixed-prefix.md.diff  (557c76f → e9b0f75)", rc, out, err, el)
    rc, out, err, el = woof(["--only", "prose", "--emit"], SHA_MIXED_PREFIX)
    show("./woof --only prose --emit  < sha-mixed-prefix.md.diff", rc, out, err, el)
    rc, out, err, el = woof(["--only", "prose"], SHA_LETTER)
    show("./woof --only prose  < sha-letter.md.diff  (e9b0f75 → ce44c93, letter prefix)", rc, out, err, el)
    rc, out, err, el = woof(["--only", "prose"], SHA_CODE_UNQUOTED)
    show("./woof --only prose  < sha-code-unquoted.diff", rc, out, err, el)
    rc, out, err, el = woof(["--only", "prose", "--emit"], SHA_CODE_UNQUOTED)
    show("./woof --only prose --emit  < sha-code-unquoted.diff", rc, out, err, el)
    rc, out, err, el = woof(["--only", "prose"], SHA_CODE_STRING)
    show("./woof --only prose  < sha-code-string.diff", rc, out, err, el)
    rc, out, err, el = woof(["--only", "prose"], HEX_0X)
    show("./woof --only prose  < hex-0x.md.diff", rc, out, err, el)

    if os.path.isdir(os.path.join(SB, ".git")):
        diff_adr = git_diff(SB, "98a8009^..98a8009")
        write(FIX / "sitbone-98a8009.diff", diff_adr.decode("utf-8", errors="replace"))
        rc, out, err, el = woof(["--only", "prose"], diff_adr)
        show("git diff sitbone 98a8009 | woof --only prose", rc, out, err, el, cap=16)
        if os.path.exists(WEFT):
            rc, out, err, el = weft(["--only", "docs"], diff_adr)
            show("git diff sitbone 98a8009 | weft --only docs  (docs/adr glob)", rc, out, err, el, cap=4)
        if os.path.exists(TALLY):
            rc, out, err, el = tally(["--only", "prose", "--chg"], diff_adr)
            show("git diff sitbone 98a8009 | tally --only prose --chg", rc, out, err, el, cap=10)
    if os.path.isdir(os.path.join(VT, ".git")):
        diff_vt = git_diff(VT, "ce44c93^..ce44c93")
        write(FIX / "voidtrace-ce44c93.diff", diff_vt.decode("utf-8", errors="replace"))
        rc, out, err, el = woof(["--only", "prose"], diff_vt)
        show("git diff voidtrace ce44c93 | woof --only prose", rc, out, err, el, cap=20)
        if os.path.exists(WEFT):
            rc, out, err, el = weft(["--only", "docs"], diff_vt)
            show("git diff voidtrace ce44c93 | weft --only docs", rc, out, err, el, cap=4)

    # ------------------------------------------------------------------
    banner("4. CJK identifiers as text on prose-class paths that are still code")
    save_diff("cjk-mixed.diff", CJK_MIXED)
    save_diff("cjk-fullwidth.diff", CJK_FULLWIDTH)
    save_diff("cjk-comment.diff", CJK_COMMENT)
    save_diff("cjk-indented.md.diff", CJK_INDENTED)
    save_diff("cjk-notes.txt.diff", CJK_TXT)
    save_diff("cjk-changelog.diff", CJK_CHANGELOG)
    save_diff("cjk-fence.md.diff", CJK_FENCE)
    save_diff("indented-ident.md.diff", INDENTED_IDENT)
    save_diff("indented-both.md.diff", INDENTED_BOTH)
    save_diff("rst-codeblock.rst.diff", RST_CODEBLOCK)
    rc, out, err, el = woof(["--only", "prose"], CJK_MIXED)
    show("./woof --only prose  < cjk-mixed.diff  (timeout_秒 → delay_秒)", rc, out, err, el)
    rc, out, err, el = woof(["--only", "prose"], CJK_FULLWIDTH)
    show("./woof --only prose  < cjk-fullwidth.diff  (３０ → ６０)", rc, out, err, el)
    rc, out, err, el = woof(["--only", "prose"], CJK_COMMENT)
    show("./woof --only prose  < cjk-comment.diff", rc, out, err, el)
    rc, out, err, el = woof(["--only", "prose"], CJK_INDENTED)
    show("./woof --only prose  < cjk-indented.md.diff  (indented sample, no fence)", rc, out, err, el)
    rc, out, err, el = woof(["--only", "prose", "--emit"], CJK_INDENTED)
    show("./woof --only prose --emit  < cjk-indented.md.diff", rc, out, err, el)
    rc, out, err, el = woof(["--only", "prose"], CJK_TXT)
    show("./woof --only prose  < cjk-notes.txt.diff  (.txt is prose ext)", rc, out, err, el)
    rc, out, err, el = woof(["--only", "prose"], CJK_CHANGELOG)
    show("./woof --only prose  < cjk-changelog.diff  (CHANGELOG basename is prose)", rc, out, err, el)
    rc, out, err, el = woof(["--only", "prose"], CJK_FENCE)
    show("./woof --only prose  < cjk-fence.md.diff  (rust fence projects CJK as ident)", rc, out, err, el)
    rc, out, err, el = woof(["--only", "prose"], INDENTED_IDENT)
    show("./woof --only prose  < indented-ident.md.diff  (ASCII ident, indented, no fence)", rc, out, err, el)
    rc, out, err, el = woof(["--only", "prose"], INDENTED_BOTH)
    show("./woof --only prose  < indented-both.md.diff", rc, out, err, el)
    rc, out, err, el = woof(["--only", "prose", "--emit"], INDENTED_BOTH)
    show("./woof --only prose --emit  < indented-both.md.diff", rc, out, err, el)
    rc, out, err, el = woof(["--only", "prose"], RST_CODEBLOCK)
    show("./woof --only prose  < rst-codeblock.rst.diff  (RST has no fence projector)", rc, out, err, el)
    rc, out, err, el = woof(["--only", "prose", "--emit"], RST_CODEBLOCK)
    show("./woof --only prose --emit  < rst-codeblock.rst.diff", rc, out, err, el)

    # ------------------------------------------------------------------
    banner("5. binary stdin traceback is rc=1; binary files are skip")
    save_diff("binary-src.diff", BINARY_SRC)
    save_diff("binary-gif.diff", BINARY_GIF)
    save_diff("git-binary-patch.diff", GIT_BINARY_PATCH)
    rc, out, err, el = woof(["--only", "prose"], BINARY_SRC)
    show("./woof --only prose  < Binary files src/secret.bin", rc, out, err, el)
    rc, out, err, el = woof(["--only", "prose"], BINARY_GIF)
    show("./woof --only prose  < Binary files docs/media/demo.gif", rc, out, err, el)
    rc, out, err, el = woof(["--only", "prose"], GIT_BINARY_PATCH)
    show("./woof --only prose  < GIT binary patch src/blob.bin", rc, out, err, el)
    rc, out, err, el = woof(["--only", "prose"], b"\x00\xff")
    show("printf '\\x00\\xff' | woof --only prose", rc, out, err, el)
    with open("/dev/urandom", "rb") as ur:
        rnd = ur.read(32)
    rc, out, err, el = woof(["--only", "prose"], rnd)
    show("/dev/urandom | head -c 32 | woof --only prose", rc, out, err, el, cap=4)
    tmp = FIX / "binary-stdin.diff"
    tmp.write_bytes(b"\x00\xff")
    rc, out, err, el = woof(["--only", "prose", str(tmp)])
    show("./woof --only prose  binary-stdin.diff  (file input errors=replace)", rc, out, err, el)
    nul = b"""diff --git a/src.rs b/src.rs
--- a/src.rs
+++ b/src.rs
@@ -1 +1 @@
-let x = 1;
+let x = 2;\x00secret;
"""
    rc, out, err, el = woof(["--only", "prose"], nul)
    show("./woof --only prose  < hunk with NUL after 2", rc, out, err, el)

    # ------------------------------------------------------------------
    banner("6. rename / mode occupancy of nothing")
    save_diff("rename-only.diff", RENAME_ONLY)
    save_diff("mode-only.diff", MODE_ONLY)
    save_diff("empty-add.diff", EMPTY_ADD)
    rc, out, err, el = woof(["--only", "prose"], RENAME_ONLY)
    show("./woof --only prose  < git mv src/foo.rs src/bar.rs (100% rename)", rc, out, err, el)
    rc, out, err, el = woof(["--only", "prose"], MODE_ONLY)
    show("./woof --only prose  < chmod +x src/run.sh", rc, out, err, el)
    rc, out, err, el = woof(["--only", "prose"], EMPTY_ADD)
    show("./woof --only prose  < add empty notes.txt", rc, out, err, el)
    rc, out, err, el = woof(["--only", "prose"], "")
    show("printf '' | woof --only prose", rc, out, err, el)
    rc, out, err, el = woof(["--only", "prose"], "\n")
    show("printf '\\n' | woof --only prose", rc, out, err, el)
    rc, out, err, el = woof(["--only", "prose"], "this is not a diff\nhello 30\n")
    show("./woof --only prose  < garbage non-diff", rc, out, err, el)

    # ------------------------------------------------------------------
    banner("7. fence/body pairing, inline ticks, untitled fence, HTML comments")
    save_diff("fence-body-swap.md.diff", FENCE_BODY_SWAP)
    save_diff("inline-tick-number.md.diff", INLINE_TICK_NUMBER)
    save_diff("untitled-fence.md.diff", UNTITLED_FENCE)
    save_diff("html-comment.md.diff", HTML_COMMENT_MD)
    save_diff("html-comment.rs.diff", HTML_COMMENT_RS)
    rc, out, err, el = woof(["--only", "prose"], FENCE_BODY_SWAP)
    show("./woof --only prose  < fence-body-swap.md.diff  (body 60↔30 with fence 30↔60)", rc, out, err, el)
    rc, out, err, el = woof(["--only", "prose", "--emit"], FENCE_BODY_SWAP)
    show("./woof --only prose --emit  < fence-body-swap.md.diff", rc, out, err, el)
    if os.path.exists(TALLY):
        rc, out, err, el = tally(["--only", "prose", "--chg"], FENCE_BODY_SWAP)
        show("./tally --only prose --chg  < fence-body-swap.md.diff", rc, out, err, el)
        rc, out, err, el = tally(["--only", "prose", "--chg", "--emit"], FENCE_BODY_SWAP)
        show("./tally --only prose --chg --emit  < fence-body-swap.md.diff", rc, out, err, el)
    rc, out, err, el = woof(["--only", "prose"], INLINE_TICK_NUMBER)
    show("./woof --only prose  < inline-tick-number.md.diff  (`30` → `60`)", rc, out, err, el)
    rc, out, err, el = woof(["--only", "prose"], UNTITLED_FENCE)
    show("./woof --only prose  < untitled-fence.md.diff", rc, out, err, el)
    rc, out, err, el = woof(["--only", "prose"], HTML_COMMENT_MD)
    show("./woof --only prose  < html-comment.md.diff", rc, out, err, el)
    rc, out, err, el = woof(["--only", "prose"], HTML_COMMENT_RS)
    show("./woof --only prose  < html-comment.rs.diff", rc, out, err, el)

    # ------------------------------------------------------------------
    banner("8. lockfile skip, moves, kizu string version")
    save_diff("lock-only.diff", LOCK_ONLY)
    save_diff("move-ident.diff", MOVE_IDENT)
    rc, out, err, el = woof(["--only", "prose"], LOCK_ONLY)
    show("./woof --only prose  < Cargo.lock 0.6.0→0.7.0", rc, out, err, el)
    rc, out, err, el = woof(["--only", "prose"], MOVE_IDENT)
    show("./woof --only prose  < move fetch_user + insert other", rc, out, err, el)
    if os.path.isdir(os.path.join(KZ, ".git")):
        try:
            diff_kz = git_diff(KZ, "9349dc5^..9349dc5")
            write(FIX / "kizu-9349dc5.diff", diff_kz.decode("utf-8", errors="replace"))
            rc, out, err, el = woof(["--only", "prose"], diff_kz)
            show("git diff kizu 9349dc5 | woof --only prose", rc, out, err, el, cap=8)
        except subprocess.CalledProcessError as e:
            log(f"kizu 9349dc5 unavailable: {e}")

    # ------------------------------------------------------------------
    banner("9. selftest still green; do not rewrite woof")
    rc, out, err, el = woof(["--selftest"])
    show("./woof --selftest  (after attacks; victim untouched)", rc, out, err, el)

    LOG.write_text("\n".join(transcript) + "\n", encoding="utf-8")
    log()
    log(f"wrote {LOG}")
    log(f"fixtures {FIX}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
