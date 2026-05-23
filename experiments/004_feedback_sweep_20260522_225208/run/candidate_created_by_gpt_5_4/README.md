# Release Packet Arbitration

This benchmark asks a solver to decide whether each fictional software release packet should be approved, rejected, or escalated under a public governance manual.

Each item contains a solver-visible evidence packet with:
- the global policy manual;
- a change request;
- zero or more amendments;
- approvals and delegated-authority tables;
- freeze notices;
- incident evidence when relevant.

The solver must output a canonical JSON string with three fields:
`decision`, `governing_rule`, and `responsible_actor`.

This is closest to document-heavy agent or expert-QA benchmarks such as GAIA, BrowseComp, and some legal-policy reasoning tasks, because the solver has to reconcile multiple artifacts rather than answer from a single prompt. It is not a duplicate: the evidence is synthetic, fully self-contained, deterministically graded, and built around adversarial release-governance edge cases where public evidence resolves the answer.
