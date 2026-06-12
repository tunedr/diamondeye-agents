# Executor Routing — de-librarian-01

This file defines which executor handles which task type on this machine.
No executor is invoked without matching against this table first.

## Primary Routing Table (updated 2026-06-05)

| Task Type | Executor | Endpoint |
|---|---|---|
| Chat, reasoning, planning, OSINT synthesis | llama3.2:latest (Ollama) | http://192.168.1.2:11434 |
| Code generation, utility, classification | qwen2.5-coder:7b (Ollama) | http://192.168.1.136:11434 |
| Embeddings | nomic-embed-text (Ollama) | http://192.168.1.2:11434 |
| Complex code / multi-file agentic edits | Codex CLI (gpt-5.x via OAuth) | Local CLI → MGMT-XPS escalation |
| Web search | SearXNG | localhost:55510 (internal) |
| PDF generation | Gotenberg | librarian-gotenberg:3000 (container name) |
| Document archive | Paperless-ngx API | 192.168.1.107:8010 |
| Knowledge retrieval | AnythingLLM API | 192.168.1.107:3001 |

## Rules
- Ollama is NEVER at localhost — always use LAN IPs above
- llama3.2:latest and nomic-embed-text are on Unraid (192.168.1.2) ONLY
- qwen2.5-coder:7b is on pop-ollama (192.168.1.136) ONLY
- Do not swap instances — wrong endpoint = silent wrong model
- Try local model first; escalate to Codex only if output quality is insufficient after one retry
- Document escalation reason in task completion record
- deepseek-r1 and qwen2.5:7b are retired from fleet use (2026-06-05) — do not route to them

## Hermes Profile → Executor Mapping (updated 2026-06-05)

| Profile | Primary Model | Endpoint |
|---|---|---|
| librarian | llama3.2:latest | http://192.168.1.2:11434/v1 |
| apollo | llama3.2:latest | http://192.168.1.2:11434/v1 |
| truth-lens | llama3.2:latest | http://192.168.1.2:11434/v1 |
| coder | qwen2.5-coder:7b | http://192.168.1.136:11434/v1 |
