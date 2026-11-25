#!/usr/bin/env python3
"""I253 A01/RQ01 preparation: own documentary checks only."""
import copy
import hashlib
import io
import json
from pathlib import Path
import runpy
import subprocess

ROOT = Path(__file__).resolve().parents[2]
P = 'docs/validation/'
BASE = '2da7986ae5902f680023c030e79f8063e732d691'
DATE = '2026-11-25'
PLAN = P+'D5-I223-PRELAUNCH-RESOURCE-CLOSURE-PLAN.json'
ACQUISITION = P+'D5-I251-GENUINE-EVIDENCE-ACQUISITION-PLAN.json'
W01 = P+'D5-I223-W01-TARGET-SCOPE-AUTHORITY-CANDIDATE.json'
W02 = P+'D5-I223-W02-PEOPLE-AND-ANCHORS-CANDIDATE.json'
PRIOR_RECON = P+'D5-I252-I251-source-reconstruction.json'
PRIOR_REVIEW = P+'D5-I252-I251-documentary-review.json'
PRIOR_AUDIT = P+'D5-I252-audit.py'
PRIOR_SEAL = P+'D5-I252-integrity.json'
PRIOR_DOC = 'docs/design/D5-I252-I251-GENUINE-EVIDENCE-PLAN-REVIEW.md'
PRIOR_FILES = {PRIOR_RECON,PRIOR_REVIEW,PRIOR_AUDIT,PRIOR_SEAL,PRIOR_DOC}
SUBJECT = P+'D5-I251-A01-RQ01-ENTRY-AUTHORITY-SCOPE-CANDIDATE.json'
PREP = P+'D5-I253-preparation-review.json'
AUDIT = P+'D5-I253-audit.py'
SEAL = P+'D5-I253-integrity.json'
DOC = 'docs/design/D5-I253-A01-RQ01-ENTRY-AUTHORITY-SCOPE.md'
FILES = {SUBJECT,PREP,AUDIT,SEAL,DOC}
STATUS = 'PASS_STATIC_SOURCE_ONLY_A01_RQ01_PREPARED_ENTRY_AUTHORITY_MISSING_NOT_ACCEPTED_NOT_ADMITTED'


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


SCOPE_SECTIONS = ['logical_source_scope','effective_environment_scope','caller_platform_ledger_scope','policy_version_inventory',
    'numeric_candidate_ledger','protocol_output_ledger','custody_record_cap_ledger','heap_scope_ledger','phase_marker_ledger',
    'guard_obligation_ledger','transport_and_output_scope','source_requalification_boundary']
RETURNS = [
    ('RT01','Autoridad preexistente de entrada y elegibilidad EA01/EA02/EA03',
     ['entry_authority_inventory','entry_authority_boundary'],
     'Cuerpos auténticos de autoridad de proyecto/scope y de revisión/aceptación, anteriores e independientes de los futuros appointments W02 o bundle. Para cada sujeto: humano canónico/aliases, emisor y cadena de delegación autorizada, competencia, ámbito, vigencia/revocación, custodia y provenance disponibles. No autoatestación, identidad Git o etiqueta del asistente como única autoridad.'),
    ('RT02','Scope lógico exacto con ausencias explícitas',
     ['logical_source_scope','effective_environment_scope','caller_platform_ledger_scope','policy_version_inventory'],
     'Declaración genuina del target PGO181 candidato02 / PFC126-CANDIDATE-03 / I122 y sus seis rutas, closure runtime/imagen/loader, caller/plataforma/ledger/epoch/policy previstos. Separar cada hecho efectivo conocido de lo todavía ausente. Los ocho hashes documentales fijan políticas candidatas, no adopción ni implementación. Hashes y correspondencias efectivos se aportan en W03; A01 no requiere fabricar ni anticipar ese freeze.'),
    ('RT03','Límites, guards, fases y exclusiones conservados',
     ['numeric_candidate_ledger','protocol_output_ledger','custody_record_cap_ledger','heap_scope_ledger','phase_marker_ledger','guard_obligation_ledger','transport_and_output_scope','source_requalification_boundary','inherited_scope_boundaries'],
     'Reconciliación íntegra de los ledgers W01 exactos y exclusiones: ninguna cuota/reserva cambiada, helper/input oculto, lectura gratuita o cota parcial promovida. Budgets y envelopes condicionales no prueban fit, servicio o éxito900. El alcance real del sucesor necesitará recualificación y costes completos posteriores.'),
    ('RT04','Matriz genuina de autoridad por acción',
     ['action_authority_ledger','existing_external_material_intake'],
     'Identificar quién puede decidir cada acción y la prueba de esa facultad, con ámbito y vigencia. La petición actual sólo permite documentos/auditoría/commit/push; no designa actores ni adopta scope. Toda implementación/build/cualificación/medición/firma/contacto/provisión/configuración/cambio activo requiere alcance y autoridad separados. No transformar la aprobación documental de scope en autoridad operativa.'),
    ('RT05','Revisión primaria R06 y decisión separada R08 genuinas',
     ['exit_predicate_dispositions','handoff_and_deferred_scope','change_control'],
     'Cuerpos de revisión y decisión con IDs/locators inmutables, bytes/digests, sujetos elegibles, autoridad/competencia/independencia, mismo scope y motivo por requisito/salida. Declarar cada referencia o dato faltante, rechazado o aportado; ninguna casilla, firma o hash acredita verdad por sí solo. Sin revisión real y aceptación separada, A01 permanece pendiente y no habilita RQ02.')]
CRITERIA = [
    ('AC01','Autoridad preexistente auténtica de entrada, emisor/cadena/ámbito/vigencia/provenance disponibles; no W02/bundle como única autoridad futura.',['RT01']),
    ('AC02','EA01 autoridad de scope, EA02 R06 y EA03 R08 con humanos canónicos, aliases, competencia y appointments reales bajo autoridad previa.',['RT01']),
    ('AC03','Todas las exclusiones/keys/custodia y elegibilidad verificadas sobre personas reales; sin autorevisión o independencia del asistente inferida.',['RT01','RT05']),
    ('AC04','Target lógico y exactamente seis rutas, closure/runtime/imagen/caller/plataforma/ledger/políticas coherentes con W01, sin helper/entrada oculta.',['RT02']),
    ('AC05','Hechos efectivos desconocidos explícitos; sin hash predictivo ni usar futuro W03 como autoridad previa, sin exigir freeze efectivo para aceptar scope lógico.',['RT02']),
    ('AC06','Ledgers de límites/guards/fases/exclusiones exactos, sin cuota/reserva cambiada ni capacidad/servicio/900 inferidos de presupuesto.',['RT03']),
    ('AC07','Autoridad por acción explícita; documentos autorizados hoy separados de toda operación futura no autorizada.',['RT04']),
    ('AC08','Inventario íntegro de cuerpos/referencias/bytes/digests/autor/provider/custodia/scope/vigencia y todos los supuestos, con ausencias/rechazos trazables.',['RT01','RT02','RT03','RT04','RT05']),
    ('AC09','Revisión primaria genuina R06 competente e independiente sobre todos los requisitos y salidas W01, con motivo y cuerpo disponible.',['RT05']),
    ('AC10','Aceptación/rechazo separado R08 genuino sobre mismo scope/cuerpos y exclusiones, nunca la misma revisión del asistente ni accepted=true sin prueba.',['RT05']),
    ('AC11','Currentness/revocación y cambios de autoridad/scope/autores/cuerpos/política/epoch/límites invalidan lo afectado antes de avanzar.',['RT01','RT02','RT03','RT04','RT05']),
    ('AC12','Sólo aceptación genuina completa de A01 permite considerar RQ02; no lanzamiento automático ni cierre de30 gates/E01-E05/D5, CE12 diferido.',['RT05'])]


def build_candidate():
    acq,work,plan = rd(ACQUISITION),rd(W01),rd(PLAN)
    lot=acq['acquisition_lots'][0]
    assert lot['id']=='A01' and lot['covers_work_packages']==['W01'] and lot['depends_on_lots']==[]
    req=plan['work_packages'][0]
    pins={**rd(PRIOR_RECON)['input_pins'],**{path:sha(path) for path in sorted(PRIOR_FILES)}}
    assert len(pins)==1062
    return dict(schema='d5.i253-a01-rq01-documentary-preparation.v1',increment='I253',date=DATE,timezone='Europe/Madrid',base_commit=BASE,
        dossier_id='PGE251-A01-RQ01-CANDIDATE-01',lot_id='A01',request_id='RQ01',work_package='W01',planned_deliverable_id=req['deliverable_id'],
        kind='LOCAL_UNSENT_REQUEST_AND_FUTURE_INTAKE_CHECKLIST_NOT_GENUINE_MATERIAL_OR_RUNTIME_SCHEMA',
        status='A01_RQ01_DOCUMENTARY_PREPARED_ENTRY_AUTHORITY_MISSING_SD01_ACTIVE_NOT_ACCEPTED_NOT_ADMITTED',
        input_pins=pins,acquisition_lot_binding=pin(ACQUISITION,'/acquisition_lots/0'),exact_acquisition_lot=lot,
        reviewed_plan_binding=pin(PRIOR_REVIEW),W01_requirement_binding=pin(PLAN,'/work_packages/0'),exact_W01_requirement=req,
        W01_documentary_checklist=pin(W01),
        entry_gate=dict(source=pin(W01,'/entry_authority_boundary'),exact_boundary=work['entry_authority_boundary'],
            SD01_stop_active=True,actual_entry_authority=None,actual_authority_verified=False,actual_scope_accepted=False,
            no_future_W02_appointment_A07_bundle_or_root_as_sole_entry_authority=True,
            no_A01_self_authorization_from_empty_predecessor_list_or_this_user_document_request=True,
            W02_identity_requirements_used_as_eligibility_criteria_not_future_W02_acceptance_precondition=True),
        unsent_request=dict(original_draft=lot['unsent_request_draft'],
            subject='RQ01 — Autoridad preexistente de entrada y scope lógico W01 / PGO181 candidato02',
            recipient_role_only=lot['intended_recipient_role_kind'],
            reviewable_request_text='Se solicita, sólo para una futura aportación bajo autoridad propia y provenance autorizada, el material RT01-RT05 descrito en este dossier. Debe permitir revisar EA01/EA02/EA03 y los tres entregables/salidas de W01. Identifique por cada cuerpo su disponibilidad, locator, bytes/digest, autor/provider/custodia, autoridad/ámbito/vigencia y dependencias; declare lo ausente. Mantenga scope lógico separado de freeze efectivo, autoridad documental separada de operaciones y revisión R06 separada de aceptación R08. No se solicita implementar, ejecutar, medir, firmar, contactar terceros, nominar o configurar nada. Si la autoridad o el material no existen, comunique el gap y el alcance específico pendiente, sin sustituirlo por un documento o aceptación sintéticos. Esta solicitud local permanece sin enviar.',
            required_return_ids=[r[0] for r in RETURNS],is_draft_only=True,sent=False,contact_authorized=False,
            actual_recipient_person=None,actual_recipient_address_or_channel=None,actual_contact_authority=None,actual_sending_or_delivery_record=None),
        authority_evidence_requests=[dict(id=row['id'],source=pin(W01,'/entry_authority_inventory/'+str(i)),exact_existing_requirement=row,
            required_return_id='RT01',required_independent_material_fields=['canonical human and complete aliases','competence and appointment under preexisting authority',
                'authority issuer and independently authentic delegation/provenance chain','exact scope and allowed/denied actions','validity/currentness/revocation',
                'complete available body inventory, immutable locator, bytes/digest, author/provider/custody','real primary review and separate decision bodies'],
            actual_human=None,actual_preexisting_authority_chain_or_body=None,actual_eligibility_or_appointment=None,
            actual_primary_review=None,actual_separate_acceptance=None,accepted=False) for i,row in enumerate(work['entry_authority_inventory'])],
        eligibility_boundary=dict(identity_policy_source=pin(W02,'/identity_policy/exact_policy'),exact_identity_policy=rd(W02)['identity_policy']['exact_policy'],
            separation_source=pin(W02,'/separation_matrix'),exact_separation_matrix=rd(W02)['separation_matrix'],
            overlap_source=pin(W02,'/overlap_policy'),exact_overlap_policy=rd(W02)['overlap_policy'],
            all_preparers_and_source_authors_in_exclusion_scope=True,
            no_assistant_git_account_role_label_key_or_signature_alone_as_canonical_human_or_independence=True,
            no_blanket_R01_R02_separation_or_future_full_roster_required_for_A01=True,
            actual_identity_authority_or_canonical_people=None,actual_separations_verified=False),
        scope_manifest_requirements=[dict(section=section,source=pin(W01,'/'+section),documentary_requirement_count=len(work[section]),
            actual_authoritative_scope_declaration=None,accepted=False) for section in SCOPE_SECTIONS],
        logical_sources=[dict(logical_path=row['logical_path'],target_kind=row['target_kind'],actual_body_digest_or_runtime_mapping=None,
            effective_source_facts_deferred_to='W03',accepted=False) for row in work['logical_source_scope']],
        known_vs_missing=dict(policy_document_pins=work['policy_version_inventory'],
            policy_hashes_are_document_integrity_not_effective_adoption_or_source_runtime_image_proof=True,
            W01_logical_scope_does_not_require_actual_future_W03_hashes_or_freeze=True,
            actual_scope_authority_declaration=None,actual_source_runtime_image_caller_platform_epoch_or_policy_facts=None,
            no_material_or_effective_snapshot_invented=True),
        requested_returns=[dict(id=rid,title=title,requirements=text,
            W01_requirement_sources=[pin(W01,'/'+key) for key in sections],
            universal_delivery_source=pin(ACQUISITION,'/evidence_delivery_contract'),
            actual_body_inventory=None,actual_received=False,actual_primary_review=None,actual_separate_acceptance=None,accepted=False)
            for rid,title,sections,text in RETURNS],
        W01_deliverable_coverage=[dict(id='WD%02d'%(i+1),source=pin(PLAN,'/work_packages/0/deliverables/'+str(i)),exact_requirement=text,
            required_return_ids=[['RT02'],['RT03'],['RT04']][i],authority_return_id='RT01',review_return_id='RT05',
            actual_complete_delivery=None,accepted=False) for i,text in enumerate(req['deliverables'])],
        acceptance_checklist=[dict(id=cid,criterion=text,required_return_ids=ids,
            actual_evidence_inventory=None,actual_R06_primary_review=None,actual_R08_separate_decision=None,
            disposition='PENDING_GENUINE_MATERIAL_AND_COMPETENT_DECISION',accepted=False) for cid,text,ids in CRITERIA],
        W01_exit_coverage=[dict(id='WX%02d'%(i+1),source=pin(PLAN,'/work_packages/0/exit_predicates/'+str(i)),exact_predicate=text,
            required_acceptance_criteria=[c[0] for c in CRITERIA],actual_genuine_disposition=None,accepted=False) for i,text in enumerate(req['exit_predicates'])],
        intake_sequence=[
            'No envío/contacto ni nominación. Sólo considerar material genuinamente aportado con autoridad propia; no fetch o verificación de servicios.',
            'Comprobar autoridad de entrada preexistente y elegibilidad de EA01/R06/R08 sin apoyarse sólo en futuros W02/bundle; si falta, conservar SD01.',
            'Inventariar íntegros RT01-RT05, scope, cuerpos disponibles/bytes/digest/provenance/validez y cada referencia/supuesto faltante o rechazado; unknown no es cero.',
            'R06 genuino revisa los tres entregables y salidas y AC01-AC12 con motivo por criterio; el asistente y su auditor no realizan esa decisión.',
            'R08 elegible separado decide aceptar/rechazar por criterio sobre los mismos cuerpos/scope y autoridad, con registro auténtico disponible.',
            'Reconciliar currentness/revocación/dependencias e impacto; sólo A01 genuinamente aceptado permite considerar el borrador RQ02 bajo sus límites propios.'],
        missing_or_rejected_material=dict(current_disposition='MISSING_NOT_RECEIVED_NOT_EVALUATED',actual_received_inventory=None,
            provided_real_bodies=[],rejected_real_bodies=[],actual_material_evaluations=0,
            missing_authority_or_unavailable_body_keeps_SD01_and_A01_unaccepted=True,
            if_provider_reports_gap='Record exact missing authority/body/scope and separately required authority/action; do not implement,run,contact,sign,configure or replace genuine evidence with another documentary PASS.',
            no_global_absence_or_infeasibility_inferred=True),
        authority_by_action=dict(source=pin(W01,'/action_authority_ledger'),exact_existing_ledger=work['action_authority_ledger'],
            documentary_request_is_not_canonical_nomination_scope_adoption_or_operational_authority=True,
            actual_new_action_authority=None,actual_contact_or_operational_action_done=False),
        preserved_cost_scope_and_limits=dict(resource_source=pin(ACQUISITION,'/preserved_resource_and_cost_rules'),
            exact_resource_rules=acq['preserved_resource_and_cost_rules'],scope_source=pin(W01,'/inherited_scope_boundaries'),exact_scope=work['inherited_scope_boundaries'],
            same_caps_guards_no_extra_Reader_members_hidden_reads_free_costs_helpers_channels_or_outputs=True,
            quotas_budgets_reserves_unchanged=True,actual_resource_capacity_service_or_success900=None),
        handoff=dict(exact_A01_completion_predicate=lot['completion_predicate'],exact_A01_missing_stop=lot['missing_or_failure_stop'],
            next_request_only_after_genuine_A01_acceptance='RQ02',RQ02_sent_or_enabled_now=False,A02_or_W02_started_or_accepted=False,
            final_route_source=pin(PLAN,'/prelaunch_handoff_and_CE12'),exact_final_route_boundary=plan['prelaunch_handoff_and_CE12'],
            prelaunch_acceptance_not_new_requirement_to_execute_final_E06_Q_root_claim_or_receipt=True,
            no_launch_certificate_promotion_or_D5_closure_from_A01_acceptance=True,
            actual_A01_completion_or_handoff=None),
        change_control=dict(source=pin(W01,'/change_control'),exact_existing_policy=work['change_control'],
            affected_entry_authority_scope_or_body_change_requires_invalidation_and_fresh_genuine_review=True,no_active_rebind_or_snapshot_refresh=True),
        current_effect={**acq['current_effect'],'A01_RQ01_documentary_prepared':True,'A01_accepted':False,'RQ01_sent':False,
            'actual_A01_authority_scope_or_review_records_created':False},
        producer=dict(identity='Same Codex assistant/chat as I251/I252',documentary_preparer_only=True,actor_independent=False,
            competent_R06_review=False,separate_R08_acceptance=False,external_contacts_made=False),
        publication=dict(commit_and_push_requested=True,publication_not_material_authority_nomination_scope_adoption_acceptance_execution_or_D5_closure=True))


NEGATIVE_CASES = [
    ('entry_stop_bypassed',('entry_gate','SD01_stop_active'),True,False),
    ('authority_verified',('entry_gate','actual_authority_verified'),False,True),
    ('future_appointment_as_authority',('entry_gate','no_future_W02_appointment_A07_bundle_or_root_as_sole_entry_authority'),True,False),
    ('self_authorization',('entry_gate','no_A01_self_authorization_from_empty_predecessor_list_or_this_user_document_request'),True,False),
    ('future_W02_required',('entry_gate','W02_identity_requirements_used_as_eligibility_criteria_not_future_W02_acceptance_precondition'),True,False),
    ('draft_sent',('unsent_request','sent'),False,True),
    ('contact_granted',('unsent_request','contact_authorized'),False,True),
    ('recipient_invented',('unsent_request','actual_recipient_person'),None,'UNVERIFIED_TEST_LABEL'),
    ('address_invented',('unsent_request','actual_recipient_address_or_channel'),None,'UNVERIFIED_TEST_LABEL'),
    ('authority_chain_fabricated',('authority_evidence_requests',0,'actual_preexisting_authority_chain_or_body'),None,{}),
    ('R06_as_genuine',('authority_evidence_requests',1,'actual_primary_review'),None,'UNVERIFIED_TEST_LABEL'),
    ('R08_accepted',('authority_evidence_requests',2,'accepted'),False,True),
    ('separation_verified',('eligibility_boundary','actual_separations_verified'),False,True),
    ('future_full_roster_required',('eligibility_boundary','no_blanket_R01_R02_separation_or_future_full_roster_required_for_A01'),True,False),
    ('scope_adopted',('scope_manifest_requirements',0,'accepted'),False,True),
    ('source_hash_predicted',('logical_sources',0,'actual_body_digest_or_runtime_mapping'),None,'UNVERIFIED_TEST_LABEL'),
    ('effective_freeze_required',('known_vs_missing','W01_logical_scope_does_not_require_actual_future_W03_hashes_or_freeze'),True,False),
    ('policy_as_runtime_proof',('known_vs_missing','policy_hashes_are_document_integrity_not_effective_adoption_or_source_runtime_image_proof'),True,False),
    ('return_received',('requested_returns',0,'actual_received'),False,True),
    ('return_accepted',('requested_returns',4,'accepted'),False,True),
    ('deliverable_created',('W01_deliverable_coverage',0,'actual_complete_delivery'),None,'UNVERIFIED_TEST_LABEL'),
    ('criterion_accepted',('acceptance_checklist',0,'accepted'),False,True),
    ('exit_accepted',('W01_exit_coverage',0,'accepted'),False,True),
    ('inventory_fabricated',('missing_or_rejected_material','actual_received_inventory'),None,[]),
    ('documentary_pass_as_material',('missing_or_rejected_material','missing_authority_or_unavailable_body_keeps_SD01_and_A01_unaccepted'),True,False),
    ('operational_authority_granted',('authority_by_action','actual_new_action_authority'),None,'UNVERIFIED_TEST_LABEL'),
    ('quota_change',('preserved_cost_scope_and_limits','quotas_budgets_reserves_unchanged'),True,False),
    ('RQ02_started',('handoff','RQ02_sent_or_enabled_now'),False,True),
    ('A02_accepted',('handoff','A02_or_W02_started_or_accepted'),False,True),
    ('final_execution_precondition',('handoff','prelaunch_acceptance_not_new_requirement_to_execute_final_E06_Q_root_claim_or_receipt'),True,False),
    ('silent_scope_transfer',('change_control','affected_entry_authority_scope_or_body_change_requires_invalidation_and_fresh_genuine_review'),True,False),
    ('D5_closed',('current_effect','D5_closed'),False,True),
    ('A01_accepted',('current_effect','A01_accepted'),False,True),
    ('independent_assistant',('producer','actor_independent'),False,True)]


def validate(d):
    for name,path,expected,_ in NEGATIVE_CASES:
        node=d
        for key in path:
            node=node[key]
        assert type(node) is type(expected) and node==expected,name
    assert d==build_candidate(),'A01/RQ01 differs from exact documentary reconstruction'
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
    assert [r['id'] for r in d['authority_evidence_requests']]==['EA01','EA02','EA03']
    assert len(d['scope_manifest_requirements'])==12 and len(d['logical_sources'])==6
    assert len(d['requested_returns'])==5 and len(d['W01_deliverable_coverage'])==3
    assert len(d['acceptance_checklist'])==12 and len(d['W01_exit_coverage'])==3
    all_returns={r['id'] for r in d['requested_returns']}
    assert all(set(row['required_return_ids'])<=all_returns for row in d['acceptance_checklist'])
    assert all(row['actual_body_digest_or_runtime_mapping'] is None and not (ROOT/row['logical_path']).exists() for row in d['logical_sources'])
    ce11=rd(P+'D5-I193-CE11-PRELAUNCH-EVIDENCE-CLOSURE-REVIEW-CANDIDATE.json')
    assert all(not (ROOT/row['path']).exists() for row in ce11['pending_I177_final_bindings'])
    return dict(schema='d5.i253-preparation-review.v1',increment='I253',date=DATE,timezone='Europe/Madrid',base_commit=BASE,status=STATUS,
        candidate=pin(SUBJECT),counts=dict(input_pins=1062,authority_slots=3,scope_sections=12,logical_source_paths=6,
            requested_returns=5,W01_deliverables=3,acceptance_criteria=12,W01_exits=3,actual_received_bodies=0,actual_authorities_verified=0,actual_lots_accepted=0),
        rejection_checks=rejection_checks(d),current_effect=d['current_effect'],provenance=d['producer'],
        source_reconstruction=dict(I252_reconstruction_and_review_reproduced=True,prior_publication_mains_called=False,prior_Path_exists_restored=True,no_new_presence_projection=True),
        limitations=['A01/RQ01 is documentary preparation only. Genuine preexisting EA01/R06/R08 authority, complete bodies and competent primary/separate decisions remain absent; SD01 active.',
            'No recipient,contact authority,nomination,delivery,canonical identity,scope adoption or actual acceptance is created. W02 eligibility policies are requirements, not a backward dependency on future W02 acceptance.',
            'Scope is logical, not effective source freeze; W03 must provide genuine hashes/closure under own authority. No future source/image/body hash is predicted.',
            'Thirty prelaunch gates and E01-E05 remain pending. No actual source,component,platform,crypto,claim,receipt,quota,reserve,binding or D5 change.'],
        work_unit=dict(rollback_files=sorted(FILES),verification_command='python3 docs/validation/D5-I253-audit.py',expected_result=STATUS,
            runtime_harness='N/A: own documentary JSON/Git/hash/pointer/coverage checks and in-memory documentary mutations only; no product/components/import/compile/discovery/tests/build/benchmark/positive crypto/signing/keygen/provisioning/contacts/clock/CPU/IO/platform/ledger/process/endpoint probes or configuration.',
            over400_lines=True,reason='One A01/RQ01 preparation with reviewable unsent request, exact source pins, intake/acceptance requirements and integrity preservation. Overage declared; no PR requested.'),
        publication=dict(commit_and_push_requested=True,publication_not_authority_material_scope_acceptance_or_execution=True))


def main():
    review=build_review()
    assert review==rd(PREP)
    prior=rd(PRIOR_SEAL)
    preserved={**prior['preserved_published749'],**prior['artifacts'],PRIOR_SEAL:sha(PRIOR_SEAL)}
    assert len(preserved)==754
    seal=rd(SEAL)
    assert seal['schema']=='d5.i253-integrity.v1' and seal['base_commit']==BASE
    assert seal['preserved_published754']==preserved and set(seal['artifacts'])==FILES-{SEAL}
    for mapping in [preserved,seal['artifacts']]:
        for path,digest in mapping.items():
            assert sha(path)==digest,path
    assert seal['source_only'] is True and seal['current_effect']==review['current_effect']
    changed=set(git('diff',BASE,'--name-only').splitlines())|set(git('ls-files','--others','--exclude-standard').splitlines())
    assert changed==FILES,changed
    subprocess.check_call(['git','merge-base','--is-ancestor',BASE,'HEAD'],cwd=ROOT)
    if git('rev-parse','HEAD')!=BASE:
        assert not git('status','--porcelain')
    print(json.dumps(dict(status=STATUS,increment='I253',input_pins=1062,preserved_published_files=754,new_files=5,
        documentary_rejections=len(review['rejection_checks']),counts=review['counts'],SD01_stop_active=True,
        prelaunch_gates_closed=0,resource_obligations_closed=0,D5_closed=False,git_head=git('rev-parse','HEAD')),sort_keys=True))


if __name__=='__main__':
    main()
