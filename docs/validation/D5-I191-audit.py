#!/usr/bin/env python3
"""I191 documentary custody schemas/order/projection checks only; no target, signatures, image build or protocol execution."""
import copy
import hashlib
import io
import json
import runpy
import subprocess
from pathlib import Path

ROOT=Path(__file__).resolve().parents[2];P='docs/validation/'
BASE='3c301856df0e0b4af73fb97350618ead35062610'
PACK=P+'D5-I191-CALLER-IMAGE-CUSTODY-SCHEMAS-CANDIDATE.json'
SPEC=P+'D5-I191-CALLER-IMAGE-CUSTODY-CONTRACT-CANDIDATE.json'
PREP=P+'D5-I191-preparation-review.json';AUDIT=P+'D5-I191-audit.py';SEAL=P+'D5-I191-integrity.json'
DOC='docs/design/D5-I191-CALLER-IMAGE-CUSTODY-CONTRACT-CANDIDATE.md'
FILES={PACK,SPEC,PREP,AUDIT,SEAL,DOC};PRIOR_SEAL=P+'D5-I190-integrity.json'


def rd(p):return json.loads((ROOT/p).read_text())
def sha(p):return hashlib.sha256((ROOT/p).read_bytes()).hexdigest()
def git(*args):return subprocess.check_output(['git',*args],cwd=ROOT,text=True).strip()
def canonical(v):return json.dumps(v,ensure_ascii=False,sort_keys=True,separators=(',',':'),allow_nan=False).encode('ascii')
def pair(a,b):return tuple(sorted((a,b)))


def evidence_order(spec):
    nodes={**{k:list(v) for k,v in spec['record_order'].items()},**{k:[] for k in spec['external_prior_nodes']}}
    pending={k:set(v) for k,v in nodes.items()};order=[]
    assert all(v<=set(nodes) for v in pending.values())
    while pending:
        ready=sorted(k for k,v in pending.items() if not v);assert ready,'Custody evidence cycle'
        order+=ready
        for k in ready:del pending[k]
        for v in pending.values():v.difference_update(ready)
    def ancestors(n):
        out=set();todo=list(nodes[n])
        while todo:
            x=todo.pop()
            if x not in out:out.add(x);todo.extend(nodes[x])
        return out
    for n in ['ACTOR_REGISTRY','IMAGE_MANIFEST','CALLER_IDENTITY','PLATFORM_CUSTODY','C_CONTEXT']:
        assert not ancestors(n)&{'ACCEPTANCE','BUNDLE','Q_REQUEST','FINAL_ROOT','LAUNCH_RECEIPT','ATOMIC_CLAIM'}
    assert {'FINAL_ROOT','Q_REQUEST','EXTERNAL_CURRENT_MAPPING'}<=ancestors('ATOMIC_CLAIM')
    assert {'BUNDLE','FINAL_ROOT','ATOMIC_CLAIM'}<=ancestors('LAUNCH_RECEIPT')
    return order


def placeholder(s,defs):
    if '$ref' in s:return placeholder(defs[s['$ref'][8:]],defs)
    if 'const' in s:return copy.deepcopy(s['const'])
    if 'enum' in s:return copy.deepcopy(s['enum'][0])
    for k in ['anyOf','oneOf']:
        if k in s:return placeholder(s[k][0],defs)
    if s['type']=='object':return {k:placeholder(v,defs) for k,v in s['properties'].items()}
    if s['type']=='array':return [placeholder(s['items'],defs) for _ in range(s['minItems'])]
    if s['type']=='integer':return s['minimum']
    if s['type']=='string':return '0'*s['minLength']
    raise AssertionError(s)


def build_review():
    spec=rd(SPEC);pins=spec['input_pins'];assert len(pins)==750
    req=''.join(BASE+':'+p+'\n' for p in sorted(pins)).encode()
    stream=io.BytesIO(subprocess.check_output(['git','cat-file','--batch'],cwd=ROOT,input=req))
    for p,h in sorted(pins.items()):
        header=stream.readline().decode().split();assert len(header)==3 and header[1]=='blob',p
        body=stream.read(int(header[2]));assert stream.read(1)==b'\n'
        assert hashlib.sha256(body).hexdigest()==h==sha(p),p
    previous=runpy.run_path(str(ROOT/(P+'D5-I190-audit.py')));r=previous['reconstruct']()
    assert rd(previous['RECON'])==r and rd(previous['REVIEW'])==previous['build_review'](r)
    prior=rd(PRIOR_SEAL);preserved={**prior['preserved_published437'],**prior['artifacts'],PRIOR_SEAL:sha(PRIOR_SEAL)}
    assert len(preserved)==442
    for p,h in preserved.items():assert sha(p)==h,p
    for binding in [spec['schema_pack'],*spec['bindings'].values()]:assert sha(binding['path'])==binding['sha256']
    pack=rd(PACK);defs=pack['$defs'];profile=rd(spec['bindings']['profile02']['path'])
    proto=rd(spec['bindings']['protocol_schemas02']['path'])['$defs'];top=spec['record_families']
    assert len(defs)==24 and len(top)==8 and len(set(top))==8
    assert pack['oneOf']==[{'$ref':'#/$defs/'+n} for n in top]
    assert [x['id'] for x in spec['rules']]==['K%02d'%i for i in range(1,17)]
    m=runpy.run_path(str(ROOT/(P+'D5-I183-audit.py')));m['schema_shape'](pack,defs)
    families=[];negative_count=0
    for n in top:
        s=defs[n];w=placeholder(s,defs)
        m['domain'](w);m['validate'](s,w,defs)
        assert sum(m['accepts'](defs[q],w,defs) for q in top)==1
        assert m['strict_body'](canonical(w))==w
        width=len(canonical(w));assert width<=spec['record_caps_bytes'][n],(n,width)
        for k in s['required']:
            bad=copy.deepcopy(w);del bad[k];m['rejected'](lambda:m['validate'](s,bad,defs));negative_count+=1
        bad=copy.deepcopy(w);bad['unknown_field']=True;m['rejected'](lambda:m['validate'](s,bad,defs));negative_count+=1
        families.append(dict(family=n,required_fields=len(s['required']),placeholder_serialized_bytes=width,
            effective_cap_bytes=spec['record_caps_bytes'][n],closed=True))
    assert spec['record_caps_bytes']['anchor_registry']==65536
    assert spec['record_caps_bytes']['custody_bundle']==262144 and spec['record_caps_bytes']['launch_receipt']==8192
    order=evidence_order(spec)
    # Definitions reuse exactly candidate02 identity/source/profile types; no wire schema changes.
    for n in ['sha256','signature','identity','validity','trusted_key','source_bindings','verifier_profile','proposal_scope']:assert defs[n]==proto[n]
    projection_fields=['roles','documentary_preparers','source_author_id','runtime_requester_id','issuer','acceptor','profile','proposal_scope',
        'accepted_source_basis_sha256','accepted_resource_index_sha256','resource_scope_sha256','suite_scope_sha256','configuration_epoch','validity']
    for n in projection_fields:assert defs['acceptance_record']['properties'][n]==proto['trust_context']['properties'][n],n
    assert 'trust_context_sha256' in defs['acceptance_record']['required']
    assert defs['acceptance_record']['properties']['decision']['const']=='IDENTITY_IMAGE_CUSTODY_ONLY_NOT_RESOURCE_OR_CAPTURE_ADMISSION'
    assert defs['caller_identity']['properties']['permission']['const']=='BOOTSTRAP_CUSTODY_ONLY_FULL_ROOT_AND_SEPARATE_REQUEST_REQUIRED'
    assert defs['launch_receipt']['properties']['role']['const']=='CALLER_PRIVATE_RECEIPT_NOT_NEW_FRAME_OR_AUTHORITY'
    roles=proto['trust_context']['properties']['roles']['properties'];assert len(roles)==8
    source_paths=set(proto['source_bindings']['properties'])
    assert len(source_paths)==6 and set(defs['image_manifest']['properties']['source_to_image']['properties'])==source_paths
    assert defs['image_manifest']['properties']['entry_mode']=={'const':'TRUSTED_IMAGE_MODULE_ENTRY'}
    assert len(defs['platform_custody']['properties']['guarantees']['properties'])==8
    inherited={pair(r['role'],r['excluded_subject']) for r in spec['inheritance']['S01_actor_exclusions']}
    expected={pair(r['role'],r['excluded_subject']) for r in profile['bootstrap']['inherited_S01_actor_exclusions']}
    assert inherited==expected and len(inherited)==8
    assert spec['inheritance']['extra_custody_separation']==['R08_ACCEPTANCE != R01_RUNTIME','R08_ACCEPTANCE != R02_PLATFORM','R08_key != R01_key','R08_key != R02_key']
    # Static identity predicates, not real people/keys or an identity resolver.
    actors={'R01':'R01','R02':'R02','R08':'R08'}
    def extra_reject(a,keys):return a['R08'] in {a['R01'],a['R02']} or keys['R08'] in {keys['R01'],keys['R02']}
    assert not extra_reject(actors,actors)
    assert not extra_reject({**actors,'R02':'R01'},{**actors,'R02':'R01'})
    for r in ['R01','R02']:
        assert extra_reject({**actors,'R08':r},actors)
        assert extra_reject(actors,{**actors,'R08':r})
    domains=spec['custody_approval_domains'];assert set(domains)=={'R01_RUNTIME','R02_PLATFORM','R08_ACCEPTANCE'}
    assert len(set(domains.values()))==3
    assert set(defs['custody_bundle']['properties']['approvals']['properties'])==set(domains)
    assert set(defs['custody_signed_core']['properties'])=={'protocol','authority_registry_epoch','anchor_registry_sha256','records','record_hashes','decision','custody_schema_pack_sha256','custody_contract_sha256'}
    assert set(defs['custody_signed_core']['properties']['records']['properties'])==set(defs['custody_signed_core']['properties']['record_hashes']['properties'])==set(top[1:6])
    assert not {'signature','bundle_sha256','launch_receipt','runtime_request','final_root'}&set(defs['custody_signed_core']['properties'])
    required_phrases={
        'K01':['outside bundle/C/repository','self-signed','cannot bootstrap trust'],
        'K02':['accountable human','separate service/process principal','same canonical human'],
        'K03':['No prep record pins C','Every referenced proof body must really exist'],
        'K05':['not a redefinition/substitute','cannot embed its own future'],
        'K06':['accepted as antecedents before C','unissued future bundle'],
        'K07':['If a platform needs additional transport/attestation','reject unchanged route'],
        'K09':['exactly one current custody mapping','Do not add bundle hash'],
        'K13':['instantaneous discovery','missing freshness assurance rejects'],
        'K14':['global atomic one-use namespace','across all approved callers/domains and restarts'],
        'K15':['not new repository Input Reader members','not permission to move required launch work outside t0']}
    rule={r['id']:r['rule'] for r in spec['rules']}
    # Individual key spellings are checked above; ensure the contract carries the material safety/acceptance constraints.
    for k,phrases in required_phrases.items():
        assert all(p in rule[k] for p in phrases),(k,phrases)
    assert spec['inheritance']['existing_full_CP07_conditions']==profile['final_CP07_conditions']
    assert spec['decision']==profile['decision'] and spec['E06']==profile['E06']
    for k in ['real_actor_or_caller_enrolled','actual_custody_bundle_or_anchor_created','actual_image_or_attestation_supplied',
              'actual_trust_or_source_image_mapping_verified','adopted','implemented','S01_accepted','F179_01_resolved','independent_acceptance',
              'product_or_components_executed','active_schema_changed','quotas_changed','rebind_applied','proposal_enabled','D5_closed']:assert spec['current_effect'][k] is False
    for s in profile['scope']['future_slots']:assert not (ROOT/s['path']).exists()
    assert not (ROOT/'testing/prospective_capture_joint_prp181').exists()
    assert set(spec['work_unit']['rollback_files'])==FILES
    return dict(schema='d5.i191-preparation-review.v1',increment='I191',date='2026-11-16',base_commit=BASE,
        status='CALLER_IMAGE_CUSTODY_CONTRACT_PREPARED_NOT_ADOPTED_NOT_IMPLEMENTED_NOT_ADMITTED',
        contract=dict(path=SPEC,sha256=sha(SPEC)),schemas=dict(path=PACK,sha256=sha(PACK)),
        input_pins=750,prior_published_files_preserved=len(preserved),definitions=24,record_families=families,
        mandatory_missing_or_unknown_key_cases=negative_count,scope='Ephemeral structural placeholders only; no positive custody/enrollment/identity/image record, signature, actual actor or service created. Schema/cap conformance is not proof of complete evidence or real record/resource fit.',
        evidence_order=order,evidence_order_acyclic=True,antecedent_records_exclude_C_acceptance_bundle_root_receipt_cycles=True,
        C_projection_fields_with_identical_types=projection_fields,unchanged_C_Q_I_A_L_and_output_bytes=True,
        S01_exclusions_preserved=8,extra_custody_exclusions_checked=4,R01_R02_overlap_permitted_if_genuine=True,
        three_approval_domains_distinct=True,actual_signatures_or_independence_verified=False,
        actual_source_image_alias_mapping_custody_ledger_clock_or_resources_verified=False,
        provenance=dict(preparer='Same Codex assistant/chat; not a real custody authority or independent acceptor',actor_independent=False,organizationally_independent=False,independent_acceptance=False),
        current_effect=spec['current_effect'],decision=spec['decision'],E06=spec['E06'],remaining_work=spec['remaining_work'],work_unit=spec['work_unit'])


def main():
    review=build_review();assert rd(PREP)==review
    prior=rd(PRIOR_SEAL);preserved={**prior['preserved_published437'],**prior['artifacts'],PRIOR_SEAL:sha(PRIOR_SEAL)}
    seal=rd(SEAL);assert seal['schema']=='d5.i191-integrity.v1' and seal['base_commit']==BASE
    assert seal['preserved_published442']==preserved and set(seal['artifacts'])==FILES-{SEAL}
    for p,h in seal['artifacts'].items():assert sha(p)==h,p
    assert seal['source_only'] and seal['resource_obligations_closed']==0 and seal['IR03']=='NOT_READY'
    for k in ['independent_acceptance','product_or_components_executed','quotas_changed','rebind_applied','proposal_enabled','D5_closed']:assert seal[k] is False
    changed=set(git('diff',BASE,'--name-only').splitlines())|set(git('ls-files','--others','--exclude-standard').splitlines());assert changed==FILES,changed
    subprocess.check_call(['git','merge-base','--is-ancestor',BASE,'HEAD'],cwd=ROOT)
    if git('rev-parse','HEAD')!=BASE:assert not git('status','--porcelain')
    print(json.dumps(dict(status='PASS_STATIC_SOURCE_ONLY',increment='I191',record_families=8,definitions=24,historical_pins=750,
        prior_published_files_preserved=442,new_files=6,S01_exclusions_preserved=8,adopted=False,implemented=False,
        actual_caller_or_image_supplied=False,product_or_components_executed=0,quotas_changed=False,rebind_applied=False,
        resource_obligations_closed=0,proposal_enabled=False,F179_01_resolved=False,D5_closed=False,IR03='NOT_READY',git_head=git('rev-parse','HEAD')),sort_keys=True))

if __name__=='__main__':main()
