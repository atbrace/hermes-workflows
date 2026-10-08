"""Packaging-specific reproducibility, manifest, and import-isolation checks."""
from __future__ import annotations

import ast
import hashlib
import importlib.util
import json
import os
import re
import subprocess
import sys
import tempfile
import types
import zipfile
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent
VERSION = re.search(r"^version:\s*([\d.]+)", (ROOT / "plugin.yaml").read_text(), re.M).group(1)


def check(label: str, condition: bool) -> None:
    if not condition:
        raise AssertionError(label)
    print("PASS", label)


def main() -> None:
    manifest = json.loads((ROOT / "dashboard/manifest.json").read_text(encoding="utf-8"))
    check("dashboard backend keeps its API and hidden tab with a loadable web entry",
          manifest.get("api") == "plugin_api.py" and manifest.get("tab", {}).get("hidden") is True
          and manifest.get("name") == "hermes-workflows" and manifest.get("version") == VERSION
          and manifest.get("entry") == "index.js" and (ROOT / "dashboard/index.js").is_file())

    collision = types.ModuleType("wfcommon")
    sys.modules["wfcommon"] = collision
    api_path = ROOT / "dashboard/plugin_api.py"
    before_path = list(sys.path)
    spec = importlib.util.spec_from_file_location("packaging_dashboard_probe", api_path)
    if spec is None or spec.loader is None:
        raise AssertionError("dashboard plugin API cannot be loaded")
    api = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(api)
    scoped = api._workflow_common()
    check("dashboard resolves its sibling wfcommon under a private module name",
          Path(scoped.__file__).resolve() == (ROOT / "wfcommon.py").resolve()
          and scoped is not collision and sys.modules["wfcommon"] is collision
          and list(sys.path) == before_path)
    sys.modules.pop("wfcommon", None)

    with tempfile.TemporaryDirectory(prefix=".tmp-package-", dir=HERE) as temp_dir:
        temp = Path(temp_dir)
        first = temp / "first.zip"
        second = temp / "second.zip"
        for target in (first, second):
            result = subprocess.run(
                [sys.executable, str(ROOT / "scripts/pack.py"), "--output", str(target)],
                cwd=ROOT, capture_output=True, text=True,
            )
            if result.returncode != 0:
                raise AssertionError(
                    f"pack.py exit {result.returncode}:\n{result.stdout}\n{result.stderr}"
                )
        first_bytes, second_bytes = first.read_bytes(), second.read_bytes()
        check("identical source trees produce byte-identical archives", first_bytes == second_bytes)
        check("sidecar pins the archive bytes",
              first.with_suffix(".zip.sha256").read_text(encoding="utf-8")
              == f"{hashlib.sha256(first_bytes).hexdigest()}  first.zip\n")

        with zipfile.ZipFile(first) as archive:
            members = set(archive.namelist())
            root = f"hermes-workflows-{VERSION}/"
            must = ("plugin.yaml", "__init__.py", "wf.py", "wfcommon.py",
                    "wf_dialect.py", "card_enforcement.py", "post_exit_hook.py",
                    "dashboard/manifest.json", "dashboard/index.js", "dashboard/plugin_api.py",
                    "desktop/plugin.js", "README.md", "INSTALL.md", "SKILL.md", "AGENTS.md",
                    "references/portable.md", "references/grammar.md", "references/operations.md",
                    "examples/README.md", "examples/basics/smoke.json", "SHA256SUMS", "install.json")
            check("runtime ZIP ships every runtime module, dashboard/desktop half, docs, skill, examples",
                  all(root + rel in members for rel in must))
            # M03 release boundary: the installer artifact carries runtime only.
            # Tests, fixtures, and repo-maintenance helpers stay repository-side
            # (git clone is the source archive). These bans are the boundary —
            # a re-added "ship it because a test needs it" row fails here.
            shipped = {m[len(root):] for m in members if not m.endswith("/")}
            banned = {p for p in shipped
                      if p.startswith(("tests/", "scripts/", "graphify"))}
            check("runtime ZIP ships no tests/, no scripts/, no generated graph data",
                  not banned)
            checksum_text = archive.read(root + "SHA256SUMS").decode("utf-8")
            rows = [line.split("  ", 1) for line in checksum_text.splitlines()]
            check("SHA256SUMS verifies every pinned source entry",
                  bool(rows) and all(len(row) == 2 and root + row[1] in members
                                     and hashlib.sha256(archive.read(root + row[1])).hexdigest() == row[0]
                                     for row in rows))
            manifest = archive.read(root + "plugin.yaml").lower()
            check("public manifest declares license, homepage and requires_hermes",
                  b"license: mit" in manifest and b"homepage: https://github.com/" in manifest
                  and b"requires_hermes:" in manifest)

        # #105 discharge, M03 shape: assert the import CLOSURE of the shipped
        # RUNTIME modules from the unpacked package root (the tests are no
        # longer shipped — same law, correct subject).
        with tempfile.TemporaryDirectory(prefix=".tmp-unpack-") as unpack_dir:
            unpacked = Path(unpack_dir)
            with zipfile.ZipFile(first) as archive:
                archive.extractall(unpacked)
            pkg = unpacked / root.rstrip("/")
            runtime_mods = sorted(pkg.glob("*.py")) + [pkg / "dashboard" / "plugin_api.py"]
            missing: dict[str, list[str]] = {}
            for mod in runtime_mods:
                tree = ast.parse(mod.read_text(encoding="utf-8"), filename=str(mod))
                names: set[str] = set()
                for node in tree.body:  # top-level imports only: the shipped-entry contract
                    if isinstance(node, ast.Import):
                        names.update(alias.name.split(".")[0] for alias in node.names)
                    elif isinstance(node, ast.ImportFrom) and node.level == 0 and node.module:
                        names.add(node.module.split(".")[0])
                candidates = sorted(
                    n for n in names
                    if n not in sys.stdlib_module_names and n != mod.stem
                )
                for m2 in candidates:
                    if (pkg / (m2 + ".py")).exists():
                        continue  # sibling runtime module
                    missing.setdefault(mod.name, []).append(m2)
            check("runtime modules import only stdlib + packaged siblings (stdlib-only promise)",
                  not missing)

    print("ALL PASS")


if __name__ == "__main__":
    main()
