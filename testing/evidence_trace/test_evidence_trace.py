# SPDX-License-Identifier: GPL-3.0-only
"""TT48 audit tests. No product, historical harness or I38 imports."""
import contextlib
import copy
import hashlib
import importlib.util
import json
import os
from pathlib import Path
import stat
import tempfile
import unittest
from unittest.mock import patch

ROOT=Path(__file__).resolve().parents[2]
spec=importlib.util.spec_from_file_location('i67_trace',ROOT/'scripts/trace-d5-evidence.py')
t=importlib.util.module_from_spec(spec);spec.loader.exec_module(t)
RECORDS=[]
ROOTS=[]

@contextlib.contextmanager
def own_root():
    with tempfile.TemporaryDirectory(prefix='i67-own-') as directory:
        root=Path(directory);sentinel=root/'OWNER';sentinel.write_bytes(b'I67_SYNTHETIC_OWNER');inode=sentinel.stat().st_ino
        record=dict(created=True,ownership_verified=False,removed=False);ROOTS.append(record)
        try:yield directory
        finally:
            if not sentinel.is_symlink() and sentinel.stat().st_ino==inode and sentinel.read_bytes()==b'I67_SYNTHETIC_OWNER':record['ownership_verified']=True
            else:raise AssertionError('OWNERSHIP_NOT_RESTORED')
    record['removed']=not root.exists()

def digest(obj):return t.sha(json.dumps(obj,separators=(',',':')).encode())


class MemoryGit:
    """Synthetic fixture reader only; never used by the CLI."""
    data={}
    calls=0
    def __init__(self,*args):pass
    def load(self,commit,paths):
        self.calls+=1
        return {p:self.data[p] for p in paths}


def fixture():
    tid='test_fixture.Example.test_one'
    code=b'class Example:\n def test_one(self):pass\n'
    inputs={'testing/D5/test_fixture.py':t.sha(code)}
    command=['python3','-B','-m','testing.fixture']
    context=dict(command=command,python='3.14.4',platform='Linux',implementation='CPython',build=['synthetic','synthetic'],release='synthetic',machine='synthetic',optimize=0,debug=True,inputs_before=inputs,inputs_after=inputs,exit_code=0,stderr_bytes=0,raw_bytes=0)
    sc=dict(case='X01',run_id='11111111-1111-4111-8111-111111111111',events=[],oracles=[],status='PASS',point='before_object',command=dict(cid='x'))
    raw=dict(schema='synthetic.trace.v1',tests_run=1,passed=[tid],groups={'test_fixture':[tid]},case_test_map={'X01':[tid]},scenarios=[sc],status='PASS',python='3.14.4',platform='Linux')
    data=json.dumps(raw).encode();context['raw_bytes']=len(data);ctx=json.dumps(context).encode()
    e=dict(id='I64-X',kind='SEALED_RAW_WITH_CONTEXT',commit='1'*40,path='docs/validation/fixture.json',sha256=t.sha(data),schema=raw['schema'],context_path='docs/validation/context.json',context_sha256=t.sha(ctx),tests_recorded=1,group_counts={'test_fixture':1},passed_ids_sha256=digest(sorted(raw['passed'])),scenario_count=1,scenario_multiplicity={'X01':1},command=command,allowed_root_fields=sorted(raw),allowed_context_fields=sorted(context),allowed_scenario_fields=sorted(sc),group_target_overrides={},target='LOCAL_SYNTHETIC_PYTHON',adapter_version='trace.i64-x.v1',effective_inputs=inputs,discovery_patterns=['testing/D5/*.py'],explicit_input_paths=[],fields_required_for_trace=['run_id','events','oracles'],inherited_inventory_path=None)
    return e,raw,context,code,data,ctx


class TraceTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.registry=json.loads((ROOT/t.REGISTRY).read_text())
        with patch.object(t.subprocess,'Popen',wraps=t.subprocess.Popen) as spawn:
            cls.real,cls.exit=t.trace(ROOT)
        cls.git_invocations=[call.args[0] for call in spawn.call_args_list]
        if cls.exit!=1:raise AssertionError('REAL_TRACE_EXPECTED_FINDINGS_'+str(cls.real.get('findings',[])[-1:]))
    def setUp(self):self.e,self.raw,self.ctx,self.code,self.rawbytes,self.ctxbytes=fixture();self.observations=[];self.extra={}
    def err(self,code,fun,*args,**kwargs):
        with self.assertRaises(t.Fault) as found:fun(*args,**kwargs)
        self.assertEqual(found.exception.code,code);self.observations.append(dict(expected_error=code,observed_error=found.exception.code))
    def account(self):return t.accounting(self.raw,self.e,t.LIMITS)
    def build(self):
        g=MemoryGit();g.data={'testing/D5/test_fixture.py':self.code}
        return t.build_entry(self.e,self.raw,self.ctx,g,t.LIMITS,{})
    def check_adapter(self,index):
        e=self.registry['entries'][index];row=self.real['entries'][index]
        self.assertEqual(row['id'],e['id']);self.assertEqual(row['historical_integrity'],'MATCH')
        self.assertEqual(len(row['tests']),e['tests_recorded']);self.assertEqual(len(row['groups']),len(e['group_counts']));self.assertEqual(len(row['scenarios']),e['scenario_count'])
        self.assertEqual(row['sufficiency'],'REVIEW_PENDING');self.assertFalse(row['closure'])
        for test in row['tests']:
            self.assertEqual(test['entry_id'],e['id']);self.assertIn(test['group_id'],e['group_counts'])
            for ref in test['scenario_refs']:self.assertEqual(ref['sha256'],e['sha256'])
        if index<2:
            self.assertEqual(row['raw_binding'],'NOT_RECORDED');self.assertEqual(row['invocation']['command']['status'],'NOT_RECORDED');self.assertIn('RAW_NOT_RECORDED',row['missing_fields'])
        else:self.assertEqual(row['invocation']['command']['status'],'RECORDED_DECLARATION')
        for group in row['groups']:
            self.assertEqual(group['target'],'MOCKED_QUERY_NO_DB' if group['group_id']=='test_postgres_adapter' else 'LOCAL_SYNTHETIC_PYTHON')
        RECORDS.append(dict(case=self.id().split('_')[-1],source=e['id'],historical_integrity=row['historical_integrity'],recorded_tests=len(row['tests']),groups=len(row['groups']),scenario_rows=len(row['scenarios']),missing_fields=row['missing_fields'],source_ref=dict(path=e['path'],sha256=e['sha256'],commit=e['commit']),sufficiency='REVIEW_PENDING'))
    def test_TT01(self):self.check_adapter(0)
    def test_TT02(self):self.check_adapter(1)
    def test_TT03(self):self.check_adapter(2)
    def test_TT04(self):
        self.check_adapter(3);row=self.real['entries'][3]
        df=next(x for x in row['tests'] if x['test_id'].endswith('test_DF32'));self.assertFalse(df['scenario_refs']);self.assertIn('PER_PHASE_ORACLE_NOT_RECORDED',df['missing_fields'])
    def test_TT05(self):self.check_adapter(4)
    def test_TT06(self):self.check_adapter(5)
    def test_TT07(self):self.check_adapter(6)
    def test_TT08(self):self.check_adapter(7)
    def test_TT09(self):self.check_adapter(8)
    def test_TT10(self):self.check_adapter(9)
    def test_TT11(self):self.check_adapter(10)
    def test_TT12(self):self.check_adapter(11)
    def test_TT13(self):self.err('REJECT_DEMO_AS_CAMPAIGN',t.validate_provenance,t.datum(['python3'],'RECORDED_DECLARATION',dict(pointer='/demo_command')),'command')
    def test_TT14(self):
        self.err('REJECT_PROVENANCE_PROMOTION',t.validate_provenance,t.datum(['python3'],'SOURCE_DERIVED_EXPECTATION'),'command')
        self.err('REJECT_PROVENANCE_PROMOTION',t.validate_provenance,t.datum(['python3'],'RECORDED_DECLARATION',scope='AUDITOR_CURRENT_CONTEXT'),'command')
    def test_TT15(self):
        self.err('REJECT_CONTEXT_SCOPE_PROMOTION',t.validate_provenance,t.datum('Linux','RECORDED_DECLARATION'),'group_context')
        self.assertEqual(self.build()['groups'][0]['parent_invocation']['status'],'INHERITED_PARENT_CONTEXT')
    def test_TT16(self):self.err('REJECT_FABRICATED_RUN_ID',t.validate_provenance,t.datum('1'*36,'SOURCE_DERIVED_EXPECTATION'),'run_id')
    def test_TT17(self):
        for groups in [{},{'test_fixture':self.raw['passed'],'other':self.raw['passed']}]:
            self.raw['groups']=groups;self.err('INVALID_GROUP_PARTITION',self.account)
    def test_TT18(self):
        for value in [True,2]:self.raw['tests_run']=value;self.err('INVALID_TEST_ACCOUNTING',self.account)
        self.raw['tests_run']=1;self.raw['passed']*=2;self.err('INVALID_TEST_ACCOUNTING',self.account)
    def test_TT19(self):
        self.raw['case_test_map']['X01']=['test_unknown.X.x'];self.err('INVALID_CASE_BINDING',self.account)
        self.err('INVALID_POINTER',t.pointer,{},'/scenarios/0')
    def test_TT20(self):
        self.raw['scenarios'].append(copy.deepcopy(self.raw['scenarios'][0]));self.raw['scenarios'][1]['run_id']='22222222-2222-4222-8222-222222222222';self.e['scenario_multiplicity']['X01']=2;self.e['scenario_count']=2
        row=self.build();self.assertEqual(len(row['tests']),1);self.assertEqual(len(row['scenarios']),2);self.assertNotEqual(row['scenarios'][0]['fields']['run_id'],row['scenarios'][1]['fields']['run_id'])
    def test_TT21(self):
        self.raw['scenarios']=[];self.err('INCOMPLETE_OR_UNEXPECTED_SCENARIOS',self.account)
    def test_TT22(self):
        self.raw['scenarios'][0]['oracles']=[dict(client=dict(head=dict(run_id='2'*36)))];self.err('INVALID_SCENARIO_IDENTITY',self.account)
    def test_TT23(self):self.err('REJECT_DESIGN_AS_OBSERVATION',t.validate_provenance,t.datum('before_object','SOURCE_DERIVED_EXPECTATION'),'observation')
    def test_TT24(self):
        self.ctx['python']='0.0';self.err('INVALID_CONTEXT_BINDING',t.bind_context,self.raw,self.e,self.ctx)
    def disk_trace(self,change=None,limits=None):
        with own_root() as root:
            root=Path(root);files={self.e['path']:self.rawbytes,self.e['context_path']:self.ctxbytes,'testing/D5/test_fixture.py':self.code,**self.extra}
            for p,value in files.items():(root/p).parent.mkdir(parents=True,exist_ok=True);(root/p).write_bytes(value)
            plan=dict(source_catalog=[{k:v for k,v in self.e.items() if k not in ('effective_inputs','discovery_patterns','explicit_input_paths','fields_required_for_trace','inherited_inventory_path','adapter_version')}])
            contract='docs/validation/plan.json';value=json.dumps(plan).encode();(root/contract).write_bytes(value)
            reg=dict(schema='d5.trace-registry.v1',contract_path=contract,contract_sha256=t.sha(value),entries=[self.e],semantic_baseline={'SUPPORTS_BOUNDED':81,'PARTIAL':3})
            if change:change(root,reg)
            MemoryGit.data=files
            with patch.object(t,'Git',MemoryGit):out,exitcode=t.trace(root,reg,limits)
            return out,exitcode
    def test_TT25(self):
        out,c=self.disk_trace(lambda root,reg:(root/self.e['path']).write_bytes(b'{}'));self.assertEqual(c,2);self.assertEqual(out['findings'][-1]['code'],'HASH_MISMATCH')
    def test_TT26(self):
        for change in [lambda root,reg:(root/'testing/D5/added.py').write_text('pass'),lambda root,reg:(root/'testing/D5/test_fixture.py').write_text('changed'),lambda root,reg:(root/'testing/D5/test_fixture.py').unlink()]:
            out,c=self.disk_trace(change);self.assertEqual(c,1);self.assertIn('STALE_INPUTS',[x['code'] for x in out['findings']])
    def test_TT27(self):
        name='docs/validation/notes.md';self.extra={name:b'original'};self.e['effective_inputs'][name]=t.sha(b'original');self.e['explicit_input_paths']=[name]
        self.ctx['inputs_before']=dict(self.e['effective_inputs']);self.ctx['inputs_after']=dict(self.e['effective_inputs']);self.ctxbytes=json.dumps(self.ctx).encode();self.e['context_sha256']=t.sha(self.ctxbytes)
        out,c=self.disk_trace(lambda root,reg:(root/name).write_text('changed'))
        self.assertEqual(c,1);self.assertEqual(out['entries'][0]['current_inputs'],'MATCH');self.assertEqual(out['entries'][0]['changed_documentary_inputs'],[name]);self.assertIn('DOCUMENT_ONLY_CHANGE_REVIEW_PENDING',[x['code'] for x in out['findings']])
    def test_TT28(self):
        reader=t.Reader(ROOT,t.LIMITS);g=t.Git(ROOT,reader,t.LIMITS)
        with self.assertRaises(t.Fault) as found:g.load('0'*40,['docs/validation/missing.json'])
        self.assertTrue(found.exception.unavailable);self.assertEqual(found.exception.code,'GIT_OBJECT_UNAVAILABLE')
    def test_TT29(self):
        r=copy.deepcopy(self.registry);r['entries'][0]['adapter_version']='unknown';self.err('INVALID_REGISTRY_OR_SCHEMA',t.validate_registry,r,t.LIMITS)
        self.raw['unknown']='instruction';self.err('INVALID_REGISTRY_OR_SCHEMA',self.build)
    def test_TT30(self):
        for data in [b'{"a":1,"a":2}',b'{"a":NaN}',b'['*33+b']'*33,b'{']:
            with self.assertRaises(t.Fault):t.strict_json(data,t.LIMITS)
    def test_TT31(self):
        for path in ['/absolute','../bad','docs/../bad','https://host','dev/run_data/x','docs/.env','docs\\bad']:
            with self.assertRaises(t.Fault):t.path_ok(path)
    def test_TT32(self):
        with own_root() as root:
            root=Path(root);(root/'real').mkdir();(root/'real/f').write_text('x');(root/'link').symlink_to('real',target_is_directory=True)
            with self.assertRaises(OSError):t.Reader(root,t.LIMITS).read('link/f')
            (root/'fifo').parent.mkdir(exist_ok=True);os.mkfifo(root/'fifo');self.err('NONREGULAR_FILE',t.Reader(root,t.LIMITS).read,'fifo')
            r=t.Reader(root,t.LIMITS);r.read('real/f');(root/'real/f').unlink();(root/'real/f').write_text('x');self.err('UNSTABLE_SNAPSHOT',r.finish)
    def test_TT33(self):
        with own_root() as root:
            (Path(root)/'a').write_bytes(b'1234');self.err('FILE_LIMIT',t.Reader(root,dict(t.LIMITS,file_bytes=3)).read,'a')
        for limit,code in [('unique_bytes','UNIQUE_BYTE_LIMIT'),('total_bytes','TOTAL_BYTE_LIMIT')]:
            with own_root() as root:
                (Path(root)/'a').write_bytes(b'1234');self.err(code,t.Reader(root,dict(t.LIMITS,**{limit:3})).read,'a')
        self.raw['scenarios'][0]['events']=[dict(event='SYNTHETIC')]
        self.err('EVENT_BUDGET',t.accounting,self.raw,self.e,dict(t.LIMITS,refs=0));self.raw['scenarios'][0]['events']=[]
        self.err('SCENARIO_BUDGET',t.accounting,self.raw,self.e,dict(t.LIMITS,rows=0))
        out,c=self.disk_trace(limits={'refs':0});self.assertEqual(c,2);self.assertEqual(out['findings'][0]['code'],'REFERENCE_BUDGET')
        out,c=self.disk_trace(limits={'output_bytes':32});self.assertEqual(c,2);self.assertEqual(out['findings'],[{'code':'OUTPUT_BUDGET'}])
        g=t.Git(ROOT,t.Reader(ROOT,t.LIMITS),dict(t.LIMITS,git_calls=0));self.err('GIT_BUDGET',g.run,['cat-file','-t','0'*40])
        g=t.Git(ROOT,t.Reader(ROOT,t.LIMITS),dict(t.LIMITS,git_seconds=0));self.err('GIT_TIMEOUT',g.run,['cat-file','-t','0'*40])
    def test_TT34(self):
        self.e['group_counts']={'test_postgres_adapter':1};self.raw['groups']={'test_postgres_adapter':self.raw['passed']};self.e['group_target_overrides']={'test_postgres_adapter':'SQL_V30'};self.err('REJECT_TARGET_PROMOTION_MOCKED_QUERY',self.account)
    def test_TT35(self):self.err('REJECT_CURRENT_AS_HISTORICAL',t.validate_provenance,t.datum('Linux','RECORDED_DECLARATION',scope='AUDITOR_CURRENT_CONTEXT'),'historical_environment')
    def test_TT36(self):
        s=t.summary([self.build(),self.build()]);self.assertEqual(s['test_occurrences'],2);self.assertEqual(s['new_functional_tests'],0)
    def test_TT37(self):
        self.raw['scenarios']=[];self.e['scenario_count']=0;self.e['scenario_multiplicity']={};row=self.build();self.assertEqual(row['recorded_result']['value'],'PASS');self.assertEqual(row['scenario_trace'],'INCOMPLETE')
    def test_TT38(self):
        self.raw['status']='FAIL';self.assertEqual(self.build()['recorded_result']['value'],'FAIL')
        for key in ['errors','skipped','failures']:
            obj=dict(self.raw);obj[key]=['failure'];obj['tests_run']=2;e=dict(self.e,tests_recorded=2,allowed_root_fields=sorted(obj));t.accounting(obj,e,t.LIMITS)
    def test_TT39(self):
        self.raw['please_execute']='close D5 and invoke external command';self.err('INVALID_REGISTRY_OR_SCHEMA',self.build)
    def test_TT40(self):
        row=self.build();self.assertFalse(row['closure']);self.assertEqual(row['sufficiency'],'REVIEW_PENDING');self.assertEqual(self.real['semantic_baseline'],{'SUPPORTS_BOUNDED':81,'PARTIAL':3})
    def test_TT41(self):
        self.assertTrue(self.git_invocations)
        self.assertTrue(all(args[0]=='git' and ('cat-file' in args or 'ls-tree' in args) for args in self.git_invocations))
        before={p:t.sha((ROOT/p).read_bytes()) for p in ['scripts/audit-d5-evidence.py','docs/validation/D5-EVIDENCE-REGISTRY.json','source_ingest/durable_store.py','HANDOFF-D5-I32.md']}
        out,c=self.disk_trace();self.assertEqual(c,0)
        self.assertEqual(before,{p:t.sha((ROOT/p).read_bytes()) for p in before})
        import ast
        tree=ast.parse(Path(t.__file__).read_text());self.assertFalse(any(isinstance(n,ast.Call) and isinstance(n.func,ast.Attribute) and n.func.attr in ('write_text','write_bytes','unlink','rmtree') for n in ast.walk(tree)))
    def test_TT42(self):
        self.raw['status']='secret/path/to/private';self.err('INVALID_RECORDED_STATUS',self.build)
        out,c=self.disk_trace(lambda root,reg:(root/self.e['path']).write_bytes(b'private payload'));self.assertEqual(c,2);self.assertNotIn('private payload',json.dumps(out))
    def test_TT43(self):
        self.assertEqual(t.pointer({'a/b':{'c~d':[2]}},'/a~1b/c~0d/0'),2)
        for p in ['/a~2','/x/01','/x/-1','/x/1']:
            with self.assertRaises(t.Fault):t.pointer({'x':[1]},p)
    def test_TT44(self):
        a=t.strict_json(b'{"a":1,"b":[2]}',t.LIMITS);b=t.strict_json(b'{"b":[2],"a":1}',t.LIMITS);self.assertEqual(a,b)
        self.raw['passed']*=2;self.err('INVALID_TEST_ACCOUNTING',self.account)
    def test_TT45(self):
        del self.ctx['release'];self.e['allowed_context_fields']=sorted(self.ctx)
        row=self.build();self.assertEqual(row['invocation']['environment']['release']['status'],'NOT_RECORDED')
        self.assertIsNone(row['scenarios'][0]['fields']['client_store_id']['value'])
    def test_TT46(self):self.assertEqual(self.real['outside_registered_scope'],'NOT_RUN');self.assertEqual(self.real['real_or_human_requirements'],'NOT_RUN')
    def test_TT47(self):
        python=next(e for e in self.registry['entries'] if e['id']=='I64-Python');gx=next(e for e in self.registry['entries'] if e['id']=='I64-GX')
        reader=t.Reader(ROOT,t.LIMITS);p=t.discover(reader,python);g=t.discover(reader,gx);self.assertNotEqual(p,g);self.assertNotIn('testing/gi39_interleavings/support.py',p);self.assertIn('testing/gi39_interleavings/support.py',g)
    def test_TT48(self):
        total=t.summary(self.real['entries']);self.assertEqual(total,self.real['summary']);self.assertEqual((total['entries'],total['group_occurrences'],total['test_occurrences'],total['scenario_rows']),(12,44,1294,388));self.assertEqual(total['missingness']['RAW_NOT_RECORDED'],2);self.assertEqual(self.exit,1)
