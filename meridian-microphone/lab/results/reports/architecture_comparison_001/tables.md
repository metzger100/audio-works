# Generated comparison tables

Derived from immutable same-cohort records. Values are model-conditional; unknowns remain unknown.

| Candidate | Current mA | Rail / polarization V | Sensitivity mV/Pa | Response dB | EIN µV / dBA | Zdiff Ω / mismatch % | Active / passive |
| --- | ---: | --- | ---: | ---: | --- | --- | --- |
| candidate_0019 | 4.1035 | 13.556 / 26.1 | 13.271 | 0.66056 | 2.6961 / 18.336 | 249.49 / 5.3061 | 5 / 47 |
| candidate_0023 | 5.1504 | 11.01 / 22.546 | 10.725 | 0.47212 | 7.9043 / 33.622 | 269.63 / 12.053 | 7 / 65 |
| candidate_0012 | 4.086 | 13.598 / 22.311 | 0.013223 | 20.931 | 847.03 / 72.494 | 365.22 / 25.273 | 5 / 40 |
| candidate_0010 | unknown | unknown / unknown | unknown | unknown | unknown / unknown | unknown / unknown | 6 / 34 |
| candidate_0014 | unknown | unknown / unknown | unknown | unknown | unknown / unknown | unknown / unknown | 5 / 33 |
| candidate_0013 | 1.2343 | 20.464 / 29.204 | unknown | unknown | unknown / unknown | unknown / unknown | 1 / 35 |

## Complete check statuses

| Candidate | operating_point | frequency_response | noise | distortion | headroom | output_impedance | balance | phantom_supply | temperature | semiconductor_corners | monte_carlo | loading | startup | stability |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| candidate_0019 | pass | pass | fail | error | incomplete | fail | fail | pass | pass | incomplete | incomplete | fail | pass | fail |
| candidate_0023 | pass | pass | fail | error | incomplete | fail | fail | pass | pass | incomplete | incomplete | fail | fail | fail |
| candidate_0012 | pass | fail | fail | error | incomplete | fail | fail | fail | fail | incomplete | incomplete | fail | pass | fail |
| candidate_0010 | error | error | error | error | error | error | error | error | error | error | error | error | error | error |
| candidate_0014 | error | error | error | error | error | error | error | error | error | error | error | error | error | error |
| candidate_0013 | pass | incomplete | incomplete | incomplete | incomplete | incomplete | incomplete | incomplete | incomplete | incomplete | incomplete | incomplete | incomplete | incomplete |

Carrier additionally has an errored carrier_mechanism check; ordinary columns are unsupported periodic analyses.

## Exact BOM and sourcing observations

All prices are incomplete catalogue scenarios. Every delivered total is unknown. Each source link retains exact variant, indexed age, MOQ/pack/lead and private-route limits. Nominal values and tolerances below come from the frozen BOM; original errors remain.

### candidate_0019

[Frozen netlist](../../runs/20261009T090737Z_40e6a493/circuit.cir) · [Frozen BOM](../../runs/20261009T090737Z_40e6a493/bom.yaml) · [Connectivity diagram](candidate_0019_connectivity.svg) · [Every node/element](candidate_0019_connectivity.csv)

| Exact MPN | Installed qty | Nominal / tolerance | Package | MOQ / retail pack / excess | Indexed stock / age | Net unit EUR scenario |
| --- | ---: | --- | --- | --- | --- | ---: |
| [RC0603FR-072K2L](https://www.digikey.de/de/products/detail/yageo/RC0603FR-072K2L/727016) | 2 | 2200 ohm / 1% | 0603 / 1608 | 1 / 1 / 0 | 1.5971e+05 / last week | 0.09 |
| [EEU-FR1J470](https://www.digikey.de/de/products/detail/panasonic-electronic-components/EEU-FR1J470/3072280) | 12 | 4.7e-05 F / 20% | Radial 6.3 x 12.7mm; 2.5mm pitch | 1 / 1 / 0 | 68724 / 4 months | 0.4 |
| [RC0603FR-07100KL](https://www.digikey.de/de/products/detail/yageo/RC0603FR-07100KL/726889) | 2 | 100000 ohm / 1% | 0603 / 1608 | 1 / 1 / 0 | 5.4827e+05 / 3 days | 0.09 |
| [R82EC4100DQ70J](https://www.digikey.de/de/products/detail/kemet/R82EC4100DQ70J/1930809) | 2 | 1e-06 F / 5% | Radial 7.2 x 6 x 11.1mm; 5mm pitch | 1 / 1 / 0 | 3.1488e+05 / 3 weeks | 0.78 |
| [BC846B,215](https://www.tme.eu/de/details/bc846b.215/npn-smd-transistoren/nexperia/bc846b-215/) | 4 | BC846B device / unknown% | SOT-23 | 1 / 1 / 0 | 1.7836e+05 / product2 months; group1 week | 0.08 |
| [AC0603FR-0710KL](https://www.digikey.de/de/products/detail/yageo/AC0603FR-0710KL/2828135) | 10 | 10000 ohm / 1% | 0603 / 1608 | 1 / 1 / 0 | 1.3035e+06 / last week | 0.09 |
| [RC0603FR-071ML](https://www.digikey.de/de/products/detail/yageo/RC0603FR-071ML/729791) | 12 | 1000000 ohm / 1% | 0603 / 1608 | 1 / 1 / 0 | 1.5666e+06 / last week | 0.09 |
| [R82EC3100DQ70J](https://www.digikey.de/en/products/detail/kemet/R82EC3100DQ70J/1930807) | 2 | 1e-07 F / 5% | Radial 7.2 x 2.5 x 6.6mm; 5mm pitch | 1 / 1 / 0 | unknown / German exact price unavailable | unknown |
| [HVA12JA1G00](https://www.digikey.de/en/products/detail/stackpole-electronics-inc/HVA12JA1G00/6195865) | 1 | 1000000000.0 ohm / 5% | Axial 4 x 11mm | 1 / 1 / 0 | 1148 / last week filter listing | 0.73 |
| [RC0603FR-071KL](https://www.digikey.de/de/products/detail/yageo/RC0603FR-071KL/726843) | 1 | 1000 ohm / 1% | 0603 / 1608 | 1 / 1 / 0 | 2.9374e+06 / today | 0.09 |
| [JFE150DBVR](https://www.digikey.de/de/products/detail/texas-instruments/JFE150DBVR/18185049) | 1 | JFE150 device / unknown% | DBV SOT-23-5 | unknown / unknown / unknown | unknown / 2026-10-09 blocked; preserve 2026-10-05 parent | unknown |
| [RC0603FR-073K3L](https://www.digikey.de/de/products/detail/yageo/RC0603FR-073K3L/727126) | 1 | 3300 ohm / 1% | 0603 / 1608 | 1 / 1 / 0 | 39395 / 4 weeks | 0.09 |
| [RC0603FR-0747RL](https://www.digikey.de/de/products/detail/yageo/RC0603FR-0747RL/727252) | 2 | 47 ohm / 1% | 0603 / 1608 | 1 / 1 / 0 | 5.4354e+05 / 2 weeks | 0.09 |

Priced net subtotal EUR 10.1100; confirmed delivered total unknown. Unpriced: [{"mpn": "R82EC3100DQ70J", "quantity": 2}, {"mpn": "JFE150DBVR", "quantity": 1}].
Full supplier URLs, ratings/technology, lifecycle, exact lead-time fields, intended purchasing quantities and unknown fees are in bom_lines.csv and the machine-readable comparison. Documented dimensions conflict for EEU-FR1J470: frozen catalogue says 12.7mm body, newer primary record says 11.2mm; physical outline/lead allowance needs resolution. Factory packs are not private retail MOQs.

### candidate_0023

[Frozen netlist](../../runs/20261009T090930Z_1acba093/circuit.cir) · [Frozen BOM](../../runs/20261009T090930Z_1acba093/bom.yaml) · [Connectivity diagram](candidate_0023_connectivity.svg) · [Every node/element](candidate_0023_connectivity.csv)

| Exact MPN | Installed qty | Nominal / tolerance | Package | MOQ / retail pack / excess | Indexed stock / age | Net unit EUR scenario |
| --- | ---: | --- | --- | --- | --- | ---: |
| [RC0603FR-072K2L](https://www.digikey.de/de/products/detail/yageo/RC0603FR-072K2L/727016) | 2 | 2200 ohm / 1% | 0603 / 1608 | 1 / 1 / 0 | 1.5971e+05 / last week | 0.09 |
| [EEU-FR1J470](https://www.digikey.de/de/products/detail/panasonic-electronic-components/EEU-FR1J470/3072280) | 13 | 4.7e-05 F / 20% | Radial 6.3 x 12.7mm; 2.5mm pitch | 1 / 1 / 0 | 68724 / 4 months | 0.4 |
| [RC0603FR-07100KL](https://www.digikey.de/de/products/detail/yageo/RC0603FR-07100KL/726889) | 7 | 100000 ohm / 1% | 0603 / 1608 | 1 / 1 / 0 | 5.4827e+05 / 3 days | 0.09 |
| [R82EC4100DQ70J](https://www.digikey.de/de/products/detail/kemet/R82EC4100DQ70J/1930809) | 2 | 1e-06 F / 5% | Radial 7.2 x 6 x 11.1mm; 5mm pitch | 1 / 1 / 0 | 3.1488e+05 / 3 weeks | 0.78 |
| [BC846B,215](https://www.tme.eu/de/details/bc846b.215/npn-smd-transistoren/nexperia/bc846b-215/) | 6 | BC846B device / unknown% | SOT-23 | 1 / 1 / 0 | 1.7836e+05 / product2 months; group1 week | 0.08 |
| [AC0603FR-0710KL](https://www.digikey.de/de/products/detail/yageo/AC0603FR-0710KL/2828135) | 22 | 10000 ohm / 1% | 0603 / 1608 | 1 / 1 / 0 | 1.3035e+06 / last week | 0.09 |
| [RC0603FR-071ML](https://www.digikey.de/de/products/detail/yageo/RC0603FR-071ML/729791) | 12 | 1000000 ohm / 1% | 0603 / 1608 | 1 / 1 / 0 | 1.5666e+06 / last week | 0.09 |
| [R82EC3100DQ70J](https://www.digikey.de/en/products/detail/kemet/R82EC3100DQ70J/1930807) | 1 | 1e-07 F / 5% | Radial 7.2 x 2.5 x 6.6mm; 5mm pitch | 1 / 1 / 0 | unknown / German exact price unavailable | unknown |
| [HVA12JA1G00](https://www.digikey.de/en/products/detail/stackpole-electronics-inc/HVA12JA1G00/6195865) | 1 | 1000000000.0 ohm / 5% | Axial 4 x 11mm | 1 / 1 / 0 | 1148 / last week filter listing | 0.73 |
| [RC0603FR-071KL](https://www.digikey.de/de/products/detail/yageo/RC0603FR-071KL/726843) | 3 | 1000 ohm / 1% | 0603 / 1608 | 1 / 1 / 0 | 2.9374e+06 / today | 0.09 |
| [JFE150DBVR](https://www.digikey.de/de/products/detail/texas-instruments/JFE150DBVR/18185049) | 1 | JFE150 device / unknown% | DBV SOT-23-5 | unknown / unknown / unknown | unknown / 2026-10-09 blocked; preserve 2026-10-05 parent | unknown |
| [RC0603FR-0747RL](https://www.digikey.de/de/products/detail/yageo/RC0603FR-0747RL/727252) | 2 | 47 ohm / 1% | 0603 / 1608 | 1 / 1 / 0 | 5.4354e+05 / 2 weeks | 0.09 |

Priced net subtotal EUR 12.2900; confirmed delivered total unknown. Unpriced: [{"mpn": "R82EC3100DQ70J", "quantity": 1}, {"mpn": "JFE150DBVR", "quantity": 1}].
Full supplier URLs, ratings/technology, lifecycle, exact lead-time fields, intended purchasing quantities and unknown fees are in bom_lines.csv and the machine-readable comparison. Documented dimensions conflict for EEU-FR1J470: frozen catalogue says 12.7mm body, newer primary record says 11.2mm; physical outline/lead allowance needs resolution. Factory packs are not private retail MOQs.

### candidate_0012

[Frozen netlist](../../runs/20261009T090439Z_c6d23a08/circuit.cir) · [Frozen BOM](../../runs/20261009T090439Z_c6d23a08/bom.yaml) · [Connectivity diagram](candidate_0012_connectivity.svg) · [Every node/element](candidate_0012_connectivity.csv)

| Exact MPN | Installed qty | Nominal / tolerance | Package | MOQ / retail pack / excess | Indexed stock / age | Net unit EUR scenario |
| --- | ---: | --- | --- | --- | --- | ---: |
| [RC0603FR-072K2L](https://www.digikey.de/de/products/detail/yageo/RC0603FR-072K2L/727016) | 2 | 2200 ohm / 1% | 0603 / 1608 | 1 / 1 / 0 | 1.5971e+05 / last week | 0.09 |
| [EEU-FR1J470](https://www.digikey.de/de/products/detail/panasonic-electronic-components/EEU-FR1J470/3072280) | 6 | 4.7e-05 F / 20% | Radial 6.3 x 12.7mm; 2.5mm pitch | 1 / 1 / 0 | 68724 / 4 months | 0.4 |
| [RC0603FR-07100KL](https://www.digikey.de/de/products/detail/yageo/RC0603FR-07100KL/726889) | 2 | 100000 ohm / 1% | 0603 / 1608 | 1 / 1 / 0 | 5.4827e+05 / 3 days | 0.09 |
| [R82EC4100DQ70J](https://www.digikey.de/de/products/detail/kemet/R82EC4100DQ70J/1930809) | 1 | 1e-06 F / 5% | Radial 7.2 x 6 x 11.1mm; 5mm pitch | 1 / 1 / 0 | 3.1488e+05 / 3 weeks | 0.78 |
| [BC846B,215](https://www.tme.eu/de/details/bc846b.215/npn-smd-transistoren/nexperia/bc846b-215/) | 5 | BC846B device / unknown% | SOT-23 | 1 / 1 / 0 | 1.7836e+05 / product2 months; group1 week | 0.08 |
| [AC0603FR-0710KL](https://www.digikey.de/de/products/detail/yageo/AC0603FR-0710KL/2828135) | 9 | 10000 ohm / 1% | 0603 / 1608 | 1 / 1 / 0 | 1.3035e+06 / last week | 0.09 |
| [RC0603FR-071ML](https://www.digikey.de/de/products/detail/yageo/RC0603FR-071ML/729791) | 13 | 1000000 ohm / 1% | 0603 / 1608 | 1 / 1 / 0 | 1.5666e+06 / last week | 0.09 |
| [R82EC3100DQ70J](https://www.digikey.de/en/products/detail/kemet/R82EC3100DQ70J/1930807) | 2 | 1e-07 F / 5% | Radial 7.2 x 2.5 x 6.6mm; 5mm pitch | 1 / 1 / 0 | unknown / German exact price unavailable | unknown |
| [RC0603FR-071KL](https://www.digikey.de/de/products/detail/yageo/RC0603FR-071KL/726843) | 3 | 1000 ohm / 1% | 0603 / 1608 | 1 / 1 / 0 | 2.9374e+06 / today | 0.09 |
| [RC0603FR-0747RL](https://www.digikey.de/de/products/detail/yageo/RC0603FR-0747RL/727252) | 2 | 47 ohm / 1% | 0603 / 1608 | 1 / 1 / 0 | 5.4354e+05 / 2 weeks | 0.09 |

Priced net subtotal EUR 6.3700; confirmed delivered total unknown. Unpriced: [{"mpn": "R82EC3100DQ70J", "quantity": 2}].
Full supplier URLs, ratings/technology, lifecycle, exact lead-time fields, intended purchasing quantities and unknown fees are in bom_lines.csv and the machine-readable comparison. Documented dimensions conflict for EEU-FR1J470: frozen catalogue says 12.7mm body, newer primary record says 11.2mm; physical outline/lead allowance needs resolution. Factory packs are not private retail MOQs.

### candidate_0010

[Frozen netlist](../../runs/20261009T090436Z_496da267/circuit.cir) · [Frozen BOM](../../runs/20261009T090436Z_496da267/bom.yaml) · [Connectivity diagram](candidate_0010_connectivity.svg) · [Every node/element](candidate_0010_connectivity.csv)

| Exact MPN | Installed qty | Nominal / tolerance | Package | MOQ / retail pack / excess | Indexed stock / age | Net unit EUR scenario |
| --- | ---: | --- | --- | --- | --- | ---: |
| [RC0603FR-072K2L](https://www.digikey.de/de/products/detail/yageo/RC0603FR-072K2L/727016) | 2 | 2200 ohm / 1% | 0603 / 1608 | 1 / 1 / 0 | 1.5971e+05 / last week | 0.09 |
| [EEU-FR1J470](https://www.digikey.de/de/products/detail/panasonic-electronic-components/EEU-FR1J470/3072280) | 5 | 4.7e-05 F / 20% | Radial 6.3 x 12.7mm; 2.5mm pitch | 1 / 1 / 0 | 68724 / 4 months | 0.4 |
| [RC0603FR-07100KL](https://www.digikey.de/de/products/detail/yageo/RC0603FR-07100KL/726889) | 2 | 100000 ohm / 1% | 0603 / 1608 | 1 / 1 / 0 | 5.4827e+05 / 3 days | 0.09 |
| [R82EC4100DQ70J](https://www.digikey.de/de/products/detail/kemet/R82EC4100DQ70J/1930809) | 2 | 1e-06 F / 5% | Radial 7.2 x 6 x 11.1mm; 5mm pitch | 1 / 1 / 0 | 3.1488e+05 / 3 weeks | 0.78 |
| [BC846B,215](https://www.tme.eu/de/details/bc846b.215/npn-smd-transistoren/nexperia/bc846b-215/) | 4 | BC846B device / unknown% | SOT-23 | 1 / 1 / 0 | 1.7836e+05 / product2 months; group1 week | 0.08 |
| [AC0603FR-0710KL](https://www.digikey.de/de/products/detail/yageo/AC0603FR-0710KL/2828135) | 6 | 10000 ohm / 1% | 0603 / 1608 | 1 / 1 / 0 | 1.3035e+06 / last week | 0.09 |
| [RC0603FR-071ML](https://www.digikey.de/de/products/detail/yageo/RC0603FR-071ML/729791) | 12 | 1000000 ohm / 1% | 0603 / 1608 | 1 / 1 / 0 | 1.5666e+06 / last week | 0.09 |
| [R82EC3100DQ70J](https://www.digikey.de/en/products/detail/kemet/R82EC3100DQ70J/1930807) | 1 | 1e-07 F / 5% | Radial 7.2 x 2.5 x 6.6mm; 5mm pitch | 1 / 1 / 0 | unknown / German exact price unavailable | unknown |
| [HVA12JA1G00](https://www.digikey.de/en/products/detail/stackpole-electronics-inc/HVA12JA1G00/6195865) | 1 | 1000000000.0 ohm / 5% | Axial 4 x 11mm | 1 / 1 / 0 | 1148 / last week filter listing | 0.73 |
| [OPA197IDBVR](https://www.digikey.de/en/products/detail/texas-instruments/OPA197IDBVR/5962128) | 2 | OPAx197 device / unknown% | DBV SOT-23-5 | 1 / 1 / 0 | 29522 / 3 weeks | 1.8 |
| [RC0603FR-071KL](https://www.digikey.de/de/products/detail/yageo/RC0603FR-071KL/726843) | 1 | 1000 ohm / 1% | 0603 / 1608 | 1 / 1 / 0 | 2.9374e+06 / today | 0.09 |
| [RC0603FR-0747RL](https://www.digikey.de/de/products/detail/yageo/RC0603FR-0747RL/727252) | 2 | 47 ohm / 1% | 0603 / 1608 | 1 / 1 / 0 | 5.4354e+05 / 2 weeks | 0.09 |

Priced net subtotal EUR 10.4600; confirmed delivered total unknown. Unpriced: [{"mpn": "R82EC3100DQ70J", "quantity": 1}].
Full supplier URLs, ratings/technology, lifecycle, exact lead-time fields, intended purchasing quantities and unknown fees are in bom_lines.csv and the machine-readable comparison. Documented dimensions conflict for EEU-FR1J470: frozen catalogue says 12.7mm body, newer primary record says 11.2mm; physical outline/lead allowance needs resolution. Factory packs are not private retail MOQs.

### candidate_0014

[Frozen netlist](../../runs/20261009T090439Z_77e9f0c9/circuit.cir) · [Frozen BOM](../../runs/20261009T090439Z_77e9f0c9/bom.yaml) · [Connectivity diagram](candidate_0014_connectivity.svg) · [Every node/element](candidate_0014_connectivity.csv)

| Exact MPN | Installed qty | Nominal / tolerance | Package | MOQ / retail pack / excess | Indexed stock / age | Net unit EUR scenario |
| --- | ---: | --- | --- | --- | --- | ---: |
| [RC0603FR-072K2L](https://www.digikey.de/de/products/detail/yageo/RC0603FR-072K2L/727016) | 2 | 2200 ohm / 1% | 0603 / 1608 | 1 / 1 / 0 | 1.5971e+05 / last week | 0.09 |
| [EEU-FR1J470](https://www.digikey.de/de/products/detail/panasonic-electronic-components/EEU-FR1J470/3072280) | 5 | 4.7e-05 F / 20% | Radial 6.3 x 12.7mm; 2.5mm pitch | 1 / 1 / 0 | 68724 / 4 months | 0.4 |
| [RC0603FR-07100KL](https://www.digikey.de/de/products/detail/yageo/RC0603FR-07100KL/726889) | 2 | 100000 ohm / 1% | 0603 / 1608 | 1 / 1 / 0 | 5.4827e+05 / 3 days | 0.09 |
| [R82EC4100DQ70J](https://www.digikey.de/de/products/detail/kemet/R82EC4100DQ70J/1930809) | 1 | 1e-06 F / 5% | Radial 7.2 x 6 x 11.1mm; 5mm pitch | 1 / 1 / 0 | 3.1488e+05 / 3 weeks | 0.78 |
| [BC846B,215](https://www.tme.eu/de/details/bc846b.215/npn-smd-transistoren/nexperia/bc846b-215/) | 4 | BC846B device / unknown% | SOT-23 | 1 / 1 / 0 | 1.7836e+05 / product2 months; group1 week | 0.08 |
| [AC0603FR-0710KL](https://www.digikey.de/de/products/detail/yageo/AC0603FR-0710KL/2828135) | 6 | 10000 ohm / 1% | 0603 / 1608 | 1 / 1 / 0 | 1.3035e+06 / last week | 0.09 |
| [RC0603FR-071ML](https://www.digikey.de/de/products/detail/yageo/RC0603FR-071ML/729791) | 11 | 1000000 ohm / 1% | 0603 / 1608 | 1 / 1 / 0 | 1.5666e+06 / last week | 0.09 |
| [R82EC3100DQ70J](https://www.digikey.de/en/products/detail/kemet/R82EC3100DQ70J/1930807) | 1 | 1e-07 F / 5% | Radial 7.2 x 2.5 x 6.6mm; 5mm pitch | 1 / 1 / 0 | unknown / German exact price unavailable | unknown |
| [OPA197IDBVR](https://www.digikey.de/en/products/detail/texas-instruments/OPA197IDBVR/5962128) | 1 | OPAx197 device / unknown% | DBV SOT-23-5 | 1 / 1 / 0 | 29522 / 3 weeks | 1.8 |
| [HVA12JA1G00](https://www.digikey.de/en/products/detail/stackpole-electronics-inc/HVA12JA1G00/6195865) | 1 | 1000000000.0 ohm / 5% | Axial 4 x 11mm | 1 / 1 / 0 | 1148 / last week filter listing | 0.73 |
| [CC0603JRNPO0BN101](https://www.digikey.de/de/products/detail/yageo/CC0603JRNPO0BN101/5195647) | 1 | 1e-10 F / 5% | 0603 / 1608 | unknown / unknown / unknown | 45850 / 3 months replacement table; direct exact page inaccessible | 0.08 |
| [RC0603FR-071KL](https://www.digikey.de/de/products/detail/yageo/RC0603FR-071KL/726843) | 1 | 1000 ohm / 1% | 0603 / 1608 | 1 / 1 / 0 | 2.9374e+06 / today | 0.09 |
| [RC0603FR-0747RL](https://www.digikey.de/de/products/detail/yageo/RC0603FR-0747RL/727252) | 2 | 47 ohm / 1% | 0603 / 1608 | 1 / 1 / 0 | 5.4354e+05 / 2 weeks | 0.09 |

Priced net subtotal EUR 7.8700; confirmed delivered total unknown. Unpriced: [{"mpn": "R82EC3100DQ70J", "quantity": 1}].
Full supplier URLs, ratings/technology, lifecycle, exact lead-time fields, intended purchasing quantities and unknown fees are in bom_lines.csv and the machine-readable comparison. Documented dimensions conflict for EEU-FR1J470: frozen catalogue says 12.7mm body, newer primary record says 11.2mm; physical outline/lead allowance needs resolution. Factory packs are not private retail MOQs.

### candidate_0013

[Frozen netlist](../../runs/20261009T090547Z_1f85c513/circuit.cir) · [Frozen BOM](../../runs/20261009T090547Z_1f85c513/bom.yaml) · [Connectivity diagram](candidate_0013_connectivity.svg) · [Every node/element](candidate_0013_connectivity.csv)

| Exact MPN | Installed qty | Nominal / tolerance | Package | MOQ / retail pack / excess | Indexed stock / age | Net unit EUR scenario |
| --- | ---: | --- | --- | --- | --- | ---: |
| [RC0603FR-072K2L](https://www.digikey.de/de/products/detail/yageo/RC0603FR-072K2L/727016) | 2 | 2200 ohm / 1% | 0603 / 1608 | 1 / 1 / 0 | 1.5971e+05 / last week | 0.09 |
| [EEU-FR1J470](https://www.digikey.de/de/products/detail/panasonic-electronic-components/EEU-FR1J470/3072280) | 5 | 4.7e-05 F / 20% | Radial 6.3 x 12.7mm; 2.5mm pitch | 1 / 1 / 0 | 68724 / 4 months | 0.4 |
| [RC0603FR-07100KL](https://www.digikey.de/de/products/detail/yageo/RC0603FR-07100KL/726889) | 2 | 100000 ohm / 1% | 0603 / 1608 | 1 / 1 / 0 | 5.4827e+05 / 3 days | 0.09 |
| [R82EC4100DQ70J](https://www.digikey.de/de/products/detail/kemet/R82EC4100DQ70J/1930809) | 1 | 1e-06 F / 5% | Radial 7.2 x 6 x 11.1mm; 5mm pitch | 1 / 1 / 0 | 3.1488e+05 / 3 weeks | 0.78 |
| [BC846B,215](https://www.tme.eu/de/details/bc846b.215/npn-smd-transistoren/nexperia/bc846b-215/) | 1 | BC846B device / unknown% | SOT-23 | 1 / 1 / 0 | 1.7836e+05 / product2 months; group1 week | 0.08 |
| [AC0603FR-0710KL](https://www.digikey.de/de/products/detail/yageo/AC0603FR-0710KL/2828135) | 2 | 10000 ohm / 1% | 0603 / 1608 | 1 / 1 / 0 | 1.3035e+06 / last week | 0.09 |
| [RC0603FR-071ML](https://www.digikey.de/de/products/detail/yageo/RC0603FR-071ML/729791) | 11 | 1000000 ohm / 1% | 0603 / 1608 | 1 / 1 / 0 | 1.5666e+06 / last week | 0.09 |
| [R82EC3100DQ70J](https://www.digikey.de/en/products/detail/kemet/R82EC3100DQ70J/1930807) | 4 | 1e-07 F / 5% | Radial 7.2 x 2.5 x 6.6mm; 5mm pitch | 1 / 1 / 0 | unknown / German exact price unavailable | unknown |
| [CC0603JRNPO0BN101](https://www.digikey.de/de/products/detail/yageo/CC0603JRNPO0BN101/5195647) | 2 | 1e-10 F / 5% | 0603 / 1608 | unknown / unknown / unknown | 45850 / 3 months replacement table; direct exact page inaccessible | 0.08 |
| [HVA12JA1G00](https://www.digikey.de/en/products/detail/stackpole-electronics-inc/HVA12JA1G00/6195865) | 2 | 1000000000.0 ohm / 5% | Axial 4 x 11mm | 1 / 1 / 0 | 1148 / last week filter listing | 0.73 |
| [RC0603FR-071KL](https://www.digikey.de/de/products/detail/yageo/RC0603FR-071KL/726843) | 2 | 1000 ohm / 1% | 0603 / 1608 | 1 / 1 / 0 | 2.9374e+06 / today | 0.09 |
| [RC0603FR-0747RL](https://www.digikey.de/de/products/detail/yageo/RC0603FR-0747RL/727252) | 2 | 47 ohm / 1% | 0603 / 1608 | 1 / 1 / 0 | 5.4354e+05 / 2 weeks | 0.09 |

Priced net subtotal EUR 6.3700; confirmed delivered total unknown. Unpriced: [{"mpn": "R82EC3100DQ70J", "quantity": 4}].
Full supplier URLs, ratings/technology, lifecycle, exact lead-time fields, intended purchasing quantities and unknown fees are in bom_lines.csv and the machine-readable comparison. Documented dimensions conflict for EEU-FR1J470: frozen catalogue says 12.7mm body, newer primary record says 11.2mm; physical outline/lead allowance needs resolution. Factory packs are not private retail MOQs.

