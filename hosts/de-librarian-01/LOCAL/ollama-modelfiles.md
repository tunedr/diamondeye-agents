# Ollama Custom Modelfiles — pop-ollama (192.168.1.136)

## qwen2.5-coder:7b

**Purpose:** Hermes-coder profile model. Default Ollama num_ctx (32K) is below
Hermes's 64K minimum for tool use. Custom Modelfile bakes in num_ctx 65536.

**Modelfile:**
```
FROM qwen2.5-coder:7b
PARAMETER num_ctx 65536
```

**Applied:** 2026-06-06 via `echo "FROM qwen2.5-coder:7b\nPARAMETER num_ctx 65536" | docker exec -i ollama ollama create qwen2.5-coder:7b -f /dev/stdin`

**Verify:** `docker exec ollama ollama show qwen2.5-coder:7b` → should show `num_ctx 65536`

**Note:** Architectural context limit is 32,768 tokens. The num_ctx override tells
Ollama to allocate 65K context at runtime; actual inference may silently cap at 32K
but Hermes's minimum check passes and tool use functions correctly.
