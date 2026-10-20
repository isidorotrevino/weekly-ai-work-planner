-- SPDX-License-Identifier: GPL-3.0-only
-- D3 I3 additive prototype. Disposable validation; no deployment grants.
CREATE TABLE d3.dispatches (
  command_id uuid PRIMARY KEY REFERENCES d3.commands(id) DEFERRABLE INITIALLY DEFERRED,
  planning_run_id uuid NOT NULL REFERENCES d3.plan_manifests(planning_run_id),
  operation_id uuid NOT NULL REFERENCES public.operations(id),
  attempt_id uuid NOT NULL UNIQUE REFERENCES public.execution_attempts(id),
  reservation_id uuid NOT NULL REFERENCES d2.reservations(id),
  estimate_id uuid NOT NULL REFERENCES d3.estimates(id),
  worker_id uuid NOT NULL REFERENCES public.workers(id),resource_id uuid NOT NULL REFERENCES public.resources(id),
  generation bigint NOT NULL, recorded_at timestamptz NOT NULL DEFAULT clock_timestamp()
);
CREATE TRIGGER immutable_dispatch BEFORE UPDATE OR DELETE OR TRUNCATE ON d3.dispatches
  FOR EACH STATEMENT EXECUTE FUNCTION public.d2_reject_fact_mutation();
-- Preserve V12's relation list without editing its historical migration.
ALTER FUNCTION d3.state_relations() RENAME TO state_relations_i2;
CREATE FUNCTION d3.state_relations() RETURNS text[] LANGUAGE sql IMMUTABLE AS $$
  SELECT d3.state_relations_i2() || ARRAY['d3.dispatches'];
$$;

CREATE FUNCTION d3.dispatch(cid uuid,req jsonb) RETURNS jsonb LANGUAGE plpgsql SECURITY DEFINER
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

-- Control-plane lifecycle boundary; workers never get SQL credentials. No
-- checkpoint/preemption implementation or creation of external evidence here.
CREATE FUNCTION d3.execution(cid uuid,req jsonb) RETURNS jsonb LANGUAGE plpgsql SECURITY DEFINER
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
REVOKE ALL ON d3.dispatches FROM PUBLIC;
REVOKE ALL ON FUNCTION d3.state_relations_i2(),d3.state_relations(),d3.dispatch(uuid,jsonb),d3.execution(uuid,jsonb) FROM PUBLIC;
