#!/usr/bin/env python3
"""I211 documentary CE07 join only. Never import or execute product/components."""
import copy
import hashlib
import io
import json
import runpy
import subprocess
from contextlib import contextmanager
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
P = 'docs/validation/'
BASE = '4c4e634da477ea3fd441dc5809f5d4bd4c5bdd38'
DOS = P+'D5-I193-CE07-RESOURCE-AND-COMPATIBILITY-JOIN-CANDIDATE.json'
PLAN = P+'D5-I193-CALLER-IMAGE-CUSTODY-EVIDENCE-PLAN.json'
CONTRACT = P+'D5-I130-PLATFORM-CONTRACT-CANDIDATE.json'
CRITERIA = P+'D5-I131-E01-E05-review.json'
RESOURCE_PLAN = P+'D5-I132-E01-E05-evidence-plan.json'
BINDING_PLAN = P+'D5-I177-FOUR-BINDINGS-EVIDENCE-PLAN.json'
WORK = P+'D5-PFC126-03-E03-WORK-GROUPS.json'
CE06 = P+'D5-I193-CE06-PLATFORM-CLOCK-GLOBAL-LEDGER-CANDIDATE.json'
PRIOR_AUDIT = P+'D5-I210-audit.py'
PRIOR_RECON = P+'D5-I210-I209-source-reconstruction.json'
PRIOR_REVIEW = P+'D5-I210-I209-documentary-review.json'
PRIOR_SEAL = P+'D5-I210-integrity.json'
PRIOR_DOC = 'docs/design/D5-I210-I209-CE06-REVIEW.md'
PRIOR_FILES = {PRIOR_AUDIT, PRIOR_RECON, PRIOR_REVIEW, PRIOR_SEAL, PRIOR_DOC}
AUDIT = P+'D5-I211-audit.py'
PREP = P+'D5-I211-preparation-review.json'
SEAL = P+'D5-I211-integrity.json'
DOC = 'docs/design/D5-I211-CE07-RESOURCE-COMPATIBILITY-JOIN.md'
FILES = {DOS, AUDIT, PREP, SEAL, DOC}
STATUS = 'PASS_STATIC_SOURCE_ONLY_RESOURCE_EVIDENCE_MISSING'


def rd(p):
    return json.loads((ROOT/p).read_text())


def sha(p):
    return hashlib.sha256((ROOT/p).read_bytes()).hexdigest()


def git(*args):
    return subprocess.check_output(['git', *args], cwd=ROOT, text=True).strip()


def pin(p, pointer=''):
    return dict(path=p, sha256=sha(p), json_pointer=pointer)


def historical_pins():
    pins = {**rd(PRIOR_RECON)['input_pins'], **{p: sha(p) for p in sorted(PRIOR_FILES)}}
    assert len(pins) == 852
    return pins


def verify_blobs(pins):
    stream = io.BytesIO(subprocess.check_output(['git', 'cat-file', '--batch'], cwd=ROOT,
        input=''.join(BASE+':'+p+'\n' for p in sorted(pins)).encode()))
    for p, h in sorted(pins.items()):
        header = stream.readline().decode().split()
        assert len(header) == 3 and header[1] == 'blob', p
        body = stream.read(int(header[2]))
        assert stream.read(1) == b'\n' and hashlib.sha256(body).hexdigest() == h == sha(p), p
    assert stream.read() == b''


@contextmanager
def predecessor_CE07_presence_as_of_base():
    """Only CE07 existence in historical documentary replay; no blob/source bypass."""
    assert git('ls-tree', '--name-only', BASE, '--', DOS) == ''
    original = Path.exists
    target = ROOT/DOS
    assert original(target)
    def historical_exists(path):
        return False if path == target else original(path)
    Path.exists = historical_exists
    try:
        yield
    finally:
        Path.exists = original
    assert target.exists()


def actual_missing():
    return dict(actual_scope_binding=None, actual_provider=None, actual_proof_sha256=None,
        actual_proof_bytes=None, actual_derivation=None, actual_assumptions=None,
        actual_reviewer=None, actual_acceptance=None, accepted=False)


def build_candidate():
    plan = rd(PLAN)
    step = plan['steps'][6]
    contract = rd(CONTRACT)
    ce6 = rd(CE06)
    requirements = rd(CRITERIA)['obligations']
    resource_tasks = rd(RESOURCE_PLAN)['tasks']
    inventory = {PLAN, CONTRACT, CRITERIA, RESOURCE_PLAN, BINDING_PLAN, WORK, CE06,
        P+'D5-I172-P10-documentary-review.json', P+'D5-I178-I177-documentary-review.json'}
    inventory.update(v['path'] for v in plan['bindings'].values())
    dependencies = []
    for number, review in [(4, 'D5-I206-I205-documentary-review.json'),
                           (5, 'D5-I208-I207-documentary-review.json'),
                           (6, 'D5-I210-I209-documentary-review.json')]:
        path = plan['steps'][number-1]['candidate_dossier_path']
        inventory.update([path, P+review])
        dependencies.append(dict(step='CE%02d'%number, dossier=pin(path), review=pin(P+review),
            documentary_baseline_reviewed=True, competent_acceptance=False,
            actual_dependency_satisfied=False))
    obligation_rows = []
    criterion_rows = []
    for i, row in enumerate(requirements):
        obligation_rows.append(dict(id=row['id'], source=pin(CRITERIA, '/obligations/'+str(i)),
            complete_requirement=row['needed'], historical_status=row['status'],
            successor_status='MISSING_COMPLETE_EXACT_SCOPE_REQUALIFICATION', closed=False,
            **actual_missing()))
        for j, criterion in enumerate(row['criteria']):
            criterion_rows.append(dict(id=criterion['id'], obligation=row['id'],
                source=pin(CRITERIA, '/obligations/%d/criteria/%d'%(i,j)),
                historical_description=criterion['description'], historical_result=criterion['result'],
                successor_result='MISSING_NOT_TRANSFERRED', closes_resource_obligation=False,
                **actual_missing()))
    task_rows = []
    for i, task in enumerate(resource_tasks):
        path = task['planned_output']
        inventory.add(path)
        task_rows.append(dict(id=task['id'], obligations=task['obligations'],
            source=pin(RESOURCE_PLAN, '/tasks/'+str(i)), existing_historical_dossier=pin(path),
            bytes=(ROOT/path).stat().st_size, historical_plan_output_created=task['output_created'],
            currently_exists=True, historical_output_accepted_as_successor_proof=False,
            successor_proof_sha256=None, output_rewritten=False))
    owners = [dict(id=r['id'], owner=r['owner'], source=pin(CONTRACT, '/heap/owner_budgets/'+str(i)),
        candidate_budget_bytes=r['candidate_budget_bytes'], candidate_budget_applied=False,
        complete_requested_upper_bytes=None, complete_committed_upper_bytes=None,
        lifetime_allocator_native_GC_overlap_derivation=None, **actual_missing())
        for i,r in enumerate(contract['heap']['owner_budgets'])]
    work = []
    for i, row in enumerate(contract['cost_coverage']['activities']):
        work.append(dict(id=row['id'], source=pin(CONTRACT, '/cost_coverage/activities/'+str(i)),
            historical_activity=row, successor_complete_work_upper=None,
            successor_complete_CPU_seconds_upper=None, successor_complete_wall_seconds_upper=None,
            **actual_missing()))
    bindings = [dict(id=b['id'], path=b['path'] if 'path' in b else b['destination'],
        source=pin(BINDING_PLAN, '/four_binding_plan/'+str(i)),
        actual_body_sha256=None, actual_body_bytes=None, actual_artifact_created=False,
        accepted=False, execution_authorized=False)
        for i,b in enumerate(rd(BINDING_PLAN)['four_binding_plan'])]
    roles = []
    for row in ce6['role_scope_matrix']:
        if row['id'] in step['provenance_and_role']['primary_review_roles']:
            role = {k:v for k,v in row.items() if k != 'CE06_responsibility'}
            role['CE07_responsibility'] = {'R03':'Review genuine exact-scope E01-E05 resource derivations.',
                'R06':'Review actual runtime/platform/work/service compatibility and assumptions.',
                'R08':'Separate acceptance or rejection of genuine proofs; preserve all exclusions.'}[row['id']]
            roles.append(role)
    phase_rows = []
    for s in plan['steps']:
        if s['id'] in ['CE07','CE08','CE09','CE10','CE11','CE12']:
            phase_rows.append(dict(step=s['id'], depends_on=s['depends_on'],
                record_families=s['record_families'], accepted=False,
                current_execution_authorized=False, actual_records_available=False))
    return dict(schema='d5.i211-ce07-resource-compatibility-join-candidate.v1', increment='I211',
        date='2026-11-17', timezone='Europe/Madrid', base_commit=BASE,
        proposal_id=ce6['proposal_id'], profile_id=ce6['profile_id'], step='CE07',
        kind='MISSING_SUCCESSOR_RESOURCE_JOIN_DOCUMENTARY_DOSSIER_NOT_RESOURCE_PROOF',
        status='CE07_DOCUMENTARY_JOIN_PREPARED_RESOURCE_EVIDENCE_MISSING_NOT_ACCEPTED_NOT_ADMITTED',
        input_pins=historical_pins(), plan_binding=pin(PLAN,'/steps/6'),
        required_evidence=step['required_evidence'], planned_acceptance_checks=step['acceptance_checks'],
        contract_rules=step['contract_rules'], authorization_boundary=step['authorization_boundary'],
        dependency_gates=dependencies, documentary_inventory=[pin(p) for p in sorted(inventory)],
        producer=dict(identity='Same Codex assistant/chat as prior candidates',
            documentary_preparer_only=True, actor_independent=False, organizationally_independent=False,
            actual_provider_or_competent_acceptor=False, external_contacts_made=False),
        role_scope_matrix=roles, E01_E05_join=obligation_rows, all20_criterion_join=criterion_rows,
        historical_I132_task_join=task_rows,
        heap_join=dict(owners=owners, whole_requested_upper_bytes=None, whole_committed_upper_bytes=None,
            available_host_capacity_bytes=None, capacity_attestation=None, complete_derivation=None,
            both_processes_threads_native_GC_allocator_and_transient_lifetimes_required=True,
            owner_overlap_and_all_original_children_required=True,
            typed_body_or_Reader_caps_not_whole_heap_proof=True,
            unknown_terms_coerced_to_zero=False, finite_bound_claimed=False, capacity_verified=False),
        work_join=dict(activities=work, historical_activity_count=10, required_scalar_upper_slots=30,
            upper_slot_meaning='10 activities x work/CPU/wall; not 30 independently qualified activities',
            legacy_process_phase_vectors=pin(WORK,'/per_process_phase_work_vectors_and_units'),
            successor_complete_activity_inventory=None,
            plan_all30_work_groups_requirement_preserved=True,
            thirty_distinct_successor_groups_or_reviewed_correspondence=None,
            thirty_upper_slots_do_not_alone_satisfy_plan_all30_groups=True,
            compatible_units=None, complete_derivation=None,
            whole_work_upper=None, whole_CPU_seconds_upper=None, whole_wall_seconds_upper=None,
            sum_CPU_is_not_wall_duration=True, no_unproved_overlap_subtraction=True,
            exact_runtime_platform_and_service_compatibility_required=True, complete_verified=False),
        requalification=dict(required_legacy_scope=dict(operand_cases=179, roots=321, root_groups=12, atomic_sites=30),
            legacy_counts_are_requirements_not_successor_proof=True, actual_qualified_case_inventory=None,
            successor_effective_source_runtime_loader_caller_ledger_crypto_closure=None,
            actual_complete_new_custody_bootstrap_output_failure_path_inventory=None,
            inherited_CP03_does_not_transfer=True, source_atomicity_implementation_is_not_accepted_atomicity=True,
            ten_component_tests_are_not_complete_resource_evidence=True, component_status='NOT_RUN',
            qualification_authorized=False, SOURCE_CAPACITY_VERIFIED_issued=False),
        per_attempt_cost_coverage=dict(
            required_terms=['both coordinator and worker Input Reader ledgers and repeated reads',
                'lookup registry canonicalization hashing parsing identity/key checks and crypto',
                'freshness revocation clock sampling ledger lookups locks durable claims and receipt work',
                'frame attempts accepted and rejected prefixes and both control pipes',
                'copies sort Unicode/JSON/native codecs allocator GC destruction frames tracebacks',
                'dual context/launch output writes validation and failure/cleanup paths',
                'startup original children all threads scheduler IO observation and successful finally'],
            per_process_Reader_ledger_count=2, global_join_required=True,
            all_terms_charged_inside_t0_launch_worker_finish=True,
            offline_enrollment_build_facts_not_free_verification=True, any_term_assumed_free=False,
            actual_cost_derivations=None, actual_IO_or_service_guarantees=None),
        time_join=dict(candidate_source=pin(CONTRACT,'/time'),
            unchanged_candidate_phase_budgets=contract['time']['phase_budgets'],
            candidate_success_seconds=900, candidate_unassigned_reserve_seconds=30,
            marker_rule='Tworker ends on exact True wait_worker return tW; Tpost includes successful finally through launch return tF.',
            ordered_60_750_60_plus_30_is_budget_not_proof=True,
            watchdog_counter_deadline_or_elapsed_time_not_success_proof=True,
            compatible_clock_service_IO_scheduler_observation_guarantees=None,
            complete_phase_derivations=None, successful_completion_upper_seconds=None,
            success_within900_verified=False, reserve_transfers=0, reservations_created=False),
        accepted_prior_proof_join=dict(actual_BASIS_proof_record=None, actual_index_proof_records=None,
            exact_final_source_image_runtime_binding=None, authentic_prior_authentication=None,
            accepted_by_R03_R06_and_separate_R08=False,
            predictive_flags_typed_indices_or_placeholder_hashes_are_not_proof=True,
            final_E06_or_final_root_must_not_supply_sole_antecedent_proof=True,
            qualifying_and_final_runs_separate_not_authorized=True,
            no_automatic_prior_negative_or_positive_certificate_transfer=True),
        I177_binding_reference=bindings,
        phase_boundary=dict(steps=phase_rows,
            CE07_complete_evidence_and_prior_proof_required_before_acceptance=True,
            CE07_requires_future_C_mapping_final_root_or_receipt_as_predecessor=False,
            CE08_final_records_and_scope_freeze_not_created_now=True,
            CE09_exact_C_projection_not_created_now=True, CE10_unique_mapping_bundle_not_created_now=True,
            CE11_does_not_depend_on_CE12=True,
            CE12_separate_authorization_full_admission_and_actual_claim_before_receipt=True,
            external_prerequisites_for_receipt=plan['closure_boundaries']['external_prerequisites_for_receipt']),
        schema_boundary=dict(record_families=step['record_families'],
            dossier_is_not_positive_I191_record=True, actual_codec_crypto_or_schema_validation='NOT_RUN_NO_ACTUAL_BODY',
            no_new_positive_record_schema_or_authority_created=True),
        inherited_scope_boundaries=ce6['inherited_scope_boundaries'],
        preserved_negative_gates=ce6['preserved_negative_gates'],
        permission_boundary={**ce6['permission_boundary'],
            'authorized_documentary_actions':['READ_SOURCE_JSON_GIT_HASHES',
                'PREPARE_CE07_MISSING_RESOURCE_COMPATIBILITY_JOIN_DOSSIER',
                'RUN_DOCUMENTARY_AUDIT','COMMIT_AND_PUSH_THIS_UNIT']},
        historical_replay_policy=dict(exact_CE07_path_absent_at_BASE=True,
            only_exact_Path_exists_query_projected_during_predecessor_documentary_replay=True,
            all_historical_blobs_and_checks_preserved=True, restoration_after_success_and_exception_required=True,
            prior_publication_mains_run=False, CE08_to_CE12_dossiers_still_absent=True),
        current_effect=dict(CE07_documentary_prepared=True, CE07_accepted=False,
            actual_dependency_satisfied=False, actual_evidence_accepted=0, resource_obligations_closed=0,
            heap_capacity_verified=False, CPU_service_compatibility_verified=False,
            success_within900_verified=False, actual_prior_proofs_accepted=False,
            independent_acceptance=False, actual_qualification_PASS=False,
            product_or_components_executed=False, quotas_changed=False, reserves_changed=False,
            rebind_applied=False, proposal_enabled=False, D5_closed=False, IR03='NOT_READY'),
        decision=plan['decision'], E06=plan['E06'])


def validate(d):
    plan = rd(PLAN)
    # Reject unsafe documentary claims on their own semantics, before canonical comparison.
    assert d['heap_join']['whole_requested_upper_bytes'] is None, 'unknown_heap_as_zero'
    assert d['requalification']['actual_qualified_case_inventory'] is None, 'counts_as_qualification'
    assert d['time_join']['success_within900_verified'] is False, '900_budget_as_guarantee'
    assert d['heap_join']['typed_body_or_Reader_caps_not_whole_heap_proof'] is True, 'Reader_cap_as_heap_proof'
    assert d['per_attempt_cost_coverage']['any_term_assumed_free'] is False, 'offline_verification_free'
    assert d['per_attempt_cost_coverage']['per_process_Reader_ledger_count'] == 2, 'one_Reader_ledger'
    assert d['accepted_prior_proof_join']['final_E06_or_final_root_must_not_supply_sole_antecedent_proof'] is True, 'future_root_bootstraps_proof'
    assert all(b['actual_artifact_created'] is False for b in d['I177_binding_reference']), 'four_binding_body_fabricated'
    assert d['time_join']['reserve_transfers'] == 0, 'reserve_transfer'
    assert d['current_effect']['actual_qualification_PASS'] is False, 'actual_qualification_PASS'
    assert d['current_effect']['resource_obligations_closed'] == 0, 'documentary_closes_resource'
    assert d['phase_boundary']['CE07_requires_future_C_mapping_final_root_or_receipt_as_predecessor'] is False, 'reverse_dependency_receipt'
    assert len(d['E01_E05_join']) == 5 and len(d['all20_criterion_join']) == 20
    assert len(d['historical_I132_task_join']) == 20
    assert [r['id'] for r in d['heap_join']['owners']] == ['H%02d'%i for i in range(1,12)]
    assert len(d['work_join']['activities']) == 10
    assert len(d['work_join']['activities'])*3 == d['work_join']['required_scalar_upper_slots'] == 30
    assert [r['id'] for r in d['role_scope_matrix']] == ['R03','R06','R08']
    for rows in [d['E01_E05_join'],d['all20_criterion_join'],d['heap_join']['owners'],d['work_join']['activities']]:
        for row in rows:
            for k,v in actual_missing().items():
                assert row[k] == v and type(row[k]) is type(v), (row['id'],k)
    assert [g['step'] for g in d['dependency_gates']] == plan['steps'][6]['depends_on']
    for task in d['historical_I132_task_join']:
        assert (ROOT/task['existing_historical_dossier']['path']).exists()
    for b in d['I177_binding_reference']:
        assert not (ROOT/b['path']).exists(), b['path']
    assert len(d['I177_binding_reference']) == 4
    graph = {s['id']:s['depends_on'] for s in plan['steps']}
    prior = runpy.run_path(str(ROOT/PRIOR_AUDIT))
    closure = prior['ancestors'](graph)
    assert closure['CE07'] == {'CE01','CE02','CE03','CE04','CE05','CE06'}
    assert not ({'CE08','CE09','CE10','CE11','CE12'} & closure['CE07'])
    assert 'CE12' not in closure['CE11']
    assert all((ROOT/s['candidate_dossier_path']).exists() for s in plan['steps'][:7])
    assert all(not (ROOT/s['candidate_dossier_path']).exists() for s in plan['steps'][7:])
    assert d == build_candidate(), 'Dossier differs from pinned source reconstruction'


def rejection_checks(d):
    cases = [
        ('unknown_heap_as_zero',('heap_join','whole_requested_upper_bytes'),0),
        ('counts_as_qualification',('requalification','actual_qualified_case_inventory'),179),
        ('900_budget_as_guarantee',('time_join','success_within900_verified'),True),
        ('Reader_cap_as_heap_proof',('heap_join','typed_body_or_Reader_caps_not_whole_heap_proof'),False),
        ('offline_verification_free',('per_attempt_cost_coverage','any_term_assumed_free'),True),
        ('one_Reader_ledger',('per_attempt_cost_coverage','per_process_Reader_ledger_count'),1),
        ('future_root_bootstraps_proof',('accepted_prior_proof_join','final_E06_or_final_root_must_not_supply_sole_antecedent_proof'),False),
        ('four_binding_body_fabricated',('I177_binding_reference',0,'actual_artifact_created'),True),
        ('reserve_transfer',('time_join','reserve_transfers'),1),
        ('actual_qualification_PASS',('current_effect','actual_qualification_PASS'),True),
        ('documentary_closes_resource',('current_effect','resource_obligations_closed'),1),
        ('reverse_dependency_receipt',('phase_boundary','CE07_requires_future_C_mapping_final_root_or_receipt_as_predecessor'),True)]
    out = []
    for name,path,value in cases:
        mutant = copy.deepcopy(d)
        target = mutant
        for key in path[:-1]:
            target = target[key]
        target[path[-1]] = value
        try:
            validate(mutant)
        except AssertionError as error:
            assert str(error) == name, (name,str(error))
            out.append(dict(case=name, result='REJECTED_DOCUMENTARY_MUTATION_IN_MEMORY'))
        else:
            raise AssertionError(name)
    return out


def build_review():
    d = rd(DOS)
    verify_blobs(d['input_pins'])
    validate(d)
    previous = runpy.run_path(str(ROOT/PRIOR_AUDIT))
    original = Path.exists
    with predecessor_CE07_presence_as_of_base():
        rec = previous['reconstruct']()
        assert rec == rd(PRIOR_RECON)
        assert previous['build_review'](rec) == rd(PRIOR_REVIEW)
    assert Path.exists is original and (ROOT/DOS).exists()
    class DocumentaryProbe(Exception):
        pass
    try:
        with predecessor_CE07_presence_as_of_base():
            assert not (ROOT/DOS).exists()
            raise DocumentaryProbe()
    except DocumentaryProbe:
        pass
    else:
        raise AssertionError('Guard exception restoration not exercised')
    assert Path.exists is original and (ROOT/DOS).exists()
    return dict(schema='d5.i211-preparation-review.v1', increment='I211', date='2026-11-17',
        base_commit=BASE, status=STATUS, candidate=pin(DOS), plan=pin(PLAN,'/steps/6'),
        counts=dict(input_pins=852, historical_tasks=20, obligations=5, criteria=20,
            heap_owners=11, historical_cost_activities=10, required_work_CPU_wall_upper_slots=30,
            historical_process_phase_vectors=20, pending_I177_bindings=4, unassigned_review_roles=3,
            later_dossiers_absent=5, resource_obligations_closed=0),
        source_reconstruction=dict(exact_fixed_Git_blobs_verified=True,
            prior_I210_reconstruction_and_review_reproduced=True,
            exact_CE07_historical_absence_guard=True, guard_restored_after_success_and_exception=True,
            prior_publication_mains_run=False, historical_I132_outputs_present_not_new_proofs=True,
            original_E01_E05_and_all20_criterion_requirements_preserved=True,
            no_reverse_C_final_root_mapping_or_receipt_dependency=True),
        provenance=d['producer'], rejection_checks=rejection_checks(d),
        limitations=['Documentary consistency only; no genuine successor closure, heap, CPU, clock/service, compatibility, phase or prior BASIS/index proof accepted.',
            'Historical ten cost activities require thirty work/CPU/wall upper values, not thirty independently qualified activities. Complete successor activity inventory remains missing.',
            'Same assistant is not independent competent R03/R06/R08 review or separate acceptance. All CE04/CE05/CE06 competent prerequisites remain pending.',
            'No product/component, qualification, platform/clock/ledger probe, codec/crypto, child process, provider contact or actual claim/receipt execution.'],
        current_effect=d['current_effect'], decision=d['decision'], E06=d['E06'],
        work_unit=dict(rollback_files=sorted(FILES), verification_command='python3 docs/validation/D5-I211-audit.py',
            expected_result=STATUS, runtime_harness='N/A: documentary JSON/Git/hash/phase reconstruction only; runtime and component execution forbidden.',
            over400_lines=True, reason='One complete pinned negative CE07 join and reproducible source-only check; machine-readable matrices and inherited preservation exceed400 lines. No PR requested.'),
        publication=dict(commit_and_push_requested=True, publication_is_not_acceptance_or_admission=True))


def main():
    review = build_review()
    assert rd(PREP) == review
    prior = rd(PRIOR_SEAL)
    preserved = {**prior['preserved_published539'], **prior['artifacts'], PRIOR_SEAL:sha(PRIOR_SEAL)}
    assert len(preserved) == 544
    seal = rd(SEAL)
    assert seal['schema'] == 'd5.i211-integrity.v1' and seal['base_commit'] == BASE
    assert seal['preserved_published544'] == preserved and set(seal['artifacts']) == FILES-{SEAL}
    for pins in [preserved,seal['artifacts']]:
        for p,h in pins.items():
            assert sha(p) == h, p
    assert seal['current_effect'] == review['current_effect'] and seal['source_only']
    changed = set(git('diff',BASE,'--name-only').splitlines()) | set(git('ls-files','--others','--exclude-standard').splitlines())
    assert changed == FILES, changed
    subprocess.check_call(['git','merge-base','--is-ancestor',BASE,'HEAD'],cwd=ROOT)
    if git('rev-parse','HEAD') != BASE:
        assert not git('status','--porcelain')
    print(json.dumps(dict(status=STATUS,increment='I211',historical_pins=852,
        preserved_published_files=544,new_files=5,documentary_rejections=12,
        current_effect=review['current_effect'],git_head=git('rev-parse','HEAD')),sort_keys=True))


if __name__ == '__main__':
    main()
