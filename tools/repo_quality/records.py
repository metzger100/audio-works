# SPDX-License-Identifier: GPL-3.0-or-later
"""Record relationships and evidence prerequisites; a structural pass is no clearance."""

from pathlib import PurePosixPath
import re

from .data import load


def relationships(view):
    errors = []
    candidates = {}
    for path in sorted(view.paths):
        if re.fullmatch(
            r"meridian-microphone/lab/candidates/(?:candidate|fixture)_\d+/topology.yaml", path
        ):
            value = load(view.text, path)
            identity = PurePosixPath(path).parent.name
            if value.get("id") != identity:
                errors.append(f"Candidate identity mismatch: {path}")
            candidates[identity] = value
    for identity, value in candidates.items():
        for parent in value.get("parents", []):
            if parent not in candidates:
                errors.append(f"Missing candidate parent: {identity} -> {parent}")
        if identity in value.get("parents", []):
            errors.append(f"Self-parent candidate: {identity}")
    # Frozen originals can contain historical incomplete schemas. New/current pointers may not promote them.
    for path in sorted(view.paths):
        if not re.fullmatch(r"meridian-microphone/lab/candidates/candidate_\d+/results.json", path):
            continue
        pointer = load(view.text, path)
        if not isinstance(pointer.get("eligible", False), bool):
            errors.append(f"Eligibility must be boolean: {path}")
        record_path = pointer.get("result_file")
        if record_path:
            target = "meridian-microphone/lab/" + record_path
            if target not in view.paths:
                errors.append(f"Missing result record: {path}: {record_path}")
                continue
            record = load(view.text, target)
            if pointer.get("latest_experiment") != record.get("experiment_id"):
                errors.append(f"Result pointer identity mismatch: {path}")
            if pointer.get("eligible") != record.get("eligible") or pointer.get(
                "status"
            ) != record.get("status"):
                errors.append(f"Unsupported evidence promotion: {path}")
            if pointer.get("eligible"):
                required = {
                    "operating_point",
                    "frequency_response",
                    "noise",
                    "distortion",
                    "headroom",
                    "output_impedance",
                    "balance",
                    "phantom_supply",
                    "temperature",
                    "semiconductor_corners",
                    "monte_carlo",
                    "loading",
                    "startup",
                    "stability",
                }
                checks = record.get("checks", {})
                if (
                    record.get("status") != "qualified"
                    or record.get("source_unchanged") is False
                    or not record.get("source_manifest")
                    or record.get("missing_qualification_evidence")
                    or not required.issubset(checks)
                    or any(checks[key].get("status") != "pass" for key in required)
                ):
                    errors.append(f"Eligible evidence lacks qualification prerequisites: {path}")
    return errors
