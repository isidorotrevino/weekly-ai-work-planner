-- SPDX-License-Identifier: GPL-3.0-only
-- D4-A08/A09 approved: sealed CANCELLED->READY, live RUNNING lease only.
CREATE TABLE d4.step_intents (
 operation_id uuid PRIMARY KEY REFERENCES public.operations(id),manifest jsonb NOT NULL,
 manifest_hash text NOT NULL CHECK(manifest_hash~'^[a-f0-9]{64}$'),
 CHECK(jsonb_typeof(manifest)='object')
);
CREATE FUNCTION d4.freeze_step_intent() RETURNS trigger LANGUAGE plpgsql
SET search_path=pg_catalog,public,d2,d3,d4 AS $$
BEGIN
 IF EXISTS(SELECT 1 FROM public.execution_attempts WHERE operation_id=NEW.operation_id)
  OR NEW.manifest_hash IS DISTINCT FROM encode(public.digest(NEW.manifest::text,'sha256'),'hex')
  OR NOT EXISTS(SELECT 1 FROM d4.lab_intents fi JOIN public.operations op ON op.id=fi.operation_id WHERE fi.operation_id=NEW.operation_id
    AND convert_from(fi.context_bytes,'UTF8')::jsonb->'step_manifest'=NEW.manifest AND op.context_pack_sha256=encode(public.digest(fi.context_bytes,'sha256'),'hex'))
 THEN RAISE EXCEPTION 'Step manifest must be context-bound before first CLAIM' USING ERRCODE='23514';END IF;
 RETURN NEW;
END $$;
CREATE TRIGGER freeze_intent BEFORE INSERT ON d4.step_intents FOR EACH ROW EXECUTE FUNCTION d4.freeze_step_intent();
CREATE TABLE d4.checkpoint_commands(id uuid PRIMARY KEY,request jsonb NOT NULL,response jsonb NOT NULL);
CREATE TABLE d4.checkpoint_requests (
 id uuid PRIMARY KEY,delivery_id uuid NOT NULL REFERENCES d4.deliveries(id),operation_id uuid NOT NULL REFERENCES public.operations(id),
 attempt_id uuid NOT NULL REFERENCES public.execution_attempts(id),generation bigint NOT NULL,expected_version bigint NOT NULL
);
CREATE TABLE d4.checkpoint_proofs (
 id uuid PRIMARY KEY,request_id uuid NOT NULL REFERENCES d4.checkpoint_requests(id),proof jsonb NOT NULL
);
CREATE TABLE d4.checkpoints (
 id uuid PRIMARY KEY,request_id uuid NOT NULL UNIQUE REFERENCES d4.checkpoint_requests(id),
 proof_id uuid NOT NULL REFERENCES d4.checkpoint_proofs(id),operation_id uuid NOT NULL UNIQUE REFERENCES public.operations(id),
 source_attempt uuid NOT NULL REFERENCES public.execution_attempts(id),source_generation bigint NOT NULL,
 reservation_id uuid NOT NULL REFERENCES d2.reservations(id),context_hash text NOT NULL,policy_hash text NOT NULL,manifest_hash text NOT NULL,
 committed_version bigint NOT NULL
);
CREATE TABLE d4.continuation_authorizations (
 id uuid PRIMARY KEY,checkpoint_id uuid NOT NULL UNIQUE REFERENCES d4.checkpoints(id),reason text NOT NULL,
 authorized_version bigint NOT NULL
);
CREATE TABLE d4.continuation_links (
 checkpoint_id uuid PRIMARY KEY REFERENCES d4.checkpoints(id),authorization_id uuid NOT NULL UNIQUE REFERENCES d4.continuation_authorizations(id),
 attempt_id uuid NOT NULL UNIQUE REFERENCES public.execution_attempts(id),generation bigint NOT NULL
);
DO $$ DECLARE rel text;BEGIN
 FOREACH rel IN ARRAY ARRAY['step_intents','checkpoint_commands','checkpoint_requests','checkpoint_proofs','checkpoints','continuation_authorizations','continuation_links'] LOOP
  EXECUTE format('CREATE TRIGGER immutable_fact BEFORE UPDATE OR DELETE OR TRUNCATE ON d4.%I FOR EACH STATEMENT EXECUTE FUNCTION public.d2_reject_fact_mutation()',rel);
 END LOOP;
END $$;
INSERT INTO public.state_transition_rules VALUES('OPERATION','CANCELLED','READY','SEALED_CHECKPOINT_CONTINUATION');

CREATE FUNCTION d4.checkpoint_previous(cid uuid,req jsonb) RETURNS jsonb LANGUAGE plpgsql AS $$
DECLARE prior d4.checkpoint_commands;
BEGIN
 IF cid IS NULL OR req IS NULL OR current_setting('transaction_isolation')<>'read committed' THEN RAISE EXCEPTION 'Explicit READ COMMITTED command required' USING ERRCODE='23514';END IF;
 SELECT * INTO prior FROM d4.checkpoint_commands WHERE id=cid;
 IF FOUND THEN IF prior.request IS DISTINCT FROM req THEN RAISE EXCEPTION 'Checkpoint command conflict' USING ERRCODE='23514';END IF;RETURN prior.response;END IF;
 RETURN NULL;
END $$;
CREATE FUNCTION d4.checkpoint_request(cid uuid,delivery uuid,expected_version bigint) RETURNS jsonb LANGUAGE plpgsql SECURITY DEFINER
SET search_path=pg_catalog,public,d2,d3,d4 AS $$
DECLARE req jsonb=jsonb_build_object('action','REQUEST_CHECKPOINT','delivery',delivery,'version',expected_version);prior jsonb;info jsonb;op public.operations;result jsonb;
BEGIN
 PERFORM d3.lock_state();prior=d4.checkpoint_previous(cid,req);IF prior IS NOT NULL THEN RETURN prior;END IF;
 info=d4.lab_inspect(delivery);SELECT * INTO STRICT op FROM public.operations WHERE id=(info->>'operation')::uuid;
 IF expected_version IS DISTINCT FROM op.row_version OR op.state<>'RUNNING' OR (info->>'lease_expired')::boolean THEN RAISE EXCEPTION 'Live exact RUNNING version required' USING ERRCODE='23514';END IF;
 IF NOT coalesce((op.policy_snapshot->>'interruptible')::boolean,false) THEN result=jsonb_build_object('status','DEFERRED_NONINTERRUPTIBLE');
 ELSE
  IF NOT EXISTS(SELECT 1 FROM d4.step_intents WHERE operation_id=op.id) THEN RAISE EXCEPTION 'Frozen step intent required' USING ERRCODE='23514';END IF;
  INSERT INTO d4.checkpoint_requests VALUES(cid,delivery,op.id,(info->>'attempt')::uuid,(info->>'generation')::bigint,op.row_version);
  result=jsonb_build_object('status','CHECKPOINT_REQUESTED','request_id',cid);
 END IF;
 INSERT INTO d4.checkpoint_commands VALUES(cid,req,result);RETURN result;
END $$;

-- Restricted verifier ingress. Fixed two-step calibrated fixture, not real usage.
CREATE FUNCTION d4.record_checkpoint_proof(cid uuid,rid uuid,proof jsonb) RETURNS jsonb LANGUAGE plpgsql SECURITY DEFINER
SET search_path=pg_catalog,public,d2,d3,d4 AS $$
DECLARE r d4.checkpoint_requests;i d4.step_intents;op public.operations;old d4.checkpoint_proofs;
BEGIN
 PERFORM d3.lock_state();SELECT * INTO STRICT r FROM d4.checkpoint_requests WHERE id=rid;
 SELECT * INTO STRICT i FROM d4.step_intents WHERE operation_id=r.operation_id;SELECT * INTO STRICT op FROM public.operations WHERE id=r.operation_id;
 IF cid IS NULL OR proof->>'schema' IS DISTINCT FROM 'd4.checkpoint.proof.v1' OR proof->>'manifest_hash' IS DISTINCT FROM i.manifest_hash
  OR proof->>'context_hash' IS DISTINCT FROM op.context_pack_sha256 OR proof->>'policy_hash' IS DISTINCT FROM encode(public.digest(op.policy_snapshot::text,'sha256'),'hex')
  OR proof->>'attempt' IS DISTINCT FROM r.attempt_id::text OR proof->>'generation' IS DISTINCT FROM r.generation::text
  OR proof->'process_stopped' IS DISTINCT FROM 'true'::jsonb OR proof->'artifact_valid' IS DISTINCT FROM 'true'::jsonb
  OR proof->'receiver_closed' IS DISTINCT FROM 'true'::jsonb OR coalesce((proof->>'close_sequence')::bigint,0)<=0
  OR proof->'steps' IS DISTINCT FROM '{"step-1":"APPLIED","step-2":"ABSENT"}'::jsonb
  OR proof->'consumed_units' IS DISTINCT FROM '4'::jsonb
  OR i.manifest IS DISTINCT FROM '{"schema":"d4.steps.v1","steps":[{"id":"step-1","units":4},{"id":"step-2","units":6}]}'::jsonb
  OR EXISTS(SELECT 1 FROM d2.effect_receipts WHERE operation_id=op.id AND status='UNKNOWN')
 THEN RAISE EXCEPTION 'Complete independent sealed partial proof required' USING ERRCODE='23514';END IF;
 SELECT * INTO old FROM d4.checkpoint_proofs WHERE id=cid;
 IF FOUND THEN IF old.request_id IS DISTINCT FROM rid OR old.proof IS DISTINCT FROM proof THEN RAISE EXCEPTION 'Proof replay conflict' USING ERRCODE='23514';END IF;
 ELSE INSERT INTO d4.checkpoint_proofs VALUES(cid,rid,proof);END IF;
 RETURN jsonb_build_object('proof_id',cid);
END $$;

CREATE FUNCTION d4.commit_checkpoint(cid uuid,rid uuid,pid uuid,expected_version bigint) RETURNS jsonb LANGUAGE plpgsql SECURITY DEFINER
SET search_path=pg_catalog,public,d2,d3,d4 AS $$
DECLARE req jsonb=jsonb_build_object('action','COMMIT_CHECKPOINT','request',rid,'proof',pid,'version',expected_version);prior jsonb;
 r d4.checkpoint_requests;pr d4.checkpoint_proofs;op public.operations;i d4.step_intents;res d2.reservations;info jsonb;entries jsonb;releases jsonb;row record;delta numeric;result jsonb;
BEGIN
 PERFORM d3.lock_state();prior=d4.checkpoint_previous(cid,req);IF prior IS NOT NULL THEN RETURN prior;END IF;
 SELECT * INTO STRICT r FROM d4.checkpoint_requests WHERE id=rid;SELECT * INTO STRICT pr FROM d4.checkpoint_proofs WHERE id=pid AND request_id=rid;
 info=d4.lab_inspect(r.delivery_id);SELECT * INTO STRICT op FROM public.operations WHERE id=r.operation_id;
 SELECT * INTO STRICT i FROM d4.step_intents WHERE operation_id=op.id;SELECT * INTO STRICT res FROM d2.reservations WHERE operation_id=op.id;
 IF op.state<>'RUNNING' OR (info->>'lease_expired')::boolean OR op.row_version IS DISTINCT FROM expected_version OR r.expected_version IS DISTINCT FROM expected_version
  OR info->>'context_hash' IS DISTINCT FROM op.context_pack_sha256 OR info->>'policy_hash' IS DISTINCT FROM encode(public.digest(op.policy_snapshot::text,'sha256'),'hex')
  OR r.attempt_id IS DISTINCT FROM (info->>'attempt')::uuid OR r.generation IS DISTINCT FROM op.lease_generation
  OR NOT coalesce((op.policy_snapshot->>'interruptible')::boolean,false)
  OR pr.proof->>'context_hash' IS DISTINCT FROM op.context_pack_sha256 OR pr.proof->>'manifest_hash' IS DISTINCT FROM i.manifest_hash
  OR pr.proof->>'policy_hash' IS DISTINCT FROM encode(public.digest(op.policy_snapshot::text,'sha256'),'hex')
  OR EXISTS(SELECT 1 FROM d4.checkpoints WHERE operation_id=op.id)
  OR EXISTS(SELECT 1 FROM d2.effect_receipts er WHERE er.operation_id=op.id AND (er.status='UNKNOWN' OR er.generation<>r.generation))
  OR (SELECT count(*) FROM d2.operation_accounts WHERE operation_id=op.id)<>1
  OR EXISTS(SELECT 1 FROM d2.effect_receipts er WHERE er.operation_id=op.id AND
    NOT ((er.effect_key=op.id||'/'||op.context_pack_sha256||'/step-1' AND er.status='APPLIED') OR (er.effect_key=op.id||'/'||op.context_pack_sha256||'/step-2' AND er.status='ABSENT')))
  OR EXISTS(SELECT 1 FROM d2.effect_receipts WHERE operation_id=op.id GROUP BY effect_key,generation HAVING count(DISTINCT status)>1)
 THEN RAISE EXCEPTION 'Live sealed checkpoint identity/version required' USING ERRCODE='23514';END IF;
 entries='[]';
 FOR row IN SELECT b.*,a.units FROM d2.reservation_balances b JOIN d2.operation_accounts a ON a.account_id=b.account_id AND a.operation_id=op.id WHERE b.reservation_id=res.id ORDER BY b.account_id LOOP
  delta=4-row.consumed;
  IF delta<0 OR delta>row.outstanding OR row.units<>10 THEN RAISE EXCEPTION 'Verified bounded incremental consumption required' USING ERRCODE='23514';END IF;
  entries=entries||jsonb_build_array(jsonb_build_object('account_id',row.account_id,'settled',delta,'consumed',delta));
 END LOOP;
 IF jsonb_array_length(entries)=0 THEN RAISE EXCEPTION 'All physical accounts required' USING ERRCODE='23514';END IF;
 PERFORM d2.capacity(public.gen_random_uuid(),jsonb_build_object('action','CONSUME','reservation_id',res.id,'entries',entries,'reason','Verified checkpoint incremental consumption'));
 SELECT jsonb_agg(jsonb_build_object('account_id',account_id,'settled',outstanding) ORDER BY account_id) INTO releases FROM d2.reservation_balances WHERE reservation_id=res.id;
 PERFORM d2.capacity(public.gen_random_uuid(),jsonb_build_object('action','RELEASE','reservation_id',res.id,'entries',releases,'reason','Sealed checkpoint remainder'));
 INSERT INTO d2.effect_receipts(operation_id,generation,effect_key,status,evidence_ref) VALUES(op.id,r.generation,op.id||'/'||op.context_pack_sha256||'/step-1','APPLIED','checkpoint-proof/'||pid),(op.id,r.generation,op.id||'/'||op.context_pack_sha256||'/step-2','ABSENT','checkpoint-proof/'||pid);
 UPDATE public.execution_attempts SET state='CANCELLED',finished_at=clock_timestamp() WHERE id=r.attempt_id;
 DELETE FROM public.operation_leases WHERE operation_id=op.id;
 UPDATE public.operations SET state='CANCELLED',row_version=row_version+1 WHERE id=op.id;
 PERFORM d2.record_transition(cid,'OPERATION',op.id,'RUNNING','CANCELLED',op.row_version+1,'CONTROL_PLANE','Sealed partial checkpoint');
 INSERT INTO d4.checkpoints VALUES(cid,rid,pid,op.id,r.attempt_id,r.generation,res.id,op.context_pack_sha256,encode(public.digest(op.policy_snapshot::text,'sha256'),'hex'),i.manifest_hash,op.row_version+1);
 result=jsonb_build_object('checkpoint_id',cid,'state','CANCELLED','row_version',op.row_version+1);
 INSERT INTO d4.checkpoint_commands VALUES(cid,req,result);
 INSERT INTO public.outbox_events(aggregate_type,aggregate_id,event_type,payload) VALUES('OPERATION',op.id,'D4_CHECKPOINT_COMMITTED',result);
 RETURN result;
END $$;

CREATE FUNCTION d4.continuation_safe(oid uuid,gen bigint) RETURNS boolean LANGUAGE sql STABLE SECURITY DEFINER
SET search_path=pg_catalog,public,d2,d3,d4 AS $$
 SELECT EXISTS(SELECT 1 FROM d4.checkpoints cp JOIN d4.continuation_authorizations au ON au.checkpoint_id=cp.id
 JOIN public.operations op ON op.id=cp.operation_id JOIN d4.step_intents i ON i.operation_id=op.id
 WHERE cp.operation_id=oid AND cp.source_generation=gen AND op.lease_generation=gen AND op.row_version=au.authorized_version AND op.state='READY'
 AND cp.context_hash=op.context_pack_sha256 AND cp.policy_hash=encode(public.digest(op.policy_snapshot::text,'sha256'),'hex') AND cp.manifest_hash=i.manifest_hash
 AND NOT EXISTS(SELECT 1 FROM d4.continuation_links WHERE checkpoint_id=cp.id)
 AND NOT EXISTS(SELECT 1 FROM d2.effect_receipts er WHERE er.operation_id=oid AND NOT (er.generation=gen AND
  ((er.effect_key=oid||'/'||cp.context_hash||'/step-1' AND er.status='APPLIED') OR (er.effect_key=oid||'/'||cp.context_hash||'/step-2' AND er.status='ABSENT'))))
 AND NOT EXISTS(SELECT 1 FROM d2.effect_receipts WHERE operation_id=oid AND status='UNKNOWN')
 AND NOT EXISTS(SELECT 1 FROM d2.effect_receipts WHERE operation_id=oid GROUP BY generation,effect_key HAVING count(DISTINCT status)>1));
$$;
CREATE VIEW d4.continuation_admissions AS SELECT cp.operation_id,cp.source_generation generation,cp.id checkpoint_id,au.id authorization_id,cp.manifest_hash,
 'SEALED_CHECKPOINT'::text admission_kind,d4.continuation_safe(cp.operation_id,cp.source_generation) eligible
 FROM d4.checkpoints cp JOIN d4.continuation_authorizations au ON au.checkpoint_id=cp.id;

CREATE FUNCTION d4.authorize_continuation(cid uuid,checkpoint uuid,expected_version bigint,reason text) RETURNS jsonb LANGUAGE plpgsql SECURITY DEFINER
SET search_path=pg_catalog,public,d2,d3,d4 AS $$
DECLARE req jsonb=jsonb_build_object('action','AUTHORIZE_CONTINUATION','checkpoint',checkpoint,'version',expected_version,'reason',reason);prior jsonb;cp d4.checkpoints;op public.operations;result jsonb;
BEGIN
 PERFORM d3.lock_state();prior=d4.checkpoint_previous(cid,req);IF prior IS NOT NULL THEN RETURN prior;END IF;
 SELECT * INTO STRICT cp FROM d4.checkpoints WHERE id=checkpoint;SELECT * INTO STRICT op FROM public.operations WHERE id=cp.operation_id;
 IF op.state<>'CANCELLED' OR op.row_version IS DISTINCT FROM expected_version OR cp.committed_version IS DISTINCT FROM expected_version
  OR cp.source_generation<>op.lease_generation OR reason IS NULL OR length(btrim(reason)) NOT BETWEEN 1 AND 512
  OR cp.context_hash IS DISTINCT FROM op.context_pack_sha256 OR cp.policy_hash IS DISTINCT FROM encode(public.digest(op.policy_snapshot::text,'sha256'),'hex')
  OR EXISTS(SELECT 1 FROM d2.effect_receipts er WHERE er.operation_id=op.id AND NOT (er.generation=cp.source_generation AND
    ((er.effect_key=op.id||'/'||cp.context_hash||'/step-1' AND er.status='APPLIED') OR (er.effect_key=op.id||'/'||cp.context_hash||'/step-2' AND er.status='ABSENT'))))
  OR EXISTS(SELECT 1 FROM d2.effect_receipts WHERE operation_id=op.id AND status='UNKNOWN')
  OR EXISTS(SELECT 1 FROM d2.effect_receipts WHERE operation_id=op.id GROUP BY generation,effect_key HAVING count(DISTINCT status)>1)
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
ALTER FUNCTION d3.state_relations() RENAME TO state_relations_before_d4_i5;
CREATE FUNCTION d3.state_relations() RETURNS text[] LANGUAGE sql IMMUTABLE AS $$ SELECT d3.state_relations_before_d4_i5()||ARRAY['d4.step_intents','d4.checkpoint_requests','d4.checkpoint_proofs','d4.checkpoints','d4.continuation_authorizations','d4.continuation_links','d4.continuation_admissions']; $$;
REVOKE ALL ON ALL TABLES IN SCHEMA d4 FROM PUBLIC;
REVOKE ALL ON FUNCTION d4.checkpoint_previous(uuid,jsonb),d4.checkpoint_request(uuid,uuid,bigint),d4.record_checkpoint_proof(uuid,uuid,jsonb),d4.commit_checkpoint(uuid,uuid,uuid,bigint),d4.continuation_safe(uuid,bigint),d4.authorize_continuation(uuid,uuid,bigint,text) FROM PUBLIC;

REVOKE ALL ON FUNCTION d4.freeze_step_intent() FROM PUBLIC;
