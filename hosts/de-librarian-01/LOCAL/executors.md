# Executor Routing — de-librarian-01

This file defines which executor handles which task type on this machine.
No executor is invoked without matching against this table first.

## Primary Routing Table

| Task Type | Executor | Endpoint |
|---|---|---|
| Classification, triage, utility tasks | qwen2.5:7b (Ollama) | http://192.168.1.2:11434 |
| Reasoning, planning, OSINT synthesis | deepseek-r1:latest (Ollama) | http://192.168.1.136:11434 |
| Embeddings | nomic-embed-text (Ollama) | http://192.168.1.2:11434 |
| Code generation, complex implementation | Codex CLI (gpt-5.2 via OAuth) | Local CLI |
| Multi-file agentic edits | Claude Code | MGMT-XPS escalation |
| Web search | SearXNG | localhost:55510 (internal) |
| PDF generation | Gotenberg | librarian-gotenberg:3000 (container name) |
| Document archive | Paperless-ngx API | 192.168.1.107:8010 |
| Knowledge retrieval | AnythingLLM API | 192.168.1.107:3001 |

## Rules
- Ollama is NEVER at localhost — always use LAN IPs above
- deepseek-r1 is on pop-ollama (192.168.1.136) ONLY
- qwen2.5:7b and nomic-embed-text are on Unraid (192.168.1.2) ONLY
- Do not swap instances — wrong endpoint = silent wrong model
- Try local model first; escalate to Codex only if output quality is insufficient after one retry
- Document escalation reason in task completion record

## Hermes Profile → Executor Mapping

| Profile | Primary Model | Endpoint |
|---|---|---|
| librarian | qwen2.5:7b | http://192.168.1.2:11434/v1 |
| apollo | deepseek-r1:latest | http://192.168.1.136:11434/v1 |
| truth-lens | deepseek-r1:latest | http://192.168.1.136:11434/v1 |
| coder | qwen2.5:7b | http://192.168.1.2:11434/v1 |
