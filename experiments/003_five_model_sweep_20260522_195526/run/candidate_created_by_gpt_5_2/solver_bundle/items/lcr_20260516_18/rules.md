# LCR v1 Rules (solver-visible)

You are given a per-item folder containing:
- `ledger.csv`
- `fx_rates.csv`

Your job: compute final per-account balances in **USD cents** and output a **canonical JSON object string**:
- Keys: every `account_id` that appears anywhere in `ledger.csv`, even if final balance is 0.
- Values: signed integer USD cents.
- Canonical JSON: keys sorted lexicographically (Unicode codepoint order), no extra whitespace.

## Files

### `ledger.csv`
Columns:
- `txn_id` (string): transaction identifier. May repeat (duplicates).
- `posted_at` (string): ISO-8601 UTC timestamp, format `YYYY-MM-DDTHH:MM:SSZ`.
- `account_id` (string): account identifier (ASCII uppercase A-Z plus digits).
- `currency` (string): one of the currencies listed in `fx_rates.csv`.
- `amount_minor` (integer): signed amount in minor units of `currency` (e.g., cents).
- `type` (string): `PAYMENT`, `CHARGE`, `REFUND`, `ADJUSTMENT`, or `REVERSAL`.
- `ref_txn_id` (string): empty unless `type == REVERSAL`, in which case it references a `txn_id`.
- `status` (string): `POSTED` or `VOID`.

### `fx_rates.csv`
Columns:
- `date` (string): `YYYY-MM-DD` in UTC calendar date.
- `currency` (string)
- `usd_per_unit` (decimal string): USD per 1.0 unit of the currency. Example: `1.0735`

Rates are provided for multiple dates per currency.

## Computation

### Step 0: parse rows
Ignore ledger rows with `status == VOID`.

### Step 1: de-duplicate `txn_id`
If multiple POSTED rows share the same `txn_id`, keep **only** the row with the earliest `posted_at` timestamp (strictly earliest). Discard all later rows with that `txn_id` entirely.

### Step 2: apply reversal semantics
After de-duplication:
- A row with `type == REVERSAL` cancels (removes) the referenced transaction identified by `ref_txn_id`.
- Cancellation means: the referenced transaction contributes **0** to the final balances.
- The reversal row itself also contributes **0** to final balances.
- If multiple reversal rows reference the same `ref_txn_id`, the first one in increasing `posted_at` order is effective; later ones do nothing extra.
- If a reversal references a `ref_txn_id` that does not exist after de-duplication, it has no effect (still contributes 0).

### Step 3: FX conversion
For each non-canceled, non-REVERSAL transaction row, convert `amount_minor` to USD cents:
1. Let `d` be the UTC calendar date of `posted_at` (the `YYYY-MM-DD` portion).
2. Select the FX rate for (currency, date) using:
   - Choose the rate whose `date` is the **latest date <= d**.
   - It is guaranteed such a rate exists for every row.
3. Convert:
   - amount_units = amount_minor / minor_per_unit
   - usd = amount_units * usd_per_unit
   - usd_cents = round_to_nearest_int(usd * 100) with ties **away from zero**

Minor units per currency are:
- USD, EUR, GBP: 100
- JPY: 1

### Step 4: account aggregation
Sum USD cents per `account_id`.

## Output
Return the canonical JSON object string described at top.
