#!/usr/bin/env python3
"""I186 documentary review only: Git/JSON, exact deltas and symbolic role relations. No target/crypto execution."""
import hashlib
import io
import itertools
import json
import re
import runpy
import subprocess
from pathlib import Path

ROOT=Path(__file__).resolve().parents[2]
P='docs/validation/'
BASE='df98c54ea86b885c8768b44f34cc467c230c6456'
PACK=P+'D5-I185-PGO181-SCHEMAS-CANDIDATE-02.json'
PROFILE=P+'D5-I185-PGO181-TRUST-PROFILE-CANDIDATE-02.json'
OLD_PACK=P+'D5-I183-PGO181-SCHEMAS-CANDIDATE.json'
OLD_PROFILE=P+'D5-I183-PGO181-TRUST-PROFILE-CANDIDATE.json'
S01=P+'D5-I179-S01-ROLES-SCOPE-GATES.json'
PRIOR_SEAL=P+'D5-I185-integrity.json'
RECON=P+'D5-I186-I185-source-reconstruction.json'
REVIEW=P+'D5-I186-I185-documentary-review.json'
AUDIT=P+'D5-I186-audit.py'
SEAL=P+'D5-I186-integrity.json'
DOC='docs/design/D5-I186-I185-SEPARATION-REPAIR-REVIEW.md'
FILES={RECON,REVIEW,AUDIT,SEAL,DOC}
PRIOR_FILES={PACK,PROFILE,P+'D5-I185-preparation-review.json',P+'D5-I185-audit.py',PRIOR_SEAL,
             'docs/design/D5-I185-PGO181-SEPARATION-REPAIR-CANDIDATE.md'}


def rd(p):return json.loads((ROOT/p).read_text())
def sha(p):return hashlib.sha256((ROOT/p).read_bytes()).hexdigest()
def git(*args):return subprocess.check_output(['git',*args],cwd=ROOT,text=True).strip()
def pair(a,b):return tuple(sorted((a,b)))
def pin(p,pointer):return dict(path=p,sha256=sha(p),json_pointer=pointer)


def differences(a,b):
    pending=[('',a,b)];out=[]
    while pending:
        path,x,y=pending.pop()
        if type(x) is dict and type(y) is dict:
            for key in set(x)|set(y):
                child=path+'/'+key.replace('~','~0').replace('/','~1')
                if key not in x or key not in y:out.append(child)
                else:pending.append((child,x[key],y[key]))
        elif type(x) is not type(y) or x!=y:out.append(path)
    return sorted(out)


def independent_roles(profile):
    matrix=rd(S01)['role_authority_validity_matrix']
    required={pair(r['id'],q) for r in matrix for q in r['separation_required_from']}
    typed={pair(r['role'],r['excluded_subject']) for r in profile['bootstrap']['inherited_S01_actor_exclusions']}
    assert len(required)==len(typed)==8 and typed==required
    assert len(profile['bootstrap']['inherited_S01_actor_exclusions'])==8
    # Parse the explicit human-readable predicates independently from the typed matrix.
    written=set();key_predicates=[]
    for text in profile['bootstrap']['separation']:
        a,b=text.split(' != ')
        if a=='issuer.public_key_hex':
            assert b=='acceptor.public_key_hex';key_predicates.append(text);continue
        left=re.fullmatch(r'(R0[1-8])_[A-Z_]+',a)
        assert left
        if b=='each(documentary_preparers[].actor_id)':right='DOCUMENTARY_PREPARER'
        elif b=='source_author_id':right='SOURCE_AUTHOR'
        else:
            match=re.fullmatch(r'(R0[1-8])_[A-Z_]+',b);assert match;right=match[1]
        written.add(pair(left[1],right))
    assert len(key_predicates)==1 and len(written)==9
    assert written==required|{pair('R08','SOURCE_AUTHOR')}
    def expand(edges,n):
        result=set()
        for a,b in edges:
            aa=[f'DOC{i:02}' for i in range(n)] if a=='DOCUMENTARY_PREPARER' else [a]
            bb=[f'DOC{i:02}' for i in range(n)] if b=='DOCUMENTARY_PREPARER' else [b]
            result.update(pair(x,y) for x in aa for y in bb)
        return result
    rows=[];collision_cases=0
    for n in range(1,17):
        actual=expand(written,n)
        expected=expand(required,n)|{pair('R08','SOURCE_AUTHOR')}
        assert actual==expected
        symbols=[f'R0{i}' for i in range(1,9)]+['SOURCE_AUTHOR']+[f'DOC{i:02}' for i in range(n)]
        def rejects(values):return any(values[a]==values[b] for a,b in actual)
        assert not rejects({x:x for x in symbols})
        required_rejections=allowed_merges=0
        for a,b in itertools.combinations(symbols,2):
            model={x:x for x in symbols};model[b]=model[a]
            rejected=rejects(model)
            assert rejected==(pair(a,b) in expected)
            required_rejections+=int(rejected);allowed_merges+=int(not rejected);collision_cases+=1
        assert required_rejections==3*n+6
        rows.append(dict(preparers=n,expanded_actor_exclusions=len(actual),single_pair_partitions_checked=required_rejections+allowed_merges,
                         required_collisions_rejected=required_rejections,unconstrained_merges_not_globally_banned=allowed_merges))
    previous=rd(P+'D5-I184-I183-source-reconstruction.json')['role_separation']['symbolic_countermodels']
    assert len(previous)==5
    assert all(tuple(x['coalesced_symbols']) in required for x in previous)
    return dict(inherited_actor_exclusions=[list(x) for x in sorted(required)],missing_exclusions=[],
        inherited_exclusion_count=8,written_actor_exclusions=9,distinct_key_exclusions=1,
        preparer_cardinalities_checked=rows,single_pair_partitions_checked=collision_cases,
        all_five_I184_countermodels_rejected=True,all_list_positions_universally_covered=True,
        documentary_preparer_not_assumed_source_author=True,
        scope='Finite symbolic identity partitions and exact edge-set equality, not a runtime schedule, actual people/appointments, cryptography, alias resolver or custody proof.')


def reconstruct():
    profile=rd(PROFILE);pins={**profile['input_pins'],**{p:sha(p) for p in sorted(PRIOR_FILES)}}
    assert len(pins)==723
    requests=''.join(BASE+':'+p+'\n' for p in sorted(pins)).encode()
    stream=io.BytesIO(subprocess.check_output(['git','cat-file','--batch'],cwd=ROOT,input=requests))
    for p,h in sorted(pins.items()):
        header=stream.readline().decode().split();assert len(header)==3 and header[1]=='blob',p
        body=stream.read(int(header[2]));assert stream.read(1)==b'\n'
        assert hashlib.sha256(body).hexdigest()==h==sha(p),p
    # Predecessor documentary checks only; never its publication-boundary main.
    prior=runpy.run_path(str(ROOT/(P+'D5-I185-audit.py')))
    assert prior['build_review']()==rd(P+'D5-I185-preparation-review.json')
    pack=rd(PACK);oldpack=rd(OLD_PACK);oldprofile=rd(OLD_PROFILE);defs=pack['$defs']
    expected_delta=['/$defs/role_acceptance_scope/properties/documentary_preparers_sha256','/$defs/role_acceptance_scope/required',
        '/$defs/trust_context/properties/documentary_preparers','/$defs/trust_context/required',
        '/$defs/verifier_profile/properties/id/const','/$id','/title']
    delta=differences(oldpack,pack);assert delta==sorted(expected_delta)
    assert profile['schema_pack']['sha256']==sha(PACK)
    assert profile['profile_id']==defs['verifier_profile']['properties']['id']['const']=='PGO181-TRUST-ED25519-JCS-CANDIDATE-02'
    context=defs['trust_context'];preparers=context['properties']['documentary_preparers']
    assert 'documentary_preparers' in context['required'] and preparers['minItems']==1 and preparers['maxItems']==16
    record=preparers['items'];assert record['additionalProperties'] is False
    assert set(record['properties'])==set(record['required'])=={'actor_id','provenance_record_id','provenance_record_sha256'}
    assert 'documentary_preparers_sha256' in defs['role_acceptance_scope']['required']
    assert defs['signed_core']['properties']['role_acceptance_scope']=={'$ref':'#/$defs/role_acceptance_scope'}
    assert 'trust_context_sha256' in defs['signed_core']['required']
    assert defs['final_root']['properties']['signed_core']=={'$ref':'#/$defs/signed_core'}
    assert all(s in defs['final_root']['required'] for s in ['issuer_signature','acceptor_signature'])
    b=profile['bootstrap']['documentary_preparer_binding']
    for field,phrases in {
        'complete_list':['ordered','no duplicate','no omitted','More than16','over8192'],
        'provenance':['authentic canonical actor','exact candidate02 profile/pack digests','do not establish'],
        'identity_resolution':['same accepted identity resolution','Aliases','Missing/ambiguous/unaccepted','not assumed equal'],
        'predicate':['every one of the8','universally','No conditional waiver'],
        'binding':['trust_context_sha256','documentary_preparers_sha256','Both role-domain signatures','completeness'],
        'custody_and_cost':['not repository files or network','E01-E05','graph/IO requalification']}.items():
        assert all(s in b[field] for s in phrases),(field,phrases)
    for field in ['cryptography','scope','budget','final_CP07_conditions','decision','E06']:
        assert profile[field]==oldprofile[field],field
    for k,v in oldprofile['current_effect'].items():assert profile['current_effect'][k]==v
    assert profile['bootstrap']['assigned_persons'] is None and profile['bootstrap']['actual_key_material'] is None
    assert profile['bootstrap']['actual_context'] is None and not profile['bootstrap']['independent_acceptance']
    for s in profile['scope']['future_slots']:assert not (ROOT/s['path']).exists()
    assert not (ROOT/'testing/prospective_capture_joint_prp181').exists()
    return dict(schema='d5.i186-i185-source-reconstruction.v1',increment='I186',date='2026-11-16',base_commit=BASE,
        input_pins=pins,method='Fresh Git hash verification, separate iterative schema-delta scan, direct required-field/core binding checks and expanded symbolic role partitions for1..16 preparers.',
        exact_schema_delta=delta,role_review=independent_roles(profile),
        binding_checks=dict(preparer_records_required_closed_bounded=True,complete_sorted_unique_list_semantically_required=True,
            actual_provenance_not_established_by_schema_or_hash=True,common_authentic_canonical_actor_resolution_required=True,
            full_context_and_explicit_list_committed_in_same_signed_core=True,candidate01_profile_and_required_shapes_not_silently_accepted=True,
            schema_validation_alone_does_not_check_order_uniqueness_aliases_or_real_independence=True),
        preserved_scope=dict(schema_families=17,definitions=32,full_CP07_conditions=9,physical_Reader_paths=496,
            read_design_bytes=266693693,actual_Reader_fit_verified=False,old_scopes_limits_crypto_decision_preserved=True),
        readiness_gaps=rd(P+'D5-I184-I183-documentary-review.json')['remaining_work'],
        verdict=dict(F183_01_documentary_gap_resolved_in_candidate02=True,new_blocking_documentary_findings=0,
            independent_closure_accepted=False,competent_policy_adoption=False,actual_identity_or_independence_verified=False,
            implemented=False,F179_01_resolved=False,resource_obligations_closed=0,product_or_components_executed=0))


def build_review(rec):
    profile=rd(PROFILE)
    return dict(schema='d5.i186-i185-documentary-review.v1',increment='I186',date='2026-11-16',timezone='Europe/Madrid',base_commit=BASE,
        proposal='PGO181-SPLIT-ROOT-01',profile_id=profile['profile_id'],
        status='F183_01_DOCUMENTARY_REPAIR_CONFIRMED_IN_CANDIDATE_02_NOT_ADOPTED_NOT_IMPLEMENTED_NOT_ADMITTED',
        reconstruction=dict(path=RECON,sha256=sha(RECON)),
        provenance=dict(reviewer='Same Codex assistant/chat that prepared I183/I185',methodological_reconstruction_separate=True,
            actor_independent=False,organizationally_independent=False,independent_acceptance=False,custodian_acceptance=False),
        finding_disposition=dict(id='F183-01',disposition='RESOLVED_DOCUMENTARY_GAP_IN_CANDIDATE_02',
            evidence=[pin(S01,'/role_authority_validity_matrix'),pin(PROFILE,'/bootstrap/inherited_S01_actor_exclusions'),
                pin(PROFILE,'/bootstrap/documentary_preparer_binding'),pin(PACK,'/$defs/trust_context/properties/documentary_preparers'),
                pin(PACK,'/$defs/role_acceptance_scope/properties/documentary_preparers_sha256')],
            eight_exclusions_preserved=True,five_original_gaps_repaired=True,complete_preparer_scope_bound=True,
            historical_I184_finding_unchanged=True,independent_closure_accepted=False,
            scope='Confirms repair of exact documentary gap; no accepted real roles/trust/custody or runtime enforcement/admission.'),
        new_findings=[],checks=[dict(id=i,scope=s,result=r) for i,s,r in [
            ('R01','Eight inherited actor exclusions equal S01 and explicit predicate list','PASS_DOCUMENTARY_REPAIR'),
            ('R02','Universal scope for every preparer position/cardinality1..16','PASS_SYMBOLIC_SCOPE'),
            ('R03','All five original I184 countermodels','REJECTED_BY_CANDIDATE02_RELATIONS'),
            ('R04','Separate source-author and key predicates retained','PASS_NO_SEPARATION_LOSS'),
            ('R05','Mandatory closed provenance records plus sorted/unique/complete authentic list','PASS_DECLARED_CONTRACT_NOT_REAL_PROVENANCE'),
            ('R06','Whole context plus explicit preparer-list digest in both signed role domains','PASS_SIGNED_SCOPE_DESIGN_NOT_CRYPTO_EXECUTION'),
            ('R07','No blanket mutual-distinctness beyond required actor edges','PASS_NO_ACCIDENTAL_GLOBAL_RESTRICTION'),
            ('R08','Seven schema delta paths and candidate02 pinned identity','PASS_BOUNDED_VERSIONED_DELTA'),
            ('R09','Original source/CP07/Reader/resource/crypto scope and caps','PRESERVED_NOT_REQUALIFIED'),
            ('R10','Same reviewer/preparer actor, no appointments, adoption or execution','PASS_PROVENANCE_AND_NONADMISSION_DISCLOSURE')]],
        verdict=rec['verdict'],remaining_work=rec['readiness_gaps'],current_effect=profile['current_effect'],decision=profile['decision'],E06=profile['E06'],
        work_unit=dict(rollback_files=sorted(FILES),verification_command='python3 docs/validation/D5-I186-audit.py',expected_result='PASS_STATIC_SOURCE_ONLY',
            runtime_harness='N/A: documentary candidate review; no runtime source change/product/component/crypto execution.',over400_lines=True,
            reason='Traceable Git/schema/binding/role reconstruction, finding disposition and preservation seal as one reviewable unit; overage reported.'),
        publication=dict(commit_and_push_requested=True,publication_not_adoption_or_authority=True))


def main():
    rec=reconstruct();assert rd(RECON)==rec and rd(REVIEW)==build_review(rec)
    old=rd(PRIOR_SEAL);preserved={**old['preserved_published409'],**old['artifacts'],PRIOR_SEAL:sha(PRIOR_SEAL)}
    assert len(preserved)==415
    seal=rd(SEAL);assert seal['schema']=='d5.i186-integrity.v1' and seal['base_commit']==BASE
    assert seal['preserved_published415']==preserved and set(seal['artifacts'])==FILES-{SEAL}
    for pins in [preserved,seal['artifacts']]:
        for p,h in pins.items():assert sha(p)==h,p
    assert seal['source_only'] and seal['resource_obligations_closed']==0 and seal['IR03']=='NOT_READY'
    for k in ['independent_acceptance','product_or_components_executed','quotas_changed','rebind_applied','proposal_enabled','D5_closed']:assert seal[k] is False
    changed=set(git('diff',BASE,'--name-only').splitlines())|set(git('ls-files','--others','--exclude-standard').splitlines())
    assert changed==FILES,changed
    subprocess.check_call(['git','merge-base','--is-ancestor',BASE,'HEAD'],cwd=ROOT)
    if git('rev-parse','HEAD')!=BASE:assert not git('status','--porcelain')
    print(json.dumps(dict(status='PASS_STATIC_SOURCE_ONLY',increment='I186',candidate='02',F183_01_documentary_gap_resolved=True,
        inherited_actor_exclusions=8,missing_exclusions=0,new_blocking_documentary_findings=0,
        independent_closure_accepted=False,adopted=False,implemented=False,historical_pins=723,
        prior_published_files_preserved=415,new_files=5,product_or_components_executed=0,quotas_changed=False,rebind_applied=False,
        resource_obligations_closed=0,proposal_enabled=False,F179_01_resolved=False,D5_closed=False,IR03='NOT_READY',git_head=git('rev-parse','HEAD')),sort_keys=True))

if __name__=='__main__':main()
