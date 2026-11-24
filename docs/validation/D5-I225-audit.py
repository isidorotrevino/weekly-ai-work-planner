#!/usr/bin/env python3
"""I225 W01 documentary target scope/authority only; no product, runtime or active quota change."""
import copy
import hashlib
import io
import json
import runpy
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
P = 'docs/validation/'
BASE = '90fefb86ddd4566e5d9eb83edbedd2e0f5982117'
PLAN = P+'D5-I223-PRELAUNCH-RESOURCE-CLOSURE-PLAN.json'
SUBJECT = P+'D5-I223-W01-TARGET-SCOPE-AUTHORITY-CANDIDATE.json'
CONTRACT = P+'D5-I130-PLATFORM-CONTRACT-CANDIDATE.json'
PROFILE = P+'D5-I185-PGO181-TRUST-PROFILE-CANDIDATE-02.json'
PROTO = P+'D5-I185-PGO181-SCHEMAS-CANDIDATE-02.json'
OUTPUT = P+'D5-I187-CONTEXT-LAUNCH-SCHEMAS-CANDIDATE.json'
TRANSPORT = P+'D5-I189-BOOTSTRAP-TRANSPORT-CONTRACT-CANDIDATE.json'
GRAMMAR = P+'D5-I189-BOOTSTRAP-TRANSPORT-GRAMMAR-CANDIDATE.json'
SPEC = P+'D5-I191-CALLER-IMAGE-CUSTODY-CONTRACT-CANDIDATE.json'
PACK = P+'D5-I191-CALLER-IMAGE-CUSTODY-SCHEMAS-CANDIDATE.json'
CE01 = P+'D5-I197-CE01-SCOPE-AND-DECISION-BOUNDARY-CANDIDATE-02.json'
CE07 = P+'D5-I193-CE07-RESOURCE-AND-COMPATIBILITY-JOIN-CANDIDATE.json'
PRIOR_AUDIT = P+'D5-I224-audit.py'
PRIOR_RECON = P+'D5-I224-I223-source-reconstruction.json'
PRIOR_REVIEW = P+'D5-I224-I223-documentary-review.json'
PRIOR_SEAL = P+'D5-I224-integrity.json'
PRIOR_DOC = 'docs/design/D5-I224-I223-CLOSURE-PLAN-REVIEW.md'
PRIOR_FILES = {PRIOR_AUDIT,PRIOR_RECON,PRIOR_REVIEW,PRIOR_SEAL,PRIOR_DOC}
AUDIT = P+'D5-I225-audit.py'
PREP = P+'D5-I225-preparation-review.json'
SEAL = P+'D5-I225-integrity.json'
DOC = 'docs/design/D5-I225-W01-TARGET-SCOPE-AUTHORITY.md'
FILES = {SUBJECT,AUDIT,PREP,SEAL,DOC}
DATE = '2026-11-24'
STATUS = 'PASS_STATIC_SOURCE_ONLY_W01_ENTRY_AUTHORITY_MISSING_NOT_ACCEPTED'
POLICIES = [CONTRACT,PROTO,PROFILE,OUTPUT,TRANSPORT,GRAMMAR,SPEC,PACK]


def rd(p):
    return json.loads((ROOT/p).read_text())


def sha(p):
    return hashlib.sha256((ROOT/p).read_bytes()).hexdigest()


def git(*args):
    return subprocess.check_output(['git',*args],cwd=ROOT,text=True).strip()


def pin(p,pointer=''):
    return dict(path=p,sha256=sha(p),json_pointer=pointer)


def historical_pins():
    pins = {**rd(PRIOR_RECON)['input_pins'],**{p:sha(p) for p in sorted(PRIOR_FILES)}}
    assert len(pins) == 922
    return pins


def verify_blobs(pins):
    stream = io.BytesIO(subprocess.check_output(['git','cat-file','--batch'],cwd=ROOT,
        input=''.join(BASE+':'+p+'\n' for p in sorted(pins)).encode()))
    for p,h in sorted(pins.items()):
        header = stream.readline().decode().split()
        assert len(header) == 3 and header[1] == 'blob', p
        body = stream.read(int(header[2]))
        assert stream.read(1) == b'\n' and hashlib.sha256(body).hexdigest() == h == sha(p), p
    assert stream.read() == b''


def build_candidate():
    plan = rd(PLAN)
    w = plan['work_packages'][0]
    scope = plan['inherited_scope_boundaries']
    contract = rd(CONTRACT)
    profile = rd(PROFILE)
    transport = rd(TRANSPORT)
    spec = rd(SPEC)
    defs = rd(PACK)['$defs']
    paths = {PLAN,PRIOR_REVIEW,PRIOR_RECON,CE01,CE07,*POLICIES}
    source_rows = [dict(logical_path=p,source_of_path_set=pin(PACK,'/$defs/source_bindings'),
        target_kind='DOCUMENT' if p.endswith('/README.md') else 'PROSPECTIVE_SOURCE_NOT_YET_QUALIFIED',
        actual_path_exists=(ROOT/p).exists(),actual_successor_source_sha256=None,actual_image_member_or_digest=None,
        actual_loaded_representation=None,actual_source_runtime_mapping_proof=None,accepted=False)
        for p in defs['source_bindings']['required']]
    guards = []
    for i,rule in enumerate(profile['semantic_contracts']):
        guards.append(dict(id='PROFILE-'+rule['id'],category='PROFILE_SEMANTIC_CONTRACT',source=pin(PROFILE,'/semantic_contracts/'+str(i)),
            policy_fragment=rule,actual_successor_implementation_or_qualification_verified=False,actual_proof_sha256=None))
    for group in ['one_use_and_permissions','failure_and_outputs']:
        for name,value in transport[group].items():
            guards.append(dict(id='TRANSPORT-'+group+'-'+name,category='TRANSPORT_PERMISSION_OR_FAILURE_OUTPUT',
                source=pin(TRANSPORT,'/'+group+'/'+name),policy_fragment=value,
                actual_successor_implementation_or_qualification_verified=False,actual_proof_sha256=None))
    for i,condition in enumerate(scope['full_CP07_conditions']):
        guards.append(dict(id='CP07-%02d'%(i+1),category='FULL_ADMISSION_CONDITION',
            source=pin(PLAN,'/inherited_scope_boundaries/full_CP07_conditions/'+str(i)),policy_fragment=condition,
            actual_successor_implementation_or_qualification_verified=False,actual_proof_sha256=None))
    numeric = [dict(name=k,value=v,source=pin(PLAN,'/inherited_scope_boundaries/numeric_candidates_unchanged/'+k),
        kind='INHERITED_NUMERIC_CANDIDATE_NOT_NEW_QUOTA',actual_applied_or_changed=False) for k,v in scope['numeric_candidates_unchanged'].items()]
    protocol = [dict(name=k,value=v,source=pin(PLAN,'/inherited_scope_boundaries/protocol_and_output_caps/'+k),
        kind='CONDITIONAL_DESIGN_ENVELOPE_NOT_ACTUAL_FIT' if k in ['Reader_design_bytes_conditional','bundle_upper_conditional_on_nested_caps'] else 'INHERITED_PROTOCOL_OR_OUTPUT_CANDIDATE',
        actual_applied_or_changed=False) for k,v in scope['protocol_and_output_caps'].items()]
    authority_slots = [
        dict(id='EA01',subject='Real maintainer/accountable human authority for logical target scope',required_role='SCOPE_AUTHORITY',
            required_authority_scope='Define/approve this exact logical target and its unchanged constraints; not execution authority.'),
        dict(id='EA02',subject='Genuine competent primary reviewer R06',required_role='R06',
            required_authority_scope='Independent documentary scope/provenance/Reader and authority-boundary review, under genuine accepted appointment.'),
        dict(id='EA03',subject='Genuine separate acceptor R08',required_role='R08',
            required_authority_scope='Separate acceptance/rejection of scope, with inherited S01/custody/key exclusions and no self-review.')]
    for row in authority_slots:
        row.update(actual_canonical_human=None,actual_organization_alias_or_competence=None,actual_appointment=None,
            actual_preexisting_authority_proof_body=None,actual_authority_proof_sha256=None,actual_scope_validity=None,
            actual_custody_or_provider=None,actual_primary_review=None,actual_separate_acceptance=None,
            availability='NOT_SUPPLIED_NOT_EVALUATED',accepted=False,contact_or_nomination_authorized_now=False)
    actions = [dict(id='AA%02d'%(i+1),action=a,current_status='AUTHORIZED_DOCUMENTARY_WORK_ONLY',
        authority_kind='Explicit current user request for preparation/audit/publication, not canonical scope adoption',
        actual_runtime_authority_granted=False) for i,a in enumerate(['READ_REPOSITORY_JSON_GIT_AND_DOCUMENT_HASHES',
            'PREPARE_THIS_NEGATIVE_W01_DOSSIER','RUN_OWN_DOCUMENTARY_AUDIT','COMMIT_AND_PUSH_THIS_UNIT'])]
    denied = [(k,v) for k,v in plan['authorization_boundary'].items() if k.endswith('_authorized')]
    actions.extend(dict(id='OA%02d'%(i+1),action=k,current_status='NOT_AUTHORIZED',
        source=pin(PLAN,'/authorization_boundary/'+k),actual_action_authority=None,
        requires_separate_exact_future_authority_and_cost_proof=True,authorized_now=False) for i,(k,v) in enumerate(denied))
    return dict(schema='d5.i225-w01-target-scope-authority-candidate.v1',increment='I225',date=DATE,timezone='Europe/Madrid',base_commit=BASE,
        plan_id=plan['plan_id'],work_package='W01',planned_deliverable_id=w['deliverable_id'],
        kind='NEGATIVE_LOGICAL_TARGET_SCOPE_AND_AUTHORITY_DOSSIER_NOT_ACCEPTED_REAL_EVIDENCE_PACKAGE',
        status='W01_LOGICAL_SCOPE_PREPARED_ENTRY_AUTHORITY_MISSING_NOT_ACCEPTED_NOT_ADMITTED',
        input_pins=historical_pins(),work_package_binding=pin(PLAN,'/work_packages/0'),plan_review_binding=pin(PRIOR_REVIEW),
        required_deliverables=w['deliverables'],required_exit_predicates=w['exit_predicates'],reject_if=w['reject_if'],
        needs_separate_future_authority_for=w['needs_separate_future_authority_for'],
        documentary_inventory=[pin(p) for p in sorted(paths)],
        logical_source_scope=source_rows,
        effective_environment_scope=dict(source=pin(SPEC,'/rules/3'),
            required_closure_kinds=['interpreter','loader','stdlib','frozen modules','native/crypto extensions','allocator/GC','kernel/service/scheduler/IO','build recipe/toolchain'],
            actual_image_bytes_sha256=None,actual_runtime_sha256=None,actual_source_root_sha256=None,
            actual_interpreter_loader_or_dependency_manifest=None,actual_build_or_source_to_image_provenance=None,
            image_and_runtime_digests_are_distinct_concepts=True,
            exact_historical480_or_six_successor_sources_no_unbound_helper_required=True,
            README_document_membership_does_not_prove_test_or_runner_loaded=True,
            no_self_embedded_image_manifest_bundle_or_future_root_digest=True,
            real_effective_hashes_and_implementation_qualification_deferred_to_W03=True,
            no_host_runtime_sampling_or_build_import_compile_performed=True),
        caller_platform_ledger_scope=dict(source=pin(SPEC),
            expected_platform_guarantees=defs['platform_custody']['properties']['guarantees']['required'],
            actual_accountable_requester_or_software_caller=None,actual_protection_domain_or_constructor=None,
            actual_platform_or_service_or_backend=None,actual_clock_epoch_or_validity=None,
            actual_ledger_or_unique_mapping=None,actual_C_Q_or_invocation=None,
            required_global_claim_tuple=['trust_context_sha256','runtime_request_sha256','invocation_id'],
            required_unique_mapping_key=['configuration_epoch','SHA256(JCS(actual C))'],
            global_across_all_callers_domains_restarts_not_partitioned=True,
            mechanism_proof_not_actual_claim_and_current_backend_unselected=True,
            real_identity_platform_backend_and_guarantees_deferred_to_W02_W04=True),
        policy_version_inventory=[dict(path=p,document_sha256=sha(p),
            source_version=rd(p).get('contract_id',rd(p).get('profile_id',rd(p).get('$id',rd(p).get('schema')))),
            document_hash_is_not_runtime_image_or_proof_hash=True,actual_runtime_policy_implementation_or_adoption_verified=False)
            for p in POLICIES],
        numeric_candidate_ledger=numeric,protocol_output_ledger=protocol,
        custody_record_cap_ledger=[dict(family=n,candidate_body_cap_bytes=v,source=pin(SPEC,'/record_caps_bytes/'+n),
            actual_body_size=None,actual_cap_fit_verified=False,actual_quota_applied=False) for n,v in spec['record_caps_bytes'].items()],
        heap_scope_ledger=dict(source=pin(CONTRACT,'/heap'),candidate_heap_contract=contract['heap'],
            actual_complete_heap_or_native_allocator_GC_overlap_proof=None,actual_capacity_attestation=None,
            actual_budget_fit_verified=False,reserve_transfers_applied=0,resources_reserved=False),
        phase_marker_ledger=dict(source=pin(CONTRACT,'/time'),candidate_phase_budgets=contract['time']['phase_budgets'],
            normative_markers=contract['time']['normative_markers'],ordered_interval_rule=contract['time']['ordered_interval_rule'],
            success_path_qualification=contract['time']['success_path_qualification'],observation_latency_rule=contract['time']['observation_latency_rule'],
            candidate_success_seconds=900,unassigned_wall_candidate_reserve_seconds=30,
            actual_clock_samples_or_marker_values=None,actual_work_CPU_service_latency_or900_proof=None,
            no_missing_marker_or_unknown_cost_as_zero=True,reserve_transfers_applied=0,
            exact_True_wait_worker_tW_not_exit_or_later_validation_and_success_finally_tF_required=True),
        guard_obligation_ledger=guards,
        transport_and_output_scope=dict(route_source=pin(TRANSPORT,'/route'),required_route=transport['route'],
            trust_boundary=transport['trust_boundary'],endpoint_ownership=transport['endpoint_ownership'],
            argv_and_channel_checks=transport['argv_and_channel_checks'],framing=transport['framing'],
            output_schema_binding=pin(OUTPUT),grammar_binding=pin(GRAMMAR),
            custody_projection=spec['projection'],
            no_new_file_pipe_helper_input_wire_argv_or_output_receipt_channel=True,
            actual_control_channels_processes_outputs_or_receipts_created=False),
        source_requalification_boundary=dict(source=pin(CE07,'/requalification'),
            required_legacy_scope=rd(CE07)['requalification']['required_legacy_scope'],
            all_new_custody_bootstrap_output_failure_paths_and_costs_require_requalification=True,
            historical_CP03_atomicity_implementation_or_ten_test_counts_not_successor_evidence=True,
            actual_source_BASIS_index_atomicity_or_resource_proofs=None,
            source_and_resource_work_deferred_to_W03_W09=True),
        entry_authority_inventory=authority_slots,
        entry_authority_boundary=dict(source=pin(PRIOR_REVIEW,'/documentary_clarifications/0'),
            W01_no_predecessor_does_not_mean_self_authorized=True,
            independently_authentic_preexisting_scope_and_reviewer_authority_required_at_entry=True,
            future_W02_appointments_or_future_bundle_not_sole_forecast_authority=True,
            current_user_request_authorizes_docs_audit_commit_push_not_canonical_role_or_scope_adoption=True,
            no_implicit_nomination_contact_enrollment_or_signing=True,
            actual_entry_authority_verified=False,SD01_stop_active=True,
            logical_scope_documentation_is_not_authoritative_scope_acceptance_or_effective_source_freeze=True),
        action_authority_ledger=actions,
        existing_external_material_intake=dict(only_if_genuinely_supplied_with_its_own_authorized_provenance=True,
            actual_material_received=None,actual_provider=None,actual_competent_review=None,
            no_contact_fetch_or_verification_service_authorized=True),
        exit_predicate_dispositions=[dict(id='WX%02d'%(i+1),predicate=text,source=pin(PLAN,'/work_packages/0/exit_predicates/'+str(i)),
            documentary_content_prepared=True,actual_provider_or_scope_authority=None,actual_primary_review=None,
            actual_separate_acceptance=None,accepted=False,status='PENDING_GENUINE_SCOPE_AUTHORITY_AND_REVIEW')
            for i,text in enumerate(w['exit_predicates'])],
        handoff_and_deferred_scope=dict(source=pin(PLAN,'/prelaunch_handoff_and_CE12'),
            preserved_boundary=plan['prelaunch_handoff_and_CE12'],
            W02_identity_intake_and_W03_effective_source_facts_not_provided_or_started=True,
            W01_acceptance_cannot_be_filled_from_later_unaccepted_packages=True,
            E01_E05_and30_gates_remain_pending=True,CE12_remains_private_DEFERRED_NOT_AUTHORIZED=True,
            actual_final_E06_payload_Q_root_admission_claim_or_receipt_created=False),
        change_control=dict(source=pin(PLAN,'/scope_authentication_and_freeze_order'),
            inherited_plan_policy=plan['scope_authentication_and_freeze_order'],
            new_contributor_body_source_image_runtime_domain_epoch_key_policy_or_limit_change_requires_explicit_impact_and_fresh_review=True,
            no_automatic_prior_proof_hash_mapping_approval_or_acceptance_transfer=True,
            extra_helper_input_or_quota_change_not_authorized_to_force_fit=True,
            actual_rebind_snapshot_refresh_or_runtime_config_changed=False),
        producer=dict(identity='Same Codex assistant/chat as I223/I224',documentary_preparer_only=True,
            actor_independent=False,organizationally_independent=False,competent_R06_review=False,separate_R08_acceptance=False,external_contacts_made=False),
        inherited_scope_boundaries=scope,preserved_negative_gates=plan['preserved_negative_gates'],
        current_effect=dict(W01_documentary_prepared=True,W01_accepted=False,actual_entry_authority_verified=False,
            actual_logical_scope_accepted=False,actual_effective_source_scope_frozen=False,actual_real_evidence_package_created=False,
            actual_scope_provider_or_reviewer_assigned=False,actual_evidence_accepted=0,independent_acceptance=False,
            work_packages_accepted=0,prelaunch_gates_closed=0,resource_obligations_closed=0,
            source_implementation_changed=False,product_or_components_executed=False,quotas_changed=False,reserves_changed=False,
            resource_reservations_created=False,rebind_applied=False,authority_or_destination_created=False,
            actual_claim_worker_or_receipt_created=False,execution_authorized=False,proposal_enabled=False,D5_closed=False,IR03='NOT_READY'),
        publication=dict(commit_and_push_requested=True,publication_is_not_scope_adoption_or_execution_authority=True))


def validate(d):
    assert d['current_effect']['W01_accepted'] is False, 'premature_W01_acceptance'
    assert d['entry_authority_boundary']['actual_entry_authority_verified'] is False, 'invented_entry_authority'
    assert d['entry_authority_boundary']['future_W02_appointments_or_future_bundle_not_sole_forecast_authority'] is True, 'future_W02_authority'
    assert all(r['actual_successor_source_sha256'] is None for r in d['logical_source_scope']), 'predictive_source_hash'
    assert all(r['actual_path_exists'] is False for r in d['logical_source_scope']), 'invented_source_presence'
    assert d['effective_environment_scope']['image_and_runtime_digests_are_distinct_concepts'] is True, 'image_as_runtime'
    assert all(r['actual_applied_or_changed'] is False for r in d['numeric_candidate_ledger']), 'applied_numeric_quota'
    assert d['heap_scope_ledger']['reserve_transfers_applied'] == 0, 'reserve_transfer'
    assert d['phase_marker_ledger']['actual_work_CPU_service_latency_or900_proof'] is None, '900_budget_as_proof'
    assert d['transport_and_output_scope']['no_new_file_pipe_helper_input_wire_argv_or_output_receipt_channel'] is True, 'hidden_channel'
    assert d['current_effect']['execution_authorized'] is False, 'execution_authorized'
    assert d['current_effect']['D5_closed'] is False, 'D5_closed_by_scope'
    assert d['work_package_binding'] == pin(PLAN,'/work_packages/0')
    assert len(d['logical_source_scope']) == 6 and len(d['entry_authority_inventory']) == 3
    assert all(row['accepted'] is False and row['actual_canonical_human'] is None and row['actual_appointment'] is None for row in d['entry_authority_inventory'])
    assert d == build_candidate(), 'Dossier differs from source reconstruction'


def rejection_checks(d):
    cases = [
        ('premature_W01_acceptance',('current_effect','W01_accepted'),True),
        ('invented_entry_authority',('entry_authority_boundary','actual_entry_authority_verified'),True),
        ('future_W02_authority',('entry_authority_boundary','future_W02_appointments_or_future_bundle_not_sole_forecast_authority'),False),
        ('predictive_source_hash',('logical_source_scope',0,'actual_successor_source_sha256'),'INVENTED_DIGEST_NOT_A_REAL_SOURCE_HASH'),
        ('invented_source_presence',('logical_source_scope',0,'actual_path_exists'),True),
        ('image_as_runtime',('effective_environment_scope','image_and_runtime_digests_are_distinct_concepts'),False),
        ('applied_numeric_quota',('numeric_candidate_ledger',0,'actual_applied_or_changed'),True),
        ('reserve_transfer',('heap_scope_ledger','reserve_transfers_applied'),1),
        ('900_budget_as_proof',('phase_marker_ledger','actual_work_CPU_service_latency_or900_proof'),900),
        ('hidden_channel',('transport_and_output_scope','no_new_file_pipe_helper_input_wire_argv_or_output_receipt_channel'),False),
        ('execution_authorized',('current_effect','execution_authorized'),True),
        ('D5_closed_by_scope',('current_effect','D5_closed'),True)]
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
            out.append(dict(case=name,result='REJECTED_DOCUMENTARY_MUTATION_IN_MEMORY'))
        else:
            raise AssertionError(name)
    return out


def build_review():
    d = rd(SUBJECT)
    verify_blobs(d['input_pins'])
    validate(d)
    previous = runpy.run_path(str(ROOT/PRIOR_AUDIT))
    original = Path.exists
    rec = previous['reconstruct']()
    assert rec == rd(PRIOR_RECON) and previous['build_review'](rec) == rd(PRIOR_REVIEW)
    assert Path.exists is original
    plan = rd(PLAN)
    work = plan['work_packages'][0]
    assert work['id'] == d['work_package'] == 'W01' and work['depends_on'] == []
    assert d['required_deliverables'] == work['deliverables'] and d['required_exit_predicates'] == work['exit_predicates']
    assert d['reject_if'] == work['reject_if'] and d['planned_deliverable_id'] == work['deliverable_id']
    assert [r['logical_path'] for r in d['logical_source_scope']] == rd(PACK)['$defs']['source_bindings']['required']
    assert d['caller_platform_ledger_scope']['expected_platform_guarantees'] == rd(PACK)['$defs']['platform_custody']['properties']['guarantees']['required']
    assert len(d['caller_platform_ledger_scope']['expected_platform_guarantees']) == 8
    assert [r['required_role'] for r in d['entry_authority_inventory']] == ['SCOPE_AUTHORITY','R06','R08']
    for row in d['entry_authority_inventory']:
        assert all(v is None for k,v in row.items() if k.startswith('actual_'))
        assert row['accepted'] is False and row['contact_or_nomination_authorized_now'] is False
    assert all(row['actual_body_size'] is None and row['actual_cap_fit_verified'] is False for row in d['custody_record_cap_ledger'])
    assert all(row['actual_proof_sha256'] is None and row['actual_successor_implementation_or_qualification_verified'] is False for row in d['guard_obligation_ledger'])
    for key,value in d['current_effect'].items():
        if key == 'W01_documentary_prepared':
            assert value is True
        elif key == 'IR03':
            assert value == 'NOT_READY'
        elif key in ['actual_evidence_accepted','work_packages_accepted','prelaunch_gates_closed','resource_obligations_closed']:
            assert value == 0 and type(value) is int
        else:
            assert value is False, key
    assert d['entry_authority_boundary']['SD01_stop_active']
    return dict(schema='d5.i225-preparation-review.v1',increment='I225',date=DATE,timezone='Europe/Madrid',base_commit=BASE,
        status=STATUS,candidate=pin(SUBJECT),work_package=pin(PLAN,'/work_packages/0'),latest_plan_review=pin(PRIOR_REVIEW),
        counts=dict(input_pins=922,logical_successor_paths=6,policy_documents=len(POLICIES),numeric_candidates=len(d['numeric_candidate_ledger']),
            protocol_output_envelopes=len(d['protocol_output_ledger']),custody_record_caps=len(d['custody_record_cap_ledger']),
            guard_policy_obligations=len(d['guard_obligation_ledger']),phase_intervals=3,normative_markers=4,
            missing_entry_authority_slots=3,documentary_action_classes=4,unauthorized_operational_action_classes=len(d['action_authority_ledger'])-4,
            exit_predicates_pending=len(d['exit_predicate_dispositions']),work_packages_accepted=0,resource_obligations_closed=0),
        source_reconstruction=dict(I224_reconstruction_and_review_reproduced=True,prior_publication_mains_run=False,
            prior_Path_exists_method_restored=True,no_new_historical_presence_projection_added=True,
            known_document_hashes_distinguished_from_missing_successor_runtime_image_hashes=True,
            exact_caps_guards_markers_policy_versions_and_exclusions_preserved=True,
            genuine_W01_entry_authority_not_borrowed_from_future_W02=True),
        provenance=d['producer'],rejection_checks=rejection_checks(d),current_effect=d['current_effect'],
        limitations=['Logical scope and authority-boundary wrapper only; no actual W01 scope provider/competent R06/R08 appointment or acceptance supplied. SD01 remains active.',
            'All six successor source bodies and real digests/runtime/image/loader/caller/platform/ledger facts remain missing. Document pins and candidate budgets/guards are not source qualification or capacity/900 proof.',
            'Same assistant is not competent independent R06 review or separate R08 acceptance. No positive W01 evidence package, active scope freeze, implementation/execution/verification/contact/quota change is performed.'],
        work_unit=dict(rollback_files=sorted(FILES),verification_command='python3 docs/validation/D5-I225-audit.py',expected_result=STATUS,
            runtime_harness='N/A: documentary JSON/Git/hash/policy/cap/guard/authority reconstruction only; no product/components, build/import/compile, positive codec/crypto, platform/service/clock/ledger or process execution.',
            over400_lines=True,reason='One W01 negative scope/authority dossier with exact policy/cap/guard/phase and missing-authority ledgers plus immutable preservation; overage reported. No PR requested.'),
        publication=dict(commit_and_push_requested=True,publication_is_not_actual_scope_acceptance_or_execution_authority=True))


def main():
    review = build_review()
    assert rd(PREP) == review
    prior = rd(PRIOR_SEAL)
    preserved = {**prior['preserved_published609'],**prior['artifacts'],PRIOR_SEAL:sha(PRIOR_SEAL)}
    assert len(preserved) == 614
    seal = rd(SEAL)
    assert seal['schema'] == 'd5.i225-integrity.v1' and seal['base_commit'] == BASE
    assert seal['preserved_published614'] == preserved and set(seal['artifacts']) == FILES-{SEAL}
    for pins in [preserved,seal['artifacts']]:
        for p,h in pins.items():
            assert sha(p) == h, p
    assert seal['source_only'] and seal['current_effect'] == review['current_effect']
    changed = set(git('diff',BASE,'--name-only').splitlines()) | set(git('ls-files','--others','--exclude-standard').splitlines())
    assert changed == FILES, changed
    subprocess.check_call(['git','merge-base','--is-ancestor',BASE,'HEAD'],cwd=ROOT)
    if git('rev-parse','HEAD') != BASE:
        assert not git('status','--porcelain')
    print(json.dumps(dict(status=STATUS,increment='I225',historical_pins=922,preserved_published_files=614,
        new_files=5,counts=review['counts'],documentary_rejections=12,current_effect=review['current_effect'],git_head=git('rev-parse','HEAD')),sort_keys=True))


if __name__ == '__main__':
    main()
