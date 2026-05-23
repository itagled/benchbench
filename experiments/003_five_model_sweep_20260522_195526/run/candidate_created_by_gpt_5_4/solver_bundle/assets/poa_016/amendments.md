# Amendments

Priority order inside this packet:
1. Replacement rules
2. Additive rules
3. Waivers
4. Final review trigger

Replacement rules:
- If zone is `West` and category is `Research`, replace the entire risk score with `1`.
- If zone is `North` and category is `Medical`, replace the running fee with `12`.
- If zone is `East` and `preclear = true`, replace the risk score with the smaller of its current value and `1`; then add fee `2`.

Additive rules:
- If seal is `Cinder`, subtract fee `6` if flag `dock` is absent.
- If zone is `South` and category is `Archives`, add fee `3`.
- If `quantity >= 4`, add risk `2`.

Waivers:
- If `quantity <= 6` and `escort = true`, subtract fee `4`.
- If `declared_units != quantity` and `preclear = true`, subtract fee `2`.
- If multiple waivers apply, use only the single waiver with the largest reduction.

Final review trigger:
- If `manual_note = true` and final fee before lane assignment is at least `26`, force the final risk score to be at least `7`.
