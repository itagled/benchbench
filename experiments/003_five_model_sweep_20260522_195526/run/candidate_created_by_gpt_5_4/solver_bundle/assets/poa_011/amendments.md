# Amendments

Priority order inside this packet:
1. Replacement rules
2. Additive rules
3. Waivers
4. Final review trigger

Replacement rules:
- If zone is `North` and category is `Research`, replace the entire risk score with `2`.
- If zone is `West` and category is `Transit`, replace the running fee with `13`.
- If zone is `South` and `preclear = true`, replace the risk score with the smaller of its current value and `2`; then add fee `2`.

Additive rules:
- If seal is `Aster`, subtract fee `3` if flag `dock` is absent.
- If zone is `East` and category is `Medical`, add fee `2`.
- If `quantity >= 1`, add risk `5`.

Waivers:
- If `quantity <= 2` and `escort = true`, subtract fee `4`.
- If `declared_units != quantity` and `preclear = true`, subtract fee `3`.
- If multiple waivers apply, use only the single waiver with the largest reduction.

Final review trigger:
- If `manual_note = true` and final fee before lane assignment is at least `20`, force the final risk score to be at least `8`.
