# Broad BenchBench Sweep

This run used the broad creator prompt plus a prior-run failure report: creators saw benchmark landscape notes, prior pilot outcomes, and feedback on how the previous candidates broke.

Run root: `/Users/rohit/Documents/Workspace/Coding/benchbench/experiments/006_claude_opus_feedback_style_20260523_125611`
Creator models: `opus`
Solver models: `opus`
Creator effort: `low`
Solver effort: `low`
Creator feedback context: `/Users/rohit/Documents/Workspace/Coding/benchbench/experiments/005_claude_opus_exp003_style_20260523_125019/feedback_for_claude_opus_second_run.md`

Correction: the original solver call wrote predictions to `predictions.jsonl`
inside the isolated solver bundle and returned a prose status line, so the
first summary pass parsed zero rows. After the harness was fixed to harvest
solver-written `predictions.jsonl` files, the rerun in `solver_extension_opus.md`
scored Claude Opus at 30/30 on Conlang Rosetta. Treat the solver extension as
the authoritative self-solve result.

## Candidates

### Claude Opus: Conlang Rosetta

- Candidate: `/Users/rohit/Documents/Workspace/Coding/benchbench/experiments/006_claude_opus_feedback_style_20260523_125611/run/candidate_created_by_opus`
- Validated: `True`
- Bundle files: `3`
- Gold control: `{"accuracy": 1.0, "correct": 30, "total": 30}`
- Shifted-wrong control: `{"accuracy": 0.0, "correct": 0, "total": 30}`
- Leak scan matches: `0`

## Solver Grid

| creator | benchmark | solver Claude Opus | max score | status |
|---|---|---:|---:|---|
| Claude Opus | Conlang Rosetta | 30/30 | 30/30 | reject |

## Calls

| phase | creator | solver/model | rows | score | tokens | Claude cost | Claude cache read | returncode |
|---|---|---:|---:|---:|---:|---:|---:|---:|
| creator | opus | Claude Opus |  | NA | 778125 | 1.14086825 | 713384 | 0 |
| solver | opus | Claude Opus | 0 | 0/30 | 187241 | 0.3843135 | 163424 | 0 |

Total reported tokens: `965366`
Total reported Claude cost: `$1.5252`
