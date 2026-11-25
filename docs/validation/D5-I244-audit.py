#!/usr/bin/env python3
"""I244 W10 methodological review. Own documentary checks; no target execution."""
import copy
import hashlib
import io
import json
import runpy
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
P = 'docs/validation/'
BASE = '807187cfa35d96eab83aadbd2c86c9d9b7e556a3'
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
W09 = P+'D5-I223-W09-E01-E05-INTEGRATION-CANDIDATE.json'
CE08 = P+'D5-I193-CE08-FINAL-ANTECEDENT-FREEZE-CANDIDATE.json'
CE08_REVIEW = P+'D5-I214-I213-documentary-review.json'
PRIOR_AUDIT = P+'D5-I243-audit.py'
PRIOR_PREP = P+'D5-I243-preparation-review.json'
PRIOR_SEAL = P+'D5-I243-integrity.json'
PRIOR_DOC = 'docs/design/D5-I243-W10-FINAL-ANTECEDENT-FREEZE.md'
SUBJECT = P+'D5-I223-W10-FINAL-ANTECEDENT-FREEZE-CANDIDATE.json'
PRIOR_FILES = {SUBJECT,PRIOR_AUDIT,PRIOR_PREP,PRIOR_SEAL,PRIOR_DOC}
RECON = P+'D5-I244-I243-source-reconstruction.json'
REVIEW = P+'D5-I244-I243-documentary-review.json'
AUDIT = P+'D5-I244-audit.py'
SEAL = P+'D5-I244-integrity.json'
DOC = 'docs/design/D5-I244-I243-W10-REVIEW.md'
FILES = {RECON,REVIEW,AUDIT,SEAL,DOC}
STATUS = 'PASS_STATIC_SOURCE_ONLY_W10_REVIEW_FINAL_ANTECEDENTS_MISSING_NOT_FROZEN_NOT_ADMITTED'
FAMILIES = ['actor_registry','image_manifest','caller_identity','platform_custody']
HELPERS = ['actor','preparation_record','anchor_key','image_member_binding','image_dependency','evidence_reference','source_bindings','validity']
POLICIES = ['typed_array_limits','source_runtime_policy','policy_constant_bindings','antecedent_and_hash_policy','freshness_policy','invalidation_policy']
RECONCILIATIONS = [
    ('AUTHORS_PREPARERS_ALIASES_KEYS',W02,'identity_policy'),
    ('SIX_SOURCES_IMAGE_RUNTIME_CLOSURE',W03,'actual_image_runtime_state'),
    ('CALLER_PRINCIPAL_CONSTRUCTOR_DOMAIN',W04,'caller_policy'),
    ('PLATFORM_SERVICE_CLOCK_LEDGER_SCOPE',W04,'platform_policy'),
    ('OPERAND_ATOMICITY_COMPLETE_SCOPE',W05,'coverage_completeness'),
    ('HEAP_LIFETIMES_FIT_CAPACITY',W06,'availability_and_fit'),
    ('WORK_CPU_UNITS_SERVICE_AND_COSTS',W07,'actual_whole_work_and_time'),
    ('PHASE_SUCCESS_AND_RESERVES',W08,'time_and_reserve_account'),
    ('BASIS_INDEX_E01_E05_PRIOR_PROOFS',W09,'prior_proof_boundary'),
    ('AUTHENTIC_BASELINE_BEFORE_W09',W09,'phase_handoff')]


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


def reconstruct_graph(dag):
    graph = rd(CUSTODY)['record_order']
    assert dag['exact_record_order'] == graph == fragment(dag['source'])
    order = dag['topological_order']
    assert len(order) == len(graph) and set(order) == set(graph)
    positions = {node:i for i,node in enumerate(order)}
    assert all(positions[parent]<positions[node] for node,parents in graph.items() for parent in parents)
    assert [n for n in order if n in {f.upper() for f in FAMILIES}] == [f.upper() for f in FAMILIES]
    # Reverse adjacency reachability is independent of I243's forward fixed point.
    children = {node:set() for node in graph}
    for node,parents in graph.items():
        for parent in parents:
            children[parent].add(node)
    descendants = {}
    for root in ['ANCHOR']+[f.upper() for f in FAMILIES]:
        seen, frontier = set(), list(children[root])
        while frontier:
            node = frontier.pop()
            if node not in seen:
                seen.add(node)
                frontier.extend(children[node])
        assert root not in seen
        descendants[root] = sorted(seen)
    assert dag['invalidation_descendants'] == descendants
    for family in FAMILIES:
        # None of the four current antecedents can depend on a later C/root/receipt.
        assert not {'C_CONTEXT','ACCEPTANCE','BUNDLE','Q_REQUEST','FINAL_ROOT','LAUNCH_RECEIPT','ATOMIC_CLAIM'} & set(graph[family.upper()])
    assert dag['documentary_acyclicity_verified'] is True
    assert dag['actual_records_authentic_current_accepted_or_frozen'] is False
    return dict(exact_record_order=graph,reverse_adjacency_invalidation_descendants=descendants,
        all_edges_follow_topological_order=True,actual_authentication_currentness_acceptance_or_freeze_proved=False)


def inspect(d):
    # Reconstruct contracts, schemas, graph and scope directly from primary documents.
    plan, custody, definitions, ce08 = rd(PLAN),rd(CUSTODY),rd(PACK)['$defs'],rd(CE08)
    w = plan['work_packages'][9]
    assert d['work_package'] == 'W10' and d['planned_deliverable_id'] == w['deliverable_id']
    assert fragment(d['work_package_binding']) == w
    for key,source in [('required_deliverables','deliverables'),('required_exit_predicates','exit_predicates'),('reject_if','reject_if'),('needs_separate_future_authority_for','needs_separate_future_authority_for')]:
        assert d[key] == w[source], key
    gate = d['dependency_gate']
    assert gate['required_package_ids'] == fragment(gate['source']) == w['depends_on'] == ['W02','W03','W04','W05','W06','W07','W08','W09']
    assert gate['SD01_stop_active'] is True and gate['actual_entry_authority_or_accepted_effective_baseline'] is None
    assert all(gate['W%02d_accepted'%i] is False for i in range(1,10))
    assert gate['documentary_preparation_and_reviews_not_actual_dependency_acceptance'] is True
    assert d['role_scope_matrix'] == [r for r in rd(CE01)['role_scope_matrix'] if r['id'] in ['R01','R02','R03','R06','R08']]
    people = d['role_and_contributor_boundary']
    assert fragment(people['source']) == rd(W02)['identity_policy']
    assert people['exact_identity_policy'] == rd(W02)['identity_policy']['exact_policy']
    assert people['exact_separation_matrix'] == rd(W02)['separation_matrix'] and len(people['exact_separation_matrix']) == 14
    assert people['exact_overlap_policy'] == rd(W02)['overlap_policy']
    assert len(people['exact_identity_policy']['S01_exclusions']) == 8 and len(people['exact_identity_policy']['extra_custody_separation']) == 4
    assert people['required_provider_kind'] == w['provider_kind']
    assert people['primary_review_roles'] == w['primary_review_roles'] == ['R01','R02','R03','R06']
    assert people['separate_acceptor_role'] == w['separate_acceptor_role'] == 'R08'
    assert people['required_subjects'] == ce08['contributor_closure']['required_subjects']
    require_true(people,['actual_W05_W09_authors_providers_and_all_documentary_preparers_must_be_known_authenticated_and_in_complete_final_registry',
        'W02_CE03_remain_provisional_not_prior_final_completeness_or_future_author_approval',
        'actor_registry_first_after_actual_authors_known_and_prior_identity_authority_verified',
        'complete_sorted_unique_canonical_human_alias_role_preparer_key_scope_no_truncation_required',
        'software_principal_not_alias_to_evade_human_exclusions','document_hashes_git_assistant_labels_not_authorship_or_independence',
        'no_synthetic_person_preparation_record_or_forecast_hash'])
    for key in ['actual_complete_contributor_preparer_alias_author_provider_and_key_inventory',
        'actual_identity_competence_enrollment_appointments_custody_and_exclusion_comparisons','actual_counts',
        'actual_independent_primary_reviews','actual_separate_R08_acceptance']:
        assert people[key] is None, key
    assert people['accepted'] is False
    rows = d['freeze_record_ledger']
    assert [r['family'] for r in rows] == FAMILIES and [r['order'] for r in rows] == [1,2,3,4]
    for row in rows:
        schema = definitions[row['family']]
        assert row['exact_schema'] == schema == fragment(row['schema_source'])
        assert row['schema_source']['json_pointer'] == '/$defs/'+row['family']
        assert row['candidate_body_cap_bytes'] == custody['record_caps_bytes'][row['family']]
        assert row['cap_applied_as_quota'] is False
        assert [r['field'] for r in row['field_requirements']] == schema['required']
        for slot in row['field_requirements']:
            assert slot['actual_value'] is None and slot['status'] == 'MISSING_NOT_POSITIVE_RECORD'
        require_missing(row,['actual_frozen'])
    assert [len(r['field_requirements']) for r in rows] == [8,26,13,14]
    assert [r['candidate_body_cap_bytes'] for r in rows] == [98304,98304,8192,16384]
    assert [r['name'] for r in d['nested_schema_obligations']] == HELPERS
    for row in d['nested_schema_obligations']:
        assert row['exact_schema'] == definitions[row['name']] == fragment(row['source'])
    assert [r['id'] for r in d['contract_rule_requirements']] == ce08['contract_rules'] == ['K02','K03','K04','K05','K06','K08','K10','K12','K13','K16']
    for row in d['contract_rule_requirements']:
        assert row['exact_rule'] == next(r for r in custody['rules'] if r['id']==row['id']) == fragment(row['source'])
    inherited = d['inherited_freeze_policy_requirements']
    assert set(inherited) == set(POLICIES)
    for key,row in inherited.items():
        assert row['exact_requirement'] == ce08[key] == fragment(row['source'])
    typed = inherited['typed_array_limits']['exact_requirement']
    assert (typed['preparers_min'],typed['preparers_max']) == (definitions['actor_registry']['properties']['documentary_preparation_records']['minItems'],definitions['actor_registry']['properties']['documentary_preparation_records']['maxItems']) == (1,16)
    assert typed['actors_max'] == definitions['actor_registry']['properties']['actors']['maxItems'] == 64
    assert typed['dependencies_max'] == definitions['image_manifest']['properties']['dependencies']['maxItems'] == 128
    assert typed['keys_max'] == definitions['anchor_registry']['properties']['keys']['maxItems'] == 64
    assert typed['actual_counts'] is None and typed['truncation_or_quota_increase_allowed'] is False
    fresh = inherited['freshness_policy']['exact_requirement']
    assert fresh['snapshot_lifetime_max_seconds'] == 3600 and fresh['clock_error_max_seconds'] == 5
    assert fresh['actual_clock_currentness_or_epoch_evidence'] is None and fresh['actual_snapshot_validity'] is None
    assert fresh['actual_fresh_snapshot_created'] is False and fresh['client_date_or_host_clock_is_not_trusted_runtime_evidence'] is True
    body = d['schema_and_body_boundary']
    assert body['exact_package_contract'] == plan['evidence_package_contract'] == fragment(body['source'])
    require_true(body,['top_level_slots_and_serialized_caps_not_nested_completeness_heap_CPU_or_full_evidence_proof',
        'actual_counts_or_body_sizes_unknown_not_zero_and_caps_not_measured_fit',
        'every_reference_body_complete_available_authentic_with_bytes_digest_author_provider_custody_units_assumptions_and_validity_required',
        'positive_records_require_complete_values_not_null_or_placeholder','no_new_positive_schema_Reader_member_input_output_or_free_offline_proof',
        'complete_preparers_1_to16_actors_keys_at_most64_dependencies_at_most128_without_trimming'])
    assert body['actual_full_body_evidence_scope_closure_or_cap_fit_derivation'] is None and body['actual_positive_record_or_snapshot_created'] is False
    graph = reconstruct_graph(d['record_DAG'])
    hashes = d['hash_scope_and_validity_boundary']
    assert fragment(hashes['source']) == custody['record_order']
    require_true(hashes,['actual_complete_canonical_bodies_before_SHA256_JCS_record_hashes_or_source_root',
        'actor_then_image_then_caller_then_platform_and_authentic_antecedent_scope_required',
        'final_image_digest_not_runtime_identity_and_no_image_self_manifest_bundle_digest',
        'exact_six_source_mapping_and_complete_interpreter_loader_stdlib_frozen_native_crypto_closure_required',
        'README_DOCUMENT_and_no_test_runner_loaded_by_membership',
        'exact_selected_profile_schema_output_transport_grammar_and_custody_policies_must_be_implemented_not_just_named',
        'record_hashes_epoch_validity_and_caller_registry_image_platform_domain_constructor_resource_cross_bindings_must_agree',
        'same_epoch_current_overlapping_validity_strict_not_before_expires_lifetime3600_clock_error5_required',
        'trusted_clock_known_revocation_every_boundary_not_host_date_stale_cache_TOFU_or_hidden_lookup',
        'fresh_snapshots_only_when_real_evidence_ready_no_documentary_expiry_extension'])
    assert hashes['actual_final_hash_cross_binding_epoch_currentness_or_policy_implementation_evidence'] is None
    assert hashes['actual_clock_sample_or_fresh_snapshot_created'] is False
    reconciliation = d['W09_reconciliation_ledger']
    assert [r['id'] for r in reconciliation] == [r[0] for r in RECONCILIATIONS]
    for row,(_,path,field) in zip(reconciliation,RECONCILIATIONS):
        assert row['source']['path'] == path and row['source']['json_pointer'] == '/'+field
        assert fragment(row['source']) == rd(path)[field]
        require_missing(row)
        assert row['same_facts_verified'] is False
    boundary = d['reconciliation_and_invalidation_boundary']
    assert boundary['exact_plan_order'] == plan['scope_authentication_and_freeze_order'] == fragment(boundary['source'])
    assert fragment(boundary['W09_requirement']) == rd(W09)['phase_handoff']
    assert boundary['latest_W09_documentary_review']['path'] == P+'D5-I242-I241-documentary-review.json'
    require_true(boundary,['genuine_baseline_actor_image_caller_platform_authentication_and_real_authors_bodies_required_before_W09_not_created_retroactively_by_W10',
        'W10_follows_W09_without_supplying_its_sole_authentication_or_backward_acceptance_dependency',
        'same_effective_source_runtime_image_caller_domain_resources_actors_authors_policies_assumptions_and_hashes_must_reconcile',
        'changed_author_alias_body_source_runtime_image_caller_domain_platform_resource_epoch_key_policy_or_schema_stops_progress_and_invalidates_dependents',
        'anchor_or_key_change_revisits_anchor_policy_before_dependent_freeze',
        'affected_W02_W09_and_later_records_requalified_and_competently_reviewed_before_progress_no_automatic_proof_or_hash_transfer',
        'recomputation_or_documentary_refresh_not_active_capture_inputs_rebind'])
    assert boundary['actual_same_facts_reconciliation_or_affected_package_requalification'] is None and boundary['actual_refresh_or_active_rebind'] is False
    resource = d['resource_and_cost_boundary']
    assert fragment(resource['source']) == rd(W09)['resource_premise_handoff']
    assert fragment(resource['source_policy']) == plan['resource_and_scope_policy']
    assert resource['exact_candidate_reserve_rules'] == rd(CONTRACT)['reserve_accounting']
    require_true(resource,['actual_prior_BASIS_index_E01_E05_acceptance_and_same_scope_complete_derivations_required',
        'new_authorship_custody_proof_body_memory_registry_freshness_crypto_lookup_native_IO_and_output_work_not_free',
        'both_Reader_ledgers_global_join_all_original_native_children_failure_cleanup_and_traceback_heap_scope_preserved',
        'changed_costs_assumptions_or_graph_require_reviewed_full_heap_work_service_phase_and_Reader_bounds',
        'budgets_not_available_capacity_service_or_success900'])
    assert resource['actual_resource_or_full_Reader_fit_derivation'] is None
    assert type(resource['reserve_transfers_applied']) is int and resource['reserve_transfers_applied'] == 0
    assert resource['resources_reserved'] is False and resource['quotas_or_budgets_changed'] is False
    phase = d['phase_handoff']
    assert fragment(phase['W11_consumer']) == plan['work_packages'][10]
    require_true(phase,['four_antecedent_records_only_W11_C_projection_and_acceptance_W12_bundle_mapping_W13_gates_deferred',
        'future_C_acceptance_bundle_Q_root_claim_receipt_not_antecedent_of_current_freeze','CE11_handoff_does_not_depend_on_CE12_receipt'])
    assert phase['final_route_boundary'] == plan['prelaunch_handoff_and_CE12']
    assert phase['actual_C_acceptance_bundle_mapping_Q_root_claim_receipt_or_authority_created'] is False
    authority = d['authority_boundary']
    assert authority['inherited_boundary'] == plan['authorization_boundary'] == fragment(authority['source'])
    require_true(authority,['no_product_components_import_compile_discovery_tests_runs_builds_crypto_codec_signing_keygen_enrollment_or_provisioning',
        'no_clock_CPU_IO_schedule_service_platform_ledger_claim_replay_crash_restart_endpoint_process_sampling_benchmarks_or_probes',
        'no_identity_key_policy_operator_service_selection_configuration_provider_contacts_or_new_helpers_channels_inputs_outputs'])
    require_missing(authority)
    assert [r['predicate'] for r in d['exit_predicate_dispositions']] == w['exit_predicates']
    for row in d['exit_predicate_dispositions']:
        assert row['predicate'] == fragment(row['source'])
        require_missing(row)
    assert d['preserved_scope_and_gates'] == {k:plan[k] for k in ['inherited_scope_boundaries','preserved_negative_gates','prelaunch_handoff_and_CE12']}
    for key,value in d['current_effect'].items():
        if key == 'W10_documentary_prepared':
            assert value is True
        elif key == 'IR03':
            assert value == 'NOT_READY'
        elif key in ['actual_evidence_accepted','work_packages_accepted','prelaunch_gates_closed','resource_obligations_closed']:
            assert type(value) is int and value == 0
        else:
            assert value is False, key
    check_pointers(d)
    return graph


CRITERIA = [
    'Exact W10 deliverables, eight dependencies, exits, rejections and operational snapshot restriction match I223',
    'SD01 and W01-W09 nonacceptance remain active',
    'R01/R02/R03/R06 review and separate R08 acceptance remain unassigned',
    'W02 identity policy, fourteen separations, eight S01 and four extra custody exclusions remain exact',
    'Qualified R01/R02 overlap preserved; software/Git/assistant identity cannot evade human evidence',
    'Actual W05-W09 authors/providers and every preparer must precede final registry completeness',
    'Four records retain actor/image/caller/platform order and exact I191 schemas',
    'All61 top-level slots are missing requirements, not positive record values',
    'Candidate body caps98304/98304/8192/16384 remain unapplied and do not prove resource fit',
    'Eight nested definitions and all underlying evidence obligations retained',
    'Ten exact custody rules and six selected CE08 policies retained without stale historical availability claims',
    'Preparers1..16 actors/keys64 dependencies128 match schema requirements without truncation or measured counts',
    'Body bytes/hashes/providers/custody/authentication/epoch/validity/reviews remain missing',
    'Independent graph edge-order and reverse-adjacency checks reproduce invalidation descendants',
    'No C/acceptance/bundle/Q/root/claim/receipt is a predecessor of the four current records',
    'Canonical complete-body hashing and source-root rules reject predicted or placeholder final identities',
    'Six-source mapping, README DOCUMENT and complete exact runtime closure remain requirements',
    'Image identity is distinct from runtime and selected policies require implementation evidence',
    'Cross-record hashes, actors/requester/domain/constructor/resource scope and epoch/validity must reconcile',
    'Lifetime3600/error5/currentness/revocation requirements remain unproved; host date is not runtime evidence',
    'Ten exact W02-W09 baseline/freeze reconciliation links remain without comparisons or acceptance',
    'W10 cannot retroactively authenticate W09 or introduce a backward acceptance dependency',
    'Changed contributor/body/source/runtime/domain/resource/epoch/key/policy invalidates and requalifies dependents',
    'Anchor/key changes revisit prior anchor policy; no automatic proof/hash reuse or active rebind',
    'Prior BASIS/index/E01-E05 and full costs/Reader/heap/work/service/phase compatibility remain unaccepted',
    'Exact candidate reserve rules remain unchanged and resource costs are not free offline',
    'W11 C, W12 bundle/mapping, W13 gates and final CE12 prerequisites remain separate',
    'Inherited scope exclusions/negative gates and no-build/no-execution/no-sampling authority preserved']


def reconstruct():
    d = rd(SUBJECT)
    graph = inspect(d)
    pins = {**d['input_pins'],**{p:sha(p) for p in sorted(PRIOR_FILES)}}
    assert len(pins) == 1017
    verify_blobs(pins)
    return dict(schema='d5.i244-source-reconstruction.v1',increment='I244',date=DATE,base_commit=BASE,subject=pin(SUBJECT),input_pins=pins,
        criteria=[dict(id='RV%02d'%(i+1),criterion=t,result='PASS_DOCUMENTARY_REQUIREMENT_ONLY') for i,t in enumerate(CRITERIA)],
        counts=dict(input_pins=1017,antecedent_record_requirements=4,required_top_level_field_slots=61,nested_schema_requirements=8,
            contract_rules=10,inherited_freeze_policies=6,W09_reconciliation_requirements=10,separation_requirements=14,
            unassigned_review_roles=5,pending_exits=3,review_criteria=len(CRITERIA)),
        independent_documentary_graph=graph,current_effect={**d['current_effect'],'W10_documentary_reviewed':True})


def own_rejections(d):
    cases = [
        ('record_order_swap',('freeze_record_ledger',),list(reversed(d['freeze_record_ledger']))),
        ('schema_constant_substitution',('freeze_record_ledger',1,'exact_schema','properties','profile_sha256','const'),'UNVERIFIED_TEST_LABEL'),
        ('field_omission',('freeze_record_ledger',0,'field_requirements'),d['freeze_record_ledger'][0]['field_requirements'][:-1]),
        ('nested_dependency_cap_change',('nested_schema_obligations',4,'exact_schema','properties','component_name','maxLength'),129),
        ('typed_truncation_permission',('inherited_freeze_policy_requirements','typed_array_limits','exact_requirement','truncation_or_quota_increase_allowed'),True),
        ('preparer_cap_change',('inherited_freeze_policy_requirements','typed_array_limits','exact_requirement','preparers_max'),17),
        ('policy_constant_substitution',('inherited_freeze_policy_requirements','policy_constant_bindings','exact_requirement','expected_image_schema_constants','profile_sha256'),'UNVERIFIED_TEST_LABEL'),
        ('README_mapping_waiver',('inherited_freeze_policy_requirements','source_runtime_policy','exact_requirement','source_to_image_missing_inventory',0,'README_must_be_DOCUMENT'),False),
        ('DAG_edge_corruption',('record_DAG','exact_record_order','ACTOR_REGISTRY'),['FINAL_ROOT']),
        ('DAG_descendant_drop',('record_DAG','invalidation_descendants','ACTOR_REGISTRY'),[]),
        ('reconciliation_source_substitution',('W09_reconciliation_ledger',2,'source'),copy.deepcopy(d['W09_reconciliation_ledger'][3]['source'])),
        ('unknown_baseline_zero',('W09_reconciliation_ledger',0,'actual_authenticated_baseline_and_W09_fact'),0),
        ('snapshot_lifetime_extension',('inherited_freeze_policy_requirements','freshness_policy','exact_requirement','snapshot_lifetime_max_seconds'),3601),
        ('clock_error_waiver',('inherited_freeze_policy_requirements','freshness_policy','exact_requirement','clock_error_max_seconds'),6),
        ('host_date_as_trusted_clock',('inherited_freeze_policy_requirements','freshness_policy','exact_requirement','client_date_or_host_clock_is_not_trusted_runtime_evidence'),False),
        ('automatic_proof_reuse',('inherited_freeze_policy_requirements','invalidation_policy','exact_requirement','any_automatic_prior_proof_acceptance_or_hash_reuse'),True),
        ('missing_anchor_revisit',('reconciliation_and_invalidation_boundary','anchor_or_key_change_revisits_anchor_policy_before_dependent_freeze'),False),
        ('unreviewed_cost_change',('resource_and_cost_boundary','changed_costs_assumptions_or_graph_require_reviewed_full_heap_work_service_phase_and_Reader_bounds'),False),
        ('later_C_acceptance',('phase_handoff','four_antecedent_records_only_W11_C_projection_and_acceptance_W12_bundle_mapping_W13_gates_deferred'),False),
        ('implicit_service_configuration',('authority_boundary','no_identity_key_policy_operator_service_selection_configuration_provider_contacts_or_new_helpers_channels_inputs_outputs'),False)]
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
    return dict(schema='d5.i244-documentary-review.v1',increment='I244',date=DATE,timezone='Europe/Madrid',base_commit=BASE,
        status=STATUS,subject=pin(SUBJECT),reconstruction=pin(RECON),
        verdict='DOCUMENTARY_REQUIREMENTS_CONSISTENT_NO_NEW_DEFECT_FOUND_REAL_ANTECEDENT_FREEZE_MISSING_NOT_ADMITTED',findings=[],
        counts=rec['counts'],criteria=rec['criteria'],independent_documentary_graph=rec['independent_documentary_graph'],
        documentary_clarifications=[
            'Four records and61 missing slots are documentary requirements, not actual canonical bodies, measured byte sizes, authentic identities or accepted frozen records. Nested evidence closure and cap fit remain unproved.',
            'All actual W05-W09 authors/providers/preparers require prior identity evidence. W02 is provisional; same assistant or Git labels do not establish humans, competence, independence or R08 acceptance.',
            'Independent reverse-adjacency reconstruction confirms the documentary invalidation graph, not real authenticity or liveness. C/bundle/Q/root/claim/receipt remain later facts, never sole forecast antecedents.',
            'Ten baseline/freeze comparisons remain unknown. W10 cannot retrospectively authenticate W09; any changed author/body/source/runtime/domain/resource/epoch/key/policy requires affected-package requalification/review without automatic proof/hash transfer.',
            'Source/image/runtime/policy implementation, canonical cross-hashes, epoch/current validity/revocation and trusted clock remain missing. Client date does not satisfy runtime currentness; no snapshot is generated or expiry extended.',
            'Costs of new evidence/custody remain in both Readers and the full resource composition. No resource, quota/reserve, active rebind, later C/mapping/gate acceptance or execution authority is created.'],
        source_reconstruction=dict(primary_source_checks=True,I243_candidate_and_preparation_reproduced=True,prior_publication_mains_called=False,prior_Path_exists_restored=True,no_new_presence_projection=True),
        inherited_I243_rejection_checks=prep['rejection_checks'],additional_I244_rejection_checks=additional,current_effect=rec['current_effect'],
        provenance=dict(identity='Same Codex assistant/chat as I243',methodological_documentary_review_only=True,actor_independent=False,
            competent_R01_review=False,competent_R02_review=False,competent_R03_review=False,competent_R06_review=False,separate_R08_acceptance=False,external_contacts_made=False),
        limitations=['W02-W09 remain unaccepted; four actual bodies,61 fields, nested proofs, real authors/authentication/currentness and10 reconciliations remain missing. W10 is not frozen or accepted.',
            'SD01 active, three W10 exits unaccepted, zero accepted real packages, zero closed prelaunch gates and zero closed E01-E05 obligations. No resource/capacity/service/success900 or infeasibility proof.',
            'Same-assistant documentary checks do not satisfy competent independent primary review or separate R08 acceptance; publication grants no execution, enrollment, snapshot, build or quota authority.'],
        work_unit=dict(rollback_files=sorted(FILES),verification_command='python3 docs/validation/D5-I244-audit.py',expected_result=STATUS,
            runtime_harness='N/A: own documentary JSON/Git/hash/schema/field/DAG/role/scope checks and in-memory document mutations only. No target imports/compile/discovery/tests/runs/build, positive crypto/codec, signing/keygen/enrollment/provisioning, clock/CPU/IO/service/platform/ledger/claim/replay/process sampling/probes or contacts.',
            over400_lines=True,reason='One W10 review with primary-source reconstruction, pinned inputs, independent graph reachability, rejection checks and integrity preservation. Overage declared; no PR requested.'),
        publication=dict(commit_and_push_requested=True,publication_not_actual_freeze_identity_attestation_acceptance_or_execution_authority=True))


def main():
    rec = reconstruct()
    assert rec == rd(RECON)
    review = build_review(rec)
    assert review == rd(REVIEW)
    prior = rd(PRIOR_SEAL)
    preserved = {**prior['preserved_published704'],**prior['artifacts'],PRIOR_SEAL:sha(PRIOR_SEAL)}
    assert len(preserved) == 709
    seal = rd(SEAL)
    assert seal['schema'] == 'd5.i244-integrity.v1' and seal['base_commit'] == BASE
    assert seal['preserved_published709'] == preserved and set(seal['artifacts']) == FILES-{SEAL}
    for mapping in [preserved,seal['artifacts']]:
        for path,digest in mapping.items():
            assert sha(path) == digest, path
    assert seal['source_only'] is True and seal['current_effect'] == rec['current_effect']
    changed = set(git('diff',BASE,'--name-only').splitlines()) | set(git('ls-files','--others','--exclude-standard').splitlines())
    assert changed == FILES, changed
    subprocess.check_call(['git','merge-base','--is-ancestor',BASE,'HEAD'],cwd=ROOT)
    if git('rev-parse','HEAD') != BASE:
        assert not git('status','--porcelain')
    print(json.dumps(dict(status=STATUS,increment='I244',input_pins=1017,preserved_published_files=709,new_files=5,
        criteria=len(CRITERIA),inherited_documentary_rejections=len(review['inherited_I243_rejection_checks']),
        additional_documentary_rejections=len(review['additional_I244_rejection_checks']),findings=review['findings'],
        SD01_stop_active=True,prelaunch_gates_closed=0,resource_obligations_closed=0,D5_closed=False,git_head=git('rev-parse','HEAD')),sort_keys=True))


if __name__ == '__main__':
    main()
