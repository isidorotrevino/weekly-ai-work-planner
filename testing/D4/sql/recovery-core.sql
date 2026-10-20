-- SPDX-License-Identifier: GPL-3.0-only
-- D4-A17/A18/A19: append-only monotonic resolution, native checkpoints, terminal recovery.
CREATE TABLE d4.recovery_proofs(id uuid PRIMARY KEY,delivery_id uuid NOT NULL REFERENCES d4.deliveries(id),proof jsonb NOT NULL,evaluation jsonb NOT NULL,receipt_basis jsonb NOT NULL);
CREATE TABLE d4.recovery_observations(id uuid PRIMARY KEY,receipt_id uuid NOT NULL UNIQUE REFERENCES d2.effect_receipts(id),delivery_id uuid NOT NULL REFERENCES d4.deliveries(id),receiver_id uuid NOT NULL,step text NOT NULL,receipt jsonb NOT NULL);
CREATE TABLE d4.recovery_settlements(id uuid PRIMARY KEY,proof_id uuid NOT NULL UNIQUE REFERENCES d4.recovery_proofs(id),operation_id uuid NOT NULL REFERENCES public.operations(id),generation bigint NOT NULL,receipt_basis jsonb NOT NULL,terminal boolean NOT NULL,UNIQUE(operation_id,generation));
DO $$ DECLARE t text;BEGIN FOREACH t IN ARRAY ARRAY['recovery_proofs','recovery_settlements','recovery_observations'] LOOP EXECUTE format('CREATE TRIGGER immutable_fact BEFORE UPDATE OR DELETE OR TRUNCATE ON d4.%I FOR EACH STATEMENT EXECUTE FUNCTION public.d2_reject_fact_mutation()',t);END LOOP;END $$;
INSERT INTO public.state_transition_rules VALUES('OPERATION','RECONCILING','CANCELLED','SEALED_RECOVERY_CHECKPOINT');
CREATE FUNCTION d4.receipt_basis(oid uuid,gen bigint) RETURNS jsonb LANGUAGE sql STABLE SECURITY DEFINER SET search_path=pg_catalog,public,d2 AS $$ SELECT coalesce(jsonb_agg(to_jsonb(e) ORDER BY id),'[]') FROM d2.effect_receipts e WHERE operation_id=oid AND generation=gen; $$;
CREATE FUNCTION d4.recovery_current(sid uuid) RETURNS boolean LANGUAGE sql STABLE SECURITY DEFINER SET search_path=pg_catalog,public,d2,d3,d4 AS $$
 SELECT EXISTS(SELECT 1 FROM d4.recovery_settlements s JOIN d4.recovery_proofs p ON p.id=s.proof_id JOIN public.operations o ON o.id=s.operation_id
 WHERE s.id=sid AND s.receipt_basis=d4.receipt_basis(s.operation_id,s.generation) AND p.proof->>'context_hash'=o.context_pack_sha256 AND p.proof->>'policy_hash'=encode(public.digest(o.policy_snapshot::text,'sha256'),'hex'));
$$;
CREATE FUNCTION d4.receipt_resolved(eid uuid) RETURNS boolean LANGUAGE sql STABLE SECURITY DEFINER SET search_path=pg_catalog,public,d2,d4 AS $$
 SELECT EXISTS(SELECT 1 FROM d4.recovery_settlements s CROSS JOIN LATERAL jsonb_array_elements(s.receipt_basis) e WHERE e->>'id'=eid::text AND d4.recovery_current(s.id));
$$;
CREATE VIEW d4.unresolved_receipts AS SELECT * FROM d2.effect_receipts e WHERE NOT d4.receipt_resolved(e.id);
CREATE FUNCTION d4.recovery_info(delivery uuid) RETURNS jsonb LANGUAGE plpgsql SECURITY DEFINER SET search_path=pg_catalog,public,d2,d3,d4 AS $$
DECLARE info jsonb=d4.multi_inspect(delivery);m jsonb;steps jsonb;accounts jsonb;ctx jsonb;h text;
BEGIN
 IF info IS NULL THEN RAISE EXCEPTION 'Exact delivery required' USING ERRCODE='23514';END IF;
 IF info->'multi_checkpoint'='true'::jsonb THEN m=info->'manifest';IF NOT d4.multi_manifest_typed(m) THEN RAISE EXCEPTION 'Closed v2 required' USING ERRCODE='23514';END IF;
 ELSE
  ctx=convert_from(decode(info->>'context_b64','base64'),'UTF8')::jsonb;
  IF ctx->>'fixture'='PARTIAL' THEN
   IF NOT EXISTS(SELECT 1 FROM d4.step_intents WHERE operation_id=(info->>'operation')::uuid AND manifest='{"schema":"d4.steps.v1","steps":[{"id":"step-1","units":4},{"id":"step-2","units":6}]}'::jsonb) THEN RAISE EXCEPTION 'Frozen v1 fixture required' USING ERRCODE='23514';END IF;
   SELECT jsonb_agg(jsonb_build_object('id',x.step->>'id','effect_hash',encode(public.digest('synthetic-effect:'||(info->>'operation')||':'||(x.step->>'id'),'sha256'),'hex'),'cost',(SELECT jsonb_object_agg(a->>'account_id',x.step->'units') FROM jsonb_array_elements(info->'accounts') a)) ORDER BY n) INTO steps FROM jsonb_array_elements(ctx->'step_manifest'->'steps') WITH ORDINALITY x(step,n);
  ELSIF ctx->>'fixture'='SUCCESS' THEN steps=jsonb_build_array(jsonb_build_object('id','step-1','effect_hash',encode(public.digest('synthetic-effect:'||(info->>'operation'),'sha256'),'hex'),'cost',(SELECT jsonb_object_agg(a->>'account_id',info->'consumed_units') FROM jsonb_array_elements(info->'accounts') a)));
  ELSE RAISE EXCEPTION 'Supported frozen fixture required' USING ERRCODE='23514';END IF;
  SELECT jsonb_object_agg(a.id,jsonb_build_object('original',oa.units,'dimension',a.dimension,'unit',a.unit,'start',a.window_start,'end',a.window_end)) INTO accounts FROM d2.operation_accounts oa JOIN d2.accounts a ON a.id=oa.account_id WHERE oa.operation_id=(info->>'operation')::uuid;
  m=jsonb_build_object('schema','d4.steps.v2','resource',info->'resource','pool',(SELECT pool FROM d2.reservations WHERE operation_id=(info->>'operation')::uuid),'accounts',accounts,'steps',steps);
 END IF;
 IF info->'multi_checkpoint' IS DISTINCT FROM 'true'::jsonb AND info->'continuation'='true'::jsonb THEN
  SELECT info||jsonb_build_object('parent_evaluation',jsonb_build_object('applied',jsonb_build_object('step-1',jsonb_build_object('attempt',cp.source_attempt,'generation',cp.source_generation,'payloadHash',encode(public.digest('synthetic-effect:'||(info->>'operation')||':step-1','sha256'),'hex'))),'cumulative',(SELECT jsonb_object_agg(a->>'account_id',4) FROM jsonb_array_elements(info->'accounts') a))) INTO info FROM d4.checkpoints cp WHERE cp.operation_id=(info->>'operation')::uuid;
 END IF;
 h=encode(public.digest(m::text,'sha256'),'hex');
 RETURN info||jsonb_build_object('recovery_manifest',m,'recovery_manifest_hash',h,'receipt_basis',d4.receipt_basis((info->>'operation')::uuid,(info->>'generation')::bigint));
END $$;
CREATE FUNCTION d4.recovery_evaluate(delivery uuid,proof jsonb) RETURNS jsonb LANGUAGE plpgsql SECURITY DEFINER SET search_path=pg_catalog,public,d2,d3,d4 AS $$
DECLARE i jsonb=d4.recovery_info(delivery);m jsonb=i->'recovery_manifest';o public.operations;res d2.reservations;parent jsonb=coalesce(i->'parent_evaluation','{}');applied jsonb=coalesce(parent->'applied','{}');remaining boolean=false;progress int=0;s jsonb;r jsonb;e record;a record;cost numeric;delta numeric;prev numeric;consumes jsonb='{}';releases jsonb='{}';cumulative jsonb='{}';terminal boolean;allowed jsonb;expected_key text;
BEGIN
 SELECT * INTO STRICT o FROM public.operations WHERE id=(i->>'operation')::uuid;SELECT * INTO STRICT res FROM d2.reservations WHERE operation_id=o.id;
 IF o.state NOT IN ('RECONCILING','BLOCKED_APPROVAL') OR (i->>'lease_expired')::boolean IS DISTINCT FROM true
 OR NOT EXISTS(SELECT 1 FROM public.operation_leases l WHERE l.operation_id=o.id AND l.attempt_id=(i->>'attempt')::uuid AND l.worker_id=(i->>'worker')::uuid AND l.fencing_generation=o.lease_generation AND o.lease_generation=(i->>'generation')::bigint)
 OR proof->>'schema' IS DISTINCT FROM 'd4.recovery.proof.v1' OR proof->>'recovery_manifest_hash' IS DISTINCT FROM i->>'recovery_manifest_hash'
 OR proof->'receipt_basis' IS DISTINCT FROM i->'receipt_basis' OR proof->>'context_hash' IS DISTINCT FROM o.context_pack_sha256 OR proof->>'policy_hash' IS DISTINCT FROM encode(public.digest(o.policy_snapshot::text,'sha256'),'hex')
 OR EXISTS(SELECT 1 FROM jsonb_each(jsonb_build_object('operation',i->'operation','attempt',i->'attempt','worker',i->'worker','resource',i->'resource','generation',i->'generation')) x WHERE proof->x.key IS DISTINCT FROM x.value)
 OR proof->'process_stopped' IS DISTINCT FROM 'true'::jsonb OR proof->'artifact_valid' IS DISTINCT FROM 'true'::jsonb OR proof->'receiver_closed' IS DISTINCT FROM 'true'::jsonb
 OR coalesce(proof->>'host_observation_hash','') !~ '^[a-f0-9]{64}$' OR coalesce(proof->>'stdout_hash','') !~ '^[a-f0-9]{64}$' OR coalesce(proof->>'stderr_hash','') !~ '^[a-f0-9]{64}$'
 OR jsonb_typeof(proof->'receipts') IS DISTINCT FROM 'object' OR coalesce((proof->>'close_sequence')::bigint,0)<=0
 OR NOT EXISTS(SELECT 1 FROM d4.lab_grants g WHERE g.request->>'delivery'=delivery::text AND g.response->>'receiver_id'=proof->'receiver_seal'->>'receiverId')
 OR proof->'receiver_seal'->'steps' IS DISTINCT FROM proof->'receipts' OR proof->'receiver_seal'->'sequence' IS DISTINCT FROM proof->'close_sequence'
 OR EXISTS(SELECT 1 FROM jsonb_each(jsonb_build_object('operation',i->'operation','attempt',i->'attempt','worker',i->'worker','resource',i->'resource','generation',i->'generation')) x WHERE proof->'receiver_seal'->'identity'->x.key IS DISTINCT FROM x.value)
 OR (i->'multi_checkpoint'='true'::jsonb AND proof->'parent_checkpoint' IS DISTINCT FROM i->'parent_checkpoint')
 OR (i->'multi_checkpoint'='true'::jsonb AND i->'parent_checkpoint'<>'null'::jsonb AND NOT EXISTS(SELECT 1 FROM d4.multi_links l JOIN d4.multi_checkpoints cp ON cp.id=l.checkpoint_id WHERE cp.id=(i->>'parent_checkpoint')::uuid AND l.attempt_id=(i->>'attempt')::uuid AND l.generation=o.lease_generation AND cp.source_generation+1=o.lease_generation))
 OR res.resource_id IS DISTINCT FROM (m->>'resource')::uuid OR res.pool IS DISTINCT FROM m->>'pool'
 THEN RAISE EXCEPTION 'Exact independently stopped sealed recovery required' USING ERRCODE='23514';END IF;
 -- Prior-generation evidence must remain explained by native checkpoints/resolutions.
 IF EXISTS(SELECT 1 FROM d2.effect_receipts er WHERE er.operation_id=o.id AND er.generation<>o.lease_generation AND NOT d4.receipt_resolved(er.id) AND NOT EXISTS(
 SELECT 1 FROM d4.multi_checkpoints cp JOIN d4.multi_proofs pr ON pr.id=cp.proof_id CROSS JOIN LATERAL jsonb_each(pr.proof->'receipts') rr WHERE cp.operation_id=o.id AND cp.source_generation=er.generation AND er.effect_key=o.id||'/'||o.context_pack_sha256||'/'||rr.key AND er.status=rr.value->>'status') AND NOT EXISTS(
 SELECT 1 FROM d4.checkpoints cp WHERE cp.operation_id=o.id AND cp.source_generation=er.generation AND ((er.effect_key=o.id||'/'||o.context_pack_sha256||'/step-1' AND er.status='APPLIED') OR (er.effect_key=o.id||'/'||o.context_pack_sha256||'/step-2' AND er.status='ABSENT')))) THEN RAISE EXCEPTION 'Prior evidence unresolved' USING ERRCODE='23514';END IF;
 SELECT coalesce(jsonb_agg(value->>'id' ORDER BY n),'[]') INTO allowed FROM jsonb_array_elements(m->'steps') WITH ORDINALITY x(value,n) WHERE NOT applied ? (value->>'id');
 IF (SELECT array_agg(key ORDER BY key) FROM jsonb_each(proof->'receipts')) IS DISTINCT FROM (SELECT array_agg(value#>>'{}' ORDER BY value#>>'{}') FROM jsonb_array_elements(allowed)) THEN RAISE EXCEPTION 'Complete recovery suffix required' USING ERRCODE='23514';END IF;
 FOR s IN SELECT value FROM jsonb_array_elements(m->'steps') LOOP
  IF applied ? (s->>'id') THEN CONTINUE;END IF;r=proof->'receipts'->(s->>'id');
  IF r->>'status' IS NULL OR r->>'status' NOT IN ('APPLIED','ABSENT') OR r->'generation' IS DISTINCT FROM i->'generation' OR (r->>'status'='ABSENT' AND r->'closed' IS DISTINCT FROM 'true'::jsonb) THEN RAISE EXCEPTION 'No UNKNOWN or open result' USING ERRCODE='23514';END IF;
  IF r->>'status'='ABSENT' THEN remaining=true;
  ELSE IF remaining OR r->>'payloadHash' IS DISTINCT FROM s->>'effect_hash' THEN RAISE EXCEPTION 'Monotonic exact prefix required' USING ERRCODE='23514';END IF;progress=progress+1;applied=applied||jsonb_build_object(s->>'id',jsonb_build_object('attempt',i->'attempt','generation',i->'generation','payloadHash',r->>'payloadHash'));END IF;
 END LOOP;
 FOR e IN SELECT * FROM d2.effect_receipts WHERE operation_id=o.id AND generation=o.lease_generation LOOP
  expected_key=CASE WHEN EXISTS(SELECT 1 FROM d4.step_intents WHERE operation_id=o.id) OR i->'multi_checkpoint'='true'::jsonb THEN o.id||'/'||o.context_pack_sha256||'/' ELSE o.id||'/'||o.context_pack_sha256 END;
  IF expected_key=o.id||'/'||o.context_pack_sha256 THEN r=proof->'receipts'->'step-1';IF e.effect_key<>expected_key THEN RAISE EXCEPTION 'Unknown logical effect' USING ERRCODE='23514';END IF;
  ELSE IF left(e.effect_key,length(expected_key))<>expected_key THEN RAISE EXCEPTION 'Unknown logical effect' USING ERRCODE='23514';END IF;r=proof->'receipts'->substr(e.effect_key,length(expected_key)+1);END IF;
  IF r IS NULL OR (e.status='APPLIED' AND r->>'status'<>'APPLIED') THEN RAISE EXCEPTION 'Applied fact cannot be revoked' USING ERRCODE='23514';END IF;
  -- Any archived payload assertion must agree; an incompatible hash is never adjudicated away.
  IF EXISTS(SELECT 1 FROM d4.recovery_observations ro WHERE ro.receipt_id=e.id AND (ro.receiver_id::text IS DISTINCT FROM proof->'receiver_seal'->>'receiverId' OR (ro.receipt->>'payloadHash' IS NOT NULL AND ro.receipt->>'payloadHash' IS DISTINCT FROM r->>'payloadHash'))) OR EXISTS(SELECT 1 FROM d4.lab_evidence le WHERE le.receipt_id=e.id AND le.proof->'receipt'->>'payloadHash' IS NOT NULL AND le.proof->'receipt'->>'payloadHash' IS DISTINCT FROM r->>'payloadHash') THEN RAISE EXCEPTION 'Historical payload mismatch' USING ERRCODE='23514';END IF;
 END LOOP;
 terminal=NOT remaining;
 IF progress=0 OR (NOT terminal AND (NOT coalesce((o.policy_snapshot->>'interruptible')::boolean,false) OR (SELECT count(*) FROM public.execution_attempts WHERE operation_id=o.id)>=coalesce((o.policy_snapshot->>'max_attempts')::int,3))) THEN RAISE EXCEPTION 'Progress and continuation budget required' USING ERRCODE='23514';END IF;
 IF (SELECT array_agg(account_id::text ORDER BY account_id) FROM d2.operation_accounts WHERE operation_id=o.id) IS DISTINCT FROM (SELECT array_agg(key ORDER BY key) FROM jsonb_each(m->'accounts')) OR (SELECT array_agg(account_id::text ORDER BY account_id) FROM d2.reservation_balances WHERE reservation_id=res.id) IS DISTINCT FROM (SELECT array_agg(key ORDER BY key) FROM jsonb_each(m->'accounts')) THEN RAISE EXCEPTION 'Complete account binding required' USING ERRCODE='23514';END IF;
 FOR a IN SELECT b.*,oa.units,ac.dimension,ac.unit,ac.window_start,ac.window_end FROM d2.reservation_balances b JOIN d2.operation_accounts oa ON oa.operation_id=o.id AND oa.account_id=b.account_id JOIN d2.accounts ac ON ac.id=b.account_id WHERE b.reservation_id=res.id ORDER BY b.account_id LOOP
  SELECT coalesce(sum((value->'cost'->>a.account_id::text)::numeric),0) INTO cost FROM jsonb_array_elements(m->'steps') WHERE applied ? (value->>'id');prev=coalesce((parent->'cumulative'->>a.account_id::text)::numeric,0);
  IF i->'multi_checkpoint' IS DISTINCT FROM 'true'::jsonb AND (i->>'continuation')::boolean THEN prev=4;END IF;
  delta=cost-a.consumed;
  IF a.units IS DISTINCT FROM (m->'accounts'->a.account_id::text->>'original')::numeric OR a.dimension IS DISTINCT FROM m->'accounts'->a.account_id::text->>'dimension' OR a.unit IS DISTINCT FROM m->'accounts'->a.account_id::text->>'unit'
  OR a.window_start IS DISTINCT FROM (m->'accounts'->a.account_id::text->>'start')::timestamptz OR a.window_end IS DISTINCT FROM (m->'accounts'->a.account_id::text->>'end')::timestamptz OR clock_timestamp()<a.window_start OR clock_timestamp()>=a.window_end
  OR delta<0 OR delta>a.outstanding OR a.consumed NOT IN (prev,cost) OR (a.consumed=prev AND a.outstanding<>a.units) OR (a.consumed<>prev AND a.outstanding<>0)
  THEN RAISE EXCEPTION 'Exact recoverable journal and live accounts required' USING ERRCODE='23514';END IF;
  cumulative=cumulative||jsonb_build_object(a.account_id::text,cost);consumes=consumes||jsonb_build_object(a.account_id::text,delta);releases=releases||jsonb_build_object(a.account_id::text,a.outstanding-delta);
 END LOOP;
 RETURN jsonb_build_object('applied',applied,'cumulative',cumulative,'consume',consumes,'release',releases,'terminal',terminal,'identity',jsonb_build_object('operation',i->'operation','attempt',i->'attempt','worker',i->'worker','resource',i->'resource','generation',i->'generation'),'attempt_count',(SELECT count(*) FROM public.execution_attempts WHERE operation_id=o.id));
END $$;
CREATE FUNCTION d4.recovery_record(pid uuid,delivery uuid,proof jsonb) RETURNS jsonb LANGUAGE plpgsql SECURITY DEFINER SET search_path=pg_catalog,public,d2,d3,d4 AS $$
DECLARE old d4.recovery_proofs;ev jsonb;
BEGIN
 PERFORM d3.lock_state();SELECT * INTO old FROM d4.recovery_proofs WHERE id=pid;IF FOUND THEN IF old.delivery_id IS DISTINCT FROM delivery OR old.proof IS DISTINCT FROM proof THEN RAISE EXCEPTION 'Recovery proof conflict' USING ERRCODE='23514';END IF;RETURN old.evaluation;END IF;
 IF pid IS NULL THEN RAISE EXCEPTION 'Proof ID required' USING ERRCODE='23514';END IF;ev=d4.recovery_evaluate(delivery,proof);INSERT INTO d4.recovery_proofs VALUES(pid,delivery,proof,ev,proof->'receipt_basis');RETURN ev;
END $$;
CREATE FUNCTION d4.recovery_settle(cid uuid,pid uuid,expected_version bigint) RETURNS jsonb LANGUAGE plpgsql SECURITY DEFINER SET search_path=pg_catalog,public,d2,d3,d4 AS $$
DECLARE req jsonb=jsonb_build_object('action','RECOVERY_SETTLE','proof',pid,'version',expected_version);prior jsonb;p d4.recovery_proofs;i jsonb;o public.operations;ev jsonb;res d2.reservations;entries jsonb;cp_proof jsonb;new_state text;result jsonb;
BEGIN
 PERFORM d3.lock_state();prior=d4.checkpoint_previous(cid,req);IF prior IS NOT NULL THEN RETURN prior;END IF;SELECT * INTO STRICT p FROM d4.recovery_proofs WHERE id=pid;i=d4.recovery_info(p.delivery_id);SELECT * INTO STRICT o FROM public.operations WHERE id=(i->>'operation')::uuid;
 IF o.row_version IS DISTINCT FROM expected_version THEN RAISE EXCEPTION 'Recovery version changed' USING ERRCODE='40001';END IF;
 ev=d4.recovery_evaluate(p.delivery_id,p.proof);IF ev IS DISTINCT FROM p.evaluation THEN RAISE EXCEPTION 'Recovery evaluation changed' USING ERRCODE='40001';END IF;
 IF o.state='BLOCKED_APPROVAL' THEN UPDATE public.operations SET state='RECONCILING',row_version=row_version+1 WHERE id=o.id;PERFORM d2.record_transition(public.gen_random_uuid(),'OPERATION',o.id,'BLOCKED_APPROVAL','RECONCILING',o.row_version+1,'CONTROL_PLANE','Authoritative monotonic recovery');o.row_version=o.row_version+1;o.state='RECONCILING';END IF;
 SELECT * INTO STRICT res FROM d2.reservations WHERE operation_id=o.id;
 SELECT jsonb_agg(jsonb_build_object('account_id',key,'settled',value,'consumed',value) ORDER BY key) INTO entries FROM jsonb_each(ev->'consume');PERFORM d2.capacity(public.gen_random_uuid(),jsonb_build_object('action','CONSUME','reservation_id',res.id,'entries',entries,'reason','Conclusive recovery delta'));
 SELECT jsonb_agg(jsonb_build_object('account_id',key,'settled',value) ORDER BY key) INTO entries FROM jsonb_each(ev->'release');PERFORM d2.capacity(public.gen_random_uuid(),jsonb_build_object('action','RELEASE','reservation_id',res.id,'entries',entries,'reason','Closed recovery remainder'));
 IF p.receipt_basis IS DISTINCT FROM d4.receipt_basis(o.id,o.lease_generation) OR EXISTS(SELECT 1 FROM d2.operation_accounts oa JOIN d2.accounts ac ON ac.id=oa.account_id WHERE oa.operation_id=o.id AND (clock_timestamp()<ac.window_start OR clock_timestamp()>=ac.window_end)) THEN RAISE EXCEPTION 'Recovery basis/window changed during settlement' USING ERRCODE='23514';END IF;
 new_state=CASE WHEN (ev->>'terminal')::boolean THEN 'VERIFYING' ELSE 'CANCELLED' END;
 UPDATE public.operations SET state=new_state,row_version=row_version+1 WHERE id=o.id;UPDATE public.execution_attempts SET state=new_state,finished_at=clock_timestamp() WHERE id=(i->>'attempt')::uuid;
 PERFORM d2.record_transition(cid,'OPERATION',o.id,'RECONCILING',new_state,o.row_version+1,'CONTROL_PLANE','Conclusive sealed recovery');
 IF new_state='CANCELLED' THEN
  DELETE FROM public.operation_leases WHERE operation_id=o.id;
  INSERT INTO d4.checkpoint_requests VALUES(cid,p.delivery_id,o.id,(i->>'attempt')::uuid,o.lease_generation,expected_version);
  IF i->'multi_checkpoint'='true'::jsonb THEN
   cp_proof=p.proof||jsonb_build_object('schema','d4.checkpoint.proof.v2','manifest_hash',i->'manifest_hash');INSERT INTO d4.multi_proofs VALUES(pid,p.delivery_id,cid,cp_proof,ev);INSERT INTO d4.multi_checkpoints VALUES(cid,o.id,(i->>'parent_checkpoint')::uuid,pid,(i->>'attempt')::uuid,o.lease_generation,res.id,o.row_version+1);
  ELSE
   IF (i->>'continuation')::boolean THEN RAISE EXCEPTION 'v1 supports one partial checkpoint' USING ERRCODE='23514';END IF;
   cp_proof=p.proof||jsonb_build_object('schema','d4.checkpoint.proof.v1','manifest_hash',i->'manifest_hash','steps','{"step-1":"APPLIED","step-2":"ABSENT"}'::jsonb,'consumed_units',4);INSERT INTO d4.checkpoint_proofs VALUES(pid,cid,cp_proof);INSERT INTO d4.checkpoints VALUES(cid,cid,pid,o.id,(i->>'attempt')::uuid,o.lease_generation,res.id,o.context_pack_sha256,encode(public.digest(o.policy_snapshot::text,'sha256'),'hex'),i->>'manifest_hash',o.row_version+1);
  END IF;
 END IF;
 INSERT INTO d4.recovery_settlements VALUES(cid,pid,o.id,o.lease_generation,d4.receipt_basis(o.id,o.lease_generation),(ev->>'terminal')::boolean);
 result=jsonb_build_object('state',new_state,'checkpoint_id',CASE WHEN new_state='CANCELLED' THEN cid ELSE NULL END,'resolution_id',cid,'row_version',o.row_version+1);INSERT INTO d4.checkpoint_commands VALUES(cid,req,result);INSERT INTO public.outbox_events(aggregate_type,aggregate_id,event_type,payload) VALUES('OPERATION',o.id,'D4_RECOVERY_SETTLED',result);RETURN result;
END $$;
CREATE FUNCTION d4.recovery_accept(cid uuid,sid uuid) RETURNS jsonb LANGUAGE plpgsql SECURITY DEFINER SET search_path=pg_catalog,public,d2,d3,d4 AS $$
DECLARE req jsonb=jsonb_build_object('action','RECOVERY_ACCEPT','resolution',sid);prior jsonb;s d4.recovery_settlements;p d4.recovery_proofs;o public.operations;aid uuid;artifact uuid;result jsonb;
BEGIN
 PERFORM d3.lock_state();prior=d4.checkpoint_previous(cid,req);IF prior IS NOT NULL THEN RETURN prior;END IF;SELECT * INTO STRICT s FROM d4.recovery_settlements WHERE id=sid AND terminal;SELECT * INTO STRICT p FROM d4.recovery_proofs WHERE id=s.proof_id;SELECT * INTO STRICT o FROM public.operations WHERE id=s.operation_id;aid=(p.proof->>'attempt')::uuid;
 IF o.state<>'VERIFYING' OR o.lease_generation<>s.generation OR NOT d4.recovery_current(sid) OR NOT d2.integration_eligible(o.task_id) OR EXISTS(SELECT 1 FROM public.execution_evidence WHERE attempt_id=aid AND evidence_type='ACCEPTANCE_FAIL') OR EXISTS(SELECT 1 FROM d2.reservation_balances b JOIN d2.reservations r ON r.id=b.reservation_id WHERE r.operation_id=o.id AND (b.outstanding<>0 OR b.consumed IS DISTINCT FROM (p.evaluation->'cumulative'->>b.account_id::text)::numeric)) THEN RAISE EXCEPTION 'Current independent terminal recovery acceptance required' USING ERRCODE='23514';END IF;
 INSERT INTO public.artifacts(artifact_ref,sha256,media_type,byte_size) VALUES('recovery/'||cid,encode(public.digest(p.proof::text,'sha256'),'hex'),'application/json',octet_length(p.proof::text)) RETURNING id INTO artifact;INSERT INTO public.execution_evidence(attempt_id,artifact_id,evidence_type) VALUES(aid,artifact,'ACCEPTANCE_PASS');
 UPDATE public.operations SET state='COMPLETED',row_version=row_version+1 WHERE id=o.id;UPDATE public.execution_attempts SET state='COMPLETED',finished_at=clock_timestamp() WHERE id=aid;DELETE FROM public.operation_leases WHERE operation_id=o.id;PERFORM d2.record_transition(cid,'OPERATION',o.id,'VERIFYING','COMPLETED',o.row_version+1,'CONTROL_PLANE','Independent terminal recovery acceptance');
 result=jsonb_build_object('state','COMPLETED','row_version',o.row_version+1);INSERT INTO d4.checkpoint_commands VALUES(cid,req,result);INSERT INTO public.outbox_events(aggregate_type,aggregate_id,event_type,payload) VALUES('OPERATION',o.id,'D4_RECOVERY_ACCEPTED',result);RETURN result;
END $$;
ALTER FUNCTION d3.state_relations() RENAME TO state_relations_before_i9;
CREATE FUNCTION d3.state_relations() RETURNS text[] LANGUAGE sql IMMUTABLE AS $$ SELECT d3.state_relations_before_i9()||ARRAY['d4.recovery_proofs','d4.recovery_settlements']; $$;

CREATE FUNCTION d4.recovery_observe(cid uuid,delivery uuid,receiver uuid,step text,receipt jsonb) RETURNS jsonb LANGUAGE plpgsql SECURITY DEFINER SET search_path=pg_catalog,public,d2,d3,d4 AS $$
DECLARE i jsonb;old d4.recovery_observations;eid uuid;logical text;status text=receipt->>'status';
BEGIN
 PERFORM d3.lock_state();SELECT * INTO old FROM d4.recovery_observations WHERE id=cid;
 IF FOUND THEN IF old.delivery_id IS DISTINCT FROM delivery OR old.receiver_id IS DISTINCT FROM receiver OR old.step IS DISTINCT FROM step OR old.receipt IS DISTINCT FROM receipt THEN RAISE EXCEPTION 'Observation conflict' USING ERRCODE='23514';END IF;RETURN jsonb_build_object('receipt_id',old.receipt_id,'status',status);END IF;
 i=d4.recovery_info(delivery);
 IF cid IS NULL OR status IS NULL OR status NOT IN ('UNKNOWN','ABSENT','APPLIED') OR receipt->'generation' IS DISTINCT FROM i->'generation'
 OR NOT EXISTS(SELECT 1 FROM jsonb_array_elements(i->'recovery_manifest'->'steps') s WHERE s->>'id'=step)
 OR NOT EXISTS(SELECT 1 FROM d4.lab_grants WHERE request->>'delivery'=delivery::text AND response->>'receiver_id'=receiver::text)
 OR (status='APPLIED' AND NOT EXISTS(SELECT 1 FROM jsonb_array_elements(i->'recovery_manifest'->'steps') s WHERE s->>'id'=step AND s->>'effect_hash'=receipt->>'payloadHash'))
 OR (status='ABSENT' AND receipt->'closed' IS DISTINCT FROM 'true'::jsonb)
 THEN RAISE EXCEPTION 'Bound receiver observation required' USING ERRCODE='23514';END IF;
 logical=(i->>'operation')||'/'||(i->>'context_hash')||CASE WHEN i->'is_checkpoint_fixture'='true'::jsonb THEN '/'||step ELSE '' END;
 INSERT INTO d2.effect_receipts(operation_id,generation,effect_key,status,evidence_ref) VALUES((i->>'operation')::uuid,(i->>'generation')::bigint,logical,status,'recovery-observation/'||cid) RETURNING id INTO eid;
 INSERT INTO d4.recovery_observations VALUES(cid,eid,delivery,receiver,step,receipt);RETURN jsonb_build_object('receipt_id',eid,'status',status);
END $$;

CREATE FUNCTION d4.recovery_status(pid uuid,delivery uuid,cid uuid) RETURNS jsonb LANGUAGE plpgsql SECURITY DEFINER SET search_path=pg_catalog,public,d4 AS $$
DECLARE p d4.recovery_proofs;c d4.checkpoint_commands;
BEGIN
 SELECT * INTO p FROM d4.recovery_proofs WHERE id=pid;IF NOT FOUND THEN RETURN 'null'::jsonb;END IF;
 IF p.delivery_id IS DISTINCT FROM delivery THEN RAISE EXCEPTION 'Recovery ownership conflict' USING ERRCODE='23514';END IF;
 SELECT * INTO c FROM d4.checkpoint_commands WHERE id=cid;
 IF FOUND THEN IF c.request->>'action' IS DISTINCT FROM 'RECOVERY_SETTLE' OR c.request->>'proof' IS DISTINCT FROM pid::text THEN RAISE EXCEPTION 'Recovery command conflict' USING ERRCODE='23514';END IF;RETURN c.response;END IF;
 RETURN jsonb_build_object('pending',true,'expected_version',p.proof->'row_version');
END $$;
CREATE FUNCTION d4.recovery_audit() RETURNS jsonb LANGUAGE sql SECURITY DEFINER SET search_path=pg_catalog,public,d4 AS $$ SELECT d4.multi_audit()||jsonb_build_object('recovery_proofs',(SELECT coalesce(jsonb_agg(to_jsonb(t)),'[]') FROM d4.recovery_proofs t),'recovery_settlements',(SELECT coalesce(jsonb_agg(to_jsonb(t)),'[]') FROM d4.recovery_settlements t),'recovery_observations',(SELECT coalesce(jsonb_agg(to_jsonb(t)),'[]') FROM d4.recovery_observations t)); $$;
