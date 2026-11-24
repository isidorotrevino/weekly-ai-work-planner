#!/usr/bin/env python3
"""I220 documentary CE11 review; no product/components, runtime gate release or actual claim."""
import hashlib
import io
import json
import runpy
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
P = 'docs/validation/'
BASE = 'bcbde60f040c5baf99240491540df74d1b2501cd'
DOS = P+'D5-I193-CE11-PRELAUNCH-EVIDENCE-CLOSURE-REVIEW-CANDIDATE.json'
PLAN = P+'D5-I193-CALLER-IMAGE-CUSTODY-EVIDENCE-PLAN.json'
CHECK = P+'D5-I193-CUSTODY-EVIDENCE-CHECKLIST.json'
SPEC = P+'D5-I191-CALLER-IMAGE-CUSTODY-CONTRACT-CANDIDATE.json'
PACK = P+'D5-I191-CALLER-IMAGE-CUSTODY-SCHEMAS-CANDIDATE.json'
CE01 = P+'D5-I197-CE01-SCOPE-AND-DECISION-BOUNDARY-CANDIDATE-02.json'
CE02 = P+'D5-I201-CE02-ANCHOR-PROVENANCE-CANDIDATE-02.json'
CE07 = P+'D5-I193-CE07-RESOURCE-AND-COMPATIBILITY-JOIN-CANDIDATE.json'
CE10 = P+'D5-I193-CE10-BUNDLE-APPROVAL-AND-CURRENT-MAPPING-CANDIDATE.json'
BINDINGS = P+'D5-I177-FOUR-BINDINGS-EVIDENCE-PLAN.json'
PRIOR_AUDIT = P+'D5-I219-audit.py'
PRIOR_PREP = P+'D5-I219-preparation-review.json'
PRIOR_SEAL = P+'D5-I219-integrity.json'
PRIOR_DOC = 'docs/design/D5-I219-CE11-PRELAUNCH-EVIDENCE-CLOSURE.md'
PRIOR_FILES = {DOS,PRIOR_AUDIT,PRIOR_PREP,PRIOR_SEAL,PRIOR_DOC}
RECON = P+'D5-I220-I219-source-reconstruction.json'
REVIEW = P+'D5-I220-I219-documentary-review.json'
AUDIT = P+'D5-I220-audit.py'
SEAL = P+'D5-I220-integrity.json'
DOC = 'docs/design/D5-I220-I219-CE11-REVIEW.md'
FILES = {RECON,REVIEW,AUDIT,SEAL,DOC}
STATUS = 'PASS_STATIC_SOURCE_ONLY_PRELAUNCH_CHECKLIST_NOT_CLOSED'
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


def ancestors(graph):
    done = {}
    active = set()
    def visit(n):
        assert n in graph and n not in active, n
        if n in done:
            return done[n]
        active.add(n)
        found = set()
        for parent in graph[n]:
            found.add(parent)
            found.update(visit(parent))
        active.remove(n)
        assert n not in found
        done[n] = found
        return found
    for n in graph:
        visit(n)
    return done


def esc(token):
    return token.replace('~','~0').replace('/','~1')


def declared_reference_sites(families,defs):
    """Fresh worklist traversal of schema declaration sites, not actual proof bodies."""
    result = set()
    todo = [(family,'','/$defs/'+family,defs[family],frozenset({family})) for family in families]
    while todo:
        family,path,pointer,node,active = todo.pop()
        if '$ref' in node:
            assert node['$ref'].startswith('#/$defs/')
            name = node['$ref'][8:]
            if name == 'evidence_reference':
                result.add((family,path,pointer))
            else:
                assert name not in active
                todo.append((family,path,'/$defs/'+name,defs[name],active|{name}))
            continue
        for key,child in node.get('properties',{}).items():
            todo.append((family,path+'/'+esc(key),pointer+'/properties/'+esc(key),child,active))
        if 'items' in node:
            todo.append((family,path+'/*',pointer+'/items',node['items'],active))
        for keyword in ['oneOf','anyOf']:
            for i,child in enumerate(node.get(keyword,[])):
                todo.append((family,path,pointer+'/'+keyword+'/'+str(i),child,active))
    return result


def assert_missing_disposition(row):
    for key in ['actual_body_or_proof_sha256','actual_provider','actual_custody','actual_scope_binding',
                'actual_competent_reviewer','actual_separate_acceptor','actual_disposition']:
        assert row[key] is None, (row['id'],key)
    assert row['accepted'] is False and row['current_execution_authorized'] is False


def reconstruct():
    d = rd(DOS)
    plan = rd(PLAN)
    step = plan['steps'][10]
    check = rd(CHECK)
    spec = rd(SPEC)
    defs = rd(PACK)['$defs']
    pins = {**d['input_pins'],**{p:sha(p) for p in sorted(PRIOR_FILES)}}
    assert len(pins) == 897
    verify_blobs(pins)
    assert step['id'] == d['step'] == 'CE11' and step['candidate_dossier_path'] == DOS
    assert d['plan_binding'] == pin(PLAN,'/steps/10') and d['checklist_binding'] == pin(CHECK)
    for a,b in [('required_evidence','required_evidence'),('planned_acceptance_checks','acceptance_checks'),
                ('contract_rules','contract_rules'),('authorization_boundary','authorization_boundary'),
                ('needs_fresh_snapshot_at_launch','needs_fresh_snapshot_at_launch'),('record_families','record_families')]:
        assert d[a] == step[b]
    assert len(d['required_evidence']) == len(d['planned_acceptance_checks']) == 3 and step['record_families'] == []
    assert len(d['documentary_inventory']) == len({s['path'] for s in d['documentary_inventory']}) == 33
    for source in d['documentary_inventory']:
        assert source['sha256'] == pins[source['path']] == sha(source['path'])
    assert [r['step'] for r in d['dependency_gates']] == step['depends_on'] == ['CE%02d'%i for i in range(1,11)]
    for i,row in enumerate(d['dependency_gates']):
        path = CE01 if i == 0 else CE02 if i == 1 else plan['steps'][i]['candidate_dossier_path']
        assert row['latest_candidate'] == pin(path)
        assert row['historical_planned_path'] == plan['steps'][i]['candidate_dossier_path']
        assert fragment(row['latest_documentary_review'])['current_effect']['independent_acceptance'] is False
        assert row['documentary_baseline_reviewed'] is True
        assert row['competent_acceptance'] is False and row['actual_dependency_satisfied'] is False
    assert len(d['family_gate_dispositions']) == len(check['family_gates']) == 8
    prelaunch = []
    deferred = []
    for i,(row,source) in enumerate(zip(d['family_gate_dispositions'],check['family_gates'])):
        assert fragment(row['checklist_source']) == row['source_gate'] == source
        assert row['id'] == source['id'] and row['family'] == source['family']
        assert source['required_top_level_fields'] == defs[row['family']]['required']
        assert source['body_cap_bytes'] == spec['record_caps_bytes'][row['family']]
        assert source['accepted'] is False and source['actual_body_sha256'] is None
        if source['conditional_after_launch']:
            assert row['family'] == 'launch_receipt' and source['final_record_freeze_step'] == 'CE12'
            assert row['scope'] == 'DEFERRED_CE12_NOT_PRELAUNCH_DEPENDENCY' and row['current_status'] == 'DEFERRED_NOT_AUTHORIZED'
            deferred.append(row['id'])
        else:
            assert row['scope'] == 'PRELAUNCH_CE11' and row['current_status'] == 'MISSING_NOT_ACCEPTED'
            prelaunch.append(row['id'])
        assert_missing_disposition(row)
    assert check['prelaunch_families'] == [r['family'] for r in d['family_gate_dispositions'] if r['scope']=='PRELAUNCH_CE11']
    assert check['deferred_families'] == ['launch_receipt'] and len(prelaunch) == 7 and len(deferred) == 1
    assert len(d['rule_gate_dispositions']) == len(check['contract_rule_gates']) == 16
    rule_rows = []
    for i,(row,source) in enumerate(zip(d['rule_gate_dispositions'],check['contract_rule_gates'])):
        assert fragment(row['checklist_source']) == row['source_gate'] == source
        assert row['id'] == source['rule_id'] == row['normative_rule']['id'] == 'K%02d'%(i+1)
        assert row['normative_rule'] == spec['rules'][i]
        assert row['current_status'] == 'MISSING_NOT_ACCEPTED'
        assert_missing_disposition(row)
        rule_rows.append(dict(id=row['id'],source=pin(SPEC,'/rules/'+str(i)),
            disposition=pin(DOS,'/rule_gate_dispositions/'+str(i)),actual_competent_acceptance=False))
    assert d['contract_rules'] == [r['id'] for r in rule_rows]
    assert len(d['global_gate_dispositions']) == len(check['global_gates']) == 7
    for i,(row,source) in enumerate(zip(d['global_gate_dispositions'],check['global_gates'])):
        assert fragment(row['checklist_source']) == row['source_gate'] == source
        assert row['id'] == source['id'] == 'G%02d'%(i+1)
        assert row['current_status'] == 'COMPETENT_ACCEPTANCE_PENDING' and row['documentary_policy_preserved'] is True
        assert_missing_disposition(row)
    summary = d['checklist_summary']
    assert summary['original_total_gates'] == len(check['family_gates'])+len(check['contract_rule_gates'])+len(check['global_gates']) == 31
    assert summary['prelaunch_family_gates'] == 7 and summary['prelaunch_rule_gates'] == 16 and summary['prelaunch_global_gates'] == 7
    assert summary['current_prelaunch_gates_pending'] == len(prelaunch)+16+7 == 30
    assert summary['current_prelaunch_gates_accepted'] == 0 and summary['deferred_CE12_family_gates'] == 1
    assert summary['actual_checklist_closed'] is False and summary['negative_disposition_matrix_prepared'] is True
    assert summary['document_presence_or_schema_signature_cap_makes_proof_true'] is False
    proofs = d['proof_reference_disposition']
    expected_sites = declared_reference_sites(check['prelaunch_families'],defs)
    actual_sites = {(r['family'],r['path_template'],r['schema_source']['json_pointer']) for r in proofs['typed_reference_templates']}
    assert actual_sites == expected_sites and len(actual_sites) == len(proofs['typed_reference_templates']) == 69
    site_counts = {family:sum(x[0] == family for x in expected_sites) for family in check['prelaunch_families']}
    assert list(site_counts.values()) == [1,3,10,2,14,5,34]
    for row in proofs['typed_reference_templates']:
        assert fragment(row['schema_source']) == {'$ref':'#/$defs/evidence_reference'}
        assert all(value is None for key,value in row.items() if key.startswith('actual_'))
        assert row['status'] == 'MISSING_ACTUAL_BODY_NOT_EVALUATED' and row['accepted'] is False
    assert proofs['current_documentary_sources'] == d['documentary_inventory']
    assert proofs['provided_actual_proof_bodies'] == proofs['rejected_actual_proof_bodies'] == [] and proofs['actual_proofs_evaluated'] == 0
    assert proofs['actual_full_reference_body_inventory'] is None and proofs['actual_reference_completeness_verified'] is False
    for key in ['template_paths_are_not_actual_instance_references','provided_documentary_sources_are_not_accepted_actual_proofs',
                'absence_of_rejected_bodies_means_not_evaluated_not_accepted',
                'every_actual_missing_provided_rejected_reference_requires_exact_bytes_scope_author_custody_review',
                'static_schema_templates_are_not_complete_actual_proof_inventory']:
        assert proofs[key] is True
    assert d['E01_E05_missing_obligations'] == rd(CE07)['E01_E05_join'] and len(d['E01_E05_missing_obligations']) == 5
    for row in d['E01_E05_missing_obligations']:
        assert row['closed'] is False and row['accepted'] is False
    assert len(d['additional_proof_obligations']) == 8
    for row in d['additional_proof_obligations']:
        assert all(v is None for k,v in row.items() if k.startswith('actual_'))
        assert row['status'] == 'MISSING_NOT_EVALUATED' and row['accepted'] is False
    review = d['competent_separate_review']
    assert review['primary_role'] == 'R06' and review['separate_role'] == 'R08'
    assert all(review[k] is None for k in ['actual_primary_person','actual_separate_person','actual_appointments_or_competence','actual_review_records'])
    assert review['current_preparer_is_not_independent_reviewer'] and not review['actual_identity_anchor_image_backend_C_mapping_or_proof_accepted']
    assert [r['id'] for r in d['role_scope_matrix']] == step['provenance_and_role']['primary_review_roles'] == ['R06','R08']
    for row in d['role_scope_matrix']:
        assert row['assigned_person'] is None and row['accepted_appointment'] is False and row['current_actions_authorized'] == []
    impact = d['inherited_source_and_guard_impact']
    assert fragment(impact['source']) == rd(CE10)['inherited_scope_boundaries']
    assert impact['conditional_size_reference'] == rd(CE10)['conditional_size_reference']
    assert all(v is None for k,v in impact.items() if k.startswith('actual_') and k != 'actual_encoding_nested_caps_bundle_fit_or_guard_compatibility_verified')
    assert impact['actual_encoding_nested_caps_bundle_fit_or_guard_compatibility_verified'] is False
    for key in ['exact_effective_source_runtime_image_and_proof_scope_required',
                'CP03_counts_indices_signatures_caps_or_documentary_confirmations_not_resource_proof',
                'both_process_Reader_ledgers_all_per_attempt_native_crypto_IO_and_global_join_required',
                'no_new_C_Q_file_pipe_helper_input_output_receipt_channel']:
        assert impact[key] is True
    ce1 = rd(CE01)
    phase1 = ce1['step_obligation_boundary']
    handoff = d['prelaunch_handoff']
    assert fragment(handoff['source']) == phase1['CE11']
    assert handoff['handoff_requirement_id'] == 'X09-PRELAUNCH-HANDOFF'
    assert handoff['required_actual_custody_step_ids'] == step['depends_on'] == phase1['CE11']['required_actual_custody_step_ids']
    final_obligations = plan['closure_boundaries']['external_prerequisites_for_receipt']
    assert handoff['pending_final_route_obligations'] == final_obligations == phase1['CE11']['final_route_obligations_to_handoff']
    for key in ['actual_final_route_completion_required','CE12_receipt_claim_or_spawn_required',
                'handoff_satisfies_actual_final_prerequisites','execution_or_component_qualification_authorized',
                'actual_handoff_accepted','actual_custody_prelaunch_facts_closed']:
        assert handoff[key] is False
    assert handoff['handoff_is_not_execution_gate_release'] and handoff['current_run_command'] is None
    x09 = {r['id']:(i,r) for i,r in enumerate(ce1['external_evidence_requirements']) if r['id'].startswith('X09')}
    assert x09['X09-PRELAUNCH-HANDOFF'][1]['responsible_review_roles'] == ['R06','R08']
    assert x09['X09-FINAL-PREREQUISITES'][1]['responsible_review_roles'] == ['R04','R05','R07','R08']
    for row,original in zip(d['pending_I177_final_bindings'],rd(BINDINGS)['four_binding_plan']):
        assert fragment(row['source']) == original and row['id'] == original['id'] and row['path'] == original['path']
        assert row['historical_producer_step'] == original['producer_step']
        assert not (ROOT/row['path']).exists() and row['current_path_exists'] is False
        assert row['actual_artifact_sha256'] is None and row['accepted'] is False
    assert len(d['pending_I177_final_bindings']) == 4
    ce12 = d['CE12_boundary']
    assert fragment(ce12['source']) == phase1['CE12']
    assert ce12['external_prerequisites'] == final_obligations
    assert ce12['preclaim_external_prerequisites'] == final_obligations[:4] == phase1['CE12']['preclaim_external_prerequisites']
    assert ce12['receipt_only_external_prerequisites'] == final_obligations[4:] == phase1['CE12']['receipt_only_external_prerequisites']
    for key in ['preclaim_prerequisites_must_be_genuinely_satisfied_before_claim','all_external_prerequisites_must_be_genuinely_satisfied_before_receipt',
                'claim_is_not_its_own_precondition','receipt_remains_private_not_capture_output_or_new_wire_field',
                'uncertain_partial_expired_failed_claim_no_free_retry_or_prior_invocation_reuse']:
        assert ce12[key] is True
    for key in ['actual_claim_receipt_or_spawn_required_for_CE11','actual_CE12_currently_authorized','actual_CE12_prerequisites_satisfied']:
        assert ce12[key] is False
    graph = {s['id']:s['depends_on'] for s in plan['steps']}
    closure = ancestors(graph)
    assert closure['CE11'] == {'CE%02d'%i for i in range(1,11)} and 'CE12' not in closure['CE11']
    assert graph['CE12'] == ['CE11'] and plan['closure_boundaries']['prelaunch_depends_on_receipt'] is False
    assert d['freeze_and_invalidation_policy']['inherited_policy'] == plan['freeze_and_refresh']
    for key in ['anchor_key_change_revisit_CE02_then_affected_CE03_to_CE10_and_CE11',
                'any_new_contributor_body_scope_epoch_or_policy_requires_fresh_dependent_review',
                'no_automatic_prior_hash_proof_approval_mapping_or_acceptance_transfer']:
        assert d['freeze_and_invalidation_policy'][key] is True
    assert d['freeze_and_invalidation_policy']['actual_rebind_snapshot_refresh_or_registry_configuration_changed'] is False
    assert d['inherited_scope_boundaries'] == rd(CE10)['inherited_scope_boundaries']
    assert d['preserved_negative_gates'] == rd(CE10)['preserved_negative_gates']
    assert len(d['inherited_scope_boundaries']['S01_exclusions']) == 8
    for gate in d['preserved_negative_gates']:
        assert fragment({**gate['source'],'json_pointer':gate['json_pointer']}) == gate['observed_value']
    assert d['permission_boundary']['denied_action_classes'] == rd(CE10)['permission_boundary']['denied_action_classes']
    for key,value in d['current_effect'].items():
        if key == 'CE11_documentary_prepared':
            assert value is True
        elif key == 'IR03':
            assert value == 'NOT_READY'
        elif key in ['actual_prelaunch_evidence_accepted','resource_obligations_closed']:
            assert value == 0 and type(value) is int
        else:
            assert value is False, key
    assert d['decision'] == plan['decision'] and d['E06'] == plan['E06']
    assert all((ROOT/s['candidate_dossier_path']).exists() for s in plan['steps'][:11])
    assert not (ROOT/plan['steps'][11]['candidate_dossier_path']).exists()
    previous = runpy.run_path(str(ROOT/PRIOR_AUDIT))
    assert previous['build_review']() == rd(PRIOR_PREP)
    original = Path.exists
    assert git('ls-tree','--name-only',previous['BASE'],'--',DOS) == ''
    assert git('ls-tree','--name-only',BASE,'--',DOS) == DOS
    with previous['predecessor_CE11_presence_as_of_base']():
        assert not (ROOT/DOS).exists()
    assert Path.exists is original and (ROOT/DOS).exists()
    class DocumentaryProbe(Exception):
        pass
    try:
        with previous['predecessor_CE11_presence_as_of_base']():
            raise DocumentaryProbe()
    except DocumentaryProbe:
        pass
    assert Path.exists is original and (ROOT/DOS).exists()
    return dict(schema='d5.i220-i219-source-reconstruction.v1',increment='I220',date=DATE,base_commit=BASE,
        input_pins=pins,method='Fixed Git blobs and fresh checklist/gate count, schema reference worklist and CE01 repaired handoff/preclaim/receipt dependency reconstruction; I219 documentary build reproduced without historical publication mains.',
        checklist_review=dict(original_total=31,prelaunch_families=check['prelaunch_families'],prelaunch_family_gate_ids=prelaunch,
            rule_gate_ids=[r['id'] for r in d['rule_gate_dispositions']],global_gate_ids=[r['id'] for r in d['global_gate_dispositions']],
            prelaunch_pending=30,actual_prelaunch_accepted=0,deferred_receipt_gate_ids=deferred,actual_checklist_closed=False),
        rule_review=rule_rows,
        reference_review=dict(schema_reference_templates=69,per_family_template_counts=site_counts,
            bundle_repeats_nested_reference_templates_not_unique_actual_body_count=True,
            all_actual_template_body_author_provider_hash_and_review_missing=True,
            provided_documentary_sources=33,provided_actual_bodies=0,rejected_actual_bodies=0,actual_proofs_evaluated=0,
            actual_body_or_reference_completeness_verified=False,additional_review_topics=8,E01_E05_open=5),
        handoff_scope_review=dict(prelaunch_source=pin(CE01,'/external_evidence_requirements/'+str(x09['X09-PRELAUNCH-HANDOFF'][0])),
            prelaunch_review_role_ids=['R06','R08'],final_route_source=pin(CE01,'/external_evidence_requirements/'+str(x09['X09-FINAL-PREREQUISITES'][0])),
            deferred_final_route_review_role_ids=['R04','R05','R07','R08'],actual_persons_or_appointments_assigned=False,
            pending_I177_binding_ids=[r['id'] for r in d['pending_I177_final_bindings']],current_run_command_provided=False,
            handoff_is_not_actual_final_route_completion_or_authority=True),
        phase_review=dict(step_graph=graph,CE11_ancestors=sorted(closure['CE11']),no_CE12_receipt_claim_spawn_dependency=True,
            no_actual_final_E06_payload_Q_root_admission_completion_added_as_CE11_precondition=True,
            actual_CE01_CE10_custody_facts_still_required=True,preclaim_external_prerequisites=final_obligations[:4],
            receipt_only_prerequisites=final_obligations[4:],claim_not_own_precondition=True,
            all_actual_CE12_authorization_and_prerequisites_still_pending=True),
        preservation=dict(unassigned_review_slots=2,ten_competent_dependencies_pending=True,eight_S01_exclusions_unchanged=True,
            I219_build_and_twelve_documentary_rejections_reproduced=True,historical_CE11_absence_and_current_presence_verified=True,
            guard_restored_after_success_and_exception=True,prior_publication_mains_run=False,CE12_dossier_absent=True),
        verdict=dict(new_blocking_documentary_findings=0,CE11_documentary_baseline_confirmed=True,CE11_accepted=False,
            actual_prelaunch_checklist_closed=False,actual_handoff_accepted=False,actual_prelaunch_evidence_accepted=0,
            independent_acceptance=False,resource_obligations_closed=0,execution_authorized=False,product_or_components_executed=0))


def build_review(rec):
    d = rd(DOS)
    checks = [
        ('E01','Seven prelaunch families,16 rules and all reference dispositions in exact scope','NEGATIVE_MATRIX_PRESERVED_30_GATES_NOT_CLOSED'),
        ('E02','Competent separate review of identities/anchors/image/backend/C/mapping/proofs/impacts','REQUIREMENTS_VISIBLE_NO_ACTUAL_ACCEPTANCE_OR_INDEPENDENT_REVIEW'),
        ('E03','Explicit handoff of existing final E06/payload/Q/root/admission route','PENDING_ROUTE_AND_FOUR_BINDINGS_WITHOUT_RUN_COMMAND_OR_AUTHORITY'),
        ('A01','No launch receipt, actual claim or spawn to accept prelaunch custody facts','CE01_REPAIRED_BOUNDARY_PRESERVED_NO_RECEIPT_CYCLE'),
        ('A02','Custody disposition never flips flags, closes D5 or authorizes execution','NO_ADMISSION_OR_GATE_RELEASE'),
        ('A03','Missing roles/runtime/providers/proofs remain pending; schema/signature/caps not truth','DOCUMENTS_AND_TEMPLATES_NOT_ACTUAL_PROOF_BODIES')]
    return dict(schema='d5.i220-i219-documentary-review.v1',increment='I220',date=DATE,timezone='Europe/Madrid',
        base_commit=BASE,proposal_id=d['proposal_id'],profile_id=d['profile_id'],step='CE11',
        status='CE11_DOCUMENTARY_BASELINE_CONFIRMED_PRELAUNCH_CHECKLIST_HANDOFF_NOT_ACCEPTED_NOT_ADMITTED',
        candidate=pin(DOS),reconstruction=pin(RECON),findings=[],
        checks=[dict(id=i,scope=s,result=r) for i,s,r in checks],contract_rule_review=rec['rule_review'],
        documentary_clarifications=[
            dict(id='C01',subject='Checklist scope',disposition='31 original gates are tracked:30 prelaunch obligations remain unaccepted and one receipt family is deferred. A complete negative disposition table is not an actual closed checklist.'),
            dict(id='C02',subject='69 templates and empty rejection list',disposition='Template paths include array wildcards and repeated nested bundle declarations, not actual or unique proof bodies. No real proof evaluated or rejected here does not mean approval; actual reference/author/body completeness remains unknown.'),
            dict(id='C03',subject='Handoff versus completion',disposition='CE11 requires genuine CE01-CE10 facts/reviews. It hands off pending final route obligations without requiring final E06/payload/Q/root/admission or claim/receipt/spawn completion as an additional CE11 prerequisite.'),
            dict(id='C04',subject='Claim and review scopes',disposition='Source CE01 assigns R06/R08 prelaunch review and R04/R05/R07/R08 deferred final-route review scopes without naming actual people. Four prerequisites precede claim; actual claim/construction is necessary before receipt, not before itself. No authorization is supplied.')],
        provenance=dict(reviewer='Same Codex assistant/chat that prepared I219',methodological_reconstruction_separate=True,
            actor_independent=False,organizationally_independent=False,competent_R06_review=False,separate_R08_acceptance=False,independent_acceptance=False),
        verdict=rec['verdict'],current_effect={**d['current_effect'],'CE11_documentary_review_completed':True,
            'CE11_documentary_confirmation':True,'CE11_documentary_revision_required':False},decision=d['decision'],E06=d['E06'],
        limitations=['All30 actual prelaunch gates, ten competent prerequisite acceptances, providers/roles/source/runtime/backend/proof bodies and complete real reference inventory remain pending. Checklist and handoff are not accepted.',
            'Same assistant is not competent independent R06 review or separate R08 acceptance. Static schema/reference/checklist/dependency confirmation does not close E01-E05, D5 or grant execution.',
            'No product/components, build/import/compile, crypto/codec, platform/clock/ledger/service probe, claim/spawn/receipt, provider contact, final E06/payload/Q/root issuance, quotas/reserves or active bindings/authority/destination changes.'],
        next_scope='CE11 is a documentarily reviewed negative baseline for separately requested CE12 documentary preparation only. Actual closure, handoff, final-route prerequisites and execution authority remain absent.',
        work_unit=dict(rollback_files=sorted(FILES),verification_command='python3 docs/validation/D5-I220-audit.py',expected_result=STATUS,
            runtime_harness='N/A: documentary JSON/Git/hash/checklist/schema-reference and handoff graph checks only; no product/components or runtime claim/spawn/codec/crypto execution.',
            over400_lines=True,reason='One CE11 review with independent31-gate/69-template/handoff reconstruction and immutable preservation; overage reported. No PR requested.'),
        publication=dict(commit_and_push_requested=True,publication_is_not_prelaunch_acceptance_or_execution_authority=True))


def main():
    rec = reconstruct()
    assert rd(RECON) == rec and rd(REVIEW) == build_review(rec)
    prior = rd(PRIOR_SEAL)
    preserved = {**prior['preserved_published584'],**prior['artifacts'],PRIOR_SEAL:sha(PRIOR_SEAL)}
    assert len(preserved) == 589
    seal = rd(SEAL)
    assert seal['schema'] == 'd5.i220-integrity.v1' and seal['base_commit'] == BASE
    assert seal['preserved_published589'] == preserved and set(seal['artifacts']) == FILES-{SEAL}
    for pins in [preserved,seal['artifacts']]:
        for p,h in pins.items():
            assert sha(p) == h, p
    assert seal['source_only'] and seal['current_effect'] == rd(REVIEW)['current_effect']
    changed = set(git('diff',BASE,'--name-only').splitlines()) | set(git('ls-files','--others','--exclude-standard').splitlines())
    assert changed == FILES, changed
    subprocess.check_call(['git','merge-base','--is-ancestor',BASE,'HEAD'],cwd=ROOT)
    if git('rev-parse','HEAD') != BASE:
        assert not git('status','--porcelain')
    print(json.dumps(dict(status=STATUS,increment='I220',historical_pins=897,preserved_published_files=589,
        new_files=5,original_documentary_rejections_reproduced=12,verdict=rec['verdict'],
        proposal_enabled=False,D5_closed=False,IR03='NOT_READY',git_head=git('rev-parse','HEAD')),sort_keys=True))


if __name__ == '__main__':
    main()
