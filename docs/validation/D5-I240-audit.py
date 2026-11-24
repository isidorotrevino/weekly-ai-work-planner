#!/usr/bin/env python3
"""I240 W08 methodological review. Own documentary checks only; no target execution."""
import copy
import hashlib
import io
import json
import runpy
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
P = 'docs/validation/'
BASE = 'd391a30f85807fa34ce1be28b1e92bd5e0175c86'
DATE = '2026-11-24'
PLAN = P+'D5-I223-PRELAUNCH-RESOURCE-CLOSURE-PLAN.json'
CONTRACT = P+'D5-I130-PLATFORM-CONTRACT-CANDIDATE.json'
CE01 = P+'D5-I197-CE01-SCOPE-AND-DECISION-BOUNDARY-CANDIDATE-02.json'
CE07 = P+'D5-I193-CE07-RESOURCE-AND-COMPATIBILITY-JOIN-CANDIDATE.json'
P08 = P+'D5-PFC126-03-E05-PHASE-BOUNDS.json'
P08_REVIEW = P+'D5-I168-P08-documentary-review.json'
W04 = P+'D5-I223-W04-CALLER-PLATFORM-SERVICE-CANDIDATE.json'
W05 = P+'D5-I223-W05-SUCCESSOR-REQUALIFICATION-CANDIDATE.json'
W06 = P+'D5-I223-W06-SUCCESSOR-HEAP-LIFETIMES-CANDIDATE.json'
W07 = P+'D5-I223-W07-SUCCESSOR-WORK-CPU-UNITS-CANDIDATE.json'
W06_REVIEW = P+'D5-I236-I235-documentary-review.json'
PRIOR_AUDIT = P+'D5-I239-audit.py'
PRIOR_PREP = P+'D5-I239-preparation-review.json'
PRIOR_SEAL = P+'D5-I239-integrity.json'
PRIOR_DOC = 'docs/design/D5-I239-W08-SUCCESSOR-PHASE-BOUNDS.md'
SUBJECT = P+'D5-I223-W08-SUCCESSOR-PHASE-BOUNDS-CANDIDATE.json'
PRIOR_FILES = {SUBJECT,PRIOR_AUDIT,PRIOR_PREP,PRIOR_SEAL,PRIOR_DOC}
RECON = P+'D5-I240-I239-source-reconstruction.json'
REVIEW = P+'D5-I240-I239-documentary-review.json'
AUDIT = P+'D5-I240-audit.py'
SEAL = P+'D5-I240-integrity.json'
DOC = 'docs/design/D5-I240-I239-W08-REVIEW.md'
FILES = {RECON,REVIEW,AUDIT,SEAL,DOC}
STATUS = 'PASS_STATIC_SOURCE_ONLY_W08_REVIEW_PHASE_MARKERS_RESERVES_MISSING_NOT_ADMITTED'


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


def require_missing(row):
    assert all(value is None for key,value in row.items() if key.startswith('actual_'))
    if 'accepted' in row:
        assert row['accepted'] is False


def inspect(d):
    # Read normative sources directly. Replaying the I239 builder is separate.
    plan, contract, old, w07 = rd(PLAN), rd(CONTRACT), rd(P08), rd(W07)
    w, time = plan['work_packages'][7], contract['time']
    assert fragment(d['work_package_binding']) == w and d['work_package'] == 'W08'
    for field, source in [('required_deliverables','deliverables'),('required_exit_predicates','exit_predicates'),('reject_if','reject_if'),('needs_separate_future_authority_for','needs_separate_future_authority_for')]:
        assert d[field] == w[source], field
    gate = d['dependency_gate']
    assert gate['required_package_ids'] == fragment(gate['source']) == w['depends_on'] == ['W04','W05','W06','W07']
    assert gate['SD01_stop_active'] is True and gate['actual_entry_authority_or_accepted_effective_baseline'] is None
    assert all(gate[k+'_accepted'] is False for k in ['W01','W02','W03','W04','W05','W06','W07'])
    assert d['role_scope_matrix'] == [r for r in rd(CE01)['role_scope_matrix'] if r['id'] in ['R03','R06','R08']]
    author = d['authorship_boundary']
    assert author['required_provider_kind'] == w['provider_kind']
    assert author['required_primary_roles'] == w['primary_review_roles'] == ['R03','R06']
    assert author['required_separate_acceptor_role'] == w['separate_acceptor_role'] == 'R08'
    require_missing(author)
    hist = d['historical_reference_boundary']
    for key in ['historical_P08_is_conditional_dossier_not_successor_timing_proof','old_I122_source_anchors_do_not_bind_effective_successor',
        'historical_process_vector_labels_not_actual_PIDs_or_all30_successor_inventory','no_historical_counts_or_old_acceptance_as_successor_bound']:
        assert hist[key] is True, key
    require_missing(hist)
    clock = d['clock_and_marker_obligations']
    assert clock['required_clock_domain'] == time['clock']
    markers = clock['marker_ledger']
    assert [r['id'] for r in markers] == ['t0','tR','tW','tF']
    assert [r['historical_definition'] for r in markers] == time['normative_markers']
    for row in markers:
        assert row['historical_definition'] == fragment(row['source'])
        require_missing(row)
    for key in ['ordered_interval_rule','observation_latency_rule','forbidden_marker_substitutions']:
        assert clock[key] == time[key], key
    assert clock['no_worker_receipt_or_physical_exit_or_later_validation_as_coordinator_marker'] is True
    assert clock['actual_common_monotonic_clock_or_order_proof'] is None
    assert clock['clock_sampled'] is False and clock['markers_instrumented'] is False
    rule = time['ordered_interval_rule']
    assert rule['required_order'] == ['t0','tR','tW','tF']
    assert rule['intervals'] == {'Tpre':'tR-t0','Tworker':'tW-tR','Tpost':'tF-tW'}
    # Independent endpoint incidence reconstruction using strings from I130.
    coeffs = []
    for phase in ['Tpre','Tworker','Tpost']:
        end,start = rule['intervals'][phase].split('-')
        coeffs.append([int(marker==end)-int(marker==start) for marker in rule['required_order']])
    total = [sum(row[i] for row in coeffs) for i in range(4)]
    algebra = d['formal_phase_algebra']
    assert algebra['marker_order'] == rule['required_order']
    assert algebra['phase_difference_coefficients'] == coeffs
    assert algebra['telescoped_coefficients'] == total == [-1,0,0,1]
    assert algebra['formal_identity_verified'] is True
    for key in ['actual_marker_order_or_nonnegativity_verified','actual_complete_temporal_coverage_verified','actual_successful_execution_existence_or_liveness_verified']:
        assert algebra[key] is False, key
    phases = d['phase_derivation_ledger']
    assert len(phases) == 3 and [r['id'] for r in phases] == ['Tpre','Tworker','Tpost']
    for i,(row,source) in enumerate(zip(phases,time['phase_budgets'])):
        assert row['historical_phase_requirement'] == source == fragment(row['source'])
        assert row['candidate_wall_seconds'] == source['candidate_wall_seconds']
        require_missing(row)
        assert row['complete_coverage_verified'] is False
        for field, ref in [('historical_W07_vector_requirements','historical_process_phase_vector_obligations'),('historical_W07_compatibility_requirements','historical_compatibility_join_obligations')]:
            expected = [r for r in w07[ref] if r['historical_requirement']['phase']==row['id']]
            assert [fragment(p) for p in row[field]] == expected
            assert len(expected) == [8,6,6][i]
        v = [fragment(p)['id'] for p in row['historical_W07_vector_requirements']]
        j = [fragment(p)['id'] for p in row['historical_W07_compatibility_requirements']]
        assert v == j and len(v) == len(set(v))
    premises = d['historical_conditional_premise_obligations']
    source = old['verified_Tpre_Tworker_Tpost_upper_seconds']['conditional_theorem']['premises']
    assert len(premises) == 7 and [r['historical_requirement'] for r in premises] == source
    for row in premises:
        assert row['historical_requirement'] == fragment(row['source'])
        assert row['id'] == row['historical_requirement']['id'] and row['satisfied'] is False
        require_missing(row)
    handoff = d['successor_premise_handoff']
    for field,path,key in [('W04_service_and_clock',W04,'actual_service_state'),('W05_complete_scope',W05,'coverage_completeness'),
        ('W06_heap_fit',W06,'availability_and_fit'),('W07_complete_work',W07,'actual_whole_work_and_time'),
        ('W07_compatible_service_or_WCET',W07,'work_service_or_WCET_boundary'),('W07_per_attempt_costs',W07,'per_attempt_cost_boundary')]:
        assert fragment(handoff[field]) == rd(path)[key]
    require_missing(handoff)
    for key in ['all30_successor_work_correspondence_required_without_ten_activity_shortcut',
        'both_Reader_ledgers_global_join_and_every_added_identity_crypto_frame_custody_output_failure_cleanup_cost_required',
        'genuine_same_scope_memory_allocator_cache_load_service_units_and_validity_must_be_justified_and_reconciled',
        'complete_original_native_children_threads_transitives_rejection_prefix_and_traceback_heap_scope_preserved']:
        assert handoff[key] is True, key
    interval = d['interval_coverage']
    assert interval['exact_interval_rule'] == contract['cost_coverage']['interval_rule']
    assert set(interval['exact_cost_rules']) == {'attribution_rule','pre_tR_worker_rule','finally_rule','observation_rule','CPU_wall_rule','noncopy_rule','input_byte_rule'}
    for key,value in interval['exact_cost_rules'].items():
        assert value == contract['cost_coverage'][key]
    for key in ['worker_startup_before_main_and_post_RELEASE_receipt_before_parent_close_tR_must_be_covered_in_Tpre',
        'physical_exit_to_exact_True_wait_return_tW_stays_in_Tworker_even_if_already_exited',
        'cleanup_fresh_after_finish_validation_finally_dual_writes_and_closes_through_normal_tF_required',
        'C10_crosscutting_inside_phases_not_free_tail_or_extra_budget','no_unproved_parallel_overlap_subtraction_or_CPU_sum_as_wall']:
        assert interval[key] is True, key
    require_missing(interval)
    success = d['qualified_success_boundary']
    assert success['exact_qualification'] == time['success_path_qualification']
    assert success['failure_claim'] == time['failure_claim']
    for key in ['True_is_necessary_not_sufficient_for_success','later_checks_do_not_move_tW',
        'False_exception_timeout_nonzero_exit_rejection_invalid_finalization_not_qualified_success',
        'all_four_actual_markers_and_independent_success_checks_required','no_missing_marker_or_unknown_upper_coerced_to_zero',
        'conditional_implication_not_existence_or_liveness_proof',
        'termination_progress_IO_lock_scheduler_retry_signal_and_environment_assumptions_require_justification',
        'no_every_failure_or_cleanup_within900_claim','success_only_timing_does_not_omit_failure_costs_or_rejection_traceback_heap_requirements']:
        assert success[key] is True, key
    require_missing(success)
    account = d['time_and_reserve_account']
    assert account['exact_candidate_rules'] == contract['reserve_accounting']
    assert account['candidate_phase_seconds'] == [p['candidate_wall_seconds'] for p in time['phase_budgets']] == [60,750,60]
    assert sum(account['candidate_phase_seconds']) == account['candidate_phase_sum_seconds'] == 870
    assert account['candidate_unassigned_reserve_seconds'] == time['unassigned_wall_reserve_seconds'] == 30
    assert account['candidate_total_seconds'] == time['success_end_to_end_candidate_seconds'] == 900 == 870+30
    assert account['candidate_worker_partition'] == time['worker_service_partition']
    assert account['required_worker_inequality'] == w07['interval_and_budget_boundary']['required_worker_inequality']
    for key in ['no_extra_600_per_C04_group_process_thread_window_or_category','no_null_paid_by_reserve_or_double_outer_nested_credit','candidate_arithmetic_not_verified_service_capacity_or_success_bound']:
        assert account[key] is True, key
    assert account['actual_phase_uppers'] is None and account['actual_worker_category_vector_or_verified_sum'] is None
    assert account['actual_end_to_end_upper_seconds'] is None and account['actual_success900_proved'] is False and account['actual_infeasibility_proved'] is False
    for key in ['time_reserve_transfers_applied','nested_category_transfers_applied','heap_reserve_transfers_applied']:
        assert type(account[key]) is int and account[key] == 0, key
    assert account['resources_reserved'] is False and account['quotas_or_budgets_changed'] is False
    watchdog = d['watchdog_boundary']
    assert watchdog['historical_watchdog'] == time['current_source_watchdog'] == fragment(watchdog['source'])
    assert watchdog['process_wait900_not_end_to_end_deadline_or_success_liveness_guarantee'] is True
    assert watchdog['new_timer_or_clock_rule_installed'] is False
    phase = d['phase_handoff']
    assert phase['exact_plan_order'] == plan['scope_authentication_and_freeze_order']
    assert fragment(phase['W09_joint_acceptance']) == plan['work_packages'][8]
    assert plan['work_packages'][5]['depends_on'] == plan['work_packages'][6]['depends_on']
    for key in ['W06_and_W07_parallel_inputs_to_W08_not_reverse_dependencies',
        'W08_does_not_qualify_missing_W04_W05_W06_W07_or_accept_W09_E01_E05',
        'genuine_baseline_authors_proof_bodies_assumptions_required_before_W09',
        'W10_freeze_reconciles_same_facts_changes_invalidate_affected_proofs',
        'final_C_mapping_E06_payload_Q_root_claim_receipt_not_sole_antecedent_proof']:
        assert phase[key] is True, key
    assert phase['final_route_boundary'] == plan['prelaunch_handoff_and_CE12']
    assert phase['actual_positive_phase_BASIS_index_record_created'] is False and phase['actual_refresh_or_rebind'] is False
    authority = d['authority_boundary']
    assert authority['inherited_boundary'] == plan['authorization_boundary']
    assert authority['no_product_components_import_compile_discovery_tests_experimental_WCET_benchmarks_probes_clock_CPU_IO_schedule_service_or_platform_sampling'] is True
    assert authority['no_helpers_Reader_members_channels_inputs_outputs_ledger_claim_signing_keygen_enrollment_provisioning_or_contacts'] is True
    require_missing(authority)
    assert [r['predicate'] for r in d['exit_predicate_dispositions']] == w['exit_predicates']
    for row in d['exit_predicate_dispositions']:
        assert row['predicate'] == fragment(row['source'])
        require_missing(row)
    assert d['preserved_scope_and_gates'] == {k:plan[k] for k in ['inherited_scope_boundaries','preserved_negative_gates','prelaunch_handoff_and_CE12']}
    for key,value in d['current_effect'].items():
        if key == 'W08_documentary_prepared':
            assert value is True
        elif key == 'IR03':
            assert value == 'NOT_READY'
        elif key in ['actual_evidence_accepted','work_packages_accepted','prelaunch_gates_closed','resource_obligations_closed']:
            assert type(value) is int and value == 0
        else:
            assert value is False, key
    check_pointers(d)
    return dict(marker_order=rule['required_order'],phase_difference_coefficients=coeffs,telescoped_coefficients=total,
        formal_identity_verified=True,actual_order_coverage_liveness_or_success900_proved=False)


CRITERIA = [
    'W08 deliverables, dependency gate, three exits, rejections and future-authority restriction match I223',
    'Temporal author/service guarantor, R03/R06 and separate R08 remain unassigned',
    'Historical P08 and I122 anchors are not successor proof or source bindings',
    'Four coordinator markers retain exact I130 event definitions and common-clock requirement',
    'Actual marker values, clock identity, instrumentation and sampling remain absent',
    'Endpoint incidence independently confirms telescoping without proving order or liveness',
    'Three phase candidates retain 60/750/60 and unknown actual bounds',
    'Twenty W07 vector references and twenty compatibility references partition 8/6/6 exactly',
    'All seven historical conditional premises remain unsatisfied for the successor',
    'W04 service, W05 closure, W06 heap and W07 work premises retain exact documentary links',
    'All30, both Readers, original/native/transitive/failure costs and heap lifetimes remain required',
    'Memory/cache/load/allocator/service-unit hypotheses require genuine reconciliation',
    'Worker startup and post-receipt work before parent RELEASE close remain within Tpre coverage',
    'Exit-to-exact-True-wait-return observation remains inside Tworker even for an already-exited worker',
    'Cleanup/freshness/validation/finally/dual writes and closes remain through normal tF',
    'C10 stays inside phase composition; no unproved overlap deduction or CPU-as-wall inference',
    'Exact True remains necessary and independent later success qualification does not move tW',
    'Missing markers, timeout, rejection and invalid finalization do not prove qualified success',
    'Conditional success theorem does not establish existence, progress or all-failure deadline',
    'Success-only timing preserves rejected-prefix/traceback heap and failure-cost inventory',
    'Candidate 870+30=900 conserves one reserve and supplies no verified upper',
    'Candidate worker partition and outer/nested reserve rules match I130 without transfers',
    'Historical watchdog is not end-to-end success deadline or liveness guarantee',
    'W06/W07 parallelism, W09 joint acceptance and W10/final trust boundaries remain separate',
    'Inherited exclusions, negative gates, CE12 and no-execution/no-quota authority are preserved']


def reconstruct():
    d = rd(SUBJECT)
    algebra = inspect(d)
    pins = {**d['input_pins'],**{p:sha(p) for p in sorted(PRIOR_FILES)}}
    assert len(pins) == 997
    verify_blobs(pins)
    return dict(schema='d5.i240-source-reconstruction.v1',increment='I240',date=DATE,base_commit=BASE,subject=pin(SUBJECT),input_pins=pins,
        criteria=[dict(id='RV%02d'%(i+1),criterion=t,result='PASS_DOCUMENTARY_REQUIREMENT_ONLY') for i,t in enumerate(CRITERIA)],
        counts=dict(input_pins=997,marker_requirements=4,phase_requirements=3,historical_vector_references=20,historical_compatibility_references=20,
            unsatisfied_conditional_premises=7,unassigned_review_roles=3,pending_exits=3,review_criteria=len(CRITERIA)),
        independent_formal_algebra=algebra,current_effect={**d['current_effect'],'W08_documentary_reviewed':True})


def own_rejections(d):
    cases = [
        ('marker_reorder',('clock_and_marker_obligations','marker_ledger'),list(reversed(d['clock_and_marker_obligations']['marker_ledger']))),
        ('marker_event_substitution',('clock_and_marker_obligations','marker_ledger',2,'historical_definition','event'),'UNVERIFIED_TEST_EXIT_LABEL'),
        ('clock_domain_substitution',('clock_and_marker_obligations','required_clock_domain'),'UNVERIFIED_TEST_DOMAIN'),
        ('algebra_coefficient_corruption',('formal_phase_algebra','telescoped_coefficients'),[-1,0,1,0]),
        ('phase_drop',('phase_derivation_ledger',),d['phase_derivation_ledger'][:-1]),
        ('vector_omission',('phase_derivation_ledger',0,'historical_W07_vector_requirements'),d['phase_derivation_ledger'][0]['historical_W07_vector_requirements'][:-1]),
        ('wrong_phase_join',('phase_derivation_ledger',0,'historical_W07_compatibility_requirements',0),d['phase_derivation_ledger'][1]['historical_W07_compatibility_requirements'][0]),
        ('historical_premise_relabel',('historical_conditional_premise_obligations',0,'id'),'UNVERIFIED_TEST_PREMISE'),
        ('unjustified_liveness',('qualified_success_boundary','termination_progress_IO_lock_scheduler_retry_signal_and_environment_assumptions_require_justification'),False),
        ('reserve_double_credit',('time_and_reserve_account','candidate_total_seconds'),930),
        ('heap_reserve_transfer',('time_and_reserve_account','heap_reserve_transfers_applied'),1),
        ('unknown_end_to_end_zero',('time_and_reserve_account','actual_end_to_end_upper_seconds'),0),
        ('freeze_change_no_invalidation',('phase_handoff','W10_freeze_reconciles_same_facts_changes_invalidate_affected_proofs'),False)]
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
    additional = own_rejections(rd(SUBJECT))
    return dict(schema='d5.i240-documentary-review.v1',increment='I240',date=DATE,timezone='Europe/Madrid',base_commit=BASE,
        status=STATUS,subject=pin(SUBJECT),reconstruction=pin(RECON),
        verdict='DOCUMENTARY_REQUIREMENTS_CONSISTENT_NO_NEW_DEFECT_FOUND_REAL_PHASE_BOUNDS_MISSING_NOT_ADMITTED',findings=[],
        counts=rec['counts'],criteria=rec['criteria'],independent_formal_algebra=rec['independent_formal_algebra'],
        documentary_clarifications=[
            'I130 historical markers and P08 conditional theorem do not bind or time the effective successor. All four actual marker bindings/values and clock guarantees remain missing.',
            'Formal endpoint cancellation verifies only an identity. Complete order, coverage, finite delays, independent success eligibility and nonvacuous liveness still need genuine proof.',
            'Tpre covers worker startup and post-receipt work preceding parent tR; Tworker includes physical-exit-to-exact-True-return delay; Tpost includes successful finally/dual writes to tF.',
            '870+30=900 and 600+90+60=750 preserve candidate accounts only. No unknown bound is zero, service or reserve-funded; no new budget, transfer or timer is applied.',
            'W04/W05/W06/W07 remain unaccepted. Their actual same-scope premises and all30 work mapping are required for W08; W09 alone later joins E01-E05 acceptance.',
            'Success-only timing does not guarantee every failure/cleanup deadline or remove rejection/failure costs and traceback/heap coverage. Final freeze/root/claim cannot replace antecedent evidence.'],
        source_reconstruction=dict(primary_source_checks=True,I239_candidate_and_preparation_reproduced=True,prior_publication_mains_called=False,prior_Path_exists_restored=True,no_new_presence_projection=True),
        inherited_I239_rejection_checks=prep['rejection_checks'],additional_I240_rejection_checks=additional,current_effect=rec['current_effect'],
        provenance=dict(identity='Same Codex assistant/chat as I239',methodological_documentary_review_only=True,actor_independent=False,
            competent_R03_review=False,competent_R06_review=False,separate_R08_acceptance=False,external_contacts_made=False),
        limitations=['No actual source/runtime/clock/service/unit/heap/work/latency/liveness premise or phase bound is supplied; seven premises and three exits remain unaccepted.',
            'SD01 active; zero accepted real evidence packages, zero closed prelaunch gates and zero closed E01-E05 obligations. No infeasibility conclusion is drawn.',
            'Documentary review is not competent independent R03/R06 review or separate R08 acceptance, and authorizes no execution or quota change.'],
        work_unit=dict(rollback_files=sorted(FILES),verification_command='python3 docs/validation/D5-I240-audit.py',expected_result=STATUS,
            runtime_harness='N/A: own documentary JSON/Git/hash/source-pointer/formal-algebra and in-memory document checks only. No target imports/compile/discovery/tests/runs, experimental WCET, clock/CPU/IO/service/schedule/platform sampling/probes or external services/contact.',
            over400_lines=True,reason='One W08 review with primary-source reconstruction, pinned inputs, rejection checks and integrity preservation. Overage declared; no PR requested.'),
        publication=dict(commit_and_push_requested=True,publication_not_temporal_service_attestation_acceptance_or_execution_authority=True))


def main():
    rec = reconstruct()
    assert rec == rd(RECON)
    review = build_review(rec)
    assert review == rd(REVIEW)
    prior = rd(PRIOR_SEAL)
    preserved = {**prior['preserved_published684'],**prior['artifacts'],PRIOR_SEAL:sha(PRIOR_SEAL)}
    assert len(preserved) == 689
    seal = rd(SEAL)
    assert seal['schema'] == 'd5.i240-integrity.v1' and seal['base_commit'] == BASE
    assert seal['preserved_published689'] == preserved and set(seal['artifacts']) == FILES-{SEAL}
    for mapping in [preserved,seal['artifacts']]:
        for path,digest in mapping.items():
            assert sha(path) == digest, path
    assert seal['source_only'] is True and seal['current_effect'] == rec['current_effect']
    changed = set(git('diff',BASE,'--name-only').splitlines()) | set(git('ls-files','--others','--exclude-standard').splitlines())
    assert changed == FILES, changed
    subprocess.check_call(['git','merge-base','--is-ancestor',BASE,'HEAD'],cwd=ROOT)
    if git('rev-parse','HEAD') != BASE:
        assert not git('status','--porcelain')
    print(json.dumps(dict(status=STATUS,increment='I240',input_pins=997,preserved_published_files=689,new_files=5,
        criteria=len(CRITERIA),inherited_documentary_rejections=len(review['inherited_I239_rejection_checks']),
        additional_documentary_rejections=len(review['additional_I240_rejection_checks']),findings=review['findings'],
        SD01_stop_active=True,prelaunch_gates_closed=0,resource_obligations_closed=0,D5_closed=False,git_head=git('rev-parse','HEAD')),sort_keys=True))


if __name__ == '__main__':
    main()
