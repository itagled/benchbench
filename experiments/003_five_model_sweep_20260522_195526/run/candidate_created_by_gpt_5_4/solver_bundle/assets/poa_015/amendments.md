# Amendments

Priority order inside this packet:
1. Replacement rules
2. Additive rules
3. Waivers
4. Final review trigger

Replacement rules:
- If zone is `East` and category is `Research`, replace the entire risk score with `2`.
- If zone is `West` and category is `Medical`, replace the running fee with `7`.
- If zone is `North` and `preclear = true`, replace the risk score with the smaller of its current value and `3`; then add fee `2`.

Additive rules:
- If seal is `Dawn`, subtract fee `4` if flag `vault` is absent.
- If zone is `South` and category is `Transit`, add fee `4`.
- If `quantity >= 7`, add risk `4`.

Waivers:
- If `quantity <= 9` and `escort = true`, subtract fee `2`.
- If `declared_units != quantity` and `preclear = true`, subtract fee `2`.
- If multiple waivers apply, use only the single waiver with the largest reduction.

Final review trigger:
- If `manual_note = true` and final fee before lane assignment is at least `28`, force the final risk score to be at least `7`.
