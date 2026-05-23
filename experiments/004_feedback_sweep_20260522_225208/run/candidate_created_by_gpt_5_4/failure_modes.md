# Failure Modes

## Likely solver mistakes

- Using the original schedule instead of the final amended schedule when checking freeze windows, authority windows, or stale approvals.
- Counting approvals that were voided by a risk-tier change or a schedule shift larger than 90 minutes.
- Treating any director or security mention as valid without checking whether the signer actually held that authority.
- Forgetting that delegation validity is evaluated at the final scheduled release time, not when the delegation was first published.
- Missing the precedence order and returning a true lower-priority failure instead of the highest-priority decisive rule.
- Misreading emergency evidence and allowing a freeze override even when the incident severity is only `SEV3`.
- Treating the requester as harmless when they are the only valid approver and therefore trigger `R3`.

## Benchmark-level risks

- The current sample has no `escalate` items. The answer format supports them, but this particular sample does not exercise that branch.
- Because the policy is public and finite, a very strong solver could eventually write a careful parser-plus-simulator. The intended difficulty comes from cross-document interpretation and edge-case handling, not from impossibility.
- The evidence language is varied but still synthetic. If future runs want more realism, the next version could diversify writing styles further or add more distracting but irrelevant notes.

## What I did to reduce these risks

- Spread the 30-item sample across eight distinct governing outcomes instead of one dominant pattern.
- Kept the answer exact and auditable as a canonical JSON string.
- Made the decisive rule depend on interacting public documents rather than on a single hidden generator trick.
