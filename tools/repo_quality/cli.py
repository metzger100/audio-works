# SPDX-License-Identifier: GPL-3.0-or-later
from __future__ import annotations
import argparse
import json
from pathlib import Path
import subprocess
import sys
import tarfile

from .base import ROUTES, View
from .checks import check, install_hook
from .runner import fast_checks
from .navigation import navigation_output
from .structure import original
from .backup import create_backup, restore_backup
from .register import classify, load_register
from .navigation import render
from .evidence import new_inventory, verify_evidence


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, default=Path(__file__).resolve().parents[2])
    sub = parser.add_subparsers(dest="command", required=True)
    context = sub.add_parser("context")
    context.add_argument("route", choices=sorted(ROUTES))
    for cmd in ("files", "search"):
        p = sub.add_parser(cmd)
        p.add_argument("--include-evidence", action="store_true")
        p.add_argument("--include-history", action="store_true")
        p.add_argument("--include-generated", action="store_true")
        if cmd == "search":
            p.add_argument("pattern")
    sub.add_parser("refresh")
    p = sub.add_parser("check")
    p.add_argument("--staged", action="store_true")
    p.add_argument("--ref")
    p.add_argument("--base")
    sub.add_parser("audit")
    p = sub.add_parser("hooks")
    p.add_argument("action", choices=["install"])
    e = sub.add_parser("evidence").add_subparsers(dest="action", required=True)
    e.add_parser("verify")
    e.add_parser("inventory")
    p = e.add_parser("backup")
    p.add_argument("--destination", required=True, type=Path)
    p.add_argument("--independent", action="store_true")
    p = e.add_parser("restore")
    p.add_argument("--source", required=True, type=Path)
    p.add_argument("--destination", required=True, type=Path)
    args = parser.parse_args(argv)
    root = args.root.resolve()
    try:
        if args.command == "hooks":
            result = install_hook(root)
        elif args.command == "evidence" and args.action == "backup":
            result = create_backup(root, args.destination, args.independent)
        elif args.command == "evidence" and args.action == "restore":
            result = restore_backup(root, args.source, args.destination)
        else:
            view = View(
                root,
                getattr(args, "staged", False),
                getattr(args, "ref", None),
                getattr(args, "base", None),
            )
            r = load_register(view)
            if args.command in {"check", "audit"}:
                result = check(view, r)
                if args.command == "check" and result["status"] == "pass":
                    result["fast_checks"] = fast_checks(view, r)
                    if result["fast_checks"]["status"] != "pass":
                        result["status"] = "fail"
            elif args.command == "refresh":
                changed = []
                expected = render(view, r)
                for p in view.paths:
                    if navigation_output(p) and not original(p, r) and p not in expected:
                        (root / p).unlink()
                        changed.append(p)
                for p, data in expected.items():
                    target = root / p
                    if not target.exists() or target.read_bytes() != data:
                        target.parent.mkdir(parents=True, exist_ok=True)
                        target.write_bytes(data)
                        changed.append(p)
                result = {"status": "pass", "updated": changed}
            elif args.command == "context":
                paths = list(dict.fromkeys(r["common"] + r["routes"][args.route]))
                common_count = sum(len(view.text(p)) for p in dict.fromkeys(r["common"]))
                result = {
                    "route": args.route,
                    "common_characters": common_count,
                    "estimated_common_tokens": round(common_count / 4),
                    "reading": [
                        {
                            "path": p,
                            "role": classify(p, r),
                            "purpose": "Mandatory entry context"
                            if p in r["common"]
                            else "Task-specific contract/evidence",
                            "characters": len(view.text(p)),
                        }
                        for p in paths
                    ],
                    "note": "Read the listed material before affected work; inspect additional relevant code/evidence on demand. Load one prompt representation.",
                }
            elif args.command in {"files", "search"}:
                paths = [
                    p
                    for p in sorted(view.paths)
                    if (classify(p, r) != "evidence" or args.include_evidence)
                    and (classify(p, r) != "historical" or args.include_history)
                    and (classify(p, r) != "generated" or args.include_generated)
                ]
                if args.command == "files":
                    print("\n".join(paths))
                    return 0
                if not paths:
                    return 1
                return subprocess.run(["rg", "-n", "--", args.pattern, *paths], cwd=root).returncode
            elif args.command == "evidence":
                result = (
                    verify_evidence(root, view)
                    if args.action == "verify"
                    else new_inventory(root, view)
                )
        print(json.dumps(result, indent=2, ensure_ascii=False))
        return 0 if result.get("status", "pass") == "pass" else 1
    except (
        ValueError,
        OSError,
        KeyError,
        TypeError,
        json.JSONDecodeError,
        subprocess.CalledProcessError,
        tarfile.TarError,
    ) as error:
        print(
            json.dumps({"status": "fail", "error": str(error)}, ensure_ascii=False), file=sys.stderr
        )
        return 1
