"""
---
name: axiom-pipe
type: pipe
display_name: AXIOM Investigation
description: Four-layer AXIOM investigation pipeline: Codex planner, Agent Zero executor, Codex validator, Codex compiler -> Gotenberg -> Paperless.
---
"""

from __future__ import annotations

import asyncio
import base64
import json
import os
import re
import time
from pathlib import Path
from typing import Any

import httpx
from pydantic import BaseModel, Field

_OWUI_TASK_PREFIXES = (
    "### Task:\nSuggest",
    "### Task:\nGenerate",
    "### Task:\nCreate",
    "### Task:\nProvide",
)

_REPORT_DISCLAIMER = (
    "This report is for investigative purposes only. It does not constitute legal advice. "
    "All findings are based on publicly available records as of the report date. "
    "The absence of a public record does not mean a record does not exist."
)


class Pipe:
    class Valves(BaseModel):
        NAME: str = Field(default="AXIOM Investigation")
        OPENAI_API_BASE_URL: str = Field(
            default="https://api.openai.com/v1",
            description="OpenAI-compatible API base for Codex layers.",
        )
        OPENAI_API_KEY: str = Field(
            default="",
            description="OpenAI/Codex API key or OAuth bearer token. Leave blank to load from auth.json.",
        )
        CODEX_AUTH_PATH: str = Field(default="~/.codex/auth.json")
        PLANNER_MODEL: str = Field(default="gpt-5.2")
        VALIDATOR_MODEL: str = Field(default="gpt-5.2")
        COMPILER_MODEL: str = Field(default="gpt-5.2")
        FALLBACK_MODEL: str = Field(
            default="qwen2.5:7b",
            description="Ollama model used when Codex returns 401/429/quota error.",
        )
        FALLBACK_API_BASE_URL: str = Field(
            default="http://192.168.1.2:11434/v1",
            description="OpenAI-compatible base URL for fallback model (Ollama).",
        )
        AXIOM_URL: str = Field(default="http://192.168.1.107:7073/api/api_message")
        AXIOM_API_KEY: str = Field(default="Zu5PK6EMFE5Dd1oE")
        EXECUTOR_TIMEOUT_SECONDS: float = Field(default=30.0, ge=5.0, le=120.0)
        GOTENBERG_URL: str = Field(default="http://192.168.1.107:3000")
        PAPERLESS_URL: str = Field(default="http://192.168.1.107:8010")
        PAPERLESS_TOKEN: str = Field(default="4dae9c893a0b446802d255c8c7a24cc4fcc07237")
        PAPERLESS_TAG_ID: int = Field(default=1)
        TELEGRAM_BOT_TOKEN: str = Field(default="")
        TELEGRAM_CHAT_ID: str = Field(default="")
        CREDENTIALS_ENV_PATH: str = Field(default="~/CREDENTIALS.env")
        MAX_TASKS: int = Field(default=12, ge=1, le=20)
        TOTAL_TIMEOUT_SECONDS: int = Field(default=600, ge=60, le=1800)

    def __init__(self):
        self.valves = self.Valves()
        self._creds_loaded = False

    def pipes(self):
        return [{"id": "axiom-pipe", "name": self.valves.NAME}]

    async def pipe(self, body: dict):
        # Immediate yield prevents OpenWebUI session reaping
        yield ""

        request_text = self._extract_user_message(body)
        if not request_text:
            yield "AXIOM requires an investigation query."
            return

        for prefix in _OWUI_TASK_PREFIXES:
            if request_text.startswith(prefix):
                return

        self._load_credentials()

        yield f"**AXIOM — {request_text[:120]}**\n\n"

        deadline = time.monotonic() + float(self.valves.TOTAL_TIMEOUT_SECONDS)

        async with httpx.AsyncClient(timeout=httpx.Timeout(60.0)) as client:

            # ── LAYER 1: PLANNER ─────────────────────────────────────────
            yield "**Layer 1 — Planner (Codex)**\n"
            planner_raw = await self._call_codex(
                client=client,
                model=self.valves.PLANNER_MODEL,
                system_prompt=self._planner_prompt(),
                user_prompt=request_text,
                deadline=deadline,
            )
            plan = self._parse_plan(planner_raw, request_text)
            tasks = plan.get("tasks", [])[: self.valves.MAX_TASKS]

            if not tasks:
                yield "_Planner returned no tasks. Cannot continue._\n"
                return

            yield f"_{len(tasks)} atomic tasks planned_\n\n"
            for i, t in enumerate(tasks, 1):
                yield f"{i}. {t}\n"
            yield "\n"

            # ── LAYER 2: EXECUTOR ─────────────────────────────────────────
            yield "**Layer 2 — Executor (Agent Zero AXIOM)**\n\n"
            raw_findings: list[dict[str, Any]] = []

            for i, task in enumerate(tasks, 1):
                if time.monotonic() >= deadline:
                    yield f"_{i}/{len(tasks)} — global deadline reached, stopping_\n"
                    break
                yield f"[{i}/{len(tasks)}] {str(task)[:100]}\n"
                finding = await self._run_executor(client, str(task), deadline)
                raw_findings.append({"task": task, "finding": finding})
                icon = "✓" if "NOT FOUND" not in finding.upper() else "—"
                yield f"  {icon}\n"

            yield "\n"

            # ── LAYER 3: VALIDATOR ────────────────────────────────────────
            yield "**Layer 3 — Validator (Codex)**\n"
            validator_input = json.dumps(
                {
                    "subject": plan.get("subject", request_text),
                    "tasks_executed": len(raw_findings),
                    "findings": raw_findings,
                },
                indent=2,
            )
            validation_raw = await self._call_codex(
                client=client,
                model=self.valves.VALIDATOR_MODEL,
                system_prompt=self._validator_prompt(),
                user_prompt=validator_input,
                deadline=deadline,
            )
            yield "_Validation complete_\n\n"

            # OFAC / sanctions detection — only trigger on explicit OFAC_HIT label from validator
            if re.search(
                r"OFAC_HIT\s*:",
                validation_raw,
                re.IGNORECASE,
            ):
                await self._send_ofac_alert(client, request_text, validation_raw)
                yield "**OFAC/SANCTIONS HIT DETECTED — Operator alert sent.**\n\n"

            # ── LAYER 4: COMPILER ─────────────────────────────────────────
            yield "**Layer 4 — Compiler (Codex -> HTML -> Gotenberg -> Paperless)**\n"
            compiler_input = json.dumps(
                {
                    "request": request_text,
                    "subject": plan.get("subject", request_text),
                    "plan": plan,
                    "findings": raw_findings,
                    "validation": validation_raw,
                    "report_date": time.strftime("%Y-%m-%d"),
                },
                indent=2,
            )
            report_html = await self._call_codex(
                client=client,
                model=self.valves.COMPILER_MODEL,
                system_prompt=self._compiler_prompt(),
                user_prompt=compiler_input,
                deadline=deadline,
            )

            # Wrap in full HTML document if needed
            stripped = report_html.strip().lower()
            if not stripped.startswith("<!doctype") and not stripped.startswith("<html"):
                report_html = (
                    "<!DOCTYPE html><html><head><meta charset='utf-8'>"
                    "<title>AXIOM Report</title></head><body>"
                    + report_html
                    + "</body></html>"
                )

            # Gotenberg -> PDF
            pdf_bytes = await self._gotenberg_render(client, report_html)

            subject_slug = re.sub(r"[^a-z0-9]+", "-", request_text[:60].lower()).strip("-")
            filename = f"axiom-{time.strftime('%Y%m%d')}-{subject_slug}.pdf"

            if pdf_bytes:
                doc_id = await self._paperless_archive(
                    client, pdf_bytes, filename, request_text
                )
                if doc_id:
                    yield f"_Report archived to Paperless-ngx. Document ID: {doc_id}_\n\n"
                else:
                    yield "_Paperless archive failed — PDF available as download._\n\n"
                    b64 = base64.b64encode(pdf_bytes).decode("ascii")
                    yield f"[Download PDF](data:application/pdf;base64,{b64})\n\n"
            else:
                yield "_Gotenberg render failed — returning HTML report._\n\n"
                yield report_html + "\n"

        yield "---\n_Investigation complete._\n"

    # ── MESSAGE EXTRACTION ────────────────────────────────────────────────

    def _extract_user_message(self, body: dict) -> str:
        messages = body.get("messages") or []
        for message in reversed(messages):
            if message.get("role") != "user":
                continue
            content = message.get("content", "")
            if isinstance(content, list):
                pieces = [
                    str(p.get("text", ""))
                    for p in content
                    if isinstance(p, dict) and p.get("type") == "text"
                ]
                return " ".join(p.strip() for p in pieces if p.strip()).strip()
            return str(content).strip()
        fallback = body.get("prompt") or body.get("input") or body.get("message") or ""
        return str(fallback).strip()

    # ── CREDENTIALS ───────────────────────────────────────────────────────

    def _load_credentials(self) -> None:
        if self._creds_loaded:
            return
        self._creds_loaded = True
        env_path = Path(os.path.expanduser(self.valves.CREDENTIALS_ENV_PATH))
        if not env_path.is_file():
            return
        try:
            for line in env_path.read_text(encoding="utf-8").splitlines():
                line = line.strip()
                if not line or line.startswith("#") or "=" not in line:
                    continue
                key, _, val = line.partition("=")
                key = key.strip()
                val = val.strip().strip('"').strip("'")
                if key == "DE_ATLAS_BOT_TOKEN" and not self.valves.TELEGRAM_BOT_TOKEN:
                    self.valves.TELEGRAM_BOT_TOKEN = val
                elif key == "TELEGRAM_CHAT_ID" and not self.valves.TELEGRAM_CHAT_ID:
                    self.valves.TELEGRAM_CHAT_ID = val
        except Exception:
            pass

    # ── CODEX ─────────────────────────────────────────────────────────────

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
            candidates.extend([
                tokens.get("api_key"),
                tokens.get("OPENAI_API_KEY"),
                tokens.get("access_token"),
            ])
        for c in candidates:
            if isinstance(c, str) and c.strip():
                return c.strip()
        return ""

    def _codex_headers(self) -> dict[str, str]:
        key = self._resolve_codex_api_key()
        if not key:
            return {}
        return {"Authorization": f"Bearer {key}"}

    async def _call_codex(
        self,
        *,
        client: httpx.AsyncClient,
        model: str,
        system_prompt: str,
        user_prompt: str | list,
        deadline: float,
    ) -> str:
        remaining = max(10.0, deadline - time.monotonic())
        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt},
        ]
        # Try primary Codex endpoint first
        primary_key = self._resolve_codex_api_key()
        if primary_key:
            headers = {"Authorization": f"Bearer {primary_key}", "Content-Type": "application/json"}
            payload = {"model": model, "messages": messages, "max_completion_tokens": 4096}
            try:
                r = await client.post(
                    f"{self.valves.OPENAI_API_BASE_URL.rstrip('/')}/chat/completions",
                    headers=headers, json=payload, timeout=min(remaining, 90.0),
                )
                if r.status_code not in (401, 403, 429):
                    r.raise_for_status()
                    return r.json()["choices"][0]["message"]["content"].strip()
                # Fall through to fallback on auth/quota errors
            except Exception:
                pass
        # Fallback: Ollama
        if not self.valves.FALLBACK_MODEL or not self.valves.FALLBACK_API_BASE_URL:
            return "[Codex unavailable — no fallback configured]"
        fallback_payload = {
            "model": self.valves.FALLBACK_MODEL,
            "messages": messages,
            "max_tokens": 4096,
        }
        try:
            r = await client.post(
                f"{self.valves.FALLBACK_API_BASE_URL.rstrip('/')}/chat/completions",
                json=fallback_payload,
                timeout=min(remaining, 180.0),
            )
            r.raise_for_status()
            return r.json()["choices"][0]["message"]["content"].strip()
        except Exception as exc:
            return f"[LLM unavailable: {exc}]"

    # ── PLANNER ───────────────────────────────────────────────────────────

    def _planner_prompt(self) -> str:
        return (
            "You are the AXIOM planner. Your only job is to decompose an investigation request into atomic search tasks.\n"
            "Return strict JSON with exactly these keys:\n"
            '  {"subject": "<full name + identifiers>", "tasks": ["task 1", "task 2", ...]}\n'
            "Rules:\n"
            "- Each task is one atomic search action: one source, one target.\n"
            "- Cover: property records, court records, business filings, social media, news archives, OFAC/SDN check, professional licenses, voter registration, criminal records.\n"
            "- Do not search. Do not synthesize. Do not draw conclusions.\n"
            "- Do not include compound tasks — split them.\n"
            "- Maximum 12 tasks.\n"
            "- Return only the JSON object. No preamble, no explanation."
        )

    def _parse_plan(self, raw: str, fallback_query: str) -> dict[str, Any]:
        raw = raw.strip()
        raw = re.sub(r"^```(?:json)?\s*", "", raw)
        raw = re.sub(r"\s*```$", "", raw)
        try:
            parsed = json.loads(raw)
            if isinstance(parsed, dict) and isinstance(parsed.get("tasks"), list):
                return parsed
        except Exception:
            pass
        match = re.search(r"\{.*\}", raw, re.DOTALL)
        if match:
            try:
                parsed = json.loads(match.group())
                if isinstance(parsed, dict):
                    if not isinstance(parsed.get("tasks"), list):
                        parsed["tasks"] = [fallback_query]
                    return parsed
            except Exception:
                pass
        return {"subject": fallback_query, "tasks": [fallback_query]}

    # ── EXECUTOR ─────────────────────────────────────────────────────────

    async def _run_executor(
        self, client: httpx.AsyncClient, task: str, deadline: float
    ) -> str:
        remaining = min(
            self.valves.EXECUTOR_TIMEOUT_SECONDS,
            max(5.0, deadline - time.monotonic()),
        )
        headers = {
            "X-API-KEY": self.valves.AXIOM_API_KEY,
            "Content-Type": "application/json",
        }
        payload = {"message": task, "lifetime_hours": 1}
        try:
            response = await client.post(
                self.valves.AXIOM_URL,
                headers=headers,
                json=payload,
                timeout=remaining,
            )
            response.raise_for_status()
            data = response.json()
            return str(data.get("response") or data.get("output") or data).strip()
        except httpx.TimeoutException:
            return "NOT FOUND — executor timeout"
        except Exception as exc:
            return f"NOT FOUND — executor error: {exc}"

    # ── VALIDATOR ────────────────────────────────────────────────────────

    def _validator_prompt(self) -> str:
        return (
            "You are the AXIOM validator. Classify each raw finding using exactly one label:\n"
            "  VERIFIED — source URL confirmed, content matches the task target\n"
            "  PARTIAL — source found but incomplete or ambiguous\n"
            "  UNVERIFIED — no public record found\n"
            "  CONTRADICTED — conflicting records found\n\n"
            "Additional rules:\n"
            "- If and ONLY if a finding contains a CONFIRMED match on the OFAC SDN list or active sanctions, "
            "output a line starting with exactly: OFAC_HIT: followed by the exact hit text. "
            "Do NOT output OFAC_HIT: if the check found nothing — just label it UNVERIFIED.\n"
            "- Never fabricate sources. If not found, state explicitly.\n"
            "- Never claim a record is clean — only that no public record was found.\n"
            "- Never provide legal advice — findings are investigative observations only.\n"
            "- Return a structured validation brief covering each task."
        )

    # ── OFAC ALERT ────────────────────────────────────────────────────────

    async def _send_ofac_alert(
        self, client: httpx.AsyncClient, query: str, validation: str
    ) -> None:
        token = self.valves.TELEGRAM_BOT_TOKEN
        chat_id = self.valves.TELEGRAM_CHAT_ID
        if not token or not chat_id:
            return
        snippet = validation[:600].replace("<", "&lt;").replace(">", "&gt;")
        text = (
            f"*AXIOM OFAC ALERT*\n\n"
            f"Query: `{query[:100]}`\n\n"
            f"Validation snippet:\n```\n{snippet}\n```"
        )
        try:
            await client.post(
                f"https://api.telegram.org/bot{token}/sendMessage",
                json={"chat_id": chat_id, "text": text, "parse_mode": "Markdown"},
                timeout=10.0,
            )
        except Exception:
            pass

    # ── COMPILER ─────────────────────────────────────────────────────────

    def _compiler_prompt(self) -> str:
        return (
            "You are the AXIOM compiler. Format validated investigation findings as a complete professional HTML report.\n\n"
            "Required sections:\n"
            "1. Executive Summary (2-3 sentences)\n"
            "2. Subject Profile (name, DOB, location, aliases if found)\n"
            "3. Findings by Source (each finding with source URL, status label, and timestamp)\n"
            "4. Validation Status table (task | status | key finding)\n"
            "5. Flags (OFAC hits, legal actions, address discrepancies, other anomalies)\n"
            "6. Methodology (list of sources searched)\n"
            "7. Disclaimer\n\n"
            f"Disclaimer (use verbatim): {_REPORT_DISCLAIMER}\n\n"
            "Rules:\n"
            "- Return complete valid HTML starting with <!DOCTYPE html>.\n"
            "- Include inline CSS for professional styling: dark header bar, clean tables, readable font.\n"
            "- Every finding must cite its source URL and timestamp.\n"
            "- Never fabricate sources.\n"
            "- Never claim a record is clean — only that no public record was found.\n"
            "- If OFAC_HIT appears in validation, render it prominently in a red alert box.\n"
            "- Return only the HTML document. No markdown wrapper, no explanation."
        )

    # ── GOTENBERG ─────────────────────────────────────────────────────────

    async def _gotenberg_render(
        self, client: httpx.AsyncClient, html: str
    ) -> bytes | None:
        try:
            html_bytes = html.encode("utf-8")
            files = {"files": ("index.html", html_bytes, "text/html")}
            response = await client.post(
                f"{self.valves.GOTENBERG_URL.rstrip('/')}/forms/chromium/convert/html",
                files=files,
                timeout=60.0,
            )
            response.raise_for_status()
            return response.content
        except Exception:
            return None

    # ── PAPERLESS ─────────────────────────────────────────────────────────

    async def _paperless_archive(
        self,
        client: httpx.AsyncClient,
        pdf_bytes: bytes,
        filename: str,
        title: str,
    ) -> str | None:
        headers = {"Authorization": f"Token {self.valves.PAPERLESS_TOKEN}"}
        try:
            files = {"document": (filename, pdf_bytes, "application/pdf")}
            data = {"title": title[:128], "tags": str(self.valves.PAPERLESS_TAG_ID)}
            response = await client.post(
                f"{self.valves.PAPERLESS_URL.rstrip('/')}/api/documents/post_document/",
                headers=headers,
                files=files,
                data=data,
                timeout=60.0,
            )
            response.raise_for_status()
            result = response.json()
            if isinstance(result, dict):
                return str(result.get("id") or result.get("task_id") or "queued")
            return "queued"
        except Exception:
            return None
