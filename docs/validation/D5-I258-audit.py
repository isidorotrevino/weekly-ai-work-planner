#!/usr/bin/env python3
"""I258 documentary review of A03/RQ03. No target/component execution."""
import copy
import hashlib
import io
import json
from pathlib import Path
import runpy
import subprocess

ROOT = Path(__file__).resolve().parents[2]
P = 'docs/validation/'
BASE = '02cde01999cb79930d9bfc28e7a4cc1aa0dcd374'
DATE = '2026-11-25'
PLAN = P+'D5-I223-PRELAUNCH-RESOURCE-CLOSURE-PLAN.json'
ACQUISITION = P+'D5-I251-GENUINE-EVIDENCE-ACQUISITION-PLAN.json'
W03 = P+'D5-I223-W03-SOURCES-IMAGE-RUNTIME-CANDIDATE.json'
A02 = P+'D5-I251-A02-RQ02-PEOPLE-APPOINTMENTS-ANCHORS-CANDIDATE.json'
SUBJECT = P+'D5-I251-A03-RQ03-SOURCES-IMAGE-RUNTIME-CANDIDATE.json'
PRIOR_PREP = P+'D5-I257-preparation-review.json'
PRIOR_AUDIT = P+'D5-I257-audit.py'
PRIOR_SEAL = P+'D5-I257-integrity.json'
PRIOR_DOC = 'docs/design/D5-I257-A03-RQ03-SOURCES-IMAGE-RUNTIME.md'
PRIOR_FILES = {SUBJECT,PRIOR_PREP,PRIOR_AUDIT,PRIOR_SEAL,PRIOR_DOC}
RECON = P+'D5-I258-I257-source-reconstruction.json'
REVIEW = P+'D5-I258-I257-documentary-review.json'
AUDIT = P+'D5-I258-audit.py'
SEAL = P+'D5-I258-integrity.json'
DOC = 'docs/design/D5-I258-I257-A03-RQ03-REVIEW.md'
FILES = {RECON,REVIEW,AUDIT,SEAL,DOC}
STATUS = 'PASS_STATIC_SOURCE_ONLY_A03_RQ03_REVIEW_PREDECESSORS_AND_GENUINE_SOURCES_IMAGE_RUNTIME_PENDING_NOT_ADMITTED'


def rd(path):
    return json.loads((ROOT/path).read_text())


def sha(path):
    return hashlib.sha256((ROOT/path).read_bytes()).hexdigest()


def git(*args):
    return subprocess.check_output(['git', *args], cwd=ROOT, text=True).strip()


def pin(path, pointer=''):
    return dict(path=path, sha256=sha(path), json_pointer=pointer)


def fragment(ref):
    assert sha(ref['path']) == ref['sha256'], ref['path']
    value = rd(ref['path'])
    for token in ref.get('json_pointer','').split('/')[1:]:
        key = token.replace('~1','/').replace('~0','~')
        value = value[int(key)] if isinstance(value,list) else value[key]
    return value


def pointers(node):
    if isinstance(node,dict):
        if {'path','sha256','json_pointer'} <= set(node):
            fragment(node)
        for value in node.values():
            pointers(value)
    elif isinstance(node,list):
        for value in node:
            pointers(value)


def verify_blobs(pins):
    stream = io.BytesIO(subprocess.check_output(['git','cat-file','--batch'], cwd=ROOT,
        input=''.join(BASE+':'+path+'\n' for path in sorted(pins)).encode()))
    for path,digest in sorted(pins.items()):
        header = stream.readline().decode().split()
        assert len(header)==3 and header[1]=='blob', path
        body = stream.read(int(header[2]))
        assert stream.read(1)==b'\n' and hashlib.sha256(body).hexdigest()==digest==sha(path), path
    assert not stream.read()


def missing(row, false_fields=()):
    for key,value in row.items():
        if key.startswith('actual_'):
            assert value is False if key in false_fields else value is None,key
    if 'accepted' in row:
        assert row['accepted'] is False


def truth(row, names):
    for name in names:
        assert row[name] is True,name


RETURN_SECTIONS = [
    ['dependency_gate','role_scope_matrix','authority_and_costs'],
    ['source_to_image_missing_inventory','source_scope_policy','image_source_requirement_ledger'],
    ['actual_image_runtime_state','runtime_identity_boundary','runtime_platform_reference_boundary','closure_requirement_ledger','schema_obligations'],
    ['compiled_policy_requirements','no_self_embedding_policy','implementation_proof_boundary','image_source_requirement_ledger','phase_boundary'],
    ['role_scope_matrix','exit_predicate_dispositions','authority_and_costs','phase_boundary'],
    ['source_to_image_missing_inventory','authority_and_costs','phase_boundary']]
IM_RETURNS = [['SR02'],['SR02'],['SR03'],['SR03'],['SR04'],['SR04'],[],[],[],[]]
AC_RETURNS = [['SR01'],['SR02'],['SR02'],['SR02','SR03'],['SR03'],['SR03'],['SR03','SR05'],['SR04'],['SR04'],
    ['SR02','SR03','SR04'],['SR02','SR06'],['SR03','SR05'],['SR01','SR04','SR05'],['SR05'],['SR01','SR05','SR06'],['SR05','SR06']]


def inspect(d):
    plan,acq,w=rd(PLAN),rd(ACQUISITION),rd(W03)
    lot,req=acq['acquisition_lots'][2],plan['work_packages'][2]
    assert (d['lot_id'],d['request_id'],d['work_package'],d['planned_deliverable_id'])==('A03','RQ03','W03',req['deliverable_id'])
    assert d['exact_acquisition_lot']==fragment(d['acquisition_lot_binding'])==lot
    assert d['exact_W03_requirement']==fragment(d['W03_requirement_binding'])==req
    assert d['W03_documentary_checklist']['path']==W03
    gate=d['dependency_gate']
    assert gate['required_lot_ids']==lot['depends_on_lots']==['A01','A02']
    assert gate['required_work_package_ids']==req['depends_on']==['W01','W02']
    assert gate['exact_requirement']==fragment(gate['source'])==w['dependency_gate']
    assert gate['exact_prior_effect']==fragment(gate['A02_state_source'])==rd(A02)['current_effect']
    assert all(gate[key] is False for key in ['A01_accepted','A02_accepted','W01_accepted','W02_accepted'])
    truth(gate,['SD01_stop_active','no_documentary_PASS_as_genuine_antecedent','no_send_contact_nomination_or_positive_intake_from_preparing_this_draft'])
    missing(gate)
    draft=d['unsent_request']
    assert draft['original_draft']==lot['unsent_request_draft'] and draft['recipient_role_only']==lot['intended_recipient_role_kind']
    assert draft['required_return_ids']==['SR%02d'%i for i in range(1,7)]
    assert draft['is_draft_only'] is True and draft['sent'] is False and draft['contact_authorized'] is False
    missing(draft)
    returns=d['requested_returns']
    assert [r['id'] for r in returns]==draft['required_return_ids']
    for row,sections in zip(returns,RETURN_SECTIONS):
        assert row['requirements'] and row['W03_requirement_sources']==[pin(W03,'/'+key) for key in sections]
        assert fragment(row['universal_delivery_source'])==acq['evidence_delivery_contract']
        missing(row,['actual_received'])
    sources=d['source_requests']
    assert len(sources)==6
    assert {r['logical_path'] for r in sources}==set(w['source_scope_policy']['exact_six_paths'])
    for row,source in zip(sources,w['source_to_image_missing_inventory']):
        assert fragment(row['source'])==source and row['logical_path']==source['logical_path']
        assert row['required_representation']==source['required_representation']
        assert row['allowed_representation_policy']==source['allowed_representation_policy']
        assert row['required_return_id']=='SR02' and row['loaded_by_membership_claimed'] is False
        missing(row,['actual_path_exists'])
    assert sources[0]['logical_path'].endswith('/README.md') and sources[0]['required_representation']=='DOCUMENT'
    closure=d['closure_requests']
    assert [r['id'] for r in closure]==['CL%02d'%i for i in range(1,9)]
    for row,source in zip(closure,w['closure_requirement_ledger']):
        assert fragment(row['source'])==source
        assert row['kind']==source['kind'] and row['required_evidence']==source['required_evidence'] and row['required_return_id']=='SR03'
        missing(row)
    ims=d['image_baseline_and_deferred_requests']
    assert [r['id'] for r in ims]==['IM%02d'%i for i in range(1,11)]
    for row,source,required in zip(ims,w['image_source_requirement_ledger'],IM_RETURNS):
        assert fragment(row['source'])==source and row['normative_source']==source['source']
        assert row['required_genuine_evidence']==source['exact_requirement']['required_genuine_evidence']==fragment(row['normative_source'])['required_genuine_evidence']
        assert row['consumer_step']==source['consumer_step'] and row['work_package_consumers']==source['work_package_consumers']
        assert row['deferred_from_A03'] is source['deferred_from_W03'] and row['required_return_ids']==required
        missing(row)
    assert [r['id'] for r in ims if not r['deferred_from_A03']]==['IM%02d'%i for i in range(1,7)]
    assert [(r['id'],r['consumer_step'],r['work_package_consumers']) for r in ims if r['deferred_from_A03']]==[
        ('IM07','CE05',['W04']),('IM08','CE06',['W04']),('IM09','CE07',['W05','W06','W07','W08','W09']),('IM10','CE08',['W10'])]
    policies=d['compiled_policy_requests']
    assert len(policies)==7
    for row,source in zip(policies,w['compiled_policy_requirements']):
        assert fragment(row['source'])==source and row['image_field']==source['image_field']
        assert row['documentary_binding']==source['documentary_binding']
        assert row['required_candidate_policy_sha256']==source['required_candidate_policy_sha256']==sha(row['documentary_binding']['path'])
        assert row['required_return_id']=='SR04'
        missing(row)
    keys=['source_scope_policy','runtime_identity_boundary','runtime_platform_reference_boundary','no_self_embedding_policy','implementation_proof_boundary',
        'schema_obligations','phase_boundary','authority_and_costs','preserved_scope_and_gates','role_scope_matrix']
    assert list(d['inherited_policies'])==keys
    for key,row in d['inherited_policies'].items():
        assert row['exact_requirement']==fragment(row['source'])==w[key]
    assert [r['id'] for r in w['role_scope_matrix']]==['R01','R06','R08']
    assert w['source_scope_policy']['six_source_total_design_ceiling_bytes']==262144
    assert w['schema_obligations']['final_manifest_body_cap_bytes']==98304 and w['schema_obligations']['dependency_max']==128
    assert w['phase_boundary']['downstream_acceptance_required_as_new_reverse_W03_dependency'] is False
    assert len(d['critical_boundaries'])==12 and all(v is True for v in d['critical_boundaries'].values())
    routes=d['material_routes']
    assert routes['existing_material']['required_returns']==['SR01','SR02','SR03','SR04','SR05']
    assert routes['existing_material']['actual_route_accepted'] is False and routes['existing_material']['actual_delivery_inventory'] is None
    gap=routes['missing_material']
    assert gap['required_return_id']=='SR06'
    truth(gap,['exact_missing_item_scope_and_affected_requirements_required','separately_scoped_implementation_build_qualification_or_authority_request_required_if_needed',
        'gap_report_is_not_A03_acceptance_or_permission_to_create_material'])
    missing(gap,['actual_work_performed'])
    truth(routes,['no_global_absence_or_infeasibility_from_local_missing_paths','no_predictive_hash_or_null_as_zero'])
    delivers=d['W03_deliverable_coverage']
    assert [r['id'] for r in delivers]==['WD01','WD02','WD03']
    for i,row in enumerate(delivers):
        assert row['exact_requirement']==fragment(row['source'])==req['deliverables'][i]
        assert row['required_return_ids']==[['SR02','SR03'],['SR03'],['SR04']][i]
        assert row['authority_return_id']=='SR01' and row['review_return_id']=='SR05'
        missing(row)
    criteria=d['acceptance_checklist']; ids=['AC%02d'%i for i in range(1,17)]
    assert [r['id'] for r in criteria]==ids
    for row,required in zip(criteria,AC_RETURNS):
        assert row['criterion'] and row['required_return_ids']==required
        assert row['disposition']=='PENDING_A01_A02_GENUINE_MATERIAL_AND_COMPETENT_DECISION'
        missing(row)
    exits=d['W03_exit_coverage']
    assert [r['id'] for r in exits]==['WX01','WX02','WX03']
    for i,row in enumerate(exits):
        assert row['exact_predicate']==fragment(row['source'])==req['exit_predicates'][i]
        assert row['required_acceptance_criteria']==ids
        missing(row)
    material=d['current_material_state']
    assert material['actual_received_inventory'] is None and material['provided_real_bodies']==material['rejected_real_bodies']==[]
    assert type(material['actual_evaluations']) is int and material['actual_evaluations']==0
    assert material['actual_sources_image_runtime_or_equivalence'] is None and material['actual_provider_schedule_or_duration_guarantee'] is None
    assert material['missing_six_local_sources']==6 and material['local_missing_is_not_global_material_absence'] is True
    assert material['actual_source_implementation_build_crypto_qualification_or_target_inspection_performed'] is False
    resource=d['preserved_resource_rules']
    assert resource['exact_requirement']==fragment(resource['source'])==acq['preserved_resource_and_cost_rules']
    truth(resource,['complete_reference_and_new_route_costs_in_both_Readers_and_global_join_not_free_offline',
        'no_caps_budgets_or_262144_as_actual_heap_CPU_service_capacity_success900_proof','no_quota_budget_reserve_transfer_or_resource_reservation_applied'])
    handoff=d['handoff']
    assert handoff['exact_A03_completion_predicate']==lot['completion_predicate'] and handoff['exact_A03_missing_stop']==lot['missing_or_failure_stop']
    assert handoff['next_lot']=='A04' and handoff['required_genuine_prior_lots']==acq['acquisition_lots'][3]['depends_on_lots']==['A02','A03']
    assert handoff['A04_or_RQ04_started_sent_or_accepted'] is False
    assert handoff['exact_final_route_boundary']==fragment(handoff['final_route_source'])==plan['prelaunch_handoff_and_CE12']
    truth(handoff,['prelaunch_not_conditioned_on_actual_final_E06_payload_Q_root_admission_claim_receipt','no_automatic_launch_certificate_PJC115_R2_or_D5_release'])
    missing(handoff,['actual_final_manifest_created_or_frozen'])
    change=d['change_control']
    assert change['exact_requirement']==fragment(change['source'])==w['phase_boundary']
    truth(change,['any_changed_author_body_source_image_runtime_epoch_key_policy_scope_invalidates_affected_reviews','no_automatic_old_proof_approval_qualification_or_acceptance_transfer'])
    missing(change,['actual_refresh_or_active_rebind'])
    expected={**rd(A02)['current_effect'],'A03_RQ03_documentary_prepared':True,'A03_accepted':False,'RQ03_sent':False,
        'actual_sources_image_runtime_or_build_provenance_accepted':False,'actual_source_implementation_build_or_qualification_created':False,'actual_A03_intake_progress_or_review_records_created':False}
    assert d['current_effect']==expected
    assert d['producer']['actor_independent'] is False and d['producer']['competent_R01_R06_review'] is False
    assert d['producer']['separate_R08_acceptance'] is False and d['producer']['external_contacts_made'] is False
    pointers(d)
    return dict(source_paths=[r['logical_path'] for r in sources],closure_kinds={r['id']:r['kind'] for r in closure},
        baseline_requirements=[r['id'] for r in ims if not r['deferred_from_A03']],
        deferred_consumers={r['id']:dict(step=r['consumer_step'],works=r['work_package_consumers']) for r in ims if r['deferred_from_A03']},
        compiled_policy_fields=[r['image_field'] for r in policies],criterion_to_returns={r['id']:r['required_return_ids'] for r in criteria},
        material_routes_are_requirements_not_actual_delivery_acceptance_or_operational_authority=True,
        actual_source_runtime_image_bodies_received=0,actual_competent_reviews_or_separate_acceptances=0)


CRITERIA = [
    'A03/RQ03 preserves I251 lot,W03 exact deliverables/exits and A01/A02 genuine predecessor dependency.',
    'A01/W01 and A02/W02 remain unaccepted; preparation/review never sends RQ03 or starts positive intake.',
    'Six exact logical source paths retain unknown bodies/digests/source roots/mappings without I122 proof transfer.',
    'README DOCUMENT and permitted source representations are preserved; membership never proves tests/runner loading,import,execution or qualification.',
    'Source ceiling262144 is a candidate to reprove on complete real bytes,not absent=0,capacity or authority to trim/enlarge scope.',
    'Historical480+six source scope admits no hidden repository helpers,old extra reads or silent inputs/channels.',
    'External genuine image digest/bytes remain distinct from complete runtime identity and accepted source/build correspondence.',
    'Historical P02/P03 dossiers/rejections and local auditor Python/OS/environment do not qualify the successor target.',
    'Eight closure classes cover interpreter/ABI/config,loader,stdlib/frozen/native/crypto/allocator/GC/kernel,build/equivalence and relevant service domains.',
    'Dependency closure remains complete,ordered,unique and available,not truncated to128; manifest cap98304 is not global evidence/resource fit.',
    'Seven policy pins are exact document requirements; matching constants/hash do not prove independent policy selection or implementation.',
    'No own future image/manifest/bundle digest self-embedding or bundle-selected policy is allowed.',
    'IM01-IM06 genuine baseline includes immutable first entry before untrusted repository code without claiming full caller/platform enforcement.',
    'IM07/IM08 belong to W04,IM09 to W05-W09 and IM10 to W10; no downstream acceptance reverse edge is added.',
    'Baseline authors/facts must already be authentic before W09; W10 final actor/image/caller/platform freeze reconciles same facts before C.',
    'Existing qualified artifacts route requires own authority/provenance and predecessor acceptance,not synthetic substitutes.',
    'SR06 gap report identifies missing scope/evidence/work and separate authority but never accepts A03 or authorizes implementation/build/qualification.',
    'Missing local sources do not establish global absence/infeasibility or authorize hashes,promises,providers or dates invented here.',
    'Six returns and sixteen criteria cover all three W03 deliverables/exits with SR01 authority and SR05 genuine R01/R06/R08 decisions.',
    'Complete bodies/reference instances/bytes/digests/locators/authors/providers/custody/assumptions/currentness and same-scope decisions remain missing.',
    'Both Readers and global resource join retain all per-attempt lookup/crypto/measurement/native/IO/copy/registry/receipt/output/failure costs without free offline work.',
    'Caps/design ceilings/budgets are not heap/CPU/service/capacity/success900 proof and quotas/reserves remain unchanged.',
    'Changed authors/bodies/source/image/runtime/epoch/key/policy/scope invalidate affected reviews without automatic qualification/acceptance transfer or active rebind.',
    'A04/RQ04 remains stopped and needs genuine A02/A03; this review does not grant contact or action authority.',
    'CE12 remains private and deferred; final E06/payload/Q/root/admission/claim/receipt are not new prelaunch acceptance conditions.',
    'Same assistant documentary review is not competent independent R01/R06 or separate R08 acceptance; negative I122/CP07/component/PJC115-R2/D5/IR03 state remains intact.'
]


def reconstruct():
    d=rd(SUBJECT); result=inspect(d)
    pins={**d['input_pins'],**{path:sha(path) for path in sorted(PRIOR_FILES)}}
    assert len(pins)==1087
    verify_blobs(pins)
    return dict(schema='d5.i258-source-reconstruction.v1',increment='I258',date=DATE,timezone='Europe/Madrid',base_commit=BASE,
        subject=pin(SUBJECT),input_pins=pins,independent_reconstruction=result,
        criteria=[dict(id='RV%02d'%(i+1),criterion=text,result='PASS_DOCUMENTARY_REQUIREMENT_ONLY') for i,text in enumerate(CRITERIA)],
        current_effect={**d['current_effect'],'A03_RQ03_documentary_reviewed':True})


def own_rejections(d):
    cases=[
        ('antecedent_omitted',('dependency_gate','required_lot_ids'),['A02']),
        ('A02_accepted',('dependency_gate','A02_accepted'),True),
        ('request_sent',('unsent_request','sent'),True),
        ('source_omitted',('source_requests',),d['source_requests'][:-1]),
        ('README_as_code',('source_requests',0,'required_representation'),'PYTHON_SOURCE'),
        ('membership_as_loading',('source_requests',4,'loaded_by_membership_claimed'),True),
        ('mapping_fabricated',('source_requests',5,'actual_image_member_representation_digest_mapping'),{}),
        ('closure_class_omitted',('closure_requests',),d['closure_requests'][:-1]),
        ('closure_evidence_waived',('closure_requests',2,'required_evidence'),'UNVERIFIED_TEST_LABEL'),
        ('baseline_requirement_omitted',('image_baseline_and_deferred_requests',),d['image_baseline_and_deferred_requests'][:-1]),
        ('platform_required_early',('image_baseline_and_deferred_requests',7,'deferred_from_A03'),False),
        ('resource_consumer_changed',('image_baseline_and_deferred_requests',8,'work_package_consumers'),['W03']),
        ('final_manifest_required_early',('image_baseline_and_deferred_requests',9,'consumer_step'),'CE04'),
        ('compiled_policy_omitted',('compiled_policy_requests',),d['compiled_policy_requests'][:-1]),
        ('compiled_value_verified',('compiled_policy_requests',0,'actual_compiled_value_or_independent_selection_or_conformance_proof'),'UNVERIFIED_TEST_LABEL'),
        ('source_ceiling_changed',('inherited_policies','source_scope_policy','exact_requirement','six_source_total_design_ceiling_bytes'),262145),
        ('manifest_cap_changed',('inherited_policies','schema_obligations','exact_requirement','final_manifest_body_cap_bytes'),98305),
        ('image_as_runtime',('critical_boundaries','image_digest_not_runtime_identity_P02_P03_old_rejections_not_successor_proof'),False),
        ('target_host_adopted',('critical_boundaries','auditor_Python_OS_or_environment_not_sampled_or_adopted_as_target'),False),
        ('gap_as_permission',('material_routes','missing_material','gap_report_is_not_A03_acceptance_or_permission_to_create_material'),False),
        ('qualification_authorized',('material_routes','missing_material','actual_implementation_build_qualification_or_action_authority'),'UNVERIFIED_TEST_LABEL'),
        ('existing_material_accepted',('material_routes','existing_material','actual_route_accepted'),True),
        ('return_omitted',('requested_returns',),d['requested_returns'][:-1]),
        ('deliverable_authority_waived',('W03_deliverable_coverage',1,'authority_return_id'),'SR05'),
        ('criterion_omitted',('acceptance_checklist',),d['acceptance_checklist'][:-1]),
        ('exit_coverage_waived',('W03_exit_coverage',2,'required_acceptance_criteria'),['AC01']),
        ('inventory_fabricated',('current_material_state','actual_received_inventory'),[]),
        ('offline_cost_free',('preserved_resource_rules','complete_reference_and_new_route_costs_in_both_Readers_and_global_join_not_free_offline'),False),
        ('A04_dependency_omitted',('handoff','required_genuine_prior_lots'),['A03']),
        ('claim_as_own_prerequisite',('handoff','exact_final_route_boundary','claim_not_its_own_precondition'),False),
        ('qualification_transferred',('change_control','no_automatic_old_proof_approval_qualification_or_acceptance_transfer'),False),
        ('A03_accepted',('current_effect','A03_accepted'),True)]
    results=[]
    for name,path,value in cases:
        mutant=copy.deepcopy(d); node=mutant
        for key in path[:-1]:
            node=node[key]
        node[path[-1]]=value
        try:
            inspect(mutant)
        except AssertionError:
            results.append(dict(case=name,result='REJECTED_DOCUMENTARY_MUTATION_IN_MEMORY'))
        else:
            raise AssertionError(name)
    return results


def build_review(rec):
    previous=runpy.run_path(str(ROOT/PRIOR_AUDIT)); exists=Path.exists
    assert previous['build_candidate']()==rd(SUBJECT)
    prep=previous['build_review']()
    assert prep==rd(PRIOR_PREP) and Path.exists is exists
    return dict(schema='d5.i258-documentary-review.v1',increment='I258',date=DATE,timezone='Europe/Madrid',base_commit=BASE,status=STATUS,
        subject=pin(SUBJECT),reconstruction=pin(RECON),
        verdict='NO_NEW_DOCUMENTARY_DEFECT_FOUND_A03_RQ03_CONSISTENT_GENUINE_SOURCES_IMAGE_RUNTIME_AND_ACCEPTANCE_MISSING',findings=[],
        criteria=rec['criteria'],independent_reconstruction=rec['independent_reconstruction'],
        counts=dict(input_pins=1087,source_paths=6,closure_classes=8,compiled_policy_requirements=7,image_requirements=10,
            baseline_requirements=6,deferred_requirements=4,requested_returns=6,acceptance_criteria=16,W03_deliverables=3,W03_exits=3,review_criteria=len(CRITERIA),
            actual_received_bodies=0,actual_sources_or_runtime_accepted=0,actual_lots_accepted=0,prelaunch_gates_closed=0,resource_obligations_closed=0),
        inherited_I257_rejection_checks=prep['rejection_checks'],additional_I258_rejection_checks=own_rejections(rd(SUBJECT)),
        clarifications=[
            'A01/A02 remain unaccepted and SD01 active. This is review of a conditional unsent draft,not positive material intake,contact or implementation.',
            'Genuine qualified existing artifacts and complete source-image-runtime correspondence are required. If absent,SR06 records gaps and separate work/authority; a gap report never accepts A03 or authorizes creating substitutes.',
            'Image bytes digest is distinct from complete runtime identity/P02 evidence. Historical rejected dossiers,document pins and the auditor host do not qualify the changed successor.',
            'README DOCUMENT and membership of test/runner never establish loading/import/execution/qualification. Six-source262144 and manifest98304/dependency128 are design requirements,not actual fit or permission to truncate.',
            'IM01-IM06 establish baseline requirements. IM07/08 caller/platform remain W04; IM09 resources W05-W09; IM10 final manifest W10. No reverse acceptance dependency is introduced.',
            'All authors/bodies/baseline facts must be authentic before W09; W10 final freeze reconciles the same facts without retrospective authentication. Image artifact identity and later final custody-manifest record are distinct.',
            'Actual R01/R06 competent reviews and separate R08 acceptance are missing. The same assistant documentary review supplies none,creates no canonical authority,and cannot enable A04 or D5.'],
        source_reconstruction=dict(primary_source_checks=True,I257_candidate_and_preparation_reproduced=True,prior_publication_mains_called=False,
            prior_Path_exists_restored=True,no_new_presence_projection=True),current_effect=rec['current_effect'],
        provenance=dict(identity='Same Codex assistant/chat as I257',documentary_review_only=True,actor_independent=False,
            competent_R01_R06_review=False,separate_R08_acceptance=False,external_contacts_made=False),
        limitations=['A01/A02/A03 remain unaccepted,SD01 active,RQ03 unsent; six local sources absent and no genuine material or decisions received.',
            'No implementation,build,source/runtime/image qualification,host inspection,crypto validation or actual proof acceptance occurs. Complete provenance/closure/resources remain missing.',
            'Thirty gates,E01-E05 and D5 remain open. No product/component run,probe,contact,signing,configuration,claim,receipt,quota,reserve,binding or active authority/destination change.'],
        work_unit=dict(rollback_files=sorted(FILES),verification_command='python3 docs/validation/D5-I258-audit.py',expected_result=STATUS,
            runtime_harness='N/A: own documentary JSON/Git/hash/pointer/source/closure/policy/phase checks and in-memory documentary mutations only. No target import/compile/discovery/tests/execution/build/benchmark/crypto/signing/keygen/enrollment/provisioning/contacts/platform/clock/CPU/IO/ledger/process/endpoint probes or configuration.',
            over400_lines=True,reason='Single A03/RQ03 review with source reconstruction,pins,rejection checks and preservation; overage declared,no PR requested.'),
        publication=dict(commit_and_push_requested=True,publication_not_source_runtime_authority_evidence_acceptance_execution_or_D5_closure=True))


def main():
    rec=reconstruct(); assert rec==rd(RECON)
    review=build_review(rec); assert review==rd(REVIEW)
    prior=rd(PRIOR_SEAL)
    preserved={**prior['preserved_published774'],**prior['artifacts'],PRIOR_SEAL:sha(PRIOR_SEAL)}
    assert len(preserved)==779
    seal=rd(SEAL)
    assert seal['schema']=='d5.i258-integrity.v1' and seal['base_commit']==BASE
    assert seal['preserved_published779']==preserved and set(seal['artifacts'])==FILES-{SEAL}
    for mapping in [preserved,seal['artifacts']]:
        for path,digest in mapping.items():
            assert sha(path)==digest,path
    assert seal['source_only'] is True and seal['current_effect']==rec['current_effect']
    changed=set(git('diff',BASE,'--name-only').splitlines())|set(git('ls-files','--others','--exclude-standard').splitlines())
    assert changed==FILES,changed
    subprocess.check_call(['git','merge-base','--is-ancestor',BASE,'HEAD'],cwd=ROOT)
    if git('rev-parse','HEAD')!=BASE:
        assert not git('status','--porcelain')
    print(json.dumps(dict(status=STATUS,increment='I258',input_pins=1087,preserved_published_files=779,new_files=5,review_criteria=len(CRITERIA),
        inherited_rejections=len(review['inherited_I257_rejection_checks']),additional_rejections=len(review['additional_I258_rejection_checks']),findings=review['findings'],
        SD01_stop_active=True,prelaunch_gates_closed=0,resource_obligations_closed=0,D5_closed=False,git_head=git('rev-parse','HEAD')),sort_keys=True))


if __name__=='__main__':
    main()
