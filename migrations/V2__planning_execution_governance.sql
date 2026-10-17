-- Weekly AI Work Planner / Flyway V2
CREATE TABLE workers (
 id uuid PRIMARY KEY DEFAULT gen_random_uuid(), worker_key text NOT NULL UNIQUE, host_name text NOT NULL,
 state text NOT NULL DEFAULT 'OFFLINE' CHECK(state IN ('ONLINE','OFFLINE','DRAINING')),
 last_heartbeat_at timestamptz, capabilities jsonb NOT NULL DEFAULT '{}'::jsonb
);
CREATE TABLE resources (
 id uuid PRIMARY KEY DEFAULT gen_random_uuid(), resource_key text NOT NULL UNIQUE,
 worker_id uuid REFERENCES workers(id), provider text NOT NULL,
 subscription text NOT NULL, model_profile text, enabled boolean NOT NULL DEFAULT true,
 capabilities jsonb NOT NULL DEFAULT '{}'::jsonb
);
CREATE TABLE capacity_observations (
 id uuid PRIMARY KEY DEFAULT gen_random_uuid(), resource_id uuid NOT NULL REFERENCES resources(id),
 observed_at timestamptz NOT NULL DEFAULT now(), window_start timestamptz, window_end timestamptz,
 quota_remaining_pct numeric(6,3) CHECK(quota_remaining_pct BETWEEN 0 AND 100),
 reported_input_tokens bigint CHECK(reported_input_tokens >= 0),
 reported_output_tokens bigint CHECK(reported_output_tokens >= 0),
 source text NOT NULL, confidence numeric(4,3) CHECK(confidence BETWEEN 0 AND 1)
);
CREATE INDEX idx_capacity_obs ON capacity_observations(resource_id,observed_at DESC);
CREATE TABLE planning_runs (
 id uuid PRIMARY KEY DEFAULT gen_random_uuid(), horizon_start timestamptz NOT NULL,
 horizon_end timestamptz NOT NULL, trigger_type text NOT NULL,
 status text NOT NULL DEFAULT 'DRAFT' CHECK(status IN ('DRAFT','PUBLISHED','SUPERSEDED','FAILED')),
 config_snapshot jsonb NOT NULL, config_sha256 char(64) NOT NULL,
 solver_version text NOT NULL, created_at timestamptz NOT NULL DEFAULT now(),
 CHECK(horizon_end > horizon_start)
);
CREATE TABLE capacity_budgets (
 id uuid PRIMARY KEY DEFAULT gen_random_uuid(), planning_run_id uuid NOT NULL REFERENCES planning_runs(id),
 resource_id uuid NOT NULL REFERENCES resources(id),
 window_start timestamptz NOT NULL, window_end timestamptz NOT NULL,
 capacity_unit text NOT NULL CHECK(capacity_unit IN ('CALIBRATED_QUOTA','SECONDS','TOKENS','OPERATIONS')),
 estimated_capacity numeric(18,4), confidence numeric(4,3) CHECK(confidence BETWEEN 0 AND 1),
 planned_pct numeric(5,2) NOT NULL DEFAULT 70,
 incident_pct numeric(5,2) NOT NULL DEFAULT 20,
 uncertainty_pct numeric(5,2) NOT NULL DEFAULT 10,
 CHECK(window_end > window_start),
 CHECK(planned_pct >= 0 AND incident_pct >= 0 AND uncertainty_pct >= 0),
 CHECK(planned_pct + incident_pct + uncertainty_pct = 100),
 CHECK(estimated_capacity IS NULL OR estimated_capacity >= 0),
 UNIQUE(planning_run_id,resource_id,window_start)
);
CREATE TABLE capacity_allocations (
 id uuid PRIMARY KEY DEFAULT gen_random_uuid(), planning_run_id uuid NOT NULL REFERENCES planning_runs(id),
 resource_id uuid NOT NULL REFERENCES resources(id), project_id uuid NOT NULL REFERENCES projects(id),
 pool text NOT NULL CHECK(pool IN ('PLANNED','INCIDENT','UNCERTAINTY')),
 reserved_units numeric(18,4), consumed_units numeric(18,4) NOT NULL DEFAULT 0,
 CHECK(reserved_units IS NULL OR reserved_units >= 0), CHECK(consumed_units >= 0),
 UNIQUE(planning_run_id,resource_id,project_id,pool)
);
CREATE TABLE incidents (
 id uuid PRIMARY KEY DEFAULT gen_random_uuid(), project_id uuid NOT NULL REFERENCES projects(id),
 incident_key text NOT NULL, severity text NOT NULL CHECK(severity IN ('SEV1','SEV2','SEV3','SEV4')),
 status text NOT NULL DEFAULT 'OPEN' CHECK(status IN ('OPEN','TRIAGED','INVESTIGATING','FIXING','VERIFYING','RESOLVED','REOPENED')),
 impact text, detected_at timestamptz NOT NULL DEFAULT now(), resolved_at timestamptz,
 UNIQUE(project_id,incident_key)
);
CREATE TABLE incident_task_links (
 incident_id uuid NOT NULL REFERENCES incidents(id), task_id uuid NOT NULL REFERENCES tasks(id),
 role text NOT NULL CHECK(role IN ('DIAGNOSIS','FIX','TEST','FOLLOW_UP')),
 PRIMARY KEY(incident_id,task_id,role)
);
CREATE TABLE operations (
 id uuid PRIMARY KEY DEFAULT gen_random_uuid(), task_id uuid NOT NULL REFERENCES tasks(id),
 operation_type text NOT NULL, state text NOT NULL DEFAULT 'READY' CHECK(state IN
 ('READY','WAITING_CAPACITY','BLOCKED_APPROVAL','LEASED','RUNNING','VERIFYING','RETRY_PENDING','COMPLETED','FAILED','CANCELLED','RECONCILING')),
 idempotency_key text NOT NULL UNIQUE, context_pack_sha256 char(64), context_pack_ref text,
 policy_snapshot jsonb NOT NULL DEFAULT '{}'::jsonb, lease_generation bigint NOT NULL DEFAULT 0,
 created_at timestamptz NOT NULL DEFAULT now(), row_version bigint NOT NULL DEFAULT 0
);
CREATE INDEX idx_operations_ready ON operations(created_at,id) WHERE state IN ('READY','RETRY_PENDING');
CREATE TABLE execution_attempts (
 id uuid PRIMARY KEY DEFAULT gen_random_uuid(), operation_id uuid NOT NULL REFERENCES operations(id),
 attempt_no integer NOT NULL CHECK(attempt_no > 0), worker_id uuid NOT NULL REFERENCES workers(id),
 resource_id uuid NOT NULL REFERENCES resources(id), lease_generation bigint NOT NULL,
 state text NOT NULL, started_at timestamptz, finished_at timestamptz,
 input_tokens bigint CHECK(input_tokens >= 0), output_tokens bigint CHECK(output_tokens >= 0),
 duration_ms bigint CHECK(duration_ms >= 0), error_code text, result jsonb,
 UNIQUE(operation_id,attempt_no), UNIQUE(id,operation_id)
);
CREATE TABLE operation_leases (
 operation_id uuid PRIMARY KEY REFERENCES operations(id),
 attempt_id uuid NOT NULL UNIQUE, worker_id uuid NOT NULL REFERENCES workers(id),
 fencing_generation bigint NOT NULL, expires_at timestamptz NOT NULL,
 FOREIGN KEY(attempt_id,operation_id) REFERENCES execution_attempts(id,operation_id)
);
CREATE INDEX idx_leases_expiry ON operation_leases(expires_at);
CREATE TABLE artifacts (
 id uuid PRIMARY KEY DEFAULT gen_random_uuid(), artifact_ref text NOT NULL UNIQUE,
 sha256 char(64) NOT NULL, media_type text NOT NULL, byte_size bigint CHECK(byte_size >= 0),
 created_at timestamptz NOT NULL DEFAULT now()
);
CREATE TABLE execution_evidence (
 attempt_id uuid NOT NULL REFERENCES execution_attempts(id), artifact_id uuid NOT NULL REFERENCES artifacts(id),
 evidence_type text NOT NULL, PRIMARY KEY(attempt_id,artifact_id,evidence_type)
);
CREATE TABLE schedule_entries (
 id uuid PRIMARY KEY DEFAULT gen_random_uuid(), planning_run_id uuid NOT NULL REFERENCES planning_runs(id),
 task_id uuid NOT NULL REFERENCES tasks(id), resource_id uuid NOT NULL REFERENCES resources(id),
 operation_id uuid REFERENCES operations(id), pool text NOT NULL CHECK(pool IN ('PLANNED','INCIDENT','UNCERTAINTY')),
 planned_start timestamptz, planned_end timestamptz, state text NOT NULL DEFAULT 'PLANNED',
 priority_snapshot jsonb NOT NULL, reason jsonb NOT NULL DEFAULT '{}'::jsonb,
 CHECK(planned_end IS NULL OR planned_start IS NULL OR planned_end >= planned_start)
);
CREATE TABLE task_deferrals (
 id uuid PRIMARY KEY DEFAULT gen_random_uuid(), task_id uuid NOT NULL REFERENCES tasks(id),
 planning_run_id uuid NOT NULL REFERENCES planning_runs(id), original_week date NOT NULL,
 deferred_to_week date NOT NULL, reason text NOT NULL, created_at timestamptz NOT NULL DEFAULT now(),
 CHECK(deferred_to_week > original_week)
);
CREATE TABLE approvals (
 id uuid PRIMARY KEY DEFAULT gen_random_uuid(), operation_id uuid NOT NULL REFERENCES operations(id),
 state text NOT NULL DEFAULT 'PENDING' CHECK(state IN ('PENDING','APPROVED','REJECTED','EXPIRED')),
 reason text NOT NULL, requested_at timestamptz NOT NULL DEFAULT now(),
 decided_at timestamptz, decided_by text
);
CREATE UNIQUE INDEX idx_one_pending_approval ON approvals(operation_id) WHERE state='PENDING';
CREATE TABLE audit_events (
 id uuid PRIMARY KEY DEFAULT gen_random_uuid(), occurred_at timestamptz NOT NULL DEFAULT now(),
 actor text NOT NULL, entity_type text NOT NULL, entity_id uuid NOT NULL,
 action text NOT NULL, payload jsonb NOT NULL DEFAULT '{}'::jsonb
);
CREATE INDEX idx_audit_entity ON audit_events(entity_type,entity_id,occurred_at DESC);
CREATE TABLE outbox_events (
 id uuid PRIMARY KEY DEFAULT gen_random_uuid(), aggregate_type text NOT NULL, aggregate_id uuid NOT NULL,
 event_type text NOT NULL, payload jsonb NOT NULL, created_at timestamptz NOT NULL DEFAULT now(),
 delivered_at timestamptz, attempt_count integer NOT NULL DEFAULT 0 CHECK(attempt_count >= 0)
);
CREATE INDEX idx_outbox_pending ON outbox_events(created_at) WHERE delivered_at IS NULL;
