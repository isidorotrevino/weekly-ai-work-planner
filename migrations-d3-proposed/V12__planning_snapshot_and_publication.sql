-- SPDX-License-Identifier: GPL-3.0-only
-- D3 I2 additive proposal. Disposable validation only; no production promotion.
-- Kept separate from migrations-proposed/ to preserve the D2 V10->V11 audit.
CREATE SCHEMA d3;
CREATE TABLE d3.commands (
  id uuid PRIMARY KEY, request jsonb NOT NULL, response jsonb NOT NULL,
  recorded_at timestamptz NOT NULL DEFAULT clock_timestamp()
);
CREATE TABLE d3.fairness_epochs (
  id uuid PRIMARY KEY, reason text NOT NULL CHECK(length(btrim(reason))>0),
  calibration_ref text NOT NULL CHECK(length(btrim(calibration_ref))>0),
  created_at timestamptz NOT NULL DEFAULT clock_timestamp()
);
CREATE TABLE d3.settings (
  singleton boolean PRIMARY KEY DEFAULT true CHECK(singleton), policy jsonb NOT NULL,
  calibration_epoch text NOT NULL CHECK(length(btrim(calibration_epoch))>0),
  fairness_epoch uuid NOT NULL REFERENCES d3.fairness_epochs(id)
);
CREATE TABLE d3.estimates (
  id uuid PRIMARY KEY, operation_id uuid NOT NULL REFERENCES public.operations(id),
  resource_id uuid NOT NULL REFERENCES public.resources(id), units jsonb NOT NULL CHECK(jsonb_typeof(units)='object' AND units<>'{}'),
  duration_ms bigint NOT NULL CHECK(duration_ms>0), confidence numeric(4,3) NOT NULL CHECK(confidence BETWEEN 0 AND 1),
  calibration_ref text NOT NULL CHECK(length(btrim(calibration_ref))>0), provenance text NOT NULL CHECK(length(btrim(provenance))>0),
  observed_at timestamptz NOT NULL, valid_until timestamptz NOT NULL CHECK(valid_until>observed_at),
  UNIQUE(id,operation_id,resource_id)
);
CREATE TABLE d3.estimate_heads (
  operation_id uuid NOT NULL, resource_id uuid NOT NULL, estimate_id uuid NOT NULL,
  PRIMARY KEY(operation_id,resource_id),
  FOREIGN KEY(estimate_id,operation_id,resource_id) REFERENCES d3.estimates(id,operation_id,resource_id)
);
CREATE TABLE d3.calendars (
  id uuid PRIMARY KEY,resource_id uuid NOT NULL REFERENCES public.resources(id),
  slots jsonb NOT NULL CHECK(jsonb_typeof(slots)='array'), UNIQUE(id,resource_id)
);
CREATE TABLE d3.calendar_heads (
  resource_id uuid PRIMARY KEY REFERENCES public.resources(id),calendar_id uuid NOT NULL,
  FOREIGN KEY(calendar_id,resource_id) REFERENCES d3.calendars(id,resource_id)
);
CREATE TABLE d3.incident_classifications (
  incident_id uuid PRIMARY KEY REFERENCES public.incidents(id),active_response boolean NOT NULL,
  reason text NOT NULL CHECK(length(btrim(reason))>0)
);
CREATE TABLE d3.eligibility_ticks (
  id bigint GENERATED ALWAYS AS IDENTITY PRIMARY KEY, operation_id uuid NOT NULL REFERENCES public.operations(id),
  eligible boolean NOT NULL,observed_at timestamptz NOT NULL,valid_until timestamptz NOT NULL CHECK(valid_until>=observed_at),command_id uuid NOT NULL REFERENCES d3.commands(id) DEFERRABLE INITIALLY DEFERRED
);
CREATE INDEX eligibility_operation_time ON d3.eligibility_ticks(operation_id,observed_at,id);
CREATE TABLE d3.lane_attributions (
  reservation_id uuid PRIMARY KEY REFERENCES d2.reservations(id),
  lane text NOT NULL CHECK(lane IN ('WEIGHTED','AGED','URGENT','INCIDENT')),
  reason text NOT NULL CHECK(length(btrim(reason))>0), created_at timestamptz NOT NULL DEFAULT clock_timestamp()
);
CREATE VIEW d3.lane_usage AS
  SELECT b.account_id,a.lane,sum(b.outstanding+b.consumed) units
  FROM d3.lane_attributions a JOIN d2.reservation_balances b ON b.reservation_id=a.reservation_id
  WHERE a.lane IN ('AGED','URGENT') GROUP BY b.account_id,a.lane;
CREATE VIEW d3.eligible_intervals AS
  SELECT t.operation_id,t.eligible,t.observed_at,
    least(t.valid_until,t.next_at,(SELECT min(a.started_at) FROM public.execution_attempts a
      WHERE a.operation_id=t.operation_id AND a.started_at>=t.observed_at)) end_at
  FROM (SELECT operation_id,eligible,observed_at,valid_until,
    lead(observed_at) OVER(PARTITION BY operation_id ORDER BY observed_at,id) next_at
    FROM d3.eligibility_ticks) t;
CREATE TABLE d3.captures (
  id uuid PRIMARY KEY,captured_at timestamptz NOT NULL,basis_hash char(64) NOT NULL,body jsonb NOT NULL
);
CREATE TABLE d3.plan_head (
  singleton boolean PRIMARY KEY DEFAULT true CHECK(singleton),planning_run_id uuid REFERENCES public.planning_runs(id)
);
INSERT INTO d3.plan_head VALUES(true,NULL);
CREATE TABLE d3.plan_manifests (
  planning_run_id uuid PRIMARY KEY REFERENCES public.planning_runs(id),capture_id uuid NOT NULL REFERENCES d3.captures(id),
  result jsonb NOT NULL
);
CREATE TRIGGER manifest_write_lock BEFORE INSERT OR UPDATE OR DELETE ON d3.plan_manifests FOR EACH STATEMENT EXECUTE FUNCTION public.d2_plan_write_lock();
CREATE TRIGGER manifest_guard BEFORE INSERT OR UPDATE OR DELETE ON d3.plan_manifests FOR EACH ROW EXECUTE FUNCTION public.d2_plan_child_guard();
CREATE TRIGGER manifest_no_truncate BEFORE TRUNCATE ON d3.plan_manifests FOR EACH STATEMENT EXECUTE FUNCTION public.d2_reject_fact_mutation();
DO $$ DECLARE rel text; BEGIN
  FOREACH rel IN ARRAY ARRAY['commands','fairness_epochs','estimates','calendars','eligibility_ticks','lane_attributions','captures'] LOOP
    EXECUTE format('CREATE TRIGGER immutable_fact BEFORE UPDATE OR DELETE OR TRUNCATE ON d3.%I FOR EACH STATEMENT EXECUTE FUNCTION public.d2_reject_fact_mutation()',rel);
  END LOOP;
END $$;

-- Whitelist shared by snapshot and publication locks. Full row sets, not max IDs.
CREATE FUNCTION d3.state_relations() RETURNS text[] LANGUAGE sql IMMUTABLE AS $$
  SELECT ARRAY[
    'public.projects','public.tasks','public.operations','public.resources','public.workers',
    'public.task_dependencies','public.project_dependencies','public.capability_requirements',
    'public.capabilities','public.capability_versions','public.approvals','public.execution_attempts',
    'public.operation_leases','public.incidents','public.incident_task_links','public.execution_evidence',
    'public.artifacts','public.planning_runs','public.schedule_entries','public.capacity_budgets','public.capacity_allocations','public.task_deferrals',
    'd2.accounts','d2.operation_accounts','d2.reservations','d2.journal','d2.capacity_limits','d2.loans',
    'd2.resolutions','d2.capability_producers','d2.capability_epochs','d2.verifications','d2.effect_receipts',
    'd2.checkpoint_receipts','d2.execution_snapshots','d2.budget_accounts','d2.plan_reservations',
    'd3.settings','d3.fairness_epochs','d3.estimates','d3.estimate_heads','d3.calendars','d3.calendar_heads',
    'd3.incident_classifications','d3.eligibility_ticks','d3.lane_attributions','d3.plan_head','d3.plan_manifests'
  ]::text[];
$$;
-- STABLE gives every nested SELECT the same calling-statement MVCC snapshot.
CREATE FUNCTION d3.state_body() RETURNS jsonb LANGUAGE plpgsql STABLE SECURITY DEFINER
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
      WHERE r.capabilities @> coalesce(o.policy_snapshot->'required_capabilities','{}') AND w.capabilities @> coalesce(o.policy_snapshot->'required_capabilities','{}')));
  RETURN body;
END $$;
CREATE FUNCTION d3.lock_state() RETURNS void LANGUAGE plpgsql AS $$
DECLARE rel text;
BEGIN
  -- Publication mutex first, global D2 mutex second, relation/row locks last.
  PERFORM pg_advisory_xact_lock(742001);PERFORM pg_advisory_xact_lock(742002);
  FOR rel IN SELECT unnest(d3.state_relations()) ORDER BY 1 LOOP
    -- Their BEFORE-statement/row guards already serialize writes using the
    -- held mutexes. A SHARE table lock would invert those trigger lock orders.
    IF rel NOT IN ('public.planning_runs','public.schedule_entries','public.capacity_budgets','public.capacity_allocations','public.task_deferrals','d2.budget_accounts','d2.plan_reservations','d3.plan_manifests',
      'public.task_dependencies','public.project_dependencies','public.capability_requirements',
      'd2.resolutions','d2.capability_producers','d2.operation_accounts') THEN
      EXECUTE format('LOCK TABLE %s IN SHARE MODE',rel);
    END IF;
  END LOOP;
END $$;
CREATE FUNCTION d3.previous_command(cid uuid,req jsonb) RETURNS jsonb LANGUAGE plpgsql AS $$
DECLARE previous d3.commands;
BEGIN
  SELECT * INTO previous FROM d3.commands WHERE id=cid;
  IF FOUND THEN
    IF previous.request IS DISTINCT FROM req THEN RAISE EXCEPTION 'Command payload conflict' USING ERRCODE='23505';END IF;
    RETURN previous.response;
  END IF;
  RETURN NULL;
END $$;

-- Administrative metadata changes; execution role never receives this entrypoint.
CREATE FUNCTION d3.configure(cid uuid,req jsonb) RETURNS jsonb LANGUAGE plpgsql SECURITY DEFINER
SET search_path=pg_catalog,public,d2,d3 AS $$
DECLARE previous jsonb;result jsonb;action text=req->>'action';entry record;item jsonb;rid uuid;oid uuid;eid uuid;head uuid;
BEGIN
  PERFORM pg_advisory_xact_lock(742002);
  previous=d3.previous_command(cid,req);IF previous IS NOT NULL THEN RETURN previous;END IF;
  IF nullif(btrim(req->>'reason'),'') IS NULL THEN RAISE EXCEPTION 'Reason required' USING ERRCODE='23514';END IF;
  IF action='PROFILE' THEN
    IF req->'policy'->>'schema_version' IS DISTINCT FROM 'd3.snapshot.v1'
      OR req->'policy'->>'timezone' IS DISTINCT FROM 'Europe/Madrid'
      OR coalesce((req->'policy'->>'max_operations')::integer,0)<=0
      OR coalesce((req->'policy'->>'max_edges')::integer,0)<=0
      OR coalesce((req->'policy'->>'max_candidates')::integer,0)<=0
      OR coalesce((req->'policy'->>'max_compute_ms')::bigint,0)<=0
      OR nullif(btrim(req->>'calibration_epoch'),'') IS NULL THEN RAISE EXCEPTION 'Explicit valid profile required' USING ERRCODE='23514';END IF;
    eid=(req->>'epoch_id')::uuid;
    INSERT INTO d3.fairness_epochs VALUES(eid,req->>'reason',req->>'calibration_epoch',clock_timestamp());
    INSERT INTO d3.settings VALUES(true,req->'policy',req->>'calibration_epoch',eid)
      ON CONFLICT(singleton) DO UPDATE SET policy=EXCLUDED.policy,calibration_epoch=EXCLUDED.calibration_epoch,fairness_epoch=EXCLUDED.fairness_epoch;
    result=jsonb_build_object('epoch_id',eid);
  ELSIF action='ESTIMATE' THEN
    oid=(req->>'operation_id')::uuid;rid=(req->>'resource_id')::uuid;eid=(req->>'estimate_id')::uuid;
    SELECT estimate_id INTO head FROM d3.estimate_heads WHERE operation_id=oid AND resource_id=rid;
    IF head IS DISTINCT FROM (req->>'expected_estimate_id')::uuid THEN RAISE EXCEPTION 'Estimate head conflict' USING ERRCODE='40001';END IF;
    IF jsonb_typeof(req->'units') IS DISTINCT FROM 'object' OR req->'units'='{}' THEN RAISE EXCEPTION 'Account vector required' USING ERRCODE='23514';END IF;
    FOR entry IN SELECT * FROM jsonb_each(req->'units') LOOP
      IF jsonb_typeof(entry.value)<>'number' OR (entry.value::text)::numeric<=0 OR (entry.value::text)::numeric>=1e14
        OR (entry.value::text)::numeric<>round((entry.value::text)::numeric,4)
        OR NOT EXISTS(SELECT 1 FROM d2.accounts WHERE id=entry.key::uuid AND resource_id=rid) THEN RAISE EXCEPTION 'Invalid account vector' USING ERRCODE='23514';END IF;
    END LOOP;
    INSERT INTO d3.estimates VALUES(eid,oid,rid,req->'units',(req->>'duration_ms')::bigint,(req->>'confidence')::numeric,
      req->>'calibration_ref',req->>'provenance',(req->>'observed_at')::timestamptz,(req->>'valid_until')::timestamptz);
    INSERT INTO d3.estimate_heads VALUES(oid,rid,eid) ON CONFLICT(operation_id,resource_id) DO UPDATE SET estimate_id=EXCLUDED.estimate_id;
    result=jsonb_build_object('estimate_id',eid);
  ELSIF action='CALENDAR' THEN
    rid=(req->>'resource_id')::uuid;eid=(req->>'calendar_id')::uuid;
    SELECT calendar_id INTO head FROM d3.calendar_heads WHERE resource_id=rid;
    IF head IS DISTINCT FROM (req->>'expected_calendar_id')::uuid THEN RAISE EXCEPTION 'Calendar head conflict' USING ERRCODE='40001';END IF;
    IF jsonb_typeof(req->'slots') IS DISTINCT FROM 'array' THEN RAISE EXCEPTION 'Calendar array required' USING ERRCODE='23514';END IF;
    FOR item IN SELECT value FROM jsonb_array_elements(req->'slots') LOOP
      IF (item->>'start') IS NULL OR (item->>'end') IS NULL OR (item->>'end')::timestamptz<=(item->>'start')::timestamptz THEN RAISE EXCEPTION 'Invalid calendar slot' USING ERRCODE='23514';END IF;
    END LOOP;
    INSERT INTO d3.calendars VALUES(eid,rid,req->'slots');
    INSERT INTO d3.calendar_heads VALUES(rid,eid) ON CONFLICT(resource_id) DO UPDATE SET calendar_id=EXCLUDED.calendar_id;
    result=jsonb_build_object('calendar_id',eid);
  ELSIF action='INCIDENT' THEN
    INSERT INTO d3.incident_classifications VALUES((req->>'incident_id')::uuid,(req->>'active_response')::boolean,req->>'reason')
      ON CONFLICT(incident_id) DO UPDATE SET active_response=EXCLUDED.active_response,reason=EXCLUDED.reason;
    result=jsonb_build_object('classified',true);
  ELSIF action='ATTRIBUTE_LEGACY' THEN
    SELECT resource_id INTO STRICT rid FROM d2.reservations WHERE id=(req->>'reservation_id')::uuid;
    IF EXISTS(SELECT 1 FROM d2.reservations WHERE id=(req->>'reservation_id')::uuid AND (pool='INCIDENT') IS DISTINCT FROM (req->>'lane'='INCIDENT')) THEN RAISE EXCEPTION 'Lane/pool mismatch' USING ERRCODE='23514';END IF;
    INSERT INTO d3.lane_attributions(reservation_id,lane,reason) VALUES((req->>'reservation_id')::uuid,req->>'lane',req->>'reason');
    result=jsonb_build_object('attributed',true);
  ELSE RAISE EXCEPTION 'Unknown configuration action' USING ERRCODE='23514';END IF;
  INSERT INTO d3.commands(id,request,response) VALUES(cid,req,result);
  INSERT INTO public.audit_events(actor,entity_type,entity_id,action,payload) VALUES(session_user,'D3_METADATA',cid,action,jsonb_build_object('reason',req->>'reason'));
  RETURN result;
END $$;

CREATE FUNCTION d3.capture(cid uuid,req jsonb) RETURNS jsonb LANGUAGE plpgsql SECURITY DEFINER
SET search_path=pg_catalog,public,d2,d3 AS $$
DECLARE previous jsonb;body jsonb;result jsonb;observed timestamptz;
BEGIN
  IF req->>'action' IS DISTINCT FROM 'CAPTURE' THEN RAISE EXCEPTION 'Capture action required' USING ERRCODE='23514';END IF;
  PERFORM pg_advisory_xact_lock(742002);
  previous=d3.previous_command(cid,req);IF previous IS NOT NULL THEN RETURN previous;END IF;
  observed=clock_timestamp();body=d3.state_body();
  IF jsonb_array_length(body->'d3.settings')<>1 THEN RAISE EXCEPTION 'Explicit planning profile/epoch required' USING ERRCODE='23514';END IF;
  INSERT INTO d3.captures VALUES(cid,observed,encode(public.digest(body::text,'sha256'),'hex'),body);
  result=jsonb_build_object('capture_id',cid);
  INSERT INTO d3.commands(id,request,response) VALUES(cid,req,result);RETURN result;
END $$;
CREATE FUNCTION d3.read_capture(cid uuid) RETURNS jsonb LANGUAGE sql STABLE SECURITY DEFINER
SET search_path=pg_catalog,public,d2,d3 SET TimeZone='UTC' AS $$
  SELECT to_jsonb(c) FROM d3.captures c WHERE id=cid;
$$;

-- D2's priority view also contains paused consumers. D3 requires a currently
-- active higher-priority downstream task for the explicit P4 exception.
CREATE FUNCTION d3.p4_blocking_exception(tid uuid) RETURNS boolean LANGUAGE sql STABLE AS $$
  WITH RECURSIVE reachable(node) AS (
    SELECT b FROM d2.active_blocking_edges WHERE a=tid::text
    UNION SELECT e.b FROM reachable r JOIN d2.active_blocking_edges e ON e.a=r.node
  )
  SELECT EXISTS(SELECT 1 FROM reachable r JOIN public.tasks t ON t.id::text=r.node JOIN public.projects p ON p.id=t.project_id
    WHERE p.status='ACTIVE' AND p.priority<>'P4' AND t.status NOT IN ('DONE','CANCELLED','FAILED')
    AND coalesce(p.priority_weight_override,CASE p.priority WHEN 'P0' THEN 8 WHEN 'P1' THEN 4 WHEN 'P2' THEN 2 ELSE 1 END)>0);
$$;

-- Observed guard transitions, not plan publications, maintain eligible waiting time.
CREATE FUNCTION d3.observe_eligibility(cid uuid) RETURNS jsonb LANGUAGE plpgsql SECURITY DEFINER
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
      AND (NOT EXISTS(SELECT 1 FROM public.execution_attempts WHERE operation_id=item.id) OR (EXISTS(SELECT 1 FROM d2.effect_receipts WHERE operation_id=item.id AND generation=item.lease_generation AND status='ABSENT') AND NOT EXISTS(SELECT 1 FROM d2.effect_receipts WHERE operation_id=item.id AND generation=item.lease_generation AND status<>'ABSENT')))
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
        AND r.capabilities @> coalesce(item.policy_snapshot->'required_capabilities','{}') AND w.capabilities @> coalesce(item.policy_snapshot->'required_capabilities','{}')
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

CREATE FUNCTION d3.publish(cid uuid,req jsonb) RETURNS jsonb LANGUAGE plpgsql SECURITY DEFINER
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
      AND (NOT EXISTS(SELECT 1 FROM d2.effect_receipts WHERE operation_id=op.id AND generation=op.lease_generation AND status='ABSENT') OR EXISTS(SELECT 1 FROM d2.effect_receipts WHERE operation_id=op.id AND generation=op.lease_generation AND status<>'ABSENT')) THEN
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
REVOKE ALL ON SCHEMA d3 FROM PUBLIC;
REVOKE ALL ON ALL TABLES IN SCHEMA d3 FROM PUBLIC;
REVOKE ALL ON ALL FUNCTIONS IN SCHEMA d3 FROM PUBLIC;
