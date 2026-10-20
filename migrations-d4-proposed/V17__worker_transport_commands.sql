-- SPDX-License-Identifier: GPL-3.0-only
-- Synthetic D4 HTTPS adapter. No changes to V1-V16 or checkpoint/retry semantics.
CREATE TABLE d4.transport_commands (
  id uuid PRIMARY KEY,worker_id uuid NOT NULL REFERENCES public.workers(id),
  envelope jsonb NOT NULL,response jsonb NOT NULL,
  recorded_at timestamptz NOT NULL DEFAULT clock_timestamp()
);
CREATE TRIGGER immutable_transport_fact BEFORE UPDATE OR DELETE OR TRUNCATE ON d4.transport_commands
  FOR EACH STATEMENT EXECUTE FUNCTION public.d2_reject_fact_mutation();

-- Only the trusted control plane has EXECUTE. No worker-supplied SQL principal.
CREATE FUNCTION d4.transport(cid uuid,principal_worker uuid,envelope jsonb) RETURNS jsonb
LANGUAGE plpgsql SECURITY DEFINER SET search_path=pg_catalog,public,d2,d3,d4 AS $$
DECLARE prior d4.transport_commands;req jsonb=envelope->'request';action text=req->>'action';
  response jsonb;assignment jsonb;candidate record;
BEGIN
  IF current_setting('transaction_isolation') <> 'read committed' THEN
    RAISE EXCEPTION 'Transport requires READ COMMITTED' USING ERRCODE='25001';END IF;
  PERFORM d3.lock_state();PERFORM d4.require_worker(principal_worker);
  IF cid IS NULL OR jsonb_typeof(envelope) IS DISTINCT FROM 'object' OR
    octet_length(envelope::text)>65536 OR envelope - ARRAY['schema_version','command_id','correlation_id','request'] <> '{}'::jsonb OR
    envelope->>'schema_version' IS DISTINCT FROM 'd4.worker.v1' OR
    (envelope->>'command_id')::uuid IS DISTINCT FROM cid OR
    (envelope->>'correlation_id')::uuid IS NULL OR jsonb_typeof(req) IS DISTINCT FROM 'object' THEN
    RAISE EXCEPTION 'Invalid transport envelope' USING ERRCODE='22023';END IF;
  SELECT * INTO prior FROM d4.transport_commands WHERE id=cid;
  IF FOUND THEN
    IF prior.worker_id IS DISTINCT FROM principal_worker OR prior.envelope IS DISTINCT FROM envelope THEN
      RAISE EXCEPTION 'Transport command content conflict' USING ERRCODE='23514';END IF;
    RETURN prior.response;
  END IF;
  IF action='POLL' THEN
    IF req <> '{"action":"POLL"}'::jsonb THEN RAISE EXCEPTION 'Poll has no client assignment selector' USING ERRCODE='23514';END IF;
    assignment=d4.current_assignment(principal_worker);
    IF assignment='null'::jsonb THEN
      SELECT e.planning_run_id,e.operation_id,e.resource_id INTO candidate
      FROM d3.plan_head h JOIN public.schedule_entries e ON e.planning_run_id=h.planning_run_id
      JOIN public.resources r ON r.id=e.resource_id JOIN public.operations op ON op.id=e.operation_id
      WHERE r.worker_id=principal_worker AND op.state='READY' AND e.state='PLANNED'
        AND e.planned_start<=clock_timestamp() AND e.planned_end>clock_timestamp()
      ORDER BY e.planned_start,e.operation_id LIMIT 1;
      IF FOUND THEN
        assignment=d4.deliver(public.gen_random_uuid(),principal_worker,jsonb_build_object('action','DELIVER',
          'plan_id',candidate.planning_run_id,'operation_id',candidate.operation_id,'resource_id',candidate.resource_id));
      END IF;
    END IF;
    response=jsonb_build_object('assignment',assignment,'receipt_only',true);
  ELSIF action='ACK' THEN response=d4.ack(cid,principal_worker,req);
  ELSIF action IN ('START','HEARTBEAT','CALLBACK') THEN response=d4.worker_execution(cid,principal_worker,req);
  ELSIF action='PRESENCE' THEN
    IF req <> '{"action":"PRESENCE"}'::jsonb THEN RAISE EXCEPTION 'Presence cannot grant capabilities' USING ERRCODE='23514';END IF;
    UPDATE public.workers SET last_heartbeat_at=clock_timestamp() WHERE id=principal_worker;
    -- Keep administrative state and capabilities; no auto-ONLINE or auto-approval.
    response=jsonb_build_object('observed',true,'receipt_only',true);
  ELSE RAISE EXCEPTION 'Worker transport action not allowed' USING ERRCODE='23514';END IF;
  response=jsonb_build_object('schema_version','d4.worker.v1','command_id',cid,
    'correlation_id',envelope->>'correlation_id','result',response);
  INSERT INTO d4.transport_commands(id,worker_id,envelope,response) VALUES(cid,principal_worker,envelope,response);
  RETURN response;
END $$;

CREATE FUNCTION d4.read_transport_command(principal_worker uuid,cid uuid) RETURNS jsonb
LANGUAGE plpgsql SECURITY DEFINER SET search_path=pg_catalog,public,d2,d3,d4 AS $$
DECLARE response jsonb;
BEGIN
  PERFORM d4.require_worker(principal_worker);
  SELECT c.response INTO response FROM d4.transport_commands c WHERE id=cid AND worker_id=principal_worker;
  IF NOT FOUND THEN RAISE EXCEPTION 'Command unavailable for principal' USING ERRCODE='42501';END IF;
  RETURN response;
END $$;
REVOKE ALL ON d4.transport_commands FROM PUBLIC;
REVOKE ALL ON FUNCTION d4.transport(uuid,uuid,jsonb),d4.read_transport_command(uuid,uuid) FROM PUBLIC;
