# SPDX-License-Identifier: GPL-3.0-only
"""PG64: new synthetic suites, stores, channels and directories only."""
import ast
import contextlib
import copy
import io
import json
import os
from pathlib import Path
import signal
import subprocess
import sys
import tempfile
import types
import unittest
from unittest.mock import patch
from testing.prospective_capture_paged import capture as p, worker as w
c=p.c
ROOT=p.ROOT
ROOTS=[];CHILDREN=[];DETAILS=[]
RID='11111111-1111-4111-8111-111111111111';SID='22222222-2222-4222-8222-222222222222'


@contextlib.contextmanager
def owned():
    row=dict(ownership_verified=False,removed=False,sibling_preserved=False);ROOTS.append(row)
    with tempfile.TemporaryDirectory(prefix='i73-own-') as temp:
        base=Path(temp);root=base/'packet';root.mkdir();owner=c.OwnedRoot(root);sibling=base/'sibling';sibling.write_bytes(b'SYNTHETIC_SIBLING')
        try:yield base,root,owner
        finally:owner.verify();row['ownership_verified']=True;row['sibling_preserved']=sibling.read_bytes()==b'SYNTHETIC_SIBLING'
    row['removed']=not base.exists()


class ExampleStore:
    calls=0
    def __init__(self,path,run_id,store_id,role,reducer,genesis,*,hook=None):
        type(self).calls+=1
        if path=='raise':raise LookupError('SYNTHETIC')
        self.result=dict(head=dict(run_id=run_id,store_id=store_id),state={});self.snapshots=0
    def snapshot(self):self.snapshots+=1;return self.result


def discard(fn,*args,**kwargs):fn(*args,**kwargs)


def make_store(path='synthetic',rid=RID,sid=SID):return ExampleStore(path,rid,sid,'CLIENT',None,None)


def example(methods,domain=False,module='pg_synthetic',name='Example',records=False):
    cls=type(name,(unittest.TestCase,),dict(__module__=module,**methods));ids=[module+'.'+name+'.'+k for k in sorted(methods)]
    entry=dict(id='P01_SYNTHETIC_ONLY',expected_test_ids=ids,expected_tests=len(ids),expected_groups={module:len(ids)},group_policies={module:dict(target='SYNTHETIC_COMPONENT_ONLY',domain_required=domain,no_store_reason=None if domain else 'SYNTHETIC_UNIT_NO_DURABLE_BOUNDARY')},record_sources=[dict(module='pg_records',field='RECORDS',raw_pointer='/scenarios')] if records else [],method_bindings={tid:dict(status='SOURCE_DERIVED_EXPECTATION',scope='SYNTHETIC_ONLY') for tid in ids},expected_raw_scenarios=1 if records else 0,expected_scenario_multiplicity={'SYNTHETIC':1} if records else {})
    return cls,entry


def run_suite(cls,entry,records=None,before=None,after=None):
    class Result(unittest.TestResult):
        def __init__(self):super().__init__();self.passed=[]
        def addSuccess(self,test):self.passed.append(test.id());return super().addSuccess(test)
    if before:before()
    result=Result();unittest.defaultTestLoader.loadTestsFromTestCase(cls).run(result)
    if after:after()
    raw=dict(status='PASS' if result.wasSuccessful() else 'FAIL',tests_run=result.testsRun,passed=result.passed,failures=[t.id() for t,_ in result.failures],errors=[t.id() for t,_ in result.errors],skipped=[t.id() for t,_ in result.skipped],scenarios=copy.deepcopy(records or []),case_test_map={'SYNTHETIC':[entry['expected_test_ids'][0]]} if records else {})
    print(json.dumps(raw,separators=(',',':')));return 0 if result.wasSuccessful() else 1


def all_events(root,side):
    # Only small synthetic artifacts are materialized by tests, never by collector.
    return [e for page in side.get('pages',[]) for e in json.loads((root/page['name']).read_text())['events']]


def fixture_authority(root,reg):
    for name in p.authority_inputs()|{p.REGISTRY}:
        dest=root/name;dest.parent.mkdir(parents=True,exist_ok=True);dest.write_bytes(b'SYNTHETIC_COMPONENT_PIN')
    (root/p.REGISTRY).write_bytes(p.encode(reg))
    (root/'docs/validation/D5-I73-tests-raw.json').write_bytes(p.encode(dict(status='PASS',tests_run=64,functional_campaigns_executed=0,forbidden_imports=[])))
    pin='testing/prospective_capture_paged/README.md';seal=dict(artifacts={pin:c.sha((root/pin).read_bytes())});(root/'docs/validation/D5-I73-integrity.json').write_bytes(p.encode(seal))
    approved=dict(schema='d5.paged-capture-authority.v1',phase='I74_EXPLICITLY_APPROVED',scopes=['P01'],registry_sha256=c.sha((root/p.REGISTRY).read_bytes()),capture_inputs={n:c.sha((root/n).read_bytes()) for n in p.authority_inputs()})
    (root/p.AUTHORITY).write_bytes(p.encode(approved));return approved


class PagedTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):cls.registry=p.read_registry()
    def setUp(self):self.observations=[]
    def err(self,code,fn,*args,**kwargs):
        with self.assertRaises(c.CaptureFault) as got:fn(*args,**kwargs)
        self.assertEqual(got.exception.code,code);self.observations.append(dict(expected=code,observed=got.exception.code))
    def suite(self,methods,*,domain=False,module='pg_synthetic',name='Example',policies=(),constructor=None,observed=(),limits=None,records=None,before=None,after=None,verify=True):
        cls,entry=example(methods,domain,module,name,records is not None);data=types.ModuleType('pg_records');data.RECORDS=records if records is not None else []
        with owned() as (base,root,owner),patch.dict(sys.modules,{'pg_records':data}):
            output=io.StringIO();side=w.exercise(entry,lambda:run_suite(cls,entry,data.RECORDS,before,after),output,owner,policies,observed,constructor,limits)
            raw=json.loads(output.getvalue()) if output.getvalue() else None
            if verify and side.get('status')=='TRACE_CAPTURED_PENDING_SUFFICIENCY_REVIEW':
                check=p.validate_pages(p.evidence_reader(base),'packet',side,limits);self.assertEqual(check['events'],side['event_count'])
            events=all_events(root,side);self.observations.append(dict(status=side['status'],events=side.get('event_count'),raw_tests=raw.get('tests_run') if raw else None))
            return side,raw,events
    def small(self):return self.suite({'test_one':lambda s:s.assertEqual(1,1)})
    def copy_registry(self,root):
        names={p.REGISTRY,c.REGISTRY,'docs/validation/D5-I72-design-review.json'}|{q['source']['path'] for q in self.registry['policies']}|{self.registry['constructor_observer']['source']['path']}
        for n in names:dest=root/n;dest.parent.mkdir(parents=True,exist_ok=True);dest.write_bytes((ROOT/n).read_bytes())
    def page_fixture(self,root,owner,n=3,limits=None):
        sink=p.PageSink(owner,RID,limits)
        for i in range(n):sink.append(dict(event='NOTE',sequence=i,test_frame_id=None))
        sink.close();return sink,dict(capture_run_id=RID,pages=sink.manifest,frames=[],event_count=n,pages_bytes=sink.total_bytes)
    def test_PG01(self):
        with owned() as (base,root,owner):
            self.err('I74_AUTHORIZATION_REQUIRED',p.authority,base,'P01',self.registry)
            with patch.object(w.p,'read_registry',return_value=self.registry),patch.object(w.importlib,'import_module',side_effect=AssertionError('NO_IMPORT')) as imp,contextlib.redirect_stderr(io.StringIO()):
                self.assertEqual(w.main(['P01','4','5','6','7',RID],base),2);imp.assert_not_called()
    def test_PG02(self):
        with owned() as (base,root,owner):
            fixture_authority(base,self.registry);(base/'testing/prospective_capture_paged/capture.py').write_bytes(b'CHANGED');self.err('STALE_AUTHORITY',p.authority,base,'P01',self.registry)
            self.copy_registry(base);(base/'docs/validation/D5-I72-design-review.json').write_bytes(b'{}');self.err('STALE_CONTRACT',p.read_registry,base)
    def test_PG03(self):
        for bad in ['P02','../P01','python','P01 --anything']:self.err('INVALID_SCOPE',p.scope,bad)
        with patch.object(p,'launch') as launch,contextlib.redirect_stdout(io.StringIO()):self.assertEqual(p.main(['--module','anything']),2);launch.assert_not_called()
    def test_PG04(self):
        side,raw,events=self.small();entry=copy.deepcopy(self.registry['entry'])
        self.err('INVALID_RESULT_BINDING',c.aggregate_capture,side,[],raw,entry)
        self.assertEqual(len(set(entry['expected_test_ids'])),321);self.assertEqual(sum(entry['expected_groups'].values()),321)
    def test_PG05(self):
        with owned() as (base,root,owner):
            (root/'a.py').write_text('a');entry=dict(runner_explicit_input_paths=[],runner_discovery_patterns=['packet/*.py'],runner_effective_inputs={})
            before=c.runner_files(base,entry);(root/'b.py').write_text('b');after=c.runner_files(base,entry);self.assertEqual(c.compare_inputs(before,after)['status'],'STALE_INPUTS')
            (root/'b.py').unlink();(root/'a.py').write_text('different');self.assertEqual(c.compare_inputs(before,c.runner_files(base,entry))['changed_runtime'],['packet/a.py'])
            (root/'doc.md').write_text('a');entry['runner_explicit_input_paths']=['packet/doc.md'];before=c.runner_files(base,entry);(root/'doc.md').write_text('b');self.assertEqual(c.compare_inputs(before,c.runner_files(base,entry))['status'],'DOCUMENT_ONLY_CHANGE_REVIEW_PENDING')
    def test_PG06(self):
        before=c.sha((ROOT/'docs/validation/D5-I71-P01/sidecar.json').read_bytes())
        with owned() as (base,root,owner):
            self.copy_registry(base);(base/c.REGISTRY).write_text('{}');self.err('STALE_LEGACY_REGISTRY',p.read_registry,base)
        self.assertEqual(before,c.sha((ROOT/'docs/validation/D5-I71-P01/sidecar.json').read_bytes()))
    def test_PG07(self):
        self.assertEqual(p.plan()['status'],'NOT_RUN_I74_AUTHORIZATION_REQUIRED');self.assertFalse(p.plan()['functional_execution_authorized']);self.assertEqual(forbidden(),[])
    def test_PG08(self):
        with owned() as (base,root,owner):
            approved=fixture_authority(base,self.registry);self.assertEqual(p.authority(base,'P01',self.registry),approved)
            self.assertFalse((ROOT/p.AUTHORITY).exists());self.assertEqual(self.registry['functional_execution_authorized'],False)
        self.observations.append(dict(authority_scope='SYNTHETIC_ROOT_ONLY_NOT_INDEPENDENT_ATTESTATION'))
    def test_PG09(self):
        with owned() as (base,root,owner):
            e=dict(event='N',sequence=0);n=p.PageSink(owner,RID).size(1,len(p.encode(e)));sink=p.PageSink(owner,RID,dict(page_bytes=n));sink.append(e);sink.close();self.assertEqual(sink.manifest[0]['bytes'],n)
    def test_PG10(self):
        with owned() as (base,root,owner):
            e=dict(event='N',sequence=0);n=p.PageSink(owner,RID).size(1,len(p.encode(e)));sink=p.PageSink(owner,RID,dict(page_bytes=n));sink.append(e);sink.append(dict(e,sequence=1));sink.close();self.assertEqual([q['event_count'] for q in sink.manifest],[1,1])
    def test_PG11(self):
        with owned() as (base,root,owner):self.err('EVENT_SIZE_BUDGET',p.PageSink(owner,RID).append,dict(event='N',sequence=0,value='x'*4096))
    def test_PG12(self):
        with owned() as (base,root,owner):
            e=dict(event='N',sequence=0);n=p.PageSink(owner,RID).size(1,len(p.encode(e)));sink=p.PageSink(owner,RID,dict(page_bytes=n,pages=2));sink.append(e);sink.append(dict(e,sequence=1));self.err('PAGE_COUNT_BUDGET',sink.append,dict(e,sequence=2));self.assertEqual(len(sink.manifest),2)
        with owned() as (base,root,owner):
            sink=p.PageSink(owner,RID,dict(event_pages_total_bytes=n-1));self.err('PAGES_TOTAL_BUDGET',sink.append,e)
    def test_PG13(self):
        with owned() as (base,root,owner):
            sink=p.PageSink(owner,RID)
            for i in range(131072):sink.append(dict(event='N',sequence=i,test_frame_id=None))
            self.err('EVENT_CAMPAIGN_BUDGET',sink.append,dict(event='N',sequence=131072));sink.close();self.assertEqual(len(sink),131072);self.assertLessEqual(sink.total_bytes,64*1024*1024)
    def test_PG14(self):
        def test(s):
            for _ in range(2049):s.assertTrue(True)
        side,raw,events=self.suite({'test_many':test},limits=dict(page_bytes=32768),verify=False)
        self.assertIn('EVENT_TEST_BUDGET',side['errors']);self.assertEqual(side['frames'][0]['event_count'],2048);self.assertEqual(raw['status'],'PASS')
    def test_PG15(self):
        with owned() as (base,root,owner):
            sink,side=self.page_fixture(root,owner);bad=copy.deepcopy(side);bad['pages'][0]['page_index']=2
            self.err('INVALID_PAGE_HEADER',p.validate_pages,p.evidence_reader(base),'packet',bad)
            bad=copy.deepcopy(side);bad['pages']=[];self.err('PAGE_SET_MISMATCH',p.validate_pages,p.evidence_reader(base),'packet',bad)
            b=json.loads((root/sink.manifest[0]['name']).read_text());b.update(events=[],event_count=0,last_sequence=-1);bb=p.encode(b);(root/sink.manifest[0]['name']).write_bytes(bb);side['pages'][0].update(bytes=len(bb),sha256=c.sha(bb));self.err('EMPTY_PAGE',p.validate_pages,p.evidence_reader(base),'packet',side)
    def test_PG16(self):
        with owned() as (base,root,owner):
            _,side=self.page_fixture(root,owner);side['pages'][0]['sha256']='0'*64;self.err('INVALID_PACKET_BINDING',p.validate_pages,p.evidence_reader(base),'packet',side)
        with owned() as (base,root,owner):
            _,side=self.page_fixture(root,owner);page=side['pages'][0];file=root/page['name'];data=json.loads(file.read_text());data['page_index']=True;b=p.encode(data);file.write_bytes(b);page.update(bytes=len(b),sha256=c.sha(b));self.err('INVALID_PAGE_HEADER',p.validate_pages,p.evidence_reader(base),'packet',side)
    def test_PG17(self):
        with owned() as (base,root,owner):
            _,side=self.page_fixture(root,owner);page=side['pages'][0];file=root/page['name'];d=json.loads(file.read_text());d['events'][1]['sequence']=0;b=p.encode(d);file.write_bytes(b);page.update(bytes=len(b),sha256=c.sha(b));self.err('INVALID_EVENT_SEQUENCE',p.validate_pages,p.evidence_reader(base),'packet',side)
    def test_PG18(self):
        def test(s):
            for i in range(12):s.assertEqual(i,i)
        side,raw,events=self.suite({'test_many':test},limits=dict(page_bytes=900));self.assertGreater(len(side['pages']),2);self.assertEqual(side['frames'][0]['event_end'],side['event_count'])
    def test_PG19(self):
        side,raw,events=self.suite({'test_a':lambda s:s.assertTrue(True),'test_b':lambda s:s.assertFalse(False)});self.assertEqual(len(side['pages']),1);self.assertEqual(len(side['frames']),2)
    def test_PG20(self):
        side,raw,events=self.suite({'test_a':lambda s:s.assertTrue(True)},before=make_store,constructor=ExampleStore)
        self.assertTrue(any(e['test_frame_id'] is None for e in events));self.assertEqual(side['frames'][0]['construction_refs'],[])
    def test_PG21(self):
        with owned() as (base,root,owner):
            _,side=self.page_fixture(root,owner);name='packet/'+side['pages'][0]['name'];size=(base/name).stat().st_size;reader=p.evidence_reader(base,dict(evidence_read_bytes=size))
            reader.read(name);self.err('READ_BUDGET',reader.read,name)
    def test_PG22(self):
        with owned() as (base,root,owner):
            sink,side=self.page_fixture(root,owner,300,dict(page_bytes=900));self.assertEqual(sink.chunks,[]);self.assertFalse(hasattr(sink,'__getitem__'));self.assertLessEqual(sink.peak_buffer_bytes,900);self.assertGreater(len(sink.manifest),10)
    def test_PG23(self):
        with owned() as (base,root,owner):
            sink=p.PageSink(owner,RID);sink.append(dict(sequence=0,event='N'))
            with patch.object(owner,'create',side_effect=OSError('SYNTHETIC_DISK_FULL')):self.assertRaises(OSError,sink.close)
            self.assertFalse(sink.closed);self.assertEqual(sink.manifest,[])
        with patch.object(p.PageSink,'flush',side_effect=OSError('SYNTHETIC_DISK_FULL')):
            side,raw,_=self.suite({'test_a':lambda s:s.assertTrue(True)},verify=False);self.assertIn('PAGE_FINALIZATION_ERROR',side['errors']);self.assertEqual(raw['status'],'PASS')
        with patch.object(p,'write_all',side_effect=OSError('SYNTHETIC_WRITE_FAILED')):
            side,raw,_=self.suite({'test_a':lambda s:discard(list,(s.assertTrue(True) for _ in range(10))),'test_b':lambda s:s.assertTrue(True)},limits=dict(page_bytes=900),verify=False)
            self.assertIn('PAGE_WRITE_ERROR',side['errors']);self.assertEqual(raw['tests_run'],1);self.assertEqual(raw['status'],'PASS')
    def test_PG24(self):
        records=[]
        def test(s):records.append(dict(case='SYNTHETIC'));s.assertTrue(True)
        side,raw,_=self.suite({'test_a':test},records=records,verify=False);self.assertEqual(side['status'],'INCOMPLETE_CAPTURE');self.assertIn('INCOMPLETE_CHILD_SCENARIO',side['frames'][0]['missing'])
    def test_PG25(self):
        box={}
        def test(s):
            st=make_store();out=st.result;s.assertIs(st.snapshot(),out);s.assertEqual(st.snapshots,1);box['st']=st
        side,_,_=self.suite({'test_a':test},observed=[(ExampleStore,'snapshot')]);self.assertEqual(box['st'].snapshots,1);self.assertTrue(side['observers_restored'])
    def test_PG26(self):
        def test(s):
            with s.subTest(n=1):s.assertEqual(1,2)
        side,raw,_=self.suite({'test_a':test});self.assertEqual(raw['status'],'FAIL');self.assertEqual(side['frames'][0]['result'],'FAIL')
    def test_PG27(self):
        side,_,events=self.suite({'test_a':lambda s:discard(s.assertRaises,ValueError)})
        self.assertIn('EXPECTED_EXCEPTION_DECLARED',[e['event'] for e in events]);self.assertNotIn('EXPECTED_EXCEPTION_EXIT_OBSERVED',[e['event'] for e in events])
    def test_PG28(self):
        side,raw,_=self.suite({'test_a':lambda s:s.assertIsInstance('value',str)},verify=False);self.assertEqual(raw['status'],'PASS');self.assertIn('OPERAND_NOT_RECORDED',side['frames'][0]['missing']);self.assertEqual(side['status'],'INCOMPLETE_CAPTURE')
    def test_PG29(self):
        records=[]
        def test(s):records.append(dict(case='SYNTHETIC',run_id=RID,events=[],oracles=[],status='PASS'));s.assertTrue(True)
        side,raw,_=self.suite({'test_a':test},records=records,after=lambda:records[0].update(status='CHANGED'),verify=False);self.assertIn('RECORD_MUTATED_AFTER_TEST',side['errors'])
    def test_PG30(self):
        old=json.loads((ROOT/c.REGISTRY).read_text())['entries'][0];self.assertEqual(self.registry['entry']['method_bindings'],old['method_bindings']);self.assertEqual(len(old['method_bindings']),321)
        for case in ['DF01','DR01']:
            pol=next(v for v in self.registry['policies'] if v['case']==case);a=pol['source'];t=ast.parse((ROOT/a['path']).read_text());cl=next(n for n in t.body if isinstance(n,ast.ClassDef) and n.name==a['class_name']);fn=next(n for n in cl.body if isinstance(n,ast.FunctionDef) and n.name==a['function']);self.assertEqual(fn.lineno,a['line'])
    def test_PG31(self):
        side,raw,_=self.suite({'test_a':lambda s:s.assertTrue(True),'test_b':lambda s:s.assertTrue(True)},limits=dict(events_campaign=2),verify=False);self.assertEqual(raw['status'],'PASS');self.assertEqual(raw['tests_run'],1);self.assertIn('INCOMPLETE_TEST_SET',side['errors']);self.assertIn('INVALID_TEST_COUNT',side['errors'])
    def test_PG32(self):
        original=ExampleStore.snapshot
        def test(s):ExampleStore.snapshot=lambda self:None
        side,_,_=self.suite({'test_a':test},observed=[(ExampleStore,'snapshot')],constructor=ExampleStore,verify=False);self.assertIn('OBSERVER_IDENTITY_CHANGED',side['errors']);self.assertIs(ExampleStore.snapshot,original)
    def policy_case(self,case):
        pol=next(v for v in self.registry['policies'] if v['case']==case);module,cls,method=pol['test_id'].split('.')
        def test(s):
            if pol['classification']=='NEGATIVE_DOMAIN':make_store()
            s.assertEqual(1,1)
        side,raw,_=self.suite({method:test},domain=True,module=module,name=cls,policies=[pol],constructor=ExampleStore)
        self.assertEqual(side['frames'][0]['missing'],[]);self.assertEqual(side['status'],'TRACE_CAPTURED_PENDING_SUFFICIENCY_REVIEW');self.assertEqual(side['frames'][0]['domain_scope']['status'],'NOT_APPLICABLE' if pol['classification']=='NO_STORE_CONTROL' else 'NEGATIVE_DOMAIN_CONSTRUCTION_REFERENCE')
        return side
    def test_PG33(self):self.policy_case('DF01')
    def test_PG34(self):self.policy_case('DF02')
    def test_PG35(self):self.policy_case('DF48')
    def test_PG36(self):self.policy_case('DR01')
    def test_PG37(self):self.policy_case('DR02')
    def test_PG38(self):
        side=self.policy_case('DF07');self.assertTrue(all(d['authority']==p.DECLARATION for d in side['construction_declarations'].values()));self.assertTrue(all(v['identity'] is None for v in side['owner_contexts'].values()))
    def test_PG39(self):self.policy_case('DF43')
    def test_PG40(self):
        side,_,_=self.suite({'test_new':lambda s:s.assertTrue(True)},domain=True,policies=self.registry['policies'],verify=False);self.assertIn('DOMAIN_IDENTITY_NOT_RECORDED',side['frames'][0]['missing'])
    def test_PG41(self):
        class Bad:
            def __init__(self,x):pass
        with owned() as (base,root,owner):
            _,entry=example({'test_a':lambda s:None});rec=p.Recorder(entry,owner);self.err('UNSUPPORTED_OBSERVER_SIGNATURE',rec.constructor,Bad)
        a=self.registry['constructor_observer']['source'];self.assertEqual(c.sha((ROOT/a['path']).read_bytes()),a['sha256'])
        module=types.ModuleType('pg_observer');module.ExampleStore=ExampleStore;path='testing/prospective_capture_paged/test_paged_capture.py'
        reg=dict(observer_specs=[],constructor_observer=dict(module='pg_observer',class_name='ExampleStore',method='__init__',source=dict(path=path,sha256=c.sha((ROOT/path).read_bytes())),signature_parameters=self.registry['constructor_observer']['signature_parameters']))
        with patch.dict(sys.modules,{'pg_observer':module}):
            observed,ctor=w.targets(reg);self.assertEqual(observed,[]);self.assertIs(ctor,ExampleStore)
            reg['constructor_observer']['signature_parameters']=['self'];self.err('UNSUPPORTED_OBSERVER_SIGNATURE',w.targets,reg)
    def test_PG42(self):
        original=ExampleStore.__init__;ExampleStore.calls=0;side,_,_=self.suite({'test_a':lambda s:discard(make_store)},constructor=ExampleStore);self.assertEqual(ExampleStore.calls,1);self.assertIs(ExampleStore.__init__,original);self.assertEqual(len(side['construction_declarations']),1)
    def test_PG43(self):
        side,raw,events=self.suite({'test_a':lambda s:s.assertRaises(LookupError,make_store,'raise')},constructor=ExampleStore);self.assertEqual(raw['status'],'PASS');self.assertEqual(side['construction_declarations'],{});self.assertIn('CONSTRUCTION_EXCEPTION',[e['event'] for e in events])
    def test_PG44(self):
        class NoRepr(str):
            def __repr__(self):raise AssertionError('NO_REPR')
        side,raw,_=self.suite({'test_a':lambda s:discard(make_store,rid=NoRepr(RID))},constructor=ExampleStore,verify=False);self.assertEqual(raw['status'],'PASS');self.assertIn('INVALID_CONSTRUCTION_METADATA',side['errors'])
    def test_PG45(self):
        box=[]
        def test(s):box.extend([make_store(),make_store()])
        side,_,_=self.suite({'test_a':test},constructor=ExampleStore);self.assertEqual(len(side['construction_declarations']),2);self.assertEqual(len(side['frames'][0]['construction_refs']),2)
    def test_PG46(self):
        def test(s):st=make_store();st.result['head']['store_id']=RID;st.snapshot()
        side,raw,_=self.suite({'test_a':test},constructor=ExampleStore,observed=[(ExampleStore,'snapshot')],verify=False);self.assertIn('CONSTRUCTION_HEAD_IDENTITY_CONFLICT',side['errors']);self.assertEqual(next(iter(side['construction_declarations'].values()))['store_id'],SID)
        def reinitialize(s):
            st=make_store();ExampleStore.__init__(st,'synthetic',RID,RID,'CLIENT',None,None)
        side,_,events=self.suite({'test_a':reinitialize},constructor=ExampleStore,verify=False);self.assertIn('CONSTRUCTION_IDENTITY_CHANGED',side['errors']);self.assertEqual(next(iter(side['construction_declarations'].values()))['store_id'],SID);self.assertIn('CONSTRUCTION_IDENTITY_CONFLICT',[e['event'] for e in events])
    def test_PG47(self):
        child=subprocess.Popen([sys.executable,'-B','-c','import json; print(json.dumps({"scope":"SYNTHETIC_CHILD_PROTOCOL"}))'],stdout=subprocess.PIPE,stderr=subprocess.DEVNULL,start_new_session=True)
        try:out,_=child.communicate(timeout=5);self.assertEqual(json.loads(out)['scope'],'SYNTHETIC_CHILD_PROTOCOL')
        finally:
            if child.poll() is None:os.killpg(child.pid,signal.SIGINT);child.wait(timeout=5)
            CHILDREN.append(dict(exitcode=child.returncode,kind='SYNTHETIC_PROTOCOL'))
        side,_,_=self.small();self.assertEqual(side['construction_declarations'],{});self.assertIn('NOT_PARENT_INSTRUMENTATION',side['child_context_scope'])
    def test_PG48(self):
        side,_,_=self.suite({'test_a':lambda s:s.assertTrue(True)},domain=True,constructor=ExampleStore,before=make_store,verify=False);self.assertTrue(side['construction_declarations']);self.assertIn('DOMAIN_IDENTITY_NOT_RECORDED',side['frames'][0]['missing'])
    def test_PG49(self):
        with owned() as (base,root,owner):
            _,entry=example({});out=io.StringIO();side=w.exercise(entry,lambda:print('x'*100),out,owner,limits=dict(raw_bytes=10));self.assertIn('RAW_BUDGET',side['errors']);self.assertLessEqual(len(out.getvalue()),10)
    def test_PG50(self):
        side,_,_=self.suite({'test_a':lambda s:s.assertTrue(True)},limits=dict(index_sidecar_bytes=100),verify=False);self.assertEqual(side['errors'],['SIDECAR_BUDGET'])
        self.err('PACKAGE_FILE_BUDGET',p.package_size,{'context.json':13*1024*1024})
    def test_PG51(self):
        self.assertEqual(c.digest_value(b'x'*(16*1024*1024))['status'],'NOT_RECORDED');self.assertEqual(c.digest_value(b'x'*(16*1024*1024-100))['status'],'OBSERVED_DIGEST')
        value=0
        for _ in range(34):value=[value]
        self.assertEqual(c.digest_value(value)['reason'],'OPERAND_DEPTH');self.err('STRING_BUDGET',c.strict_json,p.encode('x'*4097));self.err('JSON_DEPTH',c.strict_json,b'['*34+b'0'+b']'*34)
    def test_PG52(self):
        side,_,_=self.suite({'test_a':lambda s:s.assertTrue(True),'test_b':lambda s:s.assertTrue(True)},limits=dict(frames=1),verify=False);self.assertIn('FRAME_BUDGET',side['errors'])
        side,_,_=self.suite({'test_a':lambda s:discard(make_store)},constructor=ExampleStore,limits=dict(refs=1),verify=False);self.assertIn('REFERENCE_BUDGET',side['errors']);self.assertLessEqual(len(side['owner_contexts']),1)
    def test_PG53(self):
        with owned() as (base,root,owner):
            (root/'a').write_bytes(b'abc');(root/'b').write_bytes(b'def');reader=c.Reader(base,dict(unique_bytes=4));reader.read('packet/a');self.err('UNIQUE_BUDGET',reader.read,'packet/b')
            reader=c.Reader(base,dict(read_bytes=5));reader.read('packet/a');self.err('READ_BUDGET',reader.read,'packet/a')
            reader=c.Reader(base,dict(paths=1));reader.read('packet/a');self.err('PATH_BUDGET',reader.read,'packet/b')
    def test_PG54(self):
        self.err('PACKAGE_BUDGET',p.package_size,{'OWNER':2},dict(package_bytes=1));self.assertEqual(p.LIMITS['package_bytes'],112*1024*1024+4096)
        with owned() as (base,root,owner):
            (root/'a').write_bytes(b'12');reader=p.evidence_reader(base,dict(evidence_read_bytes=3));reader.read('packet/a');self.err('READ_BUDGET',reader.read,'packet/a')
    def test_PG55(self):
        class Wait:
            def wait(self,timeout):self.timeout=timeout;raise subprocess.TimeoutExpired('SYNTHETIC',timeout)
        waiter=Wait();self.assertFalse(p.wait_worker(waiter,0.01));self.assertEqual(waiter.timeout,0.01);self.assertEqual(p.LIMITS['campaign_seconds'],900)
        r,wr=os.pipe()
        try:self.err('WORKER_TIMEOUT',c.receive_line,r,0.01)
        finally:os.close(r);os.close(wr)
    def test_PG56(self):
        side,raw,events=self.suite({'test_a':lambda s:s.assertTrue(True)},limits=dict(events_campaign=3),verify=False);self.assertIn('EVENT_CAMPAIGN_BUDGET',side['errors']);self.assertEqual(raw['status'],'PASS');self.assertNotIn('TEST_END',[e['event'] for e in events])
    def test_PG57(self):
        with owned() as (base,root,owner):
            fd=owner.create('keep');p.write_all(fd,b'ORIGINAL');os.close(fd)
            with self.assertRaises(FileExistsError):owner.create('keep')
            self.assertEqual((root/'keep').read_bytes(),b'ORIGINAL')
            dest=base/p.DESTINATION;dest.mkdir(parents=True);(dest/'keep').write_bytes(b'OLD')
            with patch.object(p,'read_registry',return_value=self.registry),patch.object(p,'authority',return_value={}),patch.object(c.subprocess,'Popen') as launch:
                with self.assertRaises(FileExistsError):p.launch('P01',base)
                launch.assert_not_called();self.assertEqual((dest/'keep').read_bytes(),b'OLD')
    def test_PG58(self):
        with owned() as (base,root,owner):
            (root/'link').symlink_to(base/'sibling');self.err('NONREGULAR_FILE',c.Reader(base).read,'packet/link')
            os.mkfifo(root/'pipe');self.err('NONREGULAR_FILE',c.Reader(base).read,'packet/pipe')
            moved=base/'moved';root.rename(moved);root.mkdir()
            try:self.err('OWNER_ROOT_CHANGED',owner.verify)
            finally:root.rmdir();moved.rename(root)
    def test_PG59(self):
        with owned() as (base,root,owner):
            _,side=self.page_fixture(root,owner);bad=copy.deepcopy(side);bad['pages'][0]['name']='../sibling';self.err('PAGE_SET_MISMATCH',p.validate_pages,p.evidence_reader(base),'packet',bad)
            (root/'event-0002.json').write_text('{}');self.err('PAGE_SET_MISMATCH',p.validate_pages,p.evidence_reader(base),'packet',side)
        self.err('PACKAGE_SET_MISMATCH',p.package_size,{'../sibling':1})
    def test_PG60(self):
        self.fake_worker(check_ready=True)
        self.err('INVALID_WORKER_RELEASE',p.verify_release,dict(event='RELEASE',lease=SID),RID)
    def fake_worker(self,check_ready=False,wrong_owner=False):
        with owned() as (base,root,owner):
            rawfd=owner.create('raw');sidefd=owner.create('side');d=owner.directory();child=subprocess.Popen([sys.executable,'-B','-c','import sys; sys.stdin.read()'],stdin=subprocess.PIPE,stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL,start_new_session=True)
            try:
                identity=dict(pid=child.pid,pgid=child.pid,lease=owner.nonce)
                if check_ready:
                    st=os.fstat(d);msg=dict(event='READY',scope='P01',lease=owner.nonce,pid=child.pid,pgid=child.pid,raw_inode=os.fstat(rawfd).st_ino,sidecar_inode=os.fstat(sidefd).st_ino,directory_device=st.st_dev,directory_inode=st.st_ino)
                    p.verify_ready(msg,owner.nonce,child.pid,rawfd,sidefd,d);self.err('INVALID_WORKER_IDENTITY',p.verify_ready,dict(msg,pid=child.pid+1),owner.nonce,child.pid,rawfd,sidefd,d)
                if wrong_owner:self.err('INVALID_WORKER_IDENTITY',c.stop_owned,child,owner,dict(identity,lease=SID))
            finally:
                done=c.stop_owned(child,owner,dict(pid=child.pid,pgid=child.pid,lease=owner.nonce));child.stdin.close();CHILDREN.append(dict(exitcode=child.returncode,kind='SYNTHETIC_CHANNEL'));os.close(rawfd);os.close(sidefd);os.close(d)
            self.assertEqual(done['status'],'OWN_GROUP_GONE');self.assertNotEqual(child.returncode,-signal.SIGKILL)
    def test_PG61(self):self.fake_worker(wrong_owner=True)
    def test_PG62(self):
        for value in ['dev/a','run_data/a','private/a','../a','.aws/key']:self.err('INVALID_PUBLIC_PATH',c.public_path,value)
        with owned() as (base,root,owner):
            fd=owner.directory()
            try:channel=p.ChannelRoot(fd,owner.nonce);channel.verify();self.err('INVALID_DIRECTORY_OWNER',p.ChannelRoot,fd,SID)
            finally:os.close(fd)
            self.assertEqual((base/'sibling').read_bytes(),b'SYNTHETIC_SIBLING')
    def test_PG63(self):
        self.assertEqual(forbidden(),[]);self.assertFalse((ROOT/p.AUTHORITY).exists());self.assertFalse((ROOT/p.DESTINATION).exists());self.assertFalse(p.plan()['functional_execution_authorized'])
    def test_PG64(self):
        # Exercise the production launcher with a separately owned synthetic producer.
        # Its factory is injected here only; the public launcher never accepts a module.
        with owned() as (base,root,owner):
            (root/'runner.py').write_bytes(b'SYNTHETIC_INPUT');before={'packet/runner.py':c.sha((root/'runner.py').read_bytes())}
            _,entry=example({'test_one':lambda s:None});entry.update(runner_explicit_input_paths=['packet/runner.py'],runner_discovery_patterns=[],runner_effective_inputs=before)
            reg=dict(entry=entry);approved=dict(capture_inputs=before);real_popen=subprocess.Popen;children=[]
            script="""import sys,os,json,unittest
from testing.prospective_capture_paged import capture as p,worker as w
c=p.c
scope,side,ready,release,directory,lease=sys.argv[1:7]
side,ready,release,directory=map(int,(side,ready,release,directory))
entry=json.loads(sys.argv[7]);before=json.loads(sys.argv[8]);owner=p.ChannelRoot(directory,lease);st=os.fstat(directory)
message=dict(event='READY',scope='P01',lease=lease,pid=os.getpid(),pgid=os.getpgid(0),raw_inode=os.fstat(1).st_ino,sidecar_inode=os.fstat(side).st_ino,directory_device=st.st_dev,directory_inode=st.st_ino)
c.write_json_fd(ready,message,4096);p.write_all(ready,b'\\n');os.close(ready)
p.verify_release(c.receive_line(release,20),lease);os.close(release)
class Example(unittest.TestCase):
 def test_one(self):self.assertEqual(1,1)
Example.__module__='pg_synthetic'
def main():
 result=unittest.TestResult();unittest.defaultTestLoader.loadTestsFromTestCase(Example).run(result)
 print(json.dumps(dict(status='PASS',tests_run=1,passed=entry['expected_test_ids'],failures=[],errors=[],skipped=[],scenarios=[],case_test_map={})));return 0
sidecar=w.exercise(entry,main,w.Tee(sys.stdout),owner)
sidecar.update(runner_inputs_before=before,runner_inputs_after=before,capture_inputs_before=before,capture_inputs_after=before)
c.write_json_fd(side,sidecar,p.LIMITS['index_sidecar_bytes']);os.close(side);os.close(directory)
sys.exit(0 if sidecar['status']=='TRACE_CAPTURED_PENDING_SUFFICIENCY_REVIEW' else 1)
"""
            def producer(cmd,**kwargs):
                kwargs['cwd']=ROOT
                child=real_popen([sys.executable,'-B','-c',script,*cmd[-6:],json.dumps(entry),json.dumps(before)],**kwargs);children.append(child);return child
            (base/'docs/validation').mkdir(parents=True)
            with patch.object(p,'read_registry',return_value=reg),patch.object(p,'authority',return_value=approved),patch.object(c.subprocess,'Popen',side_effect=producer):context=p.launch('P01',base)
            for child in children:CHILDREN.append(dict(exitcode=child.returncode,kind='SYNTHETIC_PAGED_LAUNCH'))
            self.assertEqual(context['capture_status'],'TRACE_CAPTURED_PENDING_SUFFICIENCY_REVIEW',context.get('error_code'));self.assertEqual(context['cleanup']['status'],'OWN_GROUP_GONE')
            self.assertEqual(json.loads((base/p.LAUNCH_COPY).read_text()),context)
            side=json.loads((base/p.DESTINATION/'sidecar.json').read_text());reader=p.evidence_reader(base);p.package_names(reader,p.DESTINATION,side)
            self.assertEqual(side['semantic_baseline'],dict(SUPPORTS_BOUNDED=81,PARTIAL=3));self.assertFalse(side['closure']);self.assertFalse(side['D5_closed']);self.assertEqual(side['sufficiency'],'REVIEW_PENDING')
            self.observations.append(dict(scope='SYNTHETIC_PRODUCER_ONLY',page_validation=context['page_validation'],cleanup=context['cleanup']))



def forbidden():return sorted(n for n in sys.modules if n.startswith(('source_ingest','testing.D5','testing.durable_','testing.gi39_interleavings','testing.causal_frontier_cells','testing.evidence_audit','testing.evidence_trace')))
