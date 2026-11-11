#!/usr/bin/env python3
"""Read-only I116 documentary audit. No product/runner/test imports or calls.
Shape encodings and source expectations are not component or campaign results.
"""
import ast
import hashlib
import json
from pathlib import Path
import re
import subprocess

ROOT=Path(__file__).resolve().parents[2]
def read(p):return json.loads((ROOT/p).read_text())
def encode(v):return json.dumps(v,ensure_ascii=False,allow_nan=False,separators=(',',':')).encode()
def pad(v):
    if type(v) is str:return '\x00'*4096
    if type(v) is int:return 10**31-1
    if type(v) is dict:return {k:pad(x) for k,x in v.items()}
    if type(v) is list:return [pad(x) for x in v]
    return v
def main():
    assert subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip()=='50c49678568bae2abeefbe5fec0285f26c628283'
    subprocess.run(['git','diff','--quiet'],cwd=ROOT,check=True)
    subprocess.run(['git','diff','--cached','--quiet'],cwd=ROOT,check=True)
    checked={}
    def pins(m):
        for p,h in m.items():
            path=Path(p)
            assert not path.is_absolute() and '..' not in path.parts and not p.startswith('dev/run_data/'),p
            assert re.fullmatch('[0-9a-f]{64}',h)
            assert hashlib.sha256((ROOT/p).read_bytes()).hexdigest()==h,p
            assert p not in checked or checked[p]==h,p
            checked[p]=h
    hand=read('docs/validation/D5-I113-handoff-integrity.json')
    for k in ('artifacts','preserved_local_artifacts','prior_integrity_seals'):pins(hand[k])
    for p in hand['prior_integrity_seals']:pins(read(p).get('artifacts',{}))
    for p in ['docs/validation/D5-I114-integrity.json','docs/validation/D5-I115-integrity.json']:pins(read(p)['artifacts'])
    shape=read('docs/validation/D5-I116-projection-row-envelopes.json')
    raw=read('docs/validation/D5-I116-raw-context-envelopes.json')
    review=read('docs/validation/D5-I116-PJC115-gate-review.json')
    for d in (shape,raw,review):
        pins(d['inputs'])
        assert len(d['inputs'])==458
        assert d['new_tests_executed']==d['functional_campaigns_executed']==0
        for k in ('implementation_changed','quota_changed','product_or_runner_imported','functional_profile_created','future_capture_authority_or_destination_created','publication_authorized','D5_closed','H07_closed','closure','numeric_joint_capacity_certificate_created'):assert d[k] is False,k
        assert d['IR03']=='NOT_READY'
    reg=read('docs/validation/D5-SELECTOR-CAPTURE-REGISTRY.json')
    old=read('docs/validation/D5-I115-refined-reference-envelope.json')
    rows={r['test_id']:r for r in old['root_rows'] if r['mode']=='T_R'}
    assert len(shape['per_root_role_context_review'])==len(rows)==88
    special={'test_DF11':3,'test_DF12':2,'test_DR23':2,'test_DR27':4,'test_DF20':3,'test_DR37':20}
    trees={}
    for rr in shape['per_root_role_context_review']:
        row=rows[rr['test_id']];k=row['event_vector']['C'];name=rr['test_id'].split('.')[-1]
        expected=special[name] if name in special else k if k<=18 else k//2
        assert rr['global_Store_constructor_upper']==k
        assert rr['Store_per_role_per_subcase_upper']==rr['facade_per_role_per_subcase_upper']==expected<=20
        bind=shape['role_method_bindings'][rr['test_id']]
        assert bind==reg['entry']['method_bindings'][rr['test_id']]
        pins({bind['path']:bind['sha256']})
        if bind['path'] not in trees:trees[bind['path']]=ast.parse((ROOT/bind['path']).read_text())
        symbol=bind['symbol'].split('.')[-1]
        assert any(isinstance(n,ast.FunctionDef) and n.name==symbol and n.lineno==bind['line'] and n.end_lineno==bind['end_line'] for n in ast.walk(trees[bind['path']])),bind
    # DR37 factory partition:4+13+2 alternatives plus one final lab, no fresh/direct Store.
    dr37=next(n for n in ast.walk(trees['testing/D5/test_durable_relational.py']) if isinstance(n,ast.FunctionDef) and n.name=='dr37')
    limit_loops=[n for n in ast.walk(dr37) if isinstance(n,ast.For) and isinstance(n.target,ast.Tuple) and n.target.elts[0].id=='limits']
    bound_loop=next(n for n in ast.walk(dr37) if isinstance(n,ast.For) and isinstance(n.target,ast.Name) and n.target.id=='key')
    assert sorted(len(n.iter.elts) for n in limit_loops)==[2,4]
    assert len(bound_loop.iter.elts)==13
    direct_labs=[n for n in dr37.body if isinstance(n,ast.Assign) and isinstance(n.value,ast.Call) and isinstance(n.value.func,ast.Attribute) and n.value.func.attr=='lab']
    assert len(direct_labs)==1
    assert sum(len(n.iter.elts) for n in limit_loops)+13+len(direct_labs)==20
    assert not any(isinstance(n,ast.Call) and isinstance(n.func,ast.Attribute) and n.func.attr=='fresh' for n in ast.walk(dr37))
    cw=shape['counter_width_proof']
    assert cw['owner_upper']==old['owner_origins_upper']==5190
    assert cw['causal_key_upper']==old['site_charge_upper']['Q19']==37651
    assert len('O'+str(cw['owner_upper']))==5 and len('C'+str(cw['causal_key_upper']))==6
    assert shape['UUID_freshness_assumed'] is False
    model=shape['shape_models']
    for k,v in model.items():assert len(encode(v['value']))==v['encoded_bytes'],k
    assert all(v['encoded_bytes']<=4096 for k,v in model.items() if k!='group')
    specs={'group':reg['domain_schemas']['group'],'link':reg['domain_schemas']['link'],'retained':reg['projection_schemas']['retained_oracle'],'subcase':reg['projection_schemas']['subcase'],'protocol':reg['parental_contract']['protocol_extension'],'registration':reg['parental_contract']['registration_schema']}
    for k,s in specs.items():
        assert model[k]['value']['schema']==s['schema']
        assert set(model[k]['value'])==set(s['keys']),k
    assert model['group']['encoded_bytes']==4224>4096 and model['protocol']['encoded_bytes']==3767
    assert model['O']['encoded_bytes']==shape['event_uniform_causal_upper']==3538
    pg=shape['refined_page_envelope']
    assert pg['category_counts']==old['normalized_vector_totals']
    chunks=sum(pg['category_counts'][k]*(v+1) for k,v in pg['category_bytes'].items())
    pages=chunks//(2097152-256-3539)+1
    assert chunks==pg['chunks_and_commas_upper']==58767195 and pages==pg['pages_upper']==29
    assert chunks+256*pages==pg['total_page_bytes_upper']==58774619<67108864
    def cost(v):
        if type(v) is str:return 4+len(json.dumps(v,ensure_ascii=True).encode())
        if type(v) is int:return 4+len(str(v))
        if type(v) is dict:return 6+sum(cost(k)+cost(x) for k,x in v.items())
        if type(v) is list:return 6+sum(cost(x) for x in v)
        raise AssertionError(type(v))
    oe=shape['CP03_partial_oracle_envelope']
    assert cost(oe['inert_record_majorant'])==oe['per_record_digest_charged_bytes']==595
    assert 6+997*595==oe['all997_list_digest_charged_bytes']==593221<16777216
    rr=raw['raw_recipe'];tree=ast.parse((ROOT/'testing/D5/run_relational_durable_lab.py').read_text())
    report=next(n.value for n in ast.walk(tree) if isinstance(n,ast.Assign) and any(isinstance(t,ast.Name) and t.id=='report' for t in n.targets))
    maxint=9223372036854775807;ids=reg['entry']['expected_test_ids']
    body={kw.arg:(ast.literal_eval(kw.value) if isinstance(kw.value,ast.Constant) else maxint) for kw in report.keywords}
    body.update(schema='d5.i36-durable-relational-campaign.v1',mode='SYNTHETIC_ONLY',status='PASS',python=raw['runtime_binding']['python'],platform=raw['runtime_binding']['platform'],tests_run=321,groups={g:ids for g in reg['entry']['expected_groups']},passed=ids,failures=[],errors=[],skipped=[],case_test_map={f'DR{i:02}':[max(ids,key=len)] for i in range(1,41)},owned_child_exitcodes=[-255]*718,crash_exercises=[rr['crash_item']]*717,independent_oracle_observations=[rr['oracle_item']]*997,T_regression_child_exitcodes=[-255]*718,capture_regression_child_exitcodes=[-255]*718,cleanup_verified=True,elapsed_seconds=1.7976931348623157e308,inputs=reg['entry']['runner_effective_inputs'])
    assert sorted(body)==rr['report_keys']
    assert len(json.dumps(body,indent=2,sort_keys=True,ensure_ascii=False).encode())+1+32==rr['encoded_pretty_upper']==raw['original_raw_upper']==1667028<12582912
    ctx=raw['context_recipe']
    assert len(encode(pad(ctx['template'])))==ctx['padded_fixed_template_bytes']<ctx['fixed_misc_allowance']==2097152
    assert 4096*583+2==ctx['hash_map_upper']
    assert 4*ctx['hash_map_upper']+2097152==ctx['context_and_sibling_launcher_upper']==11649032<12582912
    assert raw['runtime_binding']==reg['stdlib_bindings']['runtime']
    # Pin the source facts behind the proposed limit propagation correction.
    base=ast.parse((ROOT/'testing/prospective_capture/capture.py').read_text())
    strict=next(n for n in base.body if isinstance(n,ast.FunctionDef) and n.name=='strict_json')
    assert any(isinstance(n,ast.Subscript) and ast.unparse(n)=="lim['file_bytes']" for n in ast.walk(strict))
    typed=ast.parse((ROOT/'testing/prospective_capture_typed/capture.py').read_text())
    ev=next(n for n in typed.body if isinstance(n,ast.FunctionDef) and n.name=='evidence_reader')
    call=next(n for n in ast.walk(ev) if isinstance(n,ast.Call) and isinstance(n.func,ast.Attribute) and n.func.attr=='Reader')
    overrides=call.args[1]
    assert isinstance(overrides,ast.Call) and {k.arg for k in overrides.keywords}=={'unique_bytes','read_bytes'}
    selectors=ast.parse((ROOT/'testing/prospective_capture_selectors/capture.py').read_text())
    decode=next(n for n in selectors.body if isinstance(n,ast.FunctionDef) and n.name=='read_sidecar')
    calls=[n for n in ast.walk(decode) if isinstance(n,ast.Call) and isinstance(n.func,ast.Attribute) and n.func.attr=='strict_json']
    assert len(calls)==1 and len(calls[0].args)==1 and not calls[0].keywords
    writer=next(n for n in selectors.body if isinstance(n,ast.ClassDef) and n.name=='SideWriter')
    write=next(n for n in writer.body if isinstance(n,ast.FunctionDef) and n.name=='write')
    assert ast.unparse(write.args.defaults[0])=="LIMITS['index_sidecar_bytes']"
    assert not review['PJC115_enabled'] and not review['all_seven_resolved'] and not review['implementation_approval_requested']
    assert review['candidate_limits_unchanged']==read('docs/validation/D5-I115-joint-capacity-proposal.json')['candidate_limits']
    statuses={g['id']:g['status'] for g in review['gates']}
    assert statuses['CP02'].startswith('PARTIAL_')
    assert statuses['CP03'].startswith('OPEN_') and statuses['CP05'].startswith('PARTIAL_') and statuses['CP07'].startswith('OPEN_')
    assert statuses['CP08']==statuses['CP09']=='NOT_AUTHORIZED'
    assert all(x['status']=='NOT_RUN' for x in review['proposal_revision']['additional_synthetic_checks'])
    assert not (ROOT/'testing/prospective_capture_joint').exists()
    for n in ('docs/validation/D5-JOINT-CAPTURE-REGISTRY.json','docs/validation/D5-JOINT-CAPACITY-CONTRACT.json'):assert not (ROOT/n).exists()
    for link in re.findall(r'\]\(([^)]+)\)',(ROOT/'docs/design/D5-I116-PJC115-SOURCE-GATE-REVIEW.md').read_text()):assert (ROOT/'docs/design'/link).resolve().is_file(),link
    pins(read('docs/validation/D5-I116-integrity.json')['artifacts'])
    print(json.dumps(dict(status='DOCUMENTARY_HASH_AST_SIZE_ARITHMETIC_AUDIT_PASS_NOT_PRODUCT_EXECUTION',input_pins=len(shape['inputs']),verified_paths=len(checked),role_roots=88,max_projected_event=3538,max_group_row=4224,max_protocol_row=3767,raw_upper=1667028,context_upper=11649032,refined_pages=29,CP02='PARTIAL',CP03='OPEN',CP05='PARTIAL',CP07='OPEN',PJC115_enabled=False,IR03='NOT_READY')))
if __name__=='__main__':main()
