#!/usr/bin/env python3
"""I238 W07 methodological review. Documentary JSON/Git only; no target execution."""
import copy
import hashlib
import io
import json
import runpy
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
P = 'docs/validation/'
BASE = '7360aec9aeefc1660c17a7afda09b718a606970f'
DATE = '2026-11-24'
PLAN = P+'D5-I223-PRELAUNCH-RESOURCE-CLOSURE-PLAN.json'
CE01 = P+'D5-I197-CE01-SCOPE-AND-DECISION-BOUNDARY-CANDIDATE-02.json'
CE07 = P+'D5-I193-CE07-RESOURCE-AND-COMPATIBILITY-JOIN-CANDIDATE.json'
CONTRACT = P+'D5-I130-PLATFORM-CONTRACT-CANDIDATE.json'
P06 = P+'D5-PFC126-03-E03-WORK-GROUPS.json'
P06_REVIEW = P+'D5-I164-P06-documentary-review.json'
P07 = P+'D5-PFC126-03-E03-E04-COMPATIBILITY.json'
P07_REVIEW = P+'D5-I166-P07-documentary-review.json'
W04 = P+'D5-I223-W04-CALLER-PLATFORM-SERVICE-CANDIDATE.json'
W05 = P+'D5-I223-W05-SUCCESSOR-REQUALIFICATION-CANDIDATE.json'
PACK = P+'D5-I191-CALLER-IMAGE-CUSTODY-SCHEMAS-CANDIDATE.json'
PRIOR_AUDIT = P+'D5-I237-audit.py'
PRIOR_PREP = P+'D5-I237-preparation-review.json'
PRIOR_SEAL = P+'D5-I237-integrity.json'
PRIOR_DOC = 'docs/design/D5-I237-W07-SUCCESSOR-WORK-CPU-UNITS.md'
SUBJECT = P+'D5-I223-W07-SUCCESSOR-WORK-CPU-UNITS-CANDIDATE.json'
PRIOR_FILES = {SUBJECT,PRIOR_AUDIT,PRIOR_PREP,PRIOR_SEAL,PRIOR_DOC}
RECON = P+'D5-I238-I237-source-reconstruction.json'
REVIEW = P+'D5-I238-I237-documentary-review.json'
AUDIT = P+'D5-I238-audit.py'
SEAL = P+'D5-I238-integrity.json'
DOC = 'docs/design/D5-I238-I237-W07-REVIEW.md'
FILES = {RECON,REVIEW,AUDIT,SEAL,DOC}
STATUS = 'PASS_STATIC_SOURCE_ONLY_W07_REVIEW_WORK_CPU_UNITS_MISSING_NOT_ADMITTED'


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


# These checks reconstruct the obligations from primary documentary sources,
# independently of the I237 candidate builder and its mutation validator.
def inspect(d):
    plan, contract, p06, p07 = rd(PLAN), rd(CONTRACT), rd(P06), rd(P07)
    w = plan['work_packages'][6]
    assert fragment(d['work_package_binding']) == w
    for field, source in [('required_deliverables','deliverables'),('required_exit_predicates','exit_predicates'),('reject_if','reject_if'),('needs_separate_future_authority_for','needs_separate_future_authority_for')]:
        assert d[field] == w[source], field
    assert d['dependency_gate']['required_package_ids'] == w['depends_on'] == ['W03','W04','W05']
    assert d['dependency_gate']['SD01_stop_active'] is True
    assert all(d['dependency_gate'][k+'_accepted'] is False for k in ['W01','W02','W03','W04','W05','W06'])
    assert d['role_scope_matrix'] == [r for r in rd(CE01)['role_scope_matrix'] if r['id'] in ['R03','R06','R08']]
    assert d['actual_work_WCET_authors_provider_or_review_authority'] is None
    activities = contract['cost_coverage']['activities']
    rows = d['historical_activity_obligations']
    assert len(rows) == len(activities) == 10
    for i, (row, source) in enumerate(zip(rows,activities)):
        assert row['id'] == source['id'] and row['historical_activity'] == source == fragment(row['source'])
        assert fragment(row['plan_task']) == plan['work_activity_proof_tasks'][i]
    slots = d['historical_scalar_slot_obligations']
    expected = [(a['id'], kind, '/cost_coverage/activities/'+str(i)+'/'+field) for i,a in enumerate(activities)
        for field,kind in [('verified_work_upper','WORK'),('verified_CPU_seconds_upper','CPU_SECONDS'),('verified_wall_seconds_upper','WALL_SECONDS')]]
    assert len(slots) == 30
    assert [(r['historical_activity_id'],r['required_kind'],r['source']['json_pointer']) for r in slots] == expected
    assert all(fragment(r['source']) is None for r in slots)
    source_lists = [
        ('historical_process_phase_vector_obligations', p06['per_process_phase_work_vectors_and_units']['vectors'],20),
        ('historical_compatibility_join_obligations',p07['exact_runtime_platform_process_unit_match']['joins'],20),
        ('latency_owner_obligations',p07['latency_owner_map_without_unproved_deductions']['owners'],10),
        ('phase_category_obligations',p07['CPU_IO_child_scheduler_and_native_delay_bounds']['per_phase_categories'],9)]
    for key, sources, count in source_lists:
        assert len(d[key]) == len(sources) == count, key
        for row, source in zip(d[key],sources):
            assert row['historical_requirement'] == source == fragment(row['source']), key
    vectors = p06['per_process_phase_work_vectors_and_units']['vectors']
    joins = p07['exact_runtime_platform_process_unit_match']['joins']
    for vector,join in zip(vectors,joins):
        assert vector['id'] == join['id']
        assert (vector['group_id'],vector['process_set_id'],vector['phase']) == (join['group'],join['process_set'],join['phase'])
    for key in ['historical_activity_obligations','historical_scalar_slot_obligations']+[r[0] for r in source_lists]+['per_attempt_cost_ledger']:
        for row in d[key]:
            assert row['accepted'] is False
            assert all(v is None for k,v in row.items() if k.startswith('actual_')), key
            if 'compatible' in row:
                assert row['compatible'] is False
    all30 = d['all30_successor_correspondence']
    assert fragment(all30['source']) == rd(CE07)['work_join']
    assert all30['historical_ten_activities_thirty_scalar_slots_twenty_vectors_not_thirty_successor_groups'] is True
    assert all30['no_predictive_group_IDs_or_scope_reduction'] is True
    assert all30['accepted'] is False and all(v is None for k,v in all30.items() if k.startswith('actual_'))
    route = d['work_service_or_WCET_boundary']
    source = p07['work_to_service_conversion_or_WCET_derivation']
    assert route['required_conditional_routes'] == source['conditional_routes']
    assert route['forbidden_shortcuts'] == source['forbidden_shortcuts']
    assert len(route['required_conditional_routes']) == 2 and len(route['forbidden_shortcuts']) == 6
    assert all(v is None for k,v in route.items() if k.startswith('actual_'))
    for key in ['workload_arrivals_backlog_readiness_concurrency_service_windows_and_validity_require_justification',
        'L_plus_W_over_r_only_if_applicable_theorem_complete_work_and_service_premises_proved',
        'CPU_rate_gives_CPU_execution_not_automatic_wall','CPU_sum_wait_and_wall_are_distinct',
        'no_MHz_cores_quota_frequency_budget_watchdog_or_work_over900_as_service',
        'no_unproved_parallel_overlap_subtraction_or_double_latency_credit']:
        assert route[key] is True, key
    scope = d['scope_and_complete_work_boundary']
    assert scope['exact_W05_closure_requirements'] == rd(W05)['coverage_completeness']
    assert scope['all_original_import_native_crypto_codec_allocation_GC_destruction_locks_IO_children_threads_transitives_and_rejected_routes_required'] is True
    assert scope['historical_P06_P07_and_I124_kernel_counts_not_successor_work_WCET_or_infeasibility_proof'] is True
    assert scope['bytes_clones_visits_generations_process_opportunities_not_instructions_or_seconds'] is True
    assert scope['no_33_generation_immediate_GC_or_free_noncopy_tail'] is True
    costs = rd(CE07)['per_attempt_cost_coverage']
    assert len(d['per_attempt_cost_ledger']) == 7
    assert [r['required_scope'] for r in d['per_attempt_cost_ledger']] == costs['required_terms']
    for r in d['per_attempt_cost_ledger']:
        assert r['required_scope'] == fragment(r['source'])
    boundary = d['per_attempt_cost_boundary']
    assert boundary['exact_required_coverage'] == costs
    for key in ['both_coordinator_and_worker_Reader_ledgers_and_global_join_required',
        'input_file_byte_envelopes_not_all_IO_or_CPU_and_snapshots_not_fresh_reads',
        'every_added_custody_bootstrap_frame_output_ledger_failure_and_cleanup_operation_charged',
        'offline_enrollment_build_prior_facts_not_free_required_verification',
        'unknown_work_wait_native_IO_scheduling_or_latency_not_zero']:
        assert boundary[key] is True, key
    service = d['service_dependency']
    assert service['preserved_missing_W04_service'] == rd(W04)['actual_service_state']
    assert service['actual_same_scope_runtime_platform_service_memory_cache_load_and_unit_compatibility'] is None
    assert all(v is None or v is False for v in d['actual_whole_work_and_time'].values())
    interval = d['interval_and_budget_boundary']
    assert interval['required_interval_rule'] == contract['cost_coverage']['interval_rule']
    for key,value in interval['exact_cost_rules'].items():
        assert value == contract['cost_coverage'][key]
    assert len(interval['exact_cost_rules']) == 7
    for key in ['normative_markers','ordered_interval_rule','success_path_qualification']:
        assert interval[key] == contract['time'][key]
    assert interval['candidate_phase_budgets'] == contract['time']['phase_budgets']
    assert interval['candidate_worker_partition'] == contract['time']['worker_service_partition']
    assert interval['reserve_accounting'] == contract['reserve_accounting']
    assert interval['required_worker_inequality'] == p07['worker_category_upper_vector_and_coverage_inequality']['required_inequality']
    assert interval['candidate_end_to_end_seconds'] == 900 and interval['candidate_unassigned_reserve_seconds'] == 30
    assert interval['reserve_transfers_applied'] == 0 and interval['resources_reserved'] is False and interval['quotas_or_budgets_changed'] is False
    for key in ['worker_pre_main_and_post_RELEASE_receipt_before_parent_tR_must_be_covered',
        'physical_exit_to_exact_True_wait_return_tW_observation_remains_inside_Tworker',
        'success_finally_validation_and_dual_writes_to_tF_required',
        'C10_is_crosscutting_inside_phases_not_free_tail_or_extra_budget',
        'no_extra_600_for_C04_Tpre_or_per_group_process_thread_window_category']:
        assert interval[key] is True, key
    assert interval['actual_worker_inequality_proved'] is False
    assert all(v is None for k,v in interval.items() if k.startswith('actual_') and k != 'actual_worker_inequality_proved')
    handoff = d['phase_handoff']
    assert handoff['exact_plan_order'] == plan['scope_authentication_and_freeze_order']
    assert fragment(handoff['W05_work_handoff']) == rd(W05)['resource_handoff'][1]
    assert fragment(handoff['W08_consumer']) == plan['work_packages'][7]
    assert fragment(handoff['W09_joint_acceptance']) == plan['work_packages'][8]
    assert plan['work_packages'][5]['depends_on'] == w['depends_on']
    assert {'W06','W07'} <= set(plan['work_packages'][7]['depends_on'])
    for key in ['W06_memory_and_W07_work_are_parallel_inputs_to_W08_without_reverse_baseline_dependency',
        'memory_cache_allocator_interference_assumptions_must_be_reconciled_and_justified_not_automatically_borrowed',
        'W07_does_not_prove_W06_heap_or_W08_success900_or_W09_E01_E05_acceptance',
        'genuine_effective_baseline_known_authors_bodies_assumptions_before_W09_required',
        'W10_freeze_reconciles_same_facts_and_changes_invalidate_affected_bounds',
        'final_freeze_C_mapping_E06_payload_Q_root_claim_receipt_not_sole_antecedent_proof']:
        assert handoff[key] is True, key
    assert handoff['final_route_boundary'] == plan['prelaunch_handoff_and_CE12']
    assert handoff['actual_positive_work_service_BASIS_index_proof_record_created'] is False
    assert handoff['actual_refresh_or_active_rebind'] is False
    assert d['authority_boundary']['inherited_boundary'] == plan['authorization_boundary']
    assert d['authority_boundary']['no_product_components_import_compile_test_discovery_WCET_experiment_benchmarks_probes_schedule_or_service_sampling'] is True
    assert d['authority_boundary']['actual_external_material_provider_authority_or_measurement'] is None
    assert [r['predicate'] for r in d['exit_predicate_dispositions']] == w['exit_predicates']
    for row in d['exit_predicate_dispositions']:
        assert row['predicate'] == fragment(row['source']) and row['accepted'] is False
        assert all(v is None for k,v in row.items() if k.startswith('actual_'))
    assert d['preserved_scope_and_gates'] == {k:plan[k] for k in ['inherited_scope_boundaries','preserved_negative_gates','prelaunch_handoff_and_CE12']}
    for key,value in d['current_effect'].items():
        if key == 'W07_documentary_prepared':
            assert value is True
        elif key == 'IR03':
            assert value == 'NOT_READY'
        elif key in ['actual_evidence_accepted','work_packages_accepted','prelaunch_gates_closed','resource_obligations_closed']:
            assert type(value) is int and value == 0
        else:
            assert value is False, key
    check_pointers(d)


CRITERIA = [
    'Exact W07 deliverables, dependency gate, exit predicates and future experimental authority',
    'R03/R06 requirements and separate R08 acceptance remain unassigned',
    'Ten historical activities match I130 and I223 without successor equivalence',
    'Thirty scalar slots are ten work/CPU/wall triplets, all unknown',
    'Twenty P06 vectors retain exact group/process/phase requirements',
    'Twenty P07 compatibility joins match all twenty vectors without qualified units',
    'Ten latency owners and nine phase/category requirements remain unproved',
    'I193 all30 requirement remains; no predictive group IDs or reduced scope',
    'Complete W05 original/native/transitive/failure work coverage required',
    'Conditional I124 counts do not supply successor instructions, seconds or infeasibility',
    'Service and exact-platform WCET are conditional alternatives, neither selected',
    'Compatible units, arrivals, backlog, concurrency and service-window theorem required',
    'CPU execution, summed CPU, waiting and elapsed wall remain distinct',
    'No overlap subtraction, free unknown latency or budget-derived service',
    'Seven per-attempt families include both Readers, verification, frames and dual output',
    'File-byte envelopes and snapshots do not prove all IO, CPU or fresh reads',
    'Missing W04 service and complete whole-work bounds remain missing',
    'I130 tR/tW/tF intervals preserve early worker work, reap observation and successful finally',
    'C10 stays within phase composition; candidate 600/90/60 and 60/750/60 are not proofs',
    'Thirty-second reserve remains unassigned, with no transfers or extra per-group budget',
    'W06 and W07 are parallel inputs to W08; memory/cache/interference assumptions need reconciliation',
    'W08 success900, W09 joint acceptance and W10/final trust phases remain separate',
    'Inherited scope exclusions, negative gates, CE12 boundary and no-execution authority retained']


def reconstruct():
    d = rd(SUBJECT)
    inspect(d)
    pins = {**d['input_pins'],**{p:sha(p) for p in sorted(PRIOR_FILES)}}
    assert len(pins) == 987
    verify_blobs(pins)
    return dict(schema='d5.i238-source-reconstruction.v1',increment='I238',date=DATE,base_commit=BASE,
        subject=pin(SUBJECT),input_pins=pins,criteria=[dict(id='RV%02d'%(i+1),criterion=t,result='PASS_DOCUMENTARY_REQUIREMENT_ONLY') for i,t in enumerate(CRITERIA)],
        counts=dict(input_pins=987,historical_activities=10,historical_scalar_slots=30,historical_process_phase_vectors=20,
            historical_compatibility_joins=20,latency_owner_requirements=10,phase_category_requirements=9,per_attempt_cost_families=7,
            unassigned_review_roles=3,pending_exits=3,review_criteria=len(CRITERIA)),
        current_effect={**d['current_effect'],'W07_documentary_reviewed':True})


def own_rejections(d):
    cases = [
        ('scalar_kind_relabel',('historical_scalar_slot_obligations',0,'required_kind'),'WALL_SECONDS'),
        ('vector_drop',('historical_process_phase_vector_obligations',),d['historical_process_phase_vector_obligations'][:-1]),
        ('latency_owner_drop',('latency_owner_obligations',),d['latency_owner_obligations'][:-1]),
        ('unknown_WCET_zero',('historical_process_phase_vector_obligations',0,'actual_WCET_upper_seconds'),0),
        ('arrivals_premise_dropped',('work_service_or_WCET_boundary','workload_arrivals_backlog_readiness_concurrency_service_windows_and_validity_require_justification'),False),
        ('native_closure_dropped',('scope_and_complete_work_boundary','all_original_import_native_crypto_codec_allocation_GC_destruction_locks_IO_children_threads_transitives_and_rejected_routes_required'),False),
        ('bytes_as_all_IO',('per_attempt_cost_boundary','input_file_byte_envelopes_not_all_IO_or_CPU_and_snapshots_not_fresh_reads'),False),
        ('C10_extra_budget',('interval_and_budget_boundary','C10_is_crosscutting_inside_phases_not_free_tail_or_extra_budget'),False),
        ('borrowed_memory_premises',('phase_handoff','memory_cache_allocator_interference_assumptions_must_be_reconciled_and_justified_not_automatically_borrowed'),False),
        ('freeze_change_no_invalidation',('phase_handoff','W10_freeze_reconciles_same_facts_and_changes_invalidate_affected_bounds'),False)]
    results = []
    for name,path,value in cases:
        mutant = copy.deepcopy(d)
        node = mutant
        for key in path[:-1]:
            node = node[key]
        node[path[-1]] = value
        try:
            inspect(mutant)
        except AssertionError:
            results.append(dict(case=name,result='REJECTED_DOCUMENTARY_MUTATION_IN_MEMORY'))
        else:
            raise AssertionError(name)
    return results


def build_review(rec):
    previous = runpy.run_path(str(ROOT/PRIOR_AUDIT))
    exists = Path.exists
    assert previous['build_candidate']() == rd(SUBJECT)
    prep = previous['build_review']()
    assert prep == rd(PRIOR_PREP) and Path.exists is exists
    extra = own_rejections(rd(SUBJECT))
    return dict(schema='d5.i238-documentary-review.v1',increment='I238',date=DATE,timezone='Europe/Madrid',base_commit=BASE,
        status=STATUS,subject=pin(SUBJECT),reconstruction=pin(RECON),
        verdict='DOCUMENTARY_REQUIREMENTS_CONSISTENT_NO_NEW_DEFECT_FOUND_REAL_W07_EVIDENCE_MISSING_NOT_ADMITTED',findings=[],
        counts=rec['counts'],criteria=rec['criteria'],
        documentary_clarifications=[
            'Ten historical activities / thirty scalar slots / twenty vectors do not satisfy all30 successor coverage. Genuine complete correspondence remains absent.',
            'Work counts become time only through a complete applicable service theorem or justified exact-platform WCET; summed CPU does not bound wall by itself.',
            'Both Readers, freshness/crypto/identity, frame failures, native/GC/destruction and successful dual writes remain charged per attempt; unknown is not zero.',
            'tR is parent RELEASE close; earlier post-receipt worker work belongs to Tpre. tW is exact True wait_worker return; tF includes successful finally. No extra CPU600 or reserve credit.',
            'W06 and W07 feed W08 in parallel. Their memory/cache/load/interference premises require genuine reconciliation; W07 does not qualify W04 service, prove900 or accept E01-E05.',
            'SD01 and all genuine appointments/evidence/acceptances remain open. Future freeze, bundle, Q/root/claim/receipt cannot substitute antecedent authority or evidence.'],
        source_reconstruction=dict(primary_source_checks=True,I237_candidate_and_preparation_reproduced=True,
            prior_publication_mains_called=False,prior_Path_exists_restored=True,no_new_presence_projection=True),
        inherited_I237_rejection_checks=prep['rejection_checks'],additional_I238_rejection_checks=extra,
        current_effect=rec['current_effect'],
        provenance=dict(identity='Same Codex assistant/chat as I237',methodological_documentary_review_only=True,
            actor_independent=False,competent_R03_review=False,competent_R06_review=False,separate_R08_acceptance=False,external_contacts_made=False),
        limitations=['No complete successor activity/process inventory, all30 correspondence, work/CPU/wait/wall upper, compatible unit, qualified service or WCET proof exists in this dossier.',
            'All three W07 exits remain unaccepted; SD01 active, zero accepted real packages, zero closed prelaunch gates and zero closed E01-E05 obligations.',
            'Static audit checks documents, metadata and documentary rejection cases only; it neither executes nor measures product or components.'],
        work_unit=dict(rollback_files=sorted(FILES),verification_command='python3 docs/validation/D5-I238-audit.py',expected_result=STATUS,
            runtime_harness='N/A: only own documentary JSON/Git/hash/source-pointer checks and in-memory document mutations. No product/components, imports, compile, discovery/tests, benchmarks, experimental WCET, service/clock/CPU/IO sampling or probes.',
            over400_lines=True,reason='One review unit with primary-source reconstruction, pinned inputs, negative cases and integrity preservation. Overage declared; no PR requested.'),
        publication=dict(commit_and_push_requested=True,publication_not_resource_attestation_acceptance_or_execution_authority=True))


def main():
    rec = reconstruct()
    assert rec == rd(RECON)
    review = build_review(rec)
    assert review == rd(REVIEW)
    prior = rd(PRIOR_SEAL)
    preserved = {**prior['preserved_published674'],**prior['artifacts'],PRIOR_SEAL:sha(PRIOR_SEAL)}
    assert len(preserved) == 679
    seal = rd(SEAL)
    assert seal['schema'] == 'd5.i238-integrity.v1' and seal['base_commit'] == BASE
    assert seal['preserved_published679'] == preserved and set(seal['artifacts']) == FILES-{SEAL}
    for mapping in [preserved,seal['artifacts']]:
        for path,digest in mapping.items():
            assert sha(path) == digest, path
    assert seal['source_only'] is True and seal['current_effect'] == rec['current_effect']
    changed = set(git('diff',BASE,'--name-only').splitlines()) | set(git('ls-files','--others','--exclude-standard').splitlines())
    assert changed == FILES, changed
    subprocess.check_call(['git','merge-base','--is-ancestor',BASE,'HEAD'],cwd=ROOT)
    if git('rev-parse','HEAD') != BASE:
        assert not git('status','--porcelain')
    print(json.dumps(dict(status=STATUS,increment='I238',input_pins=987,preserved_published_files=679,new_files=5,
        criteria=len(CRITERIA),inherited_documentary_rejections=len(review['inherited_I237_rejection_checks']),
        additional_documentary_rejections=len(review['additional_I238_rejection_checks']),findings=review['findings'],
        SD01_stop_active=True,prelaunch_gates_closed=0,resource_obligations_closed=0,D5_closed=False,git_head=git('rev-parse','HEAD')),sort_keys=True))


if __name__ == '__main__':
    main()
