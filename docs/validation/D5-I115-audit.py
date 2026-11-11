#!/usr/bin/env python3
"""Read-only documentary hashes/AST/arithmetic. No product, runner or test imports.
Does not prove the open byte premises or perform synthetic component validation.
"""
import ast
import hashlib
import json
from pathlib import Path
import re
import subprocess

ROOT=Path(__file__).resolve().parents[2]

def read(path):
    return json.loads((ROOT/path).read_text())

def main():
    assert subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip()=='50c49678568bae2abeefbe5fec0285f26c628283'
    subprocess.run(['git','diff','--quiet'],cwd=ROOT,check=True)
    subprocess.run(['git','diff','--cached','--quiet'],cwd=ROOT,check=True)
    verified={}
    def pins(mapping):
        for p,h in mapping.items():
            name=Path(p)
            assert not name.is_absolute() and '..' not in name.parts and not p.startswith('dev/run_data/'),p
            assert re.fullmatch('[0-9a-f]{64}',h),p
            assert hashlib.sha256((ROOT/p).read_bytes()).hexdigest()==h,p
            assert p not in verified or verified[p]==h,p
            verified[p]=h
    h=read('docs/validation/D5-I113-handoff-integrity.json')
    for k in ('artifacts','preserved_local_artifacts','prior_integrity_seals'):pins(h[k])
    for p in h['prior_integrity_seals']:pins(read(p).get('artifacts',{}))
    pins(read('docs/validation/D5-I114-integrity.json')['artifacts'])
    ref=read('docs/validation/D5-I115-refined-reference-envelope.json')
    byte=read('docs/validation/D5-I115-structural-byte-plan.json')
    prop=read('docs/validation/D5-I115-joint-capacity-proposal.json')
    for d in (ref,byte,prop):
        pins(d['inputs'])
        for k in ('implementation_changed','quota_changed','product_or_runner_imported','functional_profile_created','future_capture_authority_or_destination_created','publication_authorized','D5_closed','H07_closed','closure','numeric_joint_capacity_certificate_created'):
            assert d[k] is False,k
        assert d['new_tests_executed']==d['functional_campaigns_executed']==0
        assert d['IR03']=='NOT_READY'
    coverage=read('docs/validation/D5-I113-global-event-bound-coverage.json')['rows']
    old={r['test_id']:r for r in coverage}
    assert len(old)==len(ref['root_rows'])==ref['root_count']==321
    names={'client_perform_outcome_events':'P','Store_transact_terminal_events':'U','snapshot_call_events':'S','Drive_advance_terminal_events':'D','independent_oracle_terminal_events':'O','protocol_start_receive_finish_terminal_events':'H','Store_construction_events':'C','assertion_and_expected_context_events':'A','lifecycle_and_subtest_result_events':'L','Client_perform_terminal_returns':'P','Store_transact_terminals':'U','snapshot_returns':'S','independent_oracle_terminals':'O','protocol_start_receive_finish_terminals':'H','Store_construction_observations':'C','assertion_returns':'A','lifecycle_and_subtest_results':'L'}
    aggregate={};cats={k:0 for k in 'PUSDOCHAL'};modes={}
    for r in ref['root_rows']:
        tid=r['test_id'];o=old[tid]
        assert r['evidence']==o['evidence'] and r['event_upper']==o['event_upper']
        file,_,ptr=o['evidence'].partition('#');model=read(file)
        for token in ptr.strip('/').split('/') if ptr else []:model=model[token]
        v={k:0 for k in cats};mode=r['mode'];modes[mode]=modes.get(mode,0)+1
        if mode=='T_R':
            assert tid.startswith(('test_durable_integration.','test_durable_relational.'))
            for k,n in model.get('event_component_envelope',model.get('event_kind_vector')).items():v[names.get(k,k)]=n
        elif mode=='DRIVE':
            assert tid.startswith('test_incremental_capture.')
            v.update(model['component_envelope']);v['L']=3
        else:
            assert mode=='ASSERTION_CONTEXT_ONLY'
            v['A']=model['assertion_and_expected_context_events_upper']+model.get('callback_assertion_events_upper',0)
            v['L']=3+model['subtest_outcomes_upper']
        assert v==r['event_vector'] and sum(v.values())==o['event_upper']
        for k,n in v.items():cats[k]+=n
        direct=int('.test_DI07_' in tid);negative=int('.test_DI28_' in tid);race=int('.test_DI14_' in tid)
        k=v['C'] if mode=='T_R' else 2*negative
        returned=v['P']+v['S'];calls=v['P']+v['U']+v['D']+v['O']+v['H'];i=v['O'];p=v['H']+direct
        d=k+returned+v['U'] if mode=='T_R' else 0
        s=1+v['L']-3+(v['A'] if mode=='ASSERTION_CONTEXT_ONLY' else 0)
        w=2*k if mode=='T_R' else 0
        g=min(d,k*s);j=min(d,2*k*s)
        a=4*k+2*p+2 if mode=='T_R' else v['C']+v['H']+2*p+5*direct if mode=='DRIVE' else 0
        m=v['H'] if mode=='T_R' else v['A'] if mode=='DRIVE' else 0
        x=2*v['H'] if mode=='T_R' else 2*v['H']+2*direct+2*race if mode=='DRIVE' else 0
        links=calls+2*i
        assert (r['subcase_upper'],r['groups_upper'],r['witness_membership_upper'])==(s,g,j)
        for key,value in dict(K=k,H=returned,C=calls,I=i,P=p,D=d,W=w,A=a,M=m,X=x,L=links).items():assert r['primitives'][key]==value,(tid,key)
        q={z:0 for z in ref['site_charge_upper']}
        q.update(Q07=a,Q08=v['S'] if mode=='DRIVE' else 0,Q09=2*v['S'] if mode=='DRIVE' else 0,Q10=k if mode=='T_R' else 0,Q11=k if mode=='T_R' else 0,Q12=2*negative,Q13=2*negative,Q14=i,Q15=1+a,Q19=2*s+calls+i+p+direct+g+links,Q20=a,Q23=x,Q24=v['L']-2,Q25=direct,Q26=m,Q27=2*direct,Q28=direct,Q29=2*direct,Q30=2*k if mode=='T_R' else 0,Q31=g,Q32=2*j,Q33=min(j,d),Q34=i*(1+w),Q35=2*v['U'],Q36=i*(1+w),Q37=2*links,Q38=2*i*(1+w))
        assert q==r['site_charge_upper'],tid
        assert sum(q.values())==r['total_without_finalization'],tid
        for site,n in q.items():aggregate[site]=aggregate.get(site,0)+n
    assert modes=={'T_R':88,'DRIVE':30,'ASSERTION_CONTEXT_ONLY':203} or modes=={'ASSERTION_CONTEXT_ONLY':203,'DRIVE':30,'T_R':88}
    for k,n in ref['global_finalize_charges'].items():aggregate[k]+=n
    assert aggregate==ref['site_charge_upper'] and len(aggregate)==30
    assert sum(aggregate.values())==ref['source_global_reference_upper']==442305
    assert cats==ref['normalized_vector_totals']==byte['category_counts'] and sum(cats.values())==30129
    assert ref['owner_origins_upper']==5190 and ref['subcases_upper']==1718
    assert ref['group_keys_upper']==6615 and ref['witness_memberships_upper']==9285
    assert ref['maximum_group_witness_source_upper']==192
    original=read('docs/validation/D5-I96-source-capacity-review.json')['charging_catalog']
    assert set(aggregate)=={q['id'] for q in original if q['active']}
    trees={}
    for a in ref['source_anchors']:
        pins({a['path']:a['sha256']})
        if a['path'] not in trees:trees[a['path']]=ast.parse((ROOT/a['path']).read_text())
        assert any(isinstance(n,(ast.FunctionDef,ast.AsyncFunctionDef)) and (n.name,n.lineno,n.end_lineno)==(a['method'],a['line'],a['end_line']) for n in ast.walk(trees[a['path']])),a
    enc=lambda v:json.dumps(v,ensure_ascii=False,allow_nan=False,separators=(',',':')).encode()
    for model in byte['shape_models'].values():assert len(enc(model['value']))==model['encoded_bytes']<=model['upper']
    chunks=sum(cats[k]*(byte['event_category_bytes'][k]+1) for k in cats)
    pages=chunks//(2097152-256-4097)+1
    assert chunks==65432505 and pages==32
    assert chunks+256*pages==byte['page_packing']['page_bytes_upper']==65440697<67108864
    assert byte['large_event_precondition'].startswith('OPEN_')
    side=sum(x['upper'] for x in byte['sidecar_components'].values())
    assert side==byte['sidecar_structural_total']==35474392
    assert ((side+1048575)//1048576)*1048576==byte['sidecar_candidate_limit']==35651584
    assert byte['sidecar_gate'].startswith('NOT_PROVEN_')
    assert byte['row_byte_warning']['source_row4096_proof'] is False
    assert byte['operand_source_upper'] is byte['raw_source_upper'] is byte['context_source_upper'] is byte['launcher_source_upper'] is None
    assert len(prop['quota_comparison'])==prop['resource_count']==24
    oldlimits={r['resource']:r['current_limit'] for r in read('docs/validation/D5-I114-joint-resource-envelope.json')['resource_rows']}
    assert {r['resource']:r['current'] for r in prop['quota_comparison']}==oldlimits
    changed={r['resource'] for r in prop['quota_comparison'] if r['candidate']!=r['current']}
    assert changed=={'refs','index_sidecar_bytes','package_bytes','evidence_read_bytes'}
    c=prop['candidate_limits']
    assert c['refs']==442305 and c['index_sidecar_bytes']==35651584
    pack=67108864+12582912+c['index_sidecar_bytes']+2*12582912+36
    reads=2*(12582912+c['index_sidecar_bytes'])+3*67108864+36
    unique=12582912+c['index_sidecar_bytes']+67108864+36
    assert pack==prop['joint_package']['upper']==140509220 and c['package_bytes']-pack==4060
    assert reads==prop['joint_evidence_reader']['read_upper']==297795620 and c['evidence_read_bytes']-reads==4060
    assert unique==prop['joint_evidence_reader']['unique_upper']==115343396<134217728
    assert prop['functional_capture_authorized'] is prop['request_for_implementation_approval_now'] is False
    assert [g['status'] for g in prop['gates']]==['OPEN']*7+['NOT_AUTHORIZED']*2
    assert len(prop['synthetic_matrix'])==20 and all(r['status']=='NOT_RUN' for r in prop['synthetic_matrix'])
    assert not (ROOT/'testing/prospective_capture_joint').exists()
    for name in ('docs/validation/D5-JOINT-CAPTURE-REGISTRY.json','docs/validation/D5-JOINT-CAPACITY-CONTRACT.json'):assert not (ROOT/name).exists()
    for link in re.findall(r'\]\(([^)]+)\)',(ROOT/'docs/design/D5-I115-JOINT-CAPACITY-PROPOSAL.md').read_text()):assert (ROOT/'docs/design'/link).resolve().is_file(),link
    pins(read('docs/validation/D5-I115-integrity.json')['artifacts'])
    print(json.dumps(dict(status='DOCUMENTARY_AUDIT_PASS_NOT_COMPONENT_OR_FUNCTIONAL_EXECUTION',input_pins=len(ref['inputs']),verified_paths=len(verified),source_anchors=len(ref['source_anchors']),root_models=321,active_sites=30,reference_source_upper=442305,conditional_page_upper=32,conditional_sidecar_plan=35474392,resources=24,open_numeric_gates=7,synthetic_cases_NOT_RUN=20,joint_capacity='NOT_ESTABLISHED',IR03='NOT_READY'),ensure_ascii=False))

if __name__=='__main__':
    main()
