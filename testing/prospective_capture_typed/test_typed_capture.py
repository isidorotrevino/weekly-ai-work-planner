# SPDX-License-Identifier: GPL-3.0-only
"""AT80: new synthetic fixtures and processes; never imports historical runners."""
import ast
import contextlib
import copy
import hashlib
import hmac
import io
import json
import os
from pathlib import Path
import pathlib
import signal
import subprocess
import sys
import tempfile
import types
import unittest
from unittest.mock import patch
from testing.prospective_capture_typed import capture as p,worker as w
c=p.c;ROOT=p.ROOT
ROOTS=[];CHILDREN=[]
RID='11111111-1111-4111-8111-111111111111';SID='22222222-2222-4222-8222-222222222222'
KEY=b'synthetic-key-material-32-bytes!!'
KEY=KEY[:32]


@contextlib.contextmanager
def owned():
    row=dict(ownership_verified=False,removed=False,sibling_preserved=False);ROOTS.append(row)
    with tempfile.TemporaryDirectory(prefix='i76-own-') as temp:
        base=Path(temp);root=base/'packet';root.mkdir();owner=c.OwnedRoot(root);sibling=base/'sibling';sibling.write_bytes(b'SYNTHETIC_SIBLING')
        try:yield base,root,owner
        finally:owner.verify();row['ownership_verified']=True;row['sibling_preserved']=sibling.read_bytes()==b'SYNTHETIC_SIBLING'
    row['removed']=not base.exists()

def example(methods,domain=False,module='at_synthetic',name='Example',records=False):
    cls=type(name,(unittest.TestCase,),dict(__module__=module,**methods));ids=[module+'.'+name+'.'+k for k in sorted(methods)]
    entry=dict(id='P01_SYNTHETIC_ONLY',expected_test_ids=ids,expected_tests=len(ids),expected_groups={module:len(ids)},group_policies={module:dict(target='SYNTHETIC_COMPONENT_ONLY',domain_required=domain,no_store_reason=None if domain else 'SYNTHETIC_UNIT_NO_DURABLE_BOUNDARY')},record_sources=[dict(module='at_records',field='RECORDS',raw_pointer='/scenarios')] if records else [],method_bindings={tid:dict(status='SOURCE_DERIVED_EXPECTATION',scope='SYNTHETIC_ONLY') for tid in ids},expected_raw_scenarios=1 if records else 0,expected_scenario_multiplicity={'SYNTHETIC':1} if records else {})
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

class PlaneError(ValueError):pass
class EligibilityError(ValueError):pass


def bindings():return p.ClassBindings([('builtins.dict',dict,None,None,None),('source_ingest.plane_fixture.PlaneError',PlaneError,'a'*64,None,None),('source_ingest.eligibility_fixture.EligibilityError',EligibilityError,'b'*64,None,None)])


class Fixture:
    def __init__(self,root,run_id,scope,*,test_fault=None,test_ready=None):
        if root=='raise':raise LookupError('SYNTHETIC')
        self.out=dict(schema='d5.fixture-drive-snapshot.v1',run_id=run_id,version=0,head_sha256='a'*64);self.calls=0
    def snapshot(self):self.calls+=1;return self.out


def fixture(rid=RID):return Fixture('synthetic',rid,{})

def discard(fn,*args,**kwargs):fn(*args,**kwargs)

def forbidden():return sorted(n for n in sys.modules if n.startswith(('source_ingest','testing.D5','testing.durable_','testing.gi39_interleavings','testing.causal_frontier_cells','testing.evidence_audit','testing.evidence_trace')) or n in ('testing.prospective_capture_paged.test_paged_capture','testing.prospective_capture_paged.run_paged_lab'))


class TypedTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):cls.reg=p.read_registry()
    def setUp(self):self.observations=[]
    def err(self,code,fn,*args,**kwargs):
        with self.assertRaises(c.CaptureFault) as got:fn(*args,**kwargs)
        self.assertEqual(got.exception.code,code);self.observations.append(dict(expected=code,observed=got.exception.code))
    def proj(self,**kwargs):return p.Projector(RID,bindings(),key=KEY,**kwargs)
    def suite(self,method=None,*,methods=None,mode='unit',operand=None,limits=None,before=None,after=None,verify=True,records=None):
        methods=methods or {'test_one':method or (lambda s:s.assertTrue(True))};cls,entry=example(methods,domain=mode in ('snapshot','negative','domain'),records=records is not None);ids=entry['expected_test_ids'];profile=dict(snapshot_scopes=[dict(test_id=ids[0])] if mode=='snapshot' else [],negative_DI28=dict(criterion=dict(test_id=ids[0])) if mode=='negative' else {},operand_scopes=[dict(test_id=ids[0],helper=operand[0],operand_roles=operand[1])] if operand else [])
        data=types.ModuleType('at_records');data.RECORDS=records if records is not None else []
        with owned() as (base,root,owner),patch.dict(sys.modules,{'at_records':data}):
            out=io.StringIO();side=w.exercise(entry,lambda:run_suite(cls,entry,data.RECORDS,before,after),out,owner,observed=[(Fixture,'snapshot')],fixture_class=Fixture,profile=profile,bindings=bindings(),limits=limits)
            raw=json.loads(out.getvalue()) if out.getvalue() else None
            if verify and side.get('status')=='TRACE_CAPTURED_PENDING_SUFFICIENCY_REVIEW':p.validate_pages(p.evidence_reader(base),'packet',side,limits,profile)
            events=all_events(root,side);self.observations.append(dict(status=side['status'],raw_status=raw.get('status') if raw else None,event_count=side.get('event_count')));return side,raw,events
    def snapshot(self,edit=None,verify=True):
        def test(s):
            st=fixture()
            if edit:edit(st)
            st.snapshot()
        return self.suite(test,mode='snapshot',verify=verify)
    def path_witness(self,value=None,allowed=None,proj=None):return (proj or self.proj()).observe(Path('/component-private/a') if value is None else value,allowed or ['exact-posix-path'])
    def test_AT01(self):
        with owned() as (base,root,owner):
            self.err('I77_AUTHORIZATION_REQUIRED',p.authority,base,'P01',self.reg)
            with patch.object(p,'read_registry',return_value=self.reg),patch.object(w.importlib,'import_module') as imp,contextlib.redirect_stderr(io.StringIO()):self.assertEqual(w.main(['P01','4','5','6','7',RID],base),2);imp.assert_not_called()
    def test_AT02(self):
        for name,h in json.loads((ROOT/'docs/validation/D5-I75-integrity.json').read_text())['artifacts'].items():self.assertEqual(c.sha((ROOT/name).read_bytes()),h)
        self.assertEqual(self.reg['contract_sha256'],c.sha((ROOT/self.reg['contract_path']).read_bytes()))
        # Exercise the real authority parser on a new synthetic tree, never the workspace gate.
        with owned() as (base,root,owner):
            def put(name,value):
                file=base/name;file.parent.mkdir(parents=True,exist_ok=True);file.write_text(json.dumps(value));return c.sha(file.read_bytes())
            component='packet/component.json';put(component,{'synthetic':True})
            raw='docs/validation/D5-I76-tests-raw.json';seal='docs/validation/D5-I76-integrity.json'
            put(raw,dict(status='PASS',tests_run=80,functional_campaigns_executed=0,forbidden_imports=[]));put(seal,dict(artifacts={component:c.sha((base/component).read_bytes())}));registry_hash=put(p.REGISTRY,{'synthetic':True})
            names=[component,raw,seal,p.REGISTRY];pins={n:c.sha((base/n).read_bytes()) for n in names}
            put(p.AUTHORITY,dict(schema='d5.typed-capture-authority.v1',phase='I77_EXPLICITLY_APPROVED',scopes=['P01'],registry_sha256=registry_hash,capture_inputs=pins))
            with patch.object(p,'authority_inputs',return_value={component,raw,seal,p.REGISTRY}):
                self.assertEqual(p.authority(base,'P01',{} )['capture_inputs'],pins)
                put(component,{'synthetic':'changed'});self.err('STALE_AUTHORITY',p.authority,base,'P01',{})
    def test_AT03(self):
        for bad in ('P02','../P01','module:any','P01 anything'):self.err('INVALID_SCOPE',p.scope,bad)
    def test_AT04(self):
        old=json.loads((ROOT/p.previous.REGISTRY).read_text());self.assertEqual(self.reg['entry'],old['entry']);self.assertEqual(self.reg['policies'],old['policies'])
    def test_AT05(self):
        snap={r['test_id'] for r in self.reg['snapshot_scopes']};neg=self.reg['negative_DI28']['criterion']['test_id'];self.assertEqual(len(snap),29);self.assertNotIn(neg,snap)
        side,_,_=self.suite(lambda s:discard(fixture().snapshot),mode='domain',verify=False);self.assertIn('DOMAIN_IDENTITY_NOT_RECORDED',side['frames'][0]['missing'])
    def test_AT06(self):
        value=Path('/component-private/a');self.assertEqual(self.proj().observe(value,['class-builtins.dict'])['status'],'NOT_RECORDED')
        side,_,_=self.suite(lambda s:s.assertEqual(value,value),operand=('assertNotEqual',{'0':['exact-posix-path'],'1':['exact-posix-path']}),verify=False);self.assertIn('OPERAND_NOT_RECORDED',side['frames'][0]['missing'])
    def test_AT07(self):self.assertEqual(forbidden(),[]);self.assertEqual(p.plan()['status'],'NOT_RUN_I77_AUTHORIZATION_REQUIRED')
    def test_AT08(self):self.err('CLASS_MODULE_NOT_LOADED',p.loaded_bindings,dict(class_allowlist=[dict(id='at_module_missing.PlaneError',source={})]))
    def test_AT09(self):self.assertFalse(self.reg['functional_execution_authorized']);self.assertFalse((ROOT/p.AUTHORITY).exists());self.observations.append(dict(authority='COHERENCE_GATE_NOT_HUMAN_ATTESTATION'))
    def test_AT10(self):self.assertTrue((ROOT/'docs/validation/D5-I74-capture-authorization.json').exists());self.assertNotIn('testing.prospective_capture_paged.test_paged_capture',sys.modules)
    def test_AT11(self):
        side,_,_=self.snapshot();obs=next(iter(side['drive_observations'].values()));self.assertEqual(obs['run_id'],RID);self.assertEqual(obs['authority'],p.DRIVE_OBS);self.assertTrue(all(v['identity'] is None for v in side['owner_contexts'].values()))
    def test_AT12(self):
        self.snapshot(lambda st:st.out.update(version=1023))
        for bad in (-1,1024,True):
            side,raw,_=self.snapshot(lambda st:st.out.update(version=bad),False);self.assertIn('INVALID_DRIVE_SNAPSHOT',side['errors']);self.assertEqual(raw['status'],'PASS')
    def test_AT13(self):
        for key,bad in [('run_id','NOT_UUID'),('head_sha256','F'*64)]:
            side,_,_=self.snapshot(lambda st:st.out.update({key:bad}),False);self.assertIn('INVALID_DRIVE_SNAPSHOT',side['errors'])
    def test_AT14(self):
        class D(dict):pass
        for edit in [lambda st:st.out.update(schema='other'),lambda st:setattr(st,'out',D(st.out))]:
            side,_,_=self.snapshot(edit,False);self.assertIn('INVALID_DRIVE_SNAPSHOT',side['errors'])
    def test_AT15(self):
        side,_,_=self.snapshot();serialized=json.dumps(side['drive_observations']);self.assertNotIn('store_id',serialized);self.assertNotIn('scope_sha256',serialized)
    def test_AT16(self):
        def test(s):st=fixture();st.snapshot();st.out.update(version=1,head_sha256='b'*64);st.snapshot()
        side,_,_=self.suite(test,mode='snapshot');self.assertEqual([o['version'] for o in side['drive_observations'].values()],[0,1]);self.assertEqual(len(side['drive_identities']),1)
    def test_AT17(self):
        def test(s):st=fixture();st.snapshot();st.out['run_id']=SID;st.snapshot()
        side,raw,_=self.suite(test,mode='snapshot',verify=False);self.assertIn('DRIVE_IDENTITY_CHANGED',side['errors']);self.assertEqual(next(iter(side['drive_identities'].values()))['run_id'],RID);self.assertEqual(raw['status'],'PASS')
    def test_AT18(self):
        box=[]
        def test(s):box.extend([fixture(),fixture()]);box[0].snapshot();box[1].snapshot()
        side,_,_=self.suite(test,mode='snapshot');self.assertEqual(len(side['drive_identities']),2)
    def test_AT19(self):
        box=[]
        def test(s):st=fixture();box.append(st);s.assertIs(st.snapshot(),st.out)
        self.suite(test,mode='snapshot');self.assertEqual(box[0].calls,1)
    def test_AT20(self):
        side,_,_=self.suite(lambda s:discard(fixture().snapshot),mode='domain',verify=False);self.assertFalse(side['drive_observations']);self.assertIn('DOMAIN_IDENTITY_NOT_RECORDED',side['frames'][0]['missing'])
    def test_AT21(self):
        side,_,_=self.suite(lambda s:discard(fixture),mode='negative');self.assertEqual(len(side['fixture_construction_declarations']),1);self.assertFalse(side['drive_observations']);self.assertEqual(side['frames'][0]['domain_scope']['status'],'NEGATIVE_DOMAIN_FIXTURE_CLEANUP')
    def test_AT22(self):
        side,raw,_=self.suite(lambda s:s.assertRaises(LookupError,Fixture,'raise',RID,{}),mode='negative',verify=False);self.assertFalse(side['fixture_construction_declarations']);self.assertIn('FIXTURE_CONSTRUCTION_NOT_RECORDED',side['frames'][0]['missing']);self.assertEqual(raw['status'],'PASS')
    def test_AT23(self):
        side,_,_=self.suite(lambda s:discard(fixture),mode='negative');decl=next(iter(side['fixture_construction_declarations'].values()));self.assertEqual(set(decl),{'run_id','authority','process_scope'})
    def test_AT24(self):
        side,_,_=self.suite(mode='negative',before=fixture,verify=False);self.assertFalse(side['fixture_construction_declarations']);self.assertIn('FIXTURE_CONSTRUCTION_NOT_RECORDED',side['frames'][0]['missing'])
    def test_AT25(self):
        box=[]
        def test(s):box.extend([fixture(),fixture()])
        side,_,_=self.suite(test,mode='negative');self.assertEqual(len(side['frames'][0]['fixture_construction_refs']),2)
    def test_AT26(self):
        side,_,events=self.suite(lambda s:discard(fixture),mode='negative');self.assertNotEqual(side['frames'][0]['domain_scope']['status'],'NOT_APPLICABLE');self.assertFalse(any(e.get('method')=='snapshot' for e in events))
    def test_AT27(self):
        side,raw,_=self.suite(lambda s:discard(fixture),mode='negative');self.assertEqual(raw['status'],'PASS');self.assertEqual(next(iter(side['fixture_construction_declarations'].values()))['authority'],p.FIXTURE_DECL)
    def test_AT28(self):
        side,_,_=self.suite(lambda s:discard(fixture),mode='negative');self.assertTrue(all(d['process_scope']=='PARENT_ONLY' for d in side['fixture_construction_declarations'].values()));self.assertIn('NOT_PARENT_INSTRUMENTATION',side['child_context_scope'])
    def test_AT29(self):
        side,_,_=self.suite(lambda s:discard(fixture),mode='snapshot',verify=False);self.assertFalse(side['fixture_construction_declarations']);self.assertIn('DOMAIN_IDENTITY_NOT_RECORDED',side['frames'][0]['missing'])
    def test_AT30(self):
        def test(s):st=fixture();Fixture.__init__(st,'synthetic',SID,{})
        side,raw,_=self.suite(test,mode='negative',verify=False);self.assertIn('FIXTURE_CONSTRUCTION_IDENTITY_CHANGED',side['errors']);self.assertEqual(next(iter(side['fixture_construction_declarations'].values()))['run_id'],RID)
    def test_AT31(self):
        value=Path('/component-private/a');got=self.path_witness(value);token=hmac.new(KEY,b'd5.path.lexical.v1\0'+b'/component-private/a',hashlib.sha256).hexdigest();node=dict(kind='posix-path',token=token,scope=RID);expected=hashlib.sha256(b'd5.typed-operand-projection.v1\0'+p.canonical(node)).hexdigest();self.assertEqual(got['digest_hex'],expected);self.assertEqual(got,self.path_witness(value))
    def test_AT32(self):
        calls=[]
        def test(s):calls.append('original');s.assertNotEqual(Path('/component-private/a'),Path('/component-private/b'))
        side,raw,_=self.suite(test,operand=('assertNotEqual',{'0':['exact-posix-path'],'1':['exact-posix-path']}));self.assertEqual(calls,['original']);self.assertEqual(raw['status'],'PASS')
    def test_AT33(self):
        for value,graph in [((Path('/x'),'a'*64),'exact-tuple(exact-posix-path,builtin-str)'),([Path('/x')],'exact-list(exact-posix-path)')]:self.assertEqual(self.proj().observe(value,[graph])['status'],'OBSERVED_TYPED_PROJECTION')
    def test_AT34(self):
        class Trap(pathlib.PosixPath):
            def __str__(self):raise AssertionError('NO_COERCION')
            def __repr__(self):raise AssertionError('NO_REPR')
        self.assertEqual(self.path_witness(Trap('/x'))['status'],'NOT_RECORDED')
    def test_AT35(self):
        projector=self.proj()
        with patch.object(pathlib.PurePath,'as_posix',side_effect=AssertionError('NO_CALL')):self.assertEqual(self.path_witness(proj=projector)['reason'],'STDLIB_BINDING_CHANGED')
    def test_AT36(self):
        for value in [Path('relative'),Path('/absolute/á'),Path('/a\udcff')]:self.assertEqual(self.path_witness(value)['status'],'OBSERVED_TYPED_PROJECTION')
        with patch.object(pathlib.PosixPath,'resolve',side_effect=AssertionError('NO_IO')):self.path_witness()
    def test_AT37(self):
        got=self.path_witness();data=json.dumps(got);self.assertNotIn('/component-private',data);self.assertNotIn(KEY.decode(),data);projector=self.proj();projector.erase();self.assertEqual(self.path_witness(proj=projector)['reason'],'PATH_KEY_ERASED')
    def test_AT38(self):
        a=self.path_witness(proj=self.proj());b=self.path_witness(proj=p.Projector(RID,bindings(),key=b'y'*32));self.assertNotEqual(a['digest_hex'],b['digest_hex']);self.assertEqual(a['path_scope'],RID)
    def test_AT39(self):
        self.assertEqual(self.path_witness(proj=self.proj(limits=dict(operand_bytes=20)))['reason'],'OPERAND_BUDGET');x=[];x.append(x);self.assertEqual(self.proj().observe(x,['exact-list(exact-posix-path)'])['status'],'NOT_RECORDED')
    def test_AT40(self):
        got=self.path_witness();p.typed_witness(got,['exact-posix-path'],RID);self.assertNotIn('key',got);self.assertNotIn('sha256',got);self.assertEqual(got['digest_algorithm'],'SHA256_OF_TYPED_REPRESENTATION')
    def test_AT41(self):
        got=self.proj().observe(dict,['class-builtins.dict']);self.assertEqual(got['class_refs'],['builtins.dict']);self.assertEqual(got['root_type'],'type')
    def test_AT42(self):
        for cls,ref in [(PlaneError,'source_ingest.plane_fixture.PlaneError'),(EligibilityError,'source_ingest.eligibility_fixture.EligibilityError')]:self.assertEqual(self.proj().observe(cls,['class-'+ref])['class_refs'],[ref])
    def test_AT43(self):
        calls=[]
        class Meta(type):
            def __instancecheck__(self,obj):calls.append('instancecheck');return True
        class C(metaclass=Meta):pass
        self.assertEqual(self.proj().observe(C,[])['status'],'NOT_RECORDED');self.assertEqual(calls,[])
        self.suite(lambda s:s.assertIsInstance(object(),C),operand=('assertIsInstance',{'0':[],'1':[]}),verify=False);self.assertEqual(calls,['instancecheck'])
    def test_AT44(self):
        class Child(PlaneError):pass
        self.assertEqual(self.proj().observe(Child('CODE'),['exact-PlaneError-instance-args-projection'])['status'],'NOT_RECORDED')
    def test_AT45(self):
        ex=PlaneError('CONFLICT_LEDGER');got=self.proj().observe(ex,['exact-PlaneError-instance-args-projection']);node=dict(kind='exception-type-args',class_ref='source_ingest.plane_fixture.PlaneError',source_sha256='a'*64,args_sha256=c.digest_value(ex.args)['sha256']);self.assertEqual(got['digest_hex'],hashlib.sha256(b'd5.typed-operand-projection.v1\0'+p.canonical(node)).hexdigest())
    def test_AT46(self):
        got=self.proj().observe(EligibilityError('STALE_ACCOUNT'),['exact-EligibilityError-instance-args-projection']);self.assertEqual(got['status'],'OBSERVED_TYPED_PROJECTION');self.assertNotIn('STALE_ACCOUNT',json.dumps(got))
    def test_AT47(self):
        for args in [('lower',),('CODE','EXTRA'),(Path('/private'),),('X'*81,)]:self.assertEqual(self.proj().observe(PlaneError(*args),['exact-PlaneError-instance-args-projection'])['reason'],'EXCEPTION_ARGS_NOT_ALLOWED')
    def test_AT48(self):
        module=types.ModuleType('at_bindings');module.PlaneError=PlaneError
        with patch.dict(sys.modules,{'at_bindings':module}):
            b=p.ClassBindings([('source_ingest.plane_fixture.PlaneError',PlaneError,'a'*64,module,'PlaneError')]);module.PlaneError=EligibilityError;self.err('CLASS_BINDING_CHANGED',b.check)
    def test_AT49(self):
        roles={'0':['exact-PlaneError-instance-args-projection'],'1':['class-source_ingest.plane_fixture.PlaneError']};side,raw,_=self.suite(lambda s:s.assertIsInstance(PlaneError('CODE'),PlaneError),operand=('assertIsInstance',roles));self.assertEqual(raw['status'],'PASS');self.assertFalse(side['frames'][0]['missing'])
    def test_AT50(self):
        roles={'0':['builtin-only-original-digest'],'1':['class-builtins.dict']};side,raw,events=self.suite(lambda s:s.assertIsInstance({},dict),operand=('assertIsInstance',roles));ops=next(e['operands'] for e in events if e.get('helper')=='assertIsInstance');self.assertEqual(ops[0],c.digest_value({}));self.assertEqual(ops[1]['status'],'OBSERVED_TYPED_PROJECTION')
    def test_AT51(self):
        for value in [None,True,2,1.5,'a',b'b',{},[],(1,'x'),{'a':[2]},set([1,2])]:self.assertEqual(self.proj().observe(value,[]),c.digest_value(value))
    def test_AT52(self):
        witness=self.proj().observe(dict,['class-builtins.dict']);bad=dict(witness,root_type='PlaneError');self.err('INVALID_TYPED_WITNESS',p.typed_witness,bad,['class-builtins.dict'],RID)
        bad=dict(witness,class_refs=['source_ingest.plane_fixture.PlaneError']);self.err('INVALID_TYPED_WITNESS',p.typed_witness,bad,['class-builtins.dict'],RID)
        got=self.proj().observe([Path('/x')],['exact-list(exact-posix-path)']);self.assertEqual(got['schema'],p.TYPED_SCHEMA);self.assertNotIn('sha256',got)
    def test_AT53(self):
        side,raw,events=self.suite(lambda s:s.assertEqual([Path('/x')],[Path('/x')]),operand=('assertEqual',{'0':['exact-list(exact-posix-path)'],'1':['exact-list(exact-posix-path)']}));self.assertEqual(sum(e['event']=='ASSERTION_RETURNED' for e in events),1)
    def test_AT54(self):
        def test(s):
            with s.subTest(v=1):s.assertEqual(1,2)
        side,raw,_=self.suite(test);self.assertEqual(raw['status'],'FAIL');self.assertEqual(side['frames'][0]['result'],'FAIL')
    def test_AT55(self):
        side,raw,_=self.suite(lambda s:s.skipTest('SYNTHETIC'));self.assertEqual(side['frames'][0]['result'],'SKIP');self.assertEqual(len(raw['skipped']),1)
    def test_AT56(self):
        with patch.object(p.Projector,'observe',side_effect=OSError('SYNTHETIC_PROJECTOR')):
            side,raw,_=self.suite(lambda s:s.assertEqual(Path('/x'),Path('/x')),operand=('assertEqual',{'0':['exact-posix-path'],'1':['exact-posix-path']}),verify=False);self.assertEqual(raw['status'],'PASS');self.assertIn('OPERAND_NOT_RECORDED',side['frames'][0]['missing']);self.assertIn('TYPED_PROJECTION_ERROR',side['errors']);self.assertEqual(side['status'],'INVALID_CAPTURE')
    def test_AT57(self):
        side,raw,_=self.suite(lambda s:s.assertIsInstance('a',str),operand=('assertIsInstance',{'0':[],'1':['class-builtins.dict']}),verify=False);self.assertEqual(raw['status'],'PASS');self.assertEqual(side['status'],'INCOMPLETE_CAPTURE')
    def test_AT58(self):
        side,_,_=self.suite(lambda s:discard(fixture().snapshot),mode='domain',verify=False);self.assertEqual(side['drive_identities'],{});self.assertIn('DOMAIN_IDENTITY_NOT_RECORDED',side['frames'][0]['missing'])
    def test_AT59(self):
        before=Fixture.__init__,Fixture.snapshot,unittest.TestCase.assertEqual,unittest.TestResult.startTest;self.suite(lambda s:discard(fixture().snapshot),mode='snapshot');self.assertEqual(before,(Fixture.__init__,Fixture.snapshot,unittest.TestCase.assertEqual,unittest.TestResult.startTest))
    def test_AT60(self):
        records=[]
        def test(s):records.append(dict(case='SYNTHETIC',run_id=RID,events=[],oracles=[],status='PASS'));s.assertTrue(True)
        side,_,_=self.suite(test,records=records,after=lambda:records[0].update(status='CHANGED'),verify=False);self.assertIn('RECORD_MUTATED_AFTER_TEST',side['errors']);self.assertEqual(len(self.reg['entry']['method_bindings']),321)
    def test_AT61(self):
        def test(s):
            for _ in range(12):s.assertEqual([Path('/x')],[Path('/x')])
        side,_,_=self.suite(test,operand=('assertEqual',{'0':['exact-list(exact-posix-path)'],'1':['exact-list(exact-posix-path)']}),limits=dict(page_bytes=1400));self.assertGreater(len(side['pages']),2)
    def test_AT62(self):
        side,_,_=self.suite(methods={'test_a':lambda s:s.assertTrue(True),'test_b':lambda s:s.assertTrue(True)});self.assertEqual(len(side['frames']),2);self.assertEqual(len(side['pages']),1)
    def test_AT63(self):
        side,raw,_=self.suite(lambda s:discard(lambda:[s.assertTrue(True) for _ in range(10)]),limits=dict(events_campaign=3),verify=False);self.assertIn('EVENT_CAMPAIGN_BUDGET',side['errors']);self.assertEqual(raw['status'],'PASS');self.assertEqual(p.LIMITS['events_campaign'],131072)
        with owned() as (base,root,owner):
            sink=p.PageSink(owner,RID)
            for i in range(131072):sink.append(dict(event='SYNTHETIC_BOUNDARY',sequence=i))
            self.err('EVENT_CAMPAIGN_BUDGET',sink.append,dict(event='SYNTHETIC_BOUNDARY',sequence=131072));sink.close();self.assertEqual(sink.count,131072)
        side,_,_=self.suite(lambda s:discard(lambda:[s.assertTrue(True) for _ in range(2049)]),verify=False);self.assertIn('EVENT_TEST_BUDGET',side['errors'])
    def test_AT64(self):
        with owned() as (base,root,owner):
            sink=p.PageSink(owner,RID,dict(page_bytes=260,pages=2))
            for i in range(2):sink.append(dict(event='N',sequence=i,value='x'*40))
            self.assertRaises(c.CaptureFault,lambda:[sink.append(dict(event='N',sequence=i,value='x'*40)) for i in range(2,20)])
        self.assertEqual(p.LIMITS['event_pages_total_bytes'],64*1024*1024)
    def test_AT65(self):
        with owned() as (base,root,owner):self.err('EVENT_SIZE_BUDGET',p.PageSink(owner,RID).append,dict(sequence=0,event='N',value='x'*4096))
        self.assertEqual(self.path_witness(proj=self.proj(limits=dict(operand_bytes=16)))['reason'],'OPERAND_BUDGET')
    def test_AT66(self):
        side,_,_=self.suite(lambda s:discard(fixture().snapshot),mode='snapshot',limits=dict(refs=1),verify=False);self.assertIn('REFERENCE_BUDGET',side['errors'])
        x=0
        for _ in range(34):x=[x]
        self.assertEqual(self.proj().observe(x,[])['reason'],'OPERAND_DEPTH')
    def test_AT67(self):self.err('PACKAGE_FILE_BUDGET',p.package_size,{'sidecar.json':13*1024*1024});self.err('PACKAGE_BUDGET',p.package_size,{'OWNER':2},dict(package_bytes=1))
    def test_AT68(self):
        with owned() as (base,root,owner):
            (root/'a').write_bytes(b'12');reader=p.evidence_reader(base,dict(evidence_read_bytes=3));reader.read('packet/a');self.err('READ_BUDGET',reader.read,'packet/a')
            reader=c.Reader(base,dict(unique_bytes=1));self.err('UNIQUE_BUDGET',reader.read,'packet/a')
    def test_AT69(self):
        class Wait:
            def wait(self,timeout):self.seen=timeout;raise subprocess.TimeoutExpired('SYNTHETIC',timeout)
        wait=Wait();self.assertFalse(p.wait_worker(wait,0.01));self.assertEqual(wait.seen,0.01);self.assertEqual(p.LIMITS['campaign_seconds'],900)
    def test_AT70(self):
        side,raw,events=self.suite(limits=dict(events_campaign=3),verify=False);self.assertEqual(raw['status'],'PASS');self.assertNotIn('TEST_END',[e['event'] for e in events]);self.assertEqual(side['status'],'INVALID_CAPTURE')
    def test_AT71(self):
        with owned() as (base,root,owner):
            fd=owner.create('keep');p.write_all(fd,b'ORIGINAL');os.close(fd)
            with self.assertRaises(FileExistsError):owner.create('keep')
            (root/'link').symlink_to(base/'sibling');self.err('NONREGULAR_FILE',c.Reader(base).read,'packet/link');self.err('INVALID_PUBLIC_PATH',c.public_path,'../sibling')
    def integration(self):
        # Exercise the production launcher with a separately owned synthetic producer.
        # Its factory is injected here only; the public launcher never accepts a module.
        with owned() as (base,root,owner):
            (root/'runner.py').write_bytes(b'SYNTHETIC_INPUT');before={'packet/runner.py':c.sha((root/'runner.py').read_bytes())}
            _,entry=example({'test_one':lambda s:None});entry.update(runner_explicit_input_paths=['packet/runner.py'],runner_discovery_patterns=[],runner_effective_inputs=before)
            reg=dict(entry=entry,snapshot_scopes=[],negative_DI28={},operand_scopes=[]);approved=dict(capture_inputs=before);real_popen=subprocess.Popen;children=[]
            script="""import sys,os,json,unittest
from testing.prospective_capture_typed import capture as p,worker as w
c=p.c
scope,side,ready,release,directory,lease=sys.argv[1:7]
side,ready,release,directory=map(int,(side,ready,release,directory))
entry=json.loads(sys.argv[7]);before=json.loads(sys.argv[8]);owner=p.ChannelRoot(directory,lease);st=os.fstat(directory)
message=dict(event='READY',scope='P01',lease=lease,pid=os.getpid(),pgid=os.getpgid(0),raw_inode=os.fstat(1).st_ino,sidecar_inode=os.fstat(side).st_ino,directory_device=st.st_dev,directory_inode=st.st_ino)
c.write_json_fd(ready,message,4096);p.write_all(ready,b'\\n');os.close(ready)
p.verify_release(c.receive_line(release,20),lease);os.close(release)
class Example(unittest.TestCase):
 def test_one(self):self.assertEqual(1,1)
Example.__module__='at_synthetic'
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
            for child in children:CHILDREN.append(dict(exitcode=child.returncode,kind='SYNTHETIC_TYPED_LAUNCH'))
            self.assertEqual(context['capture_status'],'TRACE_CAPTURED_PENDING_SUFFICIENCY_REVIEW',context.get('error_code'));self.assertEqual(context['cleanup']['status'],'OWN_GROUP_GONE')
            self.assertEqual(json.loads((base/p.LAUNCH_COPY).read_text()),context)
            side=json.loads((base/p.DESTINATION/'sidecar.json').read_text());reader=p.evidence_reader(base);p.package_names(reader,p.DESTINATION,side)
            self.assertEqual(side['semantic_baseline'],dict(SUPPORTS_BOUNDED=81,PARTIAL=3));self.assertFalse(side['closure']);self.assertFalse(side['D5_closed']);self.assertEqual(side['sufficiency'],'REVIEW_PENDING')
            self.observations.append(dict(scope='SYNTHETIC_PRODUCER_ONLY',page_validation=context['page_validation'],cleanup=context['cleanup']))
    def test_AT72(self):
        with owned() as (base,root,owner):
            raw=owner.create('raw');side=owner.create('side');directory=owner.directory();child=subprocess.Popen([sys.executable,'-B','-c','import sys; sys.stdin.read()'],stdin=subprocess.PIPE,stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL,start_new_session=True)
            try:
                st=os.fstat(directory);msg=dict(event='READY',scope='P01',lease=owner.nonce,pid=child.pid,pgid=child.pid,raw_inode=os.fstat(raw).st_ino,sidecar_inode=os.fstat(side).st_ino,directory_device=st.st_dev,directory_inode=st.st_ino)
                p.verify_ready(msg,owner.nonce,child.pid,raw,side,directory)
                for key in ('lease','pid','pgid','raw_inode','sidecar_inode'):
                    bad=dict(msg);bad[key]=SID if key=='lease' else msg[key]+1;self.err('INVALID_WORKER_IDENTITY',p.verify_ready,bad,owner.nonce,child.pid,raw,side,directory)
                self.err('INVALID_DIRECTORY_CHANNEL',p.verify_ready,dict(msg,directory_inode=st.st_ino+1),owner.nonce,child.pid,raw,side,directory)
                self.err('INVALID_WORKER_RELEASE',p.verify_release,dict(event='RELEASE',lease=SID),owner.nonce)
            finally:
                done=c.stop_owned(child,owner,dict(pid=child.pid,pgid=child.pid,lease=owner.nonce));child.stdin.close();CHILDREN.append(dict(exitcode=child.returncode,kind='SYNTHETIC_READY_CHANNEL'));self.assertEqual(done['status'],'OWN_GROUP_GONE')
                for fd in (raw,side,directory):os.close(fd)
        self.integration()
    def test_AT73(self):
        with owned() as (base,root,owner):
            child=subprocess.Popen([sys.executable,'-B','-c','import sys; sys.stdin.read()'],stdin=subprocess.PIPE,stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL,start_new_session=True)
            try:
                identity=dict(pid=child.pid,pgid=child.pid,lease=owner.nonce);self.err('INVALID_WORKER_IDENTITY',c.stop_owned,child,owner,dict(identity,lease=SID))
            finally:done=c.stop_owned(child,owner,identity);child.stdin.close();CHILDREN.append(dict(exitcode=child.returncode,kind='SYNTHETIC_WAIT'))
            self.assertEqual(done['status'],'OWN_GROUP_GONE');self.assertNotEqual(child.returncode,-signal.SIGKILL)
    def test_AT74(self):
        for value in ['dev/x','run_data/x','.aws/x','private/x']:self.err('INVALID_PUBLIC_PATH',c.public_path,value)
        with owned() as (base,root,owner):self.assertEqual((base/'sibling').read_bytes(),b'SYNTHETIC_SIBLING')
    def test_AT75(self):self.assertEqual(len(self.reg['operand_scopes']),5);self.assertTrue(all(r['authority']=='STATIC_SOURCE_DESIGN_NOT_I74_RUNTIME_TYPE_ATTESTATION' for r in self.reg['operand_scopes']))
    def test_AT76(self):
        records=[]
        def test(s):records.append(dict(case='SYNTHETIC'));s.assertTrue(True)
        side,_,_=self.suite(test,records=records,verify=False);self.assertEqual(side['status'],'INCOMPLETE_CAPTURE');self.assertIn('INCOMPLETE_CHILD_SCENARIO',side['frames'][0]['missing'])
    def test_AT77(self):self.assertEqual(forbidden(),[]);self.assertNotIn('testing.prospective_capture_paged.run_paged_lab',sys.modules)
    def test_AT78(self):self.assertEqual(p.plan()['status'],'NOT_RUN_I77_AUTHORIZATION_REQUIRED');self.assertFalse((ROOT/p.AUTHORITY).exists());self.assertFalse((ROOT/p.DESTINATION).exists())
    def test_AT79(self):
        side,raw,_=self.suite(lambda s:s.assertIsInstance('x',str),verify=False);self.assertEqual(raw['status'],'PASS');self.assertEqual(side['status'],'INCOMPLETE_CAPTURE')
    def test_AT80(self):
        side,raw,_=self.suite(lambda s:discard(fixture().snapshot),mode='snapshot');self.assertEqual(side['status'],'TRACE_CAPTURED_PENDING_SUFFICIENCY_REVIEW');self.assertFalse(side['closure']);self.assertFalse(side['D5_closed']);self.assertEqual(side['semantic_baseline'],dict(SUPPORTS_BOUNDED=81,PARTIAL=3))
