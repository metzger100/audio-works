<!-- SPDX-License-Identifier: CERN-OHL-S-2.0 -->
# Diverse prerequisite feature review — 16 October 2026

Internal numerical research for Germany; no prototype, manufacture, supply or publication decision. [Policy](../../../../PATENTS.md) and [source methods/queries](../architectures/diverse-source-notes-001.md) govern. Technical merit is separate from legal claim-feature comparison. No clearance or design-around is established.

| Official inspected publication | Claim-level question | Exact implementation / preliminary feature distinction |
| --- | --- | --- |
| [EP2675188A1, pp8–9 claims1/13](https://data.epo.org/publication-server/rest/v1.2/publication-dates/20131218/patents/EP2675188NWA1/document.pdf) | Inverting amplifier, sensor and feedback capacitor in series between output/input, voltage source at their intermediate node | 0012/0024 and0014 put feedback C directly from output to sensing input; capsule has a separately fed backplate. This appears structurally different from the specified sensor/feedback-C series path, but broad interpretation/equivalents and actual granted/amended claims are unexamined. Changing Cf alone is no distinction rationale. |
| [EP2002273B1, claim1, dependents4/8](https://data.epo.org/publication-server/rest/v1.2/patents/EP2002273NWB1/document.html) | Detection electrode, amplifier, bootstrapping, discrete source/drain/gate preamplifier; drain bootstrap and cascode; guard/neutralization and DC restoration limitations | 0010 uses CMOS macro followers and a driven guard/bias bootstrap; it has no explicit discrete cascode/drain-bootstrap input stage. A future JFET cascode/guard concept0003 is a closer feature flag and requires detailed mapping. The BJT-only charge controls do not implement source/drain/gate preamplification. No family is declared cleared. |

EP2675188A1: applicant austriamicrosystems AG; filing12June2012, application12171634.4, published18December2013; classifications H04R19/04,H03F1/34. The original A1 front page supplies those dates, not an asserted earliest family priority or current right. Granted/amended claim retrieval was not established.

EP2002273B1: University of Sussex; application07712718.1, PCT/GB2007/000490, filed13February2007, priority21March2006 GB0605717, WO2007/107689, grant publication20August2014; G01R29/12,G01R19/00. These publication facts do not establish current DE validation, renewal, enforcement or term. The official PDFs are retained privately with SHA256 in the source ledger; the HTML aids claim reading.

Official register attempts on16October2026 at [EP12171634](https://register.epo.org/application?number=EP12171634) and [EP07712718](https://register.epo.org/application?number=EP07712718) failed through the web provider. No status is inferred from age, an A1/B1 code or a missing response. DPMA/DEPATISnet, WIPO family/pending coverage and broader claim searches remain incomplete. Material interpretation/equivalents/status uncertainty needs professional review before affected implementation gates.

| Structural alternative | Technical falsification | Separate claim-feature question |
| --- | --- | --- |
| BJT continuous DC current cancellation plus small charge Cf | Base-current shot/flicker and actuator noise may defeat LF budget even when DC is cancelled | Active reset/current-restoration claims need new search; a BJT label alone resolves nothing |
| Quiet fixed-reference guard for inverting charge input | Reference noise/stray C and finite reset authority | Examine guard/reference claims; removal of tracking feedback is a concrete feature difference, not yet a design-around |
| Fully floating differential CMOS island | Terminal translation and common-mode output/power compliance | Floating/common-mode power and differential sensing claims remain unexamined |
| Bipolar/transformer synchronous bridge | Winding loss, mixer noise folding, oscillator power and electrostatic back-action | Carrier bridge/synchronous detector families still require official searches and exact hardware mapping |
| Photoelectric slow DC actuator | Dark-current noise, light coupling, drift, authority and dynamic current | New photo-servo source is a technical lead; disclosure/open access implies no patent licence |

The new isolated fixtures are explicitly ideal mathematical controls. They are not claims of obtainable implementation or patent-risk resolution. Candidate hash/parent identities and finite experimental versions are frozen in the new batch's prior/plan manifests. Existing comparison001 and focused001 flags remain authoritative and unaltered. All affected prototype/manufacture/build-publication holds remain.
