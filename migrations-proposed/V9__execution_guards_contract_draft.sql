-- D2 guarded persistence kernel, not a worker/scheduler implementation.
INSERT INTO public.state_transition_rules VALUES('OPERATION','BLOCKED_APPROVAL','RECONCILING','NEW_RECONCILIATION_EVIDENCE');
CREATE TABLE d2.capability_epochs(version_id uuid PRIMARY KEY REFERENCES public.capability_versions(id),epoch bigint NOT NULL DEFAULT 0 CHECK(epoch>=0));
CREATE TABLE d2.verifications(
 id uuid PRIMARY KEY DEFAULT public.gen_random_uuid(),version_id uuid NOT NULL REFERENCES public.capability_versions(id),
 epoch bigint NOT NULL,environment text NOT NULL,contract_sha256 char(64) NOT NULL,evidence_sha256 char(64) NOT NULL,
 outcome text NOT NULL CHECK(outcome IN ('PASS','FAIL')),verified_at timestamptz NOT NULL DEFAULT clock_timestamp()
);
CREATE TABLE d2.resolutions(requirement_id uuid PRIMARY KEY REFERENCES public.capability_requirements(id),version_id uuid NOT NULL REFERENCES public.capability_versions(id));
CREATE TABLE d2.capability_producers(version_id uuid NOT NULL REFERENCES public.capability_versions(id),task_id uuid NOT NULL REFERENCES public.tasks(id),PRIMARY KEY(version_id,task_id));
CREATE TABLE d2.transition_receipts(
 command_id uuid PRIMARY KEY,entity_type text NOT NULL,entity_id uuid NOT NULL,row_version bigint NOT NULL,
 UNIQUE(entity_type,entity_id,row_version)
);
CREATE TABLE d2.effect_receipts(
 id uuid PRIMARY KEY DEFAULT public.gen_random_uuid(),operation_id uuid NOT NULL REFERENCES public.operations(id),generation bigint NOT NULL,
 effect_key text NOT NULL,status text NOT NULL CHECK(status IN ('APPLIED','ABSENT','UNKNOWN')),evidence_ref text NOT NULL,
 UNIQUE(operation_id,generation,effect_key,status)
);
DO $$ DECLARE rel text; BEGIN
 FOREACH rel IN ARRAY ARRAY['verifications','transition_receipts','effect_receipts'] LOOP
  EXECUTE format('CREATE TRIGGER immutable_fact BEFORE UPDATE OR DELETE OR TRUNCATE ON d2.%I FOR EACH STATEMENT EXECUTE FUNCTION public.d2_reject_fact_mutation()',rel);
 END LOOP;
END $$;
CREATE FUNCTION d2.compatible(version text,constraint_text text) RETURNS boolean LANGUAGE plpgsql IMMUTABLE AS $$
DECLARE v int[];c int[];cstr text;
BEGIN
 -- Intentionally bounded grammar; unsupported ranges are rejected, never guessed.
 IF version !~ '^[0-9]+\.[0-9]+\.[0-9]+$' THEN RETURN false; END IF;
 v=string_to_array(version,'.')::int[];
 IF constraint_text ~ '^=?[0-9]+\.[0-9]+\.[0-9]+$' THEN RETURN version=ltrim(constraint_text,'='); END IF;
 IF constraint_text ~ '^[0-9]+\.x$' THEN RETURN v[1]=split_part(constraint_text,'.',1)::int; END IF;
 IF constraint_text !~ '^[\^~][0-9]+\.[0-9]+\.[0-9]+$' THEN RETURN false; END IF;
 cstr=substr(constraint_text,2);c=string_to_array(cstr,'.')::int[];
 IF v<c THEN RETURN false; END IF;
 IF left(constraint_text,1)='~' THEN RETURN v[1]=c[1] AND v[2]=c[2]; END IF;
 IF c[1]>0 THEN RETURN v[1]=c[1]; END IF;
 IF c[2]>0 THEN RETURN v[1]=0 AND v[2]=c[2]; END IF;
 RETURN v=c;
END $$;
CREATE FUNCTION d2.capability_ready(vid uuid) RETURNS boolean LANGUAGE sql STABLE AS $$
 SELECT EXISTS(SELECT 1 FROM public.capability_versions v JOIN d2.capability_epochs e ON e.version_id=v.id
 WHERE v.id=vid AND v.state='AVAILABLE' AND EXISTS(SELECT 1 FROM d2.verifications x WHERE x.version_id=v.id AND x.epoch=e.epoch AND x.environment=v.environment AND x.contract_sha256=v.contract_sha256 AND x.outcome='PASS'));
$$;
CREATE FUNCTION d2.task_eligible(tid uuid) RETURNS boolean LANGUAGE sql STABLE AS $$
 SELECT NOT EXISTS(SELECT 1 FROM public.task_dependencies d JOIN public.tasks t ON t.id=d.predecessor_task_id WHERE d.successor_task_id=tid AND d.kind='HARD' AND t.status<>'DONE')
 AND NOT EXISTS(SELECT 1 FROM public.capability_requirements r LEFT JOIN d2.resolutions x ON x.requirement_id=r.id LEFT JOIN public.capability_versions v ON v.id=x.version_id
 WHERE r.consumer_task_id=tid AND r.kind='HARD' AND (x.version_id IS NULL OR v.capability_id<>r.capability_id OR v.environment<>r.environment OR NOT d2.compatible(v.version,r.version_constraint) OR NOT d2.capability_ready(v.id)));
$$;
CREATE FUNCTION d2.integration_eligible(tid uuid) RETURNS boolean LANGUAGE sql STABLE AS $$
 SELECT d2.task_eligible(tid) AND NOT EXISTS(SELECT 1 FROM public.capability_requirements r LEFT JOIN d2.resolutions x ON x.requirement_id=r.id LEFT JOIN public.capability_versions v ON v.id=x.version_id WHERE r.consumer_task_id=tid AND r.kind='MOCKABLE' AND (x.version_id IS NULL OR v.capability_id<>r.capability_id OR v.environment<>r.environment OR NOT d2.compatible(v.version,r.version_constraint) OR NOT d2.capability_ready(v.id)));
$$;
CREATE VIEW d2.blocking_edges AS
 SELECT predecessor_task_id::text a,successor_task_id::text b FROM public.task_dependencies WHERE kind='HARD'
 UNION ALL SELECT p.task_id::text,'cap:'||p.version_id FROM d2.capability_producers p
 UNION ALL SELECT 'cap:'||x.version_id,r.consumer_task_id::text FROM public.capability_requirements r JOIN d2.resolutions x ON x.requirement_id=r.id WHERE r.kind='HARD';
CREATE FUNCTION d2.graph_guard() RETURNS trigger LANGUAGE plpgsql AS $$
DECLARE cyclic boolean;
BEGIN
 PERFORM pg_advisory_xact_lock(742002);
 WITH RECURSIVE reach(a,b) AS(SELECT a,b FROM d2.blocking_edges UNION SELECT r.a,e.b FROM reach r JOIN d2.blocking_edges e ON r.b=e.a)
 SELECT EXISTS(SELECT 1 FROM reach WHERE a=b) INTO cyclic;
 IF cyclic THEN RAISE EXCEPTION 'HARD task/capability cycle' USING ERRCODE='23514'; END IF;
 WITH RECURSIVE reach(a,b) AS(SELECT provider_project_id,consumer_project_id FROM public.project_dependencies WHERE kind='HARD' UNION SELECT r.a,e.consumer_project_id FROM reach r JOIN public.project_dependencies e ON r.b=e.provider_project_id AND e.kind='HARD')
 SELECT EXISTS(SELECT 1 FROM reach WHERE a=b) INTO cyclic;
 IF cyclic THEN RAISE EXCEPTION 'Project dependency cycle' USING ERRCODE='23514'; END IF;
 RETURN NULL;
END $$;
CREATE FUNCTION d2.graph_lock() RETURNS trigger LANGUAGE plpgsql AS $$ BEGIN PERFORM pg_advisory_xact_lock(742002); RETURN NULL; END $$;
DO $$ DECLARE rel text; BEGIN
 FOREACH rel IN ARRAY ARRAY['public.task_dependencies','public.project_dependencies','public.capability_requirements','d2.resolutions','d2.capability_producers'] LOOP
  EXECUTE format('CREATE TRIGGER graph_lock BEFORE INSERT OR UPDATE OR DELETE ON %s FOR EACH STATEMENT EXECUTE FUNCTION d2.graph_lock()',rel);
  EXECUTE format('CREATE TRIGGER graph_guard AFTER INSERT OR UPDATE OR DELETE ON %s FOR EACH STATEMENT EXECUTE FUNCTION d2.graph_guard()',rel);
 END LOOP;
END $$;
CREATE FUNCTION d2.record_transition(cid uuid,kind text,eid uuid,old_state text,new_state text,version bigint,actor text,reason text) RETURNS void LANGUAGE plpgsql AS $$
BEGIN
 IF NOT EXISTS(SELECT 1 FROM public.state_transition_rules WHERE entity_type=kind AND from_state=old_state AND to_state=new_state) THEN RAISE EXCEPTION 'Illegal transition' USING ERRCODE='23514'; END IF;
 INSERT INTO d2.transition_receipts VALUES(cid,kind,eid,version);
 INSERT INTO public.state_transition_events(entity_type,entity_id,from_state,to_state,actor,reason) VALUES(kind,eid,old_state,new_state,actor,reason);
 INSERT INTO public.outbox_events(aggregate_type,aggregate_id,event_type,payload) VALUES(kind,eid,'STATE_CHANGED',jsonb_build_object('command_id',cid,'row_version',version,'from',old_state,'to',new_state));
END $$;
CREATE FUNCTION d2.transition(cid uuid,req jsonb) RETURNS jsonb
LANGUAGE plpgsql SECURITY DEFINER SET search_path=pg_catalog,public,d2 AS $$
DECLARE prior jsonb;result jsonb;kind text=req->>'entity_type'; eid uuid=(req->>'entity_id')::uuid;
 rel text;col text;current_state text;ver bigint;target text=req->>'to';cap public.capability_versions;epoch_value bigint;oid uuid; impacted record;
BEGIN
 prior=d2.begin_command(cid,req);IF prior IS NOT NULL THEN RETURN prior; END IF;
 IF req->>'actor' IS NULL OR length(btrim(req->>'reason'))=0 OR req->>'reason' IS NULL THEN RAISE EXCEPTION 'Actor/reason required' USING ERRCODE='23514'; END IF;
 rel=CASE kind WHEN 'TASK' THEN 'tasks' WHEN 'OPERATION' THEN 'operations' WHEN 'INCIDENT' THEN 'incidents' WHEN 'CAPABILITY_VERSION' THEN 'capability_versions' END;
 col=CASE WHEN kind IN ('TASK','INCIDENT') THEN 'status' ELSE 'state' END;
 IF rel IS NULL THEN RAISE EXCEPTION 'Unknown aggregate' USING ERRCODE='23514'; END IF;
 EXECUTE format('SELECT %I,row_version FROM public.%I WHERE id=$1 FOR UPDATE',col,rel) INTO STRICT current_state,ver USING eid;
 IF current_state IS DISTINCT FROM req->>'from' OR ver IS DISTINCT FROM (req->>'expected_version')::bigint THEN RAISE EXCEPTION 'State/version conflict' USING ERRCODE='40001'; END IF;
 IF kind='TASK' AND target IN ('READY','IN_PROGRESS','DONE') AND NOT d2.task_eligible(eid) THEN RAISE EXCEPTION 'Unsatisfied hard dependency' USING ERRCODE='23514'; END IF;
 IF kind='TASK' AND target='DONE' AND (NOT EXISTS(SELECT 1 FROM public.operations WHERE task_id=eid) OR EXISTS(SELECT 1 FROM public.operations WHERE task_id=eid AND state<>'COMPLETED')) THEN RAISE EXCEPTION 'All task operations must pass acceptance' USING ERRCODE='23514'; END IF;
 IF kind='TASK' AND target='DONE' AND NOT d2.integration_eligible(eid) THEN RAISE EXCEPTION 'Real integration verification required' USING ERRCODE='23514'; END IF;
 IF kind='OPERATION' AND NOT ((current_state='READY' AND target IN ('WAITING_CAPACITY','BLOCKED_APPROVAL')) OR (current_state IN ('WAITING_CAPACITY','BLOCKED_APPROVAL','RETRY_PENDING') AND target='READY')) THEN RAISE EXCEPTION 'Use fenced execution commands' USING ERRCODE='23514'; END IF;
 IF kind='OPERATION' AND target='CANCELLED' THEN RAISE EXCEPTION 'Use reconciliation before cancellation' USING ERRCODE='23514'; END IF;
 IF kind='CAPABILITY_VERSION' THEN
  SELECT * INTO STRICT cap FROM public.capability_versions WHERE id=eid;
  INSERT INTO d2.capability_epochs(version_id) VALUES(eid) ON CONFLICT DO NOTHING;
  SELECT epoch INTO epoch_value FROM d2.capability_epochs WHERE version_id=eid;
  IF target IN ('VERIFIED','AVAILABLE') AND NOT EXISTS(SELECT 1 FROM d2.verifications x WHERE x.version_id=eid AND x.epoch=epoch_value AND x.environment=cap.environment AND x.contract_sha256=cap.contract_sha256 AND x.outcome='PASS') THEN RAISE EXCEPTION 'Fresh exact verification required' USING ERRCODE='23514'; END IF;
  IF target='INVALIDATED' THEN
   UPDATE d2.capability_epochs SET epoch=epoch+1 WHERE version_id=eid;
   -- Block future admission immediately; active work must be reconciled, not
   -- silently cancelled. Atomic invalidation event drives replan/worker handling.
   FOR impacted IN SELECT o.id,o.state,o.row_version FROM public.operations o JOIN public.capability_requirements r ON r.consumer_task_id=o.task_id JOIN d2.resolutions x ON x.requirement_id=r.id WHERE x.version_id=eid AND r.kind='HARD' AND o.state IN ('LEASED','RUNNING','VERIFYING') ORDER BY o.id LOOP
    oid=impacted.id;
    PERFORM d2.record_transition(public.gen_random_uuid(),'OPERATION',oid,impacted.state,'RECONCILING',impacted.row_version+1,'CONTROL_PLANE','Capability invalidation');
    UPDATE public.operations SET state='RECONCILING',row_version=row_version+1 WHERE id=oid;
    UPDATE public.execution_attempts SET state='RECONCILING' WHERE id=(SELECT attempt_id FROM public.operation_leases WHERE operation_id=oid);
    INSERT INTO public.outbox_events(aggregate_type,aggregate_id,event_type,payload) VALUES('OPERATION',oid,'DEPENDENCY_INVALIDATED',jsonb_build_object('version_id',eid,'requires_reconciliation',true));
   END LOOP;
  END IF;
 END IF;
 PERFORM d2.record_transition(cid,kind,eid,current_state,target,ver+1,req->>'actor',req->>'reason');
 IF kind='INCIDENT' THEN
  UPDATE public.incidents SET status=target,resolved_at=CASE WHEN target='RESOLVED' THEN clock_timestamp() ELSE NULL END,row_version=ver+1 WHERE id=eid;
 ELSE EXECUTE format('UPDATE public.%I SET %I=$1,row_version=$2 WHERE id=$3',rel,col) USING target,ver+1,eid; END IF;
 result=jsonb_build_object('entity_id',eid,'row_version',ver+1,'state',target);
 INSERT INTO d2.commands VALUES(cid,req,result,clock_timestamp());RETURN result;
END $$;
CREATE TABLE d2.execution_snapshots(
 attempt_id uuid PRIMARY KEY REFERENCES public.execution_attempts(id),context_sha256 char(64) NOT NULL,context_ref text NOT NULL,
 policy_snapshot jsonb NOT NULL,policy_sha256 char(64) NOT NULL,
 CHECK(context_sha256~'^[a-f0-9]{64}$' AND policy_sha256~'^[a-f0-9]{64}$')
);
CREATE TRIGGER immutable_provenance BEFORE UPDATE OR DELETE OR TRUNCATE ON d2.execution_snapshots FOR EACH STATEMENT EXECUTE FUNCTION public.d2_reject_fact_mutation();
CREATE FUNCTION d2.capture_attempt_snapshot() RETURNS trigger LANGUAGE plpgsql AS $$
DECLARE op public.operations;
BEGIN
 SELECT * INTO STRICT op FROM public.operations WHERE id=NEW.operation_id;
 IF op.context_pack_sha256 IS NULL OR op.context_pack_ref IS NULL THEN RAISE EXCEPTION 'Versioned Context Pack required' USING ERRCODE='23514'; END IF;
 INSERT INTO d2.execution_snapshots VALUES(NEW.id,op.context_pack_sha256,op.context_pack_ref,op.policy_snapshot,encode(public.digest(op.policy_snapshot::text,'sha256'),'hex'));
 RETURN NEW;
END $$;
CREATE TRIGGER capture_attempt_snapshot AFTER INSERT ON public.execution_attempts FOR EACH ROW EXECUTE FUNCTION d2.capture_attempt_snapshot();
CREATE FUNCTION d2.execution(cid uuid,req jsonb) RETURNS jsonb
LANGUAGE plpgsql SECURITY DEFINER SET search_path=pg_catalog,public,d2 AS $$
DECLARE prior jsonb;result jsonb;op public.operations;attempt public.execution_attempts;lease public.operation_leases;
 action text=req->>'action';wid uuid=(req->>'worker_id')::uuid;rid uuid=(req->>'resource_id')::uuid;aid uuid;gen bigint;old_state text;new_state text;
 cap_result jsonb;resid uuid;rec d2.effect_receipts;expiry timestamptz;policy_hash text; approval_ok boolean;
BEGIN
 prior=d2.begin_command(cid,req);IF prior IS NOT NULL THEN RETURN prior;END IF;
 SELECT * INTO op FROM public.operations WHERE id=(req->>'operation_id')::uuid FOR UPDATE SKIP LOCKED;
 IF NOT FOUND THEN RAISE EXCEPTION 'Operation unavailable or locked' USING ERRCODE='23514'; END IF;
 old_state=op.state;
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
-- API exposure remains explicitly revoked until deployment chooses restricted roles.
REVOKE ALL ON ALL TABLES IN SCHEMA d2 FROM PUBLIC;
REVOKE ALL ON ALL FUNCTIONS IN SCHEMA d2 FROM PUBLIC;

CREATE FUNCTION d2.capacity_command(cid uuid,req jsonb) RETURNS jsonb
LANGUAGE plpgsql SECURITY DEFINER SET search_path=pg_catalog,public,d2 AS $$
BEGIN
 IF req->>'action' NOT IN ('RESERVE','RELEASE','BORROW','RETURN') OR req->>'action' IS NULL THEN RAISE EXCEPTION 'Accounting action requires reconciliation/admin entrypoint' USING ERRCODE='42501'; END IF;
 IF req->>'action'='RELEASE' AND EXISTS(SELECT 1 FROM d2.reservations r JOIN public.operations o ON o.id=r.operation_id WHERE r.id=(req->>'reservation_id')::uuid AND (o.state NOT IN ('READY','CANCELLED') OR EXISTS(SELECT 1 FROM public.operation_leases l WHERE l.operation_id=o.id))) THEN RAISE EXCEPTION 'Active commitments require verified reconciliation' USING ERRCODE='23514'; END IF;
 RETURN d2.capacity(cid,req);
END $$;
REVOKE ALL ON ALL FUNCTIONS IN SCHEMA d2 FROM PUBLIC;

CREATE TABLE d2.checkpoint_receipts(
 id uuid PRIMARY KEY DEFAULT public.gen_random_uuid(),operation_id uuid NOT NULL REFERENCES public.operations(id),generation bigint NOT NULL,
 process_stopped boolean NOT NULL,effects_resolved boolean NOT NULL,evidence_sha256 char(64) NOT NULL,
 recorded_at timestamptz NOT NULL DEFAULT clock_timestamp()
);
CREATE TRIGGER immutable_fact BEFORE UPDATE OR DELETE OR TRUNCATE ON d2.checkpoint_receipts FOR EACH STATEMENT EXECUTE FUNCTION public.d2_reject_fact_mutation();
CREATE UNIQUE INDEX one_applied_effect ON d2.effect_receipts(operation_id,effect_key) WHERE status='APPLIED';
CREATE FUNCTION d2.preempt(cid uuid,req jsonb) RETURNS jsonb
LANGUAGE plpgsql SECURITY DEFINER SET search_path=pg_catalog,public,d2 AS $$
DECLARE prior jsonb;result jsonb;op public.operations;proof d2.checkpoint_receipts;res uuid;entries jsonb;
BEGIN
 prior=d2.begin_command(cid,req);IF prior IS NOT NULL THEN RETURN prior;END IF;
 SELECT * INTO STRICT op FROM public.operations WHERE id=(req->>'operation_id')::uuid FOR UPDATE;
 IF op.state NOT IN ('LEASED','RUNNING') THEN RAISE EXCEPTION 'Active preemptible state required' USING ERRCODE='23514'; END IF;
 IF NOT coalesce((op.policy_snapshot->>'interruptible')::boolean,false) THEN
  result=jsonb_build_object('status','DEFERRED_NONINTERRUPTIBLE');
 ELSIF req->>'checkpoint_receipt_id' IS NULL THEN
  result=jsonb_build_object('status','CHECKPOINT_REQUESTED');
 ELSE
  SELECT * INTO STRICT proof FROM d2.checkpoint_receipts WHERE id=(req->>'checkpoint_receipt_id')::uuid;
  IF proof.operation_id<>op.id OR proof.generation<>op.lease_generation OR NOT proof.process_stopped OR NOT proof.effects_resolved THEN RAISE EXCEPTION 'Safe checkpoint proof required' USING ERRCODE='23514'; END IF;
  SELECT id INTO res FROM d2.reservations WHERE operation_id=op.id;
  SELECT jsonb_agg(jsonb_build_object('account_id',account_id,'settled',outstanding) ORDER BY account_id) INTO entries FROM d2.reservation_balances WHERE reservation_id=res;
  PERFORM d2.capacity(public.gen_random_uuid(),jsonb_build_object('action','RELEASE','reservation_id',res,'entries',entries,'reason','Verified checkpoint cancellation'));
  UPDATE public.execution_attempts SET state='CANCELLED',finished_at=clock_timestamp() WHERE id=(SELECT attempt_id FROM public.operation_leases WHERE operation_id=op.id);
  DELETE FROM public.operation_leases WHERE operation_id=op.id;
  UPDATE public.operations SET state='CANCELLED',row_version=row_version+1 WHERE id=op.id;
  PERFORM d2.record_transition(cid,'OPERATION',op.id,op.state,'CANCELLED',op.row_version+1,'CONTROL_PLANE','Verified checkpoint preemption');
  result=jsonb_build_object('status','CANCELLED_AT_CHECKPOINT');
 END IF;
 INSERT INTO d2.commands VALUES(cid,req,result,clock_timestamp());
 INSERT INTO public.outbox_events(aggregate_type,aggregate_id,event_type,payload) VALUES('OPERATION',op.id,'PREEMPTION_RESULT',result);
 RETURN result;
END $$;
CREATE FUNCTION d2.initial_state_guard() RETURNS trigger LANGUAGE plpgsql AS $$
DECLARE state_value text;expected text;
BEGIN
 state_value=coalesce(to_jsonb(NEW)->>'state',to_jsonb(NEW)->>'status');
 expected=CASE TG_TABLE_NAME WHEN 'tasks' THEN 'BACKLOG' WHEN 'operations' THEN 'READY' WHEN 'incidents' THEN 'OPEN' ELSE 'PLANNED' END;
 IF state_value<>expected OR NEW.row_version<>0 THEN RAISE EXCEPTION 'Initial state/version required' USING ERRCODE='23514'; END IF;
 RETURN NEW;
END $$;
DO $$ DECLARE rel text; BEGIN
 FOREACH rel IN ARRAY ARRAY['tasks','operations','incidents','capability_versions'] LOOP
  EXECUTE format('CREATE TRIGGER initial_state_guard BEFORE INSERT ON public.%I FOR EACH ROW EXECUTE FUNCTION d2.initial_state_guard()',rel);
 END LOOP;
END $$;
REVOKE ALL ON ALL FUNCTIONS IN SCHEMA d2 FROM PUBLIC;

CREATE VIEW d2.active_blocking_edges AS
 SELECT d.predecessor_task_id::text a,d.successor_task_id::text b FROM public.task_dependencies d JOIN public.tasks t ON t.id=d.predecessor_task_id WHERE d.kind='HARD' AND t.status<>'DONE'
 UNION ALL SELECT p.task_id::text,'cap:'||p.version_id FROM d2.capability_producers p WHERE NOT d2.capability_ready(p.version_id)
 UNION ALL SELECT 'cap:'||x.version_id,r.consumer_task_id::text FROM public.capability_requirements r JOIN d2.resolutions x ON x.requirement_id=r.id WHERE r.kind='HARD' AND NOT d2.capability_ready(x.version_id);
CREATE VIEW d2.effective_priorities AS
 WITH RECURSIVE base AS(SELECT t.id,t.status,coalesce(p.priority_weight_override,CASE p.priority WHEN 'P0' THEN 8 WHEN 'P1' THEN 4 WHEN 'P2' THEN 2 WHEN 'P3' THEN 1 ELSE 0 END) weight FROM public.tasks t JOIN public.projects p ON p.id=t.project_id),
 inherited(node,weight) AS(SELECT id::text,weight FROM base WHERE status NOT IN ('DONE','CANCELLED') UNION SELECT e.a,i.weight FROM d2.active_blocking_edges e JOIN inherited i ON i.node=e.b)
 SELECT b.id task_id,b.weight base_weight,greatest(b.weight,coalesce(max(i.weight),0)) effective_weight FROM base b LEFT JOIN inherited i ON i.node=b.id::text GROUP BY b.id,b.weight;
REVOKE ALL ON ALL TABLES IN SCHEMA d2 FROM PUBLIC;
REVOKE ALL ON ALL FUNCTIONS IN SCHEMA d2 FROM PUBLIC;

CREATE FUNCTION d2.incident_replan_event() RETURNS trigger LANGUAGE plpgsql AS $$
BEGIN
 IF TG_OP='INSERT' OR NEW.severity IS DISTINCT FROM OLD.severity THEN
  INSERT INTO public.audit_events(actor,entity_type,entity_id,action,payload) VALUES(current_user,'INCIDENT',NEW.id,'SEVERITY_OBSERVED',jsonb_build_object('severity',NEW.severity));
  IF NEW.severity IN ('SEV1','SEV2') AND NEW.status<>'RESOLVED' THEN
   INSERT INTO public.outbox_events(aggregate_type,aggregate_id,event_type,payload) VALUES('INCIDENT',NEW.id,'REPLAN_REQUIRED',jsonb_build_object('severity',NEW.severity,'safe_checkpoint_only',true));
  END IF;
 END IF;
 RETURN NEW;
END $$;
CREATE TRIGGER incident_replan AFTER INSERT OR UPDATE ON public.incidents FOR EACH ROW EXECUTE FUNCTION d2.incident_replan_event();
REVOKE ALL ON ALL FUNCTIONS IN SCHEMA d2 FROM PUBLIC;
