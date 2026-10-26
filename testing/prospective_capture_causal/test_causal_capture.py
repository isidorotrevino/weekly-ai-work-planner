# SPDX-License-Identifier: GPL-3.0-only
"""CT96: new synthetic data, classes, suites and owned processes only."""
import ast
import contextlib
import copy
import io
import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import threading
import types
import unittest
from unittest.mock import patch
from testing.prospective_capture_causal import capture as p,worker as w
c=p.c;ROOT=p.ROOT;ROOTS=[];CHILDREN=[]
HISTORICAL_INPUTS={}
RID='11111111-1111-4111-8111-111111111111';SID='22222222-2222-4222-8222-222222222222';CID='33333333-3333-4333-8333-333333333333';HEX='a'*64


@contextlib.contextmanager
def owned():
    row=dict(ownership_verified=False,removed=False,sibling_preserved=False);ROOTS.append(row)
    with tempfile.TemporaryDirectory(prefix='i83-own-') as tmp:
        base=Path(tmp);root=base/'packet';root.mkdir();owner=c.OwnedRoot(root);sibling=base/'sibling';sibling.write_bytes(b'I83_SYNTHETIC_SIBLING')
        try:yield base,root,owner
        finally:owner.verify();row['ownership_verified']=True;row['sibling_preserved']=sibling.read_bytes()==b'I83_SYNTHETIC_SIBLING'
    row['removed']=not base.exists()


def forbidden():
    return sorted(n for n in sys.modules if n.startswith(('source_ingest','testing.D5','testing.durable_','testing.evidence_')) or n in ('testing.prospective_capture.run_capture_lab','testing.prospective_capture.test_prospective_capture','testing.prospective_capture_paged.test_paged_capture','testing.prospective_capture_paged.run_paged_lab','testing.prospective_capture_typed.test_typed_capture','testing.prospective_capture_typed.run_typed_lab','testing.prospective_capture_late.test_late_capture','testing.prospective_capture_late.run_late_lab'))


def row(kind='T'):
    v=dict(case='SYNTHETIC_CASE',role='CLIENT',store_id=SID,seq=1,state_sha256=p.canonical_hash({'receipts':{CID:receipt()}}),receipts=1)
    if kind=='T':v.update(commit_sha256=HEX,tasks=0)
    else:v.update(head_sha256=HEX,entities=0,relations=0)
    return v


def returned():return dict(head=dict(run_id=RID,store_id=SID,role='CLIENT',seq=1,commit_sha256=HEX),state={'receipts':{CID:receipt()}},chain=[dict(seq=1,command_id=CID,request_sha256=p.store_request(req())['request_sha256'],operation={k:req()[k] for k in ('kind','args','expected')},receipt={k:v for k,v in receipt().items() if k!='historical'})])

def req():return dict(cid=CID,kind='SYNTHETIC',args={'description':'PRIVATE_SYNTHETIC_PAYLOAD'},expected=dict(seq=0,commit_sha256=HEX))

def drive():return dict(schema='d5.fixture-drive-command.v1',command_id=CID,expected_version=0,expected_head=HEX,page={'events':[]})

def receipt():
    return dict(schema='d5.durable-receipt.v1',command_id=CID,request_sha256=p.store_request(req())['request_sha256'],before_seq=0,seq=1,before_state_sha256='b'*64,after_data_sha256='c'*64,historical=False,grants_execution_authority=False,quota_consumed=0,reservations_created=0,activation_allowed=False,result={'manifest_id':HEX,'text':'PRIVATE_SYNTHETIC_PAYLOAD'})

def dr_receipt():return dict(schema='d5.fixture-drive-receipt.v1',command_id=CID,request_sha256=p.drive_request(drive())['request_sha256'],version=1,result='SYNTHETIC_CAPTURE_CONFIRMED',reference_selected=False,persistent_D2_writes=0,remote_requests=0,commit_sha256=HEX)


def synthetic_child_reply(connection):
    connection.send(('READY','after_head'))
    connection.send(('OK',{'synthetic':True}))
    connection.close()


class CausalTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):cls.reg=p.read_registry();cls.spec=cls.reg['projection_schemas'];cls.design=json.loads((ROOT/p.CONTRACT).read_text())
    def setUp(self):self.observations=[]
    def check(self,value,label):self.assertTrue(value);self.observations.append(dict(check=label,status='PASS'))
    def err(self,code,fn,*args,**kwargs):
        with self.assertRaises(c.CaptureFault) as raised:fn(*args,**kwargs)
        self.assertEqual(raised.exception.code,code);self.observations.append(dict(expected=code,observed=raised.exception.code))
    def engine(self,limits=None):
        count=[0];errors=[];events=[];lim=dict(p.LIMITS,**(limits or {}))
        def charge(n=1):count[0]+=n;p.fault(count[0]<=lim['refs'],'REFERENCE_BUDGET')
        e=p.CausalState(RID,lim,self.spec,charge,lambda k,**v:events.append(dict(event=k,**v)),errors.append);e.begin(dict(test_frame_id='FRAME_SYNTHETIC',test_id='SYNTHETIC_CASE'),self);return e,events,errors
    def retained(self,kind='T'):
        e,events,errors=self.engine();obj=object();e.declaration(obj,dict(run_id=RID,store_id=SID,role='CLIENT'));key=e.open_call('T.independent',obj,'independent',{});ref=e.retain('ct_synthetic',0,row(kind),kind,returned(),key);e.close_call(key,dict(retained_refs=[ref]));return e,key,ref
    def side(self,e):
        f=dict(test_frame_id='FRAME_SYNTHETIC',test_id='SYNTHETIC_CASE',record_links=[],owner_context_refs=[key for _,_,key in e.domains])
        for key,r in e.tables['retained_oracles'].items():f['record_links'].append(dict(module=r['source_module'],field='ORACLES',index=r['source_index'],digest=r['value_digest'],raw_pointer=None,sidecar_pointer='/retained_oracles/'+key+'/value'))
        return dict(schema=p.NORMAL_SCHEMA,capture_run_id=RID,frames=[f],owner_contexts={key:dict(identity={k:v[k] for k in ('run_id','store_id')}) for (_,_,key),v in e.domains.items()},**e.tables)
    def recorder(self,owner):
        entry=dict(id='SYNTHETIC_ONLY',expected_test_ids=['SYNTHETIC_CASE'],expected_groups={'synthetic':1},group_policies={'synthetic':dict(domain_required=False,no_store_reason='SYNTHETIC')},record_sources=[],method_bindings={})
        bindings=p.LateBindings([dict(id='builtins.dict',source=None)],c.Reader(ROOT))
        r=p.Recorder(entry,owner,profile=self.reg,bindings=bindings);r.active=dict(test_id='SYNTHETIC_CASE',test_frame_id='FRAME_SYNTHETIC',event_count=0,owner_context_refs=[]);r.frame_summary=dict(operands_missing=False,returns_missing=False);r.causal_inventory['SYNTHETIC_CASE']=dict(family='T',classification='CAUSAL_DOMAIN');r.causal.begin(r.active,self);return r
    def test_CT01(self):
        self.check(not self.design['implementation_authorized'] and not self.design['functional_capture_execution_authorized'],'historical I82 flags preserved')
        for n,h in json.loads((ROOT/'docs/validation/D5-I82-integrity.json').read_text())['artifacts'].items():self.assertEqual(c.sha((ROOT/n).read_bytes()),h)
    def test_CT02(self):
        with patch.object(w.p,'read_registry',return_value=self.reg),patch.object(w.p,'authority',side_effect=c.CaptureFault('I84_AUTHORIZATION_REQUIRED')),patch.object(w.importlib,'import_module') as imp:
            self.assertEqual(w.main(['P01','4','5','6','7',RID]),2);imp.assert_not_called()
        self.check(forbidden()==[],'functional import unreachable without authority')
    def test_CT03(self):
        with owned() as (base,root,owner):self.err('I84_AUTHORIZATION_REQUIRED',p.authority,base,'P01',self.reg)
    def test_CT04(self):
        self.assertEqual(len(self.reg['inventory']),118);self.assertEqual(self.reg['entry']['expected_tests'],321);self.assertEqual(len(self.reg['entry']['expected_groups']),12)
        for scope in ['P02','P10','../P01']:self.err('INVALID_SCOPE',p.scope,scope)
    def test_CT05(self):self.assertEqual(p.plan()['status'],'NOT_RUN_I84_AUTHORIZATION_REQUIRED');self.check(not (ROOT/p.DESTINATION).exists(),'default plan creates no destination')
    def test_CT06(self):
        self.assertEqual(self.reg['entry'],p.late.read_registry()['entry']);self.check(self.reg['functional_execution_authorized'] is False,'history not recaptured by plan')
    def test_CT07(self):
        with owned() as (base,root,owner):
            fd=owner.create('exclusive');os.close(fd)
            with self.assertRaises(FileExistsError):owner.create('exclusive')
            (root/'link').symlink_to(base/'sibling')
            with self.assertRaises(FileExistsError):owner.create('link')
        self.observations.append(dict(exclusive='PRESERVED'))
    def test_CT08(self):self.check(self.design['projection_schemas']['sidecar']['no_new_file_or_pipe'] and not self.reg['functional_execution_authorized'],'file coherence not human authority')
    def test_CT09(self):
        for r in self.reg['inventory']:self.assertEqual(c.sha((ROOT/r['source_binding']['path']).read_bytes()),r['source_binding']['sha256'])
        self.observations.append(dict(anchors_verified=118))
    def test_CT10(self):self.assertEqual(sum(r['classification']=='NO_STORE_CONTROL' for r in self.reg['inventory']),5);self.check(not any(r['I80_observed']['oracle_records'] for r in self.reg['inventory'] if r['classification']=='NO_STORE_CONTROL'),'no invented oracle in controls')
    def test_CT11(self):self.assertEqual(sum(r['classification']!='CAUSAL_DOMAIN' for r in self.reg['inventory']),8);self.check(self.reg['negative_DI28']['constructor']['method']=='__init__','negative construction remains not head')
    def test_CT12(self):self.assertEqual(321-len(self.reg['inventory']),203);self.assertEqual(self.reg['operand_scopes'],p.late.read_registry()['operand_scopes'])
    def test_CT13(self):
        e,_,_=self.engine();a=e.subcase()
        with self.subTest(mode='FIRST'):b=e.subcase()
        with self.subTest(mode='SECOND'):c1=e.subcase()
        self.check(len({a,b,c1})==3,'observed subtest objects distinct')
    def test_CT14(self):
        e,_,_=self.engine();self.check(not e.tables['retained_oracles'] and not e.calls,'source inventory creates no runtime nodes')
    def test_CT15(self):
        self.err('COMMAND_HEADER_INVALID',p.drive_request,dict(drive(),extra='unknown'))
        with owned() as (base,root,owner):
            r=self.recorder(owner);r.profile=copy.deepcopy(r.profile)
            class SyntheticLate:
                def spawn(self,req,fault=None):return req
            fn=SyntheticLate.spawn;module=types.ModuleType('ct_late');module.SyntheticLate=SyntheticLate;spec=('ct_late','SyntheticLate','spawn','Drive.spawn');r.causal_deferred.append(spec)
            r.profile['source_anchors'].append(dict(owner='SyntheticLate',method='spawn',path='testing/prospective_capture_causal/test_causal_capture.py',sha256=c.sha(Path(__file__).read_bytes()),line=fn.__code__.co_firstlineno))
            try:
                self.err('UNSUPPORTED_CAUSAL_API',r.bind_deferred,lambda name:None);self.assertEqual(r.causal_deferred,[spec]);r.bind_deferred(lambda name:module);self.assertEqual(r.causal_deferred,[]);self.assertIsNot(SyntheticLate.spawn,fn)
            finally:r.restore();r.events.close()
            self.assertIs(SyntheticLate.spawn,fn)
    def test_CT16(self):e,_,_=self.engine();self.assertEqual(len(e.tables['retained_oracles']),0);self.check(self.design['retained_oracles']['historical_rows_T']==254,'historical count does not fill current table')
    def test_CT17(self):
        e,key,ref=self.retained();self.assertEqual(e.tables['retained_oracles'][ref]['value'],row());self.assertEqual(e.tables['retained_oracles'][ref]['value_digest'],c.digest_value(row(),p.LIMITS))
    def test_CT18(self):
        e,key,ref=self.retained('R');s=self.side(e);s['frames'][0]['record_links'][0]['raw_pointer']='/observations/0';p.validate_causal(s,self.reg);self.assertEqual(s['frames'][0]['record_links'][0]['raw_pointer'],'/observations/0')
    def test_CT19(self):
        for v in [dict(row(),seq=True),dict(row(),tasks=1024),dict(row(),secret='x')]:self.err('ORACLE_VALUE_MISSING',p.oracle_value,v,'T',self.spec)
    def test_CT20(self):
        with owned() as (base,root,owner):
            r=self.recorder(owner);calls=[];result=returned();m=types.ModuleType('ct_harness');m.ORACLES=[];m.CURRENT_CASE='SYNTHETIC_CASE'
            def independent(path):calls.append(path);m.ORACLES.append(row());return result
            m.independent=independent;r.causal.declaration(m,dict(run_id=RID,store_id=SID,role='CLIENT'));r.wrap_boundary(m,'independent','T.independent')
            try:self.assertIs(m.independent('not-read'),result);self.assertEqual(calls,['not-read']);self.assertEqual(r.errors,[])
            finally:r.restore();r.events.close()
    def test_CT21(self):
        e,key,ref=self.retained();e.oracle_guards[0][0]['seq']=2;self.err('ORACLE_VALUE_MUTATED',e.check_retained)
    def test_CT22(self):
        e,_,_=self.engine();self.err('ORACLE_DOMAIN_IDENTITY_MISSING',e.domain,returned()['head'])
        e.declaration(object(),dict(run_id=RID,store_id=SID,role='CLIENT'));e.declaration(object(),dict(run_id=RID,store_id=SID,role='CLIENT'));self.err('ORACLE_DOMAIN_IDENTITY_MISSING',e.domain,returned()['head'])
    def test_CT23(self):
        e,key,ref=self.retained();s=self.side(e);p.validate_causal(s,self.reg);self.assertEqual(c.pointer(s,s['frames'][0]['record_links'][0]['sidecar_pointer']),row());self.assertIsNone(s['frames'][0]['record_links'][0]['raw_pointer'])
    def test_CT24(self):
        e,key,ref=self.retained();self.assertNotIn('state',e.tables['retained_oracles'][ref]);self.assertNotIn('chain',e.tables['retained_oracles'][ref]);self.assertEqual(e.calls[key]['authority'],'OBSERVED_PARENT_RETURN')
    def test_CT25(self):
        v=p.store_request(req());self.assertEqual(v['request_sha256'],c.sha(json.dumps({k:req()[k] for k in ('kind','args','expected')},sort_keys=True,ensure_ascii=False,separators=(',',':')).encode()));self.assertNotIn('PRIVATE_SYNTHETIC_PAYLOAD',json.dumps(v))
    def test_CT26(self):
        e,events,_=self.engine();o=object();a=e.open_call('Client.perform',o,'perform',{});b=e.open_call('Store.transact',o,'transact',p.store_request(req()));e.close_call(b,receipt());e.close_call(a,{});self.assertEqual(e.calls[b]['parent_call_ref'],a);self.assertEqual(len(events),2)
    def test_CT27(self):
        for historical in [False,True]:v=p.store_receipt(dict(receipt(),historical=historical),self.spec);self.assertIs(v['historical'],historical);self.assertEqual(v['seq'],1)
    def test_CT28(self):
        with owned() as (base,root,owner):
            r=self.recorder(owner);E=type('ExactError',(ValueError,),{});r.causal_exception_types={'SYNTHETIC_EXACT_ERROR':E};ex=E('KNOWN_CODE');self.assertEqual(r.exception(ex)['code'],'KNOWN_CODE');self.assertEqual(r.exception(OSError('PRIVATE'))['code'],'OS_ERROR');self.err('COMMAND_HEADER_INVALID',r.exception,ValueError('UNKNOWN'));r.events.close()
    def test_CT29(self):
        with owned() as (base,root,owner):
            r=self.recorder(owner);E=type('SyntheticNegative',(ValueError,),{});ex=E('INVALID_COMMAND');r.causal_exception_types={'SYNTHETIC_EXACT_ERROR':E};r.profile=copy.deepcopy(r.profile);r.profile['negative_input_selectors']['SYNTHETIC_CASE']=dict(methods=['Store.transact'],input_failures=['COMMAND_HEADER_INVALID'],exception_codes=['INVALID_COMMAND'])
            class Store:
                def transact(self,cid,kind,args,expected=None):raise ex
            r.wrap_boundary(Store,'transact','Store.transact')
            try:
                with self.assertRaises(E) as got:Store().transact(**dict(req(),cid='INVALID'))
                self.assertIs(got.exception,ex);self.assertEqual(r.errors,[]);call=next(iter(r.causal.calls.values()));self.assertEqual(call['request']['status'],'INVALID_INPUT_EXPECTED_NEGATIVE');self.assertIsNone(call['request']['request_sha256'])
            finally:r.restore();r.events.close()
    def test_CT30(self):
        class Evil(dict):
            def items(self):raise AssertionError('CUSTOM_ITERATION')
        self.err('CAUSAL_FIELD_BUDGET',p.bounded_builtin,Evil());v=req();h=p.store_request(v);v['args']['changed']=True;self.assertNotEqual(h['request_sha256'],p.store_request(v)['request_sha256'])
    def test_CT31(self):v=p.store_request(req());self.assertNotEqual(v['args_digest']['sha256'],v['request_sha256']);self.assertEqual(p.store_receipt(receipt(),self.spec)['request_sha256'],v['request_sha256'])
    def test_CT32(self):v=p.store_receipt(receipt(),self.spec);self.assertEqual(v['result_metadata'],{'manifest_id':HEX});self.assertNotIn('PRIVATE_SYNTHETIC_PAYLOAD',json.dumps(v))
    def test_CT33(self):v=p.drive_request(drive());self.assertEqual(v['expected_version'],0);self.assertNotIn('page',v);self.assertEqual(v['hash_namespace'],'DRIVE_REQUEST')
    def test_CT34(self):
        b=json.dumps(drive(),indent=2).encode();v=p.drive_request(b);self.assertEqual(v['input_bytes_sha256'],c.sha(b));self.assertEqual(v['request_sha256'],p.drive_request(drive())['request_sha256']);self.assertNotEqual(v['input_bytes_sha256'],v['request_sha256'])
    def test_CT35(self):v=p.drive_receipt(dr_receipt(),self.spec);self.assertEqual(v['commit_sha256'],HEX);self.assertNotIn('seq',v);self.assertNotIn('after_data_sha256',v)
    def test_CT36(self):self.assertEqual(self.reg['snapshot_scopes'],p.late.read_registry()['snapshot_scopes']);e,_,_=self.engine();self.check(not e.tables['protocol_instances'],'no historical observations inserted')
    def test_CT37(self):
        e,_,_=self.engine();ctx=__import__('multiprocessing').get_context('spawn');a,b=ctx.Pipe();proc=ctx.Process();e.register(proc,a,dict(run_id=RID),'snapshot',{},None)
        try:e.message(a,dict(schema='d5.fixture-drive-snapshot.v1',run_id=RID,version=0,head_sha256=HEX));self.assertEqual(next(iter(e.tables['protocol_instances'].values()))['observed_messages'][0]['authority'],'CHILD_PROTOCOL_RETURN')
        finally:a.close();b.close()
    def test_CT38(self):
        self.err('CAUSAL_FIELD_BUDGET',p.drive_request,b'x'*33,{'operand_bytes':32});self.err('COMMAND_HEADER_INVALID',p.drive_request,dict(drive(),schema='UNKNOWN'))
    def test_CT39(self):
        e,_,_=self.engine();o=object();e.declaration(o,dict(run_id=RID,store_id=SID,role='CLIENT'));self.err('ORACLE_DOMAIN_IDENTITY_MISSING',e.declaration,o,dict(run_id=CID,store_id=SID,role='CLIENT'));self.assertEqual(next(iter(e.domains.values()))['run_id'],RID)
    def test_CT40(self):self.check('OWN_FIXTURE_SNAPSHOT' in self.reg['causal_graph']['authorities'] and 'RETAINED_HARNESS_ORACLE' in self.reg['causal_graph']['authorities'],'authority domains explicit');self.assertNotEqual(t:=p.t.DRIVE_OBS,'RETAINED_HARNESS_ORACLE')
    def test_CT41(self):e,_,_=self.engine();self.assertEqual(e.tables['subcases'][e.subcase()]['kind'],'ROOT_FRAME');self.assertEqual(e.subcase(),e.subcase())
    def test_CT42(self):
        e,_,_=self.engine()
        with self.subTest(mode='SAFE'):key=e.subcase();self.assertEqual(e.tables['subcases'][key]['params'],{'mode':'SAFE'})
    def test_CT43(self):
        e,_,_=self.engine();fake=unittest.case._SubTest(self,None,unittest.case._OrderedChainMap(dict(secret='PRIVATE')));self.err('UNSUPPORTED_SUBCASE_BINDING',e.subcase,fake)
        self.assertNotIn('PRIVATE',json.dumps(e.tables))
    def test_CT44(self):
        e,_,_=self.engine()
        with self.subTest(mode='OUTER',phase='P1'):
            with self.subTest(mode='INNER'):key=e.subcase();self.assertEqual(e.tables['subcases'][key]['params'],dict(mode='INNER',phase='P1'))
    def test_CT45(self):
        e,_,_=self.engine()
        with self.subTest(mode='CALLBACK'):
            sub=self.__dict__['_subtest'];self.assertEqual(e.subcase(),e.subcase(sub));self.assertIs(e.subobjects[-1][0],sub)
    def test_CT46(self):
        e,_,_=self.engine();got=[];th=threading.Thread(target=lambda:got.append(e.subcase()));th.start();th.join();self.assertEqual(e.tables['subcases'][got[0]]['kind'],'THREAD_FRAME_SCOPE_ONLY');self.assertNotEqual(got[0],e.subcase())
    def test_CT47(self):e,_,_=self.engine();a=object();b=object();self.assertEqual(e.object_ref(a),e.object_ref(a));self.assertNotEqual(e.object_ref(a),e.object_ref(b));self.assertIs(e.objects[0][0],a)
    def test_CT48(self):
        e,_,_=self.engine();a=object();b=object();self.assertNotEqual(e.declaration(a,dict(run_id=RID,store_id=SID,role='CLIENT')),e.declaration(b,dict(run_id=RID,store_id=CID,role='CLIENT')));self.assertEqual(len(e.domains),2)
    def protocol(self):
        e,events,errors=self.engine();ctx=__import__('multiprocessing').get_context('spawn');a,b=ctx.Pipe();proc=ctx.Process();key=e.register(proc,a,dict(run_id=RID),'snapshot',{},'after_head');return e,a,b,proc,key
    def test_CT49(self):
        e,a,b,proc,key=self.protocol()
        try:self.assertIs(e.protocol_for(proc,'process_ref')[1],e.tables['protocol_instances'][key]);self.assertNotIn('root',json.dumps(e.tables))
        finally:a.close();b.close()
    def test_CT50(self):
        e,a,b,proc,key=self.protocol()
        try:e.message(a,('READY','before_replace'));v=e.tables['protocol_instances'][key];self.assertEqual(v['expected_point'],'after_head');self.assertEqual(v['observed_messages'][0]['point'],'before_replace')
        finally:a.close();b.close()
    def test_CT51(self):e,_,_=self.engine();self.assertFalse(e.message(object(),{'secret':'UNREGISTERED'}));self.assertEqual(e.tables['protocol_instances'],{})
    def test_CT52(self):
        e,a,b,proc,key=self.protocol()
        try:e.message(a,('ERROR','KNOWN_ERROR'));e.message(a,('OK',receipt()));self.assertEqual(e.tables['protocol_instances'][key]['observed_messages'][1]['command_identity'],'OBSERVED_PROTOCOL_RECEIPT')
        finally:a.close();b.close()
    def test_CT53(self):
        with owned() as (base,root,owner):
            e,_,_=self.engine();ctx=__import__('multiprocessing').get_context('spawn');a,b=ctx.Pipe();proc=ctx.Process(target=synthetic_child_reply,args=(b,));proc.start();b.close();key=e.register(proc,a,dict(run_id=RID),'snapshot',{},'after_head')
            try:
                e.message(a,a.recv());e.message(a,a.recv());proc.join(10);e.exit(proc,direct=True)
                self.assertEqual(e.tables['protocol_instances'][key]['exit_observations'],[dict(status='OBSERVED_PARENT_RETURN',returncode=0)]);self.assertEqual(len(e.tables['protocol_instances'][key]['observed_messages']),2)
            finally:
                a.close()
                if proc.is_alive():proc.terminate();proc.join(5)
                CHILDREN.append(dict(role='OWN_SYNTHETIC_PROTOCOL_PRODUCER',exitcode=proc.exitcode));self.assertEqual(proc.exitcode,0)
    def test_CT54(self):
        e,a,b,proc,key=self.protocol()
        try:e.exit(proc,None);self.assertEqual(e.tables['protocol_instances'][key]['exit_observations'][0]['status'],'PENDING_PROCESS_EXIT')
        finally:a.close();b.close()
    def test_CT55(self):
        e,a,b,proc,key=self.protocol()
        try:e.message(a,('OK',{}));msg=e.tables['protocol_instances'][key]['observed_messages'][0];self.assertEqual(msg['command_identity'],'CHILD_LOCAL_NOT_OBSERVED');self.assertNotIn('command_id',msg);self.assertNotEqual(key,CID)
        finally:a.close();b.close()
    def test_CT56(self):
        e,a,b,proc,key=self.protocol()
        try:self.err('UNSUPPORTED_PROTOCOL_MESSAGE',e.message,a,('UNRECOGNIZED_ACK',{}));self.assertEqual(e.tables['protocol_instances'][key]['observed_messages'],[])
        finally:a.close();b.close()
    def test_CT57(self):
        e,_,_=self.engine();o=object();e.declaration(o,dict(run_id=RID,store_id=SID,role='CLIENT'));e.frame=dict(test_frame_id='OTHER_FRAME',test_id='OTHER');self.err('ORACLE_DOMAIN_IDENTITY_MISSING',e.domain,returned()['head'])
    def test_CT58(self):
        with owned() as (base,root,owner):
            r=self.recorder(owner)
            class Store:
                def transact(self,cid,kind,args,expected=None):return receipt()
            store=Store();oref=r.owner(store,None);r.declarations[oref]=dict(run_id=RID,store_id=SID,role='CLIENT');r.causal.declaration(store,dict(run_id=RID,store_id=SID,role='CLIENT'))
            m=types.ModuleType('ct_synthetic');m.ORACLES=[];m.CURRENT_CASE='SYNTHETIC_CASE'
            def independent(path):m.ORACLES.append(row());return returned()
            m.independent=independent;r.wrap_boundary(Store,'transact','Store.transact');r.wrap_boundary(m,'independent','T.independent')
            try:
                store.transact(**req());m.independent('NO_IO');self.assertEqual(r.errors,[]);links=list(r.causal.tables['causal_links'].values());self.assertEqual(sum(l['relation']=='COMMAND_RECEIPT_ORACLE_COMMIT' for l in links),1);self.assertNotEqual(receipt()['after_data_sha256'],row()['state_sha256'])
            finally:r.restore();r.events.close()
    def test_CT59(self):self.assertNotEqual(receipt()['after_data_sha256'],row()['state_sha256']);self.assertIn('RECEIPT_INSERTION',self.reg['causal_graph']['post_state_hash_warning'])
    def test_CT60(self):
        e,_,_=self.engine();e.declaration(object(),dict(run_id=RID,store_id=SID,role='CLIENT'));bad=returned();bad['head']['commit_sha256']='b'*64;self.err('ORACLE_VALUE_MISSING',e.retain,'ct_synthetic',0,row(),'T',bad,'C1')
    def test_CT61(self):self.check(self.reg['observer_scope']['checkpoint_or_hook_observers'] is False and self.reg['observer_scope']['child_observers_installed'] is False,'no native fsync or child instrumentation claim')
    def test_CT62(self):
        e,_,_=self.engine();o=object();a=e.open_call('Store.transact',o,'transact',p.store_request(req()));e.close_call(a,{});b=e.open_call('Store.transact',o,'transact',p.store_request(req()));e.close_call(b,{});self.assertNotEqual(a,b);self.assertEqual(e.calls[a]['request'],e.calls[b]['request'])
    def test_CT63(self):
        e,key,ref=self.retained();s=self.side(e);self.assertEqual(p.validate_causal(s,self.reg)['status'],'CAUSAL_TABLES_VERIFIED');self.assertEqual(e.calls[key]['input_ref']['test_id'],'SYNTHETIC_CASE')
    def test_CT64(self):
        e,key,ref=self.retained();s=self.side(e);s['retained_oracles'][ref]['subcase_ref']='ORPHAN';self.err('CAUSAL_LINK_MISSING',p.validate_causal,s,self.reg)
    def test_CT65(self):
        with owned() as (base,root,owner):
            r=self.recorder(owner);out=receipt();calls=[]
            class Store:
                def transact(self,cid,kind,args,expected=None):calls.append(cid);return out
            orig=Store.transact;r.wrap_boundary(Store,'transact','Store.transact')
            try:self.assertIs(Store().transact(**req()),out);self.assertEqual(calls,[CID]);self.assertEqual(r.errors,[])
            finally:r.restore();r.events.close()
            self.assertIs(Store.transact,orig)
    def test_CT66(self):
        with owned() as (base,root,owner):
            r=self.recorder(owner);E=type('Exact',(ValueError,),{});ex=E('KNOWN');r.causal_exception_types={'SYNTHETIC':E}
            class Store:
                def transact(self,cid,kind,args,expected=None):raise ex
            r.wrap_boundary(Store,'transact','Store.transact')
            try:
                with self.assertRaises(E) as got:Store().transact(**req())
                self.assertIs(got.exception,ex);self.assertEqual(r.errors,[])
            finally:r.restore();r.events.close()
    def test_CT67(self):
        tree=ast.parse((ROOT/'testing/prospective_capture_causal/capture.py').read_text());wrapped=[n.args[1].value for n in ast.walk(tree) if isinstance(n,ast.Call) and isinstance(n.func,ast.Attribute) and n.func.attr=='patch' and len(n.args)>1 and isinstance(n.args[1],ast.Constant)];self.check(not set(wrapped)&{'checkpoint','_checkpoint','snapshot','reopen','lookup'},'no new auxiliary measurement API wrapper')
    def test_CT68(self):
        e,events,_=self.engine();o=object();a=e.open_call('facade',o,'perform',{});b=e.open_call('store',o,'transact',{});e.close_call(b,{});e.close_call(a,{});self.assertEqual(e.calls[b]['parent_call_ref'],a);self.check(all(v['event']=='CAUSAL_TERMINAL' for v in events),'terminal only')
    def test_CT69(self):
        with owned() as (base,root,owner):
            r=self.recorder(owner);calls=[]
            class Store:
                def transact(self,cid,kind,args,expected=None):calls.append('ORIGINAL');return {'unsupported':True}
            r.wrap_boundary(Store,'transact','Store.transact')
            try:self.assertEqual(Store().transact(**req()),{'unsupported':True});self.assertEqual(calls,['ORIGINAL']);self.assertIn('COMMAND_HEADER_INVALID',r.errors)
            finally:r.restore();r.events.close()
    def test_CT70(self):
        with owned() as (base,root,owner):
            r=self.recorder(owner)
            class Store:
                def transact(self,cid,kind,args,expected=None):return receipt()
            orig=Store.transact;r.wrap_boundary(Store,'transact','Store.transact');Store.transact=lambda:None;r.restore();r.events.close();self.assertIs(Store.transact,orig);self.assertIn('OBSERVER_IDENTITY_CHANGED',r.errors)
    def test_CT71(self):
        e,_,_=self.engine();fake=types.SimpleNamespace(params={});self.err('UNSUPPORTED_SUBCASE_BINDING',e.subcase,fake)
    def test_CT72(self):
        for n,h in self.design['future_runtime_dependency_scope']['pinned_existing_names'].items():self.assertEqual(HISTORICAL_INPUTS[n] if n in HISTORICAL_INPUTS else c.sha((ROOT/n).read_bytes()),h)
        self.observations.append(dict(runtime_pins_preserved=len(self.design['future_runtime_dependency_scope']['pinned_existing_names'])))
    def test_CT73(self):e,_,_=self.engine();self.err('CAUSAL_FIELD_BUDGET',e.row_budget,dict(value='x'*4096))
    def test_CT74(self):
        with owned() as (base,root,owner):
            r=self.recorder(owner)
            for i in range(2048):r.emit('SYNTHETIC_TEST')
            r.emit('SYNTHETIC_TEST');self.assertEqual(r.active['event_count'],2048);self.assertIn('EVENT_TEST_BUDGET',r.errors)
            r.active=None
            for i in range(131072-2048):r.emit('SYNTHETIC_CAMPAIGN')
            r.emit('SYNTHETIC_CAMPAIGN');self.assertEqual(len(r.events),131072);self.assertIn('EVENT_CAMPAIGN_BUDGET',r.errors);r.events.close();self.assertLessEqual(r.events.peak_buffer_bytes,p.LIMITS['page_bytes'])
            self.observations.append(dict(test_events=2048,campaign_events=131072,next_events='REJECTED'))
    def test_CT75(self):
        self.assertEqual(p.package_size({'OWNER':4096,'sidecar.json':p.LIMITS['index_sidecar_bytes']}),4096+p.LIMITS['index_sidecar_bytes']);self.err('PACKAGE_FILE_BUDGET',p.package_size,{'sidecar.json':p.LIMITS['index_sidecar_bytes']+1});self.assertEqual(p.LIMITS['pages'],32);sizes={f'event-{i:04}.json':p.LIMITS['page_bytes'] for i in range(1,33)};sizes.update({'OWNER':4096,'runner-raw.json':p.LIMITS['raw_bytes'],'sidecar.json':p.LIMITS['index_sidecar_bytes'],'context.json':p.LIMITS['context_bytes'],'launch.json':p.LIMITS['launch_bytes']});self.assertEqual(len(sizes),37);self.assertEqual(p.package_size(sizes),p.LIMITS['package_bytes'])
    def test_CT76(self):e,_,_=self.engine({'refs':2});self.err('REFERENCE_BUDGET',e.object_ref,object());self.assertEqual(len(e.tables['subcases']),1)
    def test_CT77(self):
        self.err('CAUSAL_FIELD_BUDGET',p.bounded_builtin,'x'*100,{'operand_bytes':16});v=[]
        for i in range(34):v=[v]
        self.err('CAUSAL_FIELD_BUDGET',p.bounded_builtin,v)
    def test_CT78(self):
        with owned() as (base,root,owner):
            (root/'input').write_bytes(b'12345678');r=c.Reader(base,{'read_bytes':12});r.read('packet/input');self.err('READ_BUDGET',r.read,'packet/input')
    def test_CT79(self):self.assertEqual(self.design['component_external_seconds'],300);self.assertEqual(p.LIMITS['campaign_seconds'],900);self.assertEqual(p.LIMITS['wait_seconds'],20)
    def test_CT80(self):
        with owned() as (base,root,owner):
            r=self.recorder(owner)
            for i in range(1377):r.emit('SYNTHETIC_PRIOR')
            for i in range(318):r.emit('CAUSAL_TERMINAL',causal={'synthetic':i})
            self.assertEqual(r.active['event_count'],1695);self.assertEqual(r.errors,[]);r.events.close()
    def test_CT81(self):
        e,key,ref=self.retained();s=self.side(e);self.assertEqual(p.validate_causal(s,self.reg)['rows'],2)
        broken=copy.deepcopy(s);broken['retained_oracles'][ref]['schema']='UNKNOWN';self.err('CAUSAL_SCHEMA_INVALID',p.validate_causal,broken,self.reg)
        s['retained_oracles'][ref]['value']['extra']='secret';self.err('ORACLE_VALUE_MISSING',p.validate_causal,s,self.reg)
    def test_CT82(self):
        ledger=p.Ledger(RID,pid=123);ledger.at('TARGETS');ledger.fail('CAUSAL_LINK_MISSING');ledger.at('FINALIZE');ledger.fail('STALE_INPUTS');diag=ledger.value();self.assertEqual(diag['phase'],'TARGETS');self.assertEqual(diag['code'],'SANITIZED_WORKER_ERROR');body=p.encode(dict(schema=p.FAILURE_SCHEMA,worker_diagnostic=diag));self.assertEqual(p.read_sidecar(body,RID,123)[1],diag)
    def test_CT83(self):
        with owned() as (base,root,owner):
            fd=owner.create('partial');writer=p.SideWriter(fd,RID,pid=123);ledger=p.Ledger(RID,pid=123);ledger.fail('STALE_INPUTS')
            def partial(fd,data):os.write(fd,data[:12]);raise OSError('synthetic')
            try:
                with patch.object(p,'write_all',side_effect=partial):
                    with self.assertRaises(OSError):writer.failure(ledger)
                self.assertFalse(writer.failure(ledger));self.assertEqual((root/'partial').stat().st_size,12)
            finally:os.close(fd)
    def test_CT84(self):e,key,ref=self.retained();s=self.side(e);s['frames'][0]['record_links'][0]['digest']=c.digest_value({},p.LIMITS);self.err('ORACLE_VALUE_MISSING',p.validate_causal,s,self.reg)
    def test_CT85(self):
        e,key,ref=self.retained();s=self.side(e);s['retained_oracles'][ref]['test_frame_id']='OTHER_FRAME';self.err('CAUSAL_LINK_MISSING',p.validate_causal,s,self.reg)
    def test_CT86(self):self.err('COMMAND_HEADER_INVALID',p.store_receipt,dict(receipt(),historical='N/A'),self.spec);self.err('ORACLE_VALUE_MISSING',p.oracle_value,dict(row(),role='NOT_APPLICABLE'),'T',self.spec)
    def test_CT87(self):self.assertEqual(set(self.reg['causal_graph']['authorities']),{'SOURCE_EXPECTATION','OBSERVED_PARENT_CALL','OBSERVED_PARENT_RETURN','CHILD_PROTOCOL_RETURN','RETAINED_HARNESS_ORACLE','OWN_FIXTURE_SNAPSHOT','ORIGINAL_ASSERTION_OUTCOME'});self.check(self.spec['receipt_store']['full_receipt_retained'] is False,'projection not full receipt')
    def test_CT88(self):self.check(self.reg['functional_execution_authorized'] is False and not p.plan()['closure'],'component cannot close criterion')
    def test_CT89(self):
        self.integration('success');self.integration('failure');self.integration('untrusted')
        self.check(not forbidden(),'no forbidden imports in component process')
    def test_CT90(self):self.check(all(not (ROOT/n).exists() for n in (p.AUTHORITY,p.DESTINATION,p.LAUNCH_COPY)),'I84 paths absent')
    def test_CT91(self):self.assertEqual(len(self.reg['entry']['expected_test_ids']),321);self.assertEqual(p.DESTINATION,'docs/validation/D5-I84-P01');self.assertNotEqual(p.DESTINATION,p.late.DESTINATION)
    def test_CT92(self):self.assertEqual(self.reg['semantic_baseline'],dict(SUPPORTS_BOUNDED=83,PARTIAL=1));self.assertEqual(self.design['remaining_partial_parts'],['UI04.1'])
    def test_CT93(self):
        for n,h in self.design['inputs'].items():self.assertEqual(HISTORICAL_INPUTS[n] if n in HISTORICAL_INPUTS else c.sha((ROOT/n).read_bytes()),h)
        self.observations.append(dict(historical_inputs_preserved=len(self.design['inputs'])))
    def test_CT94(self):self.check(not self.design['real_provider_access'] and not self.design['credentials_used'] and not self.design['D6_started'] and not self.design['deployment'],'P0 invariant')
    def test_CT95(self):self.check(not self.design['publication_authorized'] and not self.design['remote_network_read_performed'],'no remote authority implicit')
    def test_CT96(self):
        e,a,b,proc,key=self.protocol()
        try:self.err('UNSUPPORTED_PROTOCOL_MESSAGE',e.message,a,('UNKNOWN',{}));self.assertEqual(e.tables['protocol_instances'][key]['observed_messages'],[])
        finally:a.close();b.close()
        self.check(not (ROOT/p.AUTHORITY).exists(),'new incompatibility creates no authorization')

    def integration(self,mode):
        with owned() as (base,root,owner):
            (root/'runner.py').write_text('SYNTHETIC_ONLY\n');before={'packet/runner.py':c.sha((root/'runner.py').read_bytes())};tid='ct_synthetic.Example.test_one'
            entry=dict(id='P01',expected_tests=1,expected_test_ids=[tid],expected_groups={'ct_synthetic':1},group_policies={'ct_synthetic':dict(target='SYNTHETIC_COMPONENT_ONLY',domain_required=False,no_store_reason='SYNTHETIC_COMPONENT_ONLY')},record_sources=[],method_bindings={tid:dict(status='SOURCE_DERIVED_EXPECTATION',scope='SYNTHETIC_ONLY')},expected_raw_scenarios=0,expected_scenario_multiplicity={},runner_module='ct_synthetic_runner',runner_path='packet/runner.py',runner_explicit_input_paths=['packet/runner.py'],runner_discovery_patterns=[],runner_effective_inputs=before)
            reg=dict(entry=entry,policies=[],class_allowlist=[dict(id='builtins.dict',source=None)],snapshot_scopes=[],negative_DI28={},operand_scopes=[],projection_schemas=self.spec,inventory=[])
            approved=dict(capture_inputs=before);children=[];real_popen=subprocess.Popen
            script='''import sys,json,types,unittest
from pathlib import Path
from testing.prospective_capture_causal import capture as p,worker as w
args=sys.argv[1:7];reg=json.loads(sys.argv[7]);approved=json.loads(sys.argv[8]);root=Path(sys.argv[9]);mode=sys.argv[10]
p.read_registry=lambda *a:reg
p.authority=lambda *a:approved
if mode=='untrusted':
 def reject(*a):raise p.c.CaptureFault('I84_AUTHORIZATION_REQUIRED')
 p.authority=reject
module=types.ModuleType('ct_synthetic_runner');module.__file__=str(root/'packet/runner.py')
class Example(unittest.TestCase):
 def test_one(self):
  with self.subTest(mode='SYNTHETIC'):self.assertEqual(1,1)
Example.__module__='ct_synthetic'
def main():
 result=unittest.TestResult();unittest.defaultTestLoader.loadTestsFromTestCase(Example).run(result)
 print(json.dumps(dict(status='PASS',tests_run=1,passed=reg['entry']['expected_test_ids'],failures=[],errors=[],skipped=[],scenarios=[],case_test_map={})));return 0
module.main=main
w.importlib=types.SimpleNamespace(import_module=lambda name:module)
def targets(*args):
 if mode=='failure':raise p.c.CaptureFault('UNSUPPORTED_CAUSAL_API')
 return [],None,None
w.targets=targets
# Injection into the NEW recorder only; no historical sources/globals changed.
p.Recorder.install_causal=lambda self:None
sys.exit(w.main(args,root))
'''
            def producer(cmd,**kwargs):
                kwargs['cwd']=ROOT;child=real_popen([sys.executable,'-B','-c',script,*cmd[-6:],json.dumps(reg),json.dumps(approved),str(base),mode],**kwargs);children.append(child);return child
            (base/'docs/validation').mkdir(parents=True)
            with patch.object(p,'read_registry',return_value=reg),patch.object(p,'authority',return_value=approved),patch.object(c.subprocess,'Popen',side_effect=producer):
                context=p.launch('P01',base);self.assertRaises(FileExistsError,p.launch,'P01',base)
            for child in children:CHILDREN.append(dict(exitcode=child.returncode,role='SYNTHETIC_CAUSAL_WORKER_'+mode.upper()))
            self.assertEqual(context['cleanup']['status'],'OWN_GROUP_GONE');self.assertEqual(json.loads((base/p.LAUNCH_COPY).read_text()),context)
            if mode=='success':self.assertEqual(context['capture_status'],'TRACE_CAPTURED_PENDING_SUFFICIENCY_REVIEW',context);self.assertEqual(context['worker_diagnostic']['status'],'COMPLETED');self.assertEqual(context['page_validation']['status'],'PAGE_BINDINGS_VERIFIED')
            elif mode=='failure':self.assertEqual(context['capture_status'],'BLOCKED_WORKER_FAILURE',context);self.assertEqual(context['worker_diagnostic']['phase'],'TARGETS');self.assertEqual(context['worker_diagnostic']['code'],'SANITIZED_WORKER_ERROR');self.assertEqual((base/p.DESTINATION/'runner-raw.json').stat().st_size,0)
            else:self.assertEqual(context['worker_diagnostic_status'],'WORKER_DIAGNOSTIC_NOT_RECORDED');self.assertEqual((base/p.DESTINATION/'sidecar.json').stat().st_size,0)
            self.observations.append(dict(producer='SYNTHETIC_ONLY',mode=mode,capture_status=context['capture_status'],cleanup=context['cleanup']))
