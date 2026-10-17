# V3__capacity_ledger_and_state_history.sql

> Markdown reference copy. Canonical executable source: `migrations/V3__capacity_ledger_and_state_history.sql`. Not validated against PostgreSQL.

```sql
-- D2 v0.3: immutable capacity movements and state transition history.
-- Requires V1 and V2. Proposed migration; validate against PostgreSQL before deployment.
CREATE TABLE capacity_movements (
 id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
 budget_id uuid NOT NULL REFERENCES capacity_budgets(id),
 allocation_id uuid REFERENCES capacity_allocations(id),
 operation_id uuid REFERENCES operations(id),
 attempt_id uuid REFERENCES execution_attempts(id),
 movement_type text NOT NULL CHECK (movement_type IN ('RESERVE','RELEASE','CONSUME','ADJUST','BORROW','RETURN')),
 source_pool text CHECK (source_pool IN ('PLANNED','INCIDENT','UNCERTAINTY')),
 target_pool text CHECK (target_pool IN ('PLANNED','INCIDENT','UNCERTAINTY')),
 units numeric(18,4) NOT NULL CHECK (units > 0),
 measurement text NOT NULL CHECK (measurement IN ('ESTIMATED','REPORTED','RECONCILED')),
 confidence numeric(4,3) CHECK (confidence BETWEEN 0 AND 1),
 reason text NOT NULL,
 correlation_key text NOT NULL UNIQUE,
 recorded_at timestamptz NOT NULL DEFAULT now(),
 CHECK (
   (movement_type IN ('BORROW','RETURN') AND source_pool IS NOT NULL AND target_pool IS NOT NULL AND source_pool <> target_pool)
   OR (movement_type NOT IN ('BORROW','RETURN') AND source_pool IS NOT NULL AND target_pool IS NULL)
 )
);
CREATE INDEX idx_capacity_movements_budget_time ON capacity_movements(budget_id, recorded_at, id);
CREATE INDEX idx_capacity_movements_operation ON capacity_movements(operation_id) WHERE operation_id IS NOT NULL;
CREATE TABLE capacity_measurements (
 id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
 resource_id uuid NOT NULL REFERENCES resources(id),
 attempt_id uuid REFERENCES execution_attempts(id),
 observed_at timestamptz NOT NULL DEFAULT now(),
 metric text NOT NULL CHECK (metric IN ('INPUT_TOKENS','OUTPUT_TOKENS','DURATION_MS','QUOTA_USED_PCT','QUOTA_REMAINING_PCT','OPERATIONS')),
 value numeric(20,5) NOT NULL CHECK (value >= 0),
 provenance text NOT NULL CHECK (provenance IN ('PROVIDER','CLI','LOCAL_METER','ESTIMATE','MANUAL')),
 window_start timestamptz, window_end timestamptz,
 confidence numeric(4,3) CHECK (confidence BETWEEN 0 AND 1),
 CHECK (window_end IS NULL OR (window_start IS NOT NULL AND window_end > window_start))
);
CREATE INDEX idx_capacity_measurements_resource ON capacity_measurements(resource_id, observed_at DESC);
CREATE TABLE state_transition_rules (
 entity_type text NOT NULL CHECK (entity_type IN ('TASK','OPERATION','INCIDENT','CAPABILITY_VERSION')),
 from_state text NOT NULL,
 to_state text NOT NULL,
 requires_guard text,
 PRIMARY KEY(entity_type, from_state, to_state),
 CHECK(from_state <> to_state)
);
CREATE TABLE state_transition_events (
 id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
 entity_type text NOT NULL CHECK (entity_type IN ('TASK','OPERATION','INCIDENT','CAPABILITY_VERSION')),
 entity_id uuid NOT NULL,
 from_state text NOT NULL,
 to_state text NOT NULL,
 actor text NOT NULL,
 reason text NOT NULL,
 policy_snapshot_sha256 char(64),
 attempt_id uuid REFERENCES execution_attempts(id),
 occurred_at timestamptz NOT NULL DEFAULT now(),
 FOREIGN KEY(entity_type, from_state, to_state)
  REFERENCES state_transition_rules(entity_type, from_state, to_state)
);
CREATE INDEX idx_transition_events_entity ON state_transition_events(entity_type, entity_id, occurred_at DESC);
-- Transition enforcement requires an application service and/or entity-specific DB triggers.
-- Do not use UPDATE/DELETE for ledger and history rows; restrict DB roles accordingly.
-- Validate budget/allocation/operation/resource ownership and reserve balances in a
-- single transaction with SELECT FOR UPDATE on capacity_budgets; cross-table CHECK
-- constraints cannot enforce these invariants.
```
