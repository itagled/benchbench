# Feedback For Next BenchBench Sweep

This file is generated from the current creator/solver sweep state. After the final solver finishes, give it to the next creator models with `--feedback-context`.

BenchBench is evaluating benchmark invention. The goal is a complete benchmark package that is valid, reproducible, externally solvable in principle, and still hard after strong tool-enabled solvers attack the public solver bundle.

## Result Grid

| creator | benchmark | solver gpt-5.2 | solver gpt-5.4 | solver gpt-5.5 | solver Gemini 3.1 Pro (High) | solver Gemini 3.5 Flash (High) | solver Claude Opus 4.6 Thinking | max score | status |
|---|---|---:|---:|---:|---:|---:|---:|---:|---|
| Claude Fable 5 Thinking | Rosetta Fieldwork | 0/30 | 14/30 | 11/30 | 24/30 | 27/30 | 0/30 | 27/30 | reject |

## Benchmark Cards

These cards summarize what each prior benchmark actually asked, not just its name and score.

### Claude Fable 5 Thinking: Rosetta Fieldwork

- What it asks: Each item is an independent procedurally generated constructed mini-language. Given a parallel corpus of 16-32 sentence pairs (conlang <-> English) and one novel English query sentence, produce the conlang translation of the query.
- Intended capability: Few-shot induction of a novel morphophonological system and compositional generalization from a small parallel corpus: morpheme segmentation, affix function identification, boundary phonology (vowel harmony, hiatus deletion, nasal assimilation), irregular-for...
- Creator-anticipated failure modes: Known risks, their likelihood, and mitigations already in place.
- Validation: `True`; bundle files: `3`; leak scan matches: `0`
- Gold control: `{"accuracy": 1.0, "correct": 30, "total": 30}`
- Shifted-wrong control: `{"accuracy": 0.0, "correct": 0, "total": 30}`
- Solver results: gpt-5.2: 0/30, gpt-5.4: 14/30, gpt-5.5: 11/30, Gemini 3.1 Pro (High): 24/30, Gemini 3.5 Flash (High): 27/30, Claude Opus 4.6 Thinking: 0/30
- Current read: `reject`; max score `27/30`

## Lessons For The Next Creator

- Do not make a clean puzzle where the public packet exposes one obvious parser, simulator, BFS, or brute-force strategy.
- Do not rely on type strictness, hidden labels, private vocabulary, malformed output expectations, or missing public evidence to create low scores.
- Treat all-zero rows as audit warnings, not as automatic benchmark wins.
- Prefer complete but messy public evidence, closed answer contracts, adversarial edge cases, cross-document consistency, and partial recoverability.
- A candidate should be rejected if any strong solver gets 30/30, or if all strong solvers get 0/30 and the public bundle cannot prove external solvability.
