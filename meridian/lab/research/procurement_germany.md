# Germany procurement and cost contract

This document makes the existing owner requirements in `meridian/README.md` and `meridian/DECISIONS.md` D001, D008, D010 and D011 explicit for laboratory work. It adds no numerical spending ceiling and authorizes no purchase or supplier contact.

## Orderability and sourcing

- Recommended implementation parts must be purchasable by a private individual in the required small quantities, with a documented delivery route to Germany. A catalogue entry, bulk price, business-only account, zero-stock listing or obsolete part alone does not establish availability.
- German/EU distributors, specialist DIY/repair shops and international retail sources, including eBay and AliExpress, remain eligible. Do not impose a domestic-only restriction. Record provenance, exact part identity, documentation, counterfeit/traceability risk, repeatability, dispatch location, delivery and returns where they affect the decision.
- For every proposed implementation part, seek at least one current small-quantity Germany-delivery route. Record a second independent route or practical substitute where feasible; expose single-source dependence rather than asserting an unverified alternative.
- Record exact manufacturer/MPN/variant/package, seller URL and check date, stock/orderability, private-customer access, Germany delivery evidence, minimum order quantity, pack size, lead time and lifecycle. Separate a seller's stock claim, a publicly verified ordering route, an estimate and an unknown. Website stock is an observation, not a reservation.
- Preserve scientifically useful architectures when sourcing is unresolved, but mark their procurement readiness separately. Do not promote an unobtainable or unverified implementation as build-ready. NOS, bulk-only, selected or undocumented parts must not become hidden prerequisites.

## Price and delivered-cost evidence

- Use EUR and the quantity actually needed for one intended finished microphone. Record unit price, price-break quantity, tax basis, required purchase quantity and any unavoidable excess from packs/MOQs. Do not apply reel/bulk discounts to a small DIY order.
- Calculate basket-level delivered cost to Germany: actual purchase quantities plus shipping, applicable VAT/import taxes/duties, carrier/handling charges and payment/FX costs where relevant. Verify applicable current rules from official sources when estimating imports; do not assume historical rates, thresholds or classifications are still valid.
- Distinguish tax-inclusive retail prices, net export prices and prepaid taxes. Avoid double counting taxes or shipping. Allocate shipping at the actual order/basket level, not once per BOM line. Show multiple supplier baskets and consolidation choices transparently.
- Record quote/observation date, seller/dispatch information, currency and dated FX basis. Public stock/prices and checkout evidence have different confidence levels. Do not submit an order, supply personal/payment data or contact a seller to complete a quote under this research authorization.
- If German shipping, tax collection or fees cannot be verified publicly, retain unknown fields and explicit scenario ranges. Do not report the shelf price as a confirmed German delivered price or use a favorable shipping guess to rank a candidate.
- Report electronics BOM cost separately from capsule, mounting, connector, PCB, body/headbasket and other implementation items. A partial electronics subtotal is not the complete microphone cost. Keep unpriced items visible.
- No numeric maximum budget has been established in the current mission. Cost is a separate comparison axis; performance and reproducibility remain priorities. Do not invent a spending cap, an acceptable premium or a weighted price/performance winner. Show the measured/simulated benefit and additional delivered cost for review.

## Finished-project use and purchasing

- Research, simulation and documented alternative BOMs do not authorize buying every candidate's parts.
- Default to one Flat K47 Cardioid/Omni capsule for one intended finished microphone. A second capsule requires an intended second microphone; do not buy alternative capsules, matching services or surplus specimens for self-selection.
- Do not recommend bulk orders, additional measurement/reference hardware or comparison parts solely because they are cheap or discounted. Additional purchases require a concrete planned use and an owner decision. Disclose unavoidable pack excess; do not silently treat it as authorized spending.
- Future measurement plans should first consider existing, borrowed or otherwise accessible equipment. Clearly separate any proposed purchase from the scientific measurement requirement. Do not assume equipment access that has not been established.

## Application through the research stages

1. Device modelling: keep reproducible model validation separate from a dated component procurement register. Document obtainable implementations and any missing supply evidence.
2. Qualification: define a separately evidenced procurement/build-readiness status. Procurement does not change physical test thresholds, and an availability label cannot substitute for sourcing evidence.
3. Topology engineering: provide each representative's actual intended-quantity BOM and explain procurement dependence or substitutes. Do not discard a family solely because one chosen device is unavailable; test alternative implementations where justified.
4. Optimization: preserve technical Pareto axes and add traceable cost/availability data separately. Discrete part/substitute changes require a new implementation record and revalidation; similar labels do not prove equivalent behavior.
5. Comparison: require dated German orderability and delivered-cost coverage. Show procurement risk, remaining unknowns, cost premiums and practical substitutions alongside engineering performance. Refresh stale evidence before any later purchase recommendation.

The following stages should create a machine-readable register under `research/procurement/` with source URLs, dates, quantities, prices, cost assumptions and verification states. This contract itself contains no current supplier quote or component availability finding.
