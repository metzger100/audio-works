# Mechanical repository rules

[Quality contract](../QUALITY.md) · [Checker](../tools/repo_quality/INDEX.md)

Ordinary maintained paths use lowercase kebab-case; Python modules/packages use snake_case. Conventional control filenames and candidate/concept/fixture identifiers retain standard forms. Naming, case collisions, unsafe paths and unclassified files fail the gate.

Every maintained file must be reachable from `docs/INDEX.md`. Registered modules need a purpose and their own index. Generated indexes expose immediate contents and child hubs. Pages target 12,000 characters and must remain below the 15,000-character ceiling. Refresh is deterministic; missing, stale or obsolete generated outputs fail.

Maintained text must be UTF-8 with LF endings and a final newline. JSON/YAML/TOML must parse; duplicate mapping keys and record identities fail. Python correctness/format checks use pinned Ruff. Markdown checks inspect ordinary/reference links, images, HTML links and anchors. Empty Markdown sections, repeated paragraphs of180characters or more, conflict markers and accidental private/cache files fail.

A sole `$include` key contains a relative filename or list of filenames. A single reference substitutes its node. Lists of references concatenate lists in order or merge disjoint mappings. Reject absolute paths, parent traversal, cycles, duplicate keys/identities and mixed composition types. Original plain records remain readable. Sharding preserves numeric types and precision.

Original exclusions are limited to protected experiment/history paths, hash-declared original research, original vendor/licence bytes and media. Declared original material retains baseline Git provenance; classifications cannot erase established preservation obligations. Ordinary authored/generated text has no per-file waiver.

`check` reads the working files; `check --staged` reads the Git index; `check --ref REV --base BASE` reads committed objects and compares protected evidence to the base. Hooks use the selected checker/configuration, never unstaged substitutes, and never download or modify content. `audit` reports structural findings and preservation separately. Expensive scientific verification remains local and follows the lab contract.

One `repository-quality` CI job repeats repository checks on pushes/pull requests. Configure it as a required status check on the default branch when remote changes are separately authorized. Local hooks can be bypassed; CI alone does not block merges without branch protection. No remote setting/publication is performed by local setup.

Scientific record values, including source-relative provenance strings, are retained exactly during partitioning. [Path migrations](config/path-migrations.json) resolve old locations to current hubs; baseline Git and hashed history retain the original interpretation. The migration compares fully resolved values and complete CSV rows.

Reading routes load the project description/decisions and full scientific contract, then point to relevant evidence and memory hubs. Setup manuals and unrelated memory are loaded on demand. Necessary scientific evidence has priority over route size. `audit` reports route sizes, navigation coverage, generated freshness, Git/CI enforcement and known preservation gaps.
