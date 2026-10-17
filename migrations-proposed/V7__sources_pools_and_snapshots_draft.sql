-- Proposed D2 hardening. No deployment authorization. Transactional migration.
ALTER TABLE project_dependencies ADD COLUMN kind text NOT NULL DEFAULT 'HARD' CHECK(kind IN ('HARD','SOFT','MOCKABLE','OPTIONAL'));
ALTER TABLE source_documents ADD CONSTRAINT uq_source_document_project UNIQUE(id,project_id);
ALTER TABLE requirement_sources ADD COLUMN document_id uuid;
ALTER TABLE requirement_sources ADD COLUMN project_id uuid;
UPDATE requirement_sources s SET document_id=v.document_id,project_id=r.project_id
 FROM source_revisions v,requirements r WHERE v.id=s.revision_id AND r.id=s.requirement_id;
ALTER TABLE requirement_sources ALTER COLUMN document_id SET NOT NULL;
ALTER TABLE requirement_sources ALTER COLUMN project_id SET NOT NULL;
ALTER TABLE requirement_sources ADD CONSTRAINT fk_req_source_revision_document FOREIGN KEY(revision_id,document_id) REFERENCES source_revisions(id,document_id);
ALTER TABLE requirement_sources ADD CONSTRAINT fk_req_source_document_project FOREIGN KEY(document_id,project_id) REFERENCES source_documents(id,project_id);
ALTER TABLE requirement_sources ADD CONSTRAINT fk_req_source_requirement_project FOREIGN KEY(requirement_id,project_id) REFERENCES requirements(id,project_id);
ALTER TABLE capacity_allocations ADD CONSTRAINT uq_allocation_pool UNIQUE(id,budget_id,pool);
ALTER TABLE capacity_movements ADD CONSTRAINT ck_transfer_scope CHECK(movement_type NOT IN ('BORROW','RETURN') OR allocation_id IS NULL);
ALTER TABLE capacity_movements ADD CONSTRAINT ck_transfer_direction CHECK(
 movement_type NOT IN ('BORROW','RETURN') OR
 (movement_type='BORROW' AND source_pool='INCIDENT' AND target_pool='PLANNED') OR
 (movement_type='RETURN' AND source_pool='PLANNED' AND target_pool='INCIDENT'));
ALTER TABLE capacity_movements ADD CONSTRAINT fk_movement_allocation_pool FOREIGN KEY(allocation_id,budget_id,source_pool) REFERENCES capacity_allocations(id,budget_id,pool);
-- External namespaces cannot be guessed from legacy polymorphic rows.
ALTER TABLE external_bindings ADD COLUMN external_namespace text;
DO $$ BEGIN
 IF EXISTS(SELECT 1 FROM external_bindings) THEN
  RAISE EXCEPTION 'External namespace mapping required before V7; no namespace will be invented';
 END IF;
END $$;
ALTER TABLE external_bindings ALTER COLUMN external_namespace SET NOT NULL;
ALTER TABLE external_bindings ADD CONSTRAINT ck_external_namespace CHECK(length(btrim(external_namespace))>0);
DO $$
DECLARE c record; cols text[];
BEGIN
 FOR c IN SELECT conname,conkey FROM pg_constraint WHERE conrelid='external_bindings'::regclass AND contype='u' LOOP
  SELECT array_agg(attname::text ORDER BY ord) INTO cols FROM unnest(c.conkey) WITH ORDINALITY k(attnum,ord)
  JOIN pg_attribute a ON a.attrelid='external_bindings'::regclass AND a.attnum=k.attnum;
  IF cols=ARRAY['provider','external_type','external_id'] OR cols=ARRAY['provider','internal_type','internal_id','external_type'] THEN
   EXECUTE format('ALTER TABLE external_bindings DROP CONSTRAINT %I',c.conname);
  END IF;
 END LOOP;
END $$;
ALTER TABLE external_bindings ADD CONSTRAINT uq_external_namespace UNIQUE(provider,external_namespace,external_type,external_id);
ALTER TABLE external_bindings ADD CONSTRAINT uq_internal_namespace UNIQUE(provider,external_namespace,internal_type,internal_id,external_type);
ALTER TABLE external_bindings ADD CONSTRAINT ck_binding_type CHECK(internal_type IN ('PROJECT','TASK','REQUIREMENT','EPIC','OPERATION','INCIDENT','CAPABILITY','SOURCE_DOCUMENT'));
DO $$
DECLARE item record;
BEGIN
 FOR item IN SELECT * FROM (VALUES('PROJECT','projects'),('TASK','tasks'),('REQUIREMENT','requirements'),('EPIC','epics'),('OPERATION','operations'),('INCIDENT','incidents'),('CAPABILITY','capabilities'),('SOURCE_DOCUMENT','source_documents')) v(kind,relation_name) LOOP
  EXECUTE format('ALTER TABLE external_bindings ADD COLUMN %I uuid GENERATED ALWAYS AS (CASE WHEN internal_type=%L THEN internal_id END) STORED REFERENCES %I(id)',lower(item.kind)||'_target',item.kind,item.relation_name);
 END LOOP;
END $$;
ALTER TABLE planning_runs ADD COLUMN superseded_by uuid REFERENCES planning_runs(id);
ALTER TABLE planning_runs ADD CONSTRAINT ck_plan_successor CHECK((status='SUPERSEDED' AND superseded_by IS NOT NULL AND superseded_by<>id) OR (status<>'SUPERSEDED' AND superseded_by IS NULL));
CREATE FUNCTION d2_plan_guard() RETURNS trigger LANGUAGE plpgsql AS $$
BEGIN
 PERFORM pg_advisory_xact_lock(742001);
 IF TG_OP='INSERT' THEN
  IF NEW.status<>'DRAFT' THEN RAISE EXCEPTION 'Plan must start DRAFT' USING ERRCODE='23514'; END IF;
  RETURN NEW;
 END IF;
 IF OLD.status IN ('PUBLISHED','SUPERSEDED') THEN
  IF TG_OP='UPDATE' AND NEW IS NOT DISTINCT FROM OLD THEN RETURN NEW; END IF;
  IF TG_OP='UPDATE' AND OLD.status='PUBLISHED' AND NEW.status='SUPERSEDED'
   AND (to_jsonb(NEW)-'status'-'superseded_by')=(to_jsonb(OLD)-'status'-'superseded_by')
   AND EXISTS(SELECT 1 FROM planning_runs WHERE id=NEW.superseded_by AND status='PUBLISHED') THEN RETURN NEW; END IF;
  RAISE EXCEPTION 'Published plan is immutable; only explicit supersession allowed' USING ERRCODE='55000';
 END IF;
 IF TG_OP='DELETE' THEN RETURN OLD; END IF;
 RETURN NEW;
END $$;
CREATE TRIGGER plan_guard BEFORE INSERT OR UPDATE OR DELETE ON planning_runs FOR EACH ROW EXECUTE FUNCTION d2_plan_guard();
CREATE TRIGGER plan_no_truncate BEFORE TRUNCATE ON planning_runs FOR EACH STATEMENT EXECUTE FUNCTION d2_reject_fact_mutation();
CREATE FUNCTION d2_plan_child_guard() RETURNS trigger LANGUAGE plpgsql AS $$
DECLARE ids uuid[]; pid uuid; current_status text;
BEGIN
 PERFORM pg_advisory_xact_lock(742001);
 IF TG_OP='INSERT' THEN ids=ARRAY[NEW.planning_run_id];
 ELSIF TG_OP='DELETE' THEN ids=ARRAY[OLD.planning_run_id];
 ELSE ids=ARRAY[OLD.planning_run_id,NEW.planning_run_id]; END IF;
 FOR pid IN SELECT DISTINCT unnest(ids) ORDER BY 1 LOOP
  SELECT status INTO current_status FROM planning_runs WHERE id=pid FOR UPDATE;
  IF current_status IS DISTINCT FROM 'DRAFT' THEN RAISE EXCEPTION 'Plan children require DRAFT parent' USING ERRCODE='55000'; END IF;
 END LOOP;
 IF TG_OP='DELETE' THEN RETURN OLD; END IF;
 RETURN NEW;
END $$;
DO $$ DECLARE rel text; BEGIN
 FOREACH rel IN ARRAY ARRAY['capacity_budgets','capacity_allocations','schedule_entries','task_deferrals'] LOOP
  EXECUTE format('CREATE TRIGGER plan_child_guard BEFORE INSERT OR UPDATE OR DELETE ON %I FOR EACH ROW EXECUTE FUNCTION d2_plan_child_guard()',rel);
  EXECUTE format('CREATE TRIGGER plan_child_no_truncate BEFORE TRUNCATE ON %I FOR EACH STATEMENT EXECUTE FUNCTION d2_reject_fact_mutation()',rel);
 END LOOP;
END $$;

-- Acquire the publication mutex before the outer statement takes parent/child
-- row locks. Row-trigger-only locking can invert lock order under concurrency.
CREATE FUNCTION d2_plan_write_lock() RETURNS trigger LANGUAGE plpgsql AS $$
BEGIN PERFORM pg_advisory_xact_lock(742001);RETURN NULL;END $$;
DO $$ DECLARE rel text;BEGIN
 FOREACH rel IN ARRAY ARRAY['planning_runs','capacity_budgets','capacity_allocations','schedule_entries','task_deferrals'] LOOP
  EXECUTE format('CREATE TRIGGER plan_write_lock BEFORE INSERT OR UPDATE OR DELETE ON public.%I FOR EACH STATEMENT EXECUTE FUNCTION d2_plan_write_lock()',rel);
 END LOOP;
END $$;
