#!/usr/bin/env python3
"""I212 static CE07 source/requirement/phase review; no product/components."""
import hashlib
import io
import json
import runpy
import subprocess
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
P = 'docs/validation/'
BASE = '3a65291e3dd02d68c964bbc868d7a9a38ef22713'
DOS = P+'D5-I193-CE07-RESOURCE-AND-COMPATIBILITY-JOIN-CANDIDATE.json'
PLAN = P+'D5-I193-CALLER-IMAGE-CUSTODY-EVIDENCE-PLAN.json'
SPEC = P+'D5-I191-CALLER-IMAGE-CUSTODY-CONTRACT-CANDIDATE.json'
CONTRACT = P+'D5-I130-PLATFORM-CONTRACT-CANDIDATE.json'
CRITERIA = P+'D5-I131-E01-E05-review.json'
TASKS = P+'D5-I132-E01-E05-evidence-plan.json'
BINDINGS = P+'D5-I177-FOUR-BINDINGS-EVIDENCE-PLAN.json'
WORK = P+'D5-PFC126-03-E03-WORK-GROUPS.json'
CE06 = P+'D5-I193-CE06-PLATFORM-CLOCK-GLOBAL-LEDGER-CANDIDATE.json'
PREVIOUS = P+'D5-I211-audit.py'
PRIOR_PREP = P+'D5-I211-preparation-review.json'
PRIOR_SEAL = P+'D5-I211-integrity.json'
PRIOR_DOC = 'docs/design/D5-I211-CE07-RESOURCE-COMPATIBILITY-JOIN.md'
PRIOR_FILES = {DOS, PREVIOUS, PRIOR_PREP, PRIOR_SEAL, PRIOR_DOC}
RECON = P+'D5-I212-I211-source-reconstruction.json'
REVIEW = P+'D5-I212-I211-documentary-review.json'
AUDIT = P+'D5-I212-audit.py'
SEAL = P+'D5-I212-integrity.json'
DOC = 'docs/design/D5-I212-I211-CE07-REVIEW.md'
FILES = {RECON, REVIEW, AUDIT, SEAL, DOC}
STATUS = 'PASS_STATIC_SOURCE_ONLY_RESOURCE_EVIDENCE_MISSING'


def rd(p):
    return json.loads((ROOT/p).read_text())


def sha(p):
    return hashlib.sha256((ROOT/p).read_bytes()).hexdigest()


def git(*args):
    return subprocess.check_output(['git', *args], cwd=ROOT, text=True).strip()


def pin(p, pointer=''):
    return dict(path=p, sha256=sha(p), json_pointer=pointer)


def fragment(source):
    assert source['sha256'] == sha(source['path'])
    value = rd(source['path'])
    for token in source.get('json_pointer','').split('/')[1:]:
        key = token.replace('~1','/').replace('~0','~')
        value = value[int(key)] if isinstance(value,list) else value[key]
    return value


def verify_blobs(pins):
    stream = io.BytesIO(subprocess.check_output(['git','cat-file','--batch'],cwd=ROOT,
        input=''.join(BASE+':'+p+'\n' for p in sorted(pins)).encode()))
    for p,h in sorted(pins.items()):
        header = stream.readline().decode().split()
        assert len(header) == 3 and header[1] == 'blob', p
        body = stream.read(int(header[2]))
        assert stream.read(1) == b'\n'
        assert hashlib.sha256(body).hexdigest() == h == sha(p), p
    assert stream.read() == b''


def ancestor_sets(graph):
    active = set()
    done = {}
    def visit(n):
        assert n in graph and n not in active, n
        if n in done:
            return done[n]
        active.add(n)
        result = set()
        for parent in graph[n]:
            result.add(parent)
            result.update(visit(parent))
        active.remove(n)
        assert n not in result
        done[n] = result
        return result
    for n in graph:
        visit(n)
    return done


def require_missing(row):
    for key in ['actual_scope_binding','actual_provider','actual_proof_sha256','actual_proof_bytes',
                'actual_derivation','actual_assumptions','actual_reviewer','actual_acceptance']:
        assert row[key] is None, (row.get('id'),key)
    assert row['accepted'] is False


def reconstruct():
    d = rd(DOS)
    plan = rd(PLAN)
    step = plan['steps'][6]
    contract = rd(CONTRACT)
    prior_requirements = rd(CRITERIA)['obligations']
    ce6 = rd(CE06)
    pins = {**d['input_pins'], **{p:sha(p) for p in sorted(PRIOR_FILES)}}
    assert len(pins) == 857
    verify_blobs(pins)
    assert step['id'] == d['step'] == 'CE07' and step['candidate_dossier_path'] == DOS
    assert d['plan_binding'] == pin(PLAN,'/steps/6')
    for target,source in [('required_evidence','required_evidence'),
                          ('planned_acceptance_checks','acceptance_checks'),
                          ('authorization_boundary','authorization_boundary'),
                          ('contract_rules','contract_rules')]:
        assert d[target] == step[source]
    assert len(d['required_evidence']) == 4 and len(d['planned_acceptance_checks']) == 3
    assert d['schema_boundary']['record_families'] == step['record_families'] == []
    assert d['schema_boundary']['dossier_is_not_positive_I191_record']
    assert d['schema_boundary']['no_new_positive_record_schema_or_authority_created']
    assert d['schema_boundary']['actual_codec_crypto_or_schema_validation'] == 'NOT_RUN_NO_ACTUAL_BODY'
    paths = [row['path'] for row in d['documentary_inventory']]
    assert len(paths) == len(set(paths)) == 41
    for source in d['documentary_inventory']:
        assert pins[source['path']] == source['sha256'] == sha(source['path'])
    dependencies = d['dependency_gates']
    assert [g['step'] for g in dependencies] == step['depends_on'] == ['CE04','CE05','CE06']
    for g in dependencies:
        s = next(s for s in plan['steps'] if s['id'] == g['step'])
        assert g['dossier'] == pin(s['candidate_dossier_path'])
        assert fragment(g['review'])['current_effect']['independent_acceptance'] is False
        assert g['documentary_baseline_reviewed'] and not g['competent_acceptance'] and not g['actual_dependency_satisfied']
    assert len(d['E01_E05_join']) == len(prior_requirements) == 5
    criterion_ids = []
    historical_results = Counter()
    for i,(row,original) in enumerate(zip(d['E01_E05_join'],prior_requirements)):
        assert row['id'] == original['id'] == 'E%02d'%(i+1)
        assert fragment(row['source']) == original
        assert row['complete_requirement'] == original['needed'] and row['historical_status'] == original['status']
        assert row['closed'] is False and row['successor_status'] == 'MISSING_COMPLETE_EXACT_SCOPE_REQUALIFICATION'
        require_missing(row)
        for j,criterion in enumerate(original['criteria']):
            current = d['all20_criterion_join'][i*4+j]
            assert current['id'] == criterion['id'] and current['obligation'] == original['id']
            assert fragment(current['source']) == criterion
            assert current['historical_description'] == criterion['description']
            assert current['historical_result'] == criterion['result']
            assert current['successor_result'] == 'MISSING_NOT_TRANSFERRED'
            assert current['closes_resource_obligation'] is False
            require_missing(current)
            criterion_ids.append(current['id'])
            historical_results[criterion['result']] += 1
    assert len(d['all20_criterion_join']) == len(set(criterion_ids)) == 20
    tasks = rd(TASKS)['tasks']
    assert len(d['historical_I132_task_join']) == len(tasks) == 20
    for i,(row,task) in enumerate(zip(d['historical_I132_task_join'],tasks)):
        assert row['id'] == task['id'] and row['obligations'] == task['obligations']
        assert row['source'] == pin(TASKS,'/tasks/'+str(i))
        path = task['planned_output']
        assert row['existing_historical_dossier'] == pin(path) and path in paths
        assert row['bytes'] == (ROOT/path).stat().st_size and row['currently_exists'] is True
        assert row['historical_plan_output_created'] == task['output_created'] is False
        assert row['historical_output_accepted_as_successor_proof'] is False
        assert row['successor_proof_sha256'] is None and row['output_rewritten'] is False
    historical = rd(P+'D5-I172-P10-documentary-review.json')['acceptance']
    assert historical['resource_obligations_closed'] == 0 and not historical['all_E01_E05_verified']
    heap = d['heap_join']
    assert len(heap['owners']) == len(contract['heap']['owner_budgets']) == 11
    for row,owner in zip(heap['owners'],contract['heap']['owner_budgets']):
        assert fragment(row['source']) == owner
        assert row['id'] == owner['id'] and row['owner'] == owner['owner']
        assert row['candidate_budget_bytes'] == owner['candidate_budget_bytes']
        assert row['candidate_budget_applied'] is False
        for k in ['complete_requested_upper_bytes','complete_committed_upper_bytes','lifetime_allocator_native_GC_overlap_derivation']:
            assert row[k] is None
        require_missing(row)
    for k in ['whole_requested_upper_bytes','whole_committed_upper_bytes','available_host_capacity_bytes','capacity_attestation','complete_derivation']:
        assert heap[k] is None
    for k in ['unknown_terms_coerced_to_zero','finite_bound_claimed','capacity_verified']:
        assert heap[k] is False
    assert heap['both_processes_threads_native_GC_allocator_and_transient_lifetimes_required']
    assert heap['owner_overlap_and_all_original_children_required'] and heap['typed_body_or_Reader_caps_not_whole_heap_proof']
    work = d['work_join']
    assert len(work['activities']) == len(contract['cost_coverage']['activities']) == work['historical_activity_count'] == 10
    scalar_slots = []
    for row,activity in zip(work['activities'],contract['cost_coverage']['activities']):
        assert fragment(row['source']) == row['historical_activity'] == activity and row['id'] == activity['id']
        for measure in ['work','CPU_seconds','wall_seconds']:
            assert row['successor_complete_'+measure+'_upper'] is None
            assert activity['verified_'+measure+'_upper'] is None
            scalar_slots.append(row['id']+':'+measure)
        require_missing(row)
    assert len(set(scalar_slots)) == work['required_scalar_upper_slots'] == 30
    vectors = fragment(work['legacy_process_phase_vectors'])['vectors']
    assert len(vectors) == 20 and len({v['id'] for v in vectors}) == 20
    for k in ['successor_complete_activity_inventory','thirty_distinct_successor_groups_or_reviewed_correspondence',
              'compatible_units','complete_derivation','whole_work_upper','whole_CPU_seconds_upper','whole_wall_seconds_upper']:
        assert work[k] is None
    for k in ['plan_all30_work_groups_requirement_preserved','thirty_upper_slots_do_not_alone_satisfy_plan_all30_groups',
              'sum_CPU_is_not_wall_duration','no_unproved_overlap_subtraction','exact_runtime_platform_and_service_compatibility_required']:
        assert work[k] is True
    assert not work['complete_verified']
    qualification = d['requalification']
    assert qualification['required_legacy_scope'] == dict(operand_cases=179,roots=321,root_groups=12,atomic_sites=30)
    for k in ['actual_qualified_case_inventory','successor_effective_source_runtime_loader_caller_ledger_crypto_closure',
              'actual_complete_new_custody_bootstrap_output_failure_path_inventory']:
        assert qualification[k] is None
    assert qualification['component_status'] == 'NOT_RUN'
    assert qualification['qualification_authorized'] is False and qualification['SOURCE_CAPACITY_VERIFIED_issued'] is False
    for k in ['legacy_counts_are_requirements_not_successor_proof','inherited_CP03_does_not_transfer',
              'source_atomicity_implementation_is_not_accepted_atomicity','ten_component_tests_are_not_complete_resource_evidence']:
        assert qualification[k] is True
    cost = d['per_attempt_cost_coverage']
    assert len(cost['required_terms']) == 7 and cost['per_process_Reader_ledger_count'] == 2
    assert cost['global_join_required'] and cost['all_terms_charged_inside_t0_launch_worker_finish']
    assert cost['offline_enrollment_build_facts_not_free_verification'] and not cost['any_term_assumed_free']
    assert cost['actual_cost_derivations'] is None and cost['actual_IO_or_service_guarantees'] is None
    time = d['time_join']
    assert fragment(time['candidate_source']) == contract['time']
    assert time['unchanged_candidate_phase_budgets'] == contract['time']['phase_budgets']
    budgets = [p['candidate_wall_seconds'] for p in contract['time']['phase_budgets']]
    assert budgets == [60,750,60] and time['candidate_unassigned_reserve_seconds'] == 30
    assert sum(budgets)+time['candidate_unassigned_reserve_seconds'] == time['candidate_success_seconds'] == 900
    for k in ['compatible_clock_service_IO_scheduler_observation_guarantees','complete_phase_derivations','successful_completion_upper_seconds']:
        assert time[k] is None
    assert time['success_within900_verified'] is False and time['reserve_transfers'] == 0 and not time['reservations_created']
    assert time['ordered_60_750_60_plus_30_is_budget_not_proof'] and time['watchdog_counter_deadline_or_elapsed_time_not_success_proof']
    assert 'exact True wait_worker return tW' in time['marker_rule'] and 'finally' in time['marker_rule']
    assert contract['time']['success_path_qualification']['wait_True_is_not_capture_success']
    assert contract['cost_coverage']['interval_rule'] == contract['time']['ordered_interval_rule']
    assert contract['time']['ordered_interval_rule']['required_order'] == ['t0','tR','tW','tF']
    assert contract['time']['ordered_interval_rule']['intervals'] == dict(Tpre='tR-t0',Tworker='tW-tR',Tpost='tF-tW')
    assert contract['time']['ordered_interval_rule']['no_uncovered_exit_observation_gap']
    assert contract['time']['success_path_qualification']['later_checks_never_move_tW']
    assert contract['time']['success_path_qualification']['no_missing_marker_or_time_coerced_to_zero']
    assert [m['id'] for m in contract['time']['normative_markers']] == ['t0','tR','tW','tF']
    assert contract['time']['normative_markers'][2]['source_anchor']['kind'] == 'CALL_RETURN_EXACT_TRUE'
    assert all(m['clock_value'] is None for m in contract['time']['normative_markers'])
    proof = d['accepted_prior_proof_join']
    for k in ['actual_BASIS_proof_record','actual_index_proof_records','exact_final_source_image_runtime_binding','authentic_prior_authentication']:
        assert proof[k] is None
    assert proof['accepted_by_R03_R06_and_separate_R08'] is False
    assert all(proof[k] is True for k in ['predictive_flags_typed_indices_or_placeholder_hashes_are_not_proof',
        'final_E06_or_final_root_must_not_supply_sole_antecedent_proof','qualifying_and_final_runs_separate_not_authorized',
        'no_automatic_prior_negative_or_positive_certificate_transfer'])
    pending_bindings = []
    for row,original in zip(d['I177_binding_reference'],rd(BINDINGS)['four_binding_plan']):
        assert fragment(row['source']) == original
        assert row['id'] == original['id'] and row['path'] == original['path']
        assert not (ROOT/row['path']).exists()
        assert row['actual_body_sha256'] is None and row['actual_body_bytes'] is None
        assert all(row[k] is False for k in ['actual_artifact_created','accepted','execution_authorized'])
        pending_bindings.append(row['id'])
    assert pending_bindings == ['B01','B02','B03','B04']
    graph = {s['id']:s['depends_on'] for s in plan['steps']}
    closure = ancestor_sets(graph)
    assert closure['CE07'] == {'CE01','CE02','CE03','CE04','CE05','CE06'}
    assert not {'CE08','CE09','CE10','CE11','CE12'} & closure['CE07']
    phase = d['phase_boundary']
    assert phase['CE07_complete_evidence_and_prior_proof_required_before_acceptance']
    assert not phase['CE07_requires_future_C_mapping_final_root_or_receipt_as_predecessor']
    assert phase['CE11_does_not_depend_on_CE12'] and 'CE12' not in closure['CE11']
    assert phase['CE12_separate_authorization_full_admission_and_actual_claim_before_receipt']
    assert phase['external_prerequisites_for_receipt'] == plan['closure_boundaries']['external_prerequisites_for_receipt']
    for row in phase['steps']:
        original = next(s for s in plan['steps'] if s['id'] == row['step'])
        assert row['depends_on'] == original['depends_on'] and row['record_families'] == original['record_families']
        assert all(row[k] is False for k in ['accepted','current_execution_authorized','actual_records_available'])
    assert all((ROOT/s['candidate_dossier_path']).exists() for s in plan['steps'][:7])
    assert all(not (ROOT/s['candidate_dossier_path']).exists() for s in plan['steps'][7:])
    for k in ['CE08_final_records_and_scope_freeze_not_created_now','CE09_exact_C_projection_not_created_now',
              'CE10_unique_mapping_bundle_not_created_now']:
        assert phase[k] is True
    effect = d['current_effect']
    for k,v in effect.items():
        if k == 'CE07_documentary_prepared':
            assert v is True
        elif k == 'IR03':
            assert v == 'NOT_READY'
        elif k in ['actual_evidence_accepted','resource_obligations_closed']:
            assert v == 0 and type(v) is int
        else:
            assert v is False, k
    assert d['decision'] == plan['decision'] and d['E06'] == plan['E06']
    assert d['permission_boundary']['denied_action_classes'] == ce6['permission_boundary']['denied_action_classes']
    assert len(d['permission_boundary']['denied_action_classes']) == 14
    assert d['inherited_scope_boundaries'] == ce6['inherited_scope_boundaries']
    assert d['preserved_negative_gates'] == ce6['preserved_negative_gates']
    assert len(d['inherited_scope_boundaries']['S01_exclusions']) == 8
    assert [r['id'] for r in d['role_scope_matrix']] == step['provenance_and_role']['primary_review_roles'] == ['R03','R06','R08']
    for row in d['role_scope_matrix']:
        assert row['assigned_person'] is None and not row['accepted_appointment'] and row['current_actions_authorized'] == []
    for gate in d['preserved_negative_gates']:
        source = {**gate['source'],'json_pointer':gate['json_pointer']}
        assert fragment(source) == gate['observed_value']
    previous = runpy.run_path(str(ROOT/PREVIOUS))
    assert previous['build_review']() == rd(PRIOR_PREP)
    original_exists = Path.exists
    assert git('ls-tree','--name-only',previous['BASE'],'--',DOS) == ''
    assert git('ls-tree','--name-only',BASE,'--',DOS) == DOS
    with previous['predecessor_CE07_presence_as_of_base']():
        assert not (ROOT/DOS).exists()
    assert Path.exists is original_exists and (ROOT/DOS).exists()
    class DocumentaryProbe(Exception):
        pass
    try:
        with previous['predecessor_CE07_presence_as_of_base']():
            raise DocumentaryProbe()
    except DocumentaryProbe:
        pass
    assert Path.exists is original_exists and (ROOT/DOS).exists()
    rule_sections = {
        'K04':['requalification','E01_E05_join','dependency_gates'],
        'K05':['requalification','accepted_prior_proof_join','historical_I132_task_join'],
        'K06':['dependency_gates','accepted_prior_proof_join','phase_boundary'],
        'K08':['accepted_prior_proof_join','phase_boundary','inherited_scope_boundaries'],
        'K12':['phase_boundary','I177_binding_reference','accepted_prior_proof_join'],
        'K15':['per_attempt_cost_coverage','heap_join','work_join','time_join'],
        'K16':['schema_boundary','inherited_scope_boundaries','current_effect']}
    assert list(rule_sections) == d['contract_rules']
    rule_review = []
    for rule_id,sections in rule_sections.items():
        index,rule = next((i,r) for i,r in enumerate(rd(SPEC)['rules']) if r['id'] == rule_id)
        rule_review.append(dict(id=rule_id,rule=rule['rule'],source=pin(SPEC,'/rules/'+str(index)),
            candidate_sections=[pin(DOS,'/'+section) for section in sections],
            documentary_requirement_preserved=True,actual_rule_satisfied=False))
    return dict(schema='d5.i212-i211-source-reconstruction.v1',increment='I212',date='2026-11-17',base_commit=BASE,
        input_pins=pins, method='Fresh fixed Git blobs; direct I193/I191/I130/I131/I132/I177 criteria, ownership, cost-slot, interval and antecedent reconstruction. I211 documentary build reproduced without prior publication mains.',
        rule_review=rule_review, historical_criterion_results=dict(sorted(historical_results.items())),
        coverage=dict(obligation_ids=[r['id'] for r in d['E01_E05_join']],criterion_ids=criterion_ids,
            historical_task_ids=[t['id'] for t in tasks],heap_owner_ids=[r['id'] for r in heap['owners']],
            historical_work_CPU_wall_slots=scalar_slots,historical_process_phase_vector_ids=[v['id'] for v in vectors],
            plan_all30_groups_or_reviewed_correspondence_missing=True,slots_not_qualified_successor_groups=True,
            current_inventory_sources=41,actual_successor_inventory_or_derived_bounds_available=False,
            pending_final_bindings=pending_bindings,required_legacy_scope=qualification['required_legacy_scope']),
        phase_review=dict(graph=graph,CE07_ancestors=sorted(closure['CE07']),no_reverse_dependency=True,
            CE08_final_freeze=True,CE09_exact_C=True,CE10_unique_mapping_bundle=True,
            CE11_not_dependent_on_CE12=True,CE12_actual_claim_before_receipt_separately_authorized=True,
            final_scope_must_match_prior_accepted_proof_not_retrospectively_authenticate_it=True),
        timing_review=dict(candidate_phase_budgets=budgets,candidate_reserve_seconds=30,candidate_total_seconds=900,
            wait_return_exact_True_not_physical_exit=True,wait_True_not_success_proof=True,
            pre_tR_worker_exit_observation_success_finally_requirements_preserved=True,
            both_Reader_ledgers_and_global_join_required=True,actual_phase_or_900_bound_verified=False),
        preservation=dict(I211_build_reproduced=True,prior_publication_mains_run=False,
            historical_CE07_absent_then_current_present_verified=True,exact_presence_guard_restored_success_exception=True,
            original_twelve_documentary_rejections_reproduced=True,CE08_to_CE12_dossiers_absent=5,
            eight_S01_exclusions_unchanged=True,unassigned_roles=3,independent_acceptance=False),
        verdict=dict(new_blocking_documentary_findings=0,CE07_documentary_baseline_confirmed=True,
            CE07_accepted=False,actual_prior_proofs_accepted=False,actual_resource_derivations_verified=False,
            resource_obligations_closed=0,actual_evidence_accepted=0,independent_acceptance=False,
            product_or_components_executed=0))


def build_review(rec):
    d = rd(DOS)
    checks = [
        ('E01','Exact effective closure and complete E01-E05 derivations','PRESERVED_MISSING_NOT_REPLACED_BY_HISTORICAL_PINS'),
        ('E02','179/321/12/30 scope and new custody/bootstrap/output/failure paths','REQUALIFICATION_REQUIRED_NOT_SOURCE_COUNTS_OR_TEN_TESTS'),
        ('E03','Whole heap, all30 groups, CPU/IO/service/clock and900 seconds','UNKNOWN_BOUNDS_AND_CORRESPONDENCE_STAY_PENDING'),
        ('E04','Accepted prior BASIS/index proof scoped to final source/image/runtime','NO_PREDICTIVE_FLAGS_OR_FUTURE_ROOT_BOOTSTRAP'),
        ('A01','No CP03/indices/widths/deadlines/test-count substitution','PRESERVED_NO_RESOURCE_OR_ATOMICITY_PROMOTION'),
        ('A02','Every per-attempt machine cost inside phases and global join','BOTH_READERS_DUAL_WRITES_CRYPTO_LEDGER_FAILURE_COSTS_REQUIRED'),
        ('A03','Genuine independent R03/R06 review and separate R08','UNASSIGNED_NO_COMPETENT_ACCEPTANCE_OR_CLOSURE')]
    effect = {**d['current_effect'],'CE07_documentary_review_completed':True,
        'CE07_documentary_confirmation':True,'CE07_documentary_revision_required':False}
    return dict(schema='d5.i212-i211-documentary-review.v1',increment='I212',date='2026-11-17',
        timezone='Europe/Madrid',base_commit=BASE,proposal_id=d['proposal_id'],profile_id=d['profile_id'],step='CE07',
        status='CE07_DOCUMENTARY_BASELINE_CONFIRMED_RESOURCE_COMPATIBILITY_MISSING_NOT_ACCEPTED_NOT_ADMITTED',
        candidate=pin(DOS),reconstruction=pin(RECON),findings=[],
        checks=[dict(id=i,scope=s,result=r) for i,s,r in checks],
        contract_rule_review=rec['rule_review'],
        documentary_clarifications=[
            dict(id='C01',subject='all30 work groups',disposition='Ten activities x three scalar bounds and twenty process/phase vectors are historical references. I193 literal full-group requirement remains pending; no accepted successor inventory or reviewed correspondence.'),
            dict(id='C02',subject='I132 output_created=false',disposition='Historical planning metadata is preserved. All20 actual historical output bodies exist and are pinned; none is an accepted successor resource proof.'),
            dict(id='C03',subject='Exact True wait_worker return',disposition='tW stays at exact-True call return, not physical exit; source PFC still independently requires final success checks and successful finally. Budget arithmetic is not a900-second proof.'),
            dict(id='C04',subject='Final scope versus later freeze',disposition='Accepted antecedent proofs must cover exactly the later frozen scope. CE08/future C/root/mapping/receipt cannot supply their sole prior authentication; any change requires requalification and competent review.')],
        provenance=dict(reviewer='Same Codex assistant/chat that prepared I211',methodological_reconstruction_separate=True,
            actor_independent=False,organizationally_independent=False,competent_R03_R06_review=False,
            separate_R08_acceptance=False,independent_acceptance=False),
        verdict=rec['verdict'],current_effect=effect,decision=d['decision'],E06=d['E06'],
        limitations=['Documentary confirmation only. All actual dependency acceptances, exact successor closure, complete heap/work/CPU/IO/service/clock/phase derivations, prior proof bodies and compatible scope are missing.',
            'No resource or qualification PASS; E01-E05 remain open, E06 NOT_RUN, I122 IMPLEMENTED_NOT_ADMITTED, CP07 and correlated atomicity false, proposal and D5 not enabled.',
            'No product/component execution, build/import/compile, probe, codec/crypto, claims, enrollment, actors/keys/signatures, contact, quota/reserve/active binding change or new positive record.'],
        next_scope='CE07 may serve as a documentarily reviewed missing-evidence baseline for a separately requested CE08 documentary preparation. No actual prerequisite, final freeze, acceptance or authorization is supplied.',
        work_unit=dict(rollback_files=sorted(FILES),verification_command='python3 docs/validation/D5-I212-audit.py',expected_result=STATUS,
            runtime_harness='N/A: static documentary JSON/Git/hash/criterion/phase reconstruction; product and component execution forbidden.',
            over400_lines=True,reason='One CE07 review with separately reconstructed requirements, costs, phases and immutable preservation; machine-readable pins exceed400 lines. No PR requested.'),
        publication=dict(commit_and_push_requested=True,publication_is_not_acceptance_or_admission=True))


def main():
    rec = reconstruct()
    assert rd(RECON) == rec and rd(REVIEW) == build_review(rec)
    prior = rd(PRIOR_SEAL)
    preserved = {**prior['preserved_published544'],**prior['artifacts'],PRIOR_SEAL:sha(PRIOR_SEAL)}
    assert len(preserved) == 549
    seal = rd(SEAL)
    assert seal['schema'] == 'd5.i212-integrity.v1' and seal['base_commit'] == BASE
    assert seal['preserved_published549'] == preserved and set(seal['artifacts']) == FILES-{SEAL}
    for pins in [preserved,seal['artifacts']]:
        for p,h in pins.items():
            assert sha(p) == h, p
    assert seal['source_only'] and seal['current_effect'] == rd(REVIEW)['current_effect']
    changed = set(git('diff',BASE,'--name-only').splitlines()) | set(git('ls-files','--others','--exclude-standard').splitlines())
    assert changed == FILES, changed
    subprocess.check_call(['git','merge-base','--is-ancestor',BASE,'HEAD'],cwd=ROOT)
    if git('rev-parse','HEAD') != BASE:
        assert not git('status','--porcelain')
    print(json.dumps(dict(status=STATUS,increment='I212',historical_pins=857,preserved_published_files=549,
        new_files=5,original_documentary_rejections_reproduced=12,verdict=rec['verdict'],
        proposal_enabled=False,D5_closed=False,IR03='NOT_READY',git_head=git('rev-parse','HEAD')),sort_keys=True))


if __name__ == '__main__':
    main()
