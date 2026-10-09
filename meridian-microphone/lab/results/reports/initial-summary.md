# Initial fixture comparison

Both ideal-buffer fixtures are unqualified. Values describe the original cohort,
not a real microphone, safe capsule polarization or measured acoustic noise.

[Baseline](../runs/20261005T121311Z_f11a711a/results.json) · [Proposal](../runs/20261005T121440Z_8f1bc311/results.json)

| Metric | Baseline | Proposal |
| --- | --- | --- |
| Passive harvest current | 2.751 mA | 2.751 mA |
| Loaded internal rail | 38.508 V | 38.508 V |
| Simulated capsule polarization | 38.462 V | 37.888 V |
| Maximum audio response deviation | 3.882 dB | 0.994 dB |
| Electronics unweighted EIN, conditional | 6.784 µV RMS | 7.187 µV RMS |
| Electronics unweighted equivalent pressure | 529.1 µPa RMS | 569.1 µPa RMS |
| Electronics A-weighted noise, conditional | 17.14 dBA | 21.50 dBA |
| Worst differential output impedance | 152.1 Ω | 114.1 Ω |
| Worst diagonal impedance mismatch | 22.49% | 37.65% |
| Cold-start settling to 1% | 1.318 s | 1.978 s |
| DC/AC scenario screening | 0/16 pass | 15/16 pass |
| Scenario response median | 3.085 dB | 0.630 dB |
| Scenario response 95th / 99th percentile | 3.614 / 3.630 dB | 0.925 / 1.018 dB |
| Scenario response worst observed | 3.634 dB | 1.041 dB |

## Check outcomes

| Check | Baseline | Proposal |
| --- | --- | --- |
| operating_point | pass | pass |
| frequency_response | fail | pass |
| noise | fail | fail |
| distortion | pass | pass |
| headroom | pass | pass |
| output_impedance | pass | pass |
| balance | fail | fail |
| phantom_supply | fail | pass |
| temperature | fail | pass |
| semiconductor_corners | incomplete | incomplete |
| monte_carlo | incomplete | incomplete |
| loading | fail | fail |
| startup | pass | pass |
| stability | fail | fail |

Original-cohort verification: [22 tests](../verification/20261005T121220Z_2792e0f0/verification.json).
Current verification belongs in the repository validation record.
