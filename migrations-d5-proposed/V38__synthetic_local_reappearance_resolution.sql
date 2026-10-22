-- SPDX-License-Identifier: GPL-3.0-only
-- I18: approved I17, fresh synthetic V30 + V31-V37 only. No promotion/activation.
BEGIN;
GRANT CREATE ON SCHEMA d5 TO d5_apply_owner;
SET LOCAL ROLE d5_apply_owner;
CREATE TABLE d5.local_reappearance_proposals(
 proposal_id uuid PRIMARY KEY REFERENCES d5.commands DEFERRABLE INITIALLY DEFERRED,
 manifest_sha256 d5.hash NOT NULL,manifest jsonb NOT NULL,
 CHECK(octet_length(manifest::text)<=4194304),
 CHECK(manifest_sha256=d5.task_hash('d5.local-reappearance-task-manifest.v1',manifest))
);
CREATE TABLE d5.local_reappearance_reviews(
 command_id uuid PRIMARY KEY REFERENCES d5.commands DEFERRABLE INITIALLY DEFERRED,
 proposal_id uuid NOT NULL REFERENCES d5.local_reappearance_proposals,version bigint NOT NULL CHECK(version>0),
 decision text NOT NULL CHECK(decision IN ('ACCEPT','REJECT')),reviewer_label text NOT NULL,reason text NOT NULL,
 UNIQUE(proposal_id,version)
);
CREATE TABLE d5.local_reappearance_review_heads(
 proposal_id uuid PRIMARY KEY REFERENCES d5.local_reappearance_proposals,version bigint NOT NULL DEFAULT 0,
 review_command_id uuid REFERENCES d5.local_reappearance_reviews
);
CREATE TABLE d5.local_reappearance_packages(
 package_sha256 d5.hash PRIMARY KEY,project_id uuid NOT NULL,document_id uuid NOT NULL,items jsonb NOT NULL,
 CHECK(package_sha256=d5.task_hash('d5.local-reappearance-task-package.v1',jsonb_build_object('project_id',project_id,'document_id',document_id,'items',items)))
);
CREATE TABLE d5.local_reappearance_applications(
 package_sha256 d5.hash PRIMARY KEY REFERENCES d5.local_reappearance_packages,
 command_id uuid NOT NULL UNIQUE REFERENCES d5.commands DEFERRABLE INITIALLY DEFERRED,
 result jsonb NOT NULL,applied_at timestamptz NOT NULL DEFAULT clock_timestamp()
);
DO $$ DECLARE rel text; BEGIN
 FOREACH rel IN ARRAY ARRAY['local_reappearance_proposals','local_reappearance_reviews','local_reappearance_packages','local_reappearance_applications'] LOOP
  EXECUTE format('CREATE TRIGGER immutable BEFORE UPDATE OR DELETE OR TRUNCATE ON d5.%I FOR EACH STATEMENT EXECUTE FUNCTION d5.immutable()',rel);
 END LOOP;
END $$;
CREATE FUNCTION d5.prepare_local_reappearance_task(envelope json) RETURNS jsonb LANGUAGE plpgsql VOLATILE SECURITY DEFINER
 SET search_path=pg_catalog,pg_temp SET timezone='UTC' AS $$
DECLARE req jsonb;prior jsonb;i d5.task_intents;h d5.task_mapping_heads;r d5.comparison_reports;rh d5.row_review_heads;
 ref d5.reference_heads;rv jsonb;m jsonb;t jsonb;code text;digest text;act text;l jsonb;sp jsonb;chosen jsonb;proof jsonb;
BEGIN
 req=d5.review_envelope(envelope,'PREPARE_LOCAL_REAPPEARANCE_TASK',ARRAY['intent_id','comparison_id','report_sha256','row_sha256','expected_reference_version','expected_mapping_version','choice','reason','absence_application_command_id','absence_proposal_id','identity_declaration','identity_reason'],ARRAY['expected_reference_version','expected_mapping_version']);
 PERFORM d5.review_version(req->'expected_reference_version');PERFORM d5.review_version(req->'expected_mapping_version');
 prior=d5.review_prior(req);IF prior IS NOT NULL THEN RETURN prior;END IF;
 IF req->>'choice' NOT IN ('USE_SOURCE','KEEP_LOCAL') OR length(req->>'reason') NOT BETWEEN 1 AND 1024
 OR btrim(req->>'reason',U&'\0009\000A\000B\000C\000D\0020\0085\00A0\1680\2000\2001\2002\2003\2004\2005\2006\2007\2008\2009\200A\2028\2029\202F\205F\3000')='' OR req->>'reason' ~ '[[:cntrl:]]'
 THEN RETURN d5.task_conflict(req,'RESOLUTION_CHOICE_REQUIRED');END IF;
 IF req->>'identity_declaration'<>'SAME_SOURCE_ENTITY' OR length(req->>'identity_reason') NOT BETWEEN 1 AND 1024 OR btrim(req->>'identity_reason',U&'\0009\000A\000B\000C\000D\0020\0085\00A0\1680\2000\2001\2002\2003\2004\2005\2006\2007\2008\2009\200A\2028\2029\202F\205F\3000')='' OR req->>'identity_reason' ~ '[[:cntrl:]]'
 THEN RETURN d5.task_conflict(req,'IDENTITY_DECLARATION_REQUIRED');END IF;
 SELECT * INTO i FROM d5.task_intents WHERE intent_id=(req->>'intent_id')::uuid AND project_id=(req->>'project_id')::uuid AND document_id=(req->>'document_id')::uuid;
 IF NOT FOUND THEN RETURN d5.task_conflict(req,'INTENT_SCOPE_CONFLICT');END IF;
 SELECT * INTO STRICT h FROM d5.task_mapping_heads WHERE intent_id=i.intent_id;
 IF h.version<>d5.review_version(req->'expected_mapping_version') OR h.source_basis IS NULL OR h.projection IS NULL THEN RETURN d5.task_conflict(req,'MAPPING_VERSION_CONFLICT');END IF;
 proof=d5.read_reappearance_absence(i.project_id,i.document_id,(req->>'absence_application_command_id')::uuid,(req->>'absence_proposal_id')::uuid);
 IF proof IS NULL OR proof#>>'{absence_manifest,intent,intent_id}'<>i.intent_id::text THEN RETURN d5.task_conflict(req,'APPLIED_ABSENCE_REQUIRED');END IF;
 IF d5.review_version(proof->'mapping_version_after')<>h.version OR proof#>'{absence_manifest,before_projection}' IS DISTINCT FROM h.projection THEN RETURN d5.task_conflict(req,'ABSENCE_VERSION_CONFLICT');END IF;
 SELECT cr.* INTO r FROM d5.comparisons c JOIN d5.comparison_reports cr USING(report_sha256) WHERE c.comparison_id=(req->>'comparison_id')::uuid;
 IF NOT FOUND OR r.project_id<>i.project_id OR r.document_id<>i.document_id OR r.profile<>i.profile OR r.report_sha256<>req->>'report_sha256'
 OR r.state<>'PREVIEW_ONLY' THEN RETURN d5.task_conflict(req,'COMPARISON_SCOPE_CONFLICT');END IF;
 SELECT convert_from(row_bytes,'UTF8')::jsonb INTO rv FROM d5.review_items WHERE comparison_id=(req->>'comparison_id')::uuid AND source_key=i.source_key AND row_sha256=req->>'row_sha256';
 IF NOT FOUND OR rv->>'change'<>'ADDED' OR rv#>'{before,row}' IS DISTINCT FROM 'null'::jsonb OR rv#>'{after,row}'='null'::jsonb THEN RETURN d5.task_conflict(req,'REAPPEARANCE_ROW_REQUIRED');END IF;
 SELECT * INTO STRICT rh FROM d5.row_review_heads WHERE comparison_id=(req->>'comparison_id')::uuid AND source_key=i.source_key;
 IF NOT EXISTS(SELECT FROM d5.row_decisions WHERE command_id=rh.decision_command_id AND decision='ACCEPT') THEN RETURN d5.task_conflict(req,'SOURCE_NOT_ACCEPTED');END IF;
 SELECT * INTO STRICT ref FROM d5.reference_heads WHERE document_id=i.document_id AND profile=i.profile;
 IF ref.observation_id IS DISTINCT FROM r.before_observation_id OR ref.version<>d5.review_version(req->'expected_reference_version') THEN RETURN d5.task_conflict(req,'REFERENCE_VERSION_CONFLICT');END IF;
 code=d5.local_edit_target_guard(i,h.projection);IF code IS NOT NULL THEN RETURN d5.task_conflict(req,code);END IF;
 IF jsonb_typeof(rv#>'{after,row,fields,item}') IS DISTINCT FROM 'string'
 OR btrim(rv#>>'{after,row,fields,item}',U&'\0009\000A\000B\000C\000D\0020\0085\00A0\1680\2000\2001\2002\2003\2004\2005\2006\2007\2008\2009\200A\2028\2029\202F\205F\3000')=''
 OR jsonb_typeof(rv#>'{after,row,fields,objective}') IS DISTINCT FROM 'string' THEN RETURN d5.task_conflict(req,'INVALID_PROJECTION');END IF;
 t=d5.task_target(i.task_id);l=jsonb_build_object('title',t->'title','description',t->'description');sp=d5.task_projection(rv#>'{after,row}');
 IF NOT d5.local_edit_valid_projection(l,true) OR NOT d5.local_edit_valid_projection(sp,false) THEN RETURN d5.task_conflict(req,'INVALID_PROJECTION');END IF;
 chosen=CASE WHEN req->>'choice'='USE_SOURCE' THEN sp ELSE l END;
 act=CASE WHEN req->>'choice'='KEEP_LOCAL' THEN 'KEEP_LOCAL_REAPPEARANCE' WHEN chosen=l THEN 'LINK_LOCAL_REAPPEARANCE_EVIDENCE' ELSE 'PATCH_LOCAL_REAPPEARANCE_USE_SOURCE' END;
 m=jsonb_build_object('schema','d5.local-reappearance-task-manifest.v1','mode','LOCAL_REAPPEARANCE','proposal_id',req->>'command_id',
 'intent',to_jsonb(i),'mapping_version',h.version,'last_applied_basis',h.source_basis,'last_applied_basis_sha256',h.source_basis_sha256,'before_projection',h.projection,
 'comparison_id',req->>'comparison_id','report_sha256',r.report_sha256,'row_sha256',req->>'row_sha256','source_change',rv,
 'before_observation_id',r.before_observation_id,'after_observation_id',r.after_observation_id,'after_revision_id',(SELECT revision_id FROM d5.observations WHERE observation_id=r.after_observation_id),
 'source_decision_command_id',rh.decision_command_id,'source_decision_version',rh.version,'reference_version',ref.version,'absence_proof',proof,'identity_declaration',req->>'identity_declaration','identity_reason',req->>'identity_reason')||jsonb_build_object(
 'choice',req->>'choice','reason',req->>'reason','action',act,'local_projection',l,'result_projection',chosen,
 'task_fields_to_write',CASE WHEN act='PATCH_LOCAL_REAPPEARANCE_USE_SOURCE' THEN to_jsonb(ARRAY['title','description','row_version']) ELSE '[]'::jsonb END,
 'before_projection_sha256',d5.task_hash('d5.local-reappearance-projection.v1',h.projection),'local_projection_sha256',d5.task_hash('d5.local-reappearance-projection.v1',l),
 'after_projection_sha256',d5.task_hash('d5.local-reappearance-projection.v1',sp),'result_projection_sha256',d5.task_hash('d5.local-reappearance-projection.v1',chosen),
 'after_projection',d5.task_projection(rv#>'{after,row}'),'after_basis',d5.task_semantic(rv#>'{after,row}'),'after_basis_sha256',d5.task_hash('d5.source-basis.v1',d5.task_semantic(rv#>'{after,row}')),
 'target_schema','d5.task-target.v1','target',t,'target_sha256',d5.task_hash('d5.task-target.v1',t),'prepared_at',clock_timestamp(),'activation_allowed',false);
 digest=d5.task_hash('d5.local-reappearance-task-manifest.v1',m);
 INSERT INTO d5.local_reappearance_proposals VALUES((req->>'command_id')::uuid,digest,m);
 INSERT INTO d5.local_reappearance_review_heads(proposal_id) VALUES((req->>'command_id')::uuid);
 RETURN d5.review_finish(req,jsonb_build_object('status','OK','proposal_id',req->>'command_id','manifest_sha256',digest,'manifest',m,'writes_d2',false));
END $$;

CREATE FUNCTION d5.review_local_reappearance_task(envelope json) RETURNS jsonb LANGUAGE plpgsql VOLATILE SECURITY DEFINER
 SET search_path=pg_catalog,pg_temp AS $$
DECLARE req jsonb;prior jsonb;p d5.local_reappearance_proposals;h d5.local_reappearance_review_heads;v bigint;
BEGIN
 req=d5.review_envelope(envelope,'REVIEW_LOCAL_REAPPEARANCE_TASK',ARRAY['proposal_id','manifest_sha256','expected_version','decision','reviewer_label','reason'],ARRAY['expected_version']);
 v=d5.review_version(req->'expected_version');
 IF req->>'decision' NOT IN ('ACCEPT','REJECT') OR length(req->>'reviewer_label') NOT BETWEEN 1 AND 256 OR length(req->>'reason') NOT BETWEEN 1 AND 1024
 OR req->>'reviewer_label' ~ '[[:cntrl:]]' OR req->>'reason' ~ '[[:cntrl:]]' THEN RAISE EXCEPTION 'Invalid review';END IF;
 prior=d5.review_prior(req);IF prior IS NOT NULL THEN RETURN prior;END IF;
 SELECT * INTO p FROM d5.local_reappearance_proposals WHERE proposal_id=(req->>'proposal_id')::uuid AND manifest_sha256=req->>'manifest_sha256'
 AND manifest#>>'{intent,project_id}'=req->>'project_id' AND manifest#>>'{intent,document_id}'=req->>'document_id';
 IF NOT FOUND THEN RETURN d5.task_conflict(req,'MANIFEST_SCOPE_CONFLICT');END IF;
 SELECT * INTO STRICT h FROM d5.local_reappearance_review_heads WHERE proposal_id=p.proposal_id FOR UPDATE;
 IF h.version<>v THEN RETURN d5.task_conflict(req,'REVIEW_VERSION_CONFLICT');END IF;
 INSERT INTO d5.local_reappearance_reviews VALUES((req->>'command_id')::uuid,p.proposal_id,v+1,req->>'decision',req->>'reviewer_label',req->>'reason');
 UPDATE d5.local_reappearance_review_heads SET version=v+1,review_command_id=(req->>'command_id')::uuid WHERE proposal_id=p.proposal_id;
 RETURN d5.review_finish(req,jsonb_build_object('status','OK','proposal_id',p.proposal_id,'version_at_commit',v+1,'writes_d2',false));
END $$;
CREATE FUNCTION d5.package_local_reappearance_tasks(envelope json) RETURNS jsonb LANGUAGE plpgsql VOLATILE SECURITY DEFINER
 SET search_path=pg_catalog,pg_temp AS $$
DECLARE req jsonb;prior jsonb;pin jsonb;p d5.local_reappearance_proposals;h d5.local_reappearance_review_heads;digest text;keys text[];
BEGIN
 req=d5.review_envelope(envelope,'PACKAGE_LOCAL_REAPPEARANCE_TASKS',ARRAY['items'],ARRAY['items']);
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
 SELECT * INTO p FROM d5.local_reappearance_proposals WHERE proposal_id=(pin->>'proposal_id')::uuid;
 IF NOT FOUND OR p.manifest_sha256<>pin->>'manifest_sha256' OR p.manifest#>>'{intent,project_id}'<>req->>'project_id' OR p.manifest#>>'{intent,document_id}'<>req->>'document_id' THEN RETURN d5.task_conflict(req,'MANIFEST_SCOPE_CONFLICT');END IF;
 SELECT * INTO STRICT h FROM d5.local_reappearance_review_heads WHERE proposal_id=p.proposal_id;
 IF h.version<>d5.review_version(pin->'review_version') OR h.review_command_id IS DISTINCT FROM (pin->>'review_command_id')::uuid
 OR NOT EXISTS(SELECT FROM d5.local_reappearance_reviews WHERE command_id=h.review_command_id AND decision='ACCEPT') THEN RETURN d5.task_conflict(req,'MANIFEST_NOT_ACCEPTED');END IF;
 END LOOP;
 IF EXISTS(SELECT FROM jsonb_array_elements(req->'items') x JOIN d5.local_reappearance_proposals tp ON tp.proposal_id=(x->>'proposal_id')::uuid GROUP BY tp.manifest#>>'{intent,intent_id}' HAVING count(*)>1) THEN RAISE EXCEPTION 'One proposal per intent required';END IF;
 digest=d5.task_hash('d5.local-reappearance-task-package.v1',jsonb_build_object('project_id',req->>'project_id','document_id',req->>'document_id','items',req->'items'));
 INSERT INTO d5.local_reappearance_packages VALUES(digest,(req->>'project_id')::uuid,(req->>'document_id')::uuid,req->'items') ON CONFLICT DO NOTHING;
 RETURN d5.review_finish(req,jsonb_build_object('status','OK','package_sha256',digest,'writes_d2',false));
END $$;

CREATE FUNCTION d5.validate_local_reappearance(p d5.local_reappearance_proposals,pin jsonb) RETURNS text LANGUAGE plpgsql VOLATILE
 SET search_path=pg_catalog,pg_temp AS $$
DECLARE m jsonb=p.manifest;i d5.task_intents;h d5.task_mapping_heads;rh d5.local_reappearance_review_heads;sr d5.row_review_heads;ref d5.reference_heads;code text;t jsonb;l jsonb;chosen jsonb;act text;proof jsonb;
BEGIN
 SELECT * INTO STRICT i FROM d5.task_intents WHERE intent_id=(m#>>'{intent,intent_id}')::uuid FOR UPDATE;
 SELECT * INTO STRICT h FROM d5.task_mapping_heads WHERE intent_id=i.intent_id FOR UPDATE;
 IF to_jsonb(i) IS DISTINCT FROM m->'intent' OR h.version<>d5.review_version(m->'mapping_version') OR h.source_basis IS DISTINCT FROM m->'last_applied_basis'
 OR h.source_basis_sha256 IS DISTINCT FROM m->>'last_applied_basis_sha256' OR h.projection IS DISTINCT FROM m->'before_projection' THEN RETURN 'MAPPING_VERSION_CONFLICT';END IF;
 proof=d5.read_reappearance_absence(i.project_id,i.document_id,(m#>>'{absence_proof,application_command_id}')::uuid,(m#>>'{absence_proof,absence_proposal_id}')::uuid);
 IF proof IS DISTINCT FROM m->'absence_proof' OR d5.review_version(proof->'mapping_version_after')<>h.version THEN RETURN 'ABSENCE_VERSION_CONFLICT';END IF;
 SELECT * INTO STRICT rh FROM d5.local_reappearance_review_heads WHERE proposal_id=p.proposal_id;
 IF rh.version<>d5.review_version(pin->'review_version') OR rh.review_command_id IS DISTINCT FROM (pin->>'review_command_id')::uuid
 OR NOT EXISTS(SELECT FROM d5.local_reappearance_reviews WHERE command_id=rh.review_command_id AND decision='ACCEPT') THEN RETURN 'LOCAL_REAPPEARANCE_REVIEW_CONFLICT';END IF;
 SELECT * INTO STRICT sr FROM d5.row_review_heads WHERE comparison_id=(m->>'comparison_id')::uuid AND source_key=i.source_key;
 IF sr.version<>d5.review_version(m->'source_decision_version') OR sr.decision_command_id IS DISTINCT FROM (m->>'source_decision_command_id')::uuid
 OR NOT EXISTS(SELECT FROM d5.row_decisions WHERE command_id=sr.decision_command_id AND decision='ACCEPT') THEN RETURN 'SOURCE_REVIEW_CONFLICT';END IF;
 SELECT * INTO STRICT ref FROM d5.reference_heads WHERE document_id=i.document_id AND profile=i.profile;
 IF ref.version<>d5.review_version(m->'reference_version') OR ref.observation_id IS DISTINCT FROM (m->>'before_observation_id')::uuid THEN RETURN 'REFERENCE_VERSION_CONFLICT';END IF;
 code=d5.local_edit_target_guard(i,h.projection);IF code IS NOT NULL THEN RETURN code;END IF;
 t=d5.task_target(i.task_id);l=jsonb_build_object('title',t->'title','description',t->'description');
 chosen=CASE WHEN m->>'choice'='USE_SOURCE' THEN m->'after_projection' ELSE l END;
 act=CASE WHEN m->>'choice'='KEEP_LOCAL' THEN 'KEEP_LOCAL_REAPPEARANCE' WHEN chosen=l THEN 'LINK_LOCAL_REAPPEARANCE_EVIDENCE' ELSE 'PATCH_LOCAL_REAPPEARANCE_USE_SOURCE' END;
 IF m->>'choice' NOT IN ('USE_SOURCE','KEEP_LOCAL') OR m->>'action' IS DISTINCT FROM act OR m->'result_projection' IS DISTINCT FROM chosen
 OR m->'local_projection' IS DISTINCT FROM l OR NOT d5.local_edit_valid_projection(l,true)
 OR NOT d5.local_edit_valid_projection(m->'after_projection',false)
 OR m->'after_projection' IS DISTINCT FROM d5.task_projection(m#>'{source_change,after,row}')
 OR m->'after_basis' IS DISTINCT FROM d5.task_semantic(m#>'{source_change,after,row}')
 OR m#>>'{source_change,change}' IS DISTINCT FROM 'ADDED' OR m#>'{source_change,before,row}' IS DISTINCT FROM 'null'::jsonb
 OR m->>'identity_declaration' IS DISTINCT FROM 'SAME_SOURCE_ENTITY'
 THEN RETURN 'RESOLUTION_CONTENT_CONFLICT';END IF;
 IF t IS DISTINCT FROM m->'target' OR d5.task_hash('d5.task-target.v1',t) IS DISTINCT FROM m->>'target_sha256' THEN RETURN 'TARGET_CAS_CONFLICT';END IF;
 RETURN NULL;
END $$;
CREATE FUNCTION d5.apply_local_reappearance_tasks(envelope json) RETURNS jsonb LANGUAGE plpgsql VOLATILE SECURITY DEFINER
 SET search_path=pg_catalog,pg_temp SET timezone='UTC' AS $$
DECLARE req jsonb;prior jsonb;pkg d5.local_reappearance_packages;pin jsonb;p d5.local_reappearance_proposals;m jsonb;i d5.task_intents;code text;effects jsonb='[]'::jsonb;result jsonb;original d5.local_reappearance_applications;rid uuid;locator text;
BEGIN
 req=d5.review_envelope(envelope,'APPLY_LOCAL_REAPPEARANCE_TASKS',ARRAY['package_sha256']);
 PERFORM d5.task_lock_boundary();prior=d5.review_prior(req);IF prior IS NOT NULL THEN RETURN prior;END IF;
 SELECT * INTO pkg FROM d5.local_reappearance_packages WHERE package_sha256=req->>'package_sha256' AND project_id=(req->>'project_id')::uuid AND document_id=(req->>'document_id')::uuid;
 IF NOT FOUND THEN RETURN d5.task_conflict(req,'LOCAL_REAPPEARANCE_PACKAGE_SCOPE_CONFLICT');END IF;
 SELECT * INTO original FROM d5.local_reappearance_applications WHERE package_sha256=pkg.package_sha256;
 IF FOUND THEN RETURN d5.review_finish(req,jsonb_build_object('status','ALREADY_APPLIED','original_command_id',original.command_id,'package_sha256',pkg.package_sha256,'writes_d2',false));END IF;
 FOR pin IN SELECT x FROM jsonb_array_elements(pkg.items) x JOIN d5.local_reappearance_proposals rp ON rp.proposal_id=(x->>'proposal_id')::uuid ORDER BY rp.manifest#>>'{intent,intent_id}' LOOP
  SELECT * INTO STRICT p FROM d5.local_reappearance_proposals WHERE proposal_id=(pin->>'proposal_id')::uuid;
  IF p.manifest_sha256 IS DISTINCT FROM pin->>'manifest_sha256' OR p.manifest_sha256 IS DISTINCT FROM d5.task_hash('d5.local-reappearance-task-manifest.v1',p.manifest) THEN RAISE EXCEPTION 'Local reappearance manifest integrity failure';END IF;
  code=d5.validate_local_reappearance(p,pin);IF code IS NOT NULL THEN RETURN d5.task_conflict(req,code);END IF;
 END LOOP;
 FOR pin IN SELECT * FROM jsonb_array_elements(pkg.items) LOOP
  SELECT * INTO STRICT p FROM d5.local_reappearance_proposals WHERE proposal_id=(pin->>'proposal_id')::uuid;m=p.manifest;
  SELECT * INTO STRICT i FROM d5.task_intents WHERE intent_id=(m#>>'{intent,intent_id}')::uuid;
  IF m->>'action'='PATCH_LOCAL_REAPPEARANCE_USE_SOURCE' THEN
   UPDATE public.tasks SET title=m#>>'{result_projection,title}',description=m#>>'{result_projection,description}',row_version=row_version+1 WHERE id=i.task_id;
  END IF;
  rid=(m->>'after_revision_id')::uuid;locator=m#>>'{source_change,after,row,source_locator}';
  IF NOT EXISTS(SELECT FROM d5.observations o JOIN public.source_revisions r ON r.id=o.revision_id WHERE o.observation_id=(m->>'after_observation_id')::uuid
   AND o.document_id=i.document_id AND o.project_id=i.project_id AND o.profile=i.profile AND o.revision_id=rid
   AND locator='sha256:'||r.sha256||'#L'||(m#>>'{source_change,after,row,line_start}')) THEN RAISE EXCEPTION 'Local reappearance provenance integrity failure';END IF;
  IF EXISTS(SELECT FROM d2.task_sources WHERE task_id=i.task_id AND revision_id=rid AND source_locator=locator AND (document_id<>i.document_id OR project_id<>i.project_id)) THEN RAISE EXCEPTION 'Source link collision';END IF;
  INSERT INTO d2.task_sources VALUES(i.task_id,rid,locator,i.document_id,i.project_id) ON CONFLICT DO NOTHING;
  UPDATE d5.task_mapping_heads SET version=version+1,source_basis=m->'after_basis',projection=m->'after_projection' WHERE intent_id=i.intent_id;
  INSERT INTO public.audit_events(actor,entity_type,entity_id,action,payload) VALUES(session_user,'D5_TASK_IMPORT',i.task_id,m->>'action',
   jsonb_build_object('command_id',req->>'command_id','manifest_sha256',p.manifest_sha256,'package_sha256',pkg.package_sha256,'choice',m->>'choice','result_projection',m->'result_projection','source_projection',m->'after_projection','activation_allowed',false));
  effects=effects||jsonb_build_array(jsonb_build_object('intent_id',i.intent_id,'task_id',i.task_id,'action',m->>'action','absence_proof',m->'absence_proof','identity_declaration',m->>'identity_declaration','identity_reason',m->>'identity_reason','reason',m->>'reason','choice',m->>'choice','writes_task',m->>'action'='PATCH_LOCAL_REAPPEARANCE_USE_SOURCE','manifest_sha256',p.manifest_sha256,'result_projection',m->'result_projection','source_projection',m->'after_projection'));
 END LOOP;
 result=jsonb_build_object('status','OK','package_sha256',pkg.package_sha256,'effects',effects,'writes_d2',true,'activation_allowed',false);
 INSERT INTO d5.local_reappearance_applications(package_sha256,command_id,result) VALUES(pkg.package_sha256,(req->>'command_id')::uuid,result);
 RETURN d5.review_finish(req,result);
END $$;
CREATE FUNCTION d5.read_local_reappearance_proposal(pid uuid,doc uuid,proposal uuid) RETURNS jsonb LANGUAGE sql STABLE SECURITY DEFINER
 SET search_path=pg_catalog,pg_temp AS $$ SELECT jsonb_build_object('proposal_id',p.proposal_id,'manifest_sha256',p.manifest_sha256,'manifest',p.manifest,
 'review_version',h.version,'review_command_id',h.review_command_id) FROM d5.local_reappearance_proposals p JOIN d5.local_reappearance_review_heads h USING(proposal_id)
 WHERE p.proposal_id=proposal AND p.manifest#>>'{intent,project_id}'=pid::text AND p.manifest#>>'{intent,document_id}'=doc::text $$;
CREATE FUNCTION d5.read_local_reappearance_package(pid uuid,doc uuid,digest text) RETURNS jsonb LANGUAGE sql STABLE SECURITY DEFINER
 SET search_path=pg_catalog,pg_temp AS $$ SELECT to_jsonb(p) FROM d5.local_reappearance_packages p WHERE p.project_id=pid AND p.document_id=doc AND p.package_sha256=digest $$;
GRANT EXECUTE ON FUNCTION d5.prepare_local_reappearance_task(json),d5.package_local_reappearance_tasks(json) TO d5_writer;
GRANT EXECUTE ON FUNCTION d5.review_local_reappearance_task(json) TO d5_reviewer;
GRANT EXECUTE ON FUNCTION d5.apply_local_reappearance_tasks(json) TO d5_applier;
GRANT EXECUTE ON FUNCTION d5.read_local_reappearance_proposal(uuid,uuid,uuid),d5.read_local_reappearance_package(uuid,uuid,text) TO d5_writer,d5_reader,d5_reviewer,d5_applier;
RESET ROLE;
REVOKE CREATE ON SCHEMA d5 FROM d5_apply_owner;
COMMIT;
