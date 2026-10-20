-- SPDX-License-Identifier: GPL-3.0-only
-- DRAFT ONLY: not validated or included by a migration/bootstrap.
-- Contains duplicated A20 sketches now superseded by V27. Do not apply this file
-- as a migration: derive only additive A21/A22 objects after completing all guards.
-- A20/A21/A22: absence seals, zero-accounting revisions, separate quarantine cases.
CREATE TABLE d4.absence_seals(id uuid PRIMARY KEY,proof_id uuid NOT NULL UNIQUE REFERENCES d4.recovery_proofs(id),delivery_id uuid NOT NULL REFERENCES d4.deliveries(id),operation_id uuid NOT NULL REFERENCES public.operations(id),generation bigint NOT NULL,attempt_id uuid NOT NULL REFERENCES public.execution_attempts(id),reservation_id uuid NOT NULL REFERENCES d2.reservations(id),committed_version bigint NOT NULL,UNIQUE(operation_id,generation));
CREATE TABLE d4.absence_authorizations(id uuid PRIMARY KEY,seal_id uuid NOT NULL REFERENCES d4.absence_seals(id),authorized_version bigint NOT NULL,reason text NOT NULL);
CREATE TABLE d4.absence_links(seal_id uuid PRIMARY KEY REFERENCES d4.absence_seals(id),authorization_id uuid NOT NULL REFERENCES d4.absence_authorizations(id),attempt_id uuid NOT NULL UNIQUE REFERENCES public.execution_attempts(id),generation bigint NOT NULL);
CREATE TABLE d4.review_revisions(id uuid PRIMARY KEY,delivery_id uuid NOT NULL REFERENCES d4.deliveries(id),anchor_id uuid NOT NULL,parent_id uuid REFERENCES d4.review_revisions(id),revision_no bigint NOT NULL,operation_id uuid NOT NULL REFERENCES public.operations(id),generation bigint NOT NULL,proof jsonb NOT NULL,receipt_basis jsonb NOT NULL,UNIQUE NULLS NOT DISTINCT(delivery_id,parent_id),UNIQUE(delivery_id,revision_no));
CREATE VIEW d4.review_heads AS SELECT DISTINCT ON(delivery_id) * FROM d4.review_revisions ORDER BY delivery_id,revision_no DESC;
CREATE TABLE d4.review_cases(id uuid PRIMARY KEY,operation_id uuid NOT NULL REFERENCES public.operations(id),generation bigint NOT NULL,delivery_id uuid NOT NULL REFERENCES d4.deliveries(id),task_id uuid NOT NULL REFERENCES public.tasks(id),resource_id uuid NOT NULL REFERENCES public.resources(id),exclusive_keys jsonb NOT NULL,reason text NOT NULL,opened_version bigint NOT NULL,opening_basis jsonb NOT NULL);
CREATE TABLE d4.review_affected(case_id uuid NOT NULL REFERENCES d4.review_cases(id),attempt_id uuid NOT NULL REFERENCES public.execution_attempts(id),delivery_id uuid NOT NULL REFERENCES d4.deliveries(id),operation_id uuid NOT NULL REFERENCES public.operations(id),generation bigint NOT NULL,PRIMARY KEY(case_id,attempt_id));
CREATE TABLE d4.review_barriers(id uuid PRIMARY KEY,case_id uuid NOT NULL,attempt_id uuid NOT NULL,proof jsonb NOT NULL,FOREIGN KEY(case_id,attempt_id) REFERENCES d4.review_affected(case_id,attempt_id),UNIQUE(case_id,attempt_id));
CREATE TABLE d4.review_closures(id uuid PRIMARY KEY,case_id uuid NOT NULL UNIQUE REFERENCES d4.review_cases(id),revision_id uuid NOT NULL REFERENCES d4.review_revisions(id),reason text NOT NULL);
CREATE TABLE d4.review_authorizations(id uuid PRIMARY KEY,checkpoint_id uuid NOT NULL,revision_id uuid NOT NULL REFERENCES d4.review_revisions(id),authorized_version bigint NOT NULL,reason text NOT NULL);
CREATE TABLE d4.review_links(authorization_id uuid PRIMARY KEY REFERENCES d4.review_authorizations(id),attempt_id uuid NOT NULL UNIQUE REFERENCES public.execution_attempts(id));
CREATE TABLE d4.review_candidates(id uuid PRIMARY KEY,delivery_id uuid NOT NULL REFERENCES d4.deliveries(id),receiver_id uuid NOT NULL,step text NOT NULL,receipt jsonb NOT NULL);
CREATE VIEW d4.open_reviews AS SELECT c.* FROM d4.review_cases c WHERE NOT EXISTS(SELECT 1 FROM d4.review_closures x WHERE x.case_id=c.id);
DO $$ DECLARE t text;BEGIN FOREACH t IN ARRAY ARRAY['absence_seals','absence_authorizations','absence_links','review_revisions','review_cases','review_affected','review_barriers','review_closures','review_authorizations','review_links','review_candidates'] LOOP EXECUTE format('CREATE TRIGGER immutable_fact BEFORE UPDATE OR DELETE OR TRUNCATE ON d4.%I FOR EACH STATEMENT EXECUTE FUNCTION public.d2_reject_fact_mutation()',t);END LOOP;END $$;
CREATE FUNCTION d4.review_task_blocked(tid uuid,integrating boolean) RETURNS boolean LANGUAGE sql STABLE SECURITY DEFINER SET search_path=pg_catalog,public,d2,d4 AS $$
 WITH RECURSIVE edges(a,b) AS(
 SELECT predecessor_task_id,successor_task_id FROM public.task_dependencies WHERE kind='HARD' OR (integrating AND kind='MOCKABLE')
 UNION SELECT p.task_id,r.consumer_task_id FROM d2.capability_producers p JOIN d2.resolutions x ON x.version_id=p.version_id JOIN public.capability_requirements r ON r.id=x.requirement_id WHERE r.kind='HARD' OR (integrating AND r.kind='MOCKABLE')),
 affected(t) AS(SELECT task_id FROM d4.open_reviews UNION SELECT e.b FROM affected a JOIN edges e ON e.a=a.t)
 SELECT EXISTS(SELECT 1 FROM affected WHERE t=tid);
$$;
CREATE FUNCTION d4.case_blocks(caseid uuid,oid uuid,rid uuid) RETURNS boolean LANGUAGE sql STABLE SECURITY DEFINER SET search_path=pg_catalog,public,d4 AS $$
 SELECT EXISTS(SELECT 1 FROM d4.review_cases c JOIN public.operations o ON o.id=oid WHERE c.id=caseid AND (o.id=c.operation_id OR o.task_id=c.task_id OR rid=c.resource_id OR EXISTS(SELECT 1 FROM jsonb_array_elements_text(coalesce(o.policy_snapshot->'exclusive_keys','[]')) k WHERE c.exclusive_keys ? k.value)));
$$;
CREATE FUNCTION d4.review_blocked(oid uuid,rid uuid,integrating boolean DEFAULT false) RETURNS boolean LANGUAGE sql STABLE SECURITY DEFINER SET search_path=pg_catalog,public,d4 AS $$
 SELECT coalesce((SELECT d4.review_task_blocked(o.task_id,integrating) OR EXISTS(SELECT 1 FROM d4.open_reviews c WHERE d4.case_blocks(c.id,oid,rid)) FROM public.operations o WHERE o.id=oid),true);
$$;
CREATE FUNCTION d4.review_anchor(delivery uuid) RETURNS jsonb LANGUAGE plpgsql STABLE SECURITY DEFINER SET search_path=pg_catalog,public,d2,d3,d4 AS $$
DECLARE i jsonb=d4.recovery_info(delivery);p jsonb;aid uuid;terminal boolean=false;closeid uuid;receipts jsonb;
BEGIN
 SELECT s.id,r.proof,s.terminal INTO aid,p,terminal FROM d4.recovery_settlements s JOIN d4.recovery_proofs r ON r.id=s.proof_id WHERE r.delivery_id=delivery;
 IF aid IS NULL THEN SELECT cp.id,pr.proof INTO aid,p FROM d4.multi_checkpoints cp JOIN d4.multi_proofs pr ON pr.id=cp.proof_id WHERE pr.delivery_id=delivery;END IF;
 IF aid IS NULL THEN SELECT cp.id,pr.proof INTO aid,p FROM d4.checkpoints cp JOIN d4.checkpoint_proofs pr ON pr.id=cp.proof_id JOIN d4.checkpoint_requests r ON r.id=cp.request_id WHERE r.delivery_id=delivery;END IF;
 IF aid IS NULL THEN SELECT id,request->'proof',true INTO aid,p,terminal FROM d4.checkpoint_commands WHERE request->>'action'='ACCEPT_CONTINUATION' AND request->>'delivery'=delivery::text ORDER BY id LIMIT 1;END IF;
 IF aid IS NULL THEN SELECT id,proof,true INTO aid,p,terminal FROM d4.lab_evidence WHERE delivery_id=delivery AND acceptance AND effect_status='APPLIED' ORDER BY id LIMIT 1;END IF;
 IF aid IS NULL THEN RAISE EXCEPTION 'Verified historical anchor required' USING ERRCODE='23514';END IF;
 receipts=coalesce(p->'receipts',p->'receiver_seal'->'steps',CASE WHEN p ? 'receipt' THEN jsonb_build_object('step-1',p->'receipt') END);
 IF jsonb_typeof(receipts) IS DISTINCT FROM 'object' THEN RAISE EXCEPTION 'Complete canonical historical results required' USING ERRCODE='23514';END IF;
 closeid=coalesce((p->'receiver_seal'->>'command')::uuid,aid);
 RETURN jsonb_build_object('id',aid,'delivery',delivery,'operation',i->'operation','attempt',i->'attempt','worker',i->'worker','resource',i->'resource','generation',i->'generation','context_hash',i->'context_hash','policy_hash',i->'policy_hash','proof',p,'receipts',receipts,'close_command',closeid,'terminal',terminal,'current_basis',d4.receipt_basis((i->>'operation')::uuid,(i->>'generation')::bigint),'head',(SELECT id FROM d4.review_heads WHERE delivery_id=delivery),'info',i);
END $$;
CREATE FUNCTION d4.canonical_results(r jsonb) RETURNS jsonb LANGUAGE sql IMMUTABLE STRICT SET search_path=pg_catalog AS $$ SELECT coalesce(jsonb_object_agg(key,jsonb_build_object('status',value->'status','payloadHash',CASE WHEN value->>'status'='APPLIED' THEN value->'payloadHash' ELSE 'null'::jsonb END,'generation',value->'generation')),'{}') FROM jsonb_each(r); $$;
CREATE FUNCTION d4.revision_current(revision uuid) RETURNS boolean LANGUAGE sql STABLE SECURITY DEFINER SET search_path=pg_catalog,public,d4 AS $$
 SELECT EXISTS(SELECT 1 FROM d4.review_heads h JOIN public.operations o ON o.id=h.operation_id WHERE h.id=revision AND h.receipt_basis=d4.receipt_basis(h.operation_id,h.generation) AND h.proof->>'context_hash'=o.context_pack_sha256 AND h.proof->>'policy_hash'=encode(public.digest(o.policy_snapshot::text,'sha256'),'hex'));
$$;
CREATE OR REPLACE FUNCTION d4.recovery_current(sid uuid) RETURNS boolean LANGUAGE sql STABLE SECURITY DEFINER SET search_path=pg_catalog,public,d2,d3,d4 AS $$
 SELECT EXISTS(SELECT 1 FROM d4.recovery_settlements s JOIN d4.recovery_proofs p ON p.id=s.proof_id JOIN public.operations o ON o.id=s.operation_id LEFT JOIN d4.review_heads h ON h.delivery_id=p.delivery_id AND h.anchor_id=s.id
 WHERE s.id=sid AND coalesce(h.receipt_basis,s.receipt_basis)=d4.receipt_basis(s.operation_id,s.generation) AND p.proof->>'context_hash'=o.context_pack_sha256 AND p.proof->>'policy_hash'=encode(public.digest(o.policy_snapshot::text,'sha256'),'hex'));
$$;
CREATE OR REPLACE FUNCTION d4.receipt_resolved(eid uuid) RETURNS boolean LANGUAGE sql STABLE SECURITY DEFINER SET search_path=pg_catalog,public,d2,d4 AS $$
 SELECT EXISTS(SELECT 1 FROM d4.review_heads h CROSS JOIN LATERAL jsonb_array_elements(h.receipt_basis) e WHERE e->>'id'=eid::text AND d4.revision_current(h.id)) OR EXISTS(SELECT 1 FROM d4.recovery_settlements s CROSS JOIN LATERAL jsonb_array_elements(s.receipt_basis) e WHERE e->>'id'=eid::text AND d4.recovery_current(s.id));
$$;
CREATE FUNCTION d4.review_revise(cid uuid,delivery uuid,expected_head uuid,expected_version bigint,proof jsonb) RETURNS jsonb LANGUAGE plpgsql SECURITY DEFINER SET search_path=pg_catalog,public,d2,d3,d4 AS $$
DECLARE req jsonb=jsonb_build_object('action','REVIEW_REVISE','delivery',delivery,'parent',expected_head,'version',expected_version,'proof',proof);prior jsonb;a jsonb;h d4.review_heads;o public.operations;e record;rr jsonb;prefix text;result jsonb;
BEGIN
 PERFORM d3.lock_state();prior=d4.checkpoint_previous(cid,req);IF prior IS NOT NULL THEN RETURN prior;END IF;a=d4.review_anchor(delivery);SELECT * INTO h FROM d4.review_heads WHERE delivery_id=delivery;SELECT * INTO STRICT o FROM public.operations WHERE id=(a->>'operation')::uuid;
 IF h.id IS DISTINCT FROM expected_head OR o.row_version IS DISTINCT FROM expected_version THEN RAISE EXCEPTION 'Revision head/version changed' USING ERRCODE='40001';END IF;
 IF proof->>'schema' IS DISTINCT FROM 'd4.review.proof.v1' OR proof->'receipt_basis' IS DISTINCT FROM a->'current_basis' OR proof->>'context_hash' IS DISTINCT FROM a->>'context_hash' OR proof->>'policy_hash' IS DISTINCT FROM a->>'policy_hash'
 OR proof->'process_stopped' IS DISTINCT FROM 'true'::jsonb OR proof->'artifact_valid' IS DISTINCT FROM 'true'::jsonb OR proof->'receiver_closed' IS DISTINCT FROM 'true'::jsonb
 OR coalesce(proof->>'host_observation_hash','') !~ '^[a-f0-9]{64}$' OR coalesce(proof->>'stdout_hash','') !~ '^[a-f0-9]{64}$' OR coalesce(proof->>'stderr_hash','') !~ '^[a-f0-9]{64}$'
 OR EXISTS(SELECT 1 FROM jsonb_each(jsonb_build_object('operation',a->'operation','attempt',a->'attempt','worker',a->'worker','resource',a->'resource','generation',a->'generation')) x WHERE proof->x.key IS DISTINCT FROM x.value OR proof->'receiver_seal'->'identity'->x.key IS DISTINCT FROM x.value)
 OR d4.canonical_results(proof->'receipts') IS DISTINCT FROM d4.canonical_results(a->'receipts') OR proof->'receiver_seal'->'steps' IS DISTINCT FROM proof->'receipts'
 OR proof->'receiver_seal'->'sequence' IS DISTINCT FROM a->'proof'->'close_sequence' OR proof->'receiver_seal'->>'command' IS DISTINCT FROM a->>'close_command'
 OR NOT EXISTS(SELECT 1 FROM d4.lab_grants WHERE request->>'delivery'=delivery::text AND response->>'receiver_id'=proof->'receiver_seal'->>'receiverId')
 THEN RAISE EXCEPTION 'Same closed canonical result and independent proof required' USING ERRCODE='23514';END IF;
 prefix=o.id||'/'||o.context_pack_sha256;
 FOR e IN SELECT * FROM d2.effect_receipts WHERE operation_id=o.id AND generation=(a->>'generation')::bigint LOOP
  rr=CASE WHEN e.effect_key=prefix THEN proof->'receipts'->'step-1' WHEN left(e.effect_key,length(prefix)+1)=prefix||'/' THEN proof->'receipts'->substr(e.effect_key,length(prefix)+2) END;
  IF rr IS NULL OR (e.status='APPLIED' AND rr->>'status'<>'APPLIED') OR EXISTS(SELECT 1 FROM d4.recovery_observations ro WHERE ro.receipt_id=e.id AND (ro.receiver_id::text<>proof->'receiver_seal'->>'receiverId' OR (ro.receipt->>'payloadHash' IS NOT NULL AND ro.receipt->>'payloadHash' IS DISTINCT FROM rr->>'payloadHash'))) OR EXISTS(SELECT 1 FROM d4.lab_evidence le WHERE le.receipt_id=e.id AND le.proof->'receipt'->>'payloadHash' IS NOT NULL AND le.proof->'receipt'->>'payloadHash' IS DISTINCT FROM rr->>'payloadHash') THEN RAISE EXCEPTION 'Contradiction cannot revoke a canonical applied result' USING ERRCODE='23514';END IF;
 END LOOP;
 INSERT INTO d4.review_revisions VALUES(cid,delivery,(a->>'id')::uuid,expected_head,coalesce(h.revision_no,0)+1,o.id,(a->>'generation')::bigint,proof,a->'current_basis');UPDATE public.operations SET row_version=row_version+1 WHERE id=o.id;
 result=jsonb_build_object('revision_id',cid,'row_version',o.row_version+1,'accounting_delta',0);INSERT INTO d4.checkpoint_commands VALUES(cid,req,result);INSERT INTO public.outbox_events(aggregate_type,aggregate_id,event_type,payload) VALUES('OPERATION',o.id,'D4_REVIEW_REVISED',result);RETURN result;
END $$;
CREATE FUNCTION d4.review_open(cid uuid,oid uuid,gen bigint,reason text) RETURNS jsonb LANGUAGE plpgsql SECURITY DEFINER SET search_path=pg_catalog,public,d2,d3,d4 AS $$
DECLARE o public.operations;ds d3.dispatches;delivery uuid;prior jsonb;req jsonb=jsonb_build_object('action','REVIEW_OPEN','operation',oid,'generation',gen,'reason',reason);result jsonb;existing uuid;
BEGIN
 PERFORM d3.lock_state();prior=d4.checkpoint_previous(cid,req);IF prior IS NOT NULL THEN RETURN prior;END IF;SELECT id INTO existing FROM d4.open_reviews WHERE operation_id=oid AND generation=gen;
 IF existing IS NOT NULL THEN RETURN jsonb_build_object('case_id',existing);END IF;
 SELECT * INTO STRICT o FROM public.operations WHERE id=oid;SELECT * INTO STRICT ds FROM d3.dispatches WHERE operation_id=oid AND generation=gen;SELECT id INTO STRICT delivery FROM d4.deliveries WHERE dispatch_command_id=ds.command_id;
 IF cid IS NULL OR reason IS NULL OR length(btrim(reason)) NOT BETWEEN 1 AND 512 THEN RAISE EXCEPTION 'Explicit review cause required' USING ERRCODE='23514';END IF;
 PERFORM d4.review_anchor(delivery);
 INSERT INTO d4.review_cases VALUES(cid,oid,gen,delivery,o.task_id,ds.resource_id,coalesce(o.policy_snapshot->'exclusive_keys','[]'),reason,o.row_version+1,d4.receipt_basis(oid,gen));UPDATE public.operations SET row_version=row_version+1 WHERE id=oid;
 INSERT INTO d4.review_affected SELECT cid,l.attempt_id,d.id,l.operation_id,l.fencing_generation FROM public.operation_leases l JOIN public.operations x ON x.id=l.operation_id JOIN d3.dispatches a ON a.attempt_id=l.attempt_id JOIN d4.deliveries d ON d.dispatch_command_id=a.command_id WHERE d4.case_blocks(cid,x.id,a.resource_id) OR d4.review_task_blocked(x.task_id,coalesce((x.policy_snapshot->>'integration_phase')::boolean,false));
 result=jsonb_build_object('case_id',cid,'row_version',o.row_version+1,'affected',(SELECT count(*) FROM d4.review_affected WHERE case_id=cid));INSERT INTO d4.checkpoint_commands VALUES(cid,req,result);INSERT INTO public.outbox_events(aggregate_type,aggregate_id,event_type,payload) VALUES('OPERATION',oid,'D4_REVIEW_OPENED',result);RETURN result;
END $$;
CREATE FUNCTION d4.review_on_receipt() RETURNS trigger LANGUAGE plpgsql SECURITY DEFINER SET search_path=pg_catalog,public,d2,d3,d4 AS $$
BEGIN
 IF EXISTS(SELECT 1 FROM public.operations WHERE id=NEW.operation_id AND state IN ('COMPLETED','CANCELLED')) OR EXISTS(SELECT 1 FROM d4.recovery_settlements s WHERE s.operation_id=NEW.operation_id AND s.generation=NEW.generation) THEN PERFORM d4.review_open(public.gen_random_uuid(),NEW.operation_id,NEW.generation,'New factual receipt after settlement or terminal outcome');END IF;RETURN NEW;
END $$;
CREATE TRIGGER reopen_review AFTER INSERT ON d2.effect_receipts FOR EACH ROW EXECUTE FUNCTION d4.review_on_receipt();
CREATE FUNCTION d4.review_case_info(caseid uuid) RETURNS jsonb LANGUAGE sql STABLE SECURITY DEFINER SET search_path=pg_catalog,public,d4 AS $$ SELECT to_jsonb(c)||jsonb_build_object('open',EXISTS(SELECT 1 FROM d4.open_reviews WHERE id=caseid),'affected',(SELECT coalesce(jsonb_agg(to_jsonb(a)||jsonb_build_object('info',d4.recovery_info(a.delivery_id))),'[]') FROM d4.review_affected a WHERE a.case_id=caseid),'anchor',d4.review_anchor(c.delivery_id)) FROM d4.review_cases c WHERE c.id=caseid; $$;
CREATE FUNCTION d4.review_barrier(cid uuid,caseid uuid,attempt uuid,proof jsonb) RETURNS jsonb LANGUAGE plpgsql SECURITY DEFINER SET search_path=pg_catalog,public,d2,d3,d4 AS $$
DECLARE a d4.review_affected;i jsonb;old d4.review_barriers;
BEGIN
 PERFORM d3.lock_state();SELECT * INTO STRICT a FROM d4.review_affected WHERE case_id=caseid AND attempt_id=attempt;i=d4.recovery_info(a.delivery_id);SELECT * INTO old FROM d4.review_barriers WHERE id=cid;
 IF FOUND THEN IF old.case_id IS DISTINCT FROM caseid OR old.attempt_id IS DISTINCT FROM attempt OR old.proof IS DISTINCT FROM proof THEN RAISE EXCEPTION 'Barrier replay conflict' USING ERRCODE='23514';END IF;RETURN jsonb_build_object('barrier_id',cid);END IF;
 IF proof->'process_stopped' IS DISTINCT FROM 'true'::jsonb OR coalesce(proof->>'host_observation_hash','') !~ '^[a-f0-9]{64}$' OR coalesce((proof->'receiver_seal'->>'sequence')::bigint,0)<=0
 OR EXISTS(SELECT 1 FROM jsonb_each(jsonb_build_object('operation',i->'operation','attempt',i->'attempt','worker',i->'worker','resource',i->'resource','generation',i->'generation')) x WHERE proof->x.key IS DISTINCT FROM x.value OR proof->'receiver_seal'->'identity'->x.key IS DISTINCT FROM x.value)
 OR NOT EXISTS(SELECT 1 FROM d4.lab_grants WHERE request->>'delivery'=a.delivery_id::text AND response->>'receiver_id'=proof->'receiver_seal'->>'receiverId') THEN RAISE EXCEPTION 'Independent closed stop barrier required' USING ERRCODE='23514';END IF;
 INSERT INTO d4.review_barriers VALUES(cid,caseid,attempt,proof);RETURN jsonb_build_object('barrier_id',cid);
END $$;
CREATE FUNCTION d4.review_close(cid uuid,caseid uuid,revision uuid,reason text) RETURNS jsonb LANGUAGE plpgsql SECURITY DEFINER SET search_path=pg_catalog,public,d2,d3,d4 AS $$
DECLARE req jsonb=jsonb_build_object('action','REVIEW_CLOSE','case',caseid,'revision',revision,'reason',reason);prior jsonb;c d4.review_cases;h d4.review_heads;result jsonb;
BEGIN
 PERFORM d3.lock_state();prior=d4.checkpoint_previous(cid,req);IF prior IS NOT NULL THEN RETURN prior;END IF;SELECT * INTO STRICT c FROM d4.open_reviews WHERE id=caseid;SELECT * INTO STRICT h FROM d4.review_heads WHERE id=revision AND delivery_id=c.delivery_id;
 IF NOT d4.revision_current(revision) OR reason IS NULL OR length(btrim(reason)) NOT BETWEEN 1 AND 512 OR EXISTS(SELECT 1 FROM d4.review_affected a WHERE a.case_id=caseid AND (NOT EXISTS(SELECT 1 FROM d4.review_barriers b WHERE b.case_id=caseid AND b.attempt_id=a.attempt_id) OR EXISTS(SELECT 1 FROM public.operation_leases l JOIN public.operations o ON o.id=l.operation_id WHERE l.attempt_id=a.attempt_id AND o.state NOT IN ('RECONCILING','BLOCKED_APPROVAL'))))
 THEN RAISE EXCEPTION 'Current revision and every independent containment barrier required' USING ERRCODE='23514';END IF;
 INSERT INTO d4.review_closures VALUES(cid,caseid,revision,reason);result=jsonb_build_object('closed',true,'case_id',caseid);INSERT INTO d4.checkpoint_commands VALUES(cid,req,result);INSERT INTO public.outbox_events(aggregate_type,aggregate_id,event_type,payload) VALUES('OPERATION',c.operation_id,'D4_REVIEW_CLOSED',result);RETURN result;
END $$;
CREATE FUNCTION d4.absence_safe(oid uuid,gen bigint) RETURNS boolean LANGUAGE sql STABLE SECURITY DEFINER SET search_path=pg_catalog,public,d4 AS $$
 SELECT EXISTS(SELECT 1 FROM d4.absence_seals s JOIN d4.absence_authorizations a ON a.seal_id=s.id JOIN public.operations o ON o.id=s.operation_id WHERE s.operation_id=oid AND s.generation=gen AND o.lease_generation=gen AND o.state='READY' AND o.row_version=a.authorized_version AND d4.recovery_current(s.id) AND NOT EXISTS(SELECT 1 FROM d4.absence_links WHERE seal_id=s.id) AND NOT d4.review_blocked(o.id,(SELECT resource_id FROM d2.reservations WHERE id=s.reservation_id),coalesce((o.policy_snapshot->>'integration_phase')::boolean,false)));
$$;
CREATE FUNCTION d4.absence_authorize(cid uuid,seal uuid,expected_version bigint,reason text) RETURNS jsonb LANGUAGE plpgsql SECURITY DEFINER SET search_path=pg_catalog,public,d2,d3,d4 AS $$
DECLARE req jsonb=jsonb_build_object('action','ABSENCE_AUTHORIZE','seal',seal,'version',expected_version,'reason',reason);prior jsonb;s d4.absence_seals;o public.operations;result jsonb;
BEGIN
 PERFORM d3.lock_state();prior=d4.checkpoint_previous(cid,req);IF prior IS NOT NULL THEN RETURN prior;END IF;SELECT * INTO STRICT s FROM d4.absence_seals WHERE id=seal;SELECT * INTO STRICT o FROM public.operations WHERE id=s.operation_id;
 IF o.state NOT IN ('RETRY_PENDING','READY') OR o.row_version IS DISTINCT FROM expected_version OR o.lease_generation<>s.generation OR NOT d4.recovery_current(s.id) OR EXISTS(SELECT 1 FROM d4.absence_links WHERE seal_id=seal) OR d4.review_blocked(o.id,(SELECT resource_id FROM d2.reservations WHERE id=s.reservation_id),false) OR (SELECT count(*) FROM public.execution_attempts WHERE operation_id=o.id)>=coalesce((o.policy_snapshot->>'max_attempts')::int,3) OR reason IS NULL OR length(btrim(reason)) NOT BETWEEN 1 AND 512 THEN RAISE EXCEPTION 'Current unused absence, authorization and budget required' USING ERRCODE='23514';END IF;
 UPDATE public.operations SET state='READY',row_version=row_version+1 WHERE id=o.id;IF o.state<>'READY' THEN PERFORM d2.record_transition(cid,'OPERATION',o.id,o.state,'READY',o.row_version+1,'CONTROL_PLANE','Explicit absence retry');END IF;
 INSERT INTO d4.absence_authorizations VALUES(cid,seal,o.row_version+1,reason);result=jsonb_build_object('state','READY','row_version',o.row_version+1);INSERT INTO d4.checkpoint_commands VALUES(cid,req,result);RETURN result;
END $$;
CREATE FUNCTION d4.review_checkpoint_safe(oid uuid,gen bigint) RETURNS boolean LANGUAGE sql STABLE SECURITY DEFINER SET search_path=pg_catalog,public,d2,d4 AS $$
 SELECT EXISTS(SELECT 1 FROM d4.review_authorizations a JOIN d4.review_heads h ON h.id=a.revision_id JOIN public.operations o ON o.id=h.operation_id JOIN d2.reservations r ON r.operation_id=o.id WHERE o.id=oid AND h.generation=gen AND o.lease_generation=gen AND o.state='READY' AND o.row_version=a.authorized_version AND d4.revision_current(h.id) AND NOT d4.review_blocked(o.id,r.resource_id,false) AND (
 EXISTS(SELECT 1 FROM d4.multi_heads cp WHERE cp.id=a.checkpoint_id AND cp.operation_id=o.id AND cp.source_generation=gen AND NOT EXISTS(SELECT 1 FROM d4.multi_links WHERE checkpoint_id=cp.id) AND d4.multi_head_settled(o.id)) OR EXISTS(SELECT 1 FROM d4.checkpoints cp WHERE cp.id=a.checkpoint_id AND cp.operation_id=o.id AND cp.source_generation=gen AND NOT EXISTS(SELECT 1 FROM d4.continuation_links WHERE checkpoint_id=cp.id) AND NOT EXISTS(SELECT 1 FROM d2.reservation_balances WHERE reservation_id=r.id AND (outstanding<>0 OR consumed<>4)))));
$$;
CREATE FUNCTION d4.review_authorize(cid uuid,checkpoint uuid,revision uuid,expected_version bigint,reason text) RETURNS jsonb LANGUAGE plpgsql SECURITY DEFINER SET search_path=pg_catalog,public,d2,d3,d4 AS $$
DECLARE req jsonb=jsonb_build_object('action','REVIEW_AUTHORIZE','checkpoint',checkpoint,'revision',revision,'version',expected_version,'reason',reason);prior jsonb;h d4.review_heads;o public.operations;result jsonb;
BEGIN
 PERFORM d3.lock_state();prior=d4.checkpoint_previous(cid,req);IF prior IS NOT NULL THEN RETURN prior;END IF;SELECT * INTO STRICT h FROM d4.review_heads WHERE id=revision;SELECT * INTO STRICT o FROM public.operations WHERE id=h.operation_id;
 IF o.state NOT IN ('CANCELLED','READY') OR o.row_version IS DISTINCT FROM expected_version OR o.lease_generation<>h.generation OR NOT d4.revision_current(h.id) OR d4.review_blocked(o.id,(SELECT resource_id FROM d2.reservations WHERE operation_id=o.id),false) OR reason IS NULL OR length(btrim(reason)) NOT BETWEEN 1 AND 512 OR (SELECT count(*) FROM public.execution_attempts WHERE operation_id=o.id)>=coalesce((o.policy_snapshot->>'max_attempts')::int,3)
 OR NOT (EXISTS(SELECT 1 FROM d4.multi_heads cp WHERE cp.id=checkpoint AND cp.operation_id=o.id AND cp.source_generation=h.generation AND NOT EXISTS(SELECT 1 FROM d4.multi_links WHERE checkpoint_id=cp.id) AND d4.multi_head_settled(o.id)) OR EXISTS(SELECT 1 FROM d4.checkpoints cp WHERE cp.id=checkpoint AND cp.operation_id=o.id AND cp.source_generation=h.generation AND NOT EXISTS(SELECT 1 FROM d4.continuation_links WHERE checkpoint_id=cp.id))) THEN RAISE EXCEPTION 'Current unused reviewed checkpoint required' USING ERRCODE='23514';END IF;
 UPDATE public.operations SET state='READY',row_version=row_version+1 WHERE id=o.id;IF o.state='CANCELLED' THEN PERFORM d2.record_transition(cid,'OPERATION',o.id,'CANCELLED','READY',o.row_version+1,'CONTROL_PLANE','Explicit reviewed checkpoint');END IF;
 IF EXISTS(SELECT 1 FROM d4.multi_checkpoints WHERE id=checkpoint) THEN INSERT INTO d4.multi_authorizations SELECT cid,checkpoint,o.row_version+1,reason WHERE NOT EXISTS(SELECT 1 FROM d4.multi_authorizations WHERE checkpoint_id=checkpoint);
 ELSE INSERT INTO d4.continuation_authorizations SELECT cid,checkpoint,reason,o.row_version+1 WHERE NOT EXISTS(SELECT 1 FROM d4.continuation_authorizations WHERE checkpoint_id=checkpoint);END IF;
 INSERT INTO d4.review_authorizations VALUES(cid,checkpoint,revision,o.row_version+1,reason);result=jsonb_build_object('state','READY','row_version',o.row_version+1);INSERT INTO d4.checkpoint_commands VALUES(cid,req,result);RETURN result;
END $$;
CREATE FUNCTION d4.parent_linked(oid uuid,parent uuid,attempt uuid,gen bigint) RETURNS boolean LANGUAGE sql STABLE SECURITY DEFINER SET search_path=pg_catalog,public,d4 AS $$
 WITH RECURSIVE lineage(a,g) AS(SELECT attempt,gen UNION ALL SELECT s.attempt_id,s.generation FROM lineage x JOIN d4.absence_links l ON l.attempt_id=x.a AND l.generation=x.g JOIN d4.absence_seals s ON s.id=l.seal_id WHERE s.operation_id=oid AND s.generation+1=x.g)
 SELECT CASE WHEN parent IS NULL THEN EXISTS(SELECT 1 FROM lineage x JOIN public.execution_attempts a ON a.id=x.a WHERE a.operation_id=oid AND a.attempt_no=1 AND x.g=1) ELSE EXISTS(SELECT 1 FROM lineage x JOIN d4.multi_links l ON l.attempt_id=x.a AND l.generation=x.g JOIN d4.multi_checkpoints cp ON cp.id=l.checkpoint_id WHERE cp.id=parent AND cp.operation_id=oid AND cp.source_generation+1=x.g) END;
$$;
ALTER FUNCTION d4.continuation_safe(uuid,bigint) RENAME TO continuation_safe_before_i10;
CREATE FUNCTION d4.continuation_safe(oid uuid,gen bigint) RETURNS boolean LANGUAGE sql STABLE SECURITY DEFINER SET search_path=pg_catalog,public,d4 AS $$ SELECT (d4.continuation_safe_before_i10(oid,gen) OR d4.absence_safe(oid,gen) OR d4.review_checkpoint_safe(oid,gen)) AND NOT d4.review_blocked(oid,(SELECT resource_id FROM d2.reservations WHERE operation_id=oid),false); $$;
CREATE OR REPLACE VIEW d4.continuation_admissions AS
 SELECT cp.operation_id,cp.source_generation generation,cp.id checkpoint_id,au.id authorization_id,cp.manifest_hash,'SEALED_CHECKPOINT'::text admission_kind,d4.continuation_safe_before_i8(cp.operation_id,cp.source_generation) AND NOT d4.review_blocked(cp.operation_id,(SELECT resource_id FROM d2.reservations WHERE id=cp.reservation_id),false) eligible FROM d4.checkpoints cp JOIN d4.continuation_authorizations au ON au.checkpoint_id=cp.id
 UNION ALL SELECT cp.operation_id,cp.source_generation,cp.id,au.id,i.manifest_hash,'SEALED_CHECKPOINT',d4.multi_safe(cp.operation_id,cp.source_generation) AND NOT d4.review_blocked(cp.operation_id,(SELECT resource_id FROM d2.reservations WHERE id=cp.reservation_id),false) FROM d4.multi_heads cp JOIN d4.multi_authorizations au ON au.checkpoint_id=cp.id JOIN d4.multi_intents i ON i.operation_id=cp.operation_id
 UNION ALL SELECT s.operation_id,s.generation,s.id,a.id,p.proof->>'recovery_manifest_hash','SEALED_ABSENCE',d4.absence_safe(s.operation_id,s.generation) AND a.authorized_version=(SELECT row_version FROM public.operations WHERE id=s.operation_id) FROM d4.absence_seals s JOIN d4.absence_authorizations a ON a.seal_id=s.id JOIN d4.recovery_proofs p ON p.id=s.proof_id
 UNION ALL SELECT h.operation_id,h.generation,a.checkpoint_id,a.id,h.proof->>'manifest_hash','SEALED_REVIEW_CHECKPOINT',d4.review_checkpoint_safe(h.operation_id,h.generation) AND a.authorized_version=(SELECT row_version FROM public.operations WHERE id=h.operation_id) FROM d4.review_authorizations a JOIN d4.review_heads h ON h.id=a.revision_id;
CREATE FUNCTION d4.review_candidate(cid uuid,delivery uuid,receiver uuid,step text,receipt jsonb) RETURNS jsonb LANGUAGE plpgsql SECURITY DEFINER SET search_path=pg_catalog,public,d4 AS $$
DECLARE old d4.review_candidates;i jsonb=d4.recovery_info(delivery);
BEGIN
 PERFORM d3.lock_state();SELECT * INTO old FROM d4.review_candidates WHERE id=cid;IF FOUND THEN IF old.delivery_id IS DISTINCT FROM delivery OR old.receiver_id IS DISTINCT FROM receiver OR old.step IS DISTINCT FROM step OR old.receipt IS DISTINCT FROM receipt THEN RAISE EXCEPTION 'Candidate conflict' USING ERRCODE='23514';END IF;RETURN jsonb_build_object('candidate_id',cid);END IF;
 IF cid IS NULL OR receipt->'generation' IS DISTINCT FROM i->'generation' OR receipt->>'status' IS NULL OR receipt->>'status' NOT IN ('UNKNOWN','APPLIED','ABSENT') OR NOT EXISTS(SELECT 1 FROM d4.lab_grants WHERE request->>'delivery'=delivery::text AND response->>'receiver_id'=receiver::text) OR NOT EXISTS(SELECT 1 FROM jsonb_array_elements(i->'recovery_manifest'->'steps') s WHERE s->>'id'=step) THEN RAISE EXCEPTION 'Bound observed candidate required' USING ERRCODE='23514';END IF;
 INSERT INTO d4.review_candidates VALUES(cid,delivery,receiver,step,receipt);RETURN jsonb_build_object('candidate_id',cid);
END $$;
CREATE FUNCTION d4.review_ingest(cid uuid,candidate uuid) RETURNS jsonb LANGUAGE plpgsql SECURITY DEFINER SET search_path=pg_catalog,public,d4 AS $$
DECLARE c d4.review_candidates;BEGIN PERFORM d3.lock_state();SELECT * INTO STRICT c FROM d4.review_candidates WHERE id=candidate;RETURN d4.recovery_observe(cid,c.delivery_id,c.receiver_id,c.step,c.receipt);END $$;
