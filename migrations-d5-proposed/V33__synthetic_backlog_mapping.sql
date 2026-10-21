-- SPDX-License-Identifier: GPL-3.0-only
-- I8: disposable V30 + V31/V32 ONLY. No promotion or operational activation.
-- Requires separately pre-created d5_apply_owner NOLOGIN and d5_applier lab roles.
BEGIN;
GRANT USAGE,CREATE ON SCHEMA d5 TO d5_apply_owner;
GRANT USAGE ON SCHEMA public,d2 TO d5_apply_owner;
GRANT SELECT ON d5.commands,d5.source_registrations,d5.comparisons,d5.comparison_reports,d5.review_items,d5.row_review_heads,d5.row_decisions,d5.reference_heads,d5.observations TO d5_apply_owner;
GRANT INSERT ON d5.commands TO d5_apply_owner;
GRANT SELECT ON public.tasks,public.operations,public.schedule_entries,public.source_documents,public.source_revisions,d2.task_sources TO d5_apply_owner;
GRANT INSERT ON public.tasks,d2.task_sources,public.audit_events TO d5_apply_owner;
GRANT UPDATE(title,description,row_version) ON public.tasks TO d5_apply_owner;
GRANT REFERENCES ON public.tasks,d5.source_registrations,d5.commands TO d5_apply_owner;
GRANT EXECUTE ON FUNCTION d5.review_envelope(json,text,text[],text[]),d5.review_version(jsonb),d5.review_prior(jsonb),d5.review_finish(jsonb,jsonb),d5.immutable() TO d5_apply_owner;
-- Owned by the trusted migration administrator, NOT by the caller/apply owner.
CREATE FUNCTION d5.task_lock_boundary() RETURNS void LANGUAGE plpgsql VOLATILE SECURITY DEFINER
 SET search_path=pg_catalog,pg_temp AS $$
BEGIN
 IF current_setting('transaction_isolation')<>'read committed' THEN RAISE EXCEPTION 'READ COMMITTED required'; END IF;
 PERFORM d3.lock_state();
 PERFORM pg_advisory_xact_lock(742005);
END $$;
REVOKE ALL ON FUNCTION d5.task_lock_boundary() FROM PUBLIC;
GRANT EXECUTE ON FUNCTION d5.task_lock_boundary() TO d5_apply_owner;
GRANT USAGE ON SCHEMA d5 TO d5_applier;
SET LOCAL ROLE d5_apply_owner;
ALTER DEFAULT PRIVILEGES REVOKE EXECUTE ON FUNCTIONS FROM PUBLIC;
CREATE TABLE d5.task_intents(
 intent_id uuid PRIMARY KEY REFERENCES d5.commands DEFERRABLE INITIALLY DEFERRED,
 project_id uuid NOT NULL,document_id uuid NOT NULL,source_key text COLLATE "C" NOT NULL,
 source_key_sha256 text GENERATED ALWAYS AS (encode(public.digest(source_key,'sha256'),'hex')) STORED,
 profile d5.profile NOT NULL CHECK(profile<>'markdown-structure.v1'),
 policy text NOT NULL CHECK(policy='d5.task-projection.v1'),
 task_id uuid NOT NULL UNIQUE,task_key text COLLATE "C" NOT NULL,
 UNIQUE(document_id,source_key_sha256),UNIQUE(project_id,task_key),UNIQUE(intent_id,task_id,project_id),
 FOREIGN KEY(document_id,project_id) REFERENCES d5.source_registrations(document_id,project_id),
 CHECK(source_key ~ '^[A-Z][A-Z0-9_]*-[0-9]+$'),CHECK(length(task_key) BETWEEN 1 AND 256 AND task_key !~ '[[:cntrl:]]')
);
CREATE TABLE d5.task_mapping_heads(
 intent_id uuid PRIMARY KEY REFERENCES d5.task_intents,version bigint NOT NULL DEFAULT 0 CHECK(version>=0),
 source_basis jsonb,projection jsonb,
 CHECK((version=0 AND source_basis IS NULL AND projection IS NULL) OR version>0)
);
CREATE TABLE d5.task_destinations(
 intent_id uuid PRIMARY KEY,task_id uuid NOT NULL UNIQUE,project_id uuid NOT NULL,
 FOREIGN KEY(intent_id,task_id,project_id) REFERENCES d5.task_intents(intent_id,task_id,project_id),
 FOREIGN KEY(task_id,project_id) REFERENCES public.tasks(id,project_id)
);
CREATE TABLE d5.task_proposals(
 proposal_id uuid PRIMARY KEY REFERENCES d5.commands DEFERRABLE INITIALLY DEFERRED,
 manifest_sha256 d5.hash NOT NULL,manifest jsonb NOT NULL,
 CHECK(octet_length(manifest::text)<=4194304)
);
CREATE TABLE d5.task_proposal_reviews(
 command_id uuid PRIMARY KEY REFERENCES d5.commands DEFERRABLE INITIALLY DEFERRED,
 proposal_id uuid NOT NULL REFERENCES d5.task_proposals,version bigint NOT NULL CHECK(version>0),
 decision text NOT NULL CHECK(decision IN ('ACCEPT','REJECT')),reviewer_label text NOT NULL,reason text NOT NULL,
 UNIQUE(proposal_id,version)
);
CREATE TABLE d5.task_proposal_heads(
 proposal_id uuid PRIMARY KEY REFERENCES d5.task_proposals,version bigint NOT NULL DEFAULT 0,
 review_command_id uuid REFERENCES d5.task_proposal_reviews
);
CREATE TABLE d5.task_packages(
 package_sha256 d5.hash PRIMARY KEY,project_id uuid NOT NULL,document_id uuid NOT NULL,items jsonb NOT NULL
);
CREATE TABLE d5.task_applications(
 package_sha256 d5.hash PRIMARY KEY REFERENCES d5.task_packages,
 command_id uuid NOT NULL UNIQUE REFERENCES d5.commands DEFERRABLE INITIALLY DEFERRED,result jsonb NOT NULL,applied_at timestamptz NOT NULL DEFAULT clock_timestamp()
);
CREATE FUNCTION d5.task_hash(domain text,value jsonb) RETURNS text LANGUAGE sql IMMUTABLE STRICT
 SET search_path=pg_catalog,pg_temp AS $$ SELECT encode(public.digest(domain||':'||value::text,'sha256'),'hex') $$;
ALTER TABLE d5.task_mapping_heads ADD COLUMN source_basis_sha256 text GENERATED ALWAYS AS (d5.task_hash('d5.source-basis.v1',source_basis)) STORED;
ALTER TABLE d5.task_proposals ADD CHECK(manifest_sha256=d5.task_hash('d5.task-manifest.v1',manifest));
ALTER TABLE d5.task_packages ADD CHECK(package_sha256=d5.task_hash('d5.task-package.v1',jsonb_build_object('project_id',project_id,'document_id',document_id,'items',items)));
CREATE FUNCTION d5.task_semantic(rowval jsonb) RETURNS jsonb LANGUAGE sql IMMUTABLE
 SET search_path=pg_catalog,pg_temp AS $$
 SELECT CASE WHEN rowval IS NULL OR rowval='null'::jsonb THEN NULL ELSE jsonb_build_object(
 'schema','d5.source-basis.v1','fields',rowval->'fields','source_struck',rowval->'source_struck',
 'annotation_text',rowval#>'{source_annotation,text}') END $$;
CREATE FUNCTION d5.task_projection(rowval jsonb) RETURNS jsonb LANGUAGE sql IMMUTABLE
 SET search_path=pg_catalog,pg_temp AS $$ SELECT CASE WHEN rowval IS NULL OR rowval='null'::jsonb THEN NULL ELSE
 jsonb_build_object('title',rowval#>'{fields,item}','description',rowval#>'{fields,objective}') END $$;
CREATE FUNCTION d5.task_target(tid uuid) RETURNS jsonb LANGUAGE sql STABLE
 SET search_path=pg_catalog,pg_temp SET timezone='UTC' AS $$
 SELECT to_jsonb(t) FROM public.tasks t WHERE t.id=tid $$;
CREATE FUNCTION d5.task_conflict(req jsonb,code text) RETURNS jsonb LANGUAGE sql VOLATILE
 SET search_path=pg_catalog,pg_temp AS $$ SELECT d5.review_finish(req,jsonb_build_object('status','CONFLICT','code',code,'writes_d2',false)) $$;
DO $$ DECLARE rel text; BEGIN
 FOREACH rel IN ARRAY ARRAY['task_intents','task_destinations','task_proposals','task_proposal_reviews','task_packages','task_applications'] LOOP
 EXECUTE format('CREATE TRIGGER immutable BEFORE UPDATE OR DELETE OR TRUNCATE ON d5.%I FOR EACH STATEMENT EXECUTE FUNCTION d5.immutable()',rel);
 END LOOP;
END $$;

CREATE FUNCTION d5.register_task_intent(envelope json) RETURNS jsonb LANGUAGE plpgsql VOLATILE SECURITY DEFINER
 SET search_path=pg_catalog,pg_temp AS $$
DECLARE req jsonb;prior jsonb;
BEGIN
 req=d5.review_envelope(envelope,'REGISTER_TASK_INTENT',ARRAY['source_key','profile','policy','task_id','task_key']);
 IF req->>'policy'<>'d5.task-projection.v1' OR (req->>'profile')::d5.profile='markdown-structure.v1' THEN RAISE EXCEPTION 'Fixed projection/profile required'; END IF;
 prior=d5.review_prior(req);IF prior IS NOT NULL THEN RETURN prior;END IF;
 IF NOT EXISTS(SELECT FROM d5.source_registrations WHERE document_id=(req->>'document_id')::uuid AND project_id=(req->>'project_id')::uuid) THEN RETURN d5.task_conflict(req,'SOURCE_SCOPE_CONFLICT');END IF;
 IF EXISTS(SELECT FROM d5.task_intents WHERE (document_id=(req->>'document_id')::uuid AND source_key_sha256=encode(public.digest(req->>'source_key','sha256'),'hex'))
 OR task_id=(req->>'task_id')::uuid OR (project_id=(req->>'project_id')::uuid AND task_key=req->>'task_key'))
 OR EXISTS(SELECT FROM public.tasks WHERE id=(req->>'task_id')::uuid OR (project_id=(req->>'project_id')::uuid AND task_key=req->>'task_key')) THEN RETURN d5.task_conflict(req,'IDENTITY_CONFLICT');END IF;
 INSERT INTO d5.task_intents(intent_id,project_id,document_id,source_key,profile,policy,task_id,task_key)
 VALUES((req->>'command_id')::uuid,(req->>'project_id')::uuid,(req->>'document_id')::uuid,req->>'source_key',(req->>'profile')::d5.profile,req->>'policy',(req->>'task_id')::uuid,req->>'task_key');
 INSERT INTO d5.task_mapping_heads(intent_id) VALUES((req->>'command_id')::uuid);
 RETURN d5.review_finish(req,jsonb_build_object('status','OK','intent_id',req->>'command_id','version_at_commit',0,'writes_d2',false));
END $$;

CREATE FUNCTION d5.prepare_task_proposal(envelope json) RETURNS jsonb LANGUAGE plpgsql VOLATILE SECURITY DEFINER
 SET search_path=pg_catalog,pg_temp SET timezone='UTC' AS $$
DECLARE req jsonb;prior jsonb;i d5.task_intents;h d5.task_mapping_heads;r d5.comparison_reports;rh d5.row_review_heads;
 rv jsonb;m jsonb;target jsonb;act text;ref d5.reference_heads;beforeval jsonb;afterval jsonb;sh text;
BEGIN
 req=d5.review_envelope(envelope,'PREPARE_TASK_PROPOSAL',ARRAY['intent_id','comparison_id','row_sha256','report_sha256','expected_reference_version'],ARRAY['expected_reference_version']);
 PERFORM d5.review_version(req->'expected_reference_version');
 prior=d5.review_prior(req);IF prior IS NOT NULL THEN RETURN prior;END IF;
 SELECT * INTO i FROM d5.task_intents WHERE intent_id=(req->>'intent_id')::uuid AND project_id=(req->>'project_id')::uuid AND document_id=(req->>'document_id')::uuid;
 IF NOT FOUND THEN RETURN d5.task_conflict(req,'INTENT_SCOPE_CONFLICT');END IF;
 SELECT * INTO STRICT h FROM d5.task_mapping_heads WHERE intent_id=i.intent_id;
 SELECT cr.* INTO r FROM d5.comparisons c JOIN d5.comparison_reports cr USING(report_sha256) WHERE c.comparison_id=(req->>'comparison_id')::uuid;
 IF NOT FOUND OR r.project_id<>i.project_id OR r.document_id<>i.document_id OR r.profile<>i.profile OR r.report_sha256<>req->>'report_sha256' OR r.state<>'PREVIEW_ONLY' THEN RETURN d5.task_conflict(req,'COMPARISON_SCOPE_CONFLICT');END IF;
 SELECT convert_from(row_bytes,'UTF8')::jsonb INTO rv FROM d5.review_items WHERE comparison_id=(req->>'comparison_id')::uuid AND source_key=i.source_key AND row_sha256=req->>'row_sha256';
 IF NOT FOUND THEN RETURN d5.task_conflict(req,'NO_CHANGED_ROW_NO_BOOTSTRAP');END IF;
 SELECT * INTO STRICT rh FROM d5.row_review_heads WHERE comparison_id=(req->>'comparison_id')::uuid AND source_key=i.source_key;
 IF NOT EXISTS(SELECT FROM d5.row_decisions WHERE command_id=rh.decision_command_id AND decision='ACCEPT') THEN RETURN d5.task_conflict(req,'SOURCE_NOT_ACCEPTED');END IF;
 SELECT * INTO STRICT ref FROM d5.reference_heads WHERE document_id=i.document_id AND profile=i.profile;
 IF ref.observation_id IS DISTINCT FROM r.before_observation_id OR ref.version<>d5.review_version(req->'expected_reference_version') THEN RETURN d5.task_conflict(req,'REFERENCE_VERSION_CONFLICT');END IF;
 target=d5.task_target(i.task_id);beforeval=d5.task_semantic(rv#>'{before,row}');afterval=d5.task_semantic(rv#>'{after,row}');
 IF rv->>'change'='ABSENT_IN_OBSERVATION' THEN act='KEEP_EXISTING_NO_DELETE';
 ELSIF EXISTS(SELECT FROM d5.task_destinations WHERE intent_id=i.intent_id) THEN
  IF rv->>'change'='ADDED' THEN RETURN d5.task_conflict(req,'REAPPEARANCE_REVIEW_REQUIRED');END IF;
  IF h.source_basis IS DISTINCT FROM beforeval THEN RETURN d5.task_conflict(req,'SOURCE_BASE_CONFLICT');END IF;
  IF jsonb_build_object('title',target->'title','description',target->'description') IS DISTINCT FROM h.projection THEN RETURN d5.task_conflict(req,'LOCAL_EDIT_CONFLICT');END IF;
  act=CASE WHEN h.projection IS NOT DISTINCT FROM d5.task_projection(rv#>'{after,row}') THEN 'LINK_SOURCE_EVIDENCE' ELSE 'PATCH_BACKLOG' END;
 ELSE
  IF target IS NOT NULL OR EXISTS(SELECT FROM public.tasks WHERE project_id=i.project_id AND task_key=i.task_key) THEN RETURN d5.task_conflict(req,'TARGET_OCCUPIED');END IF;
  act='CREATE_BACKLOG';
 END IF;
 IF act<>'KEEP_EXISTING_NO_DELETE' THEN
  IF jsonb_typeof(rv#>'{after,row,fields,item}') IS DISTINCT FROM 'string' OR btrim(rv#>>'{after,row,fields,item}',U&'\0009\000A\000B\000C\000D\0020\0085\00A0\1680\2000\2001\2002\2003\2004\2005\2006\2007\2008\2009\200A\2028\2029\202F\205F\3000')=''
   OR jsonb_typeof(rv#>'{after,row,fields,objective}') IS DISTINCT FROM 'string' THEN RETURN d5.task_conflict(req,'INVALID_PROJECTION');END IF;
 END IF;
 m=jsonb_build_object('schema','d5.task-manifest.v1','intent',to_jsonb(i),'mapping_version',h.version,'comparison_id',req->>'comparison_id','report_sha256',r.report_sha256,
 'row_sha256',req->>'row_sha256','source_decision_command_id',rh.decision_command_id,'source_decision_version',rh.version,'reference_version',ref.version,
 'before_observation_id',r.before_observation_id,'after_observation_id',r.after_observation_id,'action',act,'source_change',rv,
 'before_basis',beforeval,'after_basis',afterval,'before_basis_sha256',d5.task_hash('d5.source-basis.v1',beforeval),'after_basis_sha256',d5.task_hash('d5.source-basis.v1',afterval),'before_projection',h.projection,'after_projection',d5.task_projection(rv#>'{after,row}'),
 'target_schema','d5.task-target.v1','target',target,'target_sha256',d5.task_hash('d5.task-target.v1',coalesce(target,'null'::jsonb)),
 'after_revision_id',(SELECT revision_id FROM d5.observations WHERE observation_id=r.after_observation_id),'activation_allowed',false);
 sh=d5.task_hash('d5.task-manifest.v1',m);
 INSERT INTO d5.task_proposals VALUES((req->>'command_id')::uuid,sh,m);
 INSERT INTO d5.task_proposal_heads(proposal_id) VALUES((req->>'command_id')::uuid);
 RETURN d5.review_finish(req,jsonb_build_object('status','OK','proposal_id',req->>'command_id','manifest_sha256',sh,'manifest',m,'writes_d2',false));
END $$;

CREATE FUNCTION d5.review_task_proposal(envelope json) RETURNS jsonb LANGUAGE plpgsql VOLATILE SECURITY DEFINER
 SET search_path=pg_catalog,pg_temp AS $$
DECLARE req jsonb;prior jsonb;p d5.task_proposals;h d5.task_proposal_heads;v bigint;
BEGIN
 req=d5.review_envelope(envelope,'REVIEW_TASK_PROPOSAL',ARRAY['proposal_id','manifest_sha256','expected_version','decision','reviewer_label','reason'],ARRAY['expected_version']);
 v=d5.review_version(req->'expected_version');
 IF req->>'decision' NOT IN ('ACCEPT','REJECT') OR length(req->>'reviewer_label') NOT BETWEEN 1 AND 256 OR length(req->>'reason') NOT BETWEEN 1 AND 1024
 OR req->>'reviewer_label' ~ '[[:cntrl:]]' OR req->>'reason' ~ '[[:cntrl:]]' THEN RAISE EXCEPTION 'Invalid review';END IF;
 prior=d5.review_prior(req);IF prior IS NOT NULL THEN RETURN prior;END IF;
 SELECT * INTO p FROM d5.task_proposals WHERE proposal_id=(req->>'proposal_id')::uuid AND manifest_sha256=req->>'manifest_sha256'
 AND manifest#>>'{intent,project_id}'=req->>'project_id' AND manifest#>>'{intent,document_id}'=req->>'document_id';
 IF NOT FOUND THEN RETURN d5.task_conflict(req,'MANIFEST_SCOPE_CONFLICT');END IF;
 SELECT * INTO STRICT h FROM d5.task_proposal_heads WHERE proposal_id=p.proposal_id FOR UPDATE;
 IF h.version<>v THEN RETURN d5.task_conflict(req,'REVIEW_VERSION_CONFLICT');END IF;
 INSERT INTO d5.task_proposal_reviews VALUES((req->>'command_id')::uuid,p.proposal_id,v+1,req->>'decision',req->>'reviewer_label',req->>'reason');
 UPDATE d5.task_proposal_heads SET version=v+1,review_command_id=(req->>'command_id')::uuid WHERE proposal_id=p.proposal_id;
 RETURN d5.review_finish(req,jsonb_build_object('status','OK','proposal_id',p.proposal_id,'version_at_commit',v+1,'writes_d2',false));
END $$;
CREATE FUNCTION d5.package_task_proposals(envelope json) RETURNS jsonb LANGUAGE plpgsql VOLATILE SECURITY DEFINER
 SET search_path=pg_catalog,pg_temp AS $$
DECLARE req jsonb;prior jsonb;pin jsonb;p d5.task_proposals;h d5.task_proposal_heads;digest text;keys text[];
BEGIN
 req=d5.review_envelope(envelope,'PACKAGE_TASK_PROPOSALS',ARRAY['items'],ARRAY['items']);
 IF jsonb_typeof(req->'items') IS DISTINCT FROM 'array' OR jsonb_array_length(req->'items') NOT BETWEEN 1 AND 2000 THEN RAISE EXCEPTION 'Explicit package required';END IF;
 FOR pin IN SELECT * FROM jsonb_array_elements(req->'items') LOOP
 SELECT array_agg(k ORDER BY k) INTO keys FROM jsonb_object_keys(pin) k;
 IF keys IS DISTINCT FROM ARRAY['manifest_sha256','proposal_id','review_command_id','review_version'] OR
 jsonb_typeof(pin->'manifest_sha256') IS DISTINCT FROM 'string' OR jsonb_typeof(pin->'proposal_id') IS DISTINCT FROM 'string' OR jsonb_typeof(pin->'review_command_id') IS DISTINCT FROM 'string'
 OR (pin->>'proposal_id')::uuid::text<>pin->>'proposal_id' OR (pin->>'review_command_id')::uuid::text<>pin->>'review_command_id' THEN RAISE EXCEPTION 'Closed review pin required';END IF;
 PERFORM d5.review_version(pin->'review_version');
 END LOOP;
 IF EXISTS(SELECT FROM jsonb_array_elements(req->'items') x GROUP BY x->>'proposal_id' HAVING count(*)>1) OR req->'items' IS DISTINCT FROM
 (SELECT jsonb_agg(x ORDER BY (x->>'proposal_id') COLLATE "C") FROM jsonb_array_elements(req->'items') x) THEN RAISE EXCEPTION 'Unique sorted pins required';END IF;
 prior=d5.review_prior(req);IF prior IS NOT NULL THEN RETURN prior;END IF;
 FOR pin IN SELECT * FROM jsonb_array_elements(req->'items') LOOP
 SELECT * INTO p FROM d5.task_proposals WHERE proposal_id=(pin->>'proposal_id')::uuid;
 IF NOT FOUND OR p.manifest_sha256<>pin->>'manifest_sha256' OR p.manifest#>>'{intent,project_id}'<>req->>'project_id' OR p.manifest#>>'{intent,document_id}'<>req->>'document_id' THEN RETURN d5.task_conflict(req,'MANIFEST_SCOPE_CONFLICT');END IF;
 SELECT * INTO STRICT h FROM d5.task_proposal_heads WHERE proposal_id=p.proposal_id;
 IF h.version<>d5.review_version(pin->'review_version') OR h.review_command_id IS DISTINCT FROM (pin->>'review_command_id')::uuid
 OR NOT EXISTS(SELECT FROM d5.task_proposal_reviews WHERE command_id=h.review_command_id AND decision='ACCEPT') THEN RETURN d5.task_conflict(req,'MANIFEST_NOT_ACCEPTED');END IF;
 END LOOP;
 IF EXISTS(SELECT FROM jsonb_array_elements(req->'items') x JOIN d5.task_proposals tp ON tp.proposal_id=(x->>'proposal_id')::uuid GROUP BY tp.manifest#>>'{intent,intent_id}' HAVING count(*)>1) THEN RAISE EXCEPTION 'One proposal per intent required';END IF;
 digest=d5.task_hash('d5.task-package.v1',jsonb_build_object('project_id',req->>'project_id','document_id',req->>'document_id','items',req->'items'));
 INSERT INTO d5.task_packages VALUES(digest,(req->>'project_id')::uuid,(req->>'document_id')::uuid,req->'items') ON CONFLICT DO NOTHING;
 RETURN d5.review_finish(req,jsonb_build_object('status','OK','package_sha256',digest,'writes_d2',false));
END $$;

-- Private validator used ONLY inside the D3 -> D5 boundary during APPLY.
CREATE FUNCTION d5.task_validate(p d5.task_proposals,pin jsonb) RETURNS text LANGUAGE plpgsql VOLATILE
 SET search_path=pg_catalog,pg_temp SET timezone='UTC' AS $$
DECLARE m jsonb=p.manifest;i d5.task_intents;h d5.task_mapping_heads;rh d5.task_proposal_heads;sr d5.row_review_heads;ref d5.reference_heads;t jsonb;act text=m->>'action';
BEGIN
 SELECT * INTO STRICT i FROM d5.task_intents WHERE intent_id=(m#>>'{intent,intent_id}')::uuid FOR UPDATE;
 SELECT * INTO STRICT h FROM d5.task_mapping_heads WHERE intent_id=i.intent_id FOR UPDATE;
 IF to_jsonb(i) IS DISTINCT FROM m->'intent' OR h.version<>d5.review_version(m->'mapping_version') THEN RETURN 'INTENT_VERSION_CONFLICT';END IF;
 SELECT * INTO STRICT rh FROM d5.task_proposal_heads WHERE proposal_id=p.proposal_id;
 IF rh.version<>d5.review_version(pin->'review_version') OR rh.review_command_id IS DISTINCT FROM (pin->>'review_command_id')::uuid
 OR NOT EXISTS(SELECT FROM d5.task_proposal_reviews WHERE command_id=rh.review_command_id AND decision='ACCEPT') THEN RETURN 'MANIFEST_REVIEW_CONFLICT';END IF;
 SELECT * INTO STRICT sr FROM d5.row_review_heads WHERE comparison_id=(m->>'comparison_id')::uuid AND source_key=i.source_key;
 IF sr.version<>d5.review_version(m->'source_decision_version') OR sr.decision_command_id IS DISTINCT FROM (m->>'source_decision_command_id')::uuid
 OR NOT EXISTS(SELECT FROM d5.row_decisions WHERE command_id=sr.decision_command_id AND decision='ACCEPT') THEN RETURN 'SOURCE_REVIEW_CONFLICT';END IF;
 SELECT * INTO STRICT ref FROM d5.reference_heads WHERE document_id=i.document_id AND profile=i.profile;
 IF ref.version<>d5.review_version(m->'reference_version') OR ref.observation_id IS DISTINCT FROM (m->>'before_observation_id')::uuid THEN RETURN 'REFERENCE_VERSION_CONFLICT';END IF;
 t=d5.task_target(i.task_id);
 IF act='CREATE_BACKLOG' THEN
  IF t IS NOT NULL OR EXISTS(SELECT FROM public.tasks WHERE project_id=i.project_id AND task_key=i.task_key) THEN RETURN 'TARGET_OCCUPIED';END IF;
 ELSIF act<>'KEEP_EXISTING_NO_DELETE' OR EXISTS(SELECT FROM d5.task_destinations WHERE intent_id=i.intent_id) THEN
  IF t IS NULL OR NOT EXISTS(SELECT FROM d5.task_destinations WHERE intent_id=i.intent_id AND task_id=i.task_id AND project_id=i.project_id) THEN RETURN 'TARGET_OWNERSHIP_CONFLICT';END IF;
  IF act<>'KEEP_EXISTING_NO_DELETE' AND jsonb_build_object('title',t->'title','description',t->'description') IS DISTINCT FROM h.projection THEN RETURN 'LOCAL_EDIT_CONFLICT';END IF;
  IF act<>'KEEP_EXISTING_NO_DELETE' AND (t->>'status'<>'BACKLOG' OR EXISTS(SELECT FROM public.operations WHERE task_id=i.task_id) OR EXISTS(SELECT FROM public.schedule_entries WHERE task_id=i.task_id)) THEN RETURN 'TARGET_HAS_WORK_OR_STATE';END IF;
 END IF;
 IF coalesce(t,'null'::jsonb) IS DISTINCT FROM m->'target' OR d5.task_hash('d5.task-target.v1',coalesce(t,'null'::jsonb)) IS DISTINCT FROM m->>'target_sha256' THEN RETURN 'TARGET_CAS_CONFLICT';END IF;
 IF act IN ('PATCH_BACKLOG','LINK_SOURCE_EVIDENCE') AND h.source_basis IS DISTINCT FROM m->'before_basis' THEN RETURN 'SOURCE_BASE_CONFLICT';END IF;
 RETURN NULL;
END $$;
CREATE FUNCTION d5.apply_task_proposals(envelope json) RETURNS jsonb LANGUAGE plpgsql VOLATILE SECURITY DEFINER
 SET search_path=pg_catalog,pg_temp SET timezone='UTC' AS $$
DECLARE req jsonb;prior jsonb;pkg d5.task_packages;pin jsonb;p d5.task_proposals;m jsonb;i d5.task_intents;code text;act text;result jsonb;effects jsonb='[]'::jsonb;original d5.task_applications;locator text;rid uuid;
BEGIN
 req=d5.review_envelope(envelope,'APPLY_TASK_PROPOSALS',ARRAY['package_sha256']);
 -- Never acquire the D5 mutex before this trusted boundary.
 PERFORM d5.task_lock_boundary();
 prior=d5.review_prior(req);IF prior IS NOT NULL THEN RETURN prior;END IF;
 SELECT * INTO pkg FROM d5.task_packages WHERE package_sha256=req->>'package_sha256' AND project_id=(req->>'project_id')::uuid AND document_id=(req->>'document_id')::uuid;
 IF NOT FOUND THEN RETURN d5.task_conflict(req,'PACKAGE_SCOPE_CONFLICT');END IF;
 SELECT * INTO original FROM d5.task_applications WHERE package_sha256=pkg.package_sha256;
 IF FOUND THEN RETURN d5.review_finish(req,jsonb_build_object('status','ALREADY_APPLIED','original_command_id',original.command_id,'package_sha256',pkg.package_sha256,'writes_d2',false));END IF;
 -- Validate the entire package before the first mutation. Sorted intent locks.
 FOR pin IN SELECT x FROM jsonb_array_elements(pkg.items) x JOIN d5.task_proposals tp ON tp.proposal_id=(x->>'proposal_id')::uuid ORDER BY tp.manifest#>>'{intent,intent_id}' LOOP
  SELECT * INTO STRICT p FROM d5.task_proposals WHERE proposal_id=(pin->>'proposal_id')::uuid;
  IF p.manifest_sha256 IS DISTINCT FROM pin->>'manifest_sha256' OR p.manifest_sha256 IS DISTINCT FROM d5.task_hash('d5.task-manifest.v1',p.manifest) THEN RAISE EXCEPTION 'Manifest integrity failure';END IF;
  code=d5.task_validate(p,pin);
  IF code IS NOT NULL THEN RETURN d5.task_conflict(req,code);END IF;
 END LOOP;
 FOR pin IN SELECT * FROM jsonb_array_elements(pkg.items) LOOP
  SELECT * INTO STRICT p FROM d5.task_proposals WHERE proposal_id=(pin->>'proposal_id')::uuid;m=p.manifest;
  SELECT * INTO STRICT i FROM d5.task_intents WHERE intent_id=(m#>>'{intent,intent_id}')::uuid;act=m->>'action';
  IF act='CREATE_BACKLOG' THEN
   INSERT INTO public.tasks(id,project_id,task_key,title,description,status,row_version,epic_id,urgency,deadline_at,deferred_count)
   VALUES(i.task_id,i.project_id,i.task_key,m#>>'{after_projection,title}',m#>>'{after_projection,description}','BACKLOG',0,NULL,0,NULL,0);
   INSERT INTO d5.task_destinations VALUES(i.intent_id,i.task_id,i.project_id);
  ELSIF act='PATCH_BACKLOG' THEN
   UPDATE public.tasks SET title=m#>>'{after_projection,title}',description=m#>>'{after_projection,description}',row_version=row_version+1 WHERE id=i.task_id;
  END IF;
  IF act<>'KEEP_EXISTING_NO_DELETE' THEN
   rid=(m->>'after_revision_id')::uuid;locator=m#>>'{source_change,after,row,source_locator}';
   IF NOT EXISTS(SELECT FROM d5.observations o JOIN public.source_revisions r ON r.id=o.revision_id WHERE o.observation_id=(m->>'after_observation_id')::uuid
    AND o.project_id=i.project_id AND o.document_id=i.document_id AND o.profile=i.profile AND o.revision_id=rid
    AND locator='sha256:'||r.sha256||'#L'||(m#>>'{source_change,after,row,line_start}')) THEN RAISE EXCEPTION 'Invalid after-row provenance';END IF;
   IF EXISTS(SELECT FROM d2.task_sources WHERE task_id=i.task_id AND revision_id=rid AND source_locator=locator AND (document_id<>i.document_id OR project_id<>i.project_id)) THEN RAISE EXCEPTION 'Source link collision';END IF;
   INSERT INTO d2.task_sources VALUES(i.task_id,rid,locator,i.document_id,i.project_id) ON CONFLICT DO NOTHING;
   UPDATE d5.task_mapping_heads SET version=version+1,source_basis=m->'after_basis',projection=m->'after_projection' WHERE intent_id=i.intent_id;
  ELSE
   UPDATE d5.task_mapping_heads SET version=version+1 WHERE intent_id=i.intent_id;
  END IF;
  INSERT INTO public.audit_events(actor,entity_type,entity_id,action,payload) VALUES(session_user,'D5_TASK_IMPORT',i.task_id,act,
   jsonb_build_object('command_id',req->>'command_id','manifest_sha256',p.manifest_sha256,'package_sha256',pkg.package_sha256,'activation_allowed',false));
  effects=effects||jsonb_build_array(jsonb_build_object('task_id',i.task_id,'action',act,'manifest_sha256',p.manifest_sha256));
 END LOOP;
 result=jsonb_build_object('status','OK','package_sha256',pkg.package_sha256,'effects',effects,'writes_d2',true,'activation_allowed',false);
 INSERT INTO d5.task_applications(package_sha256,command_id,result) VALUES(pkg.package_sha256,(req->>'command_id')::uuid,result);
 RETURN d5.review_finish(req,result);
END $$;
CREATE FUNCTION d5.read_task_proposal(pid uuid,doc uuid,proposal uuid) RETURNS jsonb LANGUAGE sql STABLE SECURITY DEFINER
 SET search_path=pg_catalog,pg_temp AS $$ SELECT jsonb_build_object('proposal_id',p.proposal_id,'manifest_sha256',p.manifest_sha256,'manifest',p.manifest,
 'review_version',h.version,'review_command_id',h.review_command_id) FROM d5.task_proposals p JOIN d5.task_proposal_heads h USING(proposal_id)
 WHERE p.proposal_id=proposal AND p.manifest#>>'{intent,project_id}'=pid::text AND p.manifest#>>'{intent,document_id}'=doc::text $$;
CREATE FUNCTION d5.read_task_package(pid uuid,doc uuid,digest text) RETURNS jsonb LANGUAGE sql STABLE SECURITY DEFINER
 SET search_path=pg_catalog,pg_temp AS $$ SELECT to_jsonb(p) FROM d5.task_packages p WHERE p.project_id=pid AND p.document_id=doc AND p.package_sha256=digest $$;
-- New owner default privileges already revoke PUBLIC; existing owners/ACL remain intact.
GRANT EXECUTE ON FUNCTION d5.register_task_intent(json),d5.prepare_task_proposal(json),d5.package_task_proposals(json) TO d5_writer;
GRANT EXECUTE ON FUNCTION d5.review_task_proposal(json) TO d5_reviewer;
GRANT EXECUTE ON FUNCTION d5.apply_task_proposals(json) TO d5_applier;
GRANT EXECUTE ON FUNCTION d5.read_task_proposal(uuid,uuid,uuid),d5.read_task_package(uuid,uuid,text) TO d5_writer,d5_reviewer,d5_reader,d5_applier;
RESET ROLE;
GRANT EXECUTE ON FUNCTION d5.read_comparison(uuid,uuid,uuid),d5.read_comparison_sources(uuid,uuid,uuid,uuid),d5.read_command(uuid) TO d5_applier;
REVOKE CREATE ON SCHEMA d5 FROM d5_apply_owner;
COMMIT;
