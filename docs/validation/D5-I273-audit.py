#!/usr/bin/env python3
"""I273 empty documentary reception package; no target/component execution."""
import copy
import hashlib
import io
import json
from pathlib import Path
import runpy
import subprocess

ROOT = Path(__file__).resolve().parents[2]
P = 'docs/validation/'
BASE = '677e7fcec6d5af6b38cb6b71d5eaab0d3a0de39a'
DATE = '2026-11-26'
ACQUISITION = P+'D5-I251-GENUINE-EVIDENCE-ACQUISITION-PLAN.json'
A01 = P+'D5-I251-A01-RQ01-ENTRY-AUTHORITY-SCOPE-CANDIDATE.json'
REQUEST = P+'D5-I271-RQ01-RT01-ENTRY-AUTHORITY-REQUEST-CANDIDATE.json'
PRIOR_RECON = P+'D5-I272-I271-source-reconstruction.json'
PRIOR_REVIEW = P+'D5-I272-I271-documentary-review.json'
PRIOR_AUDIT = P+'D5-I272-audit.py'
PRIOR_SEAL = P+'D5-I272-integrity.json'
PRIOR_DOC = 'docs/design/D5-I272-I271-RQ01-RT01-REVIEW.md'
PRIOR_FILES = {PRIOR_RECON,PRIOR_REVIEW,PRIOR_AUDIT,PRIOR_SEAL,PRIOR_DOC}
SUBJECT = P+'D5-I273-RQ01-RT01-EVIDENCE-RECEPTION-PACKAGE-CANDIDATE.json'
PREP = P+'D5-I273-preparation-review.json'
AUDIT = P+'D5-I273-audit.py'
SEAL = P+'D5-I273-integrity.json'
DOC = 'docs/design/D5-I273-RQ01-RT01-EVIDENCE-RECEPTION-PACKAGE.md'
FILES = {SUBJECT,PREP,AUDIT,SEAL,DOC}
STATUS = 'PASS_STATIC_SOURCE_ONLY_RQ01_RT01_EMPTY_RECEPTION_PACKAGE_PREPARED_NO_GENUINE_MATERIAL_OR_ACCEPTANCE_SD01_ACTIVE_NOT_ADMITTED'


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


# Field descriptions are documentary worksheets, not positive wire schemas or real records.
WORKSHEETS = {
'delivery':['lot_request_return_ids','delivery_id_under_own_authority','provided_at_and_time_provenance','provider_and_own_authority_reference','recipient_and_custodian','supplied_scope_and_validity','complete_original_body_inventory_references','missing_rejected_and_changed_items'],
'body_reference':['delivery_and_body_ids_under_own_authority','immutable_locator_and_actual_availability','complete_original_bytes_and_byte_count','provided_raw_digest_and_algorithm','documentary_recomputed_raw_digest_if_separately_permitted','provided_canonical_digest_and_encoding_claim','canonical_codec_or_crypto_verification_status_and_authority','author_provider_custody_own_provenance_and_all_reference_instances','exact_logical_scope_known_effective_identifiers_or_explicit_unknowns','validity_currentness_revocation_dependencies_and_assumptions'],
'person_authority':['EA_subject_and_required_role','canonical_human_and_complete_aliases','issuer_and_independent_preexisting_delegation_chain_body_references','competence_appointment_scope_allowed_denied_actions','applicable_key_purpose_custody_and_eligibility_body_references','validity_currentness_revocation_evidence','all_actual_preparers_and_exclusion_comparison_references'],
'review_decision':['genuine_role_actor_competence_appointment_authority_reference','independent_primary_or_separate_decision_body_id_locator_bytes_digest','exact_same_scope_and_reviewed_body_references','requirement_or_RC_or_A01_criterion_id_and_reason','missing_provided_rejected_or_accepted_disposition_with_scope','validity_currentness_revocation_and_invalidation_relations','decision_authenticity_provenance_without_assistant_substitution'],
'gap_change':['exact_missing_rejected_incompatible_or_changed_subject_body_authority','known_original_and_changed_scope_claims_without_overwrite','affected_requirements_references_and_A01_A08_dependents','required_separate_exact_work_actor_cost_authority_scope','invalidation_and_required_fresh_review','negative_pending_disposition_without_global_infeasibility_or_calendar_claim']}
STEPS = [
('before_any_intake','Comprobar autorización propia y provenance de una aportación genuina ya disponible. Este paquete sólo prepara;no autoriza hoy contacto/fetch/servicios de verificación,recepción operativa o aceptación. Mantener SD01;una entrega futura no autoautoriza entrada.'),
('record_delivery_without_acceptance','Si una futura aportación es genuina y autorizada bajo su propio ámbito,registrar hechos de disponibilidad/custodia y originales completos,separando claims del proveedor de hechos verificados. PROVIDED_NOT_ACCEPTED no significa autoridad/verdad ni levanta SD01;material desconocido sigue MISSING.'),
('record_integrity_without_authenticity','Mantener bytes originales,locator inmutable,byte count y digest bruto declarado/recalculado separadamente si una autorización propia lo permite. Coincidencia de bytes/hash no demuestra autoría,autoridad,currentness,competencia o independencia. Digest canónico/JCS/firma suministrados son claims hasta verificación competente autorizada;sin codec/crypto positivos aquí.'),
('reconcile_scope_and_eligibility','Relacionar cada cuerpo y referencia con EA01/EA02/EA03,siete grupos de material,ocho campos universales,seis secciones y RC aplicables. Exigir autoridad preexistente propia y14 exclusiones en scope real;sin fabricar humanos,hashes,futuro W02/roster/CE10 como requisito inverso o freeze W03 para scope lógico.'),
('independent_review_and_separate_decision','Sólo actores genuinos competentes/elegibles/autorizados pueden aportar decisiones primarias R06 y separadas R08 con cuerpos y razones por requisito en mismo scope. El asistente o este worksheet no los sustituye;sin ellos queda pendiente. RT05 mantiene review de todo A01.'),
('missing_changed_or_incompatible','Inventariar referencias/supuestos faltantes,aportados y rechazados,sin inferir aceptación de ausencia de rechazo ni unknown=0. Todo cambio invalida afectados A01-A08 y exige nueva review antes de avanzar,sin transferencia automática ni rebind/configuración para rellenar gaps.'),
('limited_followthrough','Una aceptación genuina RT01 sólo cubre su ámbito. RT02-RT05,doce criterios,tres entregables/tres salidas A01 y decisiones propias siguen necesarios antes de considerar RQ02. Sin ejecutar final E06/Q/root/claim/spawn/recibo o crear autoridad/certificado/PJC115-R2/D5 release.')]


def build_candidate():
    r,a,acq=rd(REQUEST),rd(A01),rd(ACQUISITION)
    pins={**rd(PRIOR_RECON)['input_pins'],**{p:sha(p) for p in PRIOR_FILES}};assert len(pins)==1162
    return dict(schema='d5.i273-empty-evidence-reception-package.v1',increment='I273',date=DATE,timezone='Europe/Madrid',base_commit=BASE,
        package_id='PGE251-RQ01-RT01-RECEPTION-CANDIDATE-01',lot_id='A01',request_id='RQ01',return_id='RT01',
        kind='EMPTY_LOCAL_DOCUMENTARY_RECEPTION_WORKSHEETS_NOT_ACTUAL_RECEIPT_EVIDENCE_STORE_WIRE_SCHEMA_AUTHORITY_OR_ACCEPTANCE',
        status='EMPTY_RECEPTION_PACKAGE_PREPARED_NO_MATERIAL_RECEIVED_EA01_R06_R08_AUTHORITY_MISSING_SD01_ACTIVE_NOT_ADMITTED',input_pins=pins,
        request_source=pin(REQUEST),latest_review=pin(PRIOR_REVIEW),
        exact_RT01_requirement_source=pin(A01,'/requested_returns/0'),exact_RT01_requirement=a['requested_returns'][0],
        preparation_boundary=dict(preparation_only=True,actual_operational_intake_or_verification_authorized_now=False,SD01_stop_active=True,
            actual_recipient_people_channel_contact_or_delivery_authority=None,actual_material_provider_or_schedule=None,
            RQ01_sent=False,external_contacts_made=False,no_nomination_fetch_verification_service_or_material_generation=True),
        worksheet_descriptions=[dict(name=k,field_descriptions=v,documentary_description_not_instantiated_positive_record_or_runtime_schema=True,
            actual_records_created=False) for k,v in WORKSHEETS.items()],
        reception_sequence=[dict(step=name,requirement=text,actual_action_or_material=None,performed=False) for name,text in STEPS],
        material_disposition_policy=dict(source=pin(ACQUISITION,'/intake_and_review_workflow'),
            exact_material_states=acq['intake_and_review_workflow']['allowed_future_dispositions'],
            provided_not_accepted_never_proves_authority_truth_or_admission=True,material_states_not_gate_decisions=True,
            missing_body_or_own_authority_keeps_SD01=True,actual_any_material_disposition_decision_created=False),
        documentary_integrity_policy=dict(original_bytes_and_provider_claims_retained_without_overwrite=True,
            supplied_raw_digest_separate_from_documentary_recomputed_raw_digest=True,
            supplied_canonical_digest_codec_or_signature_claim_separate_from_actual_authorized_verification=True,
            raw_hash_or_byte_match_not_authorship_authority_validity_competence_or_independence=True,
            no_positive_codec_crypto_signing_keygen_or_operational_integrity_probe_here=True,
            actual_original_evidence_bytes_or_raw_or_canonical_digest=None,actual_positive_verification_performed=False),
        documentary_trace_policy=dict(source=pin(A01,'/change_control'),exact_requirement=a['change_control'],
            preserve_original_claims_and_trace_changes_supersession_and_affected_review=True,
            documentary_append_trace_policy_not_enforced_backend_durability_global_ledger_or_custody_proof=True,
            no_backend_storage_path_service_or_runtime_Reader_member_selected=True,
            no_incoming_body_personal_data_or_claim_automatically_committed_pushed_or_published=True,
            actual_store_backend_or_global_ledger=None,actual_refresh_or_rebind=False),
        subject_reconciliation_requests=[dict(id=x['id'],required_role=x['required_role'],source=pin(REQUEST,'/subject_evidence_requests/'+str(i)),
            exact_requirement=x,mandatory_material_fields=x['mandatory_material_fields'],
            actual_received_body_references_or_canonical_subject=None,actual_preexisting_authority_chain_scope_validity_or_eligibility=None,
            actual_competent_primary_or_separate_review=None,current_material_state='MISSING',accepted=False) for i,x in enumerate(r['subject_evidence_requests'])],
        information_section_routes=[dict(name=x['name'],source=pin(REQUEST,'/requested_information_sections/'+str(i)),applies_to=x['applies_to'],
            actual_available_body_references_or_decisions=None,accepted=False) for i,x in enumerate(r['requested_information_sections'])],
        universal_delivery_requirement=dict(source=pin(REQUEST,'/universal_delivery_requirement'),exact_requirement=r['universal_delivery_requirement'],
            actual_complete_inventory_or_contract_satisfaction=None,accepted=False),
        eligibility_boundary=dict(source=pin(A01,'/eligibility_boundary'),exact_requirement=a['eligibility_boundary'],
            all_actual_preparers_scope_no_future_author_preapproval=True,W02_criteria_not_backward_W02_acceptance_or_future_full_roster_CE10_requirement=True,
            actual_people_appointments_keys_or_independence_verified=False),
        separation_reconciliation_requests=[dict(id=x['id'],rule=x['rule'],scope=x['scope'],source=pin(A01,'/eligibility_boundary/exact_separation_matrix/'+str(i)),
            actual_canonical_subject_key_comparison_or_evidence=None,actual_eligible_reviewer_decision=None,verified=False)
            for i,x in enumerate(a['eligibility_boundary']['exact_separation_matrix'])],
        RC_reconciliation_requests=[dict(id=x['id'],topic=x['topic'],criterion=x['criterion'],source=pin(REQUEST,'/RT01_intake_checklist/'+str(i)),
            actual_complete_evidence_and_own_authority_references=None,actual_primary_R06_review=None,actual_separate_R08_decision=None,
            current_disposition='PENDING_GENUINE_MATERIAL_AND_COMPETENT_PRIMARY_SEPARATE_DECISIONS',accepted=False) for i,x in enumerate(r['RT01_intake_checklist'])],
        inherited_A01_boundaries=[dict(section=x['section'],source=pin(REQUEST,'/inherited_A01_boundaries/'+str(i)),exact_requirement=x)
            for i,x in enumerate(r['inherited_A01_boundaries'])],
        empty_actual_material_state=dict(delivery_records=[],body_reference_records=[],person_authority_records=[],review_decision_records=[],gap_change_records=[],
            actual_full_reference_inventory=None,actual_available_original_bodies=None,actual_provider_custodian_or_own_receipt_authority=None,
            actual_evaluations=0,actual_genuine_authorities_or_acceptances_created=0,actual_delivery_records_received=0,
            original_document_pins_not_genuine_evidence_body_count=True,unknown_external_reference_count_not_zero=True),
        missing_material_route=dict(current_state='MISSING_NOT_RECEIVED_NOT_EVALUATED',SD01_stop_active=True,
            every_missing_rejected_incompatible_body_subject_scope_assumption_and_dependents_must_remain_visible=True,
            no_accepted_material_from_absence_of_rejection_or_template_or_hash=True,
            gap_needs_separate_exact_work_authority_not_fabrication_contact_execution_or_global_infeasibility=True,
            actual_provider_gap_report_or_new_action_authority=None,actual_work_performed=False),
        complete_A01_followthrough=dict(source=pin(REQUEST,'/complete_A01_followthrough'),exact_requirement=r['complete_A01_followthrough'],
            receipt_or_integrity_or_RT01_acceptance_not_complete_A01_or_RQ02_authority=True,
            actual_RT01_or_A01_acceptance=None,RQ02_or_downstream_enabled=False),
        critical_boundaries=dict(
            empty_packet_not_actual_receipt_inventory_evidence_store_positive_authority_or_acceptance=True,
            actual_source_reference_body_count_unknown_not_document_pin_or_template_count=True,
            receipt_of_available_body_provided_not_accepted_and_SD01_not_lifted=True,
            only_genuine_existing_supplied_material_with_own_authorized_provenance_no_contact_fetch_service=True,
            raw_bytes_digest_integrity_not_authority_authorship_currentness_competence_independence=True,
            raw_digest_canonical_digest_and_signature_claims_separate_no_positive_codec_crypto_here=True,
            original_claims_and_changes_traceable_not_backend_durability_or_global_ledger_proof=True,
            no_evidence_backend_path_service_runtime_Reader_input_or_auto_publication_selected=True,
            EA01_scope_EA02_R06_EA03_R08_authority_genuinely_preexisting_not_user_docs_request_self_or_forecast=True,
            canonical_humans_aliases_competence_appointments14_rules_all_preparers_no_label_keys_alone=True,
            W02_eligibility_not_reverse_acceptance_full_future_roster_or_CE10_no_blanket_R01_R02=True,
            logical_scope_not_effective_W03_freeze_no_predictive_hash_or_unknown_zero=True,
            complete_references_bodies_locators_bytes_digests_authors_providers_custody_scope_validity_and_all_assumptions=True,
            sixteen_RC_reconciliation_not12_full_A01_criteria_no_assistant_as_R06_R08=True,
            genuine_primary_R06_and_separate_R08_decision_bodies_reasons_exact_scope_required=True,
            RT01_partial_not_RT02_RT05_A01_three_deliverables_three_exits_or_RQ02_enablement=True,
            changed_author_body_source_runtime_scope_epoch_key_policy_invalidates_affected_A01_A08_no_automatic_transfer=True,
            gaps_no_global_infeasibility_fake_person_provider_calendar_hash_or_positive_body=True,
            no_operational_intake_execution_implementation_build_qualification_probe_configuration_or_enrollment_here=True,
            no_signing_keygen_C_Q_root_bundle_mapping_claim_worker_receipt_or_new_authority=True,
            both_Readers_global_reference_native_IO_crypto_copy_ledger_output_failure_costs_caps_guards_quotas_reserves_unchanged=True,
            CE12_private_deferred_no_final_E06_Q_root_claim_spawn_receipt_as_new_entry_prelaunch_condition=True,
            four_external_prerequisites_before_claim_then_claim_construction_before_receipt_no_self_condition_or_free_retry=True,
            no_certificate_PJC115_R2_D5_release_from_template_PASS_commit_push_or_future_custody_resource_acceptance=True),
        final_route_boundary=dict(source=pin(REQUEST,'/final_route_boundary'),exact_requirement=r['final_route_boundary'],
            current_run_command=None,actual_final_route_or_receipt_authorized=False),
        current_effect={**r['current_effect'],'RQ01_RT01_empty_documentary_reception_package_prepared':True,
            'actual_RQ01_RT01_delivery_intake_evidence_store_or_genuine_acceptance_created':False},
        producer=dict(identity='Same Codex assistant/chat as I271/I272/A01',documentary_preparer_only=True,actor_independent=False,
            competent_primary_role_review=False,separate_R08_acceptance=False,external_contacts_made=False),
        publication=dict(commit_and_push_requested=True,only_empty_documentary_package_published_no_actual_incoming_evidence=True,
            publication_not_receipt_genuine_authority_eligibility_review_acceptance_execution_or_D5_closure=True))


def validate(d):
    assert d==build_candidate(),'Empty reception package differs from exact documentary reconstruction'
    r,a,acq=rd(REQUEST),rd(A01),rd(ACQUISITION)
    assert (d['lot_id'],d['request_id'],d['return_id'])==('A01','RQ01','RT01')
    assert d['exact_RT01_requirement']==fragment(d['exact_RT01_requirement_source'])==a['requested_returns'][0]
    assert len(d['worksheet_descriptions'])==5 and [x['name'] for x in d['worksheet_descriptions']]==list(WORKSHEETS)
    assert len(d['reception_sequence'])==7
    assert d['material_disposition_policy']['exact_material_states']==acq['intake_and_review_workflow']['allowed_future_dispositions']
    assert [x['id'] for x in d['subject_reconciliation_requests']]==['EA01','EA02','EA03']
    for i,x in enumerate(d['subject_reconciliation_requests']):
        assert x['exact_requirement']==fragment(x['source'])==r['subject_evidence_requests'][i]
        assert x['mandatory_material_fields']==r['subject_evidence_requests'][i]['mandatory_material_fields'] and len(x['mandatory_material_fields'])==7
    assert [x['name'] for x in d['information_section_routes']]==[x['name'] for x in r['requested_information_sections']]
    assert len(d['separation_reconciliation_requests'])==14 and len(d['RC_reconciliation_requests'])==16
    for i,x in enumerate(d['separation_reconciliation_requests']):
        src=a['eligibility_boundary']['exact_separation_matrix'][i];assert fragment(x['source'])==src
        assert (x['id'],x['rule'],x['scope'])==(src['id'],src['rule'],src['scope'])
    for i,x in enumerate(d['RC_reconciliation_requests']):
        src=r['RT01_intake_checklist'][i];assert fragment(x['source'])==src and (x['id'],x['topic'],x['criterion'])==(src['id'],src['topic'],src['criterion'])
    assert d['complete_A01_followthrough']['exact_requirement']==fragment(d['complete_A01_followthrough']['source'])==r['complete_A01_followthrough']
    assert len(d['inherited_A01_boundaries'])==9 and len(d['critical_boundaries'])==24 and all(v is True for v in d['critical_boundaries'].values())
    state=d['empty_actual_material_state'];assert all(state[k]==[] for k in ['delivery_records','body_reference_records','person_authority_records','review_decision_records','gap_change_records'])
    assert all(type(state[k]) is int and state[k]==0 for k in ['actual_evaluations','actual_genuine_authorities_or_acceptances_created','actual_delivery_records_received'])
    assert state['actual_full_reference_inventory'] is None and state['unknown_external_reference_count_not_zero'] is True
    pointers(d)


NEGATIVE_CASES = [
('operational_intake_authorized',('preparation_boundary','actual_operational_intake_or_verification_authorized_now'),True),('SD01',('preparation_boundary','SD01_stop_active'),False),
('request_sent',('preparation_boundary','RQ01_sent'),True),('provider_invented',('preparation_boundary','actual_material_provider_or_schedule'),'UNVERIFIED_TEST_LABEL'),
('worksheet_as_record',('worksheet_descriptions',0,'actual_records_created'),True),('step_performed',('reception_sequence',0,'performed'),True),
('provided_is_accepted',('material_disposition_policy','provided_not_accepted_never_proves_authority_truth_or_admission'),False),
('digest_proves_authority',('documentary_integrity_policy','raw_hash_or_byte_match_not_authorship_authority_validity_competence_or_independence'),False),
('canonical_claim_verified',('documentary_integrity_policy','actual_positive_verification_performed'),True),
('raw_digest_invented',('documentary_integrity_policy','actual_original_evidence_bytes_or_raw_or_canonical_digest'),'UNVERIFIED_TEST_LABEL'),
('trace_as_global_ledger',('documentary_trace_policy','documentary_append_trace_policy_not_enforced_backend_durability_global_ledger_or_custody_proof'),False),
('backend_selected',('documentary_trace_policy','actual_store_backend_or_global_ledger'),'UNVERIFIED_TEST_LABEL'),
('auto_publish_evidence',('documentary_trace_policy','no_incoming_body_personal_data_or_claim_automatically_committed_pushed_or_published'),False),
('EA_missing',('subject_reconciliation_requests',),[]),('EA01_received',('subject_reconciliation_requests',0,'actual_received_body_references_or_canonical_subject'),[]),
('EA03_accepted',('subject_reconciliation_requests',2,'accepted'),True),('section_missing',('information_section_routes',),[]),
('contract_accepted',('universal_delivery_requirement','accepted'),True),('W02_backward',('eligibility_boundary','W02_criteria_not_backward_W02_acceptance_or_future_full_roster_CE10_requirement'),False),
('separation_verified',('separation_reconciliation_requests',0,'verified'),True),('RC_review_fabricated',('RC_reconciliation_requests',0,'actual_primary_R06_review'),{}),
('RC_accepted',('RC_reconciliation_requests',0,'accepted'),True),('boundary_missing',('inherited_A01_boundaries',),[]),
('delivery_fabricated',('empty_actual_material_state','delivery_records'),[{}]),('body_fabricated',('empty_actual_material_state','body_reference_records'),[{}]),
('person_fabricated',('empty_actual_material_state','person_authority_records'),[{}]),('review_fabricated',('empty_actual_material_state','review_decision_records'),[{}]),
('gap_fabricated',('empty_actual_material_state','gap_change_records'),[{}]),('inventory_zero',('empty_actual_material_state','actual_full_reference_inventory'),[]),
('evaluation_fabricated',('empty_actual_material_state','actual_evaluations'),1),('gap_as_permission',('missing_material_route','actual_provider_gap_report_or_new_action_authority'),{}),
('gap_as_infeasibility',('missing_material_route','gap_needs_separate_exact_work_authority_not_fabrication_contact_execution_or_global_infeasibility'),False),
('RT01_as_A01',('complete_A01_followthrough','receipt_or_integrity_or_RT01_acceptance_not_complete_A01_or_RQ02_authority'),False),
('RQ02_enabled',('complete_A01_followthrough','RQ02_or_downstream_enabled'),True),
('predictive_hash_allowed',('critical_boundaries','logical_scope_not_effective_W03_freeze_no_predictive_hash_or_unknown_zero'),False),
('acceptance_transfer',('critical_boundaries','changed_author_body_source_runtime_scope_epoch_key_policy_invalidates_affected_A01_A08_no_automatic_transfer'),False),
('free_costs_or_quota',('critical_boundaries','both_Readers_global_reference_native_IO_crypto_copy_ledger_output_failure_costs_caps_guards_quotas_reserves_unchanged'),False),
('receipt_precondition',('critical_boundaries','CE12_private_deferred_no_final_E06_Q_root_claim_spawn_receipt_as_new_entry_prelaunch_condition'),False),
('claim_self_condition',('critical_boundaries','four_external_prerequisites_before_claim_then_claim_construction_before_receipt_no_self_condition_or_free_retry'),False),
('run_command',('final_route_boundary','current_run_command'),'UNVERIFIED_TEST_LABEL'),('receipt_authorized',('final_route_boundary','actual_final_route_or_receipt_authorized'),True),
('A01_accepted',('current_effect','A01_accepted'),True),('D5_closed',('current_effect','D5_closed'),True),('assistant_independent',('producer','actor_independent'),True),
('publication_as_receipt',('publication','publication_not_receipt_genuine_authority_eligibility_review_acceptance_execution_or_D5_closure'),False)]


def rejections(d):
    results=[]
    for name,path,value in NEGATIVE_CASES:
        mutant=copy.deepcopy(d);node=mutant
        for key in path[:-1]:node=node[key]
        node[path[-1]]=value
        try:validate(mutant)
        except AssertionError:results.append(dict(case=name,result='REJECTED_DOCUMENTARY_MUTATION_IN_MEMORY'))
        else:raise AssertionError(name)
    return results


def build_review():
    d=rd(SUBJECT);validate(d)
    previous=runpy.run_path(str(ROOT/PRIOR_AUDIT));exists=Path.exists
    rec=previous['reconstruct']();assert rec==rd(PRIOR_RECON)
    review=previous['build_review'](rec);assert review==rd(PRIOR_REVIEW) and Path.exists is exists
    return dict(schema='d5.i273-preparation-review.v1',increment='I273',date=DATE,timezone='Europe/Madrid',base_commit=BASE,status=STATUS,subject=pin(SUBJECT),findings=[],
        counts=dict(input_pins=1162,worksheet_groups=5,worksheet_field_descriptions=sum(map(len,WORKSHEETS.values())),future_reception_steps=7,material_states=4,
            entry_subjects=3,subject_material_groups=7,universal_return_fields=8,information_sections=6,separation_requirements=14,RC_reconciliation_rows=16,
            full_A01_criteria=12,A01_deliverables=3,A01_exits=3,remaining_A01_returns=4,inherited_boundaries=9,critical_boundaries=24,
            documentary_rejections=len(NEGATIVE_CASES),preserved_published_files=854,new_files=5,actual_received_bodies=0,actual_receipts_or_genuine_acceptances_created=0,
            prelaunch_gates_closed=0,resource_obligations_closed=0),rejection_checks=rejections(d),
        source_reconstruction=dict(I271_request_A01_requirements_exact=True,I272_reconstruction_and_review_reproduced=True,prior_publication_mains_called=False,prior_Path_exists_restored=True,no_new_presence_projection=True),
        current_effect=d['current_effect'],limitations=['Empty local documentary worksheets prepare future recordkeeping only. No actual delivery/body/person/review/gap record,storage backend,material intake or verification authority is created.',
            'Receipt/provided state and raw byte integrity never prove authority/authorship/competence/independence/currentness. Canonical digests/signatures remain supplied claims until genuinely authorized verification; no codec/crypto runs here.',
            'Actual full reference inventory and external body count remain unknown. EA01/R06/R08 authority/eligibility and genuine primary/separate decisions missing,SD01 active,RQ01 unsent.',
            'RT01 does not complete RT02-RT05/A01 or enable RQ02.30 gates,E01-E05/PJC115-R2/D5 remain open;CE12/final route deferred,quotas/reserves/active authority/destinations unchanged.'],
        work_unit=dict(rollback_files=sorted(FILES),verification_command='python3 docs/validation/D5-I273-audit.py',expected_result=STATUS,over400_lines=True,
            reason='One empty RQ01/RT01 reception package with documentary worksheet descriptions,exact sources,pins,rejection checks and preservation; overage declared,no PR requested.',
            runtime_harness='N/A: own documentary JSON/Git/hash/pointer/coverage/graph checks and in-memory mutations only; no target import,compile,discovery,tests,execution,build,benchmark,codec,crypto,signing,keygen,enrollment,contacts,provision,configuration or platform/clock/CPU/IO/ledger/process/endpoint/replay/crash/restart probes.'),
        provenance=d['producer'],publication=d['publication'])


def main():
    d=rd(SUBJECT);validate(d);verify_blobs(d['input_pins'])
    review=build_review();assert review==rd(PREP)
    prior=rd(PRIOR_SEAL);preserved={**prior['preserved_published849'],**prior['artifacts'],PRIOR_SEAL:sha(PRIOR_SEAL)};assert len(preserved)==854
    seal=rd(SEAL);assert seal['schema']=='d5.i273-integrity.v1' and seal['base_commit']==BASE
    assert seal['preserved_published854']==preserved and set(seal['artifacts'])==FILES-{SEAL}
    for mapping in [preserved,seal['artifacts']]:
        for path,digest in mapping.items():assert sha(path)==digest,path
    assert seal['source_only'] is True and seal['current_effect']==d['current_effect']
    changed=set(git('diff',BASE,'--name-only').splitlines())|set(git('ls-files','--others','--exclude-standard').splitlines());assert changed==FILES,changed
    subprocess.check_call(['git','merge-base','--is-ancestor',BASE,'HEAD'],cwd=ROOT)
    if git('rev-parse','HEAD')!=BASE:assert not git('status','--porcelain')
    print(json.dumps(dict(status=STATUS,**review['counts'],D5_closed=False),sort_keys=True))


if __name__=='__main__':main()
