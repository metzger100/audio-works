# First six-mechanism architecture batch — 2026-10-09

Internal M100 Meridian MIC-34-M/MIC-34-C research under P48, using the **Arienne Audio Flat K47 Cardioid/Omni K47FRB** assumption envelope. This milestone records engineering attempts, not six passing designs. No production topology, prototype or PCB is selected. No purchases, supplier contacts, matching services, licence acceptance or external publication occurred. All implementations remain unqualified and all prototype/manufacture/build-publication gates remain held.

[Specification](../../spec/microphone-spec.yaml) · [Capsule uncertainty](../../spec/capsule-model.yaml) · [Environment](../../spec/design-constraints.yaml) · [Source register](../sources.yaml) · [Model limits](../devices/device-model-validation.md) · [Persistent roles](../memory/roles.md) · [Concept catalogue](../../search/concepts.yaml) · [All 14 families](../../search/families.yaml) · [Carrier protocol](carrier-protocol.md) · [Dated rationale](first-architecture-decisions.md).



## Inventor and Engineer record



The Inventor uses conversion physics and falsifiable hypotheses from the existing catalogue and [primary cross-domain observations](../architecture_sources/observations_2026-10-09.json). The Engineer supplies bias, power, finite loading, impedance transformation and balanced output without replacing a failed mechanism silently. The persistent roles are the documented workflow, not separate background services. Known microphone/JFET references and the semiconductor datasheets inform fair feasibility checks; no copied production microphone netlist seeded this search.

## Implementation and backend limits



All six initial attempts use actual nominal parts. The power path takes both P48 legs through2.2kΩ resistors, then a divider-fed NPN emitter-follower rail, real divider current and filtered polarization. Ten series1MΩ production resistors realize the10MΩ polarization filter; no unavailable ideal10MΩ value is claimed.47Ω/47µF legs drive the actual cable/preamp fixture. Real models include their output-driver current and stationary noise when that analysis is supported. Different NPN output structures are preserved as children instead of forcing failed CMOS macros onto every mechanism.

## Failures, physical implications and unknowns



Initial OPA-containing attempts0001–0004/0006 failed the operating-point convergence screen. A [preserved initialization probe](../probes/opa_initialization_2026-10-09/results.json) tried explicit nodesets without altering device models/specification; it also failed to produce valid operating-point data. Those are implementation/model failures, not proven impossibility of the input families. The CMOS-with-NPN-output children preserve the CMOS mechanisms long enough to expose the same unresolved macro compatibility. It would be inappropriate to replace the input devices by ideals and report an architecture advantage.


## Procurement and legal gates



[Dated ordinary-part/private Germany sourcing](../procurement/architecture_parts_2026-10-09.yaml) records exact variants, tolerance/technology/rating/package, observed stock/crawl age, MOQ/retail and factory packs, lead times, price and unresolved delivery terms. Each candidate's BOM provides installed and intended purchasing quantities, unavoidable excess (zero only where MOQ1 is evidenced), and an electronics-only cost calculation. Default is one capsule for one finished microphone. Six comparison BOMs are research alternatives, never a purchase basket.

## Qualification records and preservation



The final record tables below are generated from immutable results, including errors and unsupported tests.45 regressions pass after backend/model-framework changes. Evaluation uses seed34047 and16 original-envelope scenarios where the supported suite can reach them; no manufacturing-yield claim follows. All 14 families remain available, with minimal-active-device research still awaiting its own implementation. Final evaluations freeze the same shared source cohort; failure to reach an analysis is recorded rather than assigning a fabricated metric.

## Reading and evidence



This compact view retains findings and limits. Consult the [complete original report](../../../../docs/history/2026-10-09/meridian-microphone/lab/research/first_architecture_batch.md) for all tables, conditions, failures and contemporaneous decisions. [Current evidence hub](../../../../docs/evidence.md) and [scientific contract](../../CONTRACT.md) govern further work. Historical test counts describe the original batch. Current verification is in [repository validation](../../../../docs/validation.md).


## Reading and evidence


This compact view retains findings and limits. Consult the [complete original report](../../../../docs/history/2026-10-09/meridian-microphone/lab/research/first_architecture_batch.md) for all tables, conditions, failures and contemporaneous decisions. [Current evidence hub](../../../../docs/evidence.md) and [scientific contract](../../CONTRACT.md) govern further work. Historical test counts describe the original batch. Current verification is in [repository validation](../../../../docs/validation.md).

## Reading and evidence

This compact view retains findings and limits. Consult the [complete original report](../../../../docs/history/2026-10-09/meridian-microphone/lab/research/first_architecture_batch.md) for all tables, conditions, failures and contemporaneous decisions. [Current evidence hub](../../../../docs/evidence.md) and [scientific contract](../../CONTRACT.md) govern further work. Historical test counts describe the original batch. Current verification is in [repository validation](../../../../docs/validation.md).
