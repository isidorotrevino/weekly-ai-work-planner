#!/usr/bin/env python3
# SPDX-License-Identifier: GPL-3.0-only
"""Reviewable A21/A22 derivatives. Never edit historical SQL or generators."""
from pathlib import Path
import hashlib,sys
R=Path(__file__).resolve().parents[2]
def fn(file,name,sql=False):
 s=(R/file).read_text();a=s.index('FUNCTION '+name+'(');a=s.rfind('CREATE',0,a);b=s.index('$$;',a)+3 if sql else s.index('END $$;',a)+7;return s[a:b].replace('CREATE FUNCTION','CREATE OR REPLACE FUNCTION',1)
def once(s,a,b):
 assert s.count(a)==1,(a,s.count(a));return s.replace(a,b)
parts=[(R/'testing/D4/sql/review-active.sql').read_text()]
v27='migrations-d4-proposed/V27__sealed_absence_retry.sql';v26='migrations-d4-proposed/V26__conclusive_reconciliation.sql';v24='migrations-d4-proposed/V24__linear_multicount_checkpoints.sql';v20='migrations-d4-proposed/V20__continuation_admission_adapters.sql';v18='migrations-d4-proposed/V18__synthetic_lab_bridge.sql';v13='migrations-d3-dispatch-proposed/V13__guarded_dispatch.sql';v12='migrations-d3-proposed/V12__planning_snapshot_and_publication.sql'
s=fn(v12,'d3.state_body');s=once(s,"WHERE r.capabilities @>","WHERE NOT d4.review_blocked(o.id,r.id,coalesce((o.policy_snapshot->>'integration_phase')::boolean,false)) AND r.capabilities @>");parts.append(s)
s=fn('migrations-proposed/V9__execution_guards_contract_draft.sql','d2.execution');s=once(s,' prior=d2.begin_command',' PERFORM d3.lock_state();\n prior=d2.begin_command');s=once(s,' old_state=op.state;'," old_state=op.state;\n IF action IN ('CLAIM','START','HEARTBEAT','VERIFY','RECOVERY_VERIFY','RECONCILE','RESUME_RECONCILIATION','REJECT_VERIFICATION') THEN PERFORM d4.require_unheld(op.id,coalesce(rid,(SELECT resource_id FROM d2.reservations WHERE operation_id=op.id)));END IF;");parts.append(s)
s=fn(v13,'d3.execution');s=once(s,"  IF action IN ('START','HEARTBEAT') THEN", "  IF action IN ('START','HEARTBEAT','VERIFY','RECOVERY_VERIFY','RECONCILE','RESUME_RECONCILIATION','REJECT_VERIFICATION') THEN PERFORM d4.require_unheld(op.id,d.resource_id);END IF;\n  IF action IN ('START','HEARTBEAT') THEN");parts.append(s)
s=fn(v13,'d3.dispatch');s=once(s,'  at_time=clock_timestamp();','  PERFORM d4.require_unheld(oid,rid);\n  at_time=clock_timestamp();');parts.append(s)
s=fn(v20,'d4.publish_continuation');s=once(s,'    SELECT * INTO STRICT worker FROM','    PERFORM d4.require_unheld(op.id,resource.id);\n    SELECT * INTO STRICT worker FROM');parts.append(s)
# Physical eligibility is per resource, in addition to d2 effective dependency guards.
s=fn(v20,'d4.observe_continuation_eligibility');s=once(s,"AND r.capabilities @>","AND NOT d4.review_blocked(item.id,r.id,coalesce((item.policy_snapshot->>'integration_phase')::boolean,false)) AND r.capabilities @>");parts.append(s)
s=fn(v27,'d4.dispatch_continuation');s=once(s,'absau uuid;','absau uuid;reviewau uuid;')
s=once(s,' SELECT * INTO mi FROM'," PERFORM d4.require_unheld((req->>'operation_id')::uuid,(req->>'resource_id')::uuid);\n SELECT id INTO reviewau FROM d4.review_authorizations WHERE authorized_version=(SELECT row_version FROM public.operations WHERE id=(req->>'operation_id')::uuid) AND d4.review_checkpoint_safe((req->>'operation_id')::uuid,(SELECT lease_generation FROM public.operations WHERE id=(req->>'operation_id')::uuid));\n SELECT * INTO mi FROM")
s=once(s,'AND d4.multi_safe(h.operation_id,h.source_generation);','AND (d4.multi_safe(h.operation_id,h.source_generation) OR d4.review_checkpoint_safe(h.operation_id,h.source_generation));')
s=once(s,'OR abs.id IS NOT NULL THEN','OR abs.id IS NOT NULL OR reviewau IS NOT NULL THEN')
s=once(s,"'d4.absence_links'] LOOP","'d4.absence_links','d4.review_revisions','d4.review_cases','d4.review_unbound_affected','d4.review_affected','d4.review_barriers','d4.review_closures','d4.review_authorizations','d4.review_links','d4.review_candidates','d4.review_containments'] LOOP")
s=once(s,' RETURN result;\nEND $$;'," IF reviewau IS NOT NULL THEN INSERT INTO d4.review_links VALUES(reviewau,(result->>'attempt_id')::uuid);END IF;\n RETURN result;\nEND $$;");parts.append(s)
# New acceptance facts and continuation authorities must respect quarantine.
for file,name,needle,guard in [
 (v24,'d4.multi_authorize'," IF op.state<>'CANCELLED'",' PERFORM d4.require_unheld(op.id,(SELECT resource_id FROM d2.reservations WHERE operation_id=op.id));\n'),
 (v26,'d4.authorize_continuation'," IF op.state<>'CANCELLED'",' PERFORM d4.require_unheld(op.id,(SELECT resource_id FROM d2.reservations WHERE operation_id=op.id));\n'),
 (v27,'d4.absence_authorize'," IF o.state NOT IN",' PERFORM d4.require_unheld(o.id,(SELECT resource_id FROM d2.reservations WHERE operation_id=o.id));\n'),
 (v26,'d4.recovery_accept'," IF o.state<>'VERIFYING'",' PERFORM d4.require_unheld(o.id,(SELECT resource_id FROM d2.reservations WHERE operation_id=o.id));\n'),
 (v26,'d4.record_continuation_acceptance'," IF op.state<>'VERIFYING'",' PERFORM d4.require_unheld((info->>\'operation\')::uuid,(info->>\'resource\')::uuid);\n'),
 (v24,'d4.multi_accept'," INSERT INTO d2.effect_receipts",' PERFORM d4.require_unheld((info->>\'operation\')::uuid,(info->>\'resource\')::uuid);\n'),
 (v18,'d4.lab_record_evidence',"  logical_key=",'  IF accepted THEN PERFORM d4.require_unheld((info->>\'operation\')::uuid,(info->>\'resource\')::uuid);END IF;\n')]:
 s=fn(file,name);parts.append(once(s,needle,guard+needle))
s=fn(v27,'d4.worker_execution_status');s=once(s," RETURN jsonb_build_object('schema'", " safe=coalesce(safe,false) AND NOT d4.review_blocked((info->>'operation')::uuid,(info->>'resource')::uuid,true);\n RETURN jsonb_build_object('schema'");parts.append(s)
parts.append("REVOKE ALL ON ALL TABLES IN SCHEMA d4 FROM PUBLIC;\nREVOKE ALL ON FUNCTION d2.task_eligible(uuid),d2.integration_eligible(uuid) FROM PUBLIC;\nDO $$ DECLARE f record;BEGIN FOR f IN SELECT p.oid::regprocedure n FROM pg_proc p JOIN pg_namespace ns ON ns.oid=p.pronamespace WHERE ns.nspname='d4' AND (p.proname LIKE 'review_%' OR p.proname IN ('canonical_results','revision_current','case_blocks','require_unheld','continuation_safe')) LOOP EXECUTE format('REVOKE ALL ON FUNCTION %s FROM PUBLIC',f.n);END LOOP;END $$;")
headers=''.join('-- Source SHA256 '+f+' '+hashlib.sha256((R/f).read_bytes()).hexdigest()+'\n' for f in ['testing/D4/sql/review-active.sql',v27,v26,v24,v20,v18,v13,v12,'migrations-proposed/V9__execution_guards_contract_draft.sql'])
out='-- GENERATED A21/A22 by testing/D4/generate-review-admission.py; laboratory only.\n'+headers+'\n\n'.join(parts)+'\n';p=R/'migrations-d4-proposed/V28__verified_revision_and_quarantine.sql'
if '--check' in sys.argv:assert p.read_text()==out,'Review SQL differs'
else:p.write_text(out)
p=R/'testing/D4/lab/src/main/java/io/github/isidorotrevino/planner/postgres/AbsencePlanningStore.java';s=p.read_text().replace('AbsencePlanningStore','ReviewPlanningStore').replace("('SEALED_CHECKPOINT','SEALED_ABSENCE')","('SEALED_CHECKPOINT','SEALED_ABSENCE','SEALED_REVIEW_CHECKPOINT')");s='// Generated A21/A22 derivative SHA256 '+hashlib.sha256(p.read_bytes()).hexdigest()+'\n'+s;p=p.with_name('ReviewPlanningStore.java')
if '--check' in sys.argv:assert p.read_text()==s,'Review Java differs'
else:p.write_text(s)
