#!/usr/bin/env python3
"""I192 documentary review: Git/JSON/schema and evidence DAG arithmetic only; no target/signature/image/identity service execution."""
import hashlib
import io
import json
import runpy
import subprocess
from pathlib import Path

ROOT=Path(__file__).resolve().parents[2];P='docs/validation/'
BASE='e7d8444a620b9c81bd216da3c89a224fea666da6'
PACK=P+'D5-I191-CALLER-IMAGE-CUSTODY-SCHEMAS-CANDIDATE.json'
SPEC=P+'D5-I191-CALLER-IMAGE-CUSTODY-CONTRACT-CANDIDATE.json'
OLD_PREP=P+'D5-I191-preparation-review.json'
OLD_AUDIT=P+'D5-I191-audit.py'
PRIOR_SEAL=P+'D5-I191-integrity.json'
OLD_DOC='docs/design/D5-I191-CALLER-IMAGE-CUSTODY-CONTRACT-CANDIDATE.md'
PRIOR_FILES={PACK,SPEC,OLD_PREP,OLD_AUDIT,PRIOR_SEAL,OLD_DOC}
RECON=P+'D5-I192-I191-source-reconstruction.json'
REVIEW=P+'D5-I192-I191-documentary-review.json'
AUDIT=P+'D5-I192-audit.py';SEAL=P+'D5-I192-integrity.json'
DOC='docs/design/D5-I192-I191-CALLER-IMAGE-CUSTODY-REVIEW.md'
FILES={RECON,REVIEW,AUDIT,SEAL,DOC}


def rd(p):return json.loads((ROOT/p).read_text())
def sha(p):return hashlib.sha256((ROOT/p).read_bytes()).hexdigest()
def git(*args):return subprocess.check_output(['git',*args],cwd=ROOT,text=True).strip()
def jlen(x):return len(json.dumps(x,ensure_ascii=False,sort_keys=True,separators=(',',':'),allow_nan=False).encode('ascii'))
def pin(p,q):return dict(path=p,sha256=sha(p),json_pointer=q)
def pair(a,b):return tuple(sorted((a,b)))


def children(s):
    for k in ['properties','$defs']:yield from s.get(k,{}).values()
    for k in ['oneOf','anyOf']:yield from s.get(k,[])
    for k in ['items','propertyNames','additionalProperties']:
        if isinstance(s.get(k),dict):yield s[k]


def refs(s):
    if '$ref' in s:
        assert s['$ref'].startswith('#/$defs/');yield s['$ref'][8:]
    for q in children(s):yield from refs(q)


def dfs_order(edges):
    order=[];done=set();active=set()
    def visit(n):
        assert n in edges and n not in active
        if n in done:return
        active.add(n)
        for dep in sorted(edges[n]):visit(dep)
        active.remove(n);done.add(n);order.append(n)
    for n in sorted(edges):visit(n)
    return order


def schema_bound(s,defs,accepted_caps=None):
    accepted_caps=accepted_caps or {}
    if '$ref' in s:
        n=s['$ref'][8:];raw=schema_bound(defs[n],defs,accepted_caps)
        return min(raw,accepted_caps.get(n,raw))
    if 'const' in s:return jlen(s['const'])
    if 'enum' in s:return max(jlen(x) for x in s['enum'])
    for k in ['anyOf','oneOf']:
        if k in s:return max(schema_bound(q,defs,accepted_caps) for q in s[k])
    t=s['type']
    if t=='integer':
        assert 0<=s['minimum']<=s['maximum']<=9007199254740991
        return len(str(s['maximum']))
    if t=='string':return 2+2*s['maxLength']
    if t=='array':
        n=s['maxItems'];return 2+n*schema_bound(s['items'],defs,accepted_caps)+max(0,n-1)
    if t=='object':
        props=s['properties'];assert s['additionalProperties'] is False and set(s['required'])==set(props)
        return 2+sum(jlen(k)+1+schema_bound(v,defs,accepted_caps) for k,v in props.items())+max(0,len(props)-1)
    raise AssertionError(t)


def reconstruct():
    spec=rd(SPEC);pins={**spec['input_pins'],**{p:sha(p) for p in sorted(PRIOR_FILES)}}
    assert len(pins)==756
    req=''.join(BASE+':'+p+'\n' for p in sorted(pins)).encode()
    stream=io.BytesIO(subprocess.check_output(['git','cat-file','--batch'],cwd=ROOT,input=req))
    for p,h in sorted(pins.items()):
        head=stream.readline().decode().split();assert len(head)==3 and head[1]=='blob',p
        body=stream.read(int(head[2]));assert stream.read(1)==b'\n'
        assert hashlib.sha256(body).hexdigest()==h==sha(p),p
    previous=runpy.run_path(str(ROOT/OLD_AUDIT));assert previous['build_review']()==rd(OLD_PREP)
    pack=rd(PACK);defs=pack['$defs'];families=spec['record_families'];assert len(defs)==24 and len(families)==8
    schema_edges={n:set(refs(s)) for n,s in defs.items()};schema_order=dfs_order(schema_edges);assert len(schema_order)==24
    assert pack['oneOf']==[{'$ref':'#/$defs/'+n} for n in families]
    for b in [spec['schema_pack'],*spec['bindings'].values()]:assert sha(b['path'])==b['sha256']
    raw={n:schema_bound(defs[n],defs) for n in families}
    records=defs['custody_signed_core']['properties']['records']['properties']
    record_hashes=defs['custody_signed_core']['properties']['record_hashes']['properties']
    expected={'actor_registry','image_manifest','caller_identity','platform_custody','acceptance_record'}
    assert set(records)==set(record_hashes)==expected
    for n in expected:assert records[n]=={'$ref':'#/$defs/'+n} and record_hashes[n]=={'$ref':'#/$defs/sha256'}
    accepted_caps={n:spec['record_caps_bytes'][n] for n in expected}
    composed=schema_bound(defs['custody_bundle'],defs,accepted_caps)
    assert raw==dict(anchor_registry=35252,actor_registry=213612,image_manifest=129700,caller_identity=1933,
                    platform_custody=5940,acceptance_record=13879,custody_bundle=368348,launch_receipt=2702)
    assert composed==221644 and composed<spec['record_caps_bytes']['custody_bundle']==262144
    evidence_edges={n:set(v) for n,v in spec['record_order'].items()}
    assert not spec['external_prior_nodes'];evidence_order=dfs_order(evidence_edges);assert len(evidence_order)==16
    def ancestors(n):
        out=set();todo=list(evidence_edges[n])
        while todo:
            x=todo.pop()
            if x not in out:out.add(x);todo+=list(evidence_edges[x])
        return out
    for n in ['ANCHOR','ACTOR_REGISTRY','IMAGE_MANIFEST','CALLER_IDENTITY','PLATFORM_CUSTODY','C_CONTEXT']:
        assert not ancestors(n)&{'ACCEPTANCE','BUNDLE','Q_REQUEST','FINAL_ROOT','ATOMIC_CLAIM','LAUNCH_RECEIPT'}
    assert {'FINAL_ROOT','Q_REQUEST','EXTERNAL_CURRENT_MAPPING'}<=ancestors('ATOMIC_CLAIM')
    assert {'BUNDLE','ATOMIC_CLAIM','FINAL_ROOT'}<=ancestors('LAUNCH_RECEIPT')
    proto=rd(spec['bindings']['protocol_schemas02']['path'])['$defs'];profile=rd(spec['bindings']['profile02']['path'])
    fields=rd(OLD_PREP)['C_projection_fields_with_identical_types'];assert len(fields)==14
    for n in fields:assert defs['acceptance_record']['properties'][n]==proto['trust_context']['properties'][n]
    assert 'trust_context_sha256' in defs['acceptance_record']['required']
    assert defs['custody_bundle']['properties']['signed_core']=={'$ref':'#/$defs/custody_signed_core'}
    assert set(defs['custody_bundle']['properties']['approvals']['properties'])=={'R01_RUNTIME','R02_PLATFORM','R08_ACCEPTANCE'}
    assert 'signature_hex' in defs['custody_approval']['required'] and defs['custody_approval']['properties']['signature_hex']=={'$ref':'#/$defs/signature'}
    assert 'signature' not in defs['acceptance_record']['properties'] # approval coverage is through the bundle
    for f in ['custody_schema_pack_sha256','custody_contract_sha256']:
        assert f in defs['image_manifest']['required'] and f in defs['custody_signed_core']['required']
    assert not {'bundle_sha256','launch_receipt','runtime_request','final_root','signature'}&set(defs['custody_signed_core']['properties'])
    assert set(defs['image_manifest']['properties']['source_to_image']['properties'])==set(proto['source_bindings']['properties'])
    assert defs['image_manifest']['properties']['source_bindings']=={'$ref':'#/$defs/source_bindings'}
    assert len(defs['platform_custody']['properties']['guarantees']['properties'])==8
    assert defs['caller_identity']['properties']['permission']['const']=='BOOTSTRAP_CUSTODY_ONLY_FULL_ROOT_AND_SEPARATE_REQUEST_REQUIRED'
    assert defs['acceptance_record']['properties']['decision']['const']=='IDENTITY_IMAGE_CUSTODY_ONLY_NOT_RESOURCE_OR_CAPTURE_ADMISSION'
    assert defs['launch_receipt']['properties']['role']['const']=='CALLER_PRIVATE_RECEIPT_NOT_NEW_FRAME_OR_AUTHORITY'
    inherited={pair(r['role'],r['excluded_subject']) for r in spec['inheritance']['S01_actor_exclusions']}
    assert inherited=={pair(r['role'],r['excluded_subject']) for r in profile['bootstrap']['inherited_S01_actor_exclusions']} and len(inherited)==8
    assert spec['inheritance']['extra_custody_separation']==['R08_ACCEPTANCE != R01_RUNTIME','R08_ACCEPTANCE != R02_PLATFORM','R08_key != R01_key','R08_key != R02_key']
    assert len(set(spec['custody_approval_domains'].values()))==3
    for n in ['sha256','signature','identity','validity','trusted_key','source_bindings','verifier_profile','proposal_scope']:assert defs[n]==proto[n]
    assert spec['inheritance']['existing_full_CP07_conditions']==profile['final_CP07_conditions']
    assert spec['decision']==profile['decision'] and spec['E06']==profile['E06']
    assert not spec['current_effect']['actual_trust_or_source_image_mapping_verified'] and not spec['current_effect']['actual_custody_bundle_or_anchor_created']
    for s in profile['scope']['future_slots']:assert not (ROOT/s['path']).exists()
    assert not (ROOT/'testing/prospective_capture_joint_prp181').exists()
    return dict(schema='d5.i192-i191-source-reconstruction.v1',increment='I192',date='2026-11-16',base_commit=BASE,
        input_pins=pins,method='Fresh Git blobs; separate schema/evidence DFS, mandatory signature-coverage/C-projection paths, source/role joins and ASCII-safe size recurrence with explicit nested-record cap composition.',
        schema_checks=dict(record_families=8,definitions=24,local_reference_order=schema_order,acyclic=True,
            five_nested_records_and_hash_names_exact=True,mandatory_C_hash_under_signed_core=True,
            acceptance_has_no_standalone_signature_field=True,three_bundle_role_approvals_cover_the_same_core=True),
        evidence_checks=dict(order=evidence_order,nodes=16,acyclic=True,antecedent_records_do_not_depend_on_later_acceptance_bundle_root=True,
            atomic_claim_after_current_mapping_Q_root=True,receipt_after_claim=True,
            accepted_platform_facts_cannot_be_forecast_from_future_bundle=True,model_not_actual_enrollment_or_issuance=True),
        C_and_identity_checks=dict(identical_type_projection_fields=fields,unchanged_C_Q_I_A_L_outputs=True,
            eight_S01_exclusions_preserved=True,extra_custody_actor_key_separation_preserved=True,
            human_and_software_principals_distinct_semantically=True,aliases_provenance_appointments_require_actual_accepted_evidence=True,
            unique_external_epoch_C_mapping_required=True,root_keys_not_automatically_custody_anchors=True,
            runtime_digest_not_replaced_by_image_digest=True,exact_six_source_mapping_and_complete_closure_required=True,
            actual_identity_source_image_security_or_custody_verified=False),
        serialized_bounds=dict(unrestricted_conservative_schema_upper_bytes=raw,declared_record_caps_bytes=spec['record_caps_bytes'],
            per_nested_record_caps_assumed=accepted_caps,conditional_bundle_upper_bytes=composed,bundle_cap_bytes=262144,
            conditional_bundle_margin_bytes=262144-composed,
            scope='ASCII/safe-integer JCS bounds for typed records. Each nested record must actually satisfy its separate byte cap; schema-only conservative upper beyond a cap is not proof of infeasibility. This is neither complete referenced-evidence size nor actual record/heap/CPU/IO/phase fit.'),
        verdict=dict(new_blocking_documentary_findings=0,documentary_contract_consistent_under_external_custody_premises=True,
            adopted=False,implemented=False,independent_acceptance=False,actual_actors_caller_image_or_anchors_supplied=False,
            actual_resource_or_900_fit_verified=False,F179_01_resolved=False,resource_obligations_closed=0,product_or_components_executed=0))


def build_review(rec):
    spec=rd(SPEC)
    return dict(schema='d5.i192-i191-documentary-review.v1',increment='I192',date='2026-11-16',timezone='Europe/Madrid',base_commit=BASE,
        proposal='PGO181-SPLIT-ROOT-01',profile_id=spec['profile_id'],contract_id=spec['contract_id'],
        status='CALLER_IMAGE_CUSTODY_DOCUMENTARY_CONTRACT_CONFIRMED_NOT_ADOPTED_NOT_IMPLEMENTED_NOT_ADMITTED',
        reconstruction=dict(path=RECON,sha256=sha(RECON)),
        provenance=dict(reviewer='Same Codex assistant/chat that prepared I191 and prior contracts',methodological_reconstruction_separate=True,
            actor_independent=False,organizationally_independent=False,independent_acceptance=False,custodian_acceptance=False),
        findings=[],checks=[dict(id=i,scope=s,result=r) for i,s,r in [
            ('R01','External preaccepted anchor/digest/purpose, no supplied-key self trust','PASS_TRUST_BOUNDARY_SPEC_NOT_AUTHORITY_PROOF'),
            ('R02','Canonical accountable humans distinct from caller software, complete aliases/evidence','PASS_DECLARED_IDENTITY_POLICY_NOT_IDENTITY_RESOLUTION'),
            ('R03','Eight S01 exclusions and additional R08/R01/R02 actor/key separation','PASS_SEPARATION_PRESERVED_NOT_REAL_INDEPENDENCE'),
            ('R04','Six source/image mapping, full runtime/build/closure, no image self hash','PASS_REQUIRED_MAPPING_NOT_MEASUREMENT'),
            ('R05','Caller/platform/domain/constructor/clock/global ledger bindings','PASS_EXTERNAL_PREREQUISITES_NOT_BACKEND_PROOF'),
            ('R06','14 same-typed C fields plus exact C digest/constant/time/clock relations','PASS_PROJECTION_CONTRACT_NOT_REAL_CONTEXT'),
            ('R07','One current external epoch/C mapping without new wire fields','PASS_NO_HIDDEN_CHANNEL_AUTHORITY'),
            ('R08','All five record hashes and C digest inside common three-approval core','PASS_SIGNATURE_COVERAGE_SPEC_NOT_CRYPTO_EXECUTION'),
            ('R09','16-node evidence order, genuine antecedents before C, claim after root','PASS_DECLARED_ORDER_NO_PREDICTIVE_ACCEPTANCE'),
            ('R10','Per-record caps and conditional bundle221644 <=262144','PASS_CONDITIONAL_SERIALIZATION_NOT_RESOURCE_FIT'),
            ('R11','Prior profile02/transports/outputs and numeric/admission state preserved','PASS_NO_ACTIVE_CHANGE'),
            ('R12','Same actor, no actual anchors/identities/image/custody or resource acceptance','PASS_PROVENANCE_AND_NONADMISSION_DISCLOSURE')]],
        evidence=[pin(SPEC,'/rules'),pin(SPEC,'/record_order'),pin(PACK,'/$defs/custody_signed_core'),pin(PACK,'/$defs/acceptance_record')],
        clarifications=['The three bundle approvals sign the common core and therefore its nested acceptance/C digest; acceptance_record itself has no standalone signature. No early independent acceptance is inferred from a future bundle.',
            'Schemas are typed indices. Genuine proof bodies, competent acceptance, alias uniqueness, key purposes, record hashes, time/currentness and cross-record equality remain semantic conditions; hashes/shape alone establish none.',
            'Per-record serialized caps must be enforced in addition to schema/codec. Placeholder widths are not actual evidence-fit tests; underlying proof bodies and per-attempt verification costs are not covered by the221644 index bound.'],
        verdict=rec['verdict'],current_effect=spec['current_effect'],decision=spec['decision'],E06=spec['E06'],remaining_work=spec['remaining_work'],
        work_unit=dict(rollback_files=sorted(FILES),verification_command='python3 docs/validation/D5-I192-audit.py',expected_result='PASS_STATIC_SOURCE_ONLY',
            runtime_harness='N/A: documentary custody review; no product/component/crypto/image build/identity or protocol service execution.',over400_lines=True,
            reason='Traceable schema/evidence/signature-coverage/projection and conditional byte-bound reconstruction with review/integrity records; overage reported.'),
        publication=dict(commit_and_push_requested=True,publication_not_adoption_enrollment_or_authority=True))


def main():
    rec=reconstruct();assert rd(RECON)==rec and rd(REVIEW)==build_review(rec)
    prior=rd(PRIOR_SEAL);preserved={**prior['preserved_published442'],**prior['artifacts'],PRIOR_SEAL:sha(PRIOR_SEAL)}
    assert len(preserved)==448
    seal=rd(SEAL);assert seal['schema']=='d5.i192-integrity.v1' and seal['base_commit']==BASE
    assert seal['preserved_published448']==preserved and set(seal['artifacts'])==FILES-{SEAL}
    for pins in [preserved,seal['artifacts']]:
        for p,h in pins.items():assert sha(p)==h,p
    assert seal['source_only'] and seal['resource_obligations_closed']==0 and seal['IR03']=='NOT_READY'
    for k in ['independent_acceptance','product_or_components_executed','quotas_changed','rebind_applied','proposal_enabled','D5_closed']:assert seal[k] is False
    changed=set(git('diff',BASE,'--name-only').splitlines())|set(git('ls-files','--others','--exclude-standard').splitlines());assert changed==FILES,changed
    subprocess.check_call(['git','merge-base','--is-ancestor',BASE,'HEAD'],cwd=ROOT)
    if git('rev-parse','HEAD')!=BASE:assert not git('status','--porcelain')
    print(json.dumps(dict(status='PASS_STATIC_SOURCE_ONLY',increment='I192',new_blocking_documentary_findings=0,documentary_contract_consistent=True,
        historical_pins=756,prior_published_files_preserved=448,new_files=5,conditional_bundle_bytes=221644,adopted=False,implemented=False,
        independent_acceptance=False,actual_actors_caller_or_image_supplied=False,product_or_components_executed=0,quotas_changed=False,
        rebind_applied=False,resource_obligations_closed=0,proposal_enabled=False,F179_01_resolved=False,D5_closed=False,IR03='NOT_READY',git_head=git('rev-parse','HEAD')),sort_keys=True))

if __name__=='__main__':main()
