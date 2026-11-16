#!/usr/bin/env python3
"""I187 documentary schema/AST/wire-bound audit only; never import target or execute product/components/crypto."""
import ast
import copy
import hashlib
import io
import json
import re
import runpy
import subprocess
from pathlib import Path

ROOT=Path(__file__).resolve().parents[2];P='docs/validation/'
BASE='ade0fa496cba1507155c177daae4ae84af41b975'
PACK=P+'D5-I187-CONTEXT-LAUNCH-SCHEMAS-CANDIDATE.json'
SPEC=P+'D5-I187-CONTEXT-LAUNCH-CONTRACT-CANDIDATE.json'
PREP=P+'D5-I187-preparation-review.json';AUDIT=P+'D5-I187-audit.py';SEAL=P+'D5-I187-integrity.json'
DOC='docs/design/D5-I187-CONTEXT-LAUNCH-SCHEMAS-CANDIDATE.md'
FILES={PACK,SPEC,PREP,AUDIT,SEAL,DOC}
PRIOR_SEAL=P+'D5-I186-integrity.json'

def rd(p):return json.loads((ROOT/p).read_text())
def sha(p):return hashlib.sha256((ROOT/p).read_bytes()).hexdigest()
def git(*args):return subprocess.check_output(['git',*args],cwd=ROOT,text=True).strip()
def encoded(v):return json.dumps(v,ensure_ascii=False,sort_keys=True,separators=(',',':'),allow_nan=False).encode('ascii')


def children(s):
    for key in ['properties','$defs']:
        yield from s.get(key,{}).values()
    for key in ['oneOf','anyOf']:
        yield from s.get(key,[])
    for key in ['items','propertyNames','additionalProperties']:
        if type(s.get(key)) is dict:yield s[key]


def check_shape(s,defs,active=None):
    active=set() if active is None else active
    allowed={'$schema','$id','title','$ref','$defs','type','const','enum','properties','required','additionalProperties',
             'propertyNames','minProperties','maxProperties','items','minItems','maxItems','oneOf','anyOf','minimum','maximum','minLength','maxLength','pattern'}
    assert not set(s)-allowed
    if '$ref' in s:
        assert s['$ref'].startswith('#/$defs/')
        name=s['$ref'][8:];assert name in defs and name not in active
        check_shape(defs[name],defs,active|{name})
    if s.get('type')=='object':
        if 'properties' in s:
            assert set(s['required'])==set(s['properties']) and s['additionalProperties'] is False
        else:assert 0<=s['minProperties']<=s['maxProperties']<=4096 and type(s['additionalProperties']) is dict
    if s.get('type')=='integer':assert 0<=s['minimum']<=s['maximum']<=9007199254740991
    if s.get('type')=='string':
        assert 0<s['minLength']<=s['maxLength']<=4096;re.compile(s['pattern'])
    if s.get('type')=='array':assert 0<=s['minItems']<=s['maxItems']<=4096
    for sub in children(s):check_shape(sub,defs,active)


def wire_upper(s,defs):
    """Conservative structural byte bound on restricted printable-ASCII JCS; no runtime or schedule."""
    if '$ref' in s:return wire_upper(defs[s['$ref'][8:]],defs)
    if 'const' in s:return len(encoded(s['const']))
    if 'enum' in s:return max(len(encoded(v)) for v in s['enum'])
    for key in ['oneOf','anyOf']:
        if key in s:return max(wire_upper(q,defs) for q in s[key])
    t=s['type']
    if t=='string':return 2+2*s['maxLength'] # every printable ASCII character needs at most2 bytes
    if t=='integer':return len(str(s['maximum']))
    if t=='array':
        n=s['maxItems'];return 2+n*wire_upper(s['items'],defs)+max(0,n-1)
    if t=='object':
        if 'properties' in s:
            props=s['properties'];return 2+sum(len(encoded(k))+1+wire_upper(v,defs) for k,v in props.items())+max(0,len(props)-1)
        n=s['maxProperties'];return 2+n*(wire_upper(s['propertyNames'],defs)+1+wire_upper(s['additionalProperties'],defs))+max(0,n-1)
    raise AssertionError(t)


def placeholder(s,defs):
    if '$ref' in s:return placeholder(defs[s['$ref'][8:]],defs)
    if 'const' in s:return copy.deepcopy(s['const'])
    if 'enum' in s:return copy.deepcopy(s['enum'][0])
    for key in ['oneOf','anyOf']:
        if key in s:return placeholder(s[key][0],defs)
    t=s['type']
    if t=='object':
        if 'properties' in s:return {k:placeholder(v,defs) for k,v in s['properties'].items()}
        n=s['minProperties']
        if n==0:return {}
        branches=s['propertyNames']['anyOf']
        names=defs['historical_path']['enum']+branches[1]['enum'];assert len(names)==n
        return {p:'0'*64 for p in names}
    if t=='array':return [placeholder(s['items'],defs) for _ in range(s['minItems'])]
    if t=='integer':return s['minimum']
    if t=='string':
        if s['pattern'].startswith('^[0-9a-f]{8}') :return '00000000-0000-0000-0000-000000000000'
        return '0'*s['minLength']
    raise AssertionError(t)


def history(spec):
    pins=spec['input_pins'];assert len(pins)==728
    request=''.join(BASE+':'+p+'\n' for p in sorted(pins)).encode()
    stream=io.BytesIO(subprocess.check_output(['git','cat-file','--batch'],cwd=ROOT,input=request))
    for p,h in sorted(pins.items()):
        header=stream.readline().decode().split();assert len(header)==3 and header[1]=='blob',p
        body=stream.read(int(header[2]));assert stream.read(1)==b'\n'
        assert hashlib.sha256(body).hexdigest()==h==sha(p),p
    old=runpy.run_path(str(ROOT/(P+'D5-I186-audit.py')));r=old['reconstruct']()
    assert rd(old['RECON'])==r and rd(old['REVIEW'])==old['build_review'](r)
    prior=rd(PRIOR_SEAL);preserved={**prior['preserved_published415'],**prior['artifacts'],PRIOR_SEAL:sha(PRIOR_SEAL)}
    assert len(preserved)==420
    for p,h in preserved.items():assert sha(p)==h,p
    return preserved


def build_review():
    spec=rd(SPEC);preserved=history(spec);pack=rd(PACK);defs=pack['$defs']
    assert spec['base_commit']==BASE and spec['schema_pack']['sha256']==sha(PACK)
    assert pack['$ref']=='#/$defs/final_record'
    assert defs['context_record']==defs['launch_record']=={'$ref':'#/$defs/final_record'}
    check_shape(pack,defs);assert len(defs)==55
    assert [r['id'] for r in spec['rules']]==['O%02d'%i for i in range(1,14)]
    oldpack=rd(spec['protocol_pack_binding']['path']);oldprofile=rd(spec['profile_binding']['path'])
    assert sha(spec['protocol_pack_binding']['path'])==spec['protocol_pack_binding']['sha256']
    assert sha(spec['profile_binding']['path'])==spec['profile_binding']['sha256']
    for n in ['sha256','identity','worker_invocation','worker_ready','parent_release','capture_binding']:
        assert defs[n]==oldpack['$defs'][n]
    assert oldprofile['profile_id']==spec['profile_id']=='PGO181-TRUST-ED25519-JCS-CANDIDATE-02'
    numeric=rd(P+'D5-I122-CAPACITY-CONTRACT.json')['numeric_candidates']
    assert spec['unchanged_numeric_candidates']==numeric
    limits={k:numeric[k] for k in ['context_bytes','launch_bytes','package_bytes']}
    maximums={b['record_kind']:wire_upper(defs[b['definition']],defs) for b in spec['branches']}
    assert len(maximums)==7
    assert max(maximums.values())<=min(limits['context_bytes'],limits['launch_bytes'])
    assert maximums['BUDGET_FALLBACK']<=8192 and wire_upper(defs['no_pair_diagnostic'],defs)<=8192
    assert 32*numeric['page_bytes']+numeric['raw_bytes']+numeric['index_sidecar_bytes']+2*numeric['context_bytes']+4096==limits['package_bytes']
    # Documentary parser/evaluator only, never a target component or crypto implementation.
    m=runpy.run_path(str(ROOT/(P+'D5-I183-audit.py')))
    branch_rows=[];negative_count=0
    for row in spec['branches']:
        name=row['definition'];s=defs[name];w=placeholder(s,defs)
        m['domain'](w);m['validate'](s,w,defs);assert m['strict_body'](encoded(w))==w
        assert sum(m['accepts'](defs[q['definition']],w,defs) for q in spec['branches'])==1
        assert w['profile_id']==spec['profile_id'] and w['closure'] is False and w['D5_closed'] is False and w['publication_authorized'] is False
        for key in s['required']:
            bad=copy.deepcopy(w);del bad[key];m['rejected'](lambda:m['validate'](s,bad,defs));negative_count+=1
        bad=copy.deepcopy(w);bad['legacy_extra_field']=True;m['rejected'](lambda:m['validate'](s,bad,defs));negative_count+=1
        bad=copy.deepcopy(w);bad['capture_binding']['root_sha256']='not-a-hash';m['rejected'](lambda:m['validate'](s,bad,defs));negative_count+=1
        branch_rows.append(dict(record_kind=row['record_kind'],schema_unique=True,all_required_keys_checked=len(s['required']),wire_upper_bytes=maximums[row['record_kind']],placeholder_only=True))
    for value in [-1,None,0,{'sign':'NEGATIVE','magnitude':0},{'sign':'NONNEGATIVE','magnitude':2147483648}]:
        m['rejected'](lambda:m['validate'](defs['exit_code'],value,defs));negative_count+=1
    for value in [{'sign':'NEGATIVE','magnitude':9},{'sign':'NONNEGATIVE','magnitude':0}]:m['validate'](defs['exit_code'],value,defs)
    legacy=dict(scope='P01',capture_status='INVALID_CAPTURE',error_code='CONTEXT_BUDGET',closure=False)
    assert not any(m['accepts'](defs[q['definition']],legacy,defs) for q in spec['branches'])
    fallback=defs['record_budget_fallback']['properties'];assert 'capture_binding' in fallback and 'owner' in fallback
    assert fallback['capture_status']=={'const':'INVALID_CAPTURE'}
    omitted=set(fallback['details']['properties']['omitted_sections']['const'])
    assert omitted==set(defs['record_invalid']['properties']['details']['properties'])-{'parent_error'}
    assert 'parent_error' in fallback['details']['properties'] and 'worker_diagnostic' in fallback['details']['properties']
    assert defs['record_trace']['properties']['details']['properties']['worker']=={'$ref':'#/$defs/successful_worker'}
    assert defs['completed_reader_receipt']['properties']['completed_phases']=={'const':['BEFORE','AFTER','FINISH']}
    assert defs['completed_reader_receipt']['properties']['input_paths']=={'const':496}
    assert defs['timed_out_worker']['properties']['wait_outcome']=={'const':'WAIT_RETURNED_FALSE'}
    assert defs['no_pair_diagnostic']['properties']['schema']['const']!='d5.prp181-context-launch.v3'
    anchors=[];legacy_fields=set()
    for a in spec['source_anchors']:
        assert sha(a['path'])==a['sha256']
        tree=ast.parse((ROOT/a['path']).read_text());n=next(n for n in tree.body if isinstance(n,ast.FunctionDef) and n.name==a['symbol'])
        assert (n.lineno,n.end_lineno)==(a['line'],a['end_line'])
        assert hashlib.sha256(ast.dump(n,include_attributes=False).encode()).hexdigest()==a['AST_sha256']
        anchors.append(a)
        if a['symbol']=='launch':
            for q in ast.walk(n):
                if isinstance(q,ast.Subscript) and isinstance(q.ctx,ast.Store) and isinstance(q.value,ast.Name) and q.value.id=='context' and isinstance(q.slice,ast.Constant):legacy_fields.add(q.slice.value)
                if isinstance(q,ast.Assign) and any(isinstance(t,ast.Name) and t.id=='context' for t in q.targets) and isinstance(q.value,ast.Call) and isinstance(q.value.func,ast.Name) and q.value.func.id=='dict':legacy_fields.update(k.arg for k in q.value.keywords)
    projected={k for group in spec['legacy_projection'] for k in group.split(',')}
    assert legacy_fields==projected,(legacy_fields-projected,projected-legacy_fields)
    assert len(anchors)==6
    for path in spec['output_locations'].values():
        if isinstance(path,str):assert not (ROOT/path).exists()
    for s in oldprofile['scope']['future_slots']:assert not (ROOT/s['path']).exists()
    assert spec['decision']==oldprofile['decision'] and spec['E06']==oldprofile['E06']
    assert set(spec['work_unit']['rollback_files'])==FILES
    return dict(schema='d5.i187-preparation-review.v1',increment='I187',date='2026-11-16',base_commit=BASE,
        status='COMPLETE_CONTEXT_LAUNCH_CONTRACT_PREPARED_NOT_ADOPTED_NOT_IMPLEMENTED_NOT_ADMITTED',
        schema_pack=dict(path=PACK,sha256=sha(PACK)),contract=dict(path=SPEC,sha256=sha(SPEC)),
        input_pins=728,prior_published_files_preserved=len(preserved),definitions=55,branches=branch_rows,
        structural_wire_bound=dict(method='Acyclic restricted-ASCII JCS schema recurrence; fixed literal/enum bytes,2*maxLength+2 per variable string, max cardinality maps/arrays and union maximum. No sampling or target execution.',
            all_full_branches_upper_bytes=max(maximums.values()),per_branch_upper_bytes=maximums,
            fallback_upper_bytes=maximums['BUDGET_FALLBACK'],no_pair_diagnostic_upper_bytes=wire_upper(defs['no_pair_diagnostic'],defs),
            context_and_launch_cap_each=12582912,unchanged_package_cap=140513280,
            wire_only_not_transient_heap_CPU_actual_IO_or_output_fit=True),
        negative_structural_cases=negative_count,legacy_fields_covered=sorted(legacy_fields),source_anchors=anchors,
        binding_preserved_in_every_record_and_fallback=True,identical_pair_and_partial_write_rejection_required=True,
        pre_admission_no_persistent_pair=True,actual_output_records_created=False,
        provenance=dict(preparer='Same Codex assistant/chat; not an independent acceptor',actor_independent=False,organizationally_independent=False,independent_acceptance=False),
        current_effect=spec['current_effect'],decision=spec['decision'],E06=spec['E06'],remaining_work=spec['remaining_work'],work_unit=spec['work_unit'])


def main():
    review=build_review();assert rd(PREP)==review
    prior=rd(PRIOR_SEAL);preserved={**prior['preserved_published415'],**prior['artifacts'],PRIOR_SEAL:sha(PRIOR_SEAL)}
    seal=rd(SEAL);assert seal['schema']=='d5.i187-integrity.v1' and seal['base_commit']==BASE
    assert seal['preserved_published420']==preserved and set(seal['artifacts'])==FILES-{SEAL}
    for p,h in seal['artifacts'].items():assert sha(p)==h,p
    assert seal['source_only'] and seal['resource_obligations_closed']==0 and seal['IR03']=='NOT_READY'
    for key in ['independent_acceptance','product_or_components_executed','quotas_changed','rebind_applied','proposal_enabled','D5_closed']:assert seal[key] is False
    changed=set(git('diff',BASE,'--name-only').splitlines())|set(git('ls-files','--others','--exclude-standard').splitlines())
    assert changed==FILES,changed
    subprocess.check_call(['git','merge-base','--is-ancestor',BASE,'HEAD'],cwd=ROOT)
    if git('rev-parse','HEAD')!=BASE:assert not git('status','--porcelain')
    print(json.dumps(dict(status='PASS_STATIC_SOURCE_ONLY',increment='I187',output_branches=7,definitions=55,historical_pins=728,
        prior_published_files_preserved=420,new_files=6,wire_upper_bytes=review['structural_wire_bound']['all_full_branches_upper_bytes'],
        actual_output_fit_verified=False,adopted=False,implemented=False,product_or_components_executed=0,quotas_changed=False,
        rebind_applied=False,resource_obligations_closed=0,proposal_enabled=False,F179_01_resolved=False,D5_closed=False,IR03='NOT_READY',git_head=git('rev-parse','HEAD')),sort_keys=True))

if __name__=='__main__':main()
