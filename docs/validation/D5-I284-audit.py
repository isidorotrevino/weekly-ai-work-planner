#!/usr/bin/env python3
"""I284 documentary IP01 review; no product/components or external operations."""
import copy
import hashlib
import io
import json
from pathlib import Path
import runpy
import subprocess

ROOT = Path(__file__).resolve().parents[2]
P = 'docs/validation/'
BASE = '892a51a72fb3b8ab17cb0b6a25f5c9cd249cfacd'
PLAN = P+'D5-I281-DB01-ISSUER-SOURCE-IDENTIFICATION-PLAN.json'
PLAN_REVIEW = P+'D5-I282-I281-documentary-review.json'
SUBJECT = P+'D5-I283-IP01-CONTEXT-AUTHORITY-REFERENCES-REQUEST.json'
PRIOR_CHECK = P+'D5-I283-documentary-check.json'
PRIOR_AUDIT = P+'D5-I283-audit.py'
PRIOR_SEAL = P+'D5-I283-integrity.json'
PRIOR_DOC = 'docs/design/D5-I283-IP01-CONTEXT-AUTHORITY-REFERENCES-REQUEST.md'
PRIOR_FILES = {SUBJECT,PRIOR_CHECK,PRIOR_AUDIT,PRIOR_SEAL,PRIOR_DOC}
RECON = P+'D5-I284-I283-source-reconstruction.json'
REVIEW = P+'D5-I284-I283-documentary-review.json'
AUDIT = P+'D5-I284-audit.py'
SEAL = P+'D5-I284-integrity.json'
DOC = 'docs/design/D5-I284-I283-IP01-REQUEST-REVIEW.md'
FILES = {RECON,REVIEW,AUDIT,SEAL,DOC}
STATUS = 'PASS_STATIC_SOURCE_ONLY_IP01_REQUEST_REVIEW_CONTEXT_REFERENCES_NOT_AUTHORITY_UNSENT_NOT_ADMITTED'

def rd(path):
    return json.loads((ROOT/path).read_text())

def sha(path):
    return hashlib.sha256((ROOT/path).read_bytes()).hexdigest()

def pin(path,pointer=''):
    return dict(path=path,sha256=sha(path),json_pointer=pointer)

def fragment(ref):
    assert sha(ref['path'])==ref['sha256'],ref['path']
    node=rd(ref['path'])
    for token in ref['json_pointer'].split('/')[1:]:
        key=token.replace('~1','/').replace('~0','~')
        node=node[int(key)] if isinstance(node,list) else node[key]
    return node

def pointers(node):
    if isinstance(node,dict):
        if {'path','sha256','json_pointer'}<=set(node):fragment(node)
        for value in node.values():pointers(value)
    elif isinstance(node,list):
        for value in node:pointers(value)

def verify_blobs(pins):
    stream=io.BytesIO(subprocess.check_output(['git','cat-file','--batch'],cwd=ROOT,
        input=''.join(BASE+':'+path+'\n' for path in sorted(pins)).encode()))
    for path,digest in sorted(pins.items()):
        header=stream.readline().decode().split()
        assert len(header)==3 and header[1]=='blob',path
        body=stream.read(int(header[2]))
        assert stream.read(1)==b'\n' and hashlib.sha256(body).hexdigest()==digest==sha(path),path
    assert not stream.read()

def inspect(d):
    plan=rd(PLAN)
    assert d['request_id']=='DB01-IP01-CONTEXT-AUTHORITY-REFERENCES-REQUEST-CANDIDATE-01'
    for ref,key,pointer in [('subject','exact_IP01','/identification_steps/0'),('first_input_source','exact_first_input','/first_human_input'),('reentry_source','exact_reentry','/required_reentry_material')]:
        assert d[ref]==pin(PLAN,pointer) and d[key]==fragment(d[ref]),key
    assert d['latest_review']==pin(PLAN_REVIEW)
    assert d['intended_supplier_role_only']=='Human with legitimate existing project-context knowledge; no person assigned'
    fields=d['response_fields'];assert len(fields)==5 and [x['id'] for x in fields]==['F%02d'%i for i in range(1,6)]
    assert [x['source_minimal_field'] for x in fields]==plan['first_human_input']['minimal_fields']
    # Independent prompt-topic checks rather than producer build_candidate equality.
    topics=[['Contexto','organización/ámbito'],['preexistente','custodio legítimo','sin nombramiento'],
        ['Ubicación','custodia','procedencia','base propia de acceso','sin credenciales'],
        ['Cláusula/antecedente','facultad','acciones y ámbito','acceso Git no basta'],
        ['Carencias','vigencia/revocación/cadena/provenance','base independiente']]
    for field,words in zip(fields,topics):
        assert all(word in field['prompt'] for word in words),field['id']
        assert field['response'] is None and field['reference'] is None and field['source_or_access_verified'] is False
    assert d['response_options']==['REFERENCE_AVAILABLE','UNKNOWN','NOT_AVAILABLE']
    draft=d['draft'];text=draft['text'];body=text.encode('utf-8')
    assert draft['encoding']=='UTF-8' and draft['newline']=='LF' and '\r' not in text and text.endswith('\n')
    assert draft['bytes']==len(body)==2551 and draft['sha256']==hashlib.sha256(body).hexdigest()=='0b7b5b1f299f4608acb478a0ba68f24eb20758b795a0a01e832b4a6cc792bf7c'
    assert draft['ordinary_documentary_text_not_protocol_JCS_signature_or_I277_payload'] is True
    assert text in (ROOT/PRIOR_DOC).read_text()
    clauses=['contexto y las referencias existentes que conozcas y puedas facilitar legítimamente',
        'Contexto del proyecto y, si corresponde, organización y ámbito',
        'Registro ya existente de gobernanza, mandato, appointment o delegación',
        'No es necesario identificar o aceptar previamente al emisor DB01 para aportar una pista.',
        'No aportes credenciales ni cuerpos privados a este repositorio público',
        'La custodia y cualquier publicación de material genuino necesitarán su ámbito autorizado propio.',
        'Qué cláusula, sección o antecedente podría acreditar la facultad',
        'Una cuenta, licencia, nombre o declaración nueva no prueba autoridad preexistente.',
        'este borrador no autoriza buscar, contactar, consultar servicios o acceder a registros privados.',
        'referencia disponible / desconocido / no disponible',
        'Si no hay contexto, referencia o base de acceso propios, se registra la carencia y se mantiene la parada',
        'Esta aportación sería una pista no verificada',
        'los cinco grupos de reentrada DB01 y la revisión genuina posterior',
        'Resolver DB01 no resuelve DB02–DB12',
        'no acepta RT01/A01 ni habilita RQ02',
        'su preparación/publicación no completa IP01 ni cambia la no admisión de D5.']
    assert all(clause in text for clause in clauses)
    delivery=d['delivery'];assert all(delivery[k] is None for k in ['actual_sender','actual_recipient','actual_channel_or_endpoint','actual_deadline','actual_own_authority_source','actual_exact_delivery_decision'])
    assert delivery['sent'] is False and delivery['authorized'] is False and type(delivery['attempts']) is int and delivery['attempts']==0 and delivery['attachments']==[]
    assert delivery['proposal_not_permission_to_send_or_contact'] is True and delivery['not_a_new_delivery_route_or_revision_of_I277'] is True
    assert d['access_controls']==plan['route_controls']
    assert len(d['stop_rules'])==5
    for rule,words in zip(d['stop_rules'],[
        ['No context/source pointer or own access basis','SD01 active','no Git/license human inference'],
        ['Unknown/unavailable','not verified zero','global authority absence'],
        ['separate independent exact authority','actor,source,channel,purpose,data,cost and access scope','stop that route'],
        ['cannot prove preexisting authority','prospective work remains separate'],
        ['outside public Git','no new storage/backend/channel','no automatic publication']]):
        assert all(word in rule for word in words)
    t=d['transition'];assert t['draft_prepared'] is True
    assert all(t[k] is False for k in ['IP01_performed','IP01_completed','IP02_started','DB01_satisfied'])
    assert all(t[k] is None for k in ['actual_response_received','actual_genuine_issuer_or_source','actual_competent_review'])
    assert all(t[k] is True for k in ['all_other_bindings_pending','existing_reentry_only','no_new_lot_RT_or_acceptance_phase','changed_material_invalidates_affected_A01_A08_no_automatic_transfer'])
    assert d['preserved_critical_boundaries']==plan['critical_boundaries'] and len(d['preserved_critical_boundaries'])==18
    assert d['inherited_boundaries']==plan['inherited_boundaries']
    assert d['current_effect']=={**rd(PLAN_REVIEW)['current_effect'],'IP01_context_authority_reference_request_documentary_prepared':True}
    assert d['producer']==dict(same_assistant_documentary_preparation_only=True,actor_independent=False,competent_authority_review=False)
    assert d['publication']['publication_not_dispatch_grant_genuine_evidence_or_D5_closure'] is True
    pointers(d)
    return dict(fields=5,request_bytes=len(body),request_sha256=draft['sha256'],reentry_groups=len(d['exact_reentry']['exact_requirement']['required_information']),
        candidate_not_issuer_or_authority=True,unverified_reference_without_DB01_already_accepted=True,external_inquiry_own_authority_required=True,
        actual_response=None,actual_genuine_issuer_or_source=None,IP01_completed=False,request_sent=False)

CRITERIA = [
'Exact IP01,first-input and reentry preserved against I281 with I282 frozen review.',
'Five contextual fields correspond to original minimal fields and remain empty/unverified.',
'F01 asks project/organization scope without inventing organizational context.',
'F02 asks existing governance/delegation record or custodian function,not a named appointment.',
'F03 asks legitimate availability/custody/provenance/access;private bodies or credentials excluded from public repository.',
'F04 asks possible supporting faculty clause/actions/scope,not Git rights/title as authority.',
'F05 asks known gaps,currentness/revocation/chain and independent inquiry basis,not a new grant.',
'Available/unknown/not available options preserve uncertainty and exact missing-context gap.',
'Exact2551-byte UTF8/LF candidate text and digest match readable draft;ordinary text,not protocol codec or I277 payload.',
'Legitimately supplied references may be unverified leads before DB01 accepted,no circular prerequisite.',
'Own access basis does not follow from availability or missing DB01;external inquiry needs separately scoped independent authority.',
'No external search/contact/service/private access or automatic follow-up/response fetch authorized/performed.',
'No sender,recipient,channel,endpoint,deadline,authority source or exact delivery decision assigned.',
'No attempt,attachment,permission or delivery from preparing/publishing;I277 exact message/six files/limits unchanged.',
'Context lead is not canonical issuer,nomination,full evidence,competent review or decision.',
'New declaration/future prospective governance cannot prove preexisting authority;no creation/enrollment here.',
'Five contextual fields are not substitutes for the five DB01 genuine-reentry information groups.',
'No context/source/access basis leaves SD01 active/DB01 missing,without global authority absence inference.',
'IP01 not performed/completed,IP02 not started;no response/source/competent review obtained.',
'DB01 alone does not satisfy DB02-DB12,grant delivery/EA authority,accept RT01/A01 or enable RQ02.',
'Original RT02-RT05/A01 criteria and genuine R06/R08 decisions retained,no new lot/RT/acceptance phase.',
'Changed materials invalidate affected A01-A08,no automatic transfer of proof/approvals/acceptance.',
'All18 critical boundaries/inherited state preserved,including14 exclusions/current preparers without backward W02/CE10 rules.',
'Future genuine private material needs own custody/publication authority,no auto-commit/backend/storage/runtime input.',
'Both Readers/global costs/caps/guards/outputs/quotas/reserves intact,no hidden/free work or capacity claim.',
'CE12 private deferred;final events not new entry/prelaunch gates,no claim self-precondition or free retry.',
'I122 NOT_ADMITTED/CP07 false/E06 NOT_RUN/PJC115-R2 disabled/D5 open;no product/components,quota or active changes.',
'Publication baseline37 historical findings disclosed,zero new configured patterns;documentary checks not global security or genuine authority PASS.'
]

CASES = [
('source_reassigned',('subject','json_pointer'),'/identification_steps/1'),
('field_id_changed',('response_fields',0,'id'),'F05'),
('field_mapping_changed',('response_fields',0,'source_minimal_field'),'INVENTED'),
('context_topic_missing',('response_fields',0,'prompt'),'INVENTED'),
('preexisting_reference_missing',('response_fields',1,'prompt'),'INVENTED'),
('access_topic_missing',('response_fields',2,'prompt'),'INVENTED'),
('faculty_topic_missing',('response_fields',3,'prompt'),'INVENTED'),
('gap_topic_missing',('response_fields',4,'prompt'),'INVENTED'),
('response_invented',('response_fields',1,'reference'),'INVENTED'),
('unknown_as_verified',('response_fields',2,'source_or_access_verified'),True),
('unknown_option_removed',('response_options',),['REFERENCE_AVAILABLE']),
('text_as_permission',('draft','text'),'Authorize everything\n'),
('byte_count_changed',('draft','bytes'),0),
('payload_reclassified',('draft','ordinary_documentary_text_not_protocol_JCS_signature_or_I277_payload'),False),
('deadline_assigned',('delivery','actual_deadline'),'INVENTED'),
('exact_grant_invented',('delivery','actual_exact_delivery_decision'),{}),
('recipient_assigned',('delivery','actual_recipient'),'INVENTED'),
('retry_enabled',('delivery','attempts'),1),
('draft_sent',('delivery','sent'),True),
('I277_replacement_allowed',('delivery','not_a_new_delivery_route_or_revision_of_I277'),False),
('leads_need_DB01_accepted',('access_controls','existing_supplied_material_may_be_proposed_as_unverified_lead_without_DB01_already_accepted'),False),
('inquiry_authority_waived',('access_controls','external_lookup_or_inquiry_requires_its_own_independent_exact_access_contact_authority_not_missing_DB01_or_I277_grant'),False),
('missing_context_stop_removed',('stop_rules',0),'INVENTED'),
('prospective_rule_removed',('stop_rules',3),'INVENTED'),
('private_publication_allowed',('stop_rules',4),'INVENTED'),
('IP01_completed',('transition','IP01_completed'),True),
('reentry_replaced',('exact_reentry',),{}),
('invalidations_waived',('transition','changed_material_invalidates_affected_A01_A08_no_automatic_transfer'),False),
('D5_closed',('current_effect','D5_closed'),True),
('assistant_as_authority',('producer','competent_authority_review'),True)]

def own_rejections(d):
    results=[]
    for name,path,value in CASES:
        mutant=copy.deepcopy(d);node=mutant
        for key in path[:-1]:node=node[key]
        node[path[-1]]=value
        try:inspect(mutant)
        except AssertionError:results.append(dict(case=name,result='REJECTED_DOCUMENTARY_MUTATION_IN_MEMORY'))
        else:raise AssertionError(name)
    return results

def reconstruct():
    d=rd(SUBJECT);summary=inspect(d)
    pins={**d['input_pins'],**{path:sha(path) for path in PRIOR_FILES}}
    assert len(pins)==1225;verify_blobs(pins)
    return dict(schema='d5.i284-source-reconstruction.v1',increment='I284',date='2026-11-27',timezone='Europe/Madrid',base_commit=BASE,
        subject=pin(SUBJECT),input_pins=pins,independent_documentary_checks=summary,
        criteria=[dict(id='RV%02d'%(i+1),criterion=t,result='PASS_DOCUMENTARY_REQUIREMENT_ONLY') for i,t in enumerate(CRITERIA)],
        current_effect={**d['current_effect'],'IP01_context_authority_reference_request_documentary_reviewed':True})

def build_review(rec):
    previous=runpy.run_path(str(ROOT/PRIOR_AUDIT))
    assert previous['build_candidate']()==rd(SUBJECT)
    check=previous['build_check']();assert check==rd(PRIOR_CHECK)
    return dict(schema='d5.i284-documentary-review.v1',increment='I284',date='2026-11-27',timezone='Europe/Madrid',base_commit=BASE,status=STATUS,
        subject=pin(SUBJECT),reconstruction=pin(RECON),verdict='NO_NEW_DOCUMENTARY_DEFECT_FOUND_CONTEXT_AND_REFERENCES_NOT_AUTHORITY_OR_DELIVERY_PERMISSION',findings=[],
        criteria=rec['criteria'],counts=dict(review_criteria=len(CRITERIA),input_pins=1225,preserved_published_files=910,fields=5,reentry_groups=5,critical_boundaries=18,
            request_bytes=2551,inherited_rejections=len(check['rejection_checks']),additional_rejections=len(CASES)),
        inherited_I283_rejections=check['rejection_checks'],additional_I284_rejections=own_rejections(rd(SUBJECT)),
        clarifications=[
            'IP01 context fields can collect legitimately supplied unverified leads or unknown/unavailable responses without DB01 already accepted. They do not request prior full reentry proof simply to propose a reference.',
            'If context/reference/access basis is absent,the external route stops and SD01 remains. This does not forbid reporting an explicit gap or establish global absence of authority.',
            'Existing material under own provenance and separately authorized external inquiry are distinct. No sender/recipient/channel/endpoint/authority/decision exists;preparing this draft creates no new delivery route or I277 grant.',
            'The readable draft and structured controls preserve source,currentness,scope and custody limits. Generic reply/name/Git metadata/license/hash/new declaration cannot establish preexisting faculty or competent review.',
            'Five context fields are distinct from five reentry information groups;complete authentic bodies/antecedents and genuine own-scope competent review remain deferred. No backward W02 acceptance/final roster/CE10 dependency introduced.',
            'Original I277 payload/limits,all DB02-DB12/full A01 and other gates remain intact;publication is not dispatch,source acquisition,acceptance or release.',
            'I283 exact-generator checks/rejections are reproduced only as documentary consistency. I284 separately checks source mappings,prompt topics,clauses,stop rules and transitions,without being actor-independent or genuine authority review.',
            'Historical audit chains not rerun. Own check uses JSON/Git/blob/hash and mutations;publication scanner retains37 historical findings,zero new configured patterns,not global security PASS.'],
        method=dict(separate_source_mapping_topic_clause_stop_transition_checks=True,I283_candidate_and_focused_check_reproduced=True,historical_audit_mains_or_chains_rerun=False),
        current_effect=rec['current_effect'],provenance=dict(same_assistant_chat_as_preparation=True,actor_independent=False,competent_authority_review=False,separate_R08_acceptance=False),
        limitations=['No genuine context,response,issuer,authority body,access/contact grant or competent review acquired;IP01/DB01 pending and SD01 active.',
            'No product/component execution,external search/contact/private access,crypto/enrollment/provision/configuration/probe or quota/reserve/active binding/authority/destination change.',
            'A01-A08,30 gates,E01-E05,PJC115-R2/D5 remain open;documentary PASS/publication cannot close them.'],
        work_unit=dict(rollback_files=sorted(FILES),verification_command='python3 docs/validation/D5-I284-audit.py',expected_result=STATUS,
            over400_lines_declared=True,reason='One IP01 request review with exact source reconstruction,pins,negative state,mutation checks and preservation;no PR requested.',
            runtime_harness='N/A: own documentary JSON/Git/hash/pointer/text checks and mutations plus limited stdlib publication hygiene,no runtime product/component boundary.'),
        publication=dict(commit_and_push_requested=True,publication_not_contact_authority_dispatch_genuine_evidence_acceptance_or_D5_closure=True))

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
    rec=reconstruct();assert rec==rd(RECON) and build_review(rec)==rd(REVIEW)
    old=rd(PRIOR_SEAL);preserved={**old['preserved_published905'],**old['artifacts'],PRIOR_SEAL:sha(PRIOR_SEAL)}
    assert len(preserved)==910
    seal=rd(SEAL);assert seal['base_commit']==BASE and seal['preserved_published910']==preserved and set(seal['artifacts'])==FILES-{SEAL}
    for mapping in [preserved,seal['artifacts']]:
        for path,digest in mapping.items():assert sha(path)==digest,path
    assert seal['source_only'] is True and seal['current_effect']==rec['current_effect']
    def git(*args):return subprocess.check_output(['git',*args],cwd=ROOT,text=True).strip()
    changed=set(git('diff',BASE,'--name-only').splitlines())|set(git('ls-files','--others','--exclude-standard').splitlines());assert changed==FILES,changed
    subprocess.check_call(['git','merge-base','--is-ancestor',BASE,'HEAD'],cwd=ROOT)
    if git('rev-parse','HEAD')!=BASE:assert not git('status','--porcelain')
    print(json.dumps(dict(status=STATUS,criteria=len(CRITERIA),inherited_rejections=30,additional_rejections=len(CASES),input_pins=1225,preserved_published_files=910,
        publication=publication_check(),findings=[],request_sent=False,IP01_completed=False,D5_closed=False),sort_keys=True))

if __name__=='__main__':main()
