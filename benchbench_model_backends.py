#!/usr/bin/env python3
"""Model backend helpers for BenchBench runners."""

from __future__ import annotations

from dataclasses import dataclass
from contextlib import contextmanager
import json
import os
from pathlib import Path
import re
import shutil
import signal
import subprocess
from typing import Any


KNOWN_ANTIGRAVITY_MODELS = {
    "current": (None, "Antigravity current model"),
    "gemini-3.5-flash-high": ("Gemini 3.5 Flash (High)", "Gemini 3.5 Flash (High)"),
    "gemini-3.1-pro": ("Gemini 3.1 Pro (High)", "Gemini 3.1 Pro (High)"),
    "gemini-3.1-pro-high": ("Gemini 3.1 Pro (High)", "Gemini 3.1 Pro (High)"),
    "gemini-3.1-pro-low": ("Gemini 3.1 Pro (Low)", "Gemini 3.1 Pro (Low)"),
    "claude-sonnet-4.6-thinking": ("Claude Sonnet 4.6 (Thinking)", "Claude Sonnet 4.6 (Thinking)"),
    "claude-sonnet-4.6": ("Claude Sonnet 4.6 (Thinking)", "Claude Sonnet 4.6 (Thinking)"),
    "claude-sonnet": ("Claude Sonnet 4.6 (Thinking)", "Claude Sonnet 4.6 (Thinking)"),
    "claude-opus-4.6-thinking": ("Claude Opus 4.6 (Thinking)", "Claude Opus 4.6 (Thinking)"),
    "claude-opus-4.6": ("Claude Opus 4.6 (Thinking)", "Claude Opus 4.6 (Thinking)"),
    "claude-opus": ("Claude Opus 4.6 (Thinking)", "Claude Opus 4.6 (Thinking)"),
}

KNOWN_CLAUDE_MODELS = {
    "sonnet": ("sonnet", "Claude Sonnet"),
    "opus": ("opus", "Claude Opus"),
    "haiku": ("haiku", "Claude Haiku"),
    "claude-sonnet-4-6": ("claude-sonnet-4-6", "Claude Sonnet 4.6"),
    "claude-opus-4-6": ("claude-opus-4-6", "Claude Opus 4.6"),
    "claude-haiku-4-5": ("claude-haiku-4-5", "Claude Haiku 4.5"),
}

KNOWN_CURSOR_MODELS = {
    "claude-opus": ("claude-4.6-opus-high-thinking", "Claude Opus 4.6 Thinking"),
    "opus": ("claude-4.6-opus-high-thinking", "Claude Opus 4.6 Thinking"),
    "claude-opus-4.6-thinking": ("claude-4.6-opus-high-thinking", "Claude Opus 4.6 Thinking"),
    "claude-4.6-opus-high-thinking": ("claude-4.6-opus-high-thinking", "Claude Opus 4.6 Thinking"),
    "claude-opus-4.7-thinking-high": ("claude-opus-4-7-thinking-high", "Claude Opus 4.7 High Thinking"),
    "claude-opus-4-7-thinking-high": ("claude-opus-4-7-thinking-high", "Claude Opus 4.7 High Thinking"),
    "opus-4.7-thinking-high": ("claude-opus-4-7-thinking-high", "Claude Opus 4.7 High Thinking"),
    "fable": ("claude-fable-5-thinking-high", "Claude Fable 5 Thinking"),
    "fable-5": ("claude-fable-5-thinking-high", "Claude Fable 5 Thinking"),
    "claude-fable-5": ("claude-fable-5-thinking-high", "Claude Fable 5 Thinking"),
    "claude-fable-5-thinking-high": ("claude-fable-5-thinking-high", "Claude Fable 5 Thinking"),
    "fable-xhigh": ("claude-fable-5-thinking-xhigh", "Claude Fable 5 Extra High Thinking"),
    "claude-fable-5-thinking-xhigh": ("claude-fable-5-thinking-xhigh", "Claude Fable 5 Extra High Thinking"),
}

ANTIGRAVITY_SETTINGS_PATH = Path.home() / ".gemini" / "antigravity-cli" / "settings.json"
ANTIGRAVITY_SETTINGS_LOCK_PATH = Path.home() / ".gemini" / "antigravity-cli" / "benchbench_model.lock"
DEFAULT_CLAUDE_MAX_BUDGET_USD = "25"


@dataclass(frozen=True)
class ModelSpec:
    """A model plus the local runner that can invoke it."""

    name: str
    provider: str
    display_name: str
    codex_model: str | None = None
    antigravity_expected_label: str | None = None
    claude_model: str | None = None
    cursor_model: str | None = None

    @property
    def agent_label(self) -> str:
        if self.provider == "codex":
            return f"{self.display_name}+Codex"
        if self.provider == "antigravity":
            return f"{self.display_name}+Antigravity"
        if self.provider == "claude":
            return f"{self.display_name}+Claude Code"
        if self.provider == "cursor":
            return f"{self.display_name}+Cursor"
        return self.display_name


def safe_name(name: str) -> str:
    """Return a stable filesystem slug for model and benchmark identifiers."""

    cleaned = re.sub(r"[^A-Za-z0-9]+", "_", name.strip().lower()).strip("_")
    return cleaned or "model"


def parse_model_spec(value: str) -> ModelSpec:
    """Parse a model spec.

    Unprefixed values are Codex model names, preserving the historical runner
    behavior. Antigravity specs use `agy:<model>` or `antigravity:<model>`.
    Claude Code specs use `claude:<model>` or `anthropic:<model>`.
    Cursor specs use `cursor:<model>`.
    Because `agy --print` does not expose a model flag, Antigravity specs are
    checked after the run against the selected model label in the CLI log.
    """

    raw = value.strip()
    lowered = raw.lower()
    for prefix in ("agy:", "antigravity:"):
        if lowered.startswith(prefix):
            model_id = lowered[len(prefix) :].strip()
            expected, display = KNOWN_ANTIGRAVITY_MODELS.get(
                model_id,
                (None, raw[len(prefix) :].strip() or "Antigravity current model"),
            )
            return ModelSpec(
                name=model_id or "current",
                provider="antigravity",
                display_name=display,
                antigravity_expected_label=expected,
            )
    for prefix in ("claude:", "anthropic:"):
        if lowered.startswith(prefix):
            requested = raw[len(prefix) :].strip()
            model_id = requested.lower() or "sonnet"
            claude_model, display = KNOWN_CLAUDE_MODELS.get(
                model_id,
                (requested or "sonnet", requested or "Claude Sonnet"),
            )
            return ModelSpec(
                name=model_id,
                provider="claude",
                display_name=display,
                claude_model=claude_model,
            )
    for prefix in ("cursor:", "cursor-agent:"):
        if lowered.startswith(prefix):
            requested = raw[len(prefix) :].strip()
            model_id = requested.lower() or "claude-opus"
            cursor_model, display = KNOWN_CURSOR_MODELS.get(
                model_id,
                (requested or "claude-4.6-opus-high-thinking", requested or "Cursor model"),
            )
            return ModelSpec(
                name=model_id,
                provider="cursor",
                display_name=display,
                cursor_model=cursor_model,
            )
    return ModelSpec(name=raw, provider="codex", display_name=raw, codex_model=raw)


def parse_tokens(text: str) -> int:
    matches = re.findall(r"tokens used\s+(\d[\d,]*)", text)
    return int(matches[-1].replace(",", "")) if matches else 0


def parse_antigravity_selected_label(log_text: str) -> str | None:
    matches = re.findall(r'Propagating selected model override to backend: label="([^"]+)"', log_text)
    return matches[-1] if matches else None


def claude_tokens_used(data: dict[str, Any]) -> int:
    model_usage = data.get("modelUsage")
    if isinstance(model_usage, dict):
        total = 0
        for usage_item in model_usage.values():
            if not isinstance(usage_item, dict):
                continue
            total += sum(
                int(usage_item.get(key) or 0)
                for key in [
                    "inputTokens",
                    "cacheCreationInputTokens",
                    "cacheReadInputTokens",
                    "outputTokens",
                ]
            )
        if total:
            return total

    usage = data.get("usage")
    if not isinstance(usage, dict):
        return 0
    return sum(
        int(usage.get(key) or 0)
        for key in [
            "input_tokens",
            "cache_creation_input_tokens",
            "cache_read_input_tokens",
            "output_tokens",
        ]
    )


def claude_cache_summary(data: dict[str, Any]) -> dict[str, int]:
    usage = data.get("usage")
    if isinstance(usage, dict):
        summary = {
            "cache_creation_input_tokens": int(usage.get("cache_creation_input_tokens") or 0),
            "cache_read_input_tokens": int(usage.get("cache_read_input_tokens") or 0),
        }
        if summary["cache_creation_input_tokens"] or summary["cache_read_input_tokens"]:
            return summary

    model_usage = data.get("modelUsage")
    if isinstance(model_usage, dict):
        return {
            "cache_creation_input_tokens": sum(
                int(item.get("cacheCreationInputTokens") or 0)
                for item in model_usage.values()
                if isinstance(item, dict)
            ),
            "cache_read_input_tokens": sum(
                int(item.get("cacheReadInputTokens") or 0)
                for item in model_usage.values()
                if isinstance(item, dict)
            ),
        }
    return {"cache_creation_input_tokens": 0, "cache_read_input_tokens": 0}


def claude_metadata(data: dict[str, Any], spec: ModelSpec) -> dict[str, Any]:
    cache_summary = claude_cache_summary(data)
    return {
        "claude_model": spec.claude_model or spec.name,
        "claude_total_cost_usd": data.get("total_cost_usd"),
        "claude_usage": data.get("usage") if isinstance(data.get("usage"), dict) else {},
        "claude_model_usage": data.get("modelUsage") if isinstance(data.get("modelUsage"), dict) else {},
        "claude_cache_creation_input_tokens": cache_summary["cache_creation_input_tokens"],
        "claude_cache_read_input_tokens": cache_summary["cache_read_input_tokens"],
    }


def cursor_tokens_used(data: dict[str, Any]) -> int:
    usage = data.get("usage")
    if not isinstance(usage, dict):
        return 0
    return sum(
        int(usage.get(key) or 0)
        for key in ["inputTokens", "cacheWriteTokens", "cacheReadTokens", "outputTokens"]
    )


def cursor_metadata(data: dict[str, Any], spec: ModelSpec) -> dict[str, Any]:
    usage = data.get("usage") if isinstance(data.get("usage"), dict) else {}
    return {
        "cursor_model": spec.cursor_model or spec.name,
        "cursor_usage": usage,
        "cursor_cache_write_tokens": int(usage.get("cacheWriteTokens") or 0),
        "cursor_cache_read_tokens": int(usage.get("cacheReadTokens") or 0),
    }


def antigravity_model_id_from_label(label: str) -> str:
    for model_id, (expected, _display) in KNOWN_ANTIGRAVITY_MODELS.items():
        if expected == label:
            return model_id
    return safe_name(label).replace("_", "-")


def format_go_duration(seconds: int) -> str:
    return f"{int(seconds)}s"


def run_cmd(
    args: list[str],
    cwd: Path,
    stdin_text: str | None = None,
    timeout: int | None = None,
) -> subprocess.CompletedProcess[str]:
    process = subprocess.Popen(
        args,
        cwd=cwd,
        stdin=subprocess.PIPE if stdin_text is not None else None,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
        start_new_session=True,
    )
    try:
        stdout, stderr = process.communicate(input=stdin_text, timeout=timeout)
    except subprocess.TimeoutExpired as exc:
        try:
            os.killpg(process.pid, signal.SIGKILL)
        except (PermissionError, ProcessLookupError):
            try:
                process.kill()
            except (PermissionError, ProcessLookupError):
                pass
        try:
            stdout, stderr = process.communicate(timeout=2)
        except subprocess.TimeoutExpired:
            stdout = exc.stdout or ""
            stderr = exc.stderr or ""
        exc.stdout = stdout
        exc.stderr = stderr
        raise exc
    return subprocess.CompletedProcess(args, process.returncode, stdout, stderr)


def _write_json_atomic(path: Path, data: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp_path = path.with_name(f".{path.name}.tmp.{os.getpid()}")
    tmp_path.write_text(json.dumps(data, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    tmp_path.replace(path)


@contextmanager
def antigravity_model_setting(label: str | None):
    """Temporarily select an Antigravity model for one `agy` call.

    `agy --print` does not expose a model flag, but the CLI reads its selected
    model from `~/.gemini/antigravity-cli/settings.json`. Keep the override
    small and restore the user's original settings after the subprocess exits.
    """

    if not label:
        yield
        return

    try:
        import fcntl
    except ImportError:  # pragma: no cover - non-POSIX fallback
        fcntl = None  # type: ignore[assignment]

    ANTIGRAVITY_SETTINGS_LOCK_PATH.parent.mkdir(parents=True, exist_ok=True)
    with ANTIGRAVITY_SETTINGS_LOCK_PATH.open("w", encoding="utf-8") as lock_handle:
        if fcntl is not None:
            fcntl.flock(lock_handle.fileno(), fcntl.LOCK_EX)

        original_text = ANTIGRAVITY_SETTINGS_PATH.read_text(encoding="utf-8") if ANTIGRAVITY_SETTINGS_PATH.exists() else None
        try:
            settings = json.loads(original_text) if original_text else {}
            if not isinstance(settings, dict):
                settings = {}
            settings["model"] = label
            _write_json_atomic(ANTIGRAVITY_SETTINGS_PATH, settings)
            yield
        finally:
            if original_text is None:
                try:
                    ANTIGRAVITY_SETTINGS_PATH.unlink()
                except FileNotFoundError:
                    pass
            else:
                ANTIGRAVITY_SETTINGS_PATH.write_text(original_text, encoding="utf-8")
            if fcntl is not None:
                fcntl.flock(lock_handle.fileno(), fcntl.LOCK_UN)


def _timeout_result(exc: subprocess.TimeoutExpired, timeout: int) -> tuple[str, str, int]:
    stdout = exc.stdout or ""
    stderr = exc.stderr or ""
    if isinstance(stdout, bytes):
        stdout = stdout.decode("utf-8", errors="replace")
    if isinstance(stderr, bytes):
        stderr = stderr.decode("utf-8", errors="replace")
    stderr += f"\nTIMEOUT after {timeout} seconds\n"
    return stdout, stderr, -124


def run_codex_model(spec: ModelSpec, prompt: str, out_path: Path, cwd: Path, effort: str, timeout: int) -> dict[str, Any]:
    prompt_path = out_path.with_suffix(".prompt.txt")
    prompt_path.write_text(prompt, encoding="utf-8")
    cmd = [
        "codex",
        "exec",
        "--skip-git-repo-check",
        "--ephemeral",
        "-m",
        spec.codex_model or spec.name,
        "-c",
        f'model_reasoning_effort="{effort}"',
        "--output-last-message",
        str(out_path),
        "-",
    ]
    try:
        completed = run_cmd(cmd, cwd, stdin_text=prompt, timeout=timeout)
        stdout = completed.stdout
        stderr = completed.stderr
        returncode = completed.returncode
    except subprocess.TimeoutExpired as exc:
        stdout, stderr, returncode = _timeout_result(exc, timeout)

    stdout_path = out_path.with_suffix(".stdout.txt")
    stderr_path = out_path.with_suffix(".stderr.txt")
    stdout_path.write_text(stdout, encoding="utf-8")
    stderr_path.write_text(stderr, encoding="utf-8")
    return {
        "model": spec.name,
        "display_model": spec.display_name,
        "provider": spec.provider,
        "returncode": returncode,
        "tokens_used": parse_tokens(stdout + "\n" + stderr),
        "out_path": str(out_path),
        "stdout_path": str(stdout_path),
        "stderr_path": str(stderr_path),
        "prompt_path": str(prompt_path),
    }


def run_antigravity_model(
    spec: ModelSpec,
    prompt: str,
    out_path: Path,
    cwd: Path,
    effort: str,
    timeout: int,
) -> dict[str, Any]:
    prompt_path = out_path.with_suffix(".prompt.txt")
    stdout_path = out_path.with_suffix(".stdout.txt")
    stderr_path = out_path.with_suffix(".stderr.txt")
    log_path = out_path.with_suffix(".agy.log")
    prompt_path.write_text(prompt, encoding="utf-8")

    agy = shutil.which("agy")
    if not agy:
        message = "Antigravity CLI `agy` was not found on PATH.\n"
        out_path.write_text("", encoding="utf-8")
        stdout_path.write_text("", encoding="utf-8")
        stderr_path.write_text(message, encoding="utf-8")
        return {
            "model": spec.name,
            "display_model": spec.display_name,
            "provider": spec.provider,
            "returncode": 127,
            "tokens_used": 0,
            "out_path": str(out_path),
            "stdout_path": str(stdout_path),
            "stderr_path": str(stderr_path),
            "prompt_path": str(prompt_path),
            "antigravity_log_path": str(log_path),
            "antigravity_expected_label": spec.antigravity_expected_label,
            "antigravity_actual_label": None,
            "model_mismatch": bool(spec.antigravity_expected_label),
            "effort": effort,
        }

    cmd = [
        agy,
        "--print",
        prompt,
        "--print-timeout",
        format_go_duration(timeout),
        "--log-file",
        str(log_path),
        "--dangerously-skip-permissions",
    ]
    try:
        with antigravity_model_setting(spec.antigravity_expected_label):
            completed = run_cmd(cmd, cwd, timeout=timeout + 30)
        stdout = completed.stdout
        stderr = completed.stderr
        returncode = completed.returncode
    except subprocess.TimeoutExpired as exc:
        stdout, stderr, returncode = _timeout_result(exc, timeout)

    out_path.write_text(stdout, encoding="utf-8")
    stdout_path.write_text(stdout, encoding="utf-8")
    stderr_path.write_text(stderr, encoding="utf-8")
    log_text = log_path.read_text(encoding="utf-8", errors="replace") if log_path.exists() else ""
    actual_label = parse_antigravity_selected_label(log_text)
    expected_label = spec.antigravity_expected_label
    model_mismatch = bool(expected_label and actual_label and actual_label != expected_label)
    if expected_label and not actual_label:
        model_mismatch = True
    if model_mismatch and returncode == 0:
        returncode = 86
        stderr += (
            "\nAntigravity selected-model mismatch: "
            f"expected {expected_label!r}, saw {actual_label!r}.\n"
        )
        stderr_path.write_text(stderr, encoding="utf-8")

    return {
        "model": spec.name,
        "display_model": spec.display_name,
        "provider": spec.provider,
        "returncode": returncode,
        "tokens_used": parse_tokens(stdout + "\n" + stderr + "\n" + log_text),
        "out_path": str(out_path),
        "stdout_path": str(stdout_path),
        "stderr_path": str(stderr_path),
        "prompt_path": str(prompt_path),
        "antigravity_log_path": str(log_path),
        "antigravity_expected_label": expected_label,
        "antigravity_actual_label": actual_label,
        "model_mismatch": model_mismatch,
        "effort": effort,
    }


def run_claude_model(spec: ModelSpec, prompt: str, out_path: Path, cwd: Path, effort: str, timeout: int) -> dict[str, Any]:
    prompt_path = out_path.with_suffix(".prompt.txt")
    stdout_path = out_path.with_suffix(".stdout.txt")
    stderr_path = out_path.with_suffix(".stderr.txt")
    prompt_path.write_text(prompt, encoding="utf-8")

    claude = shutil.which("claude")
    if not claude:
        message = "Claude Code CLI `claude` was not found on PATH.\n"
        out_path.write_text("", encoding="utf-8")
        stdout_path.write_text("", encoding="utf-8")
        stderr_path.write_text(message, encoding="utf-8")
        return {
            "model": spec.name,
            "display_model": spec.display_name,
            "provider": spec.provider,
            "returncode": 127,
            "tokens_used": 0,
            "out_path": str(out_path),
            "stdout_path": str(stdout_path),
            "stderr_path": str(stderr_path),
            "prompt_path": str(prompt_path),
            "effort": effort,
        }

    max_budget_usd = os.getenv("BENCHBENCH_CLAUDE_MAX_BUDGET_USD", DEFAULT_CLAUDE_MAX_BUDGET_USD)
    cmd = [
        claude,
        "-p",
        "--model",
        spec.claude_model or spec.name,
        "--effort",
        effort if effort in {"low", "medium", "high", "xhigh", "max"} else "low",
        "--permission-mode",
        "bypassPermissions",
        "--output-format",
        "json",
        "--no-session-persistence",
        "--exclude-dynamic-system-prompt-sections",
        "--max-budget-usd",
        max_budget_usd,
    ]
    try:
        completed = run_cmd(cmd, cwd, stdin_text=prompt, timeout=timeout)
        stdout = completed.stdout
        stderr = completed.stderr
        returncode = completed.returncode
    except subprocess.TimeoutExpired as exc:
        stdout, stderr, returncode = _timeout_result(exc, timeout)

    stdout_path.write_text(stdout, encoding="utf-8")
    stderr_path.write_text(stderr, encoding="utf-8")
    data: dict[str, Any] = {}
    try:
        parsed = json.loads(stdout)
        if isinstance(parsed, dict):
            data = parsed
    except json.JSONDecodeError:
        data = {}

    result_text = data.get("result") if isinstance(data.get("result"), str) else stdout
    out_path.write_text(result_text, encoding="utf-8")
    if data.get("is_error") and returncode == 0:
        returncode = 1

    return {
        "model": spec.name,
        "display_model": spec.display_name,
        "provider": spec.provider,
        "returncode": returncode,
        "tokens_used": claude_tokens_used(data),
        "out_path": str(out_path),
        "stdout_path": str(stdout_path),
        "stderr_path": str(stderr_path),
        "prompt_path": str(prompt_path),
        "effort": effort,
        **claude_metadata(data, spec),
    }


def run_cursor_model(spec: ModelSpec, prompt: str, out_path: Path, cwd: Path, effort: str, timeout: int) -> dict[str, Any]:
    prompt_path = out_path.with_suffix(".prompt.txt")
    stdout_path = out_path.with_suffix(".stdout.txt")
    stderr_path = out_path.with_suffix(".stderr.txt")
    prompt_path.write_text(prompt, encoding="utf-8")

    cursor_agent = shutil.which("cursor-agent")
    if not cursor_agent:
        message = "Cursor Agent CLI `cursor-agent` was not found on PATH.\n"
        out_path.write_text("", encoding="utf-8")
        stdout_path.write_text("", encoding="utf-8")
        stderr_path.write_text(message, encoding="utf-8")
        return {
            "model": spec.name,
            "display_model": spec.display_name,
            "provider": spec.provider,
            "returncode": 127,
            "tokens_used": 0,
            "out_path": str(out_path),
            "stdout_path": str(stdout_path),
            "stderr_path": str(stderr_path),
            "prompt_path": str(prompt_path),
            "effort": effort,
        }

    cmd = [
        cursor_agent,
        "--print",
        "--output-format",
        "json",
        "--model",
        spec.cursor_model or spec.name,
        "--force",
        "--trust",
        "--sandbox",
        "disabled",
        "--workspace",
        str(cwd),
    ]
    try:
        completed = run_cmd(cmd, cwd, stdin_text=prompt, timeout=timeout)
        stdout = completed.stdout
        stderr = completed.stderr
        returncode = completed.returncode
    except subprocess.TimeoutExpired as exc:
        stdout, stderr, returncode = _timeout_result(exc, timeout)

    stdout_path.write_text(stdout, encoding="utf-8")
    stderr_path.write_text(stderr, encoding="utf-8")
    data: dict[str, Any] = {}
    try:
        parsed = json.loads(stdout)
        if isinstance(parsed, dict):
            data = parsed
    except json.JSONDecodeError:
        data = {}

    result_text = data.get("result") if isinstance(data.get("result"), str) else stdout
    out_path.write_text(result_text, encoding="utf-8")
    if data.get("is_error") and returncode == 0:
        returncode = 1

    return {
        "model": spec.name,
        "display_model": spec.display_name,
        "provider": spec.provider,
        "returncode": returncode,
        "tokens_used": cursor_tokens_used(data),
        "out_path": str(out_path),
        "stdout_path": str(stdout_path),
        "stderr_path": str(stderr_path),
        "prompt_path": str(prompt_path),
        "effort": effort,
        **cursor_metadata(data, spec),
    }


def run_model(spec: ModelSpec, prompt: str, out_path: Path, cwd: Path, effort: str, timeout: int) -> dict[str, Any]:
    if spec.provider == "codex":
        return run_codex_model(spec, prompt, out_path, cwd, effort, timeout)
    if spec.provider == "antigravity":
        return run_antigravity_model(spec, prompt, out_path, cwd, effort, timeout)
    if spec.provider == "claude":
        return run_claude_model(spec, prompt, out_path, cwd, effort, timeout)
    if spec.provider == "cursor":
        return run_cursor_model(spec, prompt, out_path, cwd, effort, timeout)
    raise ValueError(f"Unsupported model provider: {spec.provider}")
