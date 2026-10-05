# M100 Meridian

M100 Meridian is an original, high-performance condenser microphone research and development project for private DIY use in Germany. It is not a commercial product at this stage.

**Core parts constraint:** use standard, documented, currently obtainable components, privately orderable in small quantities for delivery to Germany. Follow the [repository component policy](../COMPONENTS.md). Numerical proposals must become actual BOMs and pass requalification with obtainable values, tolerances and device variants; sourcing gaps remain explicit.

**Mandatory patent constraint:** the design and its published implementations must avoid third-party patent infringement. Follow the [repository patent policy](../PATENTS.md): examine candidate features against relevant claims, territories and official status; resolve credible potentially blocking risks before selecting a prototype, manufacturing or publishing implementation/build guidance. Open-hardware publication remains subject to this requirement. Patent clearance has not been established.

**Active mission, 2026-10-05:** build a reproducible, simulator-driven analog research environment for the Arienne Audio Flat K47 Cardioid/Omni K47FRB, with open-hardware publication as a future objective. [Run the laboratory](lab/README.md) · [Formal specification](lab/spec/microphone_spec.yaml) · [Phase 0 report](lab/research/phase0_report.md). Earlier capsule-choice/design gates below are historical; the owner's new mission authorizes modeled electronics research across explicitly uncertain parameters. It does not authorize a purchase or select a production topology.

The microphone should serve accordion, ukulele and other acoustic instruments, professional voice-over, and distant concert recording of a male choir. The priorities are low noise, accurate transients, detail, smooth off-axis response, and a natural, slightly warm balance. Warmth should come from acoustic response and restrained voicing; transparency takes precedence over added distortion.

## Engineering targets

| Property | Initial target |
| --- | --- |
| Self-noise | Ideally ≤7 dBA, lower where physically realistic |
| Sensitivity | Sufficient for quiet instruments and distant choir recording; exact value pending capsule selection |
| Maximum SPL | Approximately ≥135 dB SPL, with a stated distortion criterion |
| Distortion | Low throughout the useful operating range |
| Output and supply | Balanced XLR, 48 V phantom power |
| Interference rejection | Excellent RF immunity and common-mode rejection |
| Acoustics | Smooth frequency response and consistent polar behavior across frequency |

These are system targets, not assumed capsule specifications. They may be revised when measurements reveal a better tradeoff.

## Availability and implementation principles

The [standard-parts policy](../COMPONENTS.md) is a mandatory implementation principle, alongside patent non-infringement. Prefer ordinary passives and current documented semiconductors; unavailable, obsolete, selected or undocumented parts must not become build prerequisites. Preserve theoretical concepts while investigating obtainable implementations.

Parts must be purchasable by a private individual in small quantities with reasonable delivery to Germany. German and European distributors, microphone DIY and repair shops, eBay, AliExpress, and other international retail sources are all eligible. Provenance, documentation, repeatability, shipping, tax, and returns matter more than country of manufacture.

**Owner clarification, 2026-10-04: purchases must serve the finished project.** Do the comparison primarily through online evidence. Do not buy competing capsules, reference parts, or surplus specimens merely for experimentation or self-selection when they would subsequently sit unused. The default capsule quantity is one for the intended M100; a pair requires an intended two-microphone use. Any additional part needs a concrete planned use and an owner decision. Low price alone does not justify an experimental purchase.

Complete information may be unobtainable. Explicitly separate uncertainties that can be measured on the chosen part and accommodated during development from intrinsic performance risks that later electronics cannot reliably remedy. A purchase may proceed with acknowledged unknowns, but it must be a reasoned choice of the intended final component, not a comparison program funded by spare parts.

Performance should come primarily from topology, acoustics, layout, controlled bias, feedback and measurement. Prefer ordinary passives, current documented semiconductors and designs tolerant of manufacturer variation. **The new mission prohibits individual device selection, matching and hidden per-device trimming.** Initial tolerance/scenario analysis now explicitly brackets unknown capsule/device parameters; measured populations must replace assumptions before yield claims.

## Current milestone and decision gate

**Capsule mission input confirmed for simulation:** Arienne Audio Flat K47, Cardioid/Omni K47FRB. The prior recommendation and procurement research remain below. No purchase or physical measurement has occurred.

- [M100 Capsule Recommendation — Revision 2](research/M100%20Capsule%20Recommendation%20%E2%80%94%20Revision%202.md): current single-capsule recommendation, additional measured and listening evidence, medium electret alternatives, procurement uncertainties, and remaining performance risks. This is the current decision document.
- [M100 Capsule Survey — Revision 1](research/M100%20Capsule%20Survey%20%E2%80%94%20Revision%201.md): broad market survey, eight candidates, three alternatives, evidence gaps, procurement costs, and characterization of the chosen capsule. The purchasing recommendation was amended on 2026-10-04 to remove comparison purchases.
- [Engineering decision log](DECISIONS.md): decisions, provisional recommendations, and unresolved gates.
- [Reference archive](research/reference-datasheets/README.md): original public datasheets used in the survey, with source URLs and hashes.

Availability and prices were researched on **4 October 2026**, Europe/Berlin. Website stock statements are observations, not reservations. No capsules have been ordered and no physical measurements have been performed by this project.

The recommended capsule's intrinsic noise, acoustic overload limit, and current-batch angular response remain insufficiently documented. Its restrained voicing, pattern options, retail availability and price support the recommendation; they do not prove the ≤7 dBA or approximately ≥135 dB SPL system targets. Any purchase is of the intended final component, with acknowledged residual risks.

**The earlier stop gate is superseded for simulation research by the owner's 2026-10-05 mission.** Begin with formal specification, executable capsule/P48 models and tested research infrastructure; investigate architectures only after that works. Capsule safety/mechanics, procurement and physical characterization remain unresolved. No production topology, PCB or prototype is selected.

## Planned stages

Formal research specification → capsule/P48 environment → automated framework → strong conventional benchmarks → diverse topology generation → numerical optimization → quality-diversity search → manufacturing robustness → separate prior-art/patent screening → prototype candidates → physical measurement/model correction. Physical capsule characterization can replace modeled assumptions as it becomes available. PCB implementation follows topology maturity.

Record patent flags when concrete features emerge; complete the separate claim/status review before an implementation advances to the affected prototype or publication gate. Patent holds do not change electrical test thresholds or erase scientifically useful experiments.

## Research conventions

Separate verified observations, manufacturer/seller claims, community reports, and unknowns. Published complete-microphone or test-fixture specifications must not be silently assigned to a bare capsule. Record exact variants, batches, measurement conditions, and assumptions. Preserve original data alongside later measurements and keep the decision log current.

The existing lowercase `meridian/` directory is used consistently for the project, including `meridian/research/`.
