#!/usr/bin/env python3
"""I269 consolidated A01-A08 documentary handoff; no target/component execution."""
import copy
import hashlib
import io
import json
from pathlib import Path
import runpy
import subprocess

ROOT = Path(__file__).resolve().parents[2]
P = 'docs/validation/'
BASE = '4d3819826a8464807938e4d8d906c016d6ebc5ac'
DATE = '2026-11-26'
PLAN = P+'D5-I223-PRELAUNCH-RESOURCE-CLOSURE-PLAN.json'
ACQUISITION = P+'D5-I251-GENUINE-EVIDENCE-ACQUISITION-PLAN.json'
PRIOR_RECON = P+'D5-I268-I267-source-reconstruction.json'
PRIOR_REVIEW = P+'D5-I268-I267-documentary-review.json'
PRIOR_AUDIT = P+'D5-I268-audit.py'
PRIOR_SEAL = P+'D5-I268-integrity.json'
PRIOR_DOC = 'docs/design/D5-I268-I267-A08-RQ08-REVIEW.md'
PRIOR_FILES = {PRIOR_RECON,PRIOR_REVIEW,PRIOR_AUDIT,PRIOR_SEAL,PRIOR_DOC}
SUBJECT = P+'D5-I269-A01-A08-CONSOLIDATED-HANDOFF-CANDIDATE.json'
PREP = P+'D5-I269-preparation-review.json'
AUDIT = P+'D5-I269-audit.py'
SEAL = P+'D5-I269-integrity.json'
DOC = 'docs/design/D5-I269-A01-A08-CONSOLIDATED-HANDOFF.md'
FILES = {SUBJECT,PREP,AUDIT,SEAL,DOC}
STATUS = 'PASS_STATIC_SOURCE_ONLY_A01_A08_HANDOFF_CONSOLIDATED_RQ01_ENTRY_AND_ALL_GENUINE_EVIDENCE_ACCEPTANCES_PENDING_NOT_ADMITTED'


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


DOSSIERS = { 'A%02d'%i:P+'D5-I251-A%02d-RQ%02d-%s-CANDIDATE.json'%(i,i,name) for i,name in enumerate([
'ENTRY-AUTHORITY-SCOPE','PEOPLE-APPOINTMENTS-ANCHORS','SOURCES-IMAGE-RUNTIME','CALLER-PLATFORM-SERVICE',
'REQUALIFICATION-COMPLETE-BOUNDS','INDEPENDENT-RESOURCE-JOIN','FINAL-CUSTODY-MAPPING','GENUINE-PRELAUNCH-GATE-DECISION'],1)}
REVIEWS = {'A%02d'%i:P+'D5-I%d-I%d-documentary-review.json'%(252+2*i,251+2*i) for i in range(1,9)}
POLICIES = 'existing_material_boundary evidence_delivery_contract critical_order_rules intake_and_review_workflow stop_rules preserved_resource_and_cost_rules final_route_boundary authority_boundary preserved_scope_and_gates'.split()
SUMMARIES = [
'Autoridad de entrada y scope objetivo: EA01 accountable scope authority,EA02 R06 y EA03 R08 auténticos bajo autoridad preexistente;scope lógico/límites/acciones y decisiones propias,sin futura A02/bundle como única justificación.',
'Humanos canónicos,aliases,competencia/appointments/claves/anchors/política previa y14 exclusiones con preparadores completos;intake provisional,no preaprobación de futuros autores.',
'Seis fuentes reales calificadas,imagen externa distinta de runtime,clausura completa interpreter/loader/stdlib/native/crypto y provenance/source-to-image/políticas/baseline inmutable;sin crear/build/cualificar aquí.',
'Caller/constructor/dominio/endpoints y ocho garantías exigibles con evidencia tipada,capacidad/servicio o WCET/demoras/reloj/global-ledger durable y custodia;nombre/fd/schema/presupuesto no mecanismo o garantía.',
'W05 primero,después W06/W07 compatibles y W08:recualificación sucesor/CP03/atomicidad/rutas,heap H01-H11 completo/vidas,all30 trabajo/CPU/IO/servicio y fases de éxito900 con todos los supuestos.',
'Join W09 genuino R03/R06 y R08 de E01-E05/20 criterios y pruebas CP03/ATOMICITY/BASIS/index;BASIS revisión separada,no octavo proof de índice;scope/unidades/premisas/costes/derivaciones completos.',
'W10→W11→W12 sobre mismos hechos W09 ya auténticos:roster/cuatro registros finales,C19/acceptance27,core8/bundle3/cinco registros/tres aprobaciones mismo core y mapping único global exacto epoch/digest C;sin emisión o configuración.',
'W13 decide cada30 gates(7familias16reglas7globales) y join compatible con R06/R08 genuinos;W13 salida,no propio antecedente;handoff X09 limitado y recibo31 CE12 privado diferido,no ejecución o cierre D5.']


def criteria_key(lot):
    return 'intake_acceptance_checklist' if lot=='A06' else 'acceptance_checklist'


def coverage_key(d,suffix):
    return next(k for k in d if k.endswith(suffix))


def build_candidate():
    acq,plan=rd(ACQUISITION),rd(PLAN);ds={k:rd(v) for k,v in DOSSIERS.items()}
    pins={**rd(PRIOR_RECON)['input_pins'],**{p:sha(p) for p in PRIOR_FILES}};assert len(pins)==1142
    lots=acq['acquisition_lots'];first=ds['A01'];last=ds['A08']
    return dict(schema='d5.i269-consolidated-handoff.v1',increment='I269',date=DATE,timezone='Europe/Madrid',base_commit=BASE,
        handoff_id='PGE251-A01-A08-HANDOFF-CANDIDATE-01',kind='LOCAL_UNSENT_CONSOLIDATED_REQUEST_INDEX_NOT_GENUINE_DELIVERY_INTAKE_ACCEPTANCE_OR_NEW_PLAN',
        status='A01_A08_DOCUMENTARY_HANDOFF_READY_FOR_REVIEW_SD01_ACTIVE_RQ01_FIRST_ALL_GENUINE_EVIDENCE_AND_ACCEPTANCES_PENDING_NOT_ADMITTED',
        input_pins=pins,plan=pin(ACQUISITION),latest_documentary_review=pin(PRIOR_REVIEW),
        cover_note=dict(text='Para revisión local:el paquete reúne RQ01-RQ08 y sus52 retornos/136 criterios existentes. Primero RQ01/RT01:autoridad preexistente EA01/EA02/EA03 y scope lógico genuinos;sin ello SD01 y ningún avance positivo. Sólo material genuino disponible con provenance autorizada propia y decisiones competentes independientes puede completar lotes. Seguir dependencias exactas;si falta/cambia material,registrar gaps y autoridad separada,no generar pruebas. No contactar/enviar/nominar/firmar/configurar/probar/ejecutar ni cambiar cuotas/reservas. Este índice y publicaciones no son evidencia externa o aceptación. CE12/finalroute aparte,diferido,sin comando o liberación.',
            recipient_roles_only=True,actual_accountable_coordinator=None,actual_recipient_persons_addresses_channels=None,actual_contact_or_delivery_authority=None,
            is_draft_only=True,sent=False,external_contacts_made=False,actual_delivery_or_receipt=None),
        first_material_request=dict(lot_id='A01',request_id='RQ01',return_key='A01/RT01',first_handoff_source=pin(ACQUISITION,'/first_handoff'),
            exact_first_handoff=acq['first_handoff'],entry_source=pin(DOSSIERS['A01'],'/entry_gate'),exact_entry_boundary=first['entry_gate'],
            required_entry_evidence=[dict(id=r['id'],subject=r['exact_existing_requirement']['subject'],required_role=r['exact_existing_requirement']['required_role'],
                source=pin(DOSSIERS['A01'],'/authority_evidence_requests/'+str(i)),mandatory_material_fields=r['required_independent_material_fields'],
                actual_genuine_body_or_authority=None,accepted=False) for i,r in enumerate(first['authority_evidence_requests'])],
            all_A01_return_keys=['A01/'+r['id'] for r in first['requested_returns']],
            no_A01_self_authorization_or_future_A02_bundle_forecast_authority=True,no_external_contact_fetch_or_verification_service_authorized=True,
            W02_eligibility_requirements_not_backward_W02_acceptance_dependency=True,SD01_stop_active=True,
            actual_entry_authority_scope_primary_or_separate_acceptance=None,RQ01_sent=False,RQ02_or_downstream_enabled=False),
        lot_cards=[dict(id=lot['id'],request_id=ds[lot['id']]['request_id'],title=lot['title'],material_summary=SUMMARIES[i],
            source=pin(ACQUISITION,'/acquisition_lots/'+str(i)),dossier=pin(DOSSIERS[lot['id']]),documentary_review=pin(REVIEWS[lot['id']]),
            request_source=pin(DOSSIERS[lot['id']],'/unsent_request'),exact_draft=ds[lot['id']]['unsent_request'],
            depends_on_lots=lot['depends_on_lots'],covers_work_packages=lot['covers_work_packages'],
            recipient_role_only=lot['intended_recipient_role_kind'],primary_review_roles=lot['required_primary_review_roles'],separate_acceptor_role=lot['separate_acceptor_role'],
            return_keys=[lot['id']+'/'+r['id'] for r in ds[lot['id']]['requested_returns']],
            intake_criterion_keys=[lot['id']+'/'+r['id'] for r in ds[lot['id']][criteria_key(lot['id'])]],
            deliverable_source=pin(DOSSIERS[lot['id']],'/'+coverage_key(ds[lot['id']],'deliverable_coverage')),
            exit_source=pin(DOSSIERS[lot['id']],'/'+coverage_key(ds[lot['id']],'exit_coverage')),
            exact_completion_predicate=lot['completion_predicate'],exact_missing_stop=lot['missing_or_failure_stop'],
            prerequisite_acceptances_not_documentary_reviews=True,current_material_disposition='MISSING',actual_received_bodies_or_decisions=None,
            actual_reviewers_or_provider=None,actual_completion_or_validity=None,request_sent=False,accepted=False) for i,lot in enumerate(lots)],
        return_index=[dict(key=k+'/'+r['id'],lot_id=k,id=r['id'],title=r['title'],source=pin(DOSSIERS[k],'/requested_returns/'+str(i)),
            complete_source_requirement_retained_not_summarized_away=True,evidence_delivery_contract=pin(ACQUISITION,'/evidence_delivery_contract'),
            actual_body_inventory_or_provenance=None,current_material_disposition='MISSING',accepted=False) for k,d in ds.items() for i,r in enumerate(d['requested_returns'])],
        intake_criterion_index=[dict(key=k+'/'+r['id'],lot_id=k,id=r['id'],source=pin(DOSSIERS[k],'/'+criteria_key(k)+'/'+str(i)),
            criterion=r['criterion'],actual_evidence_primary_review_or_separate_decision=None,accepted=False) for k,d in ds.items() for i,r in enumerate(d[criteria_key(k)])],
        work_package_handoffs=[dict(id=req['id'],lot_id=next(lot['id'] for lot in lots if req['id'] in lot['covers_work_packages']),source=pin(PLAN,'/work_packages/'+str(i)),
            depends_on_work_packages=req['depends_on'],planned_deliverable_id=req['deliverable_id'],primary_review_roles=req['primary_review_roles'],separate_acceptor_role=req['separate_acceptor_role'],
            actual_complete_package_or_competent_reviews=None,accepted=False) for i,req in enumerate(plan['work_packages'])],
        exact_order=dict(source=pin(ACQUISITION,'/lot_order'),exact_lot_order=acq['lot_order'],work_graph_source=pin(ACQUISITION,'/exact_I223_work_dependency_graph'),
            exact_work_dependency_graph=acq['exact_I223_work_dependency_graph'],critical_rules_source=pin(ACQUISITION,'/critical_order_rules'),
            exact_critical_rules=acq['critical_order_rules'],actual_lots_accepted=0,no_new_phase_lot_or_reverse_acceptance_dependency=True),
        milestone_requests=[dict(id=r['id'],lots=r['lots'],source=pin(ACQUISITION,'/real_milestones/'+str(i)),required_genuine_completion=r['evidence_of_completion'],
            actual_completion_or_date=None,accepted=False) for i,r in enumerate(acq['real_milestones'])],
        gate_collection_handoffs=[dict(id=r['id'],category=r['category'],source=pin(ACQUISITION,'/gate_to_collection_matrix/'+str(i)),
            A08_request_source=pin(DOSSIERS['A08'],'/gate_decision_requests/'+str(i)),required_collection_lots=r['required_collection_lots'],
            required_work_package_ids=r['required_work_package_ids'],W13_output_not_accepted_predecessor=('W13' in r['required_work_package_ids']),
            actual_complete_same_scope_evidence_or_R06_R08_decisions=None,accepted=False,closed=False) for i,r in enumerate(acq['gate_to_collection_matrix'])],
        resource_join_handoffs=[dict(id=r['id'],source=pin(ACQUISITION,'/resource_acceptance_matrix/'+str(i)),producer_lots=r['producer_lots'],
            A06_obligation_source=pin(DOSSIERS['A06'],'/obligation_decision_requests/'+str(i)),A08_obligation_source=pin(DOSSIERS['A08'],'/resource_decision_requests/'+str(i)),
            criterion_ids=[r['id']+'-R%d'%j for j in range(1,5)],W09_required_roles=['R03','R06','R08'],W13_required_roles=['R06','R08'],
            W13_review_not_substitute_for_W09=True,actual_joint_derivation_scope_compatibility_or_reviews=None,accepted=False,closed=False) for i,r in enumerate(acq['resource_acceptance_matrix'])],
        authority_request_ledger=[dict(work_id=r['work_id'],collection_lot=r['collection_lot'],source=pin(ACQUISITION,'/future_authority_resolution_ledger/'+str(i)),
            exact_separate_action_classes=r['exact_separate_action_classes'],if_required_for_missing_material=r['if_required_for_missing_material'],
            required_separate_proposal_fields=['exact action and purpose','canonical accountable actor and eligible reviewer','exact source/body/runtime/platform/scope and dependent packages',
                'complete resource/cost/phase and unchanged-limit impact','independent authority/provenance/validity and allowed/denied actions','invalidation and acceptance conditions'],
            actual_new_authority_actor_or_proposal=None,authorized_now=False,work_performed=False) for i,r in enumerate(acq['future_authority_resolution_ledger'])],
        inherited_policies=[dict(section=s,source=pin(ACQUISITION,'/'+s),exact_requirement=acq[s]) for s in POLICIES],
        future_intake_route=dict(source=pin(ACQUISITION,'/intake_and_review_workflow'),ordered_steps=acq['intake_and_review_workflow']['ordered_steps'],
            allowed_material_dispositions=acq['intake_and_review_workflow']['allowed_future_dispositions'],
            same_assistant_not_primary_or_separate_genuine_decision=True,all_missing_provided_rejected_reference_instances_and_assumptions_visible=True,
            unknown_not_zero_no_predictive_hash_or_template_as_body=True,actual_received_inventory=None,provided_real_bodies=[],rejected_real_bodies=[],
            actual_evaluations=0,actual_primary_review_or_separate_acceptances=None),
        critical_boundaries=dict(
            first_RQ01_preexisting_scope_and_EA01_R06_R08_authority_SD01_active_no_self_or_forecast_authority=True,
            all_eight_local_drafts_unsent_no_contact_nomination_or_fake_provider_schedule=True,
            all52_returns136_intake_criteria_and41_deliverables39_exits_preserved_in_original_dossiers=True,
            exact_lot_and_work_dependencies_no_new_phase_or_reverse_acceptance_edges=True,
            all_real_authors_preparers_full_bodies_baseline_facts_authentic_before_A06_W09=True,
            A07_final_freeze_same_W09_facts_not_retrospective_authentication=True,
            eight_roles14_exclusions_canonical_humans_keys_competence_appointments_and_R08_independent=True,
            A03_real_sources_image_runtime_and_A04_enforceable_capacity_service_before_derivations=True,
            heap_all11_owners_lifetimes_all30_work_CPU_IO_WCET_service_clock_success_phases900_complete_not_budgets=True,
            unknown_not_zero_no_unproved_overlap_CPU_sum_not_wall_watchdog_not_success=True,
            all5_obligations20_resource_criteria_A06_W09_R03_R06_R08_not_replaced_by_A08_W13=True,
            seven_index_proof_kinds_BASIS_separate_not_eighth_complete_bodies_fit_or_reject_no_truncation=True,
            all30_gate_decisions_A08_R06_R08_W13_output_not_self_predecessor=True,
            actual_reference_inventory_required_69_templates_not_unique_bodies_or_truth=True,
            both_Readers_all_global_lookup_freshness_identity_crypto_native_IO_copy_registry_ledger_receipt_output_failure_costs_retained=True,
            C19_acceptance27_no_standalone_acceptance_signature_core8_bundle3_three_same_core_role_domain_one_NUL_approvals=True,
            mapping_exact_epoch_complete_C_digest_unique_global_not_partitioned_no_extra_intrinsic_worker_channel=True,
            conditional221644_margin40500_not_real_encoding_fit_capacity_service_heap_CPU_or_reserve=True,
            changed_author_body_source_runtime_caller_domain_resource_epoch_key_policy_mapping_graph_invalidates_any_affected_A01_A08=True,
            CE12_private_receipt31_deferred_no_final_events_or_execution_as_new_prelaunch_condition=True,
            four_external_prerequisites_before_claim_then_actual_claim_construction_before_receipt_no_self_condition_free_retry_or_reuse=True,
            no_record_snapshot_C_Q_root_signature_crypto_keygen_enrollment_provision_configuration_probe_or_target_execution_authorized=True,
            no_quota_reserve_budget_transfer_authority_destination_active_binding_certificate_PJC115_R2_or_D5_release=True,
            further_documentary_PASS_or_commit_push_not_genuine_evidence_independence_or_acceptance=True),
        final_handoff_boundary=dict(A08_source=pin(DOSSIERS['A08'],'/handoff'),exact_A08_boundary=last['handoff'],
            I251_source=pin(ACQUISITION,'/final_route_boundary'),exact_I251_boundary=acq['final_route_boundary'],
            actual_accepted_prelaunch_handoff=None,current_run_command=None,actual_final_route_or_receipt_authorized=False,
            actual_Q_root_claim_spawn_receipt_or_final_artifact_created=False,no_new_A09_or_automatic_release=True),
        current_effect={**last['current_effect'],'A01_A08_consolidated_documentary_handoff_prepared':True,'actual_consolidated_handoff_delivery_or_intake_progress':False,
            'actual_new_genuine_evidence_or_authority_or_acceptance_created':False},
        producer=dict(identity='Same Codex assistant/chat as A01-A08 preparations/reviews',documentary_preparer_only=True,actor_independent=False,
            competent_primary_role_review=False,separate_R08_acceptance=False,external_contacts_made=False),
        publication=dict(commit_and_push_requested=True,publication_not_delivery_genuine_evidence_authority_acceptance_execution_or_D5_closure=True))


def validate(d):
    assert d==build_candidate(),'Consolidated handoff differs from exact documentary reconstruction'
    acq,plan=rd(ACQUISITION),rd(PLAN);lots=d['lot_cards'];ids=list(DOSSIERS)
    assert [r['id'] for r in lots]==ids and len(lots)==8
    assert len(d['return_index'])==52 and len({r['key'] for r in d['return_index']})==52
    assert len(d['intake_criterion_index'])==136 and len({r['key'] for r in d['intake_criterion_index']})==136
    assert sum(len(fragment(r['deliverable_source'])) for r in lots)==41 and sum(len(fragment(r['exit_source'])) for r in lots)==39
    for i,row in enumerate(lots):
        source=fragment(row['source']);dossier=fragment(row['dossier']);draft=fragment(row['request_source']);review=fragment(row['documentary_review'])
        assert source==acq['acquisition_lots'][i] and source['id']==row['id']==dossier['lot_id']
        assert row['exact_draft']==draft==dossier['unsent_request'] and draft['sent'] is False and draft['contact_authorized'] is False
        assert review['findings']==[] and review['provenance']['actor_independent'] is False
        assert row['depends_on_lots']==acq['lot_order']['graph'][row['id']]
    for row in d['return_index']:assert fragment(row['source'])['id']==row['id'] and row['key']==row['lot_id']+'/'+row['id']
    for row in d['intake_criterion_index']:assert fragment(row['source'])['criterion']==row['criterion']
    assert [r['id'] for r in d['work_package_handoffs']]==['W%02d'%i for i in range(1,14)]
    assert [r['id'] for r in d['milestone_requests']]==['M%02d'%i for i in range(1,8)]
    for row in d['gate_collection_handoffs']:
        src=fragment(row['source']);req=fragment(row['A08_request_source']);assert row['id']==src['id']==req['id']
        assert row['required_collection_lots']==req['required_collection_lots'] and row['required_work_package_ids']==req['producer_work_package_ids']
        assert row['W13_output_not_accepted_predecessor']==('W13' in row['required_work_package_ids'])
    assert len(d['gate_collection_handoffs'])==30 and [r['id'] for r in d['resource_join_handoffs']]==['E%02d'%i for i in range(1,6)]
    for row in d['resource_join_handoffs']:
        assert fragment(row['A06_obligation_source'])['id']==fragment(row['A08_obligation_source'])['id']==row['id']
        assert fragment(row['A06_obligation_source'])['criterion_ids']==row['criterion_ids']==fragment(row['A08_obligation_source'])['criterion_ids']
    assert len(d['authority_request_ledger'])==13 and all(r['authorized_now'] is False for r in d['authority_request_ledger'])
    order=acq['lot_order']['topological_order'];assert all(order.index(dep)<order.index(k) for k,ds in acq['lot_order']['graph'].items() for dep in ds)
    assert d['first_material_request']['exact_entry_boundary']['SD01_stop_active'] is True
    assert [r['id'] for r in d['first_material_request']['required_entry_evidence']]==['EA01','EA02','EA03']
    assert len(d['critical_boundaries'])==24 and all(v is True for v in d['critical_boundaries'].values())
    pointers(d)


# In-memory documentary changes only, never supplied as positive evidence.
NEGATIVE_CASES = [
('cover_sent',('cover_note','sent'),True),('contact',('cover_note','external_contacts_made'),True),('coordinator',('cover_note','actual_accountable_coordinator'),'UNVERIFIED_TEST_LABEL'),
('first_lot',('first_material_request','lot_id'),'A08'),('first_return',('first_material_request','return_key'),'A08/GD01'),
('entry_authority',('first_material_request','actual_entry_authority_scope_primary_or_separate_acceptance'),{}),('SD01',('first_material_request','SD01_stop_active'),False),
('downstream_enabled',('first_material_request','RQ02_or_downstream_enabled'),True),('EA_missing',('first_material_request','required_entry_evidence'),[]),
('lot_missing',('lot_cards',),[]),('dossier_changed',('lot_cards',0,'dossier','json_pointer'),'/unsent_request'),('review_as_acceptance',('lot_cards',7,'accepted'),True),
('dependency_removed',('lot_cards',7,'depends_on_lots'),['A07']),('original_draft_changed',('lot_cards',0,'exact_draft','sent'),True),
('return_missing',('return_index',),[]),('return_as_body',('return_index',0,'actual_body_inventory_or_provenance'),{}),('provided_accepted',('return_index',0,'accepted'),True),
('criterion_missing',('intake_criterion_index',),[]),('criterion_accepted',('intake_criterion_index',0,'accepted'),True),('work_missing',('work_package_handoffs',),[]),
('work_self_dependency',('work_package_handoffs',12,'depends_on_work_packages'),['W13']),('milestone_accepted',('milestone_requests',0,'accepted'),True),
('gate_missing',('gate_collection_handoffs',),[]),('gate_closed',('gate_collection_handoffs',29,'closed'),True),
('W13_self_predecessor',('gate_collection_handoffs',29,'W13_output_not_accepted_predecessor'),False),('resource_missing',('resource_join_handoffs',),[]),
('resource_review_replaced',('resource_join_handoffs',0,'W09_required_roles'),['R06','R08']),('resource_closed',('resource_join_handoffs',4,'closed'),True),
('authority_granted',('authority_request_ledger',2,'authorized_now'),True),('work_performed',('authority_request_ledger',3,'work_performed'),True),
('inventory_fabricated',('future_intake_route','actual_received_inventory'),[]),('scope_accepted',('lot_cards',0,'actual_received_bodies_or_decisions'),{}),
('proof_template_as_body',('critical_boundaries','actual_reference_inventory_required_69_templates_not_unique_bodies_or_truth'),False),
('offline_cost_free',('critical_boundaries','both_Readers_all_global_lookup_freshness_identity_crypto_native_IO_copy_registry_ledger_receipt_output_failure_costs_retained'),False),
('budget_as_proof',('critical_boundaries','heap_all11_owners_lifetimes_all30_work_CPU_IO_WCET_service_clock_success_phases900_complete_not_budgets'),False),
('fit_promoted',('critical_boundaries','conditional221644_margin40500_not_real_encoding_fit_capacity_service_heap_CPU_or_reserve'),False),
('retroauth',('critical_boundaries','A07_final_freeze_same_W09_facts_not_retrospective_authentication'),False),
('new_phase',('exact_order','no_new_phase_lot_or_reverse_acceptance_dependency'),False),('old_transfer',('critical_boundaries','changed_author_body_source_runtime_caller_domain_resource_epoch_key_policy_mapping_graph_invalidates_any_affected_A01_A08'),False),
('receipt_precondition',('critical_boundaries','CE12_private_receipt31_deferred_no_final_events_or_execution_as_new_prelaunch_condition'),False),
('claim_self_condition',('critical_boundaries','four_external_prerequisites_before_claim_then_actual_claim_construction_before_receipt_no_self_condition_free_retry_or_reuse'),False),
('run_command',('final_handoff_boundary','current_run_command'),'UNVERIFIED_TEST_LABEL'),('receipt_authorized',('final_handoff_boundary','actual_final_route_or_receipt_authorized'),True),
('A09_added',('final_handoff_boundary','no_new_A09_or_automatic_release'),False),('quotas_or_release',('critical_boundaries','no_quota_reserve_budget_transfer_authority_destination_active_binding_certificate_PJC115_R2_or_D5_release'),False),
('D5_closed',('current_effect','D5_closed'),True),('delivery_progress',('current_effect','actual_consolidated_handoff_delivery_or_intake_progress'),True),
('assistant_independent',('producer','actor_independent'),True)]


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
    return dict(schema='d5.i269-preparation-review.v1',increment='I269',date=DATE,timezone='Europe/Madrid',base_commit=BASE,status=STATUS,subject=pin(SUBJECT),findings=[],
        counts=dict(input_pins=1142,lot_cards=8,unsent_requests=8,requested_returns=52,intake_criteria=136,work_packages=13,deliverables=41,exits=39,milestones=7,
            first_entry_evidence_requirements=3,gate_collection_rows=30,resource_obligations=5,resource_criteria=20,authority_action_rows=13,inherited_policy_sections=9,
            critical_boundaries=24,documentary_rejections=len(NEGATIVE_CASES),preserved_published_files=834,new_files=5,actual_received_bodies=0,actual_lots_accepted=0,
            prelaunch_gates_closed=0,resource_obligations_closed=0),rejection_checks=rejections(d),
        source_reconstruction=dict(eight_original_dossiers_and_documentary_reviews_pinned=True,I268_reconstruction_and_review_reproduced=True,prior_publication_mains_called=False,prior_Path_exists_restored=True,no_new_presence_projection=True),
        current_effect=d['current_effect'],limitations=[
            'This is one local unsent index/cover handoff of existing A01-A08 requests,not another collection plan,new phase,external delivery,genuine evidence or accepted milestone.',
            'First genuine material remains RQ01/RT01 preexisting EA01/EA02/EA03 authority and complete A01 scope/reviews. All lots unaccepted,SD01 active; no nomination,contact or downstream positive intake.',
            '52 return requests/136 intake criteria/41 deliverables/39 exits retain original exact requirements. Index references/documentary hashes are no actual or unique proof inventory and add no free runtime inputs.',
            'No genuine identities/providers/bodies/reviews/decisions received; no schedule or completion guarantee.30 gates,E01-E05/20 criteria,PJC115-R2 and D5 remain open,CE12 deferred under separate authority.'],
        work_unit=dict(rollback_files=sorted(FILES),verification_command='python3 docs/validation/D5-I269-audit.py',expected_result=STATUS,over400_lines=True,
            reason='Single consolidated documentary handoff linking8 reviewed lots/52 returns/136 criteria,source pins,rejection checks and preservation; overage declared,no PR requested.',
            runtime_harness='N/A: own documentary JSON/Git/hash/pointer/coverage/graph checks and in-memory mutations only; no target import,compile,discovery,tests,execution,build,benchmark,codec,crypto,signing,keygen,enrollment,contacts,provision,configuration or platform/clock/CPU/IO/ledger/process/endpoint/replay/crash/restart probes.'),
        provenance=d['producer'],publication=d['publication'])


def main():
    d=rd(SUBJECT);validate(d);verify_blobs(d['input_pins'])
    review=build_review();assert review==rd(PREP)
    prior=rd(PRIOR_SEAL);preserved={**prior['preserved_published829'],**prior['artifacts'],PRIOR_SEAL:sha(PRIOR_SEAL)};assert len(preserved)==834
    seal=rd(SEAL);assert seal['schema']=='d5.i269-integrity.v1' and seal['base_commit']==BASE
    assert seal['preserved_published834']==preserved and set(seal['artifacts'])==FILES-{SEAL}
    for mapping in [preserved,seal['artifacts']]:
        for path,digest in mapping.items():assert sha(path)==digest,path
    assert seal['source_only'] is True and seal['current_effect']==d['current_effect']
    changed=set(git('diff',BASE,'--name-only').splitlines())|set(git('ls-files','--others','--exclude-standard').splitlines());assert changed==FILES,changed
    subprocess.check_call(['git','merge-base','--is-ancestor',BASE,'HEAD'],cwd=ROOT)
    if git('rev-parse','HEAD')!=BASE:assert not git('status','--porcelain')
    print(json.dumps(dict(status=STATUS,**review['counts'],D5_closed=False),sort_keys=True))


if __name__=='__main__':main()
