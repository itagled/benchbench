# Failure Modes (POA v1)

- Solvers may treat every fee reduction as stackable, even though only the single largest waiver may apply.
- Solvers may miss the distinction between fee replacement rules and additive fee rules.
- Solvers may compute the verdict before all amendments have finished changing the risk score.
- Solvers may compute the lane before all fee changes have finished.
- Solvers may silently normalize string labels or assume synonyms, even though all labels are exact.
- Solvers may use the case file fields but ignore the interpretation order stated in `shared_rules.md`.
- Solvers may notice the verdict skew and over-trust a `DENY` default, but exact-match scoring still punishes wrong fee and lane outputs.
