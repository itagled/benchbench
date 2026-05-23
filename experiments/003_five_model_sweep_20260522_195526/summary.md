# Broad BenchBench Sweep

This run used the broad creator prompt: creators saw benchmark landscape notes and prior pilot outcomes, but were not directed toward any specific domain or modality.

Run root: `/Users/rohit/Documents/Workspace/Coding/benchbench/experiments/003_five_model_sweep_20260522_195526`
Creator models: `gpt-5.2, gpt-5.4, gpt-5.5, gemini-3.1-pro, gemini-3.5-flash-high`
Solver models: `gpt-5.2, gpt-5.4, gpt-5.5, gemini-3.1-pro, gemini-3.5-flash-high`
Creator effort: `low`
Solver effort: `low`

Antigravity rows use the current selected `agy` model and are checked against the selected-model label in the CLI log when a specific Gemini label is requested.

## Candidates

### gpt-5.2: Ledger Canonical Reconciliation (LCR) v1

- Candidate: `/Users/rohit/Documents/Workspace/Coding/benchbench/experiments/003_five_model_sweep_20260522_195526/run/candidate_created_by_gpt_5_2`
- Validated: `True`
- Bundle files: `93`
- Gold control: `{"accuracy": 1.0, "correct": 30, "total": 30}`
- Shifted-wrong control: `{"accuracy": 0.0, "correct": 0, "total": 30}`
- Leak scan matches: `0`

### gpt-5.4: Patchwork Ordinance Adjudication (POA) v1

- Candidate: `/Users/rohit/Documents/Workspace/Coding/benchbench/experiments/003_five_model_sweep_20260522_195526/run/candidate_created_by_gpt_5_4`
- Validated: `True`
- Bundle files: `94`
- Gold control: `{"accuracy": 1.0, "correct": 30, "total": 30}`
- Shifted-wrong control: `{"accuracy": 0.0, "correct": 0, "total": 30}`
- Leak scan matches: `0`

### gpt-5.5: Amendment Ledger Reconciliation (ALR)

- Candidate: `/Users/rohit/Documents/Workspace/Coding/benchbench/experiments/003_five_model_sweep_20260522_195526/run/candidate_created_by_gpt_5_5`
- Validated: `True`
- Bundle files: `3`
- Gold control: `{"accuracy": 1.0, "correct": 30, "total": 30}`
- Shifted-wrong control: `{"accuracy": 0.0, "correct": 0, "total": 30}`
- Leak scan matches: `0`

### Gemini 3.1 Pro (High): Polyhedral Surface Traversal

- Candidate: `/Users/rohit/Documents/Workspace/Coding/benchbench/experiments/003_five_model_sweep_20260522_195526/run/candidate_created_by_gemini_3_1_pro`
- Validated: `True`
- Bundle files: `3`
- Gold control: `{"accuracy": 1.0, "correct": 30, "total": 30}`
- Shifted-wrong control: `{"accuracy": 0.0, "correct": 0, "total": 30}`
- Leak scan matches: `0`

### Gemini 3.5 Flash (High): Mutative Assembly Inversion (MAI)

- Candidate: `/Users/rohit/Documents/Workspace/Coding/benchbench/experiments/003_five_model_sweep_20260522_195526/run/candidate_created_by_gemini_3_5_flash_high`
- Validated: `True`
- Bundle files: `3`
- Gold control: `{"accuracy": 1.0, "correct": 30, "total": 30}`
- Shifted-wrong control: `{"accuracy": 0.0, "correct": 0, "total": 30}`
- Leak scan matches: `3`

## Solver Grid

| creator | benchmark | solver gpt-5.2 | solver gpt-5.4 | solver gpt-5.5 | solver Gemini 3.1 Pro (High) | solver Gemini 3.5 Flash (High) | max score | status |
|---|---|---:|---:|---:|---:|---:|---:|---|
| gpt-5.2 | Ledger Canonical Reconciliation (LCR) v1 | 11/30 | 30/30 | 30/30 | 30/30 | 30/30 | 30/30 | reject |
| gpt-5.4 | Patchwork Ordinance Adjudication (POA) v1 | 3/30 | 30/30 | 30/30 | 30/30 | 30/30 | 30/30 | reject |
| gpt-5.5 | Amendment Ledger Reconciliation (ALR) | 30/30 | 30/30 | 30/30 | 30/30 | 30/30 | 30/30 | reject |
| Gemini 3.1 Pro (High) | Polyhedral Surface Traversal | 30/30 | 6/30 | 30/30 | 30/30 | 30/30 | 30/30 | reject |
| Gemini 3.5 Flash (High) | Mutative Assembly Inversion (MAI) | 30/30 | 30/30 | 30/30 | 30/30 | 22/30 | 30/30 | reject |

## Calls

| phase | creator | solver/model | rows | score | tokens | returncode |
|---|---|---:|---:|---:|---:|---:|
| solver | gpt-5.2 | gpt-5.2 | 30 | 11/30 | 32777 | 0 |
| solver | gpt-5.2 | gpt-5.4 | 30 | 30/30 | 67712 | 0 |
| solver | gpt-5.2 | gpt-5.5 | 30 | 30/30 | 85868 | 0 |
| solver | gpt-5.2 | Gemini 3.1 Pro (High) | 30 | 30/30 | 0 | 0 |
| solver | gpt-5.2 | Gemini 3.5 Flash (High) | 30 | 30/30 | 0 | 0 |
| solver | gemini-3.1-pro | gpt-5.2 | 30 | 30/30 | 35962 | 0 |
| solver | gemini-3.1-pro | gpt-5.4 | 30 | 6/30 | 81420 | 0 |
| solver | gemini-3.1-pro | gpt-5.5 | 30 | 30/30 | 43647 | 0 |
| solver | gemini-3.1-pro | Gemini 3.1 Pro (High) | 30 | 30/30 | 0 | 0 |
| solver | gemini-3.1-pro | Gemini 3.5 Flash (High) | 30 | 30/30 | 0 | 0 |
| solver | gemini-3.5-flash-high | gpt-5.2 | 30 | 30/30 | 26907 | 0 |
| solver | gemini-3.5-flash-high | gpt-5.4 | 30 | 30/30 | 39957 | 0 |
| solver | gemini-3.5-flash-high | gpt-5.5 | 30 | 30/30 | 76420 | 0 |
| solver | gemini-3.5-flash-high | Gemini 3.1 Pro (High) | 30 | 30/30 | 0 | 0 |
| solver | gemini-3.5-flash-high | Gemini 3.5 Flash (High) | 23 | 22/30 | 0 | 0 |
| solver | gpt-5.4 | gpt-5.2 | 30 | 3/30 | 31119 | 0 |
| solver | gpt-5.4 | gpt-5.4 | 30 | 30/30 | 148671 | 0 |
| solver | gpt-5.4 | gpt-5.5 | 30 | 30/30 | 54804 | 0 |
| solver | gpt-5.4 | Gemini 3.1 Pro (High) | 30 | 30/30 | 0 | 0 |
| solver | gpt-5.4 | Gemini 3.5 Flash (High) | 30 | 30/30 | 0 | 0 |
| solver | gpt-5.5 | gpt-5.2 | 30 | 30/30 | 44489 | 0 |
| solver | gpt-5.5 | gpt-5.4 | 30 | 30/30 | 50268 | 0 |
| solver | gpt-5.5 | gpt-5.5 | 30 | 30/30 | 42988 | 0 |
| solver | gpt-5.5 | Gemini 3.1 Pro (High) | 30 | 30/30 | 0 | 0 |
| solver | gpt-5.5 | Gemini 3.5 Flash (High) | 30 | 30/30 | 0 | 0 |

Total reported tokens: `863009`

