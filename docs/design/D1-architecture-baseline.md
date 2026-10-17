# Weekly AI Work Planner — D1 Architecture Baseline

Status: APPROVED (functional baseline) | Version: 1.0 | Date: 2026-10-17

## Goal
Autonomous, capacity-aware engineering work orchestration across Gentle-AI Markdown plans and Google Drive business/technical documents converted into Plane epics and groomed tasks. Optional progress projection to Google Sheets or Monday.

## Resources
- Laptop: Claude Desktop Pro; Claude Code CLI subscription integration to be validated.
- PC: Claude Desktop Max 20x; Claude Code CLI subscription integration to be validated.
- PC: Codex CLI with ChatGPT Business Standard; unattended subscription authentication to be validated.
- Server: Gemma4:31B through LiteLLM; direct API worker.
No automatic fallback to paid commercial APIs or unapproved additional spending. Commercial quotas are empirical, not fixed token allowances; 20x is nominal subscription tier, not exact throughput.

## Technology and deployment
Java 21+ / Spring Boot modular monolith, PostgreSQL transactional state and lease-based queue, distributed workers on laptop/PC/server, HTTPS polling initially, Angular administrative UI later. Python adapter may reuse existing Gentle-AI routing scripts. No Temporal/Kafka/Kubernetes required for MVP. Worktrees for code isolation (not a security sandbox), immutable context packs, short focused sessions, evidence-based validation and checkpoints.

## Domain boundary
Project -> Requirement (optional) -> Epic (optional) -> Task -> Operation -> ExecutionAttempt -> Evidence/Artifact. SourceDocument/SourceRevision and ExternalBinding maintain provenance; Capacity/Resource/Policy/Approval/PlanningRun are separate domains. Stable internal UUIDs; external references never primary keys.

## Planning policies — APPROVED defaults
- Weekly rolling horizon; continuous replanning on incident, capacity, priority and dependency changes.
- Per-resource capacity budget: 70% planned work, 20% incident reserve, 10% uncertainty margin. Reservations are estimates, not fungible across providers.
- Unused incident reserve may be borrowed only by interruptible work at safe checkpoints.
- Project priorities P0/P1/P2/P3/P4 with initial weights 8/4/2/1/0; P4 paused. Weight determines proportional allocation among eligible projects, not guaranteed quotas. Configurable fairness/minimum share and starvation prevention.
- Tasks can be deferred to following weeks if deadlines and critical dependencies allow; preserve deferral reason/history.
- Incidents SEV1–SEV4, with SEV1/SEV2 immediate replanning, diagnosis, fix, test and review. Safe-checkpoint preemption only.
- Dependencies at project, capability/milestone, and task level. Dependency kinds HARD, SOFT, MOCKABLE, OPTIONAL. Capability states PLANNED, IMPLEMENTED, VERIFIED, AVAILABLE; unlock requires environment/version-compatible AVAILABLE evidence. Allow contract-first mocks but require real integration verification for completion.
- Priority inheritance applies only to the blocking path of higher-priority downstream work, not entire producer project. Validate hard dependency cycles, recalculate impact on capability/contract changes.

## Execution and governance
Autonomous by default; approvals for irreversible, rollback-unverified, destructive high-impact or otherwise policy-sensitive operations. Out-of-scope actions denied. Workers register capabilities and heartbeats, lease operations with fencing tokens, execute with bounded retries, checkpoint and return structured results. Reconcile externally applied side effects before retry; no exactly-once guarantee for external systems. Deterministic idempotent API synchronization for Plane/Sheets/Monday. Credentials stay outside LLM context; treat repo/docs as untrusted inputs.

## Capacity and scheduling
Separate observed quotas, resource uptime, technical capability, autonomy level, historical success, latency, deadlines, incident reserve and uncertainty. Unknown quota != unlimited. Preserve session and weekly reset estimates separately, avoid claiming fixed token budgets. Scheduler applies hard eligibility filters before weighted scoring. Plan outputs retain decisions, reasons, confidence and deferred work.

## Integration contracts
Gentle-AI Markdown parser requires actual sample files before format finalization. Google Drive ingestion preserves source revision/requirement evidence, Plane syncing is incremental and conflict-aware; Sheets/Monday are reporting projections by default. JSON Schema versioned ContextPack, ExecutionRequest and ExecutionResult; nullable token usage when unavailable.

## Open validation items (do not silently assume)
- Claude Code CLI subscription-based unattended execution and permissions on both machines.
- Codex CLI unattended execution and Business Standard usage observation.
- Real Gentle-AI Markdown examples and existing Python intercept scripts.
- Credentials, repo checkout/worktree distribution, actual LiteLLM performance, and external API scopes.

## Deliverables
D1 approved. D2 domain model/PostgreSQL; D3 capacity scheduler; D4 worker protocol; D5 integrations; D6 governance/operations. Changes to D1 require a recorded ADR.
