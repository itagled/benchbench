# Amendments

Priority order inside this packet:
1. Replacement rules
2. Additive rules
3. Waivers
4. Final review trigger

Replacement rules:
- If zone is `West` and category is `Medical`, replace the entire risk score with `3`.
- If zone is `South` and category is `Transit`, replace the running fee with `8`.
- If zone is `East` and `preclear = true`, replace the risk score with the smaller of its current value and `4`; then add fee `1`.

Additive rules:
- If seal is `Dawn`, subtract fee `3` if flag `dock` is absent.
- If zone is `North` and category is `Agriculture`, add fee `4`.
- If `quantity >= 3`, add risk `6`.

Waivers:
- If `quantity <= 5` and `escort = true`, subtract fee `2`.
- If `declared_units != quantity` and `preclear = true`, subtract fee `4`.
- If multiple waivers apply, use only the single waiver with the largest reduction.

Final review trigger:
- If `manual_note = true` and final fee before lane assignment is at least `34`, force the final risk score to be at least `7`.
