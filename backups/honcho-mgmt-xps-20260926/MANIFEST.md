# MGMT-XPS honcho Backup Manifest
# Created: 2026-09-26 by Claude Code — Git/resource coverage session
# Source host: MGMT-XPS — 192.168.1.221

## Current Status
RUNNING — host network, port :8000
- Fixed 2026-08-05 (prior dummy OpenRouter key caused 9-min Desk delay)
- Up since 2026-08-05 (26h at time of services.md verification)

## No Compose File
honcho was started with a direct docker run command, not a docker-compose.yml.
Reconstructed command (secrets redacted):

```bash
docker run -d \
  --name honcho \
  --network host \
  --restart unless-stopped \
  -v /home/tunedr/.hermes:/opt/data \
  -e "DB_CONNECTION_URI=postgresql+psycopg://honcho:<REDACTED:HONCHO_DB_PASSWORD>@127.0.0.1:5433/honcho" \
  -e "DATABASE_URL=postgresql+psycopg://honcho:<REDACTED:HONCHO_DB_PASSWORD>@127.0.0.1:5433/honcho" \
  -e "LLM_OPENAI_API_KEY=<REDACTED:OPENROUTER_API_KEY>" \
  -e "LLM_OPENAI_BASE_URL=https://openrouter.ai/api/v1" \
  -e "EMBEDDING_MODEL_CONFIG__TRANSPORT=openai" \
  -e "EMBEDDING_MODEL_CONFIG__MODEL=nomic-embed-text:latest" \
  -e "EMBEDDING_MODEL_CONFIG__OVERRIDES__BASE_URL=http://192.168.1.2:11434/v1" \
  -e "EMBEDDING_MODEL_CONFIG__OVERRIDES__API_KEY=dummy" \
  -e "EMBEDDING_VECTOR_DIMENSIONS=768" \
  ghcr.io/plastic-labs/honcho:latest
```

honcho-postgres runs alongside:
```bash
docker run -d \
  --name honcho-postgres \
  -p 127.0.0.1:5433:5432 \
  --restart unless-stopped \
  -v /home/tunedr/honcho/postgres-data:/var/lib/postgresql/data \
  -e POSTGRES_USER=honcho \
  -e "POSTGRES_PASSWORD=<REDACTED:HONCHO_DB_PASSWORD>" \
  -e POSTGRES_DB=honcho \
  postgres:16
```

## Secrets Needed for Recovery
- HONCHO_DB_PASSWORD: same password used across the fleet (in CREDENTIALS.env on pop-ollama)
- OPENROUTER_API_KEY: same key used in hermes-desk (in CREDENTIALS.env on pop-ollama)
- Embedding: dummy key is intentional (Ollama doesn't require auth)

## Gap Note
honcho has no docker-compose.yml. Recommend creating one to make recovery reproducible.
This is a documentation gap; the service itself is healthy.
