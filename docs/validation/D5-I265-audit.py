#!/usr/bin/env python3
"""I265 A07/RQ07 documentary preparation; no target/component execution."""
import copy
import hashlib
import io
import json
from pathlib import Path
import runpy
import subprocess

ROOT = Path(__file__).resolve().parents[2]
P = 'docs/validation/'
BASE = '786bf750d3f67b359dc525a62adc25543ec4d803'
DATE = '2026-11-26'
PLAN = P+'D5-I223-PRELAUNCH-RESOURCE-CLOSURE-PLAN.json'
ACQUISITION = P+'D5-I251-GENUINE-EVIDENCE-ACQUISITION-PLAN.json'
A06 = P+'D5-I251-A06-RQ06-INDEPENDENT-RESOURCE-JOIN-CANDIDATE.json'
PRIOR_RECON = P+'D5-I264-I263-source-reconstruction.json'
PRIOR_REVIEW = P+'D5-I264-I263-documentary-review.json'
PRIOR_AUDIT = P+'D5-I264-audit.py'
PRIOR_SEAL = P+'D5-I264-integrity.json'
PRIOR_DOC = 'docs/design/D5-I264-I263-A06-RQ06-REVIEW.md'
PRIOR_FILES = {PRIOR_RECON,PRIOR_REVIEW,PRIOR_AUDIT,PRIOR_SEAL,PRIOR_DOC}
SUBJECT = P+'D5-I251-A07-RQ07-FINAL-CUSTODY-MAPPING-CANDIDATE.json'
PREP = P+'D5-I265-preparation-review.json'
AUDIT = P+'D5-I265-audit.py'
SEAL = P+'D5-I265-integrity.json'
DOC = 'docs/design/D5-I265-A07-RQ07-FINAL-CUSTODY-MAPPING.md'
FILES = {SUBJECT,PREP,AUDIT,SEAL,DOC}
STATUS = 'PASS_STATIC_SOURCE_ONLY_A07_RQ07_PREPARED_PREDECESSORS_AND_GENUINE_FINAL_CUSTODY_MAPPING_MISSING_NOT_ADMITTED'
WORKS = {
    'W10':P+'D5-I223-W10-FINAL-ANTECEDENT-FREEZE-CANDIDATE.json',
    'W11':P+'D5-I223-W11-EXACT-C-ACCEPTANCE-CANDIDATE.json',
    'W12':P+'D5-I223-W12-BUNDLE-APPROVALS-GLOBAL-MAPPING-CANDIDATE.json'}


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


SECTIONS = {
    'W10':['role_and_contributor_boundary','freeze_record_ledger','nested_schema_obligations','contract_rule_requirements',
        'inherited_freeze_policy_requirements','schema_and_body_boundary','record_DAG','hash_scope_and_validity_boundary',
        'W09_reconciliation_ledger','reconciliation_and_invalidation_boundary','resource_and_cost_boundary','phase_handoff','authority_boundary','preserved_scope_and_gates'],
    'W11':['identity_and_decision_boundary','schema_requirement_ledger','shared_type_requirement_ledger','shared_definition_closure',
        'value_projection_requirement_ledger','validity_containment_requirement','exact_constant_requirements','antecedent_hash_requirement_ledger',
        'prior_acceptance_evidence_requirement_ledger','projection_predicate_requirements','contract_rule_requirements','inherited_projection_policy_requirements',
        'digest_and_signature_boundary','scope_and_reconciliation_boundary','resource_and_cost_boundary','phase_handoff','authority_boundary','preserved_scope_and_gates'],
    'W12':['identity_and_trust_boundary','schema_requirement_ledger','nested_record_requirement_ledger','complete_core_and_bundle_requirement',
        'approval_requirement_ledger','signature_and_authentication_boundary','global_mapping_requirement','intrinsic_constructor_boundary',
        'inherited_bundle_policy_requirements','contract_rule_requirements','conditional_size_model','accepted_fact_and_validity_boundary',
        'resource_and_invalidation_boundary','phase_handoff','authority_boundary','preserved_scope_and_gates']}
RETURNS = [
    ('RF01','Antecedentes genuinos,autoridad y reconciliación de hechos',[],
     'Aportar A02/A04/A06 genuinamente aceptados y sus antecedentes A01/A03/A05 conservados; autores/providers/preparadores W05-W09 auténticos y reviews/appointments/competencia/anchors/scope/validez propios. I264 documental no acepta A06. Roster final incluye todas las contribuciones reales sin preaprobar futuros autores o inferir humanos de Git/asistente. W10 reconcilia los mismos hechos ya autenticados antes de W09; si cambian, invalidar/revisar afectados antes de avanzar, no autenticar retrospectivamente.'),
    ('RF02','W10: roster y cuatro registros finales auténticos',['W10'],
     'Entregar,cuando existan con autoridad propia,actor_registry completo primero,luego image_manifest,caller_identity,platform_custody con cuerpos canónicos/bytes/digests/caps/epoch/vigencias/provenance y cierre de todas las referencias. Preparadores1..16,actores/claves<=64,dependencias<=128 completos/sorted/unique sin recorte. Imagen y runtime distintos; hashes/cuerpos/source/caller/domain/resource/autores deben concordar con W09 y sus premisas. No generar/provisionar/configurar snapshots o registros aquí.'),
    ('RF03','W11: C exacto y acceptance exclusivamente de custodia',['W11'],
     'Aportar C19/acceptance27 auténticos sobre W09/W10 aceptados,14 tipos compartidos y seis definiciones cerradas,13 proyecciones de valores y contención de validity,no igualdad forzada de extremos. Constantes repository/root-path/offline-key-status exactas,digest JCS de C completo,cuatro hashes de antecedentes y cinco evidencias previas genuinas. Error platform<=C<=5,lifetime<=3600/epoch/currentness/revocación;C8192/acceptance16384 sin campos nuevos. Acceptance sin firma propia;sin bundle hash en C,ni root/E06 futuros como prueba o emisión/codec/crypto por este plan.'),
    ('RF04','W12: cinco registros,core/bundle y tres aprobaciones',['W12'],
     'Entregar cinco registros finales y hashes cruzados,core cerrado8 y bundle3,con anchors/políticas seleccionados independientemente. Tres aprobaciones reales R01/R02/R08 sobre el mismo core completo,dominio exacto ASCII+un octeto NUL+JCS(core) y provenance/verificación competente bajo autoridad propia. No sustituir por dos firmas root,recortar core o autofundar anchors desde C/bundle/root;R08 humano/clave separado de R01/R02,coincidencia R01/R02 sólo mismo humano cualificado y dominios distintos. Sin firma de acceptance,validez propia bundle o C body extra. No firmar/keygen/verificar crypto aquí.'),
    ('RF05','Mapping único global y constructor intrínseco',['W12'],
     'Aportar prueba genuina de exactamente un mapping vigente por(configuration_epoch,SHA256(JCS(actual C))) hacia un bundle/caller/image/protection_domain/global_ledger_domain entre todos los callers/imágenes/dominios/restarts. No particionar/extender clave por caller/restart;una entrada observada o firma local no prueba unicidad global. Resolver autenticadamente antes de P_ROOT_CHECK y congelar mismos C/Q/constructor;worker nace en origen protegido intrínseco,sin nuevo canal/frame/receipt/helper. Conflicto/stale/rollback/revocación incierta rechaza. Mapping no claim;backend incapaz mantiene no admisión sin configuración/pruebas/replay/claim aquí.'),
    ('RF06','Caps,referencias,costes y reviews genuinos',list(WORKS),
     'Entregar inventario completo de cuerpos/referencias/bytes/digests/locators/autores/providers/custodia/unidades/supuestos/currentness y fit real de caps anidados/bundle<=262144. Modelo221644/margen40500 sólo bajo hipótesis I192 ASCII/safeinteger/escaping/nested caps probadas,no heap/CPU/reserva disponible o inviabilidad de otro modelo. Costes ambos Readers/join global completos;si cambia operación/grafo/encoding,revalidar afectados bajo límites intactos. Reviews W10/W11 R01/R02/R03/R06,W12 R01/R02/R06 y R08 separado genuinos sobre mismo scope;este asistente no los aporta.'),
    ('RF07','Gaps,SD06/SD07 y alcance separado',list(WORKS),
     'Identificar cada autor/cuerpo/binding/validez/proof/approval/mapping/backend/fit/supuesto faltante o cambiado y dependientes. Mantener SD06/SD07/no admisión e invalidar/revisar afectados cuando cambien hechos. Indicar trabajo/autoridad separados necesarios sin generar snapshots/registros/C/bundle/firmas/claves,contactar/enrolar/configurar registry/mapping/servicio,verificar crypto,probar/ejecutar o cambiar cuotas/reservas. Gap no aceptación,hash predictivo,unknown=0 o inviabilidad global.')]
CRITERIA = [
    ('AC01','A02/A04/A06 genuinos con todos los antecedentes conservados,scope/autoridad/bodies reales;PASS documental no permite envío o intake positivo.',['RF01']),
    ('AC02','Autores/providers/preparadores W05-W09 completos auténticos y elegibles,roles/anchors/appointments/exclusiones reales;sin humanos Git/asistente o autores futuros preaprobados.',['RF01','RF02']),
    ('AC03','Orden actor→imagen→caller→plataforma y W10→W11→W12;W09 ya aceptado sobre mismos hechos,no freeze retrospectivo o hash transferido.',['RF01','RF02']),
    ('AC04','Cuatro cuerpos finales canónicos/bytes/hashes/epoch/vigencia/caps/provenance y cierre completo sin recortar preparadores/actores/claves/dependencias.',['RF02']),
    ('AC05','C19/acceptance27 cerrados,14 tipos/6defs/13proyecciones+validity contenida,constants exactas y valores de hechos aceptados sin placeholders.',['RF03']),
    ('AC06','Digest JCS completo C,cuatro hashes y cinco evidencias previas reales,cuerpos disponibles/roles/validez,caps8192/16384.',['RF03']),
    ('AC07','Vigencias actuales/epoch/revocación,error platform<=C<=5,lifetime<=3600 y contención,no igualdad forzada o host date como frescura.',['RF03']),
    ('AC08','Acceptance sólo custodia sin firma propia,C sin bundle hash/campos extra;C cubierto indirectamente por acceptance/core,no C body extra.',['RF03','RF04']),
    ('AC09','Cinco registros con hashes cruzados/core8/bundle3 exactos,políticas/anchors elegidos independientemente,ningún core recortado.',['RF04']),
    ('AC10','Tres aprobaciones genuinas R01/R02/R08 mismo core completo,dominios exactos+un NUL y provenance/verificación propia,no dos firmas root.',['RF04']),
    ('AC11','R08 humano/clave separado de R01/R02;coincidencia R01/R02 sólo mismo humano cualificado y aprobaciones por dominio,ningún self-bootstrap.',['RF01','RF04']),
    ('AC12','Exactamente un mapping vigente global por(epoch,digest C),target bundle/caller/image/domain/ledger,clave no extendida/particionada o prueba local como global.',['RF05']),
    ('AC13','Resolución antes P_ROOT_CHECK y mismos C/Q/constructor congelados,worker origen protegido intrínseco sin canal/receipt/helper extra;mapping no claim.',['RF05']),
    ('AC14','Caps reales completos y bundle<=262144;221644/40500 sólo modelo condicionado,no fit/recursos o reserva afirmados ni truncamiento.',['RF06']),
    ('AC15','Inventario íntegro de instancias/cuerpos/provenance y ambos Readers/global coste,unidades/supuestos/guards/source/output compatibles,operaciones cambiadas revalidadas.',['RF02','RF03','RF04','RF05','RF06']),
    ('AC16','Reviews exactas por W y R08 separado genuinos con motivos/same scope;preparación del asistente no independencia o decisión real.',['RF06']),
    ('AC17','PJ01-PJ10 W11,PJ11-PJ12 W12 conservados;W13 gates y CE12/finalclaim no producidos o nueva dependencia de aceptación prelaunch.',['RF03','RF04','RF05']),
    ('AC18','Cambio de autor/body/source/runtime/caller/domain/resource/epoch/key/policy invalida afectados A01-A07 según impacto,sin transferencia automática/rebind activo.',['RF01','RF06','RF07']),
    ('AC19','Gaps mantienen SD06/SD07/no admisión,no snapshots/signing/keygen/crypto/enrollment/provision/configuración/contacto/runs/cuotas para rellenar expediente.',['RF07']),
    ('AC20','Sólo A07 genuino permite considerar A08 con A01-A07 completos,sin promoción de certificado/PJC115-R2,D5 o ejecución funcional.',['RF06','RF07'])]


def build_candidate():
    plan,acq=rd(PLAN),rd(ACQUISITION);lot=acq['acquisition_lots'][6]
    docs={key:rd(path) for key,path in WORKS.items()};reqs={r['id']:r for r in plan['work_packages'][9:12]}
    assert lot['depends_on_lots']==['A02','A04','A06'] and list(reqs)==list(WORKS)
    pins={**rd(PRIOR_RECON)['input_pins'],**{path:sha(path) for path in sorted(PRIOR_FILES)}}
    assert len(pins)==1122
    return dict(schema='d5.i265-a07-rq07-documentary-preparation.v1',increment='I265',date=DATE,timezone='Europe/Madrid',base_commit=BASE,
        dossier_id='PGE251-A07-RQ07-CANDIDATE-01',lot_id='A07',request_id='RQ07',covers_work_packages=list(WORKS),
        kind='CONDITIONAL_LOCAL_UNSENT_REQUEST_FOR_GENUINE_FINAL_CUSTODY_RECORDS_AND_GLOBAL_MAPPING_NOT_ISSUANCE_SIGNATURE_OR_CONFIGURATION',
        status='A07_RQ07_DOCUMENTARY_PREPARED_PREDECESSORS_UNACCEPTED_SD01_ACTIVE_NOT_ACCEPTED_NOT_ADMITTED',input_pins=pins,
        acquisition_lot_binding=pin(ACQUISITION,'/acquisition_lots/6'),exact_acquisition_lot=lot,prior_A06_review=pin(PRIOR_REVIEW),
        dependency_gate=dict(required_lot_ids=['A02','A04','A06'],required_external_work_package_ids=['W%02d'%i for i in range(2,10)],
            A06_state_source=pin(A06,'/current_effect'),exact_prior_effect=rd(A06)['current_effect'],
            A01_accepted=False,A02_accepted=False,A03_accepted=False,A04_accepted=False,A05_accepted=False,A06_accepted=False,SD01_stop_active=True,
            actual_genuine_antecedent_acceptance_bodies=None,no_documentary_PASS_as_genuine_antecedent=True,
            no_send_contact_positive_intake_records_issuance_signing_or_mapping_configuration_from_preparation=True),
        internal_work_order=dict(source=pin(ACQUISITION,'/acquisition_lots/6/internal_work_dependencies'),
            exact_I223_dependencies={key:req['depends_on'] for key,req in reqs.items()},stages=[['W10'],['W11'],['W12']],
            actual_work_packages_accepted=0,no_W10_retroactive_authentication_or_future_W13_CE12_acceptance_dependency=True),
        unsent_request=dict(original_draft=lot['unsent_request_draft'],subject='RQ07 — Finalización auténtica de custodia y mapping / W10-W12 / PGO181 candidato02',
            recipient_role_only=lot['intended_recipient_role_kind'],
            reviewable_request_text='Borrador condicionado a A02/A04/A06 genuinamente aceptados y sus antecedentes conservados. Aportar sólo bajo autoridad propia RF01-RF06: roster completo y cuatro registros finales W10 reconciliados con mismos hechos W09;C/acceptance exactos W11;cinco registros/core8/bundle3/tres aprobaciones mismo core W12;mapping único global epoch/digest C y constructor intrínseco,caps/refs/costes/reviews y R08 separado. Seguir actor→imagen→caller→plataforma y W10→W11→W12. Contención de vigencias/error conservador,anchors independientes,no firma propia acceptance o bundle hash en C. Si falta/cambia cuerpo/autor/approval/fit/backend,RF07 y SD06/SD07/no admisión. No se solicita emitir/generar snapshots/registros/C/bundle,firmar/keygen/verificar crypto,enrolar/contactar/provisionar/configurar registry/mapping/servicio,probar/ejecutar o cambiar cuotas/reservas. Antecedentes siguen sin aceptar y RQ07 no se envía.',
            required_return_ids=[r[0] for r in RETURNS],is_draft_only=True,sent=False,contact_authorized=False,
            actual_recipient_persons=None,actual_addresses_or_channels=None,actual_contact_authority=None,actual_delivery_or_receipt=None),
        work_package_requests=[dict(id=key,source=pin(PLAN,'/work_packages/'+str(int(key[1:])-1)),exact_requirement=req,
            documentary_checklist=pin(WORKS[key]),planned_deliverable_id=req['deliverable_id'],primary_review_roles=req['primary_review_roles'],
            separate_acceptor_role=req['separate_acceptor_role'],required_material_return={'W10':'RF02','W11':'RF03','W12':'RF04'}[key],
            actual_complete_records_bodies_scope_provenance_or_reviews=None,actual_separate_acceptance=None,accepted=False)
            for key,req in reqs.items()],
        requested_returns=[dict(id=rid,title=title,requirements=text,work_package_ids=works,W_requirement_sources=[pin(WORKS[key]) for key in works],
            universal_delivery_source=pin(ACQUISITION,'/evidence_delivery_contract'),actual_body_inventory=None,actual_received=False,
            actual_primary_reviews=None,actual_separate_acceptance=None,accepted=False) for rid,title,works,text in RETURNS],
        custody_scope_requirements=[dict(work_package=key,section=section,source=pin(WORKS[key],'/'+section),documentary_container_dimension=len(docs[key][section]),
            container_dimension_not_actual_records_proofs_or_fit=True,actual_complete_same_fact_material_or_review=None,accepted=False)
            for key,sections in SECTIONS.items() for section in sections],
        final_record_requests=[dict(family=row['family'],order=row['order'],source=pin(WORKS['W10'],'/freeze_record_ledger/'+str(i)),
            schema_source=row['schema_source'],field_names=[r['field'] for r in row['field_requirements']],candidate_body_cap_bytes=row['candidate_body_cap_bytes'],
            required_return_id='RF02',actual_complete_canonical_body_bytes_digest_epoch_validity_or_provenance=None,
            actual_same_fact_W09_reconciliation_or_review=None,actual_frozen=False,accepted=False) for i,row in enumerate(docs['W10']['freeze_record_ledger'])],
        context_acceptance_requests=[dict(kind=row['kind'],source=pin(WORKS['W11'],'/schema_requirement_ledger/'+str(i)),schema_source=row['source'],
            field_count=len(row['field_requirements']),candidate_body_cap_bytes=row['candidate_body_cap_bytes'],required_return_id='RF03',
            actual_complete_body_values_canonical_bytes_digest_projection_validity_or_custody=None,actual_reviews_or_acceptance=None,accepted=False)
            for i,row in enumerate(docs['W11']['schema_requirement_ledger'])],
        approval_requests=[dict(role=row['role'],source=pin(WORKS['W12'],'/approval_requirement_ledger/'+str(i)),
            required_domain_ASCII=row['required_domain_ASCII'],required_delimiter_hex=row['required_delimiter_hex'],required_delimiter_octets=row['required_delimiter_octets'],
            required_payload=row['required_payload'],required_return_id='RF04',actual_actor_key_purpose_anchor_or_currentness=None,
            actual_common_core_bytes_digest_message_signature_or_provenance_verification=None,verified=False,accepted=False)
            for i,row in enumerate(docs['W12']['approval_requirement_ledger'])],
        mapping_request=dict(source=pin(WORKS['W12'],'/global_mapping_requirement'),exact_requirement=docs['W12']['global_mapping_requirement'],
            constructor_source=pin(WORKS['W12'],'/intrinsic_constructor_boundary'),exact_constructor_requirement=docs['W12']['intrinsic_constructor_boundary'],
            required_return_id='RF05',actual_global_unique_current_mapping_key_target_authority_or_proof=None,
            actual_intrinsic_constructor_custody_or_origin_proof=None,actual_backend_selected_or_configured=False,actual_claim_worker_or_receipt_created=False,accepted=False),
        critical_boundaries=dict(
            all_actual_authors_preparers_complete_final_roster_genuine_with_prior_independent_anchors_and_authority=True,
            W10_same_facts_as_authenticated_W09_no_retrospective_authentication_or_automatic_transfer=True,
            actor_image_caller_platform_order_complete_caps_epoch_validity_and_reference_closure_no_truncation=True,
            C19_acceptance27_closed_14_types_13_values_and_validity_containment_not_equal_endpoints=True,
            complete_C_JCS_digest_four_hashes_five_prior_evidence_bodies_not_placeholders=True,
            platform_error_lte_C_error_lte5_lifetime_lte3600_same_current_epoch_and_revocation_not_host_date=True,
            custody_acceptance_no_standalone_signature_no_bundle_hash_in_C_or_extra_C_body_bundle_validity=True,
            five_records_core8_bundle3_complete_same_core_for_three_role_domain_plus_one_NUL_approvals=True,
            no_root_two_signatures_as_three_custody_approvals_no_cut_core_or_self_bootstrap_from_C_bundle_root=True,
            R08_human_key_separate_R01_R02_overlap_only_same_qualified_human_separate_domains=True,
            global_mapping_exact_epoch_complete_C_digest_not_partitioned_by_caller_image_domain_restart=True,
            exactly_one_bundle_caller_image_domain_global_ledger_target_not_local_observed_entry_as_global_proof=True,
            resolve_before_P_ROOT_CHECK_freeze_same_C_Q_constructor_worker_intrinsic_origin_no_new_channel_helper_receipt=True,
            mapping_not_actual_claim_and_incapable_backend_keeps_no_admission_no_new_transport=True,
            nested_caps_and_bundle262144_real_fit_221644_40500_only_conditional_not_resource_reserve_or_infeasibility=True,
            all_reference_costs_both_Readers_global_join_and_changed_operations_require_revalidation=True,
            PJ01_PJ10_W11_PJ11_PJ12_W12_W13_and_CE12_remain_own_consumers_no_reverse_edges=True,
            no_positive_record_snapshot_C_bundle_signature_key_crypto_check_enrollment_configuration_or_target_execution=True),
        material_routes=dict(existing_material=dict(required_returns=['RF%02d'%i for i in range(1,7)],actual_delivery_inventory=None,actual_route_accepted=False),
            missing_material=dict(required_return_id='RF07',SD06_SD07_stop_and_invalidate_affected_work_if_any_fact_or_body_changes=True,
                gap_not_acceptance_no_predictive_hash_null_zero_or_global_infeasibility=True,
                separate_exact_authority_required_for_records_snapshots_signing_crypto_contact_or_configuration=True,
                actual_gap_report=None,actual_new_action_authority=None,actual_work_performed=False)),
        deliverable_coverage=[dict(id=key+'-D%02d'%(i+1),work_package=key,source=pin(PLAN,'/work_packages/'+str(int(key[1:])-1)+'/deliverables/'+str(i)),
            exact_requirement=text,required_material_return={'W10':'RF02','W11':'RF03','W12':'RF04'}[key],mapping_return_required=(key=='W12'),
            authority_return_id='RF01',review_return_id='RF06',actual_complete_delivery=None,accepted=False)
            for key,req in reqs.items() for i,text in enumerate(req['deliverables'])],
        acceptance_checklist=[dict(id=cid,criterion=text,required_return_ids=ids,actual_evidence_inventory=None,actual_competent_primary_reviews=None,
            actual_R08_separate_decision=None,disposition='PENDING_PREDECESSORS_GENUINE_FINAL_CUSTODY_AND_MAPPING_DECISIONS',accepted=False)
            for cid,text,ids in CRITERIA],
        exit_coverage=[dict(id=key+'-X%02d'%(i+1),work_package=key,source=pin(PLAN,'/work_packages/'+str(int(key[1:])-1)+'/exit_predicates/'+str(i)),
            exact_predicate=text,required_intake_criteria=[c[0] for c in CRITERIA],actual_genuine_disposition=None,accepted=False)
            for key,req in reqs.items() for i,text in enumerate(req['exit_predicates'])],
        actual_material_state=dict(actual_received_inventory=None,provided_real_bodies=[],rejected_real_bodies=[],actual_evaluations=0,
            actual_provider_schedule_or_duration_guarantee=None,actual_records_C_acceptance_bundle_approvals_or_mapping=None,
            actual_snapshots_signing_keygen_crypto_enrollment_configuration_or_probe_performed=False),
        preserved_resource_rules=dict(source=pin(ACQUISITION,'/preserved_resource_and_cost_rules'),exact_requirement=acq['preserved_resource_and_cost_rules'],
            all_nested_and_reference_body_caps_costs_assumptions_Reader_output_guards_join_must_reconcile=True,
            no_quota_budget_reserve_transfer_or_resource_reservation_applied=True),
        handoff=dict(exact_A07_completion_predicate=lot['completion_predicate'],exact_A07_missing_stop=lot['missing_or_failure_stop'],
            next_lot='A08',required_genuine_prior_lots=['A%02d'%i for i in range(1,8)],A08_or_RQ08_started_sent_or_accepted=False,
            actual_A07_completion_or_independent_acceptance=None,actual_W13_gate_closure_or_final_route_created=False,
            final_route_source=pin(PLAN,'/prelaunch_handoff_and_CE12'),exact_final_route_boundary=plan['prelaunch_handoff_and_CE12'],
            no_final_E06_payload_Q_root_admission_claim_receipt_as_new_prelaunch_condition=True,no_automatic_certificate_PJC115_R2_execution_or_D5_release=True),
        change_control=dict(source=pin(PLAN,'/scope_authentication_and_freeze_order'),exact_requirement=plan['scope_authentication_and_freeze_order'],
            changed_author_body_source_runtime_image_caller_domain_resource_epoch_key_policy_invalidates_any_affected_A01_A07_before_progress=True,
            no_automatic_old_proof_hash_approval_or_acceptance_transfer=True,actual_refresh_or_active_rebind=False),
        current_effect={**rd(A06)['current_effect'],'A07_RQ07_documentary_prepared':True,'A07_accepted':False,'RQ07_sent':False,
            'actual_final_records_C_acceptance_bundle_approvals_or_mapping_created':False,'actual_A07_intake_progress_or_review_records_created':False},
        producer=dict(identity='Same Codex assistant/chat as I263/I264',documentary_preparer_only=True,actor_independent=False,
            competent_R01_R02_R03_R06_review=False,separate_R08_acceptance=False,external_contacts_made=False),
        publication=dict(commit_and_push_requested=True,publication_not_records_issuance_signature_mapping_authority_acceptance_execution_or_D5_closure=True))


NEGATIVE_CASES = [
    ('A06_promoted',('dependency_gate','A06_accepted'),False,True),('SD01_bypassed',('dependency_gate','SD01_stop_active'),True,False),
    ('PASS_as_antecedent',('dependency_gate','no_documentary_PASS_as_genuine_antecedent'),True,False),
    ('request_sent',('unsent_request','sent'),False,True),('contact_granted',('unsent_request','contact_authorized'),False,True),
    ('provider_invented',('unsent_request','actual_recipient_persons'),None,['UNVERIFIED_TEST_LABEL']),
    ('work_package_accepted',('work_package_requests',0,'accepted'),False,True),
    ('freeze_created',('final_record_requests',0,'actual_frozen'),False,True),
    ('C_body_fabricated',('context_acceptance_requests',0,'actual_complete_body_values_canonical_bytes_digest_projection_validity_or_custody'),None,{}),
    ('signature_fabricated',('approval_requests',0,'actual_common_core_bytes_digest_message_signature_or_provenance_verification'),None,'UNVERIFIED_TEST_LABEL'),
    ('mapping_fabricated',('mapping_request','actual_global_unique_current_mapping_key_target_authority_or_proof'),None,{}),
    ('backend_configured',('mapping_request','actual_backend_selected_or_configured'),False,True),
    ('retrospective_authentication',('critical_boundaries','W10_same_facts_as_authenticated_W09_no_retrospective_authentication_or_automatic_transfer'),True,False),
    ('validity_forced_equal',('critical_boundaries','C19_acceptance27_closed_14_types_13_values_and_validity_containment_not_equal_endpoints'),True,False),
    ('C_hash_predicted',('critical_boundaries','complete_C_JCS_digest_four_hashes_five_prior_evidence_bodies_not_placeholders'),True,False),
    ('clock_not_conservative',('critical_boundaries','platform_error_lte_C_error_lte5_lifetime_lte3600_same_current_epoch_and_revocation_not_host_date'),True,False),
    ('acceptance_signed_or_C_bundle_hash',('critical_boundaries','custody_acceptance_no_standalone_signature_no_bundle_hash_in_C_or_extra_C_body_bundle_validity'),True,False),
    ('different_role_core',('critical_boundaries','five_records_core8_bundle3_complete_same_core_for_three_role_domain_plus_one_NUL_approvals'),True,False),
    ('root_signatures_as_custody',('critical_boundaries','no_root_two_signatures_as_three_custody_approvals_no_cut_core_or_self_bootstrap_from_C_bundle_root'),True,False),
    ('R08_overlap_allowed',('critical_boundaries','R08_human_key_separate_R01_R02_overlap_only_same_qualified_human_separate_domains'),True,False),
    ('local_mapping_key',('critical_boundaries','global_mapping_exact_epoch_complete_C_digest_not_partitioned_by_caller_image_domain_restart'),True,False),
    ('local_entry_as_global',('critical_boundaries','exactly_one_bundle_caller_image_domain_global_ledger_target_not_local_observed_entry_as_global_proof'),True,False),
    ('new_mapping_channel',('critical_boundaries','resolve_before_P_ROOT_CHECK_freeze_same_C_Q_constructor_worker_intrinsic_origin_no_new_channel_helper_receipt'),True,False),
    ('mapping_as_claim',('critical_boundaries','mapping_not_actual_claim_and_incapable_backend_keeps_no_admission_no_new_transport'),True,False),
    ('conditional_margin_as_reserve',('critical_boundaries','nested_caps_and_bundle262144_real_fit_221644_40500_only_conditional_not_resource_reserve_or_infeasibility'),True,False),
    ('Reader_costs_waived',('critical_boundaries','all_reference_costs_both_Readers_global_join_and_changed_operations_require_revalidation'),True,False),
    ('crypto_authorized',('critical_boundaries','no_positive_record_snapshot_C_bundle_signature_key_crypto_check_enrollment_configuration_or_target_execution'),True,False),
    ('gap_as_authority',('material_routes','missing_material','actual_new_action_authority'),None,'UNVERIFIED_TEST_LABEL'),
    ('criterion_accepted',('acceptance_checklist',15,'accepted'),False,True),('exit_accepted',('exit_coverage',0,'accepted'),False,True),
    ('inventory_fabricated',('actual_material_state','actual_received_inventory'),None,[]),
    ('operational_snapshots_created',('actual_material_state','actual_snapshots_signing_keygen_crypto_enrollment_configuration_or_probe_performed'),False,True),
    ('quota_changed',('preserved_resource_rules','no_quota_budget_reserve_transfer_or_resource_reservation_applied'),True,False),
    ('A08_started',('handoff','A08_or_RQ08_started_sent_or_accepted'),False,True),
    ('final_route_as_prelaunch_condition',('handoff','no_final_E06_payload_Q_root_admission_claim_receipt_as_new_prelaunch_condition'),True,False),
    ('old_hash_transferred',('change_control','no_automatic_old_proof_hash_approval_or_acceptance_transfer'),True,False),
    ('A07_accepted',('current_effect','A07_accepted'),False,True),('D5_closed',('current_effect','D5_closed'),False,True),
    ('assistant_independent',('producer','actor_independent'),False,True)]


def validate(d):
    for name,path,expected,_ in NEGATIVE_CASES:
        node=d
        for key in path:
            node=node[key]
        assert type(node) is type(expected) and node==expected,name
    assert d==build_candidate(),'A07/RQ07 differs from exact documentary reconstruction'
    pointers(d)


def rejection_checks(d):
    results=[]
    for name,path,_,value in NEGATIVE_CASES:
        mutant=copy.deepcopy(d);node=mutant
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
    d=rd(SUBJECT);validate(d);verify_blobs(d['input_pins'])
    previous=runpy.run_path(str(ROOT/PRIOR_AUDIT));exists=Path.exists
    rec=previous['reconstruct']()
    assert rec==rd(PRIOR_RECON) and previous['build_review'](rec)==rd(PRIOR_REVIEW)
    assert Path.exists is exists
    reqs={r['id']:r for r in rd(PLAN)['work_packages'][9:12]}
    order=d['internal_work_order'];assert order['exact_I223_dependencies']==fragment(order['source'])=={k:r['depends_on'] for k,r in reqs.items()}
    assert order['stages']==[['W10'],['W11'],['W12']]
    complete={'W%02d'%i for i in range(2,10)}
    for stage in order['stages']:
        assert all(set(reqs[key]['depends_on'])<=complete for key in stage);complete.update(stage)
    assert [r['id'] for r in d['work_package_requests']]==list(WORKS)
    for row in d['work_package_requests']:
        assert row['exact_requirement']==fragment(row['source'])==reqs[row['id']]
        assert row['primary_review_roles']==reqs[row['id']]['primary_review_roles'] and row['separate_acceptor_role']=='R08'
    assert len(d['custody_scope_requirements'])==sum(map(len,SECTIONS.values()))==48
    records=d['final_record_requests']
    assert [r['family'] for r in records]==['actor_registry','image_manifest','caller_identity','platform_custody']
    assert [len(r['field_names']) for r in records]==[8,26,13,14] and sum(len(r['field_names']) for r in records)==61
    assert [(r['kind'],r['field_count']) for r in d['context_acceptance_requests']]==[('C',19),('ACCEPTANCE',27)]
    w11,w12=rd(WORKS['W11']),rd(WORKS['W12'])
    assert [len(w11[key]) for key in ['shared_type_requirement_ledger','shared_definition_closure','value_projection_requirement_ledger','antecedent_hash_requirement_ledger','prior_acceptance_evidence_requirement_ledger']]==[14,6,13,4,5]
    assert [(r['role'],r['required_delimiter_octets']) for r in d['approval_requests']]==[('R01_RUNTIME',1),('R02_PLATFORM',1),('R08_ACCEPTANCE',1)]
    assert len(w12['complete_core_and_bundle_requirement']['core_fields'])==8 and len(w12['complete_core_and_bundle_requirement']['bundle_fields'])==3
    assert len(w12['nested_record_requirement_ledger'])==5 and sum(len(r['field_requirements']) for r in w12['nested_record_requirement_ledger'])==88
    assert len(d['requested_returns'])==7 and len(d['acceptance_checklist'])==20
    assert len(d['deliverable_coverage'])==10 and len(d['exit_coverage'])==9
    assert d['handoff']['required_genuine_prior_lots']==rd(ACQUISITION)['acquisition_lots'][7]['depends_on_lots']
    sources=rd(P+'D5-I191-CALLER-IMAGE-CUSTODY-SCHEMAS-CANDIDATE.json')['$defs']['source_bindings']['required']
    assert all(not (ROOT/path).exists() for path in sources)
    bindings=rd(P+'D5-I193-CE11-PRELAUNCH-EVIDENCE-CLOSURE-REVIEW-CANDIDATE.json')['pending_I177_final_bindings']
    assert all(not (ROOT/r['path']).exists() for r in bindings)
    return dict(schema='d5.i265-preparation-review.v1',increment='I265',date=DATE,timezone='Europe/Madrid',base_commit=BASE,status=STATUS,candidate=pin(SUBJECT),
        counts=dict(input_pins=1122,work_packages=3,custody_sections=48,final_antecedent_records=4,antecedent_fields=61,C_fields=19,acceptance_fields=27,
            shared_types=14,shared_definitions=6,value_projections=13,antecedent_hashes=4,prior_evidence_requirements=5,nested_bundle_records=5,nested_fields=88,
            core_fields=8,bundle_fields=3,role_approvals=3,requested_returns=7,intake_criteria=20,deliverables=10,exits=9,
            actual_records_or_signatures_or_mapping_created=0,actual_received_bodies=0,actual_lots_accepted=0),
        rejection_checks=rejection_checks(d),current_effect=d['current_effect'],provenance=d['producer'],
        source_reconstruction=dict(I264_reconstruction_and_review_reproduced=True,prior_publication_mains_called=False,prior_Path_exists_restored=True,no_new_presence_projection=True),
        limitations=['A02/A04/A06 and inherited predecessors remain unaccepted,SD01 active. Conditional unsent request only; no positive finalization,C/acceptance/bundle signature,mapping or actual acceptance.',
            'W10 must reconcile same previously authentic W09 facts; changed inputs invalidate affected work before progress. Final roster/freeze cannot retroactively authenticate prior resource evidence.',
            'C/acceptance exact projections,three same-core approvals and globally unique mapping need genuine bodies/provenance/independent decisions and actual caps/currentness;221644/40500 are conditional only.',
            'No product/component execution,record/snapshot issuance,crypto/signing/keygen,enrollment/contact,registry/mapping/configuration,claim,receipt,quota,reserve,binding or D5 change.'],
        work_unit=dict(rollback_files=sorted(FILES),verification_command='python3 docs/validation/D5-I265-audit.py',expected_result=STATUS,
            runtime_harness='N/A: own documentary JSON/Git/hash/pointer/coverage/order/schema-requirement checks and in-memory documentary mutations only. No target import/compile/discovery/tests/execution/build/profiling/benchmark/positive codec/crypto/signing/keygen/enrollment/provisioning/contacts/platform/clock/CPU/IO/ledger/process/endpoint/replay/crash probes or configuration.',
            over400_lines=True,reason='Single conditional A07/RQ07 preparation covering W10-W12 final-custody/mapping handoffs with exact requirements,pins,rejection checks and preservation; overage declared,no PR requested.'),
        publication=dict(commit_and_push_requested=True,publication_not_final_records_signatures_mapping_acceptance_authority_or_execution=True))


def main():
    review=build_review();assert review==rd(PREP)
    prior=rd(PRIOR_SEAL);preserved={**prior['preserved_published809'],**prior['artifacts'],PRIOR_SEAL:sha(PRIOR_SEAL)}
    assert len(preserved)==814
    seal=rd(SEAL)
    assert seal['schema']=='d5.i265-integrity.v1' and seal['base_commit']==BASE
    assert seal['preserved_published814']==preserved and set(seal['artifacts'])==FILES-{SEAL}
    for mapping in [preserved,seal['artifacts']]:
        for path,digest in mapping.items():
            assert sha(path)==digest,path
    assert seal['source_only'] is True and seal['current_effect']==review['current_effect']
    changed=set(git('diff',BASE,'--name-only').splitlines())|set(git('ls-files','--others','--exclude-standard').splitlines())
    assert changed==FILES,changed
    subprocess.check_call(['git','merge-base','--is-ancestor',BASE,'HEAD'],cwd=ROOT)
    if git('rev-parse','HEAD')!=BASE:
        assert not git('status','--porcelain')
    print(json.dumps(dict(status=STATUS,increment='I265',input_pins=1122,preserved_published_files=814,new_files=5,
        documentary_rejections=len(review['rejection_checks']),counts=review['counts'],SD01_stop_active=True,
        prelaunch_gates_closed=0,resource_obligations_closed=0,D5_closed=False,git_head=git('rev-parse','HEAD')),sort_keys=True))


if __name__=='__main__':
    main()
