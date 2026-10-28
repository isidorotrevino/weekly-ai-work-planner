# SPDX-License-Identifier: GPL-3.0-only
"""PR96: synthetic objects and owned spawn processes; no historical suites."""
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
from testing.prospective_capture_parental import capture as p, worker as w
c=p.c;ROOT=p.ROOT;ROOTS=[];CHILDREN=[];HISTORICAL_INPUTS={}
RID='11111111-1111-4111-8111-111111111111';CID='33333333-3333-4333-8333-333333333333';OTHER='44444444-4444-4444-8444-444444444444';HEX='a'*64

class SyntheticLab:pass
class SyntheticCase(unittest.TestCase):
    def runTest(self):pass

def synthetic_snapshot(root,run_id,scope,connection):
    # root/scope are deliberately ignored by this new synthetic producer.
    connection.send(snapshot(run_id));connection.close()

def snapshot(run_id=RID):
    return dict(schema='d5.fixture-drive-snapshot.v1',run_id=run_id,version=1,head_sha256=HEX,state={'synthetic':True},committed_pages=1,occurrences=0,logical_observations=0,terminal_diagnostics=0,reference_selected=False,persistent_D2_writes=0,remote_requests=0)

def receipt():
    return dict(schema='d5.durable-receipt.v1',command_id=CID,request_sha256=HEX,before_seq=0,seq=1,before_state_sha256='b'*64,after_data_sha256='c'*64,historical=False,grants_execution_authority=False,quota_consumed=0,reservations_created=0,activation_allowed=False,result={'manifest_id':HEX,'text':'PRIVATE_SYNTHETIC'})

def drive_receipt():return dict(schema='d5.fixture-drive-receipt.v1',command_id=CID,request_sha256=HEX,version=1,result='SYNTHETIC_CAPTURE_CONFIRMED',reference_selected=False,persistent_D2_writes=0,remote_requests=0,commit_sha256=HEX)

def forbidden():
    prefixes=('source_ingest','testing.D5','testing.durable_','testing.evidence_')
    return sorted(n for n in sys.modules if n.startswith(prefixes) or n.endswith(('.test_causal_capture','.run_causal_lab','.test_late_capture','.run_late_lab','.test_typed_capture','.run_typed_lab','.test_paged_capture','.run_paged_lab','.test_prospective_capture','.run_capture_lab')))

@contextlib.contextmanager
def owned():
    row=dict(ownership_verified=False,removed=False,sibling_preserved=False);ROOTS.append(row)
    with tempfile.TemporaryDirectory(prefix='i85-own-') as tmp:
        base=Path(tmp);root=base/'packet';root.mkdir();owner=c.OwnedRoot(root);sibling=base/'sibling';sibling.write_bytes(b'I85_SYNTHETIC')
        try:yield base,root,owner
        finally:owner.verify();row.update(ownership_verified=True,sibling_preserved=sibling.read_bytes()==b'I85_SYNTHETIC')
    row['removed']=not base.exists()

@contextlib.contextmanager
def pair():
    ctx=p.multiprocessing.context.SpawnContext();a,b=ctx.Pipe()
    try:yield ctx,a,b
    finally:a.close();b.close()

class ParentalTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.reg=p.read_registry();cls.contract=cls.reg['parental_contract'];cls.spec=cls.reg['projection_schemas'];cls.design=json.loads((ROOT/p.CONTRACT).read_text())
    def setUp(self):self.observations=[]
    def check(self,value,label):self.assertTrue(value);self.observations.append(dict(check=label,status='PASS'))
    def err(self,code,fn,*args,**kwargs):
        with self.assertRaises(c.CaptureFault) as raised:fn(*args,**kwargs)
        self.assertEqual(raised.exception.code,code);self.observations.append(dict(expected=code,observed=raised.exception.code))
    def engine(self,limits=None):
        lim=dict(p.LIMITS,**(limits or {}));count=[0];errors=[];events=[]
        def charge(n=1):count[0]+=n;p.fault(count[0]<=lim['refs'],'REFERENCE_BUDGET')
        test=SyntheticCase();test.lab=SyntheticLab();test.lab.run_id=RID
        e=p.ParentalState(RID,lim,self.spec,charge,lambda k,**v:events.append(dict(event=k,**v)),errors.append,contract=self.contract)
        e.begin(dict(test_frame_id='F1',test_id=self.contract['direct_selector']['test_id']),test);e.bind(SyntheticCase,SyntheticLab,synthetic_snapshot);e.charged=count;return e
    def prepared(self,ctx,a,b):
        e=self.engine();e.pipe_return(ctx,(a,b));proc=ctx.Process(target=synthetic_snapshot,args=(object(),RID,object(),b));return e,proc,e.preview(proc)
    def started(self,ctx,a,b):
        e,proc,pre=self.prepared(ctx,a,b);pop=p.multiprocessing.popen_spawn_posix.Popen.__new__(p.multiprocessing.popen_spawn_posix.Popen);pop.pid=12345;pop.returncode=None;proc._popen=pop;e.started(proc,pre,None);return e,proc,next(iter(e.tables['protocol_instances']))
    def side(self,e):
        return dict(schema=p.NORMAL_SCHEMA,capture_run_id=RID,frames=[dict(test_frame_id='F1',test_id=self.contract['direct_selector']['test_id'],record_links=[],owner_context_refs=[])],owner_contexts={ref:dict(scope='SYNTHETIC_OBJECT',identity=None) for _,ref in e.objects},shared_reference_count=e.charged[0],**e.tables)
    def header(self,policy,value):
        return p.child_header(value,next(x for x in self.contract['child_action_policies'] if x['id']==policy),self.contract,self.spec)
    def recorder(self,owner):
        entry=dict(id='SYNTHETIC_ONLY',expected_test_ids=['SYNTHETIC_CASE'],expected_groups={'synthetic':1},group_policies={'synthetic':dict(domain_required=False,no_store_reason='SYNTHETIC')},record_sources=[],method_bindings={})
        r=p.Recorder(entry,owner,profile=self.reg,bindings=p.LateBindings([dict(id='builtins.dict',source=None)],c.Reader(ROOT)))
        r.active=dict(test_id=self.contract['direct_selector']['test_id'],test_frame_id='F1',event_count=0,owner_context_refs=[]);r.frame_summary=dict(operands_missing=False,returns_missing=False);r.causal.begin(r.active,SyntheticCase());r.causal.test.lab=SyntheticLab();r.causal.test.lab.run_id=RID;r.causal.bind(SyntheticCase,SyntheticLab,synthetic_snapshot);return r
    def test_PR01(self):
        self.check(not self.design['implementation_authorized'] and not self.design['component_test_execution_authorized'],'I84 historical design flags preserved; I85 authorized separately')
        self.assertEqual(len(self.design['child_action_policies']),15)
    def test_PR02(self):
        for name in ('docs/validation/D5-I84-capture-authorization.json','docs/validation/D5-I84-P01','docs/validation/D5-I84-P01-launch.json'):self.assertFalse((ROOT/name).exists())
        self.assertEqual(json.loads((ROOT/'docs/validation/D5-I83-plan-raw.json').read_text())['status'],'NOT_RUN_I84_AUTHORIZATION_REQUIRED')
    def test_PR03(self):
        self.check(not self.reg['functional_execution_authorized'],'component approval does not grant functional authority')
        with owned() as (base,root,owner):self.err('I86_AUTHORIZATION_REQUIRED',p.authority,base,'P01',self.reg)
    def test_PR04(self):
        for scope in ('P02','P10'):
            with self.assertRaises(c.CaptureFault):p.scope(scope)
        with owned() as (base,root,owner):
            q=base/p.AUTHORITY;q.parent.mkdir(parents=True);q.write_text(json.dumps(dict(schema='d5.causal-capture-authority.v1',phase='I84_EXPLICITLY_APPROVED',scopes=['P01'],registry_sha256=HEX,capture_inputs={})))
            self.err('I86_AUTHORIZATION_REQUIRED',p.authority,base,'P01',self.reg)
    def test_PR05(self):self.assertEqual(p.plan(registry=self.reg)['status'],'NOT_RUN_I86_AUTHORIZATION_REQUIRED');self.assertFalse((ROOT/p.DESTINATION).exists())
    def test_PR06(self):
        with owned() as (base,root,owner):
            r=copy.deepcopy(self.reg);r['parental_contract']['child_action_policies'].pop()
            class Reader:
                def read(_,name):return p.encode(r) if name==p.REGISTRY else (ROOT/name).read_bytes()
            self.err('INVALID_REGISTRY',p.read_registry,ROOT,Reader())
    def test_PR07(self):self.check(not self.reg['functional_execution_authorized'] and not p.plan(registry=self.reg)['closure'],'hash coherence has no human authority')
    def test_PR08(self):self.assertFalse(p.plan(registry=self.reg)['publication_authorized'])
    def test_PR09(self):p.verify_parental_stdlib(self.contract);self.check(type(p.multiprocessing.context.SpawnContext()) is p.multiprocessing.context.SpawnContext,'exact spawn context')
    def test_PR10(self):
        pin=next(x for x in self.contract['stdlib_source_bindings'] if x['method']=='start');self.assertEqual(list(p.inspect.signature(p.multiprocessing.process.BaseProcess.start).parameters),pin['parameters'])
    def test_PR11(self):
        with owned() as (base,root,owner):
            r=self.recorder(owner);r.causal.bindings=None;self.err('PARENT_BINDING_CHANGED',r.bind_direct);self.assertNotIn('test_incremental_capture',sys.modules);r.events.close()
    def test_PR12(self):
        with pair() as (ctx,a,b):
            e,proc,pre=self.prepared(ctx,a,b);proc._target=lambda *args:None;self.err('PARENT_TARGET_NOT_PINNED',e.preview,proc)
    def test_PR13(self):
        e=self.engine();self.err('PARENT_BINDING_CHANGED',e.bind,SyntheticCase,SyntheticLab,lambda *args:None)
    def test_PR14(self):
        class Hostile:
            def __getattribute__(self,name):raise AssertionError('must not inspect')
        e=self.engine();e.frame['test_id']='OUTSIDE';self.assertIsNone(e.preview(Hostile()));self.assertIsNone(e.pipe_return(Hostile(),Hostile()))
    def test_PR15(self):
        with pair() as (ctx,a,b):
            e,proc,pre=self.prepared(ctx,a,b);e.test.lab=object();self.err('PARENT_BINDING_CHANGED',e.preview,proc)
    def test_PR16(self):
        changed=copy.deepcopy(self.contract);changed['stdlib_source_bindings'][0]['source_sha256']='0'*64;self.err('PARENT_BINDING_CHANGED',p.verify_parental_stdlib,changed)
    def test_PR17(self):
        with pair() as (ctx,a,b):
            e=self.engine();value=(a,b);e.pipe_return(ctx,value);self.assertIs(e.pairs[0][2],a);self.assertIs(e.pairs[0][3],b);self.assertEqual(next(iter(e.tables['parental_registrations'].values()))['status'],'PROVISIONAL')
    def test_PR18(self):
        e=self.engine();out=[]
        thread=threading.Thread(target=lambda:out.append(e.pipe_return(object(),object())));thread.start();thread.join();self.assertEqual(out,[None]);self.assertFalse(e.pairs)
    def test_PR19(self):
        with pair() as (ctx,a,b):self.err('PARENT_PAIR_AMBIGUOUS',self.engine().pipe_return,ctx,[a,b])
    def test_PR20(self):
        with pair() as (ctx,a,b):self.err('PARENT_PAIR_AMBIGUOUS',self.engine().pipe_return,ctx,(a,a))
    def test_PR21(self):
        with pair() as (ctx,a,b):
            e=self.engine();e.pipe_return(ctx,(a,b));self.err('PARENT_PAIR_AMBIGUOUS',e.pipe_return,ctx,(a,b))
    def test_PR22(self):
        with pair() as (ctx,a,b):
            e,proc,pre=self.prepared(ctx,a,b);b.close();self.assertEqual(e.preview(proc),pre)
    def test_PR23(self):
        with pair() as (ctx,a,b):
            e,proc,pre=self.prepared(ctx,a,b);self.assertIs(e.pairs[0][3],b);body=p.encode(e.tables);self.assertNotIn(str(id(b)).encode(),body)
    def test_PR24(self):
        with pair() as (ctx,a,b):
            e=self.engine();e.pipe_return(ctx,(a,b));self.assertFalse(e.tables['protocol_instances']);self.assertEqual(p.validate_registrations(self.side(e),self.reg,p.LIMITS),1)
    def test_PR25(self):
        with pair() as (ctx,a,b):
            e,proc,pre=self.prepared(ctx,a,b);self.assertEqual(pre[1],RID);self.assertIs(proc._popen,None)
    def test_PR26(self):
        class Opaque:
            def __repr__(self):raise AssertionError('opaque')
            def __str__(self):raise AssertionError('opaque')
        with pair() as (ctx,a,b):
            e,proc,pre=self.prepared(ctx,a,b);proc._args=(Opaque(),RID,Opaque(),b);self.assertEqual(e.preview(proc),pre);self.assertNotIn(b'Opaque',p.encode(e.tables))
    def test_PR27(self):
        with pair() as (ctx,a,b):
            e,proc,pre=self.prepared(ctx,a,b);self.assertEqual(pre[0],next(iter(e.tables['parental_registrations'])))
    def test_PR28(self):
        with pair() as (ctx,a,b):
            e,proc,key=self.started(ctx,a,b);del proc._args;del proc._target;del proc._kwargs;self.assertEqual(e.tables['protocol_instances'][key]['domain_refs'],dict(run_id=RID))
    def test_PR29(self):
        with pair() as (ctx,a,b):
            e,proc,key=self.started(ctx,a,b);self.assertEqual(next(iter(e.tables['parental_registrations'].values()))['child_pid'],12345);self.assertEqual(p.validate_causal(self.side(e),self.reg)['rows'],3)
    def test_PR30(self):
        with pair() as (ctx,a,b):
            e,proc,pre=self.prepared(ctx,a,b);error=RuntimeError('SYNTHETIC');e.started(proc,pre,None,True);self.assertFalse(e.tables['protocol_instances']);self.assertEqual(next(iter(e.tables['parental_registrations'].values()))['start_outcome'],'EXCEPTION')
        self.wrapper_exception()
    def test_PR31(self):
        with pair() as (ctx,a,b):
            e,proc,key=self.started(ctx,a,b);proc._popen=None;self.err('PARENT_PAIR_AMBIGUOUS',e.preview,proc)
    def test_PR32(self):
        with pair() as (ctx,a,b):
            e,proc,pre=self.prepared(ctx,a,b);proc._args=(None,OTHER,None,b);self.err('PARENT_CONTEXT_MISMATCH',e.preview,proc)
    def test_PR33(self):self.real_chain()
    def test_PR34(self):
        with pair() as (ctx,a,b):
            e,proc,key=self.started(ctx,a,b);value=snapshot();e.message(a,value);msg=e.tables['protocol_instances'][key]['observed_messages'][0];self.assertEqual(msg['value_digest'],c.digest_value(value,p.LIMITS));self.assertEqual(msg['authority'],'CHILD_PROTOCOL_RETURN');self.assertNotIn('state',msg)
    def test_PR35(self):self.event_chain('positive')
    def test_PR36(self):self.event_chain('positive');self.event_chain('no_assertion')
    def test_PR37(self):self.event_chain('multiple_snapshots')
    def test_PR38(self):
        with pair() as (ctx,a,b):
            e,proc,key=self.started(ctx,a,b);self.err('CHILD_HEADER_CONFLICT',e.message,a,snapshot(OTHER));self.assertFalse(e.tables['protocol_instances'][key]['observed_messages'])
    def test_PR39(self):
        with pair() as (ctx,a,b):
            e,proc,key=self.started(ctx,a,b);e.exit(proc,direct=True);self.assertIsNone(e.tables['protocol_instances'][key]['exit_observations'][-1]['returncode']);proc._popen.returncode=0;e.exit(proc,direct=True);self.assertEqual(e.tables['protocol_instances'][key]['exit_observations'][-1]['returncode'],0)
    def test_PR40(self):self.assertIsNone(self.header('CP14',snapshot())['command_id']);self.assertEqual(self.header('CP14',snapshot())['command_id_authority'],'NOT_APPLICABLE')
    def test_PR41(self):
        for policy in ('CP03','CP04','CP06','CP09','CP10','CP12'):
            h=self.header(policy,receipt());self.assertEqual(h['command_id'],CID);self.assertNotIn('text',h['receipt']['result_metadata'])
    def test_PR42(self):
        h=self.header('CP15',drive_receipt());self.assertEqual(h['receipt']['commit_sha256'],HEX);self.assertNotIn('seq',h['receipt'])
    def test_PR43(self):
        for policy in ('CP05','CP11'):
            h=self.header(policy,dict(send_id=OTHER,ticket=RID,receipt=receipt()));self.assertEqual(h['command_id'],CID);self.assertEqual(h['selectors'],dict(send_id=OTHER,ticket=RID))
    def test_PR44(self):self.assertEqual(self.header('CP05',dict(send_id=OTHER,ticket=RID,receipt=receipt()))['coverage'],'LAST_PUBLIC_RECEIPT_ONLY_NOT_ALL_INTERNAL_COMMANDS')
    def test_PR45(self):
        for policy in ('CP07','CP13'):
            h=self.header(policy,dict(ticket=RID));self.assertEqual(h['header_status'],'REMOTE_RESULT_WITHOUT_STORE_RECEIPT');self.assertIsNone(h['receipt']);self.assertEqual(h['command_id_authority'],'CHILD_LOCAL_NOT_OBSERVED')
    def test_PR46(self):
        for policy,family in (('CP02','T'),('CP08','R')):
            value={k:0 for k in self.contract['original_return_shapes'][family]['exact_keys']};value.update(schema='d5.durable-summary.v1' if family=='T' else 'd5.relational-summary.v1',activation_allowed=False,grants_execution_authority=False,D5_closed=False)
            self.assertEqual(self.header(policy,value)['header_status'],'SNAPSHOT_NO_COMMAND')
        self.assertEqual(self.header('CP14',snapshot())['coverage'],'SNAPSHOT_OR_SUMMARY_ONLY_NOT_INDEPENDENT_STORE_ORACLE')
    def test_PR47(self):self.assertEqual(self.header('CP01',None)['header_status'],'GENESIS_NO_COMMAND_RECEIPT');self.err('CHILD_ACTION_SCHEMA_INVALID',self.header,'CP01',{})
    def test_PR48(self):
        for v in (dict(send_id=OTHER,ticket=RID,nested={'receipt':receipt()}),dict(send_id=OTHER,ticket=RID,receipt=receipt(),extra=1)):
            self.err('CHILD_ACTION_SCHEMA_INVALID',self.header,'CP05',v)
    def test_PR49(self):h=p.intent_header(dict(cid=CID));self.assertEqual(h['requested_command_id'],CID);self.assertEqual(h['authority'],'OBSERVED_PARENT_INTENT_NOT_OBSERVED_CHILD_COMMAND');self.assertIsNone(self.header('CP07',dict(ticket=RID))['command_id'])
    def test_PR50(self):self.assertEqual(self.header('CP13',dict(send_id=OTHER,ticket=RID))['command_id_authority'],'CHILD_LOCAL_NOT_OBSERVED')
    def test_PR51(self):
        with pair() as (ctx,a,b):
            e=self.engine();proc=ctx.Process();key=e.register(proc,a,dict(run_id=RID),'mutate',dict(cid=OTHER),family='T');self.err('CHILD_HEADER_CONFLICT',e.message,a,('OK',receipt()))
    def test_PR52(self):
        h=self.header('CP07',dict(ticket=RID));self.assertIsNone(h['command_id']);self.assertNotIn('uuid5',p.child_header.__code__.co_names)
    def test_PR53(self):
        with pair() as (ctx,a,b):
            e=self.engine();proc=ctx.Process();key=e.register(proc,a,dict(run_id=RID),'remote',{},point='before_object',family='T');e.message(a,('READY','before_object'));self.assertNotIn('receipt',e.tables['protocol_instances'][key]['observed_messages'][0]);self.assertFalse(e.tables['causal_links'])
    def test_PR54(self):
        for point in self.contract['negative_frontier_rules']['not_automatic_no_effect']:self.assertIn(point,p.PROTOCOL_POINTS)
        self.event_chain('changed_digest')
    def test_PR55(self):
        with pair() as (ctx,a,b):
            e,proc,key=self.started(ctx,a,b);e.message(a,('ERROR','SYNTHETIC_ERROR'));self.assertEqual(e.tables['protocol_instances'][key]['observed_messages'][0]['code'],'SYNTHETIC_ERROR');self.err('CHILD_ACTION_SCHEMA_INVALID',e.message,a,('ERROR',RuntimeError('secret')))
    def test_PR56(self):
        with pair() as (ctx,a,b):
            e,proc,key=self.started(ctx,a,b);self.err('CHILD_ACTION_SCHEMA_INVALID',e.message,a,('ACK',0));self.assertFalse(e.tables['protocol_instances'][key]['observed_messages'])
    def test_PR57(self):
        with pair() as (ctx,a,b):
            e,proc,key=self.started(ctx,a,b);e.message(a,snapshot());side=self.side(e);self.assertEqual(p.validate_causal(side,self.reg)['rows'],3);side['protocol_instances'][key]['extra']=True;self.err('CAUSAL_SCHEMA_INVALID',p.validate_causal,side,self.reg)
    def test_PR58(self):
        with pair() as (ctx,a,b):
            e=self.engine();proc=ctx.Process();key=e.register(proc,a,dict(run_id=RID),'dispatch',{},family='T');e.message(a,('OK',dict(send_id=RID,ticket=OTHER,receipt=receipt())));msg=e.tables['protocol_instances'][key]['observed_messages'][0];self.assertIn('receipt',msg['header']);self.assertNotIn('raw_pointer',msg)
    def test_PR59(self):
        with pair() as (ctx,a,b):
            e,proc,key=self.started(ctx,a,b);side=self.side(e);side['protocol_instances'][key]['registration_ref']='ORPHAN';self.err('PARENT_PROCESS_UNREGISTERED',p.validate_causal,side,self.reg)
    def test_PR60(self):
        self.assertNotEqual(receipt()['after_data_sha256'],HEX);self.assertNotEqual(p.canonical_hash({'x':1}),p.canonical_hash({'x':1},drive=True));self.assertNotEqual(c.digest_value({'x':1},p.LIMITS)['sha256'],p.canonical_hash({'x':1}))
    def test_PR61(self):
        with pair() as (ctx,a,b):
            e,proc,key=self.started(ctx,a,b);side=self.side(e);side['protocol_instances'][key]['domain_refs']['run_id']=OTHER;self.err('PARENT_CONTEXT_MISMATCH',p.validate_causal,side,self.reg)
    def test_PR62(self):
        with pair() as (ctx,a,b):
            e,proc,key=self.started(ctx,a,b);self.err('PARENT_PAIR_AMBIGUOUS',e.register,proc,a,dict(run_id=RID),'snapshot',None,family='DRIVE')
    def test_PR63(self):
        with pair() as (ctx,a,b):
            e,proc,key=self.started(ctx,a,b);side=self.side(e);side['protocol_instances'][key]['schema']='d5.causal-protocol-instance.v1';self.err('CAUSAL_SCHEMA_INVALID',p.validate_causal,side,self.reg)
    def test_PR64(self):self.event_chain('no_exit')
    def test_PR65(self):
        e=self.engine();self.err('CAUSAL_FIELD_BUDGET',e.row_budget,{'value':'x'*4096})
    def test_PR66(self):
        with owned() as (base,root,owner):
            r=self.recorder(owner);r.causal.frame=None
            for _ in range(2048):r.emit('SYNTHETIC_BOUNDARY')
            r.emit('SYNTHETIC_OVER');self.assertIn('EVENT_TEST_BUDGET',r.errors);self.assertEqual(r.active['event_count'],2048);r.events.close()
        with owned() as (base,root,owner):
            sink=p.PageSink(owner,RID);event={'event':'SYNTHETIC','sequence':0}
            for i in range(131072):sink.append(dict(event,sequence=i))
            self.err('EVENT_CAMPAIGN_BUDGET',sink.append,event);sink.close()
    def test_PR67(self):
        e=self.engine({'refs':3});self.err('REFERENCE_BUDGET',e.object_ref,object())
        value=[]
        for _ in range(34):value=[value]
        self.err('CAUSAL_FIELD_BUDGET',p.bounded_builtin,value)
    def test_PR68(self):
        self.assertEqual(p.LIMITS['index_sidecar_bytes'],12*1024*1024);self.assertEqual(p.LIMITS['refs'],16384)
        self.err('PACKAGE_SET_MISMATCH',p.package_size,{str(i):1 for i in range(38)})
    def test_PR69(self):self.err('CAUSAL_FIELD_BUDGET',p.bounded_builtin,'x'*100,{'operand_bytes':16});self.err('CHILD_ACTION_SCHEMA_INVALID',self.header,'CP03',dict(receipt(),unexpected=True))
    def test_PR70(self):
        with owned() as (base,root,owner):
            (root/'input').write_bytes(b'12345678');reader=c.Reader(base,{'read_bytes':12});reader.read('packet/input');self.err('READ_BUDGET',reader.read,'packet/input')
    def test_PR71(self):self.assertEqual(self.design['component_external_seconds'],300);self.assertEqual(p.LIMITS['campaign_seconds'],900)
    def test_PR72(self):self.assertEqual(p.plan(registry=self.reg)['expected_tests'],321);self.assertFalse(p.plan(registry=self.reg)['functional_execution_authorized'])
    def test_PR73(self):self.real_chain()
    def test_PR74(self):
        with owned() as (base,root,owner):
            r=self.recorder(owner);old=p.multiprocessing.context.BaseContext.Pipe;r.install_direct()
            try:
                with patch.object(r.causal,'pipe_return',side_effect=c.CaptureFault('PARENT_PAIR_AMBIGUOUS')):
                    a,b=p.multiprocessing.context.SpawnContext().Pipe();self.assertIn('PARENT_PAIR_AMBIGUOUS',r.errors);a.close();b.close()
            finally:r.restore();r.events.close()
            self.assertIs(p.multiprocessing.context.BaseContext.Pipe,old)
    def test_PR75(self):
        tree=ast.parse((ROOT/'testing/prospective_capture_parental/capture.py').read_text());cls=next(n for n in tree.body if isinstance(n,ast.ClassDef) and n.name=='ParentalState')
        calls={n.func.attr for n in ast.walk(cls) if isinstance(n,ast.Call) and isinstance(n.func,ast.Attribute)}
        self.assertFalse(calls & {'poll','wait','is_alive','kill','send','recv','fileno','snapshot','lookup'})
    def test_PR76(self):self.assertNotIn('install',synthetic_snapshot.__code__.co_names);self.assertEqual(self.contract['private_memory_exception']['argument_indices'],{'1':'run_id','3':'exact_child_endpoint_object'})
    def test_PR77(self):
        ledger=p.Ledger(RID,pid=123);ledger.at('TARGETS');ledger.fail('PARENT_PAIR_AMBIGUOUS');ledger.at('FINALIZE');ledger.fail('STALE_INPUTS');diag=ledger.value();self.assertEqual((diag['phase'],diag['code']),('TARGETS','SANITIZED_WORKER_ERROR'));self.assertLessEqual(len(p.encode(diag)),4096)
    def test_PR78(self):
        with owned() as (base,root,owner):
            fd=owner.create('partial');writer=p.SideWriter(fd,RID,pid=123);ledger=p.Ledger(RID,pid=123);ledger.fail('STALE_INPUTS')
            def partial(fd,data):os.write(fd,data[:12]);raise OSError('synthetic')
            try:
                with patch.object(p,'write_all',side_effect=partial):
                    with self.assertRaises(OSError):writer.failure(ledger)
                self.assertFalse(writer.failure(ledger));self.assertEqual((root/'partial').stat().st_size,12)
            finally:os.close(fd)
    def test_PR79(self):
        with owned() as (base,root,owner):
            r=self.recorder(owner);old=p.multiprocessing.context.BaseContext.Pipe;r.install_direct();r.restore();r.events.close();self.assertIs(p.multiprocessing.context.BaseContext.Pipe,old)
    def test_PR80(self):self.check(not self.reg['observer_scope']['child_observers_installed'] and not self.reg['observer_scope']['checkpoint_or_hook_observers'],'no child or checkpoint instrumenting')
    def test_PR81(self):self.assertEqual(forbidden(),[])
    def test_PR82(self):
        for name in ('D5-I83-integrity.json','D5-I84-integrity.json'):
            seal=json.loads((ROOT/'docs/validation'/name).read_text())
            for path,digest in seal['artifacts'].items():self.assertEqual(c.sha((ROOT/path).read_bytes()),digest)
    def test_PR83(self):
        for path,digest in self.design['inputs'].items():
            if path.startswith('testing/prospective_capture') and path.endswith('/capture.py'):self.assertEqual(c.sha((ROOT/path).read_bytes()),digest)
    def test_PR84(self):self.event_chain('no_snapshot');self.assertIn('UNREGISTERED_CHILD_PROTOCOL_REQUIRED',(ROOT/'testing/prospective_capture_causal/capture.py').read_text())
    def test_PR85(self):self.assertEqual(self.reg['semantic_baseline'],dict(SUPPORTS_BOUNDED=83,PARTIAL=1));self.assertEqual(self.design['remaining_partial_parts'],['UI04.1'])
    def test_PR86(self):self.check(self.design['D1_D4_closed_unchanged'] and self.design['local_I1_I20_accepted_milestone_unchanged'] and self.design['prior_30_of_35_not_promoted'],'prior milestones preserved')
    def test_PR87(self):
        for key in ('real_provider_access','credentials_used','quota_consumed','reservations_created','operational_activation','migration_promotion','deployment','D6_started'):self.assertFalse(self.design[key])
    def test_PR88(self):self.assertFalse(p.plan(registry=self.reg)['publication_authorized']);self.assertFalse(p.plan(registry=self.reg)['closure'])
    def test_PR89(self):self.integration('success');self.integration('failure');self.integration('untrusted')
    def test_PR90(self):
        e=self.engine();self.err('CHILD_ACTION_SCHEMA_INVALID',p.policy_for,self.contract,'T','unknown');self.assertFalse(e.tables['protocol_instances']);self.assertFalse((ROOT/p.AUTHORITY).exists())
    def test_PR91(self):self.assertEqual(p.plan(registry=self.reg)['status'],'NOT_RUN_I86_AUTHORIZATION_REQUIRED')
    def test_PR92(self):
        self.assertEqual(p.AUTHORITY,'docs/validation/D5-I86-capture-authorization.json');self.assertEqual(p.DESTINATION,'docs/validation/D5-I86-P01')
        for name in (p.AUTHORITY,p.DESTINATION,p.LAUNCH_COPY):self.assertFalse((ROOT/name).exists())
    def test_PR93(self):self.assertEqual(len(self.reg['entry']['expected_test_ids']),321);self.assertEqual(len(self.reg['entry']['expected_groups']),12)
    def test_PR94(self):self.assertFalse(p.plan(registry=self.reg)['closure']);self.assertEqual(p.plan(registry=self.reg)['global_review'],'OPEN')
    def test_PR95(self):self.assertFalse(self.design['closure']);self.assertFalse(self.design['D5_closed']);self.assertFalse(self.design['H07_closed'])
    def test_PR96(self):
        with pair() as (ctx,a,b):
            e,proc,key=self.started(ctx,a,b);self.err('CHILD_ACTION_SCHEMA_INVALID',e.message,a,('UNKNOWN',{}));self.assertFalse(e.tables['protocol_instances'][key]['observed_messages'])
        self.assertFalse((ROOT/p.AUTHORITY).exists())

    def wrapper_exception(self):
        with owned() as (base,root,owner):
            r=self.recorder(owner);error=RuntimeError('SYNTHETIC_START');calls=[]
            def original(obj):calls.append(obj);raise error
            # Replace only for this new synthetic test; restore exact pointer afterwards.
            with patch.object(p.multiprocessing.process.BaseProcess,'start',original):
                r.install_direct()
                try:
                    r.causal.frame['test_id']='OUTSIDE';obj=object()
                    with self.assertRaises(RuntimeError) as raised:p.multiprocessing.process.BaseProcess.start(obj)
                    self.assertIs(raised.exception,error);self.assertEqual(calls,[obj])
                finally:r.restore();r.events.close()
    def event_chain(self,mode):
        with pair() as (ctx,a,b):
            e,proc,key=self.started(ctx,a,b);e.message(a,snapshot());e.exit(proc,0);side=self.side(e);context=e.context();digest=c.digest_value(snapshot(),p.LIMITS)
            events={0:dict(event='CALL_RETURN',method='snapshot',causal_context=context,observer_authority='OWN_FIXTURE_SNAPSHOT',result_digest=digest),1:dict(event='ASSERTION_RETURNED',helper='assertEqual',operands=[digest,digest],causal_context=context),2:dict(event='TEST_RESULT',outcome='PASS',causal_context=context)}
            if mode=='no_assertion':del events[1]
            elif mode=='no_snapshot':del events[0]
            elif mode=='changed_digest':events[0]['result_digest']=c.digest_value({},p.LIMITS)
            elif mode=='multiple_snapshots':events[3]=dict(events[0])
            elif mode=='no_exit':side['protocol_instances'][key]['exit_observations']=[]
            codes={'no_assertion':'CAUSAL_LINK_MISSING','no_snapshot':'CHILD_HEADER_CONFLICT','changed_digest':'CHILD_HEADER_CONFLICT','no_exit':'PENDING_CHILD_EXIT'}
            if mode in codes:self.err(codes[mode],p.validate_direct_events,side,self.reg,events)
            else:p.validate_direct_events(side,self.reg,events)
    def real_chain(self):
        with owned() as (base,root,owner):
            r=self.recorder(owner);r.install_direct();original_recv=p.multiprocessing.connection._ConnectionBase.recv;original_join=p.multiprocessing.process.BaseProcess.join;children=[]
            # These adapters observe only original returns in this new synthetic test.
            def recv(obj):
                value=original_recv(obj);r.attempt(r.causal.message,obj,value);return value
            def join(obj,*args,**kwargs):
                value=original_join(obj,*args,**kwargs);r.attempt(r.causal.exit,obj,direct=True);return value
            try:
                with patch.object(p.multiprocessing.connection._ConnectionBase,'recv',recv),patch.object(p.multiprocessing.process.BaseProcess,'join',join):
                    ctx=p.multiprocessing.context.SpawnContext();a,b=ctx.Pipe();proc=ctx.Process(target=synthetic_snapshot,args=(object(),RID,object(),b));children.append(proc)
                    try:
                        proc.start();b.close();self.assertTrue(a.poll(10));value=a.recv();proc.join(10);self.assertEqual(value,snapshot());self.assertEqual(proc.exitcode,0)
                        row=next(iter(r.causal.tables['parental_registrations'].values()));self.assertEqual(row['status'],'START_OBSERVED');self.assertFalse(hasattr(proc,'_args'));self.assertEqual(r.errors,[])
                    finally:
                        if proc.is_alive():proc.terminate();proc.join(5)
                        a.close();b.close();CHILDREN.append(dict(exitcode=proc.exitcode,role='OWN_SYNTHETIC_SNAPSHOT'));proc.close()
            finally:r.restore();r.events.close()
            self.observations.append(dict(original_snapshot_received=True,errors=list(r.errors)))

    def integration(self,mode):
        with owned() as (base,root,owner):
            (root/'runner.py').write_text('SYNTHETIC_ONLY\n');before={'packet/runner.py':c.sha((root/'runner.py').read_bytes())};tid='pr_synthetic.Example.test_one'
            entry=dict(id='P01',expected_tests=1,expected_test_ids=[tid],expected_groups={'pr_synthetic':1},group_policies={'pr_synthetic':dict(target='SYNTHETIC_COMPONENT_ONLY',domain_required=False,no_store_reason='SYNTHETIC_COMPONENT_ONLY')},record_sources=[],method_bindings={tid:dict(status='SOURCE_DERIVED_EXPECTATION',scope='SYNTHETIC_ONLY')},expected_raw_scenarios=0,expected_scenario_multiplicity={},runner_module='pr_synthetic_runner',runner_path='packet/runner.py',runner_explicit_input_paths=['packet/runner.py'],runner_discovery_patterns=[],runner_effective_inputs=before)
            reg=dict(entry=entry,policies=[],class_allowlist=[dict(id='builtins.dict',source=None)],snapshot_scopes=[],negative_DI28={},operand_scopes=[],projection_schemas=self.spec,inventory=[],parental_contract=self.contract)
            approved=dict(capture_inputs=before);children=[];real_popen=subprocess.Popen
            script='''import sys,json,types,unittest
from pathlib import Path
from testing.prospective_capture_parental import capture as p,worker as w
args=sys.argv[1:7];reg=json.loads(sys.argv[7]);approved=json.loads(sys.argv[8]);root=Path(sys.argv[9]);mode=sys.argv[10]
p.read_registry=lambda *a:reg
p.authority=lambda *a:approved
if mode=='untrusted':
 def reject(*a):raise p.c.CaptureFault('I86_AUTHORIZATION_REQUIRED')
 p.authority=reject
module=types.ModuleType('pr_synthetic_runner');module.__file__=str(root/'packet/runner.py')
class Example(unittest.TestCase):
 def test_one(self):
  with self.subTest(mode='SYNTHETIC'):self.assertEqual(1,1)
Example.__module__='pr_synthetic'
def main():
 result=unittest.TestResult();unittest.defaultTestLoader.loadTestsFromTestCase(Example).run(result)
 print(json.dumps(dict(status='PASS',tests_run=1,passed=reg['entry']['expected_test_ids'],failures=[],errors=[],skipped=[],scenarios=[],case_test_map={})));return 0
module.main=main
w.importlib=types.SimpleNamespace(import_module=lambda name:module)
def targets(*args):
 if mode=='failure':raise p.c.CaptureFault('PARENT_BINDING_CHANGED')
 return [],None,None
w.targets=targets
p.Recorder.install_causal=lambda self:None
sys.exit(w.main(args,root))
'''
            def producer(cmd,**kwargs):
                kwargs['cwd']=ROOT;child=real_popen([sys.executable,'-B','-c',script,*cmd[-6:],json.dumps(reg),json.dumps(approved),str(base),mode],**kwargs);children.append(child);return child
            (base/'docs/validation').mkdir(parents=True)
            with patch.object(p,'read_registry',return_value=reg),patch.object(p,'authority',return_value=approved),patch.object(c.subprocess,'Popen',side_effect=producer):
                context=p.launch('P01',base);self.assertRaises(FileExistsError,p.launch,'P01',base)
            for child in children:CHILDREN.append(dict(exitcode=child.returncode,role='SYNTHETIC_PARENTAL_WORKER_'+mode.upper()))
            self.assertEqual(context['cleanup']['status'],'OWN_GROUP_GONE');self.assertEqual(json.loads((base/p.LAUNCH_COPY).read_text()),context)
            if mode=='success':self.assertEqual(context['capture_status'],'TRACE_CAPTURED_PENDING_SUFFICIENCY_REVIEW',context);self.assertEqual(context['worker_diagnostic']['status'],'COMPLETED')
            elif mode=='failure':self.assertEqual(context['capture_status'],'BLOCKED_WORKER_FAILURE',context);self.assertEqual(context['worker_diagnostic']['phase'],'TARGETS');self.assertEqual(context['worker_diagnostic']['code'],'SANITIZED_WORKER_ERROR');self.assertEqual((base/p.DESTINATION/'runner-raw.json').stat().st_size,0)
            else:self.assertEqual(context['worker_diagnostic_status'],'WORKER_DIAGNOSTIC_NOT_RECORDED');self.assertEqual((base/p.DESTINATION/'sidecar.json').stat().st_size,0)
            self.observations.append(dict(producer='SYNTHETIC_ONLY',mode=mode,capture_status=context['capture_status'],cleanup=context['cleanup']))
