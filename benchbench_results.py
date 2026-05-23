#!/usr/bin/env python3
"""Shared result parsing helpers for BenchBench runners."""

from __future__ import annotations

import json
import re
from pathlib import Path
from typing import Any


SCORE_FRACTION_RE = re.compile(r"(?<![\d.])(\d+)\s*/\s*(\d+)(?![\d.])")


def read_jsonl(path: Path) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    with path.open("r", encoding="utf-8") as handle:
        for line in handle:
            line = line.strip()
            if line:
                rows.append(json.loads(line))
    return rows


def write_jsonl(path: Path, rows: list[dict[str, Any]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as handle:
        for row in rows:
            handle.write(json.dumps(row, ensure_ascii=True, separators=(",", ":")) + "\n")


def _score_from_fraction(text: str) -> dict[str, Any] | None:
    match = SCORE_FRACTION_RE.search(text)
    if not match:
        return None
    correct = int(match.group(1))
    total = int(match.group(2))
    return {"total": total, "correct": correct, "accuracy": 0.0 if total == 0 else correct / total}


def score_summary(path: Path) -> dict[str, Any] | None:
    """Parse the loose score-report shapes produced by generated benchmarks."""

    if not path.exists():
        return None
    text = path.read_text(encoding="utf-8", errors="replace")
    try:
        data = json.loads(text)
    except Exception:
        return _score_from_fraction(text)

    if not isinstance(data, dict):
        return _score_from_fraction(text)

    total = data.get("total", data.get("n_items", data.get("total_gold", data.get("total_items"))))
    correct = data.get("correct", data.get("n_correct", data.get("exact_match", data.get("correct_predictions"))))
    accuracy = data.get("accuracy")

    if correct is None and isinstance(data.get("score"), (int, float)):
        correct = data["score"]
    if correct is None and isinstance(data.get("score"), str):
        parsed = _score_from_fraction(data["score"])
        if parsed:
            correct = parsed["correct"]
            total = parsed["total"]

    details = data.get("details", data.get("per_item", data.get("results")))
    if (total is None or correct is None) and isinstance(details, list):
        total = len(details)
        correct = sum(1 for row in details if isinstance(row, dict) and row.get("correct") is True)

    if total is None or correct is None:
        return _score_from_fraction(text)

    total_int = int(total)
    correct_int = int(correct)
    if accuracy is None:
        accuracy = 0.0 if total_int == 0 else correct_int / total_int
    return {"total": total_int, "correct": correct_int, "accuracy": accuracy}


def extract_predictions(raw: str, item_ids: list[str]) -> list[dict[str, Any]]:
    """Extract strict BenchBench prediction rows from noisy model output."""

    wanted = set(item_ids)
    by_id: dict[str, Any] = {}
    for line in raw.splitlines():
        stripped = line.strip().strip(",")
        if not (stripped.startswith("{") and stripped.endswith("}")):
            continue
        try:
            obj = json.loads(stripped)
        except Exception:
            continue
        if not isinstance(obj, dict) or set(obj) != {"id", "answer"}:
            continue
        row_id = str(obj.get("id"))
        if row_id in wanted:
            by_id[row_id] = obj["answer"]
    return [{"id": item_id, "answer": by_id[item_id]} for item_id in item_ids if item_id in by_id]


def extract_solver_predictions(raw_out_path: Path, solver_dir: Path, item_ids: list[str]) -> tuple[list[dict[str, Any]], str]:
    """Prefer a solver-written predictions.jsonl when it has more usable rows."""

    raw = raw_out_path.read_text(encoding="utf-8", errors="replace") if raw_out_path.exists() else ""
    stdout_predictions = extract_predictions(raw, item_ids)

    file_path = solver_dir / "predictions.jsonl"
    file_predictions: list[dict[str, Any]] = []
    if file_path.exists():
        file_predictions = extract_predictions(file_path.read_text(encoding="utf-8", errors="replace"), item_ids)

    if len(file_predictions) > len(stdout_predictions):
        return file_predictions, str(file_path)
    if stdout_predictions:
        return stdout_predictions, str(raw_out_path)
    return [], str(raw_out_path)


def candidate_title(candidate_dir: Path) -> str:
    spec = candidate_dir / "benchmark_spec.json"
    if spec.exists():
        try:
            data = json.loads(spec.read_text(encoding="utf-8"))
        except Exception:
            data = None
        if isinstance(data, dict):
            for key in ["benchmark_name", "name", "title", "benchmark_id", "benchmark"]:
                if data.get(key):
                    return str(data[key])

    readme = candidate_dir / "README.md"
    if readme.exists():
        for line in readme.read_text(encoding="utf-8", errors="replace").splitlines():
            if line.startswith("#"):
                return line.lstrip("#").strip()
    return candidate_dir.name
