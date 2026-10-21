-- SPDX-License-Identifier: GPL-3.0-only
-- D5 synthetic proposal only. Requires V1-V11 and pre-created d5_owner/writer/reader.
-- No promotion, provider connection, backfill or changes to D1-D4 contracts.
BEGIN;
CREATE SCHEMA d5 AUTHORIZATION d5_owner;
GRANT USAGE ON SCHEMA public TO d5_owner;
GRANT SELECT ON public.projects,public.source_documents,public.source_revisions TO d5_owner;
GRANT INSERT,REFERENCES ON public.source_documents,public.source_revisions TO d5_owner;
-- Needed for SELECT FOR SHARE, never exposed to callers.
GRANT UPDATE(id) ON public.source_documents TO d5_owner;
SET LOCAL ROLE d5_owner;
ALTER DEFAULT PRIVILEGES REVOKE EXECUTE ON FUNCTIONS FROM PUBLIC;
CREATE DOMAIN d5.profile AS text CHECK(VALUE IN
 ('markdown-structure.v1','task-register.v1','task-register-compat.v1'));
CREATE DOMAIN d5.hash AS text CHECK(VALUE ~ '^[a-f0-9]{64}$');
CREATE FUNCTION d5.identity_label(value text) RETURNS boolean LANGUAGE sql IMMUTABLE STRICT
 SET search_path=pg_catalog,pg_temp AS $$
 SELECT octet_length(value) BETWEEN 1 AND 256 AND value !~ '[[:cntrl:]]'
 AND value=btrim(value,U&'\0009\000A\000B\000C\000D\0020\0085\00A0\1680\2000\2001\2002\2003\2004\2005\2006\2007\2008\2009\200A\2028\2029\202F\205F\3000') $$;
CREATE TABLE d5.commands(
 command_id uuid PRIMARY KEY, request jsonb NOT NULL, request_sha256 d5.hash NOT NULL,
 response jsonb NOT NULL, committed_at timestamptz NOT NULL DEFAULT clock_timestamp(),
 CHECK(request_sha256=encode(public.digest('d5.source-command.v1:'||request::text,'sha256'),'hex'))
);
CREATE TABLE d5.source_registrations(
 document_id uuid PRIMARY KEY, project_id uuid NOT NULL,
 namespace text COLLATE "C" NOT NULL, logical_key text COLLATE "C" NOT NULL,
 command_id uuid NOT NULL UNIQUE REFERENCES d5.commands DEFERRABLE INITIALLY DEFERRED,
 UNIQUE(project_id,namespace,logical_key), UNIQUE(document_id,project_id),
 FOREIGN KEY(document_id,project_id) REFERENCES public.source_documents(id,project_id),
 CHECK(d5.identity_label(namespace)),
 CHECK(d5.identity_label(logical_key))
);
CREATE TABLE d5.revision_content(
 document_id uuid NOT NULL REFERENCES d5.source_registrations,
 sha256 d5.hash NOT NULL, revision_id uuid NOT NULL, source_bytes bytea NOT NULL,
 PRIMARY KEY(document_id,sha256), UNIQUE(revision_id,document_id),
 FOREIGN KEY(revision_id,document_id) REFERENCES public.source_revisions(id,document_id),
 CHECK(octet_length(source_bytes)<=2097152),
 CHECK(sha256=encode(public.digest(source_bytes,'sha256'),'hex'))
);
CREATE TABLE d5.preview_artifacts(
 preview_sha256 d5.hash PRIMARY KEY, document_id uuid NOT NULL, project_id uuid NOT NULL,
 revision_id uuid NOT NULL, profile d5.profile NOT NULL, preview_bytes bytea NOT NULL,
 UNIQUE(preview_sha256,document_id,project_id,revision_id,profile),
 FOREIGN KEY(document_id,project_id) REFERENCES d5.source_registrations(document_id,project_id),
 FOREIGN KEY(revision_id,document_id) REFERENCES d5.revision_content(revision_id,document_id),
 CHECK(octet_length(preview_bytes)<=33554432),
 CHECK(preview_sha256=encode(public.digest(preview_bytes,'sha256'),'hex'))
);
CREATE TABLE d5.observations(
 observation_id uuid PRIMARY KEY REFERENCES d5.commands(command_id) DEFERRABLE INITIALLY DEFERRED,
 preview_sha256 d5.hash NOT NULL, document_id uuid NOT NULL, project_id uuid NOT NULL,
 revision_id uuid NOT NULL, profile d5.profile NOT NULL,
 caller_label text NOT NULL, source_path text NOT NULL,
 revision_authority text NOT NULL CHECK(revision_authority='CALLER_LABEL_ONLY'),
 ingested_at timestamptz NOT NULL DEFAULT clock_timestamp(),
 UNIQUE(observation_id,document_id,project_id,profile),
 FOREIGN KEY(preview_sha256,document_id,project_id,revision_id,profile)
  REFERENCES d5.preview_artifacts(preview_sha256,document_id,project_id,revision_id,profile)
);
CREATE TABLE d5.reference_heads(
 document_id uuid NOT NULL, project_id uuid NOT NULL, profile d5.profile NOT NULL,
 observation_id uuid, version bigint NOT NULL DEFAULT 0 CHECK(version>=0),
 PRIMARY KEY(document_id,profile), UNIQUE(document_id,project_id,profile),
 FOREIGN KEY(document_id,project_id) REFERENCES d5.source_registrations(document_id,project_id),
 FOREIGN KEY(observation_id,document_id,project_id,profile)
  REFERENCES d5.observations(observation_id,document_id,project_id,profile),
 CHECK((version=0 AND observation_id IS NULL) OR (version>0 AND observation_id IS NOT NULL))
);
CREATE TABLE d5.reference_selections(
 command_id uuid PRIMARY KEY REFERENCES d5.commands DEFERRABLE INITIALLY DEFERRED,
 document_id uuid NOT NULL, project_id uuid NOT NULL, profile d5.profile NOT NULL,
 before_observation_id uuid, after_observation_id uuid NOT NULL,
 before_version bigint NOT NULL CHECK(before_version>=0), after_version bigint NOT NULL,
 reason text NOT NULL CHECK(length(reason) BETWEEN 1 AND 1024 AND reason !~ '[[:cntrl:]]'),
 FOREIGN KEY(document_id,project_id,profile) REFERENCES d5.reference_heads(document_id,project_id,profile),
 FOREIGN KEY(before_observation_id,document_id,project_id,profile) REFERENCES d5.observations(observation_id,document_id,project_id,profile),
 FOREIGN KEY(after_observation_id,document_id,project_id,profile) REFERENCES d5.observations(observation_id,document_id,project_id,profile),
 CHECK(after_version>0 AND after_version-1=before_version)
);
CREATE FUNCTION d5.immutable() RETURNS trigger LANGUAGE plpgsql SET search_path=pg_catalog,pg_temp AS $$
BEGIN RAISE EXCEPTION 'D5 fact is immutable' USING ERRCODE='55000'; END $$;
DO $$ DECLARE rel text; BEGIN
 FOREACH rel IN ARRAY ARRAY['commands','source_registrations','revision_content','preview_artifacts','observations','reference_selections'] LOOP
  EXECUTE format('CREATE TRIGGER immutable BEFORE UPDATE OR DELETE OR TRUNCATE ON d5.%I FOR EACH STATEMENT EXECUTE FUNCTION d5.immutable()',rel);
 END LOOP;
END $$;
-- Guard content linkage even for owner fixture inserts (parser semantics remain in adapter).
CREATE FUNCTION d5.content_guard() RETURNS trigger LANGUAGE plpgsql SET search_path=pg_catalog,pg_temp AS $$
BEGIN
 IF NOT EXISTS(SELECT FROM public.source_revisions r WHERE r.id=NEW.revision_id AND r.document_id=NEW.document_id
  AND r.sha256=NEW.sha256 AND r.external_revision IS NULL
  AND r.content_ref='d5:content:'||NEW.document_id::text||':sha256:'||NEW.sha256) THEN
  RAISE EXCEPTION 'D5 revision metadata mismatch' USING ERRCODE='23514'; END IF;
 RETURN NEW;
END $$;
CREATE TRIGGER content_guard BEFORE INSERT ON d5.revision_content FOR EACH ROW EXECUTE FUNCTION d5.content_guard();

CREATE FUNCTION d5.submit(envelope json, source bytea DEFAULT NULL, artifact bytea DEFAULT NULL) RETURNS jsonb
LANGUAGE plpgsql VOLATILE SECURITY DEFINER SET search_path=pg_catalog,pg_temp AS $$
DECLARE
 req jsonb; keys text[]; expected text[]; field text; act text; cid uuid; pid uuid; doc uuid;
 prior d5.commands; reg d5.source_registrations; pub public.source_documents;
 head d5.reference_heads; content d5.revision_content; stored d5.preview_artifacts;
 val jsonb; result jsonb; status text='OK'; code text; rid uuid; oid uuid; prof d5.profile;
 wanted bigint; ch d5.hash; ph d5.hash; label text; path text;
BEGIN
 IF current_setting('transaction_isolation')<>'read committed' THEN
  RAISE EXCEPTION 'D5 requires READ COMMITTED' USING ERRCODE='25001'; END IF;
 IF envelope IS NULL OR json_typeof(envelope)<>'object' THEN RAISE EXCEPTION 'Object envelope required'; END IF;
 IF EXISTS(SELECT FROM json_each(envelope) GROUP BY key HAVING count(*)>1) THEN RAISE EXCEPTION 'Duplicate envelope key'; END IF;
 req=envelope::jsonb; act=req->>'action';
 expected=ARRAY['schema','command_id','action','project_id','document_id'];
 CASE act
 WHEN 'REGISTER_SOURCE' THEN expected=expected||ARRAY['namespace','logical_key'];
 WHEN 'INGEST' THEN expected=expected||ARRAY['preview_sha256','content_sha256','profile'];
 WHEN 'SELECT_REFERENCE' THEN expected=expected||ARRAY['profile','observation_id','expected_version','reason'];
 ELSE RAISE EXCEPTION 'Unknown D5 action'; END CASE;
 SELECT array_agg(k ORDER BY k) INTO keys FROM jsonb_object_keys(req) k;
 SELECT array_agg(k ORDER BY k) INTO expected FROM unnest(expected) k;
 IF keys IS DISTINCT FROM expected OR req->>'schema' IS DISTINCT FROM 'd5.source-command.v1' THEN RAISE EXCEPTION 'Closed envelope required'; END IF;
 FOREACH field IN ARRAY expected LOOP
  IF field<>'expected_version' AND jsonb_typeof(req->field) IS DISTINCT FROM 'string' THEN RAISE EXCEPTION 'String field required: %',field; END IF;
 END LOOP;
 FOREACH field IN ARRAY ARRAY['command_id','project_id','document_id'] LOOP
  IF (req->>field)::uuid::text IS DISTINCT FROM req->>field THEN RAISE EXCEPTION 'Canonical UUID required'; END IF;
 END LOOP;
 cid=(req->>'command_id')::uuid;pid=(req->>'project_id')::uuid;doc=(req->>'document_id')::uuid;
 IF act='REGISTER_SOURCE' THEN
  FOREACH field IN ARRAY ARRAY['namespace','logical_key'] LOOP
   IF NOT d5.identity_label(req->>field) THEN RAISE EXCEPTION 'Invalid identity label'; END IF;
  END LOOP;
 ELSE prof=(req->>'profile')::d5.profile; END IF;
 IF act='SELECT_REFERENCE' THEN
  IF jsonb_typeof(req->'expected_version') IS DISTINCT FROM 'number' OR req->>'expected_version' !~ '^(0|[1-9][0-9]*)$' THEN RAISE EXCEPTION 'Integer version required'; END IF;
  wanted=(req->>'expected_version')::bigint;oid=(req->>'observation_id')::uuid;
  IF oid::text IS DISTINCT FROM req->>'observation_id' OR length(req->>'reason') NOT BETWEEN 1 AND 1024 OR req->>'reason' ~ '[[:cntrl:]]' THEN RAISE EXCEPTION 'Invalid selection'; END IF;
 END IF;
 IF act='INGEST' THEN
  IF source IS NULL OR artifact IS NULL OR octet_length(source)>2097152 OR octet_length(artifact)>33554432 THEN RAISE EXCEPTION 'Blob limit or missing blob'; END IF;
  ch=(req->>'content_sha256')::d5.hash;ph=(req->>'preview_sha256')::d5.hash;
  IF ch IS DISTINCT FROM encode(public.digest(source,'sha256'),'hex') OR ph IS DISTINCT FROM encode(public.digest(artifact,'sha256'),'hex') THEN RAISE EXCEPTION 'Blob hash mismatch'; END IF;
  val=convert_from(artifact,'UTF8')::jsonb;
  IF jsonb_typeof(val) IS DISTINCT FROM 'object' OR val->>'project_id' IS DISTINCT FROM pid::text
   OR val->>'document_id' IS DISTINCT FROM doc::text OR val->>'profile' IS DISTINCT FROM prof::text
   OR val->>'content_sha256' IS DISTINCT FROM ch::text OR val->'content_bytes' IS DISTINCT FROM to_jsonb(octet_length(source))
   OR jsonb_typeof(val->'content_base64') IS DISTINCT FROM 'string'
   OR octet_length(val->>'content_base64')>2796204
   OR val->>'state' IS DISTINCT FROM 'PREVIEW_ONLY' OR val->'activation_allowed' IS DISTINCT FROM 'false'::jsonb
   OR val->>'source_kind' IS DISTINCT FROM 'LOCAL_MARKDOWN'
   OR val->>'revision_authority' IS DISTINCT FROM 'CALLER_LABEL_ONLY'
   OR val->>'schema' IS DISTINCT FROM (CASE WHEN prof='markdown-structure.v1' THEN 'd5.local-preview.v1' ELSE 'd5.local-preview.v2' END)
   THEN RAISE EXCEPTION 'Artifact scope or metadata mismatch'; END IF;
  IF decode(val->>'content_base64','base64') IS DISTINCT FROM source THEN RAISE EXCEPTION 'Embedded bytes mismatch'; END IF;
  label=val->>'observed_revision';path=val->>'source_path';
  IF jsonb_typeof(val->'observed_revision') IS DISTINCT FROM 'string' OR length(label) NOT BETWEEN 1 AND 256 OR label ~ '[[:cntrl:]]'
   OR jsonb_typeof(val->'source_path') IS DISTINCT FROM 'string' OR path !~ '\.([mM][dD])$'
   OR path ~ '(^/|\\|(^|/)(\.|\.\.)(/|$)|//)' THEN RAISE EXCEPTION 'Invalid provenance'; END IF;
 ELSE
  IF source IS NOT NULL OR artifact IS NOT NULL THEN RAISE EXCEPTION 'Unexpected blobs'; END IF;
 END IF;
 -- Dedicated D5 lock, separate from D2 742002 and D3 742001.
 PERFORM pg_advisory_xact_lock(742005);
 SELECT * INTO prior FROM d5.commands WHERE command_id=cid;
 IF FOUND THEN
  IF prior.request IS DISTINCT FROM req THEN
   RETURN jsonb_build_object('status','CONFLICT','code','COMMAND_CONTENT_CONFLICT','command_id',cid,'receipt_only',true,'activation_allowed',false);
  END IF;
  IF act='INGEST' AND prior.response->>'status'='OK' THEN
   SELECT * INTO STRICT stored FROM d5.preview_artifacts WHERE preview_sha256=ph;
   SELECT * INTO STRICT content FROM d5.revision_content WHERE revision_id=stored.revision_id;
   IF stored.preview_bytes IS DISTINCT FROM artifact OR content.source_bytes IS DISTINCT FROM source THEN RAISE EXCEPTION 'Stored blob identity mismatch'; END IF;
  END IF;
  RETURN prior.response;
 END IF;
 SELECT * INTO reg FROM d5.source_registrations WHERE document_id=doc;
 SELECT * INTO pub FROM public.source_documents WHERE id=doc FOR SHARE;
 IF reg.document_id IS NOT NULL AND (reg.project_id<>pid OR pub.project_id IS DISTINCT FROM pid
  OR pub.source_type IS DISTINCT FROM 'OTHER' OR pub.source_uri IS DISTINCT FROM 'urn:weekly-ai-work-planner:d5:source:'||doc::text
  OR pub.current_revision_id IS NOT NULL) THEN code='IDENTITY_CONFLICT'; END IF;
 IF act='REGISTER_SOURCE' AND code IS NULL THEN
  IF reg.document_id IS NOT NULL THEN
   IF reg.namespace IS DISTINCT FROM req->>'namespace' OR reg.logical_key IS DISTINCT FROM req->>'logical_key' THEN code='IDENTITY_CONFLICT'; END IF;
  ELSIF pub.id IS NOT NULL THEN code='ADOPTION_REQUIRED';
  ELSIF EXISTS(SELECT FROM d5.source_registrations WHERE project_id=pid AND namespace=req->>'namespace' AND logical_key=req->>'logical_key')
    OR EXISTS(SELECT FROM public.source_documents WHERE source_type='OTHER' AND source_uri='urn:weekly-ai-work-planner:d5:source:'||doc::text) THEN code='IDENTITY_CONFLICT';
  ELSE
   INSERT INTO public.source_documents(id,project_id,source_type,source_uri) VALUES(doc,pid,'OTHER','urn:weekly-ai-work-planner:d5:source:'||doc::text);
   INSERT INTO d5.source_registrations VALUES(doc,pid,req->>'namespace',req->>'logical_key',cid);
   INSERT INTO d5.reference_heads(document_id,project_id,profile)
    SELECT doc,pid,p::d5.profile FROM unnest(ARRAY['markdown-structure.v1','task-register.v1','task-register-compat.v1']) p;
  END IF;
 ELSIF reg.document_id IS NULL AND code IS NULL THEN code='SOURCE_NOT_REGISTERED'; END IF;
 IF code IS NULL AND act='INGEST' THEN
  SELECT * INTO content FROM d5.revision_content WHERE document_id=doc AND sha256=ch;
  IF FOUND THEN
   IF content.source_bytes IS DISTINCT FROM source THEN RAISE EXCEPTION 'Content collision'; END IF;
   rid=content.revision_id;
  ELSE
   rid=gen_random_uuid();
   INSERT INTO public.source_revisions(id,document_id,sha256,content_ref) VALUES(rid,doc,ch,'d5:content:'||doc::text||':sha256:'||ch);
   INSERT INTO d5.revision_content VALUES(doc,ch,rid,source);
  END IF;
  SELECT * INTO stored FROM d5.preview_artifacts WHERE preview_sha256=ph;
  IF FOUND THEN
   IF stored.preview_bytes IS DISTINCT FROM artifact OR stored.document_id<>doc OR stored.project_id<>pid OR stored.revision_id<>rid OR stored.profile<>prof THEN RAISE EXCEPTION 'Artifact collision'; END IF;
  ELSE INSERT INTO d5.preview_artifacts VALUES(ph,doc,pid,rid,prof,artifact); END IF;
  INSERT INTO d5.observations(observation_id,preview_sha256,document_id,project_id,revision_id,profile,caller_label,source_path,revision_authority)
   VALUES(cid,ph,doc,pid,rid,prof,label,path,'CALLER_LABEL_ONLY');
 ELSIF code IS NULL AND act='SELECT_REFERENCE' THEN
  SELECT * INTO STRICT head FROM d5.reference_heads WHERE document_id=doc AND profile=prof FOR UPDATE;
  IF NOT EXISTS(SELECT FROM d5.observations WHERE observation_id=oid AND document_id=doc AND project_id=pid AND profile=prof) THEN code='OBSERVATION_SCOPE_CONFLICT';
  ELSIF head.version<>wanted THEN code='VERSION_CONFLICT';
  ELSE
   UPDATE d5.reference_heads SET observation_id=oid,version=version+1 WHERE document_id=doc AND profile=prof;
   INSERT INTO d5.reference_selections VALUES(cid,doc,pid,prof,head.observation_id,oid,head.version,head.version+1,req->>'reason');
  END IF;
 END IF;
 IF code IS NOT NULL THEN status='CONFLICT'; END IF;
 result=jsonb_build_object('status',status,'code',code,'command_id',cid,'action',act,'project_id',pid,'document_id',doc,'receipt_only',true,'activation_allowed',false);
 IF status='OK' AND act='INGEST' THEN result=result||jsonb_build_object('observation_id',cid,'revision_id',rid,'preview_sha256',ph); END IF;
 IF status='OK' AND act='SELECT_REFERENCE' THEN result=result||jsonb_build_object('observation_id',oid,'profile',prof,'version_at_commit',head.version+1); END IF;
 INSERT INTO d5.commands(command_id,request,request_sha256,response) VALUES(cid,req,encode(public.digest('d5.source-command.v1:'||req::text,'sha256'),'hex'),result);
 RETURN result;
END $$;

CREATE FUNCTION d5.read_command(cid uuid) RETURNS jsonb LANGUAGE sql STABLE SECURITY DEFINER
 SET search_path=pg_catalog,pg_temp AS $$ SELECT response FROM d5.commands WHERE command_id=cid $$;
CREATE FUNCTION d5.read_reference(pid uuid,doc uuid,prof d5.profile) RETURNS jsonb LANGUAGE sql STABLE SECURITY DEFINER
 SET search_path=pg_catalog,pg_temp AS $$
 SELECT jsonb_build_object('document_id',h.document_id,'project_id',h.project_id,'profile',h.profile,
  'observation_id',h.observation_id,'version',h.version,'preview_sha256',o.preview_sha256,'activation_allowed',false)
 FROM d5.reference_heads h LEFT JOIN d5.observations o ON o.observation_id=h.observation_id
 WHERE h.document_id=doc AND h.project_id=pid AND h.profile=prof $$;
CREATE FUNCTION d5.read_observation(pid uuid,doc uuid,oid uuid) RETURNS jsonb LANGUAGE sql STABLE SECURITY DEFINER
 SET search_path=pg_catalog,pg_temp AS $$
 SELECT jsonb_build_object('preview_sha256',a.preview_sha256,'preview_hex',encode(a.preview_bytes,'hex'),
  'content_sha256',c.sha256,'source_hex',encode(c.source_bytes,'hex'),'observation_id',o.observation_id)
 FROM d5.observations o JOIN d5.preview_artifacts a USING(preview_sha256)
 JOIN d5.revision_content c ON c.revision_id=o.revision_id
 WHERE o.observation_id=oid AND o.document_id=doc AND o.project_id=pid $$;
REVOKE ALL ON ALL TABLES IN SCHEMA d5 FROM PUBLIC,d5_writer,d5_reader;
REVOKE ALL ON ALL FUNCTIONS IN SCHEMA d5 FROM PUBLIC,d5_writer,d5_reader;
GRANT USAGE ON SCHEMA d5 TO d5_writer,d5_reader;
GRANT EXECUTE ON FUNCTION d5.submit(json,bytea,bytea) TO d5_writer;
GRANT EXECUTE ON FUNCTION d5.read_command(uuid),d5.read_reference(uuid,uuid,d5.profile),d5.read_observation(uuid,uuid,uuid) TO d5_writer,d5_reader;
COMMIT;
