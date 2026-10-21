-- SPDX-License-Identifier: GPL-3.0-only
-- I12: approved I11, fresh synthetic V30 + V31-V34 only. No promotion/activation.
BEGIN;
GRANT CREATE ON SCHEMA d5 TO d5_apply_owner;
SET LOCAL ROLE d5_apply_owner;
CREATE TABLE d5.reappearance_proposals(
 proposal_id uuid PRIMARY KEY REFERENCES d5.commands DEFERRABLE INITIALLY DEFERRED,
 manifest_sha256 d5.hash NOT NULL,manifest jsonb NOT NULL,
 CHECK(octet_length(manifest::text)<=4194304),
 CHECK(manifest_sha256=d5.task_hash('d5.reappearance-task-manifest.v1',manifest))
);
CREATE TABLE d5.reappearance_reviews(
 command_id uuid PRIMARY KEY REFERENCES d5.commands DEFERRABLE INITIALLY DEFERRED,
 proposal_id uuid NOT NULL REFERENCES d5.reappearance_proposals,version bigint NOT NULL CHECK(version>0),
 decision text NOT NULL CHECK(decision IN ('ACCEPT','REJECT')),reviewer_label text NOT NULL,reason text NOT NULL,
 UNIQUE(proposal_id,version)
);
CREATE TABLE d5.reappearance_review_heads(
 proposal_id uuid PRIMARY KEY REFERENCES d5.reappearance_proposals,version bigint NOT NULL DEFAULT 0,
 review_command_id uuid REFERENCES d5.reappearance_reviews
);
CREATE TABLE d5.reappearance_packages(
 package_sha256 d5.hash PRIMARY KEY,project_id uuid NOT NULL,document_id uuid NOT NULL,items jsonb NOT NULL,
 CHECK(package_sha256=d5.task_hash('d5.reappearance-task-package.v1',jsonb_build_object('project_id',project_id,'document_id',document_id,'items',items)))
);
CREATE TABLE d5.reappearance_applications(
 package_sha256 d5.hash PRIMARY KEY REFERENCES d5.reappearance_packages,
 command_id uuid NOT NULL UNIQUE REFERENCES d5.commands DEFERRABLE INITIALLY DEFERRED,
 result jsonb NOT NULL,applied_at timestamptz NOT NULL DEFAULT clock_timestamp()
);
DO $$ DECLARE rel text; BEGIN
 FOREACH rel IN ARRAY ARRAY['reappearance_proposals','reappearance_reviews','reappearance_packages','reappearance_applications'] LOOP
  EXECUTE format('CREATE TRIGGER immutable BEFORE UPDATE OR DELETE OR TRUNCATE ON d5.%I FOR EACH STATEMENT EXECUTE FUNCTION d5.immutable()',rel);
 END LOOP;
END $$;
-- Historical proof only: never dependent on today's review head/reference/task state.
CREATE FUNCTION d5.read_reappearance_absence(pid uuid,doc uuid,application uuid,proposal uuid) RETURNS jsonb
 LANGUAGE sql STABLE SECURITY DEFINER SET search_path=pg_catalog,pg_temp AS $$
 SELECT jsonb_build_object('schema','d5.reappearance-absence-proof.v1','application_command_id',a.command_id,
 'package_sha256',a.package_sha256,'absence_proposal_id',p.proposal_id,'absence_manifest_sha256',p.manifest_sha256,
 'absence_manifest',p.manifest,'application_request',c.request,'receipt',c.response,
 'mapping_version_after',d5.review_version(p.manifest->'mapping_version')+1,
 'absence_observation_id',p.manifest->>'after_observation_id')
 FROM d5.task_applications a JOIN d5.commands c ON c.command_id=a.command_id
 JOIN d5.task_packages pkg USING(package_sha256)
 JOIN d5.task_proposals p ON p.proposal_id=proposal
 JOIN d5.task_intents i ON i.intent_id=(p.manifest#>>'{intent,intent_id}')::uuid
 WHERE a.command_id=application AND pkg.project_id=pid AND pkg.document_id=doc
 AND i.project_id=pid AND i.document_id=doc AND to_jsonb(i)=p.manifest->'intent'
 AND p.manifest->>'action'='KEEP_EXISTING_NO_DELETE'
 AND p.manifest#>>'{source_change,change}'='ABSENT_IN_OBSERVATION'
 AND p.manifest#>'{source_change,before,row}' IS NOT NULL AND p.manifest#>'{source_change,before,row}'<>'null'::jsonb
 AND p.manifest#>'{source_change,after,row}'='null'::jsonb
 AND p.manifest#>>'{target,id}'=i.task_id::text AND p.manifest#>>'{target,project_id}'=pid::text
 AND c.request->>'action'='APPLY_TASK_PROPOSALS' AND c.request->>'project_id'=pid::text
 AND c.request->>'document_id'=doc::text AND c.request->>'package_sha256'=a.package_sha256
 AND c.response->>'status'='OK' AND a.result->>'status'='OK' AND c.response @> a.result
 AND a.result->>'package_sha256'=a.package_sha256
 AND a.result->'effects' @> jsonb_build_array(jsonb_build_object('task_id',i.task_id,'action','KEEP_EXISTING_NO_DELETE','manifest_sha256',p.manifest_sha256))
 AND EXISTS(SELECT FROM jsonb_array_elements(pkg.items) pin JOIN d5.task_proposal_reviews r
 ON r.command_id=(pin->>'review_command_id')::uuid AND r.proposal_id=p.proposal_id
 WHERE pin->>'proposal_id'=p.proposal_id::text AND pin->>'manifest_sha256'=p.manifest_sha256
 AND r.version=d5.review_version(pin->'review_version') AND r.decision='ACCEPT') $$;

CREATE FUNCTION d5.reappearance_target_guard(i d5.task_intents,projection jsonb) RETURNS text LANGUAGE plpgsql STABLE
 SET search_path=pg_catalog,pg_temp AS $$
DECLARE t jsonb=d5.task_target(i.task_id);
BEGIN
 IF t IS NULL OR NOT EXISTS(SELECT FROM d5.task_destinations WHERE intent_id=i.intent_id AND task_id=i.task_id AND project_id=i.project_id)
 OR t->>'project_id'<>i.project_id::text THEN RETURN 'TARGET_OWNERSHIP_CONFLICT';END IF;
 IF t->>'task_key' IS DISTINCT FROM i.task_key THEN RETURN 'TARGET_IDENTITY_CONFLICT';END IF;
 IF jsonb_build_object('title',t->'title','description',t->'description') IS DISTINCT FROM projection THEN RETURN 'LOCAL_EDIT_CONFLICT';END IF;
 IF t->>'status'<>'BACKLOG' OR EXISTS(SELECT FROM public.operations WHERE task_id=i.task_id)
 OR EXISTS(SELECT FROM public.schedule_entries WHERE task_id=i.task_id) THEN RETURN 'TARGET_HAS_WORK_OR_STATE';END IF;
 RETURN NULL;
END $$;
CREATE FUNCTION d5.prepare_reappearance_task(envelope json) RETURNS jsonb LANGUAGE plpgsql VOLATILE SECURITY DEFINER
 SET search_path=pg_catalog,pg_temp SET timezone='UTC' AS $$
DECLARE req jsonb;prior jsonb;i d5.task_intents;h d5.task_mapping_heads;r d5.comparison_reports;rh d5.row_review_heads;
 ref d5.reference_heads;proof jsonb;rv jsonb;m jsonb;t jsonb;code text;digest text;act text;
BEGIN
 req=d5.review_envelope(envelope,'PREPARE_REAPPEARANCE_TASK',ARRAY['intent_id','comparison_id','report_sha256','row_sha256','expected_reference_version','expected_mapping_version','absence_application_command_id','absence_proposal_id','identity_declaration','identity_reason'],ARRAY['expected_reference_version','expected_mapping_version']);
 PERFORM d5.review_version(req->'expected_reference_version');PERFORM d5.review_version(req->'expected_mapping_version');
 prior=d5.review_prior(req);IF prior IS NOT NULL THEN RETURN prior;END IF;
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
 code=d5.reappearance_target_guard(i,h.projection);IF code IS NOT NULL THEN RETURN d5.task_conflict(req,code);END IF;
 IF jsonb_typeof(rv#>'{after,row,fields,item}') IS DISTINCT FROM 'string'
 OR btrim(rv#>>'{after,row,fields,item}',U&'\0009\000A\000B\000C\000D\0020\0085\00A0\1680\2000\2001\2002\2003\2004\2005\2006\2007\2008\2009\200A\2028\2029\202F\205F\3000')=''
 OR jsonb_typeof(rv#>'{after,row,fields,objective}') IS DISTINCT FROM 'string' THEN RETURN d5.task_conflict(req,'INVALID_PROJECTION');END IF;
 t=d5.task_target(i.task_id);act=CASE WHEN h.projection=d5.task_projection(rv#>'{after,row}') THEN 'LINK_REAPPEARANCE_EVIDENCE' ELSE 'PATCH_REAPPEARED_BACKLOG' END;
 m=jsonb_build_object('schema','d5.reappearance-task-manifest.v1','mode','REAPPEARANCE','proposal_id',req->>'command_id',
 'intent',to_jsonb(i),'mapping_version',h.version,'last_applied_basis',h.source_basis,'last_applied_basis_sha256',h.source_basis_sha256,'before_projection',h.projection,
 'comparison_id',req->>'comparison_id','report_sha256',r.report_sha256,'row_sha256',req->>'row_sha256','source_change',rv,
 'before_observation_id',r.before_observation_id,'after_observation_id',r.after_observation_id,'after_revision_id',(SELECT revision_id FROM d5.observations WHERE observation_id=r.after_observation_id),
 'source_decision_command_id',rh.decision_command_id,'source_decision_version',rh.version,'reference_version',ref.version,'absence_proof',proof,
 'identity_declaration',req->>'identity_declaration','identity_reason',req->>'identity_reason','action',act,
 'after_projection',d5.task_projection(rv#>'{after,row}'),'after_basis',d5.task_semantic(rv#>'{after,row}'),'after_basis_sha256',d5.task_hash('d5.source-basis.v1',d5.task_semantic(rv#>'{after,row}')),
 'target_schema','d5.task-target.v1','target',t,'target_sha256',d5.task_hash('d5.task-target.v1',t),'prepared_at',clock_timestamp(),'activation_allowed',false);
 digest=d5.task_hash('d5.reappearance-task-manifest.v1',m);
 INSERT INTO d5.reappearance_proposals VALUES((req->>'command_id')::uuid,digest,m);
 INSERT INTO d5.reappearance_review_heads(proposal_id) VALUES((req->>'command_id')::uuid);
 RETURN d5.review_finish(req,jsonb_build_object('status','OK','proposal_id',req->>'command_id','manifest_sha256',digest,'manifest',m,'writes_d2',false));
END $$;

CREATE FUNCTION d5.review_reappearance_task(envelope json) RETURNS jsonb LANGUAGE plpgsql VOLATILE SECURITY DEFINER
 SET search_path=pg_catalog,pg_temp AS $$
DECLARE req jsonb;prior jsonb;p d5.reappearance_proposals;h d5.reappearance_review_heads;v bigint;
BEGIN
 req=d5.review_envelope(envelope,'REVIEW_REAPPEARANCE_TASK',ARRAY['proposal_id','manifest_sha256','expected_version','decision','reviewer_label','reason'],ARRAY['expected_version']);
 v=d5.review_version(req->'expected_version');
 IF req->>'decision' NOT IN ('ACCEPT','REJECT') OR length(req->>'reviewer_label') NOT BETWEEN 1 AND 256 OR length(req->>'reason') NOT BETWEEN 1 AND 1024
 OR req->>'reviewer_label' ~ '[[:cntrl:]]' OR req->>'reason' ~ '[[:cntrl:]]' THEN RAISE EXCEPTION 'Invalid review';END IF;
 prior=d5.review_prior(req);IF prior IS NOT NULL THEN RETURN prior;END IF;
 SELECT * INTO p FROM d5.reappearance_proposals WHERE proposal_id=(req->>'proposal_id')::uuid AND manifest_sha256=req->>'manifest_sha256'
 AND manifest#>>'{intent,project_id}'=req->>'project_id' AND manifest#>>'{intent,document_id}'=req->>'document_id';
 IF NOT FOUND THEN RETURN d5.task_conflict(req,'MANIFEST_SCOPE_CONFLICT');END IF;
 SELECT * INTO STRICT h FROM d5.reappearance_review_heads WHERE proposal_id=p.proposal_id FOR UPDATE;
 IF h.version<>v THEN RETURN d5.task_conflict(req,'REVIEW_VERSION_CONFLICT');END IF;
 INSERT INTO d5.reappearance_reviews VALUES((req->>'command_id')::uuid,p.proposal_id,v+1,req->>'decision',req->>'reviewer_label',req->>'reason');
 UPDATE d5.reappearance_review_heads SET version=v+1,review_command_id=(req->>'command_id')::uuid WHERE proposal_id=p.proposal_id;
 RETURN d5.review_finish(req,jsonb_build_object('status','OK','proposal_id',p.proposal_id,'version_at_commit',v+1,'writes_d2',false));
END $$;
CREATE FUNCTION d5.package_reappearance_tasks(envelope json) RETURNS jsonb LANGUAGE plpgsql VOLATILE SECURITY DEFINER
 SET search_path=pg_catalog,pg_temp AS $$
DECLARE req jsonb;prior jsonb;pin jsonb;p d5.reappearance_proposals;h d5.reappearance_review_heads;digest text;keys text[];
BEGIN
 req=d5.review_envelope(envelope,'PACKAGE_REAPPEARANCE_TASKS',ARRAY['items'],ARRAY['items']);
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
 SELECT * INTO p FROM d5.reappearance_proposals WHERE proposal_id=(pin->>'proposal_id')::uuid;
 IF NOT FOUND OR p.manifest_sha256<>pin->>'manifest_sha256' OR p.manifest#>>'{intent,project_id}'<>req->>'project_id' OR p.manifest#>>'{intent,document_id}'<>req->>'document_id' THEN RETURN d5.task_conflict(req,'MANIFEST_SCOPE_CONFLICT');END IF;
 SELECT * INTO STRICT h FROM d5.reappearance_review_heads WHERE proposal_id=p.proposal_id;
 IF h.version<>d5.review_version(pin->'review_version') OR h.review_command_id IS DISTINCT FROM (pin->>'review_command_id')::uuid
 OR NOT EXISTS(SELECT FROM d5.reappearance_reviews WHERE command_id=h.review_command_id AND decision='ACCEPT') THEN RETURN d5.task_conflict(req,'MANIFEST_NOT_ACCEPTED');END IF;
 END LOOP;
 IF EXISTS(SELECT FROM jsonb_array_elements(req->'items') x JOIN d5.reappearance_proposals tp ON tp.proposal_id=(x->>'proposal_id')::uuid GROUP BY tp.manifest#>>'{intent,intent_id}' HAVING count(*)>1) THEN RAISE EXCEPTION 'One proposal per intent required';END IF;
 digest=d5.task_hash('d5.reappearance-task-package.v1',jsonb_build_object('project_id',req->>'project_id','document_id',req->>'document_id','items',req->'items'));
 INSERT INTO d5.reappearance_packages VALUES(digest,(req->>'project_id')::uuid,(req->>'document_id')::uuid,req->'items') ON CONFLICT DO NOTHING;
 RETURN d5.review_finish(req,jsonb_build_object('status','OK','package_sha256',digest,'writes_d2',false));
END $$;

CREATE FUNCTION d5.validate_reappearance(p d5.reappearance_proposals,pin jsonb) RETURNS text LANGUAGE plpgsql VOLATILE
 SET search_path=pg_catalog,pg_temp AS $$
DECLARE m jsonb=p.manifest;i d5.task_intents;h d5.task_mapping_heads;rh d5.reappearance_review_heads;sr d5.row_review_heads;ref d5.reference_heads;code text;t jsonb;proof jsonb;
BEGIN
 SELECT * INTO STRICT i FROM d5.task_intents WHERE intent_id=(m#>>'{intent,intent_id}')::uuid FOR UPDATE;
 SELECT * INTO STRICT h FROM d5.task_mapping_heads WHERE intent_id=i.intent_id FOR UPDATE;
 IF to_jsonb(i) IS DISTINCT FROM m->'intent' OR h.version<>d5.review_version(m->'mapping_version') OR h.source_basis IS DISTINCT FROM m->'last_applied_basis'
 OR h.source_basis_sha256 IS DISTINCT FROM m->>'last_applied_basis_sha256' OR h.projection IS DISTINCT FROM m->'before_projection' THEN RETURN 'MAPPING_VERSION_CONFLICT';END IF;
 proof=d5.read_reappearance_absence(i.project_id,i.document_id,(m#>>'{absence_proof,application_command_id}')::uuid,(m#>>'{absence_proof,absence_proposal_id}')::uuid);
 IF proof IS DISTINCT FROM m->'absence_proof' OR d5.review_version(proof->'mapping_version_after')<>h.version THEN RETURN 'ABSENCE_VERSION_CONFLICT';END IF;
 SELECT * INTO STRICT rh FROM d5.reappearance_review_heads WHERE proposal_id=p.proposal_id;
 IF rh.version<>d5.review_version(pin->'review_version') OR rh.review_command_id IS DISTINCT FROM (pin->>'review_command_id')::uuid
 OR NOT EXISTS(SELECT FROM d5.reappearance_reviews WHERE command_id=rh.review_command_id AND decision='ACCEPT') THEN RETURN 'REAPPEARANCE_REVIEW_CONFLICT';END IF;
 SELECT * INTO STRICT sr FROM d5.row_review_heads WHERE comparison_id=(m->>'comparison_id')::uuid AND source_key=i.source_key;
 IF sr.version<>d5.review_version(m->'source_decision_version') OR sr.decision_command_id IS DISTINCT FROM (m->>'source_decision_command_id')::uuid
 OR NOT EXISTS(SELECT FROM d5.row_decisions WHERE command_id=sr.decision_command_id AND decision='ACCEPT') THEN RETURN 'SOURCE_REVIEW_CONFLICT';END IF;
 SELECT * INTO STRICT ref FROM d5.reference_heads WHERE document_id=i.document_id AND profile=i.profile;
 IF ref.version<>d5.review_version(m->'reference_version') OR ref.observation_id IS DISTINCT FROM (m->>'before_observation_id')::uuid THEN RETURN 'REFERENCE_VERSION_CONFLICT';END IF;
 code=d5.reappearance_target_guard(i,h.projection);IF code IS NOT NULL THEN RETURN code;END IF;
 t=d5.task_target(i.task_id);
 IF t IS DISTINCT FROM m->'target' OR d5.task_hash('d5.task-target.v1',t) IS DISTINCT FROM m->>'target_sha256' THEN RETURN 'TARGET_CAS_CONFLICT';END IF;
 RETURN NULL;
END $$;
CREATE FUNCTION d5.apply_reappearance_tasks(envelope json) RETURNS jsonb LANGUAGE plpgsql VOLATILE SECURITY DEFINER
 SET search_path=pg_catalog,pg_temp SET timezone='UTC' AS $$
DECLARE req jsonb;prior jsonb;pkg d5.reappearance_packages;pin jsonb;p d5.reappearance_proposals;m jsonb;i d5.task_intents;code text;effects jsonb='[]'::jsonb;result jsonb;original d5.reappearance_applications;rid uuid;locator text;
BEGIN
 req=d5.review_envelope(envelope,'APPLY_REAPPEARANCE_TASKS',ARRAY['package_sha256']);
 PERFORM d5.task_lock_boundary();prior=d5.review_prior(req);IF prior IS NOT NULL THEN RETURN prior;END IF;
 SELECT * INTO pkg FROM d5.reappearance_packages WHERE package_sha256=req->>'package_sha256' AND project_id=(req->>'project_id')::uuid AND document_id=(req->>'document_id')::uuid;
 IF NOT FOUND THEN RETURN d5.task_conflict(req,'REAPPEARANCE_PACKAGE_SCOPE_CONFLICT');END IF;
 SELECT * INTO original FROM d5.reappearance_applications WHERE package_sha256=pkg.package_sha256;
 IF FOUND THEN RETURN d5.review_finish(req,jsonb_build_object('status','ALREADY_APPLIED','original_command_id',original.command_id,'package_sha256',pkg.package_sha256,'writes_d2',false));END IF;
 FOR pin IN SELECT x FROM jsonb_array_elements(pkg.items) x JOIN d5.reappearance_proposals rp ON rp.proposal_id=(x->>'proposal_id')::uuid ORDER BY rp.manifest#>>'{intent,intent_id}' LOOP
  SELECT * INTO STRICT p FROM d5.reappearance_proposals WHERE proposal_id=(pin->>'proposal_id')::uuid;
  IF p.manifest_sha256 IS DISTINCT FROM pin->>'manifest_sha256' OR p.manifest_sha256 IS DISTINCT FROM d5.task_hash('d5.reappearance-task-manifest.v1',p.manifest) THEN RAISE EXCEPTION 'Reappearance manifest integrity failure';END IF;
  code=d5.validate_reappearance(p,pin);IF code IS NOT NULL THEN RETURN d5.task_conflict(req,code);END IF;
 END LOOP;
 FOR pin IN SELECT * FROM jsonb_array_elements(pkg.items) LOOP
  SELECT * INTO STRICT p FROM d5.reappearance_proposals WHERE proposal_id=(pin->>'proposal_id')::uuid;m=p.manifest;
  SELECT * INTO STRICT i FROM d5.task_intents WHERE intent_id=(m#>>'{intent,intent_id}')::uuid;
  IF m->>'action'='PATCH_REAPPEARED_BACKLOG' THEN
   UPDATE public.tasks SET title=m#>>'{after_projection,title}',description=m#>>'{after_projection,description}',row_version=row_version+1 WHERE id=i.task_id;
  END IF;
  rid=(m->>'after_revision_id')::uuid;locator=m#>>'{source_change,after,row,source_locator}';
  IF NOT EXISTS(SELECT FROM d5.observations o JOIN public.source_revisions r ON r.id=o.revision_id WHERE o.observation_id=(m->>'after_observation_id')::uuid
   AND o.document_id=i.document_id AND o.project_id=i.project_id AND o.profile=i.profile AND o.revision_id=rid
   AND locator='sha256:'||r.sha256||'#L'||(m#>>'{source_change,after,row,line_start}')) THEN RAISE EXCEPTION 'Reappearance provenance integrity failure';END IF;
  IF EXISTS(SELECT FROM d2.task_sources WHERE task_id=i.task_id AND revision_id=rid AND source_locator=locator AND (document_id<>i.document_id OR project_id<>i.project_id)) THEN RAISE EXCEPTION 'Source link collision';END IF;
  INSERT INTO d2.task_sources VALUES(i.task_id,rid,locator,i.document_id,i.project_id) ON CONFLICT DO NOTHING;
  UPDATE d5.task_mapping_heads SET version=version+1,source_basis=m->'after_basis',projection=m->'after_projection' WHERE intent_id=i.intent_id;
  INSERT INTO public.audit_events(actor,entity_type,entity_id,action,payload) VALUES(session_user,'D5_TASK_IMPORT',i.task_id,m->>'action',
   jsonb_build_object('command_id',req->>'command_id','manifest_sha256',p.manifest_sha256,'package_sha256',pkg.package_sha256,'activation_allowed',false));
  effects=effects||jsonb_build_array(jsonb_build_object('intent_id',i.intent_id,'task_id',i.task_id,'action',m->>'action','manifest_sha256',p.manifest_sha256));
 END LOOP;
 result=jsonb_build_object('status','OK','package_sha256',pkg.package_sha256,'effects',effects,'writes_d2',true,'activation_allowed',false);
 INSERT INTO d5.reappearance_applications(package_sha256,command_id,result) VALUES(pkg.package_sha256,(req->>'command_id')::uuid,result);
 RETURN d5.review_finish(req,result);
END $$;
CREATE FUNCTION d5.read_reappearance_proposal(pid uuid,doc uuid,proposal uuid) RETURNS jsonb LANGUAGE sql STABLE SECURITY DEFINER
 SET search_path=pg_catalog,pg_temp AS $$ SELECT jsonb_build_object('proposal_id',p.proposal_id,'manifest_sha256',p.manifest_sha256,'manifest',p.manifest,
 'review_version',h.version,'review_command_id',h.review_command_id) FROM d5.reappearance_proposals p JOIN d5.reappearance_review_heads h USING(proposal_id)
 WHERE p.proposal_id=proposal AND p.manifest#>>'{intent,project_id}'=pid::text AND p.manifest#>>'{intent,document_id}'=doc::text $$;
CREATE FUNCTION d5.read_reappearance_package(pid uuid,doc uuid,digest text) RETURNS jsonb LANGUAGE sql STABLE SECURITY DEFINER
 SET search_path=pg_catalog,pg_temp AS $$ SELECT to_jsonb(p) FROM d5.reappearance_packages p WHERE p.project_id=pid AND p.document_id=doc AND p.package_sha256=digest $$;
GRANT EXECUTE ON FUNCTION d5.prepare_reappearance_task(json),d5.package_reappearance_tasks(json) TO d5_writer;
GRANT EXECUTE ON FUNCTION d5.review_reappearance_task(json) TO d5_reviewer;
GRANT EXECUTE ON FUNCTION d5.apply_reappearance_tasks(json) TO d5_applier;
GRANT EXECUTE ON FUNCTION d5.read_reappearance_proposal(uuid,uuid,uuid),d5.read_reappearance_package(uuid,uuid,text),d5.read_reappearance_absence(uuid,uuid,uuid,uuid) TO d5_writer,d5_reader,d5_reviewer,d5_applier;
RESET ROLE;
REVOKE CREATE ON SCHEMA d5 FROM d5_apply_owner;
COMMIT;
