#!/usr/bin/env python3
"""Run extra solver models against an existing BenchBench sweep.

This is the cheap path for adding a new model family to a saved creator grid:
keep the existing generated benchmark packages fixed and add new solver columns.
"""

from __future__ import annotations

import argparse
import json
import os
import re
import shutil
import subprocess
import tempfile
from pathlib import Path
from typing import Any

from benchbench_model_backends import (
    ModelSpec,
    antigravity_model_id_from_label,
    claude_metadata,
    claude_tokens_used,
    parse_antigravity_selected_label,
    parse_model_spec,
    run_cmd,
    run_model,
    safe_name,
)
from benchbench_results import (
    candidate_title,
    extract_solver_predictions,
    read_jsonl,
    score_summary,
    write_jsonl,
)


ROOT = Path(__file__).resolve().parent
DEFAULT_RUN_ROOT = ROOT / "experiments" / "002_broad_sweep_20260515_220653"
PYTHON = shutil.which("python") or shutil.which("python3") or "python3"


SOLVER_PROMPT = """
You are {agent_label} acting as a blind BenchBench solver.

You are in an isolated solver bundle at:

{solver_bundle_path}

Use that exact directory as the working directory for every shell command and
file read/write. Some agent CLIs may open a global scratch directory by
default; ignore that scratch directory and work only in the solver bundle
above.

You may use any local computation, shell scripts, installed packages, OCR,
image processing, code, and internet access if useful. Try your best to solve
the benchmark.

The only forbidden action is inspecting parent directories or files outside this
isolated solver bundle. Do not look for gold files, generators, scorers, private
traces, or answer keys outside this directory.

Read every visible file in this bundle and solve every item.

Return only JSONL, one object per item, with exactly:
{{"id":"...","answer":"..."}}
"""


def creator_name_from_candidate_dir(candidate_dir: Path) -> str:
    slug = candidate_dir.name.replace("candidate_created_by_", "")
    match = re.fullmatch(r"gpt_5_(\d+)", slug)
    if match:
        return f"gpt-5.{match.group(1)}"
    match = re.fullmatch(r"gemini_3_(\d+)_(.+)", slug)
    if match:
        return f"gemini-3.{match.group(1)}-{match.group(2).replace('_', '-')}"
    return slug.replace("_", "-")


def effective_solver_name(spec: ModelSpec, result: dict[str, Any]) -> str:
    if spec.provider == "antigravity" and spec.name == "current" and result.get("antigravity_actual_label"):
        return antigravity_model_id_from_label(str(result["antigravity_actual_label"]))
    return spec.name


def candidate_dirs(run_root: Path, requested_creators: set[str] | None) -> list[Path]:
    run_dir = run_root / "run"
    candidates = sorted(path for path in run_dir.glob("candidate_created_by_*") if path.is_dir())
    if not requested_creators:
        return candidates
    wanted_slugs = {safe_name(name) for name in requested_creators}
    return [path for path in candidates if path.name.replace("candidate_created_by_", "") in wanted_slugs]


def run_one(
    run_root: Path,
    candidate_dir: Path,
    solver_spec: ModelSpec,
    effort: str,
    timeout: int,
    force: bool,
) -> dict[str, Any]:
    run_dir = run_root / "run"
    creator_model = creator_name_from_candidate_dir(candidate_dir)
    provisional_solver_slug = safe_name(solver_spec.name)
    raw_slug = f"{safe_name(creator_model)}__solved_by__{provisional_solver_slug}"
    raw_out_path = run_dir / f"solver_{raw_slug}.jsonl"
    solver_dir = run_dir / f"isolated_solver_{raw_slug}"
    provisional_predictions_path = candidate_dir / f"predictions_solver_{provisional_solver_slug}.jsonl"
    provisional_score_path = candidate_dir / f"score_solver_{provisional_solver_slug}.json"

    if solver_spec.name != "current" and provisional_score_path.exists() and not force:
        existing_score = score_summary(provisional_score_path)
        prediction_rows = None
        if provisional_predictions_path.exists():
            try:
                prediction_rows = len(read_jsonl(provisional_predictions_path))
            except Exception:
                prediction_rows = None
        log_path = raw_out_path.with_suffix(".agy.log")
        stdout_path = raw_out_path.with_suffix(".stdout.txt")
        stderr_path = raw_out_path.with_suffix(".stderr.txt")
        prompt_path = raw_out_path.with_suffix(".prompt.txt")
        actual_label = None
        if log_path.exists():
            actual_label = parse_antigravity_selected_label(log_path.read_text(encoding="utf-8", errors="replace"))
        tokens_used = 0
        claude_fields: dict[str, Any] = {}
        if solver_spec.provider == "claude" and stdout_path.exists():
            try:
                data = json.loads(stdout_path.read_text(encoding="utf-8"))
            except Exception:
                data = {}
            if isinstance(data, dict):
                tokens_used = claude_tokens_used(data)
                claude_fields = claude_metadata(data, solver_spec)
        result = {
            "phase": "solver_extension",
            "model": solver_spec.name,
            "display_model": solver_spec.display_name,
            "provider": solver_spec.provider,
            "returncode": 0,
            "tokens_used": tokens_used,
            "out_path": str(raw_out_path),
            "stdout_path": str(stdout_path),
            "stderr_path": str(stderr_path),
            "prompt_path": str(prompt_path),
            "antigravity_log_path": str(log_path) if log_path.exists() else None,
            "antigravity_expected_label": solver_spec.antigravity_expected_label,
            "antigravity_actual_label": actual_label,
            "model_mismatch": bool(solver_spec.antigravity_expected_label and actual_label and actual_label != solver_spec.antigravity_expected_label),
            "creator_model": creator_model,
            "solver_model": solver_spec.name,
            "solver_display_model": solver_spec.display_name,
            "benchmark": candidate_title(candidate_dir),
            "prediction_rows": prediction_rows,
            "predictions_path": str(provisional_predictions_path),
            "score_path": str(provisional_score_path),
            "score_returncode": 0,
            "score_stdout": "",
            "score_stderr": "existing score reused; pass --force to rerun",
            "score_summary": existing_score,
            "skipped_existing": True,
        }
        result.update(claude_fields)
        return result

    antigravity_temp_dir: Path | None = None
    if solver_spec.provider in {"antigravity", "claude"}:
        antigravity_temp_dir = Path(tempfile.mkdtemp(prefix=f"benchbench_{raw_slug}_"))
        solver_dir = antigravity_temp_dir
        shutil.copytree(candidate_dir / "solver_bundle", solver_dir, dirs_exist_ok=True)
    else:
        if solver_dir.exists():
            shutil.rmtree(solver_dir)
        shutil.copytree(candidate_dir / "solver_bundle", solver_dir)
    item_ids = [str(row["id"]) for row in read_jsonl(solver_dir / "items_private_sample.jsonl")]

    result = run_model(
        solver_spec,
        SOLVER_PROMPT.format(agent_label=solver_spec.agent_label, solver_bundle_path=solver_dir),
        raw_out_path,
        solver_dir,
        effort,
        timeout,
    )
    solver_model = effective_solver_name(solver_spec, result)
    solver_slug = safe_name(solver_model)
    predictions_path = candidate_dir / f"predictions_solver_{solver_slug}.jsonl"
    score_path = candidate_dir / f"score_solver_{solver_slug}.json"

    if score_path.exists() and not force:
        if antigravity_temp_dir is not None:
            shutil.rmtree(antigravity_temp_dir, ignore_errors=True)
        result.update(
            {
                "phase": "solver_extension",
                "creator_model": creator_model,
                "solver_model": solver_model,
                "solver_display_model": solver_spec.display_name,
                "benchmark": candidate_title(candidate_dir),
                "prediction_rows": None,
                "predictions_path": str(predictions_path),
                "score_path": str(score_path),
                "score_returncode": 0,
                "score_stdout": "",
                "score_stderr": "skipped existing score; pass --force to rerun",
                "score_summary": score_summary(score_path),
                "skipped_existing": True,
            }
        )
        return result

    predictions, prediction_source = (
        ([], str(raw_out_path))
        if result.get("model_mismatch")
        else extract_solver_predictions(raw_out_path, solver_dir, item_ids)
    )
    write_jsonl(predictions_path, predictions)
    if result.get("model_mismatch"):
        completed = subprocess.CompletedProcess(
            [], 86, "", "skipped scoring because Antigravity selected-model check failed"
        )
    else:
        completed = run_cmd(
            [
                PYTHON,
                "scorer.py",
                "--gold",
                "gold_private_sample.jsonl",
                "--predictions",
                str(predictions_path),
                "--out",
                str(score_path),
            ],
            candidate_dir,
            timeout=420,
        )
    if antigravity_temp_dir is not None:
        shutil.rmtree(antigravity_temp_dir, ignore_errors=True)

    result.update(
        {
            "phase": "solver_extension",
            "creator_model": creator_model,
            "solver_model": solver_model,
            "solver_display_model": solver_spec.display_name,
            "benchmark": candidate_title(candidate_dir),
            "prediction_rows": len(predictions),
            "prediction_source": prediction_source,
            "predictions_path": str(predictions_path),
            "score_path": str(score_path),
            "score_returncode": completed.returncode,
            "score_stdout": completed.stdout[-4000:],
            "score_stderr": completed.stderr[-4000:],
            "score_summary": score_summary(score_path),
            "skipped_existing": False,
        }
    )
    return result


def write_summary(run_root: Path, solver_spec: ModelSpec, manifest: list[dict[str, Any]]) -> Path:
    suffix = safe_name(solver_spec.name)
    summary_path = run_root / f"solver_extension_{suffix}.md"
    manifest_path = run_root / f"solver_extension_{suffix}_manifest.json"
    lines = [f"# Solver Extension: {solver_spec.display_name}", ""]
    lines.append(f"Run root: `{run_root}`")
    lines.append(f"Solver spec: `{solver_spec.name}`")
    lines.append(f"Provider: `{solver_spec.provider}`")
    if solver_spec.provider == "antigravity":
        lines.append(f"Expected Antigravity model label: `{solver_spec.antigravity_expected_label or 'current selected model'}`")
    if solver_spec.provider == "claude":
        lines.append(f"Claude max budget per call: `${os.getenv('BENCHBENCH_CLAUDE_MAX_BUDGET_USD', '25')}`")
    lines.append("")
    lines.append("| creator | benchmark | rows | score | accuracy | Claude cost | Claude cache read | returncode | actual model |")
    lines.append("|---|---|---:|---:|---:|---:|---:|---:|---|")
    for item in manifest:
        score = item.get("score_summary") or {}
        actual = item.get("antigravity_actual_label") or item.get("solver_display_model") or item.get("solver_model")
        rows = item.get("prediction_rows")
        lines.append(
            "| {creator} | {bench} | {rows} | {correct}/{total} | {acc} | {cost} | {cache_read} | {rc} | {actual} |".format(
                creator=item.get("creator_model"),
                bench=item.get("benchmark"),
                rows=rows,
                correct=score.get("correct", "NA"),
                total=score.get("total", "NA"),
                acc=score.get("accuracy", "NA"),
                cost=item.get("claude_total_cost_usd", ""),
                cache_read=item.get("claude_cache_read_input_tokens", ""),
                rc=item.get("returncode"),
                actual=actual,
            )
        )
    lines.append("")
    claude_cost = sum(float(item.get("claude_total_cost_usd") or 0) for item in manifest)
    if claude_cost:
        lines.append(f"Total reported Claude cost: `${claude_cost:.4f}`")
        lines.append("")
    summary_path.write_text("\n".join(lines) + "\n", encoding="utf-8")
    manifest_path.write_text(json.dumps(manifest, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    return summary_path


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Add solver results to an existing BenchBench sweep.")
    parser.add_argument("--run-root", type=Path, default=DEFAULT_RUN_ROOT)
    parser.add_argument(
        "--solver",
        default="agy:current",
        help="Solver model spec. Examples: agy:gemini-3.5-flash-high, agy:gemini-3.1-pro, claude:sonnet, gpt-5.5.",
    )
    parser.add_argument("--creator-models", nargs="*", default=None, help="Optional creator model names to include.")
    parser.add_argument("--effort", default="low", help="Codex reasoning effort; metadata only for Antigravity.")
    parser.add_argument("--timeout-seconds", type=int, default=1500)
    parser.add_argument("--force", action="store_true", help="Rerun cells even when score files already exist.")
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    run_root = args.run_root if args.run_root.is_absolute() else ROOT / args.run_root
    solver_spec = parse_model_spec(args.solver)
    creators = set(args.creator_models) if args.creator_models else None
    candidates = candidate_dirs(run_root, creators)
    if not candidates:
        raise SystemExit(f"No candidate directories found under {run_root / 'run'}")

    manifest: list[dict[str, Any]] = []
    for candidate_dir in candidates:
        creator_model = creator_name_from_candidate_dir(candidate_dir)
        print(f"[solver-extension:start] creator={creator_model} solver={solver_spec.name}", flush=True)
        result = run_one(run_root, candidate_dir, solver_spec, args.effort, args.timeout_seconds, args.force)
        manifest.append(result)
        print(
            f"[solver-extension:done] creator={creator_model} solver={result.get('solver_model')} "
            f"rows={result.get('prediction_rows')} score={result.get('score_summary')} rc={result.get('returncode')}",
            flush=True,
        )

    print(write_summary(run_root, solver_spec, manifest), flush=True)


if __name__ == "__main__":
    main()
