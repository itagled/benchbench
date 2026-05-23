# Broad BenchBench Sweep

This run used the broad creator prompt: creators saw benchmark landscape notes and prior pilot outcomes, but were not directed toward any specific domain or modality.

Run root: `/Users/rohit/Documents/Workspace/Coding/benchbench/experiments/005_claude_opus_exp003_style_20260523_125019`
Creator models: `opus`
Solver models: `opus`
Creator effort: `low`
Solver effort: `low`

## Candidates

### Claude Opus: String Rewriting Distance

- Candidate: `/Users/rohit/Documents/Workspace/Coding/benchbench/experiments/005_claude_opus_exp003_style_20260523_125019/run/candidate_created_by_opus`
- Validated: `True`
- Bundle files: `3`
- Gold control: `{"accuracy": 1.0, "correct": 30, "total": 30}`
- Shifted-wrong control: `{"accuracy": 0.0, "correct": 0, "total": 30}`
- Leak scan matches: `0`

## Solver Grid

| creator | benchmark | solver Claude Opus | max score | status |
|---|---|---:|---:|---|
| Claude Opus | String Rewriting Distance | 30/30 | 30/30 | reject |

## Calls

| phase | creator | solver/model | rows | score | tokens | Claude cost | Claude cache read | returncode |
|---|---|---:|---:|---:|---:|---:|---:|---:|
| creator | opus | Claude Opus |  | NA | 687853 | 1.113218 | 610568 | 0 |
| solver | opus | Claude Opus | 30 | 30/30 | 166307 | 0.1704255 | 156521 | 0 |

Total reported tokens: `854160`
Total reported Claude cost: `$1.2836`
