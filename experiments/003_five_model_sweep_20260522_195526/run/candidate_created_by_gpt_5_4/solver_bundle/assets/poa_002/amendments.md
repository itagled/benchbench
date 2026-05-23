# Amendments

Priority order inside this packet:
1. Replacement rules
2. Additive rules
3. Waivers
4. Final review trigger

Replacement rules:
- If zone is `South` and category is `Research`, replace the entire risk score with `0`.
- If zone is `North` and category is `Archives`, replace the running fee with `8`.
- If zone is `East` and `preclear = true`, replace the risk score with the smaller of its current value and `4`; then add fee `2`.

Additive rules:
- If seal is `Birch`, subtract fee `2` if flag `relay` is absent.
- If zone is `West` and category is `Agriculture`, add fee `1`.
- If `quantity >= 8`, add risk `2`.

Waivers:
- If `quantity <= 9` and `escort = true`, subtract fee `1`.
- If `declared_units != quantity` and `preclear = true`, subtract fee `2`.
- If multiple waivers apply, use only the single waiver with the largest reduction.

Final review trigger:
- If `manual_note = true` and final fee before lane assignment is at least `22`, force the final risk score to be at least `7`.
