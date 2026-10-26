# SPDX-License-Identifier: GPL-3.0-only
"""PF60 uses only stdlib and the new capture components, never historical runtime."""
import ast
import contextlib
import copy
import hashlib
import io
import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import time
import types
import unittest
from unittest.mock import patch
from testing.prospective_capture import capture as c, worker as w

ROOT=Path(__file__).resolve().parents[2]
OWN_ROOTS=[];CHILDREN=[];DETAILS=[]


@contextlib.contextmanager
def own_root():
    root=None;row=None
    try:
        with tempfile.TemporaryDirectory(prefix='i70-own-') as directory:
            root=Path(directory);owner=c.OwnedRoot(root);row=dict(created=True,ownership_verified=False,removed=False);OWN_ROOTS.append(row)
            try:yield root,owner
            finally:owner.verify();row['ownership_verified']=True
    finally:
        if row is not None:row['removed']=not root.exists()


def synthetic(methods,records=None,domain=False):
    cls=type('Example',(unittest.TestCase,),dict(__module__='pf_synthetic',**methods));ids=['pf_synthetic.Example.'+name for name in sorted(methods)]
    group='pf_synthetic';entry=dict(id='PF_FIXTURE',expected_test_ids=ids,expected_tests=len(ids),expected_groups={group:len(ids)},group_policies={group:dict(target='LOCAL_SYNTHETIC_PYTHON',domain_required=domain,no_store_reason=None if domain else 'UNIT_OR_VOLATILE_FIXTURE_NO_DURABLE_BOUNDARY')},record_sources=[],method_bindings={tid:dict(status='SOURCE_DERIVED_EXPECTATION',scope='SYNTHETIC_FIXTURE_ONLY',symbol=tid) for tid in ids},expected_raw_scenarios=0,expected_scenario_multiplicity={})
    if records is not None:entry['record_sources']=[dict(module='pf_synthetic_records',field='RECORDS',raw_pointer='/scenarios')]
    return cls,entry


def exercise(cls,entry,targets=(),records=None,limits=None,resultclass=unittest.TestResult):
    data=types.ModuleType('pf_synthetic_records');data.RECORDS=records if records is not None else []
    resultbox={}
    def main():
        class Result(resultclass):
            def __init__(self):super().__init__();self.passed=[]
            def addSuccess(self,test):self.passed.append(test.id());return super().addSuccess(test)
        result=Result();suite=unittest.defaultTestLoader.loadTestsFromTestCase(cls);suite.run(result);resultbox['result']=result
        ids=entry['expected_test_ids'];bad={t.id() for t,_ in result.failures+result.errors}|{t.id() for t,_ in result.skipped}|{t.id() for t,_ in result.expectedFailures}|{t.id() for t in result.unexpectedSuccesses}
        raw=dict(status='PASS' if result.wasSuccessful() else 'FAIL',tests_run=result.testsRun,passed=result.passed,errors=[t.id() for t,_ in result.errors],failures=[t.id() for t,_ in result.failures],skipped=[t.id() for t,_ in result.skipped],scenarios=copy.deepcopy(data.RECORDS),case_test_map={row['case']:[ids[0]] for row in data.RECORDS})
        print(json.dumps(raw,separators=(',',':')));return 0 if result.wasSuccessful() else 1
    output=io.StringIO()
    with patch.dict(sys.modules,{'pf_synthetic_records':data}):side=w.exercise(entry,main,output,targets,limits)
    return side,json.loads(output.getvalue()) if output.getvalue().strip() else None,resultbox.get('result')


class FakeStore:
    def __init__(self,number=1):self.calls=0;self.number=number;self.value=dict(head=dict(run_id='11111111-1111-4111-8111-111111111111',store_id=f'{self.number:08}-1111-4111-8111-111111111111',seq=1,commit_sha256='a'*64),state=dict(value=1))
    def snapshot(self):self.calls+=1;return self.value
    def perform(self,kind,args=None):self.calls+=1;return self.value


class CaptureTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):cls.registry=c.read_registry()
    def setUp(self):self.observations=[]
    def err(self,code,fn,*args,**kwargs):
        with self.assertRaises(c.CaptureFault) as found:fn(*args,**kwargs)
        self.assertEqual(found.exception.code,code);self.observations.append(dict(expected=code,observed=found.exception.code))
    def catalog(self,index):
        entry=self.registry['entries'][index];old=json.loads((ROOT/'docs/validation/D5-I69-design-review.json').read_text())['capture_catalog'][index]
        self.assertEqual(entry['id'],f'P{index+1:02}');self.assertEqual(c.sha((ROOT/entry['runner_path']).read_bytes()),entry['runner_sha256'])
        for key,value in old.items():self.assertEqual(entry[key],value)
        self.assertEqual(len(entry['expected_test_ids']),entry['expected_tests']);self.assertEqual(len(set(entry['expected_test_ids'])),entry['expected_tests'])
        self.assertNotIn(entry['runner_module'],sys.modules);self.assertEqual(c.invocation(entry['id'])['runner_context_role'],'RUNNER_DECLARATION_NOT_WORKER_ARGV')
        self.assertEqual(entry['new_execution_status'],'NOT_AUTHORIZED_NOT_RUN');self.assertTrue(all(b['status']=='SOURCE_DERIVED_EXPECTATION' for b in entry['method_bindings'].values()))
        DETAILS.append(dict(case=self._testMethodName[5:],scope=entry['id'],tests_not_executed=entry['expected_tests'],runner_sha256=entry['runner_sha256'],status='FIXED_MANIFEST_VERIFIED_NO_IMPORT'))
    def test_PF01(self):self.catalog(0)
    def test_PF02(self):self.catalog(1)
    def test_PF03(self):self.catalog(2)
    def test_PF04(self):self.catalog(3)
    def test_PF05(self):self.catalog(4)
    def test_PF06(self):self.catalog(5)
    def test_PF07(self):self.catalog(6)
    def test_PF08(self):self.catalog(7)
    def test_PF09(self):self.catalog(8)
    def test_PF10(self):self.catalog(9)
    def test_PF11(self):
        cls,e=synthetic(dict(test_a=lambda s:s.assertEqual(1,1),test_b=lambda s:s.assertTrue(True)));side,raw,result=exercise(cls,e)
        self.assertEqual([f['result'] for f in side['frames']],['PASS','PASS']);self.assertTrue(all('ended_ns' in f for f in side['frames']));self.assertEqual(result.testsRun,2);self.assertEqual(len(side['groups']),1)
    def test_PF12(self):
        def fails(s):s.assertEqual(1,2)
        def errors(s):raise ValueError('synthetic')
        def skips(s):s.skipTest('synthetic')
        def sub(s):
            with s.subTest(n=1):s.assertEqual(1,2)
        xfail=unittest.expectedFailure(lambda s:fails(s));unexpected=unittest.expectedFailure(lambda s:s.assertTrue(True))
        cls,e=synthetic(dict(test_a=fails,test_b=errors,test_c=skips,test_d=xfail,test_e=unexpected,test_f=sub));side,raw,result=exercise(cls,e)
        self.assertEqual([f['result'] for f in side['frames']],['FAIL','ERROR','SKIP','EXPECTED_FAILURE','UNEXPECTED_SUCCESS','FAIL']);self.assertEqual(raw['status'],'FAIL');self.assertEqual(result.testsRun,6)
    def test_PF13(self):
        records=[]
        def run(s):
            for i in (1,2):
                st=FakeStore(i);s.assertIs(st.snapshot(),st.value);records.append(dict(case='C01',run_id=st.value['head']['run_id'],events=[],oracles=[],status='PASS'))
        cls,e=synthetic(dict(test_one=run),records,True);e['expected_raw_scenarios']=2;e['expected_scenario_multiplicity']={'C01':2};side,raw,_=exercise(cls,e,[(FakeStore,'snapshot')],records)
        self.assertEqual(len(side['frames']),1);self.assertEqual(len(side['scenario_metadata']),2);self.assertEqual(len(side['frames'][0]['owner_context_refs']),2);self.assertEqual(len(side['frames'][0]['record_links']),2)
    def test_PF14(self):
        cls,e=synthetic(dict(test_one=lambda s:s.assertTrue(True)));side,_,_=exercise(cls,e)
        f=side['frames'][0];self.assertEqual(f['domain_scope']['status'],'NOT_APPLICABLE');self.assertFalse(f['owner_context_refs']);self.assertNotIn('store_id',f);self.assertNotEqual(f['test_frame_id'],f['capture_run_id'])
    def test_PF15(self):
        cls,e=synthetic(dict(test_one=lambda s:None));r=c.Recorder(e);r.start(cls('test_one'));side=r.finish();self.assertIn('UNFINISHED_TEST',side['errors']);self.assertEqual(side['status'],'INVALID_CAPTURE')
    def test_PF16(self):
        cls,e=synthetic(dict(test_one=lambda s:s.assertEqual([1],[1])));side,_,_=exercise(cls,e);events=[v for v in side['events'] if v['event']=='ASSERTION_RETURNED'];self.assertEqual(len(events),1);self.assertEqual(len(side['frames']),1)
    def test_PF17(self):
        store=FakeStore();before=FakeStore.snapshot
        cls,e=synthetic(dict(test_one=lambda s:s.assertIs(store.snapshot(),store.value)),domain=True);side,_,_=exercise(cls,e,[(FakeStore,'snapshot')])
        self.assertEqual(store.calls,1);self.assertIs(FakeStore.snapshot,before);self.assertEqual(side['owner_contexts'][side['frames'][0]['owner_context_refs'][0]]['identity']['store_id'],store.value['head']['store_id'])
    def test_PF18(self):
        err=ValueError('synthetic text not emitted')
        class Source:
            def call(self):raise err
        cls,e=synthetic(dict(test_one=lambda s:None));r=c.Recorder(e);r.install([(Source,'call')])
        try:
            try:Source().call()
            except ValueError as found:self.assertIs(found,err)
        finally:r.restore()
        self.assertEqual(r.events[0]['event'],'CALL_EXCEPTION');self.assertNotIn(str(err),json.dumps(r.events))
    def test_PF19(self):
        store=FakeStore();cls,e=synthetic(dict(test_one=lambda s:s.assertIs(store.snapshot(),store.value)));side,raw,result=exercise(cls,e,[(FakeStore,'snapshot')],limits={'events_test':0})
        self.assertEqual(store.calls,1);self.assertEqual(raw['status'],'PASS');self.assertEqual(side['status'],'INVALID_CAPTURE');self.assertIn('EVENT_TEST_BUDGET',side['errors']);self.assertTrue(side['observers_restored'])
    def test_PF20(self):
        cls,e=synthetic(dict(test_one=lambda s:s.skipTest('synthetic')));original=unittest.TestResult.addSkip;side,_,_=exercise(cls,e);self.assertIs(unittest.TestResult.addSkip,original);self.assertTrue(side['observers_restored'])
        r=c.Recorder(e);self.err('UNSUPPORTED_OBSERVER_API',r.install,[(FakeStore,'absent')]);self.assertIs(unittest.TestResult.addSkip,original);self.assertFalse(r.patches)
    def test_PF21(self):
        identities=[]
        def run(s):
            cm=s.assertRaises(ValueError);identities.append(type(cm))
            with cm:raise ValueError('synthetic')
            s.assertRaises(ValueError,lambda:(_ for _ in ()).throw(ValueError()))
            with s.assertRaisesRegex(ValueError,'synthetic'):raise ValueError('synthetic')
        cls,e=synthetic(dict(test_one=run));side,raw,_=exercise(cls,e)
        self.assertIs(identities[0],unittest.case._AssertRaisesContext);self.assertEqual(raw['status'],'PASS');self.assertEqual(sum(v['event']=='EXPECTED_EXCEPTION_EXIT_OBSERVED' for v in side['events']),3)
    def test_PF22(self):
        class Hostile:
            def __repr__(self):raise AssertionError('repr forbidden')
            @property
            def value(self):raise AssertionError('property forbidden')
        self.assertEqual(c.digest_value(Hostile())['reason'],'UNSUPPORTED_OPERAND');self.assertEqual(c.digest_value(b'12345',{'operand_bytes':2})['reason'],'OPERAND_BUDGET')
        self.assertNotEqual(c.digest_value(b'x')['sha256'],c.digest_value('x')['sha256']);self.assertEqual(c.digest_value({'a':1,'b':2}),c.digest_value({'b':2,'a':1}))
    def test_PF23(self):
        store=FakeStore();cls,e=synthetic(dict(test_one=lambda s:(store.snapshot(),store.perform('A'))));side,raw,_=exercise(cls,e,[(FakeStore,'snapshot'),(FakeStore,'perform')]);self.assertEqual(store.calls,2);self.assertEqual(sum(v['event']=='CALL_RETURN' for v in side['events']),2)
    def test_PF24(self):
        cls,e=synthetic(dict(test_one=lambda s:s.assertTrue(True)));side,_,_=exercise(cls,e);self.assertEqual(side['child_context_scope'],'ONLY_EXISTING_PROTOCOL_RECORDS_NOT_PARENT_INSTRUMENTATION');self.assertNotIn('child_environment',side)
    def test_PF25(self):
        v=c.invocation('P02');self.assertEqual(v['command'][-1],'P02');self.assertEqual(v['runner_context_role'],'RUNNER_DECLARATION_NOT_WORKER_ARGV');self.assertNotIn('/',v['interpreter']['basename']);self.assertEqual(v['interpreter']['normalization'],'PRIVATE_PREFIX_NOT_EMITTED')
    def test_PF26(self):
        v=c.environment();self.assertEqual(set(v),{'python','implementation','build','platform','release','machine','optimize','debug'});self.assertEqual(v['optimize'],0);self.assertTrue(v['debug'])
    def test_PF27(self):
        cls,e=synthetic(dict(test_one=lambda s:s.assertTrue(True)));side,_,_=exercise(cls,e);g=side['groups'][0];self.assertEqual(c.pointer(side,g['context_ref']),side['worker_context']);self.assertEqual(g['context_scope'],'INHERITED_WORKER_CONTEXT')
    def test_PF28(self):
        before=c.sha((ROOT/'docs/validation/D5-I34-results.json').read_bytes())
        with own_root() as (root,owner):
            with self.assertRaises(c.CaptureFault):owner.create('../D5-I34-results.json')
        self.assertEqual(before,c.sha((ROOT/'docs/validation/D5-I34-results.json').read_bytes()))
    def test_PF29(self):
        cls,e=synthetic(dict(test_one=lambda s:s.assertEqual(3,3)));side,_,_=exercise(cls,e);event=next(v for v in side['events'] if v['event']=='ASSERTION_RETURNED');self.assertEqual(event['operands'][0]['sha256'],event['operands'][1]['sha256']);self.assertEqual(side['frames'][0]['source_binding']['status'],'SOURCE_DERIVED_EXPECTATION');self.assertFalse(side['closure'])
    def test_PF30(self):
        cls,e=synthetic(dict(test_one=lambda s:s.assertTrue(True)));e['expected_test_ids']=['pf_synthetic.Other.test_other'];side,_,_=exercise(cls,e);self.assertEqual(side['status'],'INVALID_CAPTURE');self.assertIn('UNEXPECTED_TEST_ID',side['errors'])
    def test_PF31(self):
        cls,e=synthetic(dict(test_one=lambda s:None));e['expected_raw_scenarios']=1;e['expected_scenario_multiplicity']={'A':1};raw=dict(scenarios=[dict(case='A',run_id='11111111-1111-4111-8111-111111111111',status='PASS',oracles=[],events=[dict(event='READY',role='CLIENT',point='before_object',operation='APPLY')])]);rows=c.scenario_metadata(raw,e);self.assertEqual(c.pointer(raw,rows[0]['metadata_refs'][0]['pointer']),'before_object');self.assertIn('NOT_CAUSAL_ATTESTATION',rows[0]['metadata_refs'][0]['classification'])
    def test_PF32(self):
        self.err('INVALID_POINTER',c.pointer,{},'/wrong')
        cls,e=synthetic(dict(test_one=lambda s:None));e['expected_raw_scenarios']=1;e['expected_scenario_multiplicity']={'A':1};self.err('SCENARIO_MULTIPLICITY_MISMATCH',c.scenario_metadata,dict(scenarios=[dict(case='B')]),e)
    def test_PF33(self):
        for scope,tid,factory in [('P04','test_HF01','early_test'),('P04','test_HF25','fsync_test'),('P05','test_IC01','client_test'),('P05','test_IC17','remote_test')]:
            entry=next(e for e in self.registry['entries'] if e['id']==scope);binding=next(v for k,v in entry['method_bindings'].items() if k.endswith(tid));self.assertEqual(binding['symbol'],factory);self.assertEqual(binding['kind'],'FACTORY_EXPANSION_EXPECTATION');self.assertEqual(binding['status'],'SOURCE_DERIVED_EXPECTATION')
    def test_PF34(self):
        records=[]
        def run(s):records.append(dict(case='C',run_id='11111111-1111-4111-8111-111111111111',events=[],status='PASS'))
        cls,e=synthetic(dict(test_one=run),records);e['expected_raw_scenarios']=1;e['expected_scenario_multiplicity']={'C':1};side,_,_=exercise(cls,e,records=records);self.assertEqual(side['frames'][0]['capture_completeness'],'INCOMPLETE');self.assertEqual(side['groups'][0]['status'],'INCOMPLETE');self.assertEqual(side['status'],'INCOMPLETE_CAPTURE')
    def test_PF35(self):
        p=self.registry['entries'][0];g=self.registry['entries'][1];self.assertNotIn('testing/prospective_capture/capture.py',p['runner_effective_inputs']);self.assertNotEqual(p['runner_effective_inputs'],g['runner_effective_inputs'])
    def test_PF36(self):self.assertEqual(c.compare_inputs({'x.py':'a'},{'x.py':'b'})['status'],'STALE_INPUTS')
    def test_PF37(self):
        for a,b in [({}, {'new.py':'a'}),({'gone.py':'a'}, {})]:self.assertEqual(c.compare_inputs(a,b)['status'],'STALE_INPUTS')
    def test_PF38(self):self.assertEqual(c.compare_inputs({'x.md':'a'},{'x.md':'b'})['status'],'DOCUMENT_ONLY_CHANGE_REVIEW_PENDING')
    def test_PF39(self):
        for value in [b'{"a":1,"a":2}',b'{"a":NaN}',b'['*33+b']'*33,b'{']:
            with self.assertRaises(c.CaptureFault):c.strict_json(value)
        cls,e=synthetic(dict(test_one=lambda s:None));self.err('INVALID_TEST_COUNT',c.aggregate_capture,dict(frames=[]),[],dict(status='PASS',passed=[],tests_run=True),e)
    def test_PF40(self):
        cls,e=synthetic(dict(test_one=lambda s:None));side=w.exercise(e,lambda:print('{'),io.StringIO());self.assertEqual(side['status'],'INVALID_CAPTURE');self.assertIn('RAW_UNAVAILABLE_OR_INVALID',side['errors'])
    def test_PF41(self):
        target=io.StringIO();sink=c.BoundedOutput(target,3);self.err('RAW_BUDGET',sink.write,'four');self.assertEqual(target.getvalue(),'')
        cls,e=synthetic(dict(test_one=lambda s:s.assertTrue(True)));side,_,_=exercise(cls,e,limits={'sidecar_bytes':32});self.assertEqual(side['errors'],['SIDECAR_BUDGET'])
    def test_PF42(self):
        cls,e=synthetic(dict(test_one=lambda s:s.assertEqual(1,1)));side,raw,_=exercise(cls,e,limits={'event_bytes':1});self.assertEqual(raw['status'],'PASS');self.assertIn('EVENT_SIZE_BUDGET',side['errors'])
        r=c.Recorder(e,{'events_campaign':0});r.emit('X');self.assertIn('EVENT_CAMPAIGN_BUDGET',r.errors)
    def child(self,owner,code):
        p=subprocess.Popen([sys.executable,'-B','-c',code],stdin=subprocess.DEVNULL,stdout=subprocess.PIPE,stderr=subprocess.DEVNULL,start_new_session=True,env=dict(PATH=os.defpath,LANG='C'));row=dict(pid=p.pid,group=p.pid,exitcode=None,owned=True);CHILDREN.append(row)
        return p,row
    def test_PF43(self):
        with own_root() as (root,owner):
            p,row=self.child(owner,'import time;time.sleep(10)')
            try:out=c.stop_owned(p,owner,dict(pid=p.pid,pgid=p.pid,lease=owner.nonce),grace=.1);self.assertEqual(out['status'],'OWN_GROUP_GONE')
            finally:
                if p.poll() is None:c.stop_owned(p,owner,dict(pid=p.pid,pgid=p.pid,lease=owner.nonce),grace=.1)
                row['exitcode']=p.wait();p.stdout.close()
        with own_root() as (root,owner):
            rawfd=owner.create('raw.json');sidefd=owner.create('side.json');rr,rw=os.pipe();lr,lw=os.pipe()
            script=r"""import os,sys,json
from testing.prospective_capture import capture as c
side,ready,release=map(int,sys.argv[1:4]);lease=sys.argv[4]
c.write_json_fd(ready,dict(event='READY',scope='P01',lease=lease,pid=os.getpid(),pgid=os.getpgid(0),raw_inode=os.fstat(1).st_ino,sidecar_inode=os.fstat(side).st_ino),4096);os.write(ready,b'\n');os.close(ready)
c.require(c.receive_line(release,2)==dict(event='RELEASE',lease=lease),'INVALID_WORKER_RELEASE')
raw=b'{"status":"PASS","synthetic_only":true}\n';os.write(1,raw);c.write_json_fd(side,dict(raw_sha256=c.sha(raw),raw_bytes=len(raw),synthetic_only=True),4096)
"""
            p=subprocess.Popen([sys.executable,'-B','-c',script,str(sidefd),str(rw),str(lr),owner.nonce],cwd=ROOT,stdin=subprocess.DEVNULL,stdout=rawfd,stderr=subprocess.DEVNULL,pass_fds=(sidefd,rw,lr),start_new_session=True)
            row=dict(pid=p.pid,group=p.pid,owned=True,exitcode=None);CHILDREN.append(row);os.close(rw);os.close(lr)
            try:
                message=c.receive_line(rr,2);c.verify_ready(message,'P01',owner.nonce,p.pid,rawfd,sidefd)
                c.write_json_fd(lw,dict(event='RELEASE',lease=owner.nonce),4096);os.write(lw,b'\n');self.assertEqual(p.wait(timeout=2),0)
                side=json.loads((root/'side.json').read_text());self.assertEqual(side['raw_sha256'],c.sha((root/'raw.json').read_bytes()))
            finally:
                if p.poll() is None:c.stop_owned(p,owner,dict(pid=p.pid,pgid=p.pid,lease=owner.nonce),grace=.1)
                row['exitcode']=p.wait()
                for fd in (rawfd,sidefd,rr,lw):os.close(fd)
        r,wfd=os.pipe();os.close(wfd)
        try:self.err('WORKER_EOF',c.receive_line,r,.1)
        finally:os.close(r)
        r,wfd=os.pipe()
        try:self.err('WORKER_TIMEOUT',c.receive_line,r,.02)
        finally:os.close(r);os.close(wfd)
        with own_root() as (root,owner):
            p,row=self.child(owner,'raise SystemExit(7)');row['exitcode']=p.wait(timeout=5);p.stdout.close();self.assertEqual(row['exitcode'],7)
    def test_PF44(self):
        cls,e=synthetic(dict(test_one=lambda s:s.assertTrue(True)));side,raw,_=exercise(cls,e,limits={'events_test':0});self.assertEqual(raw['status'],'PASS');self.assertEqual(side['raw_functional_status'],'PASS');self.assertEqual(side['status'],'INVALID_CAPTURE')
    def test_PF45(self):
        for name in ['/outside','../outside','https://host','dev/run_data/file','docs/.env','x\\y']:
            with self.assertRaises(c.CaptureFault):c.public_path(name)
        self.err('INVALID_SCOPE',c.authority_scope,'testing.D5.run_relational_durable_lab')
    def test_PF46(self):
        with own_root() as (root,owner):
            fd=owner.create('value.bin');os.close(fd)
            with self.assertRaises(FileExistsError):owner.create('value.bin')
            (root/'link').symlink_to('value.bin')
            with self.assertRaises(c.CaptureFault):c.Reader(root).read('link')
            os.mkfifo(root/'fifo')
            self.err('NONREGULAR_FILE',c.Reader(root).read,'fifo')
            r=c.Reader(root);r.read('value.bin');(root/'value.bin').write_text('changed');self.err('UNSTABLE_SNAPSHOT',r.finish)
    def test_PF47(self):
        with own_root() as (root,owner):
            sibling=root/'sibling';sibling.write_bytes(b'unchanged');before=c.sha(sibling.read_bytes());fd=owner.create('own');os.close(fd);(root/'own').unlink();owner.verify();self.assertEqual(before,c.sha(sibling.read_bytes()))
    def test_PF48(self):
        marker='sensitive'+'/'+'private';cls,e=synthetic(dict(test_one=lambda s:s.assertEqual(marker,marker)));side,raw,_=exercise(cls,e);self.assertNotIn(marker,json.dumps(side));self.assertNotIn('Traceback',json.dumps(side));self.assertNotIn(str(ROOT),json.dumps(side))
    def test_PF49(self):
        with patch.object(w.importlib,'import_module',side_effect=AssertionError('historical import forbidden')) as load,contextlib.redirect_stderr(io.StringIO()):code=w.main(['P01','1','2','3','lease'])
        self.assertEqual(code,2);load.assert_not_called()
        with patch.object(c.subprocess,'Popen',side_effect=AssertionError('functional launch forbidden')) as spawn:self.err('I71_AUTHORIZATION_REQUIRED',c.launch,'P01')
        spawn.assert_not_called()
        result=c.plan();self.assertTrue(all(v['status']=='NOT_RUN_I71_AUTHORIZATION_REQUIRED' for v in result['catalog']));self.assertFalse(result['functional_execution_authorized'])
    def test_PF50(self):
        with own_root() as (root,owner):
            p,row=self.child(owner,'import time;time.sleep(10)')
            try:
                self.err('INVALID_WORKER_IDENTITY',c.stop_owned,p,owner,dict(pid=p.pid,pgid=p.pid,lease='wrong'));self.assertIsNone(p.poll())
            finally:c.stop_owned(p,owner,dict(pid=p.pid,pgid=p.pid,lease=owner.nonce),grace=.1);row['exitcode']=p.wait();p.stdout.close()
    def test_PF51(self):
        self.assertEqual(sum(e['expected_tests'] for e in self.registry['entries']),692);cls,e=synthetic(dict(test_one=lambda s:s.assertTrue(True)));side,_,_=exercise(cls,e);self.assertEqual(side['new_distinct_functional_tests'],0);self.assertFalse(side['historical_evidence_modified'])
    def test_PF52(self):
        cls,e=synthetic(dict(test_one=lambda s:(s.assertEqual(1,1),s.assertEqual(2,2),s.assertTrue(True))));side,_,_=exercise(cls,e);self.assertEqual(len(side['frames']),1);self.assertGreater(len(side['events']),1)
    def test_PF53(self):
        cls,e=synthetic(dict(test_one=lambda s:s.assertTrue(True)));side,_,_=exercise(cls,e);self.assertEqual(side['frames'][0]['domain_scope']['reason'],'UNIT_OR_VOLATILE_FIXTURE_NO_DURABLE_BOUNDARY');self.assertFalse(side['D5_closed'])
    def test_PF54(self):
        calls=[]
        class Recorded(unittest.TestResult):
            def addSuccess(self,test):calls.append(test.id());return super().addSuccess(test)
            def stopTest(self,test):calls.append('stop');return super().stopTest(test)
        cls,e=synthetic(dict(test_one=lambda s:s.assertTrue(True)));side,_,_=exercise(cls,e,resultclass=Recorded);self.assertEqual(calls,[e['expected_test_ids'][0],'stop']);self.assertEqual(side['frames'][0]['result'],'PASS')
    def test_PF55(self):
        cls,e=synthetic(dict(test_one=lambda s:s.assertTrue(True)));side,_,_=exercise(cls,e);self.assertEqual(side['sufficiency'],'REVIEW_PENDING');self.assertNotIn('durable_recovery_proven',side)
    def test_PF56(self):
        cls,e=synthetic(dict(test_one=lambda s:s.assertTrue(True)),domain=True);side,_,_=exercise(cls,e);self.assertEqual(side['status'],'INCOMPLETE_CAPTURE');self.assertIn('DOMAIN_IDENTITY_NOT_RECORDED',side['frames'][0]['missing'])
    def test_PF57(self):
        v=c.plan();self.assertEqual(v['semantic_baseline'],{'SUPPORTS_BOUNDED':81,'PARTIAL':3});self.assertEqual(v['phase'],'I70_COMPONENTS_ONLY');self.assertTrue(all(x['status'].startswith('NOT_RUN') for x in v['catalog']))
    def test_PF58(self):
        cls,e=synthetic(dict(test_one=lambda s:s.assertTrue(True)));side,_,_=exercise(cls,e);self.assertEqual(side['status'],'TRACE_CAPTURED_PENDING_SUFFICIENCY_REVIEW');self.assertFalse(side['closure']);self.assertEqual(side['global_review'],'OPEN')
    def test_PF59(self):
        tree=ast.parse((ROOT/'testing/prospective_capture/capture.py').read_text());self.assertFalse(any(isinstance(n,ast.ImportFrom) and (n.module or '').startswith(('source_ingest','testing.D5','testing.evidence_audit','testing.evidence_trace')) for n in ast.walk(tree)))
        self.assertTrue(all(not m.startswith(('source_ingest','testing.D5','testing.durable_','testing.gi39_interleavings','testing.evidence_trace','testing.evidence_audit')) for m in sys.modules))
    def test_PF60(self):
        before={p:c.sha((ROOT/p).read_bytes()) for p in ['docs/validation/D5-I69-design-review.json','docs/validation/D5-I69-integrity.json','docs/validation/D5-I68-results.json']};c.plan();after={p:c.sha((ROOT/p).read_bytes()) for p in before};self.assertEqual(before,after)
        self.assertTrue(all(r['ownership_verified'] and r['removed'] for r in OWN_ROOTS));self.assertTrue(all(r['exitcode'] is not None for r in CHILDREN))
