-- SPDX-License-Identifier: GPL-3.0-only
-- D4-A13/A14: separate v2 intention and chain; V1-V23 remain immutable.
CREATE TABLE d4.multi_intents(operation_id uuid PRIMARY KEY REFERENCES public.operations(id),manifest jsonb NOT NULL,manifest_hash text NOT NULL);
CREATE TABLE d4.multi_proofs(id uuid PRIMARY KEY,delivery_id uuid NOT NULL REFERENCES d4.deliveries(id),request_id uuid REFERENCES d4.checkpoint_requests(id),proof jsonb NOT NULL,evaluation jsonb NOT NULL);
CREATE TABLE d4.multi_checkpoints(
 id uuid PRIMARY KEY,operation_id uuid NOT NULL REFERENCES public.operations(id),parent_id uuid REFERENCES d4.multi_checkpoints(id),
 proof_id uuid NOT NULL UNIQUE REFERENCES d4.multi_proofs(id),source_attempt uuid NOT NULL UNIQUE REFERENCES public.execution_attempts(id),source_generation bigint NOT NULL,
 reservation_id uuid NOT NULL REFERENCES d2.reservations(id),committed_version bigint NOT NULL,
 UNIQUE(operation_id,source_generation),UNIQUE NULLS NOT DISTINCT(operation_id,parent_id));
CREATE TABLE d4.multi_authorizations(id uuid PRIMARY KEY,checkpoint_id uuid NOT NULL UNIQUE REFERENCES d4.multi_checkpoints(id),authorized_version bigint NOT NULL,reason text NOT NULL);
CREATE TABLE d4.multi_links(checkpoint_id uuid PRIMARY KEY REFERENCES d4.multi_checkpoints(id),authorization_id uuid NOT NULL UNIQUE REFERENCES d4.multi_authorizations(id),attempt_id uuid NOT NULL UNIQUE REFERENCES public.execution_attempts(id),generation bigint NOT NULL);
CREATE VIEW d4.multi_heads AS SELECT DISTINCT ON(operation_id) * FROM d4.multi_checkpoints ORDER BY operation_id,source_generation DESC;
DO $$ DECLARE rel text;BEGIN
 FOREACH rel IN ARRAY ARRAY['multi_intents','multi_proofs','multi_checkpoints','multi_authorizations','multi_links'] LOOP
 EXECUTE format('CREATE TRIGGER immutable_fact BEFORE UPDATE OR DELETE OR TRUNCATE ON d4.%I FOR EACH STATEMENT EXECUTE FUNCTION public.d2_reject_fact_mutation()',rel);
 END LOOP;
END $$;
CREATE FUNCTION d4.multi_freeze() RETURNS trigger LANGUAGE plpgsql SET search_path=pg_catalog,public,d2,d3,d4 AS $$
DECLARE m jsonb=NEW.manifest;s jsonb;a record;cost numeric;
BEGIN
 IF EXISTS(SELECT 1 FROM public.execution_attempts WHERE operation_id=NEW.operation_id) OR EXISTS(SELECT 1 FROM d4.step_intents WHERE operation_id=NEW.operation_id)
 OR NEW.manifest_hash IS DISTINCT FROM encode(public.digest(m::text,'sha256'),'hex') OR m->>'schema' IS DISTINCT FROM 'd4.steps.v2'
 OR jsonb_typeof(m->'steps') IS DISTINCT FROM 'array' OR jsonb_typeof(m->'accounts') IS DISTINCT FROM 'object'
 OR jsonb_array_length(m->'steps') NOT BETWEEN 1 AND 32 OR (SELECT count(*) FROM jsonb_object_keys(m->'accounts')) NOT BETWEEN 1 AND 8
 OR m->>'pool' NOT IN ('PLANNED','INCIDENT') OR m->>'pool' IS NULL
 OR NOT EXISTS(SELECT 1 FROM public.operations op JOIN d4.lab_intents li ON li.operation_id=op.id WHERE op.id=NEW.operation_id
 AND li.context_bytes IS NOT NULL AND convert_from(li.context_bytes,'UTF8')::jsonb->'step_manifest'=m AND op.context_pack_sha256=encode(public.digest(li.context_bytes,'sha256'),'hex'))
 THEN RAISE EXCEPTION 'Context-bound pre-CLAIM v2 intention required' USING ERRCODE='23514';END IF;
 IF (SELECT count(DISTINCT value->>'id') FROM jsonb_array_elements(m->'steps'))<>jsonb_array_length(m->'steps') THEN RAISE EXCEPTION 'Unique ordered steps required' USING ERRCODE='23514';END IF;
 FOR s IN SELECT value FROM jsonb_array_elements(m->'steps') LOOP
  IF s->>'id' !~ '^[A-Za-z0-9_-]{1,64}$' OR s->>'id' IS NULL OR s->>'effect_hash' !~ '^[a-f0-9]{64}$' OR s->>'effect_hash' IS NULL
  OR jsonb_typeof(s->'cost') IS DISTINCT FROM 'object' OR (SELECT array_agg(key ORDER BY key) FROM jsonb_each(s->'cost')) IS DISTINCT FROM (SELECT array_agg(key ORDER BY key) FROM jsonb_each(m->'accounts'))
  THEN RAISE EXCEPTION 'Complete exact cost vectors required' USING ERRCODE='23514';END IF;
  FOR a IN SELECT * FROM jsonb_each(s->'cost') LOOP
   IF jsonb_typeof(a.value)<>'number' OR (a.value::text)::numeric<0 OR (a.value::text)::numeric>=1e14 OR scale((a.value::text)::numeric)>4 THEN RAISE EXCEPTION 'Bounded decimal units required' USING ERRCODE='23514';END IF;
  END LOOP;
 END LOOP;
 FOR a IN SELECT * FROM jsonb_each(m->'accounts') LOOP
  SELECT sum((value->'cost'->>a.key)::numeric) INTO cost FROM jsonb_array_elements(m->'steps');
  IF jsonb_typeof(a.value->'original') IS DISTINCT FROM 'number' OR (a.value->>'original')::numeric<=0 OR (a.value->>'original')::numeric>=1e14 OR scale((a.value->>'original')::numeric)>4 OR cost>(a.value->>'original')::numeric
  OR NOT EXISTS(SELECT 1 FROM d2.accounts ac WHERE ac.id=a.key::uuid AND ac.resource_id=(m->>'resource')::uuid
   AND ac.dimension=a.value->>'dimension' AND ac.unit=a.value->>'unit' AND ac.window_start=(a.value->>'start')::timestamptz AND ac.window_end=(a.value->>'end')::timestamptz)
  THEN RAISE EXCEPTION 'Exact frozen physical account binding required' USING ERRCODE='23514';END IF;
 END LOOP;
 RETURN NEW;
END $$;
CREATE TRIGGER freeze_intent BEFORE INSERT ON d4.multi_intents FOR EACH ROW EXECUTE FUNCTION d4.multi_freeze();

-- Every previously ingested receipt must have exactly the provenance retained in
-- an immutable v2 checkpoint. Current final/checkpoint receipts are checked separately.
CREATE FUNCTION d4.multi_effects_safe(oid uuid) RETURNS boolean LANGUAGE sql STABLE SECURITY DEFINER SET search_path=pg_catalog,public,d2,d3,d4 AS $$
 SELECT NOT EXISTS(SELECT 1 FROM d2.effect_receipts er JOIN public.operations op ON op.id=er.operation_id WHERE er.operation_id=oid AND
 (er.status='UNKNOWN' OR NOT EXISTS(SELECT 1 FROM d4.multi_checkpoints cp JOIN d4.multi_proofs pr ON pr.id=cp.proof_id
 CROSS JOIN LATERAL jsonb_each(pr.proof->'receipts') rr WHERE cp.operation_id=oid AND cp.source_generation=er.generation
 AND er.effect_key=oid||'/'||op.context_pack_sha256||'/'||rr.key AND er.status=rr.value->>'status')))
 AND NOT EXISTS(SELECT 1 FROM d2.effect_receipts WHERE operation_id=oid GROUP BY generation,effect_key HAVING count(DISTINCT status)>1);
$$;
CREATE FUNCTION d4.multi_inspect(delivery uuid) RETURNS jsonb LANGUAGE plpgsql SECURITY DEFINER SET search_path=pg_catalog,public,d2,d3,d4 AS $$
DECLARE info jsonb=d4.i5_inspect(delivery);m d4.multi_intents;cp d4.multi_checkpoints;ev jsonb='{}';allowed jsonb;step jsonb;
BEGIN
 SELECT * INTO m FROM d4.multi_intents WHERE operation_id=(info->>'operation')::uuid;IF NOT FOUND THEN RETURN info;END IF;
 SELECT * INTO cp FROM d4.multi_heads WHERE operation_id=m.operation_id;
 IF cp.id IS NOT NULL THEN SELECT evaluation INTO ev FROM d4.multi_proofs WHERE id=cp.proof_id;END IF;
 SELECT jsonb_agg(s ORDER BY n) INTO allowed FROM jsonb_array_elements(m.manifest->'steps') WITH ORDINALITY x(s,n) WHERE NOT coalesce(ev->'applied','{}') ? (s->>'id');
 step=allowed->0;
 RETURN info||jsonb_build_object('multi_checkpoint',true,'is_checkpoint_fixture',true,'manifest',m.manifest,'manifest_hash',m.manifest_hash,
 'parent_checkpoint',cp.id,'parent_evaluation',ev,'allowed_steps',(SELECT jsonb_agg(s->>'id' ORDER BY n) FROM jsonb_array_elements(allowed) WITH ORDINALITY x(s,n)),
 'attempt_count',(SELECT count(*) FROM public.execution_attempts WHERE operation_id=m.operation_id),'max_attempts',(SELECT coalesce((policy_snapshot->>'max_attempts')::int,3) FROM public.operations WHERE id=m.operation_id),'needs_checkpoint',jsonb_array_length(allowed)>1,'current_step',step->>'id','incremental_vector',step->'cost',
 'history',(SELECT coalesce(jsonb_agg(jsonb_build_object('checkpoint',c.id,'parent',c.parent_id,'evaluation',p.evaluation) ORDER BY c.source_generation),'[]') FROM d4.multi_checkpoints c JOIN d4.multi_proofs p ON p.id=c.proof_id WHERE c.operation_id=m.operation_id));
END $$;
CREATE FUNCTION d4.multi_request(cid uuid,delivery uuid,expected_version bigint) RETURNS jsonb LANGUAGE plpgsql SECURITY DEFINER SET search_path=pg_catalog,public,d2,d3,d4 AS $$
DECLARE req jsonb=jsonb_build_object('action','MULTI_REQUEST','delivery',delivery,'version',expected_version);prior jsonb;info jsonb;result jsonb;
BEGIN
 PERFORM d3.lock_state();prior=d4.checkpoint_previous(cid,req);IF prior IS NOT NULL THEN RETURN prior;END IF;info=d4.multi_inspect(delivery);
 IF info->'multi_checkpoint' IS DISTINCT FROM 'true'::jsonb OR info->>'state'<>'RUNNING' OR (info->>'lease_expired')::boolean IS DISTINCT FROM false OR (info->>'row_version')::bigint IS DISTINCT FROM expected_version
 OR NOT EXISTS(SELECT 1 FROM public.operations WHERE id=(info->>'operation')::uuid AND policy_snapshot->'interruptible'='true')
 THEN RAISE EXCEPTION 'Live interruptible v2 identity/version required' USING ERRCODE='23514';END IF;
 INSERT INTO d4.checkpoint_requests VALUES(cid,delivery,(info->>'operation')::uuid,(info->>'attempt')::uuid,(info->>'generation')::bigint,expected_version);
 result=jsonb_build_object('request_id',cid);INSERT INTO d4.checkpoint_commands VALUES(cid,req,result);RETURN result;
END $$;
-- Recomputed both at verifier ingress and under the commit mutex. Never trusts a
-- worker-provided scalar/vector or a calculator result for ledger mutation.
CREATE FUNCTION d4.multi_evaluate(delivery uuid,proof jsonb,terminal boolean) RETURNS jsonb LANGUAGE plpgsql SECURITY DEFINER SET search_path=pg_catalog,public,d2,d3,d4 AS $$
DECLARE info jsonb=d4.multi_inspect(delivery);op public.operations;m jsonb=info->'manifest';parent jsonb=coalesce(info->'parent_evaluation','{}');applied jsonb=coalesce(parent->'applied','{}');
 cumulative jsonb='{}';consumes jsonb='{}';releases jsonb='{}';s jsonb;rr jsonb;row record;res d2.reservations;cost numeric;prev numeric;delta numeric;remaining boolean=false;progress integer=0;attempts integer;
BEGIN
 SELECT * INTO STRICT op FROM public.operations WHERE id=(info->>'operation')::uuid;SELECT * INTO STRICT res FROM d2.reservations WHERE operation_id=op.id;
 SELECT count(*) INTO attempts FROM public.execution_attempts WHERE operation_id=op.id;
 IF info->'multi_checkpoint' IS DISTINCT FROM 'true'::jsonb OR op.state IS DISTINCT FROM (CASE WHEN terminal THEN 'VERIFYING' ELSE 'RUNNING' END)
 OR (info->>'lease_expired')::boolean IS DISTINCT FROM false OR proof->>'schema' IS DISTINCT FROM 'd4.checkpoint.proof.v2'
 OR proof->'parent_checkpoint' IS DISTINCT FROM info->'parent_checkpoint'
 OR proof->>'manifest_hash' IS DISTINCT FROM info->>'manifest_hash' OR proof->>'context_hash' IS DISTINCT FROM info->>'context_hash' OR proof->>'policy_hash' IS DISTINCT FROM info->>'policy_hash'
 OR proof->>'operation' IS DISTINCT FROM info->>'operation' OR proof->>'attempt' IS DISTINCT FROM info->>'attempt' OR proof->>'worker' IS DISTINCT FROM info->>'worker' OR proof->>'resource' IS DISTINCT FROM info->>'resource' OR proof->>'generation' IS DISTINCT FROM info->>'generation'
 OR op.context_pack_sha256 IS DISTINCT FROM info->>'context_hash' OR encode(public.digest(op.policy_snapshot::text,'sha256'),'hex') IS DISTINCT FROM info->>'policy_hash'
 OR proof->'process_stopped' IS DISTINCT FROM 'true'::jsonb OR proof->'artifact_valid' IS DISTINCT FROM 'true'::jsonb OR proof->'receiver_closed' IS DISTINCT FROM 'true'::jsonb OR coalesce((proof->>'close_sequence')::bigint,0)<=0
 OR coalesce(proof->>'host_observation_hash','') !~ '^[a-f0-9]{64}$' OR coalesce(proof->>'stdout_hash','') !~ '^[a-f0-9]{64}$' OR coalesce(proof->>'stderr_hash','') !~ '^[a-f0-9]{64}$'
 OR NOT d4.multi_effects_safe(op.id) OR attempts>coalesce((op.policy_snapshot->>'max_attempts')::int,3) OR (NOT terminal AND attempts>=coalesce((op.policy_snapshot->>'max_attempts')::int,3))
 OR res.resource_id IS DISTINCT FROM (m->>'resource')::uuid OR res.pool IS DISTINCT FROM m->>'pool'
 OR (info->'parent_checkpoint'='null' AND attempts<>1)
 OR (info->'parent_checkpoint'<>'null' AND NOT EXISTS(SELECT 1 FROM d4.multi_links l JOIN d4.multi_checkpoints cp ON cp.id=l.checkpoint_id WHERE cp.id=(info->>'parent_checkpoint')::uuid AND l.attempt_id=(info->>'attempt')::uuid AND l.generation=op.lease_generation AND cp.source_generation+1=op.lease_generation))
 OR jsonb_typeof(proof->'receipts') IS DISTINCT FROM 'object'
 OR (SELECT array_agg(key ORDER BY key) FROM jsonb_each(proof->'receipts')) IS DISTINCT FROM (SELECT array_agg(value#>>'{}' ORDER BY value#>>'{}') FROM jsonb_array_elements(info->'allowed_steps'))
 THEN RAISE EXCEPTION 'Exact live independently sealed v2 proof required' USING ERRCODE='23514';END IF;
 FOR s IN SELECT value FROM jsonb_array_elements(m->'steps') LOOP
  IF applied ? (s->>'id') THEN CONTINUE;END IF;
  rr=proof->'receipts'->(s->>'id');
  IF (rr->>'generation')::bigint IS DISTINCT FROM op.lease_generation OR rr->>'status' NOT IN ('APPLIED','ABSENT') OR rr->>'status' IS NULL
   OR (rr->>'status'='ABSENT' AND rr->'closed' IS DISTINCT FROM 'true'::jsonb) THEN RAISE EXCEPTION 'No UNKNOWN or unbound absence' USING ERRCODE='23514';END IF;
  IF rr->>'status'='ABSENT' THEN remaining=true;
  ELSE
   IF remaining OR rr->>'payloadHash' IS DISTINCT FROM s->>'effect_hash' THEN RAISE EXCEPTION 'Ordered exact effect required' USING ERRCODE='23514';END IF;
   progress=progress+1;applied=applied||jsonb_build_object(s->>'id',jsonb_build_object('attempt',info->'attempt','generation',op.lease_generation,'payloadHash',rr->>'payloadHash'));
  END IF;
 END LOOP;
 IF progress=0 OR terminal IS DISTINCT FROM (NOT remaining) THEN RAISE EXCEPTION 'New progress and exact finality required' USING ERRCODE='23514';END IF;
 IF (SELECT array_agg(account_id::text ORDER BY account_id::text) FROM d2.operation_accounts WHERE operation_id=op.id) IS DISTINCT FROM (SELECT array_agg(key ORDER BY key) FROM jsonb_each(m->'accounts'))
 OR (SELECT array_agg(account_id::text ORDER BY account_id::text) FROM d2.reservation_balances WHERE reservation_id=res.id) IS DISTINCT FROM (SELECT array_agg(key ORDER BY key) FROM jsonb_each(m->'accounts'))
 THEN RAISE EXCEPTION 'All frozen accounts required' USING ERRCODE='23514';END IF;
 FOR row IN SELECT b.*,oa.units,ac.window_start,ac.window_end,ac.dimension,ac.unit FROM d2.reservation_balances b JOIN d2.operation_accounts oa ON oa.operation_id=op.id AND oa.account_id=b.account_id JOIN d2.accounts ac ON ac.id=b.account_id WHERE b.reservation_id=res.id ORDER BY b.account_id LOOP
  SELECT coalesce(sum((value->'cost'->>row.account_id::text)::numeric),0) INTO cost FROM jsonb_array_elements(m->'steps') WHERE applied ? (value->>'id');
  prev=coalesce((parent->'cumulative'->>row.account_id::text)::numeric,0);delta=cost-prev;
  IF row.units IS DISTINCT FROM (m->'accounts'->row.account_id::text->>'original')::numeric OR row.window_start IS DISTINCT FROM (m->'accounts'->row.account_id::text->>'start')::timestamptz OR row.window_end IS DISTINCT FROM (m->'accounts'->row.account_id::text->>'end')::timestamptz
   OR row.dimension IS DISTINCT FROM m->'accounts'->row.account_id::text->>'dimension' OR row.unit IS DISTINCT FROM m->'accounts'->row.account_id::text->>'unit'
   OR clock_timestamp()<row.window_start OR clock_timestamp()>=row.window_end OR delta<0 OR delta>row.units
   OR (NOT terminal AND (row.consumed<>prev OR row.outstanding<>row.units)) OR (terminal AND (row.consumed<>cost OR row.outstanding<>0))
  THEN RAISE EXCEPTION 'Atomic complete account settlement required' USING ERRCODE='23514';END IF;
  cumulative=cumulative||jsonb_build_object(row.account_id::text,cost);consumes=consumes||jsonb_build_object(row.account_id::text,delta);releases=releases||jsonb_build_object(row.account_id::text,row.units-delta);
 END LOOP;
 RETURN jsonb_build_object('applied',applied,'cumulative',cumulative,'consume',consumes,'release',releases,'identity',jsonb_build_object('operation',info->'operation','attempt',info->'attempt','worker',info->'worker','resource',info->'resource','generation',info->'generation'),'attempt_count',attempts,'terminal',terminal);
END $$;
CREATE FUNCTION d4.multi_record_proof(cid uuid,delivery uuid,rid uuid,proof jsonb) RETURNS jsonb LANGUAGE plpgsql SECURITY DEFINER SET search_path=pg_catalog,public,d2,d3,d4 AS $$
DECLARE old d4.multi_proofs;ev jsonb;
BEGIN
 PERFORM d3.lock_state();SELECT * INTO old FROM d4.multi_proofs WHERE id=cid;
 IF FOUND THEN IF old.proof IS DISTINCT FROM proof OR old.delivery_id IS DISTINCT FROM delivery OR old.request_id IS DISTINCT FROM rid THEN RAISE EXCEPTION 'Proof conflict' USING ERRCODE='23514';END IF;RETURN old.evaluation;END IF;
 IF cid IS NULL OR (rid IS NOT NULL AND NOT EXISTS(SELECT 1 FROM d4.checkpoint_requests WHERE id=rid AND delivery_id=delivery)) THEN RAISE EXCEPTION 'Bound request required' USING ERRCODE='23514';END IF;
 ev=d4.multi_evaluate(delivery,proof,rid IS NULL);INSERT INTO d4.multi_proofs VALUES(cid,delivery,rid,proof,ev);RETURN ev;
END $$;
CREATE FUNCTION d4.multi_commit(cid uuid,rid uuid,pid uuid,expected_version bigint) RETURNS jsonb LANGUAGE plpgsql SECURITY DEFINER SET search_path=pg_catalog,public,d2,d3,d4 AS $$
DECLARE req jsonb=jsonb_build_object('action','MULTI_COMMIT','request',rid,'proof',pid,'version',expected_version);prior jsonb;pr d4.multi_proofs;r d4.checkpoint_requests;op public.operations;ev jsonb;res d2.reservations;entries jsonb;result jsonb;parent uuid;
BEGIN
 PERFORM d3.lock_state();prior=d4.checkpoint_previous(cid,req);IF prior IS NOT NULL THEN RETURN prior;END IF;
 SELECT * INTO STRICT pr FROM d4.multi_proofs WHERE id=pid AND request_id=rid;SELECT * INTO STRICT r FROM d4.checkpoint_requests WHERE id=rid AND delivery_id=pr.delivery_id;SELECT * INTO STRICT op FROM public.operations WHERE id=r.operation_id;
 IF op.row_version IS DISTINCT FROM expected_version OR r.expected_version IS DISTINCT FROM expected_version OR r.attempt_id IS DISTINCT FROM (pr.proof->>'attempt')::uuid OR r.generation<>op.lease_generation
 THEN RAISE EXCEPTION 'Exact checkpoint version required' USING ERRCODE='23514';END IF;
 ev=d4.multi_evaluate(pr.delivery_id,pr.proof,false);IF ev IS DISTINCT FROM pr.evaluation THEN RAISE EXCEPTION 'Checkpoint basis changed' USING ERRCODE='40001';END IF;
 SELECT * INTO STRICT res FROM d2.reservations WHERE operation_id=op.id;parent=(pr.proof->>'parent_checkpoint')::uuid;
 SELECT jsonb_agg(jsonb_build_object('account_id',key,'settled',value,'consumed',value) ORDER BY key) INTO entries FROM jsonb_each(ev->'consume');
 PERFORM d2.capacity(public.gen_random_uuid(),jsonb_build_object('action','CONSUME','reservation_id',res.id,'entries',entries,'reason','Verified v2 incremental consumption'));
 SELECT jsonb_agg(jsonb_build_object('account_id',key,'settled',value) ORDER BY key) INTO entries FROM jsonb_each(ev->'release');
 PERFORM d2.capacity(public.gen_random_uuid(),jsonb_build_object('action','RELEASE','reservation_id',res.id,'entries',entries,'reason','Sealed v2 remainder'));
 INSERT INTO d2.effect_receipts(operation_id,generation,effect_key,status,evidence_ref) SELECT op.id,op.lease_generation,op.id||'/'||op.context_pack_sha256||'/'||key,value->>'status','multi-proof/'||pid FROM jsonb_each(pr.proof->'receipts');
 UPDATE public.execution_attempts SET state='CANCELLED',finished_at=clock_timestamp() WHERE id=r.attempt_id;DELETE FROM public.operation_leases WHERE operation_id=op.id;
 UPDATE public.operations SET state='CANCELLED',row_version=row_version+1 WHERE id=op.id;
 PERFORM d2.record_transition(cid,'OPERATION',op.id,'RUNNING','CANCELLED',op.row_version+1,'CONTROL_PLANE','Sealed linear multicount checkpoint');
 INSERT INTO d4.multi_checkpoints VALUES(cid,op.id,parent,pid,r.attempt_id,r.generation,res.id,op.row_version+1);
 result=jsonb_build_object('checkpoint_id',cid,'state','CANCELLED','row_version',op.row_version+1);INSERT INTO d4.checkpoint_commands VALUES(cid,req,result);
 INSERT INTO public.outbox_events(aggregate_type,aggregate_id,event_type,payload) VALUES('OPERATION',op.id,'D4_MULTI_CHECKPOINT_COMMITTED',result);RETURN result;
END $$;
CREATE FUNCTION d4.multi_head_settled(oid uuid) RETURNS boolean LANGUAGE sql STABLE SECURITY DEFINER SET search_path=pg_catalog,public,d2,d3,d4 AS $$
 SELECT EXISTS(SELECT 1 FROM d4.multi_heads cp JOIN d4.multi_proofs pr ON pr.id=cp.proof_id JOIN d4.multi_intents i ON i.operation_id=cp.operation_id JOIN d2.reservations r ON r.id=cp.reservation_id AND r.operation_id=cp.operation_id
 WHERE cp.operation_id=oid AND i.manifest_hash=pr.proof->>'manifest_hash' AND r.resource_id=(i.manifest->>'resource')::uuid AND r.pool=i.manifest->>'pool'
 AND (SELECT array_agg(account_id::text ORDER BY account_id::text) FROM d2.operation_accounts WHERE operation_id=oid)=(SELECT array_agg(key ORDER BY key) FROM jsonb_each(i.manifest->'accounts'))
 AND (SELECT array_agg(account_id::text ORDER BY account_id::text) FROM d2.reservation_balances WHERE reservation_id=r.id)=(SELECT array_agg(key ORDER BY key) FROM jsonb_each(i.manifest->'accounts'))
 AND NOT EXISTS(SELECT 1 FROM d2.reservation_balances b JOIN d2.operation_accounts oa ON oa.operation_id=oid AND oa.account_id=b.account_id JOIN d2.accounts a ON a.id=b.account_id WHERE b.reservation_id=r.id AND
 (b.outstanding<>0 OR b.consumed IS DISTINCT FROM (pr.evaluation->'cumulative'->>b.account_id::text)::numeric OR oa.units IS DISTINCT FROM (i.manifest->'accounts'->b.account_id::text->>'original')::numeric
 OR a.window_start IS DISTINCT FROM (i.manifest->'accounts'->b.account_id::text->>'start')::timestamptz OR a.window_end IS DISTINCT FROM (i.manifest->'accounts'->b.account_id::text->>'end')::timestamptz
 OR a.dimension IS DISTINCT FROM i.manifest->'accounts'->b.account_id::text->>'dimension' OR a.unit IS DISTINCT FROM i.manifest->'accounts'->b.account_id::text->>'unit')));
$$;
CREATE FUNCTION d4.multi_safe(oid uuid,gen bigint) RETURNS boolean LANGUAGE sql STABLE SECURITY DEFINER SET search_path=pg_catalog,public,d2,d3,d4 AS $$
 SELECT EXISTS(SELECT 1 FROM d4.multi_heads cp JOIN d4.multi_authorizations au ON au.checkpoint_id=cp.id JOIN public.operations op ON op.id=cp.operation_id JOIN d4.multi_intents i ON i.operation_id=op.id JOIN d4.multi_proofs pr ON pr.id=cp.proof_id
 WHERE op.id=oid AND cp.source_generation=gen AND op.lease_generation=gen AND op.row_version=au.authorized_version AND op.state='READY'
 AND op.context_pack_sha256=pr.proof->>'context_hash' AND encode(public.digest(op.policy_snapshot::text,'sha256'),'hex')=pr.proof->>'policy_hash' AND i.manifest_hash=pr.proof->>'manifest_hash'
 AND NOT EXISTS(SELECT 1 FROM d4.multi_links WHERE checkpoint_id=cp.id) AND d4.multi_effects_safe(oid) AND d4.multi_head_settled(oid));
$$;
CREATE FUNCTION d4.multi_authorize(cid uuid,checkpoint uuid,expected_version bigint,reason text) RETURNS jsonb LANGUAGE plpgsql SECURITY DEFINER SET search_path=pg_catalog,public,d2,d3,d4 AS $$
DECLARE req jsonb=jsonb_build_object('action','MULTI_AUTHORIZE','checkpoint',checkpoint,'version',expected_version,'reason',reason);prior jsonb;cp d4.multi_checkpoints;op public.operations;pr d4.multi_proofs;result jsonb;
BEGIN
 PERFORM d3.lock_state();prior=d4.checkpoint_previous(cid,req);IF prior IS NOT NULL THEN RETURN prior;END IF;
 SELECT * INTO STRICT cp FROM d4.multi_heads WHERE id=checkpoint;SELECT * INTO STRICT op FROM public.operations WHERE id=cp.operation_id;SELECT * INTO STRICT pr FROM d4.multi_proofs WHERE id=cp.proof_id;
 IF op.state<>'CANCELLED' OR op.row_version IS DISTINCT FROM expected_version OR cp.committed_version IS DISTINCT FROM expected_version OR cp.source_generation<>op.lease_generation
 OR reason IS NULL OR length(btrim(reason)) NOT BETWEEN 1 AND 512 OR EXISTS(SELECT 1 FROM d4.multi_authorizations WHERE checkpoint_id=checkpoint)
 OR NOT d4.multi_effects_safe(op.id) OR NOT d4.multi_head_settled(op.id) OR pr.proof->>'context_hash' IS DISTINCT FROM op.context_pack_sha256 OR pr.proof->>'policy_hash' IS DISTINCT FROM encode(public.digest(op.policy_snapshot::text,'sha256'),'hex')
 OR coalesce((op.policy_snapshot->>'max_attempts')::int,3) NOT BETWEEN 1 AND 20 OR (SELECT count(*) FROM public.execution_attempts WHERE operation_id=op.id)>=coalesce((op.policy_snapshot->>'max_attempts')::int,3)
 THEN RAISE EXCEPTION 'Unused current v2 checkpoint and attempt budget required' USING ERRCODE='23514';END IF;
 UPDATE public.operations SET state='READY',row_version=row_version+1 WHERE id=op.id;PERFORM d2.record_transition(cid,'OPERATION',op.id,'CANCELLED','READY',op.row_version+1,'CONTROL_PLANE','Explicit v2 continuation');
 INSERT INTO d4.multi_authorizations VALUES(cid,checkpoint,op.row_version+1,reason);result=jsonb_build_object('state','READY','row_version',op.row_version+1);
 INSERT INTO d4.checkpoint_commands VALUES(cid,req,result);INSERT INTO public.outbox_events(aggregate_type,aggregate_id,event_type,payload) VALUES('OPERATION',op.id,'D4_MULTI_CONTINUATION_AUTHORIZED',result);RETURN result;
END $$;
ALTER FUNCTION d4.continuation_safe(uuid,bigint) RENAME TO continuation_safe_before_i8;
CREATE FUNCTION d4.continuation_safe(oid uuid,gen bigint) RETURNS boolean LANGUAGE sql STABLE SECURITY DEFINER SET search_path=pg_catalog,public,d2,d3,d4 AS $$ SELECT d4.continuation_safe_before_i8(oid,gen) OR d4.multi_safe(oid,gen); $$;
CREATE OR REPLACE VIEW d4.continuation_admissions AS SELECT cp.operation_id,cp.source_generation generation,cp.id checkpoint_id,au.id authorization_id,cp.manifest_hash,'SEALED_CHECKPOINT'::text admission_kind,d4.continuation_safe(cp.operation_id,cp.source_generation) eligible
 FROM d4.checkpoints cp JOIN d4.continuation_authorizations au ON au.checkpoint_id=cp.id
 UNION ALL SELECT cp.operation_id,cp.source_generation,cp.id,au.id,i.manifest_hash,'SEALED_CHECKPOINT',d4.multi_safe(cp.operation_id,cp.source_generation)
 FROM d4.multi_heads cp JOIN d4.multi_authorizations au ON au.checkpoint_id=cp.id JOIN d4.multi_intents i ON i.operation_id=cp.operation_id;
ALTER FUNCTION d3.state_relations() RENAME TO state_relations_before_d4_i8;
CREATE FUNCTION d3.state_relations() RETURNS text[] LANGUAGE sql IMMUTABLE AS $$ SELECT d3.state_relations_before_d4_i8()||ARRAY['d4.multi_intents','d4.multi_proofs','d4.multi_checkpoints','d4.multi_authorizations','d4.multi_links','d4.multi_heads']; $$;
ALTER FUNCTION d4.dispatch_continuation(uuid,jsonb) RENAME TO dispatch_continuation_before_i8;
CREATE FUNCTION d4.dispatch_continuation(cid uuid,req jsonb) RETURNS jsonb LANGUAGE plpgsql SECURITY DEFINER SET search_path=pg_catalog,public,d2,d3,d4 AS $$
DECLARE prior jsonb;cp d4.multi_checkpoints;au uuid;body jsonb;captured jsonb;rel text;result jsonb;mi d4.multi_intents;
BEGIN
 PERFORM d3.lock_state();prior=d3.previous_command(cid,req);IF prior IS NOT NULL THEN RETURN prior;END IF;
 SELECT * INTO mi FROM d4.multi_intents WHERE operation_id=(req->>'operation_id')::uuid;
 IF mi.operation_id IS NOT NULL AND (
  (mi.manifest->>'resource')::uuid IS DISTINCT FROM (req->>'resource_id')::uuid
  OR NOT EXISTS(SELECT 1 FROM d3.estimate_heads eh JOIN d3.estimates e ON e.id=eh.estimate_id WHERE eh.operation_id=mi.operation_id AND eh.resource_id=(req->>'resource_id')::uuid AND e.units=(SELECT jsonb_object_agg(key,value->'original') FROM jsonb_each(mi.manifest->'accounts')))
  OR NOT EXISTS(SELECT 1 FROM d3.plan_manifests pm CROSS JOIN LATERAL jsonb_array_elements(pm.result->'decisions') d WHERE pm.planning_run_id=(req->>'plan_id')::uuid AND d->>'operationId'=mi.operation_id::text AND d->>'pool'=mi.manifest->>'pool')
  OR NOT EXISTS(SELECT 1 FROM public.operations op JOIN d4.lab_intents li ON li.operation_id=op.id WHERE op.id=mi.operation_id AND op.context_pack_sha256=encode(public.digest(li.context_bytes,'sha256'),'hex') AND convert_from(li.context_bytes,'UTF8')::jsonb->'step_manifest'=mi.manifest))
 THEN RAISE EXCEPTION 'Frozen v2 intent/mapping must match initial and retry CLAIM' USING ERRCODE='23514';END IF;
 SELECT h.* INTO cp FROM d4.multi_heads h WHERE h.operation_id=(req->>'operation_id')::uuid AND d4.multi_safe(h.operation_id,h.source_generation);
 IF mi.operation_id IS NOT NULL THEN
  body=d3.state_body();SELECT c.body INTO STRICT captured FROM d3.plan_manifests m JOIN d3.captures c ON c.id=m.capture_id WHERE m.planning_run_id=(req->>'plan_id')::uuid;
  FOREACH rel IN ARRAY ARRAY['d4.multi_intents','d4.multi_proofs','d4.multi_checkpoints','d4.multi_authorizations','d4.multi_links','d4.multi_heads'] LOOP
   IF body->rel IS DISTINCT FROM captured->rel THEN RAISE EXCEPTION 'v2 admission readset changed' USING ERRCODE='40001';END IF;
  END LOOP;
 END IF;
 IF cp.id IS NOT NULL THEN SELECT id INTO STRICT au FROM d4.multi_authorizations WHERE checkpoint_id=cp.id;END IF;
 result=d4.dispatch_continuation_before_i8(cid,req);
 IF cp.id IS NOT NULL THEN INSERT INTO d4.multi_links VALUES(cp.id,au,(result->>'attempt_id')::uuid,(result->>'generation')::bigint);END IF;
 RETURN result;
END $$;
CREATE FUNCTION d4.multi_accept(cid uuid,delivery uuid,proof jsonb) RETURNS jsonb LANGUAGE plpgsql SECURITY DEFINER SET search_path=pg_catalog,public,d2,d3,d4 AS $$
DECLARE req jsonb=jsonb_build_object('action','ACCEPT_CONTINUATION','delivery',delivery,'proof',proof);prior jsonb;ev jsonb;info jsonb;artifact uuid;result jsonb;
BEGIN
 PERFORM d3.lock_state();prior=d4.checkpoint_previous(cid,req);IF prior IS NOT NULL THEN RETURN prior;END IF;
 ev=d4.multi_evaluate(delivery,proof,true);info=d4.multi_inspect(delivery);
 INSERT INTO d2.effect_receipts(operation_id,generation,effect_key,status,evidence_ref) SELECT (info->>'operation')::uuid,(info->>'generation')::bigint,(info->>'operation')||'/'||(info->>'context_hash')||'/'||key,value->>'status','multi-final/'||cid FROM jsonb_each(proof->'receipts');
 INSERT INTO public.artifacts(artifact_ref,sha256,media_type,byte_size) VALUES('multi-final/'||cid,encode(public.digest(proof::text,'sha256'),'hex'),'application/json',octet_length(proof::text)) RETURNING id INTO artifact;
 INSERT INTO public.execution_evidence(attempt_id,artifact_id,evidence_type) VALUES((info->>'attempt')::uuid,artifact,'ACCEPTANCE_PASS');
 result=jsonb_build_object('proof_id',cid);INSERT INTO d4.checkpoint_commands VALUES(cid,req,result);RETURN result;
END $$;
CREATE FUNCTION d4.multi_finalize(cid uuid,delivery uuid) RETURNS jsonb LANGUAGE plpgsql SECURITY DEFINER SET search_path=pg_catalog,public,d2,d3,d4 AS $$
DECLARE req jsonb=jsonb_build_object('action','MULTI_FINALIZE','delivery',delivery);prior jsonb;info jsonb;result jsonb;
BEGIN
 PERFORM d3.lock_state();prior=d4.checkpoint_previous(cid,req);IF prior IS NOT NULL THEN RETURN prior;END IF;info=d4.multi_inspect(delivery);
 IF NOT EXISTS(SELECT 1 FROM d4.multi_links WHERE attempt_id=(info->>'attempt')::uuid) OR NOT EXISTS(SELECT 1 FROM d4.checkpoint_commands WHERE request->>'action'='ACCEPT_CONTINUATION' AND request->>'delivery'=delivery::text AND request->'proof'->>'schema'='d4.checkpoint.proof.v2')
 THEN RAISE EXCEPTION 'Independent final v2 acceptance required' USING ERRCODE='23514';END IF;
 result=d3.execution(cid,jsonb_build_object('action','VERIFY','operation_id',info->>'operation','attempt_id',info->>'attempt','worker_id',info->>'worker','resource_id',info->>'resource','generation',info->'generation'));INSERT INTO d4.checkpoint_commands VALUES(cid,req,result);RETURN result;
END $$;
CREATE FUNCTION d4.multi_audit() RETURNS jsonb LANGUAGE sql SECURITY DEFINER SET search_path=pg_catalog,public,d2,d3,d4 AS $$ SELECT d4.i5_audit()||jsonb_build_object(
 'multi_checkpoints',(SELECT coalesce(jsonb_agg(to_jsonb(x) ORDER BY source_generation),'[]') FROM d4.multi_checkpoints x),
 'multi_proofs',(SELECT coalesce(jsonb_agg(to_jsonb(x)),'[]') FROM d4.multi_proofs x),
 'multi_links',(SELECT coalesce(jsonb_agg(to_jsonb(x)),'[]') FROM d4.multi_links x),
 'multi_authorizations',(SELECT coalesce(jsonb_agg(to_jsonb(x)),'[]') FROM d4.multi_authorizations x)); $$;
CREATE FUNCTION d4.multi_proof_status(pid uuid,delivery uuid,rid uuid) RETURNS jsonb LANGUAGE plpgsql SECURITY DEFINER SET search_path=pg_catalog,public,d2,d3,d4 AS $$
DECLARE pr d4.multi_proofs;
BEGIN
 SELECT * INTO pr FROM d4.multi_proofs WHERE id=pid;IF NOT FOUND THEN RETURN 'null'::jsonb;END IF;
 IF pr.delivery_id IS DISTINCT FROM delivery OR pr.request_id IS DISTINCT FROM rid THEN RAISE EXCEPTION 'Proof replay ownership mismatch' USING ERRCODE='23514';END IF;
 RETURN jsonb_build_object('expected_version',(SELECT expected_version FROM d4.checkpoint_requests WHERE id=rid));
END $$;
CREATE FUNCTION d4.multi_accept_status(pid uuid,delivery uuid) RETURNS jsonb LANGUAGE plpgsql SECURITY DEFINER SET search_path=pg_catalog,public,d2,d3,d4 AS $$
DECLARE cmd d4.checkpoint_commands;
BEGIN
 SELECT * INTO cmd FROM d4.checkpoint_commands WHERE id=pid;IF NOT FOUND THEN RETURN 'null'::jsonb;END IF;
 IF cmd.request->>'action' IS DISTINCT FROM 'ACCEPT_CONTINUATION' OR cmd.request->>'delivery' IS DISTINCT FROM delivery::text OR cmd.request->'proof'->>'schema' IS DISTINCT FROM 'd4.checkpoint.proof.v2' THEN RAISE EXCEPTION 'Acceptance replay ownership mismatch' USING ERRCODE='23514';END IF;
 RETURN cmd.response;
END $$;
DO $$ DECLARE fn record;BEGIN
 FOR fn IN SELECT p.oid::regprocedure name FROM pg_proc p JOIN pg_namespace n ON n.oid=p.pronamespace WHERE n.nspname='d4' AND (p.proname LIKE 'multi_%' OR p.proname IN ('continuation_safe','dispatch_continuation')) LOOP EXECUTE format('REVOKE ALL ON FUNCTION %s FROM PUBLIC',fn.name);END LOOP;
END $$;
