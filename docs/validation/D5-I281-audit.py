#!/usr/bin/env python3
"""I281 DB01 issuer/source acquisition plan; no product/component execution."""
import copy
import hashlib
import io
import json
from pathlib import Path
import runpy
import subprocess

ROOT = Path(__file__).resolve().parents[2]
P = 'docs/validation/'
BASE = '62d008954cc95b6ceb1e48e71e731567035d53c5'
DATE = '2026-11-27'
REQUEST = P+'D5-I277-RQ01-RT01-DELIVERY-AUTHORIZATION-REQUEST-CANDIDATE.json'
GAP = P+'D5-I279-DB01-ISSUER-UNIDENTIFIED-GAP.json'
PRIOR_RECON = P+'D5-I280-I279-source-reconstruction.json'
PRIOR_REVIEW = P+'D5-I280-I279-documentary-review.json'
PRIOR_AUDIT = P+'D5-I280-audit.py'
PRIOR_SEAL = P+'D5-I280-integrity.json'
PRIOR_DOC = 'docs/design/D5-I280-I279-DB01-GAP-REVIEW.md'
PRIOR_FILES = {PRIOR_RECON,PRIOR_REVIEW,PRIOR_AUDIT,PRIOR_SEAL,PRIOR_DOC}
LOCAL_SOURCES = ['README.md','LICENSE','NOTICE','CONTRIBUTING.md','SECURITY.md','docs/README.md','scripts/check-publication.py']
SUBJECT = P+'D5-I281-DB01-ISSUER-SOURCE-IDENTIFICATION-PLAN.json'
PREP = P+'D5-I281-documentary-check.json'
AUDIT = P+'D5-I281-audit.py'
SEAL = P+'D5-I281-integrity.json'
DOC = 'docs/design/D5-I281-DB01-ISSUER-SOURCE-IDENTIFICATION-PLAN.md'
FILES = {SUBJECT,PREP,AUDIT,SEAL,DOC}
STATUS = 'PASS_STATIC_SOURCE_ONLY_DB01_IDENTIFICATION_PLAN_PREPARED_UNVERIFIED_LEADS_ONLY_GENUINE_ISSUER_SOURCE_MISSING_NOT_ADMITTED'


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


PUBLICATION_BASELINE_FINDINGS = ['HANDOFF-D5-I113.md:9: personal home-directory path', 'docs/validation/D5-I113-handoff-integrity.json:79: personal home-directory path', 'docs/validation/D5-I55-raw.json: large file needs explicit publication review', 'docs/validation/D5-I58-NA-regression-raw.json: large file needs explicit publication review', 'docs/validation/D5-I58-raw.json: large file needs explicit publication review', 'docs/validation/D5-I61-FN-regression-raw.json: large file needs explicit publication review', 'docs/validation/D5-I61-NA-regression-raw.json: large file needs explicit publication review', 'docs/validation/D5-I61-raw.json: large file needs explicit publication review', 'docs/validation/D5-I64-CE-regression-raw.json: large file needs explicit publication review', 'docs/validation/D5-I64-FN-regression-raw.json: large file needs explicit publication review', 'docs/validation/D5-I64-NA-regression-raw.json: large file needs explicit publication review', 'docs/validation/D5-I64-raw.json: large file needs explicit publication review', 'docs/validation/D5-I67-trace-raw.json: large file needs explicit publication review', 'docs/validation/D5-I71-P01/sidecar.json: large file needs explicit publication review', 'docs/validation/D5-I71-P02/runner-raw.json: large file needs explicit publication review', 'docs/validation/D5-I71-P02/sidecar.json: large file needs explicit publication review', 'docs/validation/D5-I71-P05/sidecar.json: large file needs explicit publication review', 'docs/validation/D5-I71-P08/runner-raw.json: large file needs explicit publication review', 'docs/validation/D5-I71-P09/runner-raw.json: large file needs explicit publication review', 'docs/validation/D5-I71-P09/sidecar.json: large file needs explicit publication review', 'docs/validation/D5-I71-P10/runner-raw.json: large file needs explicit publication review', 'docs/validation/D5-I71-P10/sidecar.json: large file needs explicit publication review', 'docs/validation/D5-I74-P01/event-0001.json: large file needs explicit publication review', 'docs/validation/D5-I74-P01/event-0002.json: large file needs explicit publication review', 'docs/validation/D5-I74-P01/event-0003.json: large file needs explicit publication review', 'docs/validation/D5-I80-P01/event-0001.json: large file needs explicit publication review', 'docs/validation/D5-I80-P01/event-0002.json: large file needs explicit publication review', 'docs/validation/D5-I80-P01/event-0003.json: large file needs explicit publication review', 'docs/validation/D5-I80-P01/sidecar.json: large file needs explicit publication review', 'docs/validation/D5-I81-trace-review.json: large file needs explicit publication review', 'docs/validation/D5-I89-P01/event-0001.json: large file needs explicit publication review', 'docs/validation/D5-I92-P01/event-0001.json: large file needs explicit publication review', 'docs/validation/D5-I92-P01/event-0002.json: large file needs explicit publication review', 'docs/validation/D5-I92-P01/event-0003.json: large file needs explicit publication review', 'docs/validation/D5-I92-P01/event-0004.json: large file needs explicit publication review', 'docs/validation/D5-I92-P01/sidecar.json: large file needs explicit publication review', 'docs/validation/D5-I96-source-capacity-review.json: large file needs explicit publication review']
ROOT_MARKERS = ['CODEOWNERS','.github/CODEOWNERS','GOVERNANCE.md','MAINTAINERS','MAINTAINERS.md']
SOURCE_ROUTES = [
('SR01','Existing project governance/mandate/scope decision or appointment/delegation records','Current human with legitimate project-context knowledge or authorized record custodian','Provide existing available body/reference and who owns its custody; no new appointment or retroactive authority generated.'),
('SR02','Existing maintainer/owner organizational delegation and communication-authority scope','Genuinely authorized governance/records custodian, not inferred from Git handle','Trace issuer/delegator and explicit faculty to authorize this exact documentary contact; generic repository rights alone insufficient.'),
('SR03','Identity/role directory and appointment references, if applicable under own access authority','Existing legitimate identity/organization record custodian','Resolve accountable human/aliases/competence/appointment; directory membership/title alone not delivery-authority proof.'),
('SR04','Independent provenance,currentness/revocation and delegation-chain antecedents','Existing source owner or legitimate custodian under own authority','Provide complete available antecedents and scope/validity/revocation evidence; no self-signed/new paper as sole authority or operational verification here.')]
STEPS = [
('IP01',[],'Obtain project context and authorized source pointers','Human with legitimate existing project-context knowledge; no person assigned',
 'Supply organization/project scope and who already holds its governance/mandate/appointment records,or existing record paths/references and own permission to provide/read them. This is a lead,not nomination or canonical authority.',
 'Context plus available record references/custodian/access provenance,or an exact missing-context gap.','No context/source pointer or own access basis: keep DB01 missing; do not infer a human from Git/license or contact strangers.'),
('IP02',['IP01'],'Build a finite authorized documentary search list','Legitimate source custodian/operator under existing own access authority; unassigned',
 'Prioritize SR01,then SR02,then SR03/SR04. List exact already-supplied files/record locations,scope and who may read them. Local public metadata may provide leads only. This plan performs no external search/fetch.',
 'Finite source list with availability/access/provenance and expected authority clause; unknowns explicit.','Unavailable/private/external source without own access authority: stop that route and record gap; do not discover credentials or add hidden services.'),
('IP03',['IP02'],'Select existing-material or separately authorized inquiry route','Legitimate human/operator able to supply existing records or independently authorized inquiry; unassigned',
 'Existing genuinely supplied material can be considered under its own provenance without first accepting DB01. If external lookup or contact is necessary,prepare exact source/actor/channel/purpose/data/cost/access scope for a separate own-authority decision; do not borrow missing DB01 or I277 delivery grant. If no independent basis exists,request locally supplied existing reference and stop external action.',
 'Available materials with own access provenance,or a precise separate inquiry/access proposal still unapproved.','This plan grants no inquiry/contact/fetch/service permission and does not require DB01 already accepted just to submit an unverified lead.'),
('IP04',['IP03'],'Separate unverified candidates from canonical issuers','Competent source/identity reviewer under own authority; unassigned',
 'From genuine supplied records only,record claimed human/aliases/organization/role,which source supports it,and uncertainties. Git account/copyright/title may guide navigation but do not establish a human,faculty or appointment. No candidate is chosen or appointed by the assistant.',
 'Unverified candidate/source links or no-candidate gap,with no authority/satisfied flag.','Ambiguous alias,software/service account or name without source: keep candidate unverified,never assign EA01/R06/R08.'),
('IP05',['IP04'],'Obtain the full preexisting authority source and chain','Legitimately authorized custodian/provider of existing records; unassigned',
 'Obtain complete already-existing issuer/delegation/appointment/mandate bodies and antecedents establishing documentary-contact faculty,allowed/denied actions,scope,competence,validity/currentness/revocation and independent provenance. Preserve available locators,bytes/digests,authors/providers/custody,all references and unknowns. Creation of a new declaration does not prove preexisting authority; governance creation,if ever necessary,is separate prospective work,not done here.',
 'Source inventory and exact supporting clauses/antecedents with independent origin,or missing-body/chain/validity gap.','Partial body,unsupported self-assertion or unavailable chain cannot satisfy DB01; do not fabricate source,sign,keygen,run crypto/probes or presume currentness from host date.'),
('IP06',['IP05'],'Review identity,faculty and current scope under own authority','Genuinely competent eligible authority/identity reviewer; unassigned',
 'Review canonical human/aliases,competence/appointment/delegation,faculty for exact I277 documentary-contact scope,validity/revocation and source independence against the5 I279 reentry information groups. Retain14 exclusions/current preparers where applicable,without backward W02 acceptance/future full roster/CE10 or blanket R01/R02 rules. A hash/byte match,license permission or Git access is not this decision.',
 'Own-scope reasoned genuine review with bodies/references and missing/rejected/verified distinctions,not assistant PASS.','Unknown faculty,identity,scope,currentness or independence: defer/reject with genuine reason under own authority; no operative verification without separate exact authority/cost scope.'),
('IP07',['IP06'],'Reconcile DB01 only and dependent invalidations','Genuine own-scope decision actor; unassigned',
 'Only genuinely sufficient issuer/source/authority material and reasoned competent decision can support DB01 resolution. Bind exact clauses/references,scope,validity and dependent changes; invalidate affected A01-A08 before progress. Retain DB02-DB12 pending unless separately evidenced and decided; do not grant delivery or accept A01 from DB01.',
 'DB01 bounded decision or explicit pending gap; other bindings unchanged unless genuinely re-reviewed.','Any actor/source/body/scope/epoch/policy/validity change requires affected fresh review,no automatic proof/approval/acceptance transfer.'),
('IP08',['IP07'],'Return to the existing I277 authorization boundary','Eligible own-authority decision actors for existing bindings; unassigned',
 'Reenter existing DB01 reentry only. Operator,recipients/channel/endpoints,payload/action/attempt limits,validity/denials and genuine exact decision DB02-DB12 remain required before any positive authorization. RT01/full A01 and EA authority are separate; no new lot/acceptance phase or automatic sending route.',
 'Existing authorization request remains not granted/not sent unless all original conditions genuinely met; no current change.','Do not send handoff,fetch responses,nominate/enroll,execute product/components,configure services/change quotas or close D5 from this plan.')]
LOCAL_FINDINGS = [
('README.md','Introductory governance/contribution paragraphs read','Public project introduction and future D6 governance note; no named canonical DB01 issuer/delegation verified here.'),
('LICENSE','Opening license text read','General software-license text; not a project-human identification or DB01 documentary-contact delegation body.'),
('NOTICE','Project notice read','Collective contributors notice; no individual canonical issuer or documentary-contact faculty verified.'),
('CONTRIBUTING.md','Contribution/publication instructions read','Maintainer approval/publication rules and contributor rights; no specific canonical DB01 issuer/delegation verified.'),
('SECURITY.md','Publication/reporting instructions read','Private reporting/publication boundaries and no dedicated security email; no channel/actor/contact authority selected.'),
('docs/README.md','Introductory continuity/index paragraphs read','Historical design/validation index; not a genuine human authority body or fresh adoption.'),
('scripts/check-publication.py','Static source read and documentary publication hygiene run','Stdlib/Git/file-text publication check only,no product imports/execution; limited patterns not evidence authenticity.')]


def build_plan():
    gap,request,review=rd(GAP),rd(REQUEST),rd(PRIOR_REVIEW)
    pins={**rd(PRIOR_RECON)['input_pins'],**{p:sha(p) for p in PRIOR_FILES|set(LOCAL_SOURCES)}};assert len(pins)==1210
    observed=set(git('ls-tree','--name-only',BASE,*ROOT_MARKERS).splitlines());assert not observed
    return dict(schema='d5.i281-db01-identification-plan.v1',increment='I281',date=DATE,timezone='Europe/Madrid',base_commit=BASE,
        plan_id='PGE251-DB01-ISSUER-SOURCE-IDENTIFICATION-PLAN-CANDIDATE-01',kind='DOCUMENTARY_WORK_PLAN_WITH_LIMITED_LOCAL_READ_LEADS_NOT_EXTERNAL_SEARCH_CONTACT_NOMINATION_AUTHORITY_OR_ACCEPTANCE',status=STATUS,
        input_pins=pins,gap_source=pin(GAP),latest_review=pin(PRIOR_REVIEW),DB01_source=pin(REQUEST,'/authorization_binding_requirements/0'),exact_DB01_requirement=request['authorization_binding_requirements'][0],
        objective='Find a genuinely supported preexisting human issuer and available authority source for exact DB01 documentary-contact faculty; keep unverified leads separate from identity/faculty proof and all delivery/acceptance authority.',
        current_gap=dict(source=pin(GAP,'/DB01_disposition'),exact_requirement=gap['DB01_disposition'],actual_identified_genuine_issuer_or_source=None,
            SD01_stop_active=True,DB01_satisfied=False,DB02_DB12_pending=True,RQ01_sent=False,RQ02_or_downstream_enabled=False),
        limited_local_reconnaissance=dict(kind='Static versioned repository metadata/document reads only,no external service or product execution',
            source_notes=[dict(path=path,source=pin(path),read_scope=scope,finding=finding,genuine_issuer_or_authority_verified=False) for path,scope,finding in LOCAL_FINDINGS],
            remote_metadata=dict(observed_origin_url='https://github.com/isidorotrevino/weekly-ai-work-planner.git',unverified_repository_account_handle='isidorotrevino',
                classification='UNVERIFIED_REPOSITORY_ACCOUNT_NAVIGATION_HINT_NOT_CANONICAL_HUMAN_OR_NOMINATED_ISSUER',actual_canonical_human_or_delegation=None),
            limited_marker_screen=dict(snapshot_commit=BASE,selected_versioned_paths=ROOT_MARKERS,observed_selected_paths=[],
                finite_filename_screen_not_global_absence_or_infeasibility_or_exhaustive_governance_search=True),
            no_external_search_or_fetch_contact_or_private_record_access_performed=True),
        prioritized_source_routes=[dict(id=i,source_class=source,possible_supplier_role_only=supplier,requested_material=material,
            actual_record_location_custodian_person_or_access_authority=None,actual_available_authority_source=None,queried=False,accepted=False) for i,source,supplier,material in SOURCE_ROUTES],
        identification_steps=[dict(id=i,depends_on=deps,title=title,responsible_role_only=owner,conditional_action=action,expected_material_result=output,stop_or_failure_rule=stop,
            actual_named_responsible_person_or_own_authority=None,actual_candidate_source_body_or_decision=None,performed=False,completed=False)
            for i,deps,title,owner,action,output,stop in STEPS],
        first_human_input=dict(required='Project/organization context and an existing governance/mandate/appointment/delegation record reference or legitimate custodian/source pointer,with own provenance/access basis; alternatively report that these are not available.',
            minimal_fields=['project/organization context','existing record/reference or legitimate custodian function','where the already-existing source can be supplied/read under own authority','how that source could establish documentary-contact faculty,not merely repository access','known gaps,scope/validity/provenance and authority for any further inquiry'],
            no_repeat_of_generic_authorize_blank_request_or_nomination=True,actual_context_source_or_custodian_received=None),
        required_reentry_material=dict(source=pin(GAP,'/reentry_requirement'),exact_requirement=gap['reentry_requirement'],
            source_availability_inventory_not_a_new_authority_or_template_proof=True,actual_preexisting_issuer_source_or_competent_review=None),
        route_controls=dict(existing_supplied_material_may_be_proposed_as_unverified_lead_without_DB01_already_accepted=True,
            external_lookup_or_inquiry_requires_its_own_independent_exact_access_contact_authority_not_missing_DB01_or_I277_grant=True,
            no_independent_access_or_inquiry_basis_means_stop_external_route_and_seek_locally_supplied_existing_reference=True,
            no_contact_fetch_discovery_service_or_private_source_read_authorized_by_plan=True,
            no_fabricated_or_retroactive_authority_from_new_declaration_or_future_governance=True,
            actual_external_searches=0,actual_contacts=0,actual_private_records_accessed=0),
        unverified_candidate_state=dict(candidate_records=[],actual_complete_candidate_inventory=None,actual_genuine_issuer_or_aliases=None,
            actual_authority_source_body_location_or_digest=None,actual_review_or_decision=None,actual_canonical_candidates_verified=0,
            repository_account_license_title_or_conversation_not_canonical_identity_or_faculty=True),
        completion_boundary=dict(DB01_only_if_genuine_issuer_source_identity_faculty_scope_validity_and_own_review_sufficient=True,
            source=pin(GAP,'/reentry_requirement'),exact_requirement=gap['reentry_requirement'],
            DB01_resolution_not_DB02_DB12_or_contact_grant_EA_authority_RT01_A01_acceptance=True,
            original_I277_payload_action_attempts_and_all_other_bindings_unchanged=True,
            no_new_A09_RT_or_prelaunch_acceptance_phase=True,actual_DB01_resolution_or_delivery_authorization=None),
        safe_material_handling=dict(source=pin('SECURITY.md'),contribution_source=pin('CONTRIBUTING.md'),
            no_credentials_private_documents_session_transcripts_unreviewed_logs_or_personal_evidence_published=True,
            future_genuine_bodies_need_own_authorized_custody_and_reviewed_publication_scope_not_auto_commit=True,
            source_locators_or_document_hashes_not_authenticity_currentness_or_independence_proof=True,
            raw_canonical_signature_claims_and_operative_verification_separate_no_codec_crypto_here=True),
        publication_hygiene=dict(tool_source=pin('scripts/check-publication.py'),baseline_returncode=1,baseline_location_category_findings=PUBLICATION_BASELINE_FINDINGS,
            baseline_findings_count=37,baseline_personal_path_findings=2,baseline_large_file_findings=35,
            no_matching_values_copied_to_plan=True,historical_files_frozen_not_modified_to_hide_findings=True,
            final_required_result='GLOBAL_EXIT1_SAME37_BASELINE_FINDINGS_AND_NO_CONFIGURED_PATTERNS_IN_NEW_I281_FILES',
            global_checker_not_claimed_PASS_or_authority_evidence=True),
        inherited_boundaries=[dict(section=s,source=pin(GAP,'/'+s),exact_requirement=gap[s]) for s in ['preserved_payload','preserved_decision_boundary','current_negative_state','critical_boundaries','final_route_boundary']],
        critical_boundaries=dict(
            plan_only_static_local_read_leads_not_external_search_contact_nomination_or_genuine_evidence=True,
            local_Git_license_notice_maintainer_metadata_not_canonical_human_or_DB01_faculty=True,
            scoped_missing_markers_not_global_authority_absence_or_infeasibility=True,
            candidate_claim_not_verified_issuer_and_new_declaration_not_preexisting_authority=True,
            existing_material_can_be_supplied_without_already_accepting_DB01_no_circular_search_grant=True,
            any_external_inquiry_own_exact_independent_access_contact_authority_not_authorized_here=True,
            genuine_full_source_chain_own_provenance_scope_validity_revocation_competence_review_required=True,
            all14_exclusions_preparers_no_W02_acceptance_future_roster_CE10_backward_gate_or_blanket_R01_R02=True,
            DB01_only_not_DB02_DB12_grant_RT01_RT02_RT05_A01_or_RQ02_enablement=True,
            exact_I277_payload_and_single_attempt_limits_unchanged_changes_invalidate_affected_reviews_no_transfer=True,
            raw_integrity_canonical_signature_claims_authenticity_authority_acceptance_separate=True,
            safe_custody_no_private_material_auto_published_or_new_backend_runtime_input=True,
            no_issuer_operator_person_endpoint_provider_schedule_hash_or_positive_body_fabricated=True,
            SD01_no_admission_no_product_component_build_qualification_probe_crypto_signing_keygen_enrollment_config_or_quota_change=True,
            both_Readers_global_reference_costs_caps_guards_outputs_quotas_reserves_unchanged_no_free_input=True,
            CE12_deferred_no_final_event_new_entry_prelaunch_condition_no_claim_self_condition_or_free_retry=True,
            no_SOURCE_CAPACITY_VERIFIED_certificate_PJC115_R2_D5_release_from_plan_PASS_or_publication=True,
            ordinary_user_gap_and_same_assistant_review_not_genuine_authority_independence_or_decision=True),
        current_effect={**review['current_effect'],'DB01_issuer_source_identification_plan_documentary_prepared':True,
            'actual_external_issuer_search_contact_source_acquisition_or_positive_authorization_progress':False},
        producer=dict(identity='Same Codex assistant/chat as I279/I280; planner and static-document reader only',documentary_preparer_only=True,actor_independent=False,
            competent_authorizing_or_primary_role_review=False,separate_R08_acceptance=False,external_contacts_made=False),
        publication=dict(commit_and_push_requested=True,publication_not_external_search_contact_nomination_authority_grant_dispatch_acceptance_execution_or_D5_closure=True))


def validate(d):
    assert d==build_plan(),'Identification plan differs from exact gap/reentry and limited local source record'
    assert d['exact_DB01_requirement']==fragment(d['DB01_source'])==rd(REQUEST)['authorization_binding_requirements'][0]
    assert len(d['limited_local_reconnaissance']['source_notes'])==7 and d['limited_local_reconnaissance']['remote_metadata']['actual_canonical_human_or_delegation'] is None
    assert [x['id'] for x in d['prioritized_source_routes']]==['SR%02d'%i for i in range(1,5)]
    rows=d['identification_steps'];assert [x['id'] for x in rows]==['IP%02d'%i for i in range(1,9)]
    for i,row in enumerate(rows):assert row['depends_on']==([] if i==0 else ['IP%02d'%i]) and row['performed'] is False and row['completed'] is False
    assert d['required_reentry_material']['exact_requirement']==fragment(d['required_reentry_material']['source'])==rd(GAP)['reentry_requirement']
    assert len(d['first_human_input']['minimal_fields'])==5 and len(d['critical_boundaries'])==18 and all(v is True for v in d['critical_boundaries'].values())
    assert d['unverified_candidate_state']['candidate_records']==[] and d['unverified_candidate_state']['actual_complete_candidate_inventory'] is None
    pointers(d)


def publication_review():
    result=subprocess.run(['python3','scripts/check-publication.py'],cwd=ROOT,text=True,capture_output=True)
    findings=[s.strip() for s in result.stdout.splitlines() if s.startswith('  ')]
    assert result.returncode==1 and findings==PUBLICATION_BASELINE_FINDINGS,'Publication findings differ from preexisting baseline'
    checker=runpy.run_path(str(ROOT/'scripts/check-publication.py'))
    for path in FILES:
        data=(ROOT/path).read_bytes();assert checker['check_path'](path) is None and len(data)<=checker['MAX_TEXT_BYTES'] and b'\0' not in data
        content=data.decode('utf-8')
        assert all(not pattern.search(content) for _,pattern in checker['SECRET_PATTERNS']),path
        assert all(checker['PLACEHOLDERS'].search(m.group(1)) for m in checker['CREDENTIAL_ASSIGNMENT'].finditer(content)),path
    assert all(s.split(':',1)[0] not in FILES for s in findings)
    return dict(global_returncode=1,unchanged_baseline_findings=37,new_I281_file_findings=0,global_checker_PASS=False,new_file_hygiene='PASS_CONFIGURED_PATTERNS_ONLY')


NEGATIVE_CASES = [
('Git_handle_as_human',('limited_local_reconnaissance','remote_metadata','actual_canonical_human_or_delegation'),'UNVERIFIED_TEST_LABEL'),
('local_read_as_authority',('limited_local_reconnaissance','source_notes',0,'genuine_issuer_or_authority_verified'),True),
('filename_screen_as_global_absence',('limited_local_reconnaissance','limited_marker_screen','finite_filename_screen_not_global_absence_or_infeasibility_or_exhaustive_governance_search'),False),
('source_location_invented',('prioritized_source_routes',0,'actual_record_location_custodian_person_or_access_authority'),'UNVERIFIED_TEST_LABEL'),
('source_queried',('prioritized_source_routes',0,'queried'),True),('step_missing',('identification_steps',),[]),('operator_invented',('identification_steps',0,'actual_named_responsible_person_or_own_authority'),'UNVERIFIED_TEST_LABEL'),
('step_executed',('identification_steps',2,'performed'),True),('step_completed',('identification_steps',7,'completed'),True),('source_body_created',('identification_steps',4,'actual_candidate_source_body_or_decision'),{}),
('first_input_fabricated',('first_human_input','actual_context_source_or_custodian_received'),{}),('reentry_source_fabricated',('required_reentry_material','actual_preexisting_issuer_source_or_competent_review'),{}),
('circular_search_authority',('route_controls','existing_supplied_material_may_be_proposed_as_unverified_lead_without_DB01_already_accepted'),False),
('external_contact_granted',('route_controls','no_contact_fetch_discovery_service_or_private_source_read_authorized_by_plan'),False),
('new_paper_as_preexisting',('route_controls','no_fabricated_or_retroactive_authority_from_new_declaration_or_future_governance'),False),
('contact_count',('route_controls','actual_contacts'),1),('candidate_fabricated',('unverified_candidate_state','candidate_records'),[{}]),
('inventory_as_zero',('unverified_candidate_state','actual_complete_candidate_inventory'),[]),('candidate_verified',('unverified_candidate_state','actual_canonical_candidates_verified'),1),
('DB01_as_full_grant',('completion_boundary','DB01_resolution_not_DB02_DB12_or_contact_grant_EA_authority_RT01_A01_acceptance'),False),
('new_A09_phase',('completion_boundary','no_new_A09_RT_or_prelaunch_acceptance_phase'),False),('positive_DB01',('completion_boundary','actual_DB01_resolution_or_delivery_authorization'),{}),
('auto_publish_private_body',('safe_material_handling','future_genuine_bodies_need_own_authorized_custody_and_reviewed_publication_scope_not_auto_commit'),False),
('global_scanner_false_PASS',('publication_hygiene','global_checker_not_claimed_PASS_or_authority_evidence'),False),('baseline_hidden',('publication_hygiene','baseline_findings_count'),0),
('scope_transfer',('critical_boundaries','exact_I277_payload_and_single_attempt_limits_unchanged_changes_invalidate_affected_reviews_no_transfer'),False),
('W02_backward',('critical_boundaries','all14_exclusions_preparers_no_W02_acceptance_future_roster_CE10_backward_gate_or_blanket_R01_R02'),False),
('A01_accepted',('current_effect','A01_accepted'),True),('D5_closed',('current_effect','D5_closed'),True),('assistant_authorizer',('producer','competent_authorizing_or_primary_role_review'),True)]


def rejection_checks(d):
    results=[]
    for name,path,value in NEGATIVE_CASES:
        mutant=copy.deepcopy(d);node=mutant
        for key in path[:-1]:node=node[key]
        node[path[-1]]=value
        try:validate(mutant)
        except AssertionError:results.append(dict(case=name,result='REJECTED_DOCUMENTARY_MUTATION_IN_MEMORY'))
        else:raise AssertionError(name)
    return results


def build_check():
    d=rd(SUBJECT);validate(d)
    return dict(schema='d5.i281-documentary-check.v1',increment='I281',date=DATE,timezone='Europe/Madrid',base_commit=BASE,status=STATUS,subject=pin(SUBJECT),findings=[],
        counts=dict(input_pins=1210,local_static_sources=7,unverified_remote_metadata_hints=1,source_routes=4,planned_steps=8,first_input_fields=5,
            DB01_reentry_information_groups=5,critical_boundaries=18,documentary_rejections=len(NEGATIVE_CASES),preserved_published_files=895,new_files=5,
            actual_external_searches=0,actual_contacts=0,actual_genuine_issuers_verified=0,actual_authority_sources_acquired=0,actual_grants_or_acceptances=0),
        rejection_checks=rejection_checks(d),method=dict(focused_gap_reentry_and_local_static_source_reconciliation=True,published_I280_hashes_and_negative_state_preserved=True,
            historical_audits_rerun=False,product_or_component_execution=False,publication_hygiene='GLOBAL_EXIT1_SAME37_BASELINE_AND_NEW_I281_FILES_CLEAR_REQUIRED_BY_MAIN'),
        current_effect=d['current_effect'],limitations=['Plan contains8 unexecuted steps and4 source classes. Local static metadata/7 source reads and remote-account hint are no verified human,delegation,faculty or candidate nomination.',
            'No external search/fetch/contact/private-record access or authority-source acquisition performed or granted. Existing legitimate supplied leads need not wait for DB01 accepted;external inquiries need independent exact own authority,not missing DB01/I277 grant.',
            'Issuer/source/context/custodian remain missing. DB01/A01 unaccepted,DB02-DB12 pending,SD01 active,RQ01 unsent. No actual source/body/human/calendar or genuine decision fabricated.',
            'Global publication checker has37 preexisting unchanged findings (2 personal path locations,35 large historical files),not a global PASS;main must verify no new findings and new-file configured-pattern hygiene.',
            'No product/components/positive protocol codec/crypto/signing/keygen/enrollment/provision/configuration/probes or quota/reserve/binding/authority/destination/certificate/PJC115-R2/D5 release.'],
        work_unit=dict(rollback_files=sorted(FILES),verification_command='python3 docs/validation/D5-I281-audit.py',expected_result=STATUS,over400_lines=True,
            reason='Single DB01 identification/source plan with finite routes,unexecuted steps,static source pins,publication baseline,rejection checks and preservation; overage declared,no PR requested.',
            runtime_harness='N/A: own documentary JSON/Git/hash/pointer checks,static local document/metadata reads,stdlib publication hygiene and in-memory mutations only. No target import,compile,discovery,tests,execution,build,benchmark,positive protocol codec,crypto,signing,keygen,enrollment,contacts,provision,configuration or platform/clock/CPU/IO/ledger/process/endpoint/replay/crash/restart probes.'),
        provenance=d['producer'],publication=d['publication'])


def main():
    d=rd(SUBJECT);validate(d);verify_blobs(d['input_pins'])
    check=build_check();assert check==rd(PREP)
    prior=rd(PRIOR_SEAL);preserved={**prior['preserved_published890'],**prior['artifacts'],PRIOR_SEAL:sha(PRIOR_SEAL)};assert len(preserved)==895
    seal=rd(SEAL);assert seal['schema']=='d5.i281-integrity.v1' and seal['base_commit']==BASE
    assert seal['preserved_published895']==preserved and set(seal['artifacts'])==FILES-{SEAL}
    for mapping in [preserved,seal['artifacts']]:
        for path,digest in mapping.items():assert sha(path)==digest,path
    assert seal['source_only'] is True and seal['current_effect']==d['current_effect']
    changed=set(git('diff',BASE,'--name-only').splitlines())|set(git('ls-files','--others','--exclude-standard').splitlines());assert changed==FILES,changed
    subprocess.check_call(['git','merge-base','--is-ancestor',BASE,'HEAD'],cwd=ROOT)
    if git('rev-parse','HEAD')!=BASE:assert not git('status','--porcelain')
    pub=publication_review()
    print(json.dumps(dict(status=STATUS,**check['counts'],publication_hygiene=pub,D5_closed=False),sort_keys=True))


if __name__=='__main__':main()
