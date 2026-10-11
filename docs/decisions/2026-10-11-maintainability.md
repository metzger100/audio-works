# Explicit workflows and contributor navigation

Date: 2026-10-11. The owner requested improvements following the repository review. This authorizes local maintenance and verification; it supplies no purchase, contact, publication or remote-settings authorization.

The review found clear subject boundaries and passing repository checks, with avoidable maintenance costs: large functions, report stages passing incidental local variables, repeated plot rendering and tight shared reading.

## Implementation

The comparison pipeline now shares a named `ComparisonData` record containing verified inputs and derived collections. Per-candidate BOM, nominal metrics, coverage, identity and raw-noise interpretation are distinct functions. Table generation, each figure, human-readable summaries and provenance have separate owners. Figures no longer cross stage boundaries or render twice. Pairing rejects unequal endpoint counts before rows can silently disappear; existing missing-value and scope rules remain.

MOS, JFET and OPA controls expose their existing sequence as small methods. The MOS DC/capacitance/leakage implementation uses one helper beside the existing characterizer; no new folder is introduced. Frozen-source replay tests compare every requested circuit, command, output, temperature, refinement, result and partial-failure state against original waveforms. These tests use retained historical sources as their oracle, without simulating replacement originals or fitting device behavior.

The six original mechanism registrations have named builders. A recorder compares their entire request sequence, metadata and explicit netlist lines with frozen source while creating no candidate. Numerical values, identities, hypotheses, order and family coverage are retained.

Navigation generation is divided into current state, source selection, module/root hubs, evidence and prompts. A complete output comparison established byte-identical generated navigation for the same selected inputs. [Start here](../start-here.md) supplies task-oriented entry points above the complete file index. Root instructions and the current decision table are edited for readability; original policies/decisions remain preserved. Mandatory policies, complete engineering contracts/specifications and additional evidence reading retain authority.

## Verification and preservation

Existing fixtures continue covering selected-index/committed-content gates, lossless partitions, original bytes, and recovery rejection. Added [device replay](../../meridian-microphone/lab/tests/test_characterization.py), [registration replay](../../meridian-microphone/lab/tests/test_batch_registration.py) and [report regressions](../../meridian-microphone/lab/tests/test_comparison.py) cover the changed scientific boundaries. [Validation](../validation/2026-10-11-maintainability.md) records checks, measured impact and omissions.

No scientific thresholds, uncertainty ranges, evaluation budgets, family counts, qualification prerequisites or repository limits change. Model/control disagreement and empty production fronts remain valid retained outcomes. There is no new arbitrary function-length rule or general exemption. The legacy ideal-fixture optimizer remains a separate historical compatibility path.

Storage requirements now follow the [GitHub owner decision](2026-10-11-github-canonical.md); private backups are optional. Existing historical declarations remain frozen. New verification evidence needs its own dated inventory and integrity check. Repository status does not establish original-evidence completeness.
