#!/usr/bin/env python3
# SPDX-License-Identifier: GPL-3.0-or-later
"""Repository navigation, mechanical quality gates and private preservation."""

from pathlib import Path
import os
import sys

TOOLS = Path(__file__).resolve().parent
LOCAL = TOOLS.parent / ".project-local/quality"
if __name__ == "__main__" and (LOCAL / "bin/python").exists() and Path(sys.prefix) != LOCAL:
    os.execv(str(LOCAL / "bin/python"), [str(LOCAL / "bin/python"), __file__, *sys.argv[1:]])
sys.path.insert(0, str(TOOLS))
for site in LOCAL.glob("lib/python*/site-packages"):
    sys.path.append(str(site))

from repo_quality.base import (
    now as now,
    canonical as canonical,
    sha as sha,
    safe_name as safe_name,
    current_path as current_path,
    private as private,
    git as git,
    tree as tree,
    View as View,
)

from repo_quality.register import (
    load_register as load_register,
    classify as classify,
    link as link,
    headings as headings,
    immutable as immutable,
)

from repo_quality.navigation import (
    record_index as record_index,
    render as render,
)

from repo_quality.evidence import (
    inventory as inventory,
    original_waveforms as original_waveforms,
    snapshot_hashes as snapshot_hashes,
    verify_evidence as verify_evidence,
    ensure_idle as ensure_idle,
    backup_paths as backup_paths,
    file_manifest as file_manifest,
    evidence_fingerprint as evidence_fingerprint,
    independent_storage as independent_storage,
    write_attestation as write_attestation,
    preservation_status as preservation_status,
    new_inventory as new_inventory,
)

from repo_quality.backup import (
    create_backup as create_backup,
    verify_tar as verify_tar,
    restore_backup as restore_backup,
)

from repo_quality.checks import (
    check as check,
    hook_installed as hook_installed,
    install_hook as install_hook,
)

from repo_quality.cli import (
    main as main,
)


from repo_quality import backup as backup, evidence as evidence
from repo_quality.base import GENERATED as GENERATED, ROUTES as ROUTES

if __name__ == "__main__":
    raise SystemExit(main())
