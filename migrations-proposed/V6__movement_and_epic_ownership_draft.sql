-- D2 proposal: relational ownership only; does not implement D2.6 accounts.
-- Requires V1-V5. Run transactionally, under migration-owner privileges.
-- Existing incompatible ownership aborts; never remap an event to another owner.
ALTER TABLE requirements ADD CONSTRAINT uq_requirement_project UNIQUE(id,project_id);
ALTER TABLE epic_requirements ADD COLUMN project_id uuid;
UPDATE epic_requirements er SET project_id=e.project_id FROM epics e WHERE e.id=er.epic_id;
ALTER TABLE epic_requirements ALTER COLUMN project_id SET NOT NULL;
ALTER TABLE epic_requirements ADD CONSTRAINT fk_epic_requirement_epic_project
 FOREIGN KEY(epic_id,project_id) REFERENCES epics(id,project_id);
ALTER TABLE epic_requirements ADD CONSTRAINT fk_epic_requirement_requirement_project
 FOREIGN KEY(requirement_id,project_id) REFERENCES requirements(id,project_id);

ALTER TABLE capacity_budgets ADD CONSTRAINT uq_budget_resource UNIQUE(id,resource_id);
ALTER TABLE capacity_allocations ADD CONSTRAINT uq_allocation_budget_project UNIQUE(id,budget_id,project_id);
ALTER TABLE execution_attempts ADD CONSTRAINT uq_attempt_operation_resource UNIQUE(id,operation_id,resource_id);

ALTER TABLE capacity_movements ADD COLUMN resource_id uuid;
ALTER TABLE capacity_movements ADD COLUMN project_id uuid;
ALTER TABLE capacity_movements ADD COLUMN task_id uuid;
-- V5 forbids UPDATE even for metadata enrichment. Exclusively lock the journal,
-- suspend ONLY its immutable_fact trigger, backfill context, then restore it in
-- this same transaction. Original event fields/keys/ids are not modified.
LOCK TABLE capacity_movements IN ACCESS EXCLUSIVE MODE;
ALTER TABLE capacity_movements DISABLE TRIGGER immutable_fact;
UPDATE capacity_movements m SET resource_id=b.resource_id
 FROM capacity_budgets b WHERE b.id=m.budget_id;
UPDATE capacity_movements m SET task_id=o.task_id, project_id=t.project_id
 FROM operations o JOIN tasks t ON t.id=o.task_id WHERE o.id=m.operation_id;
-- Allocation ownership supplies context only when no operation was provided.
-- If both exist, the FK below detects a disagreement rather than overwriting it.
UPDATE capacity_movements m SET project_id=a.project_id
 FROM capacity_allocations a WHERE a.id=m.allocation_id AND m.operation_id IS NULL;
ALTER TABLE capacity_movements ENABLE TRIGGER immutable_fact;
ALTER TABLE capacity_movements ALTER COLUMN resource_id SET NOT NULL;
ALTER TABLE capacity_movements ADD CONSTRAINT ck_movement_operation_task_pair
 CHECK((operation_id IS NULL AND task_id IS NULL) OR (operation_id IS NOT NULL AND task_id IS NOT NULL));
ALTER TABLE capacity_movements ADD CONSTRAINT ck_movement_project_context
 CHECK((operation_id IS NULL AND allocation_id IS NULL AND project_id IS NULL)
 OR ((operation_id IS NOT NULL OR allocation_id IS NOT NULL) AND project_id IS NOT NULL));
ALTER TABLE capacity_movements ADD CONSTRAINT fk_movement_budget_resource
 FOREIGN KEY(budget_id,resource_id) REFERENCES capacity_budgets(id,resource_id);
ALTER TABLE capacity_movements ADD CONSTRAINT fk_movement_attempt_operation_resource
 FOREIGN KEY(attempt_id,operation_id,resource_id) REFERENCES execution_attempts(id,operation_id,resource_id);
ALTER TABLE capacity_movements ADD CONSTRAINT fk_movement_operation_task
 FOREIGN KEY(operation_id,task_id) REFERENCES operations(id,task_id);
ALTER TABLE capacity_movements ADD CONSTRAINT fk_movement_task_project
 FOREIGN KEY(task_id,project_id) REFERENCES tasks(id,project_id);
ALTER TABLE capacity_movements ADD CONSTRAINT fk_movement_allocation_budget_project
 FOREIGN KEY(allocation_id,budget_id,project_id) REFERENCES capacity_allocations(id,budget_id,project_id);
-- Pool semantics, source ownership, current fencing and capacity balances remain open.
