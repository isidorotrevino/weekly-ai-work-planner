-- SPDX-License-Identifier: GPL-3.0-only
-- D3 callable coordinator prototype. No daemon, login or deployment grants.
-- Coordinator bookkeeping is deliberately outside the physical snapshot readset.
CREATE TABLE d3.planning_requests (
  id uuid PRIMARY KEY DEFAULT public.gen_random_uuid(),
  state text NOT NULL CHECK(state IN ('QUEUED','RUNNING','PUBLISHED','STALE','BLOCKED')),
  first_received_at timestamptz NOT NULL,due_at timestamptz NOT NULL,
  break_protection boolean NOT NULL,revision bigint NOT NULL DEFAULT 0,
  worker_id uuid,generation bigint NOT NULL DEFAULT 0,lease_until timestamptz,
  recalculations integer NOT NULL DEFAULT 0 CHECK(recalculations BETWEEN 0 AND 2),
  published_plan_id uuid REFERENCES public.planning_runs(id),failure_code text
);
CREATE UNIQUE INDEX one_open_planning_request ON d3.planning_requests((true)) WHERE state IN ('QUEUED','RUNNING');
CREATE TABLE d3.planning_events (
  id uuid PRIMARY KEY,request_id uuid NOT NULL REFERENCES d3.planning_requests(id),
  kind text NOT NULL CHECK(kind IN ('INCIDENT_CRITICAL','DEPENDENCY_INVALIDATED','CAPACITY_DEFICIT','WORKER_LOST','APPROVAL_INVALID',
    'PRIORITY_CHANGED','CAPACITY_CHANGED','DEPENDENCY_CHANGED','INCIDENT_CHANGED','ORDINARY','SWEEP')),
  occurred_at timestamptz NOT NULL,received_at timestamptz NOT NULL,content jsonb NOT NULL
);
CREATE TABLE d3.planning_attempts (
  request_id uuid NOT NULL REFERENCES d3.planning_requests(id),attempt_no integer NOT NULL CHECK(attempt_no BETWEEN 0 AND 2),
  revision bigint NOT NULL,break_protection boolean NOT NULL,
  capture_id uuid NOT NULL REFERENCES d3.captures(id),publish_command_id uuid NOT NULL UNIQUE,plan_id uuid NOT NULL UNIQUE,
  state text NOT NULL CHECK(state IN ('PREPARED','PUBLISHED','STALE','BLOCKED')),failure_code text,
  PRIMARY KEY(request_id,attempt_no)
);
CREATE TABLE d3.planning_attempt_history (
  id bigint GENERATED ALWAYS AS IDENTITY PRIMARY KEY,request_id uuid NOT NULL REFERENCES d3.planning_requests(id),
  attempt_no integer NOT NULL,action text NOT NULL,generation bigint NOT NULL,recorded_at timestamptz NOT NULL DEFAULT clock_timestamp(),detail jsonb NOT NULL
);
CREATE TABLE d3.planning_source_receipts (
  outbox_id uuid PRIMARY KEY REFERENCES public.outbox_events(id),content_sha256 char(64) NOT NULL,
  disposition text NOT NULL CHECK(disposition IN ('ACCEPTED','IGNORED')),event_id uuid REFERENCES d3.planning_events(id),
  received_at timestamptz NOT NULL DEFAULT clock_timestamp()
);
CREATE TABLE d3.planning_clock(singleton boolean PRIMARY KEY CHECK(singleton),last_sweep_at timestamptz);
INSERT INTO d3.planning_clock VALUES(true,NULL);
DO $$ DECLARE rel text;BEGIN
  FOREACH rel IN ARRAY ARRAY['planning_events','planning_attempt_history','planning_source_receipts'] LOOP
    EXECUTE format('CREATE TRIGGER immutable_fact BEFORE UPDATE OR DELETE OR TRUNCATE ON d3.%I FOR EACH STATEMENT EXECUTE FUNCTION public.d2_reject_fact_mutation()',rel);
  END LOOP;
END $$;
CREATE FUNCTION d3.coordinator_lock() RETURNS void LANGUAGE plpgsql AS $$
BEGIN PERFORM pg_advisory_xact_lock(742001);PERFORM pg_advisory_xact_lock(742002);END $$;
CREATE FUNCTION d3.enqueue_internal(eid uuid,kind text,occurred timestamptz,content jsonb) RETURNS uuid LANGUAGE plpgsql AS $$
DECLARE old d3.planning_events;r d3.planning_requests;received timestamptz;due timestamptz;urgent boolean;breaks boolean;
BEGIN
  SELECT * INTO old FROM d3.planning_events WHERE id=eid;
  IF FOUND THEN
    IF old.kind IS DISTINCT FROM kind OR old.occurred_at IS DISTINCT FROM occurred OR old.content IS DISTINCT FROM content THEN
      RAISE EXCEPTION 'Event content conflict' USING ERRCODE='23505';END IF;
    RETURN old.request_id;
  END IF;
  received=clock_timestamp();
  IF eid IS NULL OR kind IS NULL OR occurred IS NULL OR occurred>received OR content IS NULL THEN RAISE EXCEPTION 'Explicit nonfuture event required' USING ERRCODE='23514';END IF;
  urgent=kind IN ('INCIDENT_CRITICAL','DEPENDENCY_INVALIDATED','CAPACITY_DEFICIT','WORKER_LOST','APPROVAL_INVALID');
  breaks=urgent OR kind='PRIORITY_CHANGED';due=received+CASE WHEN urgent OR kind='SWEEP' THEN interval '0 seconds' ELSE interval '30 seconds' END;
  SELECT * INTO r FROM d3.planning_requests WHERE state IN ('QUEUED','RUNNING');
  IF r.id IS NULL THEN
    INSERT INTO d3.planning_requests(state,first_received_at,due_at,break_protection) VALUES('QUEUED',received,due,breaks) RETURNING * INTO r;
  ELSE
    UPDATE d3.planning_requests SET due_at=least(due_at,due),break_protection=break_protection OR breaks WHERE id=r.id;
  END IF;
  INSERT INTO d3.planning_events VALUES(eid,r.id,kind,occurred,received,content);
  UPDATE d3.planning_requests SET revision=revision+1 WHERE id=r.id;
  RETURN r.id;
END $$;
CREATE FUNCTION d3.enqueue_planning(cid uuid,req jsonb) RETURNS jsonb LANGUAGE plpgsql SECURITY DEFINER
SET search_path=pg_catalog,public,d2,d3 SET TimeZone='UTC' AS $$
DECLARE prior jsonb;result jsonb;
BEGIN
  IF req->>'action' IS DISTINCT FROM 'ENQUEUE' OR req->>'kind'='SWEEP' THEN RAISE EXCEPTION 'Explicit external planning event required' USING ERRCODE='23514';END IF;
  PERFORM d3.coordinator_lock();prior=d3.previous_command(cid,req);IF prior IS NOT NULL THEN RETURN prior;END IF;
  result=jsonb_build_object('request_id',d3.enqueue_internal((req->>'event_id')::uuid,req->>'kind',(req->>'occurred_at')::timestamptz,req->'content'));
  -- Observe at receipt, rather than inventing eligibility back to occurred_at.
  PERFORM d3.observe_eligibility(public.gen_random_uuid());
  INSERT INTO d3.commands(id,request,response) VALUES(cid,req,result);RETURN result;
END $$;
CREATE FUNCTION d3.planning_event_kind(e public.outbox_events) RETURNS text LANGUAGE sql STABLE AS $$
  SELECT CASE
    WHEN e.event_type='REPLAN_REQUIRED' AND e.aggregate_type='INCIDENT' AND e.payload->>'severity' IN ('SEV1','SEV2') THEN 'INCIDENT_CRITICAL'
    WHEN e.event_type='DEPENDENCY_INVALIDATED' OR (e.event_type='STATE_CHANGED' AND e.aggregate_type='CAPABILITY_VERSION' AND e.payload->>'to'='INVALIDATED') THEN 'DEPENDENCY_INVALIDATED'
    WHEN e.event_type='STATE_CHANGED' AND e.aggregate_type='OPERATION' AND e.payload->>'to'='RECONCILING' THEN 'WORKER_LOST'
    WHEN e.event_type='STATE_CHANGED' AND e.aggregate_type='OPERATION' AND e.payload->>'to'='BLOCKED_APPROVAL' THEN 'APPROVAL_INVALID'
    WHEN e.event_type IN ('RECALIBRATED','CONSUME','ADJUST','BORROW','RETURN','RESERVE','TOP_UP','RELEASE')
      AND EXISTS(SELECT 1 FROM d2.balances b WHERE b.available<0 AND
        (b.account_id=e.aggregate_id OR EXISTS(SELECT 1 FROM d2.reservation_balances rb WHERE rb.account_id=b.account_id AND rb.reservation_id::text=e.payload->>'reservation_id')
          OR EXISTS(SELECT 1 FROM d2.loans l WHERE l.account_id=b.account_id AND l.id::text=e.payload->>'loan_id'))) THEN 'CAPACITY_DEFICIT'
    WHEN e.event_type IN ('RECALIBRATED','RESERVE','TOP_UP','RELEASE','CONSUME','ADJUST','BORROW','RETURN') THEN 'CAPACITY_CHANGED'
    WHEN e.event_type='STATE_CHANGED' AND e.aggregate_type IN ('TASK','CAPABILITY_VERSION') THEN 'DEPENDENCY_CHANGED'
    WHEN e.event_type='STATE_CHANGED' AND e.aggregate_type='INCIDENT' THEN 'INCIDENT_CHANGED'
    WHEN e.event_type IN ('STATE_CHANGED','D3_REPLAN_REQUESTED','PREEMPTION_RESULT') THEN 'ORDINARY'
    ELSE NULL END;
$$;
CREATE FUNCTION d3.poll_planning(cid uuid) RETURNS jsonb LANGUAGE plpgsql SECURITY DEFINER
SET search_path=pg_catalog,public,d2,d3 SET TimeZone='UTC' AS $$
DECLARE req jsonb='{"action":"POLL_PLANNING"}';prior jsonb;result jsonb;e public.outbox_events;kind text;
  n integer=0;accepted integer=0;observed timestamptz;last_sweep timestamptz;swept boolean=false;
BEGIN
  PERFORM d3.coordinator_lock();prior=d3.previous_command(cid,req);IF prior IS NOT NULL THEN RETURN prior;END IF;
  -- Per-consumer receipts: never steal the global D2 delivery acknowledgement.
  -- Critical known events first; bounded intake, no timestamp/high-ID watermark.
  FOR e IN SELECT o.* FROM public.outbox_events o WHERE NOT EXISTS(SELECT 1 FROM d3.planning_source_receipts r WHERE r.outbox_id=o.id)
    ORDER BY CASE WHEN d3.planning_event_kind(o) IN ('INCIDENT_CRITICAL','DEPENDENCY_INVALIDATED','CAPACITY_DEFICIT','WORKER_LOST','APPROVAL_INVALID') THEN 0 ELSE 1 END,o.created_at,o.id LIMIT 100 LOOP
    kind=d3.planning_event_kind(e);
    IF kind IS NOT NULL THEN
      PERFORM d3.enqueue_internal(e.id,kind,least(e.created_at,clock_timestamp()),to_jsonb(e)-'delivered_at'-'attempt_count');accepted=accepted+1;
    END IF;
    INSERT INTO d3.planning_source_receipts(outbox_id,content_sha256,disposition,event_id)
      VALUES(e.id,encode(public.digest((to_jsonb(e)-'delivered_at'-'attempt_count')::text,'sha256'),'hex'),CASE WHEN kind IS NULL THEN 'IGNORED' ELSE 'ACCEPTED' END,CASE WHEN kind IS NULL THEN NULL ELSE e.id END);
    n=n+1;
  END LOOP;
  observed=clock_timestamp();SELECT last_sweep_at INTO last_sweep FROM d3.planning_clock WHERE singleton;
  IF last_sweep IS NULL OR observed>=last_sweep+interval '60 seconds' THEN
    PERFORM d3.enqueue_internal(public.gen_random_uuid(),'SWEEP',observed,jsonb_build_object('action','SWEEP'));
    UPDATE d3.planning_clock SET last_sweep_at=observed WHERE singleton;swept=true;
  END IF;
  IF accepted>0 OR swept THEN PERFORM d3.observe_eligibility(public.gen_random_uuid());END IF;
  result=jsonb_build_object('received',n,'accepted',accepted,'swept',swept,
    'backlog',EXISTS(SELECT 1 FROM public.outbox_events o WHERE NOT EXISTS(SELECT 1 FROM d3.planning_source_receipts r WHERE r.outbox_id=o.id)));
  INSERT INTO d3.commands(id,request,response) VALUES(cid,req,result);RETURN result;
END $$;
CREATE FUNCTION d3.require_planning_lease(req jsonb,allow_terminal boolean DEFAULT false) RETURNS d3.planning_requests LANGUAGE plpgsql AS $$
DECLARE r d3.planning_requests;
BEGIN
  SELECT * INTO STRICT r FROM d3.planning_requests WHERE id=(req->>'request_id')::uuid;
  IF r.worker_id IS DISTINCT FROM (req->>'worker_id')::uuid OR r.generation IS DISTINCT FROM (req->>'generation')::bigint
    OR NOT((r.state='RUNNING' AND r.lease_until>clock_timestamp()) OR (allow_terminal AND r.state IN ('PUBLISHED','STALE','BLOCKED'))) THEN
    RAISE EXCEPTION 'Planning lease fenced, expired or terminal' USING ERRCODE='55000';END IF;
  RETURN r;
END $$;
CREATE FUNCTION d3.take_planning(cid uuid,req jsonb) RETURNS jsonb LANGUAGE plpgsql SECURITY DEFINER
SET search_path=pg_catalog,public,d2,d3 SET TimeZone='UTC' AS $$
DECLARE prior jsonb;r d3.planning_requests;result jsonb;
BEGIN
  IF req->>'action' IS DISTINCT FROM 'TAKE' OR (req->>'worker_id')::uuid IS NULL THEN RAISE EXCEPTION 'Planning worker identity required' USING ERRCODE='23514';END IF;
  PERFORM d3.coordinator_lock();prior=d3.previous_command(cid,req);IF prior IS NOT NULL THEN RETURN prior;END IF;
  SELECT * INTO r FROM d3.planning_requests WHERE (state='QUEUED' AND due_at<=clock_timestamp()) OR (state='RUNNING' AND lease_until<=clock_timestamp());
  IF r.id IS NOT NULL THEN
    UPDATE d3.planning_requests SET state='RUNNING',worker_id=(req->>'worker_id')::uuid,generation=generation+1,lease_until=clock_timestamp()+interval '60 seconds' WHERE id=r.id RETURNING * INTO r;
    INSERT INTO d3.planning_attempt_history(request_id,attempt_no,action,generation,detail) VALUES(r.id,r.recalculations,'TAKEN',r.generation,'{}');
    result=jsonb_build_object('request_id',r.id,'worker_id',r.worker_id,'generation',r.generation);
  ELSE result='{}';END IF;
  INSERT INTO d3.commands(id,request,response) VALUES(cid,req,result);RETURN result;
END $$;
CREATE FUNCTION d3.prepare_planning(req jsonb) RETURNS jsonb LANGUAGE plpgsql SECURITY DEFINER
SET search_path=pg_catalog,public,d2,d3 SET TimeZone='UTC' AS $$
DECLARE r d3.planning_requests;a d3.planning_attempts;capture uuid;
BEGIN
  PERFORM d3.coordinator_lock();r=d3.require_planning_lease(req,true);
  SELECT * INTO a FROM d3.planning_attempts WHERE request_id=r.id AND attempt_no=r.recalculations;
  IF a.request_id IS NULL THEN
    IF r.state<>'RUNNING' THEN RAISE EXCEPTION 'Missing confirmed planning attempt' USING ERRCODE='55000';END IF;
    PERFORM d3.observe_eligibility(public.gen_random_uuid());capture=public.gen_random_uuid();
    PERFORM d3.capture(capture,'{"action":"CAPTURE"}');
    INSERT INTO d3.planning_attempts VALUES(r.id,r.recalculations,r.revision,r.break_protection,capture,public.gen_random_uuid(),public.gen_random_uuid(),'PREPARED',NULL) RETURNING * INTO a;
    INSERT INTO d3.planning_attempt_history(request_id,attempt_no,action,generation,detail) VALUES(r.id,a.attempt_no,'PREPARED',r.generation,jsonb_build_object('revision',a.revision));
  END IF;
  RETURN to_jsonb(a)||jsonb_build_object('request_state',r.state,'worker_id',r.worker_id,'generation',r.generation);
END $$;
CREATE FUNCTION d3.publish_planning(req jsonb) RETURNS jsonb LANGUAGE plpgsql SECURITY DEFINER
SET search_path=pg_catalog,public,d2,d3 SET TimeZone='UTC' AS $$
DECLARE r d3.planning_requests;a d3.planning_attempts;result jsonb;
BEGIN
  IF current_setting('transaction_isolation')<>'read committed' THEN RAISE EXCEPTION 'Coordinator publication requires READ COMMITTED' USING ERRCODE='25001';END IF;
  PERFORM d3.coordinator_lock();r=d3.require_planning_lease(req,true);
  SELECT * INTO STRICT a FROM d3.planning_attempts WHERE request_id=r.id AND attempt_no=(req->>'attempt_no')::integer;
  IF a.attempt_no<>r.recalculations THEN RAISE EXCEPTION 'Planning attempt superseded' USING ERRCODE='55000';END IF;
  IF r.state='PUBLISHED' THEN
    -- Delegate replay payload equality to the immutable publication command.
    RETURN d3.publish(a.publish_command_id,jsonb_build_object('action','PUBLISH','plan_id',a.plan_id,'capture_id',a.capture_id,
      'expected_current_plan_id',(SELECT (body->'d3.plan_head'->0->>'planning_run_id')::uuid FROM d3.captures WHERE id=a.capture_id),'result',req->'result'));
  END IF;
  IF r.state<>'RUNNING' THEN RAISE EXCEPTION 'Terminal planning request cannot publish' USING ERRCODE='55000';END IF;
  IF a.revision<>r.revision THEN RAISE EXCEPTION 'New planning events arrived during calculation' USING ERRCODE='40001';END IF;
  result=d3.publish(a.publish_command_id,jsonb_build_object('action','PUBLISH','plan_id',a.plan_id,'capture_id',a.capture_id,
    'expected_current_plan_id',(SELECT (body->'d3.plan_head'->0->>'planning_run_id')::uuid FROM d3.captures WHERE id=a.capture_id),'result',req->'result'));
  -- The computation lease must still be valid at final confirmation.
  PERFORM d3.require_planning_lease(req);
  UPDATE d3.planning_attempts SET state='PUBLISHED' WHERE request_id=r.id AND attempt_no=a.attempt_no;
  UPDATE d3.planning_requests SET state='PUBLISHED',published_plan_id=a.plan_id,lease_until=NULL WHERE id=r.id;
  INSERT INTO d3.planning_attempt_history(request_id,attempt_no,action,generation,detail) VALUES(r.id,a.attempt_no,'PUBLISHED',r.generation,result);
  RETURN result;
END $$;
CREATE FUNCTION d3.fail_planning(req jsonb) RETURNS jsonb LANGUAGE plpgsql SECURITY DEFINER
SET search_path=pg_catalog,public,d2,d3 SET TimeZone='UTC' AS $$
DECLARE r d3.planning_requests;a d3.planning_attempts;code text=req->>'failure_code';next_state text;
BEGIN
  PERFORM d3.coordinator_lock();r=d3.require_planning_lease(req);
  SELECT * INTO STRICT a FROM d3.planning_attempts WHERE request_id=r.id AND attempt_no=(req->>'attempt_no')::integer;
  IF a.attempt_no<>r.recalculations OR a.state<>'PREPARED' OR code IS NULL OR code !~ '^[A-Z0-9_]{1,32}$' THEN RAISE EXCEPTION 'Failure identity/code invalid' USING ERRCODE='55000';END IF;
  next_state=CASE WHEN code='40001' THEN 'STALE' ELSE 'BLOCKED' END;
  UPDATE d3.planning_attempts SET state=next_state,failure_code=code WHERE request_id=r.id AND attempt_no=a.attempt_no;
  INSERT INTO d3.planning_attempt_history(request_id,attempt_no,action,generation,detail) VALUES(r.id,a.attempt_no,next_state,r.generation,jsonb_build_object('failure_code',code));
  IF code='40001' AND r.recalculations<2 THEN
    UPDATE d3.planning_requests SET recalculations=recalculations+1,lease_until=clock_timestamp()+interval '60 seconds' WHERE id=r.id;
    RETURN jsonb_build_object('state','RETRY','recalculations',r.recalculations+1);
  END IF;
  UPDATE d3.planning_requests SET state=next_state,failure_code=code,lease_until=NULL WHERE id=r.id;
  RETURN jsonb_build_object('state',next_state,'recalculations',r.recalculations);
END $$;
CREATE FUNCTION d3.read_planning_request(rid uuid) RETURNS jsonb LANGUAGE sql STABLE SECURITY DEFINER
SET search_path=pg_catalog,public,d2,d3 SET TimeZone='UTC' AS $$
  SELECT to_jsonb(r)||jsonb_build_object('events',(SELECT coalesce(jsonb_agg(to_jsonb(e) ORDER BY received_at,id),'[]') FROM d3.planning_events e WHERE e.request_id=r.id),
    'attempts',(SELECT coalesce(jsonb_agg(to_jsonb(a) ORDER BY attempt_no),'[]') FROM d3.planning_attempts a WHERE a.request_id=r.id),
    'history',(SELECT coalesce(jsonb_agg(to_jsonb(h) ORDER BY id),'[]') FROM d3.planning_attempt_history h WHERE h.request_id=r.id))
  FROM d3.planning_requests r WHERE r.id=rid;
$$;
REVOKE ALL ON ALL TABLES IN SCHEMA d3 FROM PUBLIC;
REVOKE ALL ON ALL FUNCTIONS IN SCHEMA d3 FROM PUBLIC;
