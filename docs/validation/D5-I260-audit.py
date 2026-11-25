#!/usr/bin/env python3
"""I260 A04/RQ04 documentary review; no target/component execution."""
import copy
import hashlib
import io
import json
from pathlib import Path
import runpy
import subprocess

ROOT = Path(__file__).resolve().parents[2]
P = 'docs/validation/'
BASE = '528d7c52c498001e9a5e76e8b43940d7a1b493b1'
DATE = '2026-11-25'
PLAN = P+'D5-I223-PRELAUNCH-RESOURCE-CLOSURE-PLAN.json'
ACQUISITION = P+'D5-I251-GENUINE-EVIDENCE-ACQUISITION-PLAN.json'
W04 = P+'D5-I223-W04-CALLER-PLATFORM-SERVICE-CANDIDATE.json'
A03 = P+'D5-I251-A03-RQ03-SOURCES-IMAGE-RUNTIME-CANDIDATE.json'
SUBJECT = P+'D5-I251-A04-RQ04-CALLER-PLATFORM-SERVICE-CANDIDATE.json'
PRIOR_PREP = P+'D5-I259-preparation-review.json'
PRIOR_AUDIT = P+'D5-I259-audit.py'
PRIOR_SEAL = P+'D5-I259-integrity.json'
PRIOR_DOC = 'docs/design/D5-I259-A04-RQ04-CALLER-PLATFORM-SERVICE.md'
PRIOR_FILES = {SUBJECT,PRIOR_PREP,PRIOR_AUDIT,PRIOR_SEAL,PRIOR_DOC}
RECON = P+'D5-I260-I259-source-reconstruction.json'
REVIEW = P+'D5-I260-I259-documentary-review.json'
AUDIT = P+'D5-I260-audit.py'
SEAL = P+'D5-I260-integrity.json'
DOC = 'docs/design/D5-I260-I259-A04-RQ04-REVIEW.md'
FILES = {RECON,REVIEW,AUDIT,SEAL,DOC}
STATUS = 'PASS_STATIC_SOURCE_ONLY_A04_RQ04_REVIEW_PREDECESSORS_CALLER_PLATFORM_CAPACITY_SERVICE_PENDING_NOT_ADMITTED'


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
    ['dependency_gate','role_scope_matrix','authority_and_costs'],['caller_policy','requirement_phase_ledger'],['platform_policy'],
    ['service_evidence_ledger','actual_capacity_state','actual_service_state','heap_metric_policy','delay_requirements','candidate_budgets'],
    ['platform_policy','phase_boundary'],['role_scope_matrix','exit_predicate_dispositions','phase_boundary','authority_and_costs'],
    ['authority_and_costs','exit_predicate_dispositions','phase_boundary']]
AC_RETURNS = [['PL01'],['PL01'],['PL02'],['PL02'],['PL03'],['PL04'],['PL04'],['PL04'],['PL04'],['PL05'],['PL05'],
    ['PL02','PL05'],['PL04','PL06'],['PL01','PL06'],['PL03','PL04','PL05','PL06'],['PL06'],['PL07'],['PL01','PL06','PL07']]


def inspect(d):
    plan,acq,w=rd(PLAN),rd(ACQUISITION),rd(W04)
    lot,req=acq['acquisition_lots'][3],plan['work_packages'][3]
    assert (d['lot_id'],d['request_id'],d['work_package'],d['planned_deliverable_id'])==('A04','RQ04','W04',req['deliverable_id'])
    assert d['exact_acquisition_lot']==fragment(d['acquisition_lot_binding'])==lot
    assert d['exact_W04_requirement']==fragment(d['W04_requirement_binding'])==req
    assert d['W04_documentary_checklist']['path']==W04
    gate=d['dependency_gate']
    assert gate['required_lot_ids']==lot['depends_on_lots']==['A02','A03']
    assert gate['required_work_package_ids']==req['depends_on']==['W02','W03']
    assert gate['exact_requirement']==fragment(gate['source'])==w['dependency_gate']
    assert gate['exact_prior_effect']==fragment(gate['A03_state_source'])==rd(A03)['current_effect']
    assert all(gate[key] is False for key in ['A01_accepted','A02_accepted','A03_accepted','W02_accepted','W03_accepted'])
    truth(gate,['SD01_stop_active','no_documentary_PASS_as_genuine_antecedent','no_send_contact_nomination_positive_intake_or_backend_selection_from_this_preparation'])
    missing(gate)
    draft=d['unsent_request']
    assert draft['original_draft']==lot['unsent_request_draft'] and draft['recipient_role_only']==lot['intended_recipient_role_kind']
    assert draft['required_return_ids']==['PL%02d'%i for i in range(1,8)]
    assert draft['is_draft_only'] is True and draft['sent'] is False and draft['contact_authorized'] is False
    missing(draft)
    returns=d['requested_returns']
    assert [r['id'] for r in returns]==draft['required_return_ids']
    for row,sections in zip(returns,RETURN_SECTIONS):
        assert row['requirements'] and row['W04_requirement_sources']==[pin(W04,'/'+key) for key in sections]
        assert fragment(row['universal_delivery_source'])==acq['evidence_delivery_contract']
        missing(row,['actual_received'])
    roles=d['role_evidence_requests']
    assert [r['id'] for r in roles]==['R02','R03','R06','R08']
    for row,source in zip(roles,w['role_scope_matrix']):
        assert row['exact_role_requirement']==fragment(row['source'])==source
        assert row['required_return_ids']==['PL01','PL06']
        missing(row)
    guarantees=d['platform_guarantee_requests']
    assert len(guarantees)==8 and len({r['guarantee'] for r in guarantees})==8
    for row,source in zip(guarantees,w['platform_policy']['guarantee_evidence_inventory']):
        assert row['guarantee']==source['guarantee'] and fragment(row['source'])==source
        assert row['schema_source']==source['schema_source'] and fragment(row['schema_source'])=={'$ref':'#/$defs/evidence_reference'}
        assert row['required_return_id']=='PL03' and len(row['required_fields'])==5
        missing(row,['actual_verified'])
    services=d['service_requests']
    assert [r['id'] for r in services]==['SV%02d'%i for i in range(1,9)]
    for row,source in zip(services,w['service_evidence_ledger']):
        assert fragment(row['source'])==source and row['normative_source']==source['source']
        fragment(row['normative_source'])
        assert row['required_material']==source['required_material'] and row['required_return_id']=='PL04'
        missing(row)
    delays=d['delay_requests']
    assert [r['id'] for r in delays]==['L%02d'%i for i in range(1,9)]
    for row,source in zip(delays,w['delay_requirements']):
        assert row['exact_requirement']==fragment(row['source'])['exact_requirement']==source['exact_requirement']
        assert row['exact_requirement']==fragment(source['source']) and row['required_return_id']=='PL04'
        missing(row)
    phases=d['phase_requirement_requests']
    assert len(phases)==23 and [r['id'] for r in phases]==[r['id'] for r in w['requirement_phase_ledger']]
    for row,source in zip(phases,w['requirement_phase_ledger']):
        assert fragment(row['source'])==source and row['normative_source']==source['source']
        assert row['required_genuine_evidence']==source['exact_requirement']['required_genuine_evidence']==fragment(row['normative_source'])['required_genuine_evidence']
        assert row['consumer_step']==source['consumer_step'] and row['work_package_consumers']==source['work_package_consumers']
        assert row['deferred_from_A04'] is source['deferred_from_W04'] and row['final_route_outside_prelaunch_plan'] is source['final_route_outside_prelaunch_plan']
        expected=[]
        if not row['deferred_from_A04']:
            if row['id'].startswith('CC'):
                expected=['PL05'] if row['id']=='CC07' else ['PL02']
            else:
                expected={'PF01':['PL03'],'PF02':['PL03'],'PF03':['PL05'],'PF04':['PL05'],'PF05':['PL02','PL03'],'PF06':['PL05']}[row['id']]
        assert row['required_return_ids']==expected
        missing(row)
    active=[r for r in phases if not r['deferred_from_A04']];deferred=[r for r in phases if r['deferred_from_A04']]
    assert len(active)==13 and len(deferred)==10
    assert [r['id'] for r in phases if r['final_route_outside_prelaunch_plan']]==['CC12','PF11']
    policies=['caller_policy','platform_policy','heap_metric_policy','candidate_budgets','schema_policy','phase_boundary','authority_and_costs','preserved_scope_and_gates']
    assert list(d['inherited_policies'])==policies
    for key,row in d['inherited_policies'].items():
        assert row['exact_requirement']==fragment(row['source'])==w[key]
    assert w['platform_policy']['clock_currentness']['max_UTC_error_seconds']==5
    assert w['platform_policy']['clock_currentness']['max_snapshot_lifetime_seconds']==3600
    assert w['platform_policy']['global_one_use']['tuple_fields']==['trust_context_sha256','runtime_request_sha256','invocation_id']
    assert w['platform_policy']['global_one_use']['actual_claim_or_receipt_required_for_CE06_mechanism_evidence'] is False
    assert w['caller_policy']['inherited_transport']['explicit_control_pipe_count']==2
    assert w['caller_policy']['inherited_transport']['observed_worker_operand_count']==6
    assert w['schema_policy']['candidate_caller_body_cap_bytes']==8192 and w['schema_policy']['candidate_platform_body_cap_bytes']==16384
    assert len(d['critical_boundaries'])==15 and all(v is True for v in d['critical_boundaries'].values())
    routes=d['material_routes']
    assert routes['existing_material']['required_returns']==['PL%02d'%i for i in range(1,7)]
    assert routes['existing_material']['actual_route_accepted'] is False and routes['existing_material']['actual_delivery_inventory'] is None
    gap=routes['missing_material']
    assert gap['required_return_id']=='PL07'
    truth(gap,['SD03_stop_if_guarantee_capacity_service_clock_durability_or_intrinsic_backend_unproved',
        'exact_missing_body_scope_assumption_requirement_and_separate_work_authority_required',
        'no_measurement_probe_configuration_claim_or_quota_change_to_fill_gap','gap_report_not_acceptance_or_global_infeasibility_proof'])
    missing(gap,['actual_work_performed'])
    delivers=d['W04_deliverable_coverage']
    assert [r['id'] for r in delivers]==['WD01','WD02','WD03']
    for i,row in enumerate(delivers):
        assert row['exact_requirement']==fragment(row['source'])==req['deliverables'][i]
        assert row['required_return_ids']==[['PL02','PL03'],['PL04'],['PL05']][i]
        assert row['authority_return_id']=='PL01' and row['review_return_id']=='PL06'
        missing(row)
    criteria=d['acceptance_checklist'];ids=['AC%02d'%i for i in range(1,19)]
    assert [r['id'] for r in criteria]==ids
    for row,required in zip(criteria,AC_RETURNS):
        assert row['criterion'] and row['required_return_ids']==required
        assert row['disposition']=='PENDING_A02_A03_GENUINE_GUARANTEES_AND_COMPETENT_DECISION'
        missing(row)
    exits=d['W04_exit_coverage']
    assert [r['id'] for r in exits]==['WX01','WX02','WX03']
    for i,row in enumerate(exits):
        assert row['exact_predicate']==fragment(row['source'])==req['exit_predicates'][i]
        assert row['required_acceptance_criteria']==ids
        missing(row)
    material=d['actual_material_state']
    assert material['actual_received_inventory'] is None and material['provided_real_bodies']==material['rejected_real_bodies']==[]
    assert type(material['actual_evaluations']) is int and material['actual_evaluations']==0
    assert material['actual_provider_operator_backend_or_service_selected'] is None and material['actual_schedule_or_duration_guarantee'] is None
    assert all(material[k] is False for k in ['actual_capacity_or_service_guarantee_verified','actual_clock_or_global_ledger_verified','actual_claim_mapping_replay_crash_restart_or_platform_probe_performed'])
    resource=d['preserved_resource_rules']
    assert resource['exact_requirement']==fragment(resource['source'])==acq['preserved_resource_and_cost_rules']
    truth(resource,['all_reference_and_mechanism_costs_in_both_Readers_and_global_join_not_free_offline',
        'no_caps_budgets_or_requested_reserve_as_actual_resource_fit_or_service_success900','no_quota_budget_reserve_transfer_or_resource_reservation_applied'])
    handoff=d['handoff']
    assert handoff['exact_A04_completion_predicate']==lot['completion_predicate'] and handoff['exact_A04_missing_stop']==lot['missing_or_failure_stop']
    assert handoff['next_lot']=='A05' and handoff['required_genuine_prior_lots']==acq['acquisition_lots'][4]['depends_on_lots']==['A03','A04']
    assert handoff['A05_or_RQ05_started_sent_or_accepted'] is False
    assert handoff['exact_final_route_boundary']==fragment(handoff['final_route_source'])==plan['prelaunch_handoff_and_CE12']
    truth(handoff,['prelaunch_not_conditioned_on_actual_final_E06_payload_Q_root_admission_claim_receipt','no_automatic_launch_certificate_PJC115_R2_or_D5_release'])
    missing(handoff,['actual_final_caller_platform_C_mapping_claim_or_receipt_created'])
    change=d['change_control']
    assert change['exact_requirement']==fragment(change['source'])==w['phase_boundary']
    truth(change,['changed_operator_authority_source_runtime_caller_domain_service_load_clock_epoch_key_policy_or_body_invalidates_affected_reviews',
        'no_automatic_old_guarantee_proof_approval_or_acceptance_transfer'])
    missing(change,['actual_refresh_or_active_rebind'])
    expected={**rd(A03)['current_effect'],'A04_RQ04_documentary_prepared':True,'A04_accepted':False,'RQ04_sent':False,
        'actual_caller_platform_capacity_service_clock_or_ledger_guarantees_accepted':False,'actual_backend_selected_or_platform_probed':False,'actual_A04_intake_progress_or_review_records_created':False}
    assert d['current_effect']==expected
    assert d['producer']['actor_independent'] is False and d['producer']['competent_R02_R03_R06_review'] is False
    assert d['producer']['separate_R08_acceptance'] is False and d['producer']['external_contacts_made'] is False
    pointers(d)
    return dict(guarantee_names=[r['guarantee'] for r in guarantees],service_requirements={r['id']:r['required_material'] for r in services},
        delay_kinds={r['id']:r['exact_requirement']['delay'] for r in delays},
        active_phase_requirements=[r['id'] for r in active],deferred_consumers={r['id']:dict(step=r['consumer_step'],works=r['work_package_consumers'],outside_prelaunch=r['final_route_outside_prelaunch_plan']) for r in deferred},
        criterion_to_returns={r['id']:r['required_return_ids'] for r in criteria},actual_guarantees_or_lots_accepted=0,
        actual_provider_backend_or_service_selected=None,actual_material_received=0)


CRITERIA = [
    'A04/RQ04 preserves I251/W04 exact lot,deliverables/exits and A02/A03 genuine dependency with A01 retained.',
    'Conditional documentary preparation/review does not accept predecessors,send/contact or start positive intake/backend selection.',
    'Requester human and software caller remain distinct; genuine actor/image/domain/constructor provenance precedes resource acceptance.',
    'Capability requires intrinsic existing construction/loader/isolation and immutable first entry,not UID/PID/fd/fstat/env/hash/appointment/READY alone.',
    'Two pipes,six worker operands and ownership/duplicate closure/resource scope remain exact without new helpers/channels/ambient trust.',
    'All eight platform guarantee slots require complete enforcement bodies,operator authority,scope/assumptions/validity and actual reviews.',
    'Four roles R02/R03/R06/R08 retain scope/competence/appointments and separate acceptance; same assistant is no independent actor.',
    'Eight service classes preserve exact platform/config/metrics/process/interference/units/delays/load/clock/provider requirements.',
    'Available requested/committed allocator heap is separately attested,not RSS,serialized bytes,virtual reservation,quota or unassigned reserve.',
    'Full coordinator/worker/children/interference/shared resources and native/allocator/GC/lifetime/overlap correspondence remain required.',
    'Compatible work/service units and lower service curve/windows/backlog/readiness/concurrency/latency or exact-platform WCET are required.',
    'CPU time,wall time and process sums remain distinct; MHz/benchmark/budget/deadline/work-divided-by900 prove no service.',
    'All eight delay classes retain scope and bounds,including physical-exit-to-exact-True tW,pre-tR worker work and finally through tF.',
    'Unknown delays are not zero and overlap cannot be subtracted without proof; candidate time/heap budgets remain unproved.',
    'Trusted monotonic/UTC/error/currentness/epoch/revocation and boundary validity rules are preserved without host-date or hidden lookup assumptions.',
    'One authoritative global namespace for C/Q/invocation spans all callers/domains/restarts with atomicity/high-water/durability/rollback/crash/double-spend evidence.',
    'Mechanism proof is not an actual claim,mapping,receipt or replay test; parent/child are one invocation and uncertain/partial claims allow no free retry.',
    'Twenty-three normative phase requirements preserve thirteen W04 requirements and ten deferred,including two outside prelaunch.',
    'Resources W05-W09,freeze W10,C W11,mapping W12,claim/receipt CE12 remain later consumers without reverse acceptance edges.',
    'Capacity/service premises do not establish full program demand,heap,work,phase fit,success900 or the joint E01-E05 acceptance.',
    'Actor/image/caller/platform/capacity/service and authors/bodies must be genuine before W09; W10 final freeze cannot authenticate retrospectively.',
    'Seven returns/eighteen criteria preserve all three deliverables/exits with PL01 authority and PL06 genuine reviews/decision.',
    'Missing intrinsic backend or guarantee/premise invokes PL07/SD03,not authority to probe,measure,configure,claim or change quotas.',
    'Complete bodies/reference instances/bytes/digests/provenance/units/all assumptions and both Readers/global costs remain required without free offline work.',
    'Zero received/evaluated/accepted material and null inventory are not proof of truth,absence globally or infeasibility.',
    'Changed operator/authority/source/runtime/caller/domain/service/load/clock/epoch/key/policy/body invalidates affected reviews without automatic transfer/rebind.',
    'A05/RQ05 requires genuine A03/A04 and remains stopped; CE12/final execution is not a new prelaunch prerequisite.',
    'Negative I122/CP07/component/PJC115-R2/D5/IR03 state remains intact with no product/component execution,quota,reserve or authority change.'
]


def reconstruct():
    d=rd(SUBJECT);result=inspect(d)
    pins={**d['input_pins'],**{path:sha(path) for path in sorted(PRIOR_FILES)}}
    assert len(pins)==1097
    verify_blobs(pins)
    return dict(schema='d5.i260-source-reconstruction.v1',increment='I260',date=DATE,timezone='Europe/Madrid',base_commit=BASE,
        subject=pin(SUBJECT),input_pins=pins,independent_reconstruction=result,
        criteria=[dict(id='RV%02d'%(i+1),criterion=text,result='PASS_DOCUMENTARY_REQUIREMENT_ONLY') for i,text in enumerate(CRITERIA)],
        current_effect={**d['current_effect'],'A04_RQ04_documentary_reviewed':True})


def own_rejections(d):
    cases=[
        ('predecessor_omitted',('dependency_gate','required_lot_ids'),['A03']),('A03_accepted',('dependency_gate','A03_accepted'),True),
        ('request_sent',('unsent_request','sent'),True),('operator_fabricated',('unsent_request','actual_recipient_person'),'UNVERIFIED_TEST_LABEL'),
        ('role_omitted',('role_evidence_requests',),d['role_evidence_requests'][:-1]),
        ('guarantee_omitted',('platform_guarantee_requests',),d['platform_guarantee_requests'][:-1]),
        ('guarantee_duplicated',('platform_guarantee_requests',1,'guarantee'),d['platform_guarantee_requests'][0]['guarantee']),
        ('guarantee_verified',('platform_guarantee_requests',7,'actual_verified'),True),
        ('service_class_omitted',('service_requests',),d['service_requests'][:-1]),
        ('service_unit_fabricated',('service_requests',3,'actual_scope_unit_bound_conditions_or_derivation'),{}),
        ('delay_omitted',('delay_requests',),d['delay_requests'][:-1]),
        ('wait_return_gap_waived',('delay_requests',4,'exact_requirement','delay'),'worker_exit_TEST_LABEL'),
        ('phase_omitted',('phase_requirement_requests',),d['phase_requirement_requests'][:-1]),
        ('resources_required_early',('phase_requirement_requests',7,'deferred_from_A04'),False),
        ('claim_moved_to_prelaunch',('phase_requirement_requests',11,'final_route_outside_prelaunch_plan'),False),
        ('capability_from_fd',('critical_boundaries','caller_requester_principal_and_capability_not_UID_PID_fd_env_hash_READY_or_appointment'),False),
        ('reserve_as_available',('critical_boundaries','attested_available_requested_committed_heap_not_RSS_quota_virtual_reservation_or_candidate_reserve'),False),
        ('MHz_as_service',('critical_boundaries','CPU_work_service_compatible_units_or_exact_platform_WCET_not_MHz_benchmark_deadline_or_work_divided_by900'),False),
        ('load_conditions_omitted',('critical_boundaries','load_cache_memory_windows_backlog_readiness_concurrency_and_process_interference_explicit'),False),
        ('local_ledger_allowed',('critical_boundaries','global_ledger_across_callers_domains_restarts_atomic_durable_high_water_no_double_spend'),False),
        ('clock_error_increased',('inherited_policies','platform_policy','exact_requirement','clock_currentness','max_UTC_error_seconds'),6),
        ('claim_needed_for_mechanism',('inherited_policies','platform_policy','exact_requirement','global_one_use','actual_claim_or_receipt_required_for_CE06_mechanism_evidence'),True),
        ('caller_cap_increased',('inherited_policies','schema_policy','exact_requirement','candidate_caller_body_cap_bytes'),8193),
        ('SD03_waived',('material_routes','missing_material','SD03_stop_if_guarantee_capacity_service_clock_durability_or_intrinsic_backend_unproved'),False),
        ('gap_as_action_authority',('material_routes','missing_material','actual_new_action_authority'),'UNVERIFIED_TEST_LABEL'),
        ('return_omitted',('requested_returns',),d['requested_returns'][:-1]),
        ('deliverable_review_waived',('W04_deliverable_coverage',1,'review_return_id'),'PL04'),
        ('criterion_omitted',('acceptance_checklist',),d['acceptance_checklist'][:-1]),
        ('criterion_accepted',('acceptance_checklist',15,'accepted'),True),
        ('exit_coverage_waived',('W04_exit_coverage',0,'required_acceptance_criteria'),['AC01']),
        ('inventory_fabricated',('actual_material_state','actual_received_inventory'),[]),
        ('service_verified',('actual_material_state','actual_capacity_or_service_guarantee_verified'),True),
        ('offline_costs_free',('preserved_resource_rules','all_reference_and_mechanism_costs_in_both_Readers_and_global_join_not_free_offline'),False),
        ('A05_dependency_removed',('handoff','required_genuine_prior_lots'),['A04']),
        ('claim_as_own_prerequisite',('handoff','exact_final_route_boundary','claim_not_its_own_precondition'),False),
        ('guarantee_transferred',('change_control','no_automatic_old_guarantee_proof_approval_or_acceptance_transfer'),False),
        ('A04_accepted',('current_effect','A04_accepted'),True),('assistant_R08',('producer','separate_R08_acceptance'),True)]
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
    return dict(schema='d5.i260-documentary-review.v1',increment='I260',date=DATE,timezone='Europe/Madrid',base_commit=BASE,status=STATUS,
        subject=pin(SUBJECT),reconstruction=pin(RECON),
        verdict='NO_NEW_DOCUMENTARY_DEFECT_FOUND_A04_RQ04_CONSISTENT_GENUINE_CALLER_PLATFORM_CAPACITY_SERVICE_AND_ACCEPTANCE_MISSING',findings=[],
        criteria=rec['criteria'],independent_reconstruction=rec['independent_reconstruction'],
        counts=dict(input_pins=1097,roles=4,platform_guarantees=8,service_classes=8,delay_classes=8,phase_requirements=23,
            active_A04_requirements=13,deferred_requirements=10,final_route_requirements=2,requested_returns=7,acceptance_criteria=18,
            W04_deliverables=3,W04_exits=3,review_criteria=len(CRITERIA),actual_guarantees_accepted=0,actual_received_bodies=0,actual_lots_accepted=0,
            prelaunch_gates_closed=0,resource_obligations_closed=0),
        inherited_I259_rejection_checks=prep['rejection_checks'],additional_I260_rejection_checks=own_rejections(rd(SUBJECT)),
        clarifications=[
            'A02/A03 and inherited A01 remain unaccepted,SD01 active. Conditional request is unsent and review creates no positive intake,operator/backend selection or caller capability.',
            'Caller needs intrinsic genuine construction/isolation/entry/channel custody before untrusted code; UID/PID/fd/env/hash/appointment/READY alone is no capability or execution permission.',
            'Available requested/committed capacity and compatible service/WCET premises need provider authority,units,process/load/cache/memory/window/backlog/readiness/concurrency/delay evidence. Budgets,reserves,MHz or benchmark are not guarantees.',
            'W04 accepts premises only when genuinely complete; full program demand/heap/work/phase fit and joint E01-E05 remain W05-W09. This separation neither waives the premise proof nor closes resources early.',
            'Global clock/currentness and one-use/durable mechanism evidence is not an actual claim,mapping,receipt,replay or crash test. Parent/child are one invocation; uncertain/partial states permit no free retry.',
            'Thirteen of23 phase requirements belong to W04; ten remain deferred,including CC12/PF11 outside prelaunch. No later resource/freeze/C/mapping/claim acceptance is added as a reverse prerequisite.',
            'Actor/image/caller/platform/capacity/service/authors/bodies must be genuine before W09. W10 finalizes the same facts without retrospective authority or automatic guarantee transfer.',
            'PL07/SD03 keeps no admission when mechanism/premise is unproved. The same assistant review is neither R02/R03/R06 competent review nor separate R08 acceptance,does not fill gaps and grants no operational authority.'],
        source_reconstruction=dict(primary_source_checks=True,I259_candidate_and_preparation_reproduced=True,prior_publication_mains_called=False,
            prior_Path_exists_restored=True,no_new_presence_projection=True),current_effect=rec['current_effect'],
        provenance=dict(identity='Same Codex assistant/chat as I259',documentary_review_only=True,actor_independent=False,
            competent_R02_R03_R06_review=False,separate_R08_acceptance=False,external_contacts_made=False),
        limitations=['A02/A03/A04 remain unaccepted with inherited A01,SD01 active,RQ04 unsent. No actual operator,backend,service,guarantee or material is accepted.',
            'Genuine mechanism/capacity/service/clock/durability/provider bodies and R02/R03/R06/R08 decisions remain missing. This is no attestation,contract issuance,capability or fit proof.',
            'Thirty gates,E01-E05 and D5 remain open. No product/component execution,backend implementation,probe,contact,signing,configuration,claim,receipt,quota,reserve,binding or active authority/destination change.'],
        work_unit=dict(rollback_files=sorted(FILES),verification_command='python3 docs/validation/D5-I260-audit.py',expected_result=STATUS,
            runtime_harness='N/A: own documentary JSON/Git/hash/pointer/guarantee/service/delay/phase checks and in-memory documentary mutations only. No target import/compile/discovery/tests/execution/build/benchmark/crypto/signing/keygen/enrollment/provisioning/contacts/platform/clock/CPU/IO/ledger/process/endpoint/replay/crash/restart probes or configuration.',
            over400_lines=True,reason='Single A04/RQ04 review with primary-source reconstruction,pins,rejection checks and preservation; overage declared,no PR requested.'),
        publication=dict(commit_and_push_requested=True,publication_not_attestation_capability_authority_guarantee_acceptance_execution_or_D5_closure=True))


def main():
    rec=reconstruct();assert rec==rd(RECON)
    review=build_review(rec);assert review==rd(REVIEW)
    prior=rd(PRIOR_SEAL);preserved={**prior['preserved_published784'],**prior['artifacts'],PRIOR_SEAL:sha(PRIOR_SEAL)}
    assert len(preserved)==789
    seal=rd(SEAL)
    assert seal['schema']=='d5.i260-integrity.v1' and seal['base_commit']==BASE
    assert seal['preserved_published789']==preserved and set(seal['artifacts'])==FILES-{SEAL}
    for mapping in [preserved,seal['artifacts']]:
        for path,digest in mapping.items():
            assert sha(path)==digest,path
    assert seal['source_only'] is True and seal['current_effect']==rec['current_effect']
    changed=set(git('diff',BASE,'--name-only').splitlines())|set(git('ls-files','--others','--exclude-standard').splitlines())
    assert changed==FILES,changed
    subprocess.check_call(['git','merge-base','--is-ancestor',BASE,'HEAD'],cwd=ROOT)
    if git('rev-parse','HEAD')!=BASE:
        assert not git('status','--porcelain')
    print(json.dumps(dict(status=STATUS,increment='I260',input_pins=1097,preserved_published_files=789,new_files=5,review_criteria=len(CRITERIA),
        inherited_rejections=len(review['inherited_I259_rejection_checks']),additional_rejections=len(review['additional_I260_rejection_checks']),findings=review['findings'],
        SD01_stop_active=True,prelaunch_gates_closed=0,resource_obligations_closed=0,D5_closed=False,git_head=git('rev-parse','HEAD')),sort_keys=True))


if __name__=='__main__':
    main()
