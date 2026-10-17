<!-- SPDX-License-Identifier: GPL-3.0-or-later -->
# Candidate-linked patent screening 001

Compiled **17 October 2026** from searches on **16–17 October 2026** and official observations on **16 October**. M100 Meridian MIC-34-M/MIC-34-C, K47FRB under P48. **Phase 8 is partially executed; all affected prototype, manufacture and implementation/build-publication gates remain held.** No prototype selection or legal non-infringement opinion follows.

[Machine entry](candidate-screening-001.json) · [Exact versions/features/activities](candidate-versions-001.json) · [Claim elements](claim-mappings-001.json) · [Territorial records](territory-status-001.json) · [Official queries](queries-official-001.json) · [Web queries](queries-web-001.json) · [Sources/hashes](sources-screening-001.json) · [Holds/review questions](holds-screening-001.json) · [Prior-record audit](screening-audit-001.json).

## Implementation and execution audit

Read reporting-route authority, the continuation contract, comparison 001, current netlists and resolved BOM/topology includes, all existing patent-feature records and actual Prompts 6–10 findings. Inventoried all 25 candidates; mapped the nine versions below. Complete hashes, per-reference BOM identities, netlist lines and activity/territory bindings are in the version matrix. No circuit, BOM, model, threshold or budget changed; no electrical tests ran.

| Candidate | Actual mechanism | Netlist SHA256 prefix |
| --- | --- | --- |
|0019|Fixed-divider/source-degenerated JFET, final backplate bypass, four 47µF/output leg|1fef5a2021b4|
|0017|Same mechanism, two 47µF/output leg|06d104a8f60e|
|0023|Discrete source-current servo, unfiltered final backplate, four 47µF/output leg|d251a442c098|
|0025|0023 child: actual final backplate filter with loss/inductance/insulation|cc607ebd7e74|
|0012|BJT differential charge input; direct 100nF feedback; two 1MΩ parallel continuous resets|f99b52316c84|
|0024|0012 child: additional series 100pF feedback capacitor; continuous reset retained|65bab5628d9b|
|0010|CMOS follower, separate driven guard, AC-bootstrapped high-resistance bias return|72312902d040|
|0014|CMOS charge input; direct 100pF feedback and 1GΩ continuous reset|cb9c764bd9d0|
|0013|Ideal anti-phase floating bridge, voltage buffers, synchronous product, passive lowpasses, ideal outputs|7234e1621376|

All have two 2.2kΩ P48 extraction paths, raw filtering, divider/NPN emitter-follower rail, reference and passive polarization networks. Real output candidates use two driven legs; symmetry and impedance balance are engineering questions, not established patent distinctions.0012/0024 use the bipolar pair's two outputs; the other real-output variants add a phase inverter.0013 has **Eoutp/Eoutn ideals**. The original inaccurate carrier real-output flag and its comparison 001 correction both remain intact.

JFE150 candidates actually connect VCH/VCL protection terminals to rail/g; the vendor model contains internal ESD blocks. A 17 October complementary protection query added unreviewed US8170238/US9276531 leads. No extra external protection, fault-reset or custom capsule-manufacturing circuit was added. IC internals, supplied-component rights and physical capsule construction remain separate unknowns. Parts/library changes and isolated floating/charge/carrier controls in Prompts 6–10 are not additional integrated candidate children.0025 is the new integrated child from Prompt9;0024 is retained from optimization.

Earlier records contain flags/prepared queries, component-linked leads and four limited official-document inspections across focused/diverse reports: EP1585365B1, EP2590434B1, EP2675188A1 and EP2002273B1. None established complete candidate screening or current DE status. The earlier “two inspections” readiness shorthand omitted the later diverse pair. This report adds evidence without relabelling those original flags.

## Executed searches and access limits

Executed 34 complementary web discovery queries, 15 DEPATISnet keyword/number searches, one DEPATISnet family search and 13 matching DPMAregister record inspections. Counts describe operations/documents, not screened rights. The official ledger records fields, UTC observations, filters, accessible results/samples, negative searches and selection errors; the source ledger records exact HTTP retrieval times, MIME, redirects and byte hashes. Broad result lists were not fully exported or claim-reviewed.

Refreshed the official service/coverage routes through [DPMA document research](https://www.dpma.de/english/search/depatisnet/index.html), [German register](https://www.dpma.de/english/search/dpmaregister/index.html), [EPO services](https://www.epo.org/en/searching-for-patents), [WIPO](https://patentscope.wipo.int/) and [USPTO](https://www.uspto.gov/patents/search). DEPATISnet provides multinational publication research; DPMAregister supplies German legal/procedural records. EPO publication-server PDFs were accessible. Espacenet and the European Patent Register reached security interstitials/403 responses. PATENTSCOPE's exact WO2011054671 search reached an image challenge. USPTO Patent Center was blank and six official PDF endpoints returned403. No challenge was solved or access control bypassed. These are coverage gaps, not negative patent findings.

Complementary terms covered phantom/Phantomspeisung, fixed bias/source degeneration, current servo, reference/backplate filtering, differential/impedance-balanced output, charge/reset, driven guard/bootstrap, bridge/anti-phase/synchronous demodulation and analogous electrometer/capacitance/displacement/MEMS mechanisms. Inventor/assignee leads included Steiner, Sussex/Prance, Sennheiser/Staat, Audio-Technica and Logitech. IPC H04R19/04,H03F1/34 came from relevant publications; G01R29/12 from EP2002273 and G01R27/26 from the charge-family divisionals. CPC H03F3/1855 was visually confirmed on the mirrored US12021490 cover and used in a complementary web query. Classification searches are scoped, not complete searches of every subclass.

Examples: broad “microphone phantom” returned 3,254 hits, first 100 inspected; EP+H04R19/04+“charge feedback” returned 32; EP+“microphone servo” returned 173, first 100 inspected. The narrow DE?+English phantom query returned no documents; the German Phantomspeisung query returned 13. Same-paragraph wording and language explain why that negative cannot establish absence of rights. Guard/electrometer, reset and analogous demodulation searches returned additional unreviewed leads. Newer grants/applications and the EP19153261.3 divisional remain explicitly open.

The exact US12021490 family button returned US11711058B1, US12021490B2, US20230246604A1 and US20230261617A1. The mirrored cover confirms a continuation and terminal disclaimer; it does not establish current maintenance, disclaimer effect or expiry. DE/EP/US/WO searches are not worldwide clearance. A WO publication is not an enforceable worldwide right; EP designation alone does not establish German effect.

## Official claims and German observations

Retained 15 PDFs from official publishers, including the superseded EP2675188A1, and mapped 14 scoped official publication claim sets. Nine US mirrored publication sets were inspected provisionally; official US originals/current status remain unverified. Exact publication versions and dependent limitations are in the claim tables. Description/figure context was used; representative charge, electrometer and German RF drawings were rendered and inspected. Circuit resemblance or novelty supplies no conclusion.

| Official publication(s) | Claims inspected | Exact-version distinction / remaining question |
| --- | --- | --- |
|EP2675188B1; EP2955936B1; EP3229493B1; EP3509323B1|1/11;1/13;1/11;1/9, plus material dependents|All require sensor/Cf series feedback. Current charge graphs are out→Cf→f, capsule f–b; they do not demonstrate out→Cf→b→capsule→f. Further mandatory limitations differ: lowpass bias; charge pump; anti-parallel source diodes; further-input capacitor. Construction/equivalents/current amendments remain open.|
|EP2002273B1|1, dependents2–8|0010 has guard/bootstrap functions; no explicit inserted discrete FET preamplifier with drain bootstrap and source/cascode connection. IC internals/equivalents/electrode construction unresolved.|
|EP2174416B1|1, dependents2–12|Bias bootstrap is present in0010; additional tuned narrow-band feedback/filter is not implemented.|
|EP2648333B1|1/10, dependents2–9|No identified feedback amplifier→voltage-offset adder→anti-parallel diode→input chain. Additional divisional not yet resolved.|
|EP2330831A1|1/7/16 and dependents|0023/0025 source-current servo raises microphone/interface-boundary and separated AC/DC-path questions. IC/digital limitations are absent in some claims, not all. Related US9392361 grant not obtained officially.|
|DE102010000686B4|1/2|0013 has ideal bridge/demodulation functions, but no HF coil/transformer or physical stabilizer with mandatory green LED. Broader US8515099 claim 1 lacks that green-LED restriction.|
|EP2974369B1|1/14 and dependents|Continuous Rf reset does not implement mute/fault detection, timer, reset threshold and recovery cancellation.|
|EP3114857B1|1, dependents2–12|Noncircular membrane, directional stress and compensating backplate construction cannot be resolved from electrical capsule parameters. No custom capsule manufacture implemented.|
|EP1585365B1; EP0096778B1; EP2590434B1|1 and dependents;1 and dependents;1/8 and dependents|Digital polarization correction absent; power-converter scope distinguished from divider/follower; dynamic-microphone/two-coil-pair filter structure absent. Each is a scoped finding only.|

DPMAregister observations on 16 October 2026 show the combined label **“Anhängig/in Kraft”** for the four charge grants, EP2002273, EP2174416, EP2648333, EP3114857 and DE102010000686. This label is retained exactly; it is not an enforceability opinion. [German record2675188](https://register.dpma.de/DPMAregister/pat/register?AKZ=E121716344) and the full territorial ledger identify the precise national entries, dates and procedural events.

Explicit German events support narrower prior-art/status findings: [EP1585365's DE right](https://register.dpma.de/DPMAregister/pat/register?AKZ=E044500734) expired by term on 30 March 2024; [EP0096778's DE right](https://register.dpma.de/DPMAregister/pat/register?AKZ=E831052477) on 26 May 2003. [EP2974369's DE record](https://register.dpma.de/DPMAregister/pat/register?AKZ=E147210710) records nonpayment lapse on 1 October 2020. EP2330831's record is nonpending/lapsed; it does not decide its priority/PCT/US or other family rights. EP2590434 status remains unverified. No expiry was inferred merely from age, a third-party badge or a fee-due date. General term rules are context, not substitutes for individual status/term evidence.

**No blocking claim identified within the executed scope** for the mapped official independent claims whose required circuit relationships appear absent. This does not resolve physical capsule claims, broad/mirrored US claims, equivalents, unreviewed documents, pending rights or unseen amendments. The wider Phase 8 requirement remains incomplete. In particular, US8644529 independent 1/16 broadly concern differential capsule converters:0013's two ideal buffers require review, despite the absence of the narrower FET implementation. US12021490's mirrored independent set is1/6/15; the earlier 1/11 handoff was a lead, and 11 depends on 6.

## Holds, alternatives and evidence needed

The matrix records intended private noncommercial Germany use and separate hypothetical DE/outside-DE manufacture, import/supply/distribution and internet build-guidance scenarios. Actors, manufacturing/destination countries and actual publication content remain unresolved. [PatG9](https://www.gesetze-im-internet.de/patg/__9.html), [10](https://www.gesetze-im-internet.de/patg/__10.html) and [11](https://www.gesetze-im-internet.de/patg/__11.html) require activity-specific interpretation; no private-DIY, research, open-hardware or exhaustion assumption releases a hold.

Exact holds: **all nine** common P48/regulation/output and capsule/activity coverage; **0023/0025** source-current servo; **0012/0024/0014** charge feedback/reset; **0010** driven guard/bootstrap; **0013** floating bridge/demodulation and unfinished hardware; **0017/0019/0023/0025** component-internal protection provenance. The hold register ties each to documents, unresolved limitations and professional-review questions.

Alternatives to investigate are fixed bias instead of source-current servo, passive insulation instead of tracking guard, voltage instead of capacitive-feedback sensing, direct sensing instead of RF demodulation, and materially different power/output mechanisms. They are not established design-arounds.0025's filter and0024's Cf combination were remapped; value/package/name changes alone resolve nothing. Every new structural child needs new claims research and full applicable engineering requalification.

Resolve holds with current official amended/granted/pending claims and national effect, complete relevant family/divisional/citation chains, professional assessment of material construction/equivalents/status/activity uncertainty, and reliable capsule construction/provenance. Preserve all engineering failures and unaffected research. No holder contact, licence acceptance, payment, purchase or external publication is authorized.

## Preservation and reproduction

Original PDFs, HTML, mirrors, notices, redirects, challenge/403/expired-session failures and provider receipts stay under the existing ignored architecture-source boundary. Public ledgers retain hashes and relative references; GitHub does not restore those private bytes. Token-bearing DPMA request URLs remain only in hashed private receipts; start at the stable register entry and follow its published-document/full-document links in one normal session. Original failure and successful session PDFs are distinct.

Repeat the field queries at the official entry URLs in the ledgers; changing database contents can change results. Verify originals from the lab with `sha256sum -c results/evidence-20261017T084357Z-cecb52ec.sha256`; resolve structured includes with `meridian_lab.core.read_yaml`. [Validation](../../../../docs/validation/2026-10-17-patent-screening.md) separates new-byte integrity and historical gaps. A 17 October refresh was cancelled before execution; this report asserts the dated 16 October observations only. Refresh official status before a held release. Repository checks validate files/links/hashes, not legal coverage or electrical qualification.
