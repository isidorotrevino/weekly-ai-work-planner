-- D2 provenance, optimistic sync and at-least-once delivery acknowledgement.
-- These functions do not call Drive/Plane or an external system.
CREATE TABLE d2.budget_accounts(
 budget_id uuid NOT NULL,planning_run_id uuid NOT NULL,resource_id uuid NOT NULL,account_id uuid NOT NULL,
 estimated_capacity numeric(18,4),confidence numeric(4,3) CHECK(confidence BETWEEN 0 AND 1),calibration_ref text NOT NULL,
 PRIMARY KEY(budget_id,account_id),
 FOREIGN KEY(budget_id,planning_run_id,resource_id) REFERENCES public.capacity_budgets(id,planning_run_id,resource_id),
 FOREIGN KEY(account_id,resource_id) REFERENCES d2.accounts(id,resource_id)
);
CREATE TRIGGER plan_write_lock BEFORE INSERT OR UPDATE OR DELETE ON d2.budget_accounts FOR EACH STATEMENT EXECUTE FUNCTION public.d2_plan_write_lock();
CREATE TRIGGER plan_child_guard BEFORE INSERT OR UPDATE OR DELETE ON d2.budget_accounts FOR EACH ROW EXECUTE FUNCTION public.d2_plan_child_guard();
CREATE TRIGGER no_truncate BEFORE TRUNCATE ON d2.budget_accounts FOR EACH STATEMENT EXECUTE FUNCTION public.d2_reject_fact_mutation();
CREATE TABLE d2.delivery_receipts(
 outbox_id uuid PRIMARY KEY REFERENCES public.outbox_events(id),payload_sha256 char(64) NOT NULL,acknowledged_at timestamptz NOT NULL DEFAULT clock_timestamp()
);
DO $$ DECLARE rel text; BEGIN
 FOREACH rel IN ARRAY ARRAY['d2.delivery_receipts','public.artifacts','public.execution_evidence','public.capacity_observations'] LOOP
  EXECUTE format('CREATE TRIGGER immutable_provenance BEFORE UPDATE OR DELETE OR TRUNCATE ON %s FOR EACH STATEMENT EXECUTE FUNCTION public.d2_reject_fact_mutation()',rel);
 END LOOP;
END $$;
CREATE FUNCTION d2.outbox_fact_guard() RETURNS trigger LANGUAGE plpgsql AS $$
BEGIN
 IF (to_jsonb(NEW)-'delivered_at'-'attempt_count')<>(to_jsonb(OLD)-'delivered_at'-'attempt_count') THEN RAISE EXCEPTION 'Outbox event payload is immutable' USING ERRCODE='55000'; END IF;
 RETURN NEW;
END $$;
CREATE TRIGGER outbox_fact_guard BEFORE UPDATE ON public.outbox_events FOR EACH ROW EXECUTE FUNCTION d2.outbox_fact_guard();
CREATE TRIGGER outbox_no_delete BEFORE DELETE OR TRUNCATE ON public.outbox_events FOR EACH STATEMENT EXECUTE FUNCTION public.d2_reject_fact_mutation();
CREATE FUNCTION d2.ack_outbox(cid uuid,req jsonb) RETURNS jsonb
LANGUAGE plpgsql SECURITY DEFINER SET search_path=pg_catalog,public,d2 AS $$
DECLARE prior jsonb;result jsonb;e public.outbox_events;actual text;
BEGIN
 prior=d2.begin_command(cid,req);IF prior IS NOT NULL THEN RETURN prior;END IF;
 SELECT * INTO STRICT e FROM public.outbox_events WHERE id=(req->>'outbox_id')::uuid FOR UPDATE;
 actual=encode(public.digest(e.payload::text,'sha256'),'hex');
 IF actual IS DISTINCT FROM req->>'payload_sha256' THEN RAISE EXCEPTION 'Delivery payload mismatch' USING ERRCODE='23514'; END IF;
 INSERT INTO d2.delivery_receipts VALUES(e.id,actual,clock_timestamp()) ON CONFLICT DO NOTHING;
 UPDATE public.outbox_events SET delivered_at=coalesce(delivered_at,clock_timestamp()) WHERE id=e.id;
 result=jsonb_build_object('outbox_id',e.id,'acknowledged',true);
 INSERT INTO d2.commands VALUES(cid,req,result,clock_timestamp());RETURN result;
END $$;
CREATE FUNCTION d2.sync_source(cid uuid,req jsonb) RETURNS jsonb
LANGUAGE plpgsql SECURITY DEFINER SET search_path=pg_catalog,public,d2 AS $$
DECLARE prior jsonb;result jsonb;b public.external_bindings;doc public.source_documents;local_hash text;revision uuid;
BEGIN
 prior=d2.begin_command(cid,req);IF prior IS NOT NULL THEN RETURN prior;END IF;
 SELECT * INTO STRICT b FROM public.external_bindings WHERE id=(req->>'binding_id')::uuid FOR UPDATE;
 IF b.internal_type<>'SOURCE_DOCUMENT' THEN RAISE EXCEPTION 'Source binding required' USING ERRCODE='23514'; END IF;
 SELECT * INTO STRICT doc FROM public.source_documents WHERE id=b.internal_id FOR UPDATE;
 SELECT sha256 INTO local_hash FROM public.source_revisions WHERE id=doc.current_revision_id;
 IF b.last_revision IS DISTINCT FROM req->>'expected_external_revision' OR local_hash IS DISTINCT FROM req->>'expected_local_sha256' THEN
  UPDATE public.external_bindings SET sync_state='CONFLICT' WHERE id=b.id;
  result=jsonb_build_object('status','CONFLICT');
 ELSE
  IF req->>'sha256' IS NULL OR req->>'sha256' !~ '^[a-f0-9]{64}$' OR req->>'observed_revision' IS NULL OR req->>'content_ref' IS NULL THEN RAISE EXCEPTION 'Versioned source evidence required' USING ERRCODE='23514';END IF;
  INSERT INTO public.source_revisions(document_id,external_revision,sha256,content_ref) VALUES(doc.id,req->>'observed_revision',req->>'sha256',req->>'content_ref') ON CONFLICT(document_id,sha256) DO NOTHING;
  SELECT id INTO STRICT revision FROM public.source_revisions WHERE document_id=doc.id AND sha256=req->>'sha256';
  UPDATE public.source_documents SET current_revision_id=revision WHERE id=doc.id;
  UPDATE public.external_bindings SET last_revision=req->>'observed_revision',sync_state='SYNCED' WHERE id=b.id;
  result=jsonb_build_object('status','SYNCED','revision_id',revision);
 END IF;
 INSERT INTO d2.commands VALUES(cid,req,result,clock_timestamp());
 INSERT INTO public.outbox_events(aggregate_type,aggregate_id,event_type,payload) VALUES('SOURCE_DOCUMENT',doc.id,'SYNC_RESULT',result);
 RETURN result;
END $$;
REVOKE ALL ON ALL TABLES IN SCHEMA d2 FROM PUBLIC;
REVOKE ALL ON ALL FUNCTIONS IN SCHEMA d2 FROM PUBLIC;

-- Minimal MVP state vocabularies; future domain workflows extend them through
-- reviewed migrations, not arbitrary text from a connector.
ALTER TABLE public.requirements ADD CONSTRAINT ck_requirement_state CHECK(status IN ('DRAFT','READY','APPROVED','REJECTED','ARCHIVED'));
ALTER TABLE public.epics ADD CONSTRAINT ck_epic_state CHECK(status IN ('BACKLOG','READY','IN_PROGRESS','BLOCKED','VERIFYING','DONE','CANCELLED','FAILED','DEFERRED'));
ALTER TABLE public.epics ADD COLUMN row_version bigint NOT NULL DEFAULT 0;
ALTER TABLE public.execution_attempts ADD CONSTRAINT ck_attempt_state CHECK(state IN ('LEASED','RUNNING','VERIFYING','COMPLETED','FAILED','CANCELLED','RECONCILING'));
ALTER TABLE public.schedule_entries ADD CONSTRAINT ck_schedule_state CHECK(state IN ('PLANNED','DEFERRED','CANCELLED'));
-- Direct lineage for Gentle-AI tasks that have no epic or requirement.
CREATE TABLE d2.task_sources(
 task_id uuid NOT NULL,revision_id uuid NOT NULL,source_locator text NOT NULL DEFAULT '',document_id uuid NOT NULL,project_id uuid NOT NULL,
 PRIMARY KEY(task_id,revision_id,source_locator),
 FOREIGN KEY(task_id,project_id) REFERENCES public.tasks(id,project_id),
 FOREIGN KEY(revision_id,document_id) REFERENCES public.source_revisions(id,document_id),
 FOREIGN KEY(document_id,project_id) REFERENCES public.source_documents(id,project_id)
);
CREATE TRIGGER immutable_fact BEFORE UPDATE OR DELETE OR TRUNCATE ON d2.task_sources FOR EACH STATEMENT EXECUTE FUNCTION public.d2_reject_fact_mutation();
REVOKE ALL ON ALL TABLES IN SCHEMA d2 FROM PUBLIC;
