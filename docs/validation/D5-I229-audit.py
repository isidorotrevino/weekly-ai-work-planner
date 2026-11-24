#!/usr/bin/env python3
"""I229 W03 negative source/image/runtime dossier. Documentary JSON/Git only."""
import copy
import hashlib
import io
import json
import runpy
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
P = 'docs/validation/'
BASE = 'dd241bbec9bedcc19349f04cd685187d150b08c8'
DATE = '2026-11-24'
PLAN = P+'D5-I223-PRELAUNCH-RESOURCE-CLOSURE-PLAN.json'
W01 = P+'D5-I223-W01-TARGET-SCOPE-AUTHORITY-CANDIDATE.json'
W02 = P+'D5-I223-W02-PEOPLE-AND-ANCHORS-CANDIDATE.json'
CE01 = P+'D5-I197-CE01-SCOPE-AND-DECISION-BOUNDARY-CANDIDATE-02.json'
CE04 = P+'D5-I193-CE04-IMAGE-SOURCE-BASELINE-CANDIDATE.json'
CE04_REVIEW = P+'D5-I206-I205-documentary-review.json'
P02 = P+'D5-PFC126-03-E01-RUNTIME-IDENTITY.json'
P02_REVIEW = P+'D5-I136-P02-documentary-review.json'
P03 = P+'D5-PFC126-03-E04-PLATFORM-ENVELOPE.json'
P03_REVIEW = P+'D5-I138-P03-documentary-review.json'
SPEC = P+'D5-I191-CALLER-IMAGE-CUSTODY-CONTRACT-CANDIDATE.json'
PACK = P+'D5-I191-CALLER-IMAGE-CUSTODY-SCHEMAS-CANDIDATE.json'
PRIOR_RECON = P+'D5-I228-I227-source-reconstruction.json'
PRIOR_REVIEW = P+'D5-I228-I227-documentary-review.json'
PRIOR_AUDIT = P+'D5-I228-audit.py'
PRIOR_SEAL = P+'D5-I228-integrity.json'
PRIOR_DOC = 'docs/design/D5-I228-I227-W02-REVIEW.md'
PRIOR_FILES = {PRIOR_RECON,PRIOR_REVIEW,PRIOR_AUDIT,PRIOR_SEAL,PRIOR_DOC}
SUBJECT = P+'D5-I223-W03-SOURCES-IMAGE-RUNTIME-CANDIDATE.json'
PREP = P+'D5-I229-preparation-review.json'
AUDIT = P+'D5-I229-audit.py'
SEAL = P+'D5-I229-integrity.json'
DOC = 'docs/design/D5-I229-W03-SOURCES-IMAGE-RUNTIME.md'
FILES = {SUBJECT,PREP,AUDIT,SEAL,DOC}
STATUS = 'PASS_STATIC_SOURCE_ONLY_W03_SOURCES_IMAGE_RUNTIME_MISSING_SD01_ACTIVE_NOT_ADMITTED'


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
    plan,baseline,pack,spec = rd(PLAN),rd(CE04),rd(PACK)['$defs'],rd(SPEC)
    w = plan['work_packages'][2]
    pins = {**rd(PRIOR_RECON)['input_pins'],**{p:sha(p) for p in sorted(PRIOR_FILES)}}
    assert len(pins) == 942
    inventory = sorted({PLAN,W01,W02,PRIOR_REVIEW,CE01,CE04,CE04_REVIEW,P02,P02_REVIEW,P03,P03_REVIEW,SPEC,PACK})
    source_by_path = {r['logical_path']:r for r in baseline['source_to_image_missing_inventory']}
    source_rows = [dict(**source_by_path[path],source=pin(CE04,'/source_to_image_missing_inventory/'+str(next(i for i,r in enumerate(baseline['source_to_image_missing_inventory']) if r['logical_path']==path))),actual_path_exists=(ROOT/path).exists()) for path in pack['source_bindings']['required']]
    consumers = {'CE04':['W03'],'CE05':['W04'],'CE06':['W04'],'CE07':['W05','W06','W07','W08','W09'],'CE08':['W10']}
    requirements = [dict(id=r['id'],source=pin(CE04,'/image_source_requirements/'+str(i)),exact_requirement=r,
        consumer_step=r['consumer_step'],work_package_consumers=consumers[r['consumer_step']],deferred_from_W03=r['consumer_step']!='CE04',actual_evidence=None,actual_primary_review=None,actual_separate_acceptance=None,accepted=False)
        for i,r in enumerate(baseline['image_source_requirements'])]
    closure = [
        ('EXACT_INTERPRETER_STDLIB_FROZEN_NATIVE',P02,'/exact_interpreter_stdlib_frozen_builtin_extension_closure','Exact interpreter executable/config/version/ABI and all stdlib, builtin/frozen/native/crypto bodies with authenticated identity/closure evidence'),
        ('LOADER_AND_FIRST_ENTRY',CE04,'/source_scope_policy','Complete import/load resolution and immutable initial module origin; no cwd/PYTHONPATH/sitecustomize or unbound helper trust'),
        ('NATIVE_ALLOCATOR_GC_KERNEL',P02,'/native_dependency_allocator_kernel_config_pins','Exact native/crypto/transitive libraries, allocator/GC/build configuration and relevant kernel/ABI pins; no unproved native overhead'),
        ('SOURCE_BINARY_BUILD_MAPPING',P02,'/source_binary_build_correspondence','Real source-to-binary/image equivalence, recipe/toolchain identity and complete provenance, not a digest assertion alone'),
        ('ACTUAL_TARGET_IDENTITY',P02,'/actual_target_not_just_observed_local_reference','Actual accepted target identity; historical I122/local auditor observations do not qualify successor'),
        ('IMAGE_DEPENDENCY_MEMBERS',PACK,'/$defs/image_dependency','Complete authentic image dependency manifest under typed bounds, sorted/unique per policy; no truncation or omitted references'),
        ('PLATFORM_RUNTIME_PINS',P03,'/platform_runtime_pin_set_and_validity','Compatibility with P03 full platform/runtime pin set and validity; actual platform guarantees remain W04 obligations'),
        ('SERVICE_AND_PROCESS_DOMAINS',P02,'/clock_and_process_service_domain_identity','Identify compatible clock/process/service domains and their provenance; no clock sampling or CPU/service attestation is inferred')]
    return dict(schema='d5.i229-w03-sources-image-runtime-candidate.v1',increment='I229',date=DATE,timezone='Europe/Madrid',base_commit=BASE,
        work_package='W03',planned_deliverable_id=w['deliverable_id'],
        kind='NEGATIVE_SOURCE_IMAGE_RUNTIME_BASELINE_DOSSIER_NOT_SOURCE_IMPLEMENTATION_NOT_IMAGE_MANIFEST_NOT_ACCEPTED_REAL_EVIDENCE_PACKAGE',
        status='W03_DOCUMENTARY_PREPARED_SOURCES_IMAGE_RUNTIME_MISSING_W01_W02_UNACCEPTED_SD01_ACTIVE_NOT_ADMITTED',
        input_pins=pins,work_package_binding=pin(PLAN,'/work_packages/2'),required_deliverables=w['deliverables'],required_exit_predicates=w['exit_predicates'],
        reject_if=w['reject_if'],needs_separate_future_authority_for=w['needs_separate_future_authority_for'],documentary_inventory=[pin(p) for p in inventory],
        dependency_gate=dict(source=pin(PRIOR_REVIEW,'/documentary_clarifications/0'),required_package_ids=w['depends_on'],
            W01_accepted=False,W02_accepted=False,actual_entry_authority=None,actual_prior_scope_or_anchor_acceptance=None,SD01_stop_active=True,
            documentary_preparation_does_not_start_positive_package_progress=True,no_future_bundle_or_downstream_freeze_as_sole_prior_authority=True),
        role_scope_matrix=[r for r in rd(CE01)['role_scope_matrix'] if r['id'] in ['R01','R06','R08']],
        source_to_image_missing_inventory=source_rows,source_scope_policy=baseline['source_scope_policy'],
        actual_image_runtime_state=baseline['actual_image_runtime_state'],runtime_identity_boundary=baseline['runtime_identity_boundary'],
        runtime_platform_reference_boundary=dict(P02=pin(P02),P02_review=pin(P02_REVIEW),P03=pin(P03),P03_review=pin(P03_REVIEW),
            historical_dossiers_and_rejections_not_successor_proof=True,P02_P03_exact_effective_scope_compatibility_required=True,
            actual_successor_runtime_or_platform_compatibility=None,auditor_python_OS_or_environment_not_sampled_or_adopted=True),
        closure_requirement_ledger=[dict(id='CL%02d'%(i+1),kind=k,source=pin(p,ptr),required_evidence=t,actual_complete_inventory=None,actual_body_digests=None,actual_provenance=None,actual_equivalence_derivation=None,accepted=False) for i,(k,p,ptr,t) in enumerate(closure)],
        image_source_requirement_ledger=requirements,
        compiled_policy_requirements=baseline['compiled_policy_requirements'],no_self_embedding_policy=baseline['no_self_embedding_policy'],
        implementation_proof_boundary=dict(source=pin(SPEC,'/rules/3'),
            exact_selected_I191_contract_and_schema_must_be_externally_accepted=True,
            reviewed_six_source_implementation_must_enforce_exact_pinned_policies=True,
            document_pins_or_matching_constants_not_implementation_or_policy_selection_proof=True,
            actual_source_policy_conformance_or_external_selection_proof=None,actual_static_successor_code_review_performed=False),
        contract_rules=[dict(source=pin(SPEC,'/rules/'+str(i)),exact_rule=r) for i,r in enumerate(spec['rules']) if r['id'] in ['K04','K05','K07','K15','K16']],
        schema_obligations=baseline['schema_obligations'],
        phase_boundary=dict(source=pin(PLAN,'/scope_authentication_and_freeze_order'),exact_plan_order=plan['scope_authentication_and_freeze_order'],
            required_baseline_requirement_ids=['IM%02d'%i for i in range(1,7)],
            baseline_immutable_entry_evidence_not_caller_constructor_or_platform_enforcement_proof=True,
            caller_platform_resources_and_final_freeze_remain_own_consumers=True,
            downstream_acceptance_required_as_new_reverse_W03_dependency=False,
            baseline_actor_image_caller_platform_authentication_before_W09_required=True,
            actual_proof_authors_and_complete_bodies_before_W09_required=True,
            W10_reconciles_same_genuine_facts_not_sole_forecast_authentication=True,
            final_record_order=['actor_registry','image_manifest','caller_identity','platform_custody'],final_manifest_before_C_required=True,
            final_manifest_freeze_required_to_prepare_W03=False,actual_final_manifest_or_accepted_source_root=None,
            freeze_and_refresh_policy=baseline['freeze_and_refresh'],actual_downstream_rebind_or_snapshot_refresh=False),
        authority_and_costs=dict(source=pin(PLAN,'/authorization_boundary'),inherited_boundary=plan['authorization_boundary'],
            allowed_now=['READ_DOCUMENTS_GIT_HASHES_AND_EXACT_PATH_PRESENCE','PREPARE_THIS_NEGATIVE_DOSSIER','RUN_OWN_DOCUMENTARY_AUDIT','COMMIT_AND_PUSH_THIS_UNIT'],
            missing_sources_do_not_authorize_implementation_build_import_compile_measurement_or_qualification=True,
            actual_external_material_or_provider=None,actual_action_specific_authority=None,
            no_new_helpers_channels_fds_argv_inputs_outputs_or_ambient_trust=True,
            actual_new_route_or_helpers_created=False,actual_sources_or_image_created=False,
            per_attempt_lookup_freshness_identity_signature_measurement_copies_registry_receipt_native_IO_inside_complete_resource_join=True,
            prior_build_enrollment_or_offline_work_not_free_per_attempt_cost=True,
            actual_heap_CPU_service_compatibility_or900_proof=None,quotas_or_reserves_applied=False),
        exit_predicate_dispositions=[dict(id='WX%02d'%(i+1),source=pin(PLAN,'/work_packages/2/exit_predicates/'+str(i)),predicate=t,documentary_policy_prepared=True,actual_evidence=None,actual_primary_R01_R06_review=None,actual_separate_R08_acceptance=None,accepted=False) for i,t in enumerate(w['exit_predicates'])],
        preserved_scope_and_gates=dict(inherited_scope_boundaries=plan['inherited_scope_boundaries'],preserved_negative_gates=plan['preserved_negative_gates'],prelaunch_handoff_and_CE12=plan['prelaunch_handoff_and_CE12'],existing_CE_dossiers_not_positive_image_runtime_platform_resource_or_final_route_proof=True),
        producer=dict(identity='Same Codex assistant/chat as I227/I228',documentary_preparer_only=True,actor_independent=False,competent_R01_attestation=False,competent_R06_review=False,separate_R08_acceptance=False,external_contacts_made=False),
        current_effect=dict(W03_documentary_prepared=True,W01_accepted=False,W02_accepted=False,W03_accepted=False,actual_entry_authority_verified=False,
            actual_sources_image_runtime_or_policy_implementation_verified=False,actual_real_evidence_package_created=False,positive_I191_record_created=False,
            actual_evidence_accepted=0,work_packages_accepted=0,prelaunch_gates_closed=0,resource_obligations_closed=0,
            independent_acceptance=False,source_implementation_changed=False,product_or_components_executed=False,quotas_changed=False,reserves_changed=False,
            resource_reservations_created=False,rebind_applied=False,authority_or_destination_created=False,actual_claim_worker_or_receipt_created=False,
            execution_authorized=False,proposal_enabled=False,D5_closed=False,IR03='NOT_READY'),
        publication=dict(commit_and_push_requested=True,publication_not_baseline_acceptance_or_implementation_build_or_execution_authority=True))


def validate(d):
    assert d['dependency_gate']['SD01_stop_active'] is True and d['dependency_gate']['W01_accepted'] is False and d['dependency_gate']['W02_accepted'] is False, 'dependency_bypass'
    assert d['current_effect']['W03_accepted'] is False, 'W03_accepted'
    assert all(r['actual_source_sha256'] is None for r in d['source_to_image_missing_inventory']), 'predictive_source_hash'
    assert all(r['actual_path_exists'] is False for r in d['source_to_image_missing_inventory']), 'invented_source_presence'
    assert next(r for r in d['source_to_image_missing_inventory'] if r['logical_path'].endswith('/README.md'))['required_representation'] == 'DOCUMENT', 'README_not_document'
    assert all(r['loaded_by_membership_claimed'] is False for r in d['source_to_image_missing_inventory']), 'membership_as_load'
    assert d['source_scope_policy']['actual_total_bytes'] is None, 'missing_bytes_as_zero'
    assert d['source_scope_policy']['old_I122_proofs_transfer_to_successor'] is False, 'historical_proof_transfer'
    assert d['runtime_identity_boundary']['image_bytes_digest_does_not_substitute_P02'], 'image_as_runtime'
    assert d['runtime_identity_boundary']['target_runtime_or_host_platform_sampled'] is False, 'auditor_runtime_as_target'
    assert d['actual_image_runtime_state']['actual_complete_dependency_closure_verified'] is False, 'invented_closure'
    assert all(r['actual_compiled_value_verified'] is False for r in d['compiled_policy_requirements']), 'document_pin_as_compiled'
    assert d['no_self_embedding_policy']['own_future_image_manifest_bundle_digests_must_not_be_embedded'], 'self_embedding'
    assert d['implementation_proof_boundary']['document_pins_or_matching_constants_not_implementation_or_policy_selection_proof'], 'policy_hash_as_implementation'
    assert d['phase_boundary']['downstream_acceptance_required_as_new_reverse_W03_dependency'] is False, 'reverse_dependency'
    assert d['phase_boundary']['baseline_immutable_entry_evidence_not_caller_constructor_or_platform_enforcement_proof'], 'baseline_as_platform'
    assert d['phase_boundary']['W10_reconciles_same_genuine_facts_not_sole_forecast_authentication'], 'forecast_freeze'
    assert d['authority_and_costs']['missing_sources_do_not_authorize_implementation_build_import_compile_measurement_or_qualification'], 'implicit_implementation_authority'
    assert d['authority_and_costs']['per_attempt_lookup_freshness_identity_signature_measurement_copies_registry_receipt_native_IO_inside_complete_resource_join'], 'omitted_cost'
    assert d['authority_and_costs']['quotas_or_reserves_applied'] is False, 'quota_change'
    assert d['current_effect']['execution_authorized'] is False, 'execution_authorized'
    assert d['current_effect']['D5_closed'] is False, 'D5_closed'
    assert d == build_candidate(), 'Candidate differs from source reconstruction'
    check_pointers(d)


def rejection_checks(d):
    cases = [
        ('dependency_bypass',('dependency_gate','SD01_stop_active'),False),
        ('W03_accepted',('current_effect','W03_accepted'),True),
        ('predictive_source_hash',('source_to_image_missing_inventory',0,'actual_source_sha256'),'INVENTED_NOT_REAL_DIGEST'),
        ('invented_source_presence',('source_to_image_missing_inventory',0,'actual_path_exists'),True),
        ('README_not_document',('source_to_image_missing_inventory',0,'required_representation'),'PYTHON_SOURCE'),
        ('membership_as_load',('source_to_image_missing_inventory',0,'loaded_by_membership_claimed'),True),
        ('missing_bytes_as_zero',('source_scope_policy','actual_total_bytes'),0),
        ('historical_proof_transfer',('source_scope_policy','old_I122_proofs_transfer_to_successor'),True),
        ('image_as_runtime',('runtime_identity_boundary','image_bytes_digest_does_not_substitute_P02'),False),
        ('auditor_runtime_as_target',('runtime_identity_boundary','target_runtime_or_host_platform_sampled'),True),
        ('invented_closure',('actual_image_runtime_state','actual_complete_dependency_closure_verified'),True),
        ('document_pin_as_compiled',('compiled_policy_requirements',0,'actual_compiled_value_verified'),True),
        ('self_embedding',('no_self_embedding_policy','own_future_image_manifest_bundle_digests_must_not_be_embedded'),False),
        ('policy_hash_as_implementation',('implementation_proof_boundary','document_pins_or_matching_constants_not_implementation_or_policy_selection_proof'),False),
        ('reverse_dependency',('phase_boundary','downstream_acceptance_required_as_new_reverse_W03_dependency'),True),
        ('baseline_as_platform',('phase_boundary','baseline_immutable_entry_evidence_not_caller_constructor_or_platform_enforcement_proof'),False),
        ('forecast_freeze',('phase_boundary','W10_reconciles_same_genuine_facts_not_sole_forecast_authentication'),False),
        ('implicit_implementation_authority',('authority_and_costs','missing_sources_do_not_authorize_implementation_build_import_compile_measurement_or_qualification'),False),
        ('omitted_cost',('authority_and_costs','per_attempt_lookup_freshness_identity_signature_measurement_copies_registry_receipt_native_IO_inside_complete_resource_join'),False),
        ('quota_change',('authority_and_costs','quotas_or_reserves_applied'),True),
        ('execution_authorized',('current_effect','execution_authorized'),True),
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
    assert len(d['source_to_image_missing_inventory']) == 6
    assert [r['logical_path'] for r in d['source_to_image_missing_inventory']] == rd(PACK)['$defs']['source_bindings']['required']
    for row in d['source_to_image_missing_inventory']:
        assert (ROOT/row['logical_path']).exists() is False
        assert all(v is None for k,v in row.items() if k.startswith('actual_') and k!='actual_path_exists') and row['accepted'] is False
    assert all(v is None or v is False for v in d['actual_image_runtime_state'].values())
    assert len(d['closure_requirement_ledger']) == 8 and len(d['image_source_requirement_ledger']) == 10
    assert sum(not r['deferred_from_W03'] for r in d['image_source_requirement_ledger']) == 6
    assert len(d['compiled_policy_requirements']) == 7 and len(d['schema_obligations']['definitions']) == 6
    for row in d['compiled_policy_requirements']:
        assert row['documentary_binding']['sha256'] == sha(row['documentary_binding']['path']) == row['required_candidate_policy_sha256']
        assert row['actual_compiled_policy_sha256'] is None and row['actual_independent_policy_selection_acceptance'] is None
    assert [r['id'] for r in d['role_scope_matrix']] == ['R01','R06','R08']
    assert all(r['accepted_appointment'] is False and r['canonical_actor_id'] is None for r in d['role_scope_matrix'])
    for key,value in d['current_effect'].items():
        if key == 'W03_documentary_prepared':
            assert value is True
        elif key == 'IR03':
            assert value == 'NOT_READY'
        elif key in ['actual_evidence_accepted','work_packages_accepted','prelaunch_gates_closed','resource_obligations_closed']:
            assert type(value) is int and value == 0
        else:
            assert value is False, key
    return dict(schema='d5.i229-preparation-review.v1',increment='I229',date=DATE,timezone='Europe/Madrid',base_commit=BASE,
        status=STATUS,candidate=pin(SUBJECT),work_package=pin(PLAN,'/work_packages/2'),
        counts=dict(input_pins=942,source_paths=6,closure_categories=8,image_requirements=10,baseline_requirements=6,deferred_requirements=4,policy_pins=7,schema_fragments=6,unassigned_role_slots=3,pending_exit_predicates=3),
        source_reconstruction=dict(I228_reconstruction_and_review_reproduced=True,prior_publication_mains_called=False,prior_Path_exists_restored=True,no_new_presence_projection=True),
        rejection_checks=rejection_checks(d),current_effect=d['current_effect'],provenance=d['producer'],
        limitations=['W01/W02 unaccepted and SD01 active; W03 is documentary missing-evidence preparation only, not actual source/image/runtime material or a real accepted package.',
            'All source/image/runtime/build/dependency/mapping/external-policy-selection facts remain unavailable. P02/P03 historic dossiers and document pins do not qualify the successor or current auditor environment.',
            'Caller/platform/resource qualification and final freeze remain separate. Actual baseline and proof authors/bodies must be authenticated before W09; W10 cannot retroactively authenticate them.',
            'Same assistant checks do not provide competent R01 attestation, independent R06 review or separate R08 acceptance. No implementation, build, measurement, execution, signing, service or contact is performed.'],
        work_unit=dict(rollback_files=sorted(FILES),verification_command='python3 docs/validation/D5-I229-audit.py',expected_result=STATUS,
            runtime_harness='N/A: own documentary JSON/Git/hash/policy/path-presence checks only; no product/components imports/build/compile/tests/benchmarks, positive codec/crypto, image/runtime/platform measurement, clocks/ledger/claim/processes/signing/keygen/enrollment/provisioning/services/contact.',
            over400_lines=True,reason='One negative W03 source/image/runtime dossier with exact pins, closure/mapping/phase matrices, documentary checks and preservation; overage declared. No PR requested.'),
        publication=dict(commit_and_push_requested=True,publication_not_baseline_acceptance_or_implementation_build_or_execution_authority=True))


def main():
    review = build_review()
    assert rd(PREP) == review
    prior = rd(PRIOR_SEAL)
    preserved = {**prior['preserved_published629'],**prior['artifacts'],PRIOR_SEAL:sha(PRIOR_SEAL)}
    assert len(preserved) == 634
    seal = rd(SEAL)
    assert seal['schema'] == 'd5.i229-integrity.v1' and seal['base_commit'] == BASE
    assert seal['preserved_published634'] == preserved and set(seal['artifacts']) == FILES-{SEAL}
    for pins in [preserved,seal['artifacts']]:
        for path,digest in pins.items():
            assert sha(path) == digest, path
    assert seal['source_only'] is True and seal['current_effect'] == review['current_effect']
    changed = set(git('diff',BASE,'--name-only').splitlines()) | set(git('ls-files','--others','--exclude-standard').splitlines())
    assert changed == FILES, changed
    subprocess.check_call(['git','merge-base','--is-ancestor',BASE,'HEAD'],cwd=ROOT)
    if git('rev-parse','HEAD') != BASE:
        assert not git('status','--porcelain')
    print(json.dumps(dict(status=STATUS,increment='I229',historical_pins=942,preserved_published_files=634,new_files=5,
        documentary_rejections=len(review['rejection_checks']),counts=review['counts'],current_effect=review['current_effect'],git_head=git('rev-parse','HEAD')),sort_keys=True))


if __name__ == '__main__':
    main()
