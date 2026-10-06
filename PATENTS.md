# Patent non-infringement requirement

**Owner requirement, 2026-10-05:** avoid third-party patent infringement as a mandatory design, implementation and release constraint alongside engineering, reproducibility and procurement.

Covers proposed hardware, software, signal conversion, power/bias, manufacturing and published implementation/build guidance where patent rights may be relevant; existing artifacts are not asserted cleared.

## Claims and territory determine the review

Screen claims against the actual implementation and intended activities. European protection is determined by claims interpreted with the description/drawings: [EPC Article 69](https://www.epo.org/en/legal/epc/2020/a69.html).

Rights are territorial. Record current status, applicable states and enforcement framework: [DPMA overview](https://www.dpma.de/english/patents/patent_protection/index.html), [EPC Article 64](https://www.epo.org/en/legal/epc/2020/a64.html).

Start with Germany/relevant European rights; add territories for manufacture, use, supply or distribution. DE/EP/US/WO family searches are not worldwide clearance; map each right to its territory.

Originality, unfamiliar schematics, changed values, application notes, disclosure, open licensing and private DIY are not automatic clearance. Keep copyright/model redistribution and engineering qualification separate.

## Required screening evidence

For each promising implementation, before advancing through the gates below:

1. Define candidate/version, features, activities, territories and date: charge/current sensing, bootstrapping, floating/differential sensing, servos, common-mode power extraction, output drive and carrier demodulation as relevant.
2. Record reproducible feature/classification searches in official databases/registers. Inspect relevant families, granted/amended claims and pending applications; results or schematic resemblance alone do not establish coverage.
3. Map claim elements to the candidate, including independent claims, dependent limitations, interpretation/equivalents uncertainty and reasons for apparent overlap/distinction. Refer material uncertainty for professional review.
4. Record publication/grant IDs, family, priority/filing dates, territory, official status source/date, term/status evidence and relied-on licences/authorizations. Old priority dates, third-party badges or one inactive member do not establish expiry/freedom to operate.
5. Distinguish territorial expired/non-enforceable prior art, no blocking claim identified within a defined search, potentially relevant claims, unresolved risks and documented resolutions. State search limits/unexamined areas; none is a blanket guarantee.
6. Revisit mappings after structural changes, relevant substitutions, territory/status changes. Preserve original evidence and decisions.

## Implementation and release gates

- Flag features early as candidates become concrete. Complete the separate claim/status screening before affected prototype selection, manufacture or implementation/build publication.
- Hold affected features/implementations with credible unresolved potentially blocking risks. Preserve experiments/research memory; do not erase results or disguise patent-dependent families.
- Resolve holds through evidence-backed alternatives, applicable documented licensing/authorization or suitable professional assessment. Authorization must match implementation, activities and territory. Contact, payment, licence acceptance and external publication require separate authorization.
- Assess alternatives against claims and rerun affected engineering tests. Cosmetic redraws, renaming or value changes do not substantiate a design-around.
- Continue unaffected research/documentation. Internal records and unscreened benchmarks are not cleared implementations or public build recommendations.
- Report screening alongside simulation, procurement and physical evidence; performance, novelty, cost and passing SPICE cannot override holds.

## Project records and reporting

Meridian's [patent track](meridian/lab/research/patents/README.md) and [register](meridian/lab/research/patents/register.yaml) retain candidate-linked searches, mappings, sources, review dates, unresolved cases and resolutions. Include status/scope in comparisons and prototype/release decisions.

Agents record evidence/risks, not legal non-infringement opinions or global “patent safe” labels. Material interpretation, coverage or status uncertainty needs appropriate professional review before held releases. Finding no patents does not prove none apply.

**Current status:** candidate-level screening is incomplete; no clearance asserted. This review gate does not automate legal determinations.
