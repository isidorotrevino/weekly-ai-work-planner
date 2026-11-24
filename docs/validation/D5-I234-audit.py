#!/usr/bin/env python3
"""I234 documentary W05 review. No product/components or qualification execution."""
import copy
import hashlib
import io
import json
import runpy
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
P = 'docs/validation/'
BASE = '6a3f27548896147fe9e17b669f59a6d601baae98'
DATE = '2026-11-24'
PLAN = P+'D5-I223-PRELAUNCH-RESOURCE-CLOSURE-PLAN.json'
SUBJECT = P+'D5-I223-W05-SUCCESSOR-REQUALIFICATION-CANDIDATE.json'
CE01 = P+'D5-I197-CE01-SCOPE-AND-DECISION-BOUNDARY-CANDIDATE-02.json'
CE07 = P+'D5-I193-CE07-RESOURCE-AND-COMPATIBILITY-JOIN-CANDIDATE.json'
CENSUS = P+'D5-I119-output-operand-envelopes.json'
UNITS = P+'D5-I120-unit-operand-source-proof.json'
ATOMIC = P+'D5-I122-atomicity-implementation.json'
MANIFEST = P+'D5-I122-COMPONENTS-MANIFEST.json'
PROFILE = P+'D5-I185-PGO181-TRUST-PROFILE-CANDIDATE-02.json'
PROTO = P+'D5-I185-PGO181-SCHEMAS-CANDIDATE-02.json'
OUTPUT = P+'D5-I187-CONTEXT-LAUNCH-SCHEMAS-CANDIDATE.json'
TRANSPORT = P+'D5-I189-BOOTSTRAP-TRANSPORT-CONTRACT-CANDIDATE.json'
SPEC = P+'D5-I191-CALLER-IMAGE-CUSTODY-CONTRACT-CANDIDATE.json'
PACK = P+'D5-I191-CALLER-IMAGE-CUSTODY-SCHEMAS-CANDIDATE.json'
ENTRY_REVIEW = P+'D5-I232-I231-documentary-review.json'
PRIOR_AUDIT = P+'D5-I233-audit.py'
PRIOR_PREP = P+'D5-I233-preparation-review.json'
PRIOR_SEAL = P+'D5-I233-integrity.json'
PRIOR_DOC = 'docs/design/D5-I233-W05-SUCCESSOR-REQUALIFICATION.md'
PRIOR_FILES = {SUBJECT,PRIOR_AUDIT,PRIOR_PREP,PRIOR_SEAL,PRIOR_DOC}
RECON = P+'D5-I234-I233-source-reconstruction.json'
REVIEW = P+'D5-I234-I233-documentary-review.json'
AUDIT = P+'D5-I234-audit.py'
SEAL = P+'D5-I234-integrity.json'
DOC = 'docs/design/D5-I234-I233-W05-REVIEW.md'
FILES = {RECON,REVIEW,AUDIT,SEAL,DOC}
STATUS = 'PASS_STATIC_SOURCE_ONLY_W05_REVIEW_REQUALIFICATION_MISSING_NOT_ADMITTED'


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


def check_negative_boundaries(d):
    assert d['dependency_gate']['SD01_stop_active'] is True, 'SD01_bypass'
    assert d['current_effect']['W05_accepted'] is False, 'W05_accepted'
    assert d['inherited_scope_boundary']['counts_are_historical_obligations_not_actual_successor_inventory'], 'counts_as_inventory'
    assert d['inherited_scope_boundary']['historical_lexical_census_not_value_or_successor_proof'], 'lexical_as_value'
    assert d['inherited_scope_boundary']['historical_CP03_or_atomicity_code_or_ten_tests_do_not_transfer'], 'historical_transfer'
    assert all(r['actual_successor_case_id_or_mapping'] is None for r in d['historical_operand_obligations']), 'invented_case'
    assert all(r['accepted'] is False for r in d['historical_root_obligations']), 'root_acceptance'
    assert all(r['actual_correlated_metadata_charge_page_alias_original_and_failure_derivation'] is None for r in d['historical_atomicity_obligations']), 'invented_atomicity'
    assert d['atomicity_required_reasoning']['source_written_or_phase_count_not_atomicity_acceptance'], 'code_as_atomicity'
    assert d['coverage_completeness']['actual_complete_cross_product_and_source_mapping'] is None, 'invented_coverage'
    assert d['coverage_completeness']['all_added_or_changed_success_exception_rejection_timeout_cleanup_fallback_and_transitive_routes_required'], 'omitted_failure'
    assert d['coverage_completeness']['all_effective_process_thread_child_native_crypto_loader_backend_work_and_guards_required'], 'omitted_closure'
    assert d['qualification_boundary']['qualification_authorized'] is False, 'qualification_authority'
    assert d['qualification_boundary']['qualification_or_component_tests_executed'] == 0, 'invented_run'
    assert d['qualification_boundary']['original_ten_test_names_not_final_successor_suite_or_results'], 'ten_tests_as_suite'
    assert d['qualification_boundary']['component_request_separate_from_runtime_request_and_final_E06'], 'request_collapse'
    assert d['qualification_boundary']['actual_qualification_request_or_permission'] is None, 'invented_request'
    assert d['basis_index_boundary']['W05_contributes_source_operand_atomicity_and_coverage_derivations_not_accepted_E01_E05'], 'premature_resources'
    assert d['basis_index_boundary']['W09_join_not_reverse_W05_dependency'], 'reverse_dependency'
    assert d['basis_index_boundary']['actual_positive_BASIS_index_or_proof_record_created'] is False, 'positive_proof_record'
    assert d['basis_index_boundary']['full_self_contained_derivations_and_all_assumptions_must_fit_or_graph_must_be_reviewed_no_truncation'], 'truncated_proof'
    assert d['cost_and_scope_boundary']['root_groups_atomic_sites_and_work_groups_are_distinct_inventories'], 'group_collapse'
    assert d['cost_and_scope_boundary']['unknown_work_memory_latency_or_capacity_not_zero'], 'unknown_zero'
    assert d['cost_and_scope_boundary']['quotas_or_reserves_changed'] is False, 'quota_change'
    assert d['phase_and_authority_boundary']['genuine_effective_baseline_and_known_real_proof_authors_bodies_before_W09_required'], 'late_authentication'
    assert d['phase_and_authority_boundary']['final_freeze_C_mapping_E06_payload_Q_root_claim_or_receipt_not_sole_antecedent_proof'], 'future_final_as_proof'
    assert d['phase_and_authority_boundary']['final_qualification_not_antecedent_run_and_not_authorized'], 'final_as_antecedent'
    assert d['phase_and_authority_boundary']['no_new_Reader_members_channels_helpers_inputs_outputs_or_active_rebind'], 'hidden_input'
    assert all(r['accepted'] is False for r in d['exit_predicate_dispositions']), 'exit_acceptance'
    assert d['current_effect']['D5_closed'] is False and d['current_effect']['execution_authorized'] is False, 'positive_effect'


def inspect_scope(d):
    """Review against source documents independently of I233's builder."""
    check_negative_boundaries(d)
    plan,join,census,units,atomic = rd(PLAN),rd(CE07),rd(CENSUS)['assertion_root_census']['rows'],rd(UNITS)['rows'],rd(ATOMIC)['rows']
    work = plan['work_packages'][4]
    assert d['work_package'] == work['id'] == 'W05' and fragment(d['work_package_binding']) == work
    assert d['planned_deliverable_id'] == work['deliverable_id']
    for target,source in [('required_deliverables','deliverables'),('required_exit_predicates','exit_predicates'),('reject_if','reject_if'),('needs_separate_future_authority_for','needs_separate_future_authority_for')]:
        assert d[target] == work[source]
    assert len(d['required_deliverables']) == len(d['required_exit_predicates']) == 3
    dep = d['dependency_gate']
    assert dep['required_package_ids'] == work['depends_on'] == ['W03','W04']
    assert all(dep[k] is False for k in ['W01_accepted','W02_accepted','W03_accepted','W04_accepted'])
    assert dep['actual_entry_authority_or_accepted_effective_baseline'] is None and dep['documentary_preparation_not_positive_dependency_progress']
    assert fragment(dep['source']) == rd(ENTRY_REVIEW)['documentary_clarifications'][0]
    assert d['role_scope_matrix'] == [r for r in rd(CE01)['role_scope_matrix'] if r['id'] in ['R03','R04','R05','R06','R08']]
    assert work['primary_review_roles'] == ['R03','R05','R06'] and work['separate_acceptor_role'] == 'R08'
    assert d['actual_proof_author_provider_custody_or_appointment'] is None
    inherited = d['inherited_scope_boundary']
    assert inherited['exact_requirements'] == join['requalification'] == fragment(inherited['source'])
    assert inherited['required_counts'] == join['requalification']['required_legacy_scope'] == dict(operand_cases=179,roots=321,root_groups=12,atomic_sites=30)
    assert all(v is None for k,v in inherited.items() if k.startswith('actual_'))
    operand_rows = d['historical_operand_obligations']
    assert len(operand_rows) == len(units) == 179
    assert len({r['historical_census_index'] for r in operand_rows}) == 179
    for i,(row,original) in enumerate(zip(operand_rows,units)):
        index = original['I119_census_index']
        assert row['source'] == pin(UNITS,'/rows/'+str(i)) and fragment(row['source']) == original
        assert row['historical_census_index'] == index and row['historical_test_id'] == census[index]['test_id']
        assert row['historical_root'] == pin(CENSUS,'/assertion_root_census/rows/'+str(index))
    roots = d['historical_root_obligations']
    assert len(roots) == len(census) == 321
    for i,(row,original) in enumerate(zip(roots,census)):
        assert row['historical_census_index'] == i and row['historical_test_id'] == original['test_id']
        assert row['source'] == pin(CENSUS,'/assertion_root_census/rows/'+str(i)) and fragment(row['source']) == original
    groups = d['historical_group_obligations']
    expected_groups = {}
    for i,row in enumerate(census):
        module = row['test_id'].partition('.')[0]
        expected_groups.setdefault(module,[]).append(i)
    assert len(groups) == len(expected_groups) == 12
    assert {r['historical_group']:r['historical_census_indices'] for r in groups} == expected_groups
    assert sorted(i for row in groups for i in row['historical_census_indices']) == list(range(321))
    sites = d['historical_atomicity_obligations']
    assert len(sites) == len(atomic) == 30 and len({r['historical_site'] for r in sites}) == 30
    for i,(row,original) in enumerate(zip(sites,atomic)):
        assert row['historical_site'] == original['site'] and row['source'] == pin(ATOMIC,'/rows/'+str(i))
        assert fragment(row['source']) == original
    for rows in [operand_rows,roots,groups,sites]:
        for row in rows:
            assert row['accepted'] is False and all(v is None for k,v in row.items() if k.startswith('actual_'))
    reason = d['atomicity_required_reasoning']
    assert reason['historical_design_reference'] == rd(ATOMIC)['implementation'] == fragment(reason['source'])
    assert reason['exact_successor_all_sites_new_paths_and_interleavings_need_own_proof']
    assert all(v is None for k,v in reason.items() if k.startswith('actual_'))
    policies = d['policy_obligation_ledger']
    expected_policy = [(PROFILE,'/semantic_contracts/'+str(i),'PROFILE-'+r['id'],r) for i,r in enumerate(rd(PROFILE)['semantic_contracts'])]
    expected_policy += [(SPEC,'/rules/'+str(i),'CUSTODY-'+r['id'],r) for i,r in enumerate(rd(SPEC)['rules'])]
    for key in ['route','trust_boundary','endpoint_ownership','argv_and_channel_checks','framing','deadlines_and_cost','one_use_and_permissions','failure_and_outputs']:
        expected_policy.append((TRANSPORT,'/'+key,'TRANSPORT-'+key,rd(TRANSPORT)[key]))
    assert len(policies) == len(expected_policy) == 38
    for row,(path,pointer,identifier,value) in zip(policies,expected_policy):
        assert row['id'] == identifier and row['source'] == pin(path,pointer) and row['exact_policy'] == value == fragment(row['source'])
        assert row['accepted'] is False and all(v is None for k,v in row.items() if k.startswith('actual_'))
    families = d['new_path_family_requirements']
    assert [r['id'] for r in families] == ['RF%02d'%i for i in range(1,13)]
    assert [(r['source']['path'],r['source']['json_pointer']) for r in families] == [(SPEC,'/rules/3'),(UNITS,'/source_derivations'),(ATOMIC,'/implementation'),(PROFILE,'/semantic_contracts'),(SPEC,'/rules/6'),(SPEC,'/rules/13'),(PROFILE,'/semantic_contracts/11'),(TRANSPORT,'/framing'),(TRANSPORT,'/failure_and_outputs'),(PROFILE,'/semantic_contracts/10'),(OUTPUT,'/$defs'),(CE07,'/per_attempt_cost_coverage')]
    for row in families:
        assert row['required_scope'] and row['accepted'] is False
        assert all(v is None for k,v in row.items() if k.startswith('actual_'))
    coverage = d['coverage_completeness']
    assert coverage['required_policy_rows_are_not_test_count_or_actual_path_census']
    assert all(v is None for k,v in coverage.items() if k.startswith('actual_'))
    assert [(r['source']['path'],r['name']) for r in d['schema_obligations']] == [(PROTO,'proof'),(PROTO,'source_basis'),(PROTO,'resource_index'),(PROTO,'component_request'),(OUTPUT,'context_record'),(OUTPUT,'launch_record'),(OUTPUT,'final_record'),(OUTPUT,'worker'),(OUTPUT,'handshake'),(OUTPUT,'reader_receipt'),(OUTPUT,'diagnostic'),(OUTPUT,'no_pair_diagnostic')]
    for row in d['schema_obligations']:
        assert row['schema_fragment'] == rd(row['source']['path'])['$defs'][row['name']] == fragment(row['source'])
    qualification = d['qualification_boundary']
    assert fragment(qualification['source']) == rd(PROFILE)['semantic_contracts'][9]
    assert qualification['historical_manifest'] == pin(MANIFEST) and qualification['historical_planned_tests'] == rd(MANIFEST)['tests']
    assert len(qualification['historical_planned_tests']) == 10
    assert all(v is None for k,v in qualification.items() if k.startswith('actual_'))
    assert qualification['prior_run_evidence_only_if_genuine_exact_authority_scope_and_provenance']
    assert qualification['R04_custody_R05_separate_component_review_and_R06_provenance_required_if_runs_exist']
    assert qualification['codec_crypto_protocol_or_scheduler_tests_run'] is False and qualification['no_command_or_test_discovery_import_compile_or_source_execution']
    basis = d['basis_index_boundary']
    assert basis['historical_negative_join'] == join['accepted_prior_proof_join'] == fragment(basis['source'])
    assert basis['exact_six_sources_runtime_image_platform_policy_source_BASIS_index_mapping_and_derivations_required']
    assert basis['W09_joint_BASIS_index_atomicity_scope_and_resource_acceptance_source'] == pin(PLAN,'/work_packages/8')
    assert fragment(basis['W09_joint_BASIS_index_atomicity_scope_and_resource_acceptance_source'])['id'] == 'W09'
    assert basis['actual_BASIS_or_resource_index_body_hash_or_review'] is None
    assert basis['proof_accepted_flags_strings_schema_constants_and_placeholders_not_complete_proof']
    handoffs = d['resource_handoff']
    assert [r['consumer'] for r in handoffs] == ['W06','W07','W08']
    for i,row in enumerate(handoffs,5):
        assert row['source'] == pin(PLAN,'/work_packages/'+str(i)) and fragment(row['source'])['id'] == row['consumer']
        assert row['required'] and row['accepted'] is False and all(v is None for k,v in row.items() if k.startswith('actual_'))
    cost = d['cost_and_scope_boundary']
    assert cost['exact_required_cost_terms'] == join['per_attempt_cost_coverage'] == fragment(cost['source'])
    assert cost['exact_required_cost_terms']['per_process_Reader_ledger_count'] == 2
    assert cost['no_old_counts_or_partial_models_as_whole_heap_CPU_IO_service_compatibility_or900_proof']
    assert cost['actual_resource_or_compatibility_join'] is None and cost['resource_reservations_created'] is False
    phase = d['phase_and_authority_boundary']
    assert phase['exact_plan_order'] == plan['scope_authentication_and_freeze_order'] == fragment(phase['source'])
    assert phase['W10_freeze_reconciles_same_facts_and_changes_invalidate_affected_proofs']
    assert phase['preserved_final_route_boundary'] == plan['prelaunch_handoff_and_CE12']
    assert phase['final_binding_references'] == join['I177_binding_reference']
    for row in phase['final_binding_references']:
        assert not (ROOT/row['path']).exists() and row['actual_body_sha256'] is None and row['actual_artifact_created'] is False and row['execution_authorized'] is False
    assert phase['current_authorization'] == plan['authorization_boundary']
    assert phase['current_authorization']['current_run_command'] is None and all(v is False for k,v in phase['current_authorization'].items() if k.endswith('_authorized'))
    assert len(phase['allowed_now']) == 4 and phase['no_component_product_execution_or_source_implementation_build_probes_crypto_signing_enrollment_provider_contacts']
    assert phase['actual_downstream_refresh_rebind_authority_or_destination'] is False
    exits = d['exit_predicate_dispositions']
    assert len(exits) == 3 and [r['predicate'] for r in exits] == work['exit_predicates']
    for row in exits:
        assert row['documentary_requirements_prepared'] is True and fragment(row['source']) == row['predicate']
        assert all(v is None for k,v in row.items() if k.startswith('actual_'))
    for key in ['inherited_scope_boundaries','preserved_negative_gates','prelaunch_handoff_and_CE12']:
        assert d['preserved_scope_and_gates'][key] == plan[key]
    for row in d['preserved_scope_and_gates']['preserved_negative_gates']:
        assert fragment({**row['source'],'json_pointer':row['json_pointer']}) == row['observed_value']
    for path in rd(PACK)['$defs']['source_bindings']['required']:
        assert not (ROOT/path).exists()
    for key,value in d['current_effect'].items():
        if key == 'W05_documentary_prepared':
            assert value is True
        elif key == 'IR03':
            assert value == 'NOT_READY'
        elif key in ['actual_evidence_accepted','work_packages_accepted','prelaunch_gates_closed','resource_obligations_closed']:
            assert type(value) is int and value == 0
        else:
            assert value is False
    assert all(d['producer'][k] is False for k in ['actor_independent','competent_R03_review','competent_R04_execution_custody','competent_R05_review','competent_R06_review','separate_R08_acceptance','external_contacts_made'])
    check_pointers(d)


def reconstruct():
    d = rd(SUBJECT)
    pins = {**d['input_pins'],**{p:sha(p) for p in sorted(PRIOR_FILES)}}
    assert len(pins) == 967
    verify_blobs(pins)
    inspect_scope(d)
    criteria = [
        ('RC01','Exact three I223 W05 deliverables/exits and authority/rejection clauses','/work_package_binding'),
        ('RC02','W03/W04 unaccepted and SD01 active; five review/custody roles unassigned','/dependency_gate'),
        ('RC03','179 exact I120 operand obligations link to I119 census without successor mapping/proof','/historical_operand_obligations'),
        ('RC04','321 exact historical roots and12 groups partition the historical indices only','/historical_group_obligations'),
        ('RC05','30 exact I122 sites and draft/publication/alias/charge reasoning do not prove successor atomicity','/historical_atomicity_obligations'),
        ('RC06','Historical CP03, lexical reachability, source-written repair and ten tests do not transfer','/inherited_scope_boundary'),
        ('RC07','38 exact profile/custody/transport policy obligations preserved as requirements','/policy_obligation_ledger'),
        ('RC08','12 route families require all new success/failure/transitive/process paths; not complete code census','/new_path_family_requirements'),
        ('RC09','12 exact schema fragments are policy, not positive proof/BASIS/index/output records','/schema_obligations'),
        ('RC10','Any prior qualification requires genuine exact separate permission/custody/provenance; none run','/qualification_boundary'),
        ('RC11','W05 contributes derivations; W09 joint BASIS/index/atomicity/resource acceptance not advanced or reverse dependency','/basis_index_boundary'),
        ('RC12','W06 memory/lifetimes handoff remains without actual allocation proof','/resource_handoff/0'),
        ('RC13','W07 work/units/all30 correspondence distinct from12 root groups/30 sites and old counts','/resource_handoff/1'),
        ('RC14','W08 exact True wait return/finally/service/900 handoff remains unproved','/resource_handoff/2'),
        ('RC15','Both Reader ledgers and all per-attempt costs in full scope; unknowns not zero','/cost_and_scope_boundary'),
        ('RC16','Actual baseline/authors/bodies before W09; future E06/root/bundle/freeze not sole antecedent','/phase_and_authority_boundary'),
        ('RC17','Three exits and genuine independent reviews remain pending; no actual package or records','/exit_predicate_dispositions'),
        ('RC18','No quota/resource/execution/gate/D5 promotion; inherited certificate and deferred CE12 preserved','/preserved_scope_and_gates')]
    return dict(schema='d5.i234-i233-source-reconstruction.v1',increment='I234',date=DATE,timezone='Europe/Madrid',base_commit=BASE,
        subject=pin(SUBJECT),plan=pin(PLAN,'/work_packages/4'),input_pins=pins,
        criteria=[dict(id=i,criterion=t,subject=pin(SUBJECT,p),result='DOCUMENTARY_CONSISTENCY_CONFIRMED_NOT_REAL_ACCEPTANCE') for i,t,p in criteria],
        historical_group_partition=[dict(group=r['historical_group'],root_count=len(r['historical_census_indices']),actual_successor_group_mapping=None) for r in d['historical_group_obligations']],
        counts=dict(input_pins=967,criteria=18,historical_operands=179,historical_roots=321,historical_root_groups=12,historical_atomic_sites=30,policy_obligations=38,new_path_families=12,schema_fragments=12,resource_consumers=3,unassigned_role_slots=5,pending_exits=3),
        current_effect={**d['current_effect'],'W05_documentary_reviewed':True},methodological_review_not_independent_R03_R05_R06_R04_custody_or_separate_R08=True)


def rejection_checks():
    cases = [
        ('SD01_bypass',('dependency_gate','SD01_stop_active'),False),
        ('W05_accepted',('current_effect','W05_accepted'),True),
        ('counts_as_inventory',('inherited_scope_boundary','counts_are_historical_obligations_not_actual_successor_inventory'),False),
        ('lexical_as_value',('inherited_scope_boundary','historical_lexical_census_not_value_or_successor_proof'),False),
        ('historical_transfer',('inherited_scope_boundary','historical_CP03_or_atomicity_code_or_ten_tests_do_not_transfer'),False),
        ('invented_case',('historical_operand_obligations',0,'actual_successor_case_id_or_mapping'),'UNAUTHENTICATED_TEST_LABEL_NOT_CASE'),
        ('root_acceptance',('historical_root_obligations',0,'accepted'),True),
        ('invented_atomicity',('historical_atomicity_obligations',0,'actual_correlated_metadata_charge_page_alias_original_and_failure_derivation'),'UNVERIFIED_TEST_LABEL_NOT_PROOF'),
        ('code_as_atomicity',('atomicity_required_reasoning','source_written_or_phase_count_not_atomicity_acceptance'),False),
        ('invented_coverage',('coverage_completeness','actual_complete_cross_product_and_source_mapping'),'UNVERIFIED_TEST_LABEL_NOT_INVENTORY'),
        ('omitted_failure',('coverage_completeness','all_added_or_changed_success_exception_rejection_timeout_cleanup_fallback_and_transitive_routes_required'),False),
        ('omitted_closure',('coverage_completeness','all_effective_process_thread_child_native_crypto_loader_backend_work_and_guards_required'),False),
        ('qualification_authority',('qualification_boundary','qualification_authorized'),True),
        ('invented_run',('qualification_boundary','qualification_or_component_tests_executed'),10),
        ('ten_tests_as_suite',('qualification_boundary','original_ten_test_names_not_final_successor_suite_or_results'),False),
        ('request_collapse',('qualification_boundary','component_request_separate_from_runtime_request_and_final_E06'),False),
        ('invented_request',('qualification_boundary','actual_qualification_request_or_permission'),'UNAUTHENTICATED_TEST_LABEL_NOT_PERMISSION'),
        ('premature_resources',('basis_index_boundary','W05_contributes_source_operand_atomicity_and_coverage_derivations_not_accepted_E01_E05'),False),
        ('reverse_dependency',('basis_index_boundary','W09_join_not_reverse_W05_dependency'),False),
        ('positive_proof_record',('basis_index_boundary','actual_positive_BASIS_index_or_proof_record_created'),True),
        ('truncated_proof',('basis_index_boundary','full_self_contained_derivations_and_all_assumptions_must_fit_or_graph_must_be_reviewed_no_truncation'),False),
        ('group_collapse',('cost_and_scope_boundary','root_groups_atomic_sites_and_work_groups_are_distinct_inventories'),False),
        ('unknown_zero',('cost_and_scope_boundary','unknown_work_memory_latency_or_capacity_not_zero'),False),
        ('quota_change',('cost_and_scope_boundary','quotas_or_reserves_changed'),True),
        ('late_authentication',('phase_and_authority_boundary','genuine_effective_baseline_and_known_real_proof_authors_bodies_before_W09_required'),False),
        ('future_final_as_proof',('phase_and_authority_boundary','final_freeze_C_mapping_E06_payload_Q_root_claim_or_receipt_not_sole_antecedent_proof'),False),
        ('final_as_antecedent',('phase_and_authority_boundary','final_qualification_not_antecedent_run_and_not_authorized'),False),
        ('hidden_input',('phase_and_authority_boundary','no_new_Reader_members_channels_helpers_inputs_outputs_or_active_rebind'),False),
        ('exit_acceptance',('exit_predicate_dispositions',0,'accepted'),True),
        ('positive_effect',('current_effect','D5_closed'),True)]
    out = []
    for name,path,value in cases:
        mutant = copy.deepcopy(rd(SUBJECT))
        target = mutant
        for key in path[:-1]:
            target = target[key]
        target[path[-1]] = value
        try:
            inspect_scope(mutant)
        except AssertionError as error:
            assert str(error) == name, (name,str(error))
            out.append(dict(case=name,result='REJECTED_DOCUMENTARY_MUTATION_IN_MEMORY'))
        else:
            raise AssertionError(name)
    return out


def build_review(rec):
    previous = runpy.run_path(str(ROOT/PRIOR_AUDIT))
    exists = Path.exists
    assert previous['build_candidate']() == rd(SUBJECT)
    assert previous['build_review']() == rd(PRIOR_PREP)
    assert Path.exists is exists
    return dict(schema='d5.i234-i233-documentary-review.v1',increment='I234',date=DATE,timezone='Europe/Madrid',base_commit=BASE,
        status=STATUS,subject=pin(SUBJECT),reconstruction=pin(RECON),verdict='W05_DOCUMENTARY_REQUALIFICATION_OBLIGATIONS_AND_PHASE_BOUNDARIES_CONSISTENT_SUCCESSOR_PROOF_MISSING_NOT_ACCEPTED',
        findings=[],finding_count=0,criteria=rec['criteria'],counts=rec['counts'],
        documentary_clarifications=[
            dict(id='N01',subject='Historical obligations versus successor proof',disposition='179/321/12/30 are exact historical reference obligations with null successor mapping/derivation/acceptance. Lexical reachability, inherited CP03, source-written atomicity, ten test names or typed flags do not recertify the successor. New closure/routes may require additional obligations; old counts are not an exhaustive new code census.'),
            dict(id='N02',subject='Policy families and complete coverage',disposition='38 policy rows,12 route families and12 schema fragments are requirements, not actual complete code/path/test inventories or emitted positive records. All effective success/failure/rejection/timeout/cleanup/fallback/transitive/guard/process/native/crypto/Reader/output work needs genuine source mapping, assumptions and complete proof bodies.'),
            dict(id='N03',subject='W05 handoff and W09 joint acceptance',disposition='W05 contributes source/operand/atomicity/coverage derivations for W06 allocations/lifetimes, W07 complete work/units/all30 correspondence and W08 phases/service. W09 performs joint genuine BASIS/index/atomicity/scope/resource acceptance after W06-W08. No accepted E01-E05 flag or reverse W05 dependency is created. Root groups, atomic sites and all30 work groups remain distinct.'),
            dict(id='N04',subject='Qualification, final route and provenance',disposition='Prior qualification is usable only if genuine exact separate permission and R04 custody/R05 separate review/R06 provenance exist; none are supplied or executed. Final E06 is distinct and deferred. Binding order manifest then final raw/review/seal then payload/Q/root does not require a future root to authenticate an antecedent run. No future freeze/bundle/root/final result is sole prior proof.'),
            dict(id='N05',subject='Authority, resources and independence',disposition='W03/W04 unaccepted and SD01 active; all real authors/baselines/bodies must be authenticated before W09. Both Readers and all per-attempt costs remain in complete resource/phase composition; no unknown zero, hidden helper/read, quota/reserve change or proof of successful900. Same assistant checks do not provide competent independent R03/R05/R06, R04 run custody or separate R08 acceptance.')],
        source_replay=dict(I233_candidate_and_preparation_review_reproduced=True,prior_publication_mains_called=False,prior_Path_exists_restored=True,no_new_presence_projection=True),
        rejection_checks=rejection_checks(),current_effect=rec['current_effect'],
        provenance=dict(preparer_and_reviewer='Same Codex assistant/chat as I233',methodological_only=True,actor_independent=False,competent_R03_review=False,competent_R04_execution_custody=False,competent_R05_review=False,competent_R06_review=False,separate_R08_acceptance=False,external_contacts=False),
        next_step='Documentary W05 review complete. Positive progress remains stopped at SD01 pending genuine authority, accepted W03/W04 baseline and complete successor proof/qualification evidence; no implementation, qualification, contact or operational work initiated.',
        work_unit=dict(rollback_files=sorted(FILES),verification_command='python3 docs/validation/D5-I234-audit.py',expected_result=STATUS,
            runtime_harness='N/A: own documentary JSON/Git/hash/historical-inventory/policy/phase comparisons only; no product/components imports/build/compile/test discovery/tests/benchmarks, codec/crypto positives, scheduler/platform/clock/ledger/claim/process/replay/crash/restart/probes/signing/keygen/enrollment/provisioning/services/contact.',
            over400_lines=True,reason='One W05 review with exact pins, independently checked historical references and group partition, policy/phase/handoff comparisons, negative checks and preservation; overage declared. No PR requested.'),
        publication=dict(commit_and_push_requested=True,publication_not_qualification_source_proof_or_execution_authority=True))


def main():
    rec = reconstruct()
    assert rd(RECON) == rec
    review = build_review(rec)
    assert rd(REVIEW) == review
    prior = rd(PRIOR_SEAL)
    preserved = {**prior['preserved_published654'],**prior['artifacts'],PRIOR_SEAL:sha(PRIOR_SEAL)}
    assert len(preserved) == 659
    seal = rd(SEAL)
    assert seal['schema'] == 'd5.i234-integrity.v1' and seal['base_commit'] == BASE
    assert seal['preserved_published659'] == preserved and set(seal['artifacts']) == FILES-{SEAL}
    for pins in [preserved,seal['artifacts']]:
        for path,digest in pins.items():
            assert sha(path) == digest, path
    assert seal['source_only'] is True and seal['current_effect'] == rec['current_effect']
    changed = set(git('diff',BASE,'--name-only').splitlines()) | set(git('ls-files','--others','--exclude-standard').splitlines())
    assert changed == FILES, changed
    subprocess.check_call(['git','merge-base','--is-ancestor',BASE,'HEAD'],cwd=ROOT)
    if git('rev-parse','HEAD') != BASE:
        assert not git('status','--porcelain')
    print(json.dumps(dict(status=STATUS,increment='I234',historical_pins=967,preserved_published_files=659,new_files=5,
        criteria=18,findings=0,documentary_rejections=len(review['rejection_checks']),current_effect=rec['current_effect'],git_head=git('rev-parse','HEAD')),sort_keys=True))


if __name__ == '__main__':
    main()
