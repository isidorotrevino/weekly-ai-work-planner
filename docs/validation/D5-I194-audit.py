#!/usr/bin/env python3
"""I194 documentary plan review only: Git/JSON/reverse coverage/graphs. No product/components, image, crypto, claim or protocol execution."""
import hashlib
import io
import json
import runpy
import subprocess
from pathlib import Path

ROOT=Path(__file__).resolve().parents[2];P='docs/validation/'
BASE='ce5f5d9d099b152750659fd306fa9a157fea8904'
PLAN=P+'D5-I193-CALLER-IMAGE-CUSTODY-EVIDENCE-PLAN.json'
CHECK=P+'D5-I193-CUSTODY-EVIDENCE-CHECKLIST.json'
OLD_PREP=P+'D5-I193-preparation-review.json'
OLD_AUDIT=P+'D5-I193-audit.py'
PRIOR_SEAL=P+'D5-I193-integrity.json'
OLD_DOC='docs/design/D5-I193-CALLER-IMAGE-CUSTODY-EVIDENCE-PLAN.md'
PRIOR_FILES={PLAN,CHECK,OLD_PREP,OLD_AUDIT,PRIOR_SEAL,OLD_DOC}
RECON=P+'D5-I194-I193-source-reconstruction.json'
REVIEW=P+'D5-I194-I193-documentary-review.json'
AUDIT=P+'D5-I194-audit.py';SEAL=P+'D5-I194-integrity.json'
DOC='docs/design/D5-I194-I193-CUSTODY-EVIDENCE-PLAN-REVIEW.md'
FILES={RECON,REVIEW,AUDIT,SEAL,DOC}


def rd(p):return json.loads((ROOT/p).read_text())
def sha(p):return hashlib.sha256((ROOT/p).read_bytes()).hexdigest()
def git(*args):return subprocess.check_output(['git',*args],cwd=ROOT,text=True).strip()
def pin(p,q):return dict(path=p,sha256=sha(p),json_pointer=q)


def dependency_review(steps):
    edges={s['id']:set(s['depends_on']) for s in steps};done=set();active=set();order=[]
    def visit(n):
        assert n in edges and n not in active
        if n in done:return
        active.add(n)
        for q in sorted(edges[n]):visit(q)
        active.remove(n);done.add(n);order.append(n)
    for n in sorted(edges):visit(n)
    def ancestors(n):
        found=set();todo=list(edges[n])
        while todo:
            q=todo.pop()
            if q not in found:found.add(q);todo+=list(edges[q])
        return found
    assert ancestors('CE11')==set(edges)-{'CE11','CE12'}
    assert ancestors('CE12')==set(edges)-{'CE12'}
    assert ancestors('CE08')==set(['CE%02d'%i for i in range(1,8)])
    assert 'CE08' in ancestors('CE09') and 'CE12' not in ancestors('CE11')
    return order,ancestors


def reconstruct():
    plan=rd(PLAN);check=rd(CHECK);pins={**plan['input_pins'],**{p:sha(p) for p in sorted(PRIOR_FILES)}}
    assert len(pins)==767
    request=''.join(BASE+':'+p+'\n' for p in sorted(pins)).encode()
    stream=io.BytesIO(subprocess.check_output(['git','cat-file','--batch'],cwd=ROOT,input=request))
    for p,h in sorted(pins.items()):
        head=stream.readline().decode().split();assert len(head)==3 and head[1]=='blob',p
        body=stream.read(int(head[2]));assert stream.read(1)==b'\n'
        assert hashlib.sha256(body).hexdigest()==h==sha(p),p
    previous=runpy.run_path(str(ROOT/OLD_AUDIT));assert previous['build_review']()==rd(OLD_PREP)
    for b in plan['bindings'].values():assert sha(b['path'])==b['sha256']
    spec=rd(plan['bindings']['custody_contract']['path']);defs=rd(plan['bindings']['custody_schemas']['path'])['$defs']
    assert check['plan']==dict(path=PLAN,sha256=sha(PLAN))
    steps=plan['steps'];by_id={s['id']:s for s in steps};assert len(steps)==len(by_id)==12
    order,ancestors=dependency_review(steps)
    assert order==['CE%02d'%i for i in range(1,13)]
    final_map={'anchor_registry':'CE02','actor_registry':'CE08','image_manifest':'CE08','caller_identity':'CE08',
               'platform_custody':'CE08','acceptance_record':'CE09','custody_bundle':'CE10','launch_receipt':'CE12'}
    family_rows=[];assert len(check['family_gates'])==8
    for gate in check['family_gates']:
        f=gate['family'];final=gate['final_record_freeze_step'];assert final==final_map[f]
        stages=gate['candidate_step_ids'];assert final in stages
        assert stages==plan['record_family_coverage'][f]
        assert all(f in by_id[i]['record_families'] for i in stages)
        assert gate['required_top_level_fields']==defs[f]['required']
        assert gate['schema_pointer']=='/$defs/'+f and gate['schema_binding']==plan['bindings']['custody_schemas']
        assert gate['body_cap_bytes']==spec['record_caps_bytes'][f]
        assert gate['acceptance_requires_final_step_and_dependencies']
        assert gate['actual_body_sha256'] is None and not gate['accepted']
        assert gate['conditional_after_launch']==(f=='launch_receipt')
        assert final in ancestors('CE11') if f!='launch_receipt' else final=='CE12'
        family_rows.append(dict(family=f,intake_steps=stages,finalization_step=final,body_cap_bytes=gate['body_cap_bytes'],actual_evidence_accepted=False))
    assert set(final_map)==set(spec['record_families'])==set(plan['record_family_coverage'])
    inverse={i:set() for i in by_id};rule_rows=[]
    assert len(check['contract_rule_gates'])==16
    for index,gate in enumerate(check['contract_rule_gates']):
        rule=spec['rules'][index]['id'];assert gate['rule_id']==rule and gate['contract_rule_pointer']=='/rules/'+str(index)
        assert gate['contract_binding']==plan['bindings']['custody_contract']
        assert gate['candidate_step_ids'] and gate['status']=='PENDING_EVIDENCE_NOT_EVALUATED' and not gate['accepted']
        for i in gate['candidate_step_ids']:assert i in inverse;inverse[i].add(rule)
        rule_rows.append(dict(rule=rule,step_ids=gate['candidate_step_ids'],accepted=False))
    for i in by_id:assert inverse[i]==set(by_id[i]['contract_rules'])
    assert set().union(*inverse.values())=={'K%02d'%i for i in range(1,17)}
    assert {g['id'] for g in check['global_gates']}=={'G%02d'%i for i in range(1,8)}
    for g in check['global_gates']:assert g['status']=='PENDING_NOT_EVALUATED' and not g['accepted']
    dossiers=[]
    for i,step in by_id.items():
        assert step['status']==('DEFERRED_NOT_AUTHORIZED' if i=='CE12' else 'PLANNED_EVIDENCE_MISSING_NOT_ACCEPTED')
        assert step['required_evidence'] and step['acceptance_checks'] and step['authorization_boundary']
        assert not step['candidate_dossier_created'] and not step['accepted'] and not step['current_execution_authorized']
        assert step['actual_record_hashes'] is None
        roles=step['provenance_and_role'];assert roles['producer_person'] is None and roles['reviewer_persons'] is None
        assert not roles['accepted_appointments'] and roles['reviewer_not_automatically_evidence_author']
        assert roles['producer_role']=='EXTERNAL_EVIDENCE_PROVIDER_OR_DOCUMENTARY_PREPARER' and roles['separate_acceptor_role']=='R08'
        path=step['candidate_dossier_path'];assert not (ROOT/path).exists();dossiers.append(path)
    assert len(set(dossiers))==12
    boundary=plan['closure_boundaries']
    assert boundary['prelaunch_review']=='CE11' and boundary['deferred_receipt']=='CE12'
    assert boundary['prelaunch_depends_on_receipt'] is False and boundary['receipt_currently_authorized'] is False
    assert len(boundary['external_prerequisites_for_receipt'])==5
    assert 'SEPARATE_EXPLICIT_EXECUTION_AUTHORIZATION' in boundary['external_prerequisites_for_receipt']
    assert 'ACTUAL_FULL_ROOT_ADMISSION' in boundary['external_prerequisites_for_receipt']
    assert 'ACTUAL_ATOMIC_ONE_USE_CLAIM_AND_PROTECTED_CONSTRUCTION' in boundary['external_prerequisites_for_receipt']
    assert not boundary['custody_prelaunch_evidence_currently_accepted']
    assert check['prelaunch_families']==[f for f in spec['record_families'] if f!='launch_receipt']
    assert check['deferred_families']==['launch_receipt']
    assert check['accepted_family_count']==check['accepted_rule_count']==check['accepted_global_gate_count']==0
    assert check['current_effect']==plan['current_effect'] and check['decision']==plan['decision']==spec['decision'] and check['E06']==plan['E06']==spec['E06']
    assert plan['current_effect']['accepted_steps']==plan['current_effect']['actual_external_record_families_accepted']==plan['current_effect']['candidate_dossiers_created']==0
    assert not plan['current_effect']['current_execution_authorized'] and not plan['current_effect']['quotas_changed'] and not plan['current_effect']['rebind_applied']
    return dict(schema='d5.i194-i193-source-reconstruction.v1',increment='I194',date='2026-11-16',base_commit=BASE,
        input_pins=pins,method='Fresh Git blobs, separate DFS ancestor reconstruction and reverse checklist-to-schema/step/rule coverage; prior documentary preparation reproduced without its publication-boundary main.',
        plan_structure=dict(steps=12,dependency_order=order,acyclic=True,prelaunch_ancestors=sorted(ancestors('CE11')),
            prelaunch_does_not_depend_on_receipt=True,receipt_after_prelaunch_and_external_actual_authorization=True,
            CE08_freeze_after_CE03_intake_and_CE04_CE07_evidence_before_CE09_C=True),
        reverse_coverage=dict(families=family_rows,contract_rules=rule_rows,global_gates=7,total_gates=31,
            all_required_family_fields_caps_pointers_covered=True,all_rule_step_incidence_exact=True,
            no_intake_stage_can_substitute_for_final_freeze=True,prelaunch_families=7,deferred_receipt_families=1),
        authority_scope=dict(dossiers_not_runtime_records_or_inputs=True,all_dossiers_absent=True,all_people_unassigned=True,
            no_evidence_or_gate_accepted=True,no_provider_contact_or_build_enrollment_crypto_claim_execution_authorized=True,
            actual_runtime_or_resource_correctness_verified=False),
        verdict=dict(new_blocking_documentary_findings=0,documentary_plan_consistent=True,
            adopted=False,implemented=False,independent_acceptance=False,actual_evidence_accepted=0,
            F179_01_resolved=False,resource_obligations_closed=0,product_or_components_executed=0))


def build_review(rec):
    plan=rd(PLAN)
    return dict(schema='d5.i194-i193-documentary-review.v1',increment='I194',date='2026-11-16',timezone='Europe/Madrid',base_commit=BASE,
        proposal=plan['proposal_id'],profile_id=plan['profile_id'],plan_id=plan['plan_id'],
        status='CUSTODY_EVIDENCE_PLAN_DOCUMENTARILY_CONFIRMED_NOT_ADOPTED_NOT_EXECUTED_NOT_ADMITTED',
        reconstruction=dict(path=RECON,sha256=sha(RECON)),
        provenance=dict(reviewer='Same Codex assistant/chat that prepared I193 and previous contracts',methodological_reconstruction_separate=True,
            actor_independent=False,organizationally_independent=False,independent_acceptance=False,custodian_acceptance=False),
        findings=[],checks=[dict(id=i,scope=s,result=r) for i,s,r in [
            ('R01','12 packets, explicit deliverables/evidence/roles/dependencies/rejection boundaries','PASS_CONCRETE_DOCUMENTARY_PLAN'),
            ('R02','Eight schema families with exact fields/caps/pointers and final freeze step','PASS_REVERSE_RECORD_COVERAGE'),
            ('R03','16 K-rules and seven global gates, exact bidirectional step incidence','PASS_COMPLETE_CHECKLIST_COVERAGE'),
            ('R04','Provisional CE03 roster, CE08 complete freeze before CE09 C','PASS_NO_EARLY_COMPLETENESS_OR_FORWARD_AUTH'),
            ('R05','CE11 independent of CE12 receipt; late actual claim needs separate prerequisites','PASS_NO_PRELAUNCH_RECEIPT_CYCLE'),
            ('R06','No dossiers, actors, appointments, hashes or evidence accepted/created','PASS_TRUTHFUL_CURRENT_PENDING_STATE'),
            ('R07','Producer separate from actual competent reviewer/acceptor; eight S01/custody rules preserved','PASS_DECLARED_ROLE_POLICY_NOT_REAL_INDEPENDENCE'),
            ('R08','Refresh invalidates dependent candidate hashes; no current rebind or proof transfer','PASS_FREEZE_FRESHNESS_IMPACT_CONTRACT'),
            ('R09','Complete source/image/runtime/E01-E05 and caps/900 evidence required, no counts/placeholders substitute','PASS_RESOURCE_GATE_NOT_RESOURCE_PROOF'),
            ('R10','Plan does not authorize contact/build/probe/crypto/product/components/claim/worker or quotas','PASS_AUTHORIZATION_BOUNDARY'),
            ('R11','Same preparer/reviewer actor; no competent adoption or acceptance','PASS_PROVENANCE_DISCLOSURE')]],
        evidence=[pin(PLAN,'/steps'),pin(PLAN,'/closure_boundaries'),pin(PLAN,'/freeze_and_refresh'),pin(CHECK,'/family_gates'),pin(CHECK,'/contract_rule_gates')],
        verdict=rec['verdict'],current_effect=plan['current_effect'],decision=plan['decision'],E06=plan['E06'],
        next_scope='A separately requested CE01 documentary dossier is a possible next preparation. Keep every actual evidence/appointment/authorization gate pending until genuine competent external facts and review exist; no step automatically runs or accepts its dependencies.',
        limitations=['A complete evidence plan/checklist is not actual role/anchor/caller/image/platform/claim evidence or resource closure.',
            'CE07 requires exact sources and complete genuine bounds/requalification; CE08 refresh must revisit any proof/review invalidated by changed authors/bytes/scopes, not merely recompute hashes.',
            'CE12 is not a requirement for prelaunch custody acceptance and cannot be manufactured from schema. Actual final E06/root/Q/claim/worker actions remain separately authorized and currently absent.'],
        work_unit=dict(rollback_files=sorted(FILES),verification_command='python3 docs/validation/D5-I194-audit.py',expected_result='PASS_STATIC_SOURCE_ONLY',
            runtime_harness='N/A: documentary evidence-plan review; no product/component/crypto/image/claim/protocol execution.',over400_lines=True,
            reason='Traceable reverse coverage/DFS/finalization/authorization review and preservation seal as one documentary unit; overage reported.'),
        publication=dict(commit_and_push_requested=True,publication_not_adoption_acceptance_or_authority=True))


def main():
    rec=reconstruct();assert rd(RECON)==rec and rd(REVIEW)==build_review(rec)
    prior=rd(PRIOR_SEAL);preserved={**prior['preserved_published453'],**prior['artifacts'],PRIOR_SEAL:sha(PRIOR_SEAL)}
    assert len(preserved)==459
    seal=rd(SEAL);assert seal['schema']=='d5.i194-integrity.v1' and seal['base_commit']==BASE
    assert seal['preserved_published459']==preserved and set(seal['artifacts'])==FILES-{SEAL}
    for pins in [preserved,seal['artifacts']]:
        for p,h in pins.items():assert sha(p)==h,p
    assert seal['source_only'] and seal['resource_obligations_closed']==0 and seal['IR03']=='NOT_READY'
    for k in ['independent_acceptance','product_or_components_executed','quotas_changed','rebind_applied','proposal_enabled','D5_closed']:assert seal[k] is False
    changed=set(git('diff',BASE,'--name-only').splitlines())|set(git('ls-files','--others','--exclude-standard').splitlines());assert changed==FILES,changed
    subprocess.check_call(['git','merge-base','--is-ancestor',BASE,'HEAD'],cwd=ROOT)
    if git('rev-parse','HEAD')!=BASE:assert not git('status','--porcelain')
    print(json.dumps(dict(status='PASS_STATIC_SOURCE_ONLY',increment='I194',new_blocking_documentary_findings=0,documentary_plan_consistent=True,
        steps=12,total_gates=31,historical_pins=767,prior_published_files_preserved=459,new_files=5,
        prelaunch_depends_on_receipt=False,actual_evidence_accepted=0,adopted=False,implemented=False,independent_acceptance=False,
        product_or_components_executed=0,quotas_changed=False,rebind_applied=False,resource_obligations_closed=0,
        proposal_enabled=False,F179_01_resolved=False,D5_closed=False,IR03='NOT_READY',git_head=git('rev-parse','HEAD')),sort_keys=True))

if __name__=='__main__':main()
