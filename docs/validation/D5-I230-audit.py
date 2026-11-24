#!/usr/bin/env python3
"""I230 documentary W03 review. No product/components or positive trust operations."""
import copy
import hashlib
import io
import json
import runpy
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
P = 'docs/validation/'
BASE = '2d22dd23247c019389f7af6d42a16646588055bc'
DATE = '2026-11-24'
PLAN = P+'D5-I223-PRELAUNCH-RESOURCE-CLOSURE-PLAN.json'
SUBJECT = P+'D5-I223-W03-SOURCES-IMAGE-RUNTIME-CANDIDATE.json'
CE01 = P+'D5-I197-CE01-SCOPE-AND-DECISION-BOUNDARY-CANDIDATE-02.json'
CE04 = P+'D5-I193-CE04-IMAGE-SOURCE-BASELINE-CANDIDATE.json'
P02 = P+'D5-PFC126-03-E01-RUNTIME-IDENTITY.json'
P03 = P+'D5-PFC126-03-E04-PLATFORM-ENVELOPE.json'
SPEC = P+'D5-I191-CALLER-IMAGE-CUSTODY-CONTRACT-CANDIDATE.json'
PACK = P+'D5-I191-CALLER-IMAGE-CUSTODY-SCHEMAS-CANDIDATE.json'
ENTRY_REVIEW = P+'D5-I228-I227-documentary-review.json'
PRIOR_AUDIT = P+'D5-I229-audit.py'
PRIOR_PREP = P+'D5-I229-preparation-review.json'
PRIOR_SEAL = P+'D5-I229-integrity.json'
PRIOR_DOC = 'docs/design/D5-I229-W03-SOURCES-IMAGE-RUNTIME.md'
PRIOR_FILES = {SUBJECT,PRIOR_AUDIT,PRIOR_PREP,PRIOR_SEAL,PRIOR_DOC}
RECON = P+'D5-I230-I229-source-reconstruction.json'
REVIEW = P+'D5-I230-I229-documentary-review.json'
AUDIT = P+'D5-I230-audit.py'
SEAL = P+'D5-I230-integrity.json'
DOC = 'docs/design/D5-I230-I229-W03-REVIEW.md'
FILES = {RECON,REVIEW,AUDIT,SEAL,DOC}
STATUS = 'PASS_STATIC_SOURCE_ONLY_W03_REVIEW_SOURCES_IMAGE_RUNTIME_MISSING_NOT_ADMITTED'


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


def inspect_scope(d):
    """Independent policy/plan comparisons, separate from the I229 generator."""
    plan,baseline,pack,spec = rd(PLAN),rd(CE04),rd(PACK)['$defs'],rd(SPEC)
    w = plan['work_packages'][2]
    assert d['work_package'] == w['id'] == 'W03'
    assert fragment(d['work_package_binding']) == w and d['planned_deliverable_id'] == w['deliverable_id']
    for target,source in [('required_deliverables','deliverables'),('required_exit_predicates','exit_predicates'),('reject_if','reject_if'),('needs_separate_future_authority_for','needs_separate_future_authority_for')]:
        assert d[target] == w[source]
    assert len(d['required_deliverables']) == len(d['required_exit_predicates']) == 3
    dep = d['dependency_gate']
    assert dep['required_package_ids'] == w['depends_on'] == ['W01','W02']
    assert dep['W01_accepted'] is False and dep['W02_accepted'] is False and dep['SD01_stop_active'] is True, 'dependency_bypass'
    assert dep['actual_entry_authority'] is None and dep['actual_prior_scope_or_anchor_acceptance'] is None
    assert dep['documentary_preparation_does_not_start_positive_package_progress']
    assert dep['no_future_bundle_or_downstream_freeze_as_sole_prior_authority'], 'future_authority'
    assert fragment(dep['source']) == rd(ENTRY_REVIEW)['documentary_clarifications'][0]
    expected_roles = [r for r in rd(CE01)['role_scope_matrix'] if r['id'] in ['R01','R06','R08']]
    assert d['role_scope_matrix'] == expected_roles
    assert w['primary_review_roles'] == ['R01','R06'] and w['separate_acceptor_role'] == 'R08'
    paths = pack['source_bindings']['required']
    assert len(d['source_to_image_missing_inventory']) == len(paths) == 6
    assert [r['logical_path'] for r in d['source_to_image_missing_inventory']] == paths, 'source_scope'
    for row in d['source_to_image_missing_inventory']:
        assert row['actual_path_exists'] is False and not (ROOT/row['logical_path']).exists(), 'source_presence'
        assert row['actual_source_sha256'] is None, 'predictive_hash'
        assert all(v is None for k,v in row.items() if k.startswith('actual_') and k!='actual_path_exists')
        assert row['accepted'] is False and row['loaded_by_membership_claimed'] is False, 'membership_as_load'
        assert row['required_representation'] == ('DOCUMENT' if row['logical_path'].endswith('/README.md') else None), 'README_representation'
        assert {k:v for k,v in row.items() if k not in ['source','actual_path_exists']} == fragment(row['source'])
    scope = d['source_scope_policy']
    assert scope['actual_total_bytes'] is None, 'unknown_bytes_zero'
    assert scope['old_I122_proofs_transfer_to_successor'] is False, 'historical_transfer'
    assert scope == baseline['source_scope_policy'] and scope['six_source_total_design_ceiling_bytes'] == 262144
    assert set(scope['exact_six_paths']) == set(paths)
    assert scope['no_silent_source_scope_enlargement'] and scope['no_unbound_repository_helper_outside_historical480_or_six_sources']
    state = d['actual_image_runtime_state']
    assert state['actual_complete_dependency_closure_verified'] is False, 'invented_closure'
    assert state == baseline['actual_image_runtime_state'] and all(v is None or v is False for v in state.values())
    runtime = d['runtime_identity_boundary']
    assert runtime['image_bytes_digest_distinct_from_runtime_identity'] and runtime['image_bytes_digest_does_not_substitute_P02'], 'image_as_runtime'
    assert runtime['target_runtime_or_host_platform_sampled'] is False, 'auditor_as_target'
    assert runtime == baseline['runtime_identity_boundary']
    assert runtime['historical_P02_runtime_verified'] is False and runtime['historical_P02_is_not_successor_runtime_evidence']
    reference = d['runtime_platform_reference_boundary']
    assert reference['P02'] == pin(P02) and reference['P03'] == pin(P03)
    assert reference['historical_dossiers_and_rejections_not_successor_proof'] and reference['P02_P03_exact_effective_scope_compatibility_required']
    assert reference['actual_successor_runtime_or_platform_compatibility'] is None and reference['auditor_python_OS_or_environment_not_sampled_or_adopted']
    closure = d['closure_requirement_ledger']
    assert [r['kind'] for r in closure] == ['EXACT_INTERPRETER_STDLIB_FROZEN_NATIVE','LOADER_AND_FIRST_ENTRY','NATIVE_ALLOCATOR_GC_KERNEL','SOURCE_BINARY_BUILD_MAPPING','ACTUAL_TARGET_IDENTITY','IMAGE_DEPENDENCY_MEMBERS','PLATFORM_RUNTIME_PINS','SERVICE_AND_PROCESS_DOMAINS']
    for row in closure:
        assert row['required_evidence'] and row['accepted'] is False
        assert all(v is None for k,v in row.items() if k.startswith('actual_'))
    assert closure[0]['source'] == pin(P02,'/exact_interpreter_stdlib_frozen_builtin_extension_closure')
    assert closure[2]['source'] == pin(P02,'/native_dependency_allocator_kernel_config_pins')
    assert closure[3]['source'] == pin(P02,'/source_binary_build_correspondence')
    assert closure[4]['source'] == pin(P02,'/actual_target_not_just_observed_local_reference')
    assert closure[5]['source'] == pin(PACK,'/$defs/image_dependency')
    assert closure[6]['source'] == pin(P03,'/platform_runtime_pin_set_and_validity')
    assert closure[7]['source'] == pin(P02,'/clock_and_process_service_domain_identity')
    consumers = {'CE04':['W03'],'CE05':['W04'],'CE06':['W04'],'CE07':['W05','W06','W07','W08','W09'],'CE08':['W10']}
    rows = d['image_source_requirement_ledger']
    assert len(rows) == len(baseline['image_source_requirements']) == 10
    for i,(row,original) in enumerate(zip(rows,baseline['image_source_requirements'])):
        assert row['source'] == pin(CE04,'/image_source_requirements/'+str(i))
        assert row['id'] == original['id'] and row['exact_requirement'] == original == fragment(row['source'])
        assert row['consumer_step'] == original['consumer_step']
        assert row['work_package_consumers'] == consumers[original['consumer_step']], 'phase_mapping'
        assert row['deferred_from_W03'] is (original['consumer_step'] != 'CE04')
        assert row['accepted'] is False and all(v is None for k,v in row.items() if k.startswith('actual_'))
    assert sum(not r['deferred_from_W03'] for r in rows) == 6
    assert len(d['compiled_policy_requirements']) == 7
    for row in d['compiled_policy_requirements']:
        assert row['required_candidate_policy_sha256'] == row['documentary_binding']['sha256'] == sha(row['documentary_binding']['path'])
        assert row['actual_compiled_value_verified'] is False, 'pin_as_compiled'
        assert row['actual_compiled_policy_sha256'] is None and row['actual_independent_policy_selection_acceptance'] is None
        field = pack['image_manifest']['properties'][row['image_field']]
        if 'const' in field:
            assert field['const'] == row['required_candidate_policy_sha256']
    assert d['compiled_policy_requirements'] == baseline['compiled_policy_requirements']
    embedding = d['no_self_embedding_policy']
    assert embedding['own_future_image_manifest_bundle_digests_must_not_be_embedded'], 'self_embedding'
    assert embedding == baseline['no_self_embedding_policy']
    implementation = d['implementation_proof_boundary']
    assert fragment(implementation['source']) == spec['rules'][3] and spec['rules'][3]['id'] == 'K04'
    assert implementation['exact_selected_I191_contract_and_schema_must_be_externally_accepted']
    assert implementation['reviewed_six_source_implementation_must_enforce_exact_pinned_policies']
    assert implementation['document_pins_or_matching_constants_not_implementation_or_policy_selection_proof'], 'hash_as_implementation'
    assert implementation['actual_source_policy_conformance_or_external_selection_proof'] is None and implementation['actual_static_successor_code_review_performed'] is False
    schemas = d['schema_obligations']
    assert schemas == baseline['schema_obligations']
    assert len(schemas['definitions']) == 6 and schemas['final_manifest_body_cap_bytes'] == spec['record_caps_bytes']['image_manifest'] == 98304
    assert schemas['dependency_min'] == 1 and schemas['dependency_max'] == 128
    for row in schemas['definitions']:
        assert row['schema_fragment'] == fragment(row['source']) == pack[row['name']]
    phase = d['phase_boundary']
    assert phase['exact_plan_order'] == plan['scope_authentication_and_freeze_order'] == fragment(phase['source'])
    assert phase['required_baseline_requirement_ids'] == ['IM%02d'%i for i in range(1,7)]
    assert phase['baseline_immutable_entry_evidence_not_caller_constructor_or_platform_enforcement_proof'], 'baseline_as_enforcement'
    assert phase['caller_platform_resources_and_final_freeze_remain_own_consumers']
    assert phase['downstream_acceptance_required_as_new_reverse_W03_dependency'] is False, 'reverse_dependency'
    assert phase['baseline_actor_image_caller_platform_authentication_before_W09_required'] and phase['actual_proof_authors_and_complete_bodies_before_W09_required'], 'late_authentication'
    assert phase['W10_reconciles_same_genuine_facts_not_sole_forecast_authentication'], 'forecast_freeze'
    assert phase['final_record_order'] == ['actor_registry','image_manifest','caller_identity','platform_custody'] and phase['final_manifest_before_C_required']
    assert phase['final_manifest_freeze_required_to_prepare_W03'] is False, 'premature_freeze'
    assert phase['actual_final_manifest_or_accepted_source_root'] is None and phase['actual_downstream_rebind_or_snapshot_refresh'] is False
    assert phase['freeze_and_refresh_policy'] == baseline['freeze_and_refresh']
    cost = d['authority_and_costs']
    assert cost['inherited_boundary'] == plan['authorization_boundary'] == fragment(cost['source'])
    assert cost['inherited_boundary']['current_run_command'] is None and all(v is False for k,v in cost['inherited_boundary'].items() if k.endswith('_authorized'))
    assert cost['missing_sources_do_not_authorize_implementation_build_import_compile_measurement_or_qualification'], 'implicit_implementation'
    assert len(cost['allowed_now']) == 4 and cost['actual_external_material_or_provider'] is None and cost['actual_action_specific_authority'] is None
    assert cost['no_new_helpers_channels_fds_argv_inputs_outputs_or_ambient_trust'], 'hidden_route'
    assert cost['actual_new_route_or_helpers_created'] is False and cost['actual_sources_or_image_created'] is False
    assert cost['per_attempt_lookup_freshness_identity_signature_measurement_copies_registry_receipt_native_IO_inside_complete_resource_join'], 'omitted_cost'
    assert cost['prior_build_enrollment_or_offline_work_not_free_per_attempt_cost']
    assert cost['actual_heap_CPU_service_compatibility_or900_proof'] is None and cost['quotas_or_reserves_applied'] is False, 'quota_or_capacity_promotion'
    exits = d['exit_predicate_dispositions']
    assert len(exits) == 3 and [r['predicate'] for r in exits] == w['exit_predicates']
    for row in exits:
        assert row['documentary_policy_prepared'] is True and fragment(row['source']) == row['predicate']
        assert row['accepted'] is False and all(v is None for k,v in row.items() if k.startswith('actual_')), 'exit_acceptance'
    assert [row['exact_rule'] for row in d['contract_rules']] == [r for r in spec['rules'] if r['id'] in ['K04','K05','K07','K15','K16']]
    for row in d['contract_rules']:
        assert fragment(row['source']) == row['exact_rule']
    preserved = d['preserved_scope_and_gates']
    for key in ['inherited_scope_boundaries','preserved_negative_gates','prelaunch_handoff_and_CE12']:
        assert preserved[key] == plan[key]
    for row in preserved['preserved_negative_gates']:
        assert fragment({**row['source'],'json_pointer':row['json_pointer']}) == row['observed_value']
    assert preserved['existing_CE_dossiers_not_positive_image_runtime_platform_resource_or_final_route_proof']
    for key,value in d['current_effect'].items():
        if key == 'W03_documentary_prepared':
            assert value is True
        elif key == 'IR03':
            assert value == 'NOT_READY'
        elif key in ['actual_evidence_accepted','work_packages_accepted','prelaunch_gates_closed','resource_obligations_closed']:
            assert type(value) is int and value == 0
        else:
            assert value is False, 'positive_effect'
    assert all(d['producer'][k] is False for k in ['actor_independent','competent_R01_attestation','competent_R06_review','separate_R08_acceptance','external_contacts_made'])
    check_pointers(d)


def reconstruct():
    d = rd(SUBJECT)
    pins = {**d['input_pins'],**{p:sha(p) for p in sorted(PRIOR_FILES)}}
    assert len(pins) == 947
    verify_blobs(pins)
    inspect_scope(d)
    criteria = [
        ('RC01','I223 W03 three deliverables/exits and authority/rejection clauses exact','/work_package_binding'),
        ('RC02','W01/W02 unaccepted and SD01 active; preparation grants no authority','/dependency_gate'),
        ('RC03','Six exact absent sources; README DOCUMENT; membership does not prove load','/source_to_image_missing_inventory'),
        ('RC04','Unknown source totals not zero;262144 candidate ceiling and historical480/six helper scope preserved','/source_scope_policy'),
        ('RC05','Image bytes and full runtime identities distinct; historical/auditor environment not target evidence','/runtime_identity_boundary'),
        ('RC06','Eight complete-closure requirement categories retain unknown genuine inventories/provenance/equivalence','/closure_requirement_ledger'),
        ('RC07','Ten exact requirements: six baseline and four correctly deferred references','/image_source_requirement_ledger'),
        ('RC08','Seven document policy hashes do not prove actual compiled selection/implementation','/compiled_policy_requirements'),
        ('RC09','No own future image/manifest/bundle digest embedding; external image identity still missing','/no_self_embedding_policy'),
        ('RC10','Six schemas,1-128 dependencies and98304 manifest cap are candidates, not body/fit proof','/schema_obligations'),
        ('RC11','Baseline first entry does not discharge caller/constructor/platform enforcement','/phase_boundary'),
        ('RC12','Baseline/authors/proofs before W09; W10 reconciles same facts without forecast authority or reverse dependency','/phase_boundary'),
        ('RC13','Missing artifacts do not authorize implementation/build/measurement/execution; full per-attempt cost remains charged','/authority_and_costs'),
        ('RC14','R01/R06/R08 unassigned and three exits unaccepted without real evidence','/exit_predicate_dispositions'),
        ('RC15','K04/K05/K07/K15/K16, inherited certificate/caps and deferred CE12 preserved','/preserved_scope_and_gates'),
        ('RC16','No real package/source/image/runtime/resource/admission/D5 promotion','/current_effect')]
    return dict(schema='d5.i230-i229-source-reconstruction.v1',increment='I230',date=DATE,timezone='Europe/Madrid',base_commit=BASE,
        subject=pin(SUBJECT),plan=pin(PLAN,'/work_packages/2'),input_pins=pins,
        criteria=[dict(id=i,criterion=t,subject=pin(SUBJECT,p),result='DOCUMENTARY_CONSISTENCY_CONFIRMED_NOT_REAL_ACCEPTANCE') for i,t,p in criteria],
        requirement_phase_mapping=[dict(id=r['id'],source=r['source'],consumer_step=r['consumer_step'],work_package_consumers=r['work_package_consumers'],deferred=r['deferred_from_W03'],actually_accepted=False) for r in d['image_source_requirement_ledger']],
        counts=dict(input_pins=947,criteria=16,source_paths=6,closure_categories=8,requirements=10,baseline_requirements=6,deferred_requirements=4,policies=7,schemas=6,unassigned_review_roles=3,pending_exits=3),
        current_effect={**d['current_effect'],'W03_documentary_reviewed':True},methodological_review_not_R01_attestation_independent_R06_or_separate_R08=True)


def rejection_checks():
    cases = [
        ('dependency_bypass',('dependency_gate','SD01_stop_active'),False),
        ('future_authority',('dependency_gate','no_future_bundle_or_downstream_freeze_as_sole_prior_authority'),False),
        ('predictive_hash',('source_to_image_missing_inventory',0,'actual_source_sha256'),'INVENTED_NOT_REAL_DIGEST'),
        ('source_presence',('source_to_image_missing_inventory',0,'actual_path_exists'),True),
        ('README_representation',('source_to_image_missing_inventory',0,'required_representation'),'PYTHON_SOURCE'),
        ('membership_as_load',('source_to_image_missing_inventory',0,'loaded_by_membership_claimed'),True),
        ('unknown_bytes_zero',('source_scope_policy','actual_total_bytes'),0),
        ('historical_transfer',('source_scope_policy','old_I122_proofs_transfer_to_successor'),True),
        ('invented_closure',('actual_image_runtime_state','actual_complete_dependency_closure_verified'),True),
        ('image_as_runtime',('runtime_identity_boundary','image_bytes_digest_does_not_substitute_P02'),False),
        ('auditor_as_target',('runtime_identity_boundary','target_runtime_or_host_platform_sampled'),True),
        ('phase_mapping',('image_source_requirement_ledger',6,'work_package_consumers'),['W03']),
        ('pin_as_compiled',('compiled_policy_requirements',0,'actual_compiled_value_verified'),True),
        ('self_embedding',('no_self_embedding_policy','own_future_image_manifest_bundle_digests_must_not_be_embedded'),False),
        ('hash_as_implementation',('implementation_proof_boundary','document_pins_or_matching_constants_not_implementation_or_policy_selection_proof'),False),
        ('baseline_as_enforcement',('phase_boundary','baseline_immutable_entry_evidence_not_caller_constructor_or_platform_enforcement_proof'),False),
        ('reverse_dependency',('phase_boundary','downstream_acceptance_required_as_new_reverse_W03_dependency'),True),
        ('late_authentication',('phase_boundary','actual_proof_authors_and_complete_bodies_before_W09_required'),False),
        ('forecast_freeze',('phase_boundary','W10_reconciles_same_genuine_facts_not_sole_forecast_authentication'),False),
        ('premature_freeze',('phase_boundary','final_manifest_freeze_required_to_prepare_W03'),True),
        ('implicit_implementation',('authority_and_costs','missing_sources_do_not_authorize_implementation_build_import_compile_measurement_or_qualification'),False),
        ('hidden_route',('authority_and_costs','no_new_helpers_channels_fds_argv_inputs_outputs_or_ambient_trust'),False),
        ('omitted_cost',('authority_and_costs','per_attempt_lookup_freshness_identity_signature_measurement_copies_registry_receipt_native_IO_inside_complete_resource_join'),False),
        ('quota_or_capacity_promotion',('authority_and_costs','quotas_or_reserves_applied'),True),
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
    return dict(schema='d5.i230-i229-documentary-review.v1',increment='I230',date=DATE,timezone='Europe/Madrid',base_commit=BASE,
        status=STATUS,subject=pin(SUBJECT),reconstruction=pin(RECON),verdict='W03_DOCUMENTARY_SOURCE_IMAGE_RUNTIME_AND_PHASE_BOUNDARIES_CONSISTENT_EVIDENCE_MISSING_NOT_ACCEPTED',
        findings=[],finding_count=0,criteria=rec['criteria'],counts=rec['counts'],
        documentary_clarifications=[
            dict(id='N01',subject='Negative dossier and authority',disposition='W01/W02 and SD01 remain blocking. W03 review is documentary only and creates no sources/image/runtime, trusted baseline or accepted real evidence package. Missing sources do not authorize implementation/build/measurement/import/qualification.'),
            dict(id='N02',subject='Different identity and evidence commitments',disposition='Actual six-source digests, source-root/mapping, final external image bytes, complete runtime/P02 identity, compiled policy selection and implemented semantics need distinct genuine evidence. Document hashes, schema constants, historical I122/P02/P03 or auditor environment do not substitute for them.'),
            dict(id='N03',subject='Baseline versus enforcement and resources',disposition='IM01-IM06 are baseline; IM07/IM08 remain caller/platform W04 obligations, IM09 spans W05-W09 qualification/resources and IM10 belongs to W10 freeze. Baseline immutable first entry does not prove actual constructor/enforcement. No reverse acceptance dependency or implicit downstream acceptance is added.'),
            dict(id='N04',subject='Antecedent authentication and freeze',disposition='Actual baseline actor/image/caller/platform facts and complete proof authors/bodies must be authenticated before W09 resource acceptance. W10 reconciles the same accepted facts, not forecast authority; changes invalidate affected hashes/reviews and require requalification. No active refresh/rebind is applied.'),
            dict(id='N05',subject='Costs, final route and independent roles',disposition='Per-attempt verification/lookup/freshness/copies/registry/receipt/native/IO remains in complete phases/resources; caps or offline labels do not prove capacity/900. CE12 and final E06/Q/root/claim remain separate and unperformed. Same assistant review is not R01 attestation, independent R06 or separate R08 acceptance.')],
        source_replay=dict(I229_candidate_and_preparation_review_reproduced=True,prior_publication_mains_called=False,prior_Path_exists_restored=True,no_new_presence_projection=True),
        rejection_checks=rejection_checks(),current_effect=rec['current_effect'],
        provenance=dict(preparer_and_reviewer='Same Codex assistant/chat as I229',methodological_only=True,actor_independent=False,competent_R01_attestation=False,competent_R06_review=False,separate_R08_acceptance=False,external_contacts=False),
        next_step='Documentary W03 review complete. Positive progress remains stopped at SD01 pending genuine authority, accepted dependencies and actual source/image/runtime evidence; no implementation, contact or operational work initiated.',
        work_unit=dict(rollback_files=sorted(FILES),verification_command='python3 docs/validation/D5-I230-audit.py',expected_result=STATUS,
            runtime_harness='N/A: own documentary JSON/Git/hash/policy/path-presence comparisons only; no product/components imports/build/compile/tests/benchmarks, codec/crypto positives, target/image/runtime/platform measurement, probes/clock/ledger/claim/processes/signing/keygen/enrollment/provisioning/services/contact.',
            over400_lines=True,reason='One W03 review unit with complete source pins, semantic comparisons, phase mapping, negative checks and preservation; overage declared. No PR requested.'),
        publication=dict(commit_and_push_requested=True,publication_not_baseline_adoption_implementation_build_or_execution_authority=True))


def main():
    rec = reconstruct()
    assert rd(RECON) == rec
    review = build_review(rec)
    assert rd(REVIEW) == review
    prior = rd(PRIOR_SEAL)
    preserved = {**prior['preserved_published634'],**prior['artifacts'],PRIOR_SEAL:sha(PRIOR_SEAL)}
    assert len(preserved) == 639
    seal = rd(SEAL)
    assert seal['schema'] == 'd5.i230-integrity.v1' and seal['base_commit'] == BASE
    assert seal['preserved_published639'] == preserved and set(seal['artifacts']) == FILES-{SEAL}
    for pins in [preserved,seal['artifacts']]:
        for path,digest in pins.items():
            assert sha(path) == digest, path
    assert seal['source_only'] is True and seal['current_effect'] == rec['current_effect']
    changed = set(git('diff',BASE,'--name-only').splitlines()) | set(git('ls-files','--others','--exclude-standard').splitlines())
    assert changed == FILES, changed
    subprocess.check_call(['git','merge-base','--is-ancestor',BASE,'HEAD'],cwd=ROOT)
    if git('rev-parse','HEAD') != BASE:
        assert not git('status','--porcelain')
    print(json.dumps(dict(status=STATUS,increment='I230',historical_pins=947,preserved_published_files=639,new_files=5,
        criteria=16,findings=0,documentary_rejections=len(review['rejection_checks']),current_effect=rec['current_effect'],git_head=git('rev-parse','HEAD')),sort_keys=True))


if __name__ == '__main__':
    main()
