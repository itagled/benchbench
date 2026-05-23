# MFN-Cascade Benchmark Solver Packet

Welcome to the **MFN-Cascade** (Recursive Treaty Tariff Adjudication) solver bundle.

In this challenge, you are asked to resolve the final stable tariff rates under recursive multi-lateral trade agreements following a unilateral tariff adjustment.

## Rules & Framework

1. The general rules for MFN clauses, category hierarchies, and stalemate locking are defined in:
   `treaties/common_framework.txt`

2. The specific bilateral agreements are located in:
   `treaties/treaty_[nation1]_[nation2].txt`

3. Overriding multilateral amendments are located in:
   `treaties/amendment_[date].txt`

4. For each item in `items_private_sample.jsonl`, you are given:
   - `id`: Unique identifier
   - `date`: The historical date of the query
   - `prompt`: The specific query describing the starting event and the target rate to calculate.

## Format of the Output

You must output a predictions JSONL file named `predictions.jsonl` where each line contains exactly:
`{"id": "...", "answer": "..."}`

The `answer` field must be:
- The exact stable rate formatted as a percentage with one decimal place (e.g. `5.2%`), OR
- If the system did not converge after 20 rounds of updates, prefix it with `STALEMATE_` and format the locked rate at round 20 rounded to 1 decimal place (e.g. `STALEMATE_3.5%`).

Always read the treaties, common framework, and active amendments up to the query date very carefully.
