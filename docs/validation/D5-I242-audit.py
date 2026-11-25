#!/usr/bin/env python3
"""I242 W09 methodological review. Own documentary checks; no target execution."""
import copy
import hashlib
import io
import json
import runpy
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
P = 'docs/validation/'
BASE = '981d32ac412b515388117e2a626d5b6530693b5e'
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
PRIOR_AUDIT = P+'D5-I241-audit.py'
PRIOR_PREP = P+'D5-I241-preparation-review.json'
PRIOR_SEAL = P+'D5-I241-integrity.json'
PRIOR_DOC = 'docs/design/D5-I241-W09-E01-E05-INTEGRATION.md'
SUBJECT = P+'D5-I223-W09-E01-E05-INTEGRATION-CANDIDATE.json'
PRIOR_FILES = {SUBJECT,PRIOR_AUDIT,PRIOR_PREP,PRIOR_SEAL,PRIOR_DOC}
RECON = P+'D5-I242-I241-source-reconstruction.json'
REVIEW = P+'D5-I242-I241-documentary-review.json'
AUDIT = P+'D5-I242-audit.py'
SEAL = P+'D5-I242-integrity.json'
DOC = 'docs/design/D5-I242-I241-W09-REVIEW.md'
FILES = {RECON,REVIEW,AUDIT,SEAL,DOC}
STATUS = 'PASS_STATIC_SOURCE_ONLY_W09_REVIEW_JOINT_EVIDENCE_MISSING_NOT_ADMITTED'


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


def require_missing(row, false_fields=()):
    for key,value in row.items():
        if key.startswith('actual_'):
            assert value is False if key in false_fields else value is None, key
    if 'accepted' in row:
        assert row['accepted'] is False


def require_true(row, names):
    for key in names:
        assert row[key] is True, key


def inspect(d):
    # Reconstruct requirements from primary sources, independently of I241's builder.
    plan, ce07, people = rd(PLAN), rd(CE07), rd(W02)
    w = plan['work_packages'][8]
    assert d['work_package'] == 'W09' and d['planned_deliverable_id'] == w['deliverable_id']
    assert fragment(d['work_package_binding']) == w
    for key,source in [('required_deliverables','deliverables'),('required_exit_predicates','exit_predicates'),('reject_if','reject_if'),('needs_separate_future_authority_for','needs_separate_future_authority_for')]:
        assert d[key] == w[source], key
    gate = d['dependency_gate']
    assert gate['required_package_ids'] == fragment(gate['source']) == w['depends_on'] == ['W02','W03','W04','W05','W06','W07','W08']
    assert gate['SD01_stop_active'] is True
    assert all(gate['W%02d_accepted'%i] is False for i in range(1,9))
    assert gate['actual_entry_authority_or_accepted_effective_baseline'] is None
    assert gate['documentary_preparation_and_review_not_dependency_acceptance'] is True
    assert d['role_scope_matrix'] == [r for r in rd(CE01)['role_scope_matrix'] if r['id'] in ['R03','R06','R08']]
    identity = d['role_and_identity_boundary']
    assert identity['required_provider_kind'] == w['provider_kind']
    assert identity['primary_roles'] == w['primary_review_roles'] == ['R03','R06']
    assert identity['separate_acceptor'] == w['separate_acceptor_role'] == 'R08'
    assert fragment(identity['source']) == people['identity_policy']
    assert identity['exact_identity_policy'] == people['identity_policy']['exact_policy']
    assert identity['separation_matrix'] == people['separation_matrix'] and len(identity['separation_matrix']) == 14
    assert len(identity['exact_identity_policy']['S01_exclusions']) == 8
    assert len(identity['exact_identity_policy']['extra_custody_separation']) == 4
    assert identity['overlap_policy'] == people['overlap_policy']
    assert identity['overlap_policy']['no_blanket_R01_R02_separation_added'] is True
    require_true(identity,['W02_intake_provisional_not_final_completeness_or_future_author_preapproval',
        'all_actual_W05_W08_authors_providers_and_all_documentary_preparers_must_be_identified_enrolled_and_authenticated_before_acceptance',
        'actor_strings_keys_git_or_assistant_labels_not_competence_appointment_or_independence'])
    require_missing(identity)
    evidence = d['evidence_package_requirements']
    assert evidence['exact_contract'] == fragment(evidence['source']) == plan['evidence_package_contract']
    assert len(evidence['exact_contract']['mandatory_fields']) == 6
    require_true(evidence,['no_new_positive_record_schema_or_Runtime_Reader_member_defined',
        'document_hashes_templates_accepted_flags_or_typed_indices_not_real_proof','missing_body_actor_provider_or_assumption_blocks_acceptance'])
    require_missing(evidence)
    obligations,criteria = d['resource_obligation_ledger'],d['criterion_revalidation_ledger']
    assert [r['id'] for r in obligations] == ['E01','E02','E03','E04','E05']
    assert len(criteria) == 20 and len({r['id'] for r in criteria}) == 20
    for i,row in enumerate(obligations):
        primary = plan['resource_obligation_matrix'][i]
        assert row['exact_plan_requirement'] == primary == fragment(row['source'])
        assert fragment(row['CE07_requirement']) == ce07['E01_E05_join'][i]
        assert row['id'] == primary['id']
        assert row['criterion_ids'] == [c['id'] for c in criteria if c['obligation']==row['id']]
        assert len(row['criterion_ids']) == 4 and row['closed'] is False
        require_missing(row)
    for i,row in enumerate(criteria):
        primary = plan['resource_criterion_matrix'][i]
        assert row['exact_plan_requirement'] == primary == fragment(row['source'])
        assert (row['id'],row['obligation']) == (primary['id'],primary['obligation'])
        assert row['historical_I131_criterion'] == primary['source']
        assert fragment(row['historical_I131_criterion']) == fragment(primary['source'])
        assert fragment(row['CE07_requirement']) == ce07['all20_criterion_join'][i]
        assert row['required_disposition'] == 'RECHECK_APPLICABILITY_AND_COMPLETE_EXACT_SUCCESSOR_EVIDENCE_NO_HISTORICAL_RESULT_TRANSFER'
        assert row['closes_resource_obligation'] is False
        require_missing(row)
    selected = [r for r in rd(CUSTODY)['rules'] if r['id'] in ce07['contract_rules']]
    assert [r['id'] for r in selected] == ['K04','K05','K06','K08','K12','K15','K16']
    assert [r['exact_rule'] for r in d['contract_rule_requirements']] == selected
    selected_profile = [r for r in rd(PROFILE)['semantic_contracts'] if r['id'] in ['C02','C03','C04','C11']]
    assert [r['exact_rule'] for r in d['profile_proof_requirements']] == selected_profile
    for row in d['contract_rule_requirements']+d['profile_proof_requirements']:
        assert row['exact_rule'] == fragment(row['source']) and row['id'] == row['exact_rule']['id']
    prior = d['prior_proof_boundary']
    assert prior['exact_negative_join'] == fragment(prior['source']) == ce07['accepted_prior_proof_join']
    assert fragment(prior['W05_basis_index_requirements']) == rd(W05)['basis_index_boundary']
    proof = prior['required_proof_kind_ledger']
    assert [r['kind'] for r in proof] == ['E01','E02','E03','E04','E05','CP03','ATOMICITY']
    assert [r['required_reviewer_role'] for r in proof] == ['R03_RESOURCES']*5+['R06_ADMISSION_REVIEWER']*2
    assert prior['basis_reviewer_role'] == 'R06_ADMISSION_REVIEWER'
    for row in proof:
        assert fragment(row['source']) == next(r for r in rd(PROFILE)['semantic_contracts'] if r['id']=='C03')
        require_missing(row)
    require_true(prior,['exact_source_image_runtime_policy_scope_and_current_antecedent_authentication_required',
        'complete_self_contained_derivations_must_fit_reviewed_32768_limit_or_reject_and_review_graph_without_truncation',
        'no_hidden_extra_files_future_proof_reads_or_cost_free_offline_evidence','seven_proof_requirements_not_seven_actual_records',
        'CP03_historical_scope_and_written_atomicity_not_successor_acceptance',
        'tests_flags_certificates_strings_or_placeholder_hashes_not_complete_proofs',
        'antecedent_qualification_and_final_E06_separate_not_authorized','final_E06_payload_Q_root_claim_receipt_not_sole_antecedent_proof'])
    require_missing(prior, ['actual_positive_BASIS_index_or_proof_record_created'])
    handoff = d['resource_premise_handoff']
    source_requirements = [
        ('W03_exact_sources_image_runtime',W03,'actual_image_runtime_state'),('W04_service',W04,'actual_service_state'),('W04_capacity',W04,'actual_capacity_state'),
        ('W05_complete_scope',W05,'coverage_completeness'),('W05_atomicity',W05,'atomicity_required_reasoning'),
        ('W06_heap_fit',W06,'availability_and_fit'),('W06_requested_heap',W06,'requested_rollup'),('W06_committed_heap',W06,'committed_rollup'),
        ('W07_complete_work',W07,'actual_whole_work_and_time'),('W07_all30',W07,'all30_successor_correspondence'),
        ('W07_compatible_service_or_WCET',W07,'work_service_or_WCET_boundary'),('W07_per_attempt_costs',W07,'per_attempt_cost_boundary'),
        ('W08_phase_bounds',W08,'phase_derivation_ledger'),('W08_qualified_success',W08,'qualified_success_boundary'),('W08_reserves',W08,'time_and_reserve_account')]
    for key,path,field in source_requirements:
        assert handoff[key]['path'] == path and handoff[key]['json_pointer'] == '/'+field
        assert fragment(handoff[key]) == rd(path)[field]
    require_true(handoff,['same_effective_scope_memory_allocator_cache_load_clock_units_service_windows_and_validity_must_be_justified_and_reconciled',
        'all11_heap_owners_lifetimes_allocator_complete_fit_and_separate_available_capacity_required',
        'all30_work_group_correspondence_not_ten_activities_thirty_scalar_slots_or_twenty_vectors',
        'all_original_native_children_threads_transitives_failure_paths_and_retained_traceback_scope_required',
        'both_Readers_global_join_freshness_identity_crypto_ledger_frames_dual_outputs_and_cleanup_costs_required',
        'no_CPU_sum_as_wall_unproved_overlap_subtraction_or_unknown_upper_as_zero',
        'worker_pre_tR_work_exit_to_exact_True_tW_observation_and_successful_finally_to_tF_covered',
        'complete_ordered_phase_bounds_and_nonvacuous_success_liveness_not_watchdog_elapsed_or_budget_sum',
        'no_every_failure_cleanup_within900_claim_and_no_actual_infeasibility_conclusion'])
    require_missing(handoff,['actual_complete_E01_E05_join_accepted'])
    reserves = d['resource_and_reserve_boundary']
    assert reserves['exact_plan_policy'] == fragment(reserves['source']) == plan['resource_and_scope_policy']
    assert reserves['exact_candidate_reserve_rules'] == rd(CONTRACT)['reserve_accounting']
    require_true(reserves,['all_missing_heap_work_service_delay_phase_bounds_unknown_not_zero',
        'budgets_not_capacity_service_or_success900_proof','no_partial_positive_or_documentary_PASS_as_joint_E01_E05_closure'])
    require_missing(reserves)
    assert type(reserves['transfers_applied']) is int and reserves['transfers_applied'] == 0
    assert reserves['resources_reserved'] is False and reserves['quotas_or_budgets_changed'] is False
    phase = d['phase_handoff']
    assert phase['exact_plan_order'] == fragment(phase['source']) == plan['scope_authentication_and_freeze_order']
    assert fragment(phase['W10_consumer']) == plan['work_packages'][9]
    assert 'W10' not in w['depends_on']
    require_true(phase,['actual_baseline_actor_image_caller_platform_facts_previously_authenticated_before_resource_acceptance_required',
        'actual_authors_providers_complete_bodies_and_assumptions_known_authenticated_before_W09_acceptance_required',
        'W10_final_freeze_not_required_as_W09_sole_authentication_or_backward_dependency',
        'W10_CE08_reconciles_same_facts_changed_inputs_invalidate_then_requalify_affected_packages',
        'W11_C_W12_bundle_mapping_W13_gates_and_CE12_not_created_or_accepted_by_W09',
        'no_future_CE10_approval_or_final_root_used_as_prior_authentication'])
    # Two actual_* keys in this section express requirements, not actual decisions.
    assert phase['actual_final_actor_registry_C_bundle_root_claim_receipt_or_authority'] is None
    assert phase['actual_refresh_or_active_rebind'] is False
    assert phase['final_route_boundary'] == plan['prelaunch_handoff_and_CE12']
    final = d['final_binding_boundary']
    assert final['exact_negative_binding_requirements'] == fragment(final['source']) == ce07['I177_binding_reference']
    require_true(final,['no_actual_B01_B04_artifact_or_body_produced','no_qualification_or_final_component_run_authorized'])
    authority = d['authority_boundary']
    assert authority['inherited_boundary'] == fragment(authority['source']) == plan['authorization_boundary']
    require_true(authority,['no_product_components_import_compile_discovery_tests_runs_experimental_WCET_benchmarks_clock_CPU_IO_service_platform_sampling_or_probes',
        'no_actual_crypto_codec_ledger_claim_provisioning_signing_keygen_enrollment_provider_contacts_or_new_helpers_channels_inputs_outputs'])
    require_missing(authority)
    assert [r['predicate'] for r in d['exit_predicate_dispositions']] == w['exit_predicates']
    for row in d['exit_predicate_dispositions']:
        assert row['predicate'] == fragment(row['source'])
        require_missing(row)
    assert d['preserved_scope_and_gates'] == {k:plan[k] for k in ['inherited_scope_boundaries','preserved_negative_gates','prelaunch_handoff_and_CE12']}
    for key,value in d['current_effect'].items():
        if key == 'W09_documentary_prepared':
            assert value is True
        elif key == 'IR03':
            assert value == 'NOT_READY'
        elif key in ['actual_evidence_accepted','work_packages_accepted','prelaunch_gates_closed','resource_obligations_closed']:
            assert type(value) is int and value == 0
        else:
            assert value is False, key
    check_pointers(d)


CRITERIA = [
    'W09 contract, seven dependency requirements, three exits, rejection and future-authority boundaries match I223',
    'SD01 and W01-W08 nonacceptance remain active; preparation does not accept a dependency',
    'R03/R06 primary roles and separate R08 have no assigned competent independent decisions',
    'W02 exact identity policy retains fourteen separation requirements and eight S01 exclusions',
    'Four extra custody separations and qualified R01/R02 overlap are preserved without extra blanket exclusion',
    'All actual authors/providers/preparers require prior enrollment/authentication; provisional intake is not final completeness',
    'Six mandatory body/provenance/scope/unit/validity fields remain missing and document hashes are not evidence',
    'Five obligations link exact I223 and CE07 requirements, remain unaccepted and unclosed',
    'Twenty unique criteria partition four per obligation and retain exact I131/I223/CE07 references',
    'Every criterion requires successor applicability and full evidence without historical result transfer',
    'Seven I191 custody rules and four profile rules match exact source text and hashes',
    'Seven proof kinds are requirements only, not actual accepted proof records',
    'E01-E05 proof reviews require R03; CP03/ATOMICITY and BASIS require R06 with real accepted review IDs',
    'Registry/contract/index/BASIS domains, exact actual bytes/source/runtime scope and no future backpins are preserved',
    'Self-contained 32768 proof-fit requirement rejects truncation and hidden extra reads',
    'Historical CP03, written atomicity, certificates, tests and flags do not transfer successor acceptance',
    'Fifteen source premise links preserve pending W03-W08 scope/atomicity/heap/work/service/phase states',
    'Same-scope memory/cache/allocator/load/clock/service-unit/validity assumptions require genuine reconciliation',
    'Eleven-owner heap fit/capacity and all30 successor work remain unproved and unreduced',
    'Both Readers, global costs, original/native/transitive/failure/traceback scope remain required',
    'Pre-tR worker work, exit-to-exact-True tW observation, successful finally to tF and liveness remain required',
    'No CPU-as-wall, unproved overlap deduction, missing-as-zero, watchdog success or all-failure deadline inference',
    'Exact candidate heap/time/nested reserve rules are conserved without transfers, quotas or capacity attestations',
    'No partial positive or documentary PASS becomes joint E01-E05 closure',
    'Baseline and real authors/bodies precede acceptance; W10/CE10 cannot supply sole retrospective authentication',
    'W10 change invalidation and later C/bundle/gates/E06/root/claim/receipt boundaries remain separate',
    'Four final bindings, inherited exclusions/CE12 and no-execution authority remain negative']


def reconstruct():
    d = rd(SUBJECT)
    inspect(d)
    pins = {**d['input_pins'],**{p:sha(p) for p in sorted(PRIOR_FILES)}}
    assert len(pins) == 1007
    verify_blobs(pins)
    return dict(schema='d5.i242-source-reconstruction.v1',increment='I242',date=DATE,base_commit=BASE,subject=pin(SUBJECT),input_pins=pins,
        criteria=[dict(id='RV%02d'%(i+1),criterion=t,result='PASS_DOCUMENTARY_REQUIREMENT_ONLY') for i,t in enumerate(CRITERIA)],
        counts=dict(input_pins=1007,resource_obligations=5,criteria_to_revalidate=20,criteria_per_obligation=4,prior_proof_kind_requirements=7,
            custody_rules=7,profile_proof_rules=4,separation_requirements=14,S01_exclusions=8,extra_custody_separations=4,
            source_premise_links=15,unassigned_review_roles=3,pending_exits=3,review_criteria=len(CRITERIA)),
        current_effect={**d['current_effect'],'W09_documentary_reviewed':True})


def own_rejections(d):
    cases = [
        ('obligation_drop',('resource_obligation_ledger',),d['resource_obligation_ledger'][:-1]),
        ('criterion_duplicate',('criterion_revalidation_ledger',1),copy.deepcopy(d['criterion_revalidation_ledger'][0])),
        ('historical_result_transfer',('criterion_revalidation_ledger',0,'required_disposition'),'HISTORICAL_ACCEPTANCE_TEST_LABEL'),
        ('criterion_scope_substitution',('criterion_revalidation_ledger',0,'obligation'),'E02'),
        ('proof_role_substitution',('prior_proof_boundary','required_proof_kind_ledger',5,'required_reviewer_role'),'R03_RESOURCES'),
        ('basis_reviewer_substitution',('prior_proof_boundary','basis_reviewer_role'),'R03_RESOURCES'),
        ('proof_rule_truncation',('profile_proof_requirements',1,'exact_rule','rule'),'INCOMPLETE_TEST_RULE'),
        ('S01_exclusion_drop',('role_and_identity_boundary','exact_identity_policy','S01_exclusions'),d['role_and_identity_boundary']['exact_identity_policy']['S01_exclusions'][:-1]),
        ('blanket_R01_R02_separation',('role_and_identity_boundary','overlap_policy','no_blanket_R01_R02_separation_added'),False),
        ('invented_body_inventory',('evidence_package_requirements','actual_complete_proof_body_inventory_locators_bytes_digests_authors_custody_availability'),'UNVERIFIED_TEST_LABEL'),
        ('invented_BASIS_body',('prior_proof_boundary','actual_BASIS_body_digest_bytes_or_review'),'UNVERIFIED_TEST_LABEL'),
        ('wrong_premise_link',('resource_premise_handoff','W04_capacity'),copy.deepcopy(d['resource_premise_handoff']['W04_service'])),
        ('nested_reserve_credit',('resource_and_reserve_boundary','exact_candidate_reserve_rules','worker_nested','category_reserve_seconds'),30),
        ('premature_later_gate_acceptance',('phase_handoff','W11_C_W12_bundle_mapping_W13_gates_and_CE12_not_created_or_accepted_by_W09'),False),
        ('implicit_operational_crypto',('authority_boundary','no_actual_crypto_codec_ledger_claim_provisioning_signing_keygen_enrollment_provider_contacts_or_new_helpers_channels_inputs_outputs'),False)]
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
    return dict(schema='d5.i242-documentary-review.v1',increment='I242',date=DATE,timezone='Europe/Madrid',base_commit=BASE,
        status=STATUS,subject=pin(SUBJECT),reconstruction=pin(RECON),
        verdict='DOCUMENTARY_REQUIREMENTS_CONSISTENT_NO_NEW_DEFECT_FOUND_REAL_JOINT_ACCEPTANCE_MISSING_NOT_ADMITTED',findings=[],
        counts=rec['counts'],criteria=rec['criteria'],
        documentary_clarifications=[
            'All five obligations and twenty criteria require genuine exact-successor evidence and fresh applicability review; reference/documentary/resource classifications transfer no closure.',
            'Seven proof kinds are requirements only. E01-E05 review IDs must resolve to genuine R03 reviews; CP03/ATOMICITY/BASIS require R06, with separate R08 acceptance and all identity exclusions.',
            'Complete actual bodies, bytes/hashes, author/provider/custody, units, all assumptions and validity remain missing. 32768 fit is a requirement, not a proved serialized proof size; no truncation or hidden reads.',
            'W02 is provisional. Actual authors and baseline actor/image/caller/platform facts require prior authentication before W09 acceptance; W10 final freeze and CE10 approvals cannot supply sole forecast authority.',
            'W03-W08 remain unaccepted. Same-scope heap/work/service/phase assumptions, all30 coverage, both Readers and full original/native/failure/cleanup costs require genuine integrated derivations.',
            'Candidate resource/reserve arithmetic supplies no fit/capacity/service/success900; no partial positive joins close E01-E05. Later C/bundle/gates/E06/payload/Q/root/claim/receipt remain separate.'],
        source_reconstruction=dict(primary_source_checks=True,I241_candidate_and_preparation_reproduced=True,prior_publication_mains_called=False,prior_Path_exists_restored=True,no_new_presence_projection=True),
        inherited_I241_rejection_checks=prep['rejection_checks'],additional_I242_rejection_checks=additional,current_effect=rec['current_effect'],
        provenance=dict(identity='Same Codex assistant/chat as I241',methodological_documentary_review_only=True,actor_independent=False,
            competent_R03_review=False,competent_R06_review=False,separate_R08_acceptance=False,external_contacts_made=False),
        limitations=['W09 is not an actual competent independent joint decision or accepted resource package. All five obligations, twenty criteria, seven proof records, actual BASIS/index and three exits remain unaccepted.',
            'SD01 active; zero accepted real packages, zero closed prelaunch gates and zero closed E01-E05 obligations. No actual bounds, capacity, service, success900 or infeasibility is proved.',
            'Same-assistant checks do not meet genuine R03/R06 independence or R08 acceptance; documentary publication authorizes no product/component execution or quota change.'],
        work_unit=dict(rollback_files=sorted(FILES),verification_command='python3 docs/validation/D5-I242-audit.py',expected_result=STATUS,
            runtime_harness='N/A: own documentary JSON/Git/hash/source-pointer/criterion/role/phase/reserve and in-memory document checks only. No target imports/compile/discovery/tests/runs, experimental WCET, clock/CPU/IO/service/platform/schedule sampling/probes, actual codec/crypto/ledger/claim, signing/keygen/enrollment/provisioning/services/contact.',
            over400_lines=True,reason='One W09 review with primary-source reconstruction, pinned inputs, negative cases and integrity preservation. Overage declared; no PR requested.'),
        publication=dict(commit_and_push_requested=True,publication_not_E01_E05_or_BASIS_index_acceptance_or_execution_authority=True))


def main():
    rec = reconstruct()
    assert rec == rd(RECON)
    review = build_review(rec)
    assert review == rd(REVIEW)
    prior = rd(PRIOR_SEAL)
    preserved = {**prior['preserved_published694'],**prior['artifacts'],PRIOR_SEAL:sha(PRIOR_SEAL)}
    assert len(preserved) == 699
    seal = rd(SEAL)
    assert seal['schema'] == 'd5.i242-integrity.v1' and seal['base_commit'] == BASE
    assert seal['preserved_published699'] == preserved and set(seal['artifacts']) == FILES-{SEAL}
    for mapping in [preserved,seal['artifacts']]:
        for path,digest in mapping.items():
            assert sha(path) == digest, path
    assert seal['source_only'] is True and seal['current_effect'] == rec['current_effect']
    changed = set(git('diff',BASE,'--name-only').splitlines()) | set(git('ls-files','--others','--exclude-standard').splitlines())
    assert changed == FILES, changed
    subprocess.check_call(['git','merge-base','--is-ancestor',BASE,'HEAD'],cwd=ROOT)
    if git('rev-parse','HEAD') != BASE:
        assert not git('status','--porcelain')
    print(json.dumps(dict(status=STATUS,increment='I242',input_pins=1007,preserved_published_files=699,new_files=5,
        criteria=len(CRITERIA),inherited_documentary_rejections=len(review['inherited_I241_rejection_checks']),
        additional_documentary_rejections=len(review['additional_I242_rejection_checks']),findings=review['findings'],
        SD01_stop_active=True,prelaunch_gates_closed=0,resource_obligations_closed=0,D5_closed=False,git_head=git('rev-parse','HEAD')),sort_keys=True))


if __name__ == '__main__':
    main()
