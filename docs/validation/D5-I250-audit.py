#!/usr/bin/env python3
"""I250 W13 methodological review. Own documentary checks; no target execution."""
import copy
import hashlib
import io
import json
import runpy
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
P = 'docs/validation/'
BASE = 'e7e6aa7ca998ccf85c3d44cf68da9134a45e9cf7'
DATE = '2026-11-25'
PLAN = P+'D5-I223-PRELAUNCH-RESOURCE-CLOSURE-PLAN.json'
CONTRACT = P+'D5-I130-PLATFORM-CONTRACT-CANDIDATE.json'
CE01 = P+'D5-I197-CE01-SCOPE-AND-DECISION-BOUNDARY-CANDIDATE-02.json'
CE07 = P+'D5-I193-CE07-RESOURCE-AND-COMPATIBILITY-JOIN-CANDIDATE.json'
CE07_REVIEW = P+'D5-I212-I211-documentary-review.json'
W02 = P+'D5-I223-W02-PEOPLE-AND-ANCHORS-CANDIDATE.json'
W03 = P+'D5-I223-W03-SOURCES-IMAGE-RUNTIME-CANDIDATE.json'
W04 = P+'D5-I223-W04-CALLER-PLATFORM-SERVICE-CANDIDATE.json'
W05 = P+'D5-I223-W05-SUCCESSOR-REQUALIFICATION-CANDIDATE.json'
W06 = P+'D5-I223-W06-SUCCESSOR-HEAP-LIFETIMES-CANDIDATE.json'
W07 = P+'D5-I223-W07-SUCCESSOR-WORK-CPU-UNITS-CANDIDATE.json'
W08 = P+'D5-I223-W08-SUCCESSOR-PHASE-BOUNDS-CANDIDATE.json'
PACK = P+'D5-I191-CALLER-IMAGE-CUSTODY-SCHEMAS-CANDIDATE.json'
CUSTODY = P+'D5-I191-CALLER-IMAGE-CUSTODY-CONTRACT-CANDIDATE.json'
PROFILE = P+'D5-I185-PGO181-TRUST-PROFILE-CANDIDATE-02.json'
W09 = P+'D5-I223-W09-E01-E05-INTEGRATION-CANDIDATE.json'
CE08 = P+'D5-I193-CE08-FINAL-ANTECEDENT-FREEZE-CANDIDATE.json'
CE08_REVIEW = P+'D5-I214-I213-documentary-review.json'
W10 = P+'D5-I223-W10-FINAL-ANTECEDENT-FREEZE-CANDIDATE.json'
CPACK = P+'D5-I185-PGO181-SCHEMAS-CANDIDATE-02.json'
CE09 = P+'D5-I193-CE09-EXACT-C-PROJECTION-CANDIDATE.json'
CE09_REVIEW = P+'D5-I216-I215-documentary-review.json'
W11 = P+'D5-I223-W11-EXACT-C-ACCEPTANCE-CANDIDATE.json'
CE10 = P+'D5-I193-CE10-BUNDLE-APPROVAL-AND-CURRENT-MAPPING-CANDIDATE.json'
CE10_REVIEW = P+'D5-I218-I217-documentary-review.json'
SIZE = P+'D5-I192-I191-source-reconstruction.json'
W01 = P+'D5-I223-W01-TARGET-SCOPE-AUTHORITY-CANDIDATE.json'
W12 = P+'D5-I223-W12-BUNDLE-APPROVALS-GLOBAL-MAPPING-CANDIDATE.json'
CE11 = P+'D5-I193-CE11-PRELAUNCH-EVIDENCE-CLOSURE-REVIEW-CANDIDATE.json'
CE11_REVIEW = P+'D5-I220-I219-documentary-review.json'
CHECKLIST = P+'D5-I193-CUSTODY-EVIDENCE-CHECKLIST.json'
PRIOR_AUDIT = P+'D5-I249-audit.py'
PRIOR_PREP = P+'D5-I249-preparation-review.json'
PRIOR_SEAL = P+'D5-I249-integrity.json'
PRIOR_DOC = 'docs/design/D5-I249-W13-PRELAUNCH-GATE-DECISION.md'
SUBJECT = P+'D5-I223-W13-PRELAUNCH-GATE-DECISION-CANDIDATE.json'
PRIOR_FILES = {SUBJECT,PRIOR_AUDIT,PRIOR_PREP,PRIOR_SEAL,PRIOR_DOC}
RECON = P+'D5-I250-I249-source-reconstruction.json'
REVIEW = P+'D5-I250-I249-documentary-review.json'
AUDIT = P+'D5-I250-audit.py'
SEAL = P+'D5-I250-integrity.json'
DOC = 'docs/design/D5-I250-I249-W13-REVIEW.md'
FILES = {RECON,REVIEW,AUDIT,SEAL,DOC}
STATUS = 'PASS_STATIC_SOURCE_ONLY_W13_REVIEW_THIRTY_GATES_PENDING_HANDOFF_NOT_ACCEPTED_NOT_ADMITTED'
WORK_PATHS = {'W01':W01,'W02':W02,'W03':W03,'W04':W04,'W05':W05,'W06':W06,'W07':W07,'W08':W08,'W09':W09,'W10':W10,'W11':W11,'W12':W12}


def rd(path):
    return json.loads((ROOT/path).read_text())


def sha(path):
    return hashlib.sha256((ROOT/path).read_bytes()).hexdigest()


def git(*args):
    return subprocess.check_output(['git',*args],cwd=ROOT,text=True).strip()


def pin(path,pointer=''):
    return dict(path=path,sha256=sha(path),json_pointer=pointer)


def fragment(source):
    assert sha(source['path']) == source['sha256']
    value = rd(source['path'])
    for token in source.get('json_pointer','').split('/')[1:]:
        key = token.replace('~1','/').replace('~0','~')
        value = value[int(key)] if isinstance(value,list) else value[key]
    return value


def check_pointers(value):
    if isinstance(value,dict):
        if {'path','sha256','json_pointer'} <= set(value):
            fragment(value)
        for child in value.values():
            check_pointers(child)
    elif isinstance(value,list):
        for child in value:
            check_pointers(child)


def verify_blobs(pins):
    stream = io.BytesIO(subprocess.check_output(['git','cat-file','--batch'],cwd=ROOT,
        input=''.join(BASE+':'+p+'\n' for p in sorted(pins)).encode()))
    for path,digest in sorted(pins.items()):
        header = stream.readline().decode().split()
        assert len(header) == 3 and header[1] == 'blob', path
        data = stream.read(int(header[2]))
        assert stream.read(1) == b'\n' and hashlib.sha256(data).hexdigest() == digest == sha(path), path
    assert stream.read() == b''


def require_missing(row,false_fields=()):
    for key,value in row.items():
        if key.startswith('actual_'):
            assert value is False if key in false_fields else value is None,key
    if 'accepted' in row:
        assert row['accepted'] is False


def require_true(row,names):
    for key in names:
        assert row[key] is True,key


def reconstruct_reference_templates():
    definitions=rd(PACK)['$defs']
    families=[g['family'] for g in rd(CHECKLIST)['family_gates'] if g['family']!='launch_receipt']
    def walk(value,path,pointer,stack=()):
        if '$ref' in value:
            name=value['$ref'].rsplit('/',1)[1]
            if name=='evidence_reference':
                return [(path,pointer)]
            assert name not in stack,'Cyclic schema reference'
            return walk(definitions[name],path,'/$defs/'+name,stack+(name,))
        result=[]
        for key,child in value.get('properties',{}).items():
            escaped=key.replace('~','~0').replace('/','~1')
            result.extend(walk(child,path+'/'+escaped,pointer+'/properties/'+escaped,stack))
        for key in ['items','additionalProperties']:
            if isinstance(value.get(key),dict):
                result.extend(walk(value[key],path+'/*',pointer+'/'+key,stack))
        return result
    templates=[dict(family=family,path_template=path,schema_pointer=pointer) for family in families
        for path,pointer in walk(definitions[family],'','/$defs/'+family)]
    counts={family:sum(r['family']==family for r in templates) for family in families}
    assert counts=={'anchor_registry':1,'actor_registry':3,'image_manifest':10,'caller_identity':2,'platform_custody':14,'acceptance_record':5,'custody_bundle':34}
    assert len(templates)==69
    return templates,counts


def inspect(d):
    plan,ce11=rd(PLAN),rd(CE11)
    w=plan['work_packages'][12]
    assert d['work_package']=='W13' and d['planned_deliverable_id']==w['deliverable_id']
    assert fragment(d['work_package_binding'])==w
    for key,source in [('required_deliverables','deliverables'),('required_exit_predicates','exit_predicates'),('reject_if','reject_if'),('needs_separate_future_authority_for','needs_separate_future_authority_for')]:
        assert d[key]==w[source],key
    gate=d['dependency_gate']
    assert gate['required_package_ids']==fragment(gate['source'])==w['depends_on']==['W%02d'%i for i in range(1,13)]
    assert gate['SD01_stop_active'] is True and gate['documentary_preparations_and_reviews_not_actual_dependency_acceptance'] is True
    assert all(gate['W%02d_accepted'%i] is False for i in range(1,13))
    require_missing(gate)
    packages=d['package_dependency_requirements']
    assert [r['id'] for r in packages]==list(WORK_PATHS)
    for row in packages:
        assert fragment(row['plan_requirement'])==plan['work_packages'][int(row['id'][1:])-1]
        assert row['documentary_candidate']['path']==WORK_PATHS[row['id']]
        assert fragment(row['documentary_candidate'])==rd(WORK_PATHS[row['id']])
        require_missing(row)
    assert d['role_scope_matrix']==[r for r in rd(CE01)['role_scope_matrix'] if r['id'] in ['R06','R08']]
    decision=d['competent_decision_boundary']
    assert fragment(decision['source'])==rd(W02)['identity_policy']
    assert decision['exact_identity_policy']==rd(W02)['identity_policy']['exact_policy']
    assert decision['exact_separation_matrix']==rd(W02)['separation_matrix'] and len(decision['exact_separation_matrix'])==14
    assert decision['exact_overlap_policy']==rd(W02)['overlap_policy']
    assert decision['required_provider_kind']==w['provider_kind']
    assert decision['primary_review_roles']==w['primary_review_roles']==['R06']
    assert decision['separate_acceptor_role']==w['separate_acceptor_role']=='R08'
    require_true(decision,['genuine_canonical_humans_competence_appointments_independence_all_preparers_and_exclusions_required',
        'same_assistant_documentary_review_not_actual_R06_or_R08_decision',
        'W13_named_producer_means_review_output_not_own_accepted_predecessor_or_self_authorization'])
    require_missing(decision)
    rows=d['thirty_gate_disposition_ledger']
    assert len(rows)==len({r['id'] for r in rows})==30
    assert [r['id'] for r in rows]==[r['id'] for r in plan['gate_closure_matrix']]
    categories={kind:sum(r['category']==kind for r in rows) for kind in ['FAMILY','RULE','GLOBAL']}
    assert categories=={'FAMILY':7,'RULE':16,'GLOBAL':7}
    for i,row in enumerate(rows):
        expected=plan['gate_closure_matrix'][i]
        assert row['id']==expected['id'] and row['category']==expected['category']
        assert row['exact_plan_gate']==expected==fragment(row['source'])
        assert row['exact_checklist_gate_source']==expected['source']
        assert fragment(row['exact_checklist_gate_source'])==expected['source_gate']
        assert row['current_documentary_disposition']=='PENDING_MISSING_GENUINE_EVIDENCE_AND_COMPETENT_DECISION'
        assert row['missing_reason']=='Producer packages are documentary requirements only; exact genuine evidence bodies, scope/authors/providers/custody and competent primary/separate decisions are absent.'
        producers=row['producer_requirement_ledger']
        assert [r['id'] for r in producers]==expected['producer_work_package_ids']
        for producer in producers:
            work=producer['id']
            assert fragment(producer['source'])==plan['work_packages'][int(work[1:])-1]
            assert producer['W13_own_output_not_accepted_predecessor']==(work=='W13')
            if work=='W13':
                assert producer['documentary_candidate'] is None
            else:
                assert producer['documentary_candidate']['path']==WORK_PATHS[work]
            require_missing(producer)
        require_missing(row,['actual_condition_verified'])
        assert row['rejected'] is False and row['closed'] is False and row['execution_authorized'] is False
    receipt=d['deferred_receipt_gate']
    assert receipt['exact_plan_disposition']==plan['deferred_gate']==fragment(receipt['source'])
    assert receipt['id']=='FAMILY-LAUNCH_RECEIPT' and receipt['id'] not in {r['id'] for r in rows}
    assert receipt['excluded_from30_prelaunch_targets'] is True and receipt['current_status']=='DEFERRED_NOT_AUTHORIZED'
    require_missing(receipt)
    assert receipt['execution_authorized'] is False
    summary=d['disposition_summary']
    expected_counts={'prelaunch_targets':30,'family_targets':7,'rule_targets':16,'global_targets':7,'pending':30,'accepted':0,
        'rejected_actual_evidence':0,'closed':0,'separately_deferred_receipt':1,'total_checklist_dispositions':31,'actual_competent_gate_decisions':0}
    for key,value in expected_counts.items():
        assert type(summary[key]) is int and summary[key]==value,key
    assert summary['documentary_aggregate']=='NOT_ADMITTED_INSUFFICIENT_GENUINE_EVIDENCE_AND_COMPETENT_ACCEPTANCE'
    require_true(summary,['no_gate_closed_by_document_presence_schema_type_signature_flag_or_candidate_budget',
        'absence_of_actual_rejected_material_not_acceptance_or_evidence_of_fit','no_partial_positive_aggregate_or_real_checklist_closure'])
    assert summary['actual_competent_joint_decision_or_handoff'] is None
    obligations,criteria=d['E01_E05_disposition_ledger'],d['twenty_criterion_disposition_ledger']
    assert [r['id'] for r in obligations]==['E01','E02','E03','E04','E05']
    assert len(criteria)==len({r['id'] for r in criteria})==20
    for i,row in enumerate(obligations):
        assert row['exact_plan_requirement']==plan['resource_obligation_matrix'][i]==fragment(row['source'])
        assert fragment(row['W09_requirement'])==rd(W09)['resource_obligation_ledger'][i]
        assert sum(r['obligation']==row['id'] for r in criteria)==4
        require_missing(row)
        assert row['closed'] is False and row['current_documentary_disposition']=='PENDING_INSUFFICIENT_COMPLETE_SUCCESSOR_EVIDENCE'
    for i,row in enumerate(criteria):
        expected=plan['resource_criterion_matrix'][i]
        assert row['exact_plan_requirement']==expected==fragment(row['source'])
        assert (row['id'],row['obligation'])==(expected['id'],expected['obligation'])
        assert fragment(row['W09_requirement'])==rd(W09)['criterion_revalidation_ledger'][i]
        require_missing(row)
        assert row['closes_resource_obligation'] is False and row['current_documentary_disposition']=='PENDING_NOT_TRANSFERRED_FROM_HISTORICAL_RESULT'
    resource=d['joint_resource_decision_boundary']
    assert fragment(resource['source'])==rd(W09)['resource_premise_handoff']
    require_true(resource,['all_five_obligations_and20_criteria_complete_authentic_compatible_same_final_scope_caps_Reader_outputs_and_guards_required',
        'all_missing_original_native_heap_lifetime_work_CPU_IO_service_clock_phase_atomicity_BASIS_index_and900_premises_remain_visible',
        'historical_CP03_179_cases_321_roots_12_groups_30_sites_and_tests_not_successor_or_resource_acceptance',
        'all30_successor_work_correspondence_not_ten_activities_thirty_scalar_slots_or_twenty_vectors',
        'conditional_size221644_margin40500_not_actual_encoding_fit_heap_CPU_IO_service_or900_proof',
        'no_unknown_upper_as_zero_or_unproved_overlap_deduction_or_watchdog_as_success'])
    assert resource['actual_complete_joint_resource_scope_compatibility_derivation_or_acceptance'] is None
    assert type(resource['actual_E01_E05_closed']) is int and resource['actual_E01_E05_closed']==0
    references=d['proof_reference_disposition']
    assert references['exact_plan_policy']==plan['reference_completeness_policy']==fragment(references['source'])
    templates,counts=reconstruct_reference_templates()
    expected=ce11['proof_reference_disposition']['typed_reference_templates']
    assert references['exact_typed_reference_requirements']==expected==fragment(references['typed_reference_requirements_source'])
    mapped={(r['family'],r['path_template'],r['schema_source']['json_pointer']) for r in expected}
    assert mapped=={(r['family'],r['path_template'],r['schema_pointer']) for r in templates}
    assert references['static_template_count']==len(expected)==69
    for row in expected:
        assert fragment(row['schema_source'])=={'$ref':'#/$defs/evidence_reference'}
        require_missing(row)
    require_true(references,['template_paths_arrays_and_repeated_nested_records_not_actual_unique_body_count',
        'all_actual_missing_provided_rejected_references_require_immutable_locator_hash_bytes_authors_providers_custody_scope_review_and_disposition',
        'absence_of_actual_rejection_not_acceptance','documentary_sources_and_hashes_not_actual_proof_truth_or_authorship'])
    assert references['provided_actual_proof_bodies']==[] and references['rejected_actual_proof_bodies']==[]
    assert type(references['actual_proofs_evaluated']) is int and references['actual_proofs_evaluated']==0
    assert references['actual_full_reference_body_inventory'] is None and references['actual_reference_completeness_verified'] is False
    assert [r['id'] for r in d['additional_proof_requirement_ledger']]==['AP%02d'%i for i in range(1,9)]
    assert [r['id'] for r in d['stop_requirement_ledger']]==['SD%02d'%i for i in range(1,9)]
    for i,row in enumerate(d['additional_proof_requirement_ledger']):
        assert row['exact_requirement']==ce11['additional_proof_obligations'][i]==fragment(row['source'])
        require_missing(row)
    for i,row in enumerate(d['stop_requirement_ledger']):
        assert row['exact_requirement']==plan['stop_and_decision_points'][i]==fragment(row['source'])
        require_missing(row)
        assert row['documentary_rule_preserved_not_global_absence_or_infeasibility_proof'] is True
    handoff=d['deferred_handoff']
    boundary=plan['prelaunch_handoff_and_CE12']
    assert handoff['exact_plan_boundary']==boundary==fragment(handoff['source'])
    assert fragment(handoff['CE11_requirement'])==ce11['prelaunch_handoff']
    assert handoff['required_prelaunch_package_ids']==w['depends_on']
    assert handoff['pending_final_route_obligations']==boundary['final_route_obligations']
    require_true(handoff,['handoff_of_pending_obligations_not_statement_that_final_prerequisites_satisfied',
        'actual_final_E06_payload_Q_root_admission_claim_spawn_receipt_not_prerequisite_of_prelaunch_acceptance',
        'no_actual_run_command_request_root_claim_or_destination_created'])
    assert handoff['current_run_command'] is None and handoff['actual_accepted_prelaunch_facts_or_handoff'] is False
    assert handoff['execution_or_component_qualification_authorized'] is False
    final=d['CE12_boundary']
    assert final['exact_historical_boundary']==ce11['CE12_boundary']==fragment(final['source'])
    assert final['preclaim_external_prerequisites']==boundary['preclaim_external_prerequisites']
    assert final['receipt_only_external_prerequisites']==boundary['receipt_only_external_prerequisites']
    assert len(final['preclaim_external_prerequisites'])==4 and len(final['receipt_only_external_prerequisites'])==1
    assert final['preclaim_external_prerequisites']+final['receipt_only_external_prerequisites']==boundary['final_route_obligations']
    require_true(final,['all_four_preclaim_prerequisites_genuinely_satisfied_before_claim_and_fifth_actual_claim_construction_before_receipt_required',
        'claim_not_own_precondition_and_after_full_root_admission_before_paths_spawn',
        'uncertain_partial_expired_failed_claim_no_free_retry_or_invocation_reuse','receipt_private_not_capture_output_or_new_wire_field'])
    assert final['actual_claim_spawn_receipt_or_final_route_completion_required_to_close_prelaunch'] is False
    assert final['actual_execution_authorization_final_E06_payload_Q_root_full_admission_claim_construction_or_receipt'] is None
    assert final['actual_CE12_authorized'] is False and final['actual_CE12_prerequisites_satisfied'] is False and final['actual_receipt_created'] is False
    bindings=d['final_binding_requirement_ledger']
    assert [r['id'] for r in bindings]==['B01','B02','B03','B04']
    for i,row in enumerate(bindings):
        assert row['exact_historical_requirement']==ce11['pending_I177_final_bindings'][i]==fragment(row['source'])
        require_missing(row)
        assert row['current_status']=='DEFERRED_MISSING_NOT_EXECUTED_NOT_AUTHORIZED'
    impact=d['source_resource_and_invalidation_boundary']
    assert impact['exact_plan_order']==plan['scope_authentication_and_freeze_order']==fragment(impact['source'])
    assert impact['exact_CE11_policy']==ce11['freeze_and_invalidation_policy']==fragment(impact['inherited_CE11_policy'])
    assert fragment(impact['scope_policy'])==plan['resource_and_scope_policy']
    assert impact['exact_candidate_reserve_rules']==rd(CONTRACT)['reserve_accounting']
    require_true(impact,['genuine_same_effective_source_runtime_image_policy_body_epoch_author_scope_currentness_and_guard_compatibility_required',
        'both_Readers_all_per_attempt_lookup_freshness_identity_crypto_native_IO_registry_copies_receipt_output_failure_cleanup_work_inside_global_E01_E05_and_phases',
        'any_changed_author_body_source_runtime_domain_epoch_key_policy_mapping_graph_or_resource_fact_invalidates_affected_reviews_and_requires_requalification_before_progress',
        'no_automatic_hash_proof_approval_mapping_or_scope_acceptance_transfer'])
    assert impact['actual_source_Reader_output_guard_resource_impact_or_requalification_review'] is None
    assert impact['actual_refresh_rebind_registry_clock_ledger_configuration'] is False
    assert type(impact['reserve_transfers_applied']) is int and impact['reserve_transfers_applied']==0
    assert impact['resources_reserved'] is False and impact['quotas_or_budgets_changed'] is False
    assert d['non_admission_record']==dict(I122_certificate='IMPLEMENTED_NOT_ADMITTED',CP07_verified=False,correlated_atomicity_verified=False,components_status='NOT_RUN',
        SOURCE_CAPACITY_VERIFIED_issued=False,PJC115_R2_enabled=False,prelaunch_real_gate_acceptances=0,E01_E05_closed=0,
        custody_or_resource_disposition_not_functional_execution_release_or_D5_closure=True,old_active_certificate_flags_not_automatically_promoted=True,
        actual_certificate_capture_inputs_quota_authority_destination_or_D5_change=False,IR03='NOT_READY')
    authority=d['authority_boundary']
    assert authority['inherited_boundary']==plan['authorization_boundary']==fragment(authority['source'])
    require_true(authority,['no_product_components_E06_import_compile_discovery_tests_runs_build_crypto_codec_signing_keygen_enrollment_or_provisioning',
        'no_C_Q_root_admission_authority_claim_spawn_receipt_capture_destination_registry_mapping_or_service_configuration',
        'no_clock_CPU_IO_ledger_replay_crash_restart_endpoint_process_platform_benchmarks_probes_or_provider_contacts'])
    require_missing(authority)
    assert [r['predicate'] for r in d['exit_predicate_dispositions']]==w['exit_predicates']
    for row in d['exit_predicate_dispositions']:
        assert row['predicate']==fragment(row['source'])
        require_missing(row)
    assert d['preserved_scope_and_gates']=={key:plan[key] for key in ['inherited_scope_boundaries','preserved_negative_gates','prelaunch_handoff_and_CE12']}
    for key,value in d['current_effect'].items():
        if key=='W13_documentary_prepared':
            assert value is True
        elif key=='IR03':
            assert value=='NOT_READY'
        elif key in ['actual_evidence_accepted','work_packages_accepted','prelaunch_gates_closed','resource_obligations_closed']:
            assert type(value) is int and value==0
        else:
            assert value is False,key
    check_pointers(d)
    return dict(prelaunch_categories=categories,typed_templates_by_family=counts,static_template_count=69,
        gate_acceptances=0,pending_prelaunch_gates=30,separately_deferred_receipt=1,
        preclaim_prerequisites=4,receipt_only_prerequisites=1,
        actual_competent_decisions_reference_closure_handoff_or_final_prerequisites_verified=False)


CRITERIA=[
    'Exact W13 deliverables, twelve dependencies, exits, rejections and execution/claim restriction match I223',
    'W01-W12 remain unaccepted and SD01 active; document presence does not satisfy dependencies',
    'R06 and separate R08 require genuine canonical humans/competence/appointments/exclusions, not same-assistant review',
    'W13 named producer means current checklist/handoff output, not recursive accepted predecessor or self-authorization',
    'Thirty unique gate IDs and exact I223/checklist sources partition seven families,sixteen rules,seven globals',
    'Each gate preserves producers/deliverables/close-only-if/scope/caps/guards/review requirements and real evidence gaps',
    'All thirty current dispositions are pending, with no accepted/rejected/closed/verified/execution-authorized gate',
    'Launch receipt is the separate deferred31st disposition, not an added prelaunch target',
    'Aggregate negative result is not competent joint acceptance, closed checklist or handoff',
    'Five E01-E05 rows and twenty criteria preserve exact I223/W09 links with four criteria per obligation',
    'No partial resource positive or historical CP03/test/index/signature result closes the successor join',
    'All30 work and complete heap/lives/native/service/IO/clock/phase/BASIS/atomicity/900 premises remain required',
    'I192 conditional margin/model and candidate budgets prove no actual resource fit or successful duration',
    'Independent schema traversal reconstructs69 typed evidence locations with symbolic arrays/repeated bundle records',
    'Templates/document hashes are not actual unique bodies or authorship; real reference inventory remains unknown',
    'Zero provided/rejected/evaluated actual proof bodies is not evidence of approval or fit',
    'Eight additional proof topics and eight stop requirements retain exact source dispositions without global absence claim',
    'Handoff requires genuine prior facts while leaving final authorization/E06/payload/Q/root/admission obligations pending',
    'No final-route completion, claim/spawn/receipt or run command is a new precondition for prelaunch acceptance',
    'Four external preclaim prerequisites plus actual claim/construction before receipt preserve repaired CE01/CE12 order',
    'Claim is not its own prerequisite; it follows full admission before paths/spawn and uncertain states permit no free retry',
    'CE12 is unauthorized/private with no new output/wire field; its receipt cannot close CE11 retroactively',
    'Four I177 final bindings remain missing/deferred without qualification,execution or produced results',
    'Same source/runtime/image/policy/epoch/author/currentness and Reader/output/guard scope must be genuinely compatible',
    'Both Readers and all per-attempt original/native/crypto/IO/copy/registry/receipt/failure costs remain in global E01-E05',
    'Changed scope/body/key/policy/mapping/resource facts invalidate affected reviews without automatic acceptance transfer',
    'Candidate reserves/quotas/resources/capture_inputs/authority/destination stay unchanged with no active rebind',
    'I122 IMPLEMENTED_NOT_ADMITTED,CP07 false,components NOT_RUN,PJC115-R2 disabled and IR03 NOT_READY are retained',
    'Custody/resource disposition does not release functional capture/execution, promote active flags or close D5',
    'Three W13 exits remain unaccepted and no positive competent gate/handoff/final-route authority is created']


def reconstruct():
    d=rd(SUBJECT)
    dispositions=inspect(d)
    pins={**d['input_pins'],**{p:sha(p) for p in sorted(PRIOR_FILES)}}
    assert len(pins)==1047
    verify_blobs(pins)
    return dict(schema='d5.i250-source-reconstruction.v1',increment='I250',date=DATE,base_commit=BASE,subject=pin(SUBJECT),input_pins=pins,
        criteria=[dict(id='RV%02d'%(i+1),criterion=t,result='PASS_DOCUMENTARY_REQUIREMENT_ONLY') for i,t in enumerate(CRITERIA)],
        counts=dict(input_pins=1047,prerequisite_packages=12,prelaunch_gates=30,family_gates=7,rule_gates=16,global_gates=7,
            pending_gates=30,accepted_gates=0,separately_deferred_receipt=1,resource_obligations=5,criteria=20,
            typed_reference_templates=69,additional_proof_topics=8,stop_requirements=8,preclaim_external_prerequisites=4,
            receipt_only_external_prerequisites=1,final_bindings=4,unassigned_review_roles=2,pending_exits=3,review_criteria=len(CRITERIA)),
        independent_disposition_reconstruction=dispositions,current_effect={**d['current_effect'],'W13_documentary_reviewed':True})


def own_rejections(d):
    cases=[
        ('gate_omission',('thirty_gate_disposition_ledger',),d['thirty_gate_disposition_ledger'][:-1]),
        ('gate_duplicate',('thirty_gate_disposition_ledger',1),copy.deepcopy(d['thirty_gate_disposition_ledger'][0])),
        ('gate_category_substitution',('thirty_gate_disposition_ledger',0,'category'),'RULE'),
        ('gate_pending_status_substitution',('thirty_gate_disposition_ledger',0,'current_documentary_disposition'),'DOCUMENTARY_PASS_TEST_LABEL'),
        ('gate_producer_omission',('thirty_gate_disposition_ledger',1,'producer_requirement_ledger'),d['thirty_gate_disposition_ledger'][1]['producer_requirement_ledger'][:-1]),
        ('package_body_fabrication',('package_dependency_requirements',0,'actual_accepted_same_scope_package_complete_bodies_and_review_records'),'UNVERIFIED_TEST_LABEL'),
        ('receipt_in_target_count',('disposition_summary','prelaunch_targets'),31),
        ('pending_count_reduced',('disposition_summary','pending'),29),
        ('negative_as_competent_decision',('disposition_summary','actual_competent_joint_decision_or_handoff'),'UNVERIFIED_TEST_LABEL'),
        ('resource_obligation_omission',('E01_E05_disposition_ledger',),d['E01_E05_disposition_ledger'][:-1]),
        ('criterion_scope_substitution',('twenty_criterion_disposition_ledger',0,'obligation'),'E02'),
        ('reference_template_omission',('proof_reference_disposition','exact_typed_reference_requirements'),d['proof_reference_disposition']['exact_typed_reference_requirements'][:-1]),
        ('templates_as_actual_count',('proof_reference_disposition','static_template_count'),68),
        ('invented_reference_inventory',('proof_reference_disposition','actual_full_reference_body_inventory'),[]),
        ('invented_accepted_proof',('proof_reference_disposition','provided_actual_proof_bodies'),['UNVERIFIED_TEST_LABEL']),
        ('stop_condition_as_global_absence',('stop_requirement_ledger',2,'documentary_rule_preserved_not_global_absence_or_infeasibility_proof'),False),
        ('handoff_package_omission',('deferred_handoff','required_prelaunch_package_ids'),d['deferred_handoff']['required_prelaunch_package_ids'][:-1]),
        ('claim_added_as_own_precondition',('CE12_boundary','preclaim_external_prerequisites'),d['CE12_boundary']['preclaim_external_prerequisites']+d['CE12_boundary']['receipt_only_external_prerequisites']),
        ('receipt_only_prerequisite_dropped',('CE12_boundary','receipt_only_external_prerequisites'),[]),
        ('binding_body_fabrication',('final_binding_requirement_ledger',0,'actual_body_sha256_bytes_custody_or_accepted_proof'),'UNVERIFIED_TEST_LABEL'),
        ('guard_compatibility_waived',('source_resource_and_invalidation_boundary','genuine_same_effective_source_runtime_image_policy_body_epoch_author_scope_currentness_and_guard_compatibility_required'),False),
        ('scope_change_not_invalidated',('source_resource_and_invalidation_boundary','any_changed_author_body_source_runtime_domain_epoch_key_policy_mapping_graph_or_resource_fact_invalidates_affected_reviews_and_requires_requalification_before_progress'),False),
        ('component_status_promoted',('non_admission_record','components_status'),'PASS'),
        ('certificate_promoted',('non_admission_record','I122_certificate'),'ADMITTED'),
        ('implicit_platform_probe',('authority_boundary','no_clock_CPU_IO_ledger_replay_crash_restart_endpoint_process_platform_benchmarks_probes_or_provider_contacts'),False),
        ('blanket_R01_R02_separation',('competent_decision_boundary','exact_overlap_policy','no_blanket_R01_R02_separation_added'),False)]
    results=[]
    for name,path,value in cases:
        mutant=copy.deepcopy(d)
        node=mutant
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
    previous=runpy.run_path(str(ROOT/PRIOR_AUDIT))
    exists=Path.exists
    assert previous['build_candidate']()==rd(SUBJECT)
    prep=previous['build_review']()
    assert prep==rd(PRIOR_PREP) and Path.exists is exists
    additional=own_rejections(rd(SUBJECT))
    return dict(schema='d5.i250-documentary-review.v1',increment='I250',date=DATE,timezone='Europe/Madrid',base_commit=BASE,
        status=STATUS,subject=pin(SUBJECT),reconstruction=pin(RECON),
        verdict='DOCUMENTARY_NEGATIVE_DISPOSITION_CONSISTENT_NO_NEW_DEFECT_FOUND_REAL_PRELAUNCH_CHECKLIST_AND_HANDOFF_NOT_ACCEPTED',findings=[],
        counts=rec['counts'],criteria=rec['criteria'],independent_disposition_reconstruction=rec['independent_disposition_reconstruction'],
        documentary_clarifications=[
            'Thirty gates remain pending:7 families,16 rules,7 globals. Receipt is the separately deferred31st disposition, not a prelaunch target or accepted gate. A complete negative table is not the real closed checklist.',
            'Named W13 producers refer to the current genuine review/checklist/handoff deliverable requirement, not a separate accepted predecessor or permission for the same preparer to act as R06/R08.',
            'Five obligations/twenty criteria remain unaccepted, including full same-scope proofs, providers/authors/custody/units/all assumptions/Reader/guards. Historical CP03,templates,signatures or conditional budget/model arithmetic do not transfer acceptance.',
            'Independent schema traversal reconstructs69 typed evidence locations; arrays and nested bundle references are symbolic/repeated, not actual/unique proof bodies. No actual provided/rejected/evaluated bodies means no acceptance.',
            'Handoff delivers pending final obligations without run command or release. Final E06/payload/Q/root/admission/claim/spawn/receipt completion is not a new precondition for prelaunch fact acceptance.',
            'Four external prerequisites precede actual claim; actual atomic claim/protected construction is the fifth before private receipt. Claim is not its own prerequisite, uncertain/partial/expired states permit no free retry, and CE11 has no CE12 receipt dependency.',
            'SD01 remains active; competent R06/R08 identities/decisions and real evidence are absent. This completes documentary review of W13, not actual acceptance of W01-W13, I223 prelaunch closure, D5 or execution authority.'],
        source_reconstruction=dict(primary_source_checks=True,I249_candidate_and_preparation_reproduced=True,prior_publication_mains_called=False,prior_Path_exists_restored=True,no_new_presence_projection=True),
        inherited_I249_rejection_checks=prep['rejection_checks'],additional_I250_rejection_checks=additional,current_effect=rec['current_effect'],
        provenance=dict(identity='Same Codex assistant/chat as I249',methodological_documentary_review_only=True,actor_independent=False,
            competent_R06_review=False,separate_R08_acceptance=False,external_contacts_made=False),
        limitations=['W01-W12 remain unaccepted and SD01 active. W13 table/handoff are not competent R06/R08 acceptance:30 gates pending, CE12 deferred, E01-E05 open and20 criteria unaccepted.',
            'Actual bodies/bytes/scope/providers/authors/custody/derivations/units/currentness/guard/resource compatibility and independent decisions remain missing. No resource/capacity/service/success900 or infeasibility proof.',
            'No final authorization/E06/payload/Q/root/admission/claim/receipt occurs or is authorized. Documentary publication cannot promote certificate/flags,capture_inputs,quota,authority,destination or D5.'],
        work_unit=dict(rollback_files=sorted(FILES),verification_command='python3 docs/validation/D5-I250-audit.py',expected_result=STATUS,
            runtime_harness='N/A: own documentary JSON/Git/hash/gate/criterion/schema-reference/role/handoff checks and in-memory document mutations only. No target imports/compile/discovery/tests/runs/build/E06, positive crypto/codec/signing/keygen/enrollment/provisioning, registry/mapping configuration, clock/CPU/IO/service/platform/ledger/claim/replay/process sampling/probes or contacts.',
            over400_lines=True,reason='One W13 review with primary-source reconstruction, pinned inputs, independent69-template traversal, rejection checks and integrity preservation. Overage declared; no PR requested.'),
        publication=dict(commit_and_push_requested=True,publication_not_competent_gate_acceptance_handoff_execution_release_or_D5_closure=True))


def main():
    rec=reconstruct()
    assert rec==rd(RECON)
    review=build_review(rec)
    assert review==rd(REVIEW)
    prior=rd(PRIOR_SEAL)
    preserved={**prior['preserved_published734'],**prior['artifacts'],PRIOR_SEAL:sha(PRIOR_SEAL)}
    assert len(preserved)==739
    seal=rd(SEAL)
    assert seal['schema']=='d5.i250-integrity.v1' and seal['base_commit']==BASE
    assert seal['preserved_published739']==preserved and set(seal['artifacts'])==FILES-{SEAL}
    for mapping in [preserved,seal['artifacts']]:
        for path,digest in mapping.items():
            assert sha(path)==digest,path
    assert seal['source_only'] is True and seal['current_effect']==rec['current_effect']
    changed=set(git('diff',BASE,'--name-only').splitlines())|set(git('ls-files','--others','--exclude-standard').splitlines())
    assert changed==FILES,changed
    subprocess.check_call(['git','merge-base','--is-ancestor',BASE,'HEAD'],cwd=ROOT)
    if git('rev-parse','HEAD')!=BASE:
        assert not git('status','--porcelain')
    print(json.dumps(dict(status=STATUS,increment='I250',input_pins=1047,preserved_published_files=739,new_files=5,
        criteria=len(CRITERIA),inherited_documentary_rejections=len(review['inherited_I249_rejection_checks']),
        additional_documentary_rejections=len(review['additional_I250_rejection_checks']),findings=review['findings'],
        SD01_stop_active=True,prelaunch_gates_closed=0,resource_obligations_closed=0,D5_closed=False,git_head=git('rev-parse','HEAD')),sort_keys=True))


if __name__=='__main__':
    main()
