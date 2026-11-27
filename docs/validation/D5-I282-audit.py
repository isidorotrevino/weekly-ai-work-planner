#!/usr/bin/env python3
"""I282 issuer identification plan documentary review; no target execution."""
import copy
import hashlib
import io
import json
from pathlib import Path
import runpy
import subprocess

ROOT = Path(__file__).resolve().parents[2]
P = 'docs/validation/'
BASE = 'd0e77ada36f884afa0b5d8e6ed9389a0740ec716'
DATE = '2026-11-27'
REQUEST = P+'D5-I277-RQ01-RT01-DELIVERY-AUTHORIZATION-REQUEST-CANDIDATE.json'
GAP = P+'D5-I279-DB01-ISSUER-UNIDENTIFIED-GAP.json'
GAP_REVIEW = P+'D5-I280-I279-documentary-review.json'
SUBJECT = P+'D5-I281-DB01-ISSUER-SOURCE-IDENTIFICATION-PLAN.json'
PRIOR_CHECK = P+'D5-I281-documentary-check.json'
PRIOR_AUDIT = P+'D5-I281-audit.py'
PRIOR_SEAL = P+'D5-I281-integrity.json'
PRIOR_DOC = 'docs/design/D5-I281-DB01-ISSUER-SOURCE-IDENTIFICATION-PLAN.md'
PRIOR_FILES = {SUBJECT,PRIOR_CHECK,PRIOR_AUDIT,PRIOR_SEAL,PRIOR_DOC}
RECON = P+'D5-I282-I281-source-reconstruction.json'
REVIEW = P+'D5-I282-I281-documentary-review.json'
AUDIT = P+'D5-I282-audit.py'
SEAL = P+'D5-I282-integrity.json'
DOC = 'docs/design/D5-I282-I281-ISSUER-IDENTIFICATION-PLAN-REVIEW.md'
FILES = {RECON,REVIEW,AUDIT,SEAL,DOC}
STATUS = 'PASS_STATIC_SOURCE_ONLY_DB01_IDENTIFICATION_PLAN_REVIEW_UNVERIFIED_LEADS_NOT_AUTHORITY_OR_CONTACT_PERMISSION_NOT_ADMITTED'


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
    if not ref['path'].endswith('.json'):
        assert ref.get('json_pointer','')=='',ref['path']
        return (ROOT/ref['path']).read_text()
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


LOCAL_PATHS = ['README.md','LICENSE','NOTICE','CONTRIBUTING.md','SECURITY.md','docs/README.md','scripts/check-publication.py']
STEP_TITLES = ['Obtain project context and authorized source pointers','Build a finite authorized documentary search list','Select existing-material or separately authorized inquiry route',
'Separate unverified candidates from canonical issuers','Obtain the full preexisting authority source and chain','Review identity,faculty and current scope under own authority',
'Reconcile DB01 only and dependent invalidations','Return to the existing I277 authorization boundary']
SOURCE_CLASSES = ['Existing project governance/mandate/scope decision or appointment/delegation records','Existing maintainer/owner organizational delegation and communication-authority scope',
'Identity/role directory and appointment references, if applicable under own access authority','Independent provenance,currentness/revocation and delegation-chain antecedents']


def truth(d,keys):
    for key in keys:assert d[key] is True,key


def missing(d,false=()):
    for key,value in d.items():
        if key.startswith('actual_'):assert value is False if key in false else value is None,key
    if 'accepted' in d:assert d['accepted'] is False


def inspect(d):
    gap,q,review=rd(GAP),rd(REQUEST),rd(GAP_REVIEW)
    assert d['plan_id']=='PGE251-DB01-ISSUER-SOURCE-IDENTIFICATION-PLAN-CANDIDATE-01' and d['gap_source']==pin(GAP) and d['latest_review']==pin(GAP_REVIEW)
    assert d['DB01_source']==pin(REQUEST,'/authorization_binding_requirements/0') and d['exact_DB01_requirement']==fragment(d['DB01_source'])==q['authorization_binding_requirements'][0]
    current=d['current_gap'];assert current['source']==pin(GAP,'/DB01_disposition') and current['exact_requirement']==fragment(current['source'])==gap['DB01_disposition']
    assert current['SD01_stop_active'] is True and current['DB01_satisfied'] is False and current['DB02_DB12_pending'] is True and current['RQ01_sent'] is False and current['RQ02_or_downstream_enabled'] is False;missing(current)
    local=d['limited_local_reconnaissance'];assert local['kind']=='Static versioned repository metadata/document reads only,no external service or product execution'
    notes=local['source_notes'];assert [x['path'] for x in notes]==LOCAL_PATHS
    for row,path in zip(notes,LOCAL_PATHS):
        assert row['source']==pin(path) and fragment(row['source'])==(ROOT/path).read_text() and row['read_scope'] and row['finding']
        assert row['genuine_issuer_or_authority_verified'] is False
    remote=local['remote_metadata'];assert remote['observed_origin_url']=='https://github.com/isidorotrevino/weekly-ai-work-planner.git' and remote['unverified_repository_account_handle']=='isidorotrevino'
    assert remote['classification']=='UNVERIFIED_REPOSITORY_ACCOUNT_NAVIGATION_HINT_NOT_CANONICAL_HUMAN_OR_NOMINATED_ISSUER';missing(remote)
    screen=local['limited_marker_screen'];assert screen['selected_versioned_paths']==['CODEOWNERS','.github/CODEOWNERS','GOVERNANCE.md','MAINTAINERS','MAINTAINERS.md'] and screen['observed_selected_paths']==[]
    assert git('ls-tree','--name-only',screen['snapshot_commit'],*screen['selected_versioned_paths'])==''
    assert screen['finite_filename_screen_not_global_absence_or_infeasibility_or_exhaustive_governance_search'] is True and local['no_external_search_or_fetch_contact_or_private_record_access_performed'] is True
    routes=d['prioritized_source_routes'];assert [x['id'] for x in routes]==['SR%02d'%i for i in range(1,5)] and [x['source_class'] for x in routes]==SOURCE_CLASSES
    for row in routes:
        assert row['possible_supplier_role_only'] and row['requested_material'] and row['queried'] is False;missing(row)
    steps=d['identification_steps'];assert [x['id'] for x in steps]==['IP%02d'%i for i in range(1,9)] and [x['title'] for x in steps]==STEP_TITLES
    for i,row in enumerate(steps):
        assert row['depends_on']==([] if i==0 else ['IP%02d'%i])
        assert row['responsible_role_only'] and row['conditional_action'] and row['expected_material_result'] and row['stop_or_failure_rule']
        assert row['performed'] is False and row['completed'] is False;missing(row)
    first=d['first_human_input'];assert first['required'] and len(first['minimal_fields'])==5
    assert first['no_repeat_of_generic_authorize_blank_request_or_nomination'] is True;missing(first)
    material=d['required_reentry_material'];assert material['source']==pin(GAP,'/reentry_requirement') and material['exact_requirement']==fragment(material['source'])==gap['reentry_requirement']
    assert material['source_availability_inventory_not_a_new_authority_or_template_proof'] is True;missing(material)
    controls=d['route_controls'];truth(controls,['existing_supplied_material_may_be_proposed_as_unverified_lead_without_DB01_already_accepted',
        'external_lookup_or_inquiry_requires_its_own_independent_exact_access_contact_authority_not_missing_DB01_or_I277_grant',
        'no_independent_access_or_inquiry_basis_means_stop_external_route_and_seek_locally_supplied_existing_reference',
        'no_contact_fetch_discovery_service_or_private_source_read_authorized_by_plan','no_fabricated_or_retroactive_authority_from_new_declaration_or_future_governance'])
    assert all(type(controls[k]) is int and controls[k]==0 for k in ['actual_external_searches','actual_contacts','actual_private_records_accessed'])
    candidate=d['unverified_candidate_state'];assert candidate['candidate_records']==[] and type(candidate['actual_canonical_candidates_verified']) is int and candidate['actual_canonical_candidates_verified']==0
    missing({k:v for k,v in candidate.items() if k!='actual_canonical_candidates_verified'})
    assert candidate['repository_account_license_title_or_conversation_not_canonical_identity_or_faculty'] is True
    finish=d['completion_boundary'];assert finish['source']==pin(GAP,'/reentry_requirement') and finish['exact_requirement']==fragment(finish['source'])==gap['reentry_requirement']
    truth(finish,['DB01_only_if_genuine_issuer_source_identity_faculty_scope_validity_and_own_review_sufficient','DB01_resolution_not_DB02_DB12_or_contact_grant_EA_authority_RT01_A01_acceptance',
        'original_I277_payload_action_attempts_and_all_other_bindings_unchanged','no_new_A09_RT_or_prelaunch_acceptance_phase']);missing(finish)
    handling=d['safe_material_handling'];assert handling['source']==pin('SECURITY.md') and handling['contribution_source']==pin('CONTRIBUTING.md')
    truth(handling,['no_credentials_private_documents_session_transcripts_unreviewed_logs_or_personal_evidence_published','future_genuine_bodies_need_own_authorized_custody_and_reviewed_publication_scope_not_auto_commit',
        'source_locators_or_document_hashes_not_authenticity_currentness_or_independence_proof','raw_canonical_signature_claims_and_operative_verification_separate_no_codec_crypto_here'])
    pub=d['publication_hygiene'];assert pub['tool_source']==pin('scripts/check-publication.py') and pub['baseline_returncode']==1
    baseline=pub['baseline_location_category_findings'];assert len(baseline)==pub['baseline_findings_count']==37
    assert sum('personal home-directory path' in x for x in baseline)==pub['baseline_personal_path_findings']==2
    assert sum('large file needs explicit publication review' in x for x in baseline)==pub['baseline_large_file_findings']==35
    truth(pub,['no_matching_values_copied_to_plan','historical_files_frozen_not_modified_to_hide_findings','global_checker_not_claimed_PASS_or_authority_evidence'])
    inherited=d['inherited_boundaries'];sections=['preserved_payload','preserved_decision_boundary','current_negative_state','critical_boundaries','final_route_boundary']
    assert [x['section'] for x in inherited]==sections
    for row,s in zip(inherited,sections):assert row['source']==pin(GAP,'/'+s) and row['exact_requirement']==fragment(row['source'])==gap[s]
    assert len(d['critical_boundaries'])==18 and all(v is True for v in d['critical_boundaries'].values())
    assert d['current_effect']=={**review['current_effect'],'DB01_issuer_source_identification_plan_documentary_prepared':True,'actual_external_issuer_search_contact_source_acquisition_or_positive_authorization_progress':False}
    assert all(d['producer'][k] is False for k in ['actor_independent','competent_authorizing_or_primary_role_review','separate_R08_acceptance','external_contacts_made'])
    assert d['publication']['publication_not_external_search_contact_nomination_authority_grant_dispatch_acceptance_execution_or_D5_closure'] is True
    pointers(d)
    return dict(source_route_classes=SOURCE_CLASSES,step_titles=STEP_TITLES,all_steps_unexecuted=True,local_static_source_count=7,remote_hint_not_canonical_identity=True,
        finite_marker_screen_not_global_absence=True,supplied_leads_do_not_require_DB01_already_accepted=True,external_inquiry_needs_independent_exact_authority=True,
        actual_canonical_candidates=None,actual_genuine_issuer_or_source=None,DB01_resolution_not_full_authorization=True,
        publication_global_returncode=1,publication_baseline_findings=37,actual_external_searches=0,actual_contacts=0,actual_genuine_acceptances=0)

CRITERIA = [
'I281 preserves exact DB01/I277 and I279 reentry requirement with I280 frozen review baseline,not authority creation.',
'Current gap remains issuer/source missing,SD01 active,DB01 unsatisfied,DB02-DB12 pending,RQ01 unsent and RQ02 disabled.',
'Seven pinned local sources are static reads only with limited read scope,not a genuine preexisting authority dossier or effective environment proof.',
'Public Git remote/account is an unverified navigation hint,not a canonical human,owner mandate or nominated issuer.',
'Collective copyright/license/maintainer labels do not establish project-human identity or DB01 documentary-contact faculty.',
'Selected versioned CODEOWNERS/GOVERNANCE/MAINTAINERS screen is finite historical filename observation,not exhaustive search or global authority absence.',
'Four prioritized source classes retain existing governance/delegation,organizational faculty,identity/appointment and independent chain/currentness provenance.',
'Source supplier roles are descriptive,unassigned,locations/access/availability unknown,no queried/accepted source.',
'Eight IP IDs/titles/dependencies retain actionable conditional actions,expected material outputs and explicit stop/failure rules.',
'All eight steps unexecuted/no named accountable person/source/body/decision or completion,distinct from already performed limited static reads.',
'First human input asks existing context/record/custodian/access/provenance/faculty/gaps,not generic blank authorization or nomination.',
'Existing legitimately supplied records may be considered as unverified leads without first accepting DB01,no circular proof/contact grant.',
'External inquiry/search/private access requires its own independent exact source/actor/channel/purpose/data/cost/access authority,not missing DB01/I277 grant.',
'Without that independent basis,stop external route and seek legitimately supplied existing reference;plan itself grants no contact/fetch/service/private access.',
'Unverified candidate claims do not become canonical issuer;ambiguity/service accounts/names without source remain unsupported.',
'Preexisting full delegation/mandate/appointment chain and explicit documentary-contact faculty needed,no retroactive authority from newly created declaration.',
'Future governance creation,if needed,is separate prospective work under own authority,not performed or proof of former DB01 faculty here.',
'Genuine available complete bodies/locators/bytes/digests/author/provider/custody/all antecedents/scope/validity/revocation required,no hash/self-assertion/host date as authority.',
'Competent own-scope genuine review and reasons remain required,no same-assistant PASS or metadata as decision.',
'All14 exclusions/current preparers remain applicable,without backward W02 acceptance/full future roster/CE10 or blanket R01/R02 rules.',
'No actual candidate records/inventory/human/source/review supplied,candidate inventory unknown and genuine verifications zero.',
'DB01 alone cannot satisfy DB02-DB12,grant delivery/EA authority,accept RT01/A01 or enable RQ02,no new A09/RT/prelaunch acceptance phase.',
'Exact I277 payload/limits and all other bindings unchanged;changed source/actor/body/scope/epoch/policy/validity invalidates affected A01-A08 before progress,no automatic transfer.',
'Existing gap/reentry five information groups complete,not replaced by plan steps or new documentary criteria.',
'SECURITY/CONTRIBUTING custody/publication rules retain no credentials/private bodies/transcripts/unreviewed logs or auto-publication of incoming evidence.',
'Raw/canonical/signature claims and authorized operative verification remain distinct,no positive codec/crypto/signing/keygen or probes.',
'Global publication scanner exit1/same37 baseline(two personal path locations,35 large historical files) disclosed,not global PASS;new files require clear configured patterns.',
'Baseline warnings do not justify modifying frozen historical artifacts or expose matching values;publication hygiene no authority proof or exhaustive scanner.',
'Both Readers/global reference costs,caps/guards/outputs/quotas/reserves unchanged,no hidden/free inputs or resource guarantee.',
'CE12 private deferred,no final event as new entry/prelaunch condition;claim not own precondition/no free retry,final route separately authorized.',
'No genuine source acquired,issuer verified,authority grant or acceptance;all A01-A08/30 gates/E01-E05/PJC115-R2/D5 remain open.',
'No product/components/build/qualification/execution/enrollment/provision/configuration/probe/contact or active binding/authority/destination/certificate change from plan/publication.'
]


def reconstruct():
    d=rd(SUBJECT);result=inspect(d);pins={**d['input_pins'],**{p:sha(p) for p in PRIOR_FILES}}
    assert len(pins)==1215;verify_blobs(pins)
    return dict(schema='d5.i282-source-reconstruction.v1',increment='I282',date=DATE,timezone='Europe/Madrid',base_commit=BASE,subject=pin(SUBJECT),input_pins=pins,
        independent_reconstruction=result,criteria=[dict(id='RV%02d'%(i+1),criterion=t,result='PASS_DOCUMENTARY_REQUIREMENT_ONLY') for i,t in enumerate(CRITERIA)],
        current_effect={**d['current_effect'],'DB01_issuer_source_identification_plan_documentary_reviewed':True})


def own_rejections(d):
    cases=[
('DB01_reassigned',('DB01_source','json_pointer'),'/authorization_binding_requirements/1'),('source_missing',('limited_local_reconnaissance','source_notes'),d['limited_local_reconnaissance']['source_notes'][:-1]),
('metadata_as_human',('limited_local_reconnaissance','remote_metadata','classification'),'CANONICAL_ISSUER'),('global_absence_claim',('limited_local_reconnaissance','limited_marker_screen','finite_filename_screen_not_global_absence_or_infeasibility_or_exhaustive_governance_search'),False),
('route_missing',('prioritized_source_routes',),d['prioritized_source_routes'][:-1]),('source_class_changed',('prioritized_source_routes',0,'source_class'),'GIT_HANDLE_AUTHORITY'),
('source_availability_invented',('prioritized_source_routes',0,'actual_available_authority_source'),{}),('route_accepted',('prioritized_source_routes',0,'accepted'),True),
('step_order_changed',('identification_steps',0,'id'),'IP08'),('dependency_skipped',('identification_steps',5,'depends_on'),[]),
('step_stop_removed',('identification_steps',4,'stop_or_failure_rule'),''),('output_removed',('identification_steps',6,'expected_material_result'),''),
('first_input_missing',('first_human_input','minimal_fields'),[]),('context_as_received',('first_human_input','actual_context_source_or_custodian_received'),{}),
('reentry_replaced',('required_reentry_material','source','json_pointer'),'/binding_dispositions'),
('independent_inquiry_waived',('route_controls','external_lookup_or_inquiry_requires_its_own_independent_exact_access_contact_authority_not_missing_DB01_or_I277_grant'),False),
('no_basis_route_enabled',('route_controls','no_independent_access_or_inquiry_basis_means_stop_external_route_and_seek_locally_supplied_existing_reference'),False),
('retroactive_authority_allowed',('route_controls','no_fabricated_or_retroactive_authority_from_new_declaration_or_future_governance'),False),
('private_access_performed',('route_controls','actual_private_records_accessed'),1),('candidate_identity_invented',('unverified_candidate_state','actual_genuine_issuer_or_aliases'),'UNVERIFIED_TEST_LABEL'),
('source_digest_invented',('unverified_candidate_state','actual_authority_source_body_location_or_digest'),'UNVERIFIED_TEST_LABEL'),
('own_review_created',('unverified_candidate_state','actual_review_or_decision'),{}),('completion_faculty_waived',('completion_boundary','DB01_only_if_genuine_issuer_source_identity_faculty_scope_validity_and_own_review_sufficient'),False),
('payload_limit_change_allowed',('completion_boundary','original_I277_payload_action_attempts_and_all_other_bindings_unchanged'),False),
('publication_private_data_allowed',('safe_material_handling','no_credentials_private_documents_session_transcripts_unreviewed_logs_or_personal_evidence_published'),False),
('raw_hash_as_authority',('safe_material_handling','source_locators_or_document_hashes_not_authenticity_currentness_or_independence_proof'),False),
('baseline_counts_changed',('publication_hygiene','baseline_large_file_findings'),0),('inherited_boundary_missing',('inherited_boundaries',),d['inherited_boundaries'][:-1]),
('external_progress_claimed',('current_effect','actual_external_issuer_search_contact_source_acquisition_or_positive_authorization_progress'),True),
('assistant_review_authority',('producer','competent_authorizing_or_primary_role_review'),True)]
    results=[]
    for name,path,value in cases:
        mutant=copy.deepcopy(d);node=mutant
        for key in path[:-1]:node=node[key]
        node[path[-1]]=value
        try:inspect(mutant)
        except AssertionError:results.append(dict(case=name,result='REJECTED_DOCUMENTARY_MUTATION_IN_MEMORY'))
        else:raise AssertionError(name)
    return results


def publication_review():
    baseline=rd(SUBJECT)['publication_hygiene']['baseline_location_category_findings']
    result=subprocess.run(['python3','scripts/check-publication.py'],cwd=ROOT,text=True,capture_output=True)
    findings=[s.strip() for s in result.stdout.splitlines() if s.startswith('  ')]
    assert result.returncode==1 and findings==baseline,'Publication findings differ from frozen37 baseline'
    checker=runpy.run_path(str(ROOT/'scripts/check-publication.py'))
    for path in FILES:
        data=(ROOT/path).read_bytes();assert checker['check_path'](path) is None and len(data)<=checker['MAX_TEXT_BYTES'] and b'\0' not in data
        content=data.decode('utf-8');assert all(not pattern.search(content) for _,pattern in checker['SECRET_PATTERNS']),path
        assert all(checker['PLACEHOLDERS'].search(m.group(1)) for m in checker['CREDENTIAL_ASSIGNMENT'].finditer(content)),path
    assert all(s.split(':',1)[0] not in FILES for s in findings)
    return dict(global_returncode=1,unchanged_baseline_findings=37,new_I282_file_findings=0,global_checker_PASS=False,new_file_hygiene='PASS_CONFIGURED_PATTERNS_ONLY')


def build_review(rec):
    previous=runpy.run_path(str(ROOT/PRIOR_AUDIT));assert previous['build_plan']()==rd(SUBJECT)
    check=previous['build_check']();assert check==rd(PRIOR_CHECK) and check['method']['historical_audits_rerun'] is False
    return dict(schema='d5.i282-documentary-review.v1',increment='I282',date=DATE,timezone='Europe/Madrid',base_commit=BASE,status=STATUS,
        subject=pin(SUBJECT),reconstruction=pin(RECON),verdict='NO_NEW_DOCUMENTARY_DEFECT_FOUND_UNVERIFIED_LEADS_AND_UNEXECUTED_ROUTES_NOT_GENUINE_ISSUER_OR_AUTHORITY',findings=[],criteria=rec['criteria'],independent_reconstruction=rec['independent_reconstruction'],
        counts=dict(input_pins=1215,preserved_published_files=900,local_static_sources=7,source_routes=4,unexecuted_plan_steps=8,first_input_fields=5,reentry_material_groups=5,
            review_criteria=len(CRITERIA),global_publication_baseline_findings=37,actual_external_searches=0,actual_contacts=0,actual_private_records_accessed=0,
            actual_genuine_issuers_or_sources_verified=0,actual_grants_or_acceptances=0),
        inherited_I281_rejection_checks=check['rejection_checks'],additional_I282_rejection_checks=own_rejections(rd(SUBJECT)),
        clarifications=['Seven static document reads and one public Git-account metadata hint are bounded local observations,not canonical human identity,preexisting delegation or DB01 faculty. Collective notices/license/maintainer titles cannot appoint an issuer.',
            'Finite marker screen belongs to its recorded commit and selected versioned paths,not an exhaustive authority search or proof of global absence/infeasibility.',
            'Existing legitimately supplied material can be proposed as an unverified lead before DB01 accepted. External inquiry requires its own independent exact access/contact basis,not borrowing missing DB01/I277 delivery grant;without it,stop external route and seek an existing locally supplied reference.',
            'All8 steps/4 source routes remain unexecuted and unassigned,no candidate/body/authority/source acquired or review created. Newly creating governance would be separate prospective work,never automatic proof of preexisting faculty.',
            'Genuine issuer/source/identity/faculty/scope/currentness and competent own-scope review remain necessary for DB01. DB02-DB12,RT02-RT05/full A01 and genuine R06/R08 decisions stay pending,no delivery or RQ02 enablement from plan.',
            'Global publication checker remains exit1 with the same37 preexisting location/category findings. New I282 files must be clear of configured patterns;this is no global PASS,exhaustive secret scan or authority evidence.',
            'Historical files,exact I277 payload/limits and all negative state preserved. No historical audit chain rerun,only I281 focused check and local source/byte/hash reconciliation.',
            'SD01/no admission and CE12/private receipt separately deferred,no final event new entry/prelaunch condition or automatic certificate/PJC115-R2/D5 release.'],
        method=dict(independent_route_step_access_reentry_source_checks=True,I281_plan_and_focused_check_reproduced=True,earlier_historical_audits_rerun=False,prior_publication_mains_called=False,
            required_publication_result='GLOBAL_EXIT1_SAME37_BASELINE_AND_NEW_I282_CONFIGURED_PATTERNS_CLEAR'),
        current_effect=rec['current_effect'],provenance=dict(identity='Same Codex assistant/chat as I281/I279',documentary_review_only=True,actor_independent=False,competent_authorizing_or_primary_role_review=False,separate_R08_acceptance=False,external_contacts_made=False),
        limitations=['Issuer/source/context/custodian and own inquiry/access authority still missing,no plan steps executed,SD01 active,request/handoff unsent and DB01/A01 not accepted.',
            'All A01-A08,30 gates,E01-E05/20 criteria,PJC115-R2/D5 open. Documentary quote/hash/JSON/metadata/mutation PASS gives no genuine authority,eligibility,capacity,service or900 fit.',
            'No external search/fetch/contact/private access,product/component execution,positive protocol codec/crypto/signing/keygen/enrollment/provision/configuration/probe or quota/reserve/binding/authority/destination/certificate change.'],
        work_unit=dict(rollback_files=sorted(FILES),verification_command='python3 docs/validation/D5-I282-audit.py',expected_result=STATUS,over400_lines=True,
            reason='One issuer/source-plan review with independent route/step/control reconstruction,pins,rejection checks,publication baseline and preservation; overage declared,no PR requested.',
            runtime_harness='N/A: own documentary JSON/Git/hash/pointer checks,static source reconciliation,stdlib publication hygiene and in-memory mutations only; no target import,compile,discovery,tests,execution,build,benchmark,positive protocol codec,crypto,signing,keygen,enrollment,contacts,provision,configuration or platform/clock/CPU/IO/ledger/process/endpoint/replay/crash/restart probes.'),
        publication=dict(commit_and_push_requested=True,publication_not_external_search_contact_nomination_genuine_authority_grant_dispatch_acceptance_execution_or_D5_closure=True))


def main():
    rec=reconstruct();assert rec==rd(RECON)
    review=build_review(rec);assert review==rd(REVIEW)
    prior=rd(PRIOR_SEAL);preserved={**prior['preserved_published895'],**prior['artifacts'],PRIOR_SEAL:sha(PRIOR_SEAL)};assert len(preserved)==900
    seal=rd(SEAL);assert seal['schema']=='d5.i282-integrity.v1' and seal['base_commit']==BASE
    assert seal['preserved_published900']==preserved and set(seal['artifacts'])==FILES-{SEAL}
    for mapping in [preserved,seal['artifacts']]:
        for path,digest in mapping.items():assert sha(path)==digest,path
    assert seal['source_only'] is True and seal['current_effect']==rec['current_effect']
    changed=set(git('diff',BASE,'--name-only').splitlines())|set(git('ls-files','--others','--exclude-standard').splitlines());assert changed==FILES,changed
    subprocess.check_call(['git','merge-base','--is-ancestor',BASE,'HEAD'],cwd=ROOT)
    if git('rev-parse','HEAD')!=BASE:assert not git('status','--porcelain')
    pub=publication_review()
    print(json.dumps(dict(status=STATUS,input_pins=1215,preserved_published_files=900,new_files=5,review_criteria=len(CRITERIA),inherited_rejections=len(review['inherited_I281_rejection_checks']),additional_rejections=len(review['additional_I282_rejection_checks']),findings=review['findings'],publication_hygiene=pub,D5_closed=False),sort_keys=True))


if __name__=='__main__':main()
