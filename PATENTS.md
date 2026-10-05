# Patent non-infringement requirement

**Owner requirement, 2026-10-05:** this repository and its project implementations must avoid infringement of third-party patents. This is a mandatory design, implementation and release constraint, alongside engineering performance, reproducibility and practical procurement.

The requirement applies to proposed hardware, software, signal-conversion mechanisms, power/bias arrangements, manufacturing methods and published implementation/build guidance where patent rights may be relevant. It is a project requirement, not a statement that every repository artifact has already been legally cleared.

## Claims and territory determine the review

Screen relevant claims against the actual implementation and intended activities. For European patents, claims determine the extent of protection, interpreted with the description and drawings. [EPC Article 69](https://www.epo.org/en/legal/epc/2020/a69.html).

Record territorial scope and current rights status. Patent rights are territorial; the DPMA describes German patent rights as effective in Germany. European rights also require attention to the applicable state and enforcement framework. [DPMA patent-protection overview](https://www.dpma.de/english/patents/patent_protection/index.html), [EPC Article 64](https://www.epo.org/en/legal/epc/2020/a64.html).

Start with Germany and relevant European rights for the current project. Add other territories when intended manufacture, use, supply or distribution makes them relevant. Use DE, EP, US and WO publications to find related families as appropriate, but map each actual right to its territory; a family-search route is not a worldwide clearance.

Original invention, an unfamiliar schematic, changed component values, a supplier application note, public disclosure, an open-source licence or private DIY intent must not be treated as automatic patent clearance. Patent review is separate from copyright/model-redistribution permission and engineering qualification.

## Required screening evidence

For each promising implementation, and before advancing it through the gates below:

1. Define the exact candidate/version, implemented features, intended activities, territories and review date. Identify features such as charge/current sensing, bootstrapping, floating/differential sensing, servos, common-mode power extraction, output drive and carrier demodulation.
2. Record reproducible feature/classification searches in official patent databases and registers. Inspect potentially relevant families, granted and amended claims and relevant pending applications. Search results or visual schematic resemblance alone do not establish claim coverage.
3. Create a claim-element mapping to the candidate. Include relevant independent claims, dependent limitations and uncertainty about interpretation or equivalents. Preserve reasons for both apparent overlap and apparent distinction; refer material uncertainty for professional review.
4. Record publication/grant identifiers, family, priority and filing dates, territory, official status source/date, term/status evidence and any licence/authorization relied on. Never infer expiry or freedom to operate solely from an old priority date, a third-party status badge or one inactive family member.
5. Distinguish expired/non-enforceable prior art in a specified territory, no blocking claim identified within a defined search, potentially relevant claims, unresolved risks and documented resolutions. Record search limits and unexamined areas. These states do not constitute a blanket non-infringement guarantee.
6. Revisit the mapping after structural changes, relevant implementation substitutions, changed territories or new status information. Keep the original evidence and decision history.

## Implementation and release gates

- Add early feature-level patent flags as architecture candidates become concrete. Comprehensive claim/status screening remains a separate research track; it must be completed before selecting an affected implementation for prototyping, manufacture or publishing its implementation/build guidance.
- A credible unresolved potentially blocking claim risk places the affected feature/implementation on hold at those gates. Preserve experiments and research memory; do not erase results or disguise a patent-dependent design as a different family.
- Resolve a hold through an evidence-backed alternative, applicable documented authorization/licensing or a suitable professional assessment. Any authorization must match the implementation, activities and territory. Contact, payment, licence acceptance and external publication require their own authorization; this policy does not grant them.
- Assess the revised alternative against claims and re-run affected engineering tests. A cosmetic redraw, renaming or resistor change is not a substantiated design-around.
- Continue unaffected research and documentation. Do not represent an internal research record or unscreened benchmark as a cleared implementation or public build recommendation.
- Record the screening state alongside simulation, procurement and physical evidence. High performance, novelty, cost or a passing SPICE suite cannot override a patent hold.

## Project records and reporting

For Meridian use [the patent track](meridian/lab/research/patents/README.md) and its [register](meridian/lab/research/patents/register.yaml). Preserve candidate-linked searches, claim mappings, sources, review dates, unresolved cases and resolution evidence. Capture the patent status and scope in comparison reports and release/prototype decisions.

Agents may gather evidence and flag risk; they must not issue a legal non-infringement opinion or label a design globally “patent safe.” Material interpretation, coverage or status uncertainty requires appropriate professional review before releasing a held implementation. Do not treat the absence of discovered patents as proof that none apply.

Current status: this policy has been added; candidate-level freedom-to-operate screening has not been completed. No patent clearance is asserted. The policy is an instruction and review gate; an automated legal determination has not been implemented.
