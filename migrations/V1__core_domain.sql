-- Weekly AI Work Planner / PostgreSQL 16+ / Flyway V1
CREATE EXTENSION IF NOT EXISTS pgcrypto;

CREATE TABLE projects (
 id uuid PRIMARY KEY DEFAULT gen_random_uuid(), code text NOT NULL UNIQUE, name text NOT NULL,
 workflow_type text NOT NULL CHECK (workflow_type IN ('GENTLE_AI','DRIVE_PLANE','HYBRID')),
 status text NOT NULL DEFAULT 'ACTIVE' CHECK (status IN ('ACTIVE','PAUSED','ARCHIVED')),
 priority text NOT NULL DEFAULT 'P2' CHECK (priority IN ('P0','P1','P2','P3','P4')),
 priority_weight_override numeric(10,3) CHECK (priority_weight_override >= 0),
 deferral_allowed boolean NOT NULL DEFAULT true, row_version bigint NOT NULL DEFAULT 0,
 created_at timestamptz NOT NULL DEFAULT now(), updated_at timestamptz NOT NULL DEFAULT now()
);
CREATE TABLE project_priority_history (
 id uuid PRIMARY KEY DEFAULT gen_random_uuid(), project_id uuid NOT NULL REFERENCES projects(id),
 priority text NOT NULL CHECK (priority IN ('P0','P1','P2','P3','P4')),
 effective_at timestamptz NOT NULL DEFAULT now(), reason text, actor text NOT NULL
);
CREATE INDEX idx_priority_history_project ON project_priority_history(project_id,effective_at DESC);
CREATE TABLE project_dependencies (
 id uuid PRIMARY KEY DEFAULT gen_random_uuid(), provider_project_id uuid NOT NULL REFERENCES projects(id),
 consumer_project_id uuid NOT NULL REFERENCES projects(id), description text,
 CHECK (provider_project_id <> consumer_project_id), UNIQUE(provider_project_id,consumer_project_id)
);
CREATE TABLE source_documents (
 id uuid PRIMARY KEY DEFAULT gen_random_uuid(), project_id uuid NOT NULL REFERENCES projects(id),
 source_type text NOT NULL CHECK (source_type IN ('GENTLE_AI','GOOGLE_DRIVE','PLANE','OTHER')),
 source_uri text NOT NULL, current_revision_id uuid, created_at timestamptz NOT NULL DEFAULT now(),
 UNIQUE(source_type,source_uri)
);
CREATE TABLE source_revisions (
 id uuid PRIMARY KEY DEFAULT gen_random_uuid(), document_id uuid NOT NULL REFERENCES source_documents(id),
 external_revision text, sha256 char(64) NOT NULL, content_ref text NOT NULL,
 observed_at timestamptz NOT NULL DEFAULT now(), UNIQUE(document_id,sha256),
 UNIQUE(id,document_id)
);
ALTER TABLE source_documents ADD CONSTRAINT fk_current_revision_same_document
 FOREIGN KEY (current_revision_id,id) REFERENCES source_revisions(id,document_id) DEFERRABLE INITIALLY DEFERRED;
CREATE TABLE requirements (
 id uuid PRIMARY KEY DEFAULT gen_random_uuid(), project_id uuid NOT NULL REFERENCES projects(id),
 requirement_key text NOT NULL, title text NOT NULL, description text,
 status text NOT NULL DEFAULT 'DRAFT', row_version bigint NOT NULL DEFAULT 0,
 UNIQUE(project_id,requirement_key)
);
CREATE TABLE requirement_sources (
 requirement_id uuid NOT NULL REFERENCES requirements(id), revision_id uuid NOT NULL REFERENCES source_revisions(id),
 source_locator text NOT NULL DEFAULT '', PRIMARY KEY(requirement_id,revision_id,source_locator)
);
CREATE TABLE epics (
 id uuid PRIMARY KEY DEFAULT gen_random_uuid(), project_id uuid NOT NULL REFERENCES projects(id),
 epic_key text NOT NULL, title text NOT NULL, status text NOT NULL DEFAULT 'BACKLOG',
 UNIQUE(project_id,epic_key), UNIQUE(id,project_id)
);
CREATE TABLE epic_requirements (
 epic_id uuid NOT NULL REFERENCES epics(id), requirement_id uuid NOT NULL REFERENCES requirements(id),
 PRIMARY KEY(epic_id,requirement_id)
);
CREATE TABLE tasks (
 id uuid PRIMARY KEY DEFAULT gen_random_uuid(), project_id uuid NOT NULL REFERENCES projects(id),
 epic_id uuid, task_key text NOT NULL, title text NOT NULL, description text,
 status text NOT NULL DEFAULT 'BACKLOG' CHECK(status IN ('BACKLOG','READY','BLOCKED','IN_PROGRESS','VERIFYING','DONE','DEFERRED','FAILED','CANCELLED')),
 urgency smallint NOT NULL DEFAULT 0 CHECK(urgency BETWEEN 0 AND 5),
 deadline_at timestamptz, deferred_count integer NOT NULL DEFAULT 0 CHECK(deferred_count >= 0),
 row_version bigint NOT NULL DEFAULT 0, created_at timestamptz NOT NULL DEFAULT now(),
 UNIQUE(project_id,task_key), UNIQUE(id,project_id),
 FOREIGN KEY(epic_id,project_id) REFERENCES epics(id,project_id)
);
CREATE INDEX idx_tasks_ready ON tasks(project_id,status,urgency DESC) WHERE status IN ('READY','BLOCKED');
CREATE TABLE task_dependencies (
 id uuid PRIMARY KEY DEFAULT gen_random_uuid(), predecessor_task_id uuid NOT NULL REFERENCES tasks(id),
 successor_task_id uuid NOT NULL REFERENCES tasks(id),
 kind text NOT NULL CHECK(kind IN ('HARD','SOFT','MOCKABLE','OPTIONAL')),
 CHECK(predecessor_task_id <> successor_task_id), UNIQUE(predecessor_task_id,successor_task_id)
);
CREATE INDEX idx_task_dep_successor ON task_dependencies(successor_task_id);
CREATE TABLE capabilities (
 id uuid PRIMARY KEY DEFAULT gen_random_uuid(), provider_project_id uuid NOT NULL REFERENCES projects(id),
 capability_key text NOT NULL, description text, UNIQUE(provider_project_id,capability_key)
);
CREATE TABLE capability_versions (
 id uuid PRIMARY KEY DEFAULT gen_random_uuid(), capability_id uuid NOT NULL REFERENCES capabilities(id),
 version text NOT NULL, environment text NOT NULL,
 state text NOT NULL DEFAULT 'PLANNED' CHECK(state IN ('PLANNED','IMPLEMENTED','VERIFIED','AVAILABLE','INVALIDATED')),
 contract_sha256 char(64), contract_ref text, row_version bigint NOT NULL DEFAULT 0,
 UNIQUE(capability_id,version,environment)
);
CREATE TABLE capability_evidence (
 id uuid PRIMARY KEY DEFAULT gen_random_uuid(), capability_version_id uuid NOT NULL REFERENCES capability_versions(id),
 evidence_type text NOT NULL, artifact_ref text NOT NULL, verified_at timestamptz NOT NULL DEFAULT now(),
 outcome text NOT NULL CHECK(outcome IN ('PASS','FAIL'))
);
CREATE TABLE capability_requirements (
 id uuid PRIMARY KEY DEFAULT gen_random_uuid(), consumer_task_id uuid NOT NULL REFERENCES tasks(id),
 capability_id uuid NOT NULL REFERENCES capabilities(id), version_constraint text NOT NULL,
 environment text NOT NULL, kind text NOT NULL CHECK(kind IN ('HARD','SOFT','MOCKABLE','OPTIONAL')),
 UNIQUE(consumer_task_id,capability_id,environment)
);
CREATE TABLE external_bindings (
 id uuid PRIMARY KEY DEFAULT gen_random_uuid(), provider text NOT NULL,
 external_type text NOT NULL, external_id text NOT NULL,
 internal_type text NOT NULL, internal_id uuid NOT NULL,
 last_revision text, sync_state text NOT NULL DEFAULT 'SYNCED',
 UNIQUE(provider,external_type,external_id), UNIQUE(provider,internal_type,internal_id,external_type)
);
-- internal_type/internal_id is a polymorphic reference; validate target existence in application services.
