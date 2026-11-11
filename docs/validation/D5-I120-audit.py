#!/usr/bin/env python3
"""I120 read-only documentary checks: AST/JSON/hash/length arithmetic only.

Never imports, compiles or executes product/candidates/components. PASS checks
source-review records, not a functional result or an admission authorization.
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
M={}
def rd(path):return json.loads((ROOT/path).read_text())
def sha(path):return hashlib.sha256((ROOT/path).read_bytes()).hexdigest()
def enc(x):return json.dumps(x,ensure_ascii=False,allow_nan=False,separators=(',',':')).encode()
def git(*args):return subprocess.check_output(['git',*args],cwd=ROOT,text=True).strip()
def asthash(n):return hashlib.sha256(ast.dump(n,include_attributes=False).encode()).hexdigest()
def symbol(path,name):
    ns=ast.parse((ROOT/path).read_text()).body
    for part in name.split('.'):
        n=next(n for n in ns if isinstance(n,(ast.FunctionDef,ast.ClassDef)) and n.name==part);ns=n.body
    return n

def measure(s):
    k = s['kind']
    if k == 'ref':
        return measure(M[s['name']])
    if k in ('primitive', 'safe-string', 'integer'):
        if k == 'primitive':
            n = s['string_chars']
            d = max(6 + 12 * n, 4 + s['integer_decimal_digits'], 13)
            a = max(2 + 12 * n, s['integer_decimal_digits'], 5)
            u = max(2 + 4 * n, s['integer_decimal_digits'], 5)
        elif k == 'safe-string':
            n = s['JSON_unescaped_ASCII_chars']
            d = 6 + n
            a = u = 2 + n
        else:
            d = 4 + s['digits']
            a = u = s['digits']
        return dict(digest=d, JSON_ASCII=a, JSON_UTF8=u, depth=0)
    if k == 'literal':
        a = len(json.dumps(s['value'], ensure_ascii=True, separators=(',', ':')).encode())
        u = len(enc(s['value']))
        return dict(digest=len(type(s['value']).__name__) + 1 + a, JSON_ASCII=a, JSON_UTF8=u, depth=0)
    if k == 'object':
        rows = [(measure(dict(kind='literal', value=key)), measure(v)) for key, v in s['fields'].items()]
        n = len(rows)
        return dict(digest=6 + sum((a['digest'] + b['digest'] for a, b in rows)), JSON_ASCII=2 + sum((a['JSON_ASCII'] + 1 + b['JSON_ASCII'] for a, b in rows)) + max(0, n - 1), JSON_UTF8=2 + sum((a['JSON_UTF8'] + 1 + b['JSON_UTF8'] for a, b in rows)) + max(0, n - 1), depth=1 + max((b['depth'] for a, b in rows), default=-1))
    if k in ('map', 'list'):
        n = s['count']
        v = measure(s['item'])
        if k == 'map':
            a = measure(s['key'])
            return dict(digest=6 + n * (a['digest'] + v['digest']), JSON_ASCII=2 + n * (a['JSON_ASCII'] + 1 + v['JSON_ASCII']) + max(0, n - 1), JSON_UTF8=2 + n * (a['JSON_UTF8'] + 1 + v['JSON_UTF8']) + max(0, n - 1), depth=1 + v['depth'])
        return dict(digest=6 + n * v['digest'], JSON_ASCII=2 + n * v['JSON_ASCII'] + max(0, n - 1), JSON_UTF8=2 + n * v['JSON_UTF8'] + max(0, n - 1), depth=1 + v['depth'])
    if k == 'augmented':
        out = measure(s['base'])
        for e in s['additions']:
            x = measure(e['item'])
            n = e['count']
            out['digest'] += n * x['digest']
            for key in ('JSON_ASCII', 'JSON_UTF8'):
                out[key] += n * (x[key] + 3)
            out['depth'] = max(out['depth'], e['depth_offset'] + x['depth'])
        return out
    raise AssertionError(k)

def main():
    global M
    d=rd(P+'D5-I120-unit-operand-source-proof.json');b=rd(P+'D5-I120-binding-supplement.json');g=rd(P+'D5-I120-gate-disposition.json');seal=rd(P+'D5-I120-integrity.json')
    assert git('rev-parse','HEAD')==d['base_commit']==b['base_commit']==seal['base_commit']=='50c49678568bae2abeefbe5fec0285f26c628283'
    assert not git('diff','--name-only') and not git('diff','--cached','--name-only')
    assert len(seal['prior_untracked60'])==60
    for p,h in seal['prior_untracked60'].items():assert sha(p)==h,p
    for p,h in seal['artifacts'].items():assert sha(p)==h,p
    assert P+'D5-I120-integrity.json' not in seal['artifacts']
    expected=set(seal['prior_untracked60'])|set(seal['artifacts'])|{P+'D5-I120-integrity.json'}
    assert set(git('ls-files','--others','--exclude-standard').splitlines())==expected
    # Preserve the complete prior I119 proof/source state, not just its labels.
    priorseal=rd(P+'D5-I119-integrity.json')
    for mapping in (priorseal['artifacts'],priorseal['prior_untracked45'],priorseal['inherited_inputs477']):
        for p,h in mapping.items():assert sha(p)==h,p
    for p,info in d['source_anchors'].items():assert sha(p)==info['sha256'] and (ROOT/p).stat().st_size==info['bytes'],p
    assert sha(d['predecessor']['path'])==d['predecessor']['sha256']
    old=rd(d['predecessor']['path']);M=d['definitions']
    assert os.pathconf('/', 'PC_PATH_MAX')==4096
    assert hashlib.sha256(Path('/usr/include/linux/limits.h').read_bytes()).hexdigest()==old['typed_path_proof']['linux_header_sha256']
    assert M['batch_source_row']['fields']['claims']['fields'].keys()=={'status','verified'}
    for name,s in M.items():
        n=measure(s);assert n==d['definition_sizes'][name],name
        assert n['digest']<16777216 and n['depth']<=32,name
    assert d['definition_sizes']['batch_root']['digest']==14096422
    assert M['batch_data']['additions'][0]['count']==640
    assert M['batch_data']['additions'][1]['count']==M['batch_data']['additions'][2]['count']==1120
    assert d['definition_sizes']['RB01_asserted_raw_source']['JSON_ASCII']+4<65536
    assert d['definition_sizes']['eligibility_facts']['digest']==4250363
    assert d['definition_sizes']['comparison']['digest']==1799459
    assert d['auxiliary_limits']['set128_digest_upper']==5+128*(8+d['definition_sizes']['scalar']['digest']+64+len(str(d['definition_sizes']['scalar']['digest'])))
    assert d['auxiliary_limits']['bytes_digest_upper']==65536+6+5+1
    # Check whole-producer key coverage from the pinned AST. Optional/majorant
    # fields are allowed; missing original emitted fields are not.
    def dictkeys(call):
        assert isinstance(call,ast.Call) and isinstance(call.func,ast.Name) and call.func.id=='dict'
        return {kw.arg for kw in call.keywords if kw.arg is not None}
    element=symbol('source_ingest/batch_fixture.py','element');ret=next(n for n in element.body if isinstance(n,ast.Return))
    assert dictkeys(ret.value)==set(M['batch_source_row']['fields'])
    view=symbol('source_ingest/plane_fixture.py','ReconciliationLab._view');ret=next(n for n in view.body if isinstance(n,ast.Return))
    assert dictkeys(ret.value)==set(M['plane_command']['fields'])
    facts=symbol('source_ingest/eligibility_fixture.py','EligibilityLab.inspect_facts')
    dc=next(n for n in ast.walk(facts) if isinstance(n,ast.Call) and isinstance(n.func,ast.Name) and n.func.id=='dict')
    assert dictkeys(dc)==set(M['eligibility_facts']['fields'])
    obs=symbol('source_ingest/eligibility_fixture.py','observation');ret=next(n for n in obs.body if isinstance(n,ast.Return))
    assert dictkeys(ret.value)==set(M['observation']['fields'])
    inspectfn=symbol('source_ingest/batch_fixture.py','BatchLab.inspect');assert '_sources' not in ast.unparse(inspectfn) and '_manifests' not in ast.unparse(inspectfn)
    tree=ast.parse((ROOT/'source_ingest/batch_fixture.py').read_text())
    assignments={n.targets[0].id:n.value for n in tree.body if isinstance(n,ast.Assign) and isinstance(n.targets[0],ast.Name)}
    assert ast.literal_eval(assignments['DEPENDENCIES'])==('HARD','SOFT','MOCKABLE','OPTIONAL')
    for key,val in [('MAX_ELEMENTS',32),('MAX_DECLARATIONS',64),('MAX_ENTITIES',128),('MAX_RELATIONS',256),('MAX_COMMANDS',128)]:assert ast.literal_eval(assignments[key])==val
    # Domain numbers used by the correlated derivation, not new quotas.
    assert 5*32==160 and 5*64==320 and 2*320==640 and 160+3*320==1120
    assert 4*32==128 and 4*64==256
    # Reconstruct every successful outer assertion slot and its helper closure
    # membership from the predecessor census and original source AST.
    pending={i:r for i,r in enumerate(old['assertion_root_census']['rows']) if r['value_closure']=='OPEN_PER_SLOT_SOURCE_FOOTPRINT_PROOF'}
    assert len(pending)==len(d['rows'])==179
    assert {r['I119_census_index'] for r in d['rows']}==set(pending)
    seen=set();counts=Counter();cache={}
    for row in d['rows']:
        original=pending[row['I119_census_index']];group=original['test_id'].split('.')[0];counts[group]+=1
        path=original['path'];cls=original['symbol'].split('.')[0]
        if (path,cls) not in cache:cache[path,cls]={n.name:n for n in symbol(path,cls).body if isinstance(n,ast.FunctionDef)}
        methods=cache[path,cls];expected_sites=[];used_calls=set()
        for site in original['assertion_sites']:
            if site['expected_exception_arguments_not_digested']:continue
            call=next(n for n in ast.walk(methods[site['owner']]) if isinstance(n,ast.Call) and id(n) not in used_calls and n.lineno==site['line'] and asthash(n)==site['operand_AST_sha256'])
            used_calls.add(id(call))
            one=site['helper'] in ('assertTrue','assertFalse','assertIsNone','assertIsNotNone')
            assert not call.keywords and not any(isinstance(n,ast.Starred) for n in call.args)
            vals=[ast.unparse(n) for n in call.args[:1 if one else 2]]
            expected_sites.append([d['assertion_site_sources'].index(path),site['owner'],site['line'],call.col_offset,site['helper'],vals])
        assert [d['assertion_site_catalog'][i] for i in row['sites']]==expected_sites,original['test_id']
        seen.update(row['sites'])
    assert len(seen)==len(d['assertion_site_catalog'])==498
    assert sum(len(s[5]) for s in d['assertion_site_catalog'])==934
    assert dict(counts)==d['group_counts']=={'test_register_comparison':16,'test_register_compat':11,'test_offline_integration':35,'test_profiles_quotas':38,'test_plane_reconciliation':41,'test_relational_batch':38}
    for group,names in d['families'].items():
        upper=max([d['definition_sizes'][n]['digest'] for n in names]+[v for k,v in d['auxiliary_limits'].items() if k!='maximum_depth'])
        assert upper==d['family_digest_upper'][group]<16777216
    assert max(d['family_digest_upper'].values())==14096422
    assert max(old['resource_results']['max_reviewed_positive_digest_or_combined'],max(d['family_digest_upper'].values()))==14890036
    assert 16777216-14890036==1887180
    assert all(d[k] is False for k in ('product_or_component_executed','product_or_runner_imported','candidate_imported_or_compiled','quota_changed','existing_files_changed','proposal_enabled','CP07_recertified','correlated_atomicity_verified','D5_closed','closure'))
    assert d['global_CP03_resolved'] is True and d['unit_roots_resolved']==179 and d['unit_roots_remaining']==0
    # Exact logical replacements; verify snapshot bytes without applying them.
    mapping=b['proposed_replacements'];replacements={p:rd(info['snapshot']) for p,info in mapping.items()}
    for p,info in mapping.items():
        assert sha(info['snapshot'])==info['sha256'] and (ROOT/info['snapshot']).stat().st_size==info['bytes']
        assert sha(p)==info['predecessor_sha256']
        assert (ROOT/info['snapshot']).read_bytes()==enc(replacements[p])+b'\n'
    C=P+'D5-JOINT-CAPACITY-CONTRACT.json';R=P+'D5-JOINT-CAPTURE-REGISTRY.json';K=P+'D5-JOINT-CAPACITY-CERTIFICATE.json';T=P+'D5-JOINT-COMPONENTS-MANIFEST.json'
    contract,reg,cert,manifest=[replacements[p] for p in (C,R,K,T)]
    h=lambda p:mapping[p]['sha256'] if p in mapping else sha(p)
    sz=lambda p:mapping[p]['bytes'] if p in mapping else (ROOT/p).stat().st_size
    assert reg['contract_sha256']==h(C)
    assert contract['operand_proof']['global_CP03_resolved'] is True and contract['operand_proof']['sha256']==sha(P+'D5-I120-unit-operand-source-proof.json')
    for pins in (reg['implementation_sources'],reg['required_prior_inputs'],cert['source_bindings'],manifest['source_bindings'],b['proposed_logical_source_bindings']):
        for p,value in pins.items():assert h(p)==value,p
    known=set(reg['required_prior_inputs'])|set(reg['implementation_sources'])|{C,R,K,T}
    assert known==set(b['proposed_logical_source_bindings']) and len(known)==488
    assert len(reg['required_prior_inputs'])==479 and len(cert['source_bindings'])==486 and len(manifest['source_bindings'])==8
    assert set(cert['source_bindings'])==set(reg['required_prior_inputs'])|set(reg['implementation_sources'])|{C,R}
    assert set(manifest['source_bindings'])==set(reg['implementation_sources'])|{C,R,K}
    assert manifest['status']=='NOT_RUN_SOURCE_ONLY' and manifest['expected_tests']==10
    assert cert['status']=='DRAFT_NOT_ADMITTED' and cert['CP03_global_resolved'] is True
    assert cert['original_source_envelopes']['I120_unit_max']==14096422
    assert all(cert[k] is False for k in ('CP07_exact_admission_resolved','correlated_atomicity_verified','proposal_enabled','quota_values_applied','D5_closed','closure'))
    assert reg['limits']==rd(R)['limits']==contract['numeric_candidates']==rd(C)['numeric_candidates']
    assert reg['implementation_sources']==b['candidate_source_hashes']==rd(R)['implementation_sources']
    U=sum(sz(p) for p in known);schedule=b['read_schedule'];fs=b['future_metadata_size_upper']
    # The existing closed metadata schema is unchanged. Only one authority
    # capture-input name/hash entry grows, with no new self pin.
    prev=rd(P+'D5-I119-CP07-binding-review.json');added=P+'D5-I120-unit-operand-source-proof.json'
    prior=prev['exact_closed_future_metadata_sizes_including_optional_newline'];auth=P+'D5-JOINT-capture-authorization.json'
    assert fs[auth]==prior[auth]+len(enc(added))+1+len(enc('f'*64))+1
    for p in fs:
        if p!=auth:assert fs[p]==prior[p]
    F=sum(fs.values());read=3*(U+F)+4852460
    assert U==b['known_union_bytes']==87788211 and F==56876
    assert U<=87795000 and F<=57000
    assert read==schedule['worker_upper']==268387721
    assert schedule['worker_margin']==268435456-read==47735
    assert 3*(87795000+57000)+4852460==schedule['conservative_certificate_worker_upper']==268408460<268435456
    assert len(enc(b['top_metadata_model']['value']))==b['top_metadata_model']['encoded_bytes']==482757<=524288
    assert b['future_capture_inputs']==491 and b['union_including_external_authority']==492
    assert b['CP07_proposed_bindings_and_numeric_capacity_verified'] is True and b['CP07_actual_admission'] is False
    assert b['current_candidate_files_unchanged'] is True and b['proposal_enabled'] is False
    assert g['CP03_global_resolved'] is True and g['unit_roots_remaining']==0 and g['proposal_enabled'] is False and g['IR03']=='NOT_READY'
    for name in ('D5-JOINT-capture-authorization.json','D5-JOINT-tests-raw.json','D5-JOINT-results.json','D5-JOINT-integrity.json','D5-JOINT-P01','D5-JOINT-P01-launch.json'):assert not (ROOT/P/name).exists()
    print(json.dumps(dict(status='PASS_DOCUMENTARY_ONLY',source_root_count=179,remaining_unit_roots=0,unique_assertion_sites=498,slot_expressions=934,new_unit_digest_upper=14096422,global_positive_upper=14890036,operand_margin=1887180,CP03_global_resolved=True,CP07_replacement_read_upper=read,CP07_replacement_margin=47735,replacements_applied=False,product_or_components_executed=False,quota_changed=False,proposal_enabled=False,D5_closed=False,IR03='NOT_READY')))

if __name__=='__main__':main()
