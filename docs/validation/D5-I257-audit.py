#!/usr/bin/env python3
"""I257 A03/RQ03 documentary preparation; no target or component execution."""
import copy
import hashlib
import io
import json
from pathlib import Path
import runpy
import subprocess

ROOT = Path(__file__).resolve().parents[2]
P = 'docs/validation/'
BASE = '9b42ad4cb935a37266ab29dc08bb64eba6421563'
DATE = '2026-11-25'
PLAN = P+'D5-I223-PRELAUNCH-RESOURCE-CLOSURE-PLAN.json'
ACQUISITION = P+'D5-I251-GENUINE-EVIDENCE-ACQUISITION-PLAN.json'
W03 = P+'D5-I223-W03-SOURCES-IMAGE-RUNTIME-CANDIDATE.json'
A02 = P+'D5-I251-A02-RQ02-PEOPLE-APPOINTMENTS-ANCHORS-CANDIDATE.json'
PRIOR_RECON = P+'D5-I256-I255-source-reconstruction.json'
PRIOR_REVIEW = P+'D5-I256-I255-documentary-review.json'
PRIOR_AUDIT = P+'D5-I256-audit.py'
PRIOR_SEAL = P+'D5-I256-integrity.json'
PRIOR_DOC = 'docs/design/D5-I256-I255-A02-RQ02-REVIEW.md'
PRIOR_FILES = {PRIOR_RECON,PRIOR_REVIEW,PRIOR_AUDIT,PRIOR_SEAL,PRIOR_DOC}
SUBJECT = P+'D5-I251-A03-RQ03-SOURCES-IMAGE-RUNTIME-CANDIDATE.json'
PREP = P+'D5-I257-preparation-review.json'
AUDIT = P+'D5-I257-audit.py'
SEAL = P+'D5-I257-integrity.json'
DOC = 'docs/design/D5-I257-A03-RQ03-SOURCES-IMAGE-RUNTIME.md'
FILES = {SUBJECT,PREP,AUDIT,SEAL,DOC}
STATUS = 'PASS_STATIC_SOURCE_ONLY_A03_RQ03_PREPARED_PREDECESSORS_UNACCEPTED_SOURCES_IMAGE_RUNTIME_MISSING_NOT_ADMITTED'


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
    ('SR01','Antecedentes A01/A02 y autoridad genuina de proveedor/custodia',
     ['dependency_gate','role_scope_matrix','authority_and_costs'],
     'Aportar aceptación genuina de A01/W01 y A02/W02, autoridad/identidad/competencia/appointment/provenance de autores reales y R01/R06/R08, con scope/vigencia/custodia y cuerpos disponibles. La revisión documental I256 no acepta A02. No contactar, nominar o aceptar material positivamente mientras falten antecedentes; A03 no autentica retrospectivamente A01/A02.'),
    ('SR02','Seis fuentes existentes y mapping completo source-to-image',
     ['source_to_image_missing_inventory','source_scope_policy','image_source_requirement_ledger'],
     'Entregar si existen seis cuerpos reales completos ya calificados, logical paths exactos, bytes/digests físicos, source_root/versión/autores y provenance genuina de cualificación; mapping por fuente a miembro/representación/digest y prueba disponible. README es DOCUMENT; pertenencia de tests/runner no acredita carga/import/ejecución. Techo262144 a revalidar, no sumar ausencias como cero ni transferir I122. Si no existen, declarar SR06 sin crear sustitutos.'),
    ('SR03','Imagen externa, clausura runtime y provenance de build',
     ['actual_image_runtime_state','runtime_identity_boundary','runtime_platform_reference_boundary','closure_requirement_ledger','schema_obligations'],
     'Aportar digest/bytes de imagen auténtica externa separado de identidad runtime completa y su evidencia P02 compatible con P03/scope. Incluir intérprete/version/config/ABI, loader/import resolución, stdlib/builtin/frozen/native/crypto/transitivas, allocator/GC/kernel/servicio/clock/process domains y receta/toolchain/source-binary-image equivalencia. Dependencias completas, ordenadas/únicas, sin recortar a128 o usar Python/OS del auditor como target. No construir, medir, importar, compilar o ejecutar imagen/runtime para rellenar el dossier.'),
    ('SR04','Implementación de políticas y baseline de entrada inmutable',
     ['compiled_policy_requirements','no_self_embedding_policy','implementation_proof_boundary','image_source_requirement_ledger','phase_boundary'],
     'Aportar prueba genuina existente sobre los seis fuentes/imagen de que implementan exactamente las siete políticas profile/protocol/output/transport/grammar/custody pack/contract seleccionadas externamente, no sólo constantes coincidentes. No propio digest futuro imagen/manifest/bundle embebido. Probar baseline de miembro/origen de primera entrada inmutable antes de código no confiable; no sustituye caller/constructor/enforcement W04, recursos W05-W09 o freeze W10, ni los exige como nueva dependencia inversa.'),
    ('SR05','Cuerpos completos, revisión R01/R06 y decisión separada R08',
     ['role_scope_matrix','exit_predicate_dispositions','authority_and_costs','phase_boundary'],
     'Inventario completo de cuerpos/referencias/bytes/digests/locators/autores/providers/custodia/provenance/validez, derivaciones y todos los supuestos sobre mismo scope. R01/R06 competentes revisan y R08 elegible separado acepta/rechaza con motivo por requisito/salida. Baseline/autores auténticos antes de W09; W10 reconcilia mismos hechos sin autenticación retrospectiva. Ambos Readers y join global pagan costes completos; hashes/documentos/caps/PASS no prueban verdad o fit.'),
    ('SR06','Declaración trazable de material ausente y alcance separado pendiente',
     ['source_to_image_missing_inventory','authority_and_costs','phase_boundary'],
     'Si falta cualquier cuerpo/correspondencia/provenance/cualificación/autoridad, identificar el gap exacto, requisito afectado, dependientes y trabajo separado de implementación/build/cualificación/medición o autoridad que haría falta; no ejecutar, designar proveedor, dar fechas, presupuesto nuevo o hashes predictivos. Registrar material aportado sin aceptar/rechazado/ausente con motivo. Un informe de gaps nunca acepta A03 ni prueba ausencia global o inviabilidad.')]
CRITERIA = [
    ('AC01','A01/W01 y A02/W02 aceptados genuinamente y autoridad de proveedor/autores/custodios elegibles; PASS documental no antecedente positivo.',['SR01']),
    ('AC02','Los seis cuerpos reales disponibles ya calificados con paths/digests/bytes/source_root/versión/autores/provenance exactos, sin fuente predictiva o I122 transferido.',['SR02']),
    ('AC03','Mapping completo de seis fuentes a miembros/representación/digests; README DOCUMENT y no carga/import/ejecución inferida de pertenencia tests/runner.',['SR02']),
    ('AC04','Techo de fuentes262144 revalidado sobre bytes completos, ningún dato ausente=0, helper/lectura fuera de histórico480+seis o scope silenciosamente ampliado.',['SR02','SR03']),
    ('AC05','Digest de imagen auténtica externa separado de identidad runtime/P02 y evidencia de compatibilidad P03/scope; host/auditor o imagen sola no target.',['SR03']),
    ('AC06','Ocho clases CL de clausura completas con ABI/config/loader/stdlib/frozen/native/crypto/allocator/GC/kernel/toolchain y equivalencia source-binario-imagen.',['SR03']),
    ('AC07','Dependencias completas ordenadas/únicas con cuerpos y provenance, sin truncar a128, fit de índice no fit de evidencia o recursos.',['SR03','SR05']),
    ('AC08','Selección externa y conformidad real de siete políticas exactas, no constantes/hashes documentales o selección desde propio bundle.',['SR04']),
    ('AC09','Sin digest propio futuro imagen/manifest/bundle embebido, imagen esperada elegida externamente bajo custodia aceptada.',['SR04']),
    ('AC10','IM01-IM06 baseline genuino incluida entrada inmutable; IM07-IM10 diferidos a sus consumidores, sin sustituir enforcement/plataforma/recursos/freeze ni depender de su aceptación futura.',['SR02','SR03','SR04']),
    ('AC11','Artefactos y cualificación existentes con autoridad/provenance; si faltan, SR06 y no admisión, ninguna implementación/build/run/medición autorizada por ausencia.',['SR02','SR06']),
    ('AC12','Cuerpos/referencias/provenance/derivaciones/supuestos completos, costes globales ambos Readers, sin presupuesto/cap/index/hashes como capacidad/servicio/900.',['SR03','SR05']),
    ('AC13','Autores y baseline auténticos antes W09; freeze W10 posterior reconcilia mismos hechos sin completitud anticipada o autoridad retrospectiva.',['SR01','SR04','SR05']),
    ('AC14','Revisiones genuinas R01/R06 y decisión separada R08 elegibles sobre mismos cuerpos/scope con motivo por requisito/salida, no mismo asistente como independiente.',['SR05']),
    ('AC15','Cambios de autor/body/source/image/runtime/epoch/key/policy/validez invalidan afectados y requieren nueva revisión sin transferir aceptación o rebind activo.',['SR01','SR05','SR06']),
    ('AC16','Sólo A03 genuinamente aceptado permite considerar A04 con A02; no envío/contacto/run ni promoción de cuotas/certificado/PJC115-R2/D5, CE12 diferido.',['SR05','SR06'])]


def build_candidate():
    plan,acq,w=rd(PLAN),rd(ACQUISITION),rd(W03)
    lot,req=acq['acquisition_lots'][2],plan['work_packages'][2]
    assert lot['depends_on_lots']==['A01','A02'] and req['depends_on']==['W01','W02']
    pins={**rd(PRIOR_RECON)['input_pins'],**{path:sha(path) for path in sorted(PRIOR_FILES)}}
    assert len(pins)==1082
    return dict(schema='d5.i257-a03-rq03-documentary-preparation.v1',increment='I257',date=DATE,timezone='Europe/Madrid',base_commit=BASE,
        dossier_id='PGE251-A03-RQ03-CANDIDATE-01',lot_id='A03',request_id='RQ03',work_package='W03',planned_deliverable_id=req['deliverable_id'],
        kind='CONDITIONAL_LOCAL_UNSENT_REQUEST_FOR_EXISTING_QUALIFIED_SOURCES_IMAGE_RUNTIME_OR_GAP_REPORT_NOT_IMPLEMENTATION_OR_RUNTIME_RECORD',
        status='A03_RQ03_DOCUMENTARY_PREPARED_A01_A02_UNACCEPTED_SD01_ACTIVE_NOT_ACCEPTED_NOT_ADMITTED',input_pins=pins,
        acquisition_lot_binding=pin(ACQUISITION,'/acquisition_lots/2'),exact_acquisition_lot=lot,
        W03_requirement_binding=pin(PLAN,'/work_packages/2'),exact_W03_requirement=req,W03_documentary_checklist=pin(W03),prior_A02_review=pin(PRIOR_REVIEW),
        dependency_gate=dict(required_lot_ids=['A01','A02'],required_work_package_ids=['W01','W02'],
            source=pin(W03,'/dependency_gate'),exact_requirement=w['dependency_gate'],
            A02_state_source=pin(A02,'/current_effect'),exact_prior_effect=rd(A02)['current_effect'],
            A01_accepted=False,A02_accepted=False,W01_accepted=False,W02_accepted=False,SD01_stop_active=True,
            actual_genuine_antecedent_acceptance_bodies=None,no_documentary_PASS_as_genuine_antecedent=True,
            no_send_contact_nomination_or_positive_intake_from_preparing_this_draft=True),
        unsent_request=dict(original_draft=lot['unsent_request_draft'],subject='RQ03 — Fuentes, imagen y runtime / W03 / PGO181 candidato02',
            recipient_role_only=lot['intended_recipient_role_kind'],
            reviewable_request_text='Borrador condicionado a A01 y A02 genuinamente aceptados. Aportar sólo si existen bajo autoridad propia los seis fuentes efectivos ya calificados, imagen externa auténtica e identidad/clausura runtime separada, mappings/source_root y provenance completa de build/cualificación. Devolver SR01-SR05 con cuerpos/locators/bytes/digests/autores/providers/custodia/validez, evidencia de las políticas seleccionadas externamente y baseline inmutable, revisiones R01/R06 y decisión separada R08. README DOCUMENT; pertenencia tests/runner no implica carga. Si falta material, devolver SR06 con gaps y alcance/autoridad separados necesarios; no crear sustitutos. No se solicita implementar,build,medir,importar,compilar,ejecutar,cualificar,firmar,contactar terceros o configurar nada. IM07-IM10 siguen en sus fases. A01/A02 no están aceptados y RQ03 no se envía.',
            required_return_ids=[r[0] for r in RETURNS],is_draft_only=True,sent=False,contact_authorized=False,
            actual_recipient_person=None,actual_address_or_channel=None,actual_contact_authority=None,actual_delivery_or_receipt=None),
        requested_returns=[dict(id=rid,title=title,requirements=text,W03_requirement_sources=[pin(W03,'/'+key) for key in sections],
            universal_delivery_source=pin(ACQUISITION,'/evidence_delivery_contract'),actual_body_inventory=None,
            actual_received=False,actual_primary_reviews=None,actual_separate_acceptance=None,accepted=False)
            for rid,title,sections,text in RETURNS],
        source_requests=[dict(logical_path=row['logical_path'],source=pin(W03,'/source_to_image_missing_inventory/'+str(i)),
            required_representation=row['required_representation'],allowed_representation_policy=row['allowed_representation_policy'],
            required_return_id='SR02',actual_path_exists=False,actual_body_bytes_digest_source_root_author_or_custody=None,
            actual_image_member_representation_digest_mapping=None,actual_loaded_or_qualified_evidence=None,loaded_by_membership_claimed=False,accepted=False)
            for i,row in enumerate(w['source_to_image_missing_inventory'])],
        closure_requests=[dict(id=row['id'],source=pin(W03,'/closure_requirement_ledger/'+str(i)),kind=row['kind'],required_evidence=row['required_evidence'],
            required_return_id='SR03',actual_complete_inventory_body_digests_provenance_or_equivalence=None,accepted=False)
            for i,row in enumerate(w['closure_requirement_ledger'])],
        image_baseline_and_deferred_requests=[dict(id=row['id'],source=pin(W03,'/image_source_requirement_ledger/'+str(i)),normative_source=row['source'],
            required_genuine_evidence=row['exact_requirement']['required_genuine_evidence'],consumer_step=row['consumer_step'],
            work_package_consumers=row['work_package_consumers'],deferred_from_A03=row['deferred_from_W03'],
            required_return_ids={'IM01':['SR02'],'IM02':['SR02'],'IM03':['SR03'],'IM04':['SR03'],'IM05':['SR04'],'IM06':['SR04'],
                'IM07':[],'IM08':[],'IM09':[],'IM10':[]}[row['id']],
            actual_body_inventory_or_provenance=None,actual_primary_reviews_or_separate_acceptance=None,accepted=False)
            for i,row in enumerate(w['image_source_requirement_ledger'])],
        compiled_policy_requests=[dict(image_field=row['image_field'],source=pin(W03,'/compiled_policy_requirements/'+str(i)),
            documentary_binding=row['documentary_binding'],required_candidate_policy_sha256=row['required_candidate_policy_sha256'],
            required_return_id='SR04',actual_compiled_value_or_independent_selection_or_conformance_proof=None,accepted=False)
            for i,row in enumerate(w['compiled_policy_requirements'])],
        inherited_policies={key:dict(source=pin(W03,'/'+key),exact_requirement=w[key]) for key in
            ['source_scope_policy','runtime_identity_boundary','runtime_platform_reference_boundary','no_self_embedding_policy','implementation_proof_boundary',
             'schema_obligations','phase_boundary','authority_and_costs','preserved_scope_and_gates','role_scope_matrix']},
        material_routes=dict(existing_material=dict(condition='Genuinely supplied existing qualified complete artifacts with own authorized provenance and accepted predecessors.',
            required_returns=['SR01','SR02','SR03','SR04','SR05'],actual_delivery_inventory=None,actual_route_accepted=False),
            missing_material=dict(condition='Any absent body,unproved source/runtime/image correspondence,qualification,provenance or authority.',
                required_return_id='SR06',exact_missing_item_scope_and_affected_requirements_required=True,
                separately_scoped_implementation_build_qualification_or_authority_request_required_if_needed=True,
                gap_report_is_not_A03_acceptance_or_permission_to_create_material=True,actual_provider_gap_report=None,
                actual_implementation_build_qualification_or_action_authority=None,actual_work_performed=False),
            no_global_absence_or_infeasibility_from_local_missing_paths=True,no_predictive_hash_or_null_as_zero=True),
        critical_boundaries=dict(image_digest_not_runtime_identity_P02_P03_old_rejections_not_successor_proof=True,
            auditor_Python_OS_or_environment_not_sampled_or_adopted_as_target=True,
            README_DOCUMENT_tests_runner_membership_not_loading_import_execution_or_qualification=True,
            complete_dependencies_not_truncated_to128_or_helpers_silently_added=True,
            policy_document_pins_or_matching_constants_not_external_selection_or_implementation_proof=True,
            no_own_future_image_manifest_bundle_digest_embedded=True,
            IM01_IM06_baseline_not_W04_caller_constructor_or_platform_enforcement=True,
            IM07_IM08_W04_IM09_W05_W09_IM10_W10_deferred_not_reverse_acceptance_edges=True,
            genuine_authors_baseline_before_W09_W10_same_facts_not_retroactive=True,
            no_future_final_manifest_registry_or_snapshot_required_as_new_W03_dependency=True,
            no_source_build_import_compile_measurement_qualification_or_runtime_action_authorized_by_missing_material=True,
            no_new_helpers_channels_fds_argv_inputs_outputs_ambient_trust_or_active_configuration=True),
        W03_deliverable_coverage=[dict(id='WD%02d'%(i+1),source=pin(PLAN,'/work_packages/2/deliverables/'+str(i)),exact_requirement=text,
            required_return_ids=[['SR02','SR03'],['SR03'],['SR04']][i],authority_return_id='SR01',review_return_id='SR05',
            actual_complete_delivery=None,accepted=False) for i,text in enumerate(req['deliverables'])],
        acceptance_checklist=[dict(id=cid,criterion=text,required_return_ids=ids,
            actual_evidence_inventory=None,actual_R01_R06_primary_reviews=None,actual_R08_separate_decision=None,
            disposition='PENDING_A01_A02_GENUINE_MATERIAL_AND_COMPETENT_DECISION',accepted=False) for cid,text,ids in CRITERIA],
        W03_exit_coverage=[dict(id='WX%02d'%(i+1),source=pin(PLAN,'/work_packages/2/exit_predicates/'+str(i)),exact_predicate=text,
            required_acceptance_criteria=[c[0] for c in CRITERIA],actual_genuine_disposition=None,accepted=False) for i,text in enumerate(req['exit_predicates'])],
        current_material_state=dict(actual_received_inventory=None,provided_real_bodies=[],rejected_real_bodies=[],actual_evaluations=0,
            actual_sources_image_runtime_or_equivalence=None,actual_provider_schedule_or_duration_guarantee=None,
            missing_six_local_sources=6,local_missing_is_not_global_material_absence=True,
            actual_source_implementation_build_crypto_qualification_or_target_inspection_performed=False),
        preserved_resource_rules=dict(source=pin(ACQUISITION,'/preserved_resource_and_cost_rules'),exact_requirement=acq['preserved_resource_and_cost_rules'],
            complete_reference_and_new_route_costs_in_both_Readers_and_global_join_not_free_offline=True,
            no_caps_budgets_or_262144_as_actual_heap_CPU_service_capacity_success900_proof=True,
            no_quota_budget_reserve_transfer_or_resource_reservation_applied=True),
        handoff=dict(exact_A03_completion_predicate=lot['completion_predicate'],exact_A03_missing_stop=lot['missing_or_failure_stop'],
            next_lot='A04',required_genuine_prior_lots=['A02','A03'],A04_or_RQ04_started_sent_or_accepted=False,
            actual_A03_completion_or_independent_acceptance=None,actual_final_manifest_created_or_frozen=False,
            final_route_source=pin(PLAN,'/prelaunch_handoff_and_CE12'),exact_final_route_boundary=plan['prelaunch_handoff_and_CE12'],
            prelaunch_not_conditioned_on_actual_final_E06_payload_Q_root_admission_claim_receipt=True,
            no_automatic_launch_certificate_PJC115_R2_or_D5_release=True),
        change_control=dict(source=pin(W03,'/phase_boundary'),exact_requirement=w['phase_boundary'],
            any_changed_author_body_source_image_runtime_epoch_key_policy_scope_invalidates_affected_reviews=True,
            no_automatic_old_proof_approval_qualification_or_acceptance_transfer=True,actual_refresh_or_active_rebind=False),
        current_effect={**rd(A02)['current_effect'],'A03_RQ03_documentary_prepared':True,'A03_accepted':False,'RQ03_sent':False,
            'actual_sources_image_runtime_or_build_provenance_accepted':False,'actual_source_implementation_build_or_qualification_created':False,
            'actual_A03_intake_progress_or_review_records_created':False},
        producer=dict(identity='Same Codex assistant/chat as I255/I256',documentary_preparer_only=True,actor_independent=False,
            competent_R01_R06_review=False,separate_R08_acceptance=False,external_contacts_made=False),
        publication=dict(commit_and_push_requested=True,publication_not_sources_runtime_authority_material_acceptance_execution_or_D5_closure=True))


NEGATIVE_CASES = [
    ('A01_promoted',('dependency_gate','A01_accepted'),False,True),
    ('A02_promoted',('dependency_gate','A02_accepted'),False,True),
    ('SD01_bypassed',('dependency_gate','SD01_stop_active'),True,False),
    ('documentary_PASS_as_acceptance',('dependency_gate','no_documentary_PASS_as_genuine_antecedent'),True,False),
    ('request_sent',('unsent_request','sent'),False,True),
    ('contact_granted',('unsent_request','contact_authorized'),False,True),
    ('recipient_invented',('unsent_request','actual_recipient_person'),None,'UNVERIFIED_TEST_LABEL'),
    ('source_created',('source_requests',0,'actual_path_exists'),False,True),
    ('source_hash_predicted',('source_requests',1,'actual_body_bytes_digest_source_root_author_or_custody'),None,{}),
    ('membership_as_loading',('source_requests',4,'loaded_by_membership_claimed'),False,True),
    ('closure_invented',('closure_requests',0,'actual_complete_inventory_body_digests_provenance_or_equivalence'),None,[]),
    ('baseline_accepted',('image_baseline_and_deferred_requests',5,'accepted'),False,True),
    ('policy_verified',('compiled_policy_requests',0,'actual_compiled_value_or_independent_selection_or_conformance_proof'),None,'UNVERIFIED_TEST_LABEL'),
    ('existing_route_accepted',('material_routes','existing_material','actual_route_accepted'),False,True),
    ('gap_as_acceptance',('material_routes','missing_material','gap_report_is_not_A03_acceptance_or_permission_to_create_material'),True,False),
    ('missing_as_build_authority',('material_routes','missing_material','actual_implementation_build_qualification_or_action_authority'),None,'UNVERIFIED_TEST_LABEL'),
    ('work_performed',('material_routes','missing_material','actual_work_performed'),False,True),
    ('missing_value_zero',('material_routes','no_predictive_hash_or_null_as_zero'),True,False),
    ('image_as_runtime',('critical_boundaries','image_digest_not_runtime_identity_P02_P03_old_rejections_not_successor_proof'),True,False),
    ('auditor_host_as_target',('critical_boundaries','auditor_Python_OS_or_environment_not_sampled_or_adopted_as_target'),True,False),
    ('dependency_truncation',('critical_boundaries','complete_dependencies_not_truncated_to128_or_helpers_silently_added'),True,False),
    ('constants_as_implementation',('critical_boundaries','policy_document_pins_or_matching_constants_not_external_selection_or_implementation_proof'),True,False),
    ('self_embedding_allowed',('critical_boundaries','no_own_future_image_manifest_bundle_digest_embedded'),True,False),
    ('baseline_as_enforcement',('critical_boundaries','IM01_IM06_baseline_not_W04_caller_constructor_or_platform_enforcement'),True,False),
    ('downstream_reverse_dependency',('critical_boundaries','IM07_IM08_W04_IM09_W05_W09_IM10_W10_deferred_not_reverse_acceptance_edges'),True,False),
    ('late_authentication',('critical_boundaries','genuine_authors_baseline_before_W09_W10_same_facts_not_retroactive'),True,False),
    ('final_manifest_required_early',('critical_boundaries','no_future_final_manifest_registry_or_snapshot_required_as_new_W03_dependency'),True,False),
    ('source_run_authorized',('critical_boundaries','no_source_build_import_compile_measurement_qualification_or_runtime_action_authorized_by_missing_material'),True,False),
    ('criterion_accepted',('acceptance_checklist',13,'accepted'),False,True),
    ('exit_accepted',('W03_exit_coverage',2,'accepted'),False,True),
    ('inventory_fabricated',('current_material_state','actual_received_inventory'),None,[]),
    ('target_inspected',('current_material_state','actual_source_implementation_build_crypto_qualification_or_target_inspection_performed'),False,True),
    ('free_offline_costs',('preserved_resource_rules','complete_reference_and_new_route_costs_in_both_Readers_and_global_join_not_free_offline'),True,False),
    ('quota_or_reserve_changed',('preserved_resource_rules','no_quota_budget_reserve_transfer_or_resource_reservation_applied'),True,False),
    ('A04_started',('handoff','A04_or_RQ04_started_sent_or_accepted'),False,True),
    ('final_manifest_created',('handoff','actual_final_manifest_created_or_frozen'),False,True),
    ('claim_as_prelaunch_precondition',('handoff','prelaunch_not_conditioned_on_actual_final_E06_payload_Q_root_admission_claim_receipt'),True,False),
    ('qualification_transferred',('change_control','no_automatic_old_proof_approval_qualification_or_acceptance_transfer'),True,False),
    ('A03_accepted',('current_effect','A03_accepted'),False,True),
    ('D5_closed',('current_effect','D5_closed'),False,True),
    ('assistant_as_independent',('producer','actor_independent'),False,True)]


def validate(d):
    for name,path,expected,_ in NEGATIVE_CASES:
        node=d
        for key in path:
            node=node[key]
        assert type(node) is type(expected) and node==expected,name
    assert d==build_candidate(),'A03/RQ03 differs from exact documentary reconstruction'
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
    assert len(d['source_requests'])==6 and all(not (ROOT/r['logical_path']).exists() for r in d['source_requests'])
    assert [r['id'] for r in d['closure_requests']]==['CL%02d'%i for i in range(1,9)]
    rows=d['image_baseline_and_deferred_requests']
    assert [r['id'] for r in rows]==['IM%02d'%i for i in range(1,11)]
    assert [r['id'] for r in rows if not r['deferred_from_A03']]==['IM%02d'%i for i in range(1,7)]
    assert [r['work_package_consumers'] for r in rows if r['deferred_from_A03']]==[['W04'],['W04'],['W05','W06','W07','W08','W09'],['W10']]
    assert len(d['compiled_policy_requests'])==7 and len(d['requested_returns'])==6 and len(d['acceptance_checklist'])==16
    assert len(d['W03_deliverable_coverage'])==len(d['W03_exit_coverage'])==3
    assert d['handoff']['required_genuine_prior_lots']==rd(ACQUISITION)['acquisition_lots'][3]['depends_on_lots']
    bindings=rd(P+'D5-I193-CE11-PRELAUNCH-EVIDENCE-CLOSURE-REVIEW-CANDIDATE.json')['pending_I177_final_bindings']
    assert all(not (ROOT/r['path']).exists() for r in bindings)
    return dict(schema='d5.i257-preparation-review.v1',increment='I257',date=DATE,timezone='Europe/Madrid',base_commit=BASE,status=STATUS,candidate=pin(SUBJECT),
        counts=dict(input_pins=1082,source_paths=6,missing_local_sources=6,closure_classes=8,compiled_policy_requirements=7,
            image_requirements=10,baseline_image_requirements=6,deferred_image_requirements=4,requested_returns=6,acceptance_criteria=16,W03_deliverables=3,W03_exits=3,
            actual_received_bodies=0,actual_sources_or_runtime_accepted=0,actual_lots_accepted=0),
        rejection_checks=rejection_checks(d),current_effect=d['current_effect'],provenance=d['producer'],
        source_reconstruction=dict(I256_reconstruction_and_review_reproduced=True,prior_publication_mains_called=False,prior_Path_exists_restored=True,no_new_presence_projection=True),
        limitations=['A01/A02 remain unaccepted and SD01 active. Conditional draft only; no contact,positive intake or real A03 evidence/acceptance.',
            'Six local sources missing; only genuine existing qualified artifacts with own provenance could meet the material route. A gap report is not acceptance or implementation/build/qualification authority.',
            'Image and runtime remain distinct unverified identities; full closure/source equivalence/policy implementation/immutable baseline and R01/R06/R08 decisions are missing.',
            'IM07/IM08 W04,IM09 resources and IM10 W10 remain deferred without reverse dependencies. No runtime/build/probe/crypto/contact/configuration,quota/reserve,binding or D5 change.'],
        work_unit=dict(rollback_files=sorted(FILES),verification_command='python3 docs/validation/D5-I257-audit.py',expected_result=STATUS,
            runtime_harness='N/A: own documentary JSON/Git/hash/pointer/coverage/phase checks and in-memory documentary mutations only. No target import/compile/discovery/tests/execution/build/benchmark/crypto/signing/keygen/enrollment/provisioning/contacts/platform/clock/CPU/IO/ledger/process/endpoint probes or configuration.',
            over400_lines=True,reason='Single conditional A03/RQ03 request with exact material/gap routes,pins,scope/closure/phase requirements,rejection checks and preservation; overage declared,no PR requested.'),
        publication=dict(commit_and_push_requested=True,publication_not_material_implementation_authority_or_acceptance=True))


def main():
    review=build_review()
    assert review==rd(PREP)
    prior=rd(PRIOR_SEAL)
    preserved={**prior['preserved_published769'],**prior['artifacts'],PRIOR_SEAL:sha(PRIOR_SEAL)}
    assert len(preserved)==774
    seal=rd(SEAL)
    assert seal['schema']=='d5.i257-integrity.v1' and seal['base_commit']==BASE
    assert seal['preserved_published774']==preserved and set(seal['artifacts'])==FILES-{SEAL}
    for mapping in [preserved,seal['artifacts']]:
        for path,digest in mapping.items():
            assert sha(path)==digest,path
    assert seal['source_only'] is True and seal['current_effect']==review['current_effect']
    changed=set(git('diff',BASE,'--name-only').splitlines())|set(git('ls-files','--others','--exclude-standard').splitlines())
    assert changed==FILES,changed
    subprocess.check_call(['git','merge-base','--is-ancestor',BASE,'HEAD'],cwd=ROOT)
    if git('rev-parse','HEAD')!=BASE:
        assert not git('status','--porcelain')
    print(json.dumps(dict(status=STATUS,increment='I257',input_pins=1082,preserved_published_files=774,new_files=5,
        documentary_rejections=len(review['rejection_checks']),counts=review['counts'],SD01_stop_active=True,
        prelaunch_gates_closed=0,resource_obligations_closed=0,D5_closed=False,git_head=git('rev-parse','HEAD')),sort_keys=True))


if __name__=='__main__':
    main()
