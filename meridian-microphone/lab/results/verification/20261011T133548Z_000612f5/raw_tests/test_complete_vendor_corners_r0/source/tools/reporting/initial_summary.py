# SPDX-License-Identifier: GPL-3.0-or-later
"""Derive compact tables without replacing the maintained phase summary."""

from initial_common import BASE, PROPOSAL


def stage(context):
    report = f"""# Initial fixture comparison

Both ideal-buffer fixtures are unqualified. Values describe the original cohort,
not a real microphone, safe capsule polarization or measured acoustic noise.

[Baseline](../runs/{BASE}/results.json) · [Proposal](../runs/{PROPOSAL}/results.json)

| Metric | Baseline | Proposal |
| --- | --- | --- |
{context["table"]}

## Check outcomes

| Check | Baseline | Proposal |
| --- | --- | --- |
{context["checks"]}

Original-cohort verification: [{context["tests"]} tests](../{context["verification_relative"].removeprefix("results/")}).
Current verification belongs in the repository validation record.
"""
    return {**context, "report": report}
