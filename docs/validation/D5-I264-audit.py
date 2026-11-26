#!/usr/bin/env python3
"""I264 A06/RQ06 documentary review; no target/component execution."""
import copy
import hashlib
import io
import json
from pathlib import Path
import runpy
import subprocess

ROOT = Path(__file__).resolve().parents[2]
P = 'docs/validation/'
BASE = '4fa99b1a3178d96faa74efaa3d3f1a11ac3904a7'
DATE = '2026-11-26'
PLAN = P+'D5-I223-PRELAUNCH-RESOURCE-CLOSURE-PLAN.json'
ACQUISITION = P+'D5-I251-GENUINE-EVIDENCE-ACQUISITION-PLAN.json'
W09 = P+'D5-I223-W09-E01-E05-INTEGRATION-CANDIDATE.json'
A05 = P+'D5-I251-A05-RQ05-REQUALIFICATION-COMPLETE-BOUNDS-CANDIDATE.json'
SUBJECT = P+'D5-I251-A06-RQ06-INDEPENDENT-RESOURCE-JOIN-CANDIDATE.json'
PRIOR_PREP = P+'D5-I263-preparation-review.json'
PRIOR_AUDIT = P+'D5-I263-audit.py'
PRIOR_SEAL = P+'D5-I263-integrity.json'
PRIOR_DOC = 'docs/design/D5-I263-A06-RQ06-INDEPENDENT-RESOURCE-JOIN.md'
PRIOR_FILES = {SUBJECT,PRIOR_PREP,PRIOR_AUDIT,PRIOR_SEAL,PRIOR_DOC}
RECON = P+'D5-I264-I263-source-reconstruction.json'
REVIEW = P+'D5-I264-I263-documentary-review.json'
AUDIT = P+'D5-I264-audit.py'
SEAL = P+'D5-I264-integrity.json'
DOC = 'docs/design/D5-I264-I263-A06-RQ06-REVIEW.md'
FILES = {RECON,REVIEW,AUDIT,SEAL,DOC}
STATUS = 'PASS_STATIC_SOURCE_ONLY_A06_RQ06_REVIEW_PREDECESSORS_COMPLETE_PROOFS_AND_INDEPENDENT_JOIN_DECISIONS_PENDING_NOT_ADMITTED'


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


RETURN_SECTIONS = [
    ['dependency_gate','role_scope_matrix','role_and_identity_boundary','phase_handoff'],
    ['resource_obligation_ledger','criterion_revalidation_ledger','resource_premise_handoff'],
    ['prior_proof_boundary','profile_proof_requirements','contract_rule_requirements'],
    ['resource_premise_handoff','resource_and_reserve_boundary','profile_proof_requirements'],
    ['role_and_identity_boundary','exit_predicate_dispositions','authority_boundary'],
    ['evidence_package_requirements','resource_premise_handoff','final_binding_boundary','authority_boundary'],
    ['resource_obligation_ledger','prior_proof_boundary','phase_handoff','authority_boundary']]
AC_RETURNS = [['RJ01'],['RJ01','RJ05'],['RJ02'],['RJ02','RJ04'],['RJ02','RJ04'],['RJ03'],['RJ03','RJ05'],['RJ03','RJ06'],
    ['RJ04'],['RJ04'],['RJ01','RJ05'],['RJ02','RJ05'],['RJ06'],['RJ01','RJ04','RJ06'],['RJ07'],['RJ05','RJ07']]


def inspect(d):
    plan,acq,w=rd(PLAN),rd(ACQUISITION),rd(W09);lot,req=acq['acquisition_lots'][5],plan['work_packages'][8]
    assert (d['lot_id'],d['request_id'],d['work_package'],d['planned_deliverable_id'])==('A06','RQ06','W09',req['deliverable_id'])
    assert d['exact_acquisition_lot']==fragment(d['acquisition_lot_binding'])==lot
    assert d['exact_W09_requirement']==fragment(d['W09_requirement_binding'])==req
    assert d['W09_documentary_checklist']['path']==W09
    gate=d['dependency_gate']
    assert gate['required_lot_ids']==lot['depends_on_lots']==['A02','A03','A04','A05']
    assert gate['required_work_package_ids']==req['depends_on']==['W%02d'%i for i in range(2,9)]
    assert gate['exact_requirement']==fragment(gate['source'])==w['dependency_gate']
    assert gate['exact_prior_effect']==fragment(gate['A05_state_source'])==rd(A05)['current_effect']
    assert all(gate[key] is False for key in ['A01_accepted','A02_accepted','A03_accepted','A04_accepted','A05_accepted'])
    truth(gate,['SD01_stop_active','no_documentary_PASS_as_genuine_antecedent','no_send_contact_nomination_positive_intake_or_real_joint_decision_from_this_preparation'])
    missing(gate)
    draft=d['unsent_request']
    assert draft['original_draft']==lot['unsent_request_draft'] and draft['recipient_role_only']==lot['intended_recipient_role_kind']
    assert draft['required_return_ids']==['RJ%02d'%i for i in range(1,8)]
    assert draft['is_draft_only'] is True and draft['sent'] is False and draft['contact_authorized'] is False
    missing(draft)
    returns=d['requested_returns'];assert [r['id'] for r in returns]==draft['required_return_ids']
    for row,sections in zip(returns,RETURN_SECTIONS):
        assert row['requirements'] and row['W09_requirement_sources']==[pin(W09,'/'+key) for key in sections]
        assert fragment(row['universal_delivery_source'])==acq['evidence_delivery_contract']
        missing(row,['actual_received'])
    roles=d['role_evidence_requests'];assert [r['id'] for r in roles]==['R03','R06','R08']
    for row,source in zip(roles,w['role_scope_matrix']):
        assert row['exact_role_requirement']==fragment(row['source'])==source and row['required_return_ids']==['RJ01','RJ05']
        missing(row)
    obligations=d['obligation_decision_requests'];assert [r['id'] for r in obligations]==['E%02d'%i for i in range(1,6)]
    for row,source in zip(obligations,w['resource_obligation_ledger']):
        assert fragment(row['source'])==source and row['exact_plan_requirement']==source['exact_plan_requirement']==fragment(source['source'])
        assert row['criterion_ids']==source['criterion_ids']==[row['id']+'-R%d'%i for i in range(1,5)]
        assert row['required_return_ids']==['RJ02','RJ04','RJ05'] and row['closed'] is False
        missing(row)
    criteria=d['resource_criterion_requests'];assert len(criteria)==20
    assert [r['id'] for r in criteria]==[o['id']+'-R%d'%i for o in obligations for i in range(1,5)]
    for row,source in zip(criteria,w['criterion_revalidation_ledger']):
        assert fragment(row['source'])==source
        assert row['obligation']==source['obligation'] and row['exact_plan_requirement']==source['exact_plan_requirement']==fragment(source['source'])
        assert row['required_disposition']==source['required_disposition'] and row['required_return_ids']==['RJ02','RJ05']
        assert row['current_disposition']=='PENDING_REVALIDATION_GENUINE_MATERIAL_AND_COMPETENT_DECISION'
        assert row['closes_resource_obligation'] is False
        missing(row)
    kinds=d['proof_kind_requests'];assert [r['kind'] for r in kinds]==['E01','E02','E03','E04','E05','CP03','ATOMICITY']
    for row,source in zip(kinds,w['prior_proof_boundary']['required_proof_kind_ledger']):
        assert fragment(row['source'])==source and row['required_reviewer_role']==source['required_reviewer_role']
        assert row['required_return_ids']==['RJ03','RJ05']
        missing(row)
    assert [r['required_reviewer_role'] for r in kinds]==['R03_RESOURCES']*5+['R06_ADMISSION_REVIEWER']*2
    basis=d['basis_index_request']
    assert basis['exact_requirement']==fragment(basis['source'])==w['prior_proof_boundary']
    assert basis['basis_reviewer_role']==w['prior_proof_boundary']['basis_reviewer_role']=='R06_ADMISSION_REVIEWER'
    truth(basis,['BASIS_is_separate_review_not_eighth_index_proof','seven_types_not_actual_or_unique_body_count'])
    missing(basis)
    policy_keys=['role_and_identity_boundary','evidence_package_requirements','contract_rule_requirements','profile_proof_requirements',
        'resource_premise_handoff','resource_and_reserve_boundary','phase_handoff','final_binding_boundary','authority_boundary','preserved_scope_and_gates']
    assert list(d['inherited_policies'])==policy_keys
    for key,row in d['inherited_policies'].items():
        assert row['exact_requirement']==fragment(row['source'])==w[key]
    assert len(w['role_and_identity_boundary']['separation_matrix'])==14
    assert [r['id'] for r in w['profile_proof_requirements']]==['C02','C03','C04','C11']
    for row in w['profile_proof_requirements']:
        assert row['exact_rule']==fragment(row['source'])
    assert len(w['contract_rule_requirements'])==7
    assert len(d['critical_boundaries'])==16 and all(v is True for v in d['critical_boundaries'].values())
    workflow=d['decision_workflow_requirements']
    assert workflow['primary_review_roles']==req['primary_review_roles']==['R03','R06']
    assert workflow['separate_acceptor_role']==req['separate_acceptor_role']=='R08'
    assert workflow['incomplete_body_author_provider_scope_assumption_or_independence_keeps_SD08'] is True
    assert type(workflow['obligations_closed']) is int and workflow['obligations_closed']==0
    missing(workflow,['actual_independent_joint_review_or_acceptance_performed'])
    routes=d['material_routes']
    assert routes['existing_material']['required_returns']==['RJ%02d'%i for i in range(1,7)]
    assert routes['existing_material']['actual_delivery_inventory'] is None and routes['existing_material']['actual_route_accepted'] is False
    gap=routes['missing_material'];assert gap['required_return_id']=='RJ07'
    truth(gap,['SD08_stop_if_body_author_provider_scope_assumption_or_independence_missing','gap_not_acceptance_no_partial_positive_as_complete_join',
        'separately_scoped_work_authority_required_no_operational_action_from_plan','no_infeasibility_or_global_absence_inferred_from_missing_material'])
    missing(gap,['actual_work_performed'])
    delivers=d['W09_deliverable_coverage'];assert [r['id'] for r in delivers]==['WD01','WD02','WD03']
    for i,row in enumerate(delivers):
        assert row['exact_requirement']==fragment(row['source'])==req['deliverables'][i]
        assert row['required_return_ids']==[['RJ02','RJ04','RJ05'],['RJ03','RJ05','RJ06'],['RJ01','RJ05']][i]
        missing(row)
    intake=d['intake_acceptance_checklist'];intake_ids=['AC%02d'%i for i in range(1,17)]
    assert [r['id'] for r in intake]==intake_ids
    for row,required in zip(intake,AC_RETURNS):
        assert row['criterion'] and row['required_return_ids']==required
        assert row['disposition']=='PENDING_PREDECESSORS_GENUINE_COMPLETE_PROOFS_AND_INDEPENDENT_DECISIONS'
        missing(row)
    exits=d['W09_exit_coverage'];assert [r['id'] for r in exits]==['WX01','WX02','WX03']
    for i,row in enumerate(exits):
        assert row['exact_predicate']==fragment(row['source'])==req['exit_predicates'][i]
        assert row['required_intake_criteria']==intake_ids and row['required_resource_criterion_ids']==[r['id'] for r in criteria]
        missing(row)
    material=d['actual_material_state']
    assert material['actual_received_inventory'] is None and material['provided_real_bodies']==material['rejected_real_bodies']==[]
    assert type(material['actual_evaluations']) is int and material['actual_evaluations']==0
    assert material['actual_provider_or_schedule'] is None and material['actual_independent_people_appointments_or_review_records'] is None
    assert material['actual_positive_BASIS_index_proof_body_or_resource_decision_created'] is False and material['actual_operational_verification_execution_or_probe_performed'] is False
    resource=d['preserved_resource_rules']
    assert resource['exact_requirement']==fragment(resource['source'])==acq['preserved_resource_and_cost_rules']
    truth(resource,['all_scope_assumptions_bounds_capacity_service_and_reference_costs_must_reconcile','no_quota_budget_reserve_transfer_or_resource_reservation_applied'])
    handoff=d['handoff']
    assert handoff['exact_A06_completion_predicate']==lot['completion_predicate'] and handoff['exact_A06_missing_stop']==lot['missing_or_failure_stop']
    assert handoff['next_lot']=='A07' and handoff['required_genuine_prior_lots']==acq['acquisition_lots'][6]['depends_on_lots']==['A02','A04','A06']
    assert handoff['A07_or_RQ07_started_sent_or_accepted'] is False
    assert handoff['exact_final_route_boundary']==fragment(handoff['final_route_source'])==plan['prelaunch_handoff_and_CE12']
    truth(handoff,['no_final_E06_payload_Q_root_admission_claim_receipt_as_new_prelaunch_condition','no_automatic_certificate_PJC115_R2_execution_or_D5_release'])
    missing(handoff,['actual_W10_W13_C_bundle_mapping_or_final_route_created'])
    change=d['change_control']
    assert change['exact_requirement']==fragment(change['source'])==w['phase_handoff']
    truth(change,['changed_author_body_source_runtime_caller_platform_resource_units_service_load_epoch_key_policy_invalidates_affected_reviews',
        'no_automatic_old_proof_approval_or_acceptance_transfer'])
    missing(change,['actual_refresh_or_active_rebind'])
    expected={**rd(A05)['current_effect'],'A06_RQ06_documentary_prepared':True,'A06_accepted':False,'RQ06_sent':False,
        'actual_independent_joint_E01_E05_BASIS_index_acceptance_created':False,'actual_A06_intake_progress_or_review_records_created':False}
    assert d['current_effect']==expected
    assert d['producer']['actor_independent'] is False and d['producer']['competent_R03_R06_review'] is False
    assert d['producer']['separate_R08_acceptance'] is False and d['producer']['external_contacts_made'] is False
    pointers(d)
    return dict(obligation_to_resource_criteria={r['id']:r['criterion_ids'] for r in obligations},
        proof_kind_review_roles={r['kind']:r['required_reviewer_role'] for r in kinds},BASIS_review_role=basis['basis_reviewer_role'],
        resource_criteria_and_intake_criteria_distinct=True,required_work_packages=gate['required_work_package_ids'],
        actual_obligations_closed=0,actual_aggregate_decision=None,actual_independent_reviews_or_acceptances=0,actual_evaluated_material=0)


CRITERIA = [
    'A06/RQ06 preserves I251/W09 exact lot,deliverables/exits and four genuine lot/seven work predecessors with A01 retained.',
    'Conditional unsent request is no contact,nomination,positive intake or independent review; documentary PASS never accepts antecedents.',
    'Five obligations preserve exact I223/W09 requirements,producers and four criteria each without self-accepted W09 predecessor.',
    'Twenty resource criteria retain exact successor applicability revalidation and no historical I131 classification/result transfer.',
    'Sixteen intake criteria are distinct from twenty inherited resource criteria and do not replace them.',
    'E01 exact closure/platform,E02 all11 heap/lifetimes/allocator/capacity,E03 complete work/WCET remain genuine requirements.',
    'E04 compatible service/clock/delays and E05 complete qualified-success ordered phases remain required,not budget/watchdog/elapsed proof.',
    'Seven index proof kinds are E01-E05,CP03,ATOMICITY; E01-E05 reviewers R03,CP03/ATOMICITY reviewers R06 exactly.',
    'BASIS has separate R06 review and is not eighth index proof; review_record_ids need real accepted same-role/scope bodies.',
    'Registry/contract/index/BASIS/six sources/runtime/source_revision cross-bind actual bytes/scope with no future payload/root/claim antecedent.',
    'Complete self-contained proofs must fit32768 or reject/review graph without truncation,hidden files/future reads or quota increase.',
    'Seven proof kinds and69 typed templates are not actual/unique proof-body counts or complete reference inventory.',
    'R03/R06 and R08 roles,authority,competence,appointments and14 separations remain exact with genuine people,not assistant/Git/strings.',
    'All real authors/providers/preparers and complete bodies/baseline facts must be identified/enrolled/authenticated before W09 acceptance.',
    'W02 provisional intake and W10 final freeze do not postpone prior authentication or preapprove future authors; CE10/root cannot be sole forecast authority.',
    'Joint scope reconciles source/image/runtime/loader/native/crypto/caller/platform/ledger/processes/resources/epoch/policy and all units/load/cache/memory/windows/delays/validity.',
    'Eleven heap owners/lifetimes/requested/committed and separate capacity,all30 work/service/WCET and complete success phases remain required.',
    'CPU sum is not wall; unknown is not zero; overlap cannot be subtracted without proof; pre-tR worker,exactTrue tW and finally through tF remain covered.',
    'No every-failure-cleanup900 or infeasibility claim; candidate budgets/reserves never prove service/capacity/fit/liveness.',
    'No partial positive,accepted flag,test,signature,hash,derivation string or document substitutes complete joint review and separate acceptance.',
    'Genuine same-scope R03/R06 reviews and separate eligible R08 decisions need bodies/reasons per criterion,obligation,proof and complete join.',
    'Seven returns preserve all three W09 deliverables/exits and complete evidence package contract without new runtime schema/member/output.',
    'Reference instances,locators,bytes/digests,authors/providers/custody/provenance,currentness and all assumptions require full real inventory.',
    'Both Readers/global lookup/freshness/identity/crypto/native/IO/copy/registry/ledger/frames/receipt/dual-output/failure costs remain included,not free offline work.',
    'RJ07/SD08 retains negative/pending no admission for missing body/author/provider/scope/assumption/independence without operational authority.',
    'Changed author/body/source/runtime/platform/resource/units/service/load/epoch/key/policy invalidates affected reviews without automatic acceptance transfer/rebind.',
    'A07/RQ07 remains stopped; W10/W11/W12/W13/CE12 are not created/accepted by preparing W09 or added as reverse predecessors.',
    'CE12 remains deferred and final execution is not new prelaunch condition; negative I122/CP07/component/PJC115-R2/D5/IR03 state remains with no run or quota change.'
]


def reconstruct():
    d=rd(SUBJECT);result=inspect(d)
    pins={**d['input_pins'],**{path:sha(path) for path in sorted(PRIOR_FILES)}}
    assert len(pins)==1117
    verify_blobs(pins)
    return dict(schema='d5.i264-source-reconstruction.v1',increment='I264',date=DATE,timezone='Europe/Madrid',base_commit=BASE,
        subject=pin(SUBJECT),input_pins=pins,independent_reconstruction=result,
        criteria=[dict(id='RV%02d'%(i+1),criterion=text,result='PASS_DOCUMENTARY_REQUIREMENT_ONLY') for i,text in enumerate(CRITERIA)],
        current_effect={**d['current_effect'],'A06_RQ06_documentary_reviewed':True})


def own_rejections(d):
    cases=[
        ('antecedent_omitted',('dependency_gate','required_lot_ids'),['A03','A04','A05']),('A05_accepted',('dependency_gate','A05_accepted'),True),
        ('request_sent',('unsent_request','sent'),True),('role_omitted',('role_evidence_requests',),d['role_evidence_requests'][:-1]),
        ('obligation_omitted',('obligation_decision_requests',),d['obligation_decision_requests'][:-1]),
        ('criterion_link_omitted',('obligation_decision_requests',4,'criterion_ids'),['E05-R1']),
        ('obligation_closed',('obligation_decision_requests',0,'closed'),True),
        ('resource_criterion_omitted',('resource_criterion_requests',),d['resource_criterion_requests'][:-1]),
        ('resource_criterion_misassigned',('resource_criterion_requests',0,'obligation'),'E02'),
        ('criterion_disposition_promoted',('resource_criterion_requests',19,'current_disposition'),'ACCEPTED_TEST_LABEL'),
        ('proof_kind_omitted',('proof_kind_requests',),d['proof_kind_requests'][:-1]),
        ('proof_reviewer_changed',('proof_kind_requests',5,'required_reviewer_role'),'R03_RESOURCES'),
        ('BASIS_reviewer_changed',('basis_index_request','basis_reviewer_role'),'R03_RESOURCES'),
        ('BASIS_eighth_proof',('basis_index_request','BASIS_is_separate_review_not_eighth_index_proof'),False),
        ('truncation_allowed',('critical_boundaries','full_self_contained_derivations_fit32768_or_reject_review_graph_never_truncate_hide_reads_or_raise_quota'),False),
        ('historical_results_transferred',('critical_boundaries','no_partial_positive_test_flag_signature_hash_or_documentary_PASS_as_joint_closure'),False),
        ('late_authentication',('critical_boundaries','every_actual_author_provider_preparer_and_baseline_authentic_before_W09_not_future_W10_CE10'),False),
        ('clock_phase_scope_waived',('critical_boundaries','worker_pre_tR_exit_to_exact_True_tW_finally_to_tF_and_liveness_required_not_all_failures900'),False),
        ('separation_omitted',('inherited_policies','role_and_identity_boundary','exact_requirement','separation_matrix'),d['inherited_policies']['role_and_identity_boundary']['exact_requirement']['separation_matrix'][:-1]),
        ('aggregate_decision_fabricated',('decision_workflow_requirements','actual_aggregate_decision'),'UNVERIFIED_TEST_LABEL'),
        ('review_role_removed',('decision_workflow_requirements','primary_review_roles'),['R03']),
        ('SD08_waived',('material_routes','missing_material','SD08_stop_if_body_author_provider_scope_assumption_or_independence_missing'),False),
        ('gap_as_authority',('material_routes','missing_material','actual_new_action_authority'),'UNVERIFIED_TEST_LABEL'),
        ('return_omitted',('requested_returns',),d['requested_returns'][:-1]),
        ('deliverable_reference_return_omitted',('W09_deliverable_coverage',1,'required_return_ids'),['RJ03','RJ05']),
        ('intake_criterion_omitted',('intake_acceptance_checklist',),d['intake_acceptance_checklist'][:-1]),
        ('exit_resource_coverage_waived',('W09_exit_coverage',0,'required_resource_criterion_ids'),['E01-R1']),
        ('inventory_fabricated',('actual_material_state','actual_received_inventory'),[]),
        ('prior_proofs_created',('actual_material_state','actual_positive_BASIS_index_proof_body_or_resource_decision_created'),True),
        ('offline_costs_free',('critical_boundaries','both_Readers_and_all_lookup_freshness_identity_crypto_native_IO_copies_ledger_receipt_outputs_failures_in_join'),False),
        ('A07_dependency_removed',('handoff','required_genuine_prior_lots'),['A06']),
        ('claim_as_own_prerequisite',('handoff','exact_final_route_boundary','claim_not_its_own_precondition'),False),
        ('old_proof_transferred',('change_control','no_automatic_old_proof_approval_or_acceptance_transfer'),False),
        ('A06_accepted',('current_effect','A06_accepted'),True),('assistant_R08',('producer','separate_R08_acceptance'),True)]
    results=[]
    for name,path,value in cases:
        mutant=copy.deepcopy(d);node=mutant
        for key in path[:-1]:
            node=node[key]
        node[path[-1]]=value
        try:
            inspect(mutant)
        except AssertionError:
            results.append(dict(case=name,result='REJECTED_DOCUMENTARY_MUTATION_IN_MEMORY'))
        else:
            raise AssertionError(name)
    return results


def build_review(rec):
    previous=runpy.run_path(str(ROOT/PRIOR_AUDIT));exists=Path.exists
    assert previous['build_candidate']()==rd(SUBJECT)
    prep=previous['build_review']()
    assert prep==rd(PRIOR_PREP) and Path.exists is exists
    return dict(schema='d5.i264-documentary-review.v1',increment='I264',date=DATE,timezone='Europe/Madrid',base_commit=BASE,status=STATUS,
        subject=pin(SUBJECT),reconstruction=pin(RECON),
        verdict='NO_NEW_DOCUMENTARY_DEFECT_FOUND_A06_RQ06_CONSISTENT_COMPLETE_PRIOR_PROOFS_AND_GENUINE_INDEPENDENT_DECISIONS_MISSING',findings=[],
        criteria=rec['criteria'],independent_reconstruction=rec['independent_reconstruction'],
        counts=dict(input_pins=1117,required_predecessor_lots=4,required_predecessor_work_packages=7,review_roles=3,separation_requirements=14,
            resource_obligations=5,resource_criteria=20,index_proof_kinds=7,separate_BASIS_review_requirements=1,requested_returns=7,intake_criteria=16,
            W09_deliverables=3,W09_exits=3,review_criteria=len(CRITERIA),actual_received_bodies=0,actual_independent_decisions=0,actual_lots_accepted=0,
            prelaunch_gates_closed=0,resource_obligations_closed=0),
        inherited_I263_rejection_checks=prep['rejection_checks'],additional_I264_rejection_checks=own_rejections(rd(SUBJECT)),
        clarifications=[
            'A02-A05 and inherited A01 remain unaccepted,SD01 active. Conditional unsent request and same-assistant review are not genuine R03/R06/R08 decisions or positive material intake.',
            'Twenty inherited resource criteria and sixteen request-intake criteria are distinct. Every obligation retains four exact resource criteria; W09 named as decision producer is not its own accepted predecessor.',
            'Seven index proof kinds are E01-E05 under R03 and CP03/ATOMICITY under R06. BASIS keeps a separate R06 review,not an eighth index proof or actual/unique body count.',
            'Complete exact self-contained derivations must fit reviewed32768 or reject/review graph without truncation or hidden future reads. Document pins,strings,accepted flags,hashes or signatures prove no truth or resource fit.',
            'All actual authors/providers/preparers and baseline facts must be authentic before W09. W10 finalizes same facts without retrospective authority; future CE10/root cannot supply sole prior authentication.',
            'All5 obligations/20 criteria,prior proof bindings and scope/unit/service/lifetime/phase/currentness assumptions must be compatible with genuine records. No partial positive becomes joint closure.',
            'RJ07/SD08 preserves negative/pending no admission when body/author/provider/scope/assumption/independence is missing; no new authority,operational verification or quota change follows.',
            'A07/W10-W12,W13 gates and CE12 remain separate future consumers. This review creates none and grants no execution or D5 release.'],
        source_reconstruction=dict(primary_source_checks=True,I263_candidate_and_preparation_reproduced=True,prior_publication_mains_called=False,
            prior_Path_exists_restored=True,no_new_presence_projection=True),current_effect=rec['current_effect'],
        provenance=dict(identity='Same Codex assistant/chat as I263',documentary_review_only=True,actor_independent=False,
            competent_R03_R06_review=False,separate_R08_acceptance=False,external_contacts_made=False),
        limitations=['A02-A06 remain unaccepted with inherited A01,SD01 active,RQ06 unsent. No actual bodies,prior proof acceptance or independent joint decisions received.',
            'Same assistant documentary review is no genuine actor enrollment,competence,appointment,independence,resource derivation or separate acceptance. E01-E05 and all20 criteria remain pending.',
            'Thirty gates and D5 remain open. No product/component execution,operational verification,probe,contact,signing,configuration,claim,receipt,quota,reserve,binding or active authority/destination change.'],
        work_unit=dict(rollback_files=sorted(FILES),verification_command='python3 docs/validation/D5-I264-audit.py',expected_result=STATUS,
            runtime_harness='N/A: own documentary JSON/Git/hash/pointer/obligation/criterion/proof-role checks and in-memory documentary mutations only. No target import/compile/discovery/tests/execution/build/profiling/benchmark/crypto/signing/keygen/enrollment/provisioning/contacts/platform/clock/CPU/IO/ledger/process/endpoint/replay/crash probes or configuration.',
            over400_lines=True,reason='Single A06/RQ06 review with primary-source reconstruction,pins,rejection checks and preservation; overage declared,no PR requested.'),
        publication=dict(commit_and_push_requested=True,publication_not_independent_decision_prior_proof_resource_acceptance_authority_execution_or_D5_closure=True))


def main():
    rec=reconstruct();assert rec==rd(RECON)
    review=build_review(rec);assert review==rd(REVIEW)
    prior=rd(PRIOR_SEAL);preserved={**prior['preserved_published804'],**prior['artifacts'],PRIOR_SEAL:sha(PRIOR_SEAL)}
    assert len(preserved)==809
    seal=rd(SEAL)
    assert seal['schema']=='d5.i264-integrity.v1' and seal['base_commit']==BASE
    assert seal['preserved_published809']==preserved and set(seal['artifacts'])==FILES-{SEAL}
    for mapping in [preserved,seal['artifacts']]:
        for path,digest in mapping.items():
            assert sha(path)==digest,path
    assert seal['source_only'] is True and seal['current_effect']==rec['current_effect']
    changed=set(git('diff',BASE,'--name-only').splitlines())|set(git('ls-files','--others','--exclude-standard').splitlines())
    assert changed==FILES,changed
    subprocess.check_call(['git','merge-base','--is-ancestor',BASE,'HEAD'],cwd=ROOT)
    if git('rev-parse','HEAD')!=BASE:
        assert not git('status','--porcelain')
    print(json.dumps(dict(status=STATUS,increment='I264',input_pins=1117,preserved_published_files=809,new_files=5,review_criteria=len(CRITERIA),
        inherited_rejections=len(review['inherited_I263_rejection_checks']),additional_rejections=len(review['additional_I264_rejection_checks']),findings=review['findings'],
        SD01_stop_active=True,prelaunch_gates_closed=0,resource_obligations_closed=0,D5_closed=False,git_head=git('rev-parse','HEAD')),sort_keys=True))


if __name__=='__main__':
    main()
