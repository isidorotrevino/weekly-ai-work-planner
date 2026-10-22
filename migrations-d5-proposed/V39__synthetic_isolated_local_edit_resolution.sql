-- SPDX-License-Identifier: GPL-3.0-only
-- I20: approved I19, fresh synthetic V30 + V31-V38 only. No promotion/activation.
BEGIN;
GRANT CREATE ON SCHEMA d5 TO d5_apply_owner;
SET LOCAL ROLE d5_apply_owner;
CREATE TABLE d5.isolated_local_edit_proposals(
 proposal_id uuid PRIMARY KEY REFERENCES d5.commands DEFERRABLE INITIALLY DEFERRED,
 manifest_sha256 d5.hash NOT NULL,manifest jsonb NOT NULL,
 CHECK(octet_length(manifest::text)<=4194304),
 CHECK(manifest_sha256=d5.task_hash('d5.isolated-local-edit-task-manifest.v1',manifest))
);
CREATE TABLE d5.isolated_local_edit_reviews(
 command_id uuid PRIMARY KEY REFERENCES d5.commands DEFERRABLE INITIALLY DEFERRED,
 proposal_id uuid NOT NULL REFERENCES d5.isolated_local_edit_proposals,version bigint NOT NULL CHECK(version>0),
 decision text NOT NULL CHECK(decision IN ('ACCEPT','REJECT')),reviewer_label text NOT NULL,reason text NOT NULL,
 UNIQUE(proposal_id,version)
);
CREATE TABLE d5.isolated_local_edit_review_heads(
 proposal_id uuid PRIMARY KEY REFERENCES d5.isolated_local_edit_proposals,version bigint NOT NULL DEFAULT 0,
 review_command_id uuid REFERENCES d5.isolated_local_edit_reviews
);
CREATE TABLE d5.isolated_local_edit_packages(
 package_sha256 d5.hash PRIMARY KEY,project_id uuid NOT NULL,document_id uuid NOT NULL,items jsonb NOT NULL,
 CHECK(package_sha256=d5.task_hash('d5.isolated-local-edit-task-package.v1',jsonb_build_object('project_id',project_id,'document_id',document_id,'items',items)))
);
CREATE TABLE d5.isolated_local_edit_applications(
 package_sha256 d5.hash PRIMARY KEY REFERENCES d5.isolated_local_edit_packages,
 command_id uuid NOT NULL UNIQUE REFERENCES d5.commands DEFERRABLE INITIALLY DEFERRED,
 result jsonb NOT NULL,applied_at timestamptz NOT NULL DEFAULT clock_timestamp()
);
DO $$ DECLARE rel text; BEGIN
 FOREACH rel IN ARRAY ARRAY['isolated_local_edit_proposals','isolated_local_edit_reviews','isolated_local_edit_packages','isolated_local_edit_applications'] LOOP
  EXECUTE format('CREATE TRIGGER immutable BEFORE UPDATE OR DELETE OR TRUNCATE ON d5.%I FOR EACH STATEMENT EXECUTE FUNCTION d5.immutable()',rel);
 END LOOP;
END $$;
-- Fixed catalog, historical facts only. No caller-supplied SQL identifiers or date ordering.
CREATE FUNCTION d5.read_isolated_local_head_proof(pid uuid,doc uuid,iid uuid,application uuid,proposal uuid) RETURNS jsonb
 LANGUAGE plpgsql STABLE SECURITY DEFINER SET search_path=pg_catalog,pg_temp AS $$
DECLARE kind text;prefix text;reviews text;entry text;domain text;package_domain text;allowed text[];
 x record;m jsonb;i d5.task_intents;rowval jsonb;present boolean;v bigint;pin jsonb;effect jsonb;
BEGIN
 SELECT * INTO i FROM d5.task_intents WHERE intent_id=iid AND project_id=pid AND document_id=doc;
 IF NOT FOUND THEN RETURN NULL;END IF;
 FOREACH kind IN ARRAY ARRAY['task','bootstrap','reappearance','local_edit','adoption','local_reappearance','isolated_local_edit'] LOOP
  prefix=kind;reviews=kind||'_reviews';domain='d5.'||replace(kind,'_','-')||'-task-manifest.v1';
  package_domain='d5.'||replace(kind,'_','-')||'-task-package.v1';
  CASE kind
   WHEN 'task' THEN reviews='task_proposal_reviews';entry='APPLY_TASK_PROPOSALS';domain='d5.task-manifest.v1';package_domain='d5.task-package.v1';allowed=ARRAY['CREATE_BACKLOG','PATCH_BACKLOG','LINK_SOURCE_EVIDENCE','KEEP_EXISTING_NO_DELETE'];
   WHEN 'bootstrap' THEN entry='APPLY_BOOTSTRAP_TASKS';allowed=ARRAY['CREATE_INITIAL_BACKLOG'];
   WHEN 'reappearance' THEN entry='APPLY_REAPPEARANCE_TASKS';allowed=ARRAY['PATCH_REAPPEARED_BACKLOG','LINK_REAPPEARANCE_EVIDENCE'];
   WHEN 'local_edit' THEN entry='APPLY_LOCAL_EDIT_TASKS';allowed=ARRAY['PATCH_LOCAL_USE_SOURCE','LINK_LOCAL_RESOLUTION_EVIDENCE','KEEP_LOCAL_BACKLOG'];
   WHEN 'adoption' THEN entry='APPLY_ADOPTION_TASKS';allowed=ARRAY['LINK_EXISTING_BACKLOG'];
   WHEN 'local_reappearance' THEN entry='APPLY_LOCAL_REAPPEARANCE_TASKS';allowed=ARRAY['PATCH_LOCAL_REAPPEARANCE_USE_SOURCE','LINK_LOCAL_REAPPEARANCE_EVIDENCE','KEEP_LOCAL_REAPPEARANCE'];
   WHEN 'isolated_local_edit' THEN entry='APPLY_ISOLATED_LOCAL_EDIT_TASKS';allowed=ARRAY['PATCH_ISOLATED_LOCAL_USE_SOURCE','KEEP_ISOLATED_LOCAL'];
  END CASE;
  EXECUTE format('SELECT p.manifest,p.manifest_sha256,a.package_sha256,a.result,c.request,c.response,pc.response prepared_receipt,k.items,k.project_id,k.document_id
   FROM d5.%I a JOIN d5.commands c ON c.command_id=a.command_id JOIN d5.%I k USING(package_sha256)
   JOIN d5.%I p ON p.proposal_id=$2 JOIN d5.commands pc ON pc.command_id=p.proposal_id WHERE a.command_id=$1',prefix||'_applications',prefix||'_packages',prefix||'_proposals')
   INTO x USING application,proposal;
  IF x.manifest IS NULL THEN CONTINUE;END IF;
  m=x.manifest;
  IF x.project_id<>pid OR x.document_id<>doc OR m->'intent' IS DISTINCT FROM to_jsonb(i)
   OR NOT coalesce(m->>'action'=ANY(allowed),false) OR x.manifest_sha256 IS DISTINCT FROM d5.task_hash(domain,m)
   OR x.package_sha256 IS DISTINCT FROM d5.task_hash(package_domain,jsonb_build_object('project_id',pid,'document_id',doc,'items',x.items))
   OR x.request->>'action' IS DISTINCT FROM entry OR x.request->>'project_id' IS DISTINCT FROM pid::text
   OR x.request->>'document_id' IS DISTINCT FROM doc::text OR x.request->>'package_sha256' IS DISTINCT FROM x.package_sha256
   OR x.result->>'status' IS DISTINCT FROM 'OK' OR x.response->>'status' IS DISTINCT FROM 'OK' OR NOT(x.response @> x.result)
   OR x.result->>'package_sha256' IS DISTINCT FROM x.package_sha256
   OR x.prepared_receipt->>'status' IS DISTINCT FROM 'OK' OR x.prepared_receipt->>'proposal_id' IS DISTINCT FROM proposal::text
   OR x.prepared_receipt->>'manifest_sha256' IS DISTINCT FROM x.manifest_sha256 THEN RETURN NULL;END IF;
  SELECT q INTO pin FROM jsonb_array_elements(x.items) q WHERE q->>'proposal_id'=proposal::text AND q->>'manifest_sha256'=x.manifest_sha256;
  IF pin IS NULL THEN RETURN NULL;END IF;
  EXECUTE format('SELECT EXISTS(SELECT FROM d5.%I WHERE command_id=$1 AND proposal_id=$2 AND version=$3 AND decision=''ACCEPT'')',reviews)
   INTO present USING (pin->>'review_command_id')::uuid,proposal,d5.review_version(pin->'review_version');
  IF NOT present THEN RETURN NULL;END IF;
  SELECT e INTO effect FROM jsonb_array_elements(x.result->'effects') e WHERE e->>'task_id'=i.task_id::text
   AND e->>'manifest_sha256'=x.manifest_sha256 AND e->>'action'=m->>'action';
  IF effect IS NULL THEN RETURN NULL;END IF;
  v=CASE WHEN kind='adoption' THEN 1 ELSE d5.review_version(m->'mapping_version')+1 END;
  rowval=CASE WHEN kind IN ('bootstrap','adoption','isolated_local_edit') THEN m->'snapshot_row' ELSE m#>'{source_change,after,row}' END;
  present=rowval IS NOT NULL AND rowval<>'null'::jsonb;
  IF present AND (d5.task_semantic(rowval) IS DISTINCT FROM CASE WHEN kind IN ('bootstrap','adoption') THEN m->'source_basis' ELSE m->'after_basis' END
   OR d5.task_projection(rowval) IS DISTINCT FROM CASE WHEN kind IN ('bootstrap','adoption') THEN m->'projection' ELSE m->'after_projection' END) THEN RETURN NULL;END IF;
  IF NOT present AND (kind<>'task' OR m->>'action'<>'KEEP_EXISTING_NO_DELETE' OR m#>>'{source_change,change}'<>'ABSENT_IN_OBSERVATION') THEN RETURN NULL;END IF;
  RETURN jsonb_build_object('schema','d5.isolated-local-head-proof.v1','kind',kind,'application_command_id',application,'proposal_id',proposal,
   'manifest_sha256',x.manifest_sha256,'manifest',m,'package_sha256',x.package_sha256,'review_pin',pin,'application_request',x.request,
   'receipt',x.response,'effect',effect,'mapping_version_after',v,'source_present',present,
   'source_basis',d5.task_semantic(rowval),'projection',d5.task_projection(rowval));
 END LOOP;
 RETURN NULL;
END $$;
CREATE FUNCTION d5.prepare_isolated_local_edit_task(envelope json,rowbytes bytea) RETURNS jsonb LANGUAGE plpgsql VOLATILE SECURITY DEFINER
 SET search_path=pg_catalog,pg_temp SET timezone='UTC' AS $$
DECLARE req jsonb;prior jsonb;i d5.task_intents;h d5.task_mapping_heads;o d5.observations;ref d5.reference_heads;
 v jsonb;rv jsonb;m jsonb;proof jsonb;t jsonb;l jsonb;sp jsonb;chosen jsonb;code text;digest text;ch text;act text;
BEGIN
 req=d5.review_envelope(envelope,'PREPARE_ISOLATED_LOCAL_EDIT_TASK',ARRAY['intent_id','source_key','observation_id','content_sha256','preview_sha256','snapshot_row_sha256','expected_reference_version','expected_mapping_version','head_application_command_id','head_proposal_id','choice','reason'],ARRAY['expected_reference_version','expected_mapping_version']);
 PERFORM d5.review_version(req->'expected_reference_version');PERFORM d5.review_version(req->'expected_mapping_version');
 IF rowbytes IS NULL OR octet_length(rowbytes)>2097152 OR encode(public.digest(rowbytes,'sha256'),'hex') IS DISTINCT FROM req->>'snapshot_row_sha256' THEN RAISE EXCEPTION 'Invalid isolated row bytes/hash';END IF;
 rv=convert_from(rowbytes,'UTF8')::jsonb;
 prior=d5.review_prior(req);IF prior IS NOT NULL THEN RETURN prior;END IF;
 IF req->>'choice' NOT IN ('USE_SOURCE','KEEP_LOCAL') OR length(req->>'reason') NOT BETWEEN 1 AND 1024
 OR btrim(req->>'reason',U&'\0009\000A\000B\000C\000D\0020\0085\00A0\1680\2000\2001\2002\2003\2004\2005\2006\2007\2008\2009\200A\2028\2029\202F\205F\3000')='' OR req->>'reason' ~ '[[:cntrl:]]' THEN RETURN d5.task_conflict(req,'RESOLUTION_CHOICE_REQUIRED');END IF;
 SELECT * INTO i FROM d5.task_intents WHERE intent_id=(req->>'intent_id')::uuid AND project_id=(req->>'project_id')::uuid AND document_id=(req->>'document_id')::uuid AND source_key=req->>'source_key';
 IF NOT FOUND THEN RETURN d5.task_conflict(req,'INTENT_SCOPE_CONFLICT');END IF;
 SELECT * INTO STRICT h FROM d5.task_mapping_heads WHERE intent_id=i.intent_id;
 IF h.version<>d5.review_version(req->'expected_mapping_version') OR h.source_basis IS NULL OR h.projection IS NULL THEN RETURN d5.task_conflict(req,'MAPPING_VERSION_CONFLICT');END IF;
 proof=d5.read_isolated_local_head_proof(i.project_id,i.document_id,i.intent_id,(req->>'head_application_command_id')::uuid,(req->>'head_proposal_id')::uuid);
 IF proof IS NULL THEN RETURN d5.task_conflict(req,'CONFIRMED_HEAD_REQUIRED');END IF;
 IF d5.review_version(proof->'mapping_version_after')<>h.version THEN RETURN d5.task_conflict(req,'HEAD_PROOF_VERSION_CONFLICT');END IF;
 IF proof->'source_present' IS DISTINCT FROM 'true'::jsonb THEN RETURN d5.task_conflict(req,'APPLIED_ABSENCE_BLOCKED');END IF;
 IF proof->'source_basis' IS DISTINCT FROM h.source_basis OR proof->'projection' IS DISTINCT FROM h.projection THEN RETURN d5.task_conflict(req,'HEAD_PROOF_CONTENT_CONFLICT');END IF;
 SELECT * INTO o FROM d5.observations WHERE observation_id=(req->>'observation_id')::uuid AND document_id=i.document_id AND project_id=i.project_id AND profile=i.profile;
 IF NOT FOUND OR o.preview_sha256 IS DISTINCT FROM req->>'preview_sha256' THEN RETURN d5.task_conflict(req,'OBSERVATION_SCOPE_CONFLICT');END IF;
 SELECT sha256 INTO STRICT ch FROM public.source_revisions WHERE id=o.revision_id AND document_id=o.document_id;
 IF ch IS DISTINCT FROM req->>'content_sha256' THEN RETURN d5.task_conflict(req,'SOURCE_HASH_CONFLICT');END IF;
 SELECT convert_from(preview_bytes,'UTF8')::jsonb INTO STRICT v FROM d5.preview_artifacts WHERE preview_sha256=o.preview_sha256;
 IF EXISTS(SELECT FROM jsonb_array_elements(v->'diagnostics') d WHERE d->'blocking'='true'::jsonb) THEN RETURN d5.task_conflict(req,'OBSERVATION_BLOCKED');END IF;
 IF (SELECT count(*) FROM jsonb_array_elements(v->'proposals') r WHERE r->>'source_key'=i.source_key)<>1 THEN RETURN d5.task_conflict(req,'SOURCE_ROW_NOT_UNIQUE');END IF;
 IF NOT EXISTS(SELECT FROM jsonb_array_elements(v->'proposals') r WHERE r->>'source_key'=i.source_key AND r=rv) THEN RETURN d5.task_conflict(req,'SNAPSHOT_ROW_CONFLICT');END IF;
 IF NOT d5.local_edit_valid_projection(d5.task_projection(rv),false) THEN RETURN d5.task_conflict(req,'INVALID_PROJECTION');END IF;
 IF d5.task_semantic(rv) IS DISTINCT FROM h.source_basis OR d5.task_projection(rv) IS DISTINCT FROM h.projection THEN RETURN d5.task_conflict(req,'SOURCE_BASE_CONFLICT');END IF;
 SELECT * INTO STRICT ref FROM d5.reference_heads WHERE document_id=i.document_id AND profile=i.profile;
 IF ref.observation_id IS DISTINCT FROM o.observation_id OR ref.version<>d5.review_version(req->'expected_reference_version') THEN RETURN d5.task_conflict(req,'REFERENCE_VERSION_CONFLICT');END IF;
 code=d5.local_edit_target_guard(i,h.projection);IF code IS NOT NULL THEN RETURN d5.task_conflict(req,code);END IF;
 IF rv->>'source_locator' IS DISTINCT FROM 'sha256:'||ch||'#L'||(rv->>'line_start') THEN RAISE EXCEPTION 'Invalid isolated locator';END IF;
 t=d5.task_target(i.task_id);l=jsonb_build_object('title',t->'title','description',t->'description');sp=d5.task_projection(rv);
 IF NOT d5.local_edit_valid_projection(l,true) THEN RETURN d5.task_conflict(req,'INVALID_PROJECTION');END IF;
 chosen=CASE WHEN req->>'choice'='USE_SOURCE' THEN sp ELSE l END;
 act=CASE WHEN req->>'choice'='KEEP_LOCAL' THEN 'KEEP_ISOLATED_LOCAL' ELSE 'PATCH_ISOLATED_LOCAL_USE_SOURCE' END;
 m=jsonb_build_object('schema','d5.isolated-local-edit-task-manifest.v1','mode','ISOLATED_LOCAL_EDIT','proposal_id',req->>'command_id',
 'intent',to_jsonb(i),'mapping_version',h.version,'last_applied_basis',h.source_basis,'last_applied_basis_sha256',h.source_basis_sha256,'before_projection',h.projection,
 'head_proof',proof,'observation_id',o.observation_id,'revision_id',o.revision_id,'content_sha256',ch,'preview_sha256',o.preview_sha256,'snapshot_row',rv,'snapshot_row_sha256',req->>'snapshot_row_sha256',
 'reference_version',ref.version,'choice',req->>'choice','reason',req->>'reason','action',act,'local_projection',l,'result_projection',chosen,
 'task_fields_to_write',CASE WHEN act='PATCH_ISOLATED_LOCAL_USE_SOURCE' THEN to_jsonb(ARRAY['title','description','row_version']) ELSE '[]'::jsonb END,
 'before_projection_sha256',d5.task_hash('d5.isolated-local-edit-projection.v1',h.projection),'local_projection_sha256',d5.task_hash('d5.isolated-local-edit-projection.v1',l),
 'after_projection_sha256',d5.task_hash('d5.isolated-local-edit-projection.v1',sp),'result_projection_sha256',d5.task_hash('d5.isolated-local-edit-projection.v1',chosen),
 'after_projection',sp,'after_basis',h.source_basis,'after_basis_sha256',h.source_basis_sha256,
 'target_schema','d5.task-target.v1','target',t,'target_sha256',d5.task_hash('d5.task-target.v1',t),'prepared_at',clock_timestamp(),'activation_allowed',false);
 digest=d5.task_hash('d5.isolated-local-edit-task-manifest.v1',m);
 INSERT INTO d5.isolated_local_edit_proposals VALUES((req->>'command_id')::uuid,digest,m);
 INSERT INTO d5.isolated_local_edit_review_heads(proposal_id) VALUES((req->>'command_id')::uuid);
 RETURN d5.review_finish(req,jsonb_build_object('status','OK','proposal_id',req->>'command_id','manifest_sha256',digest,'manifest',m,'writes_d2',false));
END $$;

CREATE FUNCTION d5.review_isolated_local_edit_task(envelope json) RETURNS jsonb LANGUAGE plpgsql VOLATILE SECURITY DEFINER
 SET search_path=pg_catalog,pg_temp AS $$
DECLARE req jsonb;prior jsonb;p d5.isolated_local_edit_proposals;h d5.isolated_local_edit_review_heads;v bigint;
BEGIN
 req=d5.review_envelope(envelope,'REVIEW_ISOLATED_LOCAL_EDIT_TASK',ARRAY['proposal_id','manifest_sha256','expected_version','decision','reviewer_label','reason'],ARRAY['expected_version']);
 v=d5.review_version(req->'expected_version');
 IF req->>'decision' NOT IN ('ACCEPT','REJECT') OR length(req->>'reviewer_label') NOT BETWEEN 1 AND 256 OR length(req->>'reason') NOT BETWEEN 1 AND 1024
 OR req->>'reviewer_label' ~ '[[:cntrl:]]' OR req->>'reason' ~ '[[:cntrl:]]' THEN RAISE EXCEPTION 'Invalid review';END IF;
 prior=d5.review_prior(req);IF prior IS NOT NULL THEN RETURN prior;END IF;
 SELECT * INTO p FROM d5.isolated_local_edit_proposals WHERE proposal_id=(req->>'proposal_id')::uuid AND manifest_sha256=req->>'manifest_sha256'
 AND manifest#>>'{intent,project_id}'=req->>'project_id' AND manifest#>>'{intent,document_id}'=req->>'document_id';
 IF NOT FOUND THEN RETURN d5.task_conflict(req,'MANIFEST_SCOPE_CONFLICT');END IF;
 SELECT * INTO STRICT h FROM d5.isolated_local_edit_review_heads WHERE proposal_id=p.proposal_id FOR UPDATE;
 IF h.version<>v THEN RETURN d5.task_conflict(req,'REVIEW_VERSION_CONFLICT');END IF;
 INSERT INTO d5.isolated_local_edit_reviews VALUES((req->>'command_id')::uuid,p.proposal_id,v+1,req->>'decision',req->>'reviewer_label',req->>'reason');
 UPDATE d5.isolated_local_edit_review_heads SET version=v+1,review_command_id=(req->>'command_id')::uuid WHERE proposal_id=p.proposal_id;
 RETURN d5.review_finish(req,jsonb_build_object('status','OK','proposal_id',p.proposal_id,'version_at_commit',v+1,'writes_d2',false));
END $$;
CREATE FUNCTION d5.package_isolated_local_edit_tasks(envelope json) RETURNS jsonb LANGUAGE plpgsql VOLATILE SECURITY DEFINER
 SET search_path=pg_catalog,pg_temp AS $$
DECLARE req jsonb;prior jsonb;pin jsonb;p d5.isolated_local_edit_proposals;h d5.isolated_local_edit_review_heads;digest text;keys text[];
BEGIN
 req=d5.review_envelope(envelope,'PACKAGE_ISOLATED_LOCAL_EDIT_TASKS',ARRAY['items'],ARRAY['items']);
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
 SELECT * INTO p FROM d5.isolated_local_edit_proposals WHERE proposal_id=(pin->>'proposal_id')::uuid;
 IF NOT FOUND OR p.manifest_sha256<>pin->>'manifest_sha256' OR p.manifest#>>'{intent,project_id}'<>req->>'project_id' OR p.manifest#>>'{intent,document_id}'<>req->>'document_id' THEN RETURN d5.task_conflict(req,'MANIFEST_SCOPE_CONFLICT');END IF;
 SELECT * INTO STRICT h FROM d5.isolated_local_edit_review_heads WHERE proposal_id=p.proposal_id;
 IF h.version<>d5.review_version(pin->'review_version') OR h.review_command_id IS DISTINCT FROM (pin->>'review_command_id')::uuid
 OR NOT EXISTS(SELECT FROM d5.isolated_local_edit_reviews WHERE command_id=h.review_command_id AND decision='ACCEPT') THEN RETURN d5.task_conflict(req,'MANIFEST_NOT_ACCEPTED');END IF;
 END LOOP;
 IF EXISTS(SELECT FROM jsonb_array_elements(req->'items') x JOIN d5.isolated_local_edit_proposals tp ON tp.proposal_id=(x->>'proposal_id')::uuid GROUP BY tp.manifest#>>'{intent,intent_id}' HAVING count(*)>1) OR (SELECT count(DISTINCT (tp.manifest->>'observation_id',tp.manifest#>>'{intent,profile}')) FROM jsonb_array_elements(req->'items') x JOIN d5.isolated_local_edit_proposals tp ON tp.proposal_id=(x->>'proposal_id')::uuid)<>1 THEN RAISE EXCEPTION 'One proposal per intent required';END IF;
 digest=d5.task_hash('d5.isolated-local-edit-task-package.v1',jsonb_build_object('project_id',req->>'project_id','document_id',req->>'document_id','items',req->'items'));
 INSERT INTO d5.isolated_local_edit_packages VALUES(digest,(req->>'project_id')::uuid,(req->>'document_id')::uuid,req->'items') ON CONFLICT DO NOTHING;
 RETURN d5.review_finish(req,jsonb_build_object('status','OK','package_sha256',digest,'writes_d2',false));
END $$;

CREATE FUNCTION d5.validate_isolated_local_edit(p d5.isolated_local_edit_proposals,pin jsonb) RETURNS text LANGUAGE plpgsql VOLATILE
 SET search_path=pg_catalog,pg_temp AS $$
DECLARE m jsonb=p.manifest;i d5.task_intents;h d5.task_mapping_heads;rh d5.isolated_local_edit_review_heads;ref d5.reference_heads;
 code text;t jsonb;l jsonb;chosen jsonb;act text;proof jsonb;
BEGIN
 SELECT * INTO STRICT i FROM d5.task_intents WHERE intent_id=(m#>>'{intent,intent_id}')::uuid FOR UPDATE;
 SELECT * INTO STRICT h FROM d5.task_mapping_heads WHERE intent_id=i.intent_id FOR UPDATE;
 IF to_jsonb(i) IS DISTINCT FROM m->'intent' OR h.version<>d5.review_version(m->'mapping_version') OR h.source_basis IS DISTINCT FROM m->'last_applied_basis'
 OR h.source_basis_sha256 IS DISTINCT FROM m->>'last_applied_basis_sha256' OR h.projection IS DISTINCT FROM m->'before_projection' THEN RETURN 'MAPPING_VERSION_CONFLICT';END IF;
 proof=d5.read_isolated_local_head_proof(i.project_id,i.document_id,i.intent_id,(m#>>'{head_proof,application_command_id}')::uuid,(m#>>'{head_proof,proposal_id}')::uuid);
 IF proof IS NULL OR proof IS DISTINCT FROM m->'head_proof' OR d5.review_version(proof->'mapping_version_after')<>h.version
 OR proof->'source_present' IS DISTINCT FROM 'true'::jsonb OR proof->'source_basis' IS DISTINCT FROM h.source_basis OR proof->'projection' IS DISTINCT FROM h.projection THEN RETURN 'HEAD_PROOF_CONFLICT';END IF;
 SELECT * INTO STRICT rh FROM d5.isolated_local_edit_review_heads WHERE proposal_id=p.proposal_id;
 IF rh.version<>d5.review_version(pin->'review_version') OR rh.review_command_id IS DISTINCT FROM (pin->>'review_command_id')::uuid
 OR NOT EXISTS(SELECT FROM d5.isolated_local_edit_reviews WHERE command_id=rh.review_command_id AND decision='ACCEPT') THEN RETURN 'ISOLATED_LOCAL_EDIT_REVIEW_CONFLICT';END IF;
 SELECT * INTO STRICT ref FROM d5.reference_heads WHERE document_id=i.document_id AND profile=i.profile;
 IF ref.version<>d5.review_version(m->'reference_version') OR ref.observation_id IS DISTINCT FROM (m->>'observation_id')::uuid THEN RETURN 'REFERENCE_VERSION_CONFLICT';END IF;
 code=d5.local_edit_target_guard(i,h.projection);IF code IS NOT NULL THEN RETURN code;END IF;
 t=d5.task_target(i.task_id);l=jsonb_build_object('title',t->'title','description',t->'description');
 chosen=CASE WHEN m->>'choice'='USE_SOURCE' THEN h.projection ELSE l END;
 act=CASE WHEN m->>'choice'='KEEP_LOCAL' THEN 'KEEP_ISOLATED_LOCAL' ELSE 'PATCH_ISOLATED_LOCAL_USE_SOURCE' END;
 IF m->>'choice' NOT IN ('USE_SOURCE','KEEP_LOCAL') OR m->>'action' IS DISTINCT FROM act OR m->'result_projection' IS DISTINCT FROM chosen
 OR m->'local_projection' IS DISTINCT FROM l OR NOT d5.local_edit_valid_projection(l,true) OR NOT d5.local_edit_valid_projection(m->'after_projection',false)
 OR m->'after_projection' IS DISTINCT FROM h.projection OR m->'after_basis' IS DISTINCT FROM h.source_basis
 OR d5.task_semantic(m->'snapshot_row') IS DISTINCT FROM h.source_basis OR d5.task_projection(m->'snapshot_row') IS DISTINCT FROM h.projection THEN RETURN 'RESOLUTION_CONTENT_CONFLICT';END IF;
 IF t IS DISTINCT FROM m->'target' OR d5.task_hash('d5.task-target.v1',t) IS DISTINCT FROM m->>'target_sha256' THEN RETURN 'TARGET_CAS_CONFLICT';END IF;
 RETURN NULL;
END $$;
CREATE FUNCTION d5.apply_isolated_local_edit_tasks(envelope json) RETURNS jsonb LANGUAGE plpgsql VOLATILE SECURITY DEFINER
 SET search_path=pg_catalog,pg_temp SET timezone='UTC' AS $$
DECLARE req jsonb;prior jsonb;pkg d5.isolated_local_edit_packages;pin jsonb;p d5.isolated_local_edit_proposals;m jsonb;i d5.task_intents;code text;effects jsonb='[]'::jsonb;result jsonb;original d5.isolated_local_edit_applications;rid uuid;locator text;
BEGIN
 req=d5.review_envelope(envelope,'APPLY_ISOLATED_LOCAL_EDIT_TASKS',ARRAY['package_sha256']);
 PERFORM d5.task_lock_boundary();prior=d5.review_prior(req);IF prior IS NOT NULL THEN RETURN prior;END IF;
 SELECT * INTO pkg FROM d5.isolated_local_edit_packages WHERE package_sha256=req->>'package_sha256' AND project_id=(req->>'project_id')::uuid AND document_id=(req->>'document_id')::uuid;
 IF NOT FOUND THEN RETURN d5.task_conflict(req,'ISOLATED_LOCAL_EDIT_PACKAGE_SCOPE_CONFLICT');END IF;
 SELECT * INTO original FROM d5.isolated_local_edit_applications WHERE package_sha256=pkg.package_sha256;
 IF FOUND THEN RETURN d5.review_finish(req,jsonb_build_object('status','ALREADY_APPLIED','original_command_id',original.command_id,'package_sha256',pkg.package_sha256,'writes_d2',false));END IF;
 FOR pin IN SELECT x FROM jsonb_array_elements(pkg.items) x JOIN d5.isolated_local_edit_proposals rp ON rp.proposal_id=(x->>'proposal_id')::uuid ORDER BY rp.manifest#>>'{intent,intent_id}' LOOP
  SELECT * INTO STRICT p FROM d5.isolated_local_edit_proposals WHERE proposal_id=(pin->>'proposal_id')::uuid;
  IF p.manifest_sha256 IS DISTINCT FROM pin->>'manifest_sha256' OR p.manifest_sha256 IS DISTINCT FROM d5.task_hash('d5.isolated-local-edit-task-manifest.v1',p.manifest) THEN RAISE EXCEPTION 'Local resolution manifest integrity failure';END IF;
  code=d5.validate_isolated_local_edit(p,pin);IF code IS NOT NULL THEN RETURN d5.task_conflict(req,code);END IF;
 END LOOP;
 FOR pin IN SELECT * FROM jsonb_array_elements(pkg.items) LOOP
  SELECT * INTO STRICT p FROM d5.isolated_local_edit_proposals WHERE proposal_id=(pin->>'proposal_id')::uuid;m=p.manifest;
  SELECT * INTO STRICT i FROM d5.task_intents WHERE intent_id=(m#>>'{intent,intent_id}')::uuid;
  IF m->>'action'='PATCH_ISOLATED_LOCAL_USE_SOURCE' THEN
   UPDATE public.tasks SET title=m#>>'{result_projection,title}',description=m#>>'{result_projection,description}',row_version=row_version+1 WHERE id=i.task_id;
  END IF;
  rid=(m->>'revision_id')::uuid;locator=m#>>'{snapshot_row,source_locator}';
  IF NOT EXISTS(SELECT FROM d5.observations o JOIN public.source_revisions r ON r.id=o.revision_id WHERE o.observation_id=(m->>'observation_id')::uuid
   AND o.document_id=i.document_id AND o.project_id=i.project_id AND o.profile=i.profile AND o.revision_id=rid
   AND locator='sha256:'||r.sha256||'#L'||(m#>>'{snapshot_row,line_start}')) THEN RAISE EXCEPTION 'Local resolution provenance integrity failure';END IF;
  IF EXISTS(SELECT FROM d2.task_sources WHERE task_id=i.task_id AND revision_id=rid AND source_locator=locator AND (document_id<>i.document_id OR project_id<>i.project_id)) THEN RAISE EXCEPTION 'Source link collision';END IF;
  INSERT INTO d2.task_sources VALUES(i.task_id,rid,locator,i.document_id,i.project_id) ON CONFLICT DO NOTHING;
  UPDATE d5.task_mapping_heads SET version=version+1 WHERE intent_id=i.intent_id;
  INSERT INTO public.audit_events(actor,entity_type,entity_id,action,payload) VALUES(session_user,'D5_TASK_IMPORT',i.task_id,m->>'action',
   jsonb_build_object('command_id',req->>'command_id','manifest_sha256',p.manifest_sha256,'package_sha256',pkg.package_sha256,'choice',m->>'choice','result_projection',m->'result_projection','source_projection',m->'after_projection','activation_allowed',false));
  effects=effects||jsonb_build_array(jsonb_build_object('intent_id',i.intent_id,'task_id',i.task_id,'action',m->>'action','mapping_version_before',m->'mapping_version','mapping_version_after',d5.review_version(m->'mapping_version')+1,'head_proof',m->'head_proof','reason',m->>'reason','choice',m->>'choice','writes_task',m->>'action'='PATCH_ISOLATED_LOCAL_USE_SOURCE','manifest_sha256',p.manifest_sha256,'result_projection',m->'result_projection','source_projection',m->'after_projection'));
 END LOOP;
 result=jsonb_build_object('status','OK','package_sha256',pkg.package_sha256,'effects',effects,'writes_d2',true,'activation_allowed',false);
 INSERT INTO d5.isolated_local_edit_applications(package_sha256,command_id,result) VALUES(pkg.package_sha256,(req->>'command_id')::uuid,result);
 RETURN d5.review_finish(req,result);
END $$;
CREATE FUNCTION d5.read_isolated_local_edit_proposal(pid uuid,doc uuid,proposal uuid) RETURNS jsonb LANGUAGE sql STABLE SECURITY DEFINER
 SET search_path=pg_catalog,pg_temp AS $$ SELECT jsonb_build_object('proposal_id',p.proposal_id,'manifest_sha256',p.manifest_sha256,'manifest',p.manifest,
 'review_version',h.version,'review_command_id',h.review_command_id) FROM d5.isolated_local_edit_proposals p JOIN d5.isolated_local_edit_review_heads h USING(proposal_id)
 WHERE p.proposal_id=proposal AND p.manifest#>>'{intent,project_id}'=pid::text AND p.manifest#>>'{intent,document_id}'=doc::text $$;
CREATE FUNCTION d5.read_isolated_local_edit_package(pid uuid,doc uuid,digest text) RETURNS jsonb LANGUAGE sql STABLE SECURITY DEFINER
 SET search_path=pg_catalog,pg_temp AS $$ SELECT to_jsonb(p) FROM d5.isolated_local_edit_packages p WHERE p.project_id=pid AND p.document_id=doc AND p.package_sha256=digest $$;
GRANT EXECUTE ON FUNCTION d5.prepare_isolated_local_edit_task(json,bytea),d5.package_isolated_local_edit_tasks(json) TO d5_writer;
GRANT EXECUTE ON FUNCTION d5.review_isolated_local_edit_task(json) TO d5_reviewer;
GRANT EXECUTE ON FUNCTION d5.apply_isolated_local_edit_tasks(json) TO d5_applier;
GRANT EXECUTE ON FUNCTION d5.read_isolated_local_head_proof(uuid,uuid,uuid,uuid,uuid) TO d5_writer,d5_reader,d5_reviewer,d5_applier;
GRANT EXECUTE ON FUNCTION d5.read_isolated_local_edit_proposal(uuid,uuid,uuid),d5.read_isolated_local_edit_package(uuid,uuid,text) TO d5_writer,d5_reader,d5_reviewer,d5_applier;
RESET ROLE;
REVOKE CREATE ON SCHEMA d5 FROM d5_apply_owner;
COMMIT;
