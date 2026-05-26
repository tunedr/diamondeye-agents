# DiamondEye Standing Rules
# Last revised: 2026-05-25

These rules are the local GLOBAL/ control surface for DiamondEye agents. They preserve the previous standing rules, separate active law from implementation details, and incorporate the VM/project isolation boundary from the DiamondEye VM Isolation Contract.

Status meanings:
- Active: binding rule for all agents.
- Revised: binding rule with clarified wording or narrowed scope.
- Pending review: preserved rule or implementation detail that needs verification before it is treated as fleet law.
- Deprecated: preserved stale rule that should not be applied without review.

## Hard Safety Rules

1. Active: Pipeline agents must never modify their own infrastructure.
   Reason: Preserves original rule 1 and the isolation contract principle that self-repair requires an out-of-band executor/verifier.

2. Active: n8n must be paused before any pipeline surgery.
   Reason: Preserves original rule 2; applies to workflow edits, imports, migrations, activations, deletions, and runtime rewiring.

3. Active: pfSense must not be accessed or changed without explicit Branden approval.
   Reason: Preserves original rule 11 and the isolation contract global no-touch rule.

4. Active: Do not run `apt upgrade` on any remote VM without an explicit task card.
   Reason: Preserves original rule 12; upgrades are infrastructure mutation.

5. Active: Do not run destructive storage, Docker, VM, network, or service operations without explicit authorization.
   Reason: Incorporates the isolation contract no-touch rules, including no autonomous `docker system prune`, no unapproved restarts/rebuilds, and no runtime infrastructure mutation.

6. Active: No autonomous pipeline may be the sole executor or verifier of its own repair.
   Reason: Preserves original rule 18; tasks touching Atlas, scanners, routers, executors, validators, reporting, escalation, task databases, Notion bridge, or future Grist execution records must be routed out of band.

7. Active: Federation workers have scoped permission by default.
   Reason: Preserves original rule 19; read-only diagnostics may be allowed, while destructive or high-risk operations require explicit approval.

## VM/Project Isolation Rules

1. Active: Each VM/project owns its local services, local configuration, runtime state, and machine-specific `LOCAL/` ICM content.
   Reason: Added from the DiamondEye VM Isolation Contract as the active VM/project isolation boundary rule.

2. Active: Shared `GLOBAL/` ICM content is fleet documentation and must not be edited independently per VM.
   Reason: Added from the isolation contract; `GLOBAL/` changes should originate from the git-owned/local source and be propagated only by the approved Librarian process.

3. Active: `LOCAL/` ICM files are owned by their machine and are read-only from other machines unless a task explicitly authorizes that owner-scoped edit.
   Reason: Added from the isolation contract and Librarian SOUL; prevents cross-machine configuration drift.

4. Active: Cross-VM calls are allowed only through approved service endpoints documented in GLOBAL/ files, the Service Map, or an authoritative contract.
   Reason: Added from the isolation contract; prevents accidental dependency creation.

5. Revised: Tailscale IPs are preferred for inter-service traffic where available, but LAN endpoints remain documented where they are the verified or only known path.
   Reason: Preserves original rule 5 while demoting the old "Tailscale IPs only" wording to pending review because local routing documents still use LAN IPs and some hosts lack verified Tailscale.

6. Active: Proxmox, Unraid, TrueNAS, and pfSense are not general execution nodes.
   Reason: Added from the isolation contract; these platforms may be checked read-only only when the task scope allows it.

7. Active: Do not mutate n8n, Docker, services, containers, workflows, Proxmox, Unraid, TrueNAS, pfSense, or other runtime infrastructure during documentation-only tasks.
   Reason: Added from the isolation contract and current task constraints.

8. Active: Atlas and Sentinel are separate control surfaces unless an explicit migration task says otherwise.
   Reason: Added from the isolation contract; do not merge, copy, or reconcile workflows automatically.

## Cost/Routing Rules

1. Active: Claude API is reserved for revenue tools and hard escalations; it must not be used for routine internal pipeline work.
   Reason: Preserves original rule 8.

2. Active: Use local or low-cost models for high-volume and routine tasks when they satisfy the task requirements.
   Reason: Preserves original rule 9 while avoiding hard-coding stale implementation details into policy.

3. Pending review: The fleet model routing pattern currently documents DeepSeek on pop-ollama for chat/reasoning and Qwen2.5/nomic-embed on Unraid for utility/embedding.
   Reason: Preserves original rule 16 as an implementation assumption needing verification, not universal law; do not assume all Agent Zero instances still use a dual-model pattern or that no instance may be single-model until the live fleet is checked.

4. Pending review: Ollama endpoint rules should be expressed as environment-configured approved endpoints, not a blanket localhost prohibition tied to one LAN IP.
   Reason: Preserves original rule 14 while marking the old `localhost:11434` and `192.168.1.136:11434` wording as stale implementation detail needing review against the approved endpoint register.

## Storage/Data Protection Rules

1. Active: Do not delete data from any machine without explicit authorization.
   Reason: Generalizes and strengthens original rule 3 and the isolation contract global no-touch rule.

2. Revised: No data may be deleted from Unraid as part of TrueNAS migration or consolidation work until the consolidation state is explicitly verified and approved.
   Reason: Preserves original rule 3 while removing the assumption that consolidation status is currently known.

3. Active: Do not enable ZFS native dedup on TrueNAS.
   Reason: Preserves original rule 6.

4. Active: Proxmox snapshots and git tags/checkpoints are required before any major approved change.
   Reason: Preserves original rule 10; applies only when a mutation task has already been authorized.

5. Active: Credentials and secrets must not be stored in documentation.
   Reason: Added from the isolation contract and Librarian SOUL; documentation may reference credential locations without copying secret values.

## Verification/Documentation Rules

1. Active: Search Notion and local GLOBAL/ documentation before creating anything new.
   Reason: Preserves original rule 4 and the Librarian search-before-create rule.

2. Revised: Task results must be written to the appropriate local report/worklog before session end, and to Notion/SSOT only when the task permits Notion writes.
   Reason: Preserves original rule 13 and original rule 20 while respecting documentation-only or read-only task scopes.

3. Active: No build, repair, diagnostic, or routing decision is complete until evidence, changed files, before/after state, and next actions are documented in the appropriate local report and, where allowed, Notion/SSOT.
   Reason: Preserves original rule 20.

4. Active: Do not mark any host, service, or artifact unreachable, missing, broken, stale, complete, or repaired until reasonable known access paths and proof methods have been attempted and logged.
   Reason: Preserves original rule 17.

5. Active: Read-only health checks must not become mutation authority.
   Reason: Added from the isolation contract; diagnostic authority and mutation authority are separate.

6. Active: Documentation changes must preserve rule history by marking rules active, revised, pending review, or deprecated rather than silently deleting them.
   Reason: Added by this revision to make future maintenance auditable.

## Pending/Aspirational Rules

1. Pending review: TrueNAS infrastructure projects were previously gated on "Phase 2b".
   Reason: Preserves original rule 7, but "Phase 2b" is not self-evident in current local docs. Planning and documentation remain allowed; implementation requires a verified current gate and explicit task.

2. Pending review: The Librarian live inventory workflow is described as running every 6 hours across every machine.
   Reason: Preserves original rule 15, but current inventory paths, SSH reachability, Tailscale state, Notion mirrors, and propagation behavior must be verified before treating this as live operational fact.

3. Pending review: New VM build-session closeout should create or confirm `~/AGENTS/`, `GLOBAL/` structure, and `LOCAL/machine-config.md` only within the approved owner/mutation boundary.
   Reason: Preserves original rule 15 while preventing automatic SSH/scp propagation from being treated as allowed during documentation-only or no-SSH tasks.

4. Pending review: Tailscale-only configuration policy requires reconciliation with documented LAN endpoints and hosts without verified Tailscale.
   Reason: Preserves original rule 5 as a policy target needing architecture-control review.

5. Pending review: Agent Zero dual-model assumptions require live validation per instance before enforcement.
   Reason: Preserves original rule 16 while avoiding stale fleet-wide assumptions.

6. Pending review: Approved Ollama endpoint wording should be updated after endpoint verification.
   Reason: Preserves original rule 14 while recognizing the isolation contract's endpoint register prefers Tailscale where available and local GLOBAL/ files still document LAN endpoints.

## Deprecated/Stale Rules Needing Review

No existing rule is fully deprecated in this revision. The stale implementation details identified during review have been preserved under "Pending/Aspirational Rules" or revised into active boundary rules instead of being deleted.

Items requiring review before promotion back to active law:
- Tailscale-only configs versus documented LAN service endpoints.
- Librarian live inventory and propagation details.
- Agent Zero dual-model fleet assumptions.
- TrueNAS "Phase 2b" gate wording.
- `localhost`/Ollama endpoint wording and approved endpoint register alignment.
