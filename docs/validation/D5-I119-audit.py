#!/usr/bin/env python3
"""Read-only I119 documentary audit. No candidate/product import or execution.

PASS means sealed documentary arithmetic/bindings are coherent. CP03 global,
CP07 actual admission, atomicity, components and functional capture stay OPEN.
"""
import ast
import hashlib
import json
import os
import subprocess
from collections import Counter
from pathlib import Path

ROOT=Path(__file__).resolve().parents[2]
P='docs/validation/'

def rd(path):return json.loads((ROOT/path).read_text())
def sha(path):return hashlib.sha256((ROOT/path).read_bytes()).hexdigest()
def enc(x,ascii=False):return json.dumps(x,ensure_ascii=ascii,allow_nan=False,separators=(',',':')).encode()
def git(*args):return subprocess.check_output(['git',*args],cwd=ROOT,text=True).strip()
def sizes(d,a,u,depth):return dict(digest=d,JSON_ASCII=a,JSON_UTF8=u,depth=depth)

def measure(s):
    """Arithmetic on descriptions only: never construct a product value."""
    k=s['kind']
    if k=='literal':
        v=s['value'];assert v is None or type(v) in (str,int,bool)
        return sizes(len(type(v).__name__)+1+len(enc(v,True)),len(enc(v,True)),len(enc(v)),0)
    if k=='string':
        n=s['chars'];a=2+n*(1 if s['alphabet']=='ASCII' else 12);u=2+n*(1 if s['alphabet']=='ASCII' else 4)
        return sizes(4+a,a,u,0)
    if k=='integer':
        n=s['decimal_digits'];return sizes(4+n,n,n,0)
    if k=='one-of':
        rows=[measure(x) for x in s['choices']]
        return {key:max(x[key] for x in rows) for key in ('digest','JSON_ASCII','JSON_UTF8','depth')}
    if k=='object':
        rows=[(measure(dict(kind='literal',value=key)),measure(value)) for key,value in s['fields'].items()];n=len(rows)
        return sizes(6+sum(a['digest']+b['digest'] for a,b in rows),2+sum(a['JSON_ASCII']+1+b['JSON_ASCII'] for a,b in rows)+max(0,n-1),2+sum(a['JSON_UTF8']+1+b['JSON_UTF8'] for a,b in rows)+max(0,n-1),1+max((b['depth'] for a,b in rows),default=-1))
    if k in ('repeat-map','repeat-list'):
        n=s['count'];v=measure(s['item'])
        if k=='repeat-map':
            key=measure(s['key']);return sizes(6+n*(key['digest']+v['digest']),2+n*(key['JSON_ASCII']+1+v['JSON_ASCII'])+max(0,n-1),2+n*(key['JSON_UTF8']+1+v['JSON_UTF8'])+max(0,n-1),1+v['depth'])
        return sizes(6+n*v['digest'],2+n*v['JSON_ASCII']+max(0,n-1),2+n*v['JSON_UTF8']+max(0,n-1),1+v['depth'])
    if k=='forest':
        n=s['primitive_nodes'];c=s['container_nodes'];K=s['string_chars'];a=1 if s['alphabet']=='ASCII' else 12;u=1 if a==1 else 4
        return sizes(n*(6+a*K)+7*c,n*(2+a*K)+2*n+4*c,n*(2+u*K)+2*n+4*c,s['depth_upper'])
    if k=='augmented':
        out=measure(s['base'])
        for e in s['list_additions']:
            n=e['count'];v=measure(e['item']);out['digest']+=n*v['digest']
            for key in ('JSON_ASCII','JSON_UTF8'):out[key]+=n*(v[key]+1)
            out['depth']=max(out['depth'],e['leaf_depth_offset']+v['depth'])
        return out
    raise AssertionError(k)

def final_node(path,symbol):
    nodes=ast.parse((ROOT/path).read_text()).body
    for part in symbol.split('.'):
        n=[n for n in nodes if isinstance(n,(ast.ClassDef,ast.FunctionDef)) and n.name==part][-1];nodes=n.body
    return n

def ast_hash(n):return hashlib.sha256(ast.dump(n,include_attributes=False).encode()).hexdigest()

def future_sizes(r,m,known):
    auth=P+'D5-JOINT-capture-authorization.json';raw=P+'D5-JOINT-tests-raw.json';result=P+'D5-JOINT-results.json';seal=P+'D5-JOINT-integrity.json';manifest=P+'D5-JOINT-COMPONENTS-MANIFEST.json'
    rev=r['source_revision'];pins={p:'f'*64 for p in sorted(set(known)|{raw,result,seal})}
    # Width descriptions, NOT actual evidence; no output files are created.
    models={auth:dict(schema='d5.joint-capture-authority.v2',phase='JOINT_EXPLICITLY_APPROVED',scopes=['P01'],registry_sha256='f'*64,capture_inputs=pins),raw:dict(schema='d5.joint-component-raw.v2',source_revision=rev,status='PASS',tests_run=10,failures=0,errors=0,functional_campaigns_executed=0,product_or_runner_imported=False,forbidden_imports=[],elapsed_milliseconds=300000,new_module_count=9223372036854775807,closure=False,D5_closed=False),result:dict(schema='d5.joint-component-review.v2',source_revision=rev,status='PASS',tests_run=10,functional_campaigns_executed=0,product_or_runner_imported=False,raw_sha256='f'*64,manifest_sha256='f'*64,decision='ACCEPTED_COMPONENTS_ONLY',closure=False,D5_closed=False),seal:dict(schema='d5.joint-component-integrity.v2',source_revision=rev,artifacts={p:'f'*64 for p in (raw,result,manifest)},source_bindings={p:'f'*64 for p in m['source_bindings']})}
    return {p:len(enc(v))+1 for p,v in models.items()}

def main():
    proof=rd(P+'D5-I119-output-operand-envelopes.json');review=rd(P+'D5-I119-CP07-binding-review.json');seal=rd(P+'D5-I119-integrity.json');g=rd(P+'D5-I119-gate-disposition.json')
    assert git('rev-parse','HEAD')==proof['base_commit']==review['base_commit']==seal['base_commit']=='50c49678568bae2abeefbe5fec0285f26c628283'
    assert not git('diff','--name-only') and not git('diff','--cached','--name-only')
    for mapping in (seal['artifacts'],seal['prior_untracked45'],seal['inherited_inputs477'],proof['source_bindings'],review['source_bindings']):
        for p,h in mapping.items():assert sha(p)==h,p
    assert len(seal['prior_untracked45'])==45 and len(seal['inherited_inputs477'])==477
    assert P+'D5-I119-integrity.json' not in seal['artifacts']
    untracked=set(git('ls-files','--others','--exclude-standard').splitlines())
    expected=set(seal['prior_untracked45'])|set(seal['artifacts'])|{P+'D5-I119-integrity.json'}
    assert untracked==expected,(untracked-expected,expected-untracked)
    assert proof['global_CP03_resolved'] is False and proof['all_digests_fit_claimed'] is False and proof['actual_capture_invalid_claimed'] is False
    assert proof['known_I118_negative_preserved'] is True
    for name,row in proof['models'].items():
        assert measure(row['shape'])==row['size'],name
        assert row['size']['digest']<16777216 and row['size']['depth']<=32,name
    assert proof['resource_results']['full_chain_assertion_digest_upper']==14890036
    assert proof['resource_results']['all_Store_request_combined_upper']==13762309
    assert proof['resource_results']['T_client_state_digest_and_JSON_UTF8_upper']==12773503
    assert proof['resource_results']['R_client_state_digest_and_JSON_UTF8_upper']==9783694
    assert proof['resource_results']['remote_state_digest_and_JSON_UTF8_upper']==10917045
    assert proof['resource_results']['headroom_reviewed_positive_families']==1887180
    pathproof=proof['typed_path_proof'];assert os.pathconf('/', 'PC_PATH_MAX')==4096
    assert hashlib.sha256(Path('/usr/include/linux/limits.h').read_bytes()).hexdigest()==pathproof['linux_header_sha256']
    assert pathproof['lexical_charged_bytes_upper']==(4095+70)*3 and pathproof['tuple_projection_bytes_upper']==12915
    census=proof['assertion_root_census'];rows=census['rows'];assert len(rows)==len({r['test_id'] for r in rows})==321
    assert sum(r['causal_inventory'] for r in rows)==118
    pending=Counter()
    for row in rows:
        cls,method=row['symbol'].split('.');nodes=final_node(row['path'],cls);methods={n.name:n for n in nodes.body if isinstance(n,ast.FunctionDef)}
        assert method in methods
        closure=set();todo=[method]+[n for n in ('setUp','tearDown') if n in methods]
        while todo:
            name=todo.pop()
            if name in closure:continue
            closure.add(name)
            for n in ast.walk(methods[name]):
                if isinstance(n,ast.Call) and isinstance(n.func,ast.Attribute) and isinstance(n.func.value,ast.Name) and n.func.value.id=='self' and n.func.attr in methods:todo.append(n.func.attr)
        assert sorted(closure)==row['helper_closure']
        for sink in row['assertion_sites']:
            call=next(n for n in ast.walk(methods[sink['owner']]) if isinstance(n,ast.Call) and n.lineno==sink['line'] and ast_hash(n)==sink['operand_AST_sha256'])
            assert call.func.attr==sink['helper']
        if row['value_closure']=='OPEN_PER_SLOT_SOURCE_FOOTPRINT_PROOF':pending[row['test_id'].split('.')[0]]+=1
    assert dict(pending)=={'test_register_comparison':16,'test_register_compat':11,'test_offline_integration':35,'test_profiles_quotas':38,'test_relational_batch':38,'test_plane_reconciliation':41}
    assert sum(pending.values())==179 and census['unit_value_closed_roots']==24
    small=proof['small_unit_source_proof'];assert measure(small['full_preview_shape'])==small['full_preview_size']
    assert small['SQL_digest_upper']==6+12*small['SQL_chars_upper']==1400742
    for h in proof['unit_footprint_hypotheses_not_admitted']:assert h['premises_verified'] is False and h['status']=='NOT_ADMITTED'
    rp=P+'D5-JOINT-CAPTURE-REGISTRY.json';cp=P+'D5-JOINT-CAPACITY-CONTRACT.json';kp=P+'D5-JOINT-CAPACITY-CERTIFICATE.json';mp=P+'D5-JOINT-COMPONENTS-MANIFEST.json'
    reg=rd(rp);contract=rd(cp);cert=rd(kp);manifest=rd(mp)
    for m in (reg['implementation_sources'],reg['required_prior_inputs'],cert['source_bindings'],manifest['source_bindings']):
        for p,h in m.items():assert sha(p)==h,p
    assert reg['contract_sha256']==sha(cp) and contract['operand_proof']['sha256']==sha(P+'D5-I119-output-operand-envelopes.json')
    assert len(reg['required_prior_inputs'])==478 and len(reg['implementation_sources'])==5
    assert set(cert['source_bindings'])==set(reg['required_prior_inputs'])|set(reg['implementation_sources'])|{rp,cp}
    assert set(manifest['source_bindings'])==set(reg['implementation_sources'])|{rp,cp,kp}
    assert len(cert['source_bindings'])==485 and len(manifest['source_bindings'])==8
    assert cert['status']=='DRAFT_NOT_ADMITTED' and cert['component_validation']=='NOT_RUN'
    assert all(cert[k] is False for k in ('CP03_global_resolved','CP07_exact_admission_resolved','correlated_atomicity_verified','proposal_enabled','product_or_runner_imported','quota_values_applied','closure','D5_closed'))
    assert manifest['status']=='NOT_RUN_SOURCE_ONLY' and manifest['expected_tests']==10
    assert contract['operand_proof']['global_CP03_resolved'] is False
    assert contract['charging']['whole30_site_correlated_atomicity_verified'] is False
    for p in reg['implementation_sources']:
        if p.endswith('.py'):ast.parse((ROOT/p).read_text())
    testclass=final_node('testing/prospective_capture_joint/test_joint_capture.py','R2CandidateTests')
    names=['R2CandidateTests.'+n.name for n in testclass.body if isinstance(n,ast.FunctionDef) and n.name.startswith('test_')]
    assert manifest['tests']==names and len(names)==10
    assert ast.dump(final_node('testing/prospective_capture_joint/worker.py','targets'),include_attributes=False)==ast.dump(final_node('testing/prospective_capture_selectors/worker.py','targets'),include_attributes=False)
    assert ast.dump(final_node('testing/prospective_capture_joint/capture.py','BaseRecorder.bind_causal_target'),include_attributes=False)==ast.dump(final_node('testing/prospective_capture_selectors/capture.py','BaseRecorder.bind_causal_target'),include_attributes=False)
    worker=(ROOT/'testing/prospective_capture_joint/worker.py').read_text();candidate=(ROOT/'testing/prospective_capture_joint/capture.py').read_text()
    assert worker.index('approved=p.authority')<worker.index('module=importlib.import_module')
    assert "cert.get('status')=='SOURCE_CAPACITY_VERIFIED'" in candidate
    assert 'and self.causal_enabled() and self.active' in candidate
    assert 'component_sources=set(reg[\'implementation_sources\'])|{REGISTRY,CONTRACT,CERTIFICATE}' in candidate
    assert 'inputs.joint_plan.after()' in worker and 'inputs.joint_plan.finish()' in worker
    assert 'c.Reader(root)' not in ast.unparse(final_node('testing/prospective_capture_joint/worker.py','exercise'))
    known=set(reg['required_prior_inputs'])|set(reg['implementation_sources'])|{rp,cp,kp,mp}
    assert known==set(review['source_bindings']) and len(known)==487
    U=sum((ROOT/p).stat().st_size for p in known);fs=future_sizes(reg,manifest,known);F=sum(fs.values())
    assert fs==review['exact_closed_future_metadata_sizes_including_optional_newline']
    assert U==review['known_input_union_bytes']==87651290 and F==56752
    assert U<=cert['read_capacity_candidate']['known_input_union_bytes_upper']==87700000 and F<=70000
    read=3*(U+F)+4852460;schedule=review['read_schedule']
    assert schedule['worker_file_bytes_upper']==read==267976586
    assert schedule['worker_headroom_bytes']==268435456-read==458870
    assert 3*(87700000+70000)+4852460==cert['read_capacity_candidate']['worker_total_bytes_upper']==268162460<268435456
    assert len(enc(review['top_metadata_model']['value']))==review['top_metadata_model']['encoded_bytes']==482509<=524288
    assert review['CP07_candidate_sources_exactly_bound'] is True and review['CP07_candidate_numeric_schedule_resolved'] is True
    assert review['CP07_future_exact_binding_resolved'] is False and review['CP07_global_admission_resolved'] is False
    for p in ['D5-JOINT-capture-authorization.json','D5-JOINT-tests-raw.json','D5-JOINT-results.json','D5-JOINT-integrity.json','D5-JOINT-P01','D5-JOINT-P01-launch.json']:assert not (ROOT/P/p).exists(),p
    assert g['proposal_enabled'] is False and g['CP03_global_resolved'] is False and g['CP07_global_admission_resolved'] is False
    assert g['functional_campaigns_executed']==g['candidate_tests_executed']==0 and g['D5_closed'] is False and g['IR03']=='NOT_READY'
    print(json.dumps(dict(status='PASS_DOCUMENTARY_ONLY',sealed_artifacts=len(seal['artifacts']),preserved_prior_untracked=45,verified_inherited_inputs=477,root_census=321,unit_source_closed=24,unit_value_proof_pending=179,candidate_tests='NOT_RUN',worker_read_upper=read,worker_headroom=268435456-read,CP03_global_resolved=False,CP07_current_sources_bound=True,CP07_actual_admission=False,proposal_enabled=False,D5_closed=False,IR03='NOT_READY'),ensure_ascii=False))

if __name__=='__main__':main()
