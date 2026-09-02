#!/usr/bin/env python3
"""Host-execute Honor-KILL + leftover attacks against tagjoin mutate-3."""

from __future__ import annotations

import os
import subprocess
import sys
import tempfile
from pathlib import Path

ROOT = Path("/Users/annenpolka/ghq/github.com/annenpolka/brrr/lab-runs/specimen-hdd-20260902-1112")
CLI = ROOT / "lineages/candidate-tagjoin/tagjoin"
FX = ROOT / "lineages/candidate-tagjoin/fixtures"
TR = ROOT / "destroyers/_tagjoin_transfer_scratch"
SCRATCH = ROOT / "destroyers/_tagjoin3_scratch"
S052 = ROOT / "specimens/specimen-052"
PY = sys.executable

os.environ.setdefault("PATH", "/usr/bin:/bin:/usr/sbin:/sbin:/opt/homebrew/bin")


def run_cli(args, stdin=None, timeout=120):
    proc = subprocess.run(
        [PY, str(CLI), *args],
        check=False,
        capture_output=True,
        text=True,
        input=stdin,
        timeout=timeout,
    )
    return proc


def parse_rows(text: str) -> dict[str, list[list[str]]]:
    rows: dict[str, list[list[str]]] = {}
    for line in text.splitlines():
        if not line or "\t" not in line:
            continue
        name, *rest = line.split("\t")
        rows.setdefault(name, []).append(rest)
    return rows


def quals(rows, kind: str) -> list[str]:
    return [row[0] for row in rows.get(kind, [])]


def first(rows, kind: str, default="0") -> str:
    return rows.get(kind, [[default]])[0][0]


def summarize(name: str, proc) -> dict:
    rows = parse_rows(proc.stdout)
    rec = {
        "name": name,
        "rc": proc.returncode,
        "disagree": quals(rows, "disagree"),
        "agree": quals(rows, "agree"),
        "missing": quals(rows, "missing"),
        "collision": quals(rows, "collision"),
        "unparsed": quals(rows, "unparsed"),
        "join": quals(rows, "join"),
        "disagree_n": first(rows, "disagree_n"),
        "agree_n": first(rows, "agree_n"),
        "missing_n": first(rows, "missing_n"),
        "collision_n": first(rows, "collision_n"),
        "unparsed_n": first(rows, "unparsed_n"),
        "other_omitempty": rows.get("other_omitempty", [["-"]])[0],
        "stderr": (proc.stderr or "")[:400],
        "stdout_head": "\n".join(proc.stdout.splitlines()[:12]),
        "n_lines": len(proc.stdout.splitlines()),
        "n_tabs_first_join": (
            proc.stdout.splitlines()[0].count("\t") if proc.stdout.splitlines() else 0
        ),
    }
    return rec


def banner(title: str) -> None:
    print("\n" + "=" * 72)
    print(title)
    print("=" * 72)


def show(rec: dict, extra: str = "") -> None:
    print(
        f"{rec['name']}\trc={rec['rc']}\tdisagree_n={rec['disagree_n']}\t"
        f"agree_n={rec['agree_n']}\tmissing_n={rec['missing_n']}\t"
        f"collision_n={rec['collision_n']}\tunparsed_n={rec['unparsed_n']}"
    )
    if rec["unparsed"]:
        print("  unparsed", rec["unparsed"])
    if rec["join"]:
        print("  join", rec["join"])
    if rec["disagree"]:
        shown = rec["disagree"][:24]
        print("  disagree", shown, "..." if len(rec["disagree"]) > 24 else "")
    if rec["agree"]:
        shown = rec["agree"][:24]
        print("  agree", shown, "..." if len(rec["agree"]) > 24 else "")
    if rec["missing"]:
        print("  missing", rec["missing"][:12])
    if rec["collision"]:
        print("  collision", rec["collision"][:8])
    print("  other_omitempty", rec["other_omitempty"][:6])
    if rec["stderr"]:
        print("  STDERR", rec["stderr"].rstrip())
    if extra:
        print(extra)


def write_case(name: str, text: str) -> Path:
    path = SCRATCH / "cases" / name
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")
    return path


def main() -> int:
    SCRATCH.mkdir(parents=True, exist_ok=True)
    (SCRATCH / "cases").mkdir(exist_ok=True)
    (SCRATCH / "transfer").mkdir(exist_ok=True)

    banner("HONOR-KILL 1: TRANSFER CRDs must not restore unparsed")
    transfer_files = [
        ("crossplane", TR / "kubernetes.crossplane.io_objects.yaml"),
        ("pixie", TR / "px.dev_viziers.yaml"),
        ("servicemonitor", TR / "monitoring.coreos.com_servicemonitors.yaml"),
        ("httproute", TR / "gateway.networking.k8s.io_httproutes.yaml"),
        ("certmanager", TR / "cert-manager.io_certificates.yaml"),
        ("openapi", TR / "apis__apps__v1_openapi.json"),
        ("k8s-types", TR / "k8s-core-v1-types.go"),
        ("argo", TR / "argoproj.io_applications.yaml"),
    ]
    transfer_recs = []
    for name, path in transfer_files:
        proc = run_cli([str(path)], timeout=180)
        rec = summarize(name, proc)
        transfer_recs.append(rec)
        (SCRATCH / "transfer" / f"{name}.out").write_text(proc.stdout)
        (SCRATCH / "transfer" / f"{name}.err").write_text(proc.stderr or "")
        (SCRATCH / "transfer" / f"{name}.rc").write_text(str(proc.returncode))
        extra = ""
        if path.exists():
            text = path.read_text(encoding="utf-8", errors="replace")
            extra = (
                f"  bytes={path.stat().st_size} "
                f"list-map-keys={text.count('x-kubernetes-list-map-keys')} "
                f"listMapKey={text.count('+listMapKey')}"
            )
        show(rec, extra)

    banner("HONOR-KILL 2: Go-name case-fold restored?")
    case_fold = """
type Spec struct {
	// +listMapKey=IP
	HostAliases []HostAlias `json:"hostAliases"`
}
type HostAlias struct {
	IP string `json:"ip,omitempty"`
}
"""
    proc = run_cli(["-"], stdin=case_fold)
    rec = summarize("listMapKey=IP vs json:ip", proc)
    show(rec)
    print("  stdout:\n" + proc.stdout)

    case_fold2 = """
type Spec struct {
	// +listMapKey=ip
	HostAliases []HostAlias `json:"hostAliases"`
}
type HostAlias struct {
	IP string `json:"IP,omitempty"`
}
"""
    proc = run_cli(["-"], stdin=case_fold2)
    rec = summarize("listMapKey=ip vs json:IP", proc)
    show(rec)
    print("  stdout:\n" + proc.stdout)

    untagged = """
type Spec struct {
	// +listMapKey=name
	Items []Item `json:"items"`
}
type Item struct {
	Name string
}
"""
    proc = run_cli(["-"], stdin=untagged)
    rec = summarize("untagged Name vs listMapKey=name", proc)
    show(rec)
    print("  stdout:\n" + proc.stdout)

    address = """
type Spec struct {
	// +listMapKey=ip
	HostAliases []HostAlias `json:"hostAliases"`
}
type HostAlias struct {
	IP string `json:"address,omitempty"`
}
"""
    proc = run_cli(["-"], stdin=address)
    rec = summarize("listMapKey=ip vs json:address field IP", proc)
    show(rec)

    sibling = """
type Spec struct {
	// +listMapKey=IP
	HostAliases []HostAlias `json:"hostAliases"`
}
type HostAlias struct {
	Addr string `json:"address"`
	IP string `json:"ip,omitempty"`
}
"""
    proc = run_cli(["-"], stdin=sibling)
    rec = summarize("listMapKey=IP vs sibling json:ip", proc)
    show(rec)

    banner("HONOR-KILL 3: FILE.go FILE.yaml disagree_n drop?")
    proc = run_cli([str(FX / "052-types.go"), str(FX / "crd-list-map.yaml")])
    rec = summarize("go then yaml", proc)
    show(rec)
    print("  stdout:\n" + proc.stdout)
    proc = run_cli([str(FX / "crd-list-map.yaml"), str(FX / "052-types.go")])
    rec = summarize("yaml then go", proc)
    show(rec)
    blob = (FX / "052-types.go").read_text() + "\n" + (FX / "crd-list-map.yaml").read_text()
    proc = run_cli(["-"], stdin=blob)
    rec = summarize("concat blob stdin", proc)
    show(rec)
    print("  stdout:\n" + proc.stdout)

    banner("HONOR-KILL 4: THIN_WRAPPER of grep HostAlias table?")
    grep = subprocess.run(
        ["grep", "-nE", r"omitempty|listMapKey|\+optional", str(FX / "052-types.go")],
        check=False,
        capture_output=True,
        text=True,
    )
    print("grep hits:")
    print(grep.stdout)
    proc = run_cli([str(FX / "052-types.go")])
    rec = summarize("owned 052", proc)
    show(rec)
    proc = run_cli([str(S052 / "files/types_excerpt.go")])
    rec = summarize("specimen-052 excerpt", proc)
    show(rec)
    proc = run_cli([str(FX / "unseen-ports.go")])
    rec = summarize("unseen ports", proc)
    show(rec)
    proc = run_cli([str(FX / "agree-name.go")])
    rec = summarize("agree-name", proc)
    show(rec)

    banner("REMAINING: YAML anchors / aliases")
    alias_required = """
hostAliases:
  type: array
  x-kubernetes-list-map-keys: &keys
    - ip
  items:
    required: *keys
    properties:
      ip:
        type: string
"""
    proc = run_cli(["-"], stdin=alias_required)
    rec = summarize("alias required: *keys", proc)
    show(rec)
    print("  stdout:\n" + proc.stdout)

    merge_key = """
defs:
  listmap: &lm
    x-kubernetes-list-map-keys:
      - ip
    items:
      required:
        - ip
      properties:
        ip:
          type: string
hostAliases:
  type: array
  <<: *lm
"""
    proc = run_cli(["-"], stdin=merge_key)
    rec = summarize("merge key <<: *lm", proc)
    show(rec)
    print("  stdout:\n" + proc.stdout)

    alias_whole = """
hostAliases: &ha
  type: array
  x-kubernetes-list-map-keys:
    - ip
  items:
    required:
      - ip
    properties:
      ip:
        type: string
podIPs: *ha
"""
    proc = run_cli(["-"], stdin=alias_whole)
    rec = summarize("alias whole node *ha", proc)
    show(rec)
    print("  stdout:\n" + proc.stdout)

    tagged = """
hostAliases:
  type: array
  x-kubernetes-list-map-keys: !!seq
    - ip
  items:
    required:
      - ip
    properties:
      ip:
        type: string
"""
    proc = run_cli(["-"], stdin=tagged)
    rec = summarize("yaml tag !!seq", proc)
    show(rec)
    print("  stdout:\n" + proc.stdout)

    banner("REMAINING: Go vs YAML separate rows")
    proc = run_cli([str(FX / "052-types.go"), str(FX / "crd-list-map.yaml")])
    rec = summarize("separate rows go+yaml", proc)
    print("  rows:")
    for line in proc.stdout.splitlines():
        if line.startswith(("disagree", "agree", "missing")) and "\t" in line:
            print("   ", line.split("\t")[0], line.split("\t")[1])

    banner("REMAINING: duplicate list-map collapse")
    dup_yaml = """
spec:
  a:
    hostAliases:
      type: array
      x-kubernetes-list-map-keys: [ip]
      items:
        properties:
          ip: {type: string}
  b:
    hostAliases:
      type: array
      x-kubernetes-list-map-keys: [ip]
      items:
        required: [ip]
        properties:
          ip: {type: string}
"""
    proc = run_cli(["-"], stdin=dup_yaml)
    rec = summarize("dup hostAliases.ip optional then required", proc)
    show(rec)
    print("  stdout:\n" + proc.stdout)

    httproute_hits = (TR / "gateway.networking.k8s.io_httproutes.yaml").read_text().count(
        "x-kubernetes-list-map-keys"
    )
    httproute_out = (SCRATCH / "transfer/httproute.out").read_text()
    hrows = parse_rows(httproute_out)
    print(
        f"  HTTPRoute file hits={httproute_hits} "
        f"cli_rows={len(hrows.get('agree', []))+len(hrows.get('disagree', []))} "
        f"agree_n={first(hrows,'agree_n')} disagree_n={first(hrows,'disagree_n')}"
    )

    banner("REMAINING: protobuf opt is not a verdict")
    proto = """
type Spec struct {
	// +listMapKey=name
	Items []Item `json:"items"`
}
type Item struct {
	Name string `json:"name" protobuf:"bytes,1,opt,name=name"`
}
"""
    proc = run_cli(["-"], stdin=proto)
    rec = summarize("protobuf opt required json", proc)
    show(rec)
    print("  stdout:\n" + proc.stdout)

    banner("REMAINING: tabs inside json tags")
    tab_tag = (
        "type Spec struct {\n"
        "\t// +listMapKey=name\n"
        "\tItems []Item `json:\"items\"`\n"
        "}\n"
        "type Item struct {\n"
        '\tName string `json:"na\tme,omitempty"`\n'
        "}\n"
    )
    proc = run_cli(["-"], stdin=tab_tag)
    rec = summarize("tab in json name", proc)
    show(rec)
    print("  first line tabs", rec["n_tabs_first_join"])
    print("  stdout repr:", repr(proc.stdout))

    tab_as_key = (
        "type Spec struct {\n"
        "\t// +listMapKey=name\n"
        "\tItems []Item `json:\"items\"`\n"
        "}\n"
        "type Item struct {\n"
        '\tName string `json:"name,omitempty"`\n'
        "}\n"
    )
    # tab only as field indent, key is name
    proc = run_cli(["-"], stdin=tab_as_key)
    rec = summarize("tabs as go indent only", proc)
    show(rec)

    banner("REMAINING: rc=0 without --check still includes disagree")
    proc = run_cli([str(FX / "052-types.go")])
    rec = summarize("owned without --check", proc)
    show(rec)
    proc = run_cli(["--check", str(FX / "052-types.go")])
    rec = summarize("owned with --check", proc)
    show(rec)

    banner("EXTRA: folded scalars, flow maps, JSON-in-YAML, BOM YAML")
    folded = """
hostAliases:
  description: >
    wrapped
    prose
  type: array
  x-kubernetes-list-map-keys:
    - ip
  items:
    properties:
      ip:
        type: string
"""
    proc = run_cli(["-"], stdin=folded)
    rec = summarize("folded > scalar then keys", proc)
    show(rec)

    flow = """
hostAliases: {type: array, x-kubernetes-list-map-keys: [ip], items: {properties: {ip: {type: string}}}}
"""
    proc = run_cli(["-"], stdin=flow)
    rec = summarize("flow mapping", proc)
    show(rec)
    print("  stdout:\n" + proc.stdout)

    json_in_yaml = """
apiVersion: apiextensions.k8s.io/v1
kind: CustomResourceDefinition
spec:
  versions:
  - name: v1
    schema:
      openAPIV3Schema:
        properties:
          hostAliases:
            type: array
            x-kubernetes-list-map-keys: ["ip"]
            items:
              properties:
                ip:
                  type: string
"""
    proc = run_cli(["-"], stdin=json_in_yaml)
    rec = summarize("quoted ip in yaml array", proc)
    show(rec)

    block_plain = """
conditions:
  description: |
    line1
    line2
  type: array
  x-kubernetes-list-map-keys:
    - type
  items:
    required:
      - type
    properties:
      type:
        type: string
"""
    proc = run_cli(["-"], stdin=block_plain)
    rec = summarize("description | (no dash)", proc)
    show(rec)

    banner("EXTRA: concat vs multi-file; patchMergeKey only; json comma omitempty")
    proc = run_cli(["-"], stdin='// +listMapKey=name\n')
    rec = summarize("listMapKey prose only", proc)
    show(rec)

    patch_only = """
type Spec struct {
	// +patchMergeKey=ip
	HostAliases []HostAlias `json:"hostAliases"`
}
type HostAlias struct {
	IP string `json:"ip,omitempty"`
}
"""
    proc = run_cli(["-"], stdin=patch_only)
    rec = summarize("patchMergeKey only", proc)
    show(rec)

    empty_json = """
type Spec struct {
	// +listMapKey=Name
	Items []Item `json:"items"`
}
type Item struct {
	Name string `json:",omitempty"`
}
"""
    proc = run_cli(["-"], stdin=empty_json)
    rec = summarize("json comma omitempty listMapKey=Name", proc)
    show(rec)
    print("  stdout:\n" + proc.stdout)

    empty_json_name = """
type Spec struct {
	// +listMapKey=name
	Items []Item `json:"items"`
}
type Item struct {
	Name string `json:",omitempty"`
}
"""
    proc = run_cli(["-"], stdin=empty_json_name)
    rec = summarize("json comma omitempty listMapKey=name", proc)
    show(rec)

    banner("EXTRA: CRD versions with description |- before keys (TRANSFER shape)")
    versions_block = """
apiVersion: apiextensions.k8s.io/v1
kind: CustomResourceDefinition
spec:
  versions:
  - name: v1
    schema:
      openAPIV3Schema:
        properties:
          conditions:
            description: |-
              wrapped
              prose that used to break the walker
            type: array
            x-kubernetes-list-map-keys:
            - type
            items:
              required:
              - type
              properties:
                type:
                  type: string
"""
    proc = run_cli(["-"], stdin=versions_block)
    rec = summarize("versions + description |-", proc)
    show(rec)
    print("  stdout:\n" + proc.stdout)

    banner("EXTRA: JSON OpenAPI $ref external / allOf")
    ext_ref = """
{
  "hostAliases": {
    "type": "array",
    "x-kubernetes-list-map-keys": ["ip"],
    "items": {"$ref": "https://example.com/schemas/hostalias"}
  }
}
"""
    proc = run_cli(["-"], stdin=ext_ref)
    rec = summarize("external $ref", proc)
    show(rec)
    print("  stdout:\n" + proc.stdout)

    banner("EXTRA: huge 400 pairs timing")
    parts = []
    for i in range(400):
        parts.append(
            f"type L{i} struct {{\n"
            f"\t// +listMapKey=name\n"
            f'\tItems []E{i} `json:"items,omitempty"`\n'
            f"}}\n"
            f"type E{i} struct {{\n"
            f'\tName string `json:"name,omitempty"`\n'
            f"}}\n"
        )
    proc = run_cli(["-"], stdin="\n".join(parts), timeout=30)
    rec = summarize("400 pairs", proc)
    show(rec)

    banner("GREP vs CLI join on owned fixture")
    print("grep does not print verdict/qual of identity-only optional keys.")
    print("CLI disagrees:", rec)  # placeholder overwritten below
    proc = run_cli([str(FX / "052-types.go")])
    print(proc.stdout)

    # write machine summary
    kill1 = any(
        r["name"] in {"crossplane", "pixie", "servicemonitor"} and (
            r["unparsed_n"] != "0" or "unparsed" in r["unparsed"] or r["rc"] == 2 and not r["agree"]
        )
        for r in transfer_recs
    )
    print("\n\nKILL1_TRANSFER_UNPARSED", kill1)
    for r in transfer_recs:
        if r["name"] in {"crossplane", "pixie", "servicemonitor", "openapi", "httproute", "certmanager"}:
            print(
                " ",
                r["name"],
                "unparsed_n",
                r["unparsed_n"],
                "agree_n",
                r["agree_n"],
                "disagree_n",
                r["disagree_n"],
                "rc",
                r["rc"],
            )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
