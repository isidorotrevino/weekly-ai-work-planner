-- D2 executable contract prototype. New accounts are NOT automatically populated
-- from legacy capacity_movements: legacy reconciliation requires explicit review.
CREATE EXTENSION IF NOT EXISTS btree_gist;
CREATE SCHEMA d2;
CREATE TABLE d2.accounts(
 id uuid PRIMARY KEY DEFAULT public.gen_random_uuid(), resource_id uuid NOT NULL REFERENCES public.resources(id),
 dimension text NOT NULL, unit text NOT NULL CHECK(unit IN ('CALIBRATED_QUOTA','SECONDS','TOKENS','OPERATIONS')),
 window_kind text NOT NULL, window_key text NOT NULL, window_start timestamptz NOT NULL, window_end timestamptz NOT NULL,
 provenance text NOT NULL, confidence numeric(4,3) CHECK(confidence BETWEEN 0 AND 1),
 initial_capacity numeric(18,4) CHECK(initial_capacity>=0 AND initial_capacity<1e14),
 UNIQUE(resource_id,dimension,window_kind,window_key), CHECK(window_end>window_start),
 CHECK(length(btrim(window_key))>0 AND length(btrim(dimension))>0), UNIQUE(id,resource_id)
);
ALTER TABLE d2.accounts ADD CONSTRAINT no_same_kind_overlap EXCLUDE USING gist(resource_id WITH =,dimension WITH =,window_kind WITH =,tstzrange(window_start,window_end,'[)') WITH &&);
CREATE TABLE d2.operation_accounts(
 operation_id uuid NOT NULL REFERENCES public.operations(id), account_id uuid NOT NULL REFERENCES d2.accounts(id),
 units numeric(18,4) NOT NULL CHECK(units>0 AND units<1e14), calibration_ref text NOT NULL CHECK(length(btrim(calibration_ref))>0),
 PRIMARY KEY(operation_id,account_id)
);
CREATE TABLE d2.reservations(
 id uuid PRIMARY KEY, operation_id uuid NOT NULL UNIQUE REFERENCES public.operations(id),
 resource_id uuid NOT NULL REFERENCES public.resources(id), pool text NOT NULL CHECK(pool IN ('PLANNED','INCIDENT')),
 created_at timestamptz NOT NULL DEFAULT clock_timestamp()
);
CREATE TABLE d2.plan_reservations(
 planning_run_id uuid NOT NULL REFERENCES public.planning_runs(id), reservation_id uuid NOT NULL REFERENCES d2.reservations(id),
 PRIMARY KEY(planning_run_id,reservation_id)
);
CREATE TRIGGER plan_write_lock BEFORE INSERT OR UPDATE OR DELETE ON d2.plan_reservations FOR EACH STATEMENT EXECUTE FUNCTION public.d2_plan_write_lock();
CREATE TRIGGER plan_child_guard BEFORE INSERT OR UPDATE OR DELETE ON d2.plan_reservations FOR EACH ROW EXECUTE FUNCTION public.d2_plan_child_guard();
CREATE TRIGGER no_truncate BEFORE TRUNCATE ON d2.plan_reservations FOR EACH STATEMENT EXECUTE FUNCTION public.d2_reject_fact_mutation();
CREATE TABLE d2.commands(
 id uuid PRIMARY KEY, request jsonb NOT NULL, response jsonb NOT NULL,
 recorded_at timestamptz NOT NULL DEFAULT clock_timestamp()
);
CREATE TABLE d2.journal(
 id bigint GENERATED ALWAYS AS IDENTITY PRIMARY KEY, command_id uuid NOT NULL REFERENCES d2.commands(id) DEFERRABLE INITIALLY DEFERRED,
 account_id uuid NOT NULL REFERENCES d2.accounts(id), pool text NOT NULL CHECK(pool IN ('PLANNED','INCIDENT','UNCERTAINTY')),
 reservation_id uuid REFERENCES d2.reservations(id), loan_id uuid,
 limit_delta numeric(18,4) NOT NULL DEFAULT 0, commitment_delta numeric(18,4) NOT NULL DEFAULT 0, consumption_delta numeric(18,4) NOT NULL DEFAULT 0,
 CHECK(abs(limit_delta)<1e14 AND abs(commitment_delta)<1e14 AND abs(consumption_delta)<1e14)
);
CREATE INDEX journal_account_pool ON d2.journal(account_id,pool);
CREATE INDEX journal_reservation ON d2.journal(reservation_id,account_id);
CREATE TABLE d2.loans(
 id uuid PRIMARY KEY, account_id uuid NOT NULL REFERENCES d2.accounts(id), operation_id uuid NOT NULL REFERENCES public.operations(id),
 units numeric(18,4) NOT NULL CHECK(units>0 AND units<1e14)
);
ALTER TABLE d2.journal ADD CONSTRAINT fk_journal_loan FOREIGN KEY(loan_id) REFERENCES d2.loans(id);
CREATE TABLE d2.capacity_limits(
 id bigint GENERATED ALWAYS AS IDENTITY PRIMARY KEY,command_id uuid NOT NULL REFERENCES d2.commands(id) DEFERRABLE INITIALLY DEFERRED,
 account_id uuid NOT NULL REFERENCES d2.accounts(id),capacity numeric(18,4) NOT NULL CHECK(capacity>=0 AND capacity<1e14),
 confidence numeric(4,3) NOT NULL CHECK(confidence BETWEEN 0 AND 1),evidence_sha256 char(64) NOT NULL
);
CREATE INDEX capacity_limits_latest ON d2.capacity_limits(account_id,id DESC);
CREATE VIEW d2.balances AS
 SELECT a.id account_id,p.pool,coalesce(l.capacity,a.initial_capacity)*p.fraction+coalesce(sum(j.limit_delta),0) effective_limit,
 coalesce(sum(j.commitment_delta),0) outstanding,coalesce(sum(j.consumption_delta),0) consumed,
 coalesce(l.capacity,a.initial_capacity)*p.fraction+coalesce(sum(j.limit_delta-j.commitment_delta-j.consumption_delta),0) available
 FROM d2.accounts a LEFT JOIN LATERAL (SELECT capacity FROM d2.capacity_limits WHERE account_id=a.id ORDER BY id DESC LIMIT 1) l ON true CROSS JOIN (VALUES('PLANNED',0.7::numeric),('INCIDENT',0.2::numeric),('UNCERTAINTY',0.1::numeric)) p(pool,fraction)
 LEFT JOIN d2.journal j ON j.account_id=a.id AND j.pool=p.pool GROUP BY a.id,l.capacity,p.pool,p.fraction;
CREATE VIEW d2.reservation_balances AS
 SELECT reservation_id,account_id,sum(commitment_delta) outstanding,sum(consumption_delta) consumed
 FROM d2.journal WHERE reservation_id IS NOT NULL GROUP BY reservation_id,account_id;
DO $$ DECLARE rel text; BEGIN
 FOREACH rel IN ARRAY ARRAY['accounts','reservations','commands','journal','loans','capacity_limits'] LOOP
  EXECUTE format('CREATE TRIGGER immutable_fact BEFORE UPDATE OR DELETE OR TRUNCATE ON d2.%I FOR EACH STATEMENT EXECUTE FUNCTION public.d2_reject_fact_mutation()',rel);
 END LOOP;
END $$;
CREATE FUNCTION d2.mapping_guard() RETURNS trigger LANGUAGE plpgsql AS $$
DECLARE oid uuid;
BEGIN
 PERFORM pg_advisory_xact_lock(742002);
 oid=CASE WHEN TG_OP='DELETE' THEN OLD.operation_id ELSE NEW.operation_id END;
 IF EXISTS(SELECT 1 FROM d2.reservations WHERE operation_id=oid) OR
 (TG_OP='UPDATE' AND EXISTS(SELECT 1 FROM d2.reservations WHERE operation_id=OLD.operation_id)) THEN
  RAISE EXCEPTION 'Reservation account mapping is frozen' USING ERRCODE='55000';
 END IF;
 IF TG_OP='DELETE' THEN RETURN OLD; END IF;
 RETURN NEW;
END $$;
CREATE TRIGGER mapping_guard BEFORE INSERT OR UPDATE OR DELETE ON d2.operation_accounts FOR EACH ROW EXECUTE FUNCTION d2.mapping_guard();
CREATE TRIGGER mapping_no_truncate BEFORE TRUNCATE ON d2.operation_accounts FOR EACH STATEMENT EXECUTE FUNCTION public.d2_reject_fact_mutation();
CREATE FUNCTION d2.begin_command(cid uuid,req jsonb) RETURNS jsonb LANGUAGE plpgsql AS $$
DECLARE previous d2.commands;
BEGIN
 -- Conservative validation kernel: one global transaction lock. It establishes
 -- correctness first; finer-grained parallelism is not claimed by this prototype.
 PERFORM pg_advisory_xact_lock(742002);
 SELECT * INTO previous FROM d2.commands WHERE id=cid;
 IF FOUND THEN
  IF previous.request<>req THEN RAISE EXCEPTION 'Idempotency payload conflict' USING ERRCODE='23505'; END IF;
  RETURN previous.response;
 END IF;
 RETURN NULL;
END $$;
CREATE FUNCTION d2.capacity(cid uuid,req jsonb) RETURNS jsonb
LANGUAGE plpgsql SECURITY DEFINER SET search_path=pg_catalog,public,d2 AS $$
DECLARE prior jsonb; result jsonb; action text=req->>'action'; op public.operations; acct d2.accounts;
 res d2.reservations; item record; entry jsonb; rid uuid; aid uuid; lid uuid; n numeric; s numeric; c numeric;
 b d2.balances; pending numeric; total_consumed numeric; debt numeric; original d2.commands; sum_ids uuid[]; given_ids uuid[];
BEGIN
 prior=d2.begin_command(cid,req); IF prior IS NOT NULL THEN RETURN prior; END IF;
 IF req->>'reason' IS NULL OR length(btrim(req->>'reason'))=0 THEN RAISE EXCEPTION 'Reason required' USING ERRCODE='23514'; END IF;
 IF action='RESERVE' THEN
  SELECT * INTO STRICT op FROM public.operations WHERE id=(req->>'operation_id')::uuid FOR UPDATE;
  IF op.state NOT IN ('READY','LEASED') THEN RAISE EXCEPTION 'Operation cannot reserve' USING ERRCODE='23514'; END IF;
  IF req->>'pool' NOT IN ('PLANNED','INCIDENT') OR req->>'pool' IS NULL THEN RAISE EXCEPTION 'Invalid pool' USING ERRCODE='23514'; END IF;
  IF NOT EXISTS(SELECT 1 FROM d2.operation_accounts WHERE operation_id=op.id) THEN RAISE EXCEPTION 'No binding accounts' USING ERRCODE='23514'; END IF;
  rid=cid;
  FOR item IN SELECT m.*,a.resource_id FROM d2.operation_accounts m JOIN d2.accounts a ON a.id=m.account_id WHERE operation_id=op.id ORDER BY m.account_id LOOP
   SELECT * INTO STRICT acct FROM d2.accounts WHERE id=item.account_id FOR UPDATE;
   IF acct.window_start>clock_timestamp() OR acct.window_end<=clock_timestamp() THEN RAISE EXCEPTION 'Account outside active window' USING ERRCODE='23514'; END IF;
   SELECT * INTO STRICT b FROM d2.balances WHERE account_id=acct.id AND pool=req->>'pool';
   IF b.available IS NULL OR b.available<item.units THEN RAISE EXCEPTION 'WAITING_CAPACITY' USING ERRCODE='23514'; END IF;
   IF NOT EXISTS(SELECT 1 FROM d2.reservations WHERE id=rid) THEN
    INSERT INTO d2.reservations VALUES(rid,op.id,acct.resource_id,req->>'pool',clock_timestamp());
   ELSIF (SELECT resource_id FROM d2.reservations WHERE id=rid)<>acct.resource_id THEN RAISE EXCEPTION 'Mixed resources' USING ERRCODE='23514'; END IF;
   INSERT INTO d2.journal(command_id,account_id,pool,reservation_id,commitment_delta) VALUES(cid,acct.id,req->>'pool',rid,item.units);
  END LOOP;
  result=jsonb_build_object('reservation_id',rid);
 ELSIF action='TOP_UP' THEN
  SELECT * INTO STRICT res FROM d2.reservations WHERE id=(req->>'reservation_id')::uuid;
  IF NOT EXISTS(SELECT 1 FROM public.operations WHERE id=res.operation_id AND state='READY') THEN RAISE EXCEPTION 'Retry READY state required' USING ERRCODE='23514';END IF;
  FOR item IN SELECT m.account_id,m.units FROM d2.operation_accounts m WHERE m.operation_id=res.operation_id ORDER BY m.account_id LOOP
   PERFORM 1 FROM d2.accounts WHERE id=item.account_id FOR UPDATE;
   SELECT outstanding INTO STRICT pending FROM d2.reservation_balances WHERE reservation_id=res.id AND account_id=item.account_id;
   n=greatest(item.units-pending,0);
   SELECT * INTO STRICT b FROM d2.balances WHERE account_id=item.account_id AND pool=res.pool;
   IF n>0 AND (b.available IS NULL OR b.available<n) THEN RAISE EXCEPTION 'WAITING_CAPACITY on retry' USING ERRCODE='23514';END IF;
   IF n>0 THEN INSERT INTO d2.journal(command_id,account_id,pool,reservation_id,commitment_delta) VALUES(cid,item.account_id,res.pool,res.id,n);END IF;
  END LOOP;
  result=jsonb_build_object('reservation_id',res.id);
 ELSIF action IN ('RELEASE','CONSUME','ADJUST') THEN
  SELECT * INTO STRICT res FROM d2.reservations WHERE id=(req->>'reservation_id')::uuid;
  IF action='ADJUST' THEN
   SELECT * INTO STRICT original FROM d2.commands WHERE id=(req->>'corrects_command_id')::uuid;
   IF original.request->>'action' NOT IN ('CONSUME','ADJUST') OR original.request->>'reservation_id'<>res.id::text THEN RAISE EXCEPTION 'Correction must identify consumption for same reservation' USING ERRCODE='23514'; END IF;
  END IF;
  SELECT array_agg(account_id ORDER BY account_id) INTO sum_ids FROM d2.reservation_balances WHERE reservation_id=res.id;
  SELECT array_agg((value->>'account_id')::uuid ORDER BY (value->>'account_id')::uuid) INTO given_ids FROM jsonb_array_elements(req->'entries');
  IF given_ids IS DISTINCT FROM sum_ids THEN RAISE EXCEPTION 'All reservation accounts required exactly once' USING ERRCODE='23514'; END IF;
  FOR entry IN SELECT value FROM jsonb_array_elements(req->'entries') ORDER BY (value->>'account_id')::uuid LOOP
   aid=(entry->>'account_id')::uuid;
   PERFORM 1 FROM d2.accounts WHERE id=aid FOR UPDATE;
   SELECT outstanding,consumed INTO STRICT pending,total_consumed FROM d2.reservation_balances WHERE reservation_id=res.id AND account_id=aid;
   s=CASE WHEN action='ADJUST' THEN 0 ELSE (entry->>'settled')::numeric END;
   c=CASE WHEN action='RELEASE' THEN 0 ELSE (entry->>'consumed')::numeric END;
   IF s IS NULL OR c IS NULL OR NOT(abs(s)<1e14 AND abs(c)<1e14) OR s<0 OR s>pending OR total_consumed+c<0 OR (action<>'ADJUST' AND c<0) THEN RAISE EXCEPTION 'Invalid settlement/correction' USING ERRCODE='23514'; END IF;
   INSERT INTO d2.journal(command_id,account_id,pool,reservation_id,commitment_delta,consumption_delta) VALUES(cid,aid,res.pool,res.id,-s,c);
  END LOOP;
  result=jsonb_build_object('reservation_id',res.id);
 ELSIF action IN ('BORROW','RETURN') THEN
  n=(req->>'units')::numeric;
  IF n IS NULL OR NOT(n>0 AND n<1e14) THEN RAISE EXCEPTION 'Positive finite amount required' USING ERRCODE='23514'; END IF;
  IF action='BORROW' THEN
   aid=(req->>'account_id')::uuid;
   SELECT * INTO STRICT op FROM public.operations WHERE id=(req->>'operation_id')::uuid;
   IF NOT coalesce((op.policy_snapshot->>'interruptible')::boolean,false) OR NOT coalesce((op.policy_snapshot->>'checkpoint_verified')::boolean,false) THEN RAISE EXCEPTION 'Checkpointable operation required' USING ERRCODE='23514'; END IF;
   IF NOT EXISTS(SELECT 1 FROM d2.operation_accounts WHERE operation_id=op.id AND account_id=aid) THEN RAISE EXCEPTION 'Borrow account mismatch' USING ERRCODE='23514'; END IF;
   PERFORM 1 FROM d2.accounts WHERE id=aid FOR UPDATE;
   IF EXISTS(SELECT 1 FROM public.incidents WHERE status<>'RESOLVED' AND severity IN ('SEV1','SEV2')) THEN RAISE EXCEPTION 'Incident demand prevents borrowing' USING ERRCODE='23514'; END IF;
   SELECT * INTO STRICT b FROM d2.balances WHERE account_id=aid AND pool='INCIDENT';
   IF b.available IS NULL OR b.available<n THEN RAISE EXCEPTION 'Insufficient idle incident reserve' USING ERRCODE='23514'; END IF;
   lid=cid; INSERT INTO d2.loans VALUES(lid,aid,op.id,n);
   INSERT INTO d2.journal(command_id,account_id,pool,loan_id,limit_delta) VALUES(cid,aid,'INCIDENT',lid,-n),(cid,aid,'PLANNED',lid,n);
  ELSE
   SELECT id,account_id INTO STRICT lid,aid FROM d2.loans WHERE id=(req->>'loan_id')::uuid;
   PERFORM 1 FROM d2.accounts WHERE id=aid FOR UPDATE;
   SELECT sum(limit_delta) INTO debt FROM d2.journal WHERE loan_id=lid AND pool='PLANNED';
   SELECT * INTO STRICT b FROM d2.balances WHERE account_id=aid AND pool='PLANNED';
   IF b.available IS NULL OR b.available<n OR debt<n THEN RAISE EXCEPTION 'Return exceeds debt or free capacity' USING ERRCODE='23514'; END IF;
   INSERT INTO d2.journal(command_id,account_id,pool,loan_id,limit_delta) VALUES(cid,aid,'PLANNED',lid,-n),(cid,aid,'INCIDENT',lid,n);
  END IF;
  result=jsonb_build_object('loan_id',lid);
 ELSE RAISE EXCEPTION 'Unknown capacity action' USING ERRCODE='23514';
 END IF;
 INSERT INTO d2.commands VALUES(cid,req,result,clock_timestamp());
 INSERT INTO public.outbox_events(aggregate_type,aggregate_id,event_type,payload) VALUES('D2_COMMAND',cid,action,result);
 RETURN result;
END $$;
-- No role is created in migrations. Deployment must bind a non-login schema
-- owner and grant only reviewed entrypoints to the control-plane role.
REVOKE ALL ON ALL TABLES IN SCHEMA d2 FROM PUBLIC;
REVOKE ALL ON ALL FUNCTIONS IN SCHEMA d2 FROM PUBLIC;
REVOKE ALL ON SCHEMA d2 FROM PUBLIC;

CREATE FUNCTION d2.recalibrate(cid uuid,req jsonb) RETURNS jsonb
LANGUAGE plpgsql SECURITY DEFINER SET search_path=pg_catalog,public,d2 AS $$
DECLARE previous jsonb;result jsonb;aid uuid=(req->>'account_id')::uuid;
BEGIN
 previous=d2.begin_command(cid,req);IF previous IS NOT NULL THEN RETURN previous;END IF;
 IF req->>'reason' IS NULL OR length(btrim(req->>'reason'))=0 OR req->>'evidence_sha256' !~ '^[a-f0-9]{64}$' OR req->>'evidence_sha256' IS NULL THEN RAISE EXCEPTION 'Evidence and reason required' USING ERRCODE='23514';END IF;
 PERFORM 1 FROM d2.accounts WHERE id=aid FOR UPDATE;
 INSERT INTO d2.capacity_limits(command_id,account_id,capacity,confidence,evidence_sha256) VALUES(cid,aid,(req->>'capacity')::numeric,(req->>'confidence')::numeric,req->>'evidence_sha256');
 SELECT jsonb_build_object('account_id',aid,'available',available) INTO STRICT result FROM d2.balances WHERE account_id=aid AND pool='PLANNED';
 INSERT INTO d2.commands VALUES(cid,req,result,clock_timestamp());
 INSERT INTO public.outbox_events(aggregate_type,aggregate_id,event_type,payload) VALUES('CAPACITY_ACCOUNT',aid,'RECALIBRATED',result);
 RETURN result;
END $$;
REVOKE ALL ON ALL FUNCTIONS IN SCHEMA d2 FROM PUBLIC;
