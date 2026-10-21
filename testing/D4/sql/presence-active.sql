-- SPDX-License-Identifier: GPL-3.0-only
-- A24: durable presence, never process/lease authority.
CREATE TABLE d4.presence_sessions(id uuid PRIMARY KEY,worker_id uuid NOT NULL REFERENCES d4.worker_catalog(worker_id),previous_id uuid REFERENCES d4.presence_sessions(id),opened_at timestamptz NOT NULL DEFAULT clock_timestamp());
CREATE TABLE d4.presence_heads(worker_id uuid PRIMARY KEY REFERENCES d4.worker_catalog(worker_id),session_id uuid NOT NULL UNIQUE REFERENCES d4.presence_sessions(id),sequence bigint NOT NULL DEFAULT 0 CHECK(sequence>=0),observed_at timestamptz);
CREATE TABLE d4.presence_commands(id uuid PRIMARY KEY,request jsonb NOT NULL,response jsonb NOT NULL);
CREATE TABLE d4.presence_delivery(delivery_id uuid PRIMARY KEY REFERENCES d4.deliveries(id),session_id uuid NOT NULL REFERENCES d4.presence_sessions(id));
CREATE TABLE d4.session_transport_commands(id uuid PRIMARY KEY,worker_id uuid NOT NULL,request jsonb NOT NULL,response jsonb NOT NULL);
DO $$ DECLARE n text;BEGIN FOREACH n IN ARRAY ARRAY['presence_sessions','presence_commands','presence_delivery','session_transport_commands'] LOOP EXECUTE format('CREATE TRIGGER immutable_fact BEFORE UPDATE OR DELETE OR TRUNCATE ON d4.%I FOR EACH STATEMENT EXECUTE FUNCTION public.d2_reject_fact_mutation()',n);END LOOP;END $$;
CREATE FUNCTION d4.presence_current(wid uuid) RETURNS jsonb LANGUAGE sql STABLE SECURITY DEFINER SET search_path=pg_catalog,public,d4 AS $$ SELECT coalesce((SELECT jsonb_build_object('session_id',session_id,'sequence',sequence,'observed_at',observed_at,'fresh',observed_at BETWEEN clock_timestamp()-interval '90 seconds' AND clock_timestamp()) FROM d4.presence_heads WHERE worker_id=wid),'null'::jsonb); $$;
CREATE FUNCTION d4.presence_live(wid uuid) RETURNS boolean LANGUAGE sql STABLE SECURITY DEFINER SET search_path=pg_catalog,public,d4 AS $$ SELECT EXISTS(SELECT 1 FROM d4.presence_heads h JOIN d4.worker_catalog c ON c.worker_id=h.worker_id JOIN public.workers w ON w.id=h.worker_id WHERE h.worker_id=wid AND c.enabled AND w.state='ONLINE' AND h.observed_at BETWEEN clock_timestamp()-interval '90 seconds' AND clock_timestamp()); $$;
CREATE FUNCTION d4.require_presence(wid uuid) RETURNS void LANGUAGE plpgsql SECURITY DEFINER SET search_path=pg_catalog,public,d4 AS $$ BEGIN IF EXISTS(SELECT 1 FROM d4.worker_catalog WHERE worker_id=wid) AND NOT d4.presence_live(wid) THEN RAISE EXCEPTION 'Fresh durable worker presence required' USING ERRCODE='23514';END IF;END $$;
CREATE FUNCTION d4.presence_open(cid uuid,wid uuid,sid uuid,expected uuid) RETURNS jsonb LANGUAGE plpgsql SECURITY DEFINER SET search_path=pg_catalog,public,d2,d3,d4 AS $$
DECLARE req jsonb=jsonb_build_object('worker',wid,'session',sid,'expected',expected);p d4.presence_commands;h d4.presence_heads;result jsonb;
BEGIN
 PERFORM d3.lock_state();SELECT * INTO p FROM d4.presence_commands WHERE id=cid;IF FOUND THEN IF p.request IS DISTINCT FROM req THEN RAISE EXCEPTION 'Presence replay conflict' USING ERRCODE='23514';END IF;RETURN p.response;END IF;
 IF cid IS NULL OR sid IS NULL OR NOT EXISTS(SELECT 1 FROM d4.worker_catalog c JOIN public.workers w ON w.id=c.worker_id WHERE c.worker_id=wid AND c.enabled AND w.state='ONLINE') THEN RAISE EXCEPTION 'Authorized online catalog worker required' USING ERRCODE='23514';END IF;
 SELECT * INTO h FROM d4.presence_heads WHERE worker_id=wid;IF h.session_id IS DISTINCT FROM expected THEN RAISE EXCEPTION 'Presence head changed' USING ERRCODE='40001';END IF;
 INSERT INTO d4.presence_sessions(id,worker_id,previous_id) VALUES(sid,wid,expected);
 INSERT INTO d4.presence_heads(worker_id,session_id) VALUES(wid,sid) ON CONFLICT(worker_id) DO UPDATE SET session_id=excluded.session_id,sequence=0,observed_at=NULL;
 result=jsonb_build_object('session_id',sid,'sequence',0,'receipt_only',true);INSERT INTO d4.presence_commands VALUES(cid,req,result);RETURN result;
END $$;
CREATE FUNCTION d4.presence_beat(cid uuid,wid uuid,sid uuid,seq bigint) RETURNS jsonb LANGUAGE plpgsql SECURITY DEFINER SET search_path=pg_catalog,public,d2,d3,d4 AS $$
DECLARE req jsonb=jsonb_build_object('worker',wid,'session',sid,'sequence',seq);p d4.presence_commands;h d4.presence_heads;result jsonb;at_time timestamptz;
BEGIN
 PERFORM d3.lock_state();SELECT * INTO p FROM d4.presence_commands WHERE id=cid;IF FOUND THEN IF p.request IS DISTINCT FROM req THEN RAISE EXCEPTION 'Presence replay conflict' USING ERRCODE='23514';END IF;RETURN p.response;END IF;
 SELECT * INTO h FROM d4.presence_heads WHERE worker_id=wid;IF cid IS NULL OR sid IS DISTINCT FROM h.session_id OR seq IS NULL OR seq<>h.sequence+1 OR NOT EXISTS(SELECT 1 FROM d4.worker_catalog WHERE worker_id=wid AND enabled) THEN RAISE EXCEPTION 'Current session and next monotonic sequence required' USING ERRCODE='23514';END IF;
 at_time=clock_timestamp();UPDATE d4.presence_heads SET sequence=seq,observed_at=at_time WHERE worker_id=wid;UPDATE public.workers SET last_heartbeat_at=at_time WHERE id=wid;
 result=jsonb_build_object('session_id',sid,'sequence',seq,'observed_at',at_time,'receipt_only',true);INSERT INTO d4.presence_commands VALUES(cid,req,result);RETURN result;
END $$;
CREATE FUNCTION d4.require_delivery_presence(delivery uuid) RETURNS void LANGUAGE plpgsql SECURITY DEFINER SET search_path=pg_catalog,public,d4 AS $$
BEGIN IF NOT EXISTS(SELECT 1 FROM d4.presence_delivery b JOIN d4.deliveries d ON d.id=b.delivery_id JOIN d4.presence_heads h ON h.worker_id=d.worker_id AND h.session_id=b.session_id WHERE b.delivery_id=delivery AND d4.presence_live(d.worker_id)) THEN RAISE EXCEPTION 'Delivery belongs to a superseded or missing worker incarnation' USING ERRCODE='23514';END IF;END $$;
CREATE FUNCTION d4.session_audit() RETURNS jsonb LANGUAGE sql SECURITY DEFINER SET search_path=pg_catalog,public,d4 AS $$ SELECT d4.review_audit()||jsonb_build_object('presence_sessions',(SELECT coalesce(jsonb_agg(to_jsonb(t)),'[]') FROM d4.presence_sessions t),'presence_heads',(SELECT coalesce(jsonb_agg(to_jsonb(t)),'[]') FROM d4.presence_heads t),'presence_delivery',(SELECT coalesce(jsonb_agg(to_jsonb(t)),'[]') FROM d4.presence_delivery t)); $$;

ALTER FUNCTION d3.state_relations() RENAME TO state_relations_before_presence;
CREATE FUNCTION d3.state_relations() RETURNS text[] LANGUAGE sql IMMUTABLE AS $$ SELECT d3.state_relations_before_presence()||ARRAY['d4.presence_sessions','d4.presence_heads','d4.presence_delivery']; $$;
