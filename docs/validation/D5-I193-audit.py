#!/usr/bin/env python3
"""I193 documentary evidence-plan checks only. No product/components, crypto, image, claim or protocol execution."""
import hashlib
import io
import json
import runpy
import subprocess
from pathlib import Path

ROOT=Path(__file__).resolve().parents[2];P='docs/validation/'
BASE='24b1ce69e404add2eea97f061f377699eab1b85c'
PLAN=P+'D5-I193-CALLER-IMAGE-CUSTODY-EVIDENCE-PLAN.json'
CHECK=P+'D5-I193-CUSTODY-EVIDENCE-CHECKLIST.json'
PREP=P+'D5-I193-preparation-review.json';AUDIT=P+'D5-I193-audit.py';SEAL=P+'D5-I193-integrity.json'
DOC='docs/design/D5-I193-CALLER-IMAGE-CUSTODY-EVIDENCE-PLAN.md'
FILES={PLAN,CHECK,PREP,AUDIT,SEAL,DOC};PRIOR_SEAL=P+'D5-I192-integrity.json'


def rd(p):return json.loads((ROOT/p).read_text())
def sha(p):return hashlib.sha256((ROOT/p).read_bytes()).hexdigest()
def git(*args):return subprocess.check_output(['git',*args],cwd=ROOT,text=True).strip()


def topo(edges):
    pending={k:set(v) for k,v in edges.items()};order=[]
    assert all(v<=set(pending) for v in pending.values())
    while pending:
        ready=sorted(k for k,v in pending.items() if not v)
        if not ready:return None
        order+=ready
        for k in ready:del pending[k]
        for v in pending.values():v.difference_update(ready)
    return order


def build_review():
    plan=rd(PLAN);check=rd(CHECK);pins=plan['input_pins'];assert len(pins)==761
    requests=''.join(BASE+':'+p+'\n' for p in sorted(pins)).encode()
    stream=io.BytesIO(subprocess.check_output(['git','cat-file','--batch'],cwd=ROOT,input=requests))
    for p,h in sorted(pins.items()):
        header=stream.readline().decode().split();assert len(header)==3 and header[1]=='blob',p
        body=stream.read(int(header[2]));assert stream.read(1)==b'\n'
        assert hashlib.sha256(body).hexdigest()==h==sha(p),p
    previous=runpy.run_path(str(ROOT/(P+'D5-I192-audit.py')));r=previous['reconstruct']()
    assert rd(previous['RECON'])==r and rd(previous['REVIEW'])==previous['build_review'](r)
    prior=rd(PRIOR_SEAL);preserved={**prior['preserved_published448'],**prior['artifacts'],PRIOR_SEAL:sha(PRIOR_SEAL)}
    assert len(preserved)==453
    for p,h in preserved.items():assert sha(p)==h,p
    for b in plan['bindings'].values():assert sha(b['path'])==b['sha256']
    spec=rd(plan['bindings']['custody_contract']['path']);pack=rd(plan['bindings']['custody_schemas']['path']);defs=pack['$defs']
    assert plan['base_commit']==check['base_commit']==BASE and plan['increment']==check['increment']=='I193'
    assert check['plan']==dict(path=PLAN,sha256=sha(PLAN))
    steps=plan['steps'];ids=[s['id'] for s in steps];assert ids==['CE%02d'%i for i in range(1,13)]
    edges={s['id']:s['depends_on'] for s in steps};order=topo(edges);assert order==ids
    def closure(n):
        out=set();todo=list(edges[n])
        while todo:
            x=todo.pop()
            if x not in out:out.add(x);todo+=edges[x]
        return out
    assert closure('CE11')==set(ids[:10]) and 'CE12' not in closure('CE11')
    assert closure('CE12')==set(ids[:11])
    assert 'CE08' in closure('CE09') and set(['CE03','CE04','CE05','CE06','CE07'])<=closure('CE08')
    # Deliberately reversed receipt dependency would introduce the prohibited cycle.
    bad={k:list(v) for k,v in edges.items()};bad['CE11'].append('CE12');assert topo(bad) is None
    assert plan['closure_boundaries']['prelaunch_review']=='CE11' and plan['closure_boundaries']['deferred_receipt']=='CE12'
    assert plan['closure_boundaries']['prelaunch_depends_on_receipt'] is False
    assert not plan['closure_boundaries']['receipt_currently_authorized'] and not plan['closure_boundaries']['custody_prelaunch_evidence_currently_accepted']
    assert plan['closure_boundaries']['external_prerequisites_for_receipt']==['SEPARATE_EXPLICIT_EXECUTION_AUTHORIZATION','ACTUAL_FINAL_E06_AND_PAYLOAD',
        'ACTUAL_Q_AND_TRUSTED_FINAL_ROOT','ACTUAL_FULL_ROOT_ADMISSION','ACTUAL_ATOMIC_ONE_USE_CLAIM_AND_PROTECTED_CONSTRUCTION']
    all_rules={r['id'] for r in spec['rules']};coverage={f:[] for f in spec['record_families']};paths=[]
    for step in steps:
        i=step['id'];assert step['status']==('DEFERRED_NOT_AUTHORIZED' if i=='CE12' else 'PLANNED_EVIDENCE_MISSING_NOT_ACCEPTED')
        assert not step['accepted'] and not step['current_execution_authorized']
        assert step['actual_record_hashes'] is None and not step['candidate_dossier_created']
        assert step['required_evidence'] and step['acceptance_checks'] and step['authorization_boundary']
        role=step['provenance_and_role'];assert role['producer_role']=='EXTERNAL_EVIDENCE_PROVIDER_OR_DOCUMENTARY_PREPARER'
        assert role['producer_person'] is None and role['reviewer_persons'] is None
        assert not role['accepted_appointments'] and role['reviewer_not_automatically_evidence_author']
        assert role['separate_acceptor_role']=='R08' and role['primary_review_roles']
        assert set(step['contract_rules'])<=all_rules
        path=step['candidate_dossier_path'];assert path.startswith(P+'D5-I193-'+i+'-') and path.endswith('-CANDIDATE.json')
        assert not (ROOT/path).exists();paths.append(path)
        for f in step['record_families']:assert f in coverage;coverage[f].append(i)
    assert len(set(paths))==12 and plan['record_family_coverage']==coverage
    assert coverage['launch_receipt']==['CE12']
    assert all(v and any(i in closure('CE11') for i in v) for f,v in coverage.items() if f!='launch_receipt')
    assert 'CE08' in coverage['actor_registry'] and 'CE03' in coverage['actor_registry']
    assert len(check['family_gates'])==8 and len(check['contract_rule_gates'])==16 and len(check['global_gates'])==7
    for gate in check['family_gates']:
        f=gate['family'];assert gate['schema_binding']==plan['bindings']['custody_schemas']
        assert gate['schema_pointer']=='/$defs/'+f and gate['required_top_level_fields']==defs[f]['required']
        assert gate['candidate_step_ids']==coverage[f] and gate['body_cap_bytes']==spec['record_caps_bytes'][f]
        assert gate['conditional_after_launch']==(f=='launch_receipt')
        assert gate['status']==('DEFERRED_NOT_AUTHORIZED' if f=='launch_receipt' else 'PENDING_EVIDENCE_NOT_EVALUATED')
        assert gate['actual_body_sha256'] is None and not gate['accepted']
        final={'anchor_registry':'CE02','actor_registry':'CE08','image_manifest':'CE08','caller_identity':'CE08','platform_custody':'CE08','acceptance_record':'CE09','custody_bundle':'CE10','launch_receipt':'CE12'}[f]
        assert gate['final_record_freeze_step']==final and final in coverage[f] and gate['acceptance_requires_final_step_and_dependencies']
    for index,gate in enumerate(check['contract_rule_gates']):
        key=spec['rules'][index]['id'];assert gate['rule_id']==key and gate['contract_rule_pointer']=='/rules/'+str(index)
        assert gate['contract_binding']==plan['bindings']['custody_contract']
        expected=[s['id'] for s in steps if key in s['contract_rules']]
        assert gate['candidate_step_ids']==expected and expected
        assert gate['status']=='PENDING_EVIDENCE_NOT_EVALUATED' and not gate['accepted']
    assert set().union(*(set(s['contract_rules']) for s in steps))==all_rules
    for g in check['global_gates']:assert g['status']=='PENDING_NOT_EVALUATED' and not g['accepted']
    assert check['prelaunch_families']==[f for f in spec['record_families'] if f!='launch_receipt']
    assert check['deferred_families']==['launch_receipt']
    assert check['accepted_family_count']==check['accepted_rule_count']==check['accepted_global_gate_count']==0
    assert check['current_effect']==plan['current_effect'] and check['decision']==plan['decision']==spec['decision'] and check['E06']==plan['E06']==spec['E06']
    assert plan['current_effect']['candidate_dossiers_created']==plan['current_effect']['actual_external_record_families_accepted']==plan['current_effect']['accepted_steps']==0
    assert plan['current_effect']['evidence_plan_prepared'] and plan['current_effect']['F183_01_documentary_repair_preserved']
    for k in ['actual_actors_caller_image_or_anchors_supplied','current_execution_authorized','adopted','implemented','S01_accepted','F179_01_resolved',
        'independent_acceptance','product_or_components_executed','active_schema_changed','quotas_changed','rebind_applied','proposal_enabled','D5_closed']:assert plan['current_effect'][k] is False
    assert plan['current_effect']['resource_obligations_closed']==0 and plan['current_effect']['IR03']=='NOT_READY'
    assert set(plan['work_unit']['rollback_files'])==FILES
    return dict(schema='d5.i193-preparation-review.v1',increment='I193',date='2026-11-16',base_commit=BASE,
        status='CONCRETE_CUSTODY_EVIDENCE_PLAN_PREPARED_NOT_ADOPTED_NOT_EXECUTED_NOT_ADMITTED',
        plan=dict(path=PLAN,sha256=sha(PLAN)),checklist=dict(path=CHECK,sha256=sha(CHECK)),input_pins=761,prior_published_files_preserved=len(preserved),
        dependency_order=order,step_count=12,family_gate_count=8,contract_rule_gate_count=16,global_gate_count=7,
        prelaunch_antecedent_steps=sorted(closure('CE11')),receipt_not_a_prelaunch_prerequisite=True,
        artificial_receipt_cycle_rejected=True,provisional_actor_roster_before_final_freeze_C=True,
        complete_record_and_rule_coverage=True,prelaunch_family_count=7,receipt_family_deferred=True,
        no_dossiers_or_positive_external_records_created=True,no_people_assigned_or_appointments_accepted=True,
        actual_evidence_accepted_count=0,current_execution_authorized=False,
        provenance=dict(preparer='Same Codex assistant/chat; no real external custodian/reviewer appointed',actor_independent=False,organizationally_independent=False,independent_acceptance=False),
        current_effect=plan['current_effect'],decision=plan['decision'],E06=plan['E06'],work_unit=plan['work_unit'])


def main():
    review=build_review();assert rd(PREP)==review
    prior=rd(PRIOR_SEAL);preserved={**prior['preserved_published448'],**prior['artifacts'],PRIOR_SEAL:sha(PRIOR_SEAL)}
    seal=rd(SEAL);assert seal['schema']=='d5.i193-integrity.v1' and seal['base_commit']==BASE
    assert seal['preserved_published453']==preserved and set(seal['artifacts'])==FILES-{SEAL}
    for p,h in seal['artifacts'].items():assert sha(p)==h,p
    assert seal['source_only'] and seal['resource_obligations_closed']==0 and seal['IR03']=='NOT_READY'
    for k in ['independent_acceptance','product_or_components_executed','quotas_changed','rebind_applied','proposal_enabled','D5_closed']:assert seal[k] is False
    changed=set(git('diff',BASE,'--name-only').splitlines())|set(git('ls-files','--others','--exclude-standard').splitlines());assert changed==FILES,changed
    subprocess.check_call(['git','merge-base','--is-ancestor',BASE,'HEAD'],cwd=ROOT)
    if git('rev-parse','HEAD')!=BASE:assert not git('status','--porcelain')
    print(json.dumps(dict(status='PASS_STATIC_SOURCE_ONLY',increment='I193',planned_steps=12,record_families=8,contract_rules=16,global_gates=7,
        historical_pins=761,prior_published_files_preserved=453,new_files=6,actual_evidence_accepted=0,receipt_authorized=False,
        adopted=False,implemented=False,product_or_components_executed=0,quotas_changed=False,rebind_applied=False,
        resource_obligations_closed=0,proposal_enabled=False,F179_01_resolved=False,D5_closed=False,IR03='NOT_READY',git_head=git('rev-parse','HEAD')),sort_keys=True))

if __name__=='__main__':main()
