-- D2 v0.5 PROPOSAL. Only exercised in disposable audit databases.
-- Does not implement scheduler, transition guards, balances or worker protocol.
-- Never rewrite V1-V4: keep their Flyway checksums and imported evidence.

-- Backfill only when a single candidate exists. Never guess a quota window.
DO $$
BEGIN
 IF EXISTS (
  SELECT 1 FROM capacity_allocations a WHERE a.budget_id IS NULL AND
  (SELECT count(*) FROM capacity_budgets b WHERE b.planning_run_id=a.planning_run_id
   AND b.resource_id=a.resource_id) <> 1
 ) THEN
  RAISE EXCEPTION 'Allocation budget backfill is ambiguous or missing; explicit mapping required';
 END IF;
END $$;
UPDATE capacity_allocations a SET budget_id=b.id FROM capacity_budgets b
 WHERE a.budget_id IS NULL AND b.planning_run_id=a.planning_run_id AND b.resource_id=a.resource_id;
ALTER TABLE capacity_allocations VALIDATE CONSTRAINT fk_allocation_budget_same_run_resource;
ALTER TABLE capacity_allocations ALTER COLUMN budget_id SET NOT NULL;

-- One allocation per physical budget, project and pool; allow multiple windows.
DO $$
DECLARE constraint_name text;
BEGIN
 SELECT c.conname INTO STRICT constraint_name FROM pg_constraint c
 WHERE c.conrelid='capacity_allocations'::regclass AND c.contype='u'
 AND c.conkey=ARRAY[
  (SELECT attnum FROM pg_attribute WHERE attrelid=c.conrelid AND attname='planning_run_id'),
  (SELECT attnum FROM pg_attribute WHERE attrelid=c.conrelid AND attname='resource_id'),
  (SELECT attnum FROM pg_attribute WHERE attrelid=c.conrelid AND attname='project_id'),
  (SELECT attnum FROM pg_attribute WHERE attrelid=c.conrelid AND attname='pool')
 ]::smallint[];
 EXECUTE format('ALTER TABLE capacity_allocations DROP CONSTRAINT %I',constraint_name);
END $$;
ALTER TABLE capacity_allocations ADD CONSTRAINT uq_allocation_budget_project_pool UNIQUE(budget_id,project_id,pool);
ALTER TABLE capacity_allocations ADD CONSTRAINT uq_allocation_budget_identity UNIQUE(id,budget_id);
ALTER TABLE capacity_movements ADD CONSTRAINT fk_movement_allocation_budget
 FOREIGN KEY(allocation_id,budget_id) REFERENCES capacity_allocations(id,budget_id);

ALTER TABLE execution_attempts ADD CONSTRAINT uq_attempt_fencing_identity
 UNIQUE(id,operation_id,worker_id,lease_generation);
ALTER TABLE execution_attempts ADD CONSTRAINT uq_attempt_operation_generation UNIQUE(operation_id,lease_generation);
ALTER TABLE execution_attempts ADD CONSTRAINT uq_attempt_resource UNIQUE(id,resource_id);
ALTER TABLE execution_attempts ADD CONSTRAINT ck_attempt_time CHECK(finished_at IS NULL OR (started_at IS NOT NULL AND finished_at>=started_at));
ALTER TABLE operation_leases ADD CONSTRAINT ck_lease_generation_positive CHECK(fencing_generation>0);
ALTER TABLE operation_leases ADD CONSTRAINT fk_lease_attempt_fence
 FOREIGN KEY(attempt_id,operation_id,worker_id,fencing_generation)
 REFERENCES execution_attempts(id,operation_id,worker_id,lease_generation);
ALTER TABLE capacity_movements ADD CONSTRAINT ck_movement_attempt_has_operation CHECK(attempt_id IS NULL OR operation_id IS NOT NULL);
ALTER TABLE capacity_movements ADD CONSTRAINT fk_movement_attempt_operation
 FOREIGN KEY(attempt_id,operation_id) REFERENCES execution_attempts(id,operation_id);
ALTER TABLE capacity_measurements ADD CONSTRAINT fk_measurement_attempt_resource
 FOREIGN KEY(attempt_id,resource_id) REFERENCES execution_attempts(id,resource_id);
ALTER TABLE capacity_measurements ADD CONSTRAINT ck_measurement_percentage
 CHECK(metric NOT IN ('QUOTA_USED_PCT','QUOTA_REMAINING_PCT') OR value<=100);
ALTER TABLE capacity_measurements ADD CONSTRAINT ck_measurement_window_pair
 CHECK((window_start IS NULL AND window_end IS NULL) OR
 (window_start IS NOT NULL AND window_end IS NOT NULL AND window_end>window_start));
ALTER TABLE capacity_observations ADD CONSTRAINT ck_observation_window_pair
 CHECK((window_start IS NULL AND window_end IS NULL) OR
 (window_start IS NOT NULL AND window_end IS NOT NULL AND window_end>window_start));

ALTER TABLE operations ADD CONSTRAINT uq_operation_task UNIQUE(id,task_id);
ALTER TABLE schedule_entries ADD CONSTRAINT fk_schedule_operation_task
 FOREIGN KEY(operation_id,task_id) REFERENCES operations(id,task_id);
ALTER TABLE schedule_entries ADD CONSTRAINT ck_schedule_slot
 CHECK((planned_start IS NULL AND planned_end IS NULL) OR
 (planned_start IS NOT NULL AND planned_end IS NOT NULL AND planned_end>planned_start));
ALTER TABLE incidents ADD COLUMN row_version bigint NOT NULL DEFAULT 0;
ALTER TABLE incidents ADD CONSTRAINT ck_incident_resolution
 CHECK((status='RESOLVED' AND resolved_at IS NOT NULL AND resolved_at>=detected_at)
 OR (status<>'RESOLVED' AND resolved_at IS NULL));

-- Freeze facts, not operational projections. No approval expiry default: legacy
-- approvals must be explicitly rebound, otherwise this migration fails safely.
ALTER TABLE approvals ADD COLUMN expires_at timestamptz;
ALTER TABLE approvals ADD COLUMN context_snapshot_sha256 char(64);
ALTER TABLE approvals ADD COLUMN policy_snapshot_sha256 char(64);
ALTER TABLE approvals ADD CONSTRAINT ck_approval_decision
 CHECK((state IN ('APPROVED','REJECTED') AND decided_at IS NOT NULL AND decided_by IS NOT NULL)
 OR state IN ('PENDING','EXPIRED'));
ALTER TABLE approvals ADD CONSTRAINT ck_approved_snapshot
 CHECK(state<>'APPROVED' OR
 (expires_at IS NOT NULL AND expires_at>decided_at AND decided_at>=requested_at
 AND context_snapshot_sha256 IS NOT NULL AND policy_snapshot_sha256 IS NOT NULL));

CREATE FUNCTION d2_reject_fact_mutation() RETURNS trigger LANGUAGE plpgsql AS $$
BEGIN RAISE EXCEPTION 'Append-only relation %: % forbidden', TG_TABLE_NAME, TG_OP USING ERRCODE='55000'; END $$;
DO $$
DECLARE relation_name text;
BEGIN
 FOREACH relation_name IN ARRAY ARRAY['source_revisions','capability_evidence','capacity_movements',
  'capacity_measurements','state_transition_events','project_priority_history','audit_events','task_deferrals']
 LOOP
  EXECUTE format('CREATE TRIGGER immutable_fact BEFORE UPDATE OR DELETE OR TRUNCATE ON %I FOR EACH STATEMENT EXECUTE FUNCTION d2_reject_fact_mutation()',relation_name);
 END LOOP;
END $$;
-- DB owner can change DDL. Restricted application roles still required.
-- Remaining cross-entity state/lease/balance/DAG guards are specified in D2.5.
