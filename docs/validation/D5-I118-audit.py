#!/usr/bin/env python3
"""Read-only I118 documentary audit; no product/runner imports or execution.

AST inspection, JSON sizing and symbolic length arithmetic are not component
or functional tests. PASS cannot enable R2, create authority, or close D5.
"""
import ast
import copy
import hashlib
import json
import re
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
P = 'docs/validation/D5-I118-'

def read(path):
    return json.loads((ROOT/path).read_text())

def sha(path):
    return hashlib.sha256((ROOT/path).read_bytes()).hexdigest()

def encode(value):
    return json.dumps(value,ensure_ascii=False,allow_nan=False,separators=(',',':')).encode()

def git(*args):
    return subprocess.check_output(['git',*args],cwd=ROOT,text=True).strip()

def node(path,symbol):
    body=ast.parse((ROOT/path).read_text()).body
    for part in symbol.split('.'):
        out=next(n for n in body if isinstance(n,(ast.FunctionDef,ast.ClassDef)) and n.name==part)
        body=out.body
    return out

def has_ast(tree,expression):
    expected=ast.dump(ast.parse(expression,mode='eval').body,include_attributes=False)
    return any(ast.dump(n,include_attributes=False)==expected for n in ast.walk(tree))

NAMES={'bounded_builtin','canonical_hash','store_request','drive_request','store_receipt','drive_receipt','oracle_value','oracle_commit','child_header'}
class Census(ast.NodeVisitor):
    def __init__(self,path):
        self.path=path;self.stack=[];self.rows=[]
    def visit_FunctionDef(self,n):
        self.stack.append(n.name);self.generic_visit(n);self.stack.pop()
    def visit_ClassDef(self,n):
        self.stack.append(n.name);self.generic_visit(n);self.stack.pop()
    def visit_Call(self,n):
        f=n.func
        name=f.id if isinstance(f,ast.Name) else f.attr if isinstance(f,ast.Attribute) else None
        if name in NAMES or name in ('digest_value','observe'):
            self.rows.append(dict(path=self.path,line=n.lineno,end_line=n.end_lineno,
                owner='.'.join(self.stack),callee=ast.unparse(f),expression=ast.unparse(n),
                expression_AST_sha256=hashlib.sha256(ast.dump(n,include_attributes=False).encode()).hexdigest(),
                runtime_reachability='NOT_INFERRED_FROM_LEXICAL_PRESENCE',
                value_closure='NOT_PROVEN_BY_THIS_CENSUS'))
        self.generic_visit(n)

def main():
    c=read(P+'CP03-source-disposition.json')
    r=read(P+'CP07-binding-review.json')
    g=read(P+'gate-disposition.json')
    seal=read(P+'integrity.json')
    assert git('rev-parse','HEAD')==c['base_commit']=='50c49678568bae2abeefbe5fec0285f26c628283'
    assert not git('diff','--name-only') and not git('diff','--cached','--name-only')
    checked=set()
    for doc in (c,r,g):
        assert doc['inputs']==c['inputs'] and len(doc['inputs'])==471
        assert doc['increment']=='I118' and doc['date']=='2026-11-10'
        assert doc['IR03']=='NOT_READY' and doc['global_review']=='OPEN'
        assert doc['new_tests_executed']==doc['functional_campaigns_executed']==0
        assert doc['semantic_baseline']=='P0;83 SUPPORTS_BOUNDED/1 PARTIAL'
        assert doc['remaining_partial_parts']==['UI04.1']
        for flag in ('product_or_runner_imported','implementation_changed','quota_changed',
                     'functional_profile_created','future_capture_authority_or_destination_created',
                     'publication_authorized','D5_closed','H07_closed','closure','real_providers',
                     'credentials','consumption','reservations','activation','promotion','deployment','D6'):
            assert doc[flag] is False,flag
    for mapping in (c['inputs'],seal['prior_local_files'],seal['artifacts']):
        for path,h in mapping.items():
            assert not Path(path).is_absolute() and '..' not in Path(path).parts
            assert not path.startswith('dev/run_data/'),path
            assert sha(path)==h,path
            checked.add(path)
    assert len(seal['prior_local_files'])==39 and len(seal['artifacts'])==5
    expected=set(r['manifest_design']['dossier_names'])
    assert len(expected)==6 and expected==set(seal['artifacts'])|{P+'integrity.json'}
    assert set(git('ls-files','--others','--exclude-standard').splitlines())==set(seal['prior_local_files'])|expected
    for a in c['source_anchors']:
        n=node(a['path'],a['symbol'])
        assert sha(a['path'])==a['sha256']
        assert n.lineno==a['line'] and n.end_lineno==a['end_line']
        assert hashlib.sha256(ast.dump(n,include_attributes=False).encode()).hexdigest()==a['AST_sha256']

    product='source_ingest/incremental_fixture.py'
    fixture='testing/D5/test_incremental_capture.py'
    observer='testing/prospective_capture_selectors/capture.py'
    base='testing/prospective_capture/capture.py'
    typed='testing/prospective_capture_typed/capture.py'
    tid=c['negative_case']['test_id'];case=c['negative_case']
    method=node(fixture,'IncrementalCaptureTest.'+tid.rsplit('.',1)[-1])
    assert has_ast(method,"self.store.advance(b' '*(MAX_OBJECT+1))")
    module=ast.parse((ROOT/product).read_text())
    maximum=next(n.value for n in module.body if isinstance(n,ast.Assign) and any(isinstance(t,ast.Name) and t.id=='MAX_OBJECT' for t in n.targets))
    assert ast.dump(maximum,include_attributes=False)==ast.dump(ast.parse('32*1024*1024',mode='eval').body,include_attributes=False)
    decode=node(product,'decode')
    assert has_ast(decode,"type(data) is not bytes or len(data) > MAX_OBJECT")
    assert has_ast(decode,"fail('OBJECT_LIMIT')")
    advance=node(product,'FixtureStore.advance')
    assert isinstance(advance.body[0],ast.Assign) and has_ast(advance.body[0],"decode(value if type(value) is bytes else encode(value))")
    drive=node(observer,'drive_request')
    assert has_ast(drive,"fault(len(value)<=lim['operand_bytes'],'CAUSAL_FIELD_BUDGET')")
    assert has_ast(drive,'c.strict_json(value)')
    guarded=next(n for n in drive.body if isinstance(n,ast.If))
    assert has_ast(guarded.body[0],"fault(len(value)<=lim['operand_bytes'],'CAUSAL_FIELD_BUDGET')")
    assert has_ast(guarded.body[-1],'c.strict_json(value)')
    wrapper=node(observer,'BaseRecorder.wrap_boundary')
    assert has_ast(wrapper,"c.digest_value({k:v for k,v in b.items() if k!='self'},rec.limits)")
    assert has_ast(wrapper,"observer in candidate['methods']") and has_ast(wrapper,"failure.code in candidate['input_failures']")
    assert has_ast(wrapper,"projection.get('code') not in negative['exception_codes']")
    assert has_ast(wrapper,"fault(negative is None,'COMMAND_HEADER_INVALID')")
    nested=next(n for n in wrapper.body if isinstance(n,ast.FunctionDef) and n.name=='wrapped')
    assert sum(isinstance(n,ast.Call) and isinstance(n.func,ast.Name) and n.func.id=='old' for n in ast.walk(nested))==2
    # One is the causal-disabled early return; on the causal-selected path only
    # the other original call is reached. This audit does not invoke either.
    assert has_ast(nested.body[0].test,'not rec.causal_enabled()')
    main_try=next(n for n in nested.body if isinstance(n,ast.Try) and any(has_ast(x,'old(*args,**kwargs)') for x in n.body))
    assert any(isinstance(n,ast.Raise) and n.exc is None for h in main_try.handlers for n in h.body)
    registry=read('docs/validation/D5-SELECTOR-CAPTURE-REGISTRY.json')
    selector=registry['negative_input_selectors'][tid]
    assert selector==case['selector']
    assert 'FixtureStore.advance' in selector['methods']
    assert 'CAUSAL_FIELD_BUDGET' in selector['input_failures'] and 'OBJECT_LIMIT' in selector['exception_codes']
    digest=node(base,'digest_value')
    assert has_ast(digest,"used<=lim['operand_bytes']")
    assert has_ast(digest,'range(0,len(x),65536)')
    assert has_ast(digest,"dict(status='NOT_RECORDED',reason=ex.code if isinstance(ex,CaptureFault) else 'UNSUPPORTED_OPERAND',sha256=None)")
    n=32*1024*1024+1;lim=16777216
    scalar=n+6+len(str(n))+1
    full=6+4+len(json.dumps('value').encode())+scalar
    prefix=5+4+len(json.dumps('value').encode())+6+len(str(n))+1
    chunks=(lim-prefix)//65536+1
    assert n==case['input_bytes']==33554433
    assert scalar==case['full_bytes_scalar_cost']==33554448
    assert full==case['full_fallback_dict_cost']==33554465
    assert full-lim==case['full_fallback_excess']==16777249
    charged=case['first_over_limit_stream_charge']
    assert prefix==charged['fixed_prefix_bytes']==31
    assert chunks==charged['chunks']==256
    assert prefix+65536*(chunks-1)<=lim<prefix+65536*chunks==charged['attempted_total']==16777247
    assert case['fallback_input_digest']==dict(status='NOT_RECORDED',reason='OPERAND_BUDGET',sha256=None)
    assert not case['input_buffer_materialized'] and not case['product_or_codec_called']
    assert len(encode(case['negative_request_model']))==case['negative_request_model_bytes']
    assert len(encode(case['negative_terminal_model']))==case['negative_terminal_model_bytes']==1182<1397<3546
    validator=node(observer,'validate_call_header')
    exception_branch=next(n for n in validator.body if isinstance(n,ast.If) and has_ast(n.test,"row['outcome']=='EXCEPTION'"))
    assert isinstance(exception_branch.body[-1],ast.Return)

    leaves=c['typed_leaves'];projector=node(typed,'Projector.observe')
    assert any(isinstance(n,ast.Constant) and n.value=='[A-Z][A-Z0-9_]{0,79}' for n in ast.walk(projector))
    args_digest=6+4+len(json.dumps('A'*80).encode())+1
    assert args_digest==leaves['exception_argument_tuple_digest_upper']==93
    tag=len(b'd5.typed-operand-projection.v1\0')
    assert tag+args_digest+len(encode(leaves['exception_leaf']))==leaves['exception_total_charge_upper']==383
    assert tag+len(encode(leaves['class_leaf']))==leaves['class_total_charge_upper']==189
    assert max(leaves['exception_total_charge_upper'],leaves['class_total_charge_upper'])<leaves['allowance_upper']==512
    assert not leaves['path_cases_resolved']
    census=c['lexical_operand_sink_census'];sites=[]
    for path in census['paths']:
        walk=Census(path);walk.visit(ast.parse((ROOT/path).read_text()));sites+=walk.rows
    assert sites==census['sites'] and len(sites)==census['site_count']==62
    assert len(c['mandatory_obligations'])==10
    assert all(x['status']=='OPEN_SOURCE_VALUE_CLOSURE' for x in c['mandatory_obligations'])
    assert not c['global_CP03_resolved'] and not c['all_digests_fit_claimed']
    assert not c['actual_capture_invalid_claimed']

    union=sum((ROOT/p).stat().st_size for p in c['inputs'])
    assert union==r['known_documentary_union']['unique_bytes']==84917841
    assert len(c['inputs'])==r['known_documentary_union']['paths']==471
    assert max((ROOT/p).stat().st_size for p in c['inputs'])==r['known_documentary_union']['maximum_file_bytes']==9755833
    old=read('docs/validation/D5-I117-reader-capacity-design.json')
    assert union-old['existing_documentary_union']['unique_bytes']==r['I117_growth']['additional_bytes']==837075
    schedule=r['reader_design'];base_read=3*union+4852460;remaining=268435456-base_read
    assert base_read==schedule['base_three_phase_worker_upper']==259605983
    assert remaining==schedule['weighted_remaining_bytes']==8829473
    assert remaining//3==schedule['conditional_S_max_if_X_zero']==2943157
    assert schedule['S_new_files_bytes'] is None and schedule['X_new_extra_reads_bytes'] is None
    assert not schedule['X_zero_proven'] and schedule['unchanged_active_Reader']
    assert not schedule['legacy_finish_currently_present']
    i96=read('docs/validation/D5-I96-reader-envelope.json')['reader_budget']['input_path']
    assert not i96['finish_on_same_input_reader_in_current_launcher'] and not i96['finish_on_same_input_reader_in_current_worker']
    assert 4852460==i96['full_worker_normal_input_read_upper']-i96['launcher_upper_without_late_checks']
    manifest=r['manifest_design']
    assert manifest['total_paths_upper']==471+6+12+1==490
    assert len(manifest['future_fixed_names'])==12
    for row in r['absent_future_files']:
        assert row['path'] in manifest['future_fixed_names']
        assert not (ROOT/row['path']).exists() and not row['exists']
        assert row['sha256'] is None and row['byte_size'] is None
    assert not (ROOT/'testing/prospective_capture_joint').exists()
    assert r['authority']==dict(path=None,sha256=None,destination=None,created=False)
    model=r['top_metadata_model'];top=model['value']
    assert len(encode(top))==model['encoded_bytes']==483185<model['allowance']==524288
    assert len(top['capture_inputs_before'])==len(top['capture_inputs_after'])==490
    assert top['capture_inputs_before']==top['capture_inputs_after']
    assert all(top['capture_inputs_before'][p]==h for p,h in c['inputs'].items())
    assert model['all_future_hashes_are_width_placeholders']
    assert r['CP07_current_pin_inventory_resolved'] and not r['CP07_future_exact_binding_resolved']
    assert not r['CP07_global_resolved'] and not r['source_namespace_created']
    assert not r['dependency_order']['stage_split_applied'] and not r['dependency_order']['gate_requirements_waived']
    assert g['candidate_limits_unchanged']==read('docs/validation/D5-I117-PJC115-R2-design.json')['numeric_candidates']
    assert len(g['candidate_limits_unchanged'])==24
    assert not g['all_requested_gates_resolved'] and not g['proposal_enabled']
    assert not any(g[k] for k in ('implementation_authorized','component_execution_authorized','capture_authorized','approval_requested','source_capacity_certificate_created'))
    assert all(x['status']=='NOT_RUN' for x in g['new_synthetic_checks']) and len(g['new_synthetic_checks'])==6
    for link in re.findall(r'\]\(([^)]+)\)',(ROOT/'docs/design/D5-I118-CP03-CP07-ENABLEMENT-REVIEW.md').read_text()):
        assert (ROOT/'docs/design'/link).resolve().is_file(),link
    dossier_bytes=sum((ROOT/p).stat().st_size for p in expected)
    assert 3*dossier_bytes<remaining
    print(json.dumps(dict(status='DOCUMENTARY_HASH_AST_JSON_LENGTH_AUDIT_PASS_NOT_PRODUCT_EXECUTION',
        existing_input_pins=471,verified_paths=len(checked),prior_local_files=39,I118_files=6,
        DI24_input_bytes=n,DI24_full_fallback_cost=full,DI24_first_failed_charge=charged['attempted_total'],
        DI24_result='EXPECTED_SELECTED_NEGATIVE_NOT_FULL_DIGEST_NOT_RUNTIME_RESULT',
        typed_exception_upper=383,typed_class_upper=189,lexical_sink_sites=62,
        mandatory_global_CP03='OPEN',future_exact_CP07='OPEN',reader_base=base_read,
        weighted_margin_before_I118=remaining,I118_dossier_bytes=dossier_bytes,
        weighted_margin_after_I118=remaining-3*dossier_bytes,unknown_future_bytes_and_extra_reads=True,
        top_metadata_bytes=model['encoded_bytes'],PJC115_R2_enabled=False,IR03='NOT_READY',D5_closed=False)))

if __name__=='__main__':
    main()
