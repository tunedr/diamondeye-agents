# DiamondEye Standing Rules — Cannot Be Overridden

1. Pipeline never modifies its own infrastructure
2. n8n must be paused before any pipeline surgery
3. No data deleted from Unraid until TrueNAS consolidation is complete
4. Search Notion before creating anything new
5. Tailscale IPs only for inter-service traffic — never LAN IPs in configs
6. No ZFS native dedup on TrueNAS
7. TrueNAS infrastructure projects gated on Phase 2b — planning and docs allowed
8. Claude API = revenue tools and hard escalations only — never internal pipeline
9. DeepSeek and Ollama handle high-volume and routine tasks — protect Claude credits
10. Proxmox snapshots and git tags before any major change
11. pfSense: do not touch without explicit Branden approval
12. No apt upgrade on any remote VM without explicit task card
13. All task results go to Notion before session ends
14. Ollama is NEVER at localhost from any non-pop-ollama service. Always at 192.168.1.136:11434. Any service on VM 104, MGMT-XPS, or any container referencing localhost:11434 is misconfigured. Use os.environ.get("OLLAMA_HOST", "http://192.168.1.136:11434") pattern.
15. ICM Inventory: The Librarian (de-librarian-01) maintains a live inventory of all ICM markdown files across every machine every 6 hours. Before closing any build session on a new VM, Claude Code must: (a) create ~/AGENTS/ on the new VM, (b) copy GLOBAL/ ICM structure from MGMT-XPS via scp, (c) write LOCAL/machine-config.md with machine-specific details, (d) confirm the Librarian's next inventory run will pick it up. See GLOBAL/icm-inventory-spec.md for full spec.
16. All Agent Zero instances use the dual-model pattern. DeepSeek on pop-ollama (192.168.1.136:11434) for reasoning and execution. Qwen2.5:7b on Unraid (192.168.1.2:11434) for classification and embedding. Never load both models on the same GPU. Never wire an instance to a single model only.
