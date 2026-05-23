# Dossier cdor-025: Incident Reconciliation Packet
## Intake Note
Region: Eastport. Channel: web portal. Incident type: duplicate intake. Cause logged by intake: software migration.
The operating date was 2026-04-12; quality office opened the case on 2026-04-16. The affected count currently stands at 211. Severity entered in the local register: red.
Vulnerable-population flag: yes. Cross-region service touch: yes. Comparable incidents in the preceding 90 days: 2. Consent repair flag: yes.

## Procedure Manual Excerpt, effective before current amendments
Manual date 2026-02-08. Amber matters are normally due in 10 business days after discovery; red matters in 5; critical matters in 2. A board review was originally required only for critical matters. Local manager signoff was the ordinary hold.

## Amendment Log
Amendment posted 2026-04-02. Where affected count is at least 100, notification must be no later than 3 business days. A vulnerable-population flag shortens the outside limit to 4 business days. Cross-region service touch shortens it to 2 business days. Two or more comparable incidents in the prior 90 days shortens it to 1 business day. Apply the strictest live deadline, not the most recent sentence.
For amber matters caused by vendor outage or software migration, add a 2-business-day grace period only if affected count is below 50 and there is no vulnerable-population flag. This grace rule never extends red or critical cases.

## Board and Hold Rules
Board review is required for critical matters, cross-region matters, and repeat incidents with at least two comparable incidents in 90 days. For red matters, board review is conditionally required when either count is at least 100 or a vulnerable group is involved. Otherwise it is not required.
Freeze new intake for critical cases with count at least 100. Require regional supervisor signoff for repeat incidents with two or more prior comparables unless the incident type is missed handoff. For amber client-no-show cases, no hold is imposed. All remaining cases use local manager signoff.

## Remediation Rules
If consent repair is flagged and a vulnerable group is involved, use individual_notice_and_consent_repair. If the incident is duplicate intake and that first rule does not apply, use merge_and_audit_duplicate_records. If the cause is vendor outage or software migration and neither earlier remediation applies, use system_fix_with_retrospective_sample. All other cases use manager_attestation_only.

## Required Answer Format
Return one JSON object with exactly these keys: notify_by, board_review, remediation, hold, evidence_codes. Dates must be ISO YYYY-MM-DD. evidence_codes must be a sorted list of the public trigger codes that set the notification deadline.
