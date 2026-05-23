# Release Governance Manual RG-7

This benchmark packet models a fictional release-governance process.

## Rule Precedence

When several clauses apply, use the highest-priority decisive clause below.
If a decisive reject rule applies, return `reject`.
If no decisive reject rule applies but the evidence is incomplete or conflicting in a way the packet cannot resolve, return `escalate`.
Otherwise return `approve`.

Priority order:
1. `R7` emergency evidence conflict or missing required emergency co-sign.
2. `R6` sensitive change missing required security approval.
3. `R5` active freeze window blocks the release.
4. `R4` all approvals became stale after a scope-changing amendment.
5. `R3` separation-of-duties failure.
6. `R2` approver lacked authority at the scheduled release time.
7. `R1` request never received the minimum valid approvals.
8. `A1` packet is valid and approvable.

## Approval Thresholds

`R1`: Every request needs two valid approvals tied to the final scope.
At least one valid approval must come from Operations or a valid Operations delegate.
For high-risk requests, one valid approval must come from a Director.

## Authority

`R2`: An approval is valid only if, at the scheduled release time, the signer had matching authority for the service domain.
Delegations are valid only inside their published start and end times and only for the listed domain.

## Separation Of Duties

`R3`: The requester cannot satisfy both required approvals by themselves.
If the requester signed as one approver, the second required approval must come from a different person.

## Staleness After Scope Change

`R4`: Any amendment that changes the scheduled release time by more than 90 minutes, or changes the risk tier, voids all earlier approvals.
After such an amendment, the request must collect a fresh full set of approvals.

## Freeze Windows

`R5`: A release scheduled inside an active freeze window is rejected unless the packet shows an emergency override.
An emergency override requires:
- an incident ticket marked `SEV1` or `SEV2`;
- one valid Director approval after the incident opened; and
- one valid Operations approval after the incident opened.

## Sensitive Changes

`R6`: A request touching any data tagged `regulated` or `credential` requires one valid Security approval tied to the final scope.
For low-risk requests, the Security approval may also count toward the base two approvals.

## Emergency Evidence Integrity

`R7`: If the packet claims emergency status but the incident evidence is contradictory, closed before the qualifying approvals, or below `SEV2`, reject under `R7`.

## Approval Timing

Approvals count only if they were sent after the request existed and before the scheduled release time.
