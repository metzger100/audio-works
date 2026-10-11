# Meridian decisions

Current operative view, 11 October 2026. [Hashed original rationale](../docs/history/2026-10-09/meridian-microphone/DECISIONS.md) retains all historical entries. D014 supersedes D002/D012's simulation stop; D010 supersedes D006's comparison purchases; D026 supersedes D009's folder name. Purchase/characterization and implementation qualification remain unresolved.

| ID / date | Decision or recommendation | Status |
| --- | --- | --- |
| D001 / 2026-10-04 | Develop an original microphone for private DIY use in Germany. | Owner requirement |
| D002 / 2026-10-04 | Research the real capsule market before designing any electronics or body. | Historical simulation stop superseded by D014; physical gates open |
| D003 / 2026-10-04 | Keep medium, small, and large diaphragm architectures open; do not equate outer capsule diameter with active diaphragm diameter. | Accepted research principle |
| D004 / 2026-10-04 | Retain ≤7 dBA and approximately ≥135 dB SPL as aspirational system targets, not a filter that discards better choir acoustics. | Provisional target interpretation |
| D005 / 2026-10-04 | Treat test-amplifier noise/SPL and complete-microphone sensitivity as system measurements, not bare-capsule specifications. | Accepted research principle |
| D006 / 2026-10-04 | Originally proposed purchasing Arienne Flat K47, Haun KA 200 N, and Transound TSB-2555B/JLI-2555BXZ3-GP for physical comparison. | **Purchase recommendation superseded by D010** |
| D007 / 2026-10-04 | Do not use generic marketplace capsules as established OEM equivalents without evidence. | Accepted research principle |
| D008 / 2026-10-04 | Use current import rules and explicit shipping assumptions in procurement estimates. | Accepted research principle |
| D009 / 2026-10-04 | Keep the existing lowercase `meridian/` project directory. | Superseded by D026 |
| D010 / 2026-10-04 | Buy only parts with an intended use in the finished project. Default to one chosen capsule; do not purchase comparison capsules, acoustic references, or surplus units for self-selection without a concrete planned use and an owner decision. | **Owner requirement; active** |
| D011 / 2026-10-04 | Resolve gaps through online evidence where possible; document and accept residual risks before purchasing the intended final capsule. Characterize that purchased capsule to guide implementation. | Accepted research method |
| D012 / 2026-10-04 | Recommend **one Arienne Audio Flat K47, normal Cardioid/Omni K47FRB**, intended to remain in the finished M100. | **Simulation input confirmed by D014; physical selection pending** |
| D013 / 2026-10-04 | Keep current-batch noise, overload, safe polarization and angular behavior explicitly unresolved; do not assume a later circuit can correct intrinsic capsule limits. | Accepted evidence boundary |
| D014 / 2026-10-05 | Use Flat K47 Cardioid/Omni K47FRB as the explicit capsule input for a simulator-driven research laboratory; create executable environment, tests, optimization and diversity archive before designing a production circuit. | **Owner mission; active** |
| D015 / 2026-10-05 | Prohibit individual semiconductor selection, beta matching and concealed unit trimming; qualify manufacturer variation and retain multiple architecture families. | **Owner requirement; active** |
| D016 / 2026-10-05 | The repository and project implementations must avoid third-party patent infringement; require dated claim/territory/status screening and hold affected implementations with credible unresolved potentially blocking risks before prototype selection, manufacture or implementation publication. | **Owner requirement; active** |
| D017 / 2026-10-05 | Make standard, documented, currently obtainable parts a core repository principle. Verify private small-quantity Germany sourcing and delivered costs; realize optimized values with actual parts and requalify their tolerances and substitutions. | **Owner requirement; active** |

| ID / date | Decision / rationale | Status |
| --- | --- | --- |
| D018 /2026-10-05 | [Scoped device agreement](lab/research/devices/device-model-validation.md); no complete qualified microphone set | Partial research |
| D019 /2026-10-05 | GPL-3.0-or-later software, CERN-OHL-S-2.0 hardware; [scope](../LICENSE); third-party terms/earlier grants retained | Owner-directed |
| D020 /2026-10-06 | Rename remote repository to audio-works and update current links | Owner-directed |
| D021 /2026-10-06 | Lead public docs with M100 Audio Works and builder readiness; [build conventions](../CONTRIBUTING.md#documenting-a-hardware-project) | Owner-directed |
| D022 /2026-10-06 | Plain English; remove status slogan/process jargon | Owner-directed |
| D023 /2026-10-06 | Public projects are released/not released, without maturity labels | Owner-directed |
| D024 /2026-10-06 | Wider audio-hardware range is a goal; current work is microphone research | Owner-directed |
| D025 /2026-10-06 | Standard logo on ivory in both GitHub themes; retain masters/shared geometry | Owner-directed |
| D026 /2026-10-06 | Rename meridian to meridian-microphone, family/device folders; preserve evidence/legacy recovery | Owner-directed |
| D027 /2026-10-09 | [Six-mechanism attempts](lab/research/architectures/first-architecture-decisions.md), retained failures/children/families | No selection |
| D028 /2026-10-09 | [Scoped optimization](lab/research/architectures/optimization/robust-optimization-decisions.md) | All holds retained |
| D029 /2026-10-09 | [Intermediate comparison](lab/research/architectures/architecture-comparison-001-decisions.md) | No winner |
| D030 /2026-10-09 | [Continuation plan](lab/research/prompts/DECISIONS.md); deferred measurement access | Gates retained |
| D031 /2026-10-09 | [Parts strengthening](lab/research/devices/parts-database-expansion-002-decisions.md); earlier owner publication direction | No qualification promotion |
| D032 /2026-10-10 | [Concise reports and subject/tool separation](../docs/decisions/2026-10-10-meridian-cleanup.md) | Owner-directed cleanup |
| D033 /2026-10-11 | [One research home, verified original relocation and concise current guides](../docs/decisions/2026-10-11-research-consolidation.md) | Owner-directed completion |

| D034 /2026-10-11 | [Scoped reading, flat data pages and shared candidate conditions](../docs/decisions/2026-10-11-reading-and-data-layout.md) | Owner-directed overhead reduction |

| D035 /2026-10-11 | [Shared page folders and consolidated subject documents](../docs/decisions/2026-10-11-folder-layout.md) | Owner-directed folder cleanup |

The historical G1 gate still requires intended capsule/variant/use, quantity, Germany delivered quote, interface facts, confidence and acknowledged residual risks before purchasing. Default one capsule; a second needs an intended second microphone. Record batch/serial and calibrated measurements before architecture selection. No purchase/contact authorization follows from this log.
