"""
---
name: truth-lens-pipe
type: pipe
display_name: Truth Lens
description: Four-layer Truth Lens pipeline: Codex planner, Agent Zero executor, Codex validator, Codex presenter.
---
"""

from __future__ import annotations

import asyncio
import base64
import hashlib
import json
import os
import re
import sys
import time
from pathlib import Path
from typing import Any, Dict, List
from urllib.parse import quote, urlsplit, urlunsplit

import httpx
from pydantic import BaseModel, Field

_OWUI_TASK_PREFIXES = (
    "### Task:\nSuggest",
    "### Task:\nGenerate",
    "### Task:\nCreate",
    "### Task:\nProvide",
)

_SEARCH_DELAY = 2
_SEARCH_TOP_N = 8
_MAX_VARIANTS = 6


class Pipe:
    class Valves(BaseModel):
        NAME: str = Field(default="Truth Lens", description="Display name in OpenWebUI.")
        OPENAI_API_BASE_URL: str = Field(
            default="https://api.openai.com/v1",
            description="OpenAI-compatible API base for Codex layers.",
        )
        OPENAI_API_KEY: str = Field(
            default="",
            description="OpenAI/Codex API key or OAuth token; may be left blank if loaded from auth.json.",
        )
        CODEX_AUTH_PATH: str = Field(default="~/.codex/auth.json")
        PLANNER_MODEL: str = Field(default="gpt-5.2")
        VALIDATOR_MODEL: str = Field(default="gpt-5.2")
        PRESENTER_MODEL: str = Field(default="gpt-5.2")
        FALLBACK_MODEL: str = Field(default="qwen2.5:7b")
        FALLBACK_API_BASE_URL: str = Field(default="http://192.168.1.2:11434/v1")
        EXECUTOR_URL: str = Field(default="http://192.168.1.108:7072/api/api_message")
        SEARXNG_URL: str = Field(default="http://192.168.1.2:8081/search")
        A0_ENV_PATH: str = Field(default="/a0/usr/.env")
        EXECUTOR_TIMEOUT_SECONDS: int = Field(default=300, ge=10, le=900)
        TOTAL_TIMEOUT_SECONDS: int = Field(default=900, ge=30, le=1800)
        MAX_TASKS: int = Field(default=8, ge=1, le=20)
        PROJECT_NAME: str = Field(default="Truth Lens")
        AGENT_PROFILE: str = Field(default="")

    def __init__(self):
        self.valves = self.Valves()

    def pipes(self):
        return [{"id": "truth-lens-pipe", "name": self.valves.NAME}]

    async def pipe(self, body: dict):
        request_text = self._extract_user_message(body)
        image_refs = self._extract_image_refs(body)

        if not request_text and not image_refs:
            yield "Truth Lens requires a text claim, URL, or image."
            return

        for prefix in _OWUI_TASK_PREFIXES:
            if request_text.startswith(prefix):
                return

        yield "Truth Lens — analyzing claim...\n\n"

        deadline = time.monotonic() + float(self.valves.TOTAL_TIMEOUT_SECONDS)
        async with httpx.AsyncClient(timeout=self._client_timeout(60)) as client:
            if image_refs:
                yield "Truth Lens — extracting text from image(s)...\n"
                request_text = await self._extract_text_from_images(
                    client=client,
                    image_refs=image_refs,
                    deadline=deadline,
                    request_text=request_text,
                )

            yield "Truth Lens — running planner (Codex)...\n"
            self._log_phase("planner", request_text)
            planner_raw = await self._call_codex(
                client=client,
                model=self.valves.PLANNER_MODEL,
                system_prompt=self._planner_prompt(),
                user_prompt=request_text,
                deadline=deadline,
            )
            plan = self._parse_json_object(planner_raw) or self._fallback_plan(request_text)
            atomic_tasks = self._normalize_tasks(plan.get("atomic_tasks"), request_text)

            yield f"Truth Lens — {len(atomic_tasks)} task(s) planned\n\n"

            executor_session = await self._prepare_executor_session(client=client, deadline=deadline)
            raw_findings = []

            for index, task in enumerate(atomic_tasks, start=1):
                if time.monotonic() >= deadline:
                    break
                yield f"[{index}/{len(atomic_tasks)}] {task.get('task','')[:80]}\n"
                finding = await self._run_atomic_task(
                    client=client,
                    task=task,
                    request_text=request_text,
                    deadline=deadline,
                    task_index=index,
                    executor_session=executor_session,
                )
                raw_findings.append(finding)

            yield "\nTruth Lens — validating findings (Codex)...\n"
            validator_input = json.dumps(
                {
                    "request": request_text,
                    "planner_output": plan,
                    "executor_findings": raw_findings,
                },
                indent=2,
            )

            self._log_phase("validator", f"{len(raw_findings)} findings")
            validation_raw = await self._call_codex(
                client=client,
                model=self.valves.VALIDATOR_MODEL,
                system_prompt=self._validator_prompt(),
                user_prompt=validator_input,
                deadline=deadline,
            )

            yield "Truth Lens — formatting report (Codex)...\n\n"
            presenter_input = json.dumps(
                {
                    "request": request_text,
                    "planner_output": plan,
                    "executor_findings": raw_findings,
                    "validation": validation_raw,
                    "source_count": self._count_sources(raw_findings),
                },
                indent=2,
            )

            self._log_phase("presenter", "formatting final response")
            presenter_raw = await self._call_codex(
                client=client,
                model=self.valves.PRESENTER_MODEL,
                system_prompt=self._presenter_prompt(),
                user_prompt=presenter_input,
                deadline=deadline,
            )

            result = presenter_raw.strip() or self._fallback_presenter(request_text, raw_findings, validation_raw)
            yield result

    def _extract_user_message(self, body: dict) -> str:
        messages = body.get("messages") or []
        for message in reversed(messages):
            if message.get("role") != "user":
                continue
            content = message.get("content", "")
            if isinstance(content, list):
                pieces = []
                for part in content:
                    if isinstance(part, dict) and part.get("type") == "text":
                        pieces.append(str(part.get("text", "")))
                return " ".join(piece.strip() for piece in pieces if piece.strip()).strip()
            return str(content).strip()

        fallback = body.get("prompt") or body.get("input") or body.get("message") or ""
        return str(fallback).strip()

    def _extract_image_refs(self, body: dict) -> list[str]:
        refs: list[str] = []
        candidates = [body.get("images"), body.get("attachments"), body.get("files")]
        for candidate in candidates:
            if not candidate:
                continue
            if isinstance(candidate, list):
                for item in candidate:
                    if isinstance(item, str):
                        refs.append(item)
                    elif isinstance(item, dict):
                        for key in ("url", "path", "base64", "data"):
                            value = item.get(key)
                            if value:
                                refs.append(str(value))
                                break
        return refs

    def _planner_prompt(self) -> str:
        return (
            "You are the Truth Lens planner.\n"
            "Break the user's claim into atomic verification tasks only.\n"
            "Return strict JSON with keys: claim, claim_type, atomic_tasks, notes.\n"
            "Each atomic task must contain: id, task, query, source_priority, expected_output, risk_flags.\n"
            "Do not write a verdict. Do not summarize. Do not search."
        )

    def _validator_prompt(self) -> str:
        return (
            "You are the Truth Lens validator.\n"
            "Classify the executor findings using TRUE, FALSE, PARTIALLY TRUE, MISSING CONTEXT, or UNVERIFIABLE.\n"
            "Identify missing context, likely business model, and legal/financial/health flags when present.\n"
            "Return concise JSON or a tight validation brief. Do not invent sources."
        )

    def _presenter_prompt(self) -> str:
        return (
            "You are the Truth Lens presenter.\n"
            "Format the final response for a non-technical family user.\n"
            "Use plain English and keep the structure:\n"
            "Verdict, What they told you, What they did not tell you, Flags, Sources, Follow-up.\n"
            "Never expose chain-of-thought. Never editorialize.\n"
            "If validation or findings are incomplete, clearly say what was not found and what was searched."
        )

    async def _extract_text_from_images(
        self,
        *,
        client: httpx.AsyncClient,
        image_refs: list[str],
        deadline: float,
        request_text: str,
    ) -> str:
        self._log_phase("vision", f"{len(image_refs)} image refs")
        prompt = (
            "Extract all visible text and the core claims from the provided image(s).\n"
            "Return a compact transcription plus a short list of the claims being made."
        )
        content: list[dict[str, Any]] = [{"type": "text", "text": prompt}]
        for ref in image_refs[:4]:
            content.append({"type": "image_url", "image_url": {"url": self._normalize_image_ref(ref)}})
        vision_raw = await self._call_codex(
            client=client,
            model=self.valves.PLANNER_MODEL,
            system_prompt="You extract text from screenshots for Truth Lens.",
            user_prompt=content,
            deadline=deadline,
        )
        merged = "\n".join(part for part in [request_text, vision_raw.strip()] if part)
        return merged.strip()

    async def _run_atomic_task(
        self,
        *,
        client: httpx.AsyncClient,
        task: dict[str, Any],
        request_text: str,
        deadline: float,
        task_index: int,
        executor_session: dict[str, str] | None,
    ) -> dict[str, Any]:
        task_payload = json.dumps(
            {
                "request": request_text,
                "task": task,
                "output_contract": {
                    "FOUND": "what was found",
                    "SOURCE": "exact URL",
                    "DATE": "publication or retrieval date",
                    "CONFIDENCE": "HIGH / MEDIUM / LOW",
                    "FLAGS": "pattern flags if any",
                    "NOT_FOUND": "only if genuine",
                },
            },
            indent=2,
        )
        self._log_phase("executor", f"task {task_index}: {task.get('task', 'unnamed task')}")
        result = await self._call_executor(client, task_payload, deadline, executor_session)
        if result is None:
            result = await self._direct_search(client, task, deadline)
        return {
            "task": task,
            "status": "ok",
            "result": result,
        }

    async def _prepare_executor_session(
        self, *, client: httpx.AsyncClient, deadline: float
    ) -> dict[str, str] | None:
        timeout = self._remaining_timeout(deadline, default=min(20, self.valves.EXECUTOR_TIMEOUT_SECONDS))
        try:
            response = await client.get(self._executor_base_url() + "/csrf_token", timeout=timeout)
            response.raise_for_status()
            data = response.json()
            token = str(data.get("token") or "").strip()
            if not token:
                return None
            runtime_id = str(data.get("runtime_id") or "").strip()
            headers = {"X-CSRF-Token": token}
            if runtime_id:
                headers["X-CSRF-Runtime"] = runtime_id
            return headers
        except Exception as exc:
            self._log_phase("executor-auth-fallback", str(exc))
            return None

    async def _call_executor(
        self,
        client: httpx.AsyncClient,
        task_payload: str,
        deadline: float,
        executor_session: dict[str, str] | None,
    ) -> str | None:
        timeout = self._remaining_timeout(deadline, default=self.valves.EXECUTOR_TIMEOUT_SECONDS)
        payload = {"text": task_payload}
        headers = dict(executor_session or {})
        candidates = self._executor_url_candidates()

        for url in candidates:
            try:
                response = await client.post(
                    url,
                    json=payload,
                    headers=headers,
                    timeout=timeout,
                )
                if response.status_code in {404, 405}:
                    self._log_phase("executor-fallback", f"{url} HTTP {response.status_code}")
                    continue
                if response.status_code >= 400:
                    self._log_phase("executor-fallback", f"{url} HTTP {response.status_code}")
                    return None
                data = response.json()
                if isinstance(data, dict):
                    if isinstance(data.get("message"), str):
                        return data["message"]
                    if isinstance(data.get("response"), str):
                        return data["response"]
                    if isinstance(data.get("response"), dict):
                        return json.dumps(data["response"], indent=2)
                return response.text.strip()
            except Exception as exc:
                self._log_phase("executor-fallback", f"{url} {exc}")
                continue
        return None

    def _generate_claim_variants(self, query: str) -> list[str]:
        variants: list[str] = []
        seen: set[str] = set()

        def add(q: str) -> None:
            q = q.strip()
            if q and q not in seen:
                seen.add(q)
                variants.append(q)

        add(query)
        add(f'"{query}" fact check')
        add(f'{query} official statement OR press release OR announcement')
        add(f'{query} site:snopes.com OR site:politifact.com OR site:reuters.com')
        add(f'{query} complaint OR warning OR scam OR fraud OR recall')
        add(f'{query} FDA OR FTC OR court OR lawsuit OR settlement OR regulatory')
        return variants[:_MAX_VARIANTS]

    async def _direct_search(
        self, client: httpx.AsyncClient, task: dict[str, Any], deadline: float
    ) -> str:
        query = str(task.get("query") or task.get("task") or "").strip()
        if not query:
            return self._format_not_found(task, "no query")

        variants = self._generate_claim_variants(query)
        all_items: list[dict[str, Any]] = []
        seen_urls: set[str] = set()

        for i, variant in enumerate(variants):
            timeout = self._remaining_timeout(deadline, default=30)
            try:
                response = await client.get(
                    self.valves.SEARXNG_URL,
                    params={"q": variant, "format": "json"},
                    timeout=timeout,
                )
                if response.status_code < 400:
                    data = response.json()
                    results = data.get("results") if isinstance(data, dict) else []
                    if isinstance(results, list):
                        for item in results[:_SEARCH_TOP_N]:
                            if not isinstance(item, dict):
                                continue
                            url = str(item.get("url") or "").strip()
                            if url and url.startswith("http") and url not in seen_urls:
                                seen_urls.add(url)
                                item["_variant"] = variant
                                all_items.append(item)
            except Exception as exc:
                self._log_phase("direct-search-variant", f"variant {i + 1}: {exc}")
            if i < len(variants) - 1:
                await asyncio.sleep(_SEARCH_DELAY)

        if not all_items:
            return self._format_not_found(task, f"no SearXNG hits across {len(variants)} variants")

        lines = [
            f"TASK: {task.get('task', query)}",
            f"VARIANTS_SEARCHED: {len(variants)}",
            f"UNIQUE_RESULTS: {len(all_items)}",
            "RESULTS:",
        ]
        for item in all_items[:20]:
            title = str(item.get("title") or item.get("url") or "result").strip()
            url = str(item.get("url") or "").strip()
            snippet = str(item.get("content") or item.get("parsed_url") or "").strip()
            published = str(item.get("publishedDate") or item.get("published_date") or "").strip()
            lines.append(f"- FOUND: {title}")
            if url:
                lines.append(f"  SOURCE: {url}")
            if published:
                lines.append(f"  DATE: {published}")
            if snippet:
                lines.append(f"  SNIPPET: {snippet[:400]}")
            lines.append("  CONFIDENCE: MEDIUM")
        return "\n".join(lines)

    async def _call_codex(
        self,
        *,
        client: httpx.AsyncClient,
        model: str,
        system_prompt: str,
        user_prompt: str | list[dict[str, Any]],
        deadline: float,
    ) -> str:
        messages: list[dict[str, Any]] = [{"role": "system", "content": system_prompt}]
        messages.append({"role": "user", "content": user_prompt})
        payload = {
            "model": model,
            "messages": messages,
            "temperature": 0.1,
        }
        headers = self._codex_headers()
        timeout = self._remaining_timeout(deadline, default=60)
        response = await client.post(
            f"{self.valves.OPENAI_API_BASE_URL.rstrip('/')}/chat/completions",
            json=payload,
            headers=headers,
            timeout=timeout,
        )
        if response.status_code >= 400:
            self._log_phase("codex-fallback", f"HTTP {response.status_code}")
            return self._offline_codex_fallback(system_prompt=system_prompt, user_prompt=user_prompt)
        try:
            data = response.json()
            return str(data["choices"][0]["message"]["content"]).strip()
        except Exception as exc:
            self._log_phase("codex-fallback", str(exc))
            return self._offline_codex_fallback(system_prompt=system_prompt, user_prompt=user_prompt)

    def _offline_codex_fallback(
        self, *, system_prompt: str, user_prompt: str | list[dict[str, Any]]
    ) -> str:
        prompt = system_prompt.lower()
        user_text = ""
        if isinstance(user_prompt, str):
            user_text = user_prompt
        elif isinstance(user_prompt, list):
            for part in user_prompt:
                if isinstance(part, dict) and part.get("type") == "text":
                    user_text += str(part.get("text", "")) + "\n"
        parsed = self._parse_json_object(user_text) if user_text else None

        if "planner" in prompt:
            request_text = user_text.strip() or (parsed.get("request") if isinstance(parsed, dict) else "")
            return json.dumps(self._fallback_plan(str(request_text)), indent=2)

        if "validator" in prompt:
            findings = []
            request_text = user_text.strip()
            if isinstance(parsed, dict):
                request_text = str(parsed.get("request") or request_text)
                findings = parsed.get("executor_findings") or []
            verdict = "UNVERIFIABLE" if not findings else "MISSING CONTEXT"
            return json.dumps(
                {
                    "verdict": verdict,
                    "what_they_told_you": request_text[:280],
                    "what_they_didnt_tell_you": "Codex was unavailable, so this validator used the raw research findings and offline fallback.",
                    "flags": [],
                    "confidence": "LOW",
                },
                indent=2,
            )

        if "presenter" in prompt:
            request_text = ""
            findings = []
            validation_raw = ""
            if isinstance(parsed, dict):
                request_text = str(parsed.get("request") or "")
                findings = parsed.get("executor_findings") or []
                validation_raw = str(parsed.get("validation") or "")
            return self._fallback_presenter(request_text, findings, validation_raw)

        return json.dumps(
            {
                "note": "Offline fallback used",
                "content": user_text[:1000],
            },
            indent=2,
        )

    def _normalize_tasks(self, tasks: Any, request_text: str) -> list[dict[str, Any]]:
        normalized: list[dict[str, Any]] = []
        if isinstance(tasks, list):
            for index, task in enumerate(tasks, start=1):
                if not isinstance(task, dict):
                    continue
                normalized.append(
                    {
                        "id": str(task.get("id") or f"task-{index}"),
                        "task": str(task.get("task") or request_text).strip(),
                        "query": str(task.get("query") or task.get("task") or request_text).strip(),
                        "source_priority": task.get("source_priority") or [],
                        "expected_output": str(task.get("expected_output") or "raw findings").strip(),
                        "risk_flags": task.get("risk_flags") or [],
                    }
                )
        if not normalized:
            normalized.append(
                {
                    "id": "task-1",
                    "task": request_text,
                    "query": request_text,
                    "source_priority": ["search"],
                    "expected_output": "raw findings",
                    "risk_flags": [],
                }
            )
        return normalized[: self.valves.MAX_TASKS]

    def _fallback_plan(self, request_text: str) -> dict[str, Any]:
        return {
            "claim": request_text,
            "claim_type": "unknown",
            "atomic_tasks": [
                {
                    "id": "task-1",
                    "task": request_text,
                    "query": request_text,
                    "source_priority": ["search"],
                    "expected_output": "raw findings",
                    "risk_flags": [],
                }
            ],
            "notes": "Planner fallback used because the model did not return JSON.",
        }

    def _fallback_presenter(
        self, request_text: str, findings: list[dict[str, Any]], validation_raw: str
    ) -> str:
        lines = [
            "Truth Lens",
            f"Claim: {request_text}",
            "",
            "Verdict: UNVERIFIABLE",
            "What they told you: The request was received, but the presentation layer could not format a full response.",
            "What they did not tell you: See the raw findings and validation output below.",
            "",
            "Validation:",
            validation_raw[:1200],
            "",
            "Raw findings:",
        ]
        for item in findings:
            task = item.get("task", {})
            lines.append(f"- {task.get('task', 'task')}")
            result = str(item.get("result", ""))
            lines.append(result[:600])
        return "\n".join(lines)

    def _format_not_found(self, task: dict[str, Any], reason: str) -> str:
        return "\n".join(
            [
                f"TASK: {task.get('task', 'task')}",
                f"QUERY: {task.get('query', '')}",
                f"NOT_FOUND: {reason}",
            ]
        )

    def _count_sources(self, findings: list[dict[str, Any]]) -> int:
        sources = set()
        for finding in findings:
            result = str(finding.get("result", ""))
            for line in result.splitlines():
                if line.startswith("SOURCE:"):
                    sources.add(line.split("SOURCE:", 1)[1].strip())
        return len(sources)

    def _parse_json_object(self, text: str) -> dict[str, Any] | None:
        text = text.strip()
        if not text:
            return None
        try:
            obj = json.loads(text)
            return obj if isinstance(obj, dict) else None
        except Exception:
            pass

        fenced = re.search(r"```(?:json)?\s*(\{.*?\})\s*```", text, re.DOTALL)
        if fenced:
            try:
                obj = json.loads(fenced.group(1))
                return obj if isinstance(obj, dict) else None
            except Exception:
                pass

        block = re.search(r"\{.*\}", text, re.DOTALL)
        if block:
            try:
                obj = json.loads(block.group(0))
                return obj if isinstance(obj, dict) else None
            except Exception:
                return None
        return None

    def _executor_headers(self) -> dict[str, str]:
        key = self._derive_executor_key()
        if not key:
            return {}
        return {"X-API-KEY": key}

    def _executor_base_url(self) -> str:
        parts = urlsplit(self.valves.EXECUTOR_URL)
        if not parts.scheme or not parts.netloc:
            return self.valves.EXECUTOR_URL.rstrip("/")
        return urlunsplit((parts.scheme, parts.netloc, "", "", ""))

    def _executor_url_candidates(self) -> list[str]:
        raw = self.valves.EXECUTOR_URL.rstrip("/")
        parts = urlsplit(raw)
        base = self._executor_base_url()
        candidates = [raw]
        path = parts.path.rstrip("/")
        if path.endswith("/api/api_message"):
            candidates.append(base + "/message")
            candidates.append(base + "/api/message")
        elif path.endswith("/api/message"):
            candidates.append(base + "/message")
        elif path.endswith("/message"):
            candidates.append(base + "/api/message")
            candidates.append(base + "/api/api_message")
        else:
            candidates.append(base + "/message")
        deduped: list[str] = []
        for candidate in candidates:
            candidate = candidate.rstrip("/")
            if candidate not in deduped:
                deduped.append(candidate)
        return deduped

    def _codex_headers(self) -> dict[str, str]:
        key = self._resolve_codex_api_key()
        if not key:
            self._log_phase("codex-auth", "No Codex API key found; requests may fail until auth is configured.")
            return {}
        return {"Authorization": f"Bearer {key}"}

    def _resolve_codex_api_key(self) -> str:
        direct = (self.valves.OPENAI_API_KEY or os.getenv("OPENAI_API_KEY") or "").strip()
        if direct:
            return direct

        auth_path = Path(os.path.expanduser(self.valves.CODEX_AUTH_PATH))
        if not auth_path.is_file():
            return ""

        try:
            data = json.loads(auth_path.read_text(encoding="utf-8"))
        except Exception:
            return ""

        if not isinstance(data, dict):
            return ""

        candidates = [
            data.get("OPENAI_API_KEY"),
            data.get("openai_api_key"),
            data.get("api_key"),
        ]
        tokens = data.get("tokens")
        if isinstance(tokens, dict):
            candidates.extend(
                [
                    tokens.get("api_key"),
                    tokens.get("OPENAI_API_KEY"),
                    tokens.get("access_token"),
                ]
            )

        for candidate in candidates:
            if isinstance(candidate, str) and candidate.strip():
                return candidate.strip()
        return ""

    def _derive_executor_key(self) -> str:
        runtime_id = self._read_persistent_runtime_id()
        if not runtime_id:
            return ""
        digest = hashlib.sha256((runtime_id + "::").encode("utf-8")).digest()
        return base64.urlsafe_b64encode(digest)[:16].decode("ascii").rstrip("=")

    def _read_persistent_runtime_id(self) -> str:
        env_path = Path(self.valves.A0_ENV_PATH)
        if not env_path.exists():
            return ""
        try:
            for line in env_path.read_text(encoding="utf-8").splitlines():
                if line.startswith("A0_PERSISTENT_RUNTIME_ID="):
                    return line.split("=", 1)[1].strip().strip('"').strip("'")
        except Exception:
            return ""
        return ""

    def _normalize_image_ref(self, ref: str) -> str:
        ref = ref.strip()
        if not ref:
            return ref
        if ref.startswith("data:image/") or ref.startswith("http://") or ref.startswith("https://"):
            return ref
        path = Path(ref)
        if path.exists() and path.is_file():
            mime = "image/png"
            if path.suffix.lower() in {".jpg", ".jpeg"}:
                mime = "image/jpeg"
            elif path.suffix.lower() == ".webp":
                mime = "image/webp"
            elif path.suffix.lower() == ".gif":
                mime = "image/gif"
            encoded = base64.b64encode(path.read_bytes()).decode("ascii")
            return f"data:{mime};base64,{encoded}"
        return ref

    def _client_timeout(self, seconds: int) -> httpx.Timeout:
        return httpx.Timeout(connect=min(30, seconds), read=seconds, write=min(30, seconds), pool=min(30, seconds))

    def _remaining_timeout(self, deadline: float, default: int) -> httpx.Timeout:
        remaining = max(5.0, deadline - time.monotonic())
        seconds = min(default, int(remaining))
        return self._client_timeout(seconds)

    def _log_phase(self, phase: str, message: str) -> None:
        print(f"[truth-lens] {phase}: {message}", file=sys.stderr, flush=True)
