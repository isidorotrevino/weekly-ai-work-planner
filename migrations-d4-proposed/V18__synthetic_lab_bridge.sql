-- SPDX-License-Identifier: GPL-3.0-only
-- Synthetic laboratory bridge; no checkpoint transitions, no migration promotion.
CREATE TABLE d4.lab_intents (
  operation_id uuid PRIMARY KEY REFERENCES public.operations(id),context_bytes bytea NOT NULL,
  consumed_units numeric NOT NULL CHECK(consumed_units>=0)
);
CREATE TABLE d4.lab_grants (
  id uuid PRIMARY KEY,request jsonb NOT NULL,response jsonb NOT NULL
);
CREATE TABLE d4.lab_evidence (
  id uuid PRIMARY KEY,delivery_id uuid NOT NULL REFERENCES d4.deliveries(id),
  effect_status text NOT NULL CHECK(effect_status IN ('APPLIED','UNKNOWN')),
  receipt_id uuid NOT NULL REFERENCES d2.effect_receipts(id),acceptance boolean NOT NULL,
  proof jsonb NOT NULL,recorded_at timestamptz NOT NULL DEFAULT clock_timestamp()
);
DO $$ DECLARE r text;BEGIN
  FOREACH r IN ARRAY ARRAY['lab_intents','lab_grants','lab_evidence'] LOOP
    EXECUTE format('CREATE TRIGGER immutable_fact BEFORE UPDATE OR DELETE OR TRUNCATE ON d4.%I FOR EACH STATEMENT EXECUTE FUNCTION public.d2_reject_fact_mutation()',r);
  END LOOP;
END $$;

CREATE FUNCTION d4.lab_inspect(delivery uuid) RETURNS jsonb LANGUAGE sql SECURITY DEFINER
SET search_path=pg_catalog,public,d2,d3,d4 AS $$
 SELECT jsonb_build_object('delivery_id',dl.id,'operation',ds.operation_id,'attempt',ds.attempt_id,
  'worker',ds.worker_id,'resource',ds.resource_id,'generation',ds.generation,'state',op.state,
  'lease_expires_at',l.expires_at,'lease_expired',l.expires_at<=clock_timestamp(),'database_now',clock_timestamp(),
  'context_hash',x.context_sha256,'policy_hash',x.policy_sha256,'context_b64',encode(fi.context_bytes,'base64'),
  'consumed_units',fi.consumed_units,'unresolved_evidence',EXISTS(SELECT 1 FROM d2.effect_receipts er WHERE er.operation_id=op.id AND er.generation=ds.generation AND er.status<>'APPLIED'),'accounts',(SELECT jsonb_agg(jsonb_build_object('account_id',m.account_id,'units',m.units,
     'outstanding',b.outstanding,'consumed',b.consumed) ORDER BY m.account_id)
    FROM d2.operation_accounts m JOIN d2.reservation_balances b ON b.account_id=m.account_id AND b.reservation_id=ds.reservation_id WHERE m.operation_id=op.id))
 FROM d4.deliveries dl JOIN d3.dispatches ds ON ds.command_id=dl.dispatch_command_id
 JOIN public.operations op ON op.id=ds.operation_id JOIN d2.execution_snapshots x ON x.attempt_id=ds.attempt_id
 JOIN d4.lab_intents fi ON fi.operation_id=op.id LEFT JOIN public.operation_leases l ON l.attempt_id=ds.attempt_id
 WHERE dl.id=delivery;
$$;

CREATE FUNCTION d4.lab_authorize(cid uuid,wid uuid,delivery uuid,receiver uuid) RETURNS jsonb
LANGUAGE plpgsql SECURITY DEFINER SET search_path=pg_catalog,public,d2,d3,d4 AS $$
DECLARE req jsonb=jsonb_build_object('worker',wid,'delivery',delivery,'receiver',receiver);prior d4.lab_grants;info jsonb;result jsonb;
BEGIN
  IF current_setting('transaction_isolation')<>'read committed' THEN RAISE EXCEPTION 'READ COMMITTED required' USING ERRCODE='25001';END IF;
  PERFORM d3.lock_state();PERFORM d4.require_worker(wid);
  SELECT * INTO prior FROM d4.lab_grants WHERE id=cid;
  IF FOUND THEN IF prior.request IS DISTINCT FROM req THEN RAISE EXCEPTION 'Grant command conflict' USING ERRCODE='23514';END IF;RETURN prior.response;END IF;
  IF cid IS NULL OR receiver IS NULL OR NOT EXISTS(SELECT 1 FROM d4.deliveries WHERE id=delivery AND worker_id=wid) THEN RAISE EXCEPTION 'Grant ownership mismatch' USING ERRCODE='42501';END IF;
  info=d4.lab_inspect(delivery);
  IF encode(public.digest(decode(info->>'context_b64','base64'),'sha256'),'hex') IS DISTINCT FROM info->>'context_hash' THEN RAISE EXCEPTION 'Context bytes mismatch' USING ERRCODE='23514';END IF;
  IF info->>'state'<>'RUNNING' THEN RAISE EXCEPTION 'RUNNING required for grant' USING ERRCODE='23514';END IF;
  -- This reuses every D3/D2 admission and full 60-second renewal guard.
  PERFORM d4.worker_execution(cid,wid,jsonb_build_object('action','HEARTBEAT','delivery_id',delivery));
  result=d4.lab_inspect(delivery)||jsonb_build_object('receiver_id',receiver,'issued_at',clock_timestamp());
  IF result->'lease_expired'='true'::jsonb OR result->>'lease_expires_at' IS NULL THEN RAISE EXCEPTION 'Lease expired during grant' USING ERRCODE='23514';END IF;
  INSERT INTO d4.lab_grants VALUES(cid,req,result);RETURN result;
END $$;

-- Granted only to the separate verifier LOGIN, never the control-plane runtime.
CREATE FUNCTION d4.lab_record_evidence(cid uuid,delivery uuid,status text,accepted boolean,proof jsonb) RETURNS jsonb
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

CREATE FUNCTION d4.lab_admin(cid uuid,delivery uuid,action text,proof_id uuid) RETURNS jsonb
LANGUAGE plpgsql SECURITY DEFINER SET search_path=pg_catalog,public,d2,d3,d4 AS $$
DECLARE info jsonb;req jsonb;proof d4.lab_evidence;
BEGIN
  PERFORM d3.lock_state();info=d4.lab_inspect(delivery);
  IF info IS NULL OR action IS NULL OR action NOT IN ('EXPIRE','RECONCILE','VERIFY','RECOVERY_VERIFY') THEN RAISE EXCEPTION 'Lab recovery action not allowed' USING ERRCODE='23514';END IF;
  req=jsonb_build_object('action',action,'operation_id',info->>'operation','attempt_id',info->>'attempt','worker_id',info->>'worker','resource_id',info->>'resource','generation',info->'generation');
  IF action<>'EXPIRE' THEN
    SELECT * INTO proof FROM d4.lab_evidence WHERE id=proof_id AND delivery_id=delivery;
    IF NOT FOUND OR (action IN ('VERIFY','RECOVERY_VERIFY') AND NOT proof.acceptance) THEN RAISE EXCEPTION 'Independent verifier evidence required' USING ERRCODE='23514';END IF;
    IF action IN ('VERIFY','RECOVERY_VERIFY') AND (info->>'unresolved_evidence')::boolean THEN RAISE EXCEPTION 'Unresolved or contradictory evidence remains blocked' USING ERRCODE='23514';END IF;
    req=req||jsonb_build_object('receipt_id',proof.receipt_id);
    IF action='RECOVERY_VERIFY' THEN req=req||jsonb_build_object('entries',(SELECT jsonb_agg(jsonb_build_object('account_id',a->>'account_id','settled',(a->>'outstanding')::numeric,'consumed',(info->>'consumed_units')::numeric)) FROM jsonb_array_elements(info->'accounts') a));END IF;
  END IF;
  RETURN d3.execution(cid,req);
END $$;

CREATE FUNCTION d4.lab_audit() RETURNS jsonb LANGUAGE sql SECURITY DEFINER
SET search_path=pg_catalog,public,d2,d3,d4 AS $$
 SELECT jsonb_build_object('database_now',clock_timestamp(),
 'operations',(SELECT coalesce(jsonb_agg(to_jsonb(o) ORDER BY o.id),'[]') FROM public.operations o),
 'attempts',(SELECT coalesce(jsonb_agg(to_jsonb(a) ORDER BY a.id),'[]') FROM public.execution_attempts a),
 'leases',(SELECT coalesce(jsonb_agg(to_jsonb(l) ORDER BY l.operation_id),'[]') FROM public.operation_leases l),
 'balances',(SELECT coalesce(jsonb_agg(to_jsonb(b) ORDER BY b.account_id,b.pool),'[]') FROM d2.balances b),
 'reservations',(SELECT coalesce(jsonb_agg(to_jsonb(r) ORDER BY r.id),'[]') FROM d2.reservations r),
 'journal',(SELECT coalesce(jsonb_agg(to_jsonb(j) ORDER BY j.id),'[]') FROM d2.journal j),
 'deliveries',(SELECT coalesce(jsonb_agg(to_jsonb(d) ORDER BY d.id),'[]') FROM d4.deliveries d),
 'evidence',(SELECT coalesce(jsonb_agg(to_jsonb(e) ORDER BY e.id),'[]') FROM d4.lab_evidence e),
 'effects',(SELECT coalesce(jsonb_agg(to_jsonb(e) ORDER BY e.id),'[]') FROM d2.effect_receipts e),
 'plans',(SELECT coalesce(jsonb_agg(to_jsonb(p) ORDER BY p.created_at),'[]') FROM public.planning_runs p),
 'schedule',(SELECT coalesce(jsonb_agg(to_jsonb(s) ORDER BY s.id),'[]') FROM public.schedule_entries s),
 'manifests',(SELECT coalesce(jsonb_agg(jsonb_build_object('plan',m.planning_run_id,'result',m.result)),'[]') FROM d3.plan_manifests m),
 'head',(SELECT planning_run_id FROM d3.plan_head));
$$;
REVOKE ALL ON ALL TABLES IN SCHEMA d4 FROM PUBLIC;
REVOKE ALL ON FUNCTION d4.lab_inspect(uuid),d4.lab_authorize(uuid,uuid,uuid,uuid),d4.lab_record_evidence(uuid,uuid,text,boolean,jsonb),d4.lab_admin(uuid,uuid,text,uuid),d4.lab_audit() FROM PUBLIC;
