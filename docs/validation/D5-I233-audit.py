#!/usr/bin/env python3
"""I233 W05 negative successor requalification dossier. Documentary JSON/Git only."""
import copy
import hashlib
import io
import json
import runpy
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
P = 'docs/validation/'
BASE = 'b7865813ecebe5f8461d794a54eb29edc13baa74'
DATE = '2026-11-24'
PLAN = P+'D5-I223-PRELAUNCH-RESOURCE-CLOSURE-PLAN.json'
CE01 = P+'D5-I197-CE01-SCOPE-AND-DECISION-BOUNDARY-CANDIDATE-02.json'
CE07 = P+'D5-I193-CE07-RESOURCE-AND-COMPATIBILITY-JOIN-CANDIDATE.json'
CE07_REVIEW = P+'D5-I212-I211-documentary-review.json'
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
CONTRACT = P+'D5-I130-PLATFORM-CONTRACT-CANDIDATE.json'
PRIOR_RECON = P+'D5-I232-I231-source-reconstruction.json'
PRIOR_REVIEW = P+'D5-I232-I231-documentary-review.json'
PRIOR_AUDIT = P+'D5-I232-audit.py'
PRIOR_SEAL = P+'D5-I232-integrity.json'
PRIOR_DOC = 'docs/design/D5-I232-I231-W04-REVIEW.md'
PRIOR_FILES = {PRIOR_RECON,PRIOR_REVIEW,PRIOR_AUDIT,PRIOR_SEAL,PRIOR_DOC}
SUBJECT = P+'D5-I223-W05-SUCCESSOR-REQUALIFICATION-CANDIDATE.json'
PREP = P+'D5-I233-preparation-review.json'
AUDIT = P+'D5-I233-audit.py'
SEAL = P+'D5-I233-integrity.json'
DOC = 'docs/design/D5-I233-W05-SUCCESSOR-REQUALIFICATION.md'
FILES = {SUBJECT,PREP,AUDIT,SEAL,DOC}
STATUS = 'PASS_STATIC_SOURCE_ONLY_W05_REQUALIFICATION_MISSING_SD01_ACTIVE_NOT_ADMITTED'


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


def build_candidate():
    plan,join,census,units,atomic = rd(PLAN),rd(CE07),rd(CENSUS)['assertion_root_census']['rows'],rd(UNITS)['rows'],rd(ATOMIC)['rows']
    work = plan['work_packages'][4]
    pins = {**rd(PRIOR_RECON)['input_pins'],**{p:sha(p) for p in sorted(PRIOR_FILES)}}
    assert len(pins) == 962
    inventory = sorted({PLAN,PRIOR_REVIEW,CE01,CE07,CE07_REVIEW,CENSUS,UNITS,ATOMIC,MANIFEST,PROFILE,PROTO,OUTPUT,TRANSPORT,SPEC,PACK,CONTRACT})
    groups = sorted({r['test_id'].split('.')[0] for r in census})
    inherited = dict(operand_cases=179,roots=321,root_groups=12,atomic_sites=30)
    policy_rows = []
    for path,key in [(PROFILE,'semantic_contracts'),(SPEC,'rules')]:
        for i,row in enumerate(rd(path)[key]):
            policy_rows.append(dict(id=('PROFILE-' if path==PROFILE else 'CUSTODY-')+row['id'],source=pin(path,'/'+key+'/'+str(i)),exact_policy=row,actual_successor_path_inventory=None,actual_source_scope_or_proof=None,accepted=False))
    for key in ['route','trust_boundary','endpoint_ownership','argv_and_channel_checks','framing','deadlines_and_cost','one_use_and_permissions','failure_and_outputs']:
        policy_rows.append(dict(id='TRANSPORT-'+key,source=pin(TRANSPORT,'/'+key),exact_policy=rd(TRANSPORT)[key],actual_successor_path_inventory=None,actual_source_scope_or_proof=None,accepted=False))
    families = [
        ('RF01','Effective source/runtime/loader/crypto/caller/platform/ledger closure',SPEC,'/rules/3'),
        ('RF02','All original operands, helper/assertion operands, selectors and rejected prefixes',UNITS,'/source_derivations'),
        ('RF03','Correlated atomic draft/publication/charges/aliases/original-exception/finalization paths',ATOMIC,'/implementation'),
        ('RF04','Canonical parsing/JCS/hash/strict crypto and complete role/preparer/anchor identity checks',PROFILE,'/semantic_contracts'),
        ('RF05','Actual origin/immutable entry/constructor/custody and domain-mapping compatibility',SPEC,'/rules/6'),
        ('RF06','Clock/currentness/revocation and globally atomic durable partial/failure one-use paths',SPEC,'/rules/13'),
        ('RF07','Coordinator pre-admission/paths and independent worker checks before READY/functional imports',PROFILE,'/semantic_contracts/11'),
        ('RF08','Two-pipe ownership/frame EOF/order/attempts/I-A-L correlation and release guards',TRANSPORT,'/framing'),
        ('RF09','Every parent/child exception, rejection, missing/trusted channel and cleanup route',TRANSPORT,'/failure_and_outputs'),
        ('RF10','Both physical Reader ledgers, stable496 paths, fresh reads/listings/copies across phases',PROFILE,'/semantic_contracts/10'),
        ('RF11','Complete context/launch success/failure/timeout/fallback/no-pair outputs and two writes',OUTPUT,'/$defs'),
        ('RF12','All processes/threads/children/native/GC/IO/service/observation and per-attempt costs',CE07,'/per_attempt_cost_coverage')]
    return dict(schema='d5.i233-w05-successor-requalification-candidate.v1',increment='I233',date=DATE,timezone='Europe/Madrid',base_commit=BASE,
        work_package='W05',planned_deliverable_id=work['deliverable_id'],kind='NEGATIVE_REQUALIFICATION_REQUIREMENT_DOSSIER_NOT_SUCCESSOR_CENSUS_NOT_SOURCE_PROOF_NOT_ACCEPTED_REAL_EVIDENCE_PACKAGE',
        status='W05_DOCUMENTARY_PREPARED_SUCCESSOR_INVENTORIES_DERIVATIONS_QUALIFICATION_MISSING_SD01_ACTIVE_NOT_ADMITTED',
        input_pins=pins,work_package_binding=pin(PLAN,'/work_packages/4'),required_deliverables=work['deliverables'],required_exit_predicates=work['exit_predicates'],reject_if=work['reject_if'],needs_separate_future_authority_for=work['needs_separate_future_authority_for'],documentary_inventory=[pin(p) for p in inventory],
        dependency_gate=dict(source=pin(PRIOR_REVIEW,'/documentary_clarifications/0'),required_package_ids=work['depends_on'],W01_accepted=False,W02_accepted=False,W03_accepted=False,W04_accepted=False,SD01_stop_active=True,
            actual_entry_authority_or_accepted_effective_baseline=None,documentary_preparation_not_positive_dependency_progress=True),
        role_scope_matrix=[r for r in rd(CE01)['role_scope_matrix'] if r['id'] in ['R03','R04','R05','R06','R08']],
        actual_proof_author_provider_custody_or_appointment=None,
        inherited_scope_boundary=dict(source=pin(CE07,'/requalification'),exact_requirements=join['requalification'],required_counts=inherited,
            counts_are_historical_obligations_not_actual_successor_inventory=True,
            historical_lexical_census_not_value_or_successor_proof=True,historical_CP03_or_atomicity_code_or_ten_tests_do_not_transfer=True,
            actual_successor_case_root_group_site_or_new_path_inventory=None,actual_successor_counts=None,actual_requalification_or_correlated_atomicity_proof=None),
        historical_operand_obligations=[dict(source=pin(UNITS,'/rows/'+str(i)),historical_census_index=r['I119_census_index'],historical_test_id=census[r['I119_census_index']]['test_id'],historical_root=pin(CENSUS,'/assertion_root_census/rows/'+str(r['I119_census_index'])),
            actual_successor_case_id_or_mapping=None,actual_operand_value_domain_derivation=None,actual_proof_body_hash_or_custody=None,accepted=False) for i,r in enumerate(units)],
        historical_root_obligations=[dict(source=pin(CENSUS,'/assertion_root_census/rows/'+str(i)),historical_census_index=i,historical_test_id=r['test_id'],
            actual_successor_root_or_helper_mapping=None,actual_reachability_and_operand_value_proof=None,actual_proof_body_hash_or_custody=None,accepted=False) for i,r in enumerate(census)],
        historical_group_obligations=[dict(historical_group=g,source=pin(CENSUS,'/assertion_root_census/rows'),historical_census_indices=[i for i,r in enumerate(census) if r['test_id'].split('.')[0]==g],
            actual_successor_group_or_complete_coverage_proof=None,accepted=False) for g in groups],
        historical_atomicity_obligations=[dict(source=pin(ATOMIC,'/rows/'+str(i)),historical_site=r['site'],
            actual_successor_site_or_phase_mapping=None,actual_correlated_metadata_charge_page_alias_original_and_failure_derivation=None,actual_proof_body_hash_or_custody=None,accepted=False) for i,r in enumerate(atomic)],
        atomicity_required_reasoning=dict(source=pin(ATOMIC,'/implementation'),historical_design_reference=rd(ATOMIC)['implementation'],
            exact_successor_all_sites_new_paths_and_interleavings_need_own_proof=True,source_written_or_phase_count_not_atomicity_acceptance=True,
            actual_successor_publication_lock_draft_exception_alias_or_finalization_proof=None,actual_successor_charge_and_lifetime_derivations=None),
        policy_obligation_ledger=policy_rows,
        new_path_family_requirements=[dict(id=i,required_scope=t,source=pin(p,ptr),actual_complete_source_path_inventory=None,actual_rejection_prefix_transitive_and_guard_proof=None,actual_process_phase_allocation_or_work_ledger=None,accepted=False) for i,t,p,ptr in families],
        coverage_completeness=dict(required_policy_rows_are_not_test_count_or_actual_path_census=True,
            all_added_or_changed_success_exception_rejection_timeout_cleanup_fallback_and_transitive_routes_required=True,
            all_effective_process_thread_child_native_crypto_loader_backend_work_and_guards_required=True,
            actual_complete_cross_product_and_source_mapping=None,actual_assumptions_or_proof_bodies=None,actual_reviewer_completeness_record=None),
        schema_obligations=[dict(name=n,source=pin(p,'/$defs/'+n),schema_fragment=rd(p)['$defs'][n]) for p,n in [(PROTO,'proof'),(PROTO,'source_basis'),(PROTO,'resource_index'),(PROTO,'component_request'),(OUTPUT,'context_record'),(OUTPUT,'launch_record'),(OUTPUT,'final_record'),(OUTPUT,'worker'),(OUTPUT,'handshake'),(OUTPUT,'reader_receipt'),(OUTPUT,'diagnostic'),(OUTPUT,'no_pair_diagnostic')]],
        qualification_boundary=dict(source=pin(PROFILE,'/semantic_contracts/9'),historical_manifest=pin(MANIFEST),historical_planned_tests=rd(MANIFEST)['tests'],
            original_ten_test_names_not_final_successor_suite_or_results=True,
            actual_qualification_request_or_permission=None,actual_request_body_hash_or_validity=None,actual_execution_custody_run_record=None,actual_raw_review_seal_or_results=None,
            prior_run_evidence_only_if_genuine_exact_authority_scope_and_provenance=True,
            component_request_separate_from_runtime_request_and_final_E06=True,
            R04_custody_R05_separate_component_review_and_R06_provenance_required_if_runs_exist=True,
            qualification_authorized=False,qualification_or_component_tests_executed=0,codec_crypto_protocol_or_scheduler_tests_run=False,
            no_command_or_test_discovery_import_compile_or_source_execution=True),
        basis_index_boundary=dict(source=pin(CE07,'/accepted_prior_proof_join'),historical_negative_join=join['accepted_prior_proof_join'],
            exact_six_sources_runtime_image_platform_policy_source_BASIS_index_mapping_and_derivations_required=True,
            W05_contributes_source_operand_atomicity_and_coverage_derivations_not_accepted_E01_E05=True,
            W09_joint_BASIS_index_atomicity_scope_and_resource_acceptance_source=pin(PLAN,'/work_packages/8'),
            W09_join_not_reverse_W05_dependency=True,actual_BASIS_or_resource_index_body_hash_or_review=None,
            proof_accepted_flags_strings_schema_constants_and_placeholders_not_complete_proof=True,
            full_self_contained_derivations_and_all_assumptions_must_fit_or_graph_must_be_reviewed_no_truncation=True,
            actual_positive_BASIS_index_or_proof_record_created=False),
        resource_handoff=[
            dict(consumer='W06',source=pin(PLAN,'/work_packages/5'),required='Complete allocation/lifetime/overlap ledger for originals/observer/clones/memo/frames/codecs/Reader/output/native/GC/allocator across processes and all added/rejected paths',actual_successor_allocation_ledger=None,accepted=False),
            dict(consumer='W07',source=pin(PLAN,'/work_packages/6'),required='Complete successor work/operation/process/phase and compatible units including every30 work groups; ten activities/thirty scalar bounds/twenty historical vectors do not automatically map to them',actual_successor_work_group_inventory_or_correspondence=None,accepted=False),
            dict(consumer='W08',source=pin(PLAN,'/work_packages/7'),required='All work/guard/Reader/custody/failure/IO/child/observation terms to exact True wait return tW and success finally tF, compatible with W04 service; no success900 from budgets',actual_successor_phase_and_service_derivation=None,accepted=False)],
        cost_and_scope_boundary=dict(source=pin(CE07,'/per_attempt_cost_coverage'),exact_required_cost_terms=join['per_attempt_cost_coverage'],
            root_groups_atomic_sites_and_work_groups_are_distinct_inventories=True,
            no_old_counts_or_partial_models_as_whole_heap_CPU_IO_service_compatibility_or900_proof=True,
            unknown_work_memory_latency_or_capacity_not_zero=True,actual_resource_or_compatibility_join=None,
            quotas_or_reserves_changed=False,resource_reservations_created=False),
        phase_and_authority_boundary=dict(source=pin(PLAN,'/scope_authentication_and_freeze_order'),exact_plan_order=plan['scope_authentication_and_freeze_order'],
            genuine_effective_baseline_and_known_real_proof_authors_bodies_before_W09_required=True,
            final_freeze_C_mapping_E06_payload_Q_root_claim_or_receipt_not_sole_antecedent_proof=True,
            final_qualification_not_antecedent_run_and_not_authorized=True,W10_freeze_reconciles_same_facts_and_changes_invalidate_affected_proofs=True,
            preserved_final_route_boundary=plan['prelaunch_handoff_and_CE12'],final_binding_references=join['I177_binding_reference'],
            current_authorization=plan['authorization_boundary'],
            allowed_now=['READ_DOCUMENTS_GIT_HASHES_AND_EXACT_PATH_PRESENCE','PREPARE_THIS_NEGATIVE_DOSSIER','RUN_OWN_DOCUMENTARY_AUDIT','COMMIT_AND_PUSH_THIS_UNIT'],
            no_component_product_execution_or_source_implementation_build_probes_crypto_signing_enrollment_provider_contacts=True,
            no_new_Reader_members_channels_helpers_inputs_outputs_or_active_rebind=True,actual_downstream_refresh_rebind_authority_or_destination=False),
        exit_predicate_dispositions=[dict(id='WX%02d'%(i+1),source=pin(PLAN,'/work_packages/4/exit_predicates/'+str(i)),predicate=t,documentary_requirements_prepared=True,actual_evidence=None,actual_primary_R03_R05_R06_review=None,actual_separate_R08_acceptance=None,accepted=False) for i,t in enumerate(work['exit_predicates'])],
        preserved_scope_and_gates=dict(inherited_scope_boundaries=plan['inherited_scope_boundaries'],preserved_negative_gates=plan['preserved_negative_gates'],prelaunch_handoff_and_CE12=plan['prelaunch_handoff_and_CE12']),
        current_effect=dict(W05_documentary_prepared=True,W01_accepted=False,W02_accepted=False,W03_accepted=False,W04_accepted=False,W05_accepted=False,actual_entry_authority_verified=False,
            actual_successor_operand_root_atomicity_route_or_resource_evidence_verified=False,actual_real_evidence_package_created=False,positive_I191_or_BASIS_index_proof_record_created=False,
            actual_evidence_accepted=0,work_packages_accepted=0,prelaunch_gates_closed=0,resource_obligations_closed=0,
            independent_acceptance=False,source_implementation_changed=False,product_or_components_executed=False,quotas_changed=False,reserves_changed=False,resource_reservations_created=False,rebind_applied=False,authority_or_destination_created=False,actual_claim_worker_or_receipt_created=False,
            execution_authorized=False,proposal_enabled=False,D5_closed=False,IR03='NOT_READY'),
        producer=dict(identity='Same Codex assistant/chat as I231/I232',documentary_preparer_only=True,actor_independent=False,competent_R03_review=False,competent_R04_execution_custody=False,competent_R05_review=False,competent_R06_review=False,separate_R08_acceptance=False,external_contacts_made=False),
        publication=dict(commit_and_push_requested=True,publication_not_qualification_source_proof_or_execution_authority=True))


def validate(d):
    assert d['dependency_gate']['SD01_stop_active'] is True and d['dependency_gate']['W03_accepted'] is False and d['dependency_gate']['W04_accepted'] is False, 'dependency_bypass'
    assert d['current_effect']['W05_accepted'] is False, 'W05_accepted'
    assert d['inherited_scope_boundary']['counts_are_historical_obligations_not_actual_successor_inventory'], 'counts_as_inventory'
    assert d['inherited_scope_boundary']['historical_CP03_or_atomicity_code_or_ten_tests_do_not_transfer'], 'historical_transfer'
    assert all(r['actual_successor_case_id_or_mapping'] is None for r in d['historical_operand_obligations']), 'invented_case_mapping'
    assert all(r['accepted'] is False for r in d['historical_root_obligations']), 'root_acceptance'
    assert all(r['actual_correlated_metadata_charge_page_alias_original_and_failure_derivation'] is None for r in d['historical_atomicity_obligations']), 'invented_atomicity'
    assert d['atomicity_required_reasoning']['source_written_or_phase_count_not_atomicity_acceptance'], 'code_as_atomicity'
    assert d['coverage_completeness']['actual_complete_cross_product_and_source_mapping'] is None, 'invented_complete_coverage'
    assert d['coverage_completeness']['all_added_or_changed_success_exception_rejection_timeout_cleanup_fallback_and_transitive_routes_required'], 'omitted_failure_path'
    assert d['qualification_boundary']['qualification_authorized'] is False, 'qualification_authorized'
    assert d['qualification_boundary']['qualification_or_component_tests_executed'] == 0, 'invented_test_run'
    assert d['qualification_boundary']['original_ten_test_names_not_final_successor_suite_or_results'], 'ten_tests_as_suite'
    assert d['qualification_boundary']['component_request_separate_from_runtime_request_and_final_E06'], 'request_collapse'
    assert d['basis_index_boundary']['W05_contributes_source_operand_atomicity_and_coverage_derivations_not_accepted_E01_E05'], 'premature_resources'
    assert d['basis_index_boundary']['W09_join_not_reverse_W05_dependency'], 'reverse_dependency'
    assert d['basis_index_boundary']['actual_positive_BASIS_index_or_proof_record_created'] is False, 'positive_proof_record'
    assert d['basis_index_boundary']['full_self_contained_derivations_and_all_assumptions_must_fit_or_graph_must_be_reviewed_no_truncation'], 'truncated_proof'
    assert d['cost_and_scope_boundary']['root_groups_atomic_sites_and_work_groups_are_distinct_inventories'], 'group_count_collapse'
    assert d['cost_and_scope_boundary']['unknown_work_memory_latency_or_capacity_not_zero'], 'unknown_zero'
    assert d['cost_and_scope_boundary']['quotas_or_reserves_changed'] is False, 'quota_change'
    assert d['phase_and_authority_boundary']['final_freeze_C_mapping_E06_payload_Q_root_claim_or_receipt_not_sole_antecedent_proof'], 'future_E06_as_proof'
    assert d['phase_and_authority_boundary']['no_new_Reader_members_channels_helpers_inputs_outputs_or_active_rebind'], 'hidden_input'
    assert all(r['accepted'] is False for r in d['exit_predicate_dispositions']), 'exit_acceptance'
    assert d['current_effect']['D5_closed'] is False, 'D5_closed'
    assert d == build_candidate(), 'Candidate differs from source reconstruction'
    check_pointers(d)


def rejection_checks(d):
    cases = [
        ('dependency_bypass',('dependency_gate','SD01_stop_active'),False),
        ('W05_accepted',('current_effect','W05_accepted'),True),
        ('counts_as_inventory',('inherited_scope_boundary','counts_are_historical_obligations_not_actual_successor_inventory'),False),
        ('historical_transfer',('inherited_scope_boundary','historical_CP03_or_atomicity_code_or_ten_tests_do_not_transfer'),False),
        ('invented_case_mapping',('historical_operand_obligations',0,'actual_successor_case_id_or_mapping'),'UNAUTHENTICATED_TEST_LABEL_NOT_CASE'),
        ('root_acceptance',('historical_root_obligations',0,'accepted'),True),
        ('invented_atomicity',('historical_atomicity_obligations',0,'actual_correlated_metadata_charge_page_alias_original_and_failure_derivation'),'UNVERIFIED_TEST_LABEL_NOT_PROOF'),
        ('code_as_atomicity',('atomicity_required_reasoning','source_written_or_phase_count_not_atomicity_acceptance'),False),
        ('invented_complete_coverage',('coverage_completeness','actual_complete_cross_product_and_source_mapping'),'UNVERIFIED_TEST_LABEL_NOT_INVENTORY'),
        ('omitted_failure_path',('coverage_completeness','all_added_or_changed_success_exception_rejection_timeout_cleanup_fallback_and_transitive_routes_required'),False),
        ('qualification_authorized',('qualification_boundary','qualification_authorized'),True),
        ('invented_test_run',('qualification_boundary','qualification_or_component_tests_executed'),10),
        ('ten_tests_as_suite',('qualification_boundary','original_ten_test_names_not_final_successor_suite_or_results'),False),
        ('request_collapse',('qualification_boundary','component_request_separate_from_runtime_request_and_final_E06'),False),
        ('premature_resources',('basis_index_boundary','W05_contributes_source_operand_atomicity_and_coverage_derivations_not_accepted_E01_E05'),False),
        ('reverse_dependency',('basis_index_boundary','W09_join_not_reverse_W05_dependency'),False),
        ('positive_proof_record',('basis_index_boundary','actual_positive_BASIS_index_or_proof_record_created'),True),
        ('truncated_proof',('basis_index_boundary','full_self_contained_derivations_and_all_assumptions_must_fit_or_graph_must_be_reviewed_no_truncation'),False),
        ('group_count_collapse',('cost_and_scope_boundary','root_groups_atomic_sites_and_work_groups_are_distinct_inventories'),False),
        ('unknown_zero',('cost_and_scope_boundary','unknown_work_memory_latency_or_capacity_not_zero'),False),
        ('quota_change',('cost_and_scope_boundary','quotas_or_reserves_changed'),True),
        ('future_E06_as_proof',('phase_and_authority_boundary','final_freeze_C_mapping_E06_payload_Q_root_claim_or_receipt_not_sole_antecedent_proof'),False),
        ('hidden_input',('phase_and_authority_boundary','no_new_Reader_members_channels_helpers_inputs_outputs_or_active_rebind'),False),
        ('exit_acceptance',('exit_predicate_dispositions',0,'accepted'),True),
        ('D5_closed',('current_effect','D5_closed'),True)]
    result = []
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
            result.append(dict(case=name,result='REJECTED_DOCUMENTARY_MUTATION_IN_MEMORY'))
        else:
            raise AssertionError(name)
    return result


def build_review():
    d = rd(SUBJECT)
    verify_blobs(d['input_pins'])
    validate(d)
    previous = runpy.run_path(str(ROOT/PRIOR_AUDIT))
    exists = Path.exists
    rec = previous['reconstruct']()
    assert rec == rd(PRIOR_RECON) and previous['build_review'](rec) == rd(PRIOR_REVIEW)
    assert Path.exists is exists
    census = rd(CENSUS)['assertion_root_census']['rows']
    assert len(d['historical_operand_obligations']) == 179 and len(d['historical_root_obligations']) == len(census) == 321
    assert len(d['historical_group_obligations']) == 12 and len(d['historical_atomicity_obligations']) == 30
    assert len({r['historical_census_index'] for r in d['historical_operand_obligations']}) == 179
    assert [r['historical_census_index'] for r in d['historical_root_obligations']] == list(range(321))
    assert sorted(i for row in d['historical_group_obligations'] for i in row['historical_census_indices']) == list(range(321))
    assert len({r['historical_site'] for r in d['historical_atomicity_obligations']}) == 30
    for row in d['historical_operand_obligations']:
        assert row['historical_census_index'] == fragment(row['source'])['I119_census_index']
        assert row['historical_test_id'] == fragment(row['historical_root'])['test_id']
    for group in ['historical_operand_obligations','historical_root_obligations','historical_group_obligations','historical_atomicity_obligations','policy_obligation_ledger','new_path_family_requirements']:
        for row in d[group]:
            assert row['accepted'] is False and all(v is None for k,v in row.items() if k.startswith('actual_'))
    assert len(d['policy_obligation_ledger']) == 38 and len(d['new_path_family_requirements']) == 12 and len(d['schema_obligations']) == 12
    for row in d['policy_obligation_ledger']:
        assert row['exact_policy'] == fragment(row['source'])
    for row in d['schema_obligations']:
        assert row['schema_fragment'] == fragment(row['source'])
    assert [r['id'] for r in d['role_scope_matrix']] == ['R03','R04','R05','R06','R08']
    assert all(r['canonical_actor_id'] is None and r['accepted_appointment'] is False for r in d['role_scope_matrix'])
    assert [r['consumer'] for r in d['resource_handoff']] == ['W06','W07','W08']
    for row in d['phase_and_authority_boundary']['final_binding_references']:
        assert not (ROOT/row['path']).exists() and row['actual_body_sha256'] is None and row['actual_artifact_created'] is False
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
            assert value is False, key
    return dict(schema='d5.i233-preparation-review.v1',increment='I233',date=DATE,timezone='Europe/Madrid',base_commit=BASE,
        status=STATUS,candidate=pin(SUBJECT),work_package=pin(PLAN,'/work_packages/4'),
        counts=dict(input_pins=962,historical_operand_obligations=179,historical_roots=321,historical_root_groups=12,historical_atomic_sites=30,policy_obligations=38,new_path_family_requirements=12,schema_fragments=12,resource_consumers=3,unassigned_role_slots=5,pending_exits=3),
        source_reconstruction=dict(I232_reconstruction_and_review_reproduced=True,prior_publication_mains_called=False,prior_Path_exists_restored=True,no_new_presence_projection=True),
        rejection_checks=rejection_checks(d),current_effect=d['current_effect'],provenance=d['producer'],
        limitations=['W01-W04 remain unaccepted and SD01 active; W05 is a negative requirement dossier, not a successor census, source proof, qualification result or real accepted package.',
            'All179/321/12/30 rows are exact historical references and new-scope obligations. Actual successor mappings, sources/runtime/platform/caller/ledger/crypto closure, complete paths, authors, proof bodies and independent decisions remain absent.',
            'W05 feeds memory/work/phase evidence W06-W08. W09 accepts joint BASIS/index/atomicity/resource evidence; no accepted E01-E05 flags or reverse W05 dependency are manufactured. Final qualification/E06/Q/root/claim/receipt remain separate.',
            'Same assistant checks do not satisfy competent R03/R05/R06 or separate R08; no R04 custody/run exists. No source implementation, execution/import/compile/test discovery, positive codec/crypto or platform/clock/ledger probe is performed.'],
        work_unit=dict(rollback_files=sorted(FILES),verification_command='python3 docs/validation/D5-I233-audit.py',expected_result=STATUS,
            runtime_harness='N/A: own documentary JSON/Git/hash/policy/historical-inventory checks only; no product/components imports/build/compile/tests/benchmarks, codec/crypto positives, scheduler/platform/clock/ledger/claim/process/replay/crash/restart/probes/signing/keygen/enrollment/provisioning/services/contact.',
            over400_lines=True,reason='One W05 negative requalification dossier with exact historical obligations, new-path/policy requirements, handoffs, pins/checks and preservation; overage declared. No PR requested.'),
        publication=dict(commit_and_push_requested=True,publication_not_qualification_source_proof_or_execution_authority=True))


def main():
    review = build_review()
    assert rd(PREP) == review
    prior = rd(PRIOR_SEAL)
    preserved = {**prior['preserved_published649'],**prior['artifacts'],PRIOR_SEAL:sha(PRIOR_SEAL)}
    assert len(preserved) == 654
    seal = rd(SEAL)
    assert seal['schema'] == 'd5.i233-integrity.v1' and seal['base_commit'] == BASE
    assert seal['preserved_published654'] == preserved and set(seal['artifacts']) == FILES-{SEAL}
    for pins in [preserved,seal['artifacts']]:
        for path,digest in pins.items():
            assert sha(path) == digest, path
    assert seal['source_only'] is True and seal['current_effect'] == review['current_effect']
    changed = set(git('diff',BASE,'--name-only').splitlines()) | set(git('ls-files','--others','--exclude-standard').splitlines())
    assert changed == FILES, changed
    subprocess.check_call(['git','merge-base','--is-ancestor',BASE,'HEAD'],cwd=ROOT)
    if git('rev-parse','HEAD') != BASE:
        assert not git('status','--porcelain')
    print(json.dumps(dict(status=STATUS,increment='I233',historical_pins=962,preserved_published_files=654,new_files=5,
        documentary_rejections=len(review['rejection_checks']),counts=review['counts'],current_effect=review['current_effect'],git_head=git('rev-parse','HEAD')),sort_keys=True))


if __name__ == '__main__':
    main()
