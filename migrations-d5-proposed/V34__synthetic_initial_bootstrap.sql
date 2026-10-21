-- SPDX-License-Identifier: GPL-3.0-only
-- I10: approved I9 bootstrap, disposable V30 + V31/V32/V33 only. No promotion.
BEGIN;
GRANT CREATE ON SCHEMA d5 TO d5_apply_owner;
GRANT SELECT ON d5.preview_artifacts TO d5_apply_owner;
SET LOCAL ROLE d5_apply_owner;
CREATE TABLE d5.bootstrap_proposals(
 proposal_id uuid PRIMARY KEY REFERENCES d5.commands DEFERRABLE INITIALLY DEFERRED,
 manifest_sha256 d5.hash NOT NULL,manifest jsonb NOT NULL,
 CHECK(octet_length(manifest::text)<=4194304),
 CHECK(manifest_sha256=d5.task_hash('d5.bootstrap-task-manifest.v1',manifest))
);
CREATE TABLE d5.bootstrap_reviews(
 command_id uuid PRIMARY KEY REFERENCES d5.commands DEFERRABLE INITIALLY DEFERRED,
 proposal_id uuid NOT NULL REFERENCES d5.bootstrap_proposals,version bigint NOT NULL CHECK(version>0),
 decision text NOT NULL CHECK(decision IN ('ACCEPT','REJECT')),reviewer_label text NOT NULL,reason text NOT NULL,
 UNIQUE(proposal_id,version)
);
CREATE TABLE d5.bootstrap_review_heads(
 proposal_id uuid PRIMARY KEY REFERENCES d5.bootstrap_proposals,version bigint NOT NULL DEFAULT 0,
 review_command_id uuid REFERENCES d5.bootstrap_reviews
);
CREATE TABLE d5.bootstrap_packages(
 package_sha256 d5.hash PRIMARY KEY,project_id uuid NOT NULL,document_id uuid NOT NULL,items jsonb NOT NULL,
 CHECK(package_sha256=d5.task_hash('d5.bootstrap-task-package.v1',jsonb_build_object('project_id',project_id,'document_id',document_id,'items',items)))
);
CREATE TABLE d5.bootstrap_applications(
 package_sha256 d5.hash PRIMARY KEY REFERENCES d5.bootstrap_packages,
 command_id uuid NOT NULL UNIQUE REFERENCES d5.commands DEFERRABLE INITIALLY DEFERRED,
 result jsonb NOT NULL,applied_at timestamptz NOT NULL DEFAULT clock_timestamp()
);
DO $$ DECLARE rel text; BEGIN
 FOREACH rel IN ARRAY ARRAY['bootstrap_proposals','bootstrap_reviews','bootstrap_packages','bootstrap_applications'] LOOP
  EXECUTE format('CREATE TRIGGER immutable BEFORE UPDATE OR DELETE OR TRUNCATE ON d5.%I FOR EACH STATEMENT EXECUTE FUNCTION d5.immutable()',rel);
 END LOOP;
END $$;
CREATE FUNCTION d5.bootstrap_initial(i d5.task_intents) RETURNS boolean LANGUAGE sql STABLE
 SET search_path=pg_catalog,pg_temp AS $$
 SELECT EXISTS(SELECT FROM d5.task_mapping_heads WHERE intent_id=i.intent_id AND version=0 AND source_basis IS NULL AND projection IS NULL)
 AND NOT EXISTS(SELECT FROM d5.task_destinations WHERE intent_id=i.intent_id)
 AND NOT EXISTS(SELECT FROM d5.task_applications WHERE result->'effects' @> jsonb_build_array(jsonb_build_object('task_id',i.task_id)))
 AND NOT EXISTS(SELECT FROM d5.bootstrap_applications WHERE result->'effects' @> jsonb_build_array(jsonb_build_object('intent_id',i.intent_id))) $$;

CREATE FUNCTION d5.prepare_bootstrap_task(envelope json,rowbytes bytea) RETURNS jsonb LANGUAGE plpgsql VOLATILE SECURITY DEFINER
 SET search_path=pg_catalog,pg_temp SET timezone='UTC' AS $$
DECLARE req jsonb;prior jsonb;i d5.task_intents;o d5.observations;ref d5.reference_heads;v jsonb;rowval jsonb;m jsonb;digest text;ch text;
BEGIN
 req=d5.review_envelope(envelope,'PREPARE_BOOTSTRAP_TASK',ARRAY['intent_id','source_key','observation_id','content_sha256','preview_sha256','snapshot_row_sha256','expected_reference_version'],ARRAY['expected_reference_version']);
 PERFORM d5.review_version(req->'expected_reference_version');
 IF rowbytes IS NULL OR octet_length(rowbytes)>2097152 OR encode(public.digest(rowbytes,'sha256'),'hex') IS DISTINCT FROM req->>'snapshot_row_sha256' THEN RAISE EXCEPTION 'Invalid bootstrap row bytes/hash';END IF;
 rowval=convert_from(rowbytes,'UTF8')::jsonb;
 prior=d5.review_prior(req);IF prior IS NOT NULL THEN RETURN prior;END IF;
 SELECT * INTO i FROM d5.task_intents WHERE intent_id=(req->>'intent_id')::uuid AND project_id=(req->>'project_id')::uuid AND document_id=(req->>'document_id')::uuid AND source_key=req->>'source_key';
 IF NOT FOUND THEN RETURN d5.task_conflict(req,'INTENT_SCOPE_CONFLICT');END IF;
 IF NOT d5.bootstrap_initial(i) THEN RETURN d5.task_conflict(req,'INITIAL_INTENT_REQUIRED');END IF;
 SELECT * INTO o FROM d5.observations WHERE observation_id=(req->>'observation_id')::uuid AND document_id=i.document_id AND project_id=i.project_id AND profile=i.profile;
 IF NOT FOUND OR o.preview_sha256 IS DISTINCT FROM req->>'preview_sha256' THEN RETURN d5.task_conflict(req,'OBSERVATION_SCOPE_CONFLICT');END IF;
 SELECT sha256 INTO STRICT ch FROM public.source_revisions WHERE id=o.revision_id AND document_id=i.document_id;
 IF ch IS DISTINCT FROM req->>'content_sha256' THEN RETURN d5.task_conflict(req,'SOURCE_HASH_CONFLICT');END IF;
 SELECT convert_from(preview_bytes,'UTF8')::jsonb INTO STRICT v FROM d5.preview_artifacts WHERE preview_sha256=o.preview_sha256;
 IF EXISTS(SELECT FROM jsonb_array_elements(v->'diagnostics') d WHERE d->'blocking'='true'::jsonb) THEN RETURN d5.task_conflict(req,'OBSERVATION_BLOCKED');END IF;
 IF (SELECT count(*) FROM jsonb_array_elements(v->'proposals') r WHERE r->>'source_key'=i.source_key)<>1 THEN RETURN d5.task_conflict(req,'SOURCE_ROW_NOT_UNIQUE');END IF;
 IF NOT EXISTS(SELECT FROM jsonb_array_elements(v->'proposals') r WHERE r->>'source_key'=i.source_key AND r=rowval) THEN RETURN d5.task_conflict(req,'SNAPSHOT_ROW_CONFLICT');END IF;
 SELECT * INTO STRICT ref FROM d5.reference_heads WHERE document_id=i.document_id AND profile=i.profile;
 IF ref.observation_id IS DISTINCT FROM o.observation_id OR ref.version<>d5.review_version(req->'expected_reference_version') THEN RETURN d5.task_conflict(req,'REFERENCE_VERSION_CONFLICT');END IF;
 IF EXISTS(SELECT FROM public.tasks WHERE id=i.task_id OR (project_id=i.project_id AND task_key=i.task_key)) THEN RETURN d5.task_conflict(req,'TARGET_OCCUPIED');END IF;
 IF jsonb_typeof(rowval#>'{fields,item}') IS DISTINCT FROM 'string'
 OR btrim(rowval#>>'{fields,item}',U&'\0009\000A\000B\000C\000D\0020\0085\00A0\1680\2000\2001\2002\2003\2004\2005\2006\2007\2008\2009\200A\2028\2029\202F\205F\3000')=''
 OR jsonb_typeof(rowval#>'{fields,objective}') IS DISTINCT FROM 'string' THEN RETURN d5.task_conflict(req,'INVALID_PROJECTION');END IF;
 IF rowval->>'source_locator' IS DISTINCT FROM 'sha256:'||ch||'#L'||(rowval->>'line_start') THEN RAISE EXCEPTION 'Invalid source locator';END IF;
 m=jsonb_build_object('schema','d5.bootstrap-task-manifest.v1','mode','BOOTSTRAP_INITIAL','proposal_id',req->>'command_id',
 'intent',to_jsonb(i),'mapping_version',0,'observation_id',o.observation_id,'revision_id',o.revision_id,'content_sha256',ch,'preview_sha256',o.preview_sha256,
 'reference_version',ref.version,'snapshot_row',rowval,'snapshot_row_sha256',req->>'snapshot_row_sha256',
 'action','CREATE_INITIAL_BACKLOG','projection',d5.task_projection(rowval),'source_basis',d5.task_semantic(rowval),
 'source_basis_sha256',d5.task_hash('d5.source-basis.v1',d5.task_semantic(rowval)),'prior_applied_basis',NULL,
 'target_expectation',jsonb_build_object('schema','d5.bootstrap-target-absence.v1','task_id',i.task_id,'project_id',i.project_id,'task_key',i.task_key,'absent',true),
 'prepared_at',clock_timestamp(),'activation_allowed',false);
 digest=d5.task_hash('d5.bootstrap-task-manifest.v1',m);
 INSERT INTO d5.bootstrap_proposals VALUES((req->>'command_id')::uuid,digest,m);
 INSERT INTO d5.bootstrap_review_heads(proposal_id) VALUES((req->>'command_id')::uuid);
 RETURN d5.review_finish(req,jsonb_build_object('status','OK','proposal_id',req->>'command_id','manifest_sha256',digest,'manifest',m,'writes_d2',false));
END $$;

CREATE FUNCTION d5.review_bootstrap_task(envelope json) RETURNS jsonb LANGUAGE plpgsql VOLATILE SECURITY DEFINER
 SET search_path=pg_catalog,pg_temp AS $$
DECLARE req jsonb;prior jsonb;p d5.bootstrap_proposals;h d5.bootstrap_review_heads;v bigint;
BEGIN
 req=d5.review_envelope(envelope,'REVIEW_BOOTSTRAP_TASK',ARRAY['proposal_id','manifest_sha256','expected_version','decision','reviewer_label','reason'],ARRAY['expected_version']);
 v=d5.review_version(req->'expected_version');
 IF req->>'decision' NOT IN ('ACCEPT','REJECT') OR length(req->>'reviewer_label') NOT BETWEEN 1 AND 256 OR length(req->>'reason') NOT BETWEEN 1 AND 1024
 OR req->>'reviewer_label' ~ '[[:cntrl:]]' OR req->>'reason' ~ '[[:cntrl:]]' THEN RAISE EXCEPTION 'Invalid review';END IF;
 prior=d5.review_prior(req);IF prior IS NOT NULL THEN RETURN prior;END IF;
 SELECT * INTO p FROM d5.bootstrap_proposals WHERE proposal_id=(req->>'proposal_id')::uuid AND manifest_sha256=req->>'manifest_sha256'
 AND manifest#>>'{intent,project_id}'=req->>'project_id' AND manifest#>>'{intent,document_id}'=req->>'document_id';
 IF NOT FOUND THEN RETURN d5.task_conflict(req,'MANIFEST_SCOPE_CONFLICT');END IF;
 SELECT * INTO STRICT h FROM d5.bootstrap_review_heads WHERE proposal_id=p.proposal_id FOR UPDATE;
 IF h.version<>v THEN RETURN d5.task_conflict(req,'REVIEW_VERSION_CONFLICT');END IF;
 INSERT INTO d5.bootstrap_reviews VALUES((req->>'command_id')::uuid,p.proposal_id,v+1,req->>'decision',req->>'reviewer_label',req->>'reason');
 UPDATE d5.bootstrap_review_heads SET version=v+1,review_command_id=(req->>'command_id')::uuid WHERE proposal_id=p.proposal_id;
 RETURN d5.review_finish(req,jsonb_build_object('status','OK','proposal_id',p.proposal_id,'version_at_commit',v+1,'writes_d2',false));
END $$;
CREATE FUNCTION d5.package_bootstrap_tasks(envelope json) RETURNS jsonb LANGUAGE plpgsql VOLATILE SECURITY DEFINER
 SET search_path=pg_catalog,pg_temp AS $$
DECLARE req jsonb;prior jsonb;pin jsonb;p d5.bootstrap_proposals;h d5.bootstrap_review_heads;digest text;keys text[];
BEGIN
 req=d5.review_envelope(envelope,'PACKAGE_BOOTSTRAP_TASKS',ARRAY['items'],ARRAY['items']);
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
 SELECT * INTO p FROM d5.bootstrap_proposals WHERE proposal_id=(pin->>'proposal_id')::uuid;
 IF NOT FOUND OR p.manifest_sha256<>pin->>'manifest_sha256' OR p.manifest#>>'{intent,project_id}'<>req->>'project_id' OR p.manifest#>>'{intent,document_id}'<>req->>'document_id' THEN RETURN d5.task_conflict(req,'MANIFEST_SCOPE_CONFLICT');END IF;
 SELECT * INTO STRICT h FROM d5.bootstrap_review_heads WHERE proposal_id=p.proposal_id;
 IF h.version<>d5.review_version(pin->'review_version') OR h.review_command_id IS DISTINCT FROM (pin->>'review_command_id')::uuid
 OR NOT EXISTS(SELECT FROM d5.bootstrap_reviews WHERE command_id=h.review_command_id AND decision='ACCEPT') THEN RETURN d5.task_conflict(req,'MANIFEST_NOT_ACCEPTED');END IF;
 END LOOP;
 IF EXISTS(SELECT FROM jsonb_array_elements(req->'items') x JOIN d5.bootstrap_proposals tp ON tp.proposal_id=(x->>'proposal_id')::uuid GROUP BY tp.manifest#>>'{intent,intent_id}' HAVING count(*)>1) THEN RAISE EXCEPTION 'One proposal per intent required';END IF;
 digest=d5.task_hash('d5.bootstrap-task-package.v1',jsonb_build_object('project_id',req->>'project_id','document_id',req->>'document_id','items',req->'items'));
 INSERT INTO d5.bootstrap_packages VALUES(digest,(req->>'project_id')::uuid,(req->>'document_id')::uuid,req->'items') ON CONFLICT DO NOTHING;
 RETURN d5.review_finish(req,jsonb_build_object('status','OK','package_sha256',digest,'writes_d2',false));
END $$;

CREATE FUNCTION d5.validate_bootstrap(p d5.bootstrap_proposals,pin jsonb) RETURNS text LANGUAGE plpgsql VOLATILE
 SET search_path=pg_catalog,pg_temp AS $$
DECLARE m jsonb=p.manifest;i d5.task_intents;h d5.bootstrap_review_heads;ref d5.reference_heads;
BEGIN
 SELECT * INTO STRICT i FROM d5.task_intents WHERE intent_id=(m#>>'{intent,intent_id}')::uuid FOR UPDATE;
 PERFORM 1 FROM d5.task_mapping_heads WHERE intent_id=i.intent_id FOR UPDATE;
 IF to_jsonb(i) IS DISTINCT FROM m->'intent' OR NOT d5.bootstrap_initial(i) THEN RETURN 'INITIAL_INTENT_REQUIRED';END IF;
 SELECT * INTO STRICT h FROM d5.bootstrap_review_heads WHERE proposal_id=p.proposal_id;
 IF h.version<>d5.review_version(pin->'review_version') OR h.review_command_id IS DISTINCT FROM (pin->>'review_command_id')::uuid
 OR NOT EXISTS(SELECT FROM d5.bootstrap_reviews WHERE command_id=h.review_command_id AND decision='ACCEPT') THEN RETURN 'BOOTSTRAP_REVIEW_CONFLICT';END IF;
 SELECT * INTO STRICT ref FROM d5.reference_heads WHERE document_id=i.document_id AND profile=i.profile;
 IF ref.version<>d5.review_version(m->'reference_version') OR ref.observation_id IS DISTINCT FROM (m->>'observation_id')::uuid THEN RETURN 'REFERENCE_VERSION_CONFLICT';END IF;
 IF EXISTS(SELECT FROM public.tasks WHERE id=i.task_id OR (project_id=i.project_id AND task_key=i.task_key)) THEN RETURN 'TARGET_OCCUPIED';END IF;
 RETURN NULL;
END $$;
CREATE FUNCTION d5.apply_bootstrap_tasks(envelope json) RETURNS jsonb LANGUAGE plpgsql VOLATILE SECURITY DEFINER
 SET search_path=pg_catalog,pg_temp SET timezone='UTC' AS $$
DECLARE req jsonb;prior jsonb;pkg d5.bootstrap_packages;pin jsonb;p d5.bootstrap_proposals;m jsonb;i d5.task_intents;code text;effects jsonb='[]'::jsonb;result jsonb;original d5.bootstrap_applications;
BEGIN
 req=d5.review_envelope(envelope,'APPLY_BOOTSTRAP_TASKS',ARRAY['package_sha256']);
 PERFORM d5.task_lock_boundary();
 prior=d5.review_prior(req);IF prior IS NOT NULL THEN RETURN prior;END IF;
 SELECT * INTO pkg FROM d5.bootstrap_packages WHERE package_sha256=req->>'package_sha256' AND project_id=(req->>'project_id')::uuid AND document_id=(req->>'document_id')::uuid;
 IF NOT FOUND THEN RETURN d5.task_conflict(req,'BOOTSTRAP_PACKAGE_SCOPE_CONFLICT');END IF;
 SELECT * INTO original FROM d5.bootstrap_applications WHERE package_sha256=pkg.package_sha256;
 IF FOUND THEN RETURN d5.review_finish(req,jsonb_build_object('status','ALREADY_APPLIED','original_command_id',original.command_id,'package_sha256',pkg.package_sha256,'writes_d2',false));END IF;
 FOR pin IN SELECT x FROM jsonb_array_elements(pkg.items) x JOIN d5.bootstrap_proposals bp ON bp.proposal_id=(x->>'proposal_id')::uuid ORDER BY bp.manifest#>>'{intent,intent_id}' LOOP
  SELECT * INTO STRICT p FROM d5.bootstrap_proposals WHERE proposal_id=(pin->>'proposal_id')::uuid;
  IF p.manifest_sha256 IS DISTINCT FROM pin->>'manifest_sha256' OR p.manifest_sha256 IS DISTINCT FROM d5.task_hash('d5.bootstrap-task-manifest.v1',p.manifest) THEN RAISE EXCEPTION 'Bootstrap manifest integrity failure';END IF;
  code=d5.validate_bootstrap(p,pin);IF code IS NOT NULL THEN RETURN d5.task_conflict(req,code);END IF;
 END LOOP;
 FOR pin IN SELECT * FROM jsonb_array_elements(pkg.items) LOOP
  SELECT * INTO STRICT p FROM d5.bootstrap_proposals WHERE proposal_id=(pin->>'proposal_id')::uuid;m=p.manifest;
  SELECT * INTO STRICT i FROM d5.task_intents WHERE intent_id=(m#>>'{intent,intent_id}')::uuid;
  INSERT INTO public.tasks(id,project_id,task_key,title,description,status,row_version,epic_id,urgency,deadline_at,deferred_count)
   VALUES(i.task_id,i.project_id,i.task_key,m#>>'{projection,title}',m#>>'{projection,description}','BACKLOG',0,NULL,0,NULL,0);
  INSERT INTO d5.task_destinations VALUES(i.intent_id,i.task_id,i.project_id);
  IF NOT EXISTS(SELECT FROM d5.observations o JOIN public.source_revisions r ON r.id=o.revision_id WHERE o.observation_id=(m->>'observation_id')::uuid
   AND o.document_id=i.document_id AND o.project_id=i.project_id AND o.profile=i.profile AND o.revision_id=(m->>'revision_id')::uuid
   AND r.sha256=m->>'content_sha256' AND o.preview_sha256=m->>'preview_sha256'
   AND m#>>'{snapshot_row,source_locator}'='sha256:'||r.sha256||'#L'||(m#>>'{snapshot_row,line_start}')) THEN RAISE EXCEPTION 'Bootstrap provenance integrity failure';END IF;
  INSERT INTO d2.task_sources VALUES(i.task_id,(m->>'revision_id')::uuid,m#>>'{snapshot_row,source_locator}',i.document_id,i.project_id);
  UPDATE d5.task_mapping_heads SET version=1,source_basis=m->'source_basis',projection=m->'projection' WHERE intent_id=i.intent_id;
  INSERT INTO public.audit_events(actor,entity_type,entity_id,action,payload) VALUES(session_user,'D5_TASK_IMPORT',i.task_id,'CREATE_INITIAL_BACKLOG',
   jsonb_build_object('command_id',req->>'command_id','manifest_sha256',p.manifest_sha256,'package_sha256',pkg.package_sha256,'activation_allowed',false));
  effects=effects||jsonb_build_array(jsonb_build_object('intent_id',i.intent_id,'task_id',i.task_id,'action','CREATE_INITIAL_BACKLOG','manifest_sha256',p.manifest_sha256));
 END LOOP;
 result=jsonb_build_object('status','OK','package_sha256',pkg.package_sha256,'effects',effects,'writes_d2',true,'activation_allowed',false);
 INSERT INTO d5.bootstrap_applications(package_sha256,command_id,result) VALUES(pkg.package_sha256,(req->>'command_id')::uuid,result);
 RETURN d5.review_finish(req,result);
END $$;
CREATE FUNCTION d5.read_bootstrap_proposal(pid uuid,doc uuid,proposal uuid) RETURNS jsonb LANGUAGE sql STABLE SECURITY DEFINER
 SET search_path=pg_catalog,pg_temp AS $$ SELECT jsonb_build_object('proposal_id',p.proposal_id,'manifest_sha256',p.manifest_sha256,'manifest',p.manifest,
 'review_version',h.version,'review_command_id',h.review_command_id) FROM d5.bootstrap_proposals p JOIN d5.bootstrap_review_heads h USING(proposal_id)
 WHERE p.proposal_id=proposal AND p.manifest#>>'{intent,project_id}'=pid::text AND p.manifest#>>'{intent,document_id}'=doc::text $$;
CREATE FUNCTION d5.read_bootstrap_package(pid uuid,doc uuid,digest text) RETURNS jsonb LANGUAGE sql STABLE SECURITY DEFINER
 SET search_path=pg_catalog,pg_temp AS $$ SELECT to_jsonb(p) FROM d5.bootstrap_packages p WHERE p.project_id=pid AND p.document_id=doc AND p.package_sha256=digest $$;
GRANT EXECUTE ON FUNCTION d5.prepare_bootstrap_task(json,bytea),d5.package_bootstrap_tasks(json) TO d5_writer;
GRANT EXECUTE ON FUNCTION d5.review_bootstrap_task(json) TO d5_reviewer;
GRANT EXECUTE ON FUNCTION d5.apply_bootstrap_tasks(json) TO d5_applier;
GRANT EXECUTE ON FUNCTION d5.read_bootstrap_proposal(uuid,uuid,uuid),d5.read_bootstrap_package(uuid,uuid,text) TO d5_writer,d5_reader,d5_reviewer,d5_applier;
RESET ROLE;
REVOKE CREATE ON SCHEMA d5 FROM d5_apply_owner;
COMMIT;
