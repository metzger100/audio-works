# Standard parts and availability policy

**Core repository principle — owner requirement, 2026-10-05:** implement designs with standard, documented, currently obtainable parts. Performance and reproducibility must survive ordinary production variation. A design whose performance depends on an unavailable, selected or undocumented specimen is not a reproducible build.

This principle applies across Audiotech projects, including Meridian, and to agent instructions, topology engineering, optimization, comparison reports and future build guidance. Project-specific requirements may strengthen it; agents must not silently relax it.

## Standard components and repeatable construction

- Use ordinary off-the-shelf passives, documented current-production semiconductors and practical packages. State actual manufacturer/part number, nominal value, technology, rating, tolerance and package where they affect behavior. Prefer supported parts with dependable supply and practical substitutes or additional sources.
- Do not make NOS, discontinued stock, unidentified marketplace parts, custom-selected specimens, hand-matched transistors or undocumented individual characteristics prerequisites of an intended build. Historical parts and ideal components may remain explicitly labelled research controls.
- Establish performance through topology, feedback, resistor ratios, controlled bias and tolerance to documented device variation. Meridian prohibits individual device selection, matching and hidden per-unit trimming. Buying a batch to select a few favorable specimens is not an acceptable sourcing strategy.
- Precision, low-leakage or other specialist components remain possible when their measurable function justifies them. Document the need, realistic production variation, price and obtainable exact variant; a boutique label is not evidence of benefit. The specified Arienne capsule remains Meridian's research input. A custom PCB, enclosure or acoustic structure is a separate documented fabrication decision; it does not excuse an inaccessible electronics BOM.

## Evidence of availability

For current private DIY projects, intended build parts must be orderable by a private individual in the required small quantities with delivery to Germany. German/EU and international retail routes remain eligible; country of manufacture alone does not determine suitability.

Record dated evidence for exact part/variant/package, supplier URL, lifecycle, stock/orderability, private-customer access, Germany delivery, minimum order quantity, pack size and lead time. A catalogue listing or a typical SPICE model is insufficient. Identify another independent source or a practical substitute where feasible. Expose single-source dependence and unknowns; a similarly named part is not an electrically validated substitute.

Availability is a dated observation, not a promise of future stock. Refresh evidence before a purchase recommendation or build release. Preserve scientifically interesting architectures with sourcing gaps, but mark their implementations unverified for procurement. Resolve unavailable, obsolete or undocumented implementation dependencies before prototype selection or recommending their construction. Preserve the family while investigating an obtainable implementation.

## From optimized values to a buildable BOM

Continuous numerical optimization may identify useful value regions. Before presenting an implementation as buildable, translate them into actual obtainable nominal values and component combinations. Use standard preferred-value series where practical; the specific tolerance, voltage rating, package and technology must also be obtainable. An arbitrary high-precision simulator value is not a parts specification.

Preserve the continuous proposal, create a traceable implementation revision, and re-run the complete applicable qualification suite with the actual nominal values, documented tolerances and relevant parasitics, leakage, noise and temperature behavior. Recheck substitutions and series/parallel combinations, including changed component count, cost and layout effects. Do not retain an ideal-value performance claim as if it described the realized BOM. Keep missing behavior explicitly unqualified.

## German delivered cost and purchasing

Compare EUR costs at the quantities needed for the intended finished equipment. Include actual pack/MOQ quantities, basket-level shipping, applicable taxes/import costs and fees; expose unknown charges and avoid bulk-price assumptions. Seek inexpensive precision parts where useful, while preserving performance and reproducibility. No numerical spending ceiling is established; show cost separately from engineering merit.

Meridian's [Germany procurement contract](meridian/lab/research/procurement_germany.md) supplies the detailed evidence rules. Parts purchases must serve the finished project; unused comparison parts, selection batches or extra capsules need a concrete planned use and owner decision. Research and documentation authorize no purchase, supplier contact or payment.

## Evidence states and other gates

Keep simulation merit, procurement readiness, patent screening and physical qualification separate. Standard parts and good availability do not establish patent clearance; the [mandatory patent policy](PATENTS.md) also applies. Neither affordability nor an attractive simulation result can override a missing implementation prerequisite.

This policy adds repository instructions and review requirements. It does not implement an automatic stock checker or certify any current BOM. Availability, price and realized-part qualification must be established through dated candidate-linked evidence in subsequent research.
