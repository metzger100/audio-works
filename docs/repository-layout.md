# Repository layout

Use the [repository hub](INDEX.md) for navigation. `python3 tools/project.py audit` counts maintained folders separately from original-only evidence folders in the selected repository view; local environments and ignored caches are excluded. A folder represents a subject, implementation identity or distinct executable role. Create one when its contents need that boundary, rather than adding a wrapper around a document.

| Root | Responsibility |
| --- | --- |
| `meridian-microphone/` | Project overview/decisions and its executable research laboratory |
| `branding/` | Current identity, artwork, proposals and preserved history |
| `docs/` | Shared navigation, repository configuration, decisions and validation |
| `tools/`, `tests/` | Repository gates, preservation tools and their regression fixtures |
| `.githooks/`, `.github/` | Local gates and the single CI workflow |
| `LICENSES/` | Original licence texts |

The laboratory keeps specifications, model libraries, candidate implementations, search, optimization, measurement, scientific code/tests and evidence distinct. [Laboratory navigation](../meridian-microphone/lab/INDEX.md) supplies their immediate contents. Candidate/proposal folders retain stable identities and parents.

Maintained research has eight subject folders: **architectures, capsules, devices, memory, patents, procurement, prompts and sources**. Mechanisms, benchmarks, source interpretation and foundation findings belong with architectures; manufacturer evidence interpretation belongs with devices. Reports live with their subject; executable controls/report generators live in laboratory tooling; derived tables live in results. [Research entry](../meridian-microphone/lab/research/README.md) maps questions to those subjects.

Large mutable records share `data-pages/` within their parent. Each document owns a deterministic namespace, so BOM and topology pages coexist without colliding. Large navigation hubs share `index-pages/`, with hub-prefixed filenames. Page folders have no document wrapper directories. [Mechanical rules](quality-rules.md) enforce the layout and bounded text.

Frozen experiments contain source copies and many individual simulator jobs. Their folder count reflects recorded experiments, including failures. Original research directories such as `architecture_sources/`, private `device_sources/local/` and `probes/` retain their evidence identity. Find them through [original history](history.md) and [experiment indexes](evidence.md); current subject hubs explain their scope. Preserve those paths and bytes rather than merging experimental cohorts.
