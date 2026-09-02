#!/usr/bin/env python3
"""Host-execute Honor-KILL + leftover-identity attacks against tagjoin mutate-3 (pass 4)."""

from __future__ import annotations

import importlib.machinery
import importlib.util
import json
import os
import subprocess
import sys
from collections import defaultdict
from pathlib import Path

ROOT = Path("/Users/annenpolka/ghq/github.com/annenpolka/brrr/lab-runs/specimen-hdd-20260902-1112")
CLI = ROOT / "lineages/candidate-tagjoin/tagjoin"
FX = ROOT / "lineages/candidate-tagjoin/fixtures"
TR = ROOT / "destroyers/_tagjoin_transfer_scratch"
SCRATCH = ROOT / "destroyers/_tagjoin4_scratch"
S052 = ROOT / "specimens/specimen-052"
PY = sys.executable

os.environ.setdefault("PATH", "/usr/bin:/bin:/usr/sbin:/sbin:/opt/homebrew/bin")


def load_mod():
    loader = importlib.machinery.SourceFileLoader("tagjoin_cli4", str(CLI))
    spec = importlib.util.spec_from_loader(loader.name, loader)
    assert spec is not None
    mod = importlib.util.module_from_spec(spec)
    sys.modules[loader.name] = mod
    loader.exec_module(mod)
    return mod


TJ = load_mod()


def run_cli(args, stdin=None, timeout=180):
    return subprocess.run(
        [PY, str(CLI), *args],
        check=False,
        capture_output=True,
        text=True,
        input=stdin,
        timeout=timeout,
    )


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
        "stdout_head": "\n".join(proc.stdout.splitlines()[:16]),
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


def yaml_node(list_name: str, key: str, *, required: bool, default: bool = False) -> str:
    req = f"      required:\n      - {key}\n" if required else ""
    default_line = "          default: x\n" if default else ""
    return (
        f"{list_name}:\n"
        f"  type: array\n"
        f"  x-kubernetes-list-map-keys:\n"
        f"  - {key}\n"
        f"  items:\n"
        f"{req}"
        f"    properties:\n"
        f"      {key}:\n"
        f"        type: string\n"
        f"{default_line}"
    )


def collect_yaml_optionality(text: str) -> dict[tuple[str, str], list[str]]:
    """Honesty: every (list_name, key) verdict the walker sees, no first-wins."""
    tree = TJ.load_schema_tree(text)
    found: dict[tuple[str, str], list[str]] = defaultdict(list)
    if tree is None:
        return found
    for path, node in TJ._walk_yaml(tree):
        if not isinstance(node, dict):
            continue
        raw_keys = node.get("x-kubernetes-list-map-keys")
        if raw_keys is None:
            continue
        keys = TJ._as_list(raw_keys)
        if not keys:
            continue
        list_name = TJ._path_list_name(path)
        for key in keys:
            join = TJ._join_from_yaml_node(list_name, key, node, tree)
            if join is None:
                found[(list_name, key)].append("unresolved")
            else:
                found[(list_name, key)].append(join.verdict)
    return found


def main() -> int:
    SCRATCH.mkdir(parents=True, exist_ok=True)
    (SCRATCH / "cases").mkdir(exist_ok=True)
    (SCRATCH / "transfer").mkdir(exist_ok=True)
    kill_flags: dict[str, bool] = {}
    leftover_lies: list[str] = []

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

    kill_flags["transfer_unparsed"] = any(
        r["name"] in {"crossplane", "pixie", "servicemonitor"}
        and (r["unparsed_n"] != "0" or r["unparsed"] or (r["rc"] == 2 and not r["agree"]))
        for r in transfer_recs
    )
    print("KILL1_TRANSFER_UNPARSED", kill_flags["transfer_unparsed"])

    banner("HONOR-KILL 2: Go-name case-fold restored?")
    cases_fold = {
        "listMapKey=IP vs json:ip": """
type Spec struct {
	// +listMapKey=IP
	HostAliases []HostAlias `json:"hostAliases"`
}
type HostAlias struct {
	IP string `json:"ip,omitempty"`
}
""",
        "listMapKey=ip vs json:IP": """
type Spec struct {
	// +listMapKey=ip
	HostAliases []HostAlias `json:"hostAliases"`
}
type HostAlias struct {
	IP string `json:"IP,omitempty"`
}
""",
        "untagged Name vs listMapKey=name": """
type Spec struct {
	// +listMapKey=name
	Items []Item `json:"items"`
}
type Item struct {
	Name string
}
""",
        "listMapKey=ip vs json:address field IP": """
type Spec struct {
	// +listMapKey=ip
	HostAliases []HostAlias `json:"hostAliases"`
}
type HostAlias struct {
	IP string `json:"address,omitempty"`
}
""",
        "listMapKey=IP vs sibling json:ip": """
type Spec struct {
	// +listMapKey=IP
	HostAliases []HostAlias `json:"hostAliases"`
}
type HostAlias struct {
	Addr string `json:"address"`
	IP string `json:"ip,omitempty"`
}
""",
    }
    fold_kill = False
    for name, text in cases_fold.items():
        write_case(name.replace(" ", "_").replace(":", "_") + ".go", text)
        proc = run_cli(["-"], stdin=text)
        rec = summarize(name, proc)
        show(rec)
        print("  stdout:\n" + proc.stdout)
        if rec["disagree"] and any("HostAlias.IP" in d or d.endswith(".IP") for d in rec["disagree"]):
            if "json:ip" in name or "json:IP" in name or "address" in name or "sibling" in name:
                fold_kill = True
        if name.startswith("listMapKey=IP vs json:ip") and "HostAlias.IP" in rec["disagree"]:
            fold_kill = True
        if name.startswith("listMapKey=ip vs json:IP") and "HostAlias.ip" in rec["disagree"]:
            fold_kill = True
    kill_flags["case_fold"] = fold_kill
    print("KILL2_CASE_FOLD", fold_kill)

    banner("HONOR-KILL 3: FILE.go FILE.yaml disagree_n drop?")
    proc = run_cli([str(FX / "052-types.go"), str(FX / "crd-list-map.yaml")])
    rec = summarize("go then yaml", proc)
    show(rec)
    print("  stdout:\n" + proc.stdout)
    go_yaml_n = rec["disagree_n"]
    proc = run_cli([str(FX / "crd-list-map.yaml"), str(FX / "052-types.go")])
    rec = summarize("yaml then go", proc)
    show(rec)
    yaml_go_n = rec["disagree_n"]
    blob = (FX / "052-types.go").read_text() + "\n" + (FX / "crd-list-map.yaml").read_text()
    proc = run_cli(["-"], stdin=blob)
    rec = summarize("concat blob stdin", proc)
    show(rec)
    print("  stdout:\n" + proc.stdout)
    concat_n = rec["disagree_n"]
    proc = run_cli(["--check", str(FX / "052-types.go"), str(FX / "crd-list-map.yaml")])
    rec = summarize("check go yaml", proc)
    show(rec)
    kill_flags["silent_disagree_n2"] = {go_yaml_n, yaml_go_n, concat_n} == {"2"} or (
        go_yaml_n == "2" or yaml_go_n == "2"
    )
    # Honor KILL if silent disagree_n 2 (YAML half dropped). Honest is 4.
    print("KILL3_SILENT_DISAGREE_N2", kill_flags["silent_disagree_n2"], "ns", go_yaml_n, yaml_go_n, concat_n)

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
    owned_names = rec["disagree"]
    proc = run_cli([str(S052 / "files/types_excerpt.go")])
    rec = summarize("specimen-052 excerpt", proc)
    show(rec)
    proc = run_cli([str(FX / "unseen-ports.go")])
    rec = summarize("unseen ports", proc)
    show(rec)
    unseen = rec["disagree"]
    proc = run_cli([str(FX / "agree-name.go")])
    rec = summarize("agree-name", proc)
    show(rec)
    thin = not (
        "LocalObjectReference.Name" in owned_names
        and "HostAlias.IP" in owned_names
        and any("ContainerPort" in d or "containerPort" in d for d in unseen)
    )
    kill_flags["thin_wrapper"] = thin
    print("KILL4_THIN_WRAPPER", thin)
    print("  owned disagree", owned_names)
    print("  unseen disagree", unseen)

    banner("LEFTOVER: mixed optionality first-wins (indent subset CAN cut this)")
    opt_then_req = (
        "spec:\n  a:\n"
        + "\n".join("    " + ln if ln else ln for ln in yaml_node("hostAliases", "ip", required=False).splitlines())
        + "\n  b:\n"
        + "\n".join("    " + ln if ln else ln for ln in yaml_node("hostAliases", "ip", required=True).splitlines())
    )
    write_case("opt_then_req.yaml", opt_then_req)
    proc = run_cli(["-"], stdin=opt_then_req)
    rec = summarize("opt then required hostAliases.ip", proc)
    show(rec)
    print("  stdout:\n" + proc.stdout)
    honesty = collect_yaml_optionality(opt_then_req)
    print("  honesty", dict(honesty))

    req_then_opt = (
        "spec:\n  a:\n"
        + "\n".join("    " + ln if ln else ln for ln in yaml_node("hostAliases", "ip", required=True).splitlines())
        + "\n  b:\n"
        + "\n".join("    " + ln if ln else ln for ln in yaml_node("hostAliases", "ip", required=False).splitlines())
    )
    write_case("req_then_opt.yaml", req_then_opt)
    proc = run_cli(["-"], stdin=req_then_opt)
    rec = summarize("required then opt hostAliases.ip", proc)
    show(rec)
    print("  stdout:\n" + proc.stdout)
    honesty2 = collect_yaml_optionality(req_then_opt)
    print("  honesty", dict(honesty2))
    req_then_opt_agree_hides = rec["agree_n"] == "1" and rec["disagree_n"] == "0"
    print("REQ_THEN_OPT_AGREE_HIDES_DISAGREE", req_then_opt_agree_hides)
    if req_then_opt_agree_hides:
        leftover_lies.append(
            "required-then-optional first-wins agree hides later disagree hostAliases.ip"
        )

    versions_mixed = """
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
            x-kubernetes-list-map-keys:
            - ip
            items:
              required:
              - ip
              properties:
                ip:
                  type: string
  - name: v2
    schema:
      openAPIV3Schema:
        properties:
          hostAliases:
            type: array
            x-kubernetes-list-map-keys:
            - ip
            items:
              properties:
                ip:
                  type: string
"""
    write_case("versions_mixed.yaml", versions_mixed)
    proc = run_cli(["-"], stdin=versions_mixed)
    rec = summarize("versions v1 required v2 optional", proc)
    show(rec)
    print("  stdout:\n" + proc.stdout)
    print("  honesty", dict(collect_yaml_optionality(versions_mixed)))
    if rec["agree_n"] == "1" and rec["disagree_n"] == "0":
        leftover_lies.append("versions mixed optionality first-wins agree hides v2 disagree")

    banner("LEFTOVER: TRANSFER files mixed optionality audit (honesty vs CLI)")
    mixed_real = []
    for name, path in transfer_files:
        if not path.exists():
            continue
        text = path.read_text(encoding="utf-8", errors="replace")
        if "x-kubernetes-list-map-keys" not in text and "+listMapKey" not in text:
            continue
        honesty = collect_yaml_optionality(text) if path.suffix in {".yaml", ".json"} else {}
        mixed = {k: v for k, v in honesty.items() if len(set(v)) > 1}
        counts = {k: (v.count("agree"), v.count("disagree"), len(v)) for k, v in honesty.items() if len(v) > 1}
        print(f"  {name} unique_keys={len(honesty)} mixed={len(mixed)} dup_same={len(counts)}")
        if mixed:
            print("    MIXED", {str(k): v for k, v in list(mixed.items())[:12]})
            mixed_real.append((name, mixed))
        if counts and not mixed:
            sample = list(counts.items())[:6]
            print("    DUP_SAME", [(str(k), c) for k, c in sample])
    print("REAL_MIXED_OPTIONALITY_FILES", [m[0] for m in mixed_real])
    if mixed_real:
        leftover_lies.append(f"real TRANSFER mixed optionality: {[m[0] for m in mixed_real]}")

    banner("LEFTOVER: anchors / aliases / tag types (full YAML parser)")
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
    write_case("alias_required.yaml", alias_required)
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
    write_case("merge_key.yaml", merge_key)
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
    write_case("alias_whole.yaml", alias_whole)
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
    write_case("tagged_seq.yaml", tagged)
    proc = run_cli(["-"], stdin=tagged)
    rec = summarize("yaml tag !!seq", proc)
    show(rec)
    print("  stdout:\n" + proc.stdout)

    flow = """
hostAliases: {type: array, x-kubernetes-list-map-keys: [ip], items: {properties: {ip: {type: string}}}}
"""
    write_case("flow.yaml", flow)
    proc = run_cli(["-"], stdin=flow)
    rec = summarize("flow mapping", proc)
    show(rec)
    print("  stdout:\n" + proc.stdout)

    banner("LEFTOVER: indent subset SHOULD still join (not a parser growth)")
    quoted = """
"hostAliases":
  type: array
  x-kubernetes-list-map-keys: ["ip"]
  items:
    properties:
      ip:
        type: string
"""
    write_case("quoted.yaml", quoted)
    proc = run_cli(["-"], stdin=quoted)
    rec = summarize("quoted keys", proc)
    show(rec)

    comment = """
hostAliases:
  type: array
  x-kubernetes-list-map-keys: [ip]  # identity
  items:
    properties:
      ip:
        type: string
"""
    write_case("comment.yaml", comment)
    proc = run_cli(["-"], stdin=comment)
    rec = summarize("inline comment after flow keys", proc)
    show(rec)

    crlf = "hostAliases:\r\n  type: array\r\n  x-kubernetes-list-map-keys:\r\n  - ip\r\n  items:\r\n    properties:\r\n      ip:\r\n        type: string\r\n"
    write_case("crlf.yaml", crlf)
    proc = run_cli(["-"], stdin=crlf)
    rec = summarize("CRLF yaml", proc)
    show(rec)

    tab_indent = "hostAliases:\n\ttype: array\n\tx-kubernetes-list-map-keys:\n\t- ip\n\titems:\n\t  properties:\n\t    ip:\n\t      type: string\n"
    write_case("tab_indent.yaml", tab_indent)
    proc = run_cli(["-"], stdin=tab_indent)
    rec = summarize("tab indent yaml", proc)
    show(rec)

    two_keys = """
hostAliases:
  type: array
  x-kubernetes-list-map-keys: [ip, hostname]
  items:
    required: [ip]
    properties:
      ip:
        type: string
      hostname:
        type: string
"""
    write_case("two_keys.yaml", two_keys)
    proc = run_cli(["-"], stdin=two_keys)
    rec = summarize("two keys one required one not", proc)
    show(rec)
    print("  stdout:\n" + proc.stdout)

    required_wrong_level = """
hostAliases:
  type: array
  x-kubernetes-list-map-keys: [ip]
  required: [ip]
  items:
    properties:
      ip:
        type: string
"""
    write_case("required_wrong_level.yaml", required_wrong_level)
    proc = run_cli(["-"], stdin=required_wrong_level)
    rec = summarize("required at list not items", proc)
    show(rec)
    print("  stdout:\n" + proc.stdout)

    banner("LEFTOVER: Go vs YAML separate rows")
    proc = run_cli([str(FX / "052-types.go"), str(FX / "crd-list-map.yaml")])
    rec = summarize("separate rows go+yaml", proc)
    print("  rows:")
    for line in proc.stdout.splitlines():
        if line.startswith(("disagree", "agree", "missing")) and "\t" in line:
            print("   ", line.split("\t")[0], line.split("\t")[1])

    banner("LEFTOVER: protobuf opt is not a verdict")
    proto = """
type Spec struct {
	// +listMapKey=name
	Items []Item `json:"items"`
}
type Item struct {
	Name string `json:"name" protobuf:"bytes,1,opt,name=name"`
}
"""
    write_case("protobuf_opt.go", proto)
    proc = run_cli(["-"], stdin=proto)
    rec = summarize("protobuf opt required json", proc)
    show(rec)
    print("  stdout:\n" + proc.stdout)

    proto_omit = """
type Spec struct {
	// +listMapKey=name
	Items []Item `json:"items"`
}
type Item struct {
	Name string `json:"name,omitempty" protobuf:"bytes,1,opt,name=name"`
}
"""
    write_case("protobuf_opt_omit.go", proto_omit)
    proc = run_cli(["-"], stdin=proto_omit)
    rec = summarize("protobuf opt + json omitempty", proc)
    show(rec)

    banner("LEFTOVER: tabs inside json tags")
    tab_tag = (
        "type Spec struct {\n"
        "\t// +listMapKey=name\n"
        "\tItems []Item `json:\"items\"`\n"
        "}\n"
        "type Item struct {\n"
        '\tName string `json:"na\tme,omitempty"`\n'
        "}\n"
    )
    write_case("tab_json.go", tab_tag)
    proc = run_cli(["-"], stdin=tab_tag)
    rec = summarize("tab in json name", proc)
    show(rec)
    print("  first line tabs", rec["n_tabs_first_join"])
    print("  stdout repr:", repr(proc.stdout))

    banner("LEFTOVER: rc=0 without --check still includes disagree")
    proc = run_cli([str(FX / "052-types.go")])
    rec = summarize("owned without --check", proc)
    show(rec)
    proc = run_cli(["--check", str(FX / "052-types.go")])
    rec = summarize("owned with --check", proc)
    show(rec)

    banner("LEFTOVER: JSON OpenAPI mixed optionality synthetic")
    mixed_json = json.dumps(
        {
            "a": {
                "hostAliases": {
                    "type": "array",
                    "x-kubernetes-list-map-keys": ["ip"],
                    "items": {"required": ["ip"], "properties": {"ip": {"type": "string"}}},
                }
            },
            "b": {
                "hostAliases": {
                    "type": "array",
                    "x-kubernetes-list-map-keys": ["ip"],
                    "items": {"properties": {"ip": {"type": "string"}}},
                }
            },
        }
    )
    write_case("mixed.json", mixed_json)
    proc = run_cli(["-"], stdin=mixed_json)
    rec = summarize("json required then optional", proc)
    show(rec)
    print("  stdout:\n" + proc.stdout)
    print("  honesty", dict(collect_yaml_optionality(mixed_json)))
    if rec["agree_n"] == "1" and rec["disagree_n"] == "0":
        leftover_lies.append("JSON required-then-optional first-wins agree hides disagree")

    mixed_json_rev = json.dumps(
        {
            "a": {
                "hostAliases": {
                    "type": "array",
                    "x-kubernetes-list-map-keys": ["ip"],
                    "items": {"properties": {"ip": {"type": "string"}}},
                }
            },
            "b": {
                "hostAliases": {
                    "type": "array",
                    "x-kubernetes-list-map-keys": ["ip"],
                    "items": {"required": ["ip"], "properties": {"ip": {"type": "string"}}},
                }
            },
        }
    )
    write_case("mixed_rev.json", mixed_json_rev)
    proc = run_cli(["-"], stdin=mixed_json_rev)
    rec = summarize("json optional then required", proc)
    show(rec)
    print("  honesty", dict(collect_yaml_optionality(mixed_json_rev)))

    banner("EXTRA: block scalars still join after mutate-3")
    proc = run_cli([str(FX / "crd-block-scalar.yaml")])
    rec = summarize("owned crd-block-scalar", proc)
    show(rec)
    proc = run_cli([str(FX / "crd-versions.yaml")])
    rec = summarize("owned crd-versions", proc)
    show(rec)
    proc = run_cli([str(FX / "crd-list-map.json")])
    rec = summarize("owned crd-list-map.json", proc)
    show(rec)
    proc = run_cli([str(FX / "crd-hyphen-key.yaml")])
    rec = summarize("owned hyphen key", proc)
    show(rec)
    proc = run_cli([str(FX / "crd-array-required.yaml")])
    rec = summarize("owned array-schema required", proc)
    show(rec)
    proc = run_cli([str(FX / "crd-ref.yaml")])
    rec = summarize("owned local $ref", proc)
    show(rec)

    banner("EXTRA: patchMergeKey only; json comma omitempty; listMapKey prose")
    proc = run_cli(["-"], stdin="// +listMapKey=name\n")
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

    json_dash = """
type Spec struct {
	// +listMapKey=name
	Items []Item `json:"items"`
}
type Item struct {
	Name string `json:"-"`
}
"""
    proc = run_cli(["-"], stdin=json_dash)
    rec = summarize("json dash", proc)
    show(rec)

    banner("EXTRA: 400 pairs timing")
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
    proc = run_cli([str(FX / "052-types.go")])
    print(proc.stdout)

    banner("VERDICT INPUTS")
    print("kill_flags", json.dumps(kill_flags, indent=2))
    print("leftover_lies", leftover_lies)
    honor_kill = any(kill_flags.values())
    print("HONOR_KILL_ANY", honor_kill)
    print("LEFTOVER_IDENTITY_LIE_INDENT_CAN_CUT", leftover_lies)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
