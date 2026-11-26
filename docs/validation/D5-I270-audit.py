#!/usr/bin/env python3
"""I270 consolidated handoff review; no target/component execution."""
import copy
import hashlib
import io
import json
from pathlib import Path
import runpy
import subprocess

ROOT = Path(__file__).resolve().parents[2]
P = 'docs/validation/'
BASE = '92fb07d83c0ec3387bd21cdd17f30abd8f4f98cb'
DATE = '2026-11-26'
PLAN = P+'D5-I223-PRELAUNCH-RESOURCE-CLOSURE-PLAN.json'
ACQUISITION = P+'D5-I251-GENUINE-EVIDENCE-ACQUISITION-PLAN.json'
SUBJECT = P+'D5-I269-A01-A08-CONSOLIDATED-HANDOFF-CANDIDATE.json'
PRIOR_PREP = P+'D5-I269-preparation-review.json'
PRIOR_AUDIT = P+'D5-I269-audit.py'
PRIOR_SEAL = P+'D5-I269-integrity.json'
PRIOR_DOC = 'docs/design/D5-I269-A01-A08-CONSOLIDATED-HANDOFF.md'
PRIOR_FILES = {SUBJECT,PRIOR_PREP,PRIOR_AUDIT,PRIOR_SEAL,PRIOR_DOC}
RECON = P+'D5-I270-I269-source-reconstruction.json'
REVIEW = P+'D5-I270-I269-documentary-review.json'
AUDIT = P+'D5-I270-audit.py'
SEAL = P+'D5-I270-integrity.json'
DOC = 'docs/design/D5-I270-I269-CONSOLIDATED-HANDOFF-REVIEW.md'
FILES = {RECON,REVIEW,AUDIT,SEAL,DOC}
STATUS = 'PASS_STATIC_SOURCE_ONLY_CONSOLIDATED_HANDOFF_REVIEW_RQ01_ENTRY_AND_ALL_GENUINE_EVIDENCE_ACCEPTANCES_PENDING_NOT_ADMITTED'


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


DOSSIERS = {'A%02d'%i:P+'D5-I251-A%02d-RQ%02d-%s-CANDIDATE.json'%(i,i,n) for i,n in enumerate([
'ENTRY-AUTHORITY-SCOPE','PEOPLE-APPOINTMENTS-ANCHORS','SOURCES-IMAGE-RUNTIME','CALLER-PLATFORM-SERVICE',
'REQUALIFICATION-COMPLETE-BOUNDS','INDEPENDENT-RESOURCE-JOIN','FINAL-CUSTODY-MAPPING','GENUINE-PRELAUNCH-GATE-DECISION'],1)}
REVIEWS = {'A%02d'%i:P+'D5-I%d-I%d-documentary-review.json'%(252+2*i,251+2*i) for i in range(1,9)}
POLICIES = 'existing_material_boundary evidence_delivery_contract critical_order_rules intake_and_review_workflow stop_rules preserved_resource_and_cost_rules final_route_boundary authority_boundary preserved_scope_and_gates'.split()


def inspect(d):
    acq,plan=rd(ACQUISITION),rd(PLAN);ds={k:rd(v) for k,v in DOSSIERS.items()};ids=list(DOSSIERS)
    assert d['handoff_id']=='PGE251-A01-A08-HANDOFF-CANDIDATE-01' and d['plan']==pin(ACQUISITION)
    cover=d['cover_note'];assert cover['text'] and cover['recipient_roles_only'] is True and cover['is_draft_only'] is True
    assert cover['sent'] is False and cover['external_contacts_made'] is False;missing(cover)
    first=d['first_material_request']
    assert (first['lot_id'],first['request_id'],first['return_key'])==('A01','RQ01','A01/RT01')
    assert first['exact_first_handoff']==fragment(first['first_handoff_source'])==acq['first_handoff']
    assert first['entry_source']==pin(DOSSIERS['A01'],'/entry_gate') and first['exact_entry_boundary']==fragment(first['entry_source'])==ds['A01']['entry_gate']
    boundary=first['exact_entry_boundary']
    truth(boundary,['SD01_stop_active','no_future_W02_appointment_A07_bundle_or_root_as_sole_entry_authority','no_A01_self_authorization_from_empty_predecessor_list_or_this_user_document_request','W02_identity_requirements_used_as_eligibility_criteria_not_future_W02_acceptance_precondition'])
    assert boundary['actual_authority_verified'] is False and boundary['actual_scope_accepted'] is False
    entry=first['required_entry_evidence'];assert [r['id'] for r in entry]==['EA01','EA02','EA03']
    for i,row in enumerate(entry):
        source=ds['A01']['authority_evidence_requests'][i]
        assert row['source']==pin(DOSSIERS['A01'],'/authority_evidence_requests/'+str(i)) and fragment(row['source'])==source
        assert row['subject']==source['exact_existing_requirement']['subject'] and row['required_role']==source['exact_existing_requirement']['required_role']
        assert row['mandatory_material_fields']==source['required_independent_material_fields'];missing(row)
    assert [r['required_role'] for r in entry]==['SCOPE_AUTHORITY','R06','R08']
    assert first['all_A01_return_keys']==['A01/RT%02d'%i for i in range(1,6)]
    truth(first,['no_A01_self_authorization_or_future_A02_bundle_forecast_authority','no_external_contact_fetch_or_verification_service_authorized','W02_eligibility_requirements_not_backward_W02_acceptance_dependency','SD01_stop_active'])
    assert first['RQ01_sent'] is False and first['RQ02_or_downstream_enabled'] is False;missing(first)
    cards=d['lot_cards'];assert [r['id'] for r in cards]==ids
    expected_returns=[];expected_criteria=[];deliveries=exits=0
    for i,row in enumerate(cards):
        k=row['id'];lot=acq['acquisition_lots'][i];dossier=ds[k];criterion_key='intake_acceptance_checklist' if k=='A06' else 'acceptance_checklist'
        assert row['source']==pin(ACQUISITION,'/acquisition_lots/'+str(i)) and fragment(row['source'])==lot
        assert row['dossier']==pin(DOSSIERS[k]) and fragment(row['dossier'])==dossier
        assert row['documentary_review']==pin(REVIEWS[k]);review=fragment(row['documentary_review'])
        assert review['findings']==[] and review['provenance']['actor_independent'] is False
        assert row['request_id']==dossier['request_id']==lot['unsent_request_draft']['id'] and row['title']==lot['title']
        assert row['request_source']==pin(DOSSIERS[k],'/unsent_request') and row['exact_draft']==fragment(row['request_source'])==dossier['unsent_request']
        assert row['exact_draft']['original_draft']==lot['unsent_request_draft'] and row['exact_draft']['is_draft_only'] is True
        assert row['exact_draft']['sent'] is False and row['exact_draft']['contact_authorized'] is False
        assert row['depends_on_lots']==lot['depends_on_lots']==acq['lot_order']['graph'][k] and row['covers_work_packages']==lot['covers_work_packages']
        assert row['recipient_role_only']==lot['intended_recipient_role_kind'] and row['primary_review_roles']==lot['required_primary_review_roles'] and row['separate_acceptor_role']==lot['separate_acceptor_role']=='R08'
        assert row['exact_completion_predicate']==lot['completion_predicate'] and row['exact_missing_stop']==lot['missing_or_failure_stop']
        rk=[k+'/'+r['id'] for r in dossier['requested_returns']];ck=[k+'/'+r['id'] for r in dossier[criterion_key]]
        assert row['return_keys']==rk and row['intake_criterion_keys']==ck
        expected_returns.extend((k,j,r) for j,r in enumerate(dossier['requested_returns']))
        expected_criteria.extend((k,criterion_key,j,r) for j,r in enumerate(dossier[criterion_key]))
        for suffix in ['deliverable_coverage','exit_coverage']:
            sk=next(s for s in dossier if s.endswith(suffix));ref=row['deliverable_source' if suffix=='deliverable_coverage' else 'exit_source']
            assert ref==pin(DOSSIERS[k],'/'+sk) and fragment(ref)==dossier[sk]
            if suffix=='deliverable_coverage':deliveries+=len(dossier[sk])
            else:exits+=len(dossier[sk])
        assert row['material_summary'] and row['prerequisite_acceptances_not_documentary_reviews'] is True
        assert row['current_material_disposition']=='MISSING' and row['request_sent'] is False;missing(row)
    assert (deliveries,exits)==(41,39)
    returns=d['return_index'];assert len(returns)==len(expected_returns)==52 and len({r['key'] for r in returns})==52
    for row,(k,i,src) in zip(returns,expected_returns):
        assert (row['key'],row['lot_id'],row['id'],row['title'])==(k+'/'+src['id'],k,src['id'],src['title'])
        assert row['source']==pin(DOSSIERS[k],'/requested_returns/'+str(i)) and fragment(row['source'])==src
        assert row['evidence_delivery_contract']==pin(ACQUISITION,'/evidence_delivery_contract')
        assert row['complete_source_requirement_retained_not_summarized_away'] is True and row['current_material_disposition']=='MISSING';missing(row)
    criteria=d['intake_criterion_index'];assert len(criteria)==len(expected_criteria)==136 and len({r['key'] for r in criteria})==136
    for row,(k,sk,i,src) in zip(criteria,expected_criteria):
        assert (row['key'],row['lot_id'],row['id'],row['criterion'])==(k+'/'+src['id'],k,src['id'],src['criterion'])
        assert row['source']==pin(DOSSIERS[k],'/'+sk+'/'+str(i)) and fragment(row['source'])==src;missing(row)
    works=d['work_package_handoffs'];assert [r['id'] for r in works]==['W%02d'%i for i in range(1,14)]
    for i,row in enumerate(works):
        src=plan['work_packages'][i];assert row['source']==pin(PLAN,'/work_packages/'+str(i)) and fragment(row['source'])==src
        for key,sk in [('depends_on_work_packages','depends_on'),('planned_deliverable_id','deliverable_id'),('primary_review_roles','primary_review_roles'),('separate_acceptor_role','separate_acceptor_role')]:assert row[key]==src[sk]
        assert row['lot_id']==next(lot['id'] for lot in acq['acquisition_lots'] if row['id'] in lot['covers_work_packages']);missing(row)
    order=d['exact_order']
    for sourcekey,valuekey,section in [('source','exact_lot_order','lot_order'),('work_graph_source','exact_work_dependency_graph','exact_I223_work_dependency_graph'),('critical_rules_source','exact_critical_rules','critical_order_rules')]:
        assert order[sourcekey]==pin(ACQUISITION,'/'+section) and order[valuekey]==fragment(order[sourcekey])==acq[section]
    assert type(order['actual_lots_accepted']) is int and order['actual_lots_accepted']==0 and order['no_new_phase_lot_or_reverse_acceptance_dependency'] is True
    sorted_lots=order['exact_lot_order']['topological_order'];assert sorted_lots==ids
    assert all(sorted_lots.index(dep)<sorted_lots.index(k) for k,deps in order['exact_lot_order']['graph'].items() for dep in deps)
    milestones=d['milestone_requests'];assert [r['id'] for r in milestones]==['M%02d'%i for i in range(1,8)]
    for i,row in enumerate(milestones):
        src=acq['real_milestones'][i];assert row['source']==pin(ACQUISITION,'/real_milestones/'+str(i)) and fragment(row['source'])==src
        assert row['lots']==src['lots'] and row['required_genuine_completion']==src['evidence_of_completion'];missing(row)
    gates=d['gate_collection_handoffs'];assert [r['id'] for r in gates]==[r['id'] for r in acq['gate_to_collection_matrix']] and len(gates)==30
    categories={'FAMILY':0,'RULE':0,'GLOBAL':0}
    for i,row in enumerate(gates):
        src=acq['gate_to_collection_matrix'][i];req=ds['A08']['gate_decision_requests'][i]
        assert row['source']==pin(ACQUISITION,'/gate_to_collection_matrix/'+str(i)) and fragment(row['source'])==src
        assert row['A08_request_source']==pin(DOSSIERS['A08'],'/gate_decision_requests/'+str(i)) and fragment(row['A08_request_source'])==req
        assert row['category']==src['category']==req['category'];categories[row['category']]+=1
        assert row['required_collection_lots']==src['required_collection_lots']==req['required_collection_lots']
        assert row['required_work_package_ids']==src['required_work_package_ids']==req['producer_work_package_ids']
        assert row['W13_output_not_accepted_predecessor']==('W13' in row['required_work_package_ids']) and row['closed'] is False;missing(row)
    assert categories==dict(FAMILY=7,RULE=16,GLOBAL=7)
    resources=d['resource_join_handoffs'];assert [r['id'] for r in resources]==['E%02d'%i for i in range(1,6)]
    for i,row in enumerate(resources):
        src=acq['resource_acceptance_matrix'][i];assert row['source']==pin(ACQUISITION,'/resource_acceptance_matrix/'+str(i)) and fragment(row['source'])==src
        assert row['producer_lots']==src['producer_lots']
        for key,path,section in [('A06_obligation_source',DOSSIERS['A06'],'obligation_decision_requests'),('A08_obligation_source',DOSSIERS['A08'],'resource_decision_requests')]:
            assert row[key]==pin(path,'/'+section+'/'+str(i));obligation=fragment(row[key]);assert obligation['id']==row['id'] and obligation['criterion_ids']==row['criterion_ids']
        assert row['criterion_ids']==[row['id']+'-R%d'%j for j in range(1,5)] and row['W09_required_roles']==['R03','R06','R08'] and row['W13_required_roles']==['R06','R08']
        assert row['W13_review_not_substitute_for_W09'] is True and row['closed'] is False;missing(row)
    authorities=d['authority_request_ledger'];assert len(authorities)==13
    fields=['exact action and purpose','canonical accountable actor and eligible reviewer','exact source/body/runtime/platform/scope and dependent packages',
        'complete resource/cost/phase and unchanged-limit impact','independent authority/provenance/validity and allowed/denied actions','invalidation and acceptance conditions']
    for i,row in enumerate(authorities):
        src=acq['future_authority_resolution_ledger'][i];assert row['source']==pin(ACQUISITION,'/future_authority_resolution_ledger/'+str(i)) and fragment(row['source'])==src
        for key in ['work_id','collection_lot','exact_separate_action_classes','if_required_for_missing_material']:assert row[key]==src[key]
        assert row['required_separate_proposal_fields']==fields and row['authorized_now'] is False and row['work_performed'] is False;missing(row)
    policies=d['inherited_policies'];assert [r['section'] for r in policies]==POLICIES
    for row,s in zip(policies,POLICIES):assert row['source']==pin(ACQUISITION,'/'+s) and row['exact_requirement']==fragment(row['source'])==acq[s]
    intake=d['future_intake_route'];assert fragment(intake['source'])==acq['intake_and_review_workflow']
    assert intake['ordered_steps']==acq['intake_and_review_workflow']['ordered_steps'] and intake['allowed_material_dispositions']==acq['intake_and_review_workflow']['allowed_future_dispositions']
    truth(intake,['same_assistant_not_primary_or_separate_genuine_decision','all_missing_provided_rejected_reference_instances_and_assumptions_visible','unknown_not_zero_no_predictive_hash_or_template_as_body'])
    assert intake['provided_real_bodies']==intake['rejected_real_bodies']==[] and type(intake['actual_evaluations']) is int and intake['actual_evaluations']==0
    missing({k:v for k,v in intake.items() if k!='actual_evaluations'})
    assert len(d['critical_boundaries'])==24 and all(v is True for v in d['critical_boundaries'].values())
    final=d['final_handoff_boundary'];assert final['exact_A08_boundary']==fragment(final['A08_source'])==ds['A08']['handoff']
    assert final['exact_I251_boundary']==fragment(final['I251_source'])==acq['final_route_boundary']
    assert final['current_run_command'] is None and final['no_new_A09_or_automatic_release'] is True
    missing(final,['actual_final_route_or_receipt_authorized','actual_Q_root_claim_spawn_receipt_or_final_artifact_created'])
    assert d['current_effect']=={**ds['A08']['current_effect'],'A01_A08_consolidated_documentary_handoff_prepared':True,'actual_consolidated_handoff_delivery_or_intake_progress':False,'actual_new_genuine_evidence_or_authority_or_acceptance_created':False}
    assert all(d['producer'][k] is False for k in ['actor_independent','competent_primary_role_review','separate_R08_acceptance','external_contacts_made'])
    pointers(d)
    return dict(lot_order=ids,lot_return_counts={k:len(v['requested_returns']) for k,v in ds.items()},lot_intake_counts={k:len(v['intake_acceptance_checklist' if k=='A06' else 'acceptance_checklist']) for k,v in ds.items()},
        first_lot='A01',first_request='RQ01',first_return='A01/RT01',entry_roles=[r['required_role'] for r in entry],
        qualified_return_keys=52,qualified_intake_keys=136,deliverables=41,exits=39,gate_categories=categories,resource_criteria=20,
        no_self_or_forecast_entry_authority=True,no_reverse_W02_acceptance_dependency=True,actual_delivery_or_intake_progress=0,actual_genuine_acceptances=0)

CRITERIA = [
'Consolidation retains original I251 eight lots and existing requests,no new acquisition plan,phase or lot.',
'Local cover note is unsent,draft only,with coordinator/people/channels/contact authority/delivery unknown.',
'First material is A01/RQ01/RT01 and complete RT01-RT05,not downstream A08 or a new review paper.',
'EA01 scope authority,EA02 R06 and EA03 R08 preserve exact independent genuine authority/material fields.',
'Empty A01 predecessor list and user docs/publication request never create entry authority or scope adoption.',
'Future A02 appointments/A07 bundle/root cannot be sole forecast authority; W02 eligibility is not backward W02 acceptance prerequisite.',
'All A01 scope/authority/review/separate decisions remain missing,SD01 active,RQ01 unsent,RQ02/downstream not enabled.',
'Eight dossier and review pins retain their own provenance; same-assistant documentary reviews are not genuine independence or acceptance.',
'Every original complete unsent draft,recipient role,primary W roles,separate R08,completion and missing stop remains exact.',
'All lot dependencies and W coverage remain I251 exact with no skipped predecessor,self authority or reverse edge.',
'52 original returns retain exact titles,source rows,complete requirements and universal delivery contract.',
'136 original intake criteria retain exact text and lot-qualified keys,no collision or cross-lot criterion reassignment.',
'41 deliverables and39 exits retain complete original source ledgers,not summaries replacing requirements.',
'13 W handoffs preserve exact work dependency graph,lot ownership,planned IDs and own required reviews.',
'Seven milestones preserve genuine completion predicates; none accepted or given invented schedule/provider.',
'A03 real qualified source/image/runtime and A04 enforceable platform/service/capacity precede costly derivations.',
'W05 before W06/W07 then W08 remains exact,all real authors/bodies/baseline facts authenticate before A06/W09.',
'A07 freezes same accepted facts; no retrospective or future CE10/root sole authority or automatic transfer.',
'Eight roles/fourteen human-key exclusions and complete preparers remain required; assistant/Git/labels prove no human identity or independence.',
'All11 heap owners/lifetimes/native/allocator,30 successor work/WCET/CPU/IO/service/clock/success phases900 remain unproved.',
'Unknown not zero,unproved overlap not subtracted,CPU sum not wall,watchdog not success,budgets/reserves not capacity/service.',
'Five E01-E05 joins retain20 resource criteria,distinct from136 request-intake criteria.',
'W09 R03/R06/R08 decisions are not replaced by W13 R06/R08; complete same-scope join required.',
'Seven index proof kinds and separate BASIS retain exact closure,complete bodies fit or reject,no truncation or extra proof count.',
'Thirty gate collection rows preserve7 families16 rules7 globals,exact producers/lots and A08 requests.',
'W13 producers are decision outputs,not own accepted predecessors; no gate closed by document/schema/signature/flag/PASS/budget.',
'69 reference templates are not actual unique bodies or full inventory; missing/provided/rejected material and assumptions stay visible.',
'Both Readers/global lookup/freshness/identity/crypto/native/IO/copies/registry/ledger/receipt/output/failure costs remain included.',
'C19/acceptance27/core8/bundle3/three same-core role-domain-one-NUL approvals and exact global mapping remain prospective.',
'Conditional221644/40500 is not encoding/fit/heap/CPU/service/reserve proof; quotas and all limits unchanged.',
'Thirteen action-authority rows retain exact separate actions and concrete proposal fields,not granted or performed actions.',
'Nine policy sections and eight SD stops retain exact I251 rules with no inferred global infeasibility or calendar promise.',
'Future intake preserves material states,full genuine available bodies/provenance/scope/currentness and competent primary/separate decisions.',
'Changed contributor/body/source/runtime/platform/caller/domain/epoch/key/policy/mapping/graph/resource invalidates any affected A01-A08 before progress.',
'X09 communicates pending obligations only,no current command,actual accepted handoff,new A09 or automatic release.',
'CE12 receipt31 remains private deferred unauthorized,no final E06/Q/root/claim/spawn/receipt as new prelaunch antecedent.',
'Four external prerequisites before claim and actual claim/construction fifth before receipt remain separate,no self-condition or free retry.',
'All actual inventory/provider/authority/reviews/acceptances stay missing; no outbound contact,positive intake or operational record created.',
'Documentary PASS/commit/push gives no canonical authority,resource truth,independence,product execution,PJC115-R2 or D5 closure.',
'Negative I122/CP07/atomicity/component/E06/D5/IR03 state and quotas/reserves/bindings/authority/destinations remain preserved.'
]


def reconstruct():
    d=rd(SUBJECT);result=inspect(d);pins={**d['input_pins'],**{p:sha(p) for p in PRIOR_FILES}}
    assert len(pins)==1147;verify_blobs(pins)
    return dict(schema='d5.i270-source-reconstruction.v1',increment='I270',date=DATE,timezone='Europe/Madrid',base_commit=BASE,subject=pin(SUBJECT),input_pins=pins,
        independent_reconstruction=result,criteria=[dict(id='RV%02d'%(i+1),criterion=t,result='PASS_DOCUMENTARY_REQUIREMENT_ONLY') for i,t in enumerate(CRITERIA)],
        current_effect={**d['current_effect'],'A01_A08_consolidated_documentary_handoff_reviewed':True})


def own_rejections(d):
    cases=[
('entry_return_reassigned',('first_material_request','return_key'),'A02/IT01'),('entry_scope_role',('first_material_request','required_entry_evidence',0,'required_role'),'R08'),
('entry_fields_omitted',('first_material_request','required_entry_evidence',1,'mandatory_material_fields'),[]),
('forecast_authority',('first_material_request','exact_entry_boundary','no_future_W02_appointment_A07_bundle_or_root_as_sole_entry_authority'),False),
('W02_reverse_dependency',('first_material_request','W02_eligibility_requirements_not_backward_W02_acceptance_dependency'),False),
('A01_returns_omitted',('first_material_request','all_A01_return_keys'),['A01/RT01']),('lot_missing',('lot_cards',),d['lot_cards'][:-1]),
('lot_recipient_changed',('lot_cards',1,'recipient_role_only'),'UNVERIFIED_TEST_LABEL'),('lot_reviewer_removed',('lot_cards',5,'primary_review_roles'),{}),
('completion_weakened',('lot_cards',0,'exact_completion_predicate'),'DOCUMENT_PRESENT'),('stop_removed',('lot_cards',0,'exact_missing_stop'),''),
('return_key_collision',('return_index',1,'key'),'A01/RT01'),('return_scope_reassigned',('return_index',0,'lot_id'),'A08'),
('return_contract_omitted',('return_index',0,'evidence_delivery_contract','json_pointer'),'/first_handoff'),
('criterion_key_collision',('intake_criterion_index',1,'key'),'A01/AC01'),('criterion_source_reassigned',('intake_criterion_index',0,'source','json_pointer'),'/acceptance_checklist/1'),
('criterion_text_changed',('intake_criterion_index',0,'criterion'),'DOCUMENT_PRESENT'),
('work_lot_reassigned',('work_package_handoffs',12,'lot_id'),'A01'),('work_R08_replaced',('work_package_handoffs',0,'separate_acceptor_role'),'R06'),
('order_changed',('exact_order','exact_lot_order','topological_order'),['A08']),('milestone_missing',('milestone_requests',),d['milestone_requests'][:-1]),
('milestone_predicate_changed',('milestone_requests',0,'required_genuine_completion'),'DOCUMENT_PRESENT'),
('gate_category_changed',('gate_collection_handoffs',0,'category'),'GLOBAL'),('gate_lot_changed',('gate_collection_handoffs',0,'required_collection_lots'),['A08']),
('gate_source_changed',('gate_collection_handoffs',0,'A08_request_source','json_pointer'),'/gate_decision_requests/1'),
('resource_criteria_omitted',('resource_join_handoffs',4,'criterion_ids'),['E05-R1']),('resource_producer_omitted',('resource_join_handoffs',0,'producer_lots'),[]),
('W09_substituted',('resource_join_handoffs',0,'W13_review_not_substitute_for_W09'),False),
('authority_classes_omitted',('authority_request_ledger',2,'exact_separate_action_classes'),[]),('authority_proposal_fields_omitted',('authority_request_ledger',2,'required_separate_proposal_fields'),[]),
('policy_section_omitted',('inherited_policies',),d['inherited_policies'][:-1]),('SD01_changed',('inherited_policies',4,'exact_requirement','current_SD01_active'),False),
('intake_sequence_changed',('future_intake_route','ordered_steps'),[]),('provided_as_accepted',('future_intake_route','allowed_material_dispositions'),['ACCEPTED']),
('template_to_truth',('future_intake_route','unknown_not_zero_no_predictive_hash_or_template_as_body'),False),
('new_genuine_body',('future_intake_route','provided_real_bodies'),['UNVERIFIED_TEST_LABEL']),
('receipt_precondition',('final_handoff_boundary','exact_I251_boundary','no_final_route_execution_claim_spawn_receipt_as_new_precondition_of_prelaunch_acceptance'),False),
('claim_self_condition',('final_handoff_boundary','exact_I251_boundary','claim_not_own_precondition_no_free_retry_uncertain_partial_expired_states'),False),
('old_scope_transfer',('critical_boundaries','changed_author_body_source_runtime_caller_domain_resource_epoch_key_policy_mapping_graph_invalidates_any_affected_A01_A08'),False),
('assistant_primary',('producer','competent_primary_role_review'),True)]
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
    return dict(schema='d5.i270-documentary-review.v1',increment='I270',date=DATE,timezone='Europe/Madrid',base_commit=BASE,status=STATUS,
        subject=pin(SUBJECT),reconstruction=pin(RECON),verdict='NO_NEW_DOCUMENTARY_DEFECT_FOUND_RQ01_ENTRY_AUTHORITY_AND_ALL_GENUINE_EVIDENCE_ACCEPTANCES_PENDING',findings=[],
        criteria=rec['criteria'],independent_reconstruction=rec['independent_reconstruction'],
        counts=dict(input_pins=1147,preserved_published_files=839,lot_cards=8,unsent_requests=8,return_requests=52,intake_criteria=136,work_packages=13,deliverables=41,exits=39,milestones=7,
            entry_evidence_requirements=3,gate_collection_rows=30,resource_obligations=5,resource_criteria=20,authority_action_rows=13,policy_sections=9,review_criteria=len(CRITERIA),
            actual_received_bodies=0,actual_genuine_acceptances=0,prelaunch_gates_closed=0,resource_obligations_closed=0),
        inherited_I269_rejection_checks=prep['rejection_checks'],additional_I270_rejection_checks=own_rejections(rd(SUBJECT)),
        clarifications=[
            'The consolidated handoff is a local index/cover of8 already reviewed requests,not a new evidence plan or delivered package.52 returns/136 intake criteria/41 deliverables/39 exits preserve full exact source requirements.',
            'First pending material remains A01/RQ01/RT01 EA01 scope authority,EA02 R06,EA03 R08 under genuine preexisting authority plus complete RT01-RT05 scope/limits/action authority and real reviews. No document count or further assistant review supplies it.',
            'A01 has no lot predecessor but is not self-authorized. W02 identity requirements are eligibility criteria,not a requirement that future W02 be accepted before A01. Future A02/bundle/root cannot be sole entry authority.',
            'For all8 lots,canonical people,recipients,providers,contact and coordination authority,and schedules remain unspecified; preparing and publishing never nominates or contacts anyone. All lots remain unaccepted,SD01 active,RQ01 unsent,RQ02/downstream not enabled.',
            'Documentary review pins preserve provenance,not genuine actor independence.136 intake criteria differ from20 resource criteria; W13 R06/R08 does not replace W09 R03/R06/R08.',
            '13 future action-authority rows record exact separate work/authority classes and proposal fields,not granted authority,operational proposals already approved,or performed work.',
            'Genuine prior baseline/authors/proof bodies precede W09; W10 final freeze cannot retroactively authenticate. Changes invalidate any affected A01-A08 before progress,not automatic proof/approval/mapping transfer.',
            'X09 communicates pending obligations only; CE12 receipt31 private deferred unauthorized. Four external preclaim prerequisites and fifth actual claim/construction before receipt remain separate,no final events as new prelaunch condition,no A09 or automatic release.'],
        source_reconstruction=dict(primary_source_checks=True,I269_candidate_and_preparation_reproduced=True,prior_publication_mains_called=False,prior_Path_exists_restored=True,no_new_presence_projection=True),
        current_effect=rec['current_effect'],provenance=dict(identity='Same Codex assistant/chat as I269 and A01-A08 dossiers/reviews',documentary_review_only=True,actor_independent=False,competent_primary_role_review=False,separate_R08_acceptance=False,external_contacts_made=False),
        limitations=['RQ01/RT01 preexisting scope authority and reviewer eligibility remain missing,SD01 active. No actual body/provider/authority/primary or separate decision received and no downstream positive intake enabled.',
            'All A01-A08,30 gates,E01-E05/20 criteria,PJC115-R2 and D5 remain unaccepted/open. JSON/hash/pointer/graph/mutation PASS is no proof of truth,independence,capacity,service,900-second fit or global custody/mapping.',
            'No product/component execution,positive crypto/signing/keygen/enrollment/contact/provision/configuration/probe,quota/reserve/binding/authority/destination/certificate change. Final route and CE12 remain separately deferred.'],
        work_unit=dict(rollback_files=sorted(FILES),verification_command='python3 docs/validation/D5-I270-audit.py',expected_result=STATUS,over400_lines=True,
            reason='One consolidated handoff review with independent entry/source/coverage reconstruction,pins,rejection checks and preservation; overage declared,no PR requested.',
            runtime_harness='N/A: own documentary JSON/Git/hash/pointer/coverage/graph checks and in-memory mutations only; no target import,compile,discovery,tests,execution,build,benchmark,codec,crypto,signing,keygen,enrollment,contacts,provision,configuration or platform/clock/CPU/IO/ledger/process/endpoint/replay/crash/restart probes.'),
        publication=dict(commit_and_push_requested=True,publication_not_genuine_evidence_authority_review_acceptance_delivery_execution_or_D5_closure=True))


def main():
    rec=reconstruct();assert rec==rd(RECON)
    review=build_review(rec);assert review==rd(REVIEW)
    prior=rd(PRIOR_SEAL);preserved={**prior['preserved_published834'],**prior['artifacts'],PRIOR_SEAL:sha(PRIOR_SEAL)};assert len(preserved)==839
    seal=rd(SEAL);assert seal['schema']=='d5.i270-integrity.v1' and seal['base_commit']==BASE
    assert seal['preserved_published839']==preserved and set(seal['artifacts'])==FILES-{SEAL}
    for mapping in [preserved,seal['artifacts']]:
        for p,h in mapping.items():assert sha(p)==h,p
    assert seal['source_only'] is True and seal['current_effect']==rec['current_effect']
    changed=set(git('diff',BASE,'--name-only').splitlines())|set(git('ls-files','--others','--exclude-standard').splitlines());assert changed==FILES,changed
    subprocess.check_call(['git','merge-base','--is-ancestor',BASE,'HEAD'],cwd=ROOT)
    if git('rev-parse','HEAD')!=BASE:assert not git('status','--porcelain')
    print(json.dumps(dict(status=STATUS,input_pins=1147,preserved_published_files=839,new_files=5,review_criteria=len(CRITERIA),inherited_rejections=len(review['inherited_I269_rejection_checks']),additional_rejections=len(review['additional_I270_rejection_checks']),findings=review['findings'],prelaunch_gates_closed=0,resource_obligations_closed=0,D5_closed=False),sort_keys=True))


if __name__=='__main__':main()
