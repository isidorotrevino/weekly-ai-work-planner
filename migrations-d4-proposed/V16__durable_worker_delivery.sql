-- SPDX-License-Identifier: GPL-3.0-only
-- D4 laboratory proposal only. No production LOGINs or migration promotion.
CREATE SCHEMA d4;
REVOKE ALL ON SCHEMA d4 FROM PUBLIC;

-- Provisioned by the laboratory owner, never from a worker's HTTP body.
CREATE TABLE d4.worker_catalog (
  worker_id uuid PRIMARY KEY REFERENCES public.workers(id),
  enabled boolean NOT NULL DEFAULT true
);
CREATE TABLE d4.commands (
  id uuid PRIMARY KEY, worker_id uuid NOT NULL REFERENCES public.workers(id),
  request jsonb NOT NULL, response jsonb NOT NULL,
  recorded_at timestamptz NOT NULL DEFAULT clock_timestamp()
);
CREATE TABLE d4.deliveries (
  id uuid PRIMARY KEY REFERENCES d4.commands(id) DEFERRABLE INITIALLY DEFERRED,
  dispatch_command_id uuid NOT NULL UNIQUE REFERENCES d3.dispatches(command_id),
  worker_id uuid NOT NULL REFERENCES public.workers(id),
  attempt_id uuid NOT NULL UNIQUE REFERENCES public.execution_attempts(id),
  response jsonb NOT NULL, recorded_at timestamptz NOT NULL DEFAULT clock_timestamp()
);
CREATE TABLE d4.delivery_acks (
  delivery_id uuid PRIMARY KEY REFERENCES d4.deliveries(id),
  command_id uuid NOT NULL REFERENCES d4.commands(id) DEFERRABLE INITIALLY DEFERRED,
  recorded_at timestamptz NOT NULL DEFAULT clock_timestamp()
);
DO $$ DECLARE rel text; BEGIN
  FOREACH rel IN ARRAY ARRAY['commands','deliveries','delivery_acks'] LOOP
    EXECUTE format('CREATE TRIGGER immutable_fact BEFORE UPDATE OR DELETE OR TRUNCATE ON d4.%I FOR EACH STATEMENT EXECUTE FUNCTION public.d2_reject_fact_mutation()',rel);
  END LOOP;
END $$;

CREATE FUNCTION d4.require_worker(wid uuid) RETURNS void LANGUAGE plpgsql AS $$
BEGIN
  PERFORM 1 FROM d4.worker_catalog WHERE worker_id=wid AND enabled FOR SHARE;
  IF wid IS NULL OR NOT FOUND THEN
    RAISE EXCEPTION 'Worker identity unavailable' USING ERRCODE='42501';
  END IF;
END $$;
CREATE FUNCTION d4.previous_command(cid uuid,wid uuid,req jsonb) RETURNS jsonb LANGUAGE plpgsql AS $$
DECLARE prior d4.commands;
BEGIN
  IF current_setting('transaction_isolation') <> 'read committed' THEN
    RAISE EXCEPTION 'D4 commands require READ COMMITTED' USING ERRCODE='25001';END IF;
  IF cid IS NULL OR jsonb_typeof(req) IS DISTINCT FROM 'object' THEN
    RAISE EXCEPTION 'Explicit command and object required' USING ERRCODE='23514';END IF;
  SELECT * INTO prior FROM d4.commands WHERE id=cid;
  IF FOUND THEN
    IF prior.worker_id IS DISTINCT FROM wid OR prior.request IS DISTINCT FROM req THEN
      RAISE EXCEPTION 'Command content or ownership conflict' USING ERRCODE='23514';END IF;
    RETURN prior.response;
  END IF;
  RETURN NULL;
END $$;

-- principal_worker comes from the trusted mTLS adapter, not a JSON identity.
-- This SQL entrypoint is exclusively for the control plane; workers get no SQL.
CREATE FUNCTION d4.deliver(cid uuid,principal_worker uuid,req jsonb) RETURNS jsonb
LANGUAGE plpgsql SECURITY DEFINER SET search_path=pg_catalog,public,d2,d3,d4 AS $$
DECLARE prior jsonb;result jsonb;existing d4.deliveries;rid uuid;oid uuid;pid uuid;
BEGIN
  PERFORM d3.lock_state();PERFORM d4.require_worker(principal_worker);
  prior=d4.previous_command(cid,principal_worker,req);IF prior IS NOT NULL THEN RETURN prior;END IF;
  IF req->>'action' IS DISTINCT FROM 'DELIVER' OR
    req - ARRAY['action','plan_id','operation_id','resource_id'] <> '{}'::jsonb THEN
    RAISE EXCEPTION 'Explicit delivery fields required' USING ERRCODE='23514';END IF;
  rid=(req->>'resource_id')::uuid;oid=(req->>'operation_id')::uuid;pid=(req->>'plan_id')::uuid;
  IF rid IS NULL OR oid IS NULL OR pid IS NULL THEN
    RAISE EXCEPTION 'Plan, operation and resource required' USING ERRCODE='23514';END IF;
  IF NOT EXISTS(SELECT 1 FROM public.resources WHERE id=rid AND worker_id=principal_worker) THEN
    RAISE EXCEPTION 'Resource does not belong to worker' USING ERRCODE='42501';END IF;
  -- Recover a confirmed delivery even with a different polling command ID.
  -- Never call CLAIM again merely because a transport response was lost.
  SELECT dl.* INTO existing FROM d4.deliveries dl
    JOIN d3.dispatches ds ON ds.command_id=dl.dispatch_command_id
    JOIN public.operation_leases l ON l.attempt_id=dl.attempt_id
    WHERE ds.operation_id=oid AND ds.resource_id=rid AND dl.worker_id=principal_worker;
  IF FOUND THEN result=existing.response;
  ELSE
    result=d3.dispatch(cid,jsonb_build_object('action','CLAIM','plan_id',pid,
      'operation_id',oid,'resource_id',rid,'worker_id',principal_worker));
    result=result||jsonb_build_object('delivery_id',cid,'worker_id',principal_worker,
      'resource_id',rid,'receipt_only',true,'requires_start',true);
    INSERT INTO d4.deliveries(id,dispatch_command_id,worker_id,attempt_id,response)
      VALUES(cid,cid,principal_worker,(result->>'attempt_id')::uuid,result);
  END IF;
  INSERT INTO d4.commands(id,worker_id,request,response) VALUES(cid,principal_worker,req,result);
  RETURN result;
END $$;

CREATE FUNCTION d4.ack(cid uuid,principal_worker uuid,req jsonb) RETURNS jsonb
LANGUAGE plpgsql SECURITY DEFINER SET search_path=pg_catalog,public,d2,d3,d4 AS $$
DECLARE prior jsonb;result jsonb;delivery uuid=(req->>'delivery_id')::uuid;
BEGIN
  PERFORM d3.lock_state();PERFORM d4.require_worker(principal_worker);
  prior=d4.previous_command(cid,principal_worker,req);IF prior IS NOT NULL THEN RETURN prior;END IF;
  IF req->>'action' IS DISTINCT FROM 'ACK' OR req - ARRAY['action','delivery_id'] <> '{}'::jsonb THEN
    RAISE EXCEPTION 'Explicit ack fields required' USING ERRCODE='23514';END IF;
  IF NOT EXISTS(SELECT 1 FROM d4.deliveries WHERE id=delivery AND worker_id=principal_worker) THEN
    RAISE EXCEPTION 'Delivery does not belong to worker' USING ERRCODE='42501';END IF;
  INSERT INTO d4.delivery_acks(delivery_id,command_id) VALUES(delivery,cid) ON CONFLICT DO NOTHING;
  result=jsonb_build_object('delivery_id',delivery,'acknowledged',true,'receipt_only',true);
  INSERT INTO d4.commands(id,worker_id,request,response) VALUES(cid,principal_worker,req,result);
  RETURN result;
END $$;

CREATE FUNCTION d4.current_assignment(principal_worker uuid) RETURNS jsonb
LANGUAGE plpgsql SECURITY DEFINER SET search_path=pg_catalog,public,d2,d3,d4 AS $$
DECLARE result jsonb;
BEGIN
  PERFORM d4.require_worker(principal_worker);
  SELECT dl.response||jsonb_build_object('operation_state',op.state,
      'lease_expires_at',l.expires_at,'lease_expired',l.expires_at<=clock_timestamp(),
      'acknowledged',EXISTS(SELECT 1 FROM d4.delivery_acks a WHERE a.delivery_id=dl.id))
    INTO result FROM d4.deliveries dl JOIN public.operation_leases l ON l.attempt_id=dl.attempt_id
    JOIN public.operations op ON op.id=l.operation_id
    WHERE dl.worker_id=principal_worker ORDER BY dl.recorded_at DESC LIMIT 1;
  RETURN coalesce(result,'null'::jsonb);
END $$;

CREATE FUNCTION d4.worker_execution(cid uuid,principal_worker uuid,req jsonb) RETURNS jsonb
LANGUAGE plpgsql SECURITY DEFINER SET search_path=pg_catalog,public,d2,d3,d4 AS $$
DECLARE prior jsonb;result jsonb;delivery uuid=(req->>'delivery_id')::uuid;
  ds d3.dispatches;payload jsonb=coalesce(req->'payload','{}'::jsonb);action text=req->>'action';
BEGIN
  PERFORM d3.lock_state();PERFORM d4.require_worker(principal_worker);
  prior=d4.previous_command(cid,principal_worker,req);IF prior IS NOT NULL THEN RETURN prior;END IF;
  IF action IS NULL OR action NOT IN ('START','HEARTBEAT','CALLBACK') OR
    req - ARRAY['action','delivery_id','payload'] <> '{}'::jsonb OR
    jsonb_typeof(payload) IS DISTINCT FROM 'object' OR
    (action IN ('START','HEARTBEAT') AND payload <> '{}'::jsonb) OR
    (action='CALLBACK' AND payload - 'entries' <> '{}'::jsonb) THEN
    RAISE EXCEPTION 'Worker lifecycle payload/action not allowed' USING ERRCODE='23514';END IF;
  SELECT dispatch.* INTO ds FROM d4.deliveries dl JOIN d3.dispatches dispatch
    ON dispatch.command_id=dl.dispatch_command_id
    WHERE dl.id=delivery AND dl.worker_id=principal_worker;
  IF NOT FOUND THEN RAISE EXCEPTION 'Delivery does not belong to worker' USING ERRCODE='42501';END IF;
  result=d3.execution(cid,payload||jsonb_build_object('action',action,'operation_id',ds.operation_id,
    'attempt_id',ds.attempt_id,'worker_id',ds.worker_id,'resource_id',ds.resource_id,'generation',ds.generation));
  -- A repeated START receipt is deliberately not a fresh grant for an effect.
  result=result||jsonb_build_object('receipt_only',true);
  INSERT INTO d4.commands(id,worker_id,request,response) VALUES(cid,principal_worker,req,result);
  RETURN result;
END $$;
REVOKE ALL ON ALL TABLES IN SCHEMA d4 FROM PUBLIC;
REVOKE ALL ON ALL FUNCTIONS IN SCHEMA d4 FROM PUBLIC;
