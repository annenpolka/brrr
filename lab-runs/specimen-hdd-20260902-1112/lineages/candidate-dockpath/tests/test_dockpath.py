#!/usr/bin/env python3
"""cgroup says not-in-docker; mountinfo still names the container; -v is cwd."""

from __future__ import annotations

import importlib.machinery
import importlib.util
import os
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CLI = ROOT / "dockpath"
FIX = ROOT / "fixtures"
CID = "c33988ec7651ebc867cb24755eaf637a6734088bc7eef59d5799293a9e5450f7"
SHORT = CID[:12]
PODMAN = "a" * 64
CWD = "/builds/project/src"


def load_mod():
    loader = importlib.machinery.SourceFileLoader("dockpath_cli", str(CLI))
    spec = importlib.util.spec_from_loader(loader.name, loader)
    assert spec is not None
    mod = importlib.util.module_from_spec(spec)
    loader.exec_module(mod)
    return mod


DP = load_mod()


def parse_rows(text: str) -> dict[str, list[str]]:
    rows: dict[str, list[str]] = {}
    for line in text.splitlines():
        if not line or "\t" not in line:
            continue
        name, *rest = line.split("\t")
        rows[name] = rest
    return rows


def run_cli(args: list[str], **kwargs) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [sys.executable, str(CLI), *args],
        capture_output=True,
        text=True,
        check=False,
        **kwargs,
    )


def write_pair(dirpath: str, cgroup: bytes, mountinfo: bytes) -> tuple[str, str]:
    cg = os.path.join(dirpath, "cgroup")
    mi = os.path.join(dirpath, "mountinfo")
    with open(cg, "wb") as fh:
        fh.write(cgroup)
    with open(mi, "wb") as fh:
        fh.write(mountinfo)
    return cg, mi


class Specimen065Tests(unittest.TestCase):
    def test_v2_cgroup_miss_mountinfo_hit(self):
        cgroup = (FIX / "cgroup_v2.excerpt").read_bytes()
        mountinfo = (FIX / "mountinfo_v2.hostname.excerpt").read_bytes()
        result = DP.inspect(cgroup, mountinfo, CWD)
        self.assertFalse(result["cgroup_docker"])
        self.assertFalse(result["cgroup_substring"])
        self.assertEqual(result["cgroup_kind"], "v2")
        self.assertIsNone(result["cgroup_id"])
        self.assertEqual(result["mountinfo_ids"], [CID])
        self.assertEqual(result["dest"], "/src")
        self.assertEqual(result["volume"], f"{CWD}:/src")
        self.assertEqual(result["remapped"], "no")
        self.assertEqual(result["id_source"], "mountinfo")
        self.assertFalse(result["id_mismatch"])

    def test_cli_v2_owned(self):
        proc = run_cli(
            [
                str(FIX / "cgroup_v2.excerpt"),
                str(FIX / "mountinfo_v2.hostname.excerpt"),
                "--cwd",
                CWD,
            ]
        )
        self.assertEqual(proc.returncode, 0, proc.stderr)
        rows = parse_rows(proc.stdout)
        self.assertEqual(rows["cgroup_docker"], ["no"])
        self.assertEqual(rows["cgroup_substring"], ["no"])
        self.assertEqual(rows["cgroup_id"], ["none"])
        self.assertEqual(rows["mountinfo_id"], [CID])
        self.assertEqual(rows["dest"], ["/src"])
        self.assertEqual(rows["volume"], [f"{CWD}:/src"])
        self.assertEqual(rows["remapped"], ["no"])
        self.assertEqual(rows["would_inspect"], ["no"])
        self.assertEqual(rows["id_source"], ["mountinfo"])
        self.assertEqual(rows["remapped"], ["no"])

    def test_v1_mixed_unsupported_not_would(self):
        proc = run_cli(
            [
                str(FIX / "cgroup_v1.excerpt"),
                str(FIX / "mountinfo_v2.hostname.excerpt"),
                "--cwd",
                CWD,
            ]
        )
        self.assertEqual(proc.returncode, 0, proc.stderr)
        rows = parse_rows(proc.stdout)
        self.assertEqual(rows["cgroup_docker"], ["yes"])
        self.assertEqual(rows["cgroup_substring"], ["yes"])
        self.assertEqual(rows["cgroup_kind"], ["mixed"])
        self.assertEqual(rows["cgroup_docker_via"], ["cpuset"])
        self.assertEqual(rows["cgroup_id"], [CID])
        self.assertEqual(rows["cgroup_id_kind"], ["cpuset"])
        self.assertEqual(rows["mountinfo_id"], [CID])
        self.assertEqual(rows["would_inspect"], ["yes"])
        self.assertEqual(rows["remapped"], ["unsupported"])
        self.assertEqual(rows["id_source"], ["both"])
        self.assertEqual(rows["id_mismatch"], ["no"])
        self.assertEqual(rows["dest"], ["/src"])
        self.assertEqual(rows["volume"], ["none"])
        self.assertNotEqual(rows["remapped"], ["would"])
        self.assertNotIn(f"{CWD}:/src", proc.stdout)

    def test_unseen_podman_overlay(self):
        proc = run_cli(
            [
                str(FIX / "unseen-cgroup.excerpt"),
                str(FIX / "unseen-mountinfo.excerpt"),
                "--cwd",
                "/work/src",
            ]
        )
        self.assertEqual(proc.returncode, 0, proc.stderr)
        rows = parse_rows(proc.stdout)
        self.assertEqual(rows["cgroup_docker"], ["no"])
        self.assertEqual(rows["mountinfo_id"], [PODMAN])
        self.assertEqual(rows["volume"], ["/work/src:/src"])
        self.assertEqual(rows["remapped"], ["no"])
        self.assertEqual(rows["id_source"], ["mountinfo"])

    def test_missing_file(self):
        proc = run_cli(["/no/cgroup", str(FIX / "mountinfo_v2.hostname.excerpt"), "--cwd", "/x"])
        self.assertEqual(proc.returncode, 1)
        self.assertTrue(proc.stderr.startswith("dockpath:"))
        self.assertEqual(proc.stdout, "")


class DestroyerMutationTests(unittest.TestCase):
    def test_short_hex_mountinfo(self):
        with tempfile.TemporaryDirectory() as td:
            cg, mi = write_pair(
                td,
                f"5:cpuset:/docker/{SHORT}\n".encode(),
                (
                    f"730 721 8:3 /var/lib/docker/containers/{SHORT}/hostname "
                    "/etc/hostname rw - ext4 /dev/sda3 rw\n"
                ).encode(),
            )
            proc = run_cli([cg, mi, "--cwd", "/x"])
        self.assertEqual(proc.returncode, 0, proc.stderr)
        rows = parse_rows(proc.stdout)
        self.assertEqual(rows["cgroup_id"], [SHORT])
        self.assertEqual(rows["mountinfo_id"], [SHORT])
        self.assertEqual(rows["id_source"], ["both"])
        self.assertEqual(rows["remapped"], ["unsupported"])
        self.assertEqual(rows["volume"], ["none"])

    def test_short_hex_mountinfo_with_64_cpuset(self):
        with tempfile.TemporaryDirectory() as td:
            cg, mi = write_pair(
                td,
                f"5:cpuset:/docker/{CID}\n".encode(),
                (
                    f"730 721 8:3 /var/lib/docker/containers/{SHORT}/hostname "
                    "/etc/hostname rw - ext4 /dev/sda3 rw\n"
                ).encode(),
            )
            proc = run_cli([cg, mi, "--cwd", "/x"])
        rows = parse_rows(proc.stdout)
        self.assertEqual(rows["cgroup_id"], [CID])
        self.assertEqual(rows["mountinfo_id"], [SHORT])
        self.assertEqual(rows["id_source"], ["mismatch"])
        self.assertEqual(rows["id_mismatch"], ["yes"])

    def test_uppercase_64_mountinfo(self):
        upper = CID.upper()
        with tempfile.TemporaryDirectory() as td:
            cg, mi = write_pair(
                td,
                b"0::/system.slice/containerd.service\n",
                (
                    f"730 721 8:3 /var/lib/docker/containers/{upper}/hostname "
                    "/etc/hostname rw - ext4 /dev/sda3 rw\n"
                ).encode(),
            )
            proc = run_cli([cg, mi, "--cwd", "/x"])
        self.assertEqual(proc.returncode, 0, proc.stderr)
        rows = parse_rows(proc.stdout)
        self.assertEqual(rows["mountinfo_id"], [CID])
        self.assertEqual(rows["id_source"], ["mountinfo"])
        self.assertEqual(rows["remapped"], ["no"])

    def test_hex63_and_hex65_rejected(self):
        for n in (63, 65):
            hid = ("ab" * 40)[:n]
            with tempfile.TemporaryDirectory() as td:
                cg, mi = write_pair(
                    td,
                    b"0::/system.slice/containerd.service\n",
                    (
                        f"730 721 8:3 /var/lib/docker/containers/{hid}/hostname "
                        "/etc/hostname rw - ext4 /dev/sda3 rw\n"
                    ).encode(),
                )
                proc = run_cli([cg, mi, "--cwd", "/x"])
            self.assertEqual(proc.returncode, 0, proc.stderr)
            rows = parse_rows(proc.stdout)
            self.assertEqual(rows["mountinfo_id"], ["none"], n)
            self.assertEqual(rows["id_source"], ["none"], n)

    def test_kubepods_basename_is_cgroup_id(self):
        with tempfile.TemporaryDirectory() as td:
            cg, mi = write_pair(
                td,
                (
                    "12:cpuset:/kubepods/burstable/"
                    f"pod8f3c1a2b-1111-2222-3333-444444444444/{CID}\n"
                ).encode(),
                (
                    "730 721 8:3 /var/lib/kubelet/pods/"
                    "8f3c1a2b-1111-2222-3333-444444444444/etc-hosts "
                    "/etc/hosts rw - ext4 /dev/sda3 rw\n"
                ).encode(),
            )
            proc = run_cli([cg, mi, "--cwd", "/app"])
        self.assertEqual(proc.returncode, 0, proc.stderr)
        rows = parse_rows(proc.stdout)
        self.assertEqual(rows["cgroup_docker"], ["no"])
        self.assertEqual(rows["cgroup_id"], [CID])
        self.assertEqual(rows["cgroup_id_kind"], ["kubepods"])
        self.assertEqual(rows["mountinfo_id"], ["none"])
        self.assertEqual(rows["id_source"], ["cgroup"])
        self.assertEqual(rows["volume"], ["/app:/src"])
        self.assertEqual(rows["remapped"], ["no"])
        self.assertEqual(rows["would_inspect"], ["no"])

    def test_k8s_docker_scope_without_docker_mountinfo(self):
        with tempfile.TemporaryDirectory() as td:
            cg, mi = write_pair(
                td,
                f"0::/kubepods.slice/docker-{CID}.scope\n".encode(),
                (
                    "730 721 8:3 /var/lib/kubelet/pods/"
                    "8f3c1a2b-1111-2222-3333-444444444444/etc-hosts "
                    "/etc/hosts rw - ext4 /dev/sda3 rw\n"
                ).encode(),
            )
            proc = run_cli([cg, mi, "--cwd", "/app"])
        rows = parse_rows(proc.stdout)
        self.assertEqual(rows["cgroup_docker"], ["yes"])
        self.assertEqual(rows["cgroup_docker_via"], ["scope"])
        self.assertEqual(rows["cgroup_id"], [CID])
        self.assertEqual(rows["cgroup_id_kind"], ["scope"])
        self.assertEqual(rows["mountinfo_id"], ["none"])
        self.assertEqual(rows["id_source"], ["cgroup"])
        self.assertEqual(rows["would_inspect"], ["yes"])
        self.assertEqual(rows["remapped"], ["unsupported"])
        self.assertEqual(rows["volume"], ["none"])

    def test_k8s_docker_scope_with_docker_mountinfo(self):
        with tempfile.TemporaryDirectory() as td:
            cg, mi = write_pair(
                td,
                f"0::/kubepods.slice/docker-{CID}.scope\n".encode(),
                (FIX / "mountinfo_v2.hostname.excerpt").read_bytes(),
            )
            proc = run_cli([cg, mi, "--cwd", "/app"])
        rows = parse_rows(proc.stdout)
        self.assertEqual(rows["cgroup_id"], [CID])
        self.assertEqual(rows["mountinfo_id"], [CID])
        self.assertEqual(rows["id_source"], ["both"])
        self.assertEqual(rows["remapped"], ["unsupported"])
        self.assertEqual(rows["volume"], ["none"])

    def test_no_mountinfo_match(self):
        with tempfile.TemporaryDirectory() as td:
            cg, mi = write_pair(
                td,
                (FIX / "cgroup_v2.excerpt").read_bytes(),
                b"100 90 8:1 / / rw - ext4 /dev/sda1 rw\n",
            )
            proc = run_cli([cg, mi, "--cwd", CWD])
        rows = parse_rows(proc.stdout)
        self.assertEqual(rows["mountinfo_id"], ["none"])
        self.assertEqual(rows["id_source"], ["none"])
        self.assertEqual(rows["volume"], [f"{CWD}:/src"])
        self.assertEqual(rows["remapped"], ["no"])

    def test_omitted_cwd_is_required(self):
        proc = run_cli(
            [
                str(FIX / "cgroup_v2.excerpt"),
                str(FIX / "mountinfo_v2.hostname.excerpt"),
            ]
        )
        self.assertEqual(proc.returncode, 2)
        self.assertIn("--cwd", proc.stderr)
        self.assertNotIn(CWD, proc.stdout)
        self.assertNotIn(CWD, proc.stderr)

    def test_cwd_space_is_quoted_volume(self):
        proc = run_cli(
            [
                str(FIX / "cgroup_v2.excerpt"),
                str(FIX / "mountinfo_v2.hostname.excerpt"),
                "--cwd",
                "/builds/my project/src",
            ]
        )
        self.assertEqual(proc.returncode, 0, proc.stderr)
        rows = parse_rows(proc.stdout)
        self.assertEqual(rows["cwd"], ["/builds/my project/src"])
        self.assertEqual(rows["volume"], ['"/builds/my project/src":/src'])

    def test_cwd_tab_newline_colon_refused(self):
        for cwd in ("/builds/proj\tsrc", "/builds/proj\nsrc", "/host/path:/evil"):
            proc = run_cli(
                [
                    str(FIX / "cgroup_v2.excerpt"),
                    str(FIX / "mountinfo_v2.hostname.excerpt"),
                    "--cwd",
                    cwd,
                ]
            )
            self.assertEqual(proc.returncode, 1, cwd)
            self.assertTrue(proc.stderr.startswith("dockpath:"), cwd)
            self.assertEqual(proc.stdout, "", cwd)

    def test_empty_files_not_a_volume(self):
        with tempfile.TemporaryDirectory() as td:
            cg, mi = write_pair(td, b"", b"")
            proc = run_cli([cg, mi, "--cwd", "/x"])
        self.assertEqual(proc.returncode, 1)
        self.assertIn("dockpath: empty cgroup and mountinfo", proc.stderr)
        self.assertEqual(proc.stdout, "")

    def test_docker_comment_is_substring_not_inspect(self):
        with tempfile.TemporaryDirectory() as td:
            cg, mi = write_pair(
                td,
                b"0::/system.slice/containerd.service\n# see also docker docs\n",
                (FIX / "mountinfo_v2.hostname.excerpt").read_bytes(),
            )
            proc = run_cli([cg, mi, "--cwd", "/x"])
        rows = parse_rows(proc.stdout)
        self.assertEqual(rows["cgroup_substring"], ["yes"])
        self.assertEqual(rows["cgroup_docker"], ["no"])
        self.assertEqual(rows["would_inspect"], ["no"])
        self.assertEqual(rows["remapped"], ["no"])
        self.assertEqual(rows["id_source"], ["mountinfo"])
        self.assertEqual(rows["volume"], ["/x:/src"])

    def test_docker_service_is_not_in_docker(self):
        with tempfile.TemporaryDirectory() as td:
            cg, mi = write_pair(
                td,
                b"5:cpuset:/user.slice\n1:name=systemd:/system.slice/docker.service\n",
                b"100 90 8:1 / / rw - ext4 /dev/sda1 rw\n",
            )
            proc = run_cli([cg, mi, "--cwd", "/home/user"])
        rows = parse_rows(proc.stdout)
        self.assertEqual(rows["cgroup_substring"], ["yes"])
        self.assertEqual(rows["cgroup_docker"], ["no"])
        self.assertEqual(rows["cgroup_id"], ["none"])
        self.assertEqual(rows["id_source"], ["none"])
        self.assertEqual(rows["would_inspect"], ["no"])
        self.assertEqual(rows["remapped"], ["no"])
        self.assertEqual(rows["volume"], ["/home/user:/src"])

    def test_memory_controller_docker_cpuset_root(self):
        with tempfile.TemporaryDirectory() as td:
            cg, mi = write_pair(
                td,
                f"4:memory:/docker/{CID}\n5:cpuset:/\n".encode(),
                (FIX / "mountinfo_v2.hostname.excerpt").read_bytes(),
            )
            proc = run_cli([cg, mi, "--cwd", CWD])
        rows = parse_rows(proc.stdout)
        self.assertEqual(rows["cgroup_substring"], ["yes"])
        self.assertEqual(rows["cgroup_docker"], ["no"])
        self.assertEqual(rows["cgroup_id"], ["none"])
        self.assertEqual(rows["mountinfo_id"], [CID])
        self.assertEqual(rows["id_source"], ["mountinfo"])
        self.assertEqual(rows["would_inspect"], ["no"])
        self.assertEqual(rows["remapped"], ["no"])
        self.assertEqual(rows["volume"], [f"{CWD}:/src"])

    def test_invalid_utf8_cpuset_is_dockpath_error(self):
        with tempfile.TemporaryDirectory() as td:
            cg, mi = write_pair(
                td,
                b"5:cpuset:/docker/\x80\xffid\n",
                (
                    f"junk\x00\xff /var/lib/docker/containers/{CID}/hostname x\n"
                ).encode(),
            )
            proc = run_cli([cg, mi, "--cwd", "/x"])
        self.assertEqual(proc.returncode, 1)
        self.assertTrue(proc.stderr.startswith("dockpath:"))
        self.assertIn("invalid utf-8", proc.stderr)
        self.assertNotIn("Traceback", proc.stderr)
        self.assertEqual(proc.stdout, "")

    def test_binary_docker_bytes_not_remapped_unsupported_without_id(self):
        with tempfile.TemporaryDirectory() as td:
            cg, mi = write_pair(td, b"garbage\x00\x01docker\xff\xfe", b"x\n")
            proc = run_cli([cg, mi, "--cwd", "/x"])
        self.assertEqual(proc.returncode, 0, proc.stderr)
        rows = parse_rows(proc.stdout)
        self.assertEqual(rows["cgroup_substring"], ["yes"])
        self.assertEqual(rows["cgroup_docker"], ["no"])
        self.assertEqual(rows["would_inspect"], ["no"])
        self.assertEqual(rows["remapped"], ["no"])
        self.assertEqual(rows["volume"], ["/x:/src"])
        self.assertNotEqual(rows["remapped"], ["would"])

    def test_docker_scope_v2_original_raises(self):
        with tempfile.TemporaryDirectory() as td:
            cg, mi = write_pair(
                td,
                f"0::/system.slice/docker-{CID}.scope\n".encode(),
                (FIX / "mountinfo_v2.hostname.excerpt").read_bytes(),
            )
            proc = run_cli([cg, mi, "--cwd", CWD])
        rows = parse_rows(proc.stdout)
        self.assertEqual(rows["cgroup_docker"], ["yes"])
        self.assertEqual(rows["cgroup_id"], [CID])
        self.assertEqual(rows["cgroup_id_kind"], ["scope"])
        self.assertEqual(rows["mountinfo_id"], [CID])
        self.assertEqual(rows["id_source"], ["both"])
        self.assertEqual(rows["remapped"], ["unsupported"])
        self.assertEqual(rows["volume"], ["none"])

    def test_id_mismatch_row(self):
        other = "a" * 64
        with tempfile.TemporaryDirectory() as td:
            cg, mi = write_pair(
                td,
                f"5:cpuset:/docker/{other}\n".encode(),
                (FIX / "mountinfo_v2.hostname.excerpt").read_bytes(),
            )
            proc = run_cli([cg, mi, "--cwd", "/x"])
        rows = parse_rows(proc.stdout)
        self.assertEqual(rows["cgroup_id"], [other])
        self.assertEqual(rows["mountinfo_id"], [CID])
        self.assertEqual(rows["id_source"], ["mismatch"])
        self.assertEqual(rows["id_mismatch"], ["yes"])
        self.assertEqual(rows["remapped"], ["unsupported"])
        self.assertEqual(rows["volume"], ["none"])

    def test_podman_storage_userdata(self):
        with tempfile.TemporaryDirectory() as td:
            cg, mi = write_pair(
                td,
                b"0::/\n",
                (
                    f"100 90 8:1 /var/lib/containers/storage/overlay-containers/"
                    f"{PODMAN}/userdata/hostname /etc/hostname rw - ext4 /dev/sda1 rw\n"
                ).encode(),
            )
            proc = run_cli([cg, mi, "--cwd", "/work/src"])
        rows = parse_rows(proc.stdout)
        self.assertEqual(rows["mountinfo_id"], [PODMAN])
        self.assertEqual(rows["id_source"], ["mountinfo"])
        self.assertEqual(rows["volume"], ["/work/src:/src"])
        self.assertEqual(rows["remapped"], ["no"])

    def test_containerd_rootfs(self):
        with tempfile.TemporaryDirectory() as td:
            cg, mi = write_pair(
                td,
                b"0::/\n",
                (
                    f"221 189 0:46 / / rw - overlay overlay "
                    f"rw,lowerdir=/var/lib/containerd/io.containerd.snapshotter.v1.overlayfs,upperdir=x "
                    f"workdir=/var/lib/containerd/io.containerd.runtime.v2.task/k8s.io/{CID}/rootfs\n"
                ).encode(),
            )
            proc = run_cli([cg, mi, "--cwd", "/app"])
        rows = parse_rows(proc.stdout)
        self.assertEqual(rows["mountinfo_id"], [CID])
        self.assertEqual(rows["id_source"], ["mountinfo"])

    def test_dest_is_declared_not_glued_constant(self):
        proc = run_cli(
            [
                str(FIX / "cgroup_v2.excerpt"),
                str(FIX / "mountinfo_v2.hostname.excerpt"),
                "--cwd",
                "/work",
                "--dest",
                "/app",
            ]
        )
        self.assertEqual(proc.returncode, 0, proc.stderr)
        rows = parse_rows(proc.stdout)
        self.assertEqual(rows["cwd"], ["/work"])
        self.assertEqual(rows["dest"], ["/app"])
        self.assertEqual(rows["volume"], ["/work:/app"])
        self.assertNotIn(":/src", proc.stdout)

    def test_hex64_rejects_user_slice(self):
        self.assertIsNone(DP.normalize_container_id("user.slice"))
        self.assertEqual(DP.normalize_container_id(CID), CID)
        self.assertEqual(DP.normalize_container_id(SHORT), SHORT)
        self.assertTrue(DP.HEX64.fullmatch(CID))
        self.assertFalse(DP.HEX64.fullmatch(SHORT))
        self.assertFalse(DP.HEX64.fullmatch("user.slice"))

    def test_empty_cwd_flag(self):
        proc = run_cli(
            [
                str(FIX / "cgroup_v2.excerpt"),
                str(FIX / "mountinfo_v2.hostname.excerpt"),
                "--cwd",
                "",
            ]
        )
        self.assertEqual(proc.returncode, 1)
        self.assertIn("dockpath: empty cwd", proc.stderr)

    def test_directory_is_dockpath_error(self):
        proc = run_cli([str(FIX), str(FIX / "mountinfo_v2.hostname.excerpt"), "--cwd", "/x"])
        self.assertEqual(proc.returncode, 1)
        self.assertTrue(proc.stderr.startswith("dockpath:"))
        self.assertEqual(proc.stdout, "")

    def test_v1_without_mountinfo_still_unsupported(self):
        with tempfile.TemporaryDirectory() as td:
            cg, mi = write_pair(
                td,
                (FIX / "cgroup_v1.excerpt").read_bytes(),
                b"100 90 8:1 / / rw - ext4 /dev/sda1 rw\n",
            )
            proc = run_cli([cg, mi, "--cwd", CWD])
        rows = parse_rows(proc.stdout)
        self.assertEqual(rows["cgroup_kind"], ["mixed"])
        self.assertEqual(rows["cgroup_id"], [CID])
        self.assertEqual(rows["mountinfo_id"], ["none"])
        self.assertEqual(rows["id_source"], ["cgroup"])
        self.assertEqual(rows["would_inspect"], ["yes"])
        self.assertEqual(rows["remapped"], ["unsupported"])
        self.assertEqual(rows["volume"], ["none"])


if __name__ == "__main__":
    unittest.main()
