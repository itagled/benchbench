# Failure Modes

Expected solver errors:

- Using the older manual deadline after the amendment log has superseded it.
- Applying the most recently mentioned deadline instead of the strictest live deadline.
- Adding the amber system grace period to red or critical cases.
- Forgetting that business days exclude weekends.
- Treating conditional board review as ordinary required review.
- Applying duplicate-record remediation before vulnerable consent repair.
- Inferring answers from item order rather than the dossier.

Benchmark risks:

- A strong solver can write a custom parser after recognizing the generated rule family.
- The public dossiers use synthetic rules, so the benchmark measures procedural reconciliation rather than real legal expertise.
- Exact-match scoring can mark semantically correct but schema-invalid answers wrong.
- The 30-item sample is enough for a benchmark sweep but not enough for fine-grained model ranking.

Mitigations:

- Items vary across facts, triggers, exception interactions, and dates.
- The solver bundle contains all evidence needed for every answer.
- The scorer accepts answer objects or JSON-encoded answer strings but enforces a precise schema.
- The verifier checks required files, id alignment, missing assets, and obvious private-file leakage.
