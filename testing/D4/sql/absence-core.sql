-- SPDX-License-Identifier: GPL-3.0-only
-- A20: independently sealed absence, explicit retry, original TOP_UP.
CREATE TABLE d4.absence_seals(id uuid PRIMARY KEY,proof_id uuid NOT NULL UNIQUE REFERENCES d4.recovery_proofs(id),delivery_id uuid NOT NULL REFERENCES d4.deliveries(id),operation_id uuid NOT NULL REFERENCES public.operations(id),generation bigint NOT NULL,attempt_id uuid NOT NULL REFERENCES public.execution_attempts(id),reservation_id uuid NOT NULL REFERENCES d2.reservations(id),committed_version bigint NOT NULL,UNIQUE(operation_id,generation));
CREATE TABLE d4.absence_authorizations(id uuid PRIMARY KEY,seal_id uuid NOT NULL REFERENCES d4.absence_seals(id),authorized_version bigint NOT NULL,reason text NOT NULL);
CREATE TABLE d4.absence_links(seal_id uuid PRIMARY KEY REFERENCES d4.absence_seals(id),authorization_id uuid NOT NULL REFERENCES d4.absence_authorizations(id),attempt_id uuid NOT NULL UNIQUE REFERENCES public.execution_attempts(id),generation bigint NOT NULL);

DO $$ DECLARE t text;BEGIN FOREACH t IN ARRAY ARRAY['absence_seals','absence_authorizations','absence_links'] LOOP EXECUTE format('CREATE TRIGGER immutable_fact BEFORE UPDATE OR DELETE OR TRUNCATE ON d4.%I FOR EACH STATEMENT EXECUTE FUNCTION public.d2_reject_fact_mutation()',t);END LOOP;END $$;

CREATE FUNCTION d4.absence_safe(oid uuid,gen bigint) RETURNS boolean LANGUAGE sql STABLE SECURITY DEFINER SET search_path=pg_catalog,public,d4 AS $$
 SELECT EXISTS(SELECT 1 FROM d4.absence_seals s JOIN d4.absence_authorizations a ON a.seal_id=s.id JOIN public.operations o ON o.id=s.operation_id WHERE s.operation_id=oid AND s.generation=gen AND o.lease_generation=gen AND o.state='READY' AND o.row_version=a.authorized_version AND d4.recovery_current(s.id) AND NOT EXISTS(SELECT 1 FROM d4.absence_links WHERE seal_id=s.id));
$$;

CREATE FUNCTION d4.absence_authorize(cid uuid,seal uuid,expected_version bigint,reason text) RETURNS jsonb LANGUAGE plpgsql SECURITY DEFINER SET search_path=pg_catalog,public,d2,d3,d4 AS $$
DECLARE req jsonb=jsonb_build_object('action','ABSENCE_AUTHORIZE','seal',seal,'version',expected_version,'reason',reason);prior jsonb;s d4.absence_seals;o public.operations;result jsonb;
BEGIN
 PERFORM d3.lock_state();prior=d4.checkpoint_previous(cid,req);IF prior IS NOT NULL THEN RETURN prior;END IF;SELECT * INTO STRICT s FROM d4.absence_seals WHERE id=seal;SELECT * INTO STRICT o FROM public.operations WHERE id=s.operation_id;
 IF o.state NOT IN ('RETRY_PENDING','READY') OR o.row_version IS DISTINCT FROM expected_version OR o.lease_generation<>s.generation OR NOT d4.recovery_current(s.id) OR EXISTS(SELECT 1 FROM d4.absence_links WHERE seal_id=seal) OR (SELECT count(*) FROM public.execution_attempts WHERE operation_id=o.id)>=coalesce((o.policy_snapshot->>'max_attempts')::int,3) OR reason IS NULL OR length(btrim(reason)) NOT BETWEEN 1 AND 512 THEN RAISE EXCEPTION 'Current unused absence, authorization and budget required' USING ERRCODE='23514';END IF;
 UPDATE public.operations SET state='READY',row_version=row_version+1 WHERE id=o.id;IF o.state<>'READY' THEN PERFORM d2.record_transition(cid,'OPERATION',o.id,o.state,'READY',o.row_version+1,'CONTROL_PLANE','Explicit absence retry');END IF;
 INSERT INTO d4.absence_authorizations VALUES(cid,seal,o.row_version+1,reason);result=jsonb_build_object('state','READY','row_version',o.row_version+1);INSERT INTO d4.checkpoint_commands VALUES(cid,req,result);RETURN result;
END $$;

CREATE FUNCTION d4.parent_linked(oid uuid,parent uuid,attempt uuid,gen bigint) RETURNS boolean LANGUAGE sql STABLE SECURITY DEFINER SET search_path=pg_catalog,public,d4 AS $$
 WITH RECURSIVE lineage(a,g) AS(SELECT attempt,gen UNION ALL SELECT s.attempt_id,s.generation FROM lineage x JOIN d4.absence_links l ON l.attempt_id=x.a AND l.generation=x.g JOIN d4.absence_seals s ON s.id=l.seal_id WHERE s.operation_id=oid AND s.generation+1=x.g)
 SELECT CASE WHEN parent IS NULL THEN EXISTS(SELECT 1 FROM lineage x JOIN public.execution_attempts a ON a.id=x.a WHERE a.operation_id=oid AND a.attempt_no=1 AND x.g=1) ELSE EXISTS(SELECT 1 FROM lineage x JOIN d4.multi_links l ON l.attempt_id=x.a AND l.generation=x.g JOIN d4.multi_checkpoints cp ON cp.id=l.checkpoint_id WHERE cp.id=parent AND cp.operation_id=oid AND cp.source_generation+1=x.g) END;
$$;

ALTER FUNCTION d4.continuation_safe(uuid,bigint) RENAME TO continuation_safe_before_absence;
CREATE FUNCTION d4.continuation_safe(oid uuid,gen bigint) RETURNS boolean LANGUAGE sql STABLE SECURITY DEFINER SET search_path=pg_catalog,public,d4 AS $$ SELECT d4.continuation_safe_before_absence(oid,gen) OR d4.absence_safe(oid,gen); $$;
ALTER VIEW d4.continuation_admissions RENAME TO checkpoint_admissions_before_absence;
CREATE VIEW d4.continuation_admissions AS SELECT * FROM d4.checkpoint_admissions_before_absence UNION ALL SELECT s.operation_id,s.generation,s.id,a.id,p.proof->>'recovery_manifest_hash','SEALED_ABSENCE',d4.absence_safe(s.operation_id,s.generation) AND a.authorized_version=(SELECT row_version FROM public.operations WHERE id=s.operation_id) FROM d4.absence_seals s JOIN d4.absence_authorizations a ON a.seal_id=s.id JOIN d4.recovery_proofs p ON p.id=s.proof_id;
ALTER FUNCTION d3.state_relations() RENAME TO state_relations_before_absence;
CREATE FUNCTION d3.state_relations() RETURNS text[] LANGUAGE sql IMMUTABLE AS $$ SELECT d3.state_relations_before_absence()||ARRAY['d4.absence_seals','d4.absence_authorizations','d4.absence_links']; $$;
CREATE FUNCTION d4.absence_audit() RETURNS jsonb LANGUAGE sql SECURITY DEFINER SET search_path=pg_catalog,public,d4 AS $$ SELECT d4.recovery_audit()||jsonb_build_object('absence_seals',(SELECT coalesce(jsonb_agg(to_jsonb(t)),'[]') FROM d4.absence_seals t),'absence_authorizations',(SELECT coalesce(jsonb_agg(to_jsonb(t)),'[]') FROM d4.absence_authorizations t),'absence_links',(SELECT coalesce(jsonb_agg(to_jsonb(t)),'[]') FROM d4.absence_links t)); $$;

CREATE FUNCTION d4.absence_info(delivery uuid) RETURNS jsonb LANGUAGE sql SECURITY DEFINER SET search_path=pg_catalog,public,d4 AS $$ SELECT d4.recovery_info(delivery); $$;
-- Only durable seals and authorized CLAIM links may explain intermediate attempts.
CREATE FUNCTION d4.absence_lineage(delivery uuid) RETURNS jsonb LANGUAGE sql STABLE SECURITY DEFINER SET search_path=pg_catalog,public,d2,d3,d4 AS $$
 WITH RECURSIVE chain(a,g) AS (
 SELECT ds.attempt_id,ds.generation FROM d4.deliveries d JOIN d3.dispatches ds ON ds.command_id=d.dispatch_command_id WHERE d.id=delivery
 UNION ALL SELECT s.attempt_id,s.generation FROM chain x JOIN d4.absence_links l ON l.attempt_id=x.a AND l.generation=x.g JOIN d4.absence_seals s ON s.id=l.seal_id WHERE s.generation+1=x.g),
 links AS(SELECT s.generation,p.proof source,d4.recovery_info(d.id) target,sa.attempt_no source_count,ta.attempt_no target_count,encode(public.digest(p.proof::text,'sha256'),'hex') seal_hash,d4.recovery_current(s.id) current
 FROM chain x JOIN d4.absence_links l ON l.attempt_id=x.a AND l.generation=x.g JOIN d4.absence_seals s ON s.id=l.seal_id JOIN d4.recovery_proofs p ON p.id=s.proof_id JOIN public.execution_attempts sa ON sa.id=s.attempt_id JOIN public.execution_attempts ta ON ta.id=l.attempt_id JOIN d3.dispatches ds ON ds.attempt_id=l.attempt_id JOIN d4.deliveries d ON d.dispatch_command_id=ds.command_id)
 SELECT coalesce(jsonb_agg(jsonb_build_object('source',source,'target',target,'source_count',source_count,'target_count',target_count,'seal_hash',seal_hash,'current',current) ORDER BY generation),'[]') FROM links;
$$;
