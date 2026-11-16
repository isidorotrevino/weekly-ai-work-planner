#!/usr/bin/env python3
"""I185 candidate repair audit. Documentary Git/JSON/role analysis only; no target or crypto execution."""
import copy
import hashlib
import io
import json
import runpy
import subprocess
from pathlib import Path

ROOT=Path(__file__).resolve().parents[2]
P='docs/validation/'
BASE='a5c48bb713fb220d6b983176c3c1af75819d792f'
PACK=P+'D5-I185-PGO181-SCHEMAS-CANDIDATE-02.json'
PROFILE=P+'D5-I185-PGO181-TRUST-PROFILE-CANDIDATE-02.json'
PREP=P+'D5-I185-preparation-review.json'
AUDIT=P+'D5-I185-audit.py'
SEAL=P+'D5-I185-integrity.json'
DOC='docs/design/D5-I185-PGO181-SEPARATION-REPAIR-CANDIDATE.md'
FILES={PACK,PROFILE,PREP,AUDIT,SEAL,DOC}
OLD_PACK=P+'D5-I183-PGO181-SCHEMAS-CANDIDATE.json'
OLD_PROFILE=P+'D5-I183-PGO181-TRUST-PROFILE-CANDIDATE.json'
OLD_SEAL=P+'D5-I184-integrity.json'
PID='PGO181-TRUST-ED25519-JCS-CANDIDATE-02'
S01=P+'D5-I179-S01-ROLES-SCOPE-GATES.json'


def rd(p):return json.loads((ROOT/p).read_text())
def sha(p):return hashlib.sha256((ROOT/p).read_bytes()).hexdigest()
def git(*args):return subprocess.check_output(['git',*args],cwd=ROOT,text=True).strip()
def edge(a,b):return tuple(sorted((a,b)))


def changes(a,b,path=''):
    if type(a) is dict and type(b) is dict:
        out=set()
        for k in set(a)|set(b):
            q=path+'/'+k.replace('~','~0').replace('/','~1')
            out |= {q} if k not in a or k not in b else changes(a[k],b[k],q)
        return out
    return set() if a==b and type(a) is type(b) else {path}


def required_edges():
    return {edge(row['id'],other) for row in rd(S01)['role_authority_validity_matrix'] for other in row['separation_required_from']}


def role_checks(profile):
    specs=profile['bootstrap']['inherited_S01_actor_exclusions']
    required=required_edges()
    candidate={edge(r['role'],r['excluded_subject']) for r in specs}
    assert len(specs)==len(required)==8 and candidate==required
    names={'R03':'R03_RESOURCES','R04':'R04_COMPONENT_CUSTODIAN','R05':'R05_COMPONENT_REVIEWER',
           'R06':'R06_ADMISSION_REVIEWER','R07':'R07_ISSUER','R08':'R08_SEPARATE_ACCEPTOR'}
    expected={names[r['role']]+' != '+('each(documentary_preparers[].actor_id)' if r['excluded_subject']=='DOCUMENTARY_PREPARER' else names[r['excluded_subject']]) for r in specs}
    expected|={'R08_SEPARATE_ACCEPTOR != source_author_id','issuer.public_key_hex != acceptor.public_key_hex'}
    expressions=profile['bootstrap']['separation']
    assert set(expressions)==expected and len(expressions)==10
    # Symbolic identity partitions only. These symbols are not real actors or trust contexts.
    symbols={'R01','R02','R03','R04','R05','R06','R07','R08','SOURCE_AUTHOR','DOC0','DOC1'}
    distinct={s:s for s in symbols}
    def rejects(model,preparers):
        for spec in specs:
            excluded=preparers if spec['excluded_subject']=='DOCUMENTARY_PREPARER' else [spec['excluded_subject']]
            if any(model[spec['role']]==model[x] for x in excluded):return True
        return model['R08']==model['SOURCE_AUTHOR']
    assert not rejects(distinct,['DOC0','DOC1'])
    negatives=[]
    for a,b in sorted(required):
        x='DOC0' if a=='DOCUMENTARY_PREPARER' else a
        y='DOC0' if b=='DOCUMENTARY_PREPARER' else b
        model={**distinct,y:distinct[x]}
        assert rejects(model,['DOC0'])
        negatives.append(dict(inherited_exclusion=[a,b],symbolic_collision_rejected=True))
    for role in ['R03','R06','R08']:
        assert rejects({**distinct,'DOC1':role},['DOC0','DOC1'])
    assert rejects({**distinct,'SOURCE_AUTHOR':'R08'},['DOC0'])
    assert not rejects({**distinct,'SOURCE_AUTHOR':'DOC0'},['DOC0'])
    assert not rejects({**distinct,'R02':'R01'},['DOC0'])
    # Five I184 countermodels now fail; preserve that historical review without rewriting it.
    old=rd(P+'D5-I184-I183-source-reconstruction.json')['role_separation']
    assert len(old['symbolic_countermodels'])==5
    for case in old['symbolic_countermodels']:
        a,b=case['coalesced_symbols'];a='DOC0' if a=='DOCUMENTARY_PREPARER' else a;b='DOC0' if b=='DOCUMENTARY_PREPARER' else b
        assert rejects({**distinct,b:distinct[a]},['DOC0'])
    return dict(inherited_exclusions=[list(x) for x in sorted(required)],inherited_exclusion_count=8,
        missing_inherited_exclusions=[],original_eight_symbolic_collisions=negatives,
        I184_five_countermodels_now_rejected=True,second_preparer_collisions_rejected=3,
        extra_source_author_collision_rejected=True,preparer_may_equal_source_author_without_role_waiver=True,
        unconstrained_R01_R02_overlap_not_accidentally_forbidden=True,
        distinct_key_predicate_preserved=True,canonical_identity_provenance_required_not_established=True)


def verify_history(profile):
    pins=profile['input_pins'];assert len(pins)==717
    data=''.join(BASE+':'+p+'\n' for p in sorted(pins)).encode()
    stream=io.BytesIO(subprocess.check_output(['git','cat-file','--batch'],cwd=ROOT,input=data))
    for p,h in sorted(pins.items()):
        head=stream.readline().decode().split();assert len(head)==3 and head[1]=='blob',p
        body=stream.read(int(head[2]));assert stream.read(1)==b'\n'
        assert hashlib.sha256(body).hexdigest()==h==sha(p),p
    m=runpy.run_path(str(ROOT/(P+'D5-I184-audit.py')))
    rec=m['reconstruct']()
    assert rd(m['RECON'])==rec and rd(m['REVIEW'])==m['build_review'](rec)
    old=rd(OLD_SEAL)
    preserved={**old['preserved_published404'],**old['artifacts'],OLD_SEAL:sha(OLD_SEAL)}
    assert len(preserved)==409
    for p,h in preserved.items():assert sha(p)==h,p
    return preserved


def build_review():
    profile=rd(PROFILE);preserved=verify_history(profile)
    oldprofile=rd(OLD_PROFILE);oldpack=rd(OLD_PACK);pack=rd(PACK);defs=pack['$defs']
    assert profile['increment']=='I185' and profile['base_commit']==BASE and profile['profile_id']==PID
    assert profile['schema_pack']['sha256']==sha(PACK) and profile['schema_pack']['path']==PACK
    assert pack['$id']==profile['schema_pack']['id']=='urn:d5:prp181:i185:schema-candidate:02'
    assert defs['verifier_profile']['properties']['id']['const']==PID
    delta=changes(oldpack,pack)
    assert delta=={'/$id','/title','/$defs/verifier_profile/properties/id/const',
        '/$defs/trust_context/properties/documentary_preparers','/$defs/trust_context/required',
        '/$defs/role_acceptance_scope/properties/documentary_preparers_sha256','/$defs/role_acceptance_scope/required'}
    oldconst=oldpack['$defs']['verifier_profile']['properties']['id']['const']
    role_result=role_checks(profile)
    m=runpy.run_path(str(ROOT/(P+'D5-I183-audit.py')))
    m['schema_shape'](pack,defs)
    assert len(defs)==32 and len(pack['oneOf'])==17
    schemas=profile['schema_pack']['top_level_definitions']
    widths={}
    for name in schemas:
        w=m['witness'](defs[name],defs)
        if name=='trust_context':w['documentary_preparers']=[copy.deepcopy(w['documentary_preparers'][0]) for _ in range(16)]
        m['domain'](w);m['validate'](defs[name],w,defs)
        assert m['strict_body'](m['canonical'](w))==w
        assert sum(m['accepts'](defs[n],w,defs) for n in schemas)==1
        widths[name]=len(m['canonical'](w))
    context=defs['trust_context'];array=context['properties']['documentary_preparers']
    assert array['minItems']==1 and array['maxItems']==16 and 'documentary_preparers' in context['required']
    assert set(array['items']['required'])=={'actor_id','provenance_record_id','provenance_record_sha256'}
    assert array['items']['additionalProperties'] is False
    w=m['witness'](context,defs)
    rejected_shapes=0
    for mutate in [lambda x:x.pop('documentary_preparers'),lambda x:x.update(documentary_preparers=[]),
                   lambda x:x.update(documentary_preparers=[copy.deepcopy(w['documentary_preparers'][0]) for _ in range(17)]),
                   lambda x:x['documentary_preparers'][0].pop('provenance_record_sha256'),
                   lambda x:x['documentary_preparers'][0].update(unrecognized=True),
                   lambda x:x['profile'].update(id=oldconst)]:
        bad=copy.deepcopy(w);mutate(bad)
        m['rejected'](lambda:m['validate'](context,bad,defs));rejected_shapes+=1
    root=m['witness'](defs['final_root'],defs)
    del root['signed_core']['role_acceptance_scope']['documentary_preparers_sha256']
    m['rejected'](lambda:m['validate'](defs['final_root'],root,defs));rejected_shapes+=1
    root=m['witness'](defs['final_root'],defs)
    root['signed_core']['trust_verifier_profile']['id']=oldconst
    m['rejected'](lambda:m['validate'](defs['final_root'],root,defs));rejected_shapes+=1
    assert widths['trust_context']<=8192 and widths['final_root']<=8192
    assert profile['bootstrap']['context_limits']==oldprofile['bootstrap']['context_limits']
    assert profile['bootstrap']['assigned_persons'] is None and profile['bootstrap']['actual_key_material'] is None
    assert profile['bootstrap']['actual_context'] is None and profile['bootstrap']['actual_request'] is None
    for key in ['cryptography','scope','budget','references','final_CP07_conditions','remaining_work','decision','E06']:
        assert profile[key]==oldprofile[key],key
    for key,value in oldprofile['current_effect'].items():assert profile['current_effect'][key]==value
    assert profile['current_effect']['F183_01_candidate_repair_prepared']
    assert not profile['current_effect']['F183_01_independent_closure_accepted']
    for a,b in zip(oldprofile['semantic_contracts'],profile['semantic_contracts']):
        assert a['id']==b['id']
        if a['id'] in ['C08','C09']:assert b['rule'].startswith(a['rule'])
        else:assert a==b
    binding=profile['bootstrap']['documentary_preparer_binding']
    assert set(binding)=={'schema_pointer','complete_list','provenance','identity_resolution','predicate','binding','custody_and_cost','current_state'}
    commitment=profile['encoding']['hash_commitments']['documentary_preparers_sha256']
    assert commitment.startswith('SHA256(JCS(trust_context.documentary_preparers))')
    assert 'documentary_preparers_sha256' in defs['role_acceptance_scope']['required']
    for s in profile['scope']['future_slots']:assert not (ROOT/s['path']).exists()
    assert not (ROOT/'testing/prospective_capture_joint_prp181').exists()
    assert profile['finding_resolution']['eight_inherited_actor_exclusions_preserved']
    assert not profile['finding_resolution']['independent_closure_accepted']
    assert set(profile['work_unit']['rollback_files'])==FILES
    return dict(schema='d5.i185-preparation-review.v1',increment='I185',date='2026-11-16',base_commit=BASE,
        proposal='PGO181-SPLIT-ROOT-01',profile_id=PID,status='F183_01_DOCUMENTARY_REPAIR_PREPARED_IN_CANDIDATE_02_NOT_ADOPTED_NOT_IMPLEMENTED_NOT_ADMITTED',
        schema_pack=dict(path=PACK,sha256=sha(PACK)),profile=dict(path=PROFILE,sha256=sha(PROFILE)),
        exact_schema_delta=sorted(delta),role_repair=role_result,mandatory_new_shapes_rejection_cases=rejected_shapes,
        definitions=32,schema_families=17,input_pins=717,prior_published_files_preserved=len(preserved),
        in_memory_placeholder_widths=widths,
        width_scope='In-memory structural data only, including16 maximum-length preparer entries; not authentic actors, provenance, keys, signatures, evidence or a global resource/Reader fit proof. Semantic identity/ordering/completeness must be independently established.',
        binding_review=dict(whole_context_digest_covers_preparer_provenance=True,explicit_list_digest_in_both_signed_cores=True,
            authentic_actor_alias_resolution_complete_scope_and_custody_required=True,
            candidate01_context_root_profile_not_accepted_by_candidate02_shapes=True,
            actual_trust_or_independence_established=False,no_implicit_extra_runtime_files=True),
        F183_01=dict(candidate_gap_repaired=True,historical_finding_unchanged=True,separate_review_pending=True,independent_closure_accepted=False),
        provenance=dict(preparer='Same Codex assistant/chat; no actual role assignments made',actor_independent=False,organizationally_independent=False,independent_acceptance=False),
        current_effect=profile['current_effect'],decision=profile['decision'],E06=profile['E06'],remaining_work=profile['remaining_work'],work_unit=profile['work_unit'])


def main():
    review=build_review();assert rd(PREP)==review
    prior=rd(OLD_SEAL);preserved={**prior['preserved_published404'],**prior['artifacts'],OLD_SEAL:sha(OLD_SEAL)}
    seal=rd(SEAL)
    assert seal['schema']=='d5.i185-integrity.v1' and seal['base_commit']==BASE
    assert seal['preserved_published409']==preserved
    assert set(seal['artifacts'])==FILES-{SEAL}
    for p,h in seal['artifacts'].items():assert sha(p)==h,p
    assert seal['source_only'] and seal['resource_obligations_closed']==0 and seal['IR03']=='NOT_READY'
    for key in ['independent_acceptance','product_or_components_executed','quotas_changed','rebind_applied','proposal_enabled','D5_closed']:
        assert seal[key] is False
    changed=set(git('diff',BASE,'--name-only').splitlines())|set(git('ls-files','--others','--exclude-standard').splitlines())
    assert changed==FILES,changed
    subprocess.check_call(['git','merge-base','--is-ancestor',BASE,'HEAD'],cwd=ROOT)
    if git('rev-parse','HEAD')!=BASE:assert not git('status','--porcelain')
    print(json.dumps(dict(status='PASS_STATIC_SOURCE_ONLY',increment='I185',candidate='02',inherited_S01_actor_exclusions=8,
        missing_exclusions=0,F183_01_candidate_gap_repaired=True,F183_01_independent_closure_accepted=False,
        historical_pins=717,prior_published_files_preserved=409,new_files=6,adopted=False,implemented=False,
        product_or_components_executed=0,quotas_changed=False,rebind_applied=False,resource_obligations_closed=0,
        proposal_enabled=False,F179_01_resolved=False,D5_closed=False,IR03='NOT_READY',git_head=git('rev-parse','HEAD')),sort_keys=True))

if __name__=='__main__':main()
