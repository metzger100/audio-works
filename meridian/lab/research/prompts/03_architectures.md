# Prompt 3 — Implement the first diverse architectural batch

Work in `/home/leobareth/Dokumente/Audiotech/meridian/lab` on the M100 Meridian MIC-34-M/MIC-34-C research project using the Arienne Audio Flat K47 Cardioid/Omni K47FRB under P48.

Read `AGENTS.md`, `README.md`, the parent `../README.md` and `../DECISIONS.md`, `spec/*.yaml`, `research/phase0_report.md`, `research/sources.yaml`, `research/roles.md`, `research/rejected_ideas.md`, `research/discoveries.md`, `research/procurement_germany.md`, the repository `../../PATENTS.md` and `research/patents/README.md`. Inspect the current files and results before changing anything; later work may already have completed part of this task.

Preserve the hierarchy: physics/measurements → SPICE → automated tests → numerical optimization → engineering reasoning → LLM intuition. Work autonomously, create files and run applicable checks. Preserve failed experiments, raw data, source snapshots, seeds and parent relationships. Do not relax thresholds, silently narrow uncertainty ranges, hand-select devices, conceal trimming, purchase parts or contact suppliers. Unknown safe capsule polarization is not a simulated hardware rating. Freeze shared sources before running evaluations. No production topology or PCB is to be selected in this task.

Apply the existing Germany procurement constraints explicitly: parts must be orderable by a private individual in small quantities for delivery to Germany. German/EU and international retail sources remain eligible. Record dated stock/orderability, exact variants, minimum order quantities, pack sizes, lead times and intended-quantity EUR costs including shipping, applicable VAT/import charges and fees. Unknown delivered costs stay unknown or clearly labelled scenarios. Default to one capsule for one finished microphone; do not buy unused comparison parts, surplus specimens or matching services. Record unavoidable pack excess and sourcing risks. Cost remains separate from performance, with no invented numerical spending cap.

Mandatory repository constraint: avoid infringement of third-party patents. Follow `../../PATENTS.md`. Record early candidate-feature flags and dated claim/territory/official-status evidence separately from engineering merit. Before selecting an affected implementation for a prototype, manufacture or publication of implementation/build guidance, complete applicable screening and resolve credible potentially blocking risks. Keep unresolved affected implementations on hold while preserving experiments and continuing unaffected research. Originality, open-source licensing and passing simulations are not patent clearance. Reassess structural alternatives against relevant claims; refer material legal uncertainty for professional review and never issue a legal non-infringement guarantee.

Using the validated device library and qualification framework, implement a first batch that makes meaningful attempts at six competing mechanisms:

1. A strong conventional high-impedance JFET voltage-input reference with production-tolerant biasing.
2. A feedback-controlled JFET architecture with a materially different feedback or bias principle.
3. A guarded/bootstrapped CMOS voltage-input architecture.
4. A CMOS charge-feedback architecture with a defensible DC leakage-control path.
5. A BJT-only current/charge-input architecture exploring the no-FET family.
6. A floating analog capacitance bridge with carrier sensing and demodulation.

Use the persistent Inventor and Engineer roles. The Inventor states the conversion mechanism and falsifiable hypothesis; the Engineer establishes bias, power, loading, gain and balanced output while preserving that mechanism long enough to test it. Neither role may declare performance without evidence. Consult `search/concepts.yaml` and primary cross-domain sources. Known microphone circuits may serve as documented fair references, not copied production designs used to seed the invention search.

For each concept record the nine questions from the topology challenge: sensed quantity, loading, DC bias, gain/impedance transformation, balanced output, expected noise, expected distortion, likely fatal flaw and quickest falsification test.

Create distinct candidate directories with plain DUT netlists, topology metadata, device-model references, parameter bounds/provenance, hypothesis, notes and results. Respect the existing interface or implement a documented, validated backend extension. Register structural children without overwriting parents. First establish operating points and energy/current accounting, then run response, noise and the remaining supported tests. Give the conventional reference equal engineering effort; its initial failure is not evidence against JFETs as a class.

Record potentially relevant patent features, dated search/claim evidence where actually investigated and unresolved scope/status questions per candidate. Mark unscreened implementations honestly and preserve patent holds independently of simulation results. A successful structural experiment does not establish non-infringement.

Provide an intended-quantity BOM for each implementation, linked to dated private-customer Germany supply evidence and an electronics delivered-cost estimate. Expose unavailable parts, pack excess, import/shipping unknowns and substitutes. Preserve interesting unsourced concepts as research, but do not label them build-ready. Revalidate substitutions rather than assuming equivalent performance; never buy the six comparison BOMs under this task.

Use real device behavior for architecture comparisons. Ideal blocks may help isolate a mechanism, but those experiments must remain explicit unqualified controls. Count output-driver noise and current. A common validated output block can provide an initial control, but do not force it onto a mechanism that requires different common-mode or power behavior.

Disclose input-device class, FET presence throughout the audio path and FET use in power circuitry. A BJT input followed by a CMOS amplifier must not be labelled a no-FET audio architecture. Unsupported internal device classes remain unknown.

The carrier branch needs a validated periodic/time-domain noise and demodulation protocol. Do not apply ordinary DC-linearized noise analysis as complete carrier-noise evidence. If the protocol is not ready, preserve a runnable mechanism experiment and mark its qualification incomplete; an unsupported test does not reject the physical architecture.

Deliver the six engineering attempts, preserved simulations and `research/first_architecture_batch.md`. Document physically supported rejection reasons, implementation failures and unresolved model/protocol gaps separately. Update family coverage, hypotheses, discoveries and rejected ideas. Keep all 14 families available. Run `./run verify` after framework/model changes and evaluate each implemented candidate from stable sources. This milestone is completed attempts with honest evidence, not six passing designs.
