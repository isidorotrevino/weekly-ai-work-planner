# SPDX-License-Identifier: GPL-3.0-only
"""LB64 uses only new synthetic modules, suites and owned processes."""
import contextlib
import copy
import hashlib
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
from testing.prospective_capture_late import capture as p,worker as w
c=p.c;ROOT=p.ROOT;ROOTS=[];CHILDREN=[]
RID='11111111-1111-4111-8111-111111111111';SID='22222222-2222-4222-8222-222222222222'
PLANE='source_ingest.plane_fixture.PlaneError';ELIG='source_ingest.eligibility_fixture.EligibilityError'


@contextlib.contextmanager
def owned():
    row=dict(ownership_verified=False,removed=False,sibling_preserved=False);ROOTS.append(row)
    with tempfile.TemporaryDirectory(prefix='i79-own-') as temp:
        base=Path(temp);root=base/'packet';root.mkdir();owner=c.OwnedRoot(root);sibling=base/'sibling';sibling.write_bytes(b'SYNTHETIC_SIBLING')
        try:yield base,root,owner
        finally:owner.verify();row['ownership_verified']=True;row['sibling_preserved']=sibling.read_bytes()==b'SYNTHETIC_SIBLING'
    row['removed']=not base.exists()


def forbidden():return sorted(n for n in sys.modules if n.startswith(('source_ingest','testing.D5','testing.durable_','testing.gi39_interleavings','testing.causal_frontier_cells','testing.evidence_audit','testing.evidence_trace')) or n in ('testing.prospective_capture_paged.test_paged_capture','testing.prospective_capture_paged.run_paged_lab','testing.prospective_capture_typed.test_typed_capture','testing.prospective_capture_typed.run_typed_lab'))


def example(methods,domain=False):
    cls=type('Example',(unittest.TestCase,),dict(__module__='lb_synthetic',**methods));ids=['lb_synthetic.Example.'+n for n in sorted(methods)]
    entry=dict(id='P01_SYNTHETIC_ONLY',expected_tests=len(ids),expected_test_ids=ids,expected_groups={'lb_synthetic':len(ids)},group_policies={'lb_synthetic':dict(target='SYNTHETIC_COMPONENT_ONLY',domain_required=domain,no_store_reason=None if domain else 'SYNTHETIC_UNIT_NO_DURABLE_BOUNDARY')},record_sources=[],method_bindings={tid:dict(status='SOURCE_DERIVED_EXPECTATION',scope='SYNTHETIC_ONLY') for tid in ids},expected_raw_scenarios=0,expected_scenario_multiplicity={});return cls,entry


def run_suite(cls,entry,before=None,after=None):
    class Result(unittest.TestResult):
        def __init__(self):super().__init__();self.passed=[]
        def addSuccess(self,test):self.passed.append(test.id());return super().addSuccess(test)
    if before:before()
    result=Result();unittest.defaultTestLoader.loadTestsFromTestCase(cls).run(result)
    if after:after()
    raw=dict(status='PASS' if result.wasSuccessful() else 'FAIL',tests_run=result.testsRun,passed=result.passed,failures=[t.id() for t,_ in result.failures],errors=[t.id() for t,_ in result.errors],skipped=[t.id() for t,_ in result.skipped],scenarios=[],case_test_map={});print(json.dumps(raw));return 0 if result.wasSuccessful() else 1


class Fixture:
    def __init__(self,root,run_id,scope,*,test_fault=None,test_ready=None):self.out=dict(schema='d5.fixture-drive-snapshot.v1',run_id=run_id,version=0,head_sha256='a'*64)
    def snapshot(self):return self.out


class LateTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):cls.reg=p.read_registry()
    def setUp(self):self.observations=[]
    def err(self,code,fn,*args,**kwargs):
        with self.assertRaises(c.CaptureFault) as got:fn(*args,**kwargs)
        self.assertEqual(got.exception.code,code);self.observations.append(dict(expected=code,observed=got.exception.code))
    def bindings(self,base,limits=None):
        specs=[dict(id='builtins.dict',source=None)];modules={}
        for i,ref in enumerate((PLANE,ELIG)):
            module_name,name=ref.rsplit('.',1);module=types.ModuleType(module_name);cls=type(name,(ValueError,),dict(__module__=module_name));module.__dict__[name]=cls;modules[module_name]=module;path='packet/class'+str(i)+'.py';(base/path).write_text('class '+name+'(ValueError):\n    pass\n');specs.append(dict(id=ref,source=dict(path=path,sha256=c.sha((base/path).read_bytes()))))
        resolver=p.LateBindings(specs,c.Reader(base,limits),lookup=modules.get);return resolver,modules
    def suite(self,method=None,*,methods=None,roles=None,helper='assertIsInstance',before=None,after=None,mode='unit',limits=None):
        with owned() as (base,root,owner):
            resolver,modules=self.bindings(base);plane=modules[PLANE.rsplit('.',1)[0]].PlaneError
            methods=methods or {'test_one':method or (lambda s:s.assertTrue(True))};cls,entry=example(methods,domain=mode!='unit');tid=entry['expected_test_ids'][0];profile=dict(class_allowlist=resolver.specs.values(),snapshot_scopes=[dict(test_id=tid)] if mode=='snapshot' else [],negative_DI28=dict(criterion=dict(test_id=tid)) if mode=='negative' else {},operand_scopes=[dict(test_id=tid,helper=helper,operand_roles=roles)] if roles else [])
            # Pass resolver/modules explicitly to synthetic callbacks; no product module is imported.
            if before:before(resolver,modules)
            out=io.StringIO();ledger=p.Ledger(owner.nonce)
            def after_call():
                if after:after(resolver,modules)
            side=w.exercise(entry,lambda:run_suite(cls,entry,after=after_call),out,owner,observed=[(Fixture,'snapshot')],fixture_class=Fixture,profile=profile,bindings=resolver,ledger=ledger,limits=limits)
            raw=json.loads(out.getvalue()) if out.getvalue() else None
            if side['status']=='TRACE_CAPTURED_PENDING_SUFFICIENCY_REVIEW':p.validate_pages(p.evidence_reader(base),'packet',side,limits,profile)
            events=[e for page in side.get('pages',[]) for e in json.loads((root/page['name']).read_text())['events']]
            self.observations.append(dict(status=side['status'],diagnostic=side['worker_diagnostic']['code'],functional=raw['status'] if raw else 'NOT_RECORDED'));return side,raw,events
    def diag(self,code='CLASS_MODULE_NOT_LOADED',phase='ENTRYPOINT'):
        ledger=p.Ledger(RID,pid=123);ledger.at(phase);ledger.fail(code);return ledger
    def test_LB01(self):
        with owned() as (base,root,owner):self.err('I80_AUTHORIZATION_REQUIRED',p.authority,base,'P01',self.reg)
        with patch.object(p,'read_registry',return_value=self.reg),patch.object(p,'authority',side_effect=c.CaptureFault('I80_AUTHORIZATION_REQUIRED')),patch.object(w.importlib,'import_module') as imp:self.assertEqual(w.main(['P01','4','5','6','7',RID]),2);imp.assert_not_called()
    def test_LB02(self):
        for name,h in json.loads((ROOT/'docs/validation/D5-I78-integrity.json').read_text())['artifacts'].items():self.assertEqual(c.sha((ROOT/name).read_bytes()),h)
        with owned() as (base,root,owner):
            def put(n,value):
                q=base/n;q.parent.mkdir(parents=True,exist_ok=True);q.write_text(json.dumps(value));return c.sha(q.read_bytes())
            component='packet/component.json';put(component,dict(synthetic=True));raw='docs/validation/D5-I79-tests-raw.json';seal='docs/validation/D5-I79-integrity.json';put(raw,dict(status='PASS',tests_run=64,functional_campaigns_executed=0,forbidden_imports=[]));put(seal,dict(artifacts={component:c.sha((base/component).read_bytes())}));rh=put(p.REGISTRY,dict(synthetic=True));names={component,raw,seal,p.REGISTRY};pins={n:c.sha((base/n).read_bytes()) for n in names};put(p.AUTHORITY,dict(schema='d5.late-capture-authority.v1',phase='I80_EXPLICITLY_APPROVED',scopes=['P01'],registry_sha256=rh,capture_inputs=pins))
            with patch.object(p,'authority_inputs',return_value=names):
                self.assertEqual(p.authority(base,'P01',{})['capture_inputs'],pins);put(component,dict(synthetic='CHANGED'));self.err('STALE_AUTHORITY',p.authority,base,'P01',{})
    def test_LB03(self):
        for value in ['P02','../P01','module:any']:self.err('INVALID_SCOPE',p.scope,value)
        old=json.loads((ROOT/p.t.REGISTRY).read_text());self.assertEqual(self.reg['entry'],old['entry']);self.assertEqual(self.reg['policies'],old['policies'])
    def test_LB04(self):self.assertEqual(p.plan()['status'],'NOT_RUN_I80_AUTHORIZATION_REQUIRED');self.assertEqual(forbidden(),[])
    def test_LB05(self):
        contract=json.loads((ROOT/'docs/validation/D5-I78-design-review.json').read_text());self.assertFalse(contract['implementation_authorized']);self.assertFalse(contract['functional_capture_execution_authorized']);self.assertEqual(contract['status'],'PREPARED_FOR_REVIEW')
    def test_LB06(self):self.assertEqual(forbidden(),[]);self.assertFalse((ROOT/p.AUTHORITY).exists())
    def test_LB07(self):self.assertFalse(self.reg['functional_execution_authorized']);self.observations.append(dict(authority='COHERENCE_GATE_NOT_HUMAN_ATTESTATION'))
    def test_LB08(self):
        with owned() as (base,root,owner):
            fd=owner.create('keep');os.write(fd,b'ORIGINAL');os.close(fd)
            with self.assertRaises(FileExistsError):owner.create('keep')
            (root/'link').symlink_to(base/'sibling');self.err('NONREGULAR_FILE',c.Reader(base).read,'packet/link');self.err('INVALID_PUBLIC_PATH',c.public_path,'../x')
    def test_LB09(self):
        with owned() as (base,root,owner):
            resolver,modules=self.bindings(base);modules.clear();self.assertEqual(set(resolver.rows),{'builtins.dict'});resolver.check();self.assertEqual(resolver.states[PLANE],'UNRESOLVED')
    def test_LB10(self):
        with owned() as (base,root,owner):
            resolver,modules=self.bindings(base);module=modules.pop(PLANE.rsplit('.',1)[0]);resolver.check();modules[module.__name__]=module;resolver.prepare(['class-'+PLANE]);self.assertIs(resolver.rows[PLANE]['cls'],module.PlaneError)
    def test_LB11(self):
        with owned() as (base,root,owner):resolver,modules=self.bindings(base);resolver.prepare(['class-'+ELIG]);self.assertEqual(resolver.states[ELIG],'BOUND');self.assertEqual(resolver.states[PLANE],'UNRESOLVED')
    def test_LB12(self):
        with owned() as (base,root,owner):
            resolver,modules=self.bindings(base);modules.clear();projector=p.t.Projector(RID,resolver,key=b'x'*32);self.assertEqual(projector.observe({},[]),c.digest_value({}));projector.observe(Path('/synthetic'),['exact-posix-path']);self.assertEqual(set(resolver.rows),{'builtins.dict'})
    def test_LB13(self):
        side,raw,_=self.suite(lambda s:s.assertIsInstance({},dict),roles={'0':['builtin-only-original-digest'],'1':['class-builtins.dict']},helper='assertEqual');self.assertEqual(side['status'],'INCOMPLETE_CAPTURE');self.assertEqual(raw['status'],'PASS')
    def test_LB14(self):
        box={}
        def before(resolver,modules):box['cls']=modules.pop(PLANE.rsplit('.',1)[0]).PlaneError
        side,raw,_=self.suite(lambda s:s.assertIsInstance(box['cls']('CODE'),box['cls']),roles={'0':['exact-PlaneError-instance-args-projection'],'1':['class-'+PLANE]},before=before);self.assertEqual(raw['status'],'PASS');self.assertEqual(side['worker_diagnostic']['code'],'CLASS_MODULE_NOT_LOADED');self.assertEqual(side['status'],'INVALID_CAPTURE')
    def test_LB15(self):
        side,_,_=self.suite();self.assertEqual(side['worker_diagnostic']['status'],'COMPLETED');self.assertEqual(side['status'],'TRACE_CAPTURED_PENDING_SUFFICIENCY_REVIEW')
    def test_LB16(self):
        with owned() as (base,root,owner):resolver,modules=self.bindings(base);resolver.prepare(['class-'+ELIG]);resolver.prepare(['class-'+PLANE]);self.assertEqual(set(resolver.rows),{'builtins.dict',ELIG,PLANE})
    def test_LB17(self):
        with owned() as (base,root,owner):resolver,modules=self.bindings(base);resolver.prepare(['class-'+PLANE]);cls=resolver.rows[PLANE]['cls'];self.assertIs(type(cls),type);self.assertEqual(cls.__bases__,(ValueError,));resolver.check()
    def test_LB18(self):
        with owned() as (base,root,owner):
            resolver,modules=self.bindings(base);resolver.prepare(['class-'+PLANE]);first=resolver.rows[PLANE]['cls'];modules[PLANE.rsplit('.',1)[0]].PlaneError=ValueError;self.err('CLASS_BINDING_CHANGED',resolver.check);self.assertIs(resolver.rows[PLANE]['cls'],first);self.err('CLASS_BINDING_CHANGED',resolver.prepare,['class-'+PLANE])
    def test_LB19(self):
        with owned() as (base,root,owner):resolver,modules=self.bindings(base);resolver.prepare(['class-'+PLANE]);modules[PLANE.rsplit('.',1)[0]]=types.ModuleType(PLANE.rsplit('.',1)[0]);self.err('CLASS_BINDING_CHANGED',resolver.check)
    def test_LB20(self):
        with owned() as (base,root,owner):resolver,modules=self.bindings(base);(base/'packet/class0.py').write_text('CHANGED');self.err('STALE_CLASS_SOURCE',resolver.prepare,['class-'+PLANE])
    def test_LB21(self):
        class Meta(type):
            def __instancecheck__(*args):raise AssertionError('MUST_NOT_CALL')
        with owned() as (base,root,owner):resolver,modules=self.bindings(base);modules[PLANE.rsplit('.',1)[0]].PlaneError=Meta('PlaneError',(ValueError,),dict(__module__=PLANE.rsplit('.',1)[0]));self.err('UNSUPPORTED_CLASS_BINDING',resolver.prepare,['class-'+PLANE])
    def test_LB22(self):
        with owned() as (base,root,owner):
            resolver,modules=self.bindings(base);resolver.prepare(['class-'+PLANE]);other=type('PlaneError',(ValueError,),dict(__module__=PLANE.rsplit('.',1)[0]));self.assertIsNone(resolver.class_row(other));self.assertIsNone(resolver.instance_row(other('CODE')))
    def test_LB23(self):
        box={}
        def before(resolver,modules):box.update(cls=modules[PLANE.rsplit('.',1)[0]].PlaneError)
        def after(resolver,modules):modules.pop(PLANE.rsplit('.',1)[0])
        side,raw,_=self.suite(lambda s:s.assertIsInstance(box['cls']('CODE'),box['cls']),roles={'0':['exact-PlaneError-instance-args-projection'],'1':['class-'+PLANE]},before=before,after=after);self.assertEqual(raw['status'],'PASS');self.assertIn('CLASS_BINDING_CHANGED',side['errors'])
    def test_LB24(self):
        with owned() as (base,root,owner):
            resolver,modules=self.bindings(base);resolver.prepare(['class-'+PLANE]);first=resolver.rows[PLANE]['cls'];used=resolver.reader.total;resolver.prepare(['class-'+PLANE]);self.assertIs(resolver.rows[PLANE]['cls'],first);self.assertGreater(resolver.reader.total,used)
    def test_LB25(self):
        box={};calls=[]
        def before(resolver,modules):box.update(cls=modules[PLANE.rsplit('.',1)[0]].PlaneError)
        def test(s):calls.append('ORIGINAL');s.assertIsInstance(box['cls']('CODE'),box['cls'])
        side,raw,_=self.suite(test,roles={'0':['exact-PlaneError-instance-args-projection'],'1':['class-'+PLANE]},before=before);self.assertEqual(calls,['ORIGINAL']);self.assertEqual(side['status'],'TRACE_CAPTURED_PENDING_SUFFICIENCY_REVIEW')
    def test_LB26(self):
        side,raw,events=self.suite(lambda s:s.assertIsInstance(1,str),roles={'0':['exact-PlaneError-instance-args-projection'],'1':['class-'+PLANE]});self.assertEqual(raw['status'],'FAIL');self.assertTrue(any(e['event']=='ASSERTION_RAISED' for e in events));self.assertFalse(any(e.get('operands') for e in events))
    def test_LB27(self):
        with patch.object(p.LateBindings,'prepare',side_effect=OSError('PRIVATE_DIAGNOSTIC_PAYLOAD')):
            side,raw,_=self.suite(lambda s:s.assertIsInstance({},dict),roles={'0':['builtin-only-original-digest'],'1':['class-builtins.dict']});self.assertEqual(raw['status'],'PASS');self.assertEqual(side['worker_diagnostic']['code'],'TYPED_PROJECTION_ERROR');self.assertNotIn('PRIVATE_DIAGNOSTIC_PAYLOAD',json.dumps(side))
    def test_LB28(self):
        side,raw,events=self.suite(lambda s:s.assertIsInstance({},dict),roles={'0':['builtin-only-original-digest'],'1':['class-builtins.dict']});ops=next(e['operands'] for e in events if e.get('helper')=='assertIsInstance');self.assertEqual(ops[0],c.digest_value({}));self.assertEqual(ops[1]['status'],'OBSERVED_TYPED_PROJECTION')
    def test_LB29(self):
        for ref in (PLANE,ELIG):
            with owned() as (base,root,owner):
                resolver,modules=self.bindings(base);resolver.prepare(['class-'+ref]);cls=resolver.rows[ref]['cls'];projector=p.t.Projector(RID,resolver,key=b'x'*32);got=projector.observe(cls('CODE'),['exact-'+ref.rsplit('.',1)[1]+'-instance-args-projection']);self.assertEqual(got['status'],'OBSERVED_TYPED_PROJECTION');self.assertNotIn('CODE',json.dumps(got));self.assertNotIn('args',got)
    def test_LB30(self):
        with owned() as (base,root,owner):
            resolver,modules=self.bindings(base);projector=p.t.Projector(RID,resolver,key=b'x'*32)
            for v,graph in [(Path('/synthetic'),'exact-posix-path'),((Path('/synthetic'),'x'),'exact-tuple(exact-posix-path,builtin-str)'),([Path('/synthetic')],'exact-list(exact-posix-path)')]:self.assertEqual(projector.observe(v,[graph])['status'],'OBSERVED_TYPED_PROJECTION')
            self.assertEqual(set(resolver.rows),{'builtins.dict'})
    def test_LB31(self):
        def test(s):st=Fixture('synthetic',RID,{});st.snapshot()
        side,_,_=self.suite(test,mode='snapshot');self.assertTrue(side['drive_observations']);self.assertFalse(any(o['identity'] for o in side['owner_contexts'].values()))
        side,_,_=self.suite(lambda s:Fixture('synthetic',RID,{}).__init__('synthetic',RID,{}),mode='negative');self.assertTrue(side['fixture_construction_declarations']);self.assertEqual(side['frames'][0]['domain_scope']['status'],'NEGATIVE_DOMAIN_FIXTURE_CLEANUP')
    def test_LB32(self):
        old=(unittest.TestCase.assertIsInstance,unittest.TestResult.startTest,Fixture.__init__,Fixture.snapshot)
        def test(s):
            with s.subTest(v=1):s.assertEqual(1,2)
        side,raw,_=self.suite(test);self.assertEqual(raw['status'],'FAIL');self.assertEqual(side['frames'][0]['result'],'FAIL');self.assertEqual(old,(unittest.TestCase.assertIsInstance,unittest.TestResult.startTest,Fixture.__init__,Fixture.snapshot))
    def test_LB33(self):
        ledger=p.Ledger(RID,pid=123);value=ledger.value();self.assertEqual(p.validate_diagnostic(value,RID,123)['status'],'COMPLETED');self.assertEqual(value['code'],'OK')
    def test_LB34(self):
        ledger=self.diag('UNSUPPORTED_OBSERVER_API','TARGETS');body=p.encode(dict(schema=p.FAILURE_SCHEMA,worker_diagnostic=ledger.value()));side,diag=p.read_sidecar(body,RID,123);self.assertEqual(diag['phase'],'TARGETS');self.assertNotIn('frames',side)
    def test_LB35(self):
        ledger=p.Ledger(RID,pid=123);ledger.at('RUNNER_INPUTS');ledger.exception(c.CaptureFault('STALE_INPUTS'));self.assertEqual(ledger.value()['code'],'STALE_INPUTS')
    def test_LB36(self):
        class Private(Exception):
            def __str__(self):raise AssertionError('MUST_NOT_CALL')
            def __repr__(self):raise AssertionError('MUST_NOT_CALL')
        for ex in [Private(),c.CaptureFault('PRIVATE_PATH_OR_TOKEN')]:
            ledger=p.Ledger(RID,pid=123);ledger.exception(ex);self.assertEqual(ledger.value()['code'],'SANITIZED_WORKER_ERROR');self.assertNotIn('PRIVATE_PATH',json.dumps(ledger.value()))
    def test_LB37(self):
        ledger=self.diag();ledger.at('FINALIZE');ledger.fail('RAW_UNAVAILABLE_OR_INVALID');self.assertEqual(ledger.value()['phase'],'ENTRYPOINT');self.assertEqual(ledger.value()['code'],'CLASS_MODULE_NOT_LOADED')
    def test_LB38(self):
        ledger=self.diag();first=ledger.value();ledger.at('SIDECAR_WRITE');ledger.exception(OSError());self.assertEqual(first,ledger.value())
    def test_LB39(self):self.integration('failure')
    def test_LB40(self):self.err('SIDECAR_PARTIAL_OR_INVALID',p.read_sidecar,b'',RID,123)
    def test_LB41(self):
        with patch.object(p,'read_registry',return_value=self.reg),patch.object(p,'authority',side_effect=c.CaptureFault('I80_AUTHORIZATION_REQUIRED')),patch.object(p.SideWriter,'failure') as fail,patch.object(w.importlib,'import_module') as imp:self.assertEqual(w.main(['P01','4','5','6','7',RID]),2);fail.assert_not_called();imp.assert_not_called()
    def test_LB42(self):self.integration('success')
    def test_LB43(self):
        value=self.diag().value()
        for k,v in [('lease',SID),('pid',124),('pgid',124),('pid',True),('capture_run_id','bad')]:self.err('INVALID_WORKER_DIAGNOSTIC',p.validate_diagnostic,dict(value,**{k:v}),RID,123)
        self.err('INVALID_WORKER_DIAGNOSTIC',p.validate_diagnostic,dict(value,capture_run_id=SID),RID,123,RID,True)
    def test_LB44(self):
        value=self.diag().value()
        for changes in [dict(extra='PRIVATE'),dict(schema='x'),dict(phase='x'),dict(code='PRIVATE'),dict(status='COMPLETED'),dict(phase='COMPLETE'),dict(code='OK')]:self.err('INVALID_WORKER_DIAGNOSTIC',p.validate_diagnostic,dict(value,**changes),RID,123)
    def test_LB45(self):
        with owned() as (base,root,owner):
            fd=owner.create('side');writer=p.SideWriter(fd,RID,pid=123);self.assertTrue(writer.failure(self.diag()));self.assertFalse(writer.failure(self.diag()));os.close(fd);p.read_sidecar((root/'side').read_bytes(),RID,123)
    def test_LB46(self):
        with owned() as (base,root,owner):
            fd=owner.create('side');writer=p.SideWriter(fd,RID,pid=123)
            def partial(fd,body):os.write(fd,body[:7]);raise OSError('SYNTHETIC_WRITE_FAILURE')
            with patch.object(p,'write_all',side_effect=partial):
                with self.assertRaises(OSError):writer.failure(self.diag())
            self.assertFalse(writer.failure(self.diag()));os.close(fd);self.assertEqual(len((root/'side').read_bytes()),7);self.err('SIDECAR_PARTIAL_OR_INVALID',p.read_sidecar,(root/'side').read_bytes(),RID,123)
    def test_LB47(self):
        with owned() as (base,root,owner):
            child=subprocess.Popen([sys.executable,'-B','-c','import sys; sys.stdin.read()'],stdin=subprocess.PIPE,stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL,start_new_session=True)
            try:self.assertFalse(p.wait_worker(child,.01));self.err('INVALID_WORKER_IDENTITY',c.stop_owned,child,owner,dict(pid=child.pid,pgid=child.pid,lease=SID))
            finally:done=c.stop_owned(child,owner,dict(pid=child.pid,pgid=child.pid,lease=owner.nonce));child.stdin.close();CHILDREN.append(dict(exitcode=child.returncode,kind='SYNTHETIC_TIMEOUT'))
            self.assertEqual(done['status'],'OWN_GROUP_GONE');self.assertNotEqual(child.returncode,-signal.SIGKILL)
    def test_LB48(self):
        side,raw,_=self.suite(lambda s:s.assertEqual(1,2));self.assertEqual(raw['status'],'FAIL');self.assertEqual(side['worker_diagnostic']['status'],'COMPLETED');self.assertFalse(side['closure'])
    def test_LB49(self):
        with owned() as (base,root,owner):
            fd=owner.create('side');writer=p.SideWriter(fd,RID,pid=123);value=dict(schema=p.FAILURE_SCHEMA,worker_diagnostic=self.diag().value(),padding='x'*4096);self.err('SIDECAR_BUDGET',writer.write,value,4096);self.assertFalse(writer.started);os.close(fd)
    def test_LB50(self):
        side,raw,_=self.suite();self.assertEqual(side['schema'],p.NORMAL_SCHEMA);self.assertIn('worker_diagnostic',side);self.assertEqual(p.LIMITS['index_sidecar_bytes'],12*1024*1024)
    def test_LB51(self):
        self.err('PACKAGE_FILE_BUDGET',p.package_size,{'sidecar.json':13*1024*1024});self.err('PACKAGE_BUDGET',p.package_size,{'OWNER':2},dict(package_bytes=1))
        sizes={name:0 for name in ['OWNER','runner-raw.json','sidecar.json','context.json','launch.json']};sizes.update({f'event-{i:04}.json':0 for i in range(1,33)});self.assertEqual(p.package_size(sizes),0);self.err('PACKAGE_SET_MISMATCH',p.package_size,dict(sizes,**{'worker-diagnostic.json':0}))
    def test_LB52(self):
        with owned() as (base,root,owner):
            sink=p.PageSink(owner,RID)
            for i in range(131072):sink.append(dict(event='SYNTHETIC_BOUNDARY',sequence=i))
            self.err('EVENT_CAMPAIGN_BUDGET',sink.append,dict(event='SYNTHETIC_BOUNDARY',sequence=131072));sink.close();self.assertEqual(sink.count,131072)
        def test(s):
            for _ in range(2049):s.assertTrue(True)
        side,raw,_=self.suite(test);self.assertEqual(raw['status'],'PASS');self.assertIn('EVENT_TEST_BUDGET',side['errors'])
    def test_LB53(self):
        def test(s):
            for _ in range(20):s.assertTrue(True)
        side,_,_=self.suite(test,limits=dict(page_bytes=750));self.assertGreater(len(side['pages']),2)
        with owned() as (base,root,owner):
            sink=p.PageSink(owner,RID,dict(page_bytes=250,event_pages_total_bytes=250));sink.append(dict(event='N',sequence=0));sink.flush();self.err('PAGES_TOTAL_BUDGET',sink.append,dict(event='N',sequence=1))
    def test_LB54(self):
        with owned() as (base,root,owner):
            resolver,modules=self.bindings(base,dict(read_bytes=250));resolver.prepare(['class-'+PLANE]);self.err('READ_BUDGET',lambda:[resolver.check() for _ in range(20)])
            self.assertIs(resolver.reader,resolver.reader)
    def test_LB55(self):
        side,_,_=self.suite(methods={'test_a':lambda s:s.assertTrue(True),'test_b':lambda s:s.assertTrue(True)},limits=dict(frames=1));self.assertIn('FRAME_BUDGET',side['errors']);self.assertEqual(p.LIMITS['refs'],16384);self.assertEqual(len(self.reg['class_allowlist']),3)
    def test_LB56(self):self.assertEqual(p.LIMITS['campaign_seconds'],900);self.assertEqual(json.loads((ROOT/'docs/validation/D5-I78-design-review.json').read_text())['component_external_seconds'],300)
    def test_LB57(self):self.assertEqual(forbidden(),[]);self.assertTrue(all(r['ownership_verified'] and r['removed'] and r['sibling_preserved'] for r in ROOTS))
    def test_LB58(self):self.integration('late');self.integration('untrusted')
    def test_LB59(self):
        for n in ['docs/validation/D5-I76-integrity.json','docs/validation/D5-I77-integrity.json']:
            for name,h in json.loads((ROOT/n).read_text())['artifacts'].items():self.assertEqual(c.sha((ROOT/name).read_bytes()),h)
    def test_LB60(self):
        side,raw,_=self.suite(lambda s:s.assertIsInstance('a',str),roles={'0':[],'1':['class-builtins.dict']});self.assertEqual(raw['status'],'PASS');self.assertEqual(side['status'],'INCOMPLETE_CAPTURE');self.assertEqual(side['worker_diagnostic']['code'],'CAPTURE_INCOMPLETE')
    def test_LB61(self):
        side,raw,_=self.suite();self.assertEqual(side['status'],'TRACE_CAPTURED_PENDING_SUFFICIENCY_REVIEW');self.assertEqual(side['sufficiency'],'REVIEW_PENDING');self.assertFalse(side['D5_closed'])
    def test_LB62(self):self.assertFalse(p.plan()['publication_authorized']);self.assertFalse((ROOT/p.AUTHORITY).exists());self.assertFalse((ROOT/p.DESTINATION).exists())
    def test_LB63(self):self.assertEqual(self.reg['semantic_baseline'],dict(SUPPORTS_BOUNDED=81,PARTIAL=3));self.assertFalse(p.plan()['closure'])
    def test_LB64(self):
        ledger=self.diag('EVENT_CAMPAIGN_BUDGET');ledger.fail('OK');self.assertEqual(ledger.value()['code'],'EVENT_CAMPAIGN_BUDGET');self.assertEqual(self.reg['limits'],json.loads((ROOT/p.t.REGISTRY).read_text())['limits']);self.assertEqual(forbidden(),[])

    def integration(self,mode):
        # Inject only the fixed worker's dependencies inside a separate synthetic child.
        # Its real main, channels, finalization and parent launcher run unchanged.
        with owned() as (base,root,owner):
            (root/'runner.py').write_text('SYNTHETIC_RUNNER_INPUT\n');before={'packet/runner.py':c.sha((root/'runner.py').read_bytes())};_,entry=example({'test_one':lambda s:None});entry.update(runner_module='lb_synthetic_runner',runner_path='packet/runner.py',runner_explicit_input_paths=['packet/runner.py'],runner_discovery_patterns=[],runner_effective_inputs=before)
            resolver,modules=self.bindings(base);reg=dict(entry=entry,policies=[],class_allowlist=list(resolver.specs.values()),snapshot_scopes=[],negative_DI28={},operand_scopes=[]);
            if mode=='late':reg['operand_scopes']=[dict(test_id=entry['expected_test_ids'][0],helper='assertIsInstance',operand_roles={'0':['exact-PlaneError-instance-args-projection'],'1':['class-'+PLANE]})]
            approved=dict(capture_inputs=before);children=[];real_popen=subprocess.Popen
            script='''import sys,json,types,unittest
from pathlib import Path
from testing.prospective_capture_late import capture as p,worker as w
args=sys.argv[1:7];reg=json.loads(sys.argv[7]);approved=json.loads(sys.argv[8]);root=Path(sys.argv[9]);mode=sys.argv[10]
p.read_registry=lambda *a:reg
p.authority=lambda *a:approved
if mode=='untrusted':
 def reject(*a):raise p.c.CaptureFault('I80_AUTHORIZATION_REQUIRED')
 p.authority=reject
module=types.ModuleType('lb_synthetic_runner');module.__file__=str(root/'packet/runner.py')
loaded={}
class SyntheticResolver(p.LateBindings):
 def __init__(self,specs,reader):super().__init__(specs,reader,lookup=loaded.get)
if mode=='late':p.LateBindings=SyntheticResolver
class Example(unittest.TestCase):
 def test_one(self):
  if mode=='late':
   cls=loaded['source_ingest.plane_fixture'].PlaneError;self.assertIsInstance(cls('CODE'),cls)
  else:self.assertEqual(1,1)
Example.__module__='lb_synthetic'
def main():
 if mode=='late':
  assert not loaded
  local=types.ModuleType('source_ingest.plane_fixture');local.PlaneError=type('PlaneError',(ValueError,),dict(__module__='source_ingest.plane_fixture'));loaded[local.__name__]=local
 result=unittest.TestResult();unittest.defaultTestLoader.loadTestsFromTestCase(Example).run(result)
 print(json.dumps(dict(status='PASS',tests_run=1,passed=reg['entry']['expected_test_ids'],failures=[],errors=[],skipped=[],scenarios=[],case_test_map={})));return 0
module.main=main
w.importlib.import_module=lambda name:module
def targets(*args):
 if mode=='failure':raise p.c.CaptureFault('UNSUPPORTED_OBSERVER_API')
 return [],None,None
w.targets=targets
sys.exit(w.main(args,root))
'''
            def producer(cmd,**kwargs):
                kwargs['cwd']=ROOT;child=real_popen([sys.executable,'-B','-c',script,*cmd[-6:],json.dumps(reg),json.dumps(approved),str(base),mode],**kwargs);children.append(child);return child
            (base/'docs/validation').mkdir(parents=True)
            with patch.object(p,'read_registry',return_value=reg),patch.object(p,'authority',return_value=approved),patch.object(c.subprocess,'Popen',side_effect=producer):
                context=p.launch('P01',base);self.assertRaises(FileExistsError,p.launch,'P01',base)
            for child in children:CHILDREN.append(dict(exitcode=child.returncode,kind='SYNTHETIC_LATE_WORKER_'+mode.upper()))
            self.assertEqual(context['cleanup']['status'],'OWN_GROUP_GONE');self.assertEqual(json.loads((base/p.LAUNCH_COPY).read_text()),context)
            if mode in ('success','late'):self.assertEqual(context['capture_status'],'TRACE_CAPTURED_PENDING_SUFFICIENCY_REVIEW',context);self.assertEqual(context['worker_diagnostic']['status'],'COMPLETED');self.assertEqual(context['page_validation']['status'],'PAGE_BINDINGS_VERIFIED')
            elif mode=='failure':self.assertEqual(context['capture_status'],'BLOCKED_WORKER_FAILURE',context);self.assertEqual(context['worker_diagnostic']['phase'],'TARGETS');self.assertEqual(context['worker_diagnostic']['code'],'UNSUPPORTED_OBSERVER_API');self.assertEqual((base/p.DESTINATION/'runner-raw.json').stat().st_size,0)
            else:self.assertEqual(context['worker_diagnostic_status'],'WORKER_DIAGNOSTIC_NOT_RECORDED');self.assertEqual((base/p.DESTINATION/'sidecar.json').stat().st_size,0)
            self.observations.append(dict(producer='SYNTHETIC_ONLY',mode=mode,capture_status=context['capture_status'],cleanup=context['cleanup']))
