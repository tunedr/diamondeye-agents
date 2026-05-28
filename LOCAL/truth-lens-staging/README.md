# Truth Lens Staging

This directory stages the Truth Lens build requested for VM 108.

## Included
- `openwebui/truth_lens_pipe.py` - OpenWebUI pipe for planner, executor, validator, and presenter layers.
- `prompts/agent.system.main.specifics.md` - Truth Lens Agent Zero persona for raw research findings.

## Runtime dependencies baked into the pipe
- OpenAI-compatible Codex endpoint for planner/validator/presenter
- Agent Zero VM 108 API on `http://192.168.1.108:7072/api/api_message`
- SearXNG fallback on `http://192.168.1.2:8081/search`

## Manual deployment notes
- Copy the persona prompt to `/a0/prompts/agent.system.main.specifics.md` on VM 108.
- Install the pipe into the OpenWebUI custom pipe location used by VM 108.
- Set `truth-lens-pipe` as the default model for the `truth.diamondeye.net` access path.
- Create the NPM proxy for `truth.diamondeye.net` to forward to `192.168.1.108:3000`.
- Create the Cloudflare DNS record manually if automation is unavailable.

