#!/usr/bin/env python3
"""I219 negative prelaunch closure dossier; no product/components, claims or gate release."""
import copy
import hashlib
import io
import json
import runpy
import subprocess
from contextlib import contextmanager
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
P = 'docs/validation/'
BASE = '378939565177c09822ec158eae1b2f0dad03dedb'
PLAN = P+'D5-I193-CALLER-IMAGE-CUSTODY-EVIDENCE-PLAN.json'
CHECK = P+'D5-I193-CUSTODY-EVIDENCE-CHECKLIST.json'
SPEC = P+'D5-I191-CALLER-IMAGE-CUSTODY-CONTRACT-CANDIDATE.json'
PACK = P+'D5-I191-CALLER-IMAGE-CUSTODY-SCHEMAS-CANDIDATE.json'
CE01 = P+'D5-I197-CE01-SCOPE-AND-DECISION-BOUNDARY-CANDIDATE-02.json'
CE02 = P+'D5-I201-CE02-ANCHOR-PROVENANCE-CANDIDATE-02.json'
CE07 = P+'D5-I193-CE07-RESOURCE-AND-COMPATIBILITY-JOIN-CANDIDATE.json'
CE10 = P+'D5-I193-CE10-BUNDLE-APPROVAL-AND-CURRENT-MAPPING-CANDIDATE.json'
BINDINGS = P+'D5-I177-FOUR-BINDINGS-EVIDENCE-PLAN.json'
DOS = P+'D5-I193-CE11-PRELAUNCH-EVIDENCE-CLOSURE-REVIEW-CANDIDATE.json'
PRIOR_AUDIT = P+'D5-I218-audit.py'
PRIOR_RECON = P+'D5-I218-I217-source-reconstruction.json'
PRIOR_REVIEW = P+'D5-I218-I217-documentary-review.json'
PRIOR_SEAL = P+'D5-I218-integrity.json'
PRIOR_DOC = 'docs/design/D5-I218-I217-CE10-REVIEW.md'
PRIOR_FILES = {PRIOR_AUDIT,PRIOR_RECON,PRIOR_REVIEW,PRIOR_SEAL,PRIOR_DOC}
AUDIT = P+'D5-I219-audit.py'
PREP = P+'D5-I219-preparation-review.json'
SEAL = P+'D5-I219-integrity.json'
DOC = 'docs/design/D5-I219-CE11-PRELAUNCH-EVIDENCE-CLOSURE.md'
FILES = {DOS,AUDIT,PREP,SEAL,DOC}
STATUS = 'PASS_STATIC_SOURCE_ONLY_PRELAUNCH_CHECKLIST_NOT_CLOSED'


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
    assert len(pins) == 892
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


@contextmanager
def predecessor_CE11_presence_as_of_base():
    """Historical documentary replay: only new CE11 Path.exists query is projected."""
    assert git('ls-tree','--name-only',BASE,'--',DOS) == ''
    target = ROOT/DOS
    original = Path.exists
    assert original(target)
    def historical_exists(path):
        return False if path == target else original(path)
    Path.exists = historical_exists
    try:
        yield
    finally:
        Path.exists = original
    assert target.exists()


def escape_pointer(name):
    return name.replace('~','~0').replace('/','~1')


def reference_sites(families,defs):
    """Typed reference templates only. Array * is a template, never an actual record index."""
    rows = []
    def walk(node,family,path,source_pointer,active):
        if '$ref' in node:
            assert node['$ref'].startswith('#/$defs/')
            target = node['$ref'][8:]
            if target == 'evidence_reference':
                rows.append(dict(family=family,path_template=path,schema_source=pin(PACK,source_pointer),
                    actual_record_id=None,actual_body_sha256=None,actual_complete_body=None,actual_body_bytes=None,
                    actual_provider=None,actual_custody=None,actual_author=None,actual_reviewer=None,
                    actual_rejection_or_acceptance=None,status='MISSING_ACTUAL_BODY_NOT_EVALUATED',accepted=False))
                return
            assert target not in active
            walk(defs[target],family,path,'/$defs/'+target,active|{target})
            return
        for name,child in node.get('properties',{}).items():
            walk(child,family,path+'/'+escape_pointer(name),source_pointer+'/properties/'+escape_pointer(name),active)
        if 'items' in node:
            walk(node['items'],family,path+'/*',source_pointer+'/items',active)
        for keyword in ['anyOf','oneOf']:
            for i,child in enumerate(node.get(keyword,[])):
                walk(child,family,path,source_pointer+'/'+keyword+'/'+str(i),active)
    for family in families:
        walk(defs[family],family,'','/$defs/'+family,{family})
    assert len(rows) == len({(r['family'],r['path_template'],r['schema_source']['json_pointer']) for r in rows})
    return rows


def missing_gate():
    return dict(actual_body_or_proof_sha256=None,actual_provider=None,actual_custody=None,
        actual_scope_binding=None,actual_competent_reviewer=None,actual_separate_acceptor=None,
        actual_disposition=None,accepted=False,current_execution_authorized=False)


def build_candidate():
    plan = rd(PLAN)
    step = plan['steps'][10]
    check = rd(CHECK)
    defs = rd(PACK)['$defs']
    ce10 = rd(CE10)
    ce1 = rd(CE01)
    paths = {PLAN,CHECK,SPEC,PACK,CE01,CE02,CE07,CE10,BINDINGS,PRIOR_RECON,PRIOR_REVIEW,
        P+'D5-I132-E01-E05-evidence-plan.json'}
    paths.update(v['path'] for v in plan['bindings'].values())
    dependencies = []
    review_names = ['D5-I198-I197-documentary-review.json','D5-I202-I201-documentary-review.json',
        'D5-I204-I203-documentary-review.json','D5-I206-I205-documentary-review.json',
        'D5-I208-I207-documentary-review.json','D5-I210-I209-documentary-review.json',
        'D5-I212-I211-documentary-review.json','D5-I214-I213-documentary-review.json',
        'D5-I216-I215-documentary-review.json','D5-I218-I217-documentary-review.json']
    for i,review in enumerate(review_names):
        path = CE01 if i == 0 else CE02 if i == 1 else plan['steps'][i]['candidate_dossier_path']
        paths.update([path,P+review])
        dependencies.append(dict(step='CE%02d'%(i+1),latest_candidate=pin(path),latest_documentary_review=pin(P+review),
            historical_planned_path=plan['steps'][i]['candidate_dossier_path'],documentary_baseline_reviewed=True,
            competent_acceptance=False,actual_dependency_satisfied=False))
    families = []
    for i,row in enumerate(check['family_gates']):
        families.append(dict(id=row['id'],family=row['family'],checklist_source=pin(CHECK,'/family_gates/'+str(i)),
            source_gate=row,scope='DEFERRED_CE12_NOT_PRELAUNCH_DEPENDENCY' if row['conditional_after_launch'] else 'PRELAUNCH_CE11',
            current_status='DEFERRED_NOT_AUTHORIZED' if row['conditional_after_launch'] else 'MISSING_NOT_ACCEPTED',
            **missing_gate()))
    rules = [dict(id=row['rule_id'],checklist_source=pin(CHECK,'/contract_rule_gates/'+str(i)),source_gate=row,
        normative_rule=rd(SPEC)['rules'][i],current_status='MISSING_NOT_ACCEPTED',**missing_gate())
        for i,row in enumerate(check['contract_rule_gates'])]
    global_rows = [dict(id=row['id'],checklist_source=pin(CHECK,'/global_gates/'+str(i)),source_gate=row,
        current_status='COMPETENT_ACCEPTANCE_PENDING',documentary_policy_preserved=True,**missing_gate())
        for i,row in enumerate(check['global_gates'])]
    review_topics = ['Canonical humans/aliases/competence/appointments/preparers and S01/key/custody separation',
        'Independent anchors/epoch/purpose/key provenance and actual current snapshot',
        'Exact six-source image/runtime/build/loader/native/crypto closure and implementation of selected policies',
        'Caller constructor/protection domain/platform guarantees/clock/global ledger provenance',
        'Genuine complete prior BASIS/index/atomicity and E01-E05 resource/CPU/IO/phase/service/900 proofs',
        'Exact C shared types/actual values/digest/constants/clock/contained validity and custody-only acceptance',
        'Same-core three-role approvals and one global current epoch/C mapping with genuine verification records',
        'All referenced bodies/authors, actual nested caps and conditional encoding/size assumptions/source-Reader-output-guard impact']
    boundaries = ce1['step_obligation_boundary']
    return dict(schema='d5.i219-ce11-prelaunch-evidence-closure-review-candidate.v1',increment='I219',date='2026-11-17',
        timezone='Europe/Madrid',base_commit=BASE,proposal_id=ce10['proposal_id'],profile_id=ce10['profile_id'],step='CE11',
        kind='NEGATIVE_PRELAUNCH_CHECKLIST_AND_DOCUMENTARY_HANDOFF_NOT_GATE_RELEASE_OR_POSITIVE_RECORD',
        status='CE11_DOCUMENTARY_NEGATIVE_CLOSURE_PREPARED_THIRTY_PRELAUNCH_GATES_PENDING_NOT_ACCEPTED_NOT_ADMITTED',
        input_pins=historical_pins(),plan_binding=pin(PLAN,'/steps/10'),checklist_binding=pin(CHECK),
        required_evidence=step['required_evidence'],planned_acceptance_checks=step['acceptance_checks'],
        contract_rules=step['contract_rules'],authorization_boundary=step['authorization_boundary'],
        needs_fresh_snapshot_at_launch=step['needs_fresh_snapshot_at_launch'],record_families=step['record_families'],
        dependency_gates=dependencies,documentary_inventory=[pin(p) for p in sorted(paths)],
        producer=dict(identity='Same Codex assistant/chat as earlier candidates',documentary_preparer_only=True,
            actor_independent=False,organizationally_independent=False,competent_acceptance=False,external_contacts_made=False),
        role_scope_matrix=[{**{k:v for k,v in row.items() if k != 'CE01_responsibilities'},
            'CE11_responsibility':'Competent independent prelaunch evidence disposition and separate R08 acceptance; documentary preparation supplies neither.'}
            for row in ce1['role_scope_matrix'] if row['id'] in step['provenance_and_role']['primary_review_roles']],
        family_gate_dispositions=families,rule_gate_dispositions=rules,global_gate_dispositions=global_rows,
        checklist_summary=dict(original_total_gates=31,prelaunch_family_gates=7,prelaunch_rule_gates=16,prelaunch_global_gates=7,
            current_prelaunch_gates_pending=30,current_prelaunch_gates_accepted=0,deferred_CE12_family_gates=1,
            actual_checklist_closed=False,negative_disposition_matrix_prepared=True,
            document_presence_or_schema_signature_cap_makes_proof_true=False),
        proof_reference_disposition=dict(typed_reference_templates=reference_sites(check['prelaunch_families'],defs),
            template_paths_are_not_actual_instance_references=True,
            current_documentary_sources=[pin(p) for p in sorted(paths)],
            provided_documentary_sources_are_not_accepted_actual_proofs=True,
            provided_actual_proof_bodies=[],rejected_actual_proof_bodies=[],actual_proofs_evaluated=0,
            absence_of_rejected_bodies_means_not_evaluated_not_accepted=True,
            actual_full_reference_body_inventory=None,actual_reference_completeness_verified=False,
            every_actual_missing_provided_rejected_reference_requires_exact_bytes_scope_author_custody_review=True,
            static_schema_templates_are_not_complete_actual_proof_inventory=True),
        E01_E05_missing_obligations=copy.deepcopy(rd(CE07)['E01_E05_join']),
        additional_proof_obligations=[dict(id='AP%02d'%(i+1),topic=topic,actual_complete_body_inventory=None,
            actual_current_bytes_source_runtime_scope_binding=None,actual_provider=None,actual_author_scope=None,
            actual_primary_review=None,actual_separate_acceptance=None,status='MISSING_NOT_EVALUATED',accepted=False)
            for i,topic in enumerate(review_topics)],
        competent_separate_review=dict(primary_role='R06',separate_role='R08',actual_primary_person=None,
            actual_separate_person=None,actual_appointments_or_competence=None,actual_review_records=None,
            current_preparer_is_not_independent_reviewer=True,actual_identity_anchor_image_backend_C_mapping_or_proof_accepted=False),
        inherited_source_and_guard_impact=dict(source=pin(CE10,'/inherited_scope_boundaries'),
            exact_effective_source_runtime_image_and_proof_scope_required=True,
            current_actual_source_runtime_image_or_provider_binding=None,
            actual_complete_source_Reader_output_phase_and_guard_impact_review=None,
            CP03_counts_indices_signatures_caps_or_documentary_confirmations_not_resource_proof=True,
            both_process_Reader_ledgers_all_per_attempt_native_crypto_IO_and_global_join_required=True,
            actual_heap_CPU_service_clock_phase_or900_proof=None,
            conditional_size_reference=ce10['conditional_size_reference'],
            actual_encoding_nested_caps_bundle_fit_or_guard_compatibility_verified=False,
            no_new_C_Q_file_pipe_helper_input_output_receipt_channel=True),
        prelaunch_handoff=dict(source=pin(CE01,'/step_obligation_boundary/CE11'),
            handoff_requirement_id='X09-PRELAUNCH-HANDOFF',
            required_actual_custody_step_ids=step['depends_on'],
            pending_final_route_obligations=plan['closure_boundaries']['external_prerequisites_for_receipt'],
            actual_final_route_completion_required=False,CE12_receipt_claim_or_spawn_required=False,
            handoff_is_not_execution_gate_release=True,handoff_satisfies_actual_final_prerequisites=False,
            current_run_command=None,execution_or_component_qualification_authorized=False,
            actual_handoff_accepted=False,actual_custody_prelaunch_facts_closed=False),
        pending_I177_final_bindings=[dict(id=row['id'],source=pin(BINDINGS,'/four_binding_plan/'+str(i)),path=row['path'],
            historical_producer_step=row['producer_step'],actual_artifact_sha256=None,current_path_exists=(ROOT/row['path']).exists(),
            status='DEFERRED_MISSING_NOT_EXECUTED_NOT_AUTHORIZED',accepted=False)
            for i,row in enumerate(rd(BINDINGS)['four_binding_plan'])],
        CE12_boundary=dict(source=pin(CE01,'/step_obligation_boundary/CE12'),
            external_prerequisites=plan['closure_boundaries']['external_prerequisites_for_receipt'],
            preclaim_external_prerequisites=boundaries['CE12']['preclaim_external_prerequisites'],
            receipt_only_external_prerequisites=boundaries['CE12']['receipt_only_external_prerequisites'],
            preclaim_prerequisites_must_be_genuinely_satisfied_before_claim=True,
            all_external_prerequisites_must_be_genuinely_satisfied_before_receipt=True,
            claim_is_not_its_own_precondition=True,actual_claim_receipt_or_spawn_required_for_CE11=False,
            actual_CE12_currently_authorized=False,actual_CE12_prerequisites_satisfied=False,
            receipt_remains_private_not_capture_output_or_new_wire_field=True,
            uncertain_partial_expired_failed_claim_no_free_retry_or_prior_invocation_reuse=True),
        freeze_and_invalidation_policy=dict(source=pin(PLAN,'/freeze_and_refresh'),inherited_policy=plan['freeze_and_refresh'],
            anchor_key_change_revisit_CE02_then_affected_CE03_to_CE10_and_CE11=True,
            any_new_contributor_body_scope_epoch_or_policy_requires_fresh_dependent_review=True,
            no_automatic_prior_hash_proof_approval_mapping_or_acceptance_transfer=True,
            actual_rebind_snapshot_refresh_or_registry_configuration_changed=False),
        inherited_scope_boundaries=ce10['inherited_scope_boundaries'],preserved_negative_gates=ce10['preserved_negative_gates'],
        permission_boundary={**ce10['permission_boundary'],'authorized_documentary_actions':['READ_SOURCE_JSON_GIT_HASHES',
            'PREPARE_CE11_NEGATIVE_CHECKLIST_AND_DEFERRED_HANDOFF_DOSSIER','RUN_DOCUMENTARY_AUDIT','COMMIT_AND_PUSH_THIS_UNIT']},
        historical_replay_policy=dict(CE11_absent_at_BASE=True,exact_Path_exists_query_only_during_predecessor_replay=True,
            restoration_after_success_and_exception_required=True,prior_publication_mains_run=False,CE12_dossier_absent=True),
        current_effect=dict(CE11_documentary_prepared=True,CE11_accepted=False,actual_dependencies_satisfied=False,
            actual_prelaunch_checklist_closed=False,actual_prelaunch_evidence_accepted=0,actual_handoff_accepted=False,
            independent_acceptance=False,resource_obligations_closed=0,actual_claim_spawn_or_receipt_created=False,
            actual_final_E06_payload_Q_root_or_admission_created=False,SOURCE_CAPACITY_VERIFIED_issued=False,
            product_or_components_executed=False,quotas_changed=False,reserves_changed=False,rebind_applied=False,
            execution_authorized=False,proposal_enabled=False,D5_closed=False,IR03='NOT_READY'),
        decision=plan['decision'],E06=plan['E06'])


def validate(d):
    assert d['prelaunch_handoff']['CE12_receipt_claim_or_spawn_required'] is False, 'receipt_as_CE11_precondition'
    assert d['prelaunch_handoff']['actual_final_route_completion_required'] is False, 'final_route_as_CE11_precondition'
    assert d['CE12_boundary']['claim_is_not_its_own_precondition'] is True, 'claim_requires_itself'
    assert d['checklist_summary']['actual_checklist_closed'] is False, 'premature_checklist_closure'
    assert d['proof_reference_disposition']['provided_documentary_sources_are_not_accepted_actual_proofs'] is True, 'documents_as_accepted_proofs'
    assert d['checklist_summary']['document_presence_or_schema_signature_cap_makes_proof_true'] is False, 'schema_signature_cap_as_truth'
    assert d['competent_separate_review']['actual_identity_anchor_image_backend_C_mapping_or_proof_accepted'] is False, 'missing_facts_accepted'
    assert d['prelaunch_handoff']['current_run_command'] is None, 'current_run_command'
    assert d['current_effect']['SOURCE_CAPACITY_VERIFIED_issued'] is False, 'capacity_certificate_promoted'
    assert d['current_effect']['D5_closed'] is False, 'D5_closed_by_document'
    assert d['current_effect']['quotas_changed'] is False, 'quota_change'
    assert d['current_effect']['execution_authorized'] is False, 'execution_gate_release'
    assert len(d['family_gate_dispositions']) == 8 and len(d['rule_gate_dispositions']) == 16 and len(d['global_gate_dispositions']) == 7
    assert sum(r['scope'] == 'PRELAUNCH_CE11' for r in d['family_gate_dispositions']) == 7
    for rows in [d['family_gate_dispositions'],d['rule_gate_dispositions'],d['global_gate_dispositions']]:
        for row in rows:
            for key,value in missing_gate().items():
                assert row[key] == value and type(row[key]) is type(value), (row['id'],key)
    assert d['prelaunch_handoff']['required_actual_custody_step_ids'] == rd(PLAN)['steps'][10]['depends_on']
    assert [r['step'] for r in d['dependency_gates']] == rd(PLAN)['steps'][10]['depends_on']
    assert all(not (ROOT/r['path']).exists() for r in d['pending_I177_final_bindings'])
    plan = rd(PLAN)
    assert all((ROOT/s['candidate_dossier_path']).exists() for s in plan['steps'][:11])
    assert not (ROOT/plan['steps'][11]['candidate_dossier_path']).exists()
    assert d == build_candidate(), 'Dossier differs from source reconstruction'


def rejection_checks(d):
    cases = [
        ('receipt_as_CE11_precondition',('prelaunch_handoff','CE12_receipt_claim_or_spawn_required'),True),
        ('final_route_as_CE11_precondition',('prelaunch_handoff','actual_final_route_completion_required'),True),
        ('claim_requires_itself',('CE12_boundary','claim_is_not_its_own_precondition'),False),
        ('premature_checklist_closure',('checklist_summary','actual_checklist_closed'),True),
        ('documents_as_accepted_proofs',('proof_reference_disposition','provided_documentary_sources_are_not_accepted_actual_proofs'),False),
        ('schema_signature_cap_as_truth',('checklist_summary','document_presence_or_schema_signature_cap_makes_proof_true'),True),
        ('missing_facts_accepted',('competent_separate_review','actual_identity_anchor_image_backend_C_mapping_or_proof_accepted'),True),
        ('current_run_command',('prelaunch_handoff','current_run_command'),'UNAUTHORIZED_COMMAND_PLACEHOLDER'),
        ('capacity_certificate_promoted',('current_effect','SOURCE_CAPACITY_VERIFIED_issued'),True),
        ('D5_closed_by_document',('current_effect','D5_closed'),True),
        ('quota_change',('current_effect','quotas_changed'),True),
        ('execution_gate_release',('current_effect','execution_authorized'),True)]
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
    d = rd(DOS)
    verify_blobs(d['input_pins'])
    validate(d)
    previous = runpy.run_path(str(ROOT/PRIOR_AUDIT))
    original = Path.exists
    with predecessor_CE11_presence_as_of_base():
        rec = previous['reconstruct']()
        assert rec == rd(PRIOR_RECON) and previous['build_review'](rec) == rd(PRIOR_REVIEW)
    assert Path.exists is original and (ROOT/DOS).exists()
    class DocumentaryProbe(Exception):
        pass
    try:
        with predecessor_CE11_presence_as_of_base():
            assert not (ROOT/DOS).exists()
            raise DocumentaryProbe()
    except DocumentaryProbe:
        pass
    assert Path.exists is original and (ROOT/DOS).exists()
    plan = rd(PLAN)
    graph = {s['id']:s['depends_on'] for s in plan['steps']}
    closure = previous['ancestors'](graph)
    assert closure['CE11'] == {'CE%02d'%i for i in range(1,11)} and 'CE12' not in closure['CE11']
    assert d['CE12_boundary']['preclaim_external_prerequisites'] == plan['closure_boundaries']['external_prerequisites_for_receipt'][:4]
    assert d['CE12_boundary']['receipt_only_external_prerequisites'] == plan['closure_boundaries']['external_prerequisites_for_receipt'][4:]
    assert [r['id'] for r in d['role_scope_matrix']] == ['R06','R08']
    for row in d['role_scope_matrix']:
        assert row['assigned_person'] is None and row['accepted_appointment'] is False and row['current_actions_authorized'] == []
    assert d['E01_E05_missing_obligations'] == rd(CE07)['E01_E05_join'] and len(d['E01_E05_missing_obligations']) == 5
    for key,value in d['current_effect'].items():
        if key == 'CE11_documentary_prepared':
            assert value is True
        elif key == 'IR03':
            assert value == 'NOT_READY'
        elif key in ['actual_prelaunch_evidence_accepted','resource_obligations_closed']:
            assert value == 0 and type(value) is int
        else:
            assert value is False, key
    check = rd(CHECK)
    assert check['prelaunch_families'] == [r['family'] for r in d['family_gate_dispositions'] if r['scope'] == 'PRELAUNCH_CE11']
    assert check['deferred_families'] == ['launch_receipt']
    for i,row in enumerate(d['family_gate_dispositions']):
        original_gate = check['family_gates'][i]
        assert row['source_gate'] == original_gate
        assert row['family'] == original_gate['family']
        assert original_gate['required_top_level_fields'] == rd(PACK)['$defs'][row['family']]['required']
        assert original_gate['body_cap_bytes'] == rd(SPEC)['record_caps_bytes'][row['family']]
        assert (row['scope'] == 'DEFERRED_CE12_NOT_PRELAUNCH_DEPENDENCY') == (row['family'] == 'launch_receipt')
    for i,row in enumerate(d['rule_gate_dispositions']):
        assert row['source_gate'] == check['contract_rule_gates'][i]
        assert row['normative_rule'] == rd(SPEC)['rules'][i]
        assert row['id'] == row['normative_rule']['id'] == 'K%02d'%(i+1)
    for i,row in enumerate(d['global_gate_dispositions']):
        assert row['source_gate'] == check['global_gates'][i] and row['id'] == 'G%02d'%(i+1)
    assert d['record_families'] == plan['steps'][10]['record_families'] == []
    assert d['contract_rules'] == plan['steps'][10]['contract_rules'] == ['K%02d'%i for i in range(1,17)]
    assert d['decision'] == plan['decision'] and d['E06'] == plan['E06']
    proofs = d['proof_reference_disposition']
    assert proofs['provided_actual_proof_bodies'] == proofs['rejected_actual_proof_bodies'] == []
    assert proofs['actual_proofs_evaluated'] == 0 and proofs['actual_full_reference_body_inventory'] is None
    assert proofs['actual_reference_completeness_verified'] is False
    assert d['prelaunch_handoff']['pending_final_route_obligations'] == plan['closure_boundaries']['external_prerequisites_for_receipt']
    assert d['prelaunch_handoff']['handoff_satisfies_actual_final_prerequisites'] is False
    assert d['CE12_boundary']['actual_claim_receipt_or_spawn_required_for_CE11'] is False
    sites = d['proof_reference_disposition']['typed_reference_templates']
    assert len(sites) == 69
    for row in sites:
        assert previous['fragment'](row['schema_source']) == {'$ref':'#/$defs/evidence_reference'}
        assert all(v is None for k,v in row.items() if k.startswith('actual_'))
        assert row['accepted'] is False
    return dict(schema='d5.i219-preparation-review.v1',increment='I219',date='2026-11-17',base_commit=BASE,
        status=STATUS,candidate=pin(DOS),plan=pin(PLAN,'/steps/10'),
        counts=dict(input_pins=892,dependency_steps=10,prelaunch_family_gates=7,rule_gates=16,global_gates=7,
            prelaunch_gates_pending=30,prelaunch_gates_accepted=0,deferred_CE12_receipt_gate=1,
            typed_evidence_reference_templates=len(sites),additional_review_topics=8,unassigned_role_slots=2,
            pending_I177_final_bindings=4,later_dossiers_absent=1,resource_obligations_closed=0),
        provenance=d['producer'],source_reconstruction=dict(prior_I218_reconstruction_and_review_reproduced=True,
            prior_publication_mains_run=False,exact_CE11_historical_absence_guard=True,guard_restored_success_and_exception=True,
            no_receipt_claim_spawn_or_final_route_completion_required_as_CE11_dependency=True,
            actual_CE01_CE10_custody_facts_still_required=True,CE12_preclaim_vs_receipt_only_split_preserved=True,
            static_reference_templates_not_actual_proof_inventory=True),
        rejection_checks=rejection_checks(d),current_effect=d['current_effect'],decision=d['decision'],E06=d['E06'],
        limitations=['Negative closure disposition only: all30 prelaunch gates and ten competent prerequisite acceptances remain pending; no actual checklist closure or accepted handoff.',
            'Static typed reference templates plus provided documentary sources are not actual proof bodies, complete instance references, author/provenance closure or independent review. No actual proof evaluated or rejected as invalid.',
            'Same assistant is not competent independent R06 review or separate R08 acceptance. No product/component execution, claim/spawn/receipt, final route completion, authority issuance or gate release.'],
        work_unit=dict(rollback_files=sorted(FILES),verification_command='python3 docs/validation/D5-I219-audit.py',expected_result=STATUS,
            runtime_harness='N/A: documentary JSON/Git/hash/schema-reference/checklist/DAG reconstruction only; no product/components, crypto/codec, platform/service or process execution.',
            over400_lines=True,reason='One negative prelaunch closure/handoff dossier with all31 original gate dispositions and proof-reference templates; overage reported. No PR requested.'),
        publication=dict(commit_and_push_requested=True,publication_is_not_prelaunch_acceptance_or_execution_authority=True))


def main():
    review = build_review()
    assert rd(PREP) == review
    prior = rd(PRIOR_SEAL)
    preserved = {**prior['preserved_published579'],**prior['artifacts'],PRIOR_SEAL:sha(PRIOR_SEAL)}
    assert len(preserved) == 584
    seal = rd(SEAL)
    assert seal['schema'] == 'd5.i219-integrity.v1' and seal['base_commit'] == BASE
    assert seal['preserved_published584'] == preserved and set(seal['artifacts']) == FILES-{SEAL}
    for pins in [preserved,seal['artifacts']]:
        for p,h in pins.items():
            assert sha(p) == h, p
    assert seal['source_only'] and seal['current_effect'] == review['current_effect']
    changed = set(git('diff',BASE,'--name-only').splitlines()) | set(git('ls-files','--others','--exclude-standard').splitlines())
    assert changed == FILES, changed
    subprocess.check_call(['git','merge-base','--is-ancestor',BASE,'HEAD'],cwd=ROOT)
    if git('rev-parse','HEAD') != BASE:
        assert not git('status','--porcelain')
    print(json.dumps(dict(status=STATUS,increment='I219',historical_pins=892,preserved_published_files=584,
        new_files=5,documentary_rejections=12,counts=review['counts'],current_effect=review['current_effect'],git_head=git('rev-parse','HEAD')),sort_keys=True))


if __name__ == '__main__':
    main()
