-- GENERATED A21/A22 by testing/D4/generate-review-admission.py; laboratory only.
-- Source SHA256 testing/D4/sql/review-active.sql 59f93507b854fb518f5cc5bc238eaafdf659757104ebf373e52db4eddc02a63c
-- Source SHA256 migrations-d4-proposed/V27__sealed_absence_retry.sql 9521089aa70a3847d9fe1daa25cb65958aedd0eb64fa8a4eb6ead4165f25efa6
-- Source SHA256 migrations-d4-proposed/V26__conclusive_reconciliation.sql 56102f5a496cdd0e8f71f75300bff278226d4f3c54948a1cbaf33b63f74f957d
-- Source SHA256 migrations-d4-proposed/V24__linear_multicount_checkpoints.sql ea5810ed75bc1b35b1cb4b6c7617bc0980c1121cbe8c39827d0b4f2852174600
-- Source SHA256 migrations-d4-proposed/V20__continuation_admission_adapters.sql 5fbced74c05829d95a1d7a7ae4f22fc99255c0876943ba5a83b6ca1cc1ace59c
-- Source SHA256 migrations-d4-proposed/V18__synthetic_lab_bridge.sql beb4587579c9ce6b12cfdbbdbab7b1d5d77c71519f2f1ff434d5d1a7a9fdab36
-- Source SHA256 migrations-d3-dispatch-proposed/V13__guarded_dispatch.sql be319a5a90c7b522f370f72f3e407af605a39449829115e7bf51844f915ad0ef
-- Source SHA256 migrations-d3-proposed/V12__planning_snapshot_and_publication.sql dc745993cdccddb9d1e7aa332e4771339c7cb9c0d9757ed0128ba07d88d8526e
-- Source SHA256 migrations-proposed/V9__execution_guards_contract_draft.sql 8d80f14535a2c87dd3fd6cbe87698709ff3a45bba532c1f24c744769eaacfa82
-- SPDX-License-Identifier: GPL-3.0-only
-- A21/A22 additive verified revisions and separate physical quarantine.
CREATE TABLE d4.review_revisions(id uuid PRIMARY KEY,delivery_id uuid NOT NULL REFERENCES d4.deliveries(id),anchor_id uuid NOT NULL,parent_id uuid REFERENCES d4.review_revisions(id),revision_no bigint NOT NULL,operation_id uuid NOT NULL REFERENCES public.operations(id),generation bigint NOT NULL,proof jsonb NOT NULL,receipt_basis jsonb NOT NULL,UNIQUE NULLS NOT DISTINCT(delivery_id,parent_id),UNIQUE(delivery_id,revision_no));
CREATE VIEW d4.review_heads AS SELECT DISTINCT ON(delivery_id) * FROM d4.review_revisions ORDER BY delivery_id,revision_no DESC;
CREATE TABLE d4.review_cases(id uuid PRIMARY KEY,operation_id uuid NOT NULL REFERENCES public.operations(id),generation bigint NOT NULL,delivery_id uuid REFERENCES d4.deliveries(id),task_id uuid NOT NULL REFERENCES public.tasks(id),resource_id uuid REFERENCES public.resources(id),exclusive_keys jsonb NOT NULL,reason text NOT NULL,opened_version bigint NOT NULL,opening_basis jsonb NOT NULL);
CREATE TABLE d4.review_unbound_affected(case_id uuid NOT NULL REFERENCES d4.review_cases(id),attempt_id uuid NOT NULL REFERENCES public.execution_attempts(id),operation_id uuid NOT NULL REFERENCES public.operations(id),generation bigint NOT NULL,PRIMARY KEY(case_id,attempt_id));
CREATE TABLE d4.review_affected(case_id uuid NOT NULL REFERENCES d4.review_cases(id),attempt_id uuid NOT NULL REFERENCES public.execution_attempts(id),delivery_id uuid NOT NULL REFERENCES d4.deliveries(id),operation_id uuid NOT NULL REFERENCES public.operations(id),generation bigint NOT NULL,PRIMARY KEY(case_id,attempt_id));
CREATE TABLE d4.review_barriers(id uuid PRIMARY KEY,case_id uuid NOT NULL,attempt_id uuid NOT NULL,proof jsonb NOT NULL,FOREIGN KEY(case_id,attempt_id) REFERENCES d4.review_affected(case_id,attempt_id),UNIQUE(case_id,attempt_id));
CREATE TABLE d4.review_closures(id uuid PRIMARY KEY,case_id uuid NOT NULL UNIQUE REFERENCES d4.review_cases(id),revision_id uuid NOT NULL REFERENCES d4.review_revisions(id),reason text NOT NULL);
CREATE TABLE d4.review_authorizations(id uuid PRIMARY KEY,checkpoint_id uuid NOT NULL,revision_id uuid NOT NULL REFERENCES d4.review_revisions(id),authorized_version bigint NOT NULL,reason text NOT NULL);
CREATE TABLE d4.review_links(authorization_id uuid PRIMARY KEY REFERENCES d4.review_authorizations(id),attempt_id uuid NOT NULL UNIQUE REFERENCES public.execution_attempts(id));
CREATE TABLE d4.review_candidates(id uuid PRIMARY KEY,delivery_id uuid NOT NULL REFERENCES d4.deliveries(id),receiver_id uuid NOT NULL,step text NOT NULL,receipt jsonb NOT NULL);
CREATE VIEW d4.open_reviews AS SELECT c.* FROM d4.review_cases c WHERE NOT EXISTS(SELECT 1 FROM d4.review_closures x WHERE x.case_id=c.id);
DO $$ DECLARE t text;BEGIN FOREACH t IN ARRAY ARRAY['review_revisions','review_cases','review_unbound_affected','review_affected','review_barriers','review_closures','review_authorizations','review_links','review_candidates'] LOOP EXECUTE format('CREATE TRIGGER immutable_fact BEFORE UPDATE OR DELETE OR TRUNCATE ON d4.%I FOR EACH STATEMENT EXECUTE FUNCTION public.d2_reject_fact_mutation()',t);END LOOP;END $$;
CREATE FUNCTION d4.review_task_blocked(tid uuid,integrating boolean) RETURNS boolean LANGUAGE sql STABLE SECURITY DEFINER SET search_path=pg_catalog,public,d2,d4 AS $$
 WITH RECURSIVE edges(a,b) AS(
 SELECT predecessor_task_id,successor_task_id FROM public.task_dependencies WHERE kind='HARD' OR (integrating AND kind='MOCKABLE')
 UNION SELECT p.task_id,r.consumer_task_id FROM d2.capability_producers p JOIN d2.resolutions x ON x.version_id=p.version_id JOIN public.capability_requirements r ON r.id=x.requirement_id WHERE r.kind='HARD' OR (integrating AND r.kind='MOCKABLE')),
 affected(t) AS(SELECT task_id FROM d4.open_reviews UNION SELECT o.task_id FROM public.operations o JOIN d4.review_affected a ON a.operation_id=o.id JOIN d4.open_reviews c ON c.id=a.case_id UNION SELECT o.task_id FROM public.operations o JOIN d4.review_unbound_affected a ON a.operation_id=o.id JOIN d4.open_reviews c ON c.id=a.case_id UNION SELECT e.b FROM affected a JOIN edges e ON e.a=a.t)
 SELECT EXISTS(SELECT 1 FROM affected WHERE t=tid);
$$;
CREATE FUNCTION d4.case_blocks(caseid uuid,oid uuid,rid uuid) RETURNS boolean LANGUAGE sql STABLE SECURITY DEFINER SET search_path=pg_catalog,public,d4 AS $$
 SELECT EXISTS(SELECT 1 FROM d4.review_cases c JOIN public.operations o ON o.id=oid WHERE c.id=caseid AND (o.id=c.operation_id OR o.task_id=c.task_id OR rid=c.resource_id OR EXISTS(SELECT 1 FROM jsonb_array_elements_text(coalesce(o.policy_snapshot->'exclusive_keys','[]')) k WHERE c.exclusive_keys ? k.value)));
$$;
CREATE FUNCTION d4.review_blocked(oid uuid,rid uuid,integrating boolean DEFAULT false) RETURNS boolean LANGUAGE sql STABLE SECURITY DEFINER SET search_path=pg_catalog,public,d4 AS $$
 SELECT coalesce((SELECT d4.review_task_blocked(o.task_id,integrating) OR EXISTS(SELECT 1 FROM d4.open_reviews c WHERE d4.case_blocks(c.id,oid,rid)) OR EXISTS(SELECT 1 FROM d4.review_affected a JOIN d4.open_reviews c ON c.id=a.case_id WHERE a.operation_id=oid) OR EXISTS(SELECT 1 FROM d4.review_unbound_affected a JOIN d4.open_reviews c ON c.id=a.case_id WHERE a.operation_id=oid) FROM public.operations o WHERE o.id=oid),true);
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
 IF (SELECT count(DISTINCT response->>'receiver_id') FROM d4.lab_grants WHERE request->>'delivery'=delivery::text)<>1 THEN RAISE EXCEPTION 'Single historical receiver required' USING ERRCODE='23514';END IF;
 closeid=coalesce((p->'receiver_seal'->>'command')::uuid,aid);
 RETURN jsonb_build_object('id',aid,'delivery',delivery,'operation',i->'operation','attempt',i->'attempt','worker',i->'worker','resource',i->'resource','generation',i->'generation','context_hash',i->'context_hash','policy_hash',i->'policy_hash','proof',p,'receipts',receipts,'close_command',closeid,'receiver_id',(SELECT response->>'receiver_id' FROM d4.lab_grants WHERE request->>'delivery'=delivery::text LIMIT 1),'terminal',coalesce(terminal,false),'current_basis',d4.receipt_basis((i->>'operation')::uuid,(i->>'generation')::bigint),'head',(SELECT id FROM d4.review_heads WHERE delivery_id=delivery),'info',i);
END $$;
CREATE FUNCTION d4.canonical_results(r jsonb) RETURNS jsonb LANGUAGE sql IMMUTABLE STRICT SET search_path=pg_catalog AS $$ SELECT coalesce(jsonb_object_agg(key,jsonb_build_object('status',value->'status','payloadHash',CASE WHEN value->>'status'='APPLIED' THEN value->'payloadHash' ELSE 'null'::jsonb END,'generation',value->'generation')),'{}') FROM jsonb_each(r); $$;
CREATE FUNCTION d4.revision_current(revision uuid) RETURNS boolean LANGUAGE sql STABLE SECURITY DEFINER SET search_path=pg_catalog,public,d4 AS $$
 SELECT EXISTS(SELECT 1 FROM d4.review_heads h JOIN public.operations o ON o.id=h.operation_id WHERE h.id=revision AND h.receipt_basis=d4.receipt_basis(h.operation_id,h.generation) AND h.proof->>'context_hash'=o.context_pack_sha256 AND h.proof->>'policy_hash'=encode(public.digest(o.policy_snapshot::text,'sha256'),'hex') AND NOT EXISTS(SELECT 1 FROM public.execution_evidence e WHERE e.attempt_id=(h.proof->>'attempt')::uuid AND e.evidence_type='ACCEPTANCE_FAIL'));
$$;
CREATE OR REPLACE FUNCTION d4.recovery_current(sid uuid) RETURNS boolean LANGUAGE sql STABLE SECURITY DEFINER SET search_path=pg_catalog,public,d2,d3,d4 AS $$
 SELECT EXISTS(SELECT 1 FROM d4.recovery_settlements s JOIN d4.recovery_proofs p ON p.id=s.proof_id JOIN public.operations o ON o.id=s.operation_id LEFT JOIN d4.review_heads h ON h.delivery_id=p.delivery_id AND h.anchor_id=s.id
 WHERE s.id=sid AND coalesce(h.receipt_basis,s.receipt_basis)=d4.receipt_basis(s.operation_id,s.generation) AND p.proof->>'context_hash'=o.context_pack_sha256 AND p.proof->>'policy_hash'=encode(public.digest(o.policy_snapshot::text,'sha256'),'hex'));
$$;
CREATE OR REPLACE FUNCTION d4.receipt_resolved(eid uuid) RETURNS boolean LANGUAGE sql STABLE SECURITY DEFINER SET search_path=pg_catalog,public,d2,d4 AS $$
 SELECT EXISTS(SELECT 1 FROM d4.review_heads h CROSS JOIN LATERAL jsonb_array_elements(h.receipt_basis) e WHERE e->>'id'=eid::text AND d4.revision_current(h.id)) OR EXISTS(SELECT 1 FROM d4.recovery_settlements s CROSS JOIN LATERAL jsonb_array_elements(s.receipt_basis) e WHERE e->>'id'=eid::text AND d4.recovery_current(s.id));
$$;
CREATE FUNCTION d4.review_accounting_current(delivery uuid) RETURNS boolean LANGUAGE plpgsql STABLE SECURITY DEFINER SET search_path=pg_catalog,public,d2,d3,d4 AS $$
DECLARE a jsonb=d4.review_anchor(delivery);i jsonb=a->'info';m jsonb=i->'recovery_manifest';applied jsonb='{}';parent jsonb;g bigint=(a->>'generation')::bigint;o public.operations;res d2.reservations;b record;cost numeric;total numeric;
BEGIN
 SELECT * INTO STRICT o FROM public.operations WHERE id=(a->>'operation')::uuid;SELECT * INTO STRICT res FROM d2.reservations WHERE operation_id=o.id;
 IF EXISTS(SELECT 1 FROM d2.commands c WHERE c.request->>'action'='ADJUST' AND c.request->>'reservation_id'=res.id::text) THEN RETURN false;END IF;
 IF i->'multi_checkpoint'='true'::jsonb THEN SELECT pr.evaluation->'applied' INTO parent FROM d4.multi_checkpoints cp JOIN d4.multi_proofs pr ON pr.id=cp.proof_id WHERE cp.operation_id=o.id AND cp.source_generation<g ORDER BY cp.source_generation DESC LIMIT 1;applied=coalesce(parent,'{}');
 ELSIF EXISTS(SELECT 1 FROM d4.checkpoints WHERE operation_id=o.id AND source_generation<g) THEN applied=jsonb_build_object('step-1',true);END IF;
 SELECT applied||coalesce(jsonb_object_agg(key,true),'{}') INTO applied FROM jsonb_each(a->'receipts') WHERE value->>'status'='APPLIED';
 FOR b IN SELECT * FROM d2.reservation_balances WHERE reservation_id=res.id LOOP
  SELECT coalesce(sum((v->'cost'->>b.account_id::text)::numeric) FILTER(WHERE applied ? (v->>'id')),0),coalesce(sum((v->'cost'->>b.account_id::text)::numeric),0) INTO cost,total FROM jsonb_array_elements(m->'steps') v;
  IF (o.lease_generation=g AND (b.outstanding<>0 OR b.consumed<>cost)) OR b.consumed<cost OR b.consumed>total OR b.outstanding<0 OR b.outstanding>(m->'accounts'->b.account_id::text->>'original')::numeric THEN RETURN false;END IF;
 END LOOP;RETURN true;
END $$;
CREATE FUNCTION d4.review_revise(cid uuid,delivery uuid,expected_head uuid,expected_version bigint,proof jsonb) RETURNS jsonb LANGUAGE plpgsql SECURITY DEFINER SET search_path=pg_catalog,public,d2,d3,d4 AS $$
DECLARE req jsonb=jsonb_build_object('action','REVIEW_REVISE','delivery',delivery,'parent',expected_head,'version',expected_version,'proof',proof);prior jsonb;a jsonb;h d4.review_heads;o public.operations;e record;rr jsonb;prefix text;result jsonb;
BEGIN
 PERFORM d3.lock_state();prior=d4.checkpoint_previous(cid,req);IF prior IS NOT NULL THEN RETURN prior;END IF;a=d4.review_anchor(delivery);SELECT * INTO h FROM d4.review_heads WHERE delivery_id=delivery;SELECT * INTO STRICT o FROM public.operations WHERE id=(a->>'operation')::uuid;
 IF h.id IS DISTINCT FROM expected_head OR o.row_version IS DISTINCT FROM expected_version THEN RAISE EXCEPTION 'Revision head/version changed' USING ERRCODE='40001';END IF;
 IF EXISTS(SELECT 1 FROM public.execution_evidence WHERE attempt_id=(a->>'attempt')::uuid AND evidence_type='ACCEPTANCE_FAIL') OR NOT d4.review_accounting_current(delivery) OR a->>'context_hash' IS DISTINCT FROM o.context_pack_sha256 OR a->>'policy_hash' IS DISTINCT FROM encode(public.digest(o.policy_snapshot::text,'sha256'),'hex') OR jsonb_typeof(proof->'receipts') IS DISTINCT FROM 'object' OR jsonb_typeof(proof->'receiver_seal') IS DISTINCT FROM 'object' OR proof->>'schema' IS DISTINCT FROM 'd4.review.proof.v1' OR proof->'receipt_basis' IS DISTINCT FROM a->'current_basis' OR proof->>'context_hash' IS DISTINCT FROM a->>'context_hash' OR proof->>'policy_hash' IS DISTINCT FROM a->>'policy_hash'
 OR proof->'process_stopped' IS DISTINCT FROM 'true'::jsonb OR proof->'artifact_valid' IS DISTINCT FROM 'true'::jsonb OR proof->'receiver_closed' IS DISTINCT FROM 'true'::jsonb
 OR coalesce(proof->>'host_observation_hash','') !~ '^[a-f0-9]{64}$' OR coalesce(proof->>'stdout_hash','') !~ '^[a-f0-9]{64}$' OR coalesce(proof->>'stderr_hash','') !~ '^[a-f0-9]{64}$'
 OR EXISTS(SELECT 1 FROM jsonb_each(jsonb_build_object('operation',a->'operation','attempt',a->'attempt','worker',a->'worker','resource',a->'resource','generation',a->'generation')) x WHERE proof->x.key IS DISTINCT FROM x.value OR proof->'receiver_seal'->'identity'->x.key IS DISTINCT FROM x.value)
 OR EXISTS(SELECT 1 FROM jsonb_each(proof->'receipts') x WHERE x.value->>'status' IS NULL OR x.value->>'status' NOT IN ('APPLIED','ABSENT') OR (x.value->>'status'='ABSENT' AND x.value->'closed' IS DISTINCT FROM 'true'::jsonb))
 OR d4.canonical_results(proof->'receipts') IS DISTINCT FROM d4.canonical_results(a->'receipts') OR proof->'receiver_seal'->'steps' IS DISTINCT FROM proof->'receipts'
 OR proof->'receiver_seal'->'sequence' IS DISTINCT FROM a->'proof'->'close_sequence' OR proof->'receiver_seal'->>'command' IS DISTINCT FROM a->>'close_command'
 OR proof->'receiver_seal'->>'receiverId' IS DISTINCT FROM a->>'receiver_id'
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
DECLARE o public.operations;ds d3.dispatches;delivery uuid;prior jsonb;req jsonb=jsonb_build_object('action','REVIEW_OPEN','operation',oid,'generation',gen,'reason',reason);result jsonb;existing uuid;added_bound integer;added_unbound integer;
BEGIN
 PERFORM d3.lock_state();prior=d4.checkpoint_previous(cid,req);IF prior IS NOT NULL THEN RETURN prior;END IF;SELECT id INTO existing FROM d4.open_reviews WHERE operation_id=oid AND generation=gen;
 IF existing IS NOT NULL THEN result=jsonb_build_object('case_id',existing);INSERT INTO d4.checkpoint_commands VALUES(cid,req,result);RETURN result;END IF;
 SELECT * INTO STRICT o FROM public.operations WHERE id=oid;SELECT * INTO ds FROM d3.dispatches WHERE operation_id=oid AND generation=gen;SELECT id INTO delivery FROM d4.deliveries WHERE dispatch_command_id=ds.command_id;IF ds.resource_id IS NULL THEN SELECT resource_id INTO ds.resource_id FROM d2.reservations WHERE operation_id=oid;END IF;
 IF cid IS NULL OR reason IS NULL OR length(btrim(reason)) NOT BETWEEN 1 AND 512 THEN RAISE EXCEPTION 'Explicit review cause required' USING ERRCODE='23514';END IF;

 INSERT INTO d4.review_cases VALUES(cid,oid,gen,delivery,o.task_id,ds.resource_id,coalesce(o.policy_snapshot->'exclusive_keys','[]'),reason,o.row_version+1,d4.receipt_basis(oid,gen));UPDATE public.operations SET row_version=row_version+1 WHERE id=oid;
 LOOP
 INSERT INTO d4.review_affected SELECT cid,l.attempt_id,d.id,l.operation_id,l.fencing_generation FROM public.operation_leases l JOIN public.operations x ON x.id=l.operation_id JOIN d3.dispatches a ON a.attempt_id=l.attempt_id JOIN d4.deliveries d ON d.dispatch_command_id=a.command_id WHERE (d4.case_blocks(cid,x.id,a.resource_id) OR d4.review_task_blocked(x.task_id,coalesce((x.policy_snapshot->>'integration_phase')::boolean,false))) AND NOT EXISTS(SELECT 1 FROM d4.review_affected old WHERE old.case_id=cid AND old.attempt_id=l.attempt_id);
 GET DIAGNOSTICS added_bound=ROW_COUNT;
 INSERT INTO d4.review_unbound_affected SELECT cid,l.attempt_id,l.operation_id,l.fencing_generation FROM public.operation_leases l JOIN public.operations x ON x.id=l.operation_id LEFT JOIN d2.reservations r ON r.operation_id=x.id WHERE (d4.case_blocks(cid,x.id,r.resource_id) OR d4.review_task_blocked(x.task_id,coalesce((x.policy_snapshot->>'integration_phase')::boolean,false))) AND NOT EXISTS(SELECT 1 FROM d4.review_affected a WHERE a.case_id=cid AND a.attempt_id=l.attempt_id) AND NOT EXISTS(SELECT 1 FROM d4.review_unbound_affected old WHERE old.case_id=cid AND old.attempt_id=l.attempt_id);
 GET DIAGNOSTICS added_unbound=ROW_COUNT;EXIT WHEN added_bound+added_unbound=0;END LOOP;
 result=jsonb_build_object('case_id',cid,'row_version',o.row_version+1,'affected',(SELECT count(*) FROM d4.review_affected WHERE case_id=cid));INSERT INTO d4.checkpoint_commands VALUES(cid,req,result);INSERT INTO public.outbox_events(aggregate_type,aggregate_id,event_type,payload) VALUES('OPERATION',oid,'D4_REVIEW_OPENED',result);RETURN result;
END $$;
CREATE FUNCTION d4.review_on_receipt() RETURNS trigger LANGUAGE plpgsql SECURITY DEFINER SET search_path=pg_catalog,public,d2,d3,d4 AS $$
BEGIN
 IF EXISTS(SELECT 1 FROM public.operations WHERE id=NEW.operation_id AND state IN ('COMPLETED','CANCELLED')) OR EXISTS(SELECT 1 FROM d4.recovery_settlements s WHERE s.operation_id=NEW.operation_id AND s.generation=NEW.generation) OR EXISTS(SELECT 1 FROM d4.checkpoints cp WHERE cp.operation_id=NEW.operation_id AND cp.source_generation=NEW.generation) OR EXISTS(SELECT 1 FROM d4.multi_checkpoints cp WHERE cp.operation_id=NEW.operation_id AND cp.source_generation=NEW.generation) THEN PERFORM d4.review_open(public.gen_random_uuid(),NEW.operation_id,NEW.generation,'New factual receipt after settlement or terminal outcome');END IF;RETURN NEW;
END $$;
CREATE TRIGGER reopen_review AFTER INSERT ON d2.effect_receipts FOR EACH ROW EXECUTE FUNCTION d4.review_on_receipt();
CREATE TABLE d4.review_containments(id uuid PRIMARY KEY,case_id uuid NOT NULL,attempt_id uuid NOT NULL,seal jsonb NOT NULL,FOREIGN KEY(case_id,attempt_id) REFERENCES d4.review_affected(case_id,attempt_id),UNIQUE(case_id,attempt_id));
CREATE TRIGGER immutable_fact BEFORE UPDATE OR DELETE OR TRUNCATE ON d4.review_containments FOR EACH STATEMENT EXECUTE FUNCTION public.d2_reject_fact_mutation();
CREATE FUNCTION d4.review_existing_close(delivery uuid) RETURNS uuid LANGUAGE plpgsql STABLE SECURITY DEFINER SET search_path=pg_catalog,public,d2,d3,d4 AS $$
DECLARE old uuid;
BEGIN
 SELECT (ct.seal->>'command')::uuid INTO old FROM d4.review_containments ct JOIN d4.review_affected a ON a.case_id=ct.case_id AND a.attempt_id=ct.attempt_id WHERE a.delivery_id=delivery LIMIT 1;IF FOUND THEN RETURN old;END IF;
 IF EXISTS(SELECT 1 FROM d4.recovery_proofs p JOIN d4.recovery_settlements s ON s.proof_id=p.id WHERE p.delivery_id=delivery) OR EXISTS(SELECT 1 FROM d4.multi_proofs p JOIN d4.multi_checkpoints cp ON cp.proof_id=p.id WHERE p.delivery_id=delivery) OR EXISTS(SELECT 1 FROM d4.checkpoint_requests r JOIN d4.checkpoints cp ON cp.request_id=r.id WHERE r.delivery_id=delivery) OR EXISTS(SELECT 1 FROM d4.checkpoint_commands WHERE request->>'action'='ACCEPT_CONTINUATION' AND request->>'delivery'=delivery::text) OR EXISTS(SELECT 1 FROM d4.lab_evidence WHERE delivery_id=delivery AND acceptance)
 THEN RETURN (d4.review_anchor(delivery)->>'close_command')::uuid;END IF;RETURN NULL;
END $$;
CREATE FUNCTION d4.review_contained(cid uuid,caseid uuid,attempt uuid,seal jsonb) RETURNS jsonb LANGUAGE plpgsql SECURITY DEFINER SET search_path=pg_catalog,public,d4 AS $$
DECLARE a d4.review_affected;i jsonb;old d4.review_containments;
BEGIN
 PERFORM d3.lock_state();SELECT * INTO STRICT a FROM d4.review_affected WHERE case_id=caseid AND attempt_id=attempt;i=d4.lab_inspect(a.delivery_id);SELECT * INTO old FROM d4.review_containments WHERE id=cid;
 IF FOUND THEN IF old.case_id IS DISTINCT FROM caseid OR old.attempt_id IS DISTINCT FROM attempt OR old.seal IS DISTINCT FROM seal THEN RAISE EXCEPTION 'Containment conflict' USING ERRCODE='23514';END IF;RETURN jsonb_build_object('containment_id',cid);END IF;
 IF NOT EXISTS(SELECT 1 FROM d4.open_reviews WHERE id=caseid) OR coalesce((seal->>'sequence')::bigint,0)<=0 OR seal->>'command' IS NULL
 OR EXISTS(SELECT 1 FROM jsonb_each(jsonb_build_object('operation',i->'operation','attempt',i->'attempt','worker',i->'worker','resource',i->'resource','generation',i->'generation')) x WHERE seal->'identity'->x.key IS DISTINCT FROM x.value)
 OR NOT EXISTS(SELECT 1 FROM d4.lab_grants WHERE request->>'delivery'=a.delivery_id::text AND response->>'receiver_id'=seal->>'receiverId') THEN RAISE EXCEPTION 'Bound closed containment proof required' USING ERRCODE='23514';END IF;
 INSERT INTO d4.review_containments VALUES(cid,caseid,attempt,seal);RETURN jsonb_build_object('containment_id',cid);
END $$;
CREATE FUNCTION d4.review_candidate_info(cid uuid) RETURNS jsonb LANGUAGE sql STABLE SECURITY DEFINER SET search_path=pg_catalog,public,d4 AS $$ SELECT coalesce((SELECT to_jsonb(t) FROM d4.review_candidates t WHERE id=cid),'null'::jsonb); $$;
CREATE FUNCTION d4.review_status(cid uuid,delivery uuid,head uuid,version bigint) RETURNS jsonb LANGUAGE plpgsql SECURITY DEFINER SET search_path=pg_catalog,public,d4 AS $$ DECLARE c d4.checkpoint_commands;BEGIN SELECT * INTO c FROM d4.checkpoint_commands WHERE id=cid;IF NOT FOUND THEN RETURN 'null'::jsonb;END IF;IF c.request->>'action' IS DISTINCT FROM 'REVIEW_REVISE' OR c.request->>'delivery' IS DISTINCT FROM delivery::text OR c.request->>'parent' IS DISTINCT FROM head::text OR c.request->>'version' IS DISTINCT FROM version::text THEN RAISE EXCEPTION 'Review replay conflict' USING ERRCODE='23514';END IF;RETURN c.response;END $$;

CREATE FUNCTION d4.review_case_info(caseid uuid) RETURNS jsonb LANGUAGE sql STABLE SECURITY DEFINER SET search_path=pg_catalog,public,d4 AS $$ SELECT to_jsonb(c)||jsonb_build_object('source_transport_known',c.delivery_id IS NOT NULL,'open',EXISTS(SELECT 1 FROM d4.open_reviews WHERE id=caseid),'unbound_affected',(SELECT coalesce(jsonb_agg(to_jsonb(u)),'[]') FROM d4.review_unbound_affected u WHERE u.case_id=caseid),'affected',(SELECT coalesce(jsonb_agg(to_jsonb(a)||jsonb_build_object('info',d4.lab_inspect(a.delivery_id),'close_command',d4.review_existing_close(a.delivery_id))),'[]') FROM d4.review_affected a WHERE a.case_id=caseid)) FROM d4.review_cases c WHERE c.id=caseid; $$;
CREATE FUNCTION d4.review_barrier(cid uuid,caseid uuid,attempt uuid,proof jsonb) RETURNS jsonb LANGUAGE plpgsql SECURITY DEFINER SET search_path=pg_catalog,public,d2,d3,d4 AS $$
DECLARE a d4.review_affected;i jsonb;old d4.review_barriers;
BEGIN
 PERFORM d3.lock_state();SELECT * INTO STRICT a FROM d4.review_affected WHERE case_id=caseid AND attempt_id=attempt;i=d4.lab_inspect(a.delivery_id);SELECT * INTO old FROM d4.review_barriers WHERE id=cid;
 IF FOUND THEN IF old.case_id IS DISTINCT FROM caseid OR old.attempt_id IS DISTINCT FROM attempt OR old.proof IS DISTINCT FROM proof THEN RAISE EXCEPTION 'Barrier replay conflict' USING ERRCODE='23514';END IF;RETURN jsonb_build_object('barrier_id',cid);END IF;
 IF NOT EXISTS(SELECT 1 FROM d4.review_containments ct WHERE ct.case_id=caseid AND ct.attempt_id=attempt AND ct.seal=proof->'receiver_seal') OR proof->'process_stopped' IS DISTINCT FROM 'true'::jsonb OR proof->'receiver_closed' IS DISTINCT FROM 'true'::jsonb OR coalesce(proof->>'host_observation_hash','') !~ '^[a-f0-9]{64}$' OR coalesce((proof->'receiver_seal'->>'sequence')::bigint,0)<=0 OR proof->>'schema' IS DISTINCT FROM 'd4.review.barrier.v1' OR proof->>'context_hash' IS DISTINCT FROM i->>'context_hash' OR proof->>'policy_hash' IS DISTINCT FROM i->>'policy_hash' OR NOT EXISTS(SELECT 1 FROM d4.open_reviews WHERE id=caseid)
 OR EXISTS(SELECT 1 FROM jsonb_each(jsonb_build_object('operation',i->'operation','attempt',i->'attempt','worker',i->'worker','resource',i->'resource','generation',i->'generation')) x WHERE proof->x.key IS DISTINCT FROM x.value OR proof->'receiver_seal'->'identity'->x.key IS DISTINCT FROM x.value)
 OR NOT EXISTS(SELECT 1 FROM d4.lab_grants WHERE request->>'delivery'=a.delivery_id::text AND response->>'receiver_id'=proof->'receiver_seal'->>'receiverId') THEN RAISE EXCEPTION 'Independent closed stop barrier required' USING ERRCODE='23514';END IF;
 INSERT INTO d4.review_barriers VALUES(cid,caseid,attempt,proof);RETURN jsonb_build_object('barrier_id',cid);
END $$;
CREATE FUNCTION d4.review_close(cid uuid,caseid uuid,revision uuid,reason text) RETURNS jsonb LANGUAGE plpgsql SECURITY DEFINER SET search_path=pg_catalog,public,d2,d3,d4 AS $$
DECLARE req jsonb=jsonb_build_object('action','REVIEW_CLOSE','case',caseid,'revision',revision,'reason',reason);prior jsonb;c d4.review_cases;h d4.review_heads;result jsonb;
BEGIN
 PERFORM d3.lock_state();prior=d4.checkpoint_previous(cid,req);IF prior IS NOT NULL THEN RETURN prior;END IF;SELECT * INTO STRICT c FROM d4.open_reviews WHERE id=caseid;SELECT * INTO STRICT h FROM d4.review_heads WHERE id=revision AND delivery_id=c.delivery_id;
 IF EXISTS(SELECT 1 FROM d4.review_unbound_affected WHERE case_id=caseid) OR NOT d4.review_accounting_current(c.delivery_id) OR NOT d4.revision_current(revision) OR reason IS NULL OR length(btrim(reason)) NOT BETWEEN 1 AND 512 OR EXISTS(SELECT 1 FROM d4.review_affected a WHERE a.case_id=caseid AND (NOT EXISTS(SELECT 1 FROM d4.review_barriers b WHERE b.case_id=caseid AND b.attempt_id=a.attempt_id) OR EXISTS(SELECT 1 FROM public.operation_leases l JOIN public.operations o ON o.id=l.operation_id WHERE l.attempt_id=a.attempt_id AND (l.expires_at>clock_timestamp() OR (o.state NOT IN ('RECONCILING','BLOCKED_APPROVAL') AND NOT (o.state='VERIFYING' AND EXISTS(SELECT 1 FROM d4.recovery_settlements rs WHERE rs.operation_id=o.id AND rs.generation=l.fencing_generation AND rs.terminal AND d4.recovery_current(rs.id))))))))
 THEN RAISE EXCEPTION 'Current revision and every independent containment barrier required' USING ERRCODE='23514';END IF;
 INSERT INTO d4.review_closures VALUES(cid,caseid,revision,reason);result=jsonb_build_object('closed',true,'case_id',caseid);INSERT INTO d4.checkpoint_commands VALUES(cid,req,result);INSERT INTO public.outbox_events(aggregate_type,aggregate_id,event_type,payload) VALUES('OPERATION',c.operation_id,'D4_REVIEW_CLOSED',result);RETURN result;
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
 OR EXISTS(SELECT 1 FROM public.execution_evidence e JOIN d3.dispatches ds ON ds.attempt_id=e.attempt_id WHERE ds.operation_id=o.id AND ds.generation=h.generation AND e.evidence_type='ACCEPTANCE_FAIL') OR EXISTS(SELECT 1 FROM d2.reservation_balances b JOIN d2.reservations r ON r.id=b.reservation_id JOIN d2.accounts ac ON ac.id=b.account_id WHERE r.operation_id=o.id AND (b.outstanding<>0 OR clock_timestamp()<ac.window_start OR clock_timestamp()>=ac.window_end OR (EXISTS(SELECT 1 FROM d4.checkpoints WHERE id=checkpoint) AND b.consumed<>4)))
 OR NOT (EXISTS(SELECT 1 FROM d4.multi_heads cp WHERE cp.id=checkpoint AND cp.operation_id=o.id AND cp.source_generation=h.generation AND NOT EXISTS(SELECT 1 FROM d4.multi_links WHERE checkpoint_id=cp.id) AND d4.multi_head_settled(o.id)) OR EXISTS(SELECT 1 FROM d4.checkpoints cp WHERE cp.id=checkpoint AND cp.operation_id=o.id AND cp.source_generation=h.generation AND NOT EXISTS(SELECT 1 FROM d4.continuation_links WHERE checkpoint_id=cp.id))) THEN RAISE EXCEPTION 'Current unused reviewed checkpoint required' USING ERRCODE='23514';END IF;
 UPDATE public.operations SET state='READY',row_version=row_version+1 WHERE id=o.id;IF o.state='CANCELLED' THEN PERFORM d2.record_transition(cid,'OPERATION',o.id,'CANCELLED','READY',o.row_version+1,'CONTROL_PLANE','Explicit reviewed checkpoint');END IF;
 IF EXISTS(SELECT 1 FROM d4.multi_checkpoints WHERE id=checkpoint) THEN INSERT INTO d4.multi_authorizations SELECT cid,checkpoint,o.row_version+1,reason WHERE NOT EXISTS(SELECT 1 FROM d4.multi_authorizations WHERE checkpoint_id=checkpoint);
 ELSE INSERT INTO d4.continuation_authorizations SELECT cid,checkpoint,reason,o.row_version+1 WHERE NOT EXISTS(SELECT 1 FROM d4.continuation_authorizations WHERE checkpoint_id=checkpoint);END IF;
 INSERT INTO d4.review_authorizations VALUES(cid,checkpoint,revision,o.row_version+1,reason);result=jsonb_build_object('state','READY','row_version',o.row_version+1);INSERT INTO d4.checkpoint_commands VALUES(cid,req,result);RETURN result;
END $$;

CREATE FUNCTION d4.review_candidate(cid uuid,delivery uuid,receiver uuid,step text,receipt jsonb) RETURNS jsonb LANGUAGE plpgsql SECURITY DEFINER SET search_path=pg_catalog,public,d4 AS $$
DECLARE old d4.review_candidates;i jsonb=d4.recovery_info(delivery);
BEGIN
 PERFORM d3.lock_state();SELECT * INTO old FROM d4.review_candidates WHERE id=cid;IF FOUND THEN IF old.delivery_id IS DISTINCT FROM delivery OR old.receiver_id IS DISTINCT FROM receiver OR old.step IS DISTINCT FROM step OR old.receipt IS DISTINCT FROM receipt THEN RAISE EXCEPTION 'Candidate conflict' USING ERRCODE='23514';END IF;RETURN jsonb_build_object('candidate_id',cid);END IF;
 IF cid IS NULL OR receipt->'generation' IS DISTINCT FROM i->'generation' OR receipt->>'status' IS NULL OR receipt->>'status' NOT IN ('UNKNOWN','APPLIED','ABSENT') OR NOT EXISTS(SELECT 1 FROM d4.lab_grants WHERE request->>'delivery'=delivery::text AND response->>'receiver_id'=receiver::text) OR NOT EXISTS(SELECT 1 FROM jsonb_array_elements(i->'recovery_manifest'->'steps') s WHERE s->>'id'=step) THEN RAISE EXCEPTION 'Bound observed candidate required' USING ERRCODE='23514';END IF;
 INSERT INTO d4.review_candidates VALUES(cid,delivery,receiver,step,receipt);RETURN jsonb_build_object('candidate_id',cid);
END $$;
CREATE FUNCTION d4.review_ingest(cid uuid,candidate uuid) RETURNS jsonb LANGUAGE plpgsql SECURITY DEFINER SET search_path=pg_catalog,public,d4 AS $$
DECLARE c d4.review_candidates;req jsonb=jsonb_build_object('action','REVIEW_INGEST','candidate',candidate);prior jsonb;result jsonb;observed jsonb;
BEGIN PERFORM d3.lock_state();prior=d4.checkpoint_previous(cid,req);IF prior IS NOT NULL THEN RETURN prior;END IF;SELECT * INTO STRICT c FROM d4.review_candidates WHERE id=candidate;observed=d4.recovery_observe(cid,c.delivery_id,c.receiver_id,c.step,c.receipt);result=jsonb_build_object('observation',observed,'delivery_id',c.delivery_id,'case_ids',(SELECT coalesce(jsonb_agg(id),'[]') FROM d4.open_reviews WHERE delivery_id=c.delivery_id));INSERT INTO d4.checkpoint_commands VALUES(cid,req,result);RETURN result;END $$;

CREATE FUNCTION d4.review_info(delivery uuid) RETURNS jsonb LANGUAGE sql STABLE SECURITY DEFINER SET search_path=pg_catalog,public,d4 AS $$ SELECT d4.review_anchor(delivery)||jsonb_build_object('row_version',(SELECT row_version FROM public.operations WHERE id=(d4.recovery_info(delivery)->>'operation')::uuid),'effective_task_eligible',(SELECT d2.task_eligible(task_id) FROM public.operations WHERE id=(d4.recovery_info(delivery)->>'operation')::uuid),'effective_integration_eligible',(SELECT d2.integration_eligible(task_id) FROM public.operations WHERE id=(d4.recovery_info(delivery)->>'operation')::uuid),'cases',(SELECT coalesce(jsonb_agg(to_jsonb(c)),'[]') FROM d4.open_reviews c WHERE c.delivery_id=delivery)); $$;
CREATE FUNCTION d4.review_audit() RETURNS jsonb LANGUAGE sql SECURITY DEFINER SET search_path=pg_catalog,public,d4 AS $$ SELECT d4.absence_audit()||jsonb_build_object('review_revisions',(SELECT coalesce(jsonb_agg(to_jsonb(t)),'[]') FROM d4.review_revisions t),'review_cases',(SELECT coalesce(jsonb_agg(to_jsonb(t)),'[]') FROM d4.review_cases t),'review_unbound_affected',(SELECT coalesce(jsonb_agg(to_jsonb(t)),'[]') FROM d4.review_unbound_affected t),'review_affected',(SELECT coalesce(jsonb_agg(to_jsonb(t)),'[]') FROM d4.review_affected t),'review_barriers',(SELECT coalesce(jsonb_agg(to_jsonb(t)),'[]') FROM d4.review_barriers t),'review_closures',(SELECT coalesce(jsonb_agg(to_jsonb(t)),'[]') FROM d4.review_closures t),'review_authorizations',(SELECT coalesce(jsonb_agg(to_jsonb(t)),'[]') FROM d4.review_authorizations t),'review_links',(SELECT coalesce(jsonb_agg(to_jsonb(t)),'[]') FROM d4.review_links t),'review_containments',(SELECT coalesce(jsonb_agg(to_jsonb(t)),'[]') FROM d4.review_containments t)); $$;
ALTER FUNCTION d3.state_relations() RENAME TO state_relations_before_review;
CREATE FUNCTION d3.state_relations() RETURNS text[] LANGUAGE sql IMMUTABLE AS $$ SELECT d3.state_relations_before_review()||ARRAY['d4.review_revisions','d4.review_cases','d4.review_unbound_affected','d4.review_affected','d4.review_barriers','d4.review_closures','d4.review_authorizations','d4.review_links','d4.review_candidates','d4.recovery_observations','d4.review_containments']; $$;

CREATE FUNCTION d4.require_unheld(oid uuid,rid uuid) RETURNS void LANGUAGE plpgsql SECURITY DEFINER SET search_path=pg_catalog,public,d4 AS $$ BEGIN IF d4.review_blocked(oid,rid,coalesce((SELECT (policy_snapshot->>'integration_phase')::boolean FROM public.operations WHERE id=oid),false)) THEN RAISE EXCEPTION 'Physical/effective acceptance quarantine' USING ERRCODE='23514';END IF;END $$;
-- Runtime D2 contract extension approved by A22; historical source migrations stay unchanged.
ALTER FUNCTION d2.task_eligible(uuid) RENAME TO task_eligible_before_review;
CREATE FUNCTION d2.task_eligible(tid uuid) RETURNS boolean LANGUAGE sql STABLE SECURITY DEFINER SET search_path=pg_catalog,public,d2,d4 AS $$ SELECT d2.task_eligible_before_review(tid) AND NOT d4.review_task_blocked(tid,false); $$;
ALTER FUNCTION d2.integration_eligible(uuid) RENAME TO integration_eligible_before_review;
CREATE FUNCTION d2.integration_eligible(tid uuid) RETURNS boolean LANGUAGE sql STABLE SECURITY DEFINER SET search_path=pg_catalog,public,d2,d4 AS $$ SELECT d2.integration_eligible_before_review(tid) AND NOT d4.review_task_blocked(tid,true); $$;
ALTER FUNCTION d4.continuation_safe(uuid,bigint) RENAME TO continuation_safe_before_review;
CREATE FUNCTION d4.continuation_safe(oid uuid,gen bigint) RETURNS boolean LANGUAGE sql STABLE SECURITY DEFINER SET search_path=pg_catalog,public,d2,d4 AS $$ SELECT (d4.continuation_safe_before_review(oid,gen) OR d4.review_checkpoint_safe(oid,gen)) AND NOT d4.review_blocked(oid,(SELECT resource_id FROM d2.reservations WHERE operation_id=oid),coalesce((SELECT (policy_snapshot->>'integration_phase')::boolean FROM public.operations WHERE id=oid),false)); $$;
ALTER VIEW d4.continuation_admissions RENAME TO admissions_before_review;
CREATE VIEW d4.continuation_admissions AS SELECT a.operation_id,a.generation,a.checkpoint_id,a.authorization_id,a.manifest_hash,a.admission_kind,a.eligible AND NOT d4.review_blocked(a.operation_id,(SELECT resource_id FROM d2.reservations WHERE operation_id=a.operation_id),false) eligible FROM d4.admissions_before_review a
 UNION ALL SELECT h.operation_id,h.generation,a.checkpoint_id,a.id,h.proof->>'manifest_hash','SEALED_REVIEW_CHECKPOINT',d4.review_checkpoint_safe(h.operation_id,h.generation) AND a.authorized_version=(SELECT row_version FROM public.operations WHERE id=h.operation_id) FROM d4.review_authorizations a JOIN d4.review_heads h ON h.id=a.revision_id;

CREATE FUNCTION d4.review_barrier_status(caseid uuid,attempt uuid) RETURNS jsonb LANGUAGE sql STABLE SECURITY DEFINER SET search_path=pg_catalog,public,d4 AS $$ SELECT coalesce((SELECT jsonb_build_object('barrier_id',id) FROM d4.review_barriers WHERE case_id=caseid AND attempt_id=attempt),'null'::jsonb); $$;

-- Contradictory acceptance facts are never erased or silently superseded by PASS.
CREATE FUNCTION d4.review_on_failure() RETURNS trigger LANGUAGE plpgsql SECURITY DEFINER SET search_path=pg_catalog,public,d2,d3,d4 AS $$
DECLARE a public.execution_attempts;
BEGIN IF NEW.evidence_type='ACCEPTANCE_FAIL' THEN SELECT * INTO STRICT a FROM public.execution_attempts WHERE id=NEW.attempt_id;
 IF EXISTS(SELECT 1 FROM public.operations WHERE id=a.operation_id AND state IN ('COMPLETED','CANCELLED')) OR EXISTS(SELECT 1 FROM d4.recovery_settlements WHERE operation_id=a.operation_id AND generation=a.lease_generation) OR EXISTS(SELECT 1 FROM d4.multi_checkpoints WHERE operation_id=a.operation_id AND source_generation=a.lease_generation) OR EXISTS(SELECT 1 FROM d4.checkpoints WHERE operation_id=a.operation_id AND source_generation=a.lease_generation)
 THEN PERFORM d4.review_open(public.gen_random_uuid(),a.operation_id,a.lease_generation,'New acceptance failure after settlement or terminal outcome');END IF;END IF;RETURN NEW;END $$;
CREATE TRIGGER reopen_review_on_failure AFTER INSERT ON public.execution_evidence FOR EACH ROW EXECUTE FUNCTION d4.review_on_failure();


CREATE OR REPLACE FUNCTION d3.state_body() RETURNS jsonb LANGUAGE plpgsql STABLE SECURITY DEFINER
SET search_path=pg_catalog,public,d2,d3 SET TimeZone='UTC' AS $$
DECLARE rel text;rows jsonb;body jsonb='{}';
BEGIN
  FOREACH rel IN ARRAY d3.state_relations() LOOP
    EXECUTE format('SELECT coalesce(jsonb_agg(to_jsonb(t) ORDER BY to_jsonb(t)::text COLLATE "C"),''[]''::jsonb) FROM %s t',rel) INTO rows;
    body=jsonb_set(body,ARRAY[rel],rows);
  END LOOP;
  body=body||jsonb_build_object(
    'balances',(SELECT coalesce(jsonb_agg(to_jsonb(b) ORDER BY account_id,pool),'[]') FROM d2.balances b),
    'reservation_balances',(SELECT coalesce(jsonb_agg(to_jsonb(b) ORDER BY reservation_id,account_id),'[]') FROM d2.reservation_balances b),
    'blocking_edges',(SELECT coalesce(jsonb_agg(to_jsonb(e) ORDER BY a,b),'[]') FROM d2.active_blocking_edges e),
    'lane_usage',(SELECT coalesce(jsonb_agg(to_jsonb(u) ORDER BY account_id,lane),'[]') FROM d3.lane_usage u),
    'eligible_intervals',(SELECT coalesce(jsonb_agg(to_jsonb(i) ORDER BY operation_id,observed_at),'[]') FROM d3.eligible_intervals i),
    'task_guards',(SELECT coalesce(jsonb_agg(jsonb_build_object('task_id',t.id,'eligible',d2.task_eligible(t.id),
      'integration',d2.integration_eligible(t.id) AND NOT EXISTS(SELECT 1 FROM public.task_dependencies d WHERE d.successor_task_id=t.id AND d.kind='MOCKABLE')) ORDER BY t.id),'[]') FROM public.tasks t),
    'resource_compatibility',(SELECT coalesce(jsonb_agg(jsonb_build_object('resource_id',r.id,'operation_id',o.id) ORDER BY r.id,o.id),'[]')
      FROM public.resources r JOIN public.workers w ON w.id=r.worker_id CROSS JOIN public.operations o
      WHERE NOT d4.review_blocked(o.id,r.id,coalesce((o.policy_snapshot->>'integration_phase')::boolean,false)) AND r.capabilities @> coalesce(o.policy_snapshot->'required_capabilities','{}') AND w.capabilities @> coalesce(o.policy_snapshot->'required_capabilities','{}')));
  RETURN body;
END $$;

CREATE OR REPLACE FUNCTION d2.execution(cid uuid,req jsonb) RETURNS jsonb
LANGUAGE plpgsql SECURITY DEFINER SET search_path=pg_catalog,public,d2 AS $$
DECLARE prior jsonb;result jsonb;op public.operations;attempt public.execution_attempts;lease public.operation_leases;
 action text=req->>'action';wid uuid=(req->>'worker_id')::uuid;rid uuid=(req->>'resource_id')::uuid;aid uuid;gen bigint;old_state text;new_state text;
 cap_result jsonb;resid uuid;rec d2.effect_receipts;expiry timestamptz;policy_hash text; approval_ok boolean;
BEGIN
 PERFORM d3.lock_state();
 prior=d2.begin_command(cid,req);IF prior IS NOT NULL THEN RETURN prior;END IF;
 SELECT * INTO op FROM public.operations WHERE id=(req->>'operation_id')::uuid FOR UPDATE SKIP LOCKED;
 IF NOT FOUND THEN RAISE EXCEPTION 'Operation unavailable or locked' USING ERRCODE='23514'; END IF;
 old_state=op.state;
 IF action IN ('CLAIM','START','HEARTBEAT','VERIFY','RECOVERY_VERIFY','RECONCILE','RESUME_RECONCILIATION','REJECT_VERIFICATION') THEN PERFORM d4.require_unheld(op.id,coalesce(rid,(SELECT resource_id FROM d2.reservations WHERE operation_id=op.id)));END IF;
 IF action='CLAIM' THEN
  IF coalesce((op.policy_snapshot->>'max_attempts')::int,3) NOT BETWEEN 1 AND 20 THEN RAISE EXCEPTION 'Retry policy must be bounded 1..20' USING ERRCODE='23514'; END IF;
  IF (SELECT count(*) FROM public.execution_attempts WHERE operation_id=op.id)>=coalesce((op.policy_snapshot->>'max_attempts')::int,3) THEN RAISE EXCEPTION 'Bounded retry limit reached' USING ERRCODE='23514'; END IF;
  IF op.state<>'READY' OR EXISTS(SELECT 1 FROM public.operation_leases WHERE operation_id=op.id) THEN RAISE EXCEPTION 'Operation not claimable' USING ERRCODE='23514'; END IF;
  IF NOT d2.task_eligible(op.task_id) THEN RAISE EXCEPTION 'Dependency unavailable' USING ERRCODE='23514'; END IF;
  IF NOT EXISTS(SELECT 1 FROM public.resources WHERE id=rid AND worker_id=wid AND enabled AND capabilities @> coalesce(op.policy_snapshot->'required_capabilities','{}'::jsonb)) OR NOT EXISTS(SELECT 1 FROM public.workers WHERE id=wid AND state='ONLINE' AND capabilities @> coalesce(op.policy_snapshot->'required_capabilities','{}'::jsonb)) THEN RAISE EXCEPTION 'Resource/worker unavailable' USING ERRCODE='23514'; END IF;
  IF coalesce((op.policy_snapshot->>'requires_approval')::boolean,false) THEN
   policy_hash=encode(public.digest(op.policy_snapshot::text,'sha256'),'hex');
   SELECT EXISTS(SELECT 1 FROM public.approvals a WHERE a.operation_id=op.id AND a.state='APPROVED' AND a.expires_at>clock_timestamp() AND a.context_snapshot_sha256=op.context_pack_sha256 AND a.policy_snapshot_sha256=policy_hash) INTO approval_ok;
   IF NOT approval_ok THEN RAISE EXCEPTION 'Approval denied, expired or stale' USING ERRCODE='23514'; END IF;
  END IF;
  IF EXISTS(SELECT 1 FROM d2.operation_accounts m JOIN d2.accounts a ON a.id=m.account_id WHERE m.operation_id=op.id AND a.resource_id<>rid) THEN RAISE EXCEPTION 'Capacity resource mismatch' USING ERRCODE='23514'; END IF;
  SELECT id INTO resid FROM d2.reservations WHERE operation_id=op.id;
  IF resid IS NULL THEN
   cap_result=d2.capacity(public.gen_random_uuid(),jsonb_build_object('action','RESERVE','operation_id',op.id,'pool',coalesce(req->>'pool','PLANNED'),'reason','Atomic claim'));
   resid=(cap_result->>'reservation_id')::uuid;
  ELSE
   PERFORM d2.capacity(public.gen_random_uuid(),jsonb_build_object('action','TOP_UP','reservation_id',resid,'reason','Bounded retry commitment'));
  END IF;
  gen=op.lease_generation+1;aid=public.gen_random_uuid();
  INSERT INTO public.execution_attempts(id,operation_id,attempt_no,worker_id,resource_id,lease_generation,state,started_at)
   VALUES(aid,op.id,(SELECT coalesce(max(attempt_no),0)+1 FROM public.execution_attempts WHERE operation_id=op.id),wid,rid,gen,'LEASED',clock_timestamp());
  INSERT INTO public.operation_leases VALUES(op.id,aid,wid,gen,clock_timestamp()+interval '60 seconds');
  new_state='LEASED';UPDATE public.operations SET state=new_state,lease_generation=gen,row_version=row_version+1 WHERE id=op.id;
  result=jsonb_build_object('attempt_id',aid,'generation',gen,'reservation_id',resid);
 ELSE
  SELECT * INTO STRICT lease FROM public.operation_leases WHERE operation_id=op.id;
  SELECT * INTO STRICT attempt FROM public.execution_attempts WHERE id=lease.attempt_id;
  IF action='RESUME_RECONCILIATION' THEN
   IF op.state<>'BLOCKED_APPROVAL' OR NOT EXISTS(SELECT 1 FROM d2.effect_receipts WHERE id=(req->>'receipt_id')::uuid AND operation_id=op.id AND generation=op.lease_generation AND status<>'UNKNOWN') THEN RAISE EXCEPTION 'New authoritative evidence required' USING ERRCODE='23514'; END IF;
   new_state='RECONCILING';result=jsonb_build_object('state',new_state);
  ELSIF action='RECOVERY_VERIFY' THEN
   IF op.state<>'VERIFYING' OR NOT EXISTS(SELECT 1 FROM d2.effect_receipts WHERE id=(req->>'receipt_id')::uuid AND operation_id=op.id AND generation=op.lease_generation AND status='APPLIED') OR NOT EXISTS(SELECT 1 FROM public.execution_evidence WHERE attempt_id=lease.attempt_id AND evidence_type='ACCEPTANCE_PASS') OR EXISTS(SELECT 1 FROM public.execution_evidence WHERE attempt_id=lease.attempt_id AND evidence_type='ACCEPTANCE_FAIL') OR NOT d2.integration_eligible(op.task_id) THEN RAISE EXCEPTION 'Applied effect and acceptance evidence required' USING ERRCODE='23514'; END IF;
   SELECT id INTO STRICT resid FROM d2.reservations WHERE operation_id=op.id;
   PERFORM d2.capacity(public.gen_random_uuid(),jsonb_build_object('action','CONSUME','reservation_id',resid,'entries',req->'entries','reason','Recovered external effect'));
   new_state='COMPLETED';DELETE FROM public.operation_leases WHERE operation_id=op.id;result=jsonb_build_object('state',new_state);
  ELSIF action='EXPIRE' THEN
   IF lease.expires_at>clock_timestamp() OR op.state NOT IN ('LEASED','RUNNING','VERIFYING') THEN RAISE EXCEPTION 'Not an expired active lease' USING ERRCODE='23514'; END IF;
   new_state='RECONCILING';result=jsonb_build_object('state',new_state);
  ELSIF action='RECONCILE' THEN
   IF op.state<>'RECONCILING' THEN RAISE EXCEPTION 'Reconciliation state required' USING ERRCODE='23514'; END IF;
   SELECT * INTO STRICT rec FROM d2.effect_receipts WHERE id=(req->>'receipt_id')::uuid AND operation_id=op.id AND generation=op.lease_generation;
   new_state=CASE rec.status WHEN 'APPLIED' THEN 'VERIFYING' WHEN 'ABSENT' THEN 'RETRY_PENDING' ELSE 'BLOCKED_APPROVAL' END;
   IF rec.status='ABSENT' THEN DELETE FROM public.operation_leases WHERE operation_id=op.id; END IF;
   result=jsonb_build_object('state',new_state,'effect_status',rec.status);
  ELSE
   IF action IN ('START','HEARTBEAT') AND EXISTS(SELECT 1 FROM d2.execution_snapshots x WHERE x.attempt_id=lease.attempt_id AND (x.context_sha256 IS DISTINCT FROM op.context_pack_sha256 OR x.policy_snapshot IS DISTINCT FROM op.policy_snapshot)) THEN RAISE EXCEPTION 'Execution snapshot changed' USING ERRCODE='23514'; END IF;
   IF action IN ('START','HEARTBEAT') AND coalesce((op.policy_snapshot->>'requires_approval')::boolean,false) AND NOT EXISTS(SELECT 1 FROM public.approvals a WHERE a.operation_id=op.id AND a.state='APPROVED' AND a.expires_at>clock_timestamp() AND a.context_snapshot_sha256=op.context_pack_sha256 AND a.policy_snapshot_sha256=encode(public.digest(op.policy_snapshot::text,'sha256'),'hex')) THEN RAISE EXCEPTION 'Approval expired or changed' USING ERRCODE='23514'; END IF;
   IF lease.expires_at<=clock_timestamp() OR lease.fencing_generation<>op.lease_generation OR lease.attempt_id IS DISTINCT FROM (req->>'attempt_id')::uuid OR lease.fencing_generation IS DISTINCT FROM (req->>'generation')::bigint OR lease.worker_id IS DISTINCT FROM wid OR attempt.resource_id IS DISTINCT FROM rid THEN RAISE EXCEPTION 'Stale or mismatched fencing' USING ERRCODE='23514'; END IF;
   IF action='HEARTBEAT' THEN
    IF op.state NOT IN ('LEASED','RUNNING','VERIFYING') THEN RAISE EXCEPTION 'No renewable active execution' USING ERRCODE='23514'; END IF;
    UPDATE public.operation_leases SET expires_at=clock_timestamp()+interval '60 seconds' WHERE operation_id=op.id;
    result=jsonb_build_object('renewed',true);
   ELSIF action='START' AND op.state='LEASED' THEN new_state='RUNNING';result=jsonb_build_object('state',new_state);
   ELSIF action='CALLBACK' AND op.state='RUNNING' THEN
    SELECT id INTO STRICT resid FROM d2.reservations WHERE operation_id=op.id;
    cap_result=d2.capacity(public.gen_random_uuid(),jsonb_build_object('action','CONSUME','reservation_id',resid,'entries',req->'entries','reason','Fenced callback'));
    new_state='VERIFYING';UPDATE public.execution_attempts SET state='VERIFYING',finished_at=clock_timestamp() WHERE id=lease.attempt_id;
    result=jsonb_build_object('state',new_state);
   ELSIF action='REJECT_VERIFICATION' AND op.state='VERIFYING' THEN
    IF NOT EXISTS(SELECT 1 FROM public.execution_evidence WHERE attempt_id=lease.attempt_id AND evidence_type='ACCEPTANCE_FAIL') THEN RAISE EXCEPTION 'Failed acceptance evidence required' USING ERRCODE='23514'; END IF;
    new_state=CASE WHEN (SELECT count(*) FROM public.execution_attempts WHERE operation_id=op.id)<coalesce((op.policy_snapshot->>'max_attempts')::int,3) THEN 'RETRY_PENDING' ELSE 'FAILED' END;
    UPDATE public.execution_attempts SET state='FAILED',finished_at=clock_timestamp() WHERE id=lease.attempt_id;
    DELETE FROM public.operation_leases WHERE operation_id=op.id;result=jsonb_build_object('state',new_state);
   ELSIF action='VERIFY' AND op.state='VERIFYING' THEN
    IF NOT EXISTS(SELECT 1 FROM public.execution_evidence WHERE attempt_id=lease.attempt_id AND evidence_type='ACCEPTANCE_PASS') OR EXISTS(SELECT 1 FROM public.execution_evidence WHERE attempt_id=lease.attempt_id AND evidence_type='ACCEPTANCE_FAIL') OR NOT d2.integration_eligible(op.task_id) THEN RAISE EXCEPTION 'Acceptance and compatible dependencies required' USING ERRCODE='23514'; END IF;
    new_state='COMPLETED';DELETE FROM public.operation_leases WHERE operation_id=op.id;result=jsonb_build_object('state',new_state);
   ELSE RAISE EXCEPTION 'Invalid execution action/state' USING ERRCODE='23514'; END IF;
  END IF;
  IF new_state IS NOT NULL THEN UPDATE public.operations SET state=new_state,row_version=row_version+1 WHERE id=op.id; END IF;
 END IF;
 IF new_state IS NOT NULL THEN
  UPDATE public.execution_attempts SET state=CASE WHEN new_state='RETRY_PENDING' THEN 'FAILED' WHEN new_state='BLOCKED_APPROVAL' THEN 'RECONCILING' ELSE new_state END,finished_at=CASE WHEN new_state IN ('COMPLETED','FAILED','RETRY_PENDING') THEN clock_timestamp() ELSE finished_at END WHERE id=coalesce(aid,lease.attempt_id);
  PERFORM d2.record_transition(cid,'OPERATION',op.id,old_state,new_state,op.row_version+1,'CONTROL_PLANE',action);END IF;
 INSERT INTO d2.commands VALUES(cid,req,result,clock_timestamp());RETURN result;
END $$;

CREATE OR REPLACE FUNCTION d3.execution(cid uuid,req jsonb) RETURNS jsonb LANGUAGE plpgsql SECURITY DEFINER
SET search_path=pg_catalog,public,d2,d3 SET TimeZone='UTC' AS $$
DECLARE prior jsonb;result jsonb;action text=req->>'action';d d3.dispatches;op public.operations;
  now_at timestamptz;renew_until timestamptz;
BEGIN
  IF action IS NULL OR action NOT IN ('START','HEARTBEAT','CALLBACK','VERIFY','REJECT_VERIFICATION','EXPIRE','RECONCILE','RESUME_RECONCILIATION','RECOVERY_VERIFY') THEN
    RAISE EXCEPTION 'Unsupported D3 lifecycle action' USING ERRCODE='23514';END IF;
  IF current_setting('transaction_isolation')<>'read committed' THEN RAISE EXCEPTION 'Execution requires READ COMMITTED' USING ERRCODE='25001';END IF;
  PERFORM d3.lock_state();prior=d3.previous_command(cid,req);IF prior IS NOT NULL THEN RETURN prior;END IF;
  SELECT ds.* INTO STRICT d FROM d3.dispatches ds JOIN public.operation_leases l ON l.attempt_id=ds.attempt_id
    WHERE l.operation_id=(req->>'operation_id')::uuid;
  SELECT * INTO STRICT op FROM public.operations WHERE id=d.operation_id;
  -- Even reconciliation commands must identify the precise D3 attempt. D2's
  -- administrative recovery branches do not all enforce caller fencing.
  IF (req->>'attempt_id')::uuid IS DISTINCT FROM d.attempt_id OR (req->>'generation')::bigint IS DISTINCT FROM d.generation
    OR (req->>'worker_id')::uuid IS DISTINCT FROM d.worker_id OR (req->>'resource_id')::uuid IS DISTINCT FROM d.resource_id THEN
    RAISE EXCEPTION 'D3 attempt identity/fencing mismatch' USING ERRCODE='23514';END IF;
  IF (action='RECONCILE' AND EXISTS(SELECT 1 FROM d2.effect_receipts WHERE id=(req->>'receipt_id')::uuid AND operation_id=op.id AND generation=d.generation AND status='ABSENT')
      AND EXISTS(SELECT 1 FROM d2.effect_receipts WHERE operation_id=op.id AND generation=d.generation AND status<>'ABSENT'))
    OR (action='RECOVERY_VERIFY' AND EXISTS(SELECT 1 FROM d2.effect_receipts WHERE operation_id=op.id AND generation=d.generation AND status<>'APPLIED')) THEN
    RAISE EXCEPTION 'Contradictory effect evidence cannot remove physical exclusion; conclusive reconciliation required' USING ERRCODE='23514';END IF;
  IF action IN ('START','HEARTBEAT','VERIFY','RECOVERY_VERIFY','RECONCILE','RESUME_RECONCILIATION','REJECT_VERIFICATION') THEN PERFORM d4.require_unheld(op.id,d.resource_id);END IF;
  IF action IN ('START','HEARTBEAT') THEN
    now_at=clock_timestamp();renew_until=now_at+interval '60 seconds';
    IF NOT EXISTS(SELECT 1 FROM d3.plan_head h JOIN public.planning_runs pr ON pr.id=h.planning_run_id
      JOIN d3.plan_manifests m ON m.planning_run_id=pr.id CROSS JOIN LATERAL jsonb_array_elements(m.result->'decisions') x
      WHERE pr.status='PUBLISHED' AND pr.horizon_end>renew_until AND x->>'operationId'=op.id::text
      AND (x->>'resourceId')::uuid=d.resource_id AND x->>'disposition' IN ('TENTATIVE','CARRIED'))
      OR NOT EXISTS(SELECT 1 FROM public.projects p JOIN public.tasks t ON t.project_id=p.id WHERE t.id=op.task_id AND p.status='ACTIVE' AND t.status NOT IN ('DONE','FAILED','CANCELLED'))
      OR NOT d2.task_eligible(op.task_id)
      OR EXISTS(SELECT 1 FROM public.tasks t JOIN public.projects p ON p.id=t.project_id WHERE t.id=op.task_id AND p.priority='P4' AND NOT d3.p4_blocking_exception(t.id))
      OR NOT EXISTS(SELECT 1 FROM d3.plan_head h JOIN d3.plan_manifests m ON m.planning_run_id=h.planning_run_id
        JOIN d3.captures c ON c.id=m.capture_id JOIN d3.settings s ON s.singleton
        WHERE to_jsonb(s)=c.body->'d3.settings'->0)
      OR NOT EXISTS(SELECT 1 FROM d3.estimate_heads h JOIN d3.estimates e ON e.id=h.estimate_id
        WHERE h.operation_id=op.id AND h.resource_id=d.resource_id AND e.id=d.estimate_id AND e.confidence>=0.8 AND e.observed_at<=now_at AND e.valid_until>now_at)
      OR EXISTS(SELECT 1 FROM d2.reservations res WHERE res.id=d.reservation_id AND res.pool='INCIDENT'
        AND NOT EXISTS(SELECT 1 FROM public.incident_task_links l JOIN public.incidents i ON i.id=l.incident_id LEFT JOIN d3.incident_classifications cl ON cl.incident_id=i.id
          WHERE l.task_id=op.task_id AND l.role<>'FOLLOW_UP' AND i.status<>'RESOLVED' AND (i.severity IN ('SEV1','SEV2') OR coalesce(cl.active_response,false))))
      OR EXISTS(SELECT 1 FROM d2.reservations res WHERE res.id=d.reservation_id AND res.pool='PLANNED'
        AND EXISTS(SELECT 1 FROM public.incident_task_links l JOIN public.incidents i ON i.id=l.incident_id LEFT JOIN d3.incident_classifications cl ON cl.incident_id=i.id
          WHERE l.task_id=op.task_id AND l.role<>'FOLLOW_UP' AND i.status<>'RESOLVED' AND (i.severity IN ('SEV1','SEV2') OR coalesce(cl.active_response,false))))
      OR NOT EXISTS(SELECT 1 FROM public.resources r JOIN public.workers w ON w.id=r.worker_id WHERE r.id=d.resource_id AND r.enabled AND w.id=d.worker_id
        AND w.state='ONLINE' AND w.last_heartbeat_at BETWEEN now_at-interval '90 seconds' AND now_at
        AND r.capabilities @> coalesce(op.policy_snapshot->'required_capabilities','{}') AND w.capabilities @> coalesce(op.policy_snapshot->'required_capabilities','{}'))
      OR (SELECT array_agg(account_id ORDER BY account_id) FROM d2.operation_accounts WHERE operation_id=op.id) IS DISTINCT FROM
        (SELECT array_agg(id ORDER BY id) FROM d2.accounts WHERE resource_id=d.resource_id AND window_start<renew_until AND window_end>now_at)
      OR EXISTS(SELECT 1 FROM d2.operation_accounts m JOIN d2.accounts a ON a.id=m.account_id WHERE m.operation_id=op.id AND
        (a.window_start>now_at OR a.window_end<renew_until OR coalesce((SELECT confidence FROM d2.capacity_limits WHERE account_id=a.id ORDER BY id DESC LIMIT 1),a.confidence,0)<0.8))
      OR EXISTS(SELECT 1 FROM d2.operation_accounts m JOIN d2.balances b ON b.account_id=m.account_id JOIN d2.reservations res ON res.operation_id=m.operation_id AND res.pool=b.pool
        WHERE m.operation_id=op.id AND (b.available IS NULL OR b.available<0))
      OR NOT EXISTS(SELECT 1 FROM d3.calendar_heads h JOIN d3.calendars cal ON cal.id=h.calendar_id CROSS JOIN LATERAL jsonb_array_elements(cal.slots) s
        WHERE h.resource_id=d.resource_id AND (s->>'start')::timestamptz<=now_at AND (s->>'end')::timestamptz>=renew_until) THEN
      RAISE EXCEPTION 'Continuation safety changed; reconciliation/checkpoint required' USING ERRCODE='40001';END IF;
  END IF;
  IF action IN ('START','HEARTBEAT','VERIFY','RECOVERY_VERIFY') AND
    (NOT d2.integration_eligible(op.task_id) AND (action IN ('VERIFY','RECOVERY_VERIFY') OR coalesce((op.policy_snapshot->>'integration_phase')::boolean,false))
      OR ((action IN ('VERIFY','RECOVERY_VERIFY') OR coalesce((op.policy_snapshot->>'integration_phase')::boolean,false))
        AND EXISTS(SELECT 1 FROM public.task_dependencies WHERE successor_task_id=op.task_id AND kind='MOCKABLE'))) THEN
    RAISE EXCEPTION 'Real integration evidence required' USING ERRCODE='23514';END IF;
  result=d2.execution(public.gen_random_uuid(),req);
  INSERT INTO d3.commands(id,request,response) VALUES(cid,req,result);RETURN result;
END $$;

CREATE OR REPLACE FUNCTION d3.dispatch(cid uuid,req jsonb) RETURNS jsonb LANGUAGE plpgsql SECURITY DEFINER
SET search_path=pg_catalog,public,d2,d3 SET TimeZone='UTC' AS $$
DECLARE prior jsonb;pid uuid=(req->>'plan_id')::uuid;oid uuid=(req->>'operation_id')::uuid;
  rid uuid=(req->>'resource_id')::uuid;wid uuid=(req->>'worker_id')::uuid;
  op public.operations;t public.tasks;p public.projects;r public.resources;w public.workers;
  m d3.plan_manifests;c d3.captures;e d3.estimates;res d2.reservations;a d2.accounts;b d2.balances;
  item jsonb;body jsonb;rel text;entry record;pending numeric;delta numeric;used numeric;
  at_time timestamptz;finish timestamptz;pool_name text;lane_name text;result jsonb;estimate_id uuid;
BEGIN
  IF req->>'action' IS DISTINCT FROM 'CLAIM' OR pid IS NULL OR oid IS NULL OR rid IS NULL OR wid IS NULL THEN
    RAISE EXCEPTION 'Explicit plan/operation/resource/worker CLAIM required' USING ERRCODE='23514';END IF;
  IF current_setting('transaction_isolation')<>'read committed' THEN RAISE EXCEPTION 'Dispatch requires READ COMMITTED' USING ERRCODE='25001';END IF;
  PERFORM d3.lock_state();
  prior=d3.previous_command(cid,req);IF prior IS NOT NULL THEN RETURN prior;END IF;
  IF NOT EXISTS(SELECT 1 FROM d3.plan_head h JOIN public.planning_runs pr ON pr.id=h.planning_run_id
    WHERE h.planning_run_id=pid AND pr.status='PUBLISHED' AND pr.horizon_end>clock_timestamp()) THEN
    RAISE EXCEPTION 'Current published plan required' USING ERRCODE='40001';END IF;
  SELECT * INTO STRICT m FROM d3.plan_manifests WHERE planning_run_id=pid;
  SELECT * INTO STRICT c FROM d3.captures WHERE id=m.capture_id;
  SELECT value INTO item FROM jsonb_array_elements(m.result->'decisions') WHERE value->>'operationId'=oid::text;
  IF item IS NULL OR item->>'disposition'<>'TENTATIVE' OR (item->>'resourceId')::uuid IS DISTINCT FROM rid THEN
    RAISE EXCEPTION 'Operation is not a tentative assignment in this plan' USING ERRCODE='23514';END IF;
  SELECT * INTO STRICT op FROM public.operations WHERE id=oid;
  SELECT * INTO STRICT t FROM public.tasks WHERE id=op.task_id;
  SELECT * INTO STRICT p FROM public.projects WHERE id=t.project_id;
  SELECT * INTO STRICT r FROM public.resources WHERE id=rid;
  SELECT * INTO STRICT w FROM public.workers WHERE id=wid;
  body=d3.state_body();
  -- Claims of other operations may change physical facts. Never require a full
  -- pre-publication hash here; compare the immutable planning assumptions instead.
  FOREACH rel IN ARRAY ARRAY['d3.settings','public.projects','public.task_dependencies','public.project_dependencies',
    'public.capability_requirements','public.capabilities','public.capability_versions','d2.resolutions',
    'd2.capability_producers','d2.capability_epochs','d2.verifications','d3.estimate_heads','d3.calendar_heads'] LOOP
    IF body->rel IS DISTINCT FROM c.body->rel THEN RAISE EXCEPTION 'Dispatch assumptions changed: %',rel USING ERRCODE='40001';END IF;
  END LOOP;
  IF to_jsonb(op) IS DISTINCT FROM (SELECT x FROM jsonb_array_elements(c.body->'public.operations') x WHERE x->>'id'=oid::text)
    OR to_jsonb(t) IS DISTINCT FROM (SELECT x FROM jsonb_array_elements(c.body->'public.tasks') x WHERE x->>'id'=t.id::text)
    OR to_jsonb(r) IS DISTINCT FROM (SELECT x FROM jsonb_array_elements(c.body->'public.resources') x WHERE x->>'id'=rid::text) THEN
    RAISE EXCEPTION 'Operation/task/resource changed since capture' USING ERRCODE='40001';END IF;
  PERFORM d4.require_unheld(oid,rid);
  at_time=clock_timestamp();
  SELECT est.* INTO STRICT e FROM d3.estimate_heads h JOIN d3.estimates est ON est.id=h.estimate_id WHERE h.operation_id=oid AND h.resource_id=rid;
  finish=at_time+e.duration_ms*interval '1 millisecond';pool_name=item->>'pool';lane_name=item->>'lane';
  IF at_time<(item->'slot'->>'start')::timestamptz OR at_time>=(item->'slot'->>'end')::timestamptz
    OR finish>(m.result->>'horizonEnd')::timestamptz THEN RAISE EXCEPTION 'Assignment not due or expired' USING ERRCODE='40001';END IF;
  IF op.state<>'READY' OR p.status<>'ACTIVE' OR t.status IN ('DONE','FAILED','CANCELLED') OR NOT d2.task_eligible(t.id)
    OR (p.priority='P4' AND NOT d3.p4_blocking_exception(t.id)) OR NOT r.enabled OR r.worker_id IS DISTINCT FROM wid
    OR w.state<>'ONLINE' OR w.last_heartbeat_at IS NULL OR w.last_heartbeat_at<at_time-interval '90 seconds' OR w.last_heartbeat_at>at_time
    OR NOT(r.capabilities @> coalesce(op.policy_snapshot->'required_capabilities','{}'))
    OR NOT(w.capabilities @> coalesce(op.policy_snapshot->'required_capabilities','{}'))
    OR op.context_pack_sha256 IS NULL OR op.context_pack_ref IS NULL OR e.confidence<0.8 OR e.observed_at>at_time OR e.valid_until<=at_time THEN
    RAISE EXCEPTION 'Dispatch eligibility or estimate expired' USING ERRCODE='40001';END IF;
  IF coalesce((op.policy_snapshot->>'requires_approval')::boolean,false) AND NOT EXISTS(
    SELECT 1 FROM public.approvals ap WHERE ap.operation_id=oid AND ap.state='APPROVED' AND ap.expires_at>at_time
    AND ap.context_snapshot_sha256=op.context_pack_sha256 AND ap.policy_snapshot_sha256=encode(public.digest(op.policy_snapshot::text,'sha256'),'hex')) THEN
    RAISE EXCEPTION 'Fresh approval required' USING ERRCODE='23514';END IF;
  IF coalesce((op.policy_snapshot->>'integration_phase')::boolean,false) AND (NOT d2.integration_eligible(t.id)
    OR EXISTS(SELECT 1 FROM public.task_dependencies WHERE successor_task_id=t.id AND kind='MOCKABLE')) THEN
    RAISE EXCEPTION 'Real integration required' USING ERRCODE='23514';END IF;
  IF EXISTS(SELECT 1 FROM public.execution_attempts WHERE operation_id=oid) AND
    (NOT EXISTS(SELECT 1 FROM d2.effect_receipts WHERE operation_id=oid AND generation=op.lease_generation AND status='ABSENT')
    OR EXISTS(SELECT 1 FROM d2.effect_receipts WHERE operation_id=oid AND generation=op.lease_generation AND status<>'ABSENT')) THEN
    RAISE EXCEPTION 'Conclusive uncontradicted absence required for retry' USING ERRCODE='23514';END IF;
  IF NOT EXISTS(SELECT 1 FROM d3.calendar_heads h JOIN d3.calendars cal ON cal.id=h.calendar_id CROSS JOIN LATERAL jsonb_array_elements(cal.slots) s
    WHERE h.resource_id=rid AND (s->>'start')::timestamptz<=at_time AND (s->>'end')::timestamptz>=finish) THEN
    RAISE EXCEPTION 'Calendar cannot cover actual dispatch duration' USING ERRCODE='40001';END IF;
  IF EXISTS(SELECT 1 FROM public.operation_leases l JOIN public.operations active ON active.id=l.operation_id
    JOIN public.execution_attempts attempt ON attempt.id=l.attempt_id
    WHERE active.state IN ('LEASED','RUNNING','VERIFYING','RECONCILING','BLOCKED_APPROVAL') AND
    (l.worker_id=wid OR active.task_id=t.id OR EXISTS(SELECT 1 FROM jsonb_array_elements_text(coalesce(op.policy_snapshot->'exclusive_keys','[]')) k
      WHERE coalesce(active.policy_snapshot->'exclusive_keys','[]') ? k.value))) THEN
    RAISE EXCEPTION 'Physical worker/task/workspace occupied' USING ERRCODE='40001';END IF;
  IF EXISTS(SELECT 1 FROM jsonb_array_elements(m.result->'decisions') other JOIN public.operations other_op ON other_op.id=(other->>'operationId')::uuid
    JOIN public.resources other_r ON other_r.id=(other->>'resourceId')::uuid
    WHERE other->>'operationId'<>oid::text AND other->>'disposition' IN ('TENTATIVE','CARRIED')
      AND other_op.state NOT IN ('COMPLETED','CANCELLED','FAILED')
      AND tstzrange(at_time,finish,'[)') && tstzrange((other->'slot'->>'start')::timestamptz,(other->'slot'->>'end')::timestamptz,'[)')
      AND (other_r.worker_id=wid OR other_op.task_id=t.id OR EXISTS(SELECT 1 FROM jsonb_array_elements_text(coalesce(op.policy_snapshot->'exclusive_keys','[]')) k WHERE coalesce(other_op.policy_snapshot->'exclusive_keys','[]') ? k.value))) THEN
    -- Planned future slots are intentions, not physical leases. A small start
    -- delay must not make every contiguous queue undispatchable. Keep actual
    -- exclusivity above and request recalculation without rewriting the plan.
    INSERT INTO public.outbox_events(aggregate_type,aggregate_id,event_type,payload)
      VALUES('PLANNING_RUN',pid,'D3_REPLAN_REQUESTED',jsonb_build_object('reason','DISPATCH_TIMING_SHIFT','operation_id',oid,'actual_start',at_time,'estimated_end',finish));
  END IF;
  IF pool_name='INCIDENT' THEN
    IF lane_name<>'INCIDENT' OR NOT EXISTS(SELECT 1 FROM public.incident_task_links l JOIN public.incidents i ON i.id=l.incident_id LEFT JOIN d3.incident_classifications cl ON cl.incident_id=i.id
      WHERE l.task_id=t.id AND l.role<>'FOLLOW_UP' AND i.status<>'RESOLVED' AND (i.severity IN ('SEV1','SEV2') OR coalesce(cl.active_response,false))) THEN
      RAISE EXCEPTION 'Incident response no longer active' USING ERRCODE='40001';END IF;
  ELSIF pool_name IS DISTINCT FROM 'PLANNED' OR lane_name NOT IN ('WEIGHTED','AGED','URGENT') THEN RAISE EXCEPTION 'Invalid lane/pool' USING ERRCODE='23514';END IF;
  IF pool_name='PLANNED' AND EXISTS(SELECT 1 FROM public.incident_task_links l JOIN public.incidents i ON i.id=l.incident_id LEFT JOIN d3.incident_classifications cl ON cl.incident_id=i.id
    WHERE l.task_id=t.id AND l.role<>'FOLLOW_UP' AND i.status<>'RESOLVED' AND (i.severity IN ('SEV1','SEV2') OR coalesce(cl.active_response,false))) THEN
    RAISE EXCEPTION 'Incident escalation requires a new plan; no PLANNED fallback' USING ERRCODE='40001';END IF;
  SELECT * INTO res FROM d2.reservations WHERE operation_id=oid;
  IF res.id IS NOT NULL THEN
    IF res.resource_id<>rid OR res.pool<>pool_name OR e.units IS DISTINCT FROM (SELECT jsonb_object_agg(account_id::text,units) FROM d2.operation_accounts WHERE operation_id=oid)
      OR lane_name IS DISTINCT FROM coalesce((SELECT lane FROM d3.lane_attributions WHERE reservation_id=res.id),CASE WHEN res.pool='INCIDENT' THEN 'INCIDENT' ELSE 'WEIGHTED' END) THEN
      RAISE EXCEPTION 'Frozen reservation mapping/pool/lane mismatch' USING ERRCODE='23514';END IF;
  ELSE
    -- No reservation exists: replace stale tentative mappings atomically. Once
    -- reserved, V8's mapping guard freezes this vector permanently.
    DELETE FROM d2.operation_accounts WHERE operation_id=oid;
    INSERT INTO d2.operation_accounts SELECT oid,key::uuid,(value::text)::numeric,e.calibration_ref FROM jsonb_each(e.units);
  END IF;
  IF (SELECT array_agg(key ORDER BY key) FROM jsonb_each(e.units)) IS DISTINCT FROM
    (SELECT array_agg(id::text ORDER BY id::text) FROM d2.accounts WHERE resource_id=rid AND window_start<finish AND window_end>at_time) THEN
    RAISE EXCEPTION 'All current binding physical accounts required' USING ERRCODE='40001';END IF;
  FOR entry IN SELECT * FROM jsonb_each(e.units) ORDER BY key LOOP
    SELECT * INTO STRICT a FROM d2.accounts WHERE id=entry.key::uuid;
    IF a.resource_id<>rid OR a.window_start>at_time OR a.window_end<finish OR a.window_end<=clock_timestamp()
      OR coalesce((SELECT confidence FROM d2.capacity_limits WHERE account_id=a.id ORDER BY id DESC LIMIT 1),a.confidence,0)<0.8 THEN
      RAISE EXCEPTION 'Physical account window/confidence invalid, including TOP_UP' USING ERRCODE='40001';END IF;
    SELECT * INTO STRICT b FROM d2.balances WHERE account_id=a.id AND pool=pool_name;
    pending=coalesce((SELECT outstanding FROM d2.reservation_balances WHERE reservation_id=res.id AND account_id=a.id),0);
    delta=greatest((entry.value::text)::numeric-pending,0);
    IF b.available IS NULL OR b.available<0 OR b.available<delta THEN RAISE EXCEPTION 'WAITING_CAPACITY at dispatch' USING ERRCODE='40001';END IF;
    IF lane_name IN ('AGED','URGENT') THEN
      used=coalesce((SELECT units FROM d3.lane_usage WHERE account_id=a.id AND lane=lane_name),0);
      IF used+delta>coalesce((SELECT capacity FROM d2.capacity_limits WHERE account_id=a.id ORDER BY id DESC LIMIT 1),a.initial_capacity)*0.7*(CASE lane_name WHEN 'AGED' THEN 0.05 ELSE 0.20 END) THEN
        RAISE EXCEPTION 'Lane cap exhausted at dispatch' USING ERRCODE='40001';END IF;
    END IF;
  END LOOP;
  result=d2.execution(public.gen_random_uuid(),jsonb_build_object('action','CLAIM','operation_id',oid,'worker_id',wid,'resource_id',rid,'pool',pool_name));
  IF EXISTS(SELECT 1 FROM d2.operation_accounts binding JOIN d2.accounts acct ON acct.id=binding.account_id
    WHERE binding.operation_id=oid AND acct.window_end<clock_timestamp()+e.duration_ms*interval '1 millisecond') THEN
    RAISE EXCEPTION 'Physical window expired during CLAIM; all effects rolled back' USING ERRCODE='40001';END IF;
  IF res.id IS NULL THEN
    INSERT INTO d3.lane_attributions(reservation_id,lane,reason) VALUES((result->>'reservation_id')::uuid,lane_name,'D3 atomic dispatch '||cid);
  END IF;
  INSERT INTO d3.dispatches(command_id,planning_run_id,operation_id,attempt_id,reservation_id,estimate_id,worker_id,resource_id,generation)
    VALUES(cid,pid,oid,(result->>'attempt_id')::uuid,(result->>'reservation_id')::uuid,e.id,wid,rid,(result->>'generation')::bigint);
  result=result||jsonb_build_object('plan_id',pid,'operation_id',oid);
  INSERT INTO d3.commands(id,request,response) VALUES(cid,req,result);
  RETURN result;
END $$;

CREATE OR REPLACE FUNCTION d4.publish_continuation(cid uuid,req jsonb) RETURNS jsonb LANGUAGE plpgsql SECURITY DEFINER
SET search_path=pg_catalog,public,d2,d3 AS $$
DECLARE previous jsonb;c d3.captures;body jsonb;manifest jsonb=req->'result';profile jsonb;head uuid;expected uuid;
  pid uuid=(req->>'plan_id')::uuid;item jsonb;other jsonb;op public.operations;task public.tasks;project public.projects;
  resource public.resources;worker public.workers;est d3.estimates;res d2.reservations;acct d2.accounts;b d2.balances;
  entry record;bind record;amount numeric;pending numeric;used numeric;usage_key text;needed jsonb='{}';lane_needed jsonb='{}';
  start_at timestamptz;end_at timestamptz;effective_now timestamptz;capture_end timestamptz;pool_name text;lane_name text;
  rid uuid;budget_id uuid;priority jsonb;actual_policy_hash text;result jsonb;decision_ids uuid[];operation_ids uuid[];
BEGIN
  IF req->>'action' IS DISTINCT FROM 'PUBLISH' THEN RAISE EXCEPTION 'Publish action required' USING ERRCODE='23514';END IF;
  IF current_setting('transaction_isolation')<>'read committed' THEN RAISE EXCEPTION 'Publication requires fresh READ COMMITTED validation' USING ERRCODE='25001';END IF;
  PERFORM d3.lock_state();
  previous=d3.previous_command(cid,req);IF previous IS NOT NULL THEN RETURN previous;END IF;
  SELECT * INTO STRICT c FROM d3.captures WHERE id=(req->>'capture_id')::uuid;
  SELECT planning_run_id INTO head FROM d3.plan_head WHERE singleton;
  expected=(req->>'expected_current_plan_id')::uuid;
  IF head IS DISTINCT FROM expected THEN RAISE EXCEPTION 'Current plan CAS conflict' USING ERRCODE='40001';END IF;
  body=d3.state_body();
  IF encode(public.digest(body::text,'sha256'),'hex')<>c.basis_hash THEN RAISE EXCEPTION 'Planning snapshot is stale' USING ERRCODE='40001';END IF;
  IF EXISTS(SELECT 1 FROM public.planning_runs WHERE status='PUBLISHED' AND (head IS NULL OR id<>head))
    OR (head IS NOT NULL AND NOT EXISTS(SELECT 1 FROM public.planning_runs WHERE id=head AND status='PUBLISHED')) THEN
    RAISE EXCEPTION 'Unmanaged or inconsistent published plans require explicit review' USING ERRCODE='23514';END IF;
  profile=body->'d3.settings'->0;
  actual_policy_hash=encode(public.digest((profile->'policy')::text,'sha256'),'hex');
  capture_end=((c.captured_at AT TIME ZONE 'Europe/Madrid')+interval '7 days') AT TIME ZONE 'Europe/Madrid';
  IF manifest IS NULL OR manifest->>'schemaVersion' IS DISTINCT FROM 'd3.snapshot.v1'
    OR manifest->>'algorithmVersion' IS DISTINCT FROM 'd3.greedy.v1'
    OR manifest->>'status' NOT IN ('COMPLETE','PARTIAL') OR manifest->>'status' IS NULL
    OR manifest->>'policyHash' IS DISTINCT FROM actual_policy_hash
    OR manifest->>'calibrationEpoch' IS DISTINCT FROM profile->>'calibration_epoch'
    OR (manifest->>'asOf')::timestamptz IS DISTINCT FROM c.captured_at
    OR (manifest->>'horizonEnd')::timestamptz IS DISTINCT FROM capture_end
    OR jsonb_typeof(manifest->'decisions') IS DISTINCT FROM 'array' THEN
    RAISE EXCEPTION 'Invalid or non-publishable manifest' USING ERRCODE='23514';END IF;
  SELECT array_agg((x->>'operationId')::uuid ORDER BY (x->>'operationId')::uuid) INTO decision_ids FROM jsonb_array_elements(manifest->'decisions') x;
  SELECT array_agg(id ORDER BY id) INTO operation_ids FROM public.operations;
  IF decision_ids IS DISTINCT FROM operation_ids THEN RAISE EXCEPTION 'Every operation must have exactly one decision' USING ERRCODE='23514';END IF;
  IF cardinality(decision_ids)>(profile->'policy'->>'max_operations')::integer THEN RAISE EXCEPTION 'Profile size limit exceeded' USING ERRCODE='23514';END IF;
  -- Validate the complete candidate before creating its DRAFT or any children.
  FOR item IN SELECT value FROM jsonb_array_elements(manifest->'decisions') ORDER BY value->>'operationId' LOOP
    IF item->>'disposition' NOT IN ('TENTATIVE','CARRIED','BLOCKED','NEEDS_DATA','DEFERRED','CONFLICT') OR item->>'disposition' IS NULL THEN RAISE EXCEPTION 'Invalid disposition' USING ERRCODE='23514';END IF;
    SELECT * INTO STRICT op FROM public.operations WHERE id=(item->>'operationId')::uuid;
    SELECT * INTO STRICT task FROM public.tasks WHERE id=op.task_id;
    SELECT * INTO STRICT project FROM public.projects WHERE id=task.project_id;
    IF (op.state IN ('LEASED','RUNNING','VERIFYING','RECONCILING') OR (op.state='BLOCKED_APPROVAL' AND EXISTS(SELECT 1 FROM d2.reservations WHERE operation_id=op.id)))
      AND item->>'disposition'<>'CARRIED' THEN RAISE EXCEPTION 'Active commitment cannot be hidden' USING ERRCODE='23514';END IF;
    IF item->>'disposition' NOT IN ('TENTATIVE','CARRIED') THEN
      IF nullif(item->>'resourceId','') IS NOT NULL THEN RAISE EXCEPTION 'Unassigned operation has resource' USING ERRCODE='23514';END IF;
      CONTINUE;
    END IF;
    SELECT * INTO STRICT resource FROM public.resources WHERE id=(item->>'resourceId')::uuid;
    start_at=(item->'slot'->>'start')::timestamptz;end_at=(item->'slot'->>'end')::timestamptz;
    pool_name=item->>'pool';lane_name=item->>'lane';
    IF pool_name IS NULL OR pool_name NOT IN ('PLANNED','INCIDENT') OR start_at IS NULL OR end_at IS NULL OR end_at<=start_at
      OR start_at<c.captured_at OR end_at>capture_end THEN RAISE EXCEPTION 'Invalid plan interval/pool' USING ERRCODE='23514';END IF;
    SELECT * INTO res FROM d2.reservations WHERE operation_id=op.id;
    IF item->>'disposition'='CARRIED' THEN
      IF res.id IS NULL OR res.resource_id<>resource.id OR res.pool<>pool_name
        OR op.state NOT IN ('LEASED','RUNNING','VERIFYING','RECONCILING','BLOCKED_APPROVAL')
        OR start_at<>c.captured_at OR end_at<>capture_end
        OR item->'incrementalDemand' IS DISTINCT FROM '{}'::jsonb THEN RAISE EXCEPTION 'Invalid carried reservation' USING ERRCODE='23514';END IF;
      CONTINUE;
    END IF;
    effective_now=greatest(start_at,clock_timestamp());
    PERFORM d4.require_unheld(op.id,resource.id);
    SELECT * INTO STRICT worker FROM public.workers WHERE id=resource.worker_id;
    IF op.state<>'READY' OR project.status<>'ACTIVE' OR task.status IN ('DONE','CANCELLED','FAILED') OR NOT d2.task_eligible(task.id)
      OR NOT resource.enabled OR worker.state<>'ONLINE' OR worker.last_heartbeat_at IS NULL
      OR worker.last_heartbeat_at<clock_timestamp()-interval '90 seconds' OR worker.last_heartbeat_at>clock_timestamp()
      OR NOT(resource.capabilities @> coalesce(op.policy_snapshot->'required_capabilities','{}'))
      OR NOT(worker.capabilities @> coalesce(op.policy_snapshot->'required_capabilities','{}'))
      OR op.context_pack_sha256 IS NULL OR op.context_pack_ref IS NULL
      OR (SELECT count(*) FROM public.execution_attempts WHERE operation_id=op.id)>=coalesce((op.policy_snapshot->>'max_attempts')::integer,3)
      OR (coalesce((op.policy_snapshot->>'max_attempts')::integer,3) NOT BETWEEN 1 AND 20)
      OR (project.priority='P4' AND NOT d3.p4_blocking_exception(task.id)) THEN
      RAISE EXCEPTION 'Operation no longer eligible' USING ERRCODE='40001';END IF;
    IF EXISTS(SELECT 1 FROM public.execution_attempts WHERE operation_id=op.id)
      AND (NOT EXISTS(SELECT 1 FROM d2.effect_receipts WHERE operation_id=op.id AND generation=op.lease_generation AND status='ABSENT') OR EXISTS(SELECT 1 FROM d2.effect_receipts WHERE operation_id=op.id AND generation=op.lease_generation AND status<>'ABSENT')) AND NOT d4.continuation_safe(op.id,op.lease_generation) THEN
      RAISE EXCEPTION 'Retry safety evidence missing' USING ERRCODE='23514';END IF;
    IF coalesce((op.policy_snapshot->>'integration_phase')::boolean,false) AND (NOT d2.integration_eligible(task.id)
      OR EXISTS(SELECT 1 FROM public.task_dependencies WHERE successor_task_id=task.id AND kind='MOCKABLE')) THEN RAISE EXCEPTION 'Real integration guard required' USING ERRCODE='23514';END IF;
    IF coalesce((op.policy_snapshot->>'requires_approval')::boolean,false) AND NOT EXISTS(
      SELECT 1 FROM public.approvals a WHERE a.operation_id=op.id AND a.state='APPROVED' AND a.expires_at>effective_now
      AND a.context_snapshot_sha256=op.context_pack_sha256 AND a.policy_snapshot_sha256=encode(public.digest(op.policy_snapshot::text,'sha256'),'hex')) THEN
      RAISE EXCEPTION 'Approval stale or expired' USING ERRCODE='40001';END IF;
    SELECT e.* INTO STRICT est FROM d3.estimate_heads h JOIN d3.estimates e ON e.id=h.estimate_id WHERE h.operation_id=op.id AND h.resource_id=resource.id;
    IF est.confidence<0.8 OR est.valid_until<=effective_now OR est.observed_at>c.captured_at OR end_at-start_at<>est.duration_ms*interval '1 millisecond' OR end_at<=clock_timestamp() THEN
      RAISE EXCEPTION 'Estimate stale or invalid slot duration' USING ERRCODE='40001';END IF;
    IF NOT EXISTS(SELECT 1 FROM d3.calendar_heads h JOIN d3.calendars cal ON cal.id=h.calendar_id CROSS JOIN LATERAL jsonb_array_elements(cal.slots) s
      WHERE h.resource_id=resource.id AND (s->>'start')::timestamptz<=start_at AND (s->>'end')::timestamptz>=end_at) THEN RAISE EXCEPTION 'Calendar changed or no slot' USING ERRCODE='40001';END IF;
    IF EXISTS(SELECT 1 FROM public.operation_leases l JOIN public.operations active ON active.id=l.operation_id
      WHERE l.operation_id<>op.id AND l.worker_id=resource.worker_id AND active.state IN ('LEASED','RUNNING','VERIFYING','RECONCILING','BLOCKED_APPROVAL')) THEN
      RAISE EXCEPTION 'Worker occupied by a physical lease' USING ERRCODE='40001';END IF;
    IF pool_name='INCIDENT' THEN
      IF lane_name IS DISTINCT FROM 'INCIDENT' OR NOT EXISTS(SELECT 1 FROM public.incident_task_links l JOIN public.incidents i ON i.id=l.incident_id LEFT JOIN d3.incident_classifications cl ON cl.incident_id=i.id
        WHERE l.task_id=task.id AND l.role<>'FOLLOW_UP' AND i.status<>'RESOLVED' AND (i.severity IN ('SEV1','SEV2') OR coalesce(cl.active_response,false))) THEN RAISE EXCEPTION 'Incident pool needs active incident classification' USING ERRCODE='23514';END IF;
    ELSIF lane_name IS NULL OR lane_name NOT IN ('WEIGHTED','AGED','URGENT') THEN RAISE EXCEPTION 'Invalid planned lane' USING ERRCODE='23514';END IF;
    IF lane_name='AGED' AND res.id IS NULL AND coalesce((SELECT sum(greatest(extract(epoch FROM least(coalesce(i.end_at,c.captured_at),c.captured_at)-i.observed_at),0)) FROM d3.eligible_intervals i WHERE i.operation_id=op.id AND i.eligible),0)<604800 THEN
      RAISE EXCEPTION 'Seven eligible days required' USING ERRCODE='23514';END IF;
    IF lane_name='URGENT' AND res.id IS NULL AND (item->>'slack' IS NULL OR (item->>'slack')::interval>interval '24 hours') THEN
      RAISE EXCEPTION 'Urgent path slack required' USING ERRCODE='23514';END IF;
    IF res.id IS NOT NULL THEN
      IF res.resource_id<>resource.id OR res.pool<>pool_name OR est.units IS DISTINCT FROM (SELECT jsonb_object_agg(account_id::text,units) FROM d2.operation_accounts WHERE operation_id=op.id)
        OR lane_name IS DISTINCT FROM coalesce((SELECT lane FROM d3.lane_attributions WHERE reservation_id=res.id),CASE WHEN res.pool='INCIDENT' THEN 'INCIDENT' ELSE 'WEIGHTED' END) THEN
        RAISE EXCEPTION 'Frozen reservation mapping/lane mismatch' USING ERRCODE='23514';END IF;
    END IF;
    IF (SELECT array_agg(key ORDER BY key) FROM jsonb_each(est.units)) IS DISTINCT FROM
      (SELECT array_agg(id::text ORDER BY id::text) FROM d2.accounts WHERE resource_id=resource.id AND window_start<end_at AND window_end>start_at)
      OR (SELECT array_agg(key ORDER BY key) FROM jsonb_each(est.units)) IS DISTINCT FROM (SELECT array_agg(key ORDER BY key) FROM jsonb_each(item->'incrementalDemand')) THEN
      RAISE EXCEPTION 'All binding accounts required' USING ERRCODE='23514';END IF;
    FOR entry IN SELECT * FROM jsonb_each(est.units) ORDER BY key LOOP
      SELECT * INTO STRICT acct FROM d2.accounts WHERE id=entry.key::uuid;
      IF acct.window_start>start_at OR acct.window_end<end_at OR acct.window_end<=clock_timestamp()
        OR coalesce((SELECT confidence FROM d2.capacity_limits WHERE account_id=acct.id ORDER BY id DESC LIMIT 1),acct.confidence,0)<0.8 THEN RAISE EXCEPTION 'Physical account unavailable' USING ERRCODE='40001';END IF;
      SELECT * INTO STRICT b FROM d2.balances WHERE account_id=acct.id AND pool=pool_name;
      pending=coalesce((SELECT outstanding FROM d2.reservation_balances WHERE reservation_id=res.id AND account_id=acct.id),0);
      amount=greatest((entry.value::text)::numeric-pending,0);
      IF (item->'incrementalDemand'->>entry.key)::numeric IS DISTINCT FROM amount THEN RAISE EXCEPTION 'Incremental demand mismatch' USING ERRCODE='23514';END IF;
      usage_key=entry.key||':'||pool_name;used=coalesce((needed->>usage_key)::numeric,0)+amount;
      IF b.available IS NULL OR b.available<0 OR b.available<used THEN RAISE EXCEPTION 'Physical capacity no longer fits' USING ERRCODE='40001';END IF;
      needed=jsonb_set(needed,ARRAY[usage_key],to_jsonb(used));
      IF lane_name IN ('AGED','URGENT') THEN
        usage_key=entry.key||':'||lane_name;
        used=coalesce((lane_needed->>usage_key)::numeric,0)+amount;
        IF used+coalesce((SELECT units FROM d3.lane_usage WHERE account_id=acct.id AND lane=lane_name),0)>
          coalesce((SELECT capacity FROM d2.capacity_limits WHERE account_id=acct.id ORDER BY id DESC LIMIT 1),acct.initial_capacity)*0.7*(CASE lane_name WHEN 'AGED' THEN 0.05 ELSE 0.20 END) THEN
          RAISE EXCEPTION 'Lane budget exhausted' USING ERRCODE='40001';END IF;
        lane_needed=jsonb_set(lane_needed,ARRAY[usage_key],to_jsonb(used));
      END IF;
    END LOOP;
    -- Worker/workspace exclusivity among new slots; CARRIED entries represent active work.
    FOR other IN SELECT value FROM jsonb_array_elements(manifest->'decisions') WHERE value->>'disposition' IN ('TENTATIVE','CARRIED') AND value->>'operationId'<>op.id::text LOOP
      IF tstzrange(start_at,end_at,'[)') && tstzrange((other->'slot'->>'start')::timestamptz,(other->'slot'->>'end')::timestamptz,'[)')
        AND ((SELECT worker_id FROM public.resources WHERE id=(other->>'resourceId')::uuid)=resource.worker_id
          OR (SELECT task_id FROM public.operations WHERE id=(other->>'operationId')::uuid)=op.task_id
          OR EXISTS(SELECT 1 FROM public.operations other_op CROSS JOIN LATERAL jsonb_array_elements_text(coalesce(op.policy_snapshot->'exclusive_keys','[]')) k
            WHERE other_op.id=(other->>'operationId')::uuid AND coalesce(other_op.policy_snapshot->'exclusive_keys','[]') ? k.value)) THEN
        RAISE EXCEPTION 'Overlapping worker/task/workspace slots' USING ERRCODE='23514';END IF;
    END LOOP;
  END LOOP;
  INSERT INTO public.planning_runs(id,horizon_start,horizon_end,trigger_type,config_snapshot,config_sha256,solver_version)
    VALUES(pid,c.captured_at,capture_end,'D3',jsonb_build_object('capture_id',c.id,'basis_hash',c.basis_hash,'policy',profile,'result',manifest),
      encode(public.digest(jsonb_build_object('capture_id',c.id,'basis_hash',c.basis_hash,'policy',profile,'result',manifest)::text,'sha256'),'hex'),'d3.greedy.v1');
  INSERT INTO d3.plan_manifests VALUES(pid,c.id,manifest);
  FOR rid IN SELECT DISTINCT (value->>'resourceId')::uuid FROM jsonb_array_elements(manifest->'decisions') WHERE value->>'disposition' IN ('TENTATIVE','CARRIED') ORDER BY 1 LOOP
    budget_id=public.gen_random_uuid();
    INSERT INTO public.capacity_budgets(id,planning_run_id,resource_id,window_start,window_end,capacity_unit,estimated_capacity)
      SELECT budget_id,pid,rid,c.captured_at,capture_end,coalesce(min(unit),'OPERATIONS'),NULL FROM d2.accounts WHERE resource_id=rid;
    INSERT INTO d2.budget_accounts(budget_id,planning_run_id,resource_id,account_id,estimated_capacity,confidence,calibration_ref)
      SELECT budget_id,pid,rid,a.id,coalesce(l.capacity,a.initial_capacity),coalesce(l.confidence,a.confidence),profile->>'calibration_epoch'
      FROM d2.accounts a LEFT JOIN LATERAL(SELECT capacity,confidence FROM d2.capacity_limits WHERE account_id=a.id ORDER BY id DESC LIMIT 1) l ON true WHERE a.resource_id=rid;
  END LOOP;
  FOR item IN SELECT value FROM jsonb_array_elements(manifest->'decisions') WHERE value->>'disposition' IN ('TENTATIVE','CARRIED') LOOP
    SELECT * INTO STRICT op FROM public.operations WHERE id=(item->>'operationId')::uuid;
    SELECT project_id INTO rid FROM public.tasks WHERE id=op.task_id;
    SELECT id INTO budget_id FROM public.capacity_budgets WHERE planning_run_id=pid AND resource_id=(item->>'resourceId')::uuid;
    INSERT INTO public.capacity_allocations(planning_run_id,resource_id,project_id,pool,budget_id,reserved_units)
      VALUES(pid,(item->>'resourceId')::uuid,rid,item->>'pool',budget_id,NULL) ON CONFLICT DO NOTHING;
    INSERT INTO public.schedule_entries(planning_run_id,task_id,resource_id,operation_id,pool,planned_start,planned_end,state,priority_snapshot,reason)
      VALUES(pid,op.task_id,(item->>'resourceId')::uuid,op.id,item->>'pool',(item->'slot'->>'start')::timestamptz,(item->'slot'->>'end')::timestamptz,'PLANNED',item->'priority',item);
    INSERT INTO d2.plan_reservations SELECT pid,id FROM d2.reservations WHERE operation_id=op.id ON CONFLICT DO NOTHING;
  END LOOP;
  UPDATE public.planning_runs SET status='PUBLISHED' WHERE id=pid;
  IF head IS NOT NULL THEN UPDATE public.planning_runs SET status='SUPERSEDED',superseded_by=pid WHERE id=head;END IF;
  UPDATE d3.plan_head SET planning_run_id=pid WHERE singleton;
  result=jsonb_build_object('plan_id',pid,'superseded_plan_id',head,'published',true);
  INSERT INTO d3.commands(id,request,response) VALUES(cid,req,result);
  INSERT INTO public.outbox_events(aggregate_type,aggregate_id,event_type,payload) VALUES('PLANNING_RUN',pid,'PLAN_PUBLISHED',result);
  RETURN result;
END $$;

CREATE OR REPLACE FUNCTION d4.observe_continuation_eligibility(cid uuid) RETURNS jsonb LANGUAGE plpgsql SECURITY DEFINER
SET search_path=pg_catalog,public,d2,d3 AS $$
DECLARE previous jsonb;req jsonb='{"action":"OBSERVE_ELIGIBILITY"}';result jsonb;item record;
  last_value boolean;eligible boolean;observed timestamptz;until_at timestamptz;approval_until timestamptz;n integer=0;
BEGIN
  PERFORM pg_advisory_xact_lock(742002);
  previous=d3.previous_command(cid,req);IF previous IS NOT NULL THEN RETURN previous;END IF;
  observed=clock_timestamp();
  FOR item IN SELECT o.*,t.project_id,t.status task_status FROM public.operations o JOIN public.tasks t ON t.id=o.task_id ORDER BY o.id LOOP
    SELECT max(a.expires_at) INTO approval_until FROM public.approvals a WHERE a.operation_id=item.id AND a.state='APPROVED'
      AND a.context_snapshot_sha256=item.context_pack_sha256 AND a.policy_snapshot_sha256=encode(public.digest(item.policy_snapshot::text,'sha256'),'hex');
    eligible=item.state='READY' AND item.task_status NOT IN ('DONE','CANCELLED','FAILED') AND d2.task_eligible(item.task_id)
      AND EXISTS(SELECT 1 FROM public.projects p WHERE p.id=item.project_id AND p.status='ACTIVE' AND (p.priority<>'P4' OR d3.p4_blocking_exception(item.task_id)))
      AND coalesce(item.context_pack_sha256,'') ~ '^[a-f0-9]{64}$' AND nullif(item.context_pack_ref,'') IS NOT NULL
      AND NOT EXISTS(SELECT 1 FROM public.operation_leases WHERE operation_id=item.id)
      AND coalesce((item.policy_snapshot->>'max_attempts')::integer,3) BETWEEN 1 AND 20
      AND (SELECT count(*) FROM public.execution_attempts WHERE operation_id=item.id)<coalesce((item.policy_snapshot->>'max_attempts')::integer,3)
      AND (NOT EXISTS(SELECT 1 FROM public.execution_attempts WHERE operation_id=item.id) OR (EXISTS(SELECT 1 FROM d2.effect_receipts WHERE operation_id=item.id AND generation=item.lease_generation AND status='ABSENT') AND NOT EXISTS(SELECT 1 FROM d2.effect_receipts WHERE operation_id=item.id AND generation=item.lease_generation AND status<>'ABSENT')) OR d4.continuation_safe(item.id,item.lease_generation))
      AND (NOT coalesce((item.policy_snapshot->>'integration_phase')::boolean,false) OR (d2.integration_eligible(item.task_id) AND NOT EXISTS(SELECT 1 FROM public.task_dependencies WHERE successor_task_id=item.task_id AND kind='MOCKABLE')))
      AND (NOT coalesce((item.policy_snapshot->>'requires_approval')::boolean,false) OR approval_until>observed);
    until_at=NULL;
    IF coalesce(eligible,false) THEN
      SELECT max(least(e.valid_until,w.last_heartbeat_at+interval '90 seconds',bound.end_at,cal.end_at,
        CASE WHEN coalesce((item.policy_snapshot->>'requires_approval')::boolean,false) THEN approval_until ELSE 'infinity'::timestamptz END)) INTO until_at
      FROM d3.estimate_heads h JOIN d3.estimates e ON e.id=h.estimate_id JOIN public.resources r ON r.id=e.resource_id JOIN public.workers w ON w.id=r.worker_id
      JOIN LATERAL (SELECT min(a.window_end) end_at FROM jsonb_each(e.units) u JOIN d2.accounts a ON a.id=u.key::uuid) bound ON true
      JOIN LATERAL (SELECT max((s->>'end')::timestamptz) end_at FROM d3.calendar_heads ch JOIN d3.calendars c ON c.id=ch.calendar_id CROSS JOIN LATERAL jsonb_array_elements(c.slots) s
        WHERE ch.resource_id=r.id AND (s->>'start')::timestamptz<=observed AND (s->>'end')::timestamptz>=observed+e.duration_ms*interval '1 millisecond') cal ON true
      WHERE h.operation_id=item.id AND e.confidence>=0.8 AND e.valid_until>observed AND e.observed_at<=observed AND r.enabled AND w.state='ONLINE'
        AND w.last_heartbeat_at BETWEEN observed-interval '90 seconds' AND observed
        AND bound.end_at>=observed+e.duration_ms*interval '1 millisecond' AND cal.end_at IS NOT NULL
        AND NOT d4.review_blocked(item.id,r.id,coalesce((item.policy_snapshot->>'integration_phase')::boolean,false)) AND r.capabilities @> coalesce(item.policy_snapshot->'required_capabilities','{}') AND w.capabilities @> coalesce(item.policy_snapshot->'required_capabilities','{}')
        AND (SELECT array_agg(key ORDER BY key) FROM jsonb_each(e.units))=(SELECT array_agg(a.id::text ORDER BY a.id::text) FROM d2.accounts a WHERE a.resource_id=r.id AND a.window_start<=observed AND a.window_end>observed)
        AND NOT EXISTS(SELECT 1 FROM jsonb_each(e.units) u JOIN d2.accounts a ON a.id=u.key::uuid LEFT JOIN LATERAL(SELECT confidence FROM d2.capacity_limits l WHERE l.account_id=a.id ORDER BY id DESC LIMIT 1) l ON true WHERE coalesce(l.confidence,a.confidence,0)<0.8)
        AND NOT EXISTS(SELECT 1 FROM jsonb_each(e.units) u JOIN d2.balances b ON b.account_id=u.key::uuid WHERE b.available IS NULL);
    END IF;
    eligible=coalesce(eligible,false) AND until_at IS NOT NULL AND until_at>observed;
    SELECT t.eligible INTO last_value FROM d3.eligibility_ticks t WHERE operation_id=item.id ORDER BY observed_at DESC,id DESC LIMIT 1;
    IF eligible OR last_value IS DISTINCT FROM eligible THEN
      INSERT INTO d3.eligibility_ticks(operation_id,eligible,observed_at,valid_until,command_id)
        VALUES(item.id,eligible,observed,CASE WHEN eligible THEN until_at ELSE observed END,cid);n=n+1;
    END IF;
  END LOOP;
  result=jsonb_build_object('transitions',n);
  INSERT INTO d3.commands(id,request,response) VALUES(cid,req,result);RETURN result;
END $$;

CREATE OR REPLACE FUNCTION d4.dispatch_continuation(cid uuid,req jsonb) RETURNS jsonb LANGUAGE plpgsql SECURITY DEFINER SET search_path=pg_catalog,public,d2,d3,d4 AS $$
DECLARE prior jsonb;cp d4.multi_checkpoints;au uuid;body jsonb;captured jsonb;rel text;result jsonb;mi d4.multi_intents;abs d4.absence_seals;absau uuid;reviewau uuid;
BEGIN
 PERFORM d3.lock_state();prior=d3.previous_command(cid,req);IF prior IS NOT NULL THEN RETURN prior;END IF;
 PERFORM d4.require_unheld((req->>'operation_id')::uuid,(req->>'resource_id')::uuid);
 SELECT id INTO reviewau FROM d4.review_authorizations WHERE authorized_version=(SELECT row_version FROM public.operations WHERE id=(req->>'operation_id')::uuid) AND d4.review_checkpoint_safe((req->>'operation_id')::uuid,(SELECT lease_generation FROM public.operations WHERE id=(req->>'operation_id')::uuid));
 SELECT * INTO mi FROM d4.multi_intents WHERE operation_id=(req->>'operation_id')::uuid;
 IF mi.operation_id IS NOT NULL AND NOT d4.multi_manifest_typed(mi.manifest) THEN RAISE EXCEPTION 'Typed compatible v2 intention required' USING ERRCODE='23514';END IF;
 IF mi.operation_id IS NOT NULL AND (
  (mi.manifest->>'resource')::uuid IS DISTINCT FROM (req->>'resource_id')::uuid
  OR NOT EXISTS(SELECT 1 FROM d3.estimate_heads eh JOIN d3.estimates e ON e.id=eh.estimate_id WHERE eh.operation_id=mi.operation_id AND eh.resource_id=(req->>'resource_id')::uuid AND e.units=(SELECT jsonb_object_agg(key,value->'original') FROM jsonb_each(mi.manifest->'accounts')))
  OR NOT EXISTS(SELECT 1 FROM d3.plan_manifests pm CROSS JOIN LATERAL jsonb_array_elements(pm.result->'decisions') d WHERE pm.planning_run_id=(req->>'plan_id')::uuid AND d->>'operationId'=mi.operation_id::text AND d->>'pool'=mi.manifest->>'pool')
  OR NOT EXISTS(SELECT 1 FROM public.operations op JOIN d4.lab_intents li ON li.operation_id=op.id WHERE op.id=mi.operation_id AND op.context_pack_sha256=encode(public.digest(li.context_bytes,'sha256'),'hex') AND convert_from(li.context_bytes,'UTF8')::jsonb->'step_manifest'=mi.manifest))
 THEN RAISE EXCEPTION 'Frozen v2 intent/mapping must match initial and retry CLAIM' USING ERRCODE='23514';END IF;
 SELECT s.* INTO abs FROM d4.absence_seals s WHERE s.operation_id=(req->>'operation_id')::uuid AND d4.absence_safe(s.operation_id,s.generation);
 IF abs.id IS NOT NULL THEN SELECT a.id INTO STRICT absau FROM d4.absence_authorizations a WHERE a.seal_id=abs.id AND a.authorized_version=(SELECT row_version FROM public.operations WHERE id=abs.operation_id);END IF;
 SELECT h.* INTO cp FROM d4.multi_heads h WHERE h.operation_id=(req->>'operation_id')::uuid AND (d4.multi_safe(h.operation_id,h.source_generation) OR d4.review_checkpoint_safe(h.operation_id,h.source_generation));
 IF mi.operation_id IS NOT NULL OR abs.id IS NOT NULL OR reviewau IS NOT NULL THEN
  body=d3.state_body();SELECT c.body INTO STRICT captured FROM d3.plan_manifests m JOIN d3.captures c ON c.id=m.capture_id WHERE m.planning_run_id=(req->>'plan_id')::uuid;
  FOREACH rel IN ARRAY ARRAY['d4.multi_intents','d4.multi_proofs','d4.multi_checkpoints','d4.multi_authorizations','d4.multi_links','d4.multi_heads','d4.recovery_proofs','d4.recovery_settlements','d4.recovery_observations','d4.absence_seals','d4.absence_authorizations','d4.absence_links','d4.review_revisions','d4.review_cases','d4.review_unbound_affected','d4.review_affected','d4.review_barriers','d4.review_closures','d4.review_authorizations','d4.review_links','d4.review_candidates','d4.review_containments'] LOOP
   IF body->rel IS DISTINCT FROM captured->rel THEN RAISE EXCEPTION 'v2 admission readset changed' USING ERRCODE='40001';END IF;
  END LOOP;
 END IF;
 IF cp.id IS NOT NULL THEN SELECT id INTO STRICT au FROM d4.multi_authorizations WHERE checkpoint_id=cp.id;END IF;
 result=d4.dispatch_continuation_before_i8(cid,req);
 IF cp.id IS NOT NULL THEN INSERT INTO d4.multi_links VALUES(cp.id,au,(result->>'attempt_id')::uuid,(result->>'generation')::bigint);END IF;
 IF abs.id IS NOT NULL THEN INSERT INTO d4.absence_links VALUES(abs.id,absau,(result->>'attempt_id')::uuid,(result->>'generation')::bigint);END IF;
 IF reviewau IS NOT NULL THEN INSERT INTO d4.review_links VALUES(reviewau,(result->>'attempt_id')::uuid);END IF;
 RETURN result;
END $$;

CREATE OR REPLACE FUNCTION d4.multi_authorize(cid uuid,checkpoint uuid,expected_version bigint,reason text) RETURNS jsonb LANGUAGE plpgsql SECURITY DEFINER SET search_path=pg_catalog,public,d2,d3,d4 AS $$
DECLARE req jsonb=jsonb_build_object('action','MULTI_AUTHORIZE','checkpoint',checkpoint,'version',expected_version,'reason',reason);prior jsonb;cp d4.multi_checkpoints;op public.operations;pr d4.multi_proofs;result jsonb;
BEGIN
 PERFORM d3.lock_state();prior=d4.checkpoint_previous(cid,req);IF prior IS NOT NULL THEN RETURN prior;END IF;
 SELECT * INTO STRICT cp FROM d4.multi_heads WHERE id=checkpoint;SELECT * INTO STRICT op FROM public.operations WHERE id=cp.operation_id;SELECT * INTO STRICT pr FROM d4.multi_proofs WHERE id=cp.proof_id;
 PERFORM d4.require_unheld(op.id,(SELECT resource_id FROM d2.reservations WHERE operation_id=op.id));
 IF op.state<>'CANCELLED' OR op.row_version IS DISTINCT FROM expected_version OR cp.committed_version IS DISTINCT FROM expected_version OR cp.source_generation<>op.lease_generation
 OR reason IS NULL OR length(btrim(reason)) NOT BETWEEN 1 AND 512 OR EXISTS(SELECT 1 FROM d4.multi_authorizations WHERE checkpoint_id=checkpoint)
 OR NOT d4.multi_effects_safe(op.id) OR NOT d4.multi_head_settled(op.id) OR pr.proof->>'context_hash' IS DISTINCT FROM op.context_pack_sha256 OR pr.proof->>'policy_hash' IS DISTINCT FROM encode(public.digest(op.policy_snapshot::text,'sha256'),'hex')
 OR coalesce((op.policy_snapshot->>'max_attempts')::int,3) NOT BETWEEN 1 AND 20 OR (SELECT count(*) FROM public.execution_attempts WHERE operation_id=op.id)>=coalesce((op.policy_snapshot->>'max_attempts')::int,3)
 THEN RAISE EXCEPTION 'Unused current v2 checkpoint and attempt budget required' USING ERRCODE='23514';END IF;
 UPDATE public.operations SET state='READY',row_version=row_version+1 WHERE id=op.id;PERFORM d2.record_transition(cid,'OPERATION',op.id,'CANCELLED','READY',op.row_version+1,'CONTROL_PLANE','Explicit v2 continuation');
 INSERT INTO d4.multi_authorizations VALUES(cid,checkpoint,op.row_version+1,reason);result=jsonb_build_object('state','READY','row_version',op.row_version+1);
 INSERT INTO d4.checkpoint_commands VALUES(cid,req,result);INSERT INTO public.outbox_events(aggregate_type,aggregate_id,event_type,payload) VALUES('OPERATION',op.id,'D4_MULTI_CONTINUATION_AUTHORIZED',result);RETURN result;
END $$;

CREATE OR REPLACE FUNCTION d4.authorize_continuation(cid uuid,checkpoint uuid,expected_version bigint,reason text) RETURNS jsonb LANGUAGE plpgsql SECURITY DEFINER
SET search_path=pg_catalog,public,d2,d3,d4 AS $$
DECLARE req jsonb=jsonb_build_object('action','AUTHORIZE_CONTINUATION','checkpoint',checkpoint,'version',expected_version,'reason',reason);prior jsonb;cp d4.checkpoints;op public.operations;result jsonb;
BEGIN
 PERFORM d3.lock_state();prior=d4.checkpoint_previous(cid,req);IF prior IS NOT NULL THEN RETURN prior;END IF;
 SELECT * INTO STRICT cp FROM d4.checkpoints WHERE id=checkpoint;SELECT * INTO STRICT op FROM public.operations WHERE id=cp.operation_id;
 PERFORM d4.require_unheld(op.id,(SELECT resource_id FROM d2.reservations WHERE operation_id=op.id));
 IF op.state<>'CANCELLED' OR op.row_version IS DISTINCT FROM expected_version OR cp.committed_version IS DISTINCT FROM expected_version
  OR cp.source_generation<>op.lease_generation OR reason IS NULL OR length(btrim(reason)) NOT BETWEEN 1 AND 512
  OR cp.context_hash IS DISTINCT FROM op.context_pack_sha256 OR cp.policy_hash IS DISTINCT FROM encode(public.digest(op.policy_snapshot::text,'sha256'),'hex')
  OR EXISTS(SELECT 1 FROM d4.unresolved_receipts er WHERE er.operation_id=op.id AND NOT (er.generation=cp.source_generation AND
    ((er.effect_key=op.id||'/'||cp.context_hash||'/step-1' AND er.status='APPLIED') OR (er.effect_key=op.id||'/'||cp.context_hash||'/step-2' AND er.status='ABSENT'))))
  OR EXISTS(SELECT 1 FROM d4.unresolved_receipts WHERE operation_id=op.id AND status='UNKNOWN')
  OR EXISTS(SELECT 1 FROM d4.unresolved_receipts WHERE operation_id=op.id GROUP BY generation,effect_key HAVING count(DISTINCT status)>1)
  OR coalesce((op.policy_snapshot->>'max_attempts')::int,3) NOT BETWEEN 1 AND 20
  OR (SELECT count(*) FROM public.execution_attempts WHERE operation_id=op.id)>=coalesce((op.policy_snapshot->>'max_attempts')::int,3)
 THEN RAISE EXCEPTION 'Exact unused checkpoint cancellation required' USING ERRCODE='23514';END IF;
 UPDATE public.operations SET state='READY',row_version=row_version+1 WHERE id=op.id;
 PERFORM d2.record_transition(cid,'OPERATION',op.id,'CANCELLED','READY',op.row_version+1,'CONTROL_PLANE','Explicit sealed checkpoint continuation');
 INSERT INTO d4.continuation_authorizations VALUES(cid,checkpoint,reason,op.row_version+1);
 result=jsonb_build_object('authorization_id',cid,'state','READY','row_version',op.row_version+1);
 INSERT INTO d4.checkpoint_commands VALUES(cid,req,result);
 INSERT INTO public.outbox_events(aggregate_type,aggregate_id,event_type,payload) VALUES('OPERATION',op.id,'D4_CONTINUATION_AUTHORIZED',result);
 RETURN result;
END $$;

CREATE OR REPLACE FUNCTION d4.absence_authorize(cid uuid,seal uuid,expected_version bigint,reason text) RETURNS jsonb LANGUAGE plpgsql SECURITY DEFINER SET search_path=pg_catalog,public,d2,d3,d4 AS $$
DECLARE req jsonb=jsonb_build_object('action','ABSENCE_AUTHORIZE','seal',seal,'version',expected_version,'reason',reason);prior jsonb;s d4.absence_seals;o public.operations;result jsonb;
BEGIN
 PERFORM d3.lock_state();prior=d4.checkpoint_previous(cid,req);IF prior IS NOT NULL THEN RETURN prior;END IF;SELECT * INTO STRICT s FROM d4.absence_seals WHERE id=seal;SELECT * INTO STRICT o FROM public.operations WHERE id=s.operation_id;
 PERFORM d4.require_unheld(o.id,(SELECT resource_id FROM d2.reservations WHERE operation_id=o.id));
 IF o.state NOT IN ('RETRY_PENDING','READY') OR o.row_version IS DISTINCT FROM expected_version OR o.lease_generation<>s.generation OR NOT d4.recovery_current(s.id) OR EXISTS(SELECT 1 FROM d4.absence_links WHERE seal_id=seal) OR (SELECT count(*) FROM public.execution_attempts WHERE operation_id=o.id)>=coalesce((o.policy_snapshot->>'max_attempts')::int,3) OR reason IS NULL OR length(btrim(reason)) NOT BETWEEN 1 AND 512 THEN RAISE EXCEPTION 'Current unused absence, authorization and budget required' USING ERRCODE='23514';END IF;
 UPDATE public.operations SET state='READY',row_version=row_version+1 WHERE id=o.id;IF o.state<>'READY' THEN PERFORM d2.record_transition(cid,'OPERATION',o.id,o.state,'READY',o.row_version+1,'CONTROL_PLANE','Explicit absence retry');END IF;
 INSERT INTO d4.absence_authorizations VALUES(cid,seal,o.row_version+1,reason);result=jsonb_build_object('state','READY','row_version',o.row_version+1);INSERT INTO d4.checkpoint_commands VALUES(cid,req,result);RETURN result;
END $$;

CREATE OR REPLACE FUNCTION d4.recovery_accept(cid uuid,sid uuid) RETURNS jsonb LANGUAGE plpgsql SECURITY DEFINER SET search_path=pg_catalog,public,d2,d3,d4 AS $$
DECLARE req jsonb=jsonb_build_object('action','RECOVERY_ACCEPT','resolution',sid);prior jsonb;s d4.recovery_settlements;p d4.recovery_proofs;o public.operations;aid uuid;artifact uuid;result jsonb;
BEGIN
 PERFORM d3.lock_state();prior=d4.checkpoint_previous(cid,req);IF prior IS NOT NULL THEN RETURN prior;END IF;SELECT * INTO STRICT s FROM d4.recovery_settlements WHERE id=sid AND terminal;SELECT * INTO STRICT p FROM d4.recovery_proofs WHERE id=s.proof_id;SELECT * INTO STRICT o FROM public.operations WHERE id=s.operation_id;aid=(p.proof->>'attempt')::uuid;
 PERFORM d4.require_unheld(o.id,(SELECT resource_id FROM d2.reservations WHERE operation_id=o.id));
 IF o.state<>'VERIFYING' OR o.lease_generation<>s.generation OR NOT d4.recovery_current(sid) OR NOT d2.integration_eligible(o.task_id) OR EXISTS(SELECT 1 FROM public.execution_evidence WHERE attempt_id=aid AND evidence_type='ACCEPTANCE_FAIL') OR EXISTS(SELECT 1 FROM d2.reservation_balances b JOIN d2.reservations r ON r.id=b.reservation_id WHERE r.operation_id=o.id AND (b.outstanding<>0 OR b.consumed IS DISTINCT FROM (p.evaluation->'cumulative'->>b.account_id::text)::numeric)) THEN RAISE EXCEPTION 'Current independent terminal recovery acceptance required' USING ERRCODE='23514';END IF;
 INSERT INTO public.artifacts(artifact_ref,sha256,media_type,byte_size) VALUES('recovery/'||cid,encode(public.digest(p.proof::text,'sha256'),'hex'),'application/json',octet_length(p.proof::text)) RETURNING id INTO artifact;INSERT INTO public.execution_evidence(attempt_id,artifact_id,evidence_type) VALUES(aid,artifact,'ACCEPTANCE_PASS');
 UPDATE public.operations SET state='COMPLETED',row_version=row_version+1 WHERE id=o.id;UPDATE public.execution_attempts SET state='COMPLETED',finished_at=clock_timestamp() WHERE id=aid;DELETE FROM public.operation_leases WHERE operation_id=o.id;PERFORM d2.record_transition(cid,'OPERATION',o.id,'VERIFYING','COMPLETED',o.row_version+1,'CONTROL_PLANE','Independent terminal recovery acceptance');
 result=jsonb_build_object('state','COMPLETED','row_version',o.row_version+1);INSERT INTO d4.checkpoint_commands VALUES(cid,req,result);INSERT INTO public.outbox_events(aggregate_type,aggregate_id,event_type,payload) VALUES('OPERATION',o.id,'D4_RECOVERY_ACCEPTED',result);RETURN result;
END $$;

CREATE OR REPLACE FUNCTION d4.record_continuation_acceptance(cid uuid,delivery uuid,proof jsonb) RETURNS jsonb LANGUAGE plpgsql SECURITY DEFINER
SET search_path=pg_catalog,public,d2,d3,d4 AS $$
DECLARE info jsonb;op public.operations;link d4.continuation_links;cp d4.checkpoints;artifact uuid;result jsonb;req jsonb=jsonb_build_object('action','ACCEPT_CONTINUATION','delivery',delivery,'proof',proof);prior jsonb;
BEGIN
 PERFORM d3.lock_state();prior=d4.checkpoint_previous(cid,req);IF prior IS NOT NULL THEN RETURN prior;END IF;
 info=d4.i5_inspect(delivery);SELECT * INTO STRICT op FROM public.operations WHERE id=(info->>'operation')::uuid;
 SELECT * INTO STRICT link FROM d4.continuation_links WHERE attempt_id=(info->>'attempt')::uuid;
 SELECT * INTO STRICT cp FROM d4.checkpoints WHERE id=link.checkpoint_id;
 PERFORM d4.require_unheld((info->>'operation')::uuid,(info->>'resource')::uuid);
 IF op.state<>'VERIFYING' OR proof->'process_stopped' IS DISTINCT FROM 'true'::jsonb OR proof->'artifact_valid' IS DISTINCT FROM 'true'::jsonb
  OR proof->'receiver_closed' IS DISTINCT FROM 'true'::jsonb OR proof->'steps' IS DISTINCT FROM '{"step-1":"APPLIED","step-2":"APPLIED"}'::jsonb
  OR proof->>'context_hash' IS DISTINCT FROM op.context_pack_sha256 OR proof->>'manifest_hash' IS DISTINCT FROM cp.manifest_hash
  OR proof->>'attempt' IS DISTINCT FROM info->>'attempt' OR proof->>'generation' IS DISTINCT FROM info->>'generation'
  OR EXISTS(SELECT 1 FROM d2.reservation_balances WHERE reservation_id=cp.reservation_id AND (outstanding<>0 OR consumed<>10))
  OR EXISTS(SELECT 1 FROM d4.unresolved_receipts er WHERE er.operation_id=op.id AND NOT
    ((er.generation=cp.source_generation AND er.effect_key=op.id||'/'||cp.context_hash||'/step-1' AND er.status='APPLIED') OR
     (er.generation=cp.source_generation AND er.effect_key=op.id||'/'||cp.context_hash||'/step-2' AND er.status='ABSENT') OR
     (er.generation=link.generation AND er.effect_key=op.id||'/'||cp.context_hash||'/step-2' AND er.status='APPLIED')))
  OR EXISTS(SELECT 1 FROM d4.unresolved_receipts WHERE operation_id=op.id AND status='UNKNOWN')
  OR EXISTS(SELECT 1 FROM d4.unresolved_receipts WHERE operation_id=op.id GROUP BY generation,effect_key HAVING count(DISTINCT status)>1)
 THEN RAISE EXCEPTION 'Complete sealed continuation and cumulative settlement required' USING ERRCODE='23514';END IF;
 INSERT INTO d2.effect_receipts(operation_id,generation,effect_key,status,evidence_ref) VALUES(op.id,link.generation,op.id||'/'||op.context_pack_sha256||'/step-2','APPLIED','continuation-proof/'||cid);
 INSERT INTO public.artifacts(artifact_ref,sha256,media_type,byte_size) VALUES('continuation-proof/'||cid,encode(public.digest(proof::text,'sha256'),'hex'),'application/json',octet_length(proof::text)) RETURNING id INTO artifact;
 INSERT INTO public.execution_evidence(attempt_id,artifact_id,evidence_type) VALUES(link.attempt_id,artifact,'ACCEPTANCE_PASS');
 result=jsonb_build_object('proof_id',cid);INSERT INTO d4.checkpoint_commands VALUES(cid,req,result);RETURN result;
END $$;

CREATE OR REPLACE FUNCTION d4.multi_accept(cid uuid,delivery uuid,proof jsonb) RETURNS jsonb LANGUAGE plpgsql SECURITY DEFINER SET search_path=pg_catalog,public,d2,d3,d4 AS $$
DECLARE req jsonb=jsonb_build_object('action','ACCEPT_CONTINUATION','delivery',delivery,'proof',proof);prior jsonb;ev jsonb;info jsonb;artifact uuid;result jsonb;
BEGIN
 PERFORM d3.lock_state();prior=d4.checkpoint_previous(cid,req);IF prior IS NOT NULL THEN RETURN prior;END IF;
 ev=d4.multi_evaluate(delivery,proof,true);info=d4.multi_inspect(delivery);
 PERFORM d4.require_unheld((info->>'operation')::uuid,(info->>'resource')::uuid);
 INSERT INTO d2.effect_receipts(operation_id,generation,effect_key,status,evidence_ref) SELECT (info->>'operation')::uuid,(info->>'generation')::bigint,(info->>'operation')||'/'||(info->>'context_hash')||'/'||key,value->>'status','multi-final/'||cid FROM jsonb_each(proof->'receipts');
 INSERT INTO public.artifacts(artifact_ref,sha256,media_type,byte_size) VALUES('multi-final/'||cid,encode(public.digest(proof::text,'sha256'),'hex'),'application/json',octet_length(proof::text)) RETURNING id INTO artifact;
 INSERT INTO public.execution_evidence(attempt_id,artifact_id,evidence_type) VALUES((info->>'attempt')::uuid,artifact,'ACCEPTANCE_PASS');
 result=jsonb_build_object('proof_id',cid);INSERT INTO d4.checkpoint_commands VALUES(cid,req,result);RETURN result;
END $$;

CREATE OR REPLACE FUNCTION d4.lab_record_evidence(cid uuid,delivery uuid,status text,accepted boolean,proof jsonb) RETURNS jsonb
LANGUAGE plpgsql SECURITY DEFINER SET search_path=pg_catalog,public,d2,d3,d4 AS $$
DECLARE info jsonb;prior d4.lab_evidence;receipt uuid;artifact uuid;logical_key text;result jsonb;
BEGIN
  PERFORM d3.lock_state();info=d4.lab_inspect(delivery);
  IF info IS NULL OR cid IS NULL OR status NOT IN ('APPLIED','UNKNOWN') OR status IS NULL OR accepted IS NULL OR
    jsonb_typeof(proof) IS DISTINCT FROM 'object' OR proof->>'context_hash' IS DISTINCT FROM info->>'context_hash' OR
    (accepted AND (status<>'APPLIED' OR proof->'process_stopped' IS DISTINCT FROM 'true'::jsonb OR proof->'artifact_valid' IS DISTINCT FROM 'true'::jsonb OR proof->'receiver_closed' IS DISTINCT FROM 'true'::jsonb OR (info->>'unresolved_evidence')::boolean)) THEN
    RAISE EXCEPTION 'Bound verified evidence required' USING ERRCODE='23514';END IF;
  SELECT * INTO prior FROM d4.lab_evidence WHERE id=cid;
  IF FOUND THEN
    IF prior.delivery_id IS DISTINCT FROM delivery OR prior.effect_status IS DISTINCT FROM status OR prior.acceptance IS DISTINCT FROM accepted OR prior.proof IS DISTINCT FROM proof THEN RAISE EXCEPTION 'Evidence command conflict' USING ERRCODE='23514';END IF;
    RETURN jsonb_build_object('proof_id',cid,'receipt_id',prior.receipt_id);
  END IF;
  IF accepted THEN PERFORM d4.require_unheld((info->>'operation')::uuid,(info->>'resource')::uuid);END IF;
  logical_key=(info->>'operation')||'/'||(info->>'context_hash')||'/step-1';
  SELECT id INTO receipt FROM d2.effect_receipts WHERE operation_id=(info->>'operation')::uuid AND generation=(info->>'generation')::bigint AND effect_key=logical_key AND effect_receipts.status=lab_record_evidence.status;
  IF receipt IS NULL THEN
    INSERT INTO d2.effect_receipts(operation_id,generation,effect_key,status,evidence_ref)
      VALUES((info->>'operation')::uuid,(info->>'generation')::bigint,logical_key,status,'lab-proof/'||cid) RETURNING id INTO receipt;
  END IF;
  INSERT INTO public.artifacts(artifact_ref,sha256,media_type,byte_size)
    VALUES('lab-proof/'||cid,encode(public.digest(proof::text,'sha256'),'hex'),'application/json',octet_length(proof::text)) RETURNING id INTO artifact;
  IF accepted THEN INSERT INTO public.execution_evidence(attempt_id,artifact_id,evidence_type) VALUES((info->>'attempt')::uuid,artifact,'ACCEPTANCE_PASS');END IF;
  INSERT INTO d4.lab_evidence(id,delivery_id,effect_status,receipt_id,acceptance,proof) VALUES(cid,delivery,status,receipt,accepted,proof);
  RETURN jsonb_build_object('proof_id',cid,'receipt_id',receipt);
END $$;

CREATE OR REPLACE FUNCTION d4.worker_execution_status(wid uuid,delivery uuid) RETURNS jsonb
LANGUAGE plpgsql SECURITY DEFINER SET search_path=pg_catalog,public,d2,d3,d4 AS $$
DECLARE info jsonb;safe boolean;
BEGIN
 PERFORM d3.lock_state();PERFORM d4.require_worker(wid);
 IF wid IS NULL OR delivery IS NULL OR NOT EXISTS(SELECT 1 FROM d4.deliveries WHERE id=delivery AND worker_id=wid)
 THEN RAISE EXCEPTION 'Execution status ownership mismatch' USING ERRCODE='42501';END IF;
 info=d4.lab_inspect(delivery);
 SELECT op.state='COMPLETED' AND a.state='COMPLETED' AND op.lease_generation=(info->>'generation')::bigint
  AND NOT EXISTS(SELECT 1 FROM public.operation_leases WHERE operation_id=op.id)
  AND NOT EXISTS(SELECT 1 FROM d2.reservations r JOIN d2.reservation_balances b ON b.reservation_id=r.id WHERE r.operation_id=op.id AND b.outstanding<>0)
  AND EXISTS(SELECT 1 FROM public.execution_evidence WHERE attempt_id=a.id AND evidence_type='ACCEPTANCE_PASS')
  AND NOT EXISTS(SELECT 1 FROM public.execution_evidence WHERE attempt_id=a.id AND evidence_type='ACCEPTANCE_FAIL')
  AND NOT EXISTS(SELECT 1 FROM d4.unresolved_receipts WHERE operation_id=op.id AND status='UNKNOWN')
  AND NOT EXISTS(SELECT 1 FROM d4.unresolved_receipts WHERE operation_id=op.id GROUP BY generation,effect_key HAVING count(DISTINCT status)>1)
  AND (EXISTS(SELECT 1 FROM d4.lab_evidence e WHERE e.delivery_id=delivery AND e.acceptance AND e.effect_status='APPLIED'
    AND e.proof->'process_stopped'='true'::jsonb AND e.proof->'receiver_closed'='true'::jsonb AND e.proof->'artifact_valid'='true'::jsonb)
   OR EXISTS(SELECT 1 FROM d4.recovery_settlements rs JOIN d4.recovery_proofs rp ON rp.id=rs.proof_id WHERE rs.operation_id=op.id AND rs.generation=op.lease_generation AND rs.terminal AND rp.proof->>'attempt'=a.id::text AND d4.recovery_current(rs.id))
   OR EXISTS(SELECT 1 FROM d4.checkpoint_commands c WHERE c.request->>'action'='ACCEPT_CONTINUATION' AND c.request->>'delivery'=delivery::text
    AND c.request->'proof'->'process_stopped'='true'::jsonb AND c.request->'proof'->'receiver_closed'='true'::jsonb
    AND c.request->'proof'->>'attempt'=a.id::text AND c.request->'proof'->>'generation'=info->>'generation'))
 INTO safe FROM public.operations op JOIN public.execution_attempts a ON a.id=(info->>'attempt')::uuid WHERE op.id=(info->>'operation')::uuid;
 IF NOT coalesce(safe,false) THEN SELECT EXISTS(SELECT 1 FROM d4.absence_seals s JOIN public.operations o ON o.id=s.operation_id WHERE s.delivery_id=delivery AND s.attempt_id=(info->>'attempt')::uuid AND o.state='RETRY_PENDING' AND o.lease_generation=s.generation AND NOT EXISTS(SELECT 1 FROM public.operation_leases WHERE operation_id=o.id) AND d4.absence_settled(s.id)) INTO safe;END IF;
 safe=coalesce(safe,false) AND NOT d4.review_blocked((info->>'operation')::uuid,(info->>'resource')::uuid,true);
 RETURN jsonb_build_object('schema','d4.worker.execution-status.v1','delivery_id',delivery,'operation',info->'operation',
  'attempt',info->'attempt','worker',info->'worker','resource',info->'resource','generation',info->'generation',
  'state',info->'state','retirable',coalesce(safe,false));
END $$;

REVOKE ALL ON ALL TABLES IN SCHEMA d4 FROM PUBLIC;
REVOKE ALL ON FUNCTION d2.task_eligible(uuid),d2.integration_eligible(uuid) FROM PUBLIC;
DO $$ DECLARE f record;BEGIN FOR f IN SELECT p.oid::regprocedure n FROM pg_proc p JOIN pg_namespace ns ON ns.oid=p.pronamespace WHERE ns.nspname='d4' AND (p.proname LIKE 'review_%' OR p.proname IN ('canonical_results','revision_current','case_blocks','require_unheld','continuation_safe')) LOOP EXECUTE format('REVOKE ALL ON FUNCTION %s FROM PUBLIC',f.n);END LOOP;END $$;
