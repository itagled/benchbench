# Amendments

Priority order inside this packet:
1. Replacement rules
2. Additive rules
3. Waivers
4. Final review trigger

Replacement rules:
- If zone is `West` and category is `Agriculture`, replace the entire risk score with `1`.
- If zone is `East` and category is `Medical`, replace the running fee with `12`.
- If zone is `North` and `preclear = true`, replace the risk score with the smaller of its current value and `4`; then add fee `1`.

Additive rules:
- If seal is `Dawn`, subtract fee `4` if flag `relay` is absent.
- If zone is `South` and category is `Archives`, add fee `4`.
- If `quantity >= 7`, add risk `4`.

Waivers:
- If `quantity <= 9` and `escort = true`, subtract fee `1`.
- If `declared_units != quantity` and `preclear = true`, subtract fee `4`.
- If multiple waivers apply, use only the single waiver with the largest reduction.

Final review trigger:
- If `manual_note = true` and final fee before lane assignment is at least `27`, force the final risk score to be at least `6`.
