# Validation Report

## Package Status

Generated 30 private sample items with:

```bash
/Users/rohit/.pyenv/versions/global_env/bin/python generator.py --sample-count 30 --seed 20260516 --out-dir .
```

The command completed successfully. The local Python environment prints `pyenv: cannot rehash: /Users/rohit/.pyenv/shims isn't writable`, but the process exits with status 0 and writes the expected files.

## Verification

Structural verification:

```bash
/Users/rohit/.pyenv/versions/global_env/bin/python verifier.py --items solver_bundle/items_private_sample.jsonl --gold gold_private_sample.jsonl
```

Result: `verified 30 items`.

Gold self-score:

```bash
cp gold_private_sample.jsonl predictions.jsonl
/Users/rohit/.pyenv/versions/global_env/bin/python scorer.py --gold gold_private_sample.jsonl --predictions predictions.jsonl --out score_report.json
```

Result: `30/30`.

Weak baseline:

```bash
/Users/rohit/.pyenv/versions/global_env/bin/python weak_baseline.py --items solver_bundle/items_private_sample.jsonl --out weak_baseline_predictions.jsonl
/Users/rohit/.pyenv/versions/global_env/bin/python scorer.py --gold gold_private_sample.jsonl --predictions weak_baseline_predictions.jsonl --out weak_baseline_score_report.json
```

Result: `0/30`. The baseline reads severity and discovery date, applies only the old manual deadline, and returns default actions. It fails because the benchmark requires amendment precedence, exception ordering, and cross-field reconciliation.

## Solver Bundle Leakage Check

The isolated solver bundle contains only:

- `SOLVER_MANIFEST.json`
- `items_private_sample.jsonl`
- `solver_packet.md`
- `assets/cdor-001.md` through `assets/cdor-030.md`

It does not contain `gold_private_sample.jsonl`, private audit traces, generator/verifier/scorer code, hidden seeds, or answer-key files. The verifier also rejects forbidden private filenames in the solver bundle and checks all listed dossier paths exist.

## External Solvability and Identifiability

Every answer is identifiable from the public solver bundle. Each dossier states:

- the incident facts: severity, discovery date, count, vulnerable flag, cross-region flag, prior comparable count, cause, incident type, and consent flag;
- the superseded manual rule, so solvers know which tempting rule is old;
- the live amendment rules, including strictest-deadline precedence and the amber-only grace exception;
- the board review rules;
- the hold rules;
- the remediation priority order;
- the exact output schema.

A qualified external solver can determine `notify_by` by applying the strictest live notification deadline to the public discovery date and counting weekdays. The remaining fields are selected by public if/then rules in the dossier. `evidence_codes` are explicitly the public trigger codes that set the notification deadline. No answer depends on hidden generator details, private author intent, external law, or an open research problem.

For example, `cdor-001` gives discovery date `2026-04-07`, severity `red`, affected count `123`, no vulnerable flag, no cross-region flag, and one prior comparable. The public rules imply the stricter deadline is `volume>=100`, so notification is due in 3 business days: `2026-04-10`. The same public facts imply conditional board review, local manager signoff, and system-fix remediation.

## Auditability

The private file `private_audit_traces.jsonl` records the normalized facts used to generate each item, but it is not needed by solvers. It is included only to let benchmark maintainers audit whether each gold answer follows from the corresponding dossier.

## Limitations

This is a synthetic procedural benchmark. It measures cross-document obligation resolution, not real legal knowledge. A strong model may eventually infer the generator family and build a parser, but the sample is intentionally adversarial to one-pass extraction and weak rule shortcuts.
