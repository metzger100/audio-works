# Project quality and maintenance contract

[Repository](README.md) · [Current state](CURRENT.md) · [Contributing](CONTRIBUTING.md) · [Validation record](docs/VALIDATION.md)

Owner-directed quality plan: 2026-10-05. This contract applies to contributors and agents. The mandatory completion gate lives in the agent instructions. [Current facts](project.json), [generated status](CURRENT.md), [navigation](docs/INDEX.md) and [evidence index](docs/EVIDENCE.md) have distinct roles.

## Source of truth

Record current phase, scoped readiness, blockers, next task and evidence pointers in `project.json`. Record reasons, owner decisions and supersession in decision logs; preserve original entries. Keep scientific observations in their original immutable experiment records and reports. Generated indexes reproduce those statuses; missing legacy metadata is unknown. Component, patent and scientific contracts remain authoritative. A mechanical check cannot certify preserved legal/scientific meaning: review policy changes against owner requirements.

## Maintained standards

- Organization: every project file is classified; active material is reachable from module indexes; local active links work; generated views match sources. Historical broken internal links are disclosed on historical landing pages, whose current links must work.
- Context: the common onboarding set is at most 32,000 characters; its token estimate is characters divided by four. Current state is below 300 words. Routes retain mandatory policies and relevant instructions/decisions; add needed evidence on demand without a scientific reading cap.
- Evidence: preserve original records, failures, parent relationships, snapshots and hashes. Existing inventories are immutable. New scientific batches require additional dated inventories, integrity checks, backup coverage and a successful restore. All 14 architecture families remain represented; qualification thresholds are independent of tooling scores.
- Completion: refresh affected generated pages, run the fast gate and applicable tests, verify/back up new evidence, and disclose incomplete readiness. A pass in one category cannot promote another.

## Change rules

Classify each new module in the register, give it a purpose/navigation entry and extend affected routes. Keep detailed rules canonical; references and short reminders should replace duplication. Individual prompts are authoritative; generate the combined pack and load only one representation. Record phase progress rather than assuming an old prompt still needs execution.

Never silently raise budgets, weaken checks or hide evidence to obtain a pass. A changed budget/invariant needs explicit owner direction and a dated decision with before/after measurements and rationale; update the contract and checker together. These rules do not authorize hardware purchases, contacts, payments, licence acceptance or external publication.

## Gate behavior

`check` is read-only and uses current working files. `check --staged` reads Git-index content and uses the staged checker in the commit hook. Both validate generated freshness, active local links, references, classification, immutable history and common-context size. The hook reports actionable failures and never edits files. It does not run expensive simulations or require local copyrighted/waveform bytes. Install it in every new/restored checkout. Checks remain local; no CI or scheduled jobs are added.

After each completed research batch, update inventories/indexes, verify declared hashes, capture a private backup with idle evaluators and validate restoration. Fast checks report local preservation separately; a fresh clone remains usable while explicitly missing restoration-only material. Full preservation requires an independent persistent owner-controlled copy and successful restore for the declared current evidence set. Changes invalidate stale coverage; incomplete coverage remains visible.

## Backup and compatibility

Use explicit evidence allowlists and retain notices/acquisition records. Exclude credentials, caches and runtime installations. Capture a Git-history bundle, tracked working files, author-selected project files and allowlisted ignored evidence. Reject changing inputs, unsafe paths and existing restore contents. Private local attestations retain destinations outside Git. Reacquisition/reruns are not recovery of original evidence. Keep existing scientific CLI, paths, record formats, original snapshots and Git history compatible.

Pre-existing source gaps are documented in [the dated ledger](docs/LEGACY-EVIDENCE.md). Protect available bytes with an explicit incomplete capture; retain missing declarations and report preservation as incomplete. Never invent snapshots or silently accept newly missing files.

The [dated implementation validation](docs/VALIDATION.md) records demonstrated checks and remaining limits. Re-run checks after changes rather than treating that audit as a current guarantee.
