#!/usr/bin/env python3
"""I266 A07/RQ07 documentary review; no target/component execution."""
import copy
import hashlib
import io
import json
from pathlib import Path
import runpy
import subprocess

ROOT = Path(__file__).resolve().parents[2]
P = 'docs/validation/'
BASE = '18a203e1dc5a9822e25cf15c5d1e11b3c32ccd14'
DATE = '2026-11-26'
PLAN = P+'D5-I223-PRELAUNCH-RESOURCE-CLOSURE-PLAN.json'
ACQUISITION = P+'D5-I251-GENUINE-EVIDENCE-ACQUISITION-PLAN.json'
SUBJECT = P+'D5-I251-A07-RQ07-FINAL-CUSTODY-MAPPING-CANDIDATE.json'
PRIOR_PREP = P+'D5-I265-preparation-review.json'
PRIOR_AUDIT = P+'D5-I265-audit.py'
PRIOR_SEAL = P+'D5-I265-integrity.json'
PRIOR_DOC = 'docs/design/D5-I265-A07-RQ07-FINAL-CUSTODY-MAPPING.md'
PRIOR_FILES = {SUBJECT,PRIOR_PREP,PRIOR_AUDIT,PRIOR_SEAL,PRIOR_DOC}
RECON = P+'D5-I266-I265-source-reconstruction.json'
REVIEW = P+'D5-I266-I265-documentary-review.json'
AUDIT = P+'D5-I266-audit.py'
SEAL = P+'D5-I266-integrity.json'
DOC = 'docs/design/D5-I266-I265-A07-RQ07-REVIEW.md'
FILES = {RECON,REVIEW,AUDIT,SEAL,DOC}
STATUS = 'PASS_STATIC_SOURCE_ONLY_A07_RQ07_REVIEW_GENUINE_FINAL_CUSTODY_AND_GLOBAL_MAPPING_PENDING_NOT_ADMITTED'

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


WORKS = {k:P+v for k,v in [('W10','D5-I223-W10-FINAL-ANTECEDENT-FREEZE-CANDIDATE.json'),('W11','D5-I223-W11-EXACT-C-ACCEPTANCE-CANDIDATE.json'),('W12','D5-I223-W12-BUNDLE-APPROVALS-GLOBAL-MAPPING-CANDIDATE.json')]}

# Independently specified coverage, not generated from the subject's section list.
SECTIONS = {
'W10':'role_and_contributor_boundary freeze_record_ledger nested_schema_obligations contract_rule_requirements inherited_freeze_policy_requirements schema_and_body_boundary record_DAG hash_scope_and_validity_boundary W09_reconciliation_ledger reconciliation_and_invalidation_boundary resource_and_cost_boundary phase_handoff authority_boundary preserved_scope_and_gates'.split(),
'W11':'identity_and_decision_boundary schema_requirement_ledger shared_type_requirement_ledger shared_definition_closure value_projection_requirement_ledger validity_containment_requirement exact_constant_requirements antecedent_hash_requirement_ledger prior_acceptance_evidence_requirement_ledger projection_predicate_requirements contract_rule_requirements inherited_projection_policy_requirements digest_and_signature_boundary scope_and_reconciliation_boundary resource_and_cost_boundary phase_handoff authority_boundary preserved_scope_and_gates'.split(),
'W12':'identity_and_trust_boundary schema_requirement_ledger nested_record_requirement_ledger complete_core_and_bundle_requirement approval_requirement_ledger signature_and_authentication_boundary global_mapping_requirement intrinsic_constructor_boundary inherited_bundle_policy_requirements contract_rule_requirements conditional_size_model accepted_fact_and_validity_boundary resource_and_invalidation_boundary phase_handoff authority_boundary preserved_scope_and_gates'.split()}
AC_RETURNS=[['RF01'],['RF01','RF02'],['RF01','RF02'],['RF02'],['RF03'],['RF03'],['RF03'],['RF03','RF04'],['RF04'],['RF04'],['RF01','RF04'],['RF05'],['RF05'],['RF06'],['RF02','RF03','RF04','RF05','RF06'],['RF06'],['RF03','RF04','RF05'],['RF01','RF06','RF07'],['RF07'],['RF06','RF07']]


def inspect(d):
    plan,acq=rd(PLAN),rd(ACQUISITION); lot=acq['acquisition_lots'][6]
    ws={k:rd(p) for k,p in WORKS.items()}
    assert (d['lot_id'],d['request_id'],d['covers_work_packages'])==('A07','RQ07',list(WORKS))
    assert d['exact_acquisition_lot']==fragment(d['acquisition_lot_binding'])==lot
    gate=d['dependency_gate']
    assert gate['required_lot_ids']==lot['depends_on_lots']==['A02','A04','A06']
    assert gate['required_external_work_package_ids']==['W%02d'%i for i in range(2,10)]
    assert all(gate['A%02d_accepted'%i] is False for i in range(1,7))
    assert gate['exact_prior_effect']==fragment(gate['A06_state_source'])
    assert gate['SD01_stop_active'] is True and gate['no_documentary_PASS_as_genuine_antecedent'] is True
    missing(gate)
    order=d['internal_work_order'];assert order['stages']==[['W10'],['W11'],['W12']]
    assert order['exact_I223_dependencies']=={w:plan['work_packages'][int(w[1:])-1]['depends_on'] for w in WORKS}
    assert order['actual_work_packages_accepted']==0 and order['no_W10_retroactive_authentication_or_future_W13_CE12_acceptance_dependency'] is True
    draft=d['unsent_request'];assert draft['original_draft']==lot['unsent_request_draft']
    assert draft['recipient_role_only']==lot['intended_recipient_role_kind']
    assert draft['is_draft_only'] is True and draft['sent'] is False and draft['contact_authorized'] is False
    missing(draft)
    works=d['work_package_requests'];assert [x['id'] for x in works]==list(WORKS)
    for row in works:
        k=row['id'];req=plan['work_packages'][int(k[1:])-1]
        assert row['exact_requirement']==fragment(row['source'])==req
        assert row['documentary_checklist']==pin(WORKS[k]) and row['planned_deliverable_id']==req['deliverable_id']
        assert row['primary_review_roles']==req['primary_review_roles'] and row['separate_acceptor_role']==req['separate_acceptor_role']=='R08'
        assert row['required_material_return']=={'W10':'RF02','W11':'RF03','W12':'RF04'}[k]
        missing(row)
    coverage=d['custody_scope_requirements'];expected=[(k,s) for k,ss in SECTIONS.items() for s in ss]
    assert [(x['work_package'],x['section']) for x in coverage]==expected and len(coverage)==48
    for row,(k,s) in zip(coverage,expected):
        assert row['source']==pin(WORKS[k],'/'+s) and fragment(row['source'])==ws[k][s]
        assert row['documentary_container_dimension']==len(ws[k][s]) and row['container_dimension_not_actual_records_proofs_or_fit'] is True
        missing(row)
    records=d['final_record_requests'];assert len(records)==4
    for row,src in zip(records,ws['W10']['freeze_record_ledger']):
        assert fragment(row['source'])==src and row['schema_source']==src['schema_source']
        for key in ['family','order','candidate_body_cap_bytes']: assert row[key]==src[key]
        assert row['field_names']==[x['field'] for x in src['field_requirements']]
        assert row['required_return_id']=='RF02';missing(row,['actual_frozen'])
    assert [x['order'] for x in records]==[1,2,3,4]
    assert [len(x['field_names']) for x in records]==[8,26,13,14]
    contexts=d['context_acceptance_requests'];assert len(contexts)==2
    for row,src in zip(contexts,ws['W11']['schema_requirement_ledger']):
        assert fragment(row['source'])==src and row['schema_source']==src['source']
        assert row['kind']==src['kind'] and row['field_count']==len(src['field_requirements'])
        assert row['candidate_body_cap_bytes']==src['candidate_body_cap_bytes'] and row['required_return_id']=='RF03';missing(row)
    assert [x['field_count'] for x in contexts]==[19,27]
    w11=ws['W11'];assert len(w11['shared_type_requirement_ledger'])==14 and len(w11['shared_definition_closure'])==6
    assert len(w11['value_projection_requirement_ledger'])==13 and len(w11['antecedent_hash_requirement_ledger'])==4
    assert len(w11['prior_acceptance_evidence_requirement_ledger'])==5
    truth(w11['validity_containment_requirement'],['type_shared_but_value_relation_is_containment_not_forced_interval_equality','C_validity_must_be_contained_in_each_current_relevant_antecedent_and_acceptance_interval','platform_clock_error_lte_C_clock_error_lte5_and_trusted_now_error_both_sides_required'])
    approvals=d['approval_requests'];assert len(approvals)==3
    for row,src,suffix in zip(approvals,ws['W12']['approval_requirement_ledger'],['R01','R02','R08']):
        assert fragment(row['source'])==src
        for key in ['role','required_domain_ASCII','required_delimiter_hex','required_delimiter_octets','required_payload']:assert row[key]==src[key]
        assert row['required_domain_ASCII']=='D5/PGO181/CUSTODY/v1/'+suffix
        assert row['required_delimiter_hex']=='00' and type(row['required_delimiter_octets']) is int and row['required_delimiter_octets']==1
        assert row['required_return_id']=='RF04' and row['verified'] is False;missing(row)
    mapping=d['mapping_request'];assert mapping['exact_requirement']==fragment(mapping['source'])==ws['W12']['global_mapping_requirement']
    assert mapping['exact_constructor_requirement']==fragment(mapping['constructor_source'])==ws['W12']['intrinsic_constructor_boundary']
    assert mapping['required_return_id']=='RF05';missing(mapping,['actual_backend_selected_or_configured','actual_claim_worker_or_receipt_created'])
    m=mapping['exact_requirement'];assert m['exact_key_fields']==['configuration_epoch','SHA256(JCS(actual C))']
    assert m['required_unique_target_fields']==['bundle','caller','image','protection_domain','global_ledger_domain']
    core=ws['W12']['complete_core_and_bundle_requirement'];assert len(core['core_fields'])==8 and core['bundle_fields']==['schema','signed_core','approvals'] and len(core['nested_families'])==5
    size=ws['W12']['conditional_size_model'];assert sum(size['effective_nested_model_terms_bytes'].values())==size['nested_model_sum_bytes']==218360
    assert 218360+size['conditional_structure_and_approval_overhead_bytes']==size['conditional_total_upper_bytes']==221644
    assert size['candidate_bundle_cap_bytes']-221644==size['conditional_arithmetic_margin_bytes']==40500 and size['actual_fit_verified'] is False
    assert len(d['critical_boundaries'])==18 and all(x is True for x in d['critical_boundaries'].values())
    returns=d['requested_returns'];assert [x['id'] for x in returns]==draft['required_return_ids']==['RF%02d'%i for i in range(1,8)]
    for row,keys in zip(returns,[[],['W10'],['W11'],['W12'],['W12'],list(WORKS),list(WORKS)]):
        assert row['requirements'] and row['work_package_ids']==keys and row['W_requirement_sources']==[pin(WORKS[k]) for k in keys]
        assert fragment(row['universal_delivery_source'])==acq['evidence_delivery_contract'];missing(row,['actual_received'])
    intake=d['acceptance_checklist'];ids=['AC%02d'%i for i in range(1,21)];assert [x['id'] for x in intake]==ids
    for row,rr in zip(intake,AC_RETURNS):
        assert row['criterion'] and row['required_return_ids']==rr
        assert row['disposition']=='PENDING_PREDECESSORS_GENUINE_FINAL_CUSTODY_AND_MAPPING_DECISIONS';missing(row)
    for label,sourcefield,valuefield,total in [('deliverable_coverage','deliverables','exact_requirement',10),('exit_coverage','exit_predicates','exact_predicate',9)]:
        rows=d[label];expected=[(k,i,text) for k in WORKS for i,text in enumerate(plan['work_packages'][int(k[1:])-1][sourcefield])]
        assert len(rows)==len(expected)==total
        for row,(k,i,text) in zip(rows,expected):
            assert row['work_package']==k and row[valuefield]==fragment(row['source'])==text
            if label=='exit_coverage':assert row['required_intake_criteria']==ids
            else:
                assert row['required_material_return']=={'W10':'RF02','W11':'RF03','W12':'RF04'}[k]
                assert row['mapping_return_required']==(k=='W12') and row['authority_return_id']=='RF01' and row['review_return_id']=='RF06'
            missing(row)
    routes=d['material_routes'];assert routes['existing_material']['required_returns']==['RF%02d'%i for i in range(1,7)]
    missing(routes['existing_material'],['actual_route_accepted'])
    gap=routes['missing_material'];assert gap['required_return_id']=='RF07'
    assert all(v is True for k,v in gap.items() if not k.startswith('actual_') and k!='required_return_id');missing(gap,['actual_work_performed'])
    material=d['actual_material_state'];assert material['provided_real_bodies']==material['rejected_real_bodies']==[] and material['actual_evaluations']==0
    missing({k:v for k,v in material.items() if k!='actual_evaluations'},['actual_snapshots_signing_keygen_crypto_enrollment_configuration_or_probe_performed'])
    resource=d['preserved_resource_rules'];assert resource['exact_requirement']==fragment(resource['source'])==acq['preserved_resource_and_cost_rules']
    assert resource['all_nested_and_reference_body_caps_costs_assumptions_Reader_output_guards_join_must_reconcile'] is True and resource['no_quota_budget_reserve_transfer_or_resource_reservation_applied'] is True
    hand=d['handoff'];assert hand['next_lot']=='A08' and hand['required_genuine_prior_lots']==['A%02d'%i for i in range(1,8)]
    assert hand['exact_A07_completion_predicate']==lot['completion_predicate'] and hand['exact_A07_missing_stop']==lot['missing_or_failure_stop']
    assert hand['exact_final_route_boundary']==fragment(hand['final_route_source'])==plan['prelaunch_handoff_and_CE12']
    assert hand['A08_or_RQ08_started_sent_or_accepted'] is False
    truth(hand,['no_final_E06_payload_Q_root_admission_claim_receipt_as_new_prelaunch_condition','no_automatic_certificate_PJC115_R2_execution_or_D5_release']);missing(hand,['actual_W13_gate_closure_or_final_route_created'])
    change=d['change_control'];assert change['exact_requirement']==fragment(change['source'])==plan['scope_authentication_and_freeze_order']
    truth(change,['changed_author_body_source_runtime_image_caller_domain_resource_epoch_key_policy_invalidates_any_affected_A01_A07_before_progress','no_automatic_old_proof_hash_approval_or_acceptance_transfer']);missing(change,['actual_refresh_or_active_rebind'])
    assert d['current_effect']=={**fragment(gate['A06_state_source']),'A07_RQ07_documentary_prepared':True,'A07_accepted':False,'RQ07_sent':False,'actual_final_records_C_acceptance_bundle_approvals_or_mapping_created':False,'actual_A07_intake_progress_or_review_records_created':False}
    assert all(d['producer'][k] is False for k in ['actor_independent','competent_R01_R02_R03_R06_review','separate_R08_acceptance','external_contacts_made'])
    pointers(d)
    return dict(work_order=order['stages'],custody_sections=48,final_records=4,antecedent_fields=61,C_fields=19,acceptance_fields=27,shared_types=14,shared_definitions=6,value_projections=13,antecedent_hashes=4,prior_evidence_requirements=5,approval_roles=[x['role'] for x in approvals],mapping_key=m['exact_key_fields'],mapping_target=m['required_unique_target_fields'],conditional_bundle_bytes=221644,conditional_margin_bytes=40500,actual_records_or_mapping_created=0,actual_acceptances=0)

CRITERIA = [
'A07/RQ07 exact I251 scope and A02/A04/A06 dependencies retain unaccepted A01-A06 and active SD01.',
'RQ07 is local unsent conditional draft; no contact,nomination,issuance or genuine intake authority.',
'W10 to W11 to W12 exact I223 order and work dependencies; no retroactive W09 authentication.',
'All three work requests preserve deliverables,primary reviewers and separate R08.',
'All48 custody sections are exactly pinned; documentary dimensions are not actual proof or fit counts.',
'Four antecedents retain actor,image,caller,platform order,61 fields,exact schemas and body caps.',
'W10 full authors/preparers,prior anchors,record DAG and ten same-fact W09 reconciliations remain required.',
'W11 closed C19/acceptance27 exact schemas and8192/16384 caps retain genuine values.',
'Fourteen shared types,six definitions and thirteen value equalities distinguish validity containment.',
'Four antecedent hashes and five prior evidence requirements need complete genuine available bodies.',
'Current epoch,revocation,containment,platform error <= C error <=5 and lifetime <=3600 remain required.',
'Acceptance custody only,no standalone signature,bundle hash in C or extra C body/bundle validity.',
'W12 five records/eight-field core/three-field bundle and cross-hashes retain complete same core.',
'Three R01/R02/R08 approval domains require exact ASCII plus one NUL plus JCS complete core.',
'Root two signatures do not replace three custody approvals; no cut core or self-founded anchors.',
'R08 human/key separation retained; qualified R01/R02 overlap remains conditional with role domains.',
'Mapping exact key epoch and complete C digest has global uniqueness across callers/images/domains/restarts.',
'Mapping target includes bundle,caller,image,protection domain and global ledger domain; local entry not global proof.',
'Authenticated resolution precedes P_ROOT_CHECK then freezes same C/Q/admitted intrinsic constructor.',
'Worker protected origin adds no helper/frame/channel/receipt; mapping is not claim and incapable backend remains inadmissible.',
'Conditional221644 and40500 arithmetic retains ASCII,safe integers,escaping,nested caps; no actual fit or heap/CPU reserve.',
'Both Readers,full reference inventory,global joins and changed operations retain costs and revalidation.',
'Seven returns cover genuine authority,records,projection,approvals,mapping,resources/reviews and gaps.',
'Twenty intake criteria preserve exact required returns with all actual decisions pending.',
'Ten deliverables and nine exits preserve I223 source requirements and full criteria coverage.',
'SD06/SD07 and missing material require separate exact authority; no unknown-as-zero or global infeasibility.',
'Changed author/body/source/runtime/caller/domain/resource/epoch/key/policy invalidates affected acceptances.',
'A08 requires all A01-A07 genuinely accepted; no W13 gate decision or CE12 final event as reverse prerequisite.',
'All actual records/C/bundle/approvals/mapping remain absent; assistant review is no independent R01/R02/R03/R06/R08 decision.',
'I122/PJC115-R2/D5 negative state remains; no execution,crypto,configuration,quota,reserve or authority change.'
]


def reconstruct():
    d=rd(SUBJECT);result=inspect(d);pins={**d['input_pins'],**{p:sha(p) for p in PRIOR_FILES}}
    assert len(pins)==1127;verify_blobs(pins)
    return dict(schema='d5.i266-source-reconstruction.v1',increment='I266',date=DATE,timezone='Europe/Madrid',base_commit=BASE,subject=pin(SUBJECT),input_pins=pins,independent_reconstruction=result,
        criteria=[dict(id='RV%02d'%(i+1),criterion=t,result='PASS_DOCUMENTARY_REQUIREMENT_ONLY') for i,t in enumerate(CRITERIA)],current_effect={**d['current_effect'],'A07_RQ07_documentary_reviewed':True})


def own_rejections(d):
    cases=[('lot_dependency',('dependency_gate','required_lot_ids'),['A06']),('external_work',('dependency_gate','required_external_work_package_ids'),['W09']),
        ('order',('internal_work_order','stages'),[['W11'],['W10'],['W12']]),('request_return',('unsent_request','required_return_ids'),['RF01']),
        ('work_missing',('work_package_requests',),d['work_package_requests'][:-1]),('reviewer',('work_package_requests',0,'primary_review_roles'),['R01']),
        ('scope_missing',('custody_scope_requirements',),d['custody_scope_requirements'][:-1]),('scope_pointer',('custody_scope_requirements',0,'source','json_pointer'),'/authority_boundary'),
        ('dimension',('custody_scope_requirements',0,'documentary_container_dimension'),-1),('record_missing',('final_record_requests',),d['final_record_requests'][:-1]),
        ('record_order',('final_record_requests',0,'order'),4),('record_field',('final_record_requests',0,'field_names'),[]),('record_cap',('final_record_requests',0,'candidate_body_cap_bytes'),999999),
        ('context_missing',('context_acceptance_requests',),d['context_acceptance_requests'][:-1]),('C_fields',('context_acceptance_requests',0,'field_count'),20),
        ('acceptance_cap',('context_acceptance_requests',1,'candidate_body_cap_bytes'),32768),('approval_missing',('approval_requests',),d['approval_requests'][:-1]),
        ('approval_role',('approval_requests',2,'role'),'R01_RUNTIME'),('approval_domain',('approval_requests',0,'required_domain_ASCII'),'D5/ROOT'),
        ('delimiter',('approval_requests',0,'required_delimiter_octets'),2),('payload',('approval_requests',0,'required_payload'),'JCS(partial core)'),
        ('mapping_key',('mapping_request','exact_requirement','exact_key_fields'),['configuration_epoch','caller']),('mapping_target',('mapping_request','exact_requirement','required_unique_target_fields'),['bundle']),
        ('constructor',('mapping_request','exact_constructor_requirement'),{}),('return_missing',('requested_returns',),d['requested_returns'][:-1]),
        ('return_scope',('requested_returns',4,'work_package_ids'),['W10']),('intake_missing',('acceptance_checklist',),d['acceptance_checklist'][:-1]),
        ('intake_return',('acceptance_checklist',11,'required_return_ids'),['RF04']),('deliverable_missing',('deliverable_coverage',),d['deliverable_coverage'][:-1]),
        ('mapping_coverage',('deliverable_coverage',-1,'mapping_return_required'),False),('exit_missing',('exit_coverage',),d['exit_coverage'][:-1]),
        ('exit_criteria',('exit_coverage',0,'required_intake_criteria'),['AC01']),('A08_prior',('handoff','required_genuine_prior_lots'),['A07']),
        ('source_invalidation',('change_control','changed_author_body_source_runtime_image_caller_domain_resource_epoch_key_policy_invalidates_any_affected_A01_A07_before_progress'),False),
        ('assistant_reviewer',('producer','competent_R01_R02_R03_R06_review'),True)]
    results=[]
    for name,path,value in cases:
        mutant=copy.deepcopy(d);node=mutant
        for k in path[:-1]:node=node[k]
        node[path[-1]]=value
        try:inspect(mutant)
        except AssertionError:results.append(dict(case=name,result='REJECTED_DOCUMENTARY_MUTATION_IN_MEMORY'))
        else:raise AssertionError(name)
    return results


def build_review(rec):
    prior=runpy.run_path(str(ROOT/PRIOR_AUDIT));exists=Path.exists
    assert prior['build_candidate']()==rd(SUBJECT)
    prep=prior['build_review']();assert prep==rd(PRIOR_PREP) and Path.exists is exists
    return dict(schema='d5.i266-documentary-review.v1',increment='I266',date=DATE,timezone='Europe/Madrid',base_commit=BASE,status=STATUS,
        subject=pin(SUBJECT),reconstruction=pin(RECON),verdict='NO_NEW_DOCUMENTARY_DEFECT_FOUND_GENUINE_FINAL_CUSTODY_AND_GLOBAL_MAPPING_PENDING',findings=[],criteria=rec['criteria'],independent_reconstruction=rec['independent_reconstruction'],
        counts=dict(input_pins=1127,preserved_published_files=819,work_packages=3,custody_sections=48,requested_returns=7,intake_criteria=20,deliverables=10,exits=9,review_criteria=len(CRITERIA),actual_acceptances=0,prelaunch_gates_closed=0,resource_obligations_closed=0),
        inherited_I265_rejection_checks=prep['rejection_checks'],additional_I266_rejection_checks=own_rejections(rd(SUBJECT)),
        source_reconstruction=dict(primary_source_checks=True,I265_candidate_and_preparation_reproduced=True,prior_publication_mains_called=False,prior_Path_exists_restored=True,no_new_presence_projection=True),
        current_effect=rec['current_effect'],provenance=dict(identity='Same Codex assistant/chat as I265',documentary_review_only=True,actor_independent=False,competent_R01_R02_R03_R06_review=False,separate_R08_acceptance=False,external_contacts_made=False),
        limitations=['A01-A07 remain unaccepted,SD01 active,RQ07 unsent. No genuine final records,C,acceptance,bundle,approvals or mapping proof received.',
            'Documentary schemas,pins,dimensions,hashes and conditional bounds prove no authentic custody,global uniqueness,actual fit,resource service or independent acceptance.',
            'A08/W13 remains conditional on all A01-A07. Thirty prelaunch gates,E01-E05,PJC115-R2 and D5 remain open; CE12 deferred under separate exact authority.'],
        work_unit=dict(rollback_files=sorted(FILES),verification_command='python3 docs/validation/D5-I266-audit.py',expected_result=STATUS,over400_lines=True,
            reason='One documentary A07/RQ07 review with exact primary-source coverage,pins,mutations and preservation; over400 lines declared,no PR requested.',runtime_harness='N/A: own documentary JSON/Git/hash/pointer/graph/arithmetic checks and in-memory mutations only; no product/component imports,compilation,discovery,tests,execution,build,benchmark,crypto,signing,keygen,enrollment,contacts,platform/clock/CPU/IO/ledger/process/endpoint/replay/crash probes or configuration.'),
        publication=dict(commit_and_push_requested=True,publication_not_independent_review_custody_mapping_acceptance_authority_execution_or_D5_closure=True))


def main():
    rec=reconstruct();assert rec==rd(RECON)
    review=build_review(rec);assert review==rd(REVIEW)
    prior=rd(PRIOR_SEAL);preserved={**prior['preserved_published814'],**prior['artifacts'],PRIOR_SEAL:sha(PRIOR_SEAL)}
    assert len(preserved)==819
    seal=rd(SEAL);assert seal['schema']=='d5.i266-integrity.v1' and seal['base_commit']==BASE
    assert seal['preserved_published819']==preserved and set(seal['artifacts'])==FILES-{SEAL}
    for mapping in [preserved,seal['artifacts']]:
        for p,h in mapping.items():assert sha(p)==h,p
    assert seal['source_only'] is True and seal['current_effect']==rec['current_effect']
    changed=set(git('diff',BASE,'--name-only').splitlines())|set(git('ls-files','--others','--exclude-standard').splitlines());assert changed==FILES,changed
    subprocess.check_call(['git','merge-base','--is-ancestor',BASE,'HEAD'],cwd=ROOT)
    if git('rev-parse','HEAD')!=BASE:assert not git('status','--porcelain')
    print(json.dumps(dict(status=STATUS,input_pins=1127,preserved_published_files=819,new_files=5,review_criteria=len(CRITERIA),inherited_rejections=len(review['inherited_I265_rejection_checks']),additional_rejections=len(review['additional_I266_rejection_checks']),findings=review['findings'],prelaunch_gates_closed=0,resource_obligations_closed=0,D5_closed=False),sort_keys=True))


if __name__=='__main__':main()
