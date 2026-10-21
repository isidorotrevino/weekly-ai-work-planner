-- SPDX-License-Identifier: GPL-3.0-only
-- D5 synthetic proposal. Requires V11 + isolated V31; no D2 task/requirement writes.
-- d5_reviewer is a pre-created synthetic lab role, not a real user identity.
BEGIN;
SET LOCAL ROLE d5_owner;
CREATE TABLE d5.comparison_reports(
 report_sha256 d5.hash PRIMARY KEY, project_id uuid NOT NULL, document_id uuid NOT NULL,
 profile d5.profile NOT NULL CHECK(profile<>'markdown-structure.v1'),
 before_observation_id uuid NOT NULL, after_observation_id uuid NOT NULL,
 state text NOT NULL CHECK(state IN ('PREVIEW_ONLY','BLOCKED')), report_bytes bytea NOT NULL,
 FOREIGN KEY(before_observation_id,document_id,project_id,profile) REFERENCES d5.observations(observation_id,document_id,project_id,profile),
 FOREIGN KEY(after_observation_id,document_id,project_id,profile) REFERENCES d5.observations(observation_id,document_id,project_id,profile),
 CHECK(octet_length(report_bytes)<=33554432 AND report_sha256=encode(public.digest(report_bytes,'sha256'),'hex'))
);
CREATE TABLE d5.comparisons(
 comparison_id uuid PRIMARY KEY REFERENCES d5.commands DEFERRABLE INITIALLY DEFERRED,
 report_sha256 d5.hash NOT NULL REFERENCES d5.comparison_reports
);
CREATE TABLE d5.review_items(
 comparison_id uuid NOT NULL REFERENCES d5.comparisons, source_key text COLLATE "C" NOT NULL,
 row_sha256 d5.hash NOT NULL, change text NOT NULL CHECK(change IN ('ADDED','CHANGED','ABSENT_IN_OBSERVATION')),
 row_bytes bytea NOT NULL,
 source_key_sha256 text GENERATED ALWAYS AS (encode(public.digest(source_key,'sha256'),'hex')) STORED,
 PRIMARY KEY(comparison_id,source_key_sha256), UNIQUE(comparison_id,source_key_sha256,row_sha256),
 CHECK(source_key ~ '^[A-Z][A-Z0-9_]*-[0-9]+$'),
 CHECK(octet_length(row_bytes)<=2097152 AND row_sha256=encode(public.digest(row_bytes,'sha256'),'hex'))
);
CREATE TABLE d5.row_decisions(
 command_id uuid PRIMARY KEY REFERENCES d5.commands DEFERRABLE INITIALLY DEFERRED,
 comparison_id uuid NOT NULL, source_key text COLLATE "C" NOT NULL, row_sha256 d5.hash NOT NULL,
 decision text NOT NULL CHECK(decision IN ('ACCEPT','REJECT')),
 version bigint NOT NULL CHECK(version>0), reviewer_label text NOT NULL, reason text NOT NULL,
 source_key_sha256 text GENERATED ALWAYS AS (encode(public.digest(source_key,'sha256'),'hex')) STORED,
 UNIQUE(command_id,comparison_id,source_key_sha256,row_sha256), UNIQUE(comparison_id,source_key_sha256,version),
 FOREIGN KEY(comparison_id,source_key_sha256,row_sha256) REFERENCES d5.review_items(comparison_id,source_key_sha256,row_sha256)
);
CREATE TABLE d5.row_review_heads(
 comparison_id uuid NOT NULL, source_key text COLLATE "C" NOT NULL, row_sha256 d5.hash NOT NULL,
 version bigint NOT NULL DEFAULT 0 CHECK(version>=0), decision_command_id uuid,
 source_key_sha256 text GENERATED ALWAYS AS (encode(public.digest(source_key,'sha256'),'hex')) STORED,
 PRIMARY KEY(comparison_id,source_key_sha256),
 FOREIGN KEY(comparison_id,source_key_sha256,row_sha256) REFERENCES d5.review_items(comparison_id,source_key_sha256,row_sha256),
 FOREIGN KEY(decision_command_id,comparison_id,source_key_sha256,row_sha256) REFERENCES d5.row_decisions(command_id,comparison_id,source_key_sha256,row_sha256),
 CHECK((version=0 AND decision_command_id IS NULL) OR (version>0 AND decision_command_id IS NOT NULL))
);
CREATE TABLE d5.simulations(
 command_id uuid PRIMARY KEY REFERENCES d5.commands DEFERRABLE INITIALLY DEFERRED,
 comparison_id uuid NOT NULL REFERENCES d5.comparisons, reference_version bigint NOT NULL CHECK(reference_version>0),
 result jsonb NOT NULL CHECK(result->'simulation_only'='true'::jsonb AND result->'writes_d2'='false'::jsonb AND result->'activation_allowed'='false'::jsonb)
);
DO $$ DECLARE rel text; BEGIN
 FOREACH rel IN ARRAY ARRAY['comparison_reports','comparisons','review_items','row_decisions','simulations'] LOOP
  EXECUTE format('CREATE TRIGGER immutable BEFORE UPDATE OR DELETE OR TRUNCATE ON d5.%I FOR EACH STATEMENT EXECUTE FUNCTION d5.immutable()',rel);
 END LOOP;
END $$;
CREATE FUNCTION d5.review_envelope(envelope json, action text, extra text[], nonstrings text[] DEFAULT ARRAY[]::text[]) RETURNS jsonb
LANGUAGE plpgsql IMMUTABLE SET search_path=pg_catalog,pg_temp AS $$
DECLARE req jsonb; expected text[]; actual text[]; field text;
BEGIN
 IF envelope IS NULL OR json_typeof(envelope)<>'object' THEN RAISE EXCEPTION 'Object required'; END IF;
 IF EXISTS(SELECT FROM json_each(envelope) GROUP BY key HAVING count(*)>1) THEN RAISE EXCEPTION 'Duplicate key'; END IF;
 req=envelope::jsonb;
 SELECT array_agg(k ORDER BY k) INTO expected FROM unnest(ARRAY['schema','command_id','action','project_id','document_id']||extra) k;
 SELECT array_agg(k ORDER BY k) INTO actual FROM jsonb_object_keys(req) k;
 IF actual IS DISTINCT FROM expected OR req->>'schema' IS DISTINCT FROM 'd5.source-command.v1' OR req->>'action' IS DISTINCT FROM action THEN RAISE EXCEPTION 'Closed review envelope required'; END IF;
 FOREACH field IN ARRAY expected LOOP
  IF NOT field=ANY(nonstrings) THEN
   IF jsonb_typeof(req->field) IS DISTINCT FROM 'string' THEN RAISE EXCEPTION 'String required'; END IF;
   IF right(field,3)='_id' AND (req->>field)::uuid::text IS DISTINCT FROM req->>field THEN RAISE EXCEPTION 'Canonical UUID required'; END IF;
  END IF;
 END LOOP;
 RETURN req;
END $$;
CREATE FUNCTION d5.review_version(value jsonb) RETURNS bigint LANGUAGE plpgsql IMMUTABLE SET search_path=pg_catalog,pg_temp AS $$
BEGIN
 IF jsonb_typeof(value) IS DISTINCT FROM 'number' OR value::text !~ '^(0|[1-9][0-9]*)$' THEN RAISE EXCEPTION 'Nonnegative integer required'; END IF;
 RETURN value::text::bigint;
END $$;
CREATE FUNCTION d5.review_prior(req jsonb) RETURNS jsonb LANGUAGE plpgsql VOLATILE SET search_path=pg_catalog,pg_temp AS $$
DECLARE prior d5.commands;
BEGIN
 IF current_setting('transaction_isolation')<>'read committed' THEN RAISE EXCEPTION 'READ COMMITTED required'; END IF;
 PERFORM pg_advisory_xact_lock(742005);
 SELECT * INTO prior FROM d5.commands WHERE command_id=(req->>'command_id')::uuid;
 IF NOT FOUND THEN RETURN NULL; END IF;
 IF prior.request IS DISTINCT FROM req THEN RETURN jsonb_build_object('status','CONFLICT','code','COMMAND_CONTENT_CONFLICT','receipt_only',true,'activation_allowed',false); END IF;
 RETURN prior.response;
END $$;
CREATE FUNCTION d5.review_finish(req jsonb,result jsonb) RETURNS jsonb LANGUAGE plpgsql VOLATILE SET search_path=pg_catalog,pg_temp AS $$
BEGIN
 result=result||jsonb_build_object('command_id',req->>'command_id','action',req->>'action','project_id',req->>'project_id','document_id',req->>'document_id','receipt_only',true,'activation_allowed',false);
 INSERT INTO d5.commands(command_id,request,request_sha256,response) VALUES((req->>'command_id')::uuid,req,encode(public.digest('d5.source-command.v1:'||req::text,'sha256'),'hex'),result);
 RETURN result;
END $$;
CREATE FUNCTION d5.read_comparison_sources(pid uuid,doc uuid,bid uuid,aid uuid) RETURNS jsonb LANGUAGE sql STABLE SECURITY DEFINER SET search_path=pg_catalog,pg_temp AS $$
 SELECT jsonb_build_object('before',d5.read_observation(pid,doc,bid),'after',d5.read_observation(pid,doc,aid))
 FROM d5.observations b JOIN d5.observations a ON a.project_id=b.project_id AND a.document_id=b.document_id AND a.profile=b.profile
 WHERE b.observation_id=bid AND a.observation_id=aid AND b.project_id=pid AND b.document_id=doc $$;

CREATE FUNCTION d5.save_comparison(envelope json,artifact bytea) RETURNS jsonb LANGUAGE plpgsql VOLATILE SECURITY DEFINER SET search_path=pg_catalog,pg_temp AS $$
DECLARE req jsonb; prior jsonb; val jsonb; item jsonb; rowval jsonb; rowbytes bytea; cid uuid; pid uuid; doc uuid; bid uuid; aid uuid; prof d5.profile;
 ph d5.hash; bh text; ah text; bch text; ach text; stored d5.comparison_reports;
BEGIN
 req=d5.review_envelope(envelope,'SAVE_COMPARISON',ARRAY['before_observation_id','after_observation_id','profile','report_sha256']);
 cid=(req->>'command_id')::uuid;pid=(req->>'project_id')::uuid;doc=(req->>'document_id')::uuid;
 bid=(req->>'before_observation_id')::uuid;aid=(req->>'after_observation_id')::uuid;prof=(req->>'profile')::d5.profile;ph=(req->>'report_sha256')::d5.hash;
 IF artifact IS NULL OR octet_length(artifact)>33554432 OR ph IS DISTINCT FROM encode(public.digest(artifact,'sha256'),'hex') THEN RAISE EXCEPTION 'Report size/hash mismatch'; END IF;
 val=convert_from(artifact,'UTF8')::jsonb;
 IF val->>'schema' IS DISTINCT FROM 'd5.persisted-comparison.v1' OR val->>'project_id' IS DISTINCT FROM pid::text OR val->>'document_id' IS DISTINCT FROM doc::text
  OR val->>'profile' IS DISTINCT FROM prof::text OR val->'activation_allowed' IS DISTINCT FROM 'false'::jsonb
  OR val->>'state' NOT IN ('PREVIEW_ONLY','BLOCKED') OR val->>'state' IS NULL
  OR jsonb_typeof(val->'review_items') IS DISTINCT FROM 'array' OR jsonb_array_length(val->'review_items')>2000
  OR val#>>'{observations,before,observation_id}' IS DISTINCT FROM bid::text OR val#>>'{observations,after,observation_id}' IS DISTINCT FROM aid::text
  THEN RAISE EXCEPTION 'Invalid report envelope'; END IF;
 prior=d5.review_prior(req);IF prior IS NOT NULL THEN
  IF prior->>'status'='OK' THEN
   SELECT * INTO STRICT stored FROM d5.comparison_reports WHERE report_sha256=ph;
   IF stored.report_bytes IS DISTINCT FROM artifact THEN RAISE EXCEPTION 'Report collision'; END IF;
  END IF;
  RETURN prior;
 END IF;
 SELECT b.preview_sha256,a.preview_sha256,bc.sha256,ac.sha256 INTO bh,ah,bch,ach
 FROM d5.observations b JOIN d5.observations a ON a.document_id=b.document_id AND a.project_id=b.project_id AND a.profile=b.profile
 JOIN d5.revision_content bc ON bc.revision_id=b.revision_id JOIN d5.revision_content ac ON ac.revision_id=a.revision_id
 WHERE b.observation_id=bid AND a.observation_id=aid AND b.document_id=doc AND b.project_id=pid AND b.profile=prof;
 IF NOT FOUND OR prof='markdown-structure.v1' THEN RETURN d5.review_finish(req,jsonb_build_object('status','CONFLICT','code','OBSERVATION_SCOPE_CONFLICT')); END IF;
 IF val#>>'{observations,before,preview_sha256}' IS DISTINCT FROM bh OR val#>>'{observations,after,preview_sha256}' IS DISTINCT FROM ah
  OR val#>>'{observations,before,content_sha256}' IS DISTINCT FROM bch OR val#>>'{observations,after,content_sha256}' IS DISTINCT FROM ach
  OR val#>>'{comparison,before_preview_sha256}' IS DISTINCT FROM bh OR val#>>'{comparison,after_preview_sha256}' IS DISTINCT FROM ah
  OR val#>>'{comparison,before_content_sha256}' IS DISTINCT FROM bch OR val#>>'{comparison,after_content_sha256}' IS DISTINCT FROM ach
  OR val#>>'{comparison,project_id}' IS DISTINCT FROM pid::text OR val#>>'{comparison,document_id}' IS DISTINCT FROM doc::text
  OR val#>>'{comparison,profile}' IS DISTINCT FROM prof::text OR val#>>'{comparison,state}' IS DISTINCT FROM val->>'state'
  OR val#>'{comparison,activation_allowed}' IS DISTINCT FROM 'false'::jsonb
  OR (val->>'state'='BLOCKED' AND jsonb_array_length(val->'review_items')<>0) THEN RAISE EXCEPTION 'Report/source binding mismatch'; END IF;
 SELECT * INTO stored FROM d5.comparison_reports WHERE report_sha256=ph;
 IF FOUND THEN
  IF stored.report_bytes IS DISTINCT FROM artifact THEN RAISE EXCEPTION 'Report collision'; END IF;
 ELSE INSERT INTO d5.comparison_reports VALUES(ph,pid,doc,prof,bid,aid,val->>'state',artifact); END IF;
 INSERT INTO d5.comparisons VALUES(cid,ph);
 FOR item IN SELECT * FROM jsonb_array_elements(val->'review_items') LOOP
  IF jsonb_typeof(item->'row_base64') IS DISTINCT FROM 'string' OR octet_length(item->>'row_base64')>2796204 THEN RAISE EXCEPTION 'Invalid row blob'; END IF;
  rowbytes=decode(item->>'row_base64','base64');rowval=convert_from(rowbytes,'UTF8')::jsonb;
  IF rowval->>'schema' IS DISTINCT FROM 'd5.source-change.v1' OR rowval->>'project_id' IS DISTINCT FROM pid::text OR rowval->>'document_id' IS DISTINCT FROM doc::text
   OR rowval->>'profile' IS DISTINCT FROM prof::text OR rowval->>'source_key' IS DISTINCT FROM item->>'source_key' OR rowval->>'change' IS DISTINCT FROM item->>'change'
   OR rowval#>>'{before,observation_id}' IS DISTINCT FROM bid::text OR rowval#>>'{after,observation_id}' IS DISTINCT FROM aid::text
   OR rowval#>>'{before,preview_sha256}' IS DISTINCT FROM bh OR rowval#>>'{after,preview_sha256}' IS DISTINCT FROM ah
   OR rowval#>>'{before,content_sha256}' IS DISTINCT FROM bch OR rowval#>>'{after,content_sha256}' IS DISTINCT FROM ach
   OR rowval->'activation_allowed' IS DISTINCT FROM 'false'::jsonb THEN RAISE EXCEPTION 'Invalid whole-row identity'; END IF;
  INSERT INTO d5.review_items(comparison_id,source_key,row_sha256,change,row_bytes) VALUES(cid,item->>'source_key',(item->>'row_sha256')::d5.hash,item->>'change',rowbytes);
  INSERT INTO d5.row_review_heads(comparison_id,source_key,row_sha256) VALUES(cid,item->>'source_key',(item->>'row_sha256')::d5.hash);
 END LOOP;
 RETURN d5.review_finish(req,jsonb_build_object('status','OK','comparison_id',cid,'report_sha256',ph,'comparison_state',val->>'state','review_item_count',jsonb_array_length(val->'review_items')));
END $$;

CREATE FUNCTION d5.read_comparison(pid uuid,doc uuid,cid uuid) RETURNS jsonb LANGUAGE sql STABLE SECURITY DEFINER SET search_path=pg_catalog,pg_temp AS $$
 SELECT jsonb_build_object('comparison_id',c.comparison_id,'report_sha256',r.report_sha256,'report_hex',encode(r.report_bytes,'hex'))
 FROM d5.comparisons c JOIN d5.comparison_reports r USING(report_sha256) WHERE c.comparison_id=cid AND r.project_id=pid AND r.document_id=doc $$;
CREATE FUNCTION d5.read_row_review(pid uuid,doc uuid,cid uuid,key text) RETURNS jsonb LANGUAGE sql STABLE SECURITY DEFINER SET search_path=pg_catalog,pg_temp AS $$
 SELECT jsonb_build_object('comparison_id',h.comparison_id,'source_key',h.source_key,'row_sha256',h.row_sha256,'version',h.version,'decision_command_id',h.decision_command_id,'decision',d.decision)
 FROM d5.row_review_heads h JOIN d5.comparisons c USING(comparison_id) JOIN d5.comparison_reports r USING(report_sha256)
 LEFT JOIN d5.row_decisions d ON d.command_id=h.decision_command_id
 WHERE h.comparison_id=cid AND h.source_key=key AND r.project_id=pid AND r.document_id=doc $$;

CREATE FUNCTION d5.decide_row(envelope json) RETURNS jsonb LANGUAGE plpgsql VOLATILE SECURITY DEFINER SET search_path=pg_catalog,pg_temp AS $$
DECLARE req jsonb; prior jsonb; cid uuid; cmp uuid; report d5.comparison_reports; head d5.row_review_heads; wanted bigint;
BEGIN
 req=d5.review_envelope(envelope,'DECIDE_ROW',ARRAY['comparison_id','report_sha256','source_key','row_sha256','expected_version','decision','reviewer_label','reason'],ARRAY['expected_version']);
 cid=(req->>'command_id')::uuid;cmp=(req->>'comparison_id')::uuid;wanted=d5.review_version(req->'expected_version');
 IF req->>'decision' NOT IN ('ACCEPT','REJECT') OR length(req->>'reviewer_label') NOT BETWEEN 1 AND 256 OR req->>'reviewer_label' ~ '[[:cntrl:]]'
  OR length(req->>'reason') NOT BETWEEN 1 AND 1024 OR req->>'reason' ~ '[[:cntrl:]]' THEN RAISE EXCEPTION 'Invalid decision metadata'; END IF;
 prior=d5.review_prior(req);IF prior IS NOT NULL THEN RETURN prior; END IF;
 SELECT r.* INTO report FROM d5.comparisons c JOIN d5.comparison_reports r USING(report_sha256) WHERE c.comparison_id=cmp;
 IF NOT FOUND OR report.project_id<>(req->>'project_id')::uuid OR report.document_id<>(req->>'document_id')::uuid OR report.report_sha256 IS DISTINCT FROM req->>'report_sha256'
  THEN RETURN d5.review_finish(req,jsonb_build_object('status','CONFLICT','code','COMPARISON_SCOPE_CONFLICT')); END IF;
 IF report.state<>'PREVIEW_ONLY' THEN RETURN d5.review_finish(req,jsonb_build_object('status','CONFLICT','code','COMPARISON_BLOCKED')); END IF;
 SELECT * INTO head FROM d5.row_review_heads WHERE comparison_id=cmp AND source_key=req->>'source_key' FOR UPDATE;
 IF NOT FOUND OR head.row_sha256 IS DISTINCT FROM req->>'row_sha256' THEN RETURN d5.review_finish(req,jsonb_build_object('status','CONFLICT','code','ROW_SCOPE_CONFLICT')); END IF;
 IF head.version<>wanted THEN RETURN d5.review_finish(req,jsonb_build_object('status','CONFLICT','code','DECISION_VERSION_CONFLICT')); END IF;
 INSERT INTO d5.row_decisions(command_id,comparison_id,source_key,row_sha256,decision,version,reviewer_label,reason) VALUES(cid,cmp,head.source_key,head.row_sha256,req->>'decision',head.version+1,req->>'reviewer_label',req->>'reason');
 UPDATE d5.row_review_heads SET version=version+1,decision_command_id=cid WHERE comparison_id=cmp AND source_key=head.source_key;
 RETURN d5.review_finish(req,jsonb_build_object('status','OK','comparison_id',cmp,'source_key',head.source_key,'row_sha256',head.row_sha256,'decision',req->>'decision','version_at_commit',head.version+1));
END $$;

CREATE FUNCTION d5.simulate_application(envelope json) RETURNS jsonb LANGUAGE plpgsql VOLATILE SECURITY DEFINER SET search_path=pg_catalog,pg_temp AS $$
DECLARE req jsonb; prior jsonb; cid uuid; cmp uuid; report d5.comparison_reports; ref d5.reference_heads; wanted bigint;
 item jsonb; keys text[]; head d5.row_review_heads; decision d5.row_decisions; row d5.review_items; actions jsonb='[]'::jsonb; result jsonb; code text;
BEGIN
 req=d5.review_envelope(envelope,'SIMULATE_APPLICATION',ARRAY['comparison_id','report_sha256','expected_reference_version','items'],ARRAY['expected_reference_version','items']);
 cid=(req->>'command_id')::uuid;cmp=(req->>'comparison_id')::uuid;wanted=d5.review_version(req->'expected_reference_version');
 IF jsonb_typeof(req->'items') IS DISTINCT FROM 'array' OR jsonb_array_length(req->'items') NOT BETWEEN 1 AND 2000 THEN RAISE EXCEPTION 'Explicit nonempty items required'; END IF;
 FOR item IN SELECT * FROM jsonb_array_elements(req->'items') LOOP
  IF jsonb_typeof(item)<>'object' THEN RAISE EXCEPTION 'Item object required'; END IF;
  SELECT array_agg(k ORDER BY k) INTO keys FROM jsonb_object_keys(item) k;
  IF keys IS DISTINCT FROM ARRAY['decision_command_id','expected_version','row_sha256','source_key']
   OR jsonb_typeof(item->'source_key') IS DISTINCT FROM 'string' OR jsonb_typeof(item->'row_sha256') IS DISTINCT FROM 'string'
   OR jsonb_typeof(item->'decision_command_id') IS DISTINCT FROM 'string'
   OR (item->>'decision_command_id')::uuid::text IS DISTINCT FROM item->>'decision_command_id' THEN RAISE EXCEPTION 'Closed decision pin required'; END IF;
  PERFORM d5.review_version(item->'expected_version');
 END LOOP;
 IF EXISTS(SELECT FROM jsonb_array_elements(req->'items') i GROUP BY i->>'source_key' HAVING count(*)>1) THEN RAISE EXCEPTION 'Duplicate row pin'; END IF;
 IF req->'items' IS DISTINCT FROM (SELECT jsonb_agg(i ORDER BY (i->>'source_key') COLLATE "C") FROM jsonb_array_elements(req->'items') i) THEN RAISE EXCEPTION 'Items must be sorted'; END IF;
 prior=d5.review_prior(req);IF prior IS NOT NULL THEN RETURN prior; END IF;
 SELECT r.* INTO report FROM d5.comparisons c JOIN d5.comparison_reports r USING(report_sha256) WHERE c.comparison_id=cmp;
 IF NOT FOUND OR report.project_id<>(req->>'project_id')::uuid OR report.document_id<>(req->>'document_id')::uuid OR report.report_sha256 IS DISTINCT FROM req->>'report_sha256' THEN code='COMPARISON_SCOPE_CONFLICT';
 ELSIF report.state<>'PREVIEW_ONLY' THEN code='COMPARISON_BLOCKED';
 ELSE
  SELECT * INTO STRICT ref FROM d5.reference_heads WHERE document_id=report.document_id AND profile=report.profile FOR SHARE;
  IF ref.version<>wanted OR ref.observation_id IS DISTINCT FROM report.before_observation_id THEN code='REFERENCE_VERSION_CONFLICT'; END IF;
 END IF;
 IF code IS NULL THEN
  FOR item IN SELECT * FROM jsonb_array_elements(req->'items') LOOP
   SELECT * INTO head FROM d5.row_review_heads WHERE comparison_id=cmp AND source_key=item->>'source_key' FOR SHARE;
   IF NOT FOUND OR head.row_sha256 IS DISTINCT FROM item->>'row_sha256' OR head.version<>d5.review_version(item->'expected_version') OR head.decision_command_id IS DISTINCT FROM (item->>'decision_command_id')::uuid THEN code='DECISION_VERSION_CONFLICT';EXIT; END IF;
   SELECT * INTO STRICT decision FROM d5.row_decisions WHERE command_id=head.decision_command_id;
   IF decision.decision<>'ACCEPT' THEN code='ROW_NOT_ACCEPTED';EXIT; END IF;
   SELECT * INTO STRICT row FROM d5.review_items WHERE comparison_id=cmp AND source_key=head.source_key;
   actions=actions||jsonb_build_array(jsonb_build_object('source_key',row.source_key,'row_sha256',row.row_sha256,'decision_command_id',decision.command_id,'decision_version',head.version,
    'operation',CASE row.change WHEN 'ADDED' THEN 'STAGE_SOURCE_ADDITION' WHEN 'CHANGED' THEN 'STAGE_SOURCE_CHANGE' ELSE 'KEEP_EXISTING_NO_DELETE' END,'operational_effect',false));
  END LOOP;
 END IF;
 result=jsonb_build_object('status',CASE WHEN code IS NULL THEN 'OK' ELSE 'CONFLICT' END,'code',code,'simulation_only',true,'writes_d2',false,'activation_allowed',false);
 IF code IS NULL THEN
  result=result||jsonb_build_object('comparison_id',cmp,'report_sha256',report.report_sha256,'reference_version_at_commit',ref.version,'before_observation_id',report.before_observation_id,'after_observation_id',report.after_observation_id,'actions',actions);
  INSERT INTO d5.simulations VALUES(cid,cmp,ref.version,result);
 END IF;
 RETURN d5.review_finish(req,result);
END $$;
REVOKE ALL ON ALL TABLES IN SCHEMA d5 FROM PUBLIC,d5_writer,d5_reader,d5_reviewer;
REVOKE ALL ON ALL FUNCTIONS IN SCHEMA d5 FROM PUBLIC,d5_reviewer;
GRANT USAGE ON SCHEMA d5 TO d5_reviewer;
GRANT EXECUTE ON FUNCTION d5.read_comparison_sources(uuid,uuid,uuid,uuid),d5.read_comparison(uuid,uuid,uuid),d5.read_row_review(uuid,uuid,uuid,text) TO d5_writer,d5_reader,d5_reviewer;
GRANT EXECUTE ON FUNCTION d5.save_comparison(json,bytea) TO d5_writer;
GRANT EXECUTE ON FUNCTION d5.decide_row(json),d5.simulate_application(json) TO d5_reviewer;
GRANT EXECUTE ON FUNCTION d5.read_command(uuid),d5.read_reference(uuid,uuid,d5.profile),d5.read_observation(uuid,uuid,uuid) TO d5_reviewer;
COMMIT;
