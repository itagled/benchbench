# Broad BenchBench Sweep

This run used the broad creator prompt plus a prior-run failure report: creators saw benchmark landscape notes, prior pilot outcomes, and feedback on how the previous candidates broke.

Run root: `/Users/rohit/Documents/Workspace/Coding/benchbench/experiments/008_fable_creator_sweep_20260610_085405`
Creator models: `fable`
Solver models: `gpt-5.2, gpt-5.4, gpt-5.5, gemini-3.1-pro, gemini-3.5-flash-high, claude-opus`
Creator effort: `low`
Solver effort: `low`
Creator feedback context: `/Users/rohit/Documents/Workspace/Coding/benchbench/experiments/feedback_for_next_challenger_sweep_20260523.md`

Antigravity rows use the current selected `agy` model and are checked against the selected-model label in the CLI log when a specific Gemini label is requested.

## Benchmark Cards

### Claude Fable 5 Thinking: Rosetta Fieldwork

- What it asks: Each item is an independent procedurally generated constructed mini-language. Given a parallel corpus of 16-32 sentence pairs (conlang <-> English) and one novel English query sentence, produce the conlang translation of the query.
- Intended capability: Few-shot induction of a novel morphophonological system and compositional generalization from a small parallel corpus: morpheme segmentation, affix function identification, boundary phonology (vowel harmony, hiatus deletion, nasal assimilation), irregular-for...
- Creator-anticipated failure modes: Known risks, their likelihood, and mitigations already in place.
- Validation: `True`; bundle files: `3`; leak scan matches: `0`
- Gold control: `{"accuracy": 1.0, "correct": 30, "total": 30}`
- Shifted-wrong control: `{"accuracy": 0.0, "correct": 0, "total": 30}`
- Solver results: gpt-5.2: 0/30, gpt-5.4: 14/30, gpt-5.5: 11/30, Gemini 3.1 Pro (High): 24/30, Gemini 3.5 Flash (High): 27/30, Claude Opus 4.6 Thinking: 0/30
- Current read: `reject`; max score `27/30`

## Solver Grid

| creator | benchmark | solver gpt-5.2 | solver gpt-5.4 | solver gpt-5.5 | solver Gemini 3.1 Pro (High) | solver Gemini 3.5 Flash (High) | solver Claude Opus 4.6 Thinking | max score | status |
|---|---|---:|---:|---:|---:|---:|---:|---:|---|
| Claude Fable 5 Thinking | Rosetta Fieldwork | 0/30 | 14/30 | 11/30 | 24/30 | 27/30 | 0/30 | 27/30 | reject |

## Calls

| phase | creator | solver/model | rows | score | tokens | cost | cache read | cache write | returncode |
|---|---|---:|---:|---:|---:|---:|---:|---:|---:|
| creator | fable | Claude Fable 5 Thinking |  | NA | 4618287 |  | 4159334 | 350064 | 0 |
| solver | fable | gpt-5.2 | 0 | 0/30 | 0 |  |  |  | 1 |
| solver | fable | gpt-5.4 | 30 | 14/30 | 61776 |  |  |  | 0 |
| solver | fable | gpt-5.5 | 30 | 11/30 | 57911 |  |  |  | 0 |
| solver | fable | Gemini 3.1 Pro (High) | 30 | 24/30 | 0 |  |  |  | 0 |
| solver | fable | Gemini 3.5 Flash (High) | 30 | 27/30 | 0 |  |  |  | 0 |
| solver | fable | Claude Opus 4.6 Thinking | 0 | 0/30 | 0 |  | 0 | 0 | -124 |

Total reported tokens: `4737974`

## Infrastructure Failures

Two solver cells are infrastructure failures, not real zeros. Read the
Rosetta Fieldwork row as a four-solver result.

- `gpt-5.2`: the Codex CLI call failed with a deterministic 400 because the
  ChatGPT account no longer supports the `gpt-5.2` model. A backfill attempt
  through `cursor:gpt-5.2` ran ~20 minutes, then ended its turn after reading
  the bundle without emitting predictions (`rc=0`, 0 answered). Both score
  files show `answered: 0` on every item.
- `claude-opus`: timed out at the 1500s solver limit (`rc=-124`, 0 answered).
  A backfill rerun with a 3600s timeout was cancelled manually before
  completion when the run was finalized.

Usable row: gpt-5.4 14/30, gpt-5.5 11/30, Gemini 3.1 Pro 24/30,
Gemini 3.5 Flash 27/30. Status stays `reject` on max score 27/30.

