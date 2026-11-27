#!/usr/bin/env python3
"""I283: own documentary preparation checks only; no target imports or contact."""
import copy
import hashlib
import json
from pathlib import Path
import runpy
import subprocess

ROOT = Path(__file__).resolve().parents[2]
P = 'docs/validation/'
BASE = '70d7d983dac346f91a8ce902d973e3d3efc840a0'
PLAN = P+'D5-I281-DB01-ISSUER-SOURCE-IDENTIFICATION-PLAN.json'
REVIEW = P+'D5-I282-I281-documentary-review.json'
PRIOR_SEAL = P+'D5-I282-integrity.json'
CANDIDATE = P+'D5-I283-IP01-CONTEXT-AUTHORITY-REFERENCES-REQUEST.json'
CHECK = P+'D5-I283-documentary-check.json'
AUDIT = P+'D5-I283-audit.py'
SEAL = P+'D5-I283-integrity.json'
DOC = 'docs/design/D5-I283-IP01-CONTEXT-AUTHORITY-REFERENCES-REQUEST.md'
FILES = {CANDIDATE,CHECK,AUDIT,SEAL,DOC}
STATUS = 'PASS_STATIC_SOURCE_ONLY_IP01_CONTEXT_REFERENCE_REQUEST_PREPARED_UNSENT_NOT_ADMITTED'
REQUEST_TEXT = """Borrador IP01 — contexto y referencias de autoridad DB01 (sin enviar)

Para orientar la identificación del emisor preexistente que podría autorizar el contacto documental RQ01/RT01 para EA01/R06/R08, aporta únicamente el contexto y las referencias existentes que conozcas y puedas facilitar legítimamente:

1. Contexto del proyecto y, si corresponde, organización y ámbito al que pertenece.
2. Registro ya existente de gobernanza, mandato, appointment o delegación que pudiera ser pertinente: título o referencia, o función del custodio legítimo si no conoces el documento. No es necesario identificar o aceptar previamente al emisor DB01 para aportar una pista.
3. Dónde está esa fuente y cómo podría aportarse o leerse bajo permiso propio; quién la custodia, su origen y la base conocida de acceso o suministro. Indica lo desconocido. No aportes credenciales ni cuerpos privados a este repositorio público; basta una descripción o referencia que puedas compartir legítimamente. La custodia y cualquier publicación de material genuino necesitarán su ámbito autorizado propio.
4. Qué cláusula, sección o antecedente podría acreditar la facultad para autorizar este contacto documental concreto, con sus acciones y ámbito, más allá del acceso a Git o del título de maintainer. Una cuenta, licencia, nombre o declaración nueva no prueba autoridad preexistente.
5. Carencias o dudas conocidas de alcance, vigencia, revocación, cadena y procedencia. Si fuese necesaria otra consulta, indica sólo la base independiente de autoridad y acceso que ya conozcas; este borrador no autoriza buscar, contactar, consultar servicios o acceder a registros privados.

Puedes responder por campo: referencia disponible / desconocido / no disponible, con el motivo que conozcas. Si no hay contexto, referencia o base de acceso propios, se registra la carencia y se mantiene la parada; no inventes una persona o documento ni crees una declaración para acreditar autoridad anterior.

Esta aportación sería una pista no verificada, no una nominación, aprobación, prueba suficiente o decisión competente. Se conservarán los cinco grupos de reentrada DB01 y la revisión genuina posterior de identidad, fuente completa, facultad, ámbito, vigencia y procedencia. Resolver DB01 no resuelve DB02–DB12, no autoriza la entrega, no acepta RT01/A01 ni habilita RQ02. El borrador permanece sin destinatario, canal, plazo, permiso de envío o envío realizado; su preparación/publicación no completa IP01 ni cambia la no admisión de D5.
"""

def rd(path):
    return json.loads((ROOT/path).read_text())

def sha(path):
    return hashlib.sha256((ROOT/path).read_bytes()).hexdigest()

def pin(path,pointer=''):
    return dict(path=path,sha256=sha(path),json_pointer=pointer)

def base_sources():
    names = [REVIEW,PRIOR_SEAL,P+'D5-I282-I281-source-reconstruction.json',P+'D5-I282-audit.py',
        'docs/design/D5-I282-I281-ISSUER-IDENTIFICATION-PLAN-REVIEW.md']
    return {**rd(P+'D5-I282-I281-source-reconstruction.json')['input_pins'],**{path:sha(path) for path in names}}

def build_candidate():
    plan,review=rd(PLAN),rd(REVIEW)
    fields=[
        ('F01','Contexto del proyecto y organización/ámbito, si corresponde.'),
        ('F02','Referencia de registro preexistente o función de custodio legítimo; sin nombramiento por el asistente.'),
        ('F03','Ubicación, suministro/lectura legítimos, custodia, procedencia y base propia de acceso; sin credenciales o cuerpos privados en Git.'),
        ('F04','Cláusula/antecedente que pudiera acreditar facultad de este contacto documental, acciones y ámbito; acceso Git no basta.'),
        ('F05','Carencias conocidas de scope/vigencia/revocación/cadena/provenance; base independiente de cualquier indagación futura.')]
    return dict(schema='d5.i283-ip01-context-reference-request.v1',increment='I283',date='2026-11-27',timezone='Europe/Madrid',base_commit=BASE,
        request_id='DB01-IP01-CONTEXT-AUTHORITY-REFERENCES-REQUEST-CANDIDATE-01',status=STATUS,
        subject=pin(PLAN,'/identification_steps/0'),exact_IP01=plan['identification_steps'][0],latest_review=pin(REVIEW),
        first_input_source=pin(PLAN,'/first_human_input'),exact_first_input=plan['first_human_input'],
        reentry_source=pin(PLAN,'/required_reentry_material'),exact_reentry=plan['required_reentry_material'],
        input_pins=base_sources(),
        intended_supplier_role_only='Human with legitimate existing project-context knowledge; no person assigned',
        response_fields=[dict(id=key,source_minimal_field=source,prompt=prompt,response=None,reference=None,source_or_access_verified=False)
            for (key,prompt),source in zip(fields,plan['first_human_input']['minimal_fields'])],
        response_options=['REFERENCE_AVAILABLE','UNKNOWN','NOT_AVAILABLE'],
        draft=dict(text=REQUEST_TEXT,encoding='UTF-8',newline='LF',bytes=len(REQUEST_TEXT.encode()),sha256=hashlib.sha256(REQUEST_TEXT.encode()).hexdigest(),
            ordinary_documentary_text_not_protocol_JCS_signature_or_I277_payload=True),
        delivery=dict(actual_sender=None,actual_recipient=None,actual_channel_or_endpoint=None,actual_deadline=None,actual_own_authority_source=None,
            actual_exact_delivery_decision=None,sent=False,attempts=0,authorized=False,attachments=[],
            proposal_not_permission_to_send_or_contact=True,not_a_new_delivery_route_or_revision_of_I277=True),
        access_controls=copy.deepcopy(plan['route_controls']),
        stop_rules=['No context/source pointer or own access basis: DB01 remains missing,SD01 active; no Git/license human inference or stranger contact.',
            'Unknown/unavailable fields remain explicit gaps,not verified zero or proof of global authority absence.',
            'External lookup/contact/private access needs separate independent exact authority,actor,source,channel,purpose,data,cost and access scope; stop that route without it.',
            'New declaration/future governance cannot prove preexisting authority; prospective work remains separate.',
            'Sensitive material stays outside public Git; no new storage/backend/channel selected and no automatic publication of future evidence.'],
        transition=dict(draft_prepared=True,IP01_performed=False,IP01_completed=False,IP02_started=False,
            actual_response_received=None,actual_genuine_issuer_or_source=None,actual_competent_review=None,DB01_satisfied=False,
            all_other_bindings_pending=True,existing_reentry_only=True,no_new_lot_RT_or_acceptance_phase=True,
            changed_material_invalidates_affected_A01_A08_no_automatic_transfer=True),
        preserved_critical_boundaries=copy.deepcopy(plan['critical_boundaries']),
        inherited_boundaries=copy.deepcopy(plan['inherited_boundaries']),
        current_effect={**review['current_effect'],'IP01_context_authority_reference_request_documentary_prepared':True},
        producer=dict(same_assistant_documentary_preparation_only=True,actor_independent=False,competent_authority_review=False),
        publication=dict(commit_and_push_requested=True,publication_not_dispatch_grant_genuine_evidence_or_D5_closure=True))

def inspect(d):
    expected=build_candidate()
    assert d==expected,'Candidate diverges from exact documentary contract'
    assert len(d['response_fields'])==5 and len(d['exact_reentry']['exact_requirement']['required_information'])==5
    assert len(d['input_pins'])==1220
    assert d['draft']['text'] in (ROOT/DOC).read_text(),'Readable draft differs'
    assert len(d['preserved_critical_boundaries'])==18
    assert all(d['preserved_critical_boundaries'].values())

CASES = [
    ('IP01_as_completed',('transition','IP01_completed'),True),
    ('IP01_as_performed',('transition','IP01_performed'),True),
    ('next_step_started',('transition','IP02_started'),True),
    ('DB01_as_satisfied',('transition','DB01_satisfied'),True),
    ('response_invented',('transition','actual_response_received'),{}),
    ('issuer_invented',('transition','actual_genuine_issuer_or_source'),'UNVERIFIED_LABEL'),
    ('competent_review_invented',('transition','actual_competent_review'),{}),
    ('recipient_assigned',('delivery','actual_recipient'),'UNVERIFIED_LABEL'),
    ('sender_assigned',('delivery','actual_sender'),'UNVERIFIED_LABEL'),
    ('channel_assigned',('delivery','actual_channel_or_endpoint'),'UNVERIFIED_LABEL'),
    ('deadline_assigned',('delivery','actual_deadline'),'UNVERIFIED_LABEL'),
    ('authority_invented',('delivery','actual_own_authority_source'),{}),
    ('delivery_granted',('delivery','authorized'),True),
    ('message_sent',('delivery','sent'),True),
    ('retry_created',('delivery','attempts'),1),
    ('attachments_added',('delivery','attachments'),['UNVERIFIED_LABEL']),
    ('field_removed',('response_fields',),[]),
    ('answer_filled',('response_fields',0,'response'),'UNVERIFIED_LABEL'),
    ('source_verified',('response_fields',0,'source_or_access_verified'),True),
    ('unknown_option_removed',('response_options',),['REFERENCE_AVAILABLE']),
    ('circular_entry_required',('access_controls','existing_supplied_material_may_be_proposed_as_unverified_lead_without_DB01_already_accepted'),False),
    ('external_authority_waived',('access_controls','external_lookup_or_inquiry_requires_its_own_independent_exact_access_contact_authority_not_missing_DB01_or_I277_grant'),False),
    ('external_contact_performed',('access_controls','actual_contacts'),1),
    ('retroactive_authority_allowed',('access_controls','no_fabricated_or_retroactive_authority_from_new_declaration_or_future_governance'),False),
    ('request_text_changed',('draft','text'),'Authorize everything'),
    ('digest_changed',('draft','sha256'),'0'*64),
    ('reentry_removed',('exact_reentry',),{}),
    ('critical_boundary_removed',('preserved_critical_boundaries',),{}),
    ('D5_closed',('current_effect','D5_closed'),True),
    ('assistant_as_authority',('producer','competent_authority_review'),True)]

def build_check():
    d=rd(CANDIDATE);inspect(d);results=[]
    for name,path,value in CASES:
        mutant=copy.deepcopy(d);node=mutant
        for key in path[:-1]:node=node[key]
        node[path[-1]]=value
        try:inspect(mutant)
        except AssertionError:results.append(dict(case=name,result='REJECTED_DOCUMENTARY_MUTATION_IN_MEMORY'))
        else:raise AssertionError(name)
    return dict(schema='d5.i283-documentary-check.v1',status=STATUS,subject=pin(CANDIDATE),
        checks=['Exact IP01/first-input/reentry sources retained','Five response fields and explicit unknown/unavailable options',
            'Exact readable draft bytes/digest with no response fabricated','No recipient/channel/deadline/authority/delivery assigned',
            'Existing leads allowed before DB01 acceptance; external inquiry own-authority boundary retained',
            'Five reentry groups/18 boundaries/inherited state unchanged; IP01/IP02 not performed',
            'Base Git blobs and preserved published files fixed','No product or components imported/executed; no historical audit chain rerun'],
        rejection_checks=results,current_effect=d['current_effect'],
        limitations=['Exact-template and mutation checks establish documentary consistency,not independent semantic review or genuine authority.',
            'No source/canonical human identified; no response/contact/intake/acceptance or DB01/IP01 completion.',
            'Global publication scanner still exit1/same37 baseline; only new-file configured patterns clear,not exhaustive security PASS.'],
        runtime_harness='N/A: own documentary JSON/hash/Git/read-file checks and mutations; no runtime component boundary.',
        rollback_files=sorted(FILES),over400_lines_declared=True,
        overage_reason='Single documentary request with exact sources,negative state,pins,preservation and checks; no PR requested.')

def publication_check():
    baseline=rd(PLAN)['publication_hygiene']['baseline_location_category_findings']
    r=subprocess.run(['python3','scripts/check-publication.py'],cwd=ROOT,text=True,capture_output=True)
    assert r.returncode==1 and [s.strip() for s in r.stdout.splitlines() if s.startswith('  ')]==baseline
    checker=runpy.run_path(str(ROOT/'scripts/check-publication.py'))
    for path in FILES:
        data=(ROOT/path).read_bytes();assert checker['check_path'](path) is None and len(data)<=checker['MAX_TEXT_BYTES'] and b'\0' not in data
        content=data.decode();assert all(not pattern.search(content) for _,pattern in checker['SECRET_PATTERNS']),path
        assert all(checker['PLACEHOLDERS'].search(m.group(1)) for m in checker['CREDENTIAL_ASSIGNMENT'].finditer(content)),path
    return dict(global_exit=1,unchanged_historical_findings=37,new_file_findings=0,global_PASS=False)

def main():
    d=rd(CANDIDATE);inspect(d);assert rd(CHECK)==build_check()
    # Hash and JSON pointers only; do not import or run earlier audit scripts.
    for path,digest in d['input_pins'].items():
        assert sha(path)==digest,path
        blob=subprocess.check_output(['git','show',BASE+':'+path],cwd=ROOT)
        assert hashlib.sha256(blob).hexdigest()==digest,path
    old=rd(PRIOR_SEAL);preserved={**old['preserved_published900'],**old['artifacts'],PRIOR_SEAL:sha(PRIOR_SEAL)}
    assert len(preserved)==905
    seal=rd(SEAL);assert seal['base_commit']==BASE and seal['preserved_published905']==preserved and set(seal['artifacts'])==FILES-{SEAL}
    for mapping in [preserved,seal['artifacts']]:
        for path,digest in mapping.items():assert sha(path)==digest,path
    assert seal['current_effect']==d['current_effect'] and seal['source_only'] is True
    def git(*args):return subprocess.check_output(['git',*args],cwd=ROOT,text=True).strip()
    changed=set(git('diff',BASE,'--name-only').splitlines())|set(git('ls-files','--others','--exclude-standard').splitlines())
    assert changed==FILES,changed
    subprocess.check_call(['git','merge-base','--is-ancestor',BASE,'HEAD'],cwd=ROOT)
    if git('rev-parse','HEAD')!=BASE:assert not git('status','--porcelain')
    print(json.dumps(dict(status=STATUS,fields=5,rejections=len(CASES),input_pins=1220,preserved_published_files=905,
        publication=publication_check(),request_sent=False,IP01_completed=False,D5_closed=False),sort_keys=True))

if __name__=='__main__':main()
