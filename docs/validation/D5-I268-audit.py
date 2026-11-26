#!/usr/bin/env python3
"""I268 A08/RQ08 documentary review; no target/component execution."""
import copy
import hashlib
import io
import json
from pathlib import Path
import runpy
import subprocess

ROOT = Path(__file__).resolve().parents[2]
P = 'docs/validation/'
BASE = '7409c0268dbaa617a31b01d41bfdd20db57288fc'
DATE = '2026-11-26'
PLAN = P+'D5-I223-PRELAUNCH-RESOURCE-CLOSURE-PLAN.json'
ACQUISITION = P+'D5-I251-GENUINE-EVIDENCE-ACQUISITION-PLAN.json'
W13 = P+'D5-I223-W13-PRELAUNCH-GATE-DECISION-CANDIDATE.json'
A07 = P+'D5-I251-A07-RQ07-FINAL-CUSTODY-MAPPING-CANDIDATE.json'
SUBJECT = P+'D5-I251-A08-RQ08-GENUINE-PRELAUNCH-GATE-DECISION-CANDIDATE.json'
PRIOR_PREP = P+'D5-I267-preparation-review.json'
PRIOR_AUDIT = P+'D5-I267-audit.py'
PRIOR_SEAL = P+'D5-I267-integrity.json'
PRIOR_DOC = 'docs/design/D5-I267-A08-RQ08-GENUINE-PRELAUNCH-GATE-DECISION.md'
PRIOR_FILES = {SUBJECT,PRIOR_PREP,PRIOR_AUDIT,PRIOR_SEAL,PRIOR_DOC}
RECON = P+'D5-I268-I267-source-reconstruction.json'
REVIEW = P+'D5-I268-I267-documentary-review.json'
AUDIT = P+'D5-I268-audit.py'
SEAL = P+'D5-I268-integrity.json'
DOC = 'docs/design/D5-I268-I267-A08-RQ08-REVIEW.md'
FILES = {RECON,REVIEW,AUDIT,SEAL,DOC}
STATUS = 'PASS_STATIC_SOURCE_ONLY_A08_RQ08_REVIEW_GENUINE_GATE_RESOURCE_AND_INDEPENDENT_DECISIONS_PENDING_NOT_ADMITTED'


def rd(path):
    return json.loads((ROOT/path).read_text())


def sha(path):
    return hashlib.sha256((ROOT/path).read_bytes()).hexdigest()


def git(*args):
    return subprocess.check_output(['git', *args], cwd=ROOT, text=True).strip()


def pin(path, pointer=''):
    return dict(path=path, sha256=sha(path), json_pointer=pointer)


def fragment(ref):
    assert sha(ref['path']) == ref['sha256'], ref['path']
    value = rd(ref['path'])
    for token in ref.get('json_pointer','').split('/')[1:]:
        key = token.replace('~1','/').replace('~0','~')
        value = value[int(key)] if isinstance(value,list) else value[key]
    return value


def pointers(node):
    if isinstance(node,dict):
        if {'path','sha256','json_pointer'} <= set(node):
            fragment(node)
        for value in node.values():
            pointers(value)
    elif isinstance(node,list):
        for value in node:
            pointers(value)


def verify_blobs(pins):
    stream = io.BytesIO(subprocess.check_output(['git','cat-file','--batch'], cwd=ROOT,
        input=''.join(BASE+':'+path+'\n' for path in sorted(pins)).encode()))
    for path,digest in sorted(pins.items()):
        header = stream.readline().decode().split()
        assert len(header)==3 and header[1]=='blob', path
        body = stream.read(int(header[2]))
        assert stream.read(1)==b'\n' and hashlib.sha256(body).hexdigest()==digest==sha(path), path
    assert not stream.read()


def missing(row, false_fields=()):
    for key,value in row.items():
        if key.startswith('actual_'):
            assert value is False if key in false_fields else value is None,key
    if 'accepted' in row:
        assert row['accepted'] is False


def truth(row, names):
    for name in names:
        assert row[name] is True,name


# Review coverage is specified separately from the preparation generator.
SECTIONS = 'dependency_gate package_dependency_requirements role_scope_matrix competent_decision_boundary thirty_gate_disposition_ledger deferred_receipt_gate disposition_summary E01_E05_disposition_ledger twenty_criterion_disposition_ledger joint_resource_decision_boundary proof_reference_disposition additional_proof_requirement_ledger stop_requirement_ledger deferred_handoff CE12_boundary final_binding_requirement_ledger source_resource_and_invalidation_boundary non_admission_record authority_boundary exit_predicate_dispositions preserved_scope_and_gates'.split()
RETURN_SECTIONS = [
'dependency_gate package_dependency_requirements role_scope_matrix competent_decision_boundary',
'thirty_gate_disposition_ledger disposition_summary competent_decision_boundary',
'E01_E05_disposition_ledger twenty_criterion_disposition_ledger joint_resource_decision_boundary source_resource_and_invalidation_boundary',
'proof_reference_disposition additional_proof_requirement_ledger final_binding_requirement_ledger source_resource_and_invalidation_boundary',
'role_scope_matrix competent_decision_boundary disposition_summary joint_resource_decision_boundary non_admission_record',
'deferred_receipt_gate deferred_handoff CE12_boundary non_admission_record authority_boundary',
'stop_requirement_ledger source_resource_and_invalidation_boundary authority_boundary preserved_scope_and_gates']
AC_RETURNS = [['GD01'],['GD01','GD05'],['GD01','GD03'],['GD02'],['GD02','GD04'],['GD02','GD05'],['GD03'],['GD03','GD05'],['GD03'],['GD03','GD04'],['GD04'],['GD04','GD06'],['GD03','GD04'],['GD02','GD03','GD05'],['GD06'],['GD06'],['GD06'],['GD07'],['GD01','GD07'],['GD05','GD06','GD07']]


def inspect(d):
    plan,acq,w=rd(PLAN),rd(ACQUISITION),rd(W13);lot=acq['acquisition_lots'][7];req=plan['work_packages'][12]
    assert (d['lot_id'],d['request_id'],d['work_package'],d['planned_deliverable_id'])==('A08','RQ08','W13',req['deliverable_id'])
    assert d['exact_acquisition_lot']==fragment(d['acquisition_lot_binding'])==lot
    assert d['exact_W13_requirement']==fragment(d['W13_requirement_binding'])==req
    assert d['W13_documentary_checklist']==pin(W13)
    gate=d['dependency_gate'];lots=['A%02d'%i for i in range(1,8)];works=['W%02d'%i for i in range(1,13)]
    assert gate['required_lot_ids']==lot['depends_on_lots']==lots
    assert gate['required_external_work_package_ids']==req['depends_on']==works
    assert gate['actual_lot_acceptances']=={x:False for x in lots}
    assert gate['exact_prior_effect']==fragment(gate['A07_state_source'])==rd(A07)['current_effect']
    assert gate['actual_genuine_antecedent_acceptance_bodies'] is None
    truth(gate,['SD01_stop_active','no_documentary_PASS_as_genuine_antecedent','no_send_contact_positive_intake_or_gate_resource_decision_from_preparation'])
    draft=d['unsent_request'];assert draft['original_draft']==lot['unsent_request_draft'] and draft['recipient_role_only']==lot['intended_recipient_role_kind']
    assert draft['is_draft_only'] is True and draft['sent'] is False and draft['contact_authorized'] is False;missing(draft)
    inherited=d['inherited_W13_requirements'];assert [x['section'] for x in inherited]==SECTIONS
    for row,s in zip(inherited,SECTIONS):
        assert row['source']==pin(W13,'/'+s) and fragment(row['source'])==w[s]
        assert row['documentary_container_dimension']==len(w[s]) and row['dimension_not_actual_bodies_proofs_fit_or_acceptance'] is True;missing(row)
    requests=d['gate_decision_requests'];expected_ids=['FAMILY-'+x for x in ['ANCHOR_REGISTRY','ACTOR_REGISTRY','IMAGE_MANIFEST','CALLER_IDENTITY','PLATFORM_CUSTODY','ACCEPTANCE_RECORD','CUSTODY_BUNDLE']]+['RULE-K%02d'%i for i in range(1,17)]+['G%02d'%i for i in range(1,8)]
    assert [x['id'] for x in requests]==expected_ids
    categories={'FAMILY':0,'RULE':0,'GLOBAL':0};own_outputs=[]
    for i,row in enumerate(requests):
        src=w['thirty_gate_disposition_ledger'][i];pg=plan['gate_closure_matrix'][i];cg=acq['gate_to_collection_matrix'][i]
        assert row['W13_gate_source']==pin(W13,'/thirty_gate_disposition_ledger/'+str(i)) and fragment(row['W13_gate_source'])==src
        assert row['plan_gate_source']==src['source'] and fragment(row['plan_gate_source'])==src['exact_plan_gate']==pg
        assert row['collection_source']==pin(ACQUISITION,'/gate_to_collection_matrix/'+str(i)) and fragment(row['collection_source'])==cg
        assert row['id']==src['id']==pg['id']==cg['id'] and row['category']==src['category']==pg['category']==cg['category']
        categories[row['category']]+=1
        assert row['exact_requirement']==pg['exact_requirement'] and row['close_only_if']==pg['close_only_if']==cg['exact_close_only_if']
        assert row['required_collection_lots']==cg['required_collection_lots']
        producers=pg['producer_work_package_ids'];assert row['producer_work_package_ids']==cg['required_work_package_ids']==producers
        assert row['genuine_accepted_external_work_package_ids']==[x for x in producers if x!='W13']
        assert row['W13_producer_is_decision_output_not_accepted_self_predecessor']==('W13' in producers)
        if 'W13' in producers:own_outputs.append(row['id'])
        assert row['primary_review_roles']==pg['primary_review_roles']==['R06'] and row['separate_acceptor_role']==pg['separate_acceptor_role']=='R08'
        assert row['required_return_ids']==['GD02','GD04','GD05'] and row['allowed_future_dispositions']==['ACCEPTED','REJECTED','PENDING']
        assert row['current_disposition']=='PENDING_GENUINE_ANTECEDENTS_EVIDENCE_AND_INDEPENDENT_DECISIONS'
        assert all(row[k] is False for k in ['accepted','rejected','closed','execution_authorized'])
        missing(row,['actual_condition_verified'])
    assert categories==dict(FAMILY=7,RULE=16,GLOBAL=7)
    assert own_outputs==['RULE-K12','RULE-K13','RULE-K16']+['G%02d'%i for i in range(1,8)]
    obligations=d['resource_decision_requests'];assert [x['id'] for x in obligations]==['E%02d'%i for i in range(1,6)]
    for i,row in enumerate(obligations):
        src=w['E01_E05_disposition_ledger'][i]
        assert row['source']==pin(W13,'/E01_E05_disposition_ledger/'+str(i)) and fragment(row['source'])==src
        assert row['exact_plan_requirement']==src['exact_plan_requirement']==plan['resource_obligation_matrix'][i]
        assert row['criterion_ids']==[row['id']+'-R%d'%j for j in range(1,5)]
        assert row['primary_review_roles']==row['exact_plan_requirement']['primary_review_roles']==['R03','R06']
        assert row['separate_acceptor_role']=='R08' and row['required_return_ids']==['GD03','GD05'] and row['closed'] is False;missing(row)
    criteria=d['resource_criterion_requests'];criterion_ids=[o['id']+'-R%d'%j for o in obligations for j in range(1,5)]
    assert [x['id'] for x in criteria]==criterion_ids
    for i,row in enumerate(criteria):
        src=w['twenty_criterion_disposition_ledger'][i]
        assert row['source']==pin(W13,'/twenty_criterion_disposition_ledger/'+str(i)) and fragment(row['source'])==src
        assert row['exact_plan_requirement']==src['exact_plan_requirement']==plan['resource_criterion_matrix'][i]
        assert row['obligation']==src['obligation'] and row['required_return_ids']==['GD03','GD05']
        assert row['current_disposition']=='PENDING_NOT_TRANSFERRED_FROM_HISTORICAL_RESULT' and row['closes_resource_obligation'] is False;missing(row)
    roles=d['role_evidence_requests'];assert [x['id'] for x in roles]==['R06','R08']
    for i,row in enumerate(roles):
        assert row['exact_requirement']==fragment(row['source'])==w['role_scope_matrix'][i] and row['required_return_ids']==['GD01','GD05'];missing(row)
    identity=w['competent_decision_boundary'];assert len(identity['exact_separation_matrix'])==14
    truth(identity,['genuine_canonical_humans_competence_appointments_independence_all_preparers_and_exclusions_required','same_assistant_documentary_review_not_actual_R06_or_R08_decision','W13_named_producer_means_review_output_not_own_accepted_predecessor_or_self_authorization'])
    assert len(d['critical_boundaries'])==18 and all(v is True for v in d['critical_boundaries'].values())
    returns=d['requested_returns'];return_ids=['GD%02d'%i for i in range(1,8)]
    assert [x['id'] for x in returns]==draft['required_return_ids']==return_ids
    for row,sections in zip(returns,RETURN_SECTIONS):
        assert row['requirements'] and row['W13_requirement_sources']==[pin(W13,'/'+s) for s in sections.split()]
        assert fragment(row['universal_delivery_source'])==acq['evidence_delivery_contract'];missing(row,['actual_received'])
    intake=d['acceptance_checklist'];intake_ids=['AC%02d'%i for i in range(1,21)];assert [x['id'] for x in intake]==intake_ids
    for row,ids in zip(intake,AC_RETURNS):
        assert row['criterion'] and row['required_return_ids']==ids and row['disposition']=='PENDING_ALL_PREDECESSORS_GENUINE_GATE_RESOURCE_AND_INDEPENDENT_DECISIONS';missing(row)
    delivers=d['deliverable_coverage'];assert [x['id'] for x in delivers]==['WD%02d'%i for i in range(1,5)]
    for i,row in enumerate(delivers):
        assert row['exact_requirement']==fragment(row['source'])==req['deliverables'][i]
        assert row['required_return_ids']==[['GD02','GD04','GD05'],['GD03','GD05'],['GD06'],['GD05','GD06','GD07']][i];missing(row)
    exits=d['exit_coverage'];assert [x['id'] for x in exits]==['WX%02d'%i for i in range(1,4)]
    for i,row in enumerate(exits):
        assert row['exact_predicate']==fragment(row['source'])==req['exit_predicates'][i] and row['required_intake_criteria']==intake_ids;missing(row)
    ref=w['proof_reference_disposition'];assert ref['static_template_count']==69 and len(w['additional_proof_requirement_ledger'])==8
    assert len(w['final_binding_requirement_ledger'])==4 and len(w['stop_requirement_ledger'])==8
    truth(ref,['template_paths_arrays_and_repeated_nested_records_not_actual_unique_body_count','all_actual_missing_provided_rejected_references_require_immutable_locator_hash_bytes_authors_providers_custody_scope_review_and_disposition','absence_of_actual_rejection_not_acceptance'])
    routes=d['material_routes'];assert routes['existing_material']['required_returns']==return_ids[:-1];missing(routes['existing_material'],['actual_route_accepted'])
    gap=routes['missing_material'];assert gap['required_return_id']=='GD07';truth(gap,['SD01_SD08_stop_rules_preserved','gap_not_acceptance_or_global_infeasibility','separate_exact_work_authority_required']);missing(gap,['actual_work_performed'])
    material=d['actual_material_state'];assert material['provided_real_bodies']==material['rejected_real_bodies']==[] and type(material['actual_evaluations']) is int and material['actual_evaluations']==0
    missing({k:v for k,v in material.items() if k!='actual_evaluations'},['actual_positive_review_or_acceptance_records_created','actual_operational_verification_execution_signing_configuration_or_probe_performed'])
    resource=d['preserved_resource_rules'];assert resource['exact_requirement']==fragment(resource['source'])==acq['preserved_resource_and_cost_rules'];truth(resource,['no_quota_budget_reserve_transfer_or_resource_reservation_applied'])
    hand=d['handoff']
    for sourcekey,valuekey,section in [('source','exact_requirement','deferred_handoff'),('CE12_source','exact_CE12_requirement','CE12_boundary'),('receipt_source','exact_receipt_requirement','deferred_receipt_gate')]:
        assert hand[sourcekey]==pin(W13,'/'+section) and hand[valuekey]==fragment(hand[sourcekey])==w[section]
    receipt=hand['exact_receipt_requirement'];assert receipt['id']=='FAMILY-LAUNCH_RECEIPT' and receipt['excluded_from30_prelaunch_targets'] is True and receipt['current_status']=='DEFERRED_NOT_AUTHORIZED'
    ce12=hand['exact_CE12_requirement'];assert len(ce12['preclaim_external_prerequisites'])==4 and len(ce12['receipt_only_external_prerequisites'])==1
    assert ce12['actual_claim_spawn_receipt_or_final_route_completion_required_to_close_prelaunch'] is False
    truth(ce12,['claim_not_own_precondition_and_after_full_root_admission_before_paths_spawn','uncertain_partial_expired_failed_claim_no_free_retry_or_invocation_reuse','receipt_private_not_capture_output_or_new_wire_field'])
    assert hand['exact_A08_completion_predicate']==lot['completion_predicate'] and hand['exact_A08_missing_stop']==lot['missing_or_failure_stop']
    assert hand['current_run_command'] is None;truth(hand,['no_new_lot_or_automatic_release_created','final_route_requires_separate_exact_authority']);missing(hand,['actual_final_route_Q_root_claim_spawn_receipt_created'])
    change=d['change_control'];assert change['exact_requirement']==fragment(change['source'])==w['source_resource_and_invalidation_boundary']
    truth(change,['changed_material_invalidates_affected_A01_A08_before_progress','no_automatic_prior_hash_proof_approval_mapping_or_acceptance_transfer']);missing(change,['actual_refresh_or_active_rebind'])
    assert d['current_effect']=={**rd(A07)['current_effect'],'A08_RQ08_documentary_prepared':True,'A08_accepted':False,'RQ08_sent':False,'actual_genuine_prelaunch_gate_resource_or_aggregate_decisions_created':False,'actual_A08_intake_progress_or_review_records_created':False}
    assert all(d['producer'][k] is False for k in ['actor_independent','competent_R03_R06_review','separate_R08_acceptance','external_contacts_made'])
    pointers(d)
    return dict(gate_ids=expected_ids,gate_categories=categories,W13_decision_output_not_accepted_predecessor_ids=own_outputs,required_lots=lots,required_external_work_packages=works,
        obligation_criterion_join={r['id']:r['criterion_ids'] for r in obligations},gate_review_roles=['R06','R08'],W09_review_roles=['R03','R06','R08'],resource_and_intake_criteria_distinct=True,
        receipt_excluded_from30=True,preclaim_external_requirements=4,claim_construction_requirement_before_receipt=1,actual_gate_or_resource_decisions=0,actual_acceptances=0)

CRITERIA = [
'A08/RQ08 exact I251/W13 scope retains seven genuine lots and twelve external work predecessors,all unaccepted with SD01 active.',
'Unsent conditional draft grants no contact,nomination,positive intake,decision or independent authority.',
'Thirty exact ordered IDs cover seven families,sixteen rules and seven global conditions; no receipt gate included.',
'Every W13/I223/I251 gate link retains exact requirement and all close_only_if predicates.',
'Producers,collection lots and genuine accepted external work are exact; W13 outputs are not own accepted predecessors.',
'Each gate retains complete body/bytes/hash/locator/source/runtime/scope/authorship/custody/validity and derivation requirements.',
'All current gates are pending,unverified,unaccepted,not rejected,not closed and not authorized for execution.',
'Future gate dispositions accepted/rejected/pending require genuine traceable R06 review and separate R08 acceptance.',
'Gate dispositions differ from I251 material-intake states; no provided body is silently accepted.',
'W13 R06/R08 roles retain canonical humans,competence,appointments,all preparers and fourteen human/key separations.',
'R08 remains separate from R01/R02; qualified R01/R02 overlap retains independent role-domain approvals without blanket prohibition.',
'Five E01-E05 obligations each retain four exact resource criteria and genuine W09 R03/R06 and R08 decisions.',
'Twenty resource criteria retain exact successor revalidation without historical result transfer or self closure.',
'Twenty request-intake criteria are separate from twenty resource criteria and preserve seven-return coverage.',
'Joint scope must reconcile all accepted final source/runtime/image/caller/platform/epoch/policy/units/assumptions/caps/guards.',
'Full11 heap/lifetimes/allocator/native,30 successor work,WCET/CPU/IO/service/clock/phases/atomicity/BASIS/index/900 remain unproved.',
'Budgets/reserves are not capacity/service; unknown not zero,CPU sum not wall,watchdog not success,conditional221644/40500 not fit.',
'Both Readers and global lookup/freshness/identity/crypto/native/IO/copies/registry/ledger/receipt/output/failure costs remain included.',
'Sixty-nine templates with arrays/repeated nested records are not actual unique bodies or complete reference inventory.',
'All missing/provided/rejected reference bodies retain immutable availability/provenance/currentness/scope and decisions; no rejection is not acceptance.',
'Eight additional proof requirements,four bindings and eight stop rules retain exact W13 phase/authority requirements.',
'Seven returns and21 complete source sections retain full documentary requirements without new runtime schemas or hidden work.',
'Four deliverables and three exits retain I223 requirements and complete intake-criterion coverage.',
'Genuine aggregate acceptance requires all30 gates and E01-E05/20 same-scope compatible evidence,no partial positive.',
'W09 baseline facts/authors authenticate before resource acceptance; W10 finalizes same facts without retrospective or forecast authority.',
'Changed material invalidates any affected A01-A08 and forces requalification before progress,no automatic proof/hash/approval/mapping transfer.',
'SD01-SD08 missing-material route retains negative/pending no admission with separate exact authority and no inferred global infeasibility.',
'Private launch receipt remains excluded31st deferred unauthorized disposition and never new CE11/prelaunch prerequisite.',
'Four genuine external prerequisites before claim and actual claim/protected construction fifth before receipt remain distinct.',
'Claim follows full admission before paths/spawn,not own precondition; uncertain/partial/expired/failed no free retry/reuse.',
'Handoff X09 carries pending obligations,no current command,actual accepted handoff,new lot or automatic final-route authorization.',
'Custody/resource acceptance and publication grant no execution,certificate,PJC115-R2 or D5 closure; all negative state and quotas preserved.'
]


def reconstruct():
    d=rd(SUBJECT);result=inspect(d);pins={**d['input_pins'],**{p:sha(p) for p in PRIOR_FILES}}
    assert len(pins)==1137;verify_blobs(pins)
    return dict(schema='d5.i268-source-reconstruction.v1',increment='I268',date=DATE,timezone='Europe/Madrid',base_commit=BASE,subject=pin(SUBJECT),input_pins=pins,
        independent_reconstruction=result,criteria=[dict(id='RV%02d'%(i+1),criterion=t,result='PASS_DOCUMENTARY_REQUIREMENT_ONLY') for i,t in enumerate(CRITERIA)],
        current_effect={**d['current_effect'],'A08_RQ08_documentary_reviewed':True})


def own_rejections(d):
    cases=[
('lot_missing',('dependency_gate','required_lot_ids'),['A07']),('work_missing',('dependency_gate','required_external_work_package_ids'),['W12']),
('A06_promoted',('dependency_gate','actual_lot_acceptances','A06'),True),('request_return',('unsent_request','required_return_ids'),['GD01']),
('section_missing',('inherited_W13_requirements',),d['inherited_W13_requirements'][:-1]),('dimension_as_fit',('inherited_W13_requirements',0,'dimension_not_actual_bodies_proofs_fit_or_acceptance'),False),
('gate_missing',('gate_decision_requests',),d['gate_decision_requests'][:-1]),('gate_duplicate',('gate_decision_requests',29,'id'),'G06'),
('category_changed',('gate_decision_requests',0,'category'),'GLOBAL'),('gate_pointer',('gate_decision_requests',0,'W13_gate_source','json_pointer'),'/thirty_gate_disposition_ledger/1'),
('close_if_removed',('gate_decision_requests',0,'close_only_if'),[]),('collection_lot',('gate_decision_requests',0,'required_collection_lots'),['A08']),
('producer_missing',('gate_decision_requests',0,'producer_work_package_ids'),[]),('self_predecessor',('gate_decision_requests',29,'genuine_accepted_external_work_package_ids'),['W01','W09','W13']),
('self_output_flag',('gate_decision_requests',29,'W13_producer_is_decision_output_not_accepted_self_predecessor'),False),
('reviewer_replaced',('gate_decision_requests',0,'primary_review_roles'),['R03']),('R08_replaced',('gate_decision_requests',0,'separate_acceptor_role'),'R06'),
('gate_disposition',('gate_decision_requests',0,'current_disposition'),'ACCEPTED'),('future_pending_removed',('gate_decision_requests',0,'allowed_future_dispositions'),['ACCEPTED','REJECTED']),
('obligation_missing',('resource_decision_requests',),d['resource_decision_requests'][:-1]),('criterion_join_missing',('resource_decision_requests',4,'criterion_ids'),['E05-R1']),
('W09_reviewer_removed',('resource_decision_requests',0,'primary_review_roles'),['R06']),('resource_criterion_missing',('resource_criterion_requests',),d['resource_criterion_requests'][:-1]),
('criterion_misassigned',('resource_criterion_requests',0,'obligation'),'E02'),('historic_promoted',('resource_criterion_requests',0,'current_disposition'),'ACCEPTED_FROM_HISTORY'),
('role_missing',('role_evidence_requests',),d['role_evidence_requests'][:-1]),('return_missing',('requested_returns',),d['requested_returns'][:-1]),
('return_scope_missing',('requested_returns',2,'W13_requirement_sources'),[]),('intake_missing',('acceptance_checklist',),d['acceptance_checklist'][:-1]),
('intake_return_changed',('acceptance_checklist',13,'required_return_ids'),['GD05']),('deliverable_missing',('deliverable_coverage',),d['deliverable_coverage'][:-1]),
('handoff_return_removed',('deliverable_coverage',2,'required_return_ids'),['GD05']),('exit_missing',('exit_coverage',),d['exit_coverage'][:-1]),
('exit_criteria',('exit_coverage',0,'required_intake_criteria'),['AC01']),('receipt_in30',('handoff','exact_receipt_requirement','excluded_from30_prelaunch_targets'),False),
('claim_as_own_condition',('handoff','exact_CE12_requirement','claim_not_own_precondition_and_after_full_root_admission_before_paths_spawn'),False),
('receipt_precondition',('handoff','exact_CE12_requirement','actual_claim_spawn_receipt_or_final_route_completion_required_to_close_prelaunch'),True),
('work_authority',('material_routes','missing_material','separate_exact_work_authority_required'),False),('invalidation_removed',('change_control','changed_material_invalidates_affected_A01_A08_before_progress'),False),
('assistant_R08',('producer','separate_R08_acceptance'),True)]
    results=[]
    for name,path,value in cases:
        mutant=copy.deepcopy(d);node=mutant
        for key in path[:-1]:node=node[key]
        node[path[-1]]=value
        try:inspect(mutant)
        except AssertionError:results.append(dict(case=name,result='REJECTED_DOCUMENTARY_MUTATION_IN_MEMORY'))
        else:raise AssertionError(name)
    return results


def build_review(rec):
    previous=runpy.run_path(str(ROOT/PRIOR_AUDIT));exists=Path.exists
    assert previous['build_candidate']()==rd(SUBJECT)
    prep=previous['build_review']();assert prep==rd(PRIOR_PREP) and Path.exists is exists
    return dict(schema='d5.i268-documentary-review.v1',increment='I268',date=DATE,timezone='Europe/Madrid',base_commit=BASE,status=STATUS,
        subject=pin(SUBJECT),reconstruction=pin(RECON),verdict='NO_NEW_DOCUMENTARY_DEFECT_FOUND_GENUINE_PRELAUNCH_GATE_RESOURCE_AND_INDEPENDENT_DECISIONS_PENDING',findings=[],
        criteria=rec['criteria'],independent_reconstruction=rec['independent_reconstruction'],
        counts=dict(input_pins=1137,preserved_published_files=829,gate_requests=30,families=7,rules=16,global_conditions=7,obligations=5,resource_criteria=20,intake_criteria=20,
            W13_review_roles=2,W09_review_roles=3,separation_requirements=14,reference_templates=69,additional_proof_requirements=8,final_bindings=4,stop_rules=8,
            source_sections=21,requested_returns=7,deliverables=4,exits=3,review_criteria=len(CRITERIA),actual_received_bodies=0,actual_genuine_decisions=0,actual_lots_accepted=0,prelaunch_gates_closed=0,resource_obligations_closed=0),
        inherited_I267_rejection_checks=prep['rejection_checks'],additional_I268_rejection_checks=own_rejections(rd(SUBJECT)),
        clarifications=[
            'Future gate dispositions ACCEPTED/REJECTED/PENDING describe gate decisions. I251 material intake MISSING/PROVIDED_NOT_ACCEPTED/REJECTED_WITH_TRACEABLE_REASON/ACCEPTED_ONLY_BY_GENUINE_AUTHORIZED_ROLES describes evidence handling; no new wire enum or silent intake acceptance follows.',
            'W13 is named as producer for10 gate decision outputs,not a genuine accepted predecessor of itself. All required external W01-W12 and A01-A07 remain unaccepted,SD01 active,RQ08 unsent.',
            'W13 R06/R08 decisions do not substitute W09 R03/R06/R08 reviews. Twenty resource criteria and20 request-intake criteria are distinct; all5 obligations remain open.',
            'Historical rule K12 wording about acceptance binding a digest is an evidence-order reference. Selected W11/W12 and A07 boundaries retain acceptance without standalone signature,complete C digest and three approvals of the same complete core; no signature or record is issued here.',
            'All30 gates require genuine same-scope full bodies/derivations/currentness/caps/custody and independent competent decisions.69 templates are not actual unique body count; document/hash/schema/presence/signature/budget alone does not prove truth or fit.',
            'Four final binding obligations keep their own phase and separate authority. No final E06/payload/Q/root/admission/claim/spawn/receipt or final-route completion becomes a new CE11/prelaunch antecedent.',
            'CE12 remains private deferred unauthorized31st disposition; four external preclaim prerequisites and fifth actual claim/protected construction before receipt remain separate,no claim self-precondition or free retry.',
            'Handoff X09 transfers pending obligations only,no command,new lot,automatic certificate/PJC115-R2/execution or D5 release. Missing/change keeps negative state and requires affected requalification under exact separate authority.'],
        source_reconstruction=dict(primary_source_checks=True,I267_candidate_and_preparation_reproduced=True,prior_publication_mains_called=False,prior_Path_exists_restored=True,no_new_presence_projection=True),
        current_effect=rec['current_effect'],provenance=dict(identity='Same Codex assistant/chat as I267',documentary_review_only=True,actor_independent=False,competent_R03_R06_review=False,separate_R08_acceptance=False,external_contacts_made=False),
        limitations=['A01-A08 and W01-W13 remain genuinely unaccepted,SD01 active,RQ08 unsent. No evidence or independent primary/separate gate/resource/aggregate decision has been supplied.',
            'Thirty gates,E01-E05 and all20 resource criteria remain pending. Documentary reconstruction and negative checks prove no authentic custody,global mapping,heap/CPU/service/900 bound or independent acceptance.',
            'No product/component execution,positive crypto/signing/keygen,enrollment,contacts,configuration,probes,quota/reserve/authority/destination/active binding/certificate change. CE12 and final execution remain separately deferred.'],
        work_unit=dict(rollback_files=sorted(FILES),verification_command='python3 docs/validation/D5-I268-audit.py',expected_result=STATUS,over400_lines=True,
            reason='One A08/RQ08 documentary review with primary-source gate/criterion joins,source pins,negative checks and preservation; overage declared,no PR requested.',
            runtime_harness='N/A: own documentary JSON/Git/hash/pointer/coverage/graph checks and in-memory mutations only; no target import,compile,discovery,tests,execution,build,benchmark,codec,crypto,signing,keygen,enrollment,contacts,provision,configuration or platform/clock/CPU/IO/ledger/process/endpoint/replay/crash/restart probes.'),
        publication=dict(commit_and_push_requested=True,publication_not_genuine_review_acceptance_authority_execution_or_D5_closure=True))


def main():
    rec=reconstruct();assert rec==rd(RECON)
    review=build_review(rec);assert review==rd(REVIEW)
    prior=rd(PRIOR_SEAL);preserved={**prior['preserved_published824'],**prior['artifacts'],PRIOR_SEAL:sha(PRIOR_SEAL)};assert len(preserved)==829
    seal=rd(SEAL);assert seal['schema']=='d5.i268-integrity.v1' and seal['base_commit']==BASE
    assert seal['preserved_published829']==preserved and set(seal['artifacts'])==FILES-{SEAL}
    for mapping in [preserved,seal['artifacts']]:
        for p,h in mapping.items():assert sha(p)==h,p
    assert seal['source_only'] is True and seal['current_effect']==rec['current_effect']
    changed=set(git('diff',BASE,'--name-only').splitlines())|set(git('ls-files','--others','--exclude-standard').splitlines());assert changed==FILES,changed
    subprocess.check_call(['git','merge-base','--is-ancestor',BASE,'HEAD'],cwd=ROOT)
    if git('rev-parse','HEAD')!=BASE:assert not git('status','--porcelain')
    print(json.dumps(dict(status=STATUS,input_pins=1137,preserved_published_files=829,new_files=5,review_criteria=len(CRITERIA),inherited_rejections=len(review['inherited_I267_rejection_checks']),additional_rejections=len(review['additional_I268_rejection_checks']),findings=review['findings'],prelaunch_gates_closed=0,resource_obligations_closed=0,D5_closed=False),sort_keys=True))


if __name__=='__main__':main()
