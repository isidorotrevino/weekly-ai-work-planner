-- SPDX-License-Identifier: GPL-3.0-only
-- I16: approved I15 adoption; own fresh V30 + V31-V36 lab only. No promotion.
BEGIN;
GRANT CREATE ON SCHEMA d5 TO d5_apply_owner;
GRANT SELECT ON d5.preview_artifacts TO d5_apply_owner;
SET LOCAL ROLE d5_apply_owner;
CREATE TABLE d5.adoption_proposals(
 proposal_id uuid PRIMARY KEY REFERENCES d5.commands DEFERRABLE INITIALLY DEFERRED,
 manifest_sha256 d5.hash NOT NULL,manifest jsonb NOT NULL,
 CHECK(octet_length(manifest::text)<=4194304),
 CHECK(manifest_sha256=d5.task_hash('d5.adoption-task-manifest.v1',manifest))
);
CREATE TABLE d5.adoption_reviews(
 command_id uuid PRIMARY KEY REFERENCES d5.commands DEFERRABLE INITIALLY DEFERRED,
 proposal_id uuid NOT NULL REFERENCES d5.adoption_proposals,version bigint NOT NULL CHECK(version>0),
 decision text NOT NULL CHECK(decision IN ('ACCEPT','REJECT')),reviewer_label text NOT NULL,reason text NOT NULL,
 UNIQUE(proposal_id,version)
);
CREATE TABLE d5.adoption_review_heads(
 proposal_id uuid PRIMARY KEY REFERENCES d5.adoption_proposals,version bigint NOT NULL DEFAULT 0,
 review_command_id uuid REFERENCES d5.adoption_reviews
);
CREATE TABLE d5.adoption_packages(
 package_sha256 d5.hash PRIMARY KEY,project_id uuid NOT NULL,document_id uuid NOT NULL,items jsonb NOT NULL,
 CHECK(package_sha256=d5.task_hash('d5.adoption-task-package.v1',jsonb_build_object('project_id',project_id,'document_id',document_id,'items',items)))
);
CREATE TABLE d5.adoption_applications(
 package_sha256 d5.hash PRIMARY KEY REFERENCES d5.adoption_packages,
 command_id uuid NOT NULL UNIQUE REFERENCES d5.commands DEFERRABLE INITIALLY DEFERRED,
 result jsonb NOT NULL,applied_at timestamptz NOT NULL DEFAULT clock_timestamp()
);
DO $$ DECLARE rel text; BEGIN
 FOREACH rel IN ARRAY ARRAY['adoption_proposals','adoption_reviews','adoption_packages','adoption_applications'] LOOP
  EXECUTE format('CREATE TRIGGER immutable BEFORE UPDATE OR DELETE OR TRUNCATE ON d5.%I FOR EACH STATEMENT EXECUTE FUNCTION d5.immutable()',rel);
 END LOOP;
END $$;
CREATE FUNCTION d5.adoption_guard(i jsonb) RETURNS text LANGUAGE plpgsql VOLATILE
 SET search_path=pg_catalog,pg_temp AS $$
DECLARE t jsonb=d5.task_target((i->>'task_id')::uuid);
BEGIN
 IF t IS NULL OR t->>'project_id' IS DISTINCT FROM i->>'project_id' OR t->>'task_key' IS DISTINCT FROM i->>'task_key' THEN RETURN 'TARGET_IDENTITY_CONFLICT';END IF;
 IF length(i->>'task_key') NOT BETWEEN 1 AND 256 OR i->>'task_key' ~ '[[:cntrl:]]' THEN RETURN 'INVALID_TASK_KEY';END IF;
 IF EXISTS(SELECT FROM d5.task_intents WHERE intent_id=(i->>'intent_id')::uuid OR
 (document_id=(i->>'document_id')::uuid AND source_key_sha256=encode(public.digest(i->>'source_key','sha256'),'hex'))
 OR task_id=(i->>'task_id')::uuid OR (project_id=(i->>'project_id')::uuid AND task_key=i->>'task_key')) THEN RETURN 'CORRESPONDENCE_OCCUPIED';END IF;
 IF t->>'status'<>'BACKLOG' OR EXISTS(SELECT FROM public.operations WHERE task_id=(i->>'task_id')::uuid)
 OR EXISTS(SELECT FROM public.schedule_entries WHERE task_id=(i->>'task_id')::uuid) THEN RETURN 'TARGET_HAS_WORK_OR_STATE';END IF;
 IF EXISTS(SELECT FROM d2.task_sources WHERE task_id=(i->>'task_id')::uuid) THEN RETURN 'TARGET_HAS_SOURCE';END IF;
 IF NOT d5.local_edit_valid_projection(jsonb_build_object('title',t->'title','description',t->'description'),true) THEN RETURN 'INVALID_PROJECTION';END IF;
 RETURN NULL;
END $$;
CREATE FUNCTION d5.prepare_adoption_task(envelope json,rowbytes bytea) RETURNS jsonb LANGUAGE plpgsql VOLATILE SECURITY DEFINER
 SET search_path=pg_catalog,pg_temp SET timezone='UTC' AS $$
DECLARE req jsonb;prior jsonb;i jsonb;o d5.observations;ref d5.reference_heads;v jsonb;rv jsonb;m jsonb;digest text;ch text;t jsonb;l jsonb;code text;
BEGIN
 req=d5.review_envelope(envelope,'PREPARE_ADOPTION_TASK',ARRAY['source_key','profile','policy','task_id','task_key','observation_id','content_sha256','preview_sha256','snapshot_row_sha256','expected_reference_version','reason'],ARRAY['expected_reference_version']);
 PERFORM d5.review_version(req->'expected_reference_version');
 IF rowbytes IS NULL OR octet_length(rowbytes)>2097152 OR encode(public.digest(rowbytes,'sha256'),'hex') IS DISTINCT FROM req->>'snapshot_row_sha256' THEN RAISE EXCEPTION 'Invalid adoption row bytes/hash';END IF;
 rv=convert_from(rowbytes,'UTF8')::jsonb;
 prior=d5.review_prior(req);IF prior IS NOT NULL THEN RETURN prior;END IF;
 IF req->>'policy'<>'d5.task-projection.v1' OR req->>'profile' NOT IN ('task-register.v1','task-register-compat.v1') THEN RETURN d5.task_conflict(req,'POLICY_PROFILE_CONFLICT');END IF;
 IF length(req->>'reason') NOT BETWEEN 1 AND 1024 OR req->>'reason' ~ '[[:cntrl:]]' OR btrim(req->>'reason',U&'\0009\000A\000B\000C\000D\0020\0085\00A0\1680\2000\2001\2002\2003\2004\2005\2006\2007\2008\2009\200A\2028\2029\202F\205F\3000')='' THEN RETURN d5.task_conflict(req,'ADOPTION_REASON_REQUIRED');END IF;
 SELECT * INTO o FROM d5.observations WHERE observation_id=(req->>'observation_id')::uuid AND document_id=(req->>'document_id')::uuid AND project_id=(req->>'project_id')::uuid AND profile=(req->>'profile')::d5.profile;
 IF NOT FOUND OR o.preview_sha256 IS DISTINCT FROM req->>'preview_sha256' THEN RETURN d5.task_conflict(req,'OBSERVATION_SCOPE_CONFLICT');END IF;
 SELECT sha256 INTO STRICT ch FROM public.source_revisions WHERE id=o.revision_id AND document_id=o.document_id;
 IF ch IS DISTINCT FROM req->>'content_sha256' THEN RETURN d5.task_conflict(req,'SOURCE_HASH_CONFLICT');END IF;
 SELECT convert_from(preview_bytes,'UTF8')::jsonb INTO STRICT v FROM d5.preview_artifacts WHERE preview_sha256=o.preview_sha256;
 IF EXISTS(SELECT FROM jsonb_array_elements(v->'diagnostics') d WHERE d->'blocking'='true'::jsonb) THEN RETURN d5.task_conflict(req,'OBSERVATION_BLOCKED');END IF;
 IF (SELECT count(*) FROM jsonb_array_elements(v->'proposals') r WHERE r->>'source_key'=req->>'source_key')<>1 THEN RETURN d5.task_conflict(req,'SOURCE_ROW_NOT_UNIQUE');END IF;
 IF NOT EXISTS(SELECT FROM jsonb_array_elements(v->'proposals') r WHERE r->>'source_key'=req->>'source_key' AND r=rv) THEN RETURN d5.task_conflict(req,'SNAPSHOT_ROW_CONFLICT');END IF;
 SELECT * INTO STRICT ref FROM d5.reference_heads WHERE document_id=o.document_id AND profile=o.profile;
 IF ref.observation_id IS DISTINCT FROM o.observation_id OR ref.version<>d5.review_version(req->'expected_reference_version') THEN RETURN d5.task_conflict(req,'REFERENCE_VERSION_CONFLICT');END IF;
 i=jsonb_build_object('intent_id',req->>'command_id','project_id',req->>'project_id','document_id',req->>'document_id','source_key',req->>'source_key',
 'source_key_sha256',encode(public.digest(req->>'source_key','sha256'),'hex'),'profile',req->>'profile','policy',req->>'policy','task_id',req->>'task_id','task_key',req->>'task_key');
 code=d5.adoption_guard(i);IF code IS NOT NULL THEN RETURN d5.task_conflict(req,code);END IF;
 IF NOT d5.local_edit_valid_projection(d5.task_projection(rv),false) THEN RETURN d5.task_conflict(req,'INVALID_PROJECTION');END IF;
 IF rv->>'source_locator' IS DISTINCT FROM 'sha256:'||ch||'#L'||(rv->>'line_start') THEN RAISE EXCEPTION 'Invalid source locator';END IF;
 t=d5.task_target((req->>'task_id')::uuid);l=jsonb_build_object('title',t->'title','description',t->'description');
 m=jsonb_build_object('schema','d5.adoption-task-manifest.v1','mode','ADOPTION_EXISTING','proposal_id',req->>'command_id','proposed_intent_id',req->>'command_id',
 'intent',i,'observation_id',o.observation_id,'revision_id',o.revision_id,'content_sha256',ch,'preview_sha256',o.preview_sha256,
 'reference_version',ref.version,'snapshot_row',rv,'snapshot_row_sha256',req->>'snapshot_row_sha256','action','LINK_EXISTING_BACKLOG','reason',req->>'reason',
 'projection',d5.task_projection(rv),'source_basis',d5.task_semantic(rv),'source_basis_sha256',d5.task_hash('d5.source-basis.v1',d5.task_semantic(rv)),
 'prior_applied_basis',NULL,'local_projection',l,'result_projection',l,'task_fields_to_write','[]'::jsonb,
 'target_schema','d5.task-target.v1','target',t,'target_sha256',d5.task_hash('d5.task-target.v1',t),
 'target_expectation',jsonb_build_object('schema','d5.adoption-target-available.v1','correspondence_absent',true,'task_sources_empty',true,'no_work',true),
 'prepared_at',clock_timestamp(),'activation_allowed',false);
 digest=d5.task_hash('d5.adoption-task-manifest.v1',m);
 INSERT INTO d5.adoption_proposals VALUES((req->>'command_id')::uuid,digest,m);
 INSERT INTO d5.adoption_review_heads(proposal_id) VALUES((req->>'command_id')::uuid);
 RETURN d5.review_finish(req,jsonb_build_object('status','OK','proposal_id',req->>'command_id','manifest_sha256',digest,'manifest',m,'writes_d2',false));
END $$;
CREATE FUNCTION d5.review_adoption_task(envelope json) RETURNS jsonb LANGUAGE plpgsql VOLATILE SECURITY DEFINER
 SET search_path=pg_catalog,pg_temp AS $$
DECLARE req jsonb;prior jsonb;p d5.adoption_proposals;h d5.adoption_review_heads;v bigint;
BEGIN
 req=d5.review_envelope(envelope,'REVIEW_ADOPTION_TASK',ARRAY['proposal_id','manifest_sha256','expected_version','decision','reviewer_label','reason'],ARRAY['expected_version']);
 v=d5.review_version(req->'expected_version');
 IF req->>'decision' NOT IN ('ACCEPT','REJECT') OR length(req->>'reviewer_label') NOT BETWEEN 1 AND 256 OR length(req->>'reason') NOT BETWEEN 1 AND 1024
 OR req->>'reviewer_label' ~ '[[:cntrl:]]' OR req->>'reason' ~ '[[:cntrl:]]' THEN RAISE EXCEPTION 'Invalid review';END IF;
 prior=d5.review_prior(req);IF prior IS NOT NULL THEN RETURN prior;END IF;
 SELECT * INTO p FROM d5.adoption_proposals WHERE proposal_id=(req->>'proposal_id')::uuid AND manifest_sha256=req->>'manifest_sha256'
 AND manifest#>>'{intent,project_id}'=req->>'project_id' AND manifest#>>'{intent,document_id}'=req->>'document_id';
 IF NOT FOUND THEN RETURN d5.task_conflict(req,'MANIFEST_SCOPE_CONFLICT');END IF;
 SELECT * INTO STRICT h FROM d5.adoption_review_heads WHERE proposal_id=p.proposal_id FOR UPDATE;
 IF h.version<>v THEN RETURN d5.task_conflict(req,'REVIEW_VERSION_CONFLICT');END IF;
 INSERT INTO d5.adoption_reviews VALUES((req->>'command_id')::uuid,p.proposal_id,v+1,req->>'decision',req->>'reviewer_label',req->>'reason');
 UPDATE d5.adoption_review_heads SET version=v+1,review_command_id=(req->>'command_id')::uuid WHERE proposal_id=p.proposal_id;
 RETURN d5.review_finish(req,jsonb_build_object('status','OK','proposal_id',p.proposal_id,'version_at_commit',v+1,'writes_d2',false));
END $$;
CREATE FUNCTION d5.package_adoption_tasks(envelope json) RETURNS jsonb LANGUAGE plpgsql VOLATILE SECURITY DEFINER
 SET search_path=pg_catalog,pg_temp AS $$
DECLARE req jsonb;prior jsonb;pin jsonb;p d5.adoption_proposals;h d5.adoption_review_heads;digest text;keys text[];
BEGIN
 req=d5.review_envelope(envelope,'PACKAGE_ADOPTION_TASKS',ARRAY['items'],ARRAY['items']);
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
 SELECT * INTO p FROM d5.adoption_proposals WHERE proposal_id=(pin->>'proposal_id')::uuid;
 IF NOT FOUND OR p.manifest_sha256<>pin->>'manifest_sha256' OR p.manifest#>>'{intent,project_id}'<>req->>'project_id' OR p.manifest#>>'{intent,document_id}'<>req->>'document_id' THEN RETURN d5.task_conflict(req,'MANIFEST_SCOPE_CONFLICT');END IF;
 SELECT * INTO STRICT h FROM d5.adoption_review_heads WHERE proposal_id=p.proposal_id;
 IF h.version<>d5.review_version(pin->'review_version') OR h.review_command_id IS DISTINCT FROM (pin->>'review_command_id')::uuid
 OR NOT EXISTS(SELECT FROM d5.adoption_reviews WHERE command_id=h.review_command_id AND decision='ACCEPT') THEN RETURN d5.task_conflict(req,'MANIFEST_NOT_ACCEPTED');END IF;
 END LOOP;
 IF EXISTS(SELECT FROM jsonb_array_elements(req->'items') x JOIN d5.adoption_proposals ap ON ap.proposal_id=(x->>'proposal_id')::uuid GROUP BY ap.manifest#>>'{intent,source_key}' HAVING count(*)>1)
 OR EXISTS(SELECT FROM jsonb_array_elements(req->'items') x JOIN d5.adoption_proposals ap ON ap.proposal_id=(x->>'proposal_id')::uuid GROUP BY ap.manifest#>>'{intent,task_id}' HAVING count(*)>1)
 OR EXISTS(SELECT FROM jsonb_array_elements(req->'items') x JOIN d5.adoption_proposals ap ON ap.proposal_id=(x->>'proposal_id')::uuid GROUP BY ap.manifest#>>'{intent,task_key}' HAVING count(*)>1)
 OR (SELECT count(DISTINCT (ap.manifest->>'observation_id',ap.manifest#>>'{intent,profile}')) FROM jsonb_array_elements(req->'items') x JOIN d5.adoption_proposals ap ON ap.proposal_id=(x->>'proposal_id')::uuid)<>1
 THEN RAISE EXCEPTION 'Unique source/task and single snapshot required';END IF;
 digest=d5.task_hash('d5.adoption-task-package.v1',jsonb_build_object('project_id',req->>'project_id','document_id',req->>'document_id','items',req->'items'));
 INSERT INTO d5.adoption_packages VALUES(digest,(req->>'project_id')::uuid,(req->>'document_id')::uuid,req->'items') ON CONFLICT DO NOTHING;
 RETURN d5.review_finish(req,jsonb_build_object('status','OK','package_sha256',digest,'writes_d2',false));
END $$;

CREATE FUNCTION d5.validate_adoption(p d5.adoption_proposals,pin jsonb) RETURNS text LANGUAGE plpgsql VOLATILE
 SET search_path=pg_catalog,pg_temp AS $$
DECLARE m jsonb=p.manifest;i jsonb=m->'intent';h d5.adoption_review_heads;ref d5.reference_heads;code text;t jsonb;
BEGIN
 SELECT * INTO STRICT h FROM d5.adoption_review_heads WHERE proposal_id=p.proposal_id;
 IF h.version<>d5.review_version(pin->'review_version') OR h.review_command_id IS DISTINCT FROM (pin->>'review_command_id')::uuid
 OR NOT EXISTS(SELECT FROM d5.adoption_reviews WHERE command_id=h.review_command_id AND decision='ACCEPT') THEN RETURN 'ADOPTION_REVIEW_CONFLICT';END IF;
 SELECT * INTO STRICT ref FROM d5.reference_heads WHERE document_id=(i->>'document_id')::uuid AND profile=(i->>'profile')::d5.profile;
 IF ref.version<>d5.review_version(m->'reference_version') OR ref.observation_id IS DISTINCT FROM (m->>'observation_id')::uuid THEN RETURN 'REFERENCE_VERSION_CONFLICT';END IF;
 code=d5.adoption_guard(i);IF code IS NOT NULL THEN RETURN code;END IF;
 t=d5.task_target((i->>'task_id')::uuid);
 IF t IS DISTINCT FROM m->'target' OR d5.task_hash('d5.task-target.v1',t) IS DISTINCT FROM m->>'target_sha256' THEN RETURN 'TARGET_CAS_CONFLICT';END IF;
 RETURN NULL;
END $$;
CREATE FUNCTION d5.apply_adoption_tasks(envelope json) RETURNS jsonb LANGUAGE plpgsql VOLATILE SECURITY DEFINER
 SET search_path=pg_catalog,pg_temp SET timezone='UTC' AS $$
DECLARE req jsonb;prior jsonb;pkg d5.adoption_packages;pin jsonb;p d5.adoption_proposals;m jsonb;i jsonb;code text;effects jsonb='[]'::jsonb;result jsonb;original d5.adoption_applications;
BEGIN
 req=d5.review_envelope(envelope,'APPLY_ADOPTION_TASKS',ARRAY['package_sha256']);
 PERFORM d5.task_lock_boundary();prior=d5.review_prior(req);IF prior IS NOT NULL THEN RETURN prior;END IF;
 SELECT * INTO pkg FROM d5.adoption_packages WHERE package_sha256=req->>'package_sha256' AND project_id=(req->>'project_id')::uuid AND document_id=(req->>'document_id')::uuid;
 IF NOT FOUND THEN RETURN d5.task_conflict(req,'ADOPTION_PACKAGE_SCOPE_CONFLICT');END IF;
 SELECT * INTO original FROM d5.adoption_applications WHERE package_sha256=pkg.package_sha256;
 IF FOUND THEN RETURN d5.review_finish(req,jsonb_build_object('status','ALREADY_APPLIED','original_command_id',original.command_id,'package_sha256',pkg.package_sha256,'writes_d2',false,'writes_task',false));END IF;
 -- Row locks, not data writes: close the FK provenance/work insertion race.
 FOR pin IN SELECT x FROM jsonb_array_elements(pkg.items) x JOIN d5.adoption_proposals ap ON ap.proposal_id=(x->>'proposal_id')::uuid ORDER BY (ap.manifest#>>'{intent,task_id}')::uuid LOOP
  SELECT * INTO STRICT p FROM d5.adoption_proposals WHERE proposal_id=(pin->>'proposal_id')::uuid;
  IF p.manifest_sha256 IS DISTINCT FROM pin->>'manifest_sha256' OR p.manifest_sha256 IS DISTINCT FROM d5.task_hash('d5.adoption-task-manifest.v1',p.manifest) THEN RAISE EXCEPTION 'Adoption manifest integrity failure';END IF;
  PERFORM 1 FROM public.tasks WHERE id=(p.manifest#>>'{intent,task_id}')::uuid FOR UPDATE;
 END LOOP;
 FOR pin IN SELECT * FROM jsonb_array_elements(pkg.items) LOOP
  SELECT * INTO STRICT p FROM d5.adoption_proposals WHERE proposal_id=(pin->>'proposal_id')::uuid;
  code=d5.validate_adoption(p,pin);IF code IS NOT NULL THEN RETURN d5.task_conflict(req,code);END IF;
 END LOOP;
 FOR pin IN SELECT * FROM jsonb_array_elements(pkg.items) LOOP
  SELECT * INTO STRICT p FROM d5.adoption_proposals WHERE proposal_id=(pin->>'proposal_id')::uuid;m=p.manifest;i=m->'intent';
  INSERT INTO d5.task_intents(intent_id,project_id,document_id,source_key,profile,policy,task_id,task_key)
   VALUES((i->>'intent_id')::uuid,(i->>'project_id')::uuid,(i->>'document_id')::uuid,i->>'source_key',(i->>'profile')::d5.profile,i->>'policy',(i->>'task_id')::uuid,i->>'task_key');
  INSERT INTO d5.task_destinations VALUES((i->>'intent_id')::uuid,(i->>'task_id')::uuid,(i->>'project_id')::uuid);
  INSERT INTO d5.task_mapping_heads(intent_id,version,source_basis,projection) VALUES((i->>'intent_id')::uuid,1,m->'source_basis',m->'projection');
  IF NOT EXISTS(SELECT FROM d5.observations o JOIN public.source_revisions r ON r.id=o.revision_id WHERE o.observation_id=(m->>'observation_id')::uuid
   AND o.document_id=(i->>'document_id')::uuid AND o.project_id=(i->>'project_id')::uuid AND o.profile=(i->>'profile')::d5.profile AND o.revision_id=(m->>'revision_id')::uuid
   AND r.sha256=m->>'content_sha256' AND o.preview_sha256=m->>'preview_sha256'
   AND m#>>'{snapshot_row,source_locator}'='sha256:'||r.sha256||'#L'||(m#>>'{snapshot_row,line_start}')) THEN RAISE EXCEPTION 'Adoption provenance integrity failure';END IF;
  INSERT INTO d2.task_sources VALUES((i->>'task_id')::uuid,(m->>'revision_id')::uuid,m#>>'{snapshot_row,source_locator}',(i->>'document_id')::uuid,(i->>'project_id')::uuid);
  INSERT INTO public.audit_events(actor,entity_type,entity_id,action,payload) VALUES(session_user,'D5_TASK_IMPORT',(i->>'task_id')::uuid,'LINK_EXISTING_BACKLOG',
   jsonb_build_object('command_id',req->>'command_id','manifest_sha256',p.manifest_sha256,'package_sha256',pkg.package_sha256,'writes_task',false,'source_projection',m->'projection','result_projection',m->'result_projection','activation_allowed',false));
  effects=effects||jsonb_build_array(jsonb_build_object('intent_id',i->>'intent_id','task_id',i->>'task_id','action','LINK_EXISTING_BACKLOG','manifest_sha256',p.manifest_sha256,'writes_task',false,'source_projection',m->'projection','result_projection',m->'result_projection'));
 END LOOP;
 result=jsonb_build_object('status','OK','package_sha256',pkg.package_sha256,'effects',effects,'writes_d2',true,'writes_task',false,'activation_allowed',false);
 INSERT INTO d5.adoption_applications(package_sha256,command_id,result) VALUES(pkg.package_sha256,(req->>'command_id')::uuid,result);
 RETURN d5.review_finish(req,result);
END $$;
CREATE FUNCTION d5.read_adoption_proposal(pid uuid,doc uuid,proposal uuid) RETURNS jsonb LANGUAGE sql STABLE SECURITY DEFINER
 SET search_path=pg_catalog,pg_temp AS $$ SELECT jsonb_build_object('proposal_id',p.proposal_id,'manifest_sha256',p.manifest_sha256,'manifest',p.manifest,
 'review_version',h.version,'review_command_id',h.review_command_id) FROM d5.adoption_proposals p JOIN d5.adoption_review_heads h USING(proposal_id)
 WHERE p.proposal_id=proposal AND p.manifest#>>'{intent,project_id}'=pid::text AND p.manifest#>>'{intent,document_id}'=doc::text $$;
CREATE FUNCTION d5.read_adoption_package(pid uuid,doc uuid,digest text) RETURNS jsonb LANGUAGE sql STABLE SECURITY DEFINER
 SET search_path=pg_catalog,pg_temp AS $$ SELECT to_jsonb(p) FROM d5.adoption_packages p WHERE p.project_id=pid AND p.document_id=doc AND p.package_sha256=digest $$;
GRANT EXECUTE ON FUNCTION d5.prepare_adoption_task(json,bytea),d5.package_adoption_tasks(json) TO d5_writer;
GRANT EXECUTE ON FUNCTION d5.review_adoption_task(json) TO d5_reviewer;
GRANT EXECUTE ON FUNCTION d5.apply_adoption_tasks(json) TO d5_applier;
GRANT EXECUTE ON FUNCTION d5.read_adoption_proposal(uuid,uuid,uuid),d5.read_adoption_package(uuid,uuid,text) TO d5_writer,d5_reader,d5_reviewer,d5_applier;
RESET ROLE;
REVOKE CREATE ON SCHEMA d5 FROM d5_apply_owner;
COMMIT;
