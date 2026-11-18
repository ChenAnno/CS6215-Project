"""LLM backend of NSCG: headless Claude Code (`claude -p`) with structured output.

Every request is cached on disk under results/llm-cache/<sha256>.json (prompt, schema,
model, raw response, structured output, usage, cost, wall time), so a rerun of the
pipeline is free and deterministic, and the exact prompts of every reported number are
part of the artifact. Set NSCG_OFFLINE=1 to forbid new requests (replay from the cache).

Another OpenAI-compatible backend (e.g. SoCLaaS) can be used with NSCG_BACKEND=openai,
OPENAI_BASE_URL, OPENAI_API_KEY and --model <served model name>.
"""

from __future__ import annotations

import hashlib
import json
import os
import subprocess
import tempfile
import threading
import time
from pathlib import Path

PROJECT = Path(__file__).resolve().parent.parent
CACHE = Path(os.environ.get("NSCG_CACHE", PROJECT / "results" / "llm-cache"))
_lock = threading.Lock()
STATS = {"requests": 0, "cache_hits": 0, "cost_usd": 0.0, "input_tokens": 0, "output_tokens": 0,
         "cache_read_tokens": 0, "cache_write_tokens": 0, "failures": 0, "seconds": 0.0}


class LLMError(RuntimeError):
    pass


def _key(model, system, schema, prompt):
    h = hashlib.sha256()
    parts = [model, system, json.dumps(schema, sort_keys=True), prompt]
    if os.environ.get("NSCG_REPEAT"):  # an independent repetition: same prompt, a new sample
        parts.append("repeat=" + os.environ["NSCG_REPEAT"])
    for part in parts:
        h.update(part.encode())
        h.update(b"\0")
    return h.hexdigest()


def _account(rec, hit):
    with _lock:
        if hit:
            STATS["cache_hits"] += 1
        else:
            STATS["requests"] += 1
        u = rec.get("usage") or {}
        STATS["cost_usd"] += rec.get("cost_usd") or 0.0
        STATS["input_tokens"] += u.get("input_tokens", 0)
        STATS["output_tokens"] += u.get("output_tokens", 0)
        STATS["cache_read_tokens"] += u.get("cache_read_input_tokens", 0)
        STATS["cache_write_tokens"] += u.get("cache_creation_input_tokens", 0)
        STATS["seconds"] += rec.get("seconds") or 0.0


def ask(prompt: str, schema: dict, system: str, model: str = "haiku", retries: int = 3, timeout: int = 600):
    """Return (structured_output, record). Cached by (model, system, schema, prompt)."""
    CACHE.mkdir(parents=True, exist_ok=True)
    key = _key(model, system, schema, prompt)
    path = CACHE / f"{key}.json"
    if path.exists():
        rec = json.loads(path.read_text())
        _account(rec, hit=True)
        return rec["output"], rec
    if os.environ.get("NSCG_OFFLINE"):
        raise LLMError(f"offline and not cached: {key}")
    last = None
    for attempt in range(retries):
        t0 = time.time()
        try:
            if os.environ.get("NSCG_BACKEND") == "openai":
                out, raw = _openai(prompt, schema, system, model, timeout)
                usage, cost = raw.get("usage", {}), None
            else:
                out, raw = _claude(prompt, schema, system, model, timeout)
                usage, cost = raw.get("usage", {}), raw.get("total_cost_usd")
        except (LLMError, subprocess.TimeoutExpired, json.JSONDecodeError) as e:
            last = e
            time.sleep(2 + 3 * attempt)
            continue
        rec = {"key": key, "model": model, "system": system, "schema": schema, "prompt": prompt,
               "output": out, "usage": usage, "cost_usd": cost, "seconds": round(time.time() - t0, 2),
               "attempt": attempt + 1, "time": time.strftime("%Y-%m-%dT%H:%M:%S%z"),
               "model_usage": raw.get("modelUsage")}
        tmp = path.with_suffix(".tmp")
        tmp.write_text(json.dumps(rec, indent=1))
        tmp.replace(path)
        _account(rec, hit=False)
        return out, rec
    with _lock:
        STATS["failures"] += 1
    raise LLMError(f"LLM request failed after {retries} attempts: {last!r}")


def _claude(prompt, schema, system, model, timeout):
    cmd = ["claude", "-p", "--model", model, "--tools", "", "--no-session-persistence", "--strict-mcp-config",
           "--setting-sources", "", "--output-format", "json", "--system-prompt", system,
           "--json-schema", json.dumps(schema)]
    with tempfile.TemporaryDirectory(prefix="nscg-") as cwd:  # empty cwd: no CLAUDE.md, no project context
        p = subprocess.run(cmd, input=prompt, capture_output=True, text=True, timeout=timeout, cwd=cwd)
    if p.returncode != 0 and not p.stdout.strip():
        raise LLMError(f"claude exited {p.returncode}: {p.stderr[-500:]}")
    raw = json.loads(p.stdout)
    if raw.get("is_error"):
        raise LLMError(f"claude error: {str(raw.get('result'))[:300]}")
    out = raw.get("structured_output")
    if out is None:
        try:
            out = json.loads(raw.get("result", ""))
        except json.JSONDecodeError as e:
            raise LLMError(f"no structured output: {str(raw.get('result'))[:200]}") from e
    return out, raw


def _openai(prompt, schema, system, model, timeout):  # pragma: no cover - optional backend
    import urllib.request

    body = {"model": model, "temperature": 0,
            "messages": [{"role": "system", "content": system + "\nAnswer with one JSON object that matches this "
                          "JSON Schema:\n" + json.dumps(schema)},
                         {"role": "user", "content": prompt}],
            "response_format": {"type": "json_object"}}
    req = urllib.request.Request(os.environ["OPENAI_BASE_URL"].rstrip("/") + "/chat/completions",
                                 data=json.dumps(body).encode(),
                                 headers={"Content-Type": "application/json",
                                          "Authorization": "Bearer " + os.environ["OPENAI_API_KEY"]})
    with urllib.request.urlopen(req, timeout=timeout) as r:
        raw = json.loads(r.read())
    text = raw["choices"][0]["message"]["content"]
    return json.loads(text[text.find("{"): text.rfind("}") + 1]), raw
