#!/usr/bin/env python3
"""Join omitempty / +optional with listMapKey identity."""

from __future__ import annotations

import importlib.machinery
import importlib.util
import subprocess
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CLI = ROOT / "tagjoin"
FIXTURES = ROOT / "fixtures"


def load_mod():
    loader = importlib.machinery.SourceFileLoader("tagjoin_cli", str(CLI))
    spec = importlib.util.spec_from_loader(loader.name, loader)
    assert spec is not None
    mod = importlib.util.module_from_spec(spec)
    sys.modules[loader.name] = mod
    loader.exec_module(mod)
    return mod


TJ = load_mod()


def parse_rows(text: str) -> dict[str, list[list[str]]]:
    rows: dict[str, list[list[str]]] = {}
    for line in text.splitlines():
        if not line or "\t" not in line:
            continue
        name, *rest = line.split("\t")
        rows.setdefault(name, []).append(rest)
    return rows


def run_cli(args, *, stdin=None):
    return subprocess.run(
        [sys.executable, str(CLI), *args],
        check=False,
        capture_output=True,
        text=True,
        input=stdin,
    )


def quals(rows, kind: str) -> list[str]:
    return [row[0] for row in rows.get(kind, [])]


class Owned052Tests(unittest.TestCase):
    def test_wrapped_fixture_names_ip_and_name(self):
        text = (FIXTURES / "052-types.go").read_text(encoding="utf-8")
        result = TJ.inspect(text)
        names = [f"{j.elem}.{j.field_name}" for j in result["disagree"]]
        self.assertEqual(names, ["LocalObjectReference.Name", "HostAlias.IP"])
        self.assertEqual(len(result["agree"]), 0)
        self.assertEqual(result["other_omitempty"], ["HostAlias.Hostnames"])
        ip = result["disagree"][1]
        self.assertEqual(ip.json_name, "ip")
        self.assertTrue(ip.omitempty)
        self.assertFalse(ip.plus_optional)
        self.assertEqual(ip.list_name, "HostAliases")
        name = result["disagree"][0]
        self.assertTrue(name.plus_optional)
        self.assertTrue(name.omitempty)
        self.assertEqual(name.list_name, "ImagePullSecrets")

    def test_cli_wrapped_fixture(self):
        proc = run_cli([str(FIXTURES / "052-types.go")])
        self.assertEqual(proc.returncode, 0, proc.stderr)
        rows = parse_rows(proc.stdout)
        self.assertEqual(rows["disagree_n"][0], ["2"])
        self.assertEqual(rows["agree_n"][0], ["0"])
        self.assertEqual(
            quals(rows, "disagree"),
            ["LocalObjectReference.Name", "HostAlias.IP"],
        )
        name_row = rows["disagree"][0]
        self.assertIn("ImagePullSecrets", name_row)
        self.assertIn("imagePullSecrets,omitempty", name_row)
        self.assertIn("name,omitempty", name_row)
        self.assertIn("+optional,omitempty", name_row)
        self.assertEqual(name_row[name_row.index("protobuf") + 1], "opt")
        self.assertIn("listMapKey", name_row[name_row.index("identity") + 1])
        ip_row = rows["disagree"][1]
        self.assertIn("HostAliases", ip_row)
        self.assertIn("hostAliases,omitempty", ip_row)
        self.assertIn("ip,omitempty", ip_row)
        self.assertIn("omitempty", ip_row)
        self.assertNotIn("+optional,omitempty", ip_row)
        self.assertEqual(rows["other_omitempty"][0], ["HostAlias.Hostnames"])

    def test_excerpt_loose_fields_same_join(self):
        text = (FIXTURES / "excerpt.go").read_text(encoding="utf-8")
        result = TJ.inspect(text)
        names = [f"{j.elem}.{j.field_name}" for j in result["disagree"]]
        self.assertEqual(names, ["LocalObjectReference.Name", "HostAlias.IP"])

    def test_list_omitempty_is_not_the_identity_field(self):
        """Secrets omitempty; key Name is required. Do not name the list."""
        text = """
type Bag struct {
	// +listMapKey=name
	Secrets []SecretRef `json:"secrets,omitempty"`
}
type SecretRef struct {
	Name string `json:"name"`
}
"""
        result = TJ.inspect(text)
        self.assertEqual(len(result["disagree"]), 0)
        self.assertEqual(len(result["agree"]), 1)
        join = result["agree"][0]
        self.assertEqual(join.elem, "SecretRef")
        self.assertEqual(join.field_name, "Name")
        self.assertTrue(join.list_omitempty)
        self.assertFalse(join.omitempty)


class UnseenAndAgreeTests(unittest.TestCase):
    def test_unseen_containerport(self):
        proc = run_cli([str(FIXTURES / "unseen-ports.go")])
        self.assertEqual(proc.returncode, 0, proc.stderr)
        rows = parse_rows(proc.stdout)
        self.assertEqual(quals(rows, "disagree"), ["ContainerPort.ContainerPort"])
        self.assertEqual(rows["disagree_n"][0], ["1"])
        self.assertEqual(rows["agree_n"][0], ["0"])
        row = rows["disagree"][0]
        self.assertIn("Ports", row)
        self.assertIn("ports,omitempty", row)
        self.assertIn("containerPort,omitempty", row)
        self.assertEqual(rows["other_omitempty"][0], ["none"])

    def test_agree_required_name(self):
        proc = run_cli([str(FIXTURES / "agree-name.go")])
        self.assertEqual(proc.returncode, 0, proc.stderr)
        rows = parse_rows(proc.stdout)
        self.assertEqual(quals(rows, "agree"), ["Item.Name"])
        self.assertEqual(rows["disagree_n"][0], ["0"])
        self.assertEqual(rows["agree_n"][0], ["1"])
        self.assertNotIn("Item.Value", quals(rows, "disagree"))
        self.assertNotIn("Item.Value", quals(rows, "agree"))
        self.assertEqual(rows["other_omitempty"][0], ["Item.Value"])
        agree_row = rows["agree"][0]
        self.assertIn("items,omitempty", agree_row)
        self.assertEqual(agree_row[agree_row.index("json") + 1], "name")
        self.assertEqual(agree_row[agree_row.index("optional") + 1], "-")

    def test_missing_key_field(self):
        text = """
type Bag struct {
	// +listMapKey=nope
	Items []Item `json:"items"`
}
type Item struct {
	Name string `json:"name"`
}
"""
        result = TJ.inspect(text)
        self.assertEqual(len(result["missing"]), 1)
        self.assertEqual(result["missing"][0].json_name, "nope")
        self.assertEqual(result["missing"][0].elem, "Item")

    def test_stdin(self):
        text = (FIXTURES / "agree-name.go").read_text(encoding="utf-8")
        proc = run_cli(["-"], stdin=text)
        self.assertEqual(proc.returncode, 0, proc.stderr)
        rows = parse_rows(proc.stdout)
        self.assertEqual(quals(rows, "agree"), ["Item.Name"])

    def test_missing_file(self):
        proc = run_cli(["/no/such/tagjoin.go"])
        self.assertEqual(proc.returncode, 1)
        self.assertIn("tagjoin:", proc.stderr)

    def test_no_join(self):
        proc = run_cli(["-"], stdin="package p\n")
        self.assertEqual(proc.returncode, 0, proc.stderr)
        rows = parse_rows(proc.stdout)
        self.assertEqual(rows["join"][0], ["none"])
        self.assertEqual(rows["other_omitempty"][0], ["none"])
        self.assertEqual(rows["disagree_n"][0], ["0"])


class ParserTests(unittest.TestCase):
    def test_pointer_and_qualified_elem(self):
        text = """
type Spec struct {
	// +listMapKey=ip
	HostAliases []*corev1.HostAlias `json:"hostAliases"`
}
type HostAlias struct {
	IP string `json:"ip,omitempty"`
}
"""
        result = TJ.inspect(text)
        self.assertEqual(
            [f"{j.elem}.{j.field_name}" for j in result["disagree"]],
            ["HostAlias.IP"],
        )

    def test_multiple_list_map_keys(self):
        text = """
type Spec struct {
	// +listMapKey=name
	// +listMapKey=port
	Items []Item `json:"items"`
}
type Item struct {
	Name string `json:"name,omitempty"`
	Port int `json:"port"`
}
"""
        result = TJ.inspect(text)
        pairs = [(j.field_name, j.verdict) for j in result["joins"]]
        self.assertEqual(pairs, [("Name", "disagree"), ("Port", "agree")])

    def test_json_empty_name_keeps_omitempty(self):
        self.assertEqual(TJ.json_parts(",omitempty"), ("", True))
        self.assertEqual(TJ.json_parts("name,omitempty"), ("name", True))
        self.assertEqual(TJ.json_parts("omitempty"), ("omitempty", False))
        self.assertEqual(TJ.json_parts("-"), ("-", False))


class DestroyerMutationTests(unittest.TestCase):
    def test_empty_json_name_omitempty_is_disagree(self):
        """json:\",omitempty\" is Go field name + omitempty, not json name omitempty."""
        proc = run_cli([str(FIXTURES / "empty-json-name.go")])
        self.assertEqual(proc.returncode, 0, proc.stderr)
        rows = parse_rows(proc.stdout)
        self.assertEqual(quals(rows, "agree"), [])
        self.assertEqual(quals(rows, "disagree"), ["Item.Name"])
        self.assertEqual(rows["disagree_n"][0], ["1"])
        row = rows["disagree"][0]
        self.assertEqual(row[row.index("json") + 1], ",omitempty")
        self.assertEqual(row[row.index("optional") + 1], "omitempty")

    def test_json_address_is_not_listmapkey_ip(self):
        """Wire name address is not identity ip. Do not disagree HostAlias.IP."""
        proc = run_cli([str(FIXTURES / "wrong-wire.go")])
        self.assertEqual(proc.returncode, 0, proc.stderr)
        rows = parse_rows(proc.stdout)
        self.assertNotIn("HostAlias.IP", quals(rows, "disagree"))
        self.assertEqual(quals(rows, "disagree"), [])
        self.assertEqual(quals(rows, "missing"), ["HostAlias.ip"])
        self.assertEqual(rows["missing_n"][0], ["1"])

    def test_duplicate_listmapkey_counts_once(self):
        proc = run_cli([str(FIXTURES / "dup-listmapkey.go")])
        self.assertEqual(proc.returncode, 0, proc.stderr)
        rows = parse_rows(proc.stdout)
        self.assertEqual(quals(rows, "disagree"), ["Item.Name"])
        self.assertEqual(rows["disagree_n"][0], ["1"])
        self.assertEqual(len(rows.get("disagree", [])), 1)

    def test_yaml_list_map_keys_are_not_join_none(self):
        proc = run_cli([str(FIXTURES / "crd-list-map.yaml")])
        self.assertEqual(proc.returncode, 0, proc.stderr)
        rows = parse_rows(proc.stdout)
        self.assertNotIn("none", [cell for row in rows.get("join", []) for cell in row])
        self.assertEqual(
            quals(rows, "disagree"),
            ["imagePullSecrets.name", "hostAliases.ip"],
        )
        self.assertEqual(rows["disagree_n"][0], ["2"])
        self.assertEqual(rows["unparsed_n"][0], ["0"])
        name_row = rows["disagree"][0]
        self.assertEqual(
            name_row[name_row.index("identity") + 1],
            "x-kubernetes-list-map-keys",
        )
        self.assertEqual(name_row[name_row.index("optional") + 1], "not-required")

    def test_apply_error_names_ip_and_name(self):
        proc = run_cli([str(FIXTURES / "apply_error.txt")])
        self.assertEqual(proc.returncode, 0, proc.stderr)
        rows = parse_rows(proc.stdout)
        self.assertEqual(
            quals(rows, "disagree"),
            ["hostAliases.ip", "imagePullSecrets.name"],
        )
        self.assertEqual(rows["disagree_n"][0], ["2"])

    def test_check_exits_1_on_owned_disagree(self):
        proc = run_cli(["--check", str(FIXTURES / "052-types.go")])
        self.assertEqual(proc.returncode, 1, proc.stderr)
        rows = parse_rows(proc.stdout)
        self.assertEqual(
            quals(rows, "disagree"),
            ["LocalObjectReference.Name", "HostAlias.IP"],
        )

    def test_check_exits_0_on_agree(self):
        proc = run_cli(["--check", str(FIXTURES / "agree-name.go")])
        self.assertEqual(proc.returncode, 0, proc.stderr)

    def test_json_dash_is_not_a_key(self):
        text = """
type Spec struct {
	// +listMapKey=name
	Items []Item `json:"items"`
}
type Item struct {
	Name string `json:"-"`
}
"""
        result = TJ.inspect(text)
        self.assertEqual(len(result["missing"]), 1)
        self.assertEqual(result["missing"][0].elem, "Item")
        self.assertEqual(len(result["agree"]), 0)
        self.assertEqual(len(result["disagree"]), 0)

    def test_default_satisfies_identity(self):
        text = """
type Spec struct {
	// +listMapKey=name
	Items []Item `json:"items"`
}
type Item struct {
	// +default=""
	Name string `json:"name,omitempty"`
}
"""
        result = TJ.inspect(text)
        self.assertEqual(len(result["disagree"]), 0)
        self.assertEqual(len(result["agree"]), 1)
        self.assertTrue(result["agree"][0].has_default)
        self.assertTrue(result["agree"][0].omitempty)

    def test_yaml_required_key_is_agree(self):
        text = """
ports:
  type: array
  x-kubernetes-list-map-keys:
  - containerPort
  items:
    required:
    - containerPort
    properties:
      containerPort:
        type: integer
"""
        result = TJ.inspect(text)
        self.assertEqual(
            [f"{j.elem}.{j.field_name}" for j in result["agree"]],
            ["ports.containerPort"],
        )
        self.assertEqual(result["disagree"], [])

    def test_unparsed_identity_hint_is_not_join_none(self):
        proc = run_cli(
            ["-"],
            stdin="the apiserver rejected x-kubernetes-list-map-keys without required or default\n",
        )
        self.assertEqual(proc.returncode, 2, proc.stderr)
        rows = parse_rows(proc.stdout)
        self.assertEqual(rows["unparsed"][0], ["x-kubernetes-list-map-keys"])
        self.assertNotIn("none", [cell for row in rows.get("join", []) for cell in row])

    def test_multiple_files_are_one_package(self):
        proc = run_cli(
            [
                str(FIXTURES / "agree-name.go"),
                str(FIXTURES / "unseen-ports.go"),
            ]
        )
        self.assertEqual(proc.returncode, 0, proc.stderr)
        rows = parse_rows(proc.stdout)
        self.assertEqual(quals(rows, "agree"), ["Item.Name"])
        self.assertEqual(quals(rows, "disagree"), ["ContainerPort.ContainerPort"])

    def test_duplicate_json_name_is_collision(self):
        text = """
type Spec struct {
	// +listMapKey=name
	Items []Item `json:"items"`
}
type Item struct {
	A string `json:"name,omitempty"`
	B string `json:"name"`
}
"""
        result = TJ.inspect(text)
        self.assertEqual(len(result["collision"]), 1)
        self.assertEqual(result["collision"][0].json_name, "name")
        self.assertIn("A", result["collision"][0].field_name)
        self.assertIn("B", result["collision"][0].field_name)

    def test_duplicate_type_name_is_collision(self):
        proc = run_cli([str(FIXTURES / "dup-type.go")])
        self.assertEqual(proc.returncode, 0, proc.stderr)
        rows = parse_rows(proc.stdout)
        self.assertEqual(quals(rows, "collision"), ["HostAlias.ip"])
        self.assertEqual(rows["collision_n"][0], ["1"])
        self.assertEqual(quals(rows, "disagree"), [])
        self.assertEqual(quals(rows, "agree"), [])
        check = run_cli(["--check", str(FIXTURES / "dup-type.go")])
        self.assertEqual(check.returncode, 1, check.stderr)

    def test_spaces_around_listmapkey_eq(self):
        proc = run_cli([str(FIXTURES / "spaces-eq.go")])
        self.assertEqual(proc.returncode, 0, proc.stderr)
        rows = parse_rows(proc.stdout)
        self.assertEqual(quals(rows, "disagree"), ["Item.Name"])
        self.assertNotIn("none", [cell for row in rows.get("join", []) for cell in row])

    def test_bom_is_not_silent_miss(self):
        raw = (FIXTURES / "bom.go").read_bytes()
        self.assertTrue(raw.startswith(b"\xef\xbb\xbf"), raw[:8])
        proc = run_cli([str(FIXTURES / "bom.go")])
        self.assertEqual(proc.returncode, 0, proc.stderr)
        rows = parse_rows(proc.stdout)
        self.assertEqual(quals(rows, "agree"), ["Item.Name"])
        self.assertEqual(rows["unparsed_n"][0], ["0"])

    def test_inline_embed_is_the_identity_field(self):
        proc = run_cli([str(FIXTURES / "embed-inline.go")])
        self.assertEqual(proc.returncode, 0, proc.stderr)
        rows = parse_rows(proc.stdout)
        self.assertEqual(quals(rows, "disagree"), ["HostAlias.IP"])
        self.assertEqual(quals(rows, "missing"), [])
        self.assertNotIn("Base.IP", quals(rows, "disagree"))
        self.assertEqual(rows["other_omitempty"][0], ["none"])

    def test_untagged_list_field_still_joins(self):
        proc = run_cli([str(FIXTURES / "untagged-list.go")])
        self.assertEqual(proc.returncode, 0, proc.stderr)
        rows = parse_rows(proc.stdout)
        self.assertEqual(quals(rows, "disagree"), ["Item.Name"])
        self.assertNotIn("none", [cell for row in rows.get("join", []) for cell in row])

    def test_go_name_is_not_json_identity(self):
        """listMapKey=IP (Go name) vs json:\"address\" is missing, not HostAlias.IP disagree."""
        text = """
type Spec struct {
	// +listMapKey=IP
	HostAliases []HostAlias `json:"hostAliases"`
}
type HostAlias struct {
	IP string `json:"address,omitempty"`
}
"""
        result = TJ.inspect(text)
        self.assertEqual(
            [f"{j.elem}.{j.field_name}" for j in result["disagree"]],
            [],
        )
        self.assertEqual(len(result["missing"]), 1)
        self.assertEqual(result["missing"][0].json_name, "IP")

    def test_same_line_listmapkey_is_not_join_none(self):
        text = """
type Spec struct {
	Items []Item `json:"items"` // +listMapKey=name
}
type Item struct {
	Name string `json:"name,omitempty"`
}
"""
        result = TJ.inspect(text)
        self.assertEqual(
            [f"{j.elem}.{j.field_name}" for j in result["disagree"]],
            ["Item.Name"],
        )

    def test_block_comment_listmapkey_is_unparsed(self):
        proc = run_cli(
            ["-"],
            stdin="""
type Spec struct {
	/* +listMapKey=ip */
	HostAliases []HostAlias `json:"hostAliases"`
}
type HostAlias struct {
	IP string `json:"ip,omitempty"`
}
""",
        )
        self.assertEqual(proc.returncode, 2, proc.stderr)
        rows = parse_rows(proc.stdout)
        self.assertEqual(rows["unparsed"][0], ["+listMapKey"])
        self.assertNotIn("none", [cell for row in rows.get("join", []) for cell in row])

    def test_case_sensitive_wire_name_is_not_folded(self):
        """listMapKey=IP vs json:\"ip\" is missing, not disagree HostAlias.IP."""
        text = """
type Spec struct {
	// +listMapKey=IP
	HostAliases []HostAlias `json:"hostAliases"`
}
type HostAlias struct {
	IP string `json:"ip,omitempty"`
}
"""
        result = TJ.inspect(text)
        self.assertEqual(
            [f"{j.elem}.{j.field_name}" for j in result["disagree"]],
            [],
        )
        self.assertEqual(len(result["missing"]), 1)
        self.assertEqual(result["missing"][0].json_name, "IP")
        self.assertEqual(result["missing"][0].elem, "HostAlias")

    def test_untagged_go_name_is_not_folded_to_json_name(self):
        """Untagged Name vs listMapKey=name is missing (wire name Name)."""
        text = """
type Spec struct {
	// +listMapKey=name
	Items []Item `json:"items"`
}
type Item struct {
	Name string
}
"""
        result = TJ.inspect(text)
        self.assertEqual(len(result["agree"]), 0)
        self.assertEqual(len(result["disagree"]), 0)
        self.assertEqual(len(result["missing"]), 1)
        self.assertEqual(result["missing"][0].json_name, "name")

    def test_named_inline_is_not_an_embed(self):
        text = """
type Spec struct {
	// +listMapKey=ip
	HostAliases []HostAlias `json:"hostAliases"`
}
type HostAlias struct {
	Inner Base `json:"inner,inline"`
}
type Base struct {
	IP string `json:"ip,omitempty"`
}
"""
        result = TJ.inspect(text)
        self.assertEqual(
            [f"{j.elem}.{j.field_name}" for j in result["disagree"]],
            [],
        )
        self.assertEqual(len(result["missing"]), 1)
        self.assertEqual(result["missing"][0].json_name, "ip")

    def test_kubebuilder_default_colon_satisfies_identity(self):
        text = """
type Spec struct {
	// +listMapKey=name
	Items []Item `json:"items"`
}
type Item struct {
	// +kubebuilder:default:foo
	Name string `json:"name,omitempty"`
}
"""
        result = TJ.inspect(text)
        self.assertEqual(len(result["disagree"]), 0)
        self.assertEqual(len(result["agree"]), 1)
        self.assertTrue(result["agree"][0].has_default)

    def test_omitzero_is_optional_protobuf_opt_is_not(self):
        omitzero = """
type Spec struct {
	// +listMapKey=name
	Items []Item `json:"items"`
}
type Item struct {
	Name string `json:"name,omitzero"`
}
"""
        result = TJ.inspect(omitzero)
        self.assertEqual(len(result["disagree"]), 1)
        self.assertTrue(result["disagree"][0].omitzero)
        proto = """
type Spec struct {
	// +listMapKey=name
	Items []Item `json:"items"`
}
type Item struct {
	Name string `json:"name" protobuf:"bytes,1,opt,name=name"`
}
"""
        result = TJ.inspect(proto)
        self.assertEqual(len(result["agree"]), 1)
        self.assertTrue(result["agree"][0].protobuf_opt)
        self.assertFalse(result["agree"][0].omitempty)


class YamlWalkerMutationTests(unittest.TestCase):
    def test_block_scalar_does_not_drop_list_map_keys(self):
        proc = run_cli([str(FIXTURES / "crd-block-scalar.yaml")])
        self.assertEqual(proc.returncode, 0, proc.stderr)
        rows = parse_rows(proc.stdout)
        self.assertEqual(rows.get("unparsed_n", [["0"]])[0], ["0"])
        self.assertEqual(
            quals(rows, "agree"),
            ["conditions.type", "claims.name"],
        )
        self.assertEqual(rows["agree_n"][0], ["2"])
        self.assertEqual(rows["disagree_n"][0], ["0"])

    def test_versions_sequence_keeps_nested_schema(self):
        proc = run_cli([str(FIXTURES / "crd-versions.yaml")])
        self.assertEqual(proc.returncode, 0, proc.stderr)
        rows = parse_rows(proc.stdout)
        self.assertEqual(rows.get("unparsed_n", [["0"]])[0], ["0"])
        self.assertEqual(
            quals(rows, "disagree"),
            ["hostAliases.ip", "imagePullSecrets.name"],
        )
        self.assertEqual(rows["disagree_n"][0], ["2"])

    def test_json_crd_joins_list_map_keys(self):
        proc = run_cli([str(FIXTURES / "crd-list-map.json")])
        self.assertEqual(proc.returncode, 0, proc.stderr)
        rows = parse_rows(proc.stdout)
        self.assertEqual(rows.get("unparsed_n", [["0"]])[0], ["0"])
        self.assertEqual(
            quals(rows, "disagree"),
            ["hostAliases.ip", "imagePullSecrets.name"],
        )

    def test_yaml_ref_is_followed(self):
        proc = run_cli([str(FIXTURES / "crd-ref.yaml")])
        self.assertEqual(proc.returncode, 0, proc.stderr)
        rows = parse_rows(proc.stdout)
        self.assertEqual(quals(rows, "agree"), ["hostAliases.ip"])
        self.assertEqual(rows["unparsed_n"][0], ["0"])

    def test_unresolved_ref_is_unparsed_not_false_disagree(self):
        text = """
hostAliases:
  type: array
  x-kubernetes-list-map-keys:
  - ip
  items:
    $ref: '#/definitions/Missing'
"""
        proc = run_cli(["-"], stdin=text)
        self.assertEqual(proc.returncode, 2, proc.stderr)
        rows = parse_rows(proc.stdout)
        self.assertEqual(rows["unparsed"][0], ["x-kubernetes-list-map-keys"])
        self.assertEqual(quals(rows, "disagree"), [])
        self.assertEqual(rows["disagree_n"][0], ["0"])

    def test_array_level_required_is_not_item_required(self):
        proc = run_cli([str(FIXTURES / "crd-array-required.yaml")])
        self.assertEqual(proc.returncode, 0, proc.stderr)
        rows = parse_rows(proc.stdout)
        self.assertEqual(quals(rows, "disagree"), ["hostAliases.ip"])
        self.assertEqual(quals(rows, "agree"), [])

    def test_hyphenated_list_map_key_joins(self):
        proc = run_cli([str(FIXTURES / "crd-hyphen-key.yaml")])
        self.assertEqual(proc.returncode, 0, proc.stderr)
        rows = parse_rows(proc.stdout)
        self.assertEqual(quals(rows, "agree"), ["volumeMounts.mount-path"])
        self.assertEqual(rows["unparsed_n"][0], ["0"])

    def test_go_then_yaml_joins_both(self):
        proc = run_cli(
            [
                str(FIXTURES / "052-types.go"),
                str(FIXTURES / "crd-list-map.yaml"),
            ]
        )
        self.assertEqual(proc.returncode, 0, proc.stderr)
        rows = parse_rows(proc.stdout)
        self.assertEqual(
            quals(rows, "disagree"),
            [
                "LocalObjectReference.Name",
                "HostAlias.IP",
                "imagePullSecrets.name",
                "hostAliases.ip",
            ],
        )
        self.assertEqual(rows["disagree_n"][0], ["4"])
        self.assertEqual(rows["unparsed_n"][0], ["0"])

    def test_yaml_then_go_same_package_as_go_then_yaml(self):
        go_first = run_cli(
            [str(FIXTURES / "052-types.go"), str(FIXTURES / "crd-list-map.yaml")]
        )
        yaml_first = run_cli(
            [str(FIXTURES / "crd-list-map.yaml"), str(FIXTURES / "052-types.go")]
        )
        self.assertEqual(go_first.returncode, 0, go_first.stderr)
        self.assertEqual(yaml_first.returncode, 0, yaml_first.stderr)
        self.assertEqual(
            set(quals(parse_rows(go_first.stdout), "disagree")),
            set(quals(parse_rows(yaml_first.stdout), "disagree")),
        )
        self.assertEqual(parse_rows(go_first.stdout)["disagree_n"][0], ["4"])
        self.assertEqual(parse_rows(yaml_first.stdout)["disagree_n"][0], ["4"])


def _transfer_scratch() -> Path | None:
    for parent in [ROOT, *ROOT.parents]:
        cand = parent / "destroyers" / "_tagjoin_transfer_scratch"
        if cand.is_dir():
            return cand
        cand = (
            parent
            / "lab-runs"
            / "specimen-hdd-20260902-1112"
            / "destroyers"
            / "_tagjoin_transfer_scratch"
        )
        if cand.is_dir():
            return cand
    proc = subprocess.run(
        ["git", "-C", str(ROOT), "rev-parse", "--git-common-dir"],
        check=False,
        capture_output=True,
        text=True,
    )
    if proc.returncode == 0:
        common = Path(proc.stdout.strip())
        if not common.is_absolute():
            common = (ROOT / common).resolve()
        repo = common.parent if common.name == ".git" else common.parent
        cand = (
            repo
            / "lab-runs"
            / "specimen-hdd-20260902-1112"
            / "destroyers"
            / "_tagjoin_transfer_scratch"
        )
        if cand.is_dir():
            return cand
    return None


class TransferCrdTests(unittest.TestCase):
    scratch = _transfer_scratch()

    @unittest.skipUnless(scratch is not None, "transfer CRD scratch not mounted")
    def test_crossplane_objects_names_conditions_type(self):
        path = self.scratch / "kubernetes.crossplane.io_objects.yaml"
        proc = run_cli([str(path)])
        self.assertEqual(proc.returncode, 0, proc.stderr)
        rows = parse_rows(proc.stdout)
        self.assertEqual(rows["unparsed_n"][0], ["0"])
        self.assertIn("conditions.type", quals(rows, "agree"))
        self.assertNotIn("unparsed", rows)

    @unittest.skipUnless(scratch is not None, "transfer CRD scratch not mounted")
    def test_pixie_viziers_names_claims_name(self):
        path = self.scratch / "px.dev_viziers.yaml"
        proc = run_cli([str(path)])
        self.assertEqual(proc.returncode, 0, proc.stderr)
        rows = parse_rows(proc.stdout)
        self.assertEqual(rows["unparsed_n"][0], ["0"])
        self.assertIn("claims.name", quals(rows, "agree"))

    @unittest.skipUnless(scratch is not None, "transfer CRD scratch not mounted")
    def test_servicemonitor_names_real_keys(self):
        path = self.scratch / "monitoring.coreos.com_servicemonitors.yaml"
        proc = run_cli([str(path)])
        self.assertEqual(proc.returncode, 0, proc.stderr)
        rows = parse_rows(proc.stdout)
        self.assertEqual(rows["unparsed_n"][0], ["0"])
        self.assertIn("conditions.type", quals(rows, "agree"))
        for key in ("bindings.group", "bindings.resource", "bindings.name", "bindings.namespace"):
            self.assertIn(key, quals(rows, "agree"), proc.stdout)

    @unittest.skipUnless(scratch is not None, "transfer CRD scratch not mounted")
    def test_openapi_json_names_hostaliases_ip(self):
        path = self.scratch / "apis__apps__v1_openapi.json"
        proc = run_cli([str(path)])
        self.assertEqual(proc.returncode, 0, proc.stderr)
        rows = parse_rows(proc.stdout)
        self.assertEqual(rows["unparsed_n"][0], ["0"])
        self.assertIn("hostAliases.ip", quals(rows, "disagree"))
        self.assertIn("imagePullSecrets.name", quals(rows, "disagree"))
        self.assertIn("conditions.type", quals(rows, "agree"))


if __name__ == "__main__":
    unittest.main()

