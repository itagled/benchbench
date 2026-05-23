# Failure Modes (LCR v1)

## Spec-following failures
- Treating `amount_minor` as a float currency amount (it is an integer minor-unit count).
- Using the FX rate for the nearest date, rather than the most recent prior date.
- Using banker’s rounding or Python `round()` (ties-to-even) instead of ties-away-from-zero.
- Forgetting to include accounts that only appear on `VOID` rows (rules require *all accounts that appear anywhere in ledger.csv*).

## Ledger interpretation failures
- Not de-duplicating `txn_id` correctly (must keep *earliest* POSTED row by timestamp).
- De-duplicating before dropping `VOID` rows (rules say ignore VOID first, then dedupe among POSTED).
- Applying reversal before de-duplication (rules specify reversal after dedupe).
- Letting a reversal row contribute its own amount to balances (reversals contribute 0).
- “Partial reversal” or sign-flip assumptions; reversal cancels the referenced txn entirely.

## Output canonicalization failures
- Emitting pretty JSON, multi-line, or extra whitespace.
- Failing to sort keys lexicographically.
- Emitting numbers as strings or floats.

## Shortcut / non-auditable strategies (discouraged)
- Trying to infer answers by pattern matching rather than implementing the rules.
- Using a non-deterministic tool chain that can introduce floating drift without implementing ties-away-from-zero explicitly.

