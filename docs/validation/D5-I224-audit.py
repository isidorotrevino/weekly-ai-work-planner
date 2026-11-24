#!/usr/bin/env python3
"""I224 static review of real-evidence closure plan; no product/components or gate release."""
import hashlib
import io
import json
import runpy
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
P = 'docs/validation/'
BASE = '16e9437180143ddc8f1618ccc7449c6eb74de2a7'
PLAN = P+'D5-I223-PRELAUNCH-RESOURCE-CLOSURE-PLAN.json'
CHECK = P+'D5-I193-CUSTODY-EVIDENCE-CHECKLIST.json'
SPEC = P+'D5-I191-CALLER-IMAGE-CUSTODY-CONTRACT-CANDIDATE.json'
PACK = P+'D5-I191-CALLER-IMAGE-CUSTODY-SCHEMAS-CANDIDATE.json'
CONTRACT = P+'D5-I130-PLATFORM-CONTRACT-CANDIDATE.json'
CRITERIA = P+'D5-I131-E01-E05-review.json'
TASKS = P+'D5-I132-E01-E05-evidence-plan.json'
CE01 = P+'D5-I197-CE01-SCOPE-AND-DECISION-BOUNDARY-CANDIDATE-02.json'
CE11 = P+'D5-I193-CE11-PRELAUNCH-EVIDENCE-CLOSURE-REVIEW-CANDIDATE.json'
PRIOR_AUDIT = P+'D5-I223-audit.py'
PRIOR_PREP = P+'D5-I223-preparation-review.json'
PRIOR_SEAL = P+'D5-I223-integrity.json'
PRIOR_DOC = 'docs/design/D5-I223-REAL-EVIDENCE-CLOSURE-PLAN.md'
PRIOR_FILES = {PLAN,PRIOR_AUDIT,PRIOR_PREP,PRIOR_SEAL,PRIOR_DOC}
RECON = P+'D5-I224-I223-source-reconstruction.json'
REVIEW = P+'D5-I224-I223-documentary-review.json'
AUDIT = P+'D5-I224-audit.py'
SEAL = P+'D5-I224-integrity.json'
DOC = 'docs/design/D5-I224-I223-CLOSURE-PLAN-REVIEW.md'
FILES = {RECON,REVIEW,AUDIT,SEAL,DOC}
STATUS = 'PASS_STATIC_SOURCE_ONLY_REAL_EVIDENCE_PLAN_REVIEW_NOT_ADMITTED'
DATE = '2026-11-24'


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


def analyze_graph(graph):
    active = set()
    closure = {}
    level = {}
    ordered = []
    def visit(n):
        assert n in graph and n not in active, n
        if n in closure:
            return closure[n]
        active.add(n)
        found = set()
        for parent in graph[n]:
            found.add(parent)
            found.update(visit(parent))
        active.remove(n)
        assert n not in found
        closure[n] = found
        level[n] = 0 if not graph[n] else 1+max(level[p] for p in graph[n])
        ordered.append(n)
        return found
    for n in graph:
        visit(n)
    waves = [[n for n in ordered if level[n] == i] for i in range(max(level.values())+1)]
    return closure,ordered,waves


def reconstruct():
    d = rd(PLAN)
    check = rd(CHECK)
    spec = rd(SPEC)
    contract = rd(CONTRACT)
    pins = {**d['input_pins'],**{p:sha(p) for p in sorted(PRIOR_FILES)}}
    assert len(pins) == 917
    verify_blobs(pins)
    assert len(d['documentary_inventory']) == len({r['path'] for r in d['documentary_inventory']}) == 40
    for source in d['documentary_inventory']:
        assert pins[source['path']] == source['sha256'] == sha(source['path'])
    work = {w['id']:w for w in d['work_packages']}
    assert len(work) == len(d['work_packages']) == 13 and list(work) == ['W%02d'%i for i in range(1,14)]
    graph = {key:w['depends_on'] for key,w in work.items()}
    closure,ordered,waves = analyze_graph(graph)
    assert closure['W13'] == set(work)-{'W13'}
    assert waves == [['W01'],['W02'],['W03'],['W04'],['W05'],['W06','W07'],['W08'],['W09'],['W10'],['W11'],['W12'],['W13']]
    assert {'W05','W06','W07','W08'} <= closure['W09'] and not {'W10','W11','W12','W13'} & closure['W09']
    assert 'W09' in closure['W10'] and {'W09','W10'} <= closure['W11'] and 'W11' in closure['W12']
    roles = {r['id']:r for r in rd(CE01)['role_scope_matrix']}
    for w in work.values():
        assert w['provider_kind'] and w['deliverables'] and w['exit_predicates'] and w['reject_if'] and w['needs_separate_future_authority_for']
        assert set(w['primary_review_roles']) <= set(roles) and w['separate_acceptor_role'] == 'R08'
        assert w['deliverable_id'] == w['id']+'-REAL-EVIDENCE-PACKAGE'
        assert w['assigned_provider_person'] is None and w['assigned_reviewer_persons'] is None and w['actual_separate_acceptor'] is None
        assert w['appointments_accepted'] is False and w['accepted'] is False
        assert all(w[k] is None for k in ['actual_deliverable_sha256','actual_evidence_bodies','actual_review_records','actual_complete_bound','actual_scope_acceptance','completion_date_or_duration_guarantee'])
        assert w['current_authorized_actions'] == ['READ_DOCUMENTS_AND_PREPARE_REVIEWABLE_SPECIFICATIONS_ONLY']
    gate_sources = {}
    for group in ['family_gates','contract_rule_gates','global_gates']:
        for i,row in enumerate(check[group]):
            if group == 'family_gates' and row['conditional_after_launch']:
                continue
            gate_sources[row['id']] = (group,i,row)
    assert len(gate_sources) == len(d['gate_closure_matrix']) == 30
    assert {r['id'] for r in d['gate_closure_matrix']} == set(gate_sources)
    assert 'FAMILY-LAUNCH_RECEIPT' not in gate_sources
    gate_counts = {'FAMILY':0,'RULE':0,'GLOBAL':0}
    gate_review = []
    for i,row in enumerate(d['gate_closure_matrix']):
        group,source_index,source = gate_sources[row['id']]
        assert fragment(row['source']) == row['source_gate'] == source
        category = {'family_gates':'FAMILY','contract_rule_gates':'RULE','global_gates':'GLOBAL'}[group]
        assert row['category'] == category
        gate_counts[category] += 1
        expected = source['proof_obligation'] if category == 'FAMILY' else source['condition'] if category == 'GLOBAL' else next(x['rule'] for x in spec['rules'] if x['id'] == source['rule_id'])
        assert row['exact_requirement'] == expected
        producers = row['producer_work_package_ids']
        assert producers and len(producers) == len(set(producers)) and set(producers) <= set(work)
        assert row['required_deliverable_ids'] == [work[p]['deliverable_id'] for p in producers]
        assert row['closure_decision_work_package'] == 'W13' and row['primary_review_roles'] == ['R06'] and row['separate_acceptor_role'] == 'R08'
        assert len(row['close_only_if']) == 4 and row['otherwise']
        assert all(row[k] is None for k in ['actual_evidence_sha256s','actual_provider','actual_primary_review','actual_separate_acceptance'])
        assert row['actual_condition_verified'] is False and row['accepted'] is False
        gate_review.append(dict(id=row['id'],source=row['source'],plan_row=pin(PLAN,'/gate_closure_matrix/'+str(i)),
            producer_packages=producers,closure_package='W13',requirement_covered_documentarily=True,actual_gate_closed=False))
    assert gate_counts == dict(FAMILY=7,RULE=16,GLOBAL=7)
    obj = d['objective']
    assert obj['target_prelaunch_gate_ids'] == [r['id'] for r in d['gate_closure_matrix']]
    assert obj['target_gate_count'] == 30 and obj['target_resource_obligation_count'] == 5 and obj['target_criterion_count'] == 20
    assert obj['targets_are_future_evidence_dispositions_not_current_closure'] and obj['launch_receipt_CE12_excluded_from_prelaunch_targets']
    assert obj['final_E06_payload_Q_root_admission_claim_receipt_not_required_as_new_CE11_precondition'] and obj['no_execution_or_quota_change_or_D5_release_granted']
    obligations = rd(CRITERIA)['obligations']
    assert len(d['resource_obligation_matrix']) == 5 and obj['target_resource_obligations'] == [x['id'] for x in obligations]
    resource_review = []
    for i,(row,original) in enumerate(zip(d['resource_obligation_matrix'],obligations)):
        assert fragment(row['source']) == original and row['id'] == original['id'] and row['complete_requirement'] == original['needed']
        assert row['closure_decision_work_package'] == 'W09' and set(row['producer_work_package_ids']) <= closure['W09']|{'W09'}
        assert row['primary_review_roles'] == ['R03','R06'] and row['separate_acceptor_role'] == 'R08'
        assert row['exact_scope_and_all_assumptions_required'] and row['all_four_criteria_applicability_rechecked']
        assert all(row[k] is None for k in ['actual_complete_bound_or_derivation','actual_platform_capacity_service_guarantees','actual_primary_review','actual_separate_acceptance'])
        assert row['accepted'] is False and row['closed'] is False
        resource_review.append(dict(id=row['id'],source=row['source'],plan_row=pin(PLAN,'/resource_obligation_matrix/'+str(i)),
            producer_packages=row['producer_work_package_ids'],closure_package='W09',actual_obligation_closed=False))
    criteria = [(o,c) for o in obligations for c in o['criteria']]
    assert len(d['resource_criterion_matrix']) == len(criteria) == 20
    assert [r['id'] for r in d['resource_criterion_matrix']] == [c['id'] for o,c in criteria]
    classification_counts = {}
    for row,(o,c) in zip(d['resource_criterion_matrix'],criteria):
        assert fragment(row['source']) == c and row['obligation'] == o['id']
        assert row['historical_description'] == c['description'] and row['historical_kind'] == c['kind'] and row['historical_result'] == c['result']
        classification_counts[c['result']] = classification_counts.get(c['result'],0)+1
        assert row['closure_decision_work_package'] == 'W09' and row['actual_evidence_sha256s'] is None
        assert row['accepted'] is False and row['closes_resource_obligation'] is False
    assert classification_counts == {'HISTORICAL_REFERENCE_ONLY':1,'DOCUMENTARY_CONSISTENCY_ONLY':9,'COMPLETE_EVIDENCE_NOT_SUPPLIED':10}
    assert len(d['heap_owner_proof_tasks']) == 11
    for row,owner in zip(d['heap_owner_proof_tasks'],contract['heap']['owner_budgets']):
        assert fragment(row['source']) == owner and row['id'] == owner['id'] and row['owner'] == owner['owner']
        assert row['candidate_budget_bytes'] == owner['candidate_budget_bytes'] and row['producer_work_package'] == 'W06'
        assert row['candidate_budget_applied'] is False and row['accepted'] is False
        assert all(v is None for k,v in row.items() if k.startswith('actual_'))
    assert len(d['work_activity_proof_tasks']) == 10
    for row,activity in zip(d['work_activity_proof_tasks'],contract['cost_coverage']['activities']):
        assert fragment(row['source']) == row['historical_activity'] == activity and row['id'] == activity['id']
        assert row['producer_work_package'] == 'W07' and row['accepted'] is False
        assert all(v is None for k,v in row.items() if k.startswith('actual_'))
    assert len(d['historical_I132_task_requalification']) == len(rd(TASKS)['tasks']) == 20
    for row,task in zip(d['historical_I132_task_requalification'],rd(TASKS)['tasks']):
        assert fragment(row['source']) == task and row['id'] == task['id']
        assert row['existing_negative_output'] == pin(task['planned_output']) and (ROOT/task['planned_output']).exists()
        assert row['successor_requalification_required'] and row['currently_exists']
        assert row['successor_transfer_accepted'] is False and row['historical_output_rewritten'] is False
    evidence = d['evidence_package_contract']
    assert len(evidence['mandatory_fields']) == 6
    assert evidence['no_new_positive_record_schema_runtime_member_or_output_is_defined']
    assert evidence['all_missing_bounds_remain_unknown_not_zero'] and evidence['templates_and_document_hashes_not_genuine_external_evidence']
    assert evidence['actual_positive_proof_packages_created'] is False
    policy = d['resource_and_scope_policy']
    assert policy['contract'] == pin(CONTRACT)
    for field,source in [('heap_candidate_requested_bytes','requested_heap_candidate_bytes'),('heap_candidate_committed_bytes','committed_heap_candidate_bytes'),
                         ('unassigned_heap_candidate_reserve_bytes','unassigned_requested_reserve_bytes'),('allocator_overhead_candidate_bytes','allocator_overhead_candidate_bytes')]:
        assert policy[field] == contract['heap'][source]
    assert policy['heap_proof_rule'] == contract['heap']['proof_rule'] and policy['heap_reserve_rule'] == contract['heap']['reserve_rule']
    assert policy['candidate_phase_budgets'] == contract['time']['phase_budgets']
    assert policy['candidate_success_seconds'] == 900 and policy['unassigned_wall_candidate_reserve_seconds'] == 30
    assert policy['actual_reviewed_all30_group_correspondence'] is None and policy['actual_heap_fit_or_capacity'] is None and policy['actual_CPU_IO_service_phase_or900_proof'] is None
    assert policy['exact_wait_True_tW_not_physical_exit_and_success_finally_tF_required']
    assert policy['ten_historical_activities_thirty_scalar_bounds_twenty_vectors_not_automatic_all30_successor_group_coverage']
    assert policy['all_new_custody_bootstrap_lookup_crypto_ledger_receipt_failure_and_dual_output_costs_inside_global_join']
    assert policy['quotas_budgets_and_reserves_unchanged'] and policy['reserve_transfers_applied'] == 0 and not policy['resource_reservations_created']
    assert policy['inability_to_prove_fit_keeps_no_admission_not_automatic_quota_increase_or_infeasibility_claim']
    auth_scope = d['scope_authentication_and_freeze_order']
    assert all(value is True for value in auth_scope.values())
    assert 'debe revalidarse si cambian operaciones' in work['W12']['exit_predicates'][2]
    stops = d['stop_and_decision_points']
    assert [x['id'] for x in stops] == ['SD%02d'%i for i in range(1,9)]
    assert [x['after'] for x in stops] == ['W01','W03','W04','W06','W08','W10','W12','W13']
    assert all(x['condition'] and x['decision'] for x in stops)
    auth = d['authorization_boundary']
    assert auth['current_run_command'] is None
    assert all(value is False for key,value in auth.items() if key.endswith('_authorized'))
    assert auth['current_authorized_actions'] == ['READ_SOURCE_JSON_GIT_HASHES','PREPARE_THIS_REVIEWABLE_PLAN','RUN_OWN_DOCUMENTARY_AUDIT','COMMIT_AND_PUSH_THIS_UNIT']
    assert auth['future_operational_action_requires_separate_exact_authority_and_cost_evidence']
    assert auth['genuine_existing_external_material_may_only_be_considered_with_its_own_authorized_provenance']
    handoff = d['prelaunch_handoff_and_CE12']
    boundary = fragment(handoff['source'])['CE12']
    assert handoff['preclaim_external_prerequisites'] == boundary['preclaim_external_prerequisites']
    assert handoff['receipt_only_external_prerequisites'] == boundary['receipt_only_external_prerequisites']
    assert handoff['final_route_obligations'] == boundary['external_prerequisites']
    assert handoff['actual_final_route_completion_or_CE12_receipt_claim_spawn_required_to_close_prelaunch'] is False
    for key in ['target_accepting_resources_custody_not_runtime_release','claim_not_its_own_precondition',
                'actual_claim_after_full_admission_before_paths_spawn_required','actual_receipt_remains_private_and_DEFERRED_NOT_AUTHORIZED',
                'final_E06_payload_Q_root_admission_execution_and_actual_CE12_events_not_authorized_or_performed',
                'old_active_certificate_flags_not_automatically_promoted_by_future_evidence_disposition']:
        assert handoff[key] is True
    assert d['deferred_gate']['gate_id'] == 'FAMILY-LAUNCH_RECEIPT' and d['deferred_gate']['excluded_from30_prelaunch_targets']
    assert fragment(d['deferred_gate']['source'])['family'] == 'launch_receipt' and d['deferred_gate']['status'] == 'DEFERRED_NOT_AUTHORIZED'
    assert d['deferred_gate']['accepted'] is False
    references = d['reference_completeness_policy']
    assert fragment(references['source']) == rd(CE11)['proof_reference_disposition']
    assert references['typed_template_count_reference'] == 69 and references['static_templates_not_actual_or_unique_body_count']
    assert references['actual_reference_body_inventory'] is None and references['actual_proofs_accepted_by_this_plan'] == 0
    assert d['inherited_scope_boundaries'] == rd(CE11)['inherited_scope_boundaries']
    assert d['preserved_negative_gates'] == rd(CE11)['preserved_negative_gates']
    assert len(d['inherited_scope_boundaries']['S01_exclusions']) == 8
    for gate in d['preserved_negative_gates']:
        assert fragment({**gate['source'],'json_pointer':gate['json_pointer']}) == gate['observed_value']
    assert len(d['current_blockers']) == 5
    collection = d['evidence_collection_order']
    assert len(collection['first_material_decisions']) == 3 and collection['memory_and_work_proof_branches_may_run_in_parallel_after_W05']
    assert collection['no_calendar_or_completion_duration_guarantee'] and collection['no_more_documentary_passes_substitute_for_external_material']
    assert collection['actual_named_providers'] is None and collection['actual_schedule'] is None
    missing_sources = rd(PACK)['$defs']['source_bindings']['required']
    assert len(missing_sources) == 6 and all(not (ROOT/p).exists() for p in missing_sources)
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
    previous = runpy.run_path(str(ROOT/PRIOR_AUDIT))
    original = Path.exists
    assert previous['build_review']() == rd(PRIOR_PREP)
    assert Path.exists is original
    return dict(schema='d5.i224-i223-source-reconstruction.v1',increment='I224',date=DATE,base_commit=BASE,
        input_pins=pins,method='Fixed Git blobs and independent gate/criterion incidence, dependency waves, exact resource/owner/activity references, role/authority and evidence-before-acceptance review. I223 documentary build reproduced without prior publication main.',
        package_dependency_review=dict(graph=graph,topological_order=ordered,waves=waves,acyclic=True,
            W06_W07_parallel_after_W05=True,W09_no_W10_W12_future_auth_dependency=True,
            W10_requires_exact_reconciliation_or_upstream_invalidation=True,W12_new_costs_require_existing_coverage_or_revalidation=True,
            root_W01_still_requires_genuine_external_scope_authority_not_future_W02_self_appointment=True),
        gate_coverage_review=gate_review,resource_coverage_review=resource_review,
        counts=dict(work_packages=13,gate_categories=gate_counts,prelaunch_gates=30,resource_obligations=5,resource_criteria=20,
            historical_criterion_classifications=classification_counts,heap_owners=11,work_activities=10,work_CPU_wall_slots=30,
            I132_negative_outputs=20,decision_stop_points=8,missing_successor_sources=6),
        authority_review=dict(all_providers_people_appointments_and_actual_proof_bodies_missing=True,
            role_ids_not_proof_of_human_independence=True,technical_attestation_not_self_acceptance_of_resource_proof=True,
            R03_R06_and_separate_R08_genuine_acceptances_required=True,
            no_current_build_execution_probe_signing_verification_contact_provisioning_or_active_change_authorized=True,
            prelaunch_resource_acceptance_not_runtime_release_or_D5_closure=True),
        preservation=dict(historical_negative_outputs_and_caps_budgets_reserves_unchanged=True,
            eight_S01_exclusions_and_negative_gates_preserved=True,I223_build_and_twelve_documentary_rejections_reproduced=True,
            prior_Path_exists_method_restored=True,no_new_historical_presence_projection_added=True,prior_publication_mains_run=False),
        verdict=dict(new_blocking_documentary_findings=0,I223_documentary_plan_confirmed=True,
            actual_plan_executability_or_feasibility_proved=False,work_packages_accepted=0,prelaunch_gates_closed=0,
            resource_obligations_closed=0,actual_evidence_accepted=0,independent_acceptance=False,
            product_or_components_executed=0,execution_authorized=False))


def build_review(rec):
    d = rd(PLAN)
    checks = [
        ('C01','Exact30 prelaunch targets and all20 criteria','PASS_SOURCE_COVERAGE_NO_GATE_OR_RESOURCE_CLOSED'),
        ('C02','13 package deliverable/owner/reviewer/dependency/exit/reject contracts','PASS_CONCRETE_CONTRACTS_ALL_REAL_ASSIGNMENTS_AND_BODIES_MISSING'),
        ('C03','Acyclic dependency waves and parallel heap/work branch','PASS_SCHEDULE_STRUCTURE_NOT_REAL_FEASIBILITY_OR_DURATION'),
        ('C04','Prior authentication W09, final freeze reconciliation W10 and new-cost review W12','PASS_NO_FUTURE_AUTH_OR_AUTOMATIC_PROOF_TRANSFER'),
        ('C05','Eight explicit negative stop points under unchanged quotas/reserves','PASS_NO_UNKNOWN_AS_ZERO_OR_BUDGET_AS900_PROOF'),
        ('C06','Genuine independent reviewers/canonical actors and separate acceptance','PASS_ROLES_NOT_APPOINTMENTS_OR_CURRENT_ACCEPTANCE'),
        ('C07','No CE12/final-route execution as new prelaunch prerequisite','PASS_HANDOFF_NOT_AUTHORITY_OR_ADMISSION_RELEASE')]
    return dict(schema='d5.i224-i223-documentary-review.v1',increment='I224',date=DATE,timezone='Europe/Madrid',base_commit=BASE,
        plan=pin(PLAN),reconstruction=pin(RECON),status='I223_DOCUMENTARY_CLOSURE_PLAN_CONFIRMED_REAL_EVIDENCE_MISSING_NOT_ADMITTED',
        findings=[],checks=[dict(id=i,scope=s,result=r) for i,s,r in checks],
        documentary_clarifications=[
            dict(id='N01',subject='W01 entry authority',disposition='A root planning package is not self-authorizing. Genuine existing scope/reviewer authority must be supplied at entry; W02 future appointments cannot be its sole forecast authority. Without that input SD01 stops positive progress; no implicit nomination or contact.'),
            dict(id='N02',subject='W09 before W10',disposition='All proof authors/bodies and baseline actor/image/caller/platform authentication must really exist before resource acceptance. W10 later freeze only reconciles identical facts/scope; changes invalidate and requalify affected upstream work, not a backwards acceptance dependency.'),
            dict(id='N03',subject='W12 after resource join',disposition='Verifier/backend/message/copy/registry/receipt work used by W12 must already be covered by the pinned W03-W08 model. Any new operation, unit, dependency or timing premise forces revalidation; later approvals cannot retroactively pay missing cost.'),
            dict(id='N04',subject='Technical custodians and independent acceptance',disposition='R01/R02 may supply their proper attestations, but role labels or provider statements do not supply independent R03/R06 review or separate R08 acceptance. All canonical-human/alias/key/competence/appointment/exclusion evidence is still required.'),
            dict(id='N05',subject='Closure target',disposition='30 future prelaunch dispositions and5 complete resource obligations do not grant actual execution, mutate active certificates, complete final E06/Q/root/admission or close D5. CE12 stays deferred and no current command is supplied.')],
        provenance=dict(reviewer='Same Codex assistant/chat that prepared I223',methodological_reconstruction_separate=True,
            actor_independent=False,organizationally_independent=False,competent_R03_R06_review=False,
            separate_R08_acceptance=False,independent_acceptance=False),
        verdict=rec['verdict'],current_effect={**d['current_effect'],'I223_documentary_review_completed':True,
            'I223_documentary_confirmation':True,'I223_documentary_revision_required':False},
        limitations=['Coverage and an acyclic schedule are documentary properties only. Providers/people/authority, six sources, effective runtime/image/platform/service, proof bodies and every actual acceptance remain absent.',
            'No actual feasibility, closure time, full heap/CPU/IO/service/phase900 bound, global backend enforcement or ability to satisfy all gates is proved. Negative stops are valid outcomes; no quota/reserve increase is authorized to force fit.',
            'Same assistant is not competent independent acceptance. No product/components, implementation/build/import/compile, probe/clock/ledger, signing/positive crypto/codec, enrollment/provisioning/contact, claim/process or active binding/authority/destination changes.'],
        next_scope='I223 may be used as a reviewed specification for gathering genuinely authorized W01-W04 entry material. No package, person, contact or operational action is started; missing entry facts keep SD01-SD03 and all real closure pending.',
        work_unit=dict(rollback_files=sorted(FILES),verification_command='python3 docs/validation/D5-I224-audit.py',expected_result=STATUS,
            runtime_harness='N/A: documentary JSON/Git/hash/gate/criterion/owner/dependency and permission review only; no product/components, positive crypto/codec or platform/service/process execution.',
            over400_lines=True,reason='One I223 review with independent30-gate/20-criterion/13-package incidence and evidence-order reconstruction plus immutable preservation; overage reported. No PR requested.'),
        publication=dict(commit_and_push_requested=True,publication_is_not_actual_evidence_acceptance_or_execution_authority=True))


def main():
    rec = reconstruct()
    assert rd(RECON) == rec and rd(REVIEW) == build_review(rec)
    prior = rd(PRIOR_SEAL)
    preserved = {**prior['preserved_published604'],**prior['artifacts'],PRIOR_SEAL:sha(PRIOR_SEAL)}
    assert len(preserved) == 609
    seal = rd(SEAL)
    assert seal['schema'] == 'd5.i224-integrity.v1' and seal['base_commit'] == BASE
    assert seal['preserved_published609'] == preserved and set(seal['artifacts']) == FILES-{SEAL}
    for pins in [preserved,seal['artifacts']]:
        for p,h in pins.items():
            assert sha(p) == h, p
    assert seal['source_only'] and seal['current_effect'] == rd(REVIEW)['current_effect']
    changed = set(git('diff',BASE,'--name-only').splitlines()) | set(git('ls-files','--others','--exclude-standard').splitlines())
    assert changed == FILES, changed
    subprocess.check_call(['git','merge-base','--is-ancestor',BASE,'HEAD'],cwd=ROOT)
    if git('rev-parse','HEAD') != BASE:
        assert not git('status','--porcelain')
    print(json.dumps(dict(status=STATUS,increment='I224',historical_pins=917,preserved_published_files=609,
        new_files=5,original_documentary_rejections_reproduced=12,counts=rec['counts'],verdict=rec['verdict'],
        proposal_enabled=False,D5_closed=False,IR03='NOT_READY',git_head=git('rev-parse','HEAD')),sort_keys=True))


if __name__ == '__main__':
    main()
