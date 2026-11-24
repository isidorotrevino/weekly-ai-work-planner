#!/usr/bin/env python3
"""I223 real-evidence closure plan audit: static documents only, no product/components or gate release."""
import copy
import hashlib
import io
import json
import runpy
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
P = 'docs/validation/'
BASE = '643a5f290e4dfdc1a937727d01515c0a5778febf'
PLAN = P+'D5-I223-PRELAUNCH-RESOURCE-CLOSURE-PLAN.json'
CHECK = P+'D5-I193-CUSTODY-EVIDENCE-CHECKLIST.json'
SPEC = P+'D5-I191-CALLER-IMAGE-CUSTODY-CONTRACT-CANDIDATE.json'
PACK = P+'D5-I191-CALLER-IMAGE-CUSTODY-SCHEMAS-CANDIDATE.json'
CONTRACT = P+'D5-I130-PLATFORM-CONTRACT-CANDIDATE.json'
CRITERIA = P+'D5-I131-E01-E05-review.json'
TASKS = P+'D5-I132-E01-E05-evidence-plan.json'
CE01 = P+'D5-I197-CE01-SCOPE-AND-DECISION-BOUNDARY-CANDIDATE-02.json'
CE11 = P+'D5-I193-CE11-PRELAUNCH-EVIDENCE-CLOSURE-REVIEW-CANDIDATE.json'
PRIOR_AUDIT = P+'D5-I222-audit.py'
PRIOR_RECON = P+'D5-I222-I221-source-reconstruction.json'
PRIOR_REVIEW = P+'D5-I222-I221-documentary-review.json'
PRIOR_SEAL = P+'D5-I222-integrity.json'
PRIOR_DOC = 'docs/design/D5-I222-I221-CE12-REVIEW.md'
PRIOR_FILES = {PRIOR_AUDIT,PRIOR_RECON,PRIOR_REVIEW,PRIOR_SEAL,PRIOR_DOC}
AUDIT = P+'D5-I223-audit.py'
PREP = P+'D5-I223-preparation-review.json'
SEAL = P+'D5-I223-integrity.json'
DOC = 'docs/design/D5-I223-REAL-EVIDENCE-CLOSURE-PLAN.md'
FILES = {PLAN,AUDIT,PREP,SEAL,DOC}
STATUS = 'PASS_STATIC_SOURCE_ONLY_REAL_EVIDENCE_CLOSURE_PLAN_NOT_ADMITTED'
DATE = '2026-11-24'
EXPECTED_GRAPH = {
    'W01':[], 'W02':['W01'], 'W03':['W01','W02'], 'W04':['W02','W03'],
    'W05':['W03','W04'], 'W06':['W03','W04','W05'], 'W07':['W03','W04','W05'],
    'W08':['W04','W05','W06','W07'], 'W09':['W02','W03','W04','W05','W06','W07','W08'],
    'W10':['W02','W03','W04','W05','W06','W07','W08','W09'], 'W11':['W09','W10'],
    'W12':['W02','W04','W10','W11'], 'W13':['W%02d'%i for i in range(1,13)]}


def rd(p):
    return json.loads((ROOT/p).read_text())


def sha(p):
    return hashlib.sha256((ROOT/p).read_bytes()).hexdigest()


def git(*args):
    return subprocess.check_output(['git',*args],cwd=ROOT,text=True).strip()


def pin(p,pointer=''):
    return dict(path=p,sha256=sha(p),json_pointer=pointer)


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
        assert stream.read(1) == b'\n' and hashlib.sha256(body).hexdigest() == h == sha(p), p
    assert stream.read() == b''


def dependency_analysis(graph):
    done = {}
    depth = {}
    active = set()
    ordered = []
    def visit(n):
        assert n in graph and n not in active, n
        if n in done:
            return done[n]
        active.add(n)
        found = set()
        for parent in graph[n]:
            found.add(parent)
            found.update(visit(parent))
        active.remove(n)
        assert n not in found
        done[n] = found
        depth[n] = 0 if not graph[n] else 1+max(depth[p] for p in graph[n])
        ordered.append(n)
        return found
    for n in graph:
        visit(n)
    waves = [[n for n in ordered if depth[n] == i] for i in range(max(depth.values())+1)]
    return done,ordered,waves


def target_gate_sources():
    check = rd(CHECK)
    result = {}
    for group in ['family_gates','contract_rule_gates','global_gates']:
        for i,row in enumerate(check[group]):
            if group == 'family_gates' and row['conditional_after_launch']:
                continue
            result[row['id']] = (group,i,row)
    assert len(result) == 30
    return result


def validate_plan(d):
    # Semantic documentary rejection checks precede source/coverage reconstruction.
    assert len(d['gate_closure_matrix']) == 30, 'missing_gate'
    assert all(r['id'] != 'FAMILY-LAUNCH_RECEIPT' for r in d['gate_closure_matrix']), 'receipt_as_prelaunch_target'
    assert len(d['resource_criterion_matrix']) == 20, 'missing_criterion'
    assert all(w['appointments_accepted'] is False and w['accepted'] is False for w in d['work_packages']), 'unassigned_roles_accepted'
    assert d['evidence_package_contract']['templates_and_document_hashes_not_genuine_external_evidence'] is True, 'documents_as_actual_proof'
    assert all(r['actual_complete_requested_bound_bytes'] is None for r in d['heap_owner_proof_tasks']), 'unknown_heap_zero'
    assert d['resource_and_scope_policy']['actual_CPU_IO_service_phase_or900_proof'] is None, '900_budget_as_proof'
    assert d['resource_and_scope_policy']['inability_to_prove_fit_keeps_no_admission_not_automatic_quota_increase_or_infeasibility_claim'] is True, 'quota_increase_to_fit'
    assert d['authorization_boundary']['product_or_component_execution_authorized'] is False, 'execution_authorized'
    assert d['scope_authentication_and_freeze_order']['future_bundle_root_final_E06_claim_receipt_cannot_supply_sole_antecedent_authentication'] is True, 'future_bundle_prior_auth'
    assert d['current_effect']['D5_closed'] is False, 'D5_closed_by_plan'
    assert all(r['successor_transfer_accepted'] is False for r in d['historical_I132_task_requalification']), 'historical_proof_transfer'
    assert d['base_commit'] == BASE and d['date'] == DATE
    work = d['work_packages']
    assert [w['id'] for w in work] == ['W%02d'%i for i in range(1,14)]
    graph = {w['id']:w['depends_on'] for w in work}
    assert graph == EXPECTED_GRAPH
    closure,ordered,waves = dependency_analysis(graph)
    assert closure['W13'] == set(graph)-{'W13'}
    assert not {'W10','W11','W12','W13'} & closure['W09']
    role_ids = {r['id'] for r in rd(CE01)['role_scope_matrix']}
    for w in work:
        assert w['title'] and w['provider_kind'] and w['deliverables'] and w['exit_predicates'] and w['reject_if']
        assert w['deliverable_id'] == w['id']+'-REAL-EVIDENCE-PACKAGE'
        assert set(w['primary_review_roles']) <= role_ids and w['separate_acceptor_role'] == 'R08'
        assert w['assigned_provider_person'] is None and w['assigned_reviewer_persons'] is None and w['actual_separate_acceptor'] is None
        assert all(w[k] is None for k in ['actual_deliverable_sha256','actual_evidence_bodies','actual_review_records','actual_complete_bound','actual_scope_acceptance','completion_date_or_duration_guarantee'])
        assert w['current_authorized_actions'] == ['READ_DOCUMENTS_AND_PREPARE_REVIEWABLE_SPECIFICATIONS_ONLY']
        assert w['needs_separate_future_authority_for'] and w['current_status'] == 'PLANNED_REQUIRED_MATERIAL_AND_COMPETENT_DECISION_MISSING'
    sources = target_gate_sources()
    assert len({r['id'] for r in d['gate_closure_matrix']}) == 30 and {r['id'] for r in d['gate_closure_matrix']} == set(sources)
    spec = rd(SPEC)
    gate_categories = {'FAMILY':0,'RULE':0,'GLOBAL':0}
    for row in d['gate_closure_matrix']:
        group,index,source = sources[row['id']]
        assert fragment(row['source']) == row['source_gate'] == source
        expected = source['proof_obligation'] if group == 'family_gates' else source['condition'] if group == 'global_gates' else next(r['rule'] for r in spec['rules'] if r['id'] == source['rule_id'])
        assert row['exact_requirement'] == expected
        gate_categories[row['category']] += 1
        assert row['producer_work_package_ids'] and set(row['producer_work_package_ids']) <= set(graph)
        assert row['required_deliverable_ids'] == [x+'-REAL-EVIDENCE-PACKAGE' for x in row['producer_work_package_ids']]
        assert row['closure_decision_work_package'] == 'W13' and row['separate_acceptor_role'] == 'R08'
        assert row['close_only_if'] and row['otherwise']
        assert all(row[k] is None for k in ['actual_evidence_sha256s','actual_provider','actual_primary_review','actual_separate_acceptance'])
        assert row['actual_condition_verified'] is False and row['accepted'] is False
    assert gate_categories == dict(FAMILY=7,RULE=16,GLOBAL=7)
    obligations = rd(CRITERIA)['obligations']
    assert len(d['resource_obligation_matrix']) == 5
    assert [r['id'] for r in d['resource_obligation_matrix']] == [o['id'] for o in obligations]
    for row,original in zip(d['resource_obligation_matrix'],obligations):
        assert fragment(row['source']) == original and row['complete_requirement'] == original['needed']
        assert set(row['producer_work_package_ids']) <= closure['W09']|{'W09'} and row['closure_decision_work_package'] == 'W09'
        assert row['primary_review_roles'] == ['R03','R06'] and row['separate_acceptor_role'] == 'R08'
        assert row['exact_scope_and_all_assumptions_required'] and row['all_four_criteria_applicability_rechecked']
        assert all(row[k] is None for k in ['actual_complete_bound_or_derivation','actual_platform_capacity_service_guarantees','actual_primary_review','actual_separate_acceptance'])
        assert row['accepted'] is False and row['closed'] is False
    expected_criteria = [(o,c) for o in obligations for c in o['criteria']]
    assert [r['id'] for r in d['resource_criterion_matrix']] == [c['id'] for o,c in expected_criteria]
    for row,(obligation,criterion) in zip(d['resource_criterion_matrix'],expected_criteria):
        assert fragment(row['source']) == criterion and row['obligation'] == obligation['id']
        assert row['historical_description'] == criterion['description'] and row['historical_kind'] == criterion['kind'] and row['historical_result'] == criterion['result']
        assert row['actual_evidence_sha256s'] is None and not row['accepted'] and not row['closes_resource_obligation']
        assert row['closure_decision_work_package'] == 'W09' and set(row['producer_work_package_ids']) <= closure['W09']|{'W09'}
    contract = rd(CONTRACT)
    assert len(d['heap_owner_proof_tasks']) == 11
    for row,owner in zip(d['heap_owner_proof_tasks'],contract['heap']['owner_budgets']):
        assert fragment(row['source']) == owner and row['id'] == owner['id'] and row['owner'] == owner['owner']
        assert row['producer_work_package'] == 'W06' and row['candidate_budget_bytes'] == owner['candidate_budget_bytes']
        assert row['candidate_budget_applied'] is False and row['accepted'] is False
        assert all(value is None for key,value in row.items() if key.startswith('actual_'))
    assert len(d['work_activity_proof_tasks']) == 10
    for row,activity in zip(d['work_activity_proof_tasks'],contract['cost_coverage']['activities']):
        assert fragment(row['source']) == row['historical_activity'] == activity
        assert row['id'] == activity['id'] and row['producer_work_package'] == 'W07'
        assert all(value is None for key,value in row.items() if key.startswith('actual_')) and row['accepted'] is False
    tasks = rd(TASKS)['tasks']
    assert len(d['historical_I132_task_requalification']) == len(tasks) == 20
    for row,task in zip(d['historical_I132_task_requalification'],tasks):
        assert fragment(row['source']) == task and row['id'] == task['id'] and row['obligations'] == task['obligations']
        assert row['existing_negative_output'] == pin(task['planned_output']) and (ROOT/task['planned_output']).exists()
        assert row['currently_exists'] and row['successor_requalification_required'] and not row['historical_output_rewritten']
    policy = d['resource_and_scope_policy']
    assert policy['contract'] == pin(CONTRACT)
    for field,key in [('heap_candidate_requested_bytes','requested_heap_candidate_bytes'),('heap_candidate_committed_bytes','committed_heap_candidate_bytes'),
                      ('unassigned_heap_candidate_reserve_bytes','unassigned_requested_reserve_bytes'),('allocator_overhead_candidate_bytes','allocator_overhead_candidate_bytes')]:
        assert policy[field] == contract['heap'][key]
    assert policy['heap_proof_rule'] == contract['heap']['proof_rule'] and policy['heap_reserve_rule'] == contract['heap']['reserve_rule']
    assert policy['candidate_phase_budgets'] == contract['time']['phase_budgets']
    assert policy['candidate_success_seconds'] == 900 and policy['unassigned_wall_candidate_reserve_seconds'] == 30
    assert policy['actual_reviewed_all30_group_correspondence'] is None and policy['actual_heap_fit_or_capacity'] is None
    assert policy['quotas_budgets_and_reserves_unchanged'] and policy['reserve_transfers_applied'] == 0 and not policy['resource_reservations_created']
    freeze = d['scope_authentication_and_freeze_order']
    assert all(value is True for value in freeze.values())
    boundary = d['authorization_boundary']
    assert boundary['current_run_command'] is None
    assert all(value is False for key,value in boundary.items() if key.endswith('_authorized'))
    assert boundary['future_operational_action_requires_separate_exact_authority_and_cost_evidence']
    assert len(d['stop_and_decision_points']) == 8
    assert all(x['after'] in graph and x['condition'] and x['decision'] for x in d['stop_and_decision_points'])
    handoff = d['prelaunch_handoff_and_CE12']
    phase1 = rd(CE01)['step_obligation_boundary']['CE12']
    assert handoff['preclaim_external_prerequisites'] == phase1['preclaim_external_prerequisites']
    assert handoff['receipt_only_external_prerequisites'] == phase1['receipt_only_external_prerequisites']
    assert handoff['final_route_obligations'] == phase1['external_prerequisites']
    assert not handoff['actual_final_route_completion_or_CE12_receipt_claim_spawn_required_to_close_prelaunch']
    assert handoff['claim_not_its_own_precondition'] and handoff['actual_claim_after_full_admission_before_paths_spawn_required']
    assert handoff['actual_receipt_remains_private_and_DEFERRED_NOT_AUTHORIZED']
    assert handoff['old_active_certificate_flags_not_automatically_promoted_by_future_evidence_disposition']
    assert d['deferred_gate']['gate_id'] == 'FAMILY-LAUNCH_RECEIPT' and not d['deferred_gate']['accepted']
    assert fragment(d['deferred_gate']['source'])['conditional_after_launch']
    assert d['reference_completeness_policy']['source'] == pin(CE11,'/proof_reference_disposition')
    assert d['reference_completeness_policy']['typed_template_count_reference'] == 69 and d['reference_completeness_policy']['actual_reference_body_inventory'] is None
    assert d['inherited_scope_boundaries'] == rd(CE11)['inherited_scope_boundaries']
    assert d['preserved_negative_gates'] == rd(CE11)['preserved_negative_gates']
    for gate in d['preserved_negative_gates']:
        assert fragment({**gate['source'],'json_pointer':gate['json_pointer']}) == gate['observed_value']
    assert len(d['current_blockers']) == 5
    assert d['evidence_collection_order']['actual_named_providers'] is None and d['evidence_collection_order']['actual_schedule'] is None
    for key,value in d['current_effect'].items():
        if key == 'closure_plan_prepared':
            assert value is True
        elif key == 'IR03':
            assert value == 'NOT_READY'
        elif key == 'prelaunch_gates_pending':
            assert value == 30
        elif key in ['work_packages_accepted','prelaunch_gates_accepted','resource_obligations_closed','resource_criteria_accepted','actual_evidence_accepted']:
            assert value == 0 and type(value) is int
        else:
            assert value is False, key
    return graph,ordered,waves,gate_categories


def rejection_checks(d):
    cases = [
        ('missing_gate',('gate_closure_matrix',),d['gate_closure_matrix'][:-1]),
        ('receipt_as_prelaunch_target',('gate_closure_matrix',0,'id'),'FAMILY-LAUNCH_RECEIPT'),
        ('missing_criterion',('resource_criterion_matrix',),d['resource_criterion_matrix'][:-1]),
        ('unassigned_roles_accepted',('work_packages',1,'appointments_accepted'),True),
        ('documents_as_actual_proof',('evidence_package_contract','templates_and_document_hashes_not_genuine_external_evidence'),False),
        ('unknown_heap_zero',('heap_owner_proof_tasks',0,'actual_complete_requested_bound_bytes'),0),
        ('900_budget_as_proof',('resource_and_scope_policy','actual_CPU_IO_service_phase_or900_proof'),900),
        ('quota_increase_to_fit',('resource_and_scope_policy','inability_to_prove_fit_keeps_no_admission_not_automatic_quota_increase_or_infeasibility_claim'),False),
        ('execution_authorized',('authorization_boundary','product_or_component_execution_authorized'),True),
        ('future_bundle_prior_auth',('scope_authentication_and_freeze_order','future_bundle_root_final_E06_claim_receipt_cannot_supply_sole_antecedent_authentication'),False),
        ('D5_closed_by_plan',('current_effect','D5_closed'),True),
        ('historical_proof_transfer',('historical_I132_task_requalification',0,'successor_transfer_accepted'),True)]
    results = []
    for name,path,value in cases:
        mutant = copy.deepcopy(d)
        target = mutant
        for key in path[:-1]:
            target = target[key]
        target[path[-1]] = value
        try:
            validate_plan(mutant)
        except AssertionError as error:
            assert str(error) == name, (name,str(error))
            results.append(dict(case=name,result='REJECTED_DOCUMENTARY_MUTATION_IN_MEMORY'))
        else:
            raise AssertionError(name)
    return results


def build_review():
    d = rd(PLAN)
    expected_pins = {**rd(PRIOR_RECON)['input_pins'],**{p:sha(p) for p in sorted(PRIOR_FILES)}}
    assert d['input_pins'] == expected_pins and len(expected_pins) == 912
    verify_blobs(expected_pins)
    assert len(d['documentary_inventory']) == len({x['path'] for x in d['documentary_inventory']}) == 40
    for source in d['documentary_inventory']:
        assert source['sha256'] == expected_pins[source['path']] == sha(source['path'])
    graph,ordered,waves,categories = validate_plan(d)
    previous = runpy.run_path(str(ROOT/PRIOR_AUDIT))
    original = Path.exists
    rec = previous['reconstruct']()
    assert rec == rd(PRIOR_RECON) and previous['build_review'](rec) == rd(PRIOR_REVIEW)
    assert Path.exists is original
    assert all((ROOT/s['candidate_dossier_path']).exists() for s in rd(P+'D5-I193-CALLER-IMAGE-CUSTODY-EVIDENCE-PLAN.json')['steps'])
    actual_paths = rd(PACK)['$defs']['source_bindings']['required']
    assert len(actual_paths) == 6 and all(not (ROOT/p).exists() for p in actual_paths)
    return dict(schema='d5.i223-preparation-review.v1',increment='I223',date=DATE,timezone='Europe/Madrid',base_commit=BASE,
        status=STATUS,plan=pin(PLAN),counts=dict(input_pins=912,work_packages=13,gate_categories=categories,
            prelaunch_gates=30,resource_obligations=5,resource_criteria=20,heap_owners=11,
            historical_work_activities=10,work_CPU_wall_upper_slots=30,historical_I132_outputs=20,
            stop_decision_points=8,currently_missing_successor_sources=6,prelaunch_gates_accepted=0,resource_obligations_closed=0),
        dependency_review=dict(graph=graph,topological_order=ordered,evidence_waves=waves,
            heap_and_work_branches_parallel_after_W05=True,W09_no_future_freeze_bundle_as_sole_authentication=True,
            gate_receipt_and_final_execution_excluded_from_new_prelaunch_prerequisites=True,
            no_time_or_provider_guarantee=True),
        source_review=dict(I222_reconstruction_and_documentary_review_reproduced=True,prior_publication_mains_run=False,
            prior_Path_exists_method_restored=True,no_new_historical_presence_projection_added=True,
            all30_original_prelaunch_gates_and20_criteria_exactly_bound=True,old_I132_negative_outputs_preserved_not_transferred=True,
            all_existing_candidates_caps_guards_and_negative_flags_unchanged=True),
        provenance=d['producer'],rejection_checks=rejection_checks(d),current_effect=d['current_effect'],
        limitations=['Plan only:13 packages define genuine evidence/owner/reviewer/entry-exit/rejection contracts. No provider/person/appointment or package accepted, no proof body created or resource/gate closed.',
            'Six successor sources and actual image/runtime/platform/service/capacity/clock/ledger evidence remain absent. Any necessary implementation/qualification/build/probe/signing/service/contact needs separate exact authority; no commands supplied.',
            'Same assistant is not competent independent review or separate R08 acceptance. Closing future prelaunch/resource dispositions would not release execution, change active flags, accept root/claim/receipt or close D5.'],
        work_unit=dict(rollback_files=sorted(FILES),verification_command='python3 docs/validation/D5-I223-audit.py',expected_result=STATUS,
            runtime_harness='N/A: documentary JSON/Git/hash/gate/criterion/DAG and negative-policy checks only; no product/components, positive crypto/codec, platform/service, claims or process execution.',
            over400_lines=True,reason='One actionable real-evidence closure plan with13 package contracts,30 gates,20 criteria,11 owners,10 activities and immutable preservation; overage reported. No PR requested.'),
        publication=dict(commit_and_push_requested=True,publication_is_not_actual_evidence_acceptance_or_execution_authority=True))


def main():
    review = build_review()
    assert rd(PREP) == review
    prior = rd(PRIOR_SEAL)
    preserved = {**prior['preserved_published599'],**prior['artifacts'],PRIOR_SEAL:sha(PRIOR_SEAL)}
    assert len(preserved) == 604
    seal = rd(SEAL)
    assert seal['schema'] == 'd5.i223-integrity.v1' and seal['base_commit'] == BASE
    assert seal['preserved_published604'] == preserved and set(seal['artifacts']) == FILES-{SEAL}
    for pins in [preserved,seal['artifacts']]:
        for p,h in pins.items():
            assert sha(p) == h, p
    assert seal['source_only'] and seal['current_effect'] == review['current_effect']
    changed = set(git('diff',BASE,'--name-only').splitlines()) | set(git('ls-files','--others','--exclude-standard').splitlines())
    assert changed == FILES, changed
    subprocess.check_call(['git','merge-base','--is-ancestor',BASE,'HEAD'],cwd=ROOT)
    if git('rev-parse','HEAD') != BASE:
        assert not git('status','--porcelain')
    print(json.dumps(dict(status=STATUS,increment='I223',historical_pins=912,preserved_published_files=604,
        new_files=5,counts=review['counts'],evidence_waves=review['dependency_review']['evidence_waves'],
        documentary_rejections=12,current_effect=review['current_effect'],git_head=git('rev-parse','HEAD')),sort_keys=True))


if __name__ == '__main__':
    main()
