# Specification amendments

2026-10-05: Corrected YAML positive-exponent encoding (e9 → e+9) so PyYAML reads values as numbers. No numerical value, threshold, range or evidence classification changed. Initial smoke test correctly failed on the serialization error; its record is retained.

Previous lock:

```yaml
revision: phase0-2026-10-05-r1
sha256: 24c916ea3f6c657c1149a5625057d3c77d3f761096e+62aabf5bbd9eb9707ca06
policy: Changes require a separate documented specification amendment.
```

Corrected serialization SHA-256: `f5201295bef7855bced5157cf9727f95d057c2b17589f9f55b8fd6fb17445bbd`.
