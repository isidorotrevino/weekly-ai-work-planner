#!/usr/bin/env python3
"""I255 A02/RQ02 preparation; own documentary checks, no component execution."""
import copy
import hashlib
import io
import json
from pathlib import Path
import runpy
import subprocess

ROOT = Path(__file__).resolve().parents[2]
P = 'docs/validation/'
BASE = '1f937a338aa4f89301930197bd4327d6d247a06d'
DATE = '2026-11-25'
PLAN = P+'D5-I223-PRELAUNCH-RESOURCE-CLOSURE-PLAN.json'
ACQUISITION = P+'D5-I251-GENUINE-EVIDENCE-ACQUISITION-PLAN.json'
W02 = P+'D5-I223-W02-PEOPLE-AND-ANCHORS-CANDIDATE.json'
A01 = P+'D5-I251-A01-RQ01-ENTRY-AUTHORITY-SCOPE-CANDIDATE.json'
PRIOR_RECON = P+'D5-I254-I253-source-reconstruction.json'
PRIOR_REVIEW = P+'D5-I254-I253-documentary-review.json'
PRIOR_AUDIT = P+'D5-I254-audit.py'
PRIOR_SEAL = P+'D5-I254-integrity.json'
PRIOR_DOC = 'docs/design/D5-I254-I253-A01-RQ01-REVIEW.md'
PRIOR_FILES = {PRIOR_RECON,PRIOR_REVIEW,PRIOR_AUDIT,PRIOR_SEAL,PRIOR_DOC}
SUBJECT = P+'D5-I251-A02-RQ02-PEOPLE-APPOINTMENTS-ANCHORS-CANDIDATE.json'
PREP = P+'D5-I255-preparation-review.json'
AUDIT = P+'D5-I255-audit.py'
SEAL = P+'D5-I255-integrity.json'
DOC = 'docs/design/D5-I255-A02-RQ02-PEOPLE-APPOINTMENTS-ANCHORS.md'
FILES = {SUBJECT,PREP,AUDIT,SEAL,DOC}
STATUS = 'PASS_STATIC_SOURCE_ONLY_A02_RQ02_PREPARED_A01_UNACCEPTED_PEOPLE_ANCHORS_MISSING_NOT_ADMITTED'


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


RETURNS = [
    ('IT01','Autoridad propia de identidad/anchors y antecedente A01',
     ['dependency_gate','costs_and_authority'],
     'Aportar autoridad auténtica independiente de identidad/anchors, su emisor/cadena/provenance, scope/competencia/vigencia/revocación y evidencia de A01/W01 ya aceptado genuinamente. La revisión documental I254 no lo acepta. No usar A02 o un futuro bundle para justificar retrospectivamente la autoridad de A01. Si falta A01, conservar SD01: no enviar, contactar, nominar, provisionar o aceptar intake.'),
    ('IT02','Humanos canónicos, aliases, organizaciones y categorías de sujetos',
     ['subject_category_inventory','identity_policy'],
     'Entregar evidencia genuina disponible de humanos canónicos, organizaciones y resolución íntegra de aliases/colisiones para sujetos conocidos: autores de fuentes, todos los preparadores documentales, requester, autores/providers de pruebas y signatarios. Separar humanos de principal software caller y de etiquetas Git/asistente. Declarar ausencias y nuevos sujetos; no inventar registros ni preaprobar futuros autores, no reclamar roster final.'),
    ('IT03','Competencia, appointments y claves por propósito de R01-R08',
     ['role_scope_matrix','identity_policy','overlap_policy'],
     'Para cada rol exacto R01-R08, aportar humano canónico/aliases, autoridad y appointment aceptado, evidencia de competencia para sus decisiones, scope/validez/revocación, clave/propósito y provenance. Un autor/provider no obtiene automáticamente R03/R06/R08. No se designa persona ni se crea una clave/appointment aquí; toda atribución requiere autoridad propia y cuerpo auténtico.'),
    ('IT04','Anchors independientes, política previa y currentness',
     ['anchor_policy','schema_policy'],
     'Aportar política previa externa y material genuino de origen/provisión/aceptación independiente, cuerpo disponible del registry y expected digest/epochs externos previos, bindings completos ordenados/únicos purpose/key_id/actor y propósito, vigencias/revocación/currentness/reloj confiable. Repo/C/bundle/root/clave suministrada o self-signature no son bootstrap de confianza. Política de selección role-domain/core/profile/pack/contract previa; tres aprobaciones reales del mismo core se difieren a W12. Conservar schemas cerrados/caps; no generar/verificar crypto, emitir snapshots o consultar servicios por este borrador.'),
    ('IT05','Comparaciones reales de separación y provenance de preparadores',
     ['separation_matrix','overlap_policy','preparation_tracking','phase_boundary'],
     'Aportar comparaciones trazables de las catorce reglas sobre humanos/aliases/claves genuinos y todas las contribuciones conocidas. R08 separado de preparadores/R03/R04/R06/R07/source-author y R01/R02 humanos y claves; issuer y acceptor keys distintos. R01/R02 sólo pueden coincidir como mismo humano cualificado con aprobaciones por dominio en su fase. Evidencia auténtica de contribución de todo preparador, sin deducir identidad humana de este asistente o hashes Git. Intake provisional; finalizar autores/registry en W10, sin backpins a C/acceptance/bundle/root.'),
    ('IT06','Inventario completo, revisión R06 y decisión separada R08',
     ['evidence_requirement_ledger','exit_predicate_dispositions','phase_boundary','costs_and_authority'],
     'Entregar cuerpos completos y disponibles por requisito/criterio, con locators inmutables, bytes/digests, autor/provider/custodia/provenance, scope/epoch/validez y todos los supuestos; registrar ausencias/rechazos. Revisión genuina R06 y aceptación/rechazo separado R08, con elegibilidad y motivo por requisito/salida sobre mismo material. No reemplazar pruebas por flags/firmas/índices; no truncar para caber ni omitir costes de ambos Readers y join global. El asistente/auditor no acepta personas, anchors o paquete.')]
REQUIREMENT_RETURNS = {
    'AP01':['IT01','IT04'],'AP02':['IT04'],'AP03':['IT02','IT03'],'AP04':['IT03','IT04'],
    'AP05':['IT06'],'AP06':['IT04'],'AP07':['IT04'],'AP08-ANCHOR-POLICY':['IT04'],
    'AP08-BUNDLE-APPROVAL':[],'AP09':['IT04','IT06'],
    'IR01':['IT02'],'IR02':['IT02'],'IR03':['IT03'],'IR04':['IT02'],'IR05':['IT02','IT03'],
    'IR06':['IT05'],'IR07':['IT05'],'IR08':['IT02','IT05'],'IR09':[]}
CRITERIA = [
    ('AC01','A01/W01 genuinamente aceptado con autoridad de entrada verificable; I253/I254 documentales no lo satisfacen y no hay autoridad retrospectiva.',['IT01']),
    ('AC02','Autoridad independiente de identidad/anchors auténtica con provenance/ámbito/validez/revocación y cuerpo disponible.',['IT01','IT04']),
    ('AC03','Humanos/organizaciones/aliases/colisiones resueltos por autoridad real en las cinco categorías, principal software separado y ausencias explícitas.',['IT02']),
    ('AC04','Cada R01-R08 tiene competencia/appointment/scope/validez/propósito/claves genuinos; autores/providers no se convierten automáticamente en revisores/aceptante.',['IT03']),
    ('AC05','Expected digest y epochs externos preexistentes y origen/provisión/aceptación previa de anchors independientes de repo/C/bundle/root; sin TOFU o self-bootstrap.',['IT04']),
    ('AC06','Bindings purpose/key_id ordenados/únicos con actor canónico, schemas/caps existentes y cuerpos completos, sin trimming o registry sintético.',['IT03','IT04']),
    ('AC07','Política previa de selección y dominios+NUL exacta, sin exigir las tres aprobaciones futuras W12 como antecedente de confianza.',['IT04']),
    ('AC08','Vigencia/currentness/revocación/epoch/reloj confiable exigibles; unknown/stale/superseded/revoked rechaza, fecha host no prueba frescura.',['IT04']),
    ('AC09','Catorce separaciones comprobadas con humanos/claves reales; coincidencia R01/R02 sólo cualificada y aprobaciones por dominio en su fase.',['IT03','IT05']),
    ('AC10','Provenance de todos los preparadores/contribuciones conocidos; no identidad inferida de asistente/Git ni preparación con backpins futuros.',['IT02','IT05']),
    ('AC11','Intake provisional sin roster/registry final ni preaprobación de futuros autores; autores/cuerpos auténticos antes W09, freeze final W10 no retrospectivo.',['IT02','IT05']),
    ('AC12','Inventario completo de cuerpos/referencias/bytes/digests/provenance/supuestos y costes globales, sin caps tomados como capacidad/CPU/900.',['IT04','IT06']),
    ('AC13','Revisión primaria R06 y decisión separada R08 genuinas y elegibles sobre el mismo scope/cuerpos, con motivos por requisitos/salidas.',['IT06']),
    ('AC14','Cambios/revocación invalidan afectados; sólo A02 genuinamente aceptado permite considerar A03 junto con A01, sin contacto/run ni cierre D5 automático.',['IT01','IT05','IT06'])]


def build_candidate():
    plan,acq,work=rd(PLAN),rd(ACQUISITION),rd(W02)
    lot=acq['acquisition_lots'][1]
    req=plan['work_packages'][1]
    assert lot['id']=='A02' and lot['depends_on_lots']==['A01'] and req['depends_on']==['W01']
    pins={**rd(PRIOR_RECON)['input_pins'],**{path:sha(path) for path in sorted(PRIOR_FILES)}}
    assert len(pins)==1072
    return dict(schema='d5.i255-a02-rq02-documentary-preparation.v1',increment='I255',date=DATE,timezone='Europe/Madrid',base_commit=BASE,
        dossier_id='PGE251-A02-RQ02-CANDIDATE-01',lot_id='A02',request_id='RQ02',work_package='W02',planned_deliverable_id=req['deliverable_id'],
        kind='CONDITIONAL_LOCAL_UNSENT_REQUEST_AND_PROVISIONAL_INTAKE_REQUIREMENTS_NOT_PEOPLE_APPOINTMENTS_ANCHORS_OR_RUNTIME_RECORDS',
        status='A02_RQ02_DOCUMENTARY_PREPARED_A01_UNACCEPTED_SD01_ACTIVE_NOT_ACCEPTED_NOT_ADMITTED',input_pins=pins,
        acquisition_lot_binding=pin(ACQUISITION,'/acquisition_lots/1'),exact_acquisition_lot=lot,
        work_requirement_binding=pin(PLAN,'/work_packages/1'),exact_W02_requirement=req,W02_documentary_checklist=pin(W02),
        prior_A01_review=pin(PRIOR_REVIEW),
        dependency_gate=dict(required_lot_ids=['A01'],required_work_package_ids=['W01'],
            W02_dependency_source=pin(W02,'/dependency_gate'),exact_W02_dependency_requirement=work['dependency_gate'],
            A01_source=pin(A01,'/current_effect'),exact_current_A01_effect=rd(A01)['current_effect'],
            A01_accepted=False,W01_accepted=False,SD01_stop_active=True,actual_genuine_A01_acceptance_body=None,
            no_documentary_I253_I254_PASS_as_A01_acceptance=True,
            preparing_A02_draft_does_not_start_positive_intake_send_contact_nomination_or_discharge_A01=True),
        unsent_request=dict(original_draft=lot['unsent_request_draft'],
            subject='RQ02 — Humanos canónicos, competencia, appointments y anchors / W02 / PGO181 candidato02',
            recipient_role_only=lot['intended_recipient_role_kind'],
            reviewable_request_text='Borrador condicionado a A01/W01 genuinamente aceptado. Solicitar entonces, sólo bajo autoridad propia y provenance autorizada, IT01-IT06: humanos canónicos/aliases/organizaciones y principal software separado; competencia/appointments/claves por propósito de R01-R08; anchors/política previa independientes con expected digest/epochs externos, cuerpos/validez/revocación/currentness; catorce comparaciones de separación y provenance de preparadores; revisión R06 y decisión separada R08. Aportar cuerpos completos, locators/bytes/digests/autor/provider/custodia y motivos por requisito. Declarar ausencias y gaps sin inventar personas/claves o aceptar hashes/firmas como verdad. Intake provisional: W10 finaliza roster/registry y W12 recibe aprobaciones reales del bundle, que no autentican sus propios anchors. No se solicita contacto a terceros, nominación, enrollment, provisión, keygen, firma, verificación crypto/servicios, snapshots, configuración o ejecución. A01 no está aceptado y este borrador no se envía.',
            required_return_ids=[r[0] for r in RETURNS],is_draft_only=True,sent=False,contact_authorized=False,
            actual_recipient_person=None,actual_address_or_channel=None,actual_contact_authority=None,actual_sending_or_delivery_record=None),
        requested_returns=[dict(id=rid,title=title,requirements=text,W02_requirement_sources=[pin(W02,'/'+key) for key in sections],
            universal_delivery_source=pin(ACQUISITION,'/evidence_delivery_contract'),
            actual_body_inventory=None,actual_received=False,actual_primary_review=None,actual_separate_acceptance=None,accepted=False)
            for rid,title,sections,text in RETURNS],
        role_evidence_requests=[dict(id=row['id'],source=pin(W02,'/role_scope_matrix/'+str(i)),exact_role_requirement=row,
            required_return_id='IT03',required_fields=['canonical human and aliases/organization','genuine authority,scope,competence and appointment body',
                'purpose/key/actor binding and independently accepted provenance','validity,currentness,revocation','real primary review and separate decision body'],
            actual_human_or_aliases=None,actual_competence_appointment_or_authority=None,actual_purpose_key_binding=None,
            actual_currentness_or_custody=None,actual_genuine_review_and_acceptance=None,accepted=False)
            for i,row in enumerate(work['role_scope_matrix'])],
        subject_category_requests=[dict(category=row['category'],source=pin(W02,'/subject_category_inventory/'+str(i)),exact_category_requirement=row,
            required_return_ids=['IT02','IT05'],actual_canonical_subjects_or_provenance=None,complete=False,accepted=False)
            for i,row in enumerate(work['subject_category_inventory'])],
        evidence_requirement_requests=[dict(id=row['id'],source=pin(W02,'/evidence_requirement_ledger/'+str(i)),
            normative_source=row['source'],required_genuine_evidence=row['exact_requirement']['required_genuine_evidence'],
            consumer_step=row['consumer_step'],work_package_consumer=row['work_package_consumer'],deferred_from_A02=row['deferred_from_W02'],
            required_return_ids=REQUIREMENT_RETURNS[row['id']],
            source_historical_metadata_not_reinterpreted_as_current_document_presence_or_actual_acceptance=True,
            actual_body_bytes_digest_locator_author_provider_custody=None,actual_review_and_acceptance=None,accepted=False)
            for i,row in enumerate(work['evidence_requirement_ledger'])],
        inherited_policies={key:dict(source=pin(W02,'/'+key),exact_requirement=work[key]) for key in
            ['anchor_policy','identity_policy','separation_matrix','overlap_policy','schema_policy','phase_boundary','costs_and_authority','preserved_scope_and_gates']},
        authority_and_phase_rules=dict(
            anchor_expected_digest_epochs_and_policy_preexist_supplied_registry_not_repo_C_bundle_root_or_supplied_key=True,
            prior_independent_anchor_provisioning_and_acceptance_genuinely_required_not_done_here=True,
            AP08_ANCHOR_POLICY_is_prior_policy_AP08_BUNDLE_APPROVAL_deferred_to_W12_not_A02_dependency=True,
            IR01_IR08_provisional_IR09_final_completeness_W10_not_A02_dependency=True,
            real_W05_W08_authors_and_bodies_authenticated_before_W09_W10_not_retroactive=True,
            no_future_authors_preapproved_no_final_actor_registry_or_positive_preparation_record_created=True,
            actual_currentness_not_host_date_no_TOFU_stale_cache_network_file_or_environment_bootstrap=True,
            future_fresh_snapshots_only_when_evidence_ready_under_separate_authority=True,
            no_new_identity_anchor_signing_crypto_enrollment_contact_provisioning_or_configuration_authority=True,
            no_actual_clock_crypto_codec_snapshot_registry_or_service_check_performed=True),
        documentary_contribution_tracking=dict(activity='Same Codex assistant/chat prepared I255 documentary files',files=sorted(FILES),
            W02_tracking_source=pin(W02,'/preparation_tracking'),
            actual_accountable_canonical_human=None,actual_authorship_evidence_or_appointment=None,actual_positive_preparation_record=None,
            git_hashes_or_assistant_label_not_canonical_human_provenance=True,full_preparer_list_or_final_completeness_claimed=False,
            no_backpin_C_acceptance_bundle_future_root=True),
        W02_deliverable_coverage=[dict(id='WD%02d'%(i+1),source=pin(PLAN,'/work_packages/1/deliverables/'+str(i)),exact_requirement=text,
            required_return_ids=[['IT02','IT03','IT05'],['IT04'],['IT05']][i],authority_return_id='IT01',review_return_id='IT06',
            actual_complete_delivery=None,accepted=False) for i,text in enumerate(req['deliverables'])],
        acceptance_checklist=[dict(id=cid,criterion=text,required_return_ids=ids,
            actual_evidence_inventory=None,actual_R06_primary_review=None,actual_R08_separate_decision=None,
            disposition='PENDING_A01_GENUINE_MATERIAL_AND_COMPETENT_DECISION',accepted=False) for cid,text,ids in CRITERIA],
        W02_exit_coverage=[dict(id='WX%02d'%(i+1),source=pin(PLAN,'/work_packages/1/exit_predicates/'+str(i)),exact_predicate=text,
            required_acceptance_criteria=[c[0] for c in CRITERIA],actual_genuine_disposition=None,accepted=False) for i,text in enumerate(req['exit_predicates'])],
        intake_sequence=[
            'Mantener SD01: preparar sólo documentos; no enviar RQ02 ni recibir/aceptar positivamente A02 por un PASS de A01 documental.',
            'Sólo tras A01 genuino bajo su propia autoridad, considerar material genuinamente aportado con provenance propia. Envío/contacto requieren autoridad específica separada.',
            'Inventariar cuerpos completos, instancias de referencia, autores/providers/custodia/scope/validez/supuestos y ausencias/rechazos; verificar autoridad externa previa sin bootstrap circular.',
            'Revisar evidencia AP previa de anchors y política independientemente de aprobaciones futuras W12; intake IR01-IR08 de sujetos conocidos sin finalizar IR09/W10.',
            'Obtener R06 genuino y R08 separado sobre AC01-AC14 y salidas W02; este asistente/auditor no decide aceptación ni ejecuta crypto/lookup.',
            'Reconciliar epoch/currentness/revocación y cambios de identidad/autor/preparador/política/cuerpo antes de dependientes; A03 sólo se considera con A01 y A02 genuinos.'],
        missing_material=dict(current_disposition='BLOCKED_A01_MISSING_GENUINE_IDENTITY_ANCHOR_MATERIAL_NOT_RECEIVED_NOT_EVALUATED',
            actual_received_inventory=None,provided_real_bodies=[],rejected_real_bodies=[],actual_evaluations=0,
            actual_people_appointments_keys_or_anchors=None,actual_provider_or_schedule=None,
            missing_or_ambiguous_authority_body_alias_eligibility_currentness_keeps_no_admission=True,
            no_global_absence_or_infeasibility_claim=True),
        preserved_resource_rules=dict(source=pin(ACQUISITION,'/preserved_resource_and_cost_rules'),exact_requirement=acq['preserved_resource_and_cost_rules'],
            complete_bodies_and_all_costs_in_both_Readers_and_global_join_not_free_offline_work=True,
            schemas_or_caps_not_actual_heap_CPU_capacity_service_or900_fit=True,
            no_truncation_or_new_Reader_member_output_helper_hidden_lookup_or_quota_reserve_change=True),
        handoff=dict(exact_A02_completion_predicate=lot['completion_predicate'],exact_A02_missing_stop=lot['missing_or_failure_stop'],
            next_lot='A03',required_genuine_prior_lots=['A01','A02'],A03_or_RQ03_started_sent_or_accepted=False,
            actual_A02_completion_or_independent_acceptance=None,actual_final_roster_registry_anchors_or_snapshots_created=False,
            final_route_source=pin(PLAN,'/prelaunch_handoff_and_CE12'),exact_final_route_boundary=plan['prelaunch_handoff_and_CE12'],
            prelaunch_not_conditioned_on_actual_final_E06_payload_Q_root_admission_claim_receipt=True,
            no_automatic_launch_certificate_PJC115_R2_or_D5_release=True),
        change_control=dict(source=pin(W02,'/phase_boundary'),exact_requirement=work['phase_boundary'],
            changed_subject_alias_author_preparer_source_runtime_body_key_epoch_policy_revocation_invalidates_affected_reviews_before_progress=True,
            no_automatic_old_approval_proof_or_appointment_transfer=True,actual_refresh_or_active_rebind=False),
        current_effect={**rd(A01)['current_effect'],'A02_RQ02_documentary_prepared':True,'A02_accepted':False,'RQ02_sent':False,
            'actual_people_anchors_appointments_or_key_bindings_accepted':False,'actor_registry_finalized':False,'anchor_registry_provisioned':False,
            'actual_A02_intake_progress_or_review_records_created':False},
        producer=dict(identity='Same Codex assistant/chat as I253/I254',documentary_preparer_only=True,actor_independent=False,
            competent_R06_review=False,separate_R08_acceptance=False,external_contacts_made=False),
        publication=dict(commit_and_push_requested=True,publication_not_A01_A02_acceptance_people_appointment_anchor_authority_execution_or_D5_closure=True))


NEGATIVE_CASES = [
    ('A01_promoted',('dependency_gate','A01_accepted'),False,True),
    ('W01_promoted',('dependency_gate','W01_accepted'),False,True),
    ('SD01_bypassed',('dependency_gate','SD01_stop_active'),True,False),
    ('documentary_pass_as_acceptance',('dependency_gate','no_documentary_I253_I254_PASS_as_A01_acceptance'),True,False),
    ('positive_intake_started',('dependency_gate','preparing_A02_draft_does_not_start_positive_intake_send_contact_nomination_or_discharge_A01'),True,False),
    ('request_sent',('unsent_request','sent'),False,True),
    ('contact_granted',('unsent_request','contact_authorized'),False,True),
    ('recipient_fabricated',('unsent_request','actual_recipient_person'),None,'UNVERIFIED_TEST_LABEL'),
    ('material_received',('requested_returns',3,'actual_received'),False,True),
    ('human_fabricated',('role_evidence_requests',0,'actual_human_or_aliases'),None,'UNVERIFIED_TEST_LABEL'),
    ('appointment_fabricated',('role_evidence_requests',5,'actual_competence_appointment_or_authority'),None,{}),
    ('role_accepted',('role_evidence_requests',7,'accepted'),False,True),
    ('category_complete',('subject_category_requests',1,'complete'),False,True),
    ('proof_body_fabricated',('evidence_requirement_requests',0,'actual_body_bytes_digest_locator_author_provider_custody'),None,{}),
    ('historical_metadata_as_current_presence',('evidence_requirement_requests',8,'source_historical_metadata_not_reinterpreted_as_current_document_presence_or_actual_acceptance'),True,False),
    ('self_bootstrap',('authority_and_phase_rules','anchor_expected_digest_epochs_and_policy_preexist_supplied_registry_not_repo_C_bundle_root_or_supplied_key'),True,False),
    ('prior_anchor_acceptance_waived',('authority_and_phase_rules','prior_independent_anchor_provisioning_and_acceptance_genuinely_required_not_done_here'),True,False),
    ('bundle_approval_as_prior_anchor',('authority_and_phase_rules','AP08_ANCHOR_POLICY_is_prior_policy_AP08_BUNDLE_APPROVAL_deferred_to_W12_not_A02_dependency'),True,False),
    ('final_roster_required_early',('authority_and_phase_rules','IR01_IR08_provisional_IR09_final_completeness_W10_not_A02_dependency'),True,False),
    ('late_authentication',('authority_and_phase_rules','real_W05_W08_authors_and_bodies_authenticated_before_W09_W10_not_retroactive'),True,False),
    ('future_authors_preapproved',('authority_and_phase_rules','no_future_authors_preapproved_no_final_actor_registry_or_positive_preparation_record_created'),True,False),
    ('host_date_as_freshness',('authority_and_phase_rules','actual_currentness_not_host_date_no_TOFU_stale_cache_network_file_or_environment_bootstrap'),True,False),
    ('crypto_check_performed',('authority_and_phase_rules','no_actual_clock_crypto_codec_snapshot_registry_or_service_check_performed'),True,False),
    ('assistant_human_fabricated',('documentary_contribution_tracking','actual_accountable_canonical_human'),None,'UNVERIFIED_TEST_LABEL'),
    ('full_preparers_claimed',('documentary_contribution_tracking','full_preparer_list_or_final_completeness_claimed'),False,True),
    ('preparation_record_backpin',('documentary_contribution_tracking','no_backpin_C_acceptance_bundle_future_root'),True,False),
    ('criterion_accepted',('acceptance_checklist',12,'accepted'),False,True),
    ('exit_accepted',('W02_exit_coverage',2,'accepted'),False,True),
    ('inventory_fabricated',('missing_material','actual_received_inventory'),None,[]),
    ('reference_costs_free',('preserved_resource_rules','complete_bodies_and_all_costs_in_both_Readers_and_global_join_not_free_offline_work'),True,False),
    ('quota_increased',('preserved_resource_rules','no_truncation_or_new_Reader_member_output_helper_hidden_lookup_or_quota_reserve_change'),True,False),
    ('A03_started',('handoff','A03_or_RQ03_started_sent_or_accepted'),False,True),
    ('actual_snapshot_created',('handoff','actual_final_roster_registry_anchors_or_snapshots_created'),False,True),
    ('final_execution_precondition',('handoff','prelaunch_not_conditioned_on_actual_final_E06_payload_Q_root_admission_claim_receipt'),True,False),
    ('silent_acceptance_transfer',('change_control','no_automatic_old_approval_proof_or_appointment_transfer'),True,False),
    ('active_rebind',('change_control','actual_refresh_or_active_rebind'),False,True),
    ('A02_accepted',('current_effect','A02_accepted'),False,True),
    ('D5_closed',('current_effect','D5_closed'),False,True),
    ('independent_assistant',('producer','actor_independent'),False,True)]


def validate(d):
    for name,path,expected,_ in NEGATIVE_CASES:
        node=d
        for key in path:
            node=node[key]
        assert type(node) is type(expected) and node==expected,name
    assert d==build_candidate(),'A02/RQ02 differs from exact documentary reconstruction'
    pointers(d)


def rejection_checks(d):
    results=[]
    for name,path,_,value in NEGATIVE_CASES:
        mutant=copy.deepcopy(d)
        node=mutant
        for key in path[:-1]:
            node=node[key]
        node[path[-1]]=value
        try:
            validate(mutant)
        except AssertionError as error:
            assert str(error)==name,(name,str(error))
            results.append(dict(case=name,result='REJECTED_DOCUMENTARY_MUTATION_IN_MEMORY'))
        else:
            raise AssertionError(name)
    return results


def build_review():
    d=rd(SUBJECT)
    validate(d)
    verify_blobs(d['input_pins'])
    previous=runpy.run_path(str(ROOT/PRIOR_AUDIT))
    exists=Path.exists
    rec=previous['reconstruct']()
    assert rec==rd(PRIOR_RECON) and previous['build_review'](rec)==rd(PRIOR_REVIEW)
    assert Path.exists is exists
    assert [r['id'] for r in d['role_evidence_requests']]==['R%02d'%i for i in range(1,9)]
    assert len(d['subject_category_requests'])==5 and len(d['evidence_requirement_requests'])==19
    active=[r for r in d['evidence_requirement_requests'] if not r['deferred_from_A02']]
    deferred=[r for r in d['evidence_requirement_requests'] if r['deferred_from_A02']]
    assert len(active)==17 and [r['id'] for r in deferred]==['AP08-BUNDLE-APPROVAL','IR09']
    assert [r['work_package_consumer'] for r in deferred]==['W12','W10']
    assert all(r['required_return_ids'] and r['work_package_consumer']=='W02' for r in active)
    assert all(not r['required_return_ids'] for r in deferred)
    assert len(d['requested_returns'])==6 and len(d['acceptance_checklist'])==14
    assert len(d['W02_deliverable_coverage'])==len(d['W02_exit_coverage'])==3
    assert len(d['inherited_policies']['separation_matrix']['exact_requirement'])==14
    sources=rd(P+'D5-I191-CALLER-IMAGE-CUSTODY-SCHEMAS-CANDIDATE.json')['$defs']['source_bindings']['required']
    assert all(not (ROOT/path).exists() for path in sources)
    bindings=rd(P+'D5-I193-CE11-PRELAUNCH-EVIDENCE-CLOSURE-REVIEW-CANDIDATE.json')['pending_I177_final_bindings']
    assert all(not (ROOT/row['path']).exists() for row in bindings)
    return dict(schema='d5.i255-preparation-review.v1',increment='I255',date=DATE,timezone='Europe/Madrid',base_commit=BASE,status=STATUS,
        candidate=pin(SUBJECT),counts=dict(input_pins=1072,roles=8,subject_categories=5,evidence_requirements=19,active_A02_requirements=17,
            deferred_requirements=2,separation_requirements=14,requested_returns=6,acceptance_criteria=14,W02_deliverables=3,W02_exits=3,
            actual_people_or_anchors_accepted=0,actual_received_bodies=0,actual_lots_accepted=0),
        rejection_checks=rejection_checks(d),current_effect=d['current_effect'],provenance=d['producer'],
        source_reconstruction=dict(I254_reconstruction_and_review_reproduced=True,prior_publication_mains_called=False,prior_Path_exists_restored=True,no_new_presence_projection=True),
        limitations=['A01/W01 remains genuinely unaccepted and SD01 active. User authorizes preparing this conditional draft,not sending/contacting or positive A02 intake.',
            'No canonical human,alias,appointment,competence,key,anchor,registry,clock/currentness,snapshot,review or acceptance is fabricated. Six returns and fourteen criteria remain requirements only.',
            'Prior independent anchors/policy remain genuine requirements. Actual bundle approvals belong to W12; final actor completeness belongs to W10. Existing CE dossiers are documentary and do not supply material.',
            'No authority,product/component execution,build,crypto,contact,provisioning,configuration,claim,receipt,quota,reserve,binding or D5 change.'],
        work_unit=dict(rollback_files=sorted(FILES),verification_command='python3 docs/validation/D5-I255-audit.py',expected_result=STATUS,
            runtime_harness='N/A: own documentary JSON/Git/hash/pointer/coverage/phase checks and in-memory documentary mutations only; no target import/compile/discovery/tests/execution/build/benchmark/crypto/signing/keygen/enrollment/provisioning/contacts/platform/clock/CPU/IO/ledger/process/endpoint probes or configuration.',
            over400_lines=True,reason='Single conditional A02/RQ02 preparation with source pins,intake/deferred requirements,reviewable request,rejection checks and preservation; overage declared,no PR requested.'),
        publication=dict(commit_and_push_requested=True,publication_not_A01_A02_acceptance_authority_or_execution=True))


def main():
    review=build_review()
    assert review==rd(PREP)
    prior=rd(PRIOR_SEAL)
    preserved={**prior['preserved_published759'],**prior['artifacts'],PRIOR_SEAL:sha(PRIOR_SEAL)}
    assert len(preserved)==764
    seal=rd(SEAL)
    assert seal['schema']=='d5.i255-integrity.v1' and seal['base_commit']==BASE
    assert seal['preserved_published764']==preserved and set(seal['artifacts'])==FILES-{SEAL}
    for mapping in [preserved,seal['artifacts']]:
        for path,digest in mapping.items():
            assert sha(path)==digest,path
    assert seal['source_only'] is True and seal['current_effect']==review['current_effect']
    changed=set(git('diff',BASE,'--name-only').splitlines())|set(git('ls-files','--others','--exclude-standard').splitlines())
    assert changed==FILES,changed
    subprocess.check_call(['git','merge-base','--is-ancestor',BASE,'HEAD'],cwd=ROOT)
    if git('rev-parse','HEAD')!=BASE:
        assert not git('status','--porcelain')
    print(json.dumps(dict(status=STATUS,increment='I255',input_pins=1072,preserved_published_files=764,new_files=5,
        documentary_rejections=len(review['rejection_checks']),counts=review['counts'],SD01_stop_active=True,
        prelaunch_gates_closed=0,resource_obligations_closed=0,D5_closed=False,git_head=git('rev-parse','HEAD')),sort_keys=True))


if __name__=='__main__':
    main()
