# Amendments

Priority order inside this packet:
1. Replacement rules
2. Additive rules
3. Waivers
4. Final review trigger

Replacement rules:
- If zone is `North` and category is `Archives`, replace the entire risk score with `2`.
- If zone is `West` and category is `Research`, replace the running fee with `11`.
- If zone is `South` and `preclear = true`, replace the risk score with the smaller of its current value and `3`; then add fee `3`.

Additive rules:
- If seal is `Ember`, subtract fee `4` if flag `relay` is absent.
- If zone is `East` and category is `Agriculture`, add fee `2`.
- If `quantity >= 5`, add risk `6`.

Waivers:
- If `quantity <= 7` and `escort = true`, subtract fee `3`.
- If `declared_units != quantity` and `preclear = true`, subtract fee `3`.
- If multiple waivers apply, use only the single waiver with the largest reduction.

Final review trigger:
- If `manual_note = true` and final fee before lane assignment is at least `33`, force the final risk score to be at least `5`.
