#!/usr/bin/env python3
"""I262 documentary review of A05/RQ05; no target/component execution."""
import copy
import hashlib
import io
import json
from pathlib import Path
import runpy
import subprocess

ROOT = Path(__file__).resolve().parents[2]
P = 'docs/validation/'
BASE = '327cb757387b330bb4afddaf204918464679384d'
DATE = '2026-11-26'
PLAN = P+'D5-I223-PRELAUNCH-RESOURCE-CLOSURE-PLAN.json'
ACQUISITION = P+'D5-I251-GENUINE-EVIDENCE-ACQUISITION-PLAN.json'
A04 = P+'D5-I251-A04-RQ04-CALLER-PLATFORM-SERVICE-CANDIDATE.json'
SUBJECT = P+'D5-I251-A05-RQ05-REQUALIFICATION-COMPLETE-BOUNDS-CANDIDATE.json'
PRIOR_PREP = P+'D5-I261-preparation-review.json'
PRIOR_AUDIT = P+'D5-I261-audit.py'
PRIOR_SEAL = P+'D5-I261-integrity.json'
PRIOR_DOC = 'docs/design/D5-I261-A05-RQ05-REQUALIFICATION-COMPLETE-BOUNDS.md'
PRIOR_FILES = {SUBJECT,PRIOR_PREP,PRIOR_AUDIT,PRIOR_SEAL,PRIOR_DOC}
RECON = P+'D5-I262-I261-source-reconstruction.json'
REVIEW = P+'D5-I262-I261-documentary-review.json'
AUDIT = P+'D5-I262-audit.py'
SEAL = P+'D5-I262-integrity.json'
DOC = 'docs/design/D5-I262-I261-A05-RQ05-REVIEW.md'
FILES = {RECON,REVIEW,AUDIT,SEAL,DOC}
STATUS = 'PASS_STATIC_SOURCE_ONLY_A05_RQ05_REVIEW_REQUALIFICATION_COMPLETE_BOUNDS_AND_GENUINE_DECISIONS_PENDING_NOT_ADMITTED'
WORKS = {
    'W05':P+'D5-I223-W05-SUCCESSOR-REQUALIFICATION-CANDIDATE.json',
    'W06':P+'D5-I223-W06-SUCCESSOR-HEAP-LIFETIMES-CANDIDATE.json',
    'W07':P+'D5-I223-W07-SUCCESSOR-WORK-CPU-UNITS-CANDIDATE.json',
    'W08':P+'D5-I223-W08-SUCCESSOR-PHASE-BOUNDS-CANDIDATE.json'}


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


SECTIONS = {
    'W05':['inherited_scope_boundary','historical_operand_obligations','historical_root_obligations','historical_group_obligations',
        'historical_atomicity_obligations','atomicity_required_reasoning','policy_obligation_ledger','new_path_family_requirements',
        'coverage_completeness','qualification_boundary','basis_index_boundary','resource_handoff','cost_and_scope_boundary','phase_and_authority_boundary'],
    'W06':['owner_derivation_ledger','historical_allocation_class_obligations','owner_overlap_obligations','inherited_reference_boundary',
        'heap_metric_policy','lifetime_and_peak_contract','new_successor_memory_requirements','successor_coverage_boundary',
        'requested_rollup','committed_rollup','candidate_budget_ledger','availability_and_fit','phase_handoff','authority_and_costs'],
    'W07':['all30_successor_correspondence','historical_activity_obligations','historical_scalar_slot_obligations',
        'historical_process_phase_vector_obligations','historical_compatibility_join_obligations','latency_owner_obligations',
        'phase_category_obligations','work_service_or_WCET_boundary','scope_and_complete_work_boundary','per_attempt_cost_ledger',
        'per_attempt_cost_boundary','actual_whole_work_and_time','service_dependency','interval_and_budget_boundary','phase_handoff','authority_boundary'],
    'W08':['authorship_boundary','historical_reference_boundary','clock_and_marker_obligations','formal_phase_algebra','phase_derivation_ledger',
        'historical_conditional_premise_obligations','successor_premise_handoff','interval_coverage','qualified_success_boundary',
        'time_and_reserve_account','watchdog_boundary','phase_handoff','authority_boundary']}
AC_RETURNS = [['RB01'],['RB01','RB02','RB03','RB04','RB05'],['RB02'],['RB02'],['RB02','RB07'],['RB03'],['RB03'],['RB03'],
    ['RB04'],['RB04'],['RB02','RB03','RB04','RB06'],['RB04'],['RB05'],['RB05'],['RB03','RB04','RB05'],['RB01','RB06'],
    ['RB06'],['RB01','RB06'],['RB07'],['RB06','RB07']]
HISTORICAL_LISTS = [
    ('operand_cases','W05','historical_operand_obligations',179),('roots','W05','historical_root_obligations',321),
    ('root_groups','W05','historical_group_obligations',12),('atomic_sites','W05','historical_atomicity_obligations',30),
    ('new_path_families','W05','new_path_family_requirements',12),('allocation_classes','W06','historical_allocation_class_obligations',132),
    ('owner_overlap_pairs','W06','owner_overlap_obligations',55),('historical_activities','W07','historical_activity_obligations',10),
    ('scalar_slots','W07','historical_scalar_slot_obligations',30),('process_phase_vectors','W07','historical_process_phase_vector_obligations',20),
    ('compatibility_joins','W07','historical_compatibility_join_obligations',20),('conditional_phase_premises','W08','historical_conditional_premise_obligations',7)]


def inspect(d):
    plan,acq=rd(PLAN),rd(ACQUISITION);lot=acq['acquisition_lots'][4]
    docs={key:rd(path) for key,path in WORKS.items()};reqs={r['id']:r for r in plan['work_packages'][4:8]}
    assert (d['lot_id'],d['request_id'],d['covers_work_packages'])==('A05','RQ05',list(WORKS))
    assert d['exact_acquisition_lot']==fragment(d['acquisition_lot_binding'])==lot
    gate=d['dependency_gate']
    assert gate['required_lot_ids']==lot['depends_on_lots']==['A03','A04'] and gate['required_external_work_package_ids']==['W03','W04']
    assert gate['exact_prior_effect']==fragment(gate['A04_state_source'])==rd(A04)['current_effect']
    assert all(gate[key] is False for key in ['A01_accepted','A02_accepted','A03_accepted','A04_accepted'])
    truth(gate,['SD01_stop_active','no_documentary_PASS_as_genuine_antecedent','no_send_contact_positive_intake_or_qualification_from_this_preparation'])
    missing(gate)
    order=d['internal_work_order'];edges={key:r['depends_on'] for key,r in reqs.items()}
    assert order['exact_I223_dependencies']==fragment(order['source'])==edges
    assert order['stages']==[['W05'],['W06','W07'],['W08']]
    truth(order,['W06_and_W07_independent_after_W05','W08_after_complete_W04_W05_W06_W07','no_reverse_W09_or_W10_acceptance_dependency'])
    assert type(order['actual_work_packages_accepted']) is int and order['actual_work_packages_accepted']==0
    complete={'W03','W04'}
    for stage in order['stages']:
        assert all(set(edges[key])<=complete for key in stage)
        complete.update(stage)
    draft=d['unsent_request']
    assert draft['original_draft']==lot['unsent_request_draft'] and draft['recipient_role_only']==lot['intended_recipient_role_kind']
    assert draft['required_return_ids']==['RB%02d'%i for i in range(1,8)]
    assert draft['is_draft_only'] is True and draft['sent'] is False and draft['contact_authorized'] is False
    missing(draft)
    rows=d['work_package_requests']
    assert [r['id'] for r in rows]==list(WORKS)
    material_return={'W05':'RB02','W06':'RB03','W07':'RB04','W08':'RB05'}
    for row in rows:
        req=reqs[row['id']]
        assert row['exact_requirement']==fragment(row['source'])==req
        assert row['documentary_checklist']==pin(WORKS[row['id']]) and row['planned_deliverable_id']==req['deliverable_id']
        assert row['primary_review_roles']==req['primary_review_roles'] and row['separate_acceptor_role']==req['separate_acceptor_role']=='R08'
        assert row['required_material_return']==material_return[row['id']]
        missing(row)
    returns=d['requested_returns'];assert [r['id'] for r in returns]==draft['required_return_ids']
    for row,works in zip(returns,[[],['W05'],['W06'],['W07'],['W08'],list(WORKS),list(WORKS)]):
        assert row['requirements'] and row['work_package_ids']==works
        assert row['W_requirement_sources']==[pin(WORKS[key]) for key in works]
        assert fragment(row['universal_delivery_source'])==acq['evidence_delivery_contract']
        missing(row,['actual_received'])
    scope=d['derivation_scope_requirements']
    assert [(r['work_package'],r['section']) for r in scope]==[(key,section) for key,sections in SECTIONS.items() for section in sections]
    assert len(scope)==57
    for row in scope:
        expected=docs[row['work_package']][row['section']]
        assert fragment(row['source'])==expected and row['documentary_container_dimension']==len(expected)
        assert row['container_dimension_not_proof_count_or_complete_bound'] is True
        missing(row)
    dimensions={}
    for key,work,section,count in HISTORICAL_LISTS:
        assert len(docs[work][section])==count
        dimensions[key]=count
    owners=d['heap_owner_requests']
    assert [r['id'] for r in owners]==['H%02d'%i for i in range(1,12)]
    for row,source in zip(owners,docs['W06']['owner_derivation_ledger']):
        assert fragment(row['source'])==source and row['id']==source['id'] and row['owner']==source['owner']
        assert row['candidate_budget_bytes']==source['candidate_budget_bytes'] and row['budget_not_demand_or_capacity'] is True
        assert row['required_return_id']=='RB03'
        missing(row)
    all30=d['W07_all30_boundary']
    assert all30['exact_requirement']==fragment(all30['source'])==docs['W07']['all30_successor_correspondence']
    assert all30['no_invented_group_IDs_or_ten_activities_as_thirty_successor_groups'] is True
    missing(all30)
    phases=d['W08_phase_requests'];assert [r['id'] for r in phases]==['Tpre','Tworker','Tpost']
    for row,source in zip(phases,docs['W08']['phase_derivation_ledger']):
        assert fragment(row['source'])==source and row['candidate_wall_seconds']==source['candidate_wall_seconds']
        assert row['required_return_id']=='RB05'
        missing(row)
    algebra=docs['W08']['formal_phase_algebra']
    assert algebra['marker_order']==['t0','tR','tW','tF']
    assert algebra['phase_difference_coefficients']==[[-1,1,0,0],[0,-1,1,0],[0,0,-1,1]]
    assert [sum(column) for column in zip(*algebra['phase_difference_coefficients'])]==algebra['telescoped_coefficients']==[-1,0,0,1]
    assert algebra['formal_identity_verified'] is True
    assert all(algebra[key] is False for key in ['actual_marker_order_or_nonnegativity_verified','actual_complete_temporal_coverage_verified','actual_successful_execution_existence_or_liveness_verified'])
    assert len(d['critical_boundaries'])==18 and all(value is True for value in d['critical_boundaries'].values())
    routes=d['material_routes']
    assert routes['existing_derivations']['required_returns']==['RB%02d'%i for i in range(1,7)]
    assert routes['existing_derivations']['actual_delivery_inventory'] is None and routes['existing_derivations']['actual_route_accepted'] is False
    gap=routes['missing_derivations'];assert gap['required_return_id']=='RB07'
    truth(gap,['SD04_SD05_stop_if_any_incomplete_unbounded_or_incompatible_term','exact_missing_term_scope_requirement_dependency_and_separate_authority_required',
        'gap_not_acceptance_no_unknown_as_zero_or_reserve_payment','no_execution_profiling_probe_or_quota_change_to_fill_gap'])
    missing(gap,['actual_work_performed'])
    delivers=d['deliverable_coverage'];exits=d['exit_coverage']
    assert len(delivers)==len(exits)==12
    for field,which in [('deliverable_coverage','deliverables'),('exit_coverage','exit_predicates')]:
        expected_rows=[(key,i,text) for key,req in reqs.items() for i,text in enumerate(req[which])]
        for row,(key,i,text) in zip(d[field],expected_rows):
            assert row['work_package']==key and fragment(row['source'])==text
            assert row['id']==key+('-D' if which=='deliverables' else '-X')+'%02d'%(i+1)
            assert row['exact_requirement' if which=='deliverables' else 'exact_predicate']==text
            if which=='deliverables':
                assert row['required_material_return']==material_return[key] and row['authority_return_id']=='RB01' and row['review_return_id']=='RB06'
            else:
                assert row['required_acceptance_criteria']==['AC%02d'%n for n in range(1,21)]
            missing(row)
    criteria=d['acceptance_checklist'];assert [r['id'] for r in criteria]==['AC%02d'%i for i in range(1,21)]
    for row,required in zip(criteria,AC_RETURNS):
        assert row['criterion'] and row['required_return_ids']==required
        assert row['disposition']=='PENDING_A03_A04_COMPLETE_GENUINE_DERIVATIONS_AND_COMPETENT_DECISIONS'
        missing(row)
    material=d['actual_material_state']
    assert material['actual_received_inventory'] is None and material['provided_real_bodies']==material['rejected_real_bodies']==[]
    assert type(material['actual_evaluations']) is int and material['actual_evaluations']==0
    assert material['actual_derivations_or_bounds_or_qualification_evidence'] is None and material['actual_provider_schedule_or_duration_guarantee'] is None
    assert material['actual_qualification_execution_profiling_WCET_probe_or_clock_sampling_performed'] is False and material['actual_global_resource_fit_or_success900_verified'] is False
    resource=d['preserved_resource_rules']
    assert resource['exact_requirement']==fragment(resource['source'])==acq['preserved_resource_and_cost_rules']
    truth(resource,['requested_committed_availability_service_and_demand_need_complete_same_scope_derivations',
        'no_quota_budget_reserve_transfer_or_resource_reservation_applied','no_cap_template_hash_flag_signature_or_documentary_PASS_as_truth'])
    handoff=d['handoff']
    assert handoff['exact_A05_completion_predicate']==lot['completion_predicate'] and handoff['exact_A05_missing_stop']==lot['missing_or_failure_stop']
    assert handoff['next_lot']=='A06' and handoff['required_genuine_prior_lots']==acq['acquisition_lots'][5]['depends_on_lots']==['A02','A03','A04','A05']
    assert handoff['A06_or_RQ06_started_sent_or_accepted'] is False
    assert handoff['exact_final_route_boundary']==fragment(handoff['final_route_source'])==plan['prelaunch_handoff_and_CE12']
    truth(handoff,['W09_joint_review_not_reverse_predecessor_and_not_automatically_closed',
        'no_final_E06_payload_Q_root_admission_claim_receipt_as_new_prelaunch_condition','no_automatic_certificate_PJC115_R2_execution_or_D5_release'])
    missing(handoff,['actual_E01_E05_BASIS_index_or_atomicity_joint_acceptance'])
    change=d['change_control']
    assert change['exact_requirement']==fragment(change['source'])==plan['scope_authentication_and_freeze_order']
    truth(change,['changed_author_body_source_runtime_image_platform_heap_life_work_unit_service_load_epoch_key_policy_invalidates_affected_reviews',
        'no_automatic_old_derivation_proof_approval_or_acceptance_transfer'])
    missing(change,['actual_refresh_or_active_rebind'])
    expected={**rd(A04)['current_effect'],'A05_RQ05_documentary_prepared':True,'A05_accepted':False,'RQ05_sent':False,
        'actual_complete_W05_W08_derivations_or_independent_acceptance_created':False,'actual_A05_intake_progress_or_qualification_performed':False}
    assert d['current_effect']==expected
    assert d['producer']['actor_independent'] is False and d['producer']['competent_R03_R05_R06_review'] is False
    assert d['producer']['separate_R08_acceptance'] is False and d['producer']['external_contacts_made'] is False
    pointers(d)
    return dict(internal_work_dependencies=edges,stages=order['stages'],review_roles_by_work={r['id']:r['primary_review_roles'] for r in rows},
        historical_requirement_dimensions_not_actual_proofs=dimensions,section_counts_by_work={key:len(sections) for key,sections in SECTIONS.items()},
        owner_ids=[r['id'] for r in owners],candidate_phase_seconds={r['id']:r['candidate_wall_seconds'] for r in phases},
        coefficient_identity_only_not_actual_temporal_or_liveness_proof=True,actual_derivations_or_lots_accepted=0,actual_evaluated_material=0)


CRITERIA = [
    'A05/RQ05 preserves I251 four-work-package lot,A03/A04 dependency and negative inherited A01/A02 state.',
    'Preparing/reviewing a conditional draft does not accept antecedents,send/contact,start positive intake or qualify components.',
    'Independent staged graph check preserves W05 first,W06/W07 parallel,W08 after complete dependencies,without reverse W09/W10 edges.',
    'Exact W05-W08 deliverables/exits/rejections/future-authority requirements and planned package IDs are retained.',
    'W05 179 operands,321 roots,12 root groups,30 sites are historical requirements needing genuine exact successor mapping/derivations.',
    'CP03 inherited,written atomicity,ten tests,counts or negative certificates do not transfer acceptance to changed source/runtime.',
    'Twelve new path families,all transitive/process/thread/child/guards/Reader/output/rejection routes need complete coverage.',
    'Correlated metadata/charge/page/alias/original/publication/lock/draft/exception/finalization reasoning remains required for effective sites/routes.',
    'Prior qualification evidence only if genuinely authorized with R04 custody,R05 independent component review and R06 provenance; no new run here.',
    'W06 eleven owners require full cardinality,size,lifetime/peak/transient/process/native/allocator/GC coverage including originals/observer/clones/frames/codecs/output/failures.',
    '132 allocation classes and55 overlaps are recualification obligations,not complete successor proofs or disjoint lifetimes.',
    'Same-state ownership/alias/lifetime derivation or conservative overcount must avoid omission,physical witness merge,double credit or independent-peak subtraction.',
    'Requested H01-H10 and committed/H11 need complete same-state correspondence and independent W04 availability with conserved budgets/reserves.',
    'Serialized/RSS/partial getsizeof/typed caps/quota/reserve do not establish heap,slack or capacity; unknown stays unknown.',
    'W07 genuine all30 correspondence is not ten activities,thirty scalars,twenty vectors or invented group IDs.',
    'Historical10/30/20/20 and seven per-attempt cost families preserve work/CPU/wall/wait/process/phase/compatibility and original/native/failure costs.',
    'Compatible work/service unit or exact-platform WCET requires full conversion theorem,arrivals/backlog/readiness/concurrency/load/cache/memory/delay scope.',
    'CPU sums,wall and wait remain distinct; bytes/visits/MHz/work-over900 and unproved overlap/latency credit do not provide service.',
    'W08 coefficient telescoping is verified algebraically only; actual marker order,coverage,existence/liveness remain unproved.',
    'tW is exact True coordinator wait return,not worker exit/later validation; pre-tR worker work and exit observation gap remain covered obligations.',
    'Success finally/dual writes/closes through tF and independent success checks remain required; True is necessary but insufficient.',
    '60/750/60+30 and nested600/90/60 are budgets,not service/success900; no extra600,borrowed H11/reserve or double nested credit.',
    'No watchdog/deadline/elapsed/timeout/missing marker substitutes success or zero; no universal failure-cleanup900 claim or omitted rejection/traceback costs.',
    'Seven returns,57 pinned sections,twenty criteria,twelve deliverables/exits preserve complete source-bound requirements without claiming proof counts.',
    'Per-work genuine primary reviews and separate R08 are exact; same assistant documentary review supplies neither competence nor independence.',
    'Complete bodies/references/units/all assumptions/provenance/currentness/validity are required; templates,hashes,flags and signatures do not establish truth.',
    'Known authentic authors/bodies/baseline precede W09; W10 final freeze cannot authenticate them retrospectively.',
    'Own W05-W08 acceptance feeds A06/W09 independent E01-E05/BASIS/index/atomicity join,never automatic resource closure or own accepted predecessor.',
    'RB07 and SD04/SD05 retain no admission for incomplete,unbounded,incompatible or overbudget proof without profiling/experimental WCET/probe/run/quota changes.',
    'Both Readers/global costs and changed-scope invalidation remain exact with no free offline work or old-proof/approval transfer/rebind.',
    'A06 remains stopped and CE12/final E06/payload/Q/root/admission/claim/receipt are not new prelaunch conditions.',
    'Negative I122/CP07/component/PJC115-R2/D5/IR03 state remains intact without actual material,execution,quota/reserve or authority change.'
]


def reconstruct():
    d=rd(SUBJECT);result=inspect(d)
    pins={**d['input_pins'],**{path:sha(path) for path in sorted(PRIOR_FILES)}}
    assert len(pins)==1107
    verify_blobs(pins)
    return dict(schema='d5.i262-source-reconstruction.v1',increment='I262',date=DATE,timezone='Europe/Madrid',base_commit=BASE,
        subject=pin(SUBJECT),input_pins=pins,independent_reconstruction=result,
        criteria=[dict(id='RV%02d'%(i+1),criterion=text,result='PASS_DOCUMENTARY_REQUIREMENT_ONLY') for i,text in enumerate(CRITERIA)],
        current_effect={**d['current_effect'],'A05_RQ05_documentary_reviewed':True})


def own_rejections(d):
    cases=[
        ('antecedent_omitted',('dependency_gate','required_lot_ids'),['A04']),('A04_accepted',('dependency_gate','A04_accepted'),True),
        ('work_stage_order_reversed',('internal_work_order','stages'),[['W05'],['W08'],['W06','W07']]),
        ('request_sent',('unsent_request','sent'),True),('work_omitted',('work_package_requests',),d['work_package_requests'][:-1]),
        ('W05_role_removed',('work_package_requests',0,'primary_review_roles'),['R03','R06']),
        ('scope_section_omitted',('derivation_scope_requirements',),d['derivation_scope_requirements'][:-1]),
        ('historical_count_changed',('derivation_scope_requirements',1,'documentary_container_dimension'),178),
        ('scope_count_as_proof',('derivation_scope_requirements',0,'container_dimension_not_proof_count_or_complete_bound'),False),
        ('owner_omitted',('heap_owner_requests',),d['heap_owner_requests'][:-1]),
        ('owner_budget_changed',('heap_owner_requests',3,'candidate_budget_bytes'),1),
        ('owner_bound_fabricated',('heap_owner_requests',10,'actual_requested_committed_upper_or_fit'),0),
        ('all30_mapping_invented',('W07_all30_boundary','actual_successor_group_inventory_or_mapping'),[]),
        ('phase_omitted',('W08_phase_requests',),d['W08_phase_requests'][:-1]),
        ('phase_bound_fabricated',('W08_phase_requests',1,'actual_finite_wall_upper_seconds'),750),
        ('history_transferred',('critical_boundaries','historical_counts_and_CP03_written_atomicity_tests_or_certificate_not_successor_acceptance'),False),
        ('original_costs_waived',('critical_boundaries','originals_observer_clones_memo_frames_tracebacks_codecs_Readers_outputs_native_allocator_GC_lives_all_required'),False),
        ('overlap_credit_allowed',('critical_boundaries','same_state_peak_alias_ownership_or_conservative_overcount_no_omission_double_credit_or_physical_witness_merge'),False),
        ('ten_activities_as_all30',('critical_boundaries','all30_successor_requirement_not_10_activities_30_scalar_slots_20_vectors_or_predictive_IDs'),False),
        ('CPU_wall_conflated',('critical_boundaries','CPU_sums_wall_wait_process_windows_service_backlog_readiness_load_memory_cache_and_delays_explicit'),False),
        ('formal_identity_as_liveness',('critical_boundaries','telescoping_identity_or_sum_budgets_not_order_coverage_service_liveness_or_success900'),False),
        ('exit_as_tW',('critical_boundaries','exact_True_wait_return_not_physical_exit_or_later_validation_worker_pre_tR_and_finally_to_tF_covered'),False),
        ('True_as_success',('critical_boundaries','True_necessary_not_sufficient_watchdog_elapsed_timeout_missing_marker_not_success_or_zero'),False),
        ('extra600_allowed',('critical_boundaries','no_extra_600_per_activity_group_process_thread_window_or_category_no_double_nested_reserve'),False),
        ('W09_closed_early',('critical_boundaries','own_W05_W08_reviews_acceptances_not_W09_joint_E01_E05_BASIS_index_closure'),False),
        ('gap_as_authority',('material_routes','missing_derivations','actual_new_action_authority'),'UNVERIFIED_TEST_LABEL'),
        ('return_omitted',('requested_returns',),d['requested_returns'][:-1]),
        ('deliverable_review_waived',('deliverable_coverage',5,'review_return_id'),'RB03'),
        ('criterion_omitted',('acceptance_checklist',),d['acceptance_checklist'][:-1]),
        ('criterion_accepted',('acceptance_checklist',16,'accepted'),True),
        ('exit_coverage_waived',('exit_coverage',11,'required_acceptance_criteria'),['AC01']),
        ('inventory_fabricated',('actual_material_state','actual_received_inventory'),[]),
        ('success900_verified',('actual_material_state','actual_global_resource_fit_or_success900_verified'),True),
        ('quota_changed',('preserved_resource_rules','no_quota_budget_reserve_transfer_or_resource_reservation_applied'),False),
        ('A06_dependency_removed',('handoff','required_genuine_prior_lots'),['A05']),
        ('claim_as_own_prerequisite',('handoff','exact_final_route_boundary','claim_not_its_own_precondition'),False),
        ('old_derivation_transferred',('change_control','no_automatic_old_derivation_proof_approval_or_acceptance_transfer'),False),
        ('A05_accepted',('current_effect','A05_accepted'),True)]
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
    return dict(schema='d5.i262-documentary-review.v1',increment='I262',date=DATE,timezone='Europe/Madrid',base_commit=BASE,status=STATUS,
        subject=pin(SUBJECT),reconstruction=pin(RECON),
        verdict='NO_NEW_DOCUMENTARY_DEFECT_FOUND_A05_RQ05_CONSISTENT_COMPLETE_GENUINE_DERIVATIONS_AND_ACCEPTANCE_MISSING',findings=[],
        criteria=rec['criteria'],independent_reconstruction=rec['independent_reconstruction'],
        counts=dict(input_pins=1107,work_packages=4,scope_sections=57,heap_owners=11,phase_requests=3,requested_returns=7,acceptance_criteria=20,
            deliverables=12,exits=12,review_criteria=len(CRITERIA),actual_received_bodies=0,actual_complete_derivations_accepted=0,actual_lots_accepted=0,
            prelaunch_gates_closed=0,resource_obligations_closed=0),
        inherited_I261_rejection_checks=prep['rejection_checks'],additional_I262_rejection_checks=own_rejections(rd(SUBJECT)),
        clarifications=[
            'A03/A04 and inherited A01/A02 remain unaccepted,SD01 active. Conditional unsent draft is not positive intake,new qualification,proof or independent acceptance.',
            'Source-bound179/321/12/30,132 classes/55 overlaps,10/30/20/20 dimensions and57 section lengths remain requirements,not complete successor proof-body counts or all30 coverage.',
            'W05 precedes independent W06/W07 stages; W08 then needs complete compatible W04/W05/W06/W07. Own reviews are exact per work with separate R08; W09/W10 are not reverse predecessors.',
            'Heap requested/committed/H11 and independent available capacity need same-state full derivations. Conservative overcount is allowed without omission,double credit or unproved subtraction; partial models/reserve/RSS do not establish fit.',
            'All30 successor correspondence needs genuine complete scope and compatible service/WCET with all work/CPU/wait/process/window costs; old ten activities or invented group IDs cannot stand in for it.',
            'Coefficient telescoping is independently verified as a formal identity only. Actual order,coverage,liveness and qualified success remain unproved; tW is exact True wait return,not physical exit,and finally extends to tF.',
            'Complete own W05-W08 packages feed independent W09/A06 E01-E05/BASIS/index/atomicity join. Their preparation or hypothetical acceptance does not close that join or grant final execution.',
            'RB07/SD04/SD05 records incomplete/incompatible/unbounded/overbudget premises without execution,profiling,experimental WCET,probe or quota/reserve changes. Same assistant review supplies no competent R03/R05/R06 or separate R08 decision.'],
        source_reconstruction=dict(primary_source_checks=True,I261_candidate_and_preparation_reproduced=True,prior_publication_mains_called=False,
            prior_Path_exists_restored=True,no_new_presence_projection=True),current_effect=rec['current_effect'],
        provenance=dict(identity='Same Codex assistant/chat as I261',documentary_review_only=True,actor_independent=False,
            competent_R03_R05_R06_review=False,separate_R08_acceptance=False,external_contacts_made=False),
        limitations=['A03/A04/A05 remain unaccepted with inherited A01/A02,SD01 active,RQ05 unsent. No complete derivation,qualification evidence or actual review/acceptance supplied.',
            'This is no source/atomicity/heap/work/service/phase fit or successful900 proof. All actual authors/bodies/provenance/premises and independent decisions remain missing.',
            'Thirty gates,E01-E05 and D5 remain open. No product/component run,profiling,experimental WCET,probe,contact,signing,configuration,claim,receipt,quota,reserve,binding or active authority/destination change.'],
        work_unit=dict(rollback_files=sorted(FILES),verification_command='python3 docs/validation/D5-I262-audit.py',expected_result=STATUS,
            runtime_harness='N/A: own documentary JSON/Git/hash/pointer/order/requirement checks,formal coefficient arithmetic and in-memory documentary mutations only. No target import/compile/discovery/tests/execution/build/profiling/benchmark/experimental WCET/crypto/signing/keygen/enrollment/provisioning/contacts/platform/clock/CPU/IO/ledger/process/endpoint/replay/crash probes or configuration.',
            over400_lines=True,reason='Single A05/RQ05 review across four W05-W08 handoffs with primary-source reconstruction,pins,rejection checks and preservation; overage declared,no PR requested.'),
        publication=dict(commit_and_push_requested=True,publication_not_derivation_qualification_resource_acceptance_authority_execution_or_D5_closure=True))


def main():
    rec=reconstruct();assert rec==rd(RECON)
    review=build_review(rec);assert review==rd(REVIEW)
    prior=rd(PRIOR_SEAL);preserved={**prior['preserved_published794'],**prior['artifacts'],PRIOR_SEAL:sha(PRIOR_SEAL)}
    assert len(preserved)==799
    seal=rd(SEAL)
    assert seal['schema']=='d5.i262-integrity.v1' and seal['base_commit']==BASE
    assert seal['preserved_published799']==preserved and set(seal['artifacts'])==FILES-{SEAL}
    for mapping in [preserved,seal['artifacts']]:
        for path,digest in mapping.items():
            assert sha(path)==digest,path
    assert seal['source_only'] is True and seal['current_effect']==rec['current_effect']
    changed=set(git('diff',BASE,'--name-only').splitlines())|set(git('ls-files','--others','--exclude-standard').splitlines())
    assert changed==FILES,changed
    subprocess.check_call(['git','merge-base','--is-ancestor',BASE,'HEAD'],cwd=ROOT)
    if git('rev-parse','HEAD')!=BASE:
        assert not git('status','--porcelain')
    print(json.dumps(dict(status=STATUS,increment='I262',input_pins=1107,preserved_published_files=799,new_files=5,review_criteria=len(CRITERIA),
        inherited_rejections=len(review['inherited_I261_rejection_checks']),additional_rejections=len(review['additional_I262_rejection_checks']),findings=review['findings'],
        SD01_stop_active=True,prelaunch_gates_closed=0,resource_obligations_closed=0,D5_closed=False,git_head=git('rev-parse','HEAD')),sort_keys=True))


if __name__=='__main__':
    main()
