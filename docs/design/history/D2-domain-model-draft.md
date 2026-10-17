# Weekly AI Work Planner — D2 Domain and PostgreSQL Design

Status: DRAFT | Version: 0.1 | Date: 2026-10-17

## 1. Scope and invariants
D2 converts approved D1 into a relational domain model. PostgreSQL is the authoritative transactional store; Git, Drive, Plane, Sheets and Monday are external systems. UUID PKs, UTC timestamptz, optimistic version fields, immutable historical revisions, and uniqueness constraints for idempotency. Use `jsonb` for extensible provider payloads, not for core searchable relationships.

## 2. Bounded contexts
1. Portfolio: `projects`, `project_settings`, `project_priority_history`, `project_dependencies`.
2. Source/traceability: `source_documents`, `source_revisions`, `requirements`, `requirement_sources`, `epics`, `external_bindings`.
3. Work graph: `tasks`, `task_dependencies`, `capabilities`, `capability_versions`, `capability_requirements`, `capability_evidence`.
4. Planning: `planning_runs`, `capacity_budgets`, `capacity_allocations`, `schedule_entries`, `task_deferrals`, `estimates`.
5. Incidents: `incidents`, `incident_task_links`, `incident_events`.
6. Execution: `operations`, `execution_attempts`, `operation_leases`, `artifacts`, `execution_evidence`, `workers`, `resources`.
7. Governance/telemetry: `policies`, `approvals`, `capacity_observations`, `audit_events`, `outbox_events`.

## 3. Primary entity contracts
- Project: `id`, `code` unique, `name`, `workflow_type` (GENTLE_AI|DRIVE_PLANE|HYBRID), `status`, `priority` (P0..P4), `priority_weight_override`, `deferral_policy`, `created_at`, `updated_at`, `row_version`.
- Task: `id`, `project_id`, `external_key`, `title`, `description`, `status`, `urgency`, `priority_override`, `deadline_at`, `estimated_effort`, `deferred_count`, `source_revision_id` nullable, `row_version`; unique `(project_id, external_key)` when external_key exists.
- Requirement/Epic: own UUIDs and project ownership, source evidence and optional external binding. Epics are not mandatory for Gentle-AI projects.
- Capability: `id`, `provider_project_id`, `capability_key`; unique `(provider_project_id, capability_key)`; versions hold semantic version, environment, acceptance contract and state; AVAILABLE requires linked verification evidence.
- CapabilityRequirement: consumer project/task, capability version constraint, environment, dependency kind and state. TaskDependency references predecessor/successor task UUIDs across projects, type and metadata; prohibit self-edge and validate cycles at application level under transaction.
- Incident: `id`, `project_id`, `severity` (SEV1..SEV4), `status`, `impact`, `detected_at`, `resolved_at`, `source_binding_id`, `replan_triggered_at`; link to diagnosis/fix/test tasks.
- Resource: logical model/subscription profile, host, provider, mode, enabled flag, capabilities; Worker: machine instance and heartbeat; resource allocation to worker is explicit (PC can run Claude Max and Codex).
- CapacityBudget: resource, week window, capacity unit/estimate/confidence, planned/incident/uncertainty proportions and remaining reserves. CapacityAllocation: planning run, project, resource, budget pool, reserved/consumed estimate.
- PlanningRun: horizon, trigger, configuration snapshot hash, solver version, status, created_at; ScheduleEntry: operation/task, resource, pool, priority reasoning, planned slot, state; TaskDeferral: original/new week, reason, event source.
- Operation: task, type, state, idempotency key, context pack hash, policy snapshot; ExecutionAttempt: operation, attempt number, worker/resource, lease generation, timestamps, status, usage fields nullable, evidence refs. Unique `(operation_id, attempt_number)` and operation idempotency key within relevant scope.
- ExternalBinding: provider, external object type/id, internal object type/id, sync cursor, last observed revision; unique `(provider, external_object_type, external_id)`.

## 4. Data integrity and concurrency
- Enforce all foreign keys and unique external bindings. Consider partial unique indexes for optional keys.
- Use `SELECT ... FOR UPDATE SKIP LOCKED` to claim READY operations, transactional state change and monotonically increasing fencing generation.
- Expired leases require reconciliation before retrying non-idempotent effects. Store outbox event in same transaction as state changes; external connector marks delivery/reconciliation separately.
- Preserve immutable source revisions and capability evidence; never mutate an old planning run.
- Enforce capability availability through application service plus database constraints where feasible; verification environment/version must match consumers.
- Use indexes for `(project_id,status,priority)`, dependency endpoints, incident severity/status, worker heartbeat, `(resource_id,window_start)`, ready queue state and lease expiry.
- Row-level ownership and scoped credentials must be enforced by service authorization; do not expose arbitrary host command execution to model-generated payloads.

## 5. State machines (to finalize)
Task: BACKLOG -> READY -> IN_PROGRESS -> VERIFYING -> DONE; alternative BLOCKED, DEFERRED, FAILED, CANCELLED. Incident: OPEN -> TRIAGED -> INVESTIGATING -> FIXING -> VERIFYING -> RESOLVED; REOPENED allowed. Operation: READY -> LEASED -> RUNNING -> VERIFYING -> COMPLETED; alternative WAITING_CAPACITY, BLOCKED_APPROVAL, RETRY_PENDING, FAILED, CANCELLED. Capability version: PLANNED -> IMPLEMENTED -> VERIFIED -> AVAILABLE; INVALIDATED from VERIFIED/AVAILABLE with downstream impact.

## 6. D2 remaining design tasks
1. Specify cardinalities, deletion/retention rules, and detailed SQL DDL.
2. Formalize graph semantics for HARD/SOFT/MOCKABLE/OPTIONAL, critical path and cross-project priority inheritance.
3. Specify budget unit and uncertainty model separately per provider, including session/week reset and incident reserve borrowing ledger.
4. Define exact state transition guards and immutable event payloads.
5. Add Flyway migrations, indexes, data fixtures and integrity/concurrency tests.
6. Review requirements against real Gentle-AI Markdown, Plane API and Drive document IDs.

## 7. Open design decision
Choose whether project priority is a fixed weekly snapshot or may change midweek. Recommendation: retain immutable planning-run snapshots and allow changes to trigger a new run, with full historical traceability.

## 8. Detailed relational design (v0.2)
Flyway baseline migrations:
- `migrations/V1__core_domain.sql`: projects, source lineage, requirements, epics, tasks, cross-project dependencies, capability contracts/evidence, external bindings.
- `migrations/V2__planning_execution_governance.sql`: workers/resources, capacity observations, planning runs/budgets/allocations, incidents, operations/attempts/leases, schedules/deferrals, approvals, audit/outbox.

### Cardinalities
- Project 1:N Tasks/Requirements/Epics/Capabilities/Incidents; Epic 0:N Tasks; Task 1:N Operations; Operation 1:N Attempts; Operation 0:1 current Lease; Attempt N:M Artifacts via Evidence.
- Project N:M Project through `project_dependencies`; Task N:M Task through directed `task_dependencies`; Task N:M Capability through `capability_requirements`.
- SourceDocument 1:N immutable SourceRevisions; Requirement N:M SourceRevision with locator; Epic N:M Requirement.
- PlanningRun 1:N Budgets/Allocations/ScheduleEntries/Deferrals. Resource 1:N CapacityObservations/Budgets; Worker 1:N Resources (nullable assignment permits resource temporarily offline).

### Referential deletion/retention
- Default `ON DELETE NO ACTION`: do not cascade historical execution, source revisions, planning, evidence, audit, or incidents.
- Archive projects/tasks using status. Expire raw logs/artifacts only under an explicit retention policy while retaining hashes and audit metadata.
- External IDs are not PKs. `external_bindings` uses a polymorphic internal reference requiring application-level target validation; consider typed binding tables later if necessary.

### Transactional invariants beyond declarative SQL
- All dependency edges of type HARD must form a DAG; validate with recursive CTE and a transaction-scoped advisory lock for graph mutations, or use SERIALIZABLE with retry. Also validate versioned capability requirements against environment and semantic version constraints.
- `capability_versions.state = AVAILABLE` requires at least one PASS evidence for that exact version/environment, validated in a domain service transaction; invalidate downstream consumers when contract changes.
- `capacity_budgets` store proportions, not universally comparable quota units. Capacity estimates may be NULL until calibrated; a NULL estimate must not imply unlimited capacity.
- Aggregate allocation caps and reserve borrowing must be checked transactionally with locking on budget rows. A future `capacity_ledger` migration should record borrow/return and actual consumption to avoid mutable-only accounting.
- Planning runs are immutable after PUBLISHED; changing priorities or capacity creates a new run, superseding the old one. Enforce in domain service (and optionally DB triggers).
- Operations claimed with `FOR UPDATE SKIP LOCKED` increment `lease_generation`, create attempt and lease atomically; results accepted only with matching fencing generation. Lease expiry enters RECONCILING before potentially requeueing.
- External mutations require idempotency/reconciliation in connector adapter. Outbox delivery is at-least-once, not exactly-once.
- Approval applies to the exact operation and immutable policy/context snapshot. Approval expiry or snapshot changes require reauthorization.
- Project/epic/requirement ownership equality and external polymorphic references require service checks or additional DB triggers.

### Priority and dependency semantics
- Base priorities P0=8, P1=4, P2=2, P3=1, P4=0. Effective priority may inherit along the blocking path from high-priority consumers; do not rewrite base priority.
- HARD gates downstream execution. MOCKABLE allows implementation against versioned contract/mocks but gates real integration completion. SOFT permits early work with retrabajo risk. OPTIONAL never gates baseline completion.
- Deferral must preserve immutable reason and original/new week. Deadlines and blocking paths can prohibit deferral.
- Capacity default: PLANNED 70%, INCIDENT 20%, UNCERTAINTY 10%, **per resource and window**. Idle reserve can be borrowed only by interruptible work with safe checkpoints.

### Open before production readiness
1. Define exact transition matrix and database enforcement strategy for all state machines.
2. Add transactional capacity ledger and cross-budget constraints.
3. Add policy versions, source ownership enforcement, resource skill/capability normalization, provider-specific quota windows.
4. Add repeatable database integration tests with Testcontainers/PostgreSQL, Flyway validation, concurrent leasing and graph cycle tests.
5. Validate CLI automation permissions and real Gentle-AI/Plane/Drive source formats.

**Migration status:** proposed SQL, not yet applied to a PostgreSQL instance. D2 remains draft until the above are resolved.

## 9. D2.3 addendum — capacity accounting and recovery
See `D2.3-state-capacity-recovery.md` for state transition contracts, immutable capacity journal, provider measurement provenance, transactional guards and lease reconciliation. Proposed Flyway `V3__capacity_ledger_and_state_history.sql` introduces `capacity_movements`, `capacity_measurements`, `state_transition_rules` and `state_transition_events`. **D2 is still draft** pending DB validation, transition seeds, concurrency tests and stricter balance invariants.

## D2.4 addendum (draft v0.4)

See `D2.4-transitions-integrity-tests.md` for the complete seeded transition graph, transactional guards, test plan and remaining approval gates. Proposed Flyway `V4__transition_rules_and_integrity.sql` seeds allowed edges and begins phased budget FK enforcement; it is not yet executed against PostgreSQL.
