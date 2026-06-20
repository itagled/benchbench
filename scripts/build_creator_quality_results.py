#!/usr/bin/env python3
"""Build creator quality scores from saved BenchBench experiment grids.

Evaluates Rohit's canonical experiment rows with creator_score_quality
(Lorentzian quality_index, default gamma=7.0). Writes a markdown report to
experiments/canonical/creator_quality_scores.md.

Run from the repo root:

    python scripts/build_creator_quality_results.py
"""

from __future__ import annotations

import sys
from dataclasses import dataclass
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from scripts.build_6x6_result_artifacts import (
    SOLVERS,
    SOLVERS_CURRENT,
    build_grid,
    incumbent_carry_forward_grid,
)
from scripts.creator_score import (
    creator_score_quality,
    creator_score_quality_ranking,
    zero_count,
)


OUTPUT = ROOT / "experiments" / "canonical" / "creator_quality_scores.md"


@dataclass(frozen=True)
class GridSection:
    title: str
    experiment: str
    rows: list[list[str]]
    solvers: list[tuple[str, str]]


def normalize_creator_label(label: str) -> str:
    return label.replace(" (frozen)", "").strip()


def resolve_creator_indices(
    grid: list[list[str]],
    solvers: list[tuple[str, str]],
) -> list[int | None]:
    solver_labels = [label for _solver_id, label in solvers]
    indices: list[int | None] = []
    for row in grid:
        normalized = normalize_creator_label(row[0] if row else "")
        if normalized in solver_labels:
            indices.append(solver_labels.index(normalized))
        else:
            indices.append(None)
    return indices


def load_grids() -> list[GridSection]:
    exp003_rows = build_grid(
        "experiments/003_five_model_sweep_20260522_195526",
        "experiments/005_claude_opus_exp003_style_20260523_125019",
        [
            ("gpt-5.2", "GPT-5.2", "Ledger Canonical Reconciliation"),
            ("gpt-5.4", "GPT-5.4", "Patchwork Ordinance Adjudication"),
            ("gpt-5.5", "GPT-5.5", "Amendment Ledger Reconciliation"),
            ("gemini-3.1-pro", "Gemini 3.1 Pro", "Polyhedral Surface Traversal"),
            ("gemini-3.5-flash-high", "Gemini 3.5 Flash", "Mutative Assembly Inversion"),
            ("opus", "Claude Opus", "String Rewriting Distance"),
        ],
    )
    exp004_rows = build_grid(
        "experiments/004_feedback_sweep_20260522_225208",
        "experiments/006_claude_opus_feedback_style_20260523_125611",
        [
            ("gpt-5.2", "GPT-5.2", "Reimbursement Forensics"),
            ("gpt-5.4", "GPT-5.4", "release_packet_arbitration"),
            ("gpt-5.5", "GPT-5.5", "Cross-Document Obligation Resolution"),
            ("gemini-3.1-pro", "Gemini 3.1 Pro", "Corrupted LZ77 Recovery"),
            ("gemini-3.5-flash-high", "Gemini 3.5 Flash", "MFN-Cascade"),
            ("opus", "Claude Opus", "Conlang Rosetta"),
        ],
        skip={("gpt-5.5", "opus"): "skip"},
    )
    exp007_rows = build_grid(
        "experiments/007_full_feedback_6x6_20260523_172919",
        None,
        [
            ("gpt-5.2", "GPT-5.2", "Service Credit Forensics"),
            ("gpt-5.4", "GPT-5.4", "Catalog Royalty Forensics"),
            ("gpt-5.5", "GPT-5.5", "Prior Authorization Forensics"),
            ("gemini-3.1-pro", "Gemini 3.1 Pro", "Commercial Lease CAM Reconciliation"),
            ("gemini-3.5-flash-high", "Gemini 3.5 Flash", "Maritime Freight & Customs Audit"),
            ("claude-opus", "Claude Opus", "Construction Progress Payment Certification"),
        ],
        solvers=SOLVERS_CURRENT,
    )
    canonical_round3_rows = incumbent_carry_forward_grid(exp004_rows, exp007_rows)
    return [
        GridSection(
            "Round 1 — Experiment 003",
            "experiments/003_five_model_sweep_20260522_195526 (+ opus from 005)",
            exp003_rows,
            SOLVERS,
        ),
        GridSection(
            "Round 2 — Experiment 004",
            "experiments/004_feedback_sweep_20260522_225208 (+ opus from 006)",
            exp004_rows,
            SOLVERS,
        ),
        GridSection(
            "Round 3 — Raw Experiment 007",
            "experiments/007_full_feedback_6x6_20260523_172919",
            exp007_rows,
            SOLVERS_CURRENT,
        ),
        GridSection(
            "Round 3 — Canonical (incumbent carry-forward)",
            "004 incumbent + 007 challengers (see experiments/canonical/README.md)",
            canonical_round3_rows,
            SOLVERS_CURRENT,
        ),
    ]


def format_scores(row: list[str]) -> str:
    return ", ".join(row[2:])


def section_table(
    section: GridSection,
    gamma: float,
) -> list[str]:
    creator_indices = resolve_creator_indices(section.rows, section.solvers)
    ranking = creator_score_quality_ranking(section.rows, creator_indices, gamma=gamma)
    rank_by_label = {label: rank for rank, (label, _score) in enumerate(ranking, start=1)}

    lines = [
        f"## {section.title}",
        "",
        f"Source: `{section.experiment}`",
        "",
        "| rank | creator | benchmark | quality | zeros | solver scores |",
        "|---:|---|---|---:|---:|---|",
    ]
    for row, creator_index in zip(section.rows, creator_indices):
        label = row[0]
        quality = creator_score_quality(row, creator_index, gamma=gamma)
        zeros = zero_count(row, creator_index)
        rank = rank_by_label[label]
        lines.append(
            f"| {rank} | {label} | {row[1]} | {quality:.1f} | {zeros} | {format_scores(row)} |"
        )
    lines.append("")
    return lines


def best_row_per_creator(all_rows: list[tuple[str, list[str], int | None, float]]) -> list[str]:
    best: dict[str, tuple[str, float, str]] = {}
    for round_label, row, _creator_index, quality in all_rows:
        creator = normalize_creator_label(row[0])
        benchmark = row[1]
        current = best.get(creator)
        if current is None or quality > current[1]:
            best[creator] = (round_label, quality, benchmark)

    lines = [
        "## Best row per creator (across all grids)",
        "",
        "| creator | best quality | round | benchmark |",
        "|---|---:|---|---|",
    ]
    for creator in sorted(best, key=lambda c: best[c][1], reverse=True):
        round_label, quality, benchmark = best[creator]
        lines.append(f"| {creator} | {quality:.1f} | {round_label} | {benchmark} |")
    lines.append("")
    return lines


def build_report(gamma: float = 7.0) -> str:
    sections = load_grids()
    lines = [
        "# Creator Quality Scores",
        "",
        "Generated by `scripts/build_creator_quality_results.py` from saved score JSONs.",
        "",
        "Each row is scored with `creator_score_quality`: the average of per-cell "
        "`quality_index` values over non-creator solvers (creator's own column excluded).",
        f"Default Lorentzian width: `gamma={gamma}` (peak at 7/30 → 100, floor at 30/30 → 10, "
        "score 0 → 0).",
        "",
        "Grids match Rohit's canonical presentation in `experiments/canonical/README.md`, "
        "plus the raw Experiment 007 grid before incumbent carry-forward.",
        "",
    ]

    all_rows: list[tuple[str, list[str], int | None, float]] = []
    for section in sections:
        lines.extend(section_table(section, gamma))
        creator_indices = resolve_creator_indices(section.rows, section.solvers)
        short_round = section.title.split("—", 1)[0].strip()
        for row, creator_index in zip(section.rows, creator_indices):
            quality = creator_score_quality(row, creator_index, gamma=gamma)
            all_rows.append((short_round, row, creator_index, quality))

    lines.extend(best_row_per_creator(all_rows))

    global_ranking = sorted(all_rows, key=lambda item: item[3], reverse=True)
    lines.extend(
        [
            "## All rows ranked globally",
            "",
            "| rank | round | creator | benchmark | quality | zeros |",
            "|---:|---|---|---|---:|---:|",
        ]
    )
    for rank, (round_label, row, creator_index, quality) in enumerate(global_ranking, start=1):
        zeros = zero_count(row, creator_index)
        lines.append(
            f"| {rank} | {round_label} | {row[0]} | {row[1]} | {quality:.1f} | {zeros} |"
        )
    lines.append("")
    return "\n".join(lines)


def main() -> None:
    report = build_report()
    OUTPUT.write_text(report, encoding="utf-8")
    print(f"Wrote {OUTPUT.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
