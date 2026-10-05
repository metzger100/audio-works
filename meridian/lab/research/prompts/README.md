# Next-stage prompt pack

Use these prompts sequentially in the existing Audiotech workspace. Each is self-contained and tells the agent to inspect current progress, perform actual work and preserve evidence. Copy one prompt at a time; the dependency order and source-freeze rules make simultaneous execution inappropriate.

1. [Validate semiconductor models](01_device_models.md)
2. [Strengthen qualification and evidence states](02_qualification.md)
3. [Implement the first diverse architectural batch](03_architectures.md)
4. [Optimize independently and test robustness](04_robust_optimization.md)
5. [Produce the architecture comparison and measurement priorities](05_comparative_report.md)

[All five prompts in one document](prompt_pack.md).

Revision 2 makes [Germany procurement and delivered-cost requirements](../procurement_germany.md) explicit in every prompt: private small-quantity ordering, Germany delivery, actual basket costs, sourcing uncertainty and the restriction on unused comparison purchases. German/EU and international retail routes remain eligible. No numerical spending ceiling is invented.

Revision 3 adds the mandatory [patent non-infringement requirement](../../../../PATENTS.md) to every prompt: early feature flags, dated claim/territory/status evidence, unresolved-risk holds at affected implementation gates and no unsupported legal-clearance claim.

The prompts do not assume that all devices, mechanisms or candidates will succeed. Their deliverables are executable work, preserved failures and honest evidence coverage. Physical measurements and an unknown safe capsule bias remain separate gates. The complete mission and project agent contract continue to apply.

These prompts were prepared as writing artifacts; none of their engineering tasks has been launched by creating this pack.
