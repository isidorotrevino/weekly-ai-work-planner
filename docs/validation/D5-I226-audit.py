#!/usr/bin/env python3
"""I226 documentary W01 review. Reads JSON/Git only; never runs product or publication mains."""
import copy
import hashlib
import io
import json
import runpy
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
P = 'docs/validation/'
BASE = '0150290fbb217f47f5bc3601dc3312d1a5e6b44a'
DATE = '2026-11-24'
PLAN = P+'D5-I223-PRELAUNCH-RESOURCE-CLOSURE-PLAN.json'
SUBJECT = P+'D5-I223-W01-TARGET-SCOPE-AUTHORITY-CANDIDATE.json'
CONTRACT = P+'D5-I130-PLATFORM-CONTRACT-CANDIDATE.json'
PROTO = P+'D5-I185-PGO181-SCHEMAS-CANDIDATE-02.json'
PROFILE = P+'D5-I185-PGO181-TRUST-PROFILE-CANDIDATE-02.json'
OUTPUT = P+'D5-I187-CONTEXT-LAUNCH-SCHEMAS-CANDIDATE.json'
TRANSPORT = P+'D5-I189-BOOTSTRAP-TRANSPORT-CONTRACT-CANDIDATE.json'
GRAMMAR = P+'D5-I189-BOOTSTRAP-TRANSPORT-GRAMMAR-CANDIDATE.json'
SPEC = P+'D5-I191-CALLER-IMAGE-CUSTODY-CONTRACT-CANDIDATE.json'
PACK = P+'D5-I191-CALLER-IMAGE-CUSTODY-SCHEMAS-CANDIDATE.json'
CE01 = P+'D5-I197-CE01-SCOPE-AND-DECISION-BOUNDARY-CANDIDATE-02.json'
CE07 = P+'D5-I193-CE07-RESOURCE-AND-COMPATIBILITY-JOIN-CANDIDATE.json'
PLAN_REVIEW = P+'D5-I224-I223-documentary-review.json'
PRIOR_AUDIT = P+'D5-I225-audit.py'
PRIOR_PREP = P+'D5-I225-preparation-review.json'
PRIOR_SEAL = P+'D5-I225-integrity.json'
PRIOR_DOC = 'docs/design/D5-I225-W01-TARGET-SCOPE-AUTHORITY.md'
PRIOR_FILES = {SUBJECT,PRIOR_AUDIT,PRIOR_PREP,PRIOR_SEAL,PRIOR_DOC}
POLICIES = [CONTRACT,PROTO,PROFILE,OUTPUT,TRANSPORT,GRAMMAR,SPEC,PACK]
RECON = P+'D5-I226-I225-source-reconstruction.json'
REVIEW = P+'D5-I226-I225-documentary-review.json'
AUDIT = P+'D5-I226-audit.py'
SEAL = P+'D5-I226-integrity.json'
DOC = 'docs/design/D5-I226-I225-W01-REVIEW.md'
FILES = {RECON,REVIEW,AUDIT,SEAL,DOC}
STATUS = 'PASS_STATIC_SOURCE_ONLY_W01_REVIEW_ENTRY_AUTHORITY_MISSING_NOT_ADMITTED'


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


def verify_blobs(pins):
    body = subprocess.check_output(['git','cat-file','--batch'],cwd=ROOT,
        input=''.join(BASE+':'+p+'\n' for p in sorted(pins)).encode())
    stream = io.BytesIO(body)
    for path,digest in sorted(pins.items()):
        header = stream.readline().decode().split()
        assert len(header) == 3 and header[1] == 'blob', path
        data = stream.read(int(header[2]))
        assert stream.read(1) == b'\n'
        assert hashlib.sha256(data).hexdigest() == digest == sha(path), path
    assert stream.read() == b''


def check_pointers(value):
    if isinstance(value,dict):
        if {'path','sha256','json_pointer'} <= set(value):
            fragment(value)
        for child in value.values():
            check_pointers(child)
    elif isinstance(value,list):
        for child in value:
            check_pointers(child)


def inspect_scope(d):
    """Independent policy/plan comparisons, not candidate-builder equality."""
    plan = rd(PLAN)
    w = plan['work_packages'][0]
    inherited = plan['inherited_scope_boundaries']
    contract = rd(CONTRACT)
    transport = rd(TRANSPORT)
    spec = rd(SPEC)
    pack = rd(PACK)['$defs']
    assert d['work_package'] == w['id'] == 'W01' and w['depends_on'] == []
    assert fragment(d['work_package_binding']) == w and d['planned_deliverable_id'] == w['deliverable_id']
    for target,source in [('required_deliverables','deliverables'),('required_exit_predicates','exit_predicates'),
                          ('reject_if','reject_if'),('needs_separate_future_authority_for','needs_separate_future_authority_for')]:
        assert d[target] == w[source]
    assert len(d['required_deliverables']) == 3 and len(d['required_exit_predicates']) == 3
    paths = pack['source_bindings']['required']
    assert len(paths) == 6 and [r['logical_path'] for r in d['logical_source_scope']] == paths, 'source_set'
    for row in d['logical_source_scope']:
        assert (ROOT/row['logical_path']).exists() is row['actual_path_exists'] is False, 'source_presence'
        assert row['target_kind'] == ('DOCUMENT' if row['logical_path'].endswith('/README.md') else 'PROSPECTIVE_SOURCE_NOT_YET_QUALIFIED')
        assert all(row[k] is None for k in ['actual_successor_source_sha256','actual_image_member_or_digest','actual_loaded_representation','actual_source_runtime_mapping_proof']), 'predictive_hash'
        assert row['accepted'] is False
    env = d['effective_environment_scope']
    assert env['required_closure_kinds'] == ['interpreter','loader','stdlib','frozen modules','native/crypto extensions','allocator/GC','kernel/service/scheduler/IO','build recipe/toolchain']
    assert fragment(env['source']) == spec['rules'][3] and spec['rules'][3]['id'] == 'K04'
    assert all(v is None for k,v in env.items() if k.startswith('actual_'))
    assert env['image_and_runtime_digests_are_distinct_concepts'], 'image_as_runtime'
    assert env['exact_historical480_or_six_successor_sources_no_unbound_helper_required']
    assert env['README_document_membership_does_not_prove_test_or_runner_loaded']
    assert env['no_self_embedded_image_manifest_bundle_or_future_root_digest']
    caller = d['caller_platform_ledger_scope']
    assert caller['expected_platform_guarantees'] == pack['platform_custody']['properties']['guarantees']['required']
    assert len(caller['expected_platform_guarantees']) == 8
    assert all(v is None for k,v in caller.items() if k.startswith('actual_'))
    assert caller['required_global_claim_tuple'] == ['trust_context_sha256','runtime_request_sha256','invocation_id']
    assert caller['required_unique_mapping_key'] == ['configuration_epoch','SHA256(JCS(actual C))']
    assert caller['global_across_all_callers_domains_restarts_not_partitioned'], 'partitioned_ledger'
    assert [r['path'] for r in d['policy_version_inventory']] == POLICIES
    for row in d['policy_version_inventory']:
        src = rd(row['path'])
        assert row['document_sha256'] == sha(row['path'])
        assert row['source_version'] == next(src[k] for k in ['contract_id','profile_id','$id','schema'] if k in src)
        assert row['document_hash_is_not_runtime_image_or_proof_hash']
        assert row['actual_runtime_policy_implementation_or_adoption_verified'] is False
    for ledger,key in [('numeric_candidate_ledger','numeric_candidates_unchanged'),('protocol_output_ledger','protocol_and_output_caps')]:
        rows = d[ledger]
        assert len(rows) == len(inherited[key]) and {r['name']:r['value'] for r in rows} == inherited[key]
        for row in rows:
            assert row['value'] == fragment(row['source'])
            assert row['actual_applied_or_changed'] is False, 'active_quota'
    for row in d['protocol_output_ledger']:
        if row['name'] in ['Reader_design_bytes_conditional','bundle_upper_conditional_on_nested_caps']:
            assert row['kind'] == 'CONDITIONAL_DESIGN_ENVELOPE_NOT_ACTUAL_FIT', 'conditional_as_fit'
    caps = d['custody_record_cap_ledger']
    assert len(caps) == 8 and {r['family']:r['candidate_body_cap_bytes'] for r in caps} == spec['record_caps_bytes']
    for row in caps:
        assert row['candidate_body_cap_bytes'] == fragment(row['source'])
        assert row['actual_body_size'] is None and row['actual_cap_fit_verified'] is False and row['actual_quota_applied'] is False
    heap = d['heap_scope_ledger']
    assert heap['candidate_heap_contract'] == contract['heap'] == fragment(heap['source'])
    assert heap['actual_complete_heap_or_native_allocator_GC_overlap_proof'] is None and heap['actual_capacity_attestation'] is None
    assert heap['actual_budget_fit_verified'] is False and heap['resources_reserved'] is False
    assert heap['reserve_transfers_applied'] == 0, 'reserve_transfer'
    phase = d['phase_marker_ledger']
    for key in ['normative_markers','ordered_interval_rule','success_path_qualification','observation_latency_rule']:
        assert phase[key] == contract['time'][key]
    assert phase['candidate_phase_budgets'] == contract['time']['phase_budgets']
    assert [r['candidate_wall_seconds'] for r in phase['candidate_phase_budgets']] == [60,750,60]
    assert phase['candidate_success_seconds'] == 900 and phase['unassigned_wall_candidate_reserve_seconds'] == 30
    assert phase['actual_clock_samples_or_marker_values'] is None and phase['actual_work_CPU_service_latency_or900_proof'] is None, 'budget_as_900_proof'
    assert phase['reserve_transfers_applied'] == 0 and phase['no_missing_marker_or_unknown_cost_as_zero']
    assert phase['exact_True_wait_worker_tW_not_exit_or_later_validation_and_success_finally_tF_required'], 'wrong_tW'
    expected_guards = [('PROFILE-'+r['id'],PROFILE,'/semantic_contracts/'+str(i),r) for i,r in enumerate(rd(PROFILE)['semantic_contracts'])]
    for group in ['one_use_and_permissions','failure_and_outputs']:
        expected_guards += [('TRANSPORT-'+group+'-'+k,TRANSPORT,'/'+group+'/'+k,v) for k,v in transport[group].items()]
    expected_guards += [('CP07-%02d'%(i+1),PLAN,'/inherited_scope_boundaries/full_CP07_conditions/'+str(i),r) for i,r in enumerate(inherited['full_CP07_conditions'])]
    assert len(d['guard_obligation_ledger']) == len(expected_guards) == 32
    for row,(identifier,path,pointer,rule) in zip(d['guard_obligation_ledger'],expected_guards):
        assert row['id'] == identifier and row['source'] == pin(path,pointer)
        assert row['policy_fragment'] == fragment(row['source']) == rule
        assert row['actual_proof_sha256'] is None and row['actual_successor_implementation_or_qualification_verified'] is False
    route = d['transport_and_output_scope']
    assert route['required_route'] == transport['route']
    for k in ['trust_boundary','endpoint_ownership','argv_and_channel_checks','framing']:
        assert route[k] == transport[k]
    assert route['output_schema_binding'] == pin(OUTPUT) and route['grammar_binding'] == pin(GRAMMAR)
    assert route['custody_projection'] == spec['projection']
    assert route['no_new_file_pipe_helper_input_wire_argv_or_output_receipt_channel'], 'hidden_channel'
    assert route['actual_control_channels_processes_outputs_or_receipts_created'] is False
    requal = d['source_requalification_boundary']
    assert requal['required_legacy_scope'] == rd(CE07)['requalification']['required_legacy_scope'] == dict(operand_cases=179,roots=321,root_groups=12,atomic_sites=30)
    assert requal['all_new_custody_bootstrap_output_failure_paths_and_costs_require_requalification']
    assert requal['historical_CP03_atomicity_implementation_or_ten_test_counts_not_successor_evidence']
    assert requal['actual_source_BASIS_index_atomicity_or_resource_proofs'] is None
    authority = d['entry_authority_inventory']
    assert [r['required_role'] for r in authority] == ['SCOPE_AUTHORITY','R06','R08']
    assert w['primary_review_roles'] == ['R06'] and w['separate_acceptor_role'] == 'R08'
    rolemap = {r['id']:r for r in rd(CE01)['role_scope_matrix']}
    assert rolemap['R06']['separation_required_from'] == ['DOCUMENTARY_PREPARER']
    assert rolemap['R08']['separation_required_from'] == ['DOCUMENTARY_PREPARER','R03','R04','R06','R07']
    for row in authority:
        assert all(v is None for k,v in row.items() if k.startswith('actual_')), 'invented_authority'
        assert row['accepted'] is False and row['contact_or_nomination_authorized_now'] is False
    boundary = d['entry_authority_boundary']
    assert fragment(boundary['source']) == rd(PLAN_REVIEW)['documentary_clarifications'][0]
    assert boundary['W01_no_predecessor_does_not_mean_self_authorized']
    assert boundary['future_W02_appointments_or_future_bundle_not_sole_forecast_authority'], 'future_W02_authority'
    assert boundary['independently_authentic_preexisting_scope_and_reviewer_authority_required_at_entry']
    assert boundary['current_user_request_authorizes_docs_audit_commit_push_not_canonical_role_or_scope_adoption']
    assert boundary['no_implicit_nomination_contact_enrollment_or_signing']
    assert boundary['actual_entry_authority_verified'] is False and boundary['SD01_stop_active'] is True, 'SD01_waived'
    actions = d['action_authority_ledger']
    assert len(actions) == 12 and [r['action'] for r in actions[:4]] == ['READ_REPOSITORY_JSON_GIT_AND_DOCUMENT_HASHES','PREPARE_THIS_NEGATIVE_W01_DOSSIER','RUN_OWN_DOCUMENTARY_AUDIT','COMMIT_AND_PUSH_THIS_UNIT']
    assert all(r['actual_runtime_authority_granted'] is False for r in actions[:4])
    denied = {k:v for k,v in plan['authorization_boundary'].items() if k.endswith('_authorized')}
    assert all(v is False for v in denied.values()) and plan['authorization_boundary']['current_run_command'] is None
    assert [r['action'] for r in actions[4:]] == list(denied)
    for row in actions[4:]:
        assert row['authorized_now'] is False and row['actual_action_authority'] is None, 'operation_authorized'
        assert row['current_status'] == 'NOT_AUTHORIZED' and fragment(row['source']) is False
        assert row['requires_separate_exact_future_authority_and_cost_proof']
    assert d['inherited_scope_boundaries'] == inherited and len(inherited['S01_exclusions']) == 8, 'exclusion_removed'
    assert d['preserved_negative_gates'] == plan['preserved_negative_gates']
    for row in d['preserved_negative_gates']:
        source = {**row['source'],'json_pointer':row['json_pointer']}
        assert fragment(source) == row['observed_value']
    exits = d['exit_predicate_dispositions']
    assert len(exits) == 3 and [r['predicate'] for r in exits] == w['exit_predicates']
    for row in exits:
        assert fragment(row['source']) == row['predicate']
        assert row['accepted'] is False and row['documentary_content_prepared'] is True, 'exit_accepted'
        assert all(v is None for k,v in row.items() if k.startswith('actual_'))
    assert d['handoff_and_deferred_scope']['preserved_boundary'] == plan['prelaunch_handoff_and_CE12']
    assert d['handoff_and_deferred_scope']['CE12_remains_private_DEFERRED_NOT_AUTHORIZED']
    assert d['change_control']['inherited_plan_policy'] == plan['scope_authentication_and_freeze_order']
    assert d['change_control']['actual_rebind_snapshot_refresh_or_runtime_config_changed'] is False
    assert all(v is None for k,v in d['existing_external_material_intake'].items() if k.startswith('actual_'))
    for key,value in d['current_effect'].items():
        if key == 'W01_documentary_prepared':
            assert value is True
        elif key == 'IR03':
            assert value == 'NOT_READY'
        elif key in ['actual_evidence_accepted','work_packages_accepted','prelaunch_gates_closed','resource_obligations_closed']:
            assert type(value) is int and value == 0
        else:
            assert value is False, 'positive_effect'
    assert d['producer']['actor_independent'] is False and d['producer']['competent_R06_review'] is False
    assert d['producer']['separate_R08_acceptance'] is False and d['producer']['external_contacts_made'] is False
    check_pointers(d)


def reconstruct():
    d = rd(SUBJECT)
    pins = {**d['input_pins'],**{p:sha(p) for p in sorted(PRIOR_FILES)}}
    assert len(pins) == 927
    verify_blobs(pins)
    inspect_scope(d)
    checks = [
        ('RC01','W01 three deliverables, three exit predicates, rejection/authority clauses exactly bind I223','/work_package_binding'),
        ('RC02','Exactly six absent successor paths; no predicted digests, loaded mapping or hidden helper','/logical_source_scope'),
        ('RC03','Complete logical environment closure; image and runtime identities separate, facts missing','/effective_environment_scope'),
        ('RC04','Caller/platform guarantees and globally shared ledger/mapping remain unproved','/caller_platform_ledger_scope'),
        ('RC05','Eight exact document versions/hashes do not attest runtime or image identity','/policy_version_inventory'),
        ('RC06','24 numeric and12 protocol candidates preserved without application or conditional-fit promotion','/numeric_candidate_ledger'),
        ('RC07','Eight custody caps and complete candidate heap/reserves remain unproved and unallocated','/heap_scope_ledger'),
        ('RC08','60/750/60+30 and exact-True wait return/finally markers preserved without success proof','/phase_marker_ledger'),
        ('RC09','32 exact profile/transport/CP07 guards and unchanged route/output bindings','/guard_obligation_ledger'),
        ('RC10','179/321/12/30 and all new paths/costs require successor qualification','/source_requalification_boundary'),
        ('RC11','Three genuine entry-authority slots absent; W02 cannot bootstrap W01; SD01 active','/entry_authority_boundary'),
        ('RC12','Four documentary actions separated from eight unauthorized operational classes','/action_authority_ledger'),
        ('RC13','Eight S01 and extra custody exclusions plus inherited certificate state preserved','/inherited_scope_boundaries'),
        ('RC14','Three exits pending: documentary coverage is not authentic scope acceptance','/exit_predicate_dispositions'),
        ('RC15','Prelaunch/resource handoff excludes final-route execution and keeps CE12 deferred','/handoff_and_deferred_scope'),
        ('RC16','Changed facts require impact/revalidation; no current authority, resource or D5 promotion','/change_control')]
    return dict(schema='d5.i226-i225-source-reconstruction.v1',increment='I226',date=DATE,timezone='Europe/Madrid',base_commit=BASE,
        subject=pin(SUBJECT),plan=pin(PLAN,'/work_packages/0'),entry_clarification=pin(PLAN_REVIEW,'/documentary_clarifications/0'),
        input_pins=pins,criteria=[dict(id=i,criterion=t,subject=pin(SUBJECT,p),result='DOCUMENTARY_CONSISTENCY_CONFIRMED_NOT_REAL_ACCEPTANCE') for i,t,p in checks],
        counts=dict(input_pins=927,criteria=16,successor_paths=6,policies=8,numeric_candidates=24,protocol_candidates=12,
            custody_caps=8,guard_obligations=32,missing_entry_authorities=3,documentary_actions=4,unauthorized_operational_classes=8,pending_exits=3),
        successor_sources=[dict(path=r['logical_path'],exists=False,actual_digest=None,qualified=False) for r in d['logical_source_scope']],
        exit_dispositions=[dict(id=r['id'],exact_predicate=r['predicate'],documentary_consistency=True,authentic_acceptance=False) for r in d['exit_predicate_dispositions']],
        inherited_scope_boundaries=d['inherited_scope_boundaries'],preserved_negative_gates=d['preserved_negative_gates'],
        current_effect={**d['current_effect'],'W01_documentary_reviewed':True},
        methodological_review_is_not_independent_R06_or_separate_R08=True)


def rejection_checks():
    cases = [
        ('predictive_hash',('logical_source_scope',0,'actual_successor_source_sha256'),'INVENTED_NOT_REAL_DIGEST'),
        ('source_presence',('logical_source_scope',0,'actual_path_exists'),True),
        ('image_as_runtime',('effective_environment_scope','image_and_runtime_digests_are_distinct_concepts'),False),
        ('partitioned_ledger',('caller_platform_ledger_scope','global_across_all_callers_domains_restarts_not_partitioned'),False),
        ('active_quota',('numeric_candidate_ledger',0,'actual_applied_or_changed'),True),
        ('conditional_as_fit',('protocol_output_ledger',7,'kind'),'ACTUAL_FIT'),
        ('reserve_transfer',('heap_scope_ledger','reserve_transfers_applied'),1),
        ('budget_as_900_proof',('phase_marker_ledger','actual_work_CPU_service_latency_or900_proof'),900),
        ('wrong_tW',('phase_marker_ledger','exact_True_wait_worker_tW_not_exit_or_later_validation_and_success_finally_tF_required'),False),
        ('hidden_channel',('transport_and_output_scope','no_new_file_pipe_helper_input_wire_argv_or_output_receipt_channel'),False),
        ('invented_authority',('entry_authority_inventory',0,'actual_canonical_human'),'UNAUTHENTICATED_TEST_LABEL_NOT_ACTOR'),
        ('future_W02_authority',('entry_authority_boundary','future_W02_appointments_or_future_bundle_not_sole_forecast_authority'),False),
        ('SD01_waived',('entry_authority_boundary','SD01_stop_active'),False),
        ('operation_authorized',('action_authority_ledger',4,'authorized_now'),True),
        ('exclusion_removed',('inherited_scope_boundaries','S01_exclusions'),[]),
        ('exit_accepted',('exit_predicate_dispositions',0,'accepted'),True),
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
    return dict(schema='d5.i226-i225-documentary-review.v1',increment='I226',date=DATE,timezone='Europe/Madrid',base_commit=BASE,
        status=STATUS,subject=pin(SUBJECT),reconstruction=pin(RECON),
        verdict='W01_DOCUMENTARY_SCOPE_AND_AUTHORITY_BOUNDARY_CONSISTENT_ENTRY_AUTHORITY_MISSING_NOT_ACCEPTED',
        findings=[],finding_count=0,criteria=rec['criteria'],counts=rec['counts'],
        documentary_clarifications=[
            dict(id='N01',subject='Entry authority versus preparation',disposition='W01 dossier preparation/review/publication is allowed documentary work. Actual W01 acceptance still requires genuine preexisting scope authority, competent R06 and separate R08. SD01 remains active; no W02 appointments or future bundle supplies sole forecast authority.'),
            dict(id='N02',subject='Logical scope versus effective freeze',disposition='Six paths and policy documents define a target only. Missing source/image/runtime/loader/caller/platform/clock/ledger facts remain unknown; W03/W04 must genuinely supply and qualify them under separate authority. Changes require impact and revalidation, not automatic proof transfer.'),
            dict(id='N03',subject='Exits and resources',disposition='Documentary separation and absent execution authority are consistent statements, while the three exit predicates remain unaccepted as a package. Caps, guards, phases and historical counts are requirements, not real heap/CPU/service/900 proof or accepted capacity.'),
            dict(id='N04',subject='Handoff and reviewer independence',disposition='Prelaunch/resource evidence remains separate from final E06/Q/root/claim/receipt. CE12 stays deferred. Same assistant preparation and methodological review do not satisfy genuine independent R06 or separate R08 acceptance.')],
        source_replay=dict(I225_candidate_and_preparation_review_reproduced=True,publication_mains_called=False,
            prior_Path_exists_restored=True,no_new_presence_projection=True),
        rejection_checks=rejection_checks(),current_effect=rec['current_effect'],
        provenance=dict(preparer_and_reviewer='Same Codex assistant/chat as I225',methodological_only=True,
            actor_independent=False,competent_R06_review=False,separate_R08_acceptance=False,external_contacts=False),
        next_step='Documentary W01 review complete. Positive package progress stays blocked at SD01 pending genuine entry scope/reviewer authority and accepted scope; no nomination/contact or operational work is initiated.',
        work_unit=dict(rollback_files=sorted(FILES),verification_command='python3 docs/validation/D5-I226-audit.py',expected_result=STATUS,
            runtime_harness='N/A: own documentary JSON/Git/hash/policy/authority comparisons only; no product/components imports/build/compile/tests/benchmarks, crypto/codec positives, probes, clock/ledger/claim/process or service execution.',
            over400_lines=True,reason='One documentary review with complete source pins, semantic comparisons, negative checks and preservation seal; overage declared. No PR requested.'),
        publication=dict(commit_and_push_requested=True,publication_not_scope_adoption_or_execution_authority=True))


def main():
    rec = reconstruct()
    assert rec == rd(RECON)
    review = build_review(rec)
    assert review == rd(REVIEW)
    prior = rd(PRIOR_SEAL)
    preserved = {**prior['preserved_published614'],**prior['artifacts'],PRIOR_SEAL:sha(PRIOR_SEAL)}
    assert len(preserved) == 619
    seal = rd(SEAL)
    assert seal['schema'] == 'd5.i226-integrity.v1' and seal['base_commit'] == BASE
    assert seal['preserved_published619'] == preserved and set(seal['artifacts']) == FILES-{SEAL}
    for pins in [preserved,seal['artifacts']]:
        for path,digest in pins.items():
            assert sha(path) == digest, path
    assert seal['source_only'] is True and seal['current_effect'] == rec['current_effect']
    changed = set(git('diff',BASE,'--name-only').splitlines()) | set(git('ls-files','--others','--exclude-standard').splitlines())
    assert changed == FILES, changed
    subprocess.check_call(['git','merge-base','--is-ancestor',BASE,'HEAD'],cwd=ROOT)
    if git('rev-parse','HEAD') != BASE:
        assert not git('status','--porcelain')
    print(json.dumps(dict(status=STATUS,increment='I226',historical_pins=927,preserved_published_files=619,
        new_files=5,criteria=16,findings=0,documentary_rejections=len(review['rejection_checks']),current_effect=rec['current_effect'],git_head=git('rev-parse','HEAD')),sort_keys=True))


if __name__ == '__main__':
    main()
