# SPDX-License-Identifier: GPL-3.0-only
"""DW24: new synthetic witnesses, entrypoints and owned producers only."""
import ast
import contextlib
import copy
import json
import os
from pathlib import Path
import sys
import tempfile
import threading
import types
import unittest
from unittest.mock import patch
from testing.prospective_capture_domains import capture as p,worker as w
c=p.c;ROOT=p.ROOT;ROOTS=[];CHILDREN=[]
RID='11111111-1111-4111-8111-111111111111';SID='22222222-2222-4222-8222-222222222222';CID='33333333-3333-4333-8333-333333333333';OTHER='44444444-4444-4444-8444-444444444444';HEX='a'*64

class Witness:pass
class SyntheticLab:pass
class SyntheticError(ValueError):pass

def request():return dict(cid=CID,kind='SYNTHETIC',args={'synthetic':True},expected=dict(seq=0,commit_sha256=HEX))
def receipt():return dict(schema='d5.durable-receipt.v1',command_id=CID,request_sha256=p.store_request(request())['request_sha256'],before_seq=0,seq=1,before_state_sha256='b'*64,after_data_sha256='c'*64,historical=False,grants_execution_authority=False,quota_consumed=0,reservations_created=0,activation_allowed=False,result={'manifest_id':HEX})
def returned():
    rec=receipt();return dict(head=dict(run_id=RID,store_id=SID,role='CLIENT',seq=1,commit_sha256=HEX),state={'receipts':{CID:rec}},chain=[dict(seq=1,command_id=CID,request_sha256=rec['request_sha256'],operation={k:request()[k] for k in ('kind','args','expected')},receipt={k:v for k,v in rec.items() if k!='historical'})])
def oracle(kind='T'):
    row=dict(case='DW_SYNTHETIC',role='CLIENT',store_id=SID,seq=1,state_sha256=p.canonical_hash(returned()['state']),receipts=1)
    if kind=='T':row.update(commit_sha256=HEX,tasks=0)
    else:row.update(head_sha256=HEX,entities=0,relations=0)
    return row

def drive_snapshot():return dict(schema='d5.fixture-drive-snapshot.v1',run_id=RID,version=1,head_sha256=HEX,state={'synthetic':True},committed_pages=1,occurrences=0,logical_observations=0,terminal_diagnostics=0,reference_selected=False,persistent_D2_writes=0,remote_requests=0)
def synthetic_child(root,run_id,scope,connection):connection.send(drive_snapshot());connection.close()

class SyntheticStore:
    def __init__(self,path,run_id,store_id,role,reducer,genesis,*,hook=None):self.calls=0
    def snapshot(self):self.calls+=1;return returned()
    def transact(self,cid,kind,args,expected=None):self.calls+=1;return receipt()

class SyntheticDrive:
    def snapshot(self):return drive_snapshot()

@contextlib.contextmanager
def owned():
    row=dict(ownership_verified=False,removed=False,sibling_preserved=False);ROOTS.append(row)
    with tempfile.TemporaryDirectory(prefix='i88-own-') as tmp:
        base=Path(tmp);root=base/'packet';root.mkdir();owner=c.OwnedRoot(root);sibling=base/'sibling';sibling.write_bytes(b'I88_SYNTHETIC')
        try:yield base,root,owner
        finally:owner.verify();row.update(ownership_verified=True,sibling_preserved=sibling.read_bytes()==b'I88_SYNTHETIC')
    row['removed']=not base.exists()

def forbidden():
    return sorted(n for n in sys.modules if n.startswith(('source_ingest','testing.D5','testing.durable_','testing.evidence_')) or n.endswith(('.test_parental_capture','.run_parental_lab','.test_causal_capture','.run_causal_lab','.test_late_capture','.run_late_lab','.test_typed_capture','.run_typed_lab','.test_paged_capture','.run_paged_lab','.test_prospective_capture','.run_capture_lab')))

class DomainTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):cls.reg=p.read_registry();cls.spec=cls.reg['projection_schemas'];cls.design=cls.reg['domain_contract']
    def setUp(self):self.observations=[]
    def check(self,value,label):self.assertTrue(value);self.observations.append(dict(check=label,status='PASS'))
    def err(self,code,fn,*args,**kwargs):
        with self.assertRaises(c.CaptureFault) as raised:fn(*args,**kwargs)
        self.assertEqual(raised.exception.code,code);self.observations.append(dict(expected=code,observed=raised.exception.code))
    def engine(self,limits=None):
        lim=dict(p.LIMITS,**(limits or {}));count=[0];events=[];errors=[]
        def charge(n=1):count[0]+=n;p.fault(count[0]<=lim['refs'],'REFERENCE_BUDGET')
        def emit(kind,**data):events.append(dict(event=kind,sequence=len(events),test_frame_id=e.frame['test_frame_id'],**data))
        e=p.DomainState(RID,lim,self.spec,charge,emit,errors.append,contract=self.reg['parental_contract']);e.begin(dict(test_frame_id='F1',test_id='DW_SYNTHETIC'),self);e.charged=count;e.seen_events=events;e.seen_errors=errors;return e
    def witness(self,e,obj=None,identity=None,authority=p.CONSTRUCTION_AUTH):
        obj=Witness() if obj is None else obj;identity=dict(run_id=RID,store_id=SID,role='CLIENT') if identity is None else identity;ref=e.declaration(obj,identity,authority);ctx=e.context()
        if authority==p.CONSTRUCTION_AUTH:e.emit('CONSTRUCTION_OBSERVED',object_ref=ref,**identity,authority=authority,process_scope='PARENT_ONLY',causal_context=ctx)
        else:e.emit('CALL_RETURN',method='snapshot',owner_ref=ref,result_digest=c.digest_value(returned(),p.LIMITS),causal_context=ctx,domain_observation=dict(schema='d5.domain-header-observation.v1',**identity,seq=1,commit_sha256=HEX,authority=authority))
        return obj,ref
    def side(self,e):
        owners={ref:dict(scope='SYNTHETIC_OBJECT_NOT_STORE_ID',identity=None) for _,ref in e.objects};decl={}
        for g in e.tables['domain_witness_groups'].values():
            for w in g['witnesses']:
                ref=w['object_ref'];owners[ref]['identity']={k:g[k] for k in ('run_id','store_id')}
                if p.CONSTRUCTION_AUTH in w['authorities']:decl[ref]=dict(**{k:g[k] for k in p.DOMAIN_IDENTITY},authority=p.CONSTRUCTION_AUTH,process_scope='PARENT_ONLY')
        frame=dict(test_frame_id='F1',test_id='DW_SYNTHETIC',record_links=[],owner_context_refs=list(owners))
        for key,row in e.tables['retained_oracles'].items():frame['record_links'].append(dict(module=row['source_module'],field='ORACLES',index=row['source_index'],digest=row['value_digest'],raw_pointer=None,sidecar_pointer='/retained_oracles/'+key+'/value'))
        return dict(schema=p.NORMAL_SCHEMA,capture_run_id=RID,frames=[frame],owner_contexts=owners,construction_declarations=decl,shared_reference_count=e.charged[0],**e.tables)
    def retained(self,count=2,command=False):
        e=self.engine();objects=[self.witness(e) for _ in range(count)];group=e.domain(returned()['head']);command_ref=None
        if command:
            obj,ref=objects[0];command_ref=e.open_call('Store.transact',obj,'transact',p.store_request(request()));e.calls[command_ref]['domain_ref']=ref;e.close_call(command_ref,p.store_receipt(receipt(),self.spec))
        call=e.open_call('T.independent',Witness(),'independent',{'kind':'ORIGINAL_HARNESS_ORACLE'});ref=e.retain('dw_synthetic',0,oracle(),'T',returned(),call);e.link(call,ref,'RETURN_RETAINS_ORACLE',group)
        output=dict(authority='RETAINED_HARNESS_ORACLE',head=returned()['head'],retained_refs=[ref],commit=p.oracle_commit(returned(),self.spec));e.close_call(call,output)
        if command:e.link(command_ref,ref,'COMMAND_RECEIPT_ORACLE_COMMIT',group)
        return e,call,ref,command_ref
    def evidence(self,e):
        events={r['sequence']:r for r in e.seen_events};p.validate_causal(self.side(e),self.reg);p.validate_domain_evidence(self.side(e),self.reg,events,e.calls);return events
    def recorder(self,owner,tid='dw_synthetic.Run.test_one',record_sources=None):
        entry=dict(id='SYNTHETIC_ONLY',expected_test_ids=[tid],expected_groups={'dw_synthetic':1},group_policies={'dw_synthetic':dict(domain_required=False,no_store_reason='SYNTHETIC_ONLY')},record_sources=record_sources or [],method_bindings={tid:dict(status='SOURCE_DERIVED_EXPECTATION',scope='SYNTHETIC_COMPONENT_ONLY')})
        reg=copy.deepcopy(self.reg);reg['snapshot_scopes']=[];reg['operand_scopes']=[]
        r=p.Recorder(entry,owner,profile=reg,bindings=p.LateBindings([dict(id='builtins.dict',source=None)],c.Reader(ROOT)));r.causal_inventory[tid]=dict(family='T',classification='CAUSAL_DOMAIN');return r
    def test_DW01(self):
        for filename in ('D5-I85-integrity.json','D5-I86-integrity.json','D5-I87-integrity.json'):
            for n,h in json.loads((ROOT/'docs/validation'/filename).read_text())['artifacts'].items():self.assertEqual(c.sha((ROOT/n).read_bytes()),h)
        self.check(not self.design['implementation_authorized'],'I87 historical proposal unchanged; authorization I88 recorded separately')
    def test_DW02(self):
        with owned() as (base,root,owner):
            old=json.loads((ROOT/'docs/validation/D5-I86-capture-authorization.json').read_text());path=base/p.AUTHORITY;path.parent.mkdir(parents=True);path.write_text(json.dumps(old));self.err('I89_AUTHORIZATION_REQUIRED',p.authority,base,'P01',self.reg)
            self.assertFalse((base/p.DESTINATION).exists())
        self.assertNotEqual(p.DESTINATION,'docs/validation/D5-I86-P01')
    def test_DW03(self):
        e=self.engine();obj,ref=self.witness(e);self.assertEqual(p.CausalState.domain(e,returned()['head']),ref);group=e.domain(returned()['head']);self.assertEqual(e.witnesses(group),[ref]);self.evidence(e)
    def test_DW04(self):
        e=self.engine();self.err('ORACLE_DOMAIN_IDENTITY_MISSING',e.domain,returned()['head']);self.err('ORACLE_DOMAIN_IDENTITY_MISSING',p.CausalState.domain,e,returned()['head']);self.assertFalse(e.tables['domain_witness_groups'])
    def test_DW05(self):
        e=self.engine();a,ar=self.witness(e);b,br=self.witness(e);self.assertIsNot(a,b);self.err('ORACLE_DOMAIN_IDENTITY_MISSING',p.CausalState.domain,e,returned()['head']);group=e.domain(returned()['head']);self.assertEqual(e.witnesses(group),sorted([ar,br]));self.evidence(e);self.observations.append(dict(reproduced='COPIED_PINNED_LEGACY_SELECTOR_MULTIPLE_OBJECTS',new_resolution='COMPLETE_WITNESS_SET',functional_DF03_executed=False))
    def test_DW06(self):
        e=self.engine();store,ref=self.witness(e);facade,fr=self.witness(e,authority=p.RETURN_AUTH);self.witness(e,store,authority=p.RETURN_AUTH);group=e.domain(returned()['head']);self.assertEqual(e.witnesses(group),sorted([ref,fr]));self.assertEqual(len(e.tables['domain_witness_groups'][group]['witnesses']),2);self.evidence(e);self.assertFalse(e.tables['retained_oracles'])
    def test_DW07(self):
        e=self.engine();a,ar=self.witness(e);b,br=self.witness(e,identity=dict(run_id=OTHER,store_id=SID,role='CLIENT'));self.assertNotEqual(e.domain(returned()['head']),e.domain(dict(run_id=OTHER,store_id=SID,role='CLIENT')))
        side=self.side(e);groups=list(side['domain_witness_groups'].values());groups[0]['witnesses'].append(dict(object_ref=br,authorities=[p.CONSTRUCTION_AUTH]));groups[0]['witnesses'].sort(key=lambda w:w['object_ref']);self.err('ORACLE_DOMAIN_IDENTITY_MISSING',p.validate_causal,side,self.reg)
    def test_DW08(self):
        e=self.engine();self.witness(e);self.witness(e,identity=dict(run_id=RID,store_id=SID,role='REMOTE'));self.assertEqual(len(e.tables['domain_witness_groups']),2);self.evidence(e)
    def test_DW09(self):
        e=self.engine();self.witness(e)
        with self.subTest(mode='OTHER'):self.err('ORACLE_DOMAIN_IDENTITY_MISSING',e.domain,returned()['head'])
        codes=[]
        def other():
            try:e.domain(returned()['head'])
            except c.CaptureFault as ex:codes.append(ex.code)
        thread=threading.Thread(target=other);thread.start();thread.join();self.assertEqual(codes,['ORACLE_DOMAIN_IDENTITY_MISSING']);e.begin(dict(test_frame_id='F2',test_id='OTHER'),self);self.err('ORACLE_DOMAIN_IDENTITY_MISSING',e.domain,returned()['head'])
    def test_DW10(self):
        e=self.engine();obj,ref=self.witness(e);self.err('ORACLE_DOMAIN_IDENTITY_MISSING',e.declaration,obj,dict(run_id=OTHER,store_id=SID,role='CLIENT'));self.assertEqual(e.object_identities[ref],(RID,SID,'CLIENT'))
    def test_DW11(self):
        e=self.engine();self.witness(e);group=next(iter(e.tables['domain_witness_groups'].values()));self.assertNotIn('head',group);self.assertNotIn('state',group);self.assertEqual(group['witnesses'][0]['authorities'],[p.CONSTRUCTION_AUTH]);self.assertFalse(e.tables['retained_oracles']);self.evidence(e)
    def test_DW12(self):self.full_recorder()
    def test_DW13(self):
        e,call,ref,command=self.retained(command=True);events=self.evidence(e);links=[r for r in e.tables['causal_links'].values() if r['relation']=='COMMAND_RECEIPT_ORACLE_COMMIT'];self.assertEqual(len(links),1);p.validate_command_link(e.calls[command],e.tables['retained_oracles'][ref],links[0],e.calls[call]['output'],self.side(e));self.assertEqual(len(e.tables['retained_oracles'][ref]['witness_refs']),2)
    def test_DW14(self):
        e,call,ref,command=self.retained(command=True);link=next(r for r in e.tables['causal_links'].values() if r['relation']=='COMMAND_RECEIPT_ORACLE_COMMIT');e.calls[command]['output']['command_id']=OTHER;self.err('REQUEST_HASH_CONFLICT',p.validate_command_link,e.calls[command],e.tables['retained_oracles'][ref],link,e.calls[call]['output'],self.side(e))
    def test_DW15(self):
        e=self.engine();self.witness(e);self.witness(e);self.assertIsNotNone(e.domain(returned()['head']));self.err('CAUSAL_LINK_AMBIGUOUS',e.domain,returned()['head'],True);self.assertEqual(len(next(iter(e.tables['domain_witness_groups'].values()))['witnesses']),2)
        e,call,ref,command=self.retained(command=True);obj=e.objects[0][0];duplicate=e.open_call('Store.transact',obj,'transact',p.store_request(request()));e.calls[duplicate]['domain_ref']=e.calls[command]['object_ref'];e.close_call(duplicate,p.store_receipt(receipt(),self.spec));self.err('CAUSAL_LINK_AMBIGUOUS',e.link_receipt_candidates,ref,e.calls[call]['output'],e.calls[call]['domain_group_ref'])
    def test_DW16(self):self.assertNotEqual(receipt()['after_data_sha256'],oracle()['state_sha256']);self.assertNotEqual(p.canonical_hash({'x':1}),p.canonical_hash({'x':1},drive=True));self.assertNotEqual(c.digest_value({'x':1},p.LIMITS)['sha256'],p.canonical_hash({'x':1}))
    def test_DW17(self):
        e,call,ref,_=self.retained();side=self.side(e);side['retained_oracles'][ref]['domain_group_ref']='ORPHAN';self.err('ORACLE_DOMAIN_IDENTITY_MISSING',p.validate_causal,side,self.reg)
        e=self.engine();self.witness(e);side=copy.deepcopy(self.side(e));key=next(iter(side['domain_witness_groups']));group=side['domain_witness_groups'][key];group['witnesses'].append(copy.deepcopy(group['witnesses'][0]));self.err('CAUSAL_LINK_AMBIGUOUS',p.validate_causal,side,self.reg)
        e,call,ref,_=self.retained();e.calls[call]['parent_call_ref']=call
        # Test the graph traversal through the public page reader in a separate
        # new synthetic packet, including a self-cycle and restored page binding.
        self.full_recorder(attack='cycle')
    def test_DW18(self):
        e=self.engine();obj,ref=self.witness(e,authority=p.RETURN_AUTH);side=self.side(e);p.validate_causal(side,self.reg);self.err('ORACLE_DOMAIN_IDENTITY_MISSING',p.validate_domain_evidence,side,self.reg,{})
        e,call,ref,_=self.retained();events=self.evidence(e);side=self.side(e);side['retained_oracles'][ref]['witness_refs']=side['retained_oracles'][ref]['witness_refs'][:1];self.err('CAUSAL_LINK_AMBIGUOUS',p.validate_domain_evidence,side,self.reg,events,e.calls)
    def test_DW19(self):
        e=self.engine({'refs':10});self.witness(e);self.err('REFERENCE_BUDGET',self.witness,e)
        e=self.engine();blocked=False
        for i in range(200):
            try:self.witness(e)
            except c.CaptureFault as ex:self.assertEqual(ex.code,'CAUSAL_FIELD_BUDGET');blocked=True;break
        self.assertTrue(blocked);self.assertGreater(len(p.encode(next(iter(e.tables['domain_witness_groups'].values())))),4096)
        e=self.engine();self.witness(e);self.err('SIDECAR_BUDGET',p.validate_causal,self.side(e),self.reg,{'index_sidecar_bytes':16})
    def test_DW20(self):
        for k,val in self.reg['limits'].items():self.assertEqual(val,json.loads((ROOT/p.PARENTAL_REGISTRY).read_text())['limits'][k])
        with owned() as (base,root,owner):
            sink=p.PageSink(owner,RID)
            for i in range(131072):sink.append(dict(event='DW_SYNTHETIC',sequence=i))
            self.err('EVENT_CAMPAIGN_BUDGET',sink.append,dict(event='DW_OVER',sequence=131072));sink.close();self.assertLessEqual(sink.total_bytes,64*1024*1024)
            (root/'input').write_bytes(b'12345678');reader=c.Reader(base,{'read_bytes':12});reader.read('packet/input');self.err('READ_BUDGET',reader.read,'packet/input')
        self.assertEqual(p.package_size({'OWNER':4096}),4096);self.err('PACKAGE_SET_MISMATCH',p.package_size,{str(i):1 for i in range(38)})
    def test_DW21(self):
        with owned() as (base,root,owner):
            r=self.recorder(owner);r.active=dict(test_id='dw_synthetic.Run.test_one',test_frame_id='F1',event_count=0,owner_context_refs=[]);r.frame_summary=dict(operands_missing=False,returns_missing=False);r.causal.begin(r.active,self)
            module=types.ModuleType('dw_failure');module.ORACLES=[];module.CURRENT_CASE='DW_SYNTHETIC';calls=[];value=returned()
            def independent(path):calls.append(path);return value
            module.independent=independent;r.wrap_boundary(module,'independent','T.independent')
            try:self.assertIs(module.independent('NO_DOMAIN_IO'),value);self.assertEqual(calls,['NO_DOMAIN_IO']);self.assertIn('ORACLE_DOMAIN_IDENTITY_MISSING',r.errors)
            finally:r.restore();r.events.close()
            error=SyntheticError('SYNTHETIC_ERROR');calls=[]
            def raising(path):calls.append(path);raise error
            module.independent=raising;r.causal.stacks.clear();r.causal_exception_types={'dw.SyntheticError':SyntheticError};r.wrap_boundary(module,'independent','T.independent')
            try:
                with self.assertRaises(SyntheticError) as caught:module.independent('NO_DOMAIN_IO')
                self.assertIs(caught.exception,error);self.assertEqual(calls,['NO_DOMAIN_IO'])
            finally:r.restore()
    def test_DW22(self):
        with owned() as (base,root,owner):
            r=self.recorder(owner);module=types.ModuleType('dw_restore');calls=[]
            def original(path):calls.append(path);return None
            module.independent=original;r.wrap_boundary(module,'independent','T.independent');module.independent=lambda path:None;r.restore();r.events.close();self.assertIs(module.independent,original);self.assertIn('OBSERVER_IDENTITY_CHANGED',r.errors)
            fd=owner.create('partial');writer=p.SideWriter(fd,RID,pid=123);ledger=p.Ledger(RID,pid=123);ledger.at('TARGETS');ledger.fail('ORACLE_DOMAIN_IDENTITY_MISSING');ledger.at('FINALIZE');ledger.fail('STALE_INPUTS');self.assertEqual(ledger.value()['phase'],'TARGETS');self.assertEqual(ledger.value()['code'],'SANITIZED_WORKER_ERROR')
            def partial(fd,body):os.write(fd,body[:12]);raise OSError('SYNTHETIC')
            try:
                with patch.object(p,'write_all',side_effect=partial):
                    with self.assertRaises(OSError):writer.failure(ledger)
                self.assertFalse(writer.failure(ledger));self.assertEqual((root/'partial').stat().st_size,12)
            finally:os.close(fd)
    def test_DW23(self):
        contract=self.reg['parental_contract'];policy=p.policy_for(contract,'T','remote');h=p.child_header({'ticket':CID},policy,contract,self.spec);self.assertIsNone(h['command_id']);self.assertEqual(h['command_id_authority'],'CHILD_LOCAL_NOT_OBSERVED')
        policy=p.policy_for(contract,'T','dispatch');h=p.child_header(dict(send_id=RID,ticket=SID,receipt=receipt()),policy,contract,self.spec);self.assertEqual(h['command_id'],CID);self.assertEqual(h['coverage'],'LAST_PUBLIC_RECEIPT_ONLY_NOT_ALL_INTERNAL_COMMANDS');self.direct_recorder()
    def test_DW24(self):
        self.assertEqual(p.plan(registry=self.reg)['status'],'NOT_RUN_I89_AUTHORIZATION_REQUIRED');self.assertFalse(p.plan(registry=self.reg)['closure'])
        self.assertEqual(w.main(['P01','3','4','5','6',RID]),2)
        self.assertEqual(forbidden(),[])
        for n in (p.AUTHORITY,p.DESTINATION,p.LAUNCH_COPY):self.assertFalse((ROOT/n).exists())

    def full_recorder(self,attack=None):
        with owned() as (base,root,owner):
            module=types.ModuleType('dw_synthetic_oracle');module.ORACLES=[];module.CURRENT_CASE='DW_SYNTHETIC';original_return=returned();invocations=[]
            def independent(path):invocations.append(path);module.ORACLES.append(oracle());return original_return
            module.independent=independent;tid='dw_synthetic.Run.test_one';r=self.recorder(owner,tid,[dict(module=module.__name__,field='ORACLES',raw_pointer=None)])
            def run_one(test):
                first=SyntheticStore(None,RID,SID,'CLIENT',None,None);first.snapshot();second=SyntheticStore(None,RID,SID,'CLIENT',None,None);second.snapshot();test.assertEqual(second.transact(**request())['command_id'],CID);test.assertIs(module.independent('NO_DOMAIN_IO'),original_return)
            Run=type('Run',(unittest.TestCase,),dict(__module__='dw_synthetic',test_one=run_one));old_constructor=SyntheticStore.__init__;old_snapshot=SyntheticStore.snapshot;old_transact=SyntheticStore.transact
            with patch.dict(sys.modules,{module.__name__:module}):
                try:
                    r.install();r.constructor(SyntheticStore);r.wrap_return(SyntheticStore,'snapshot');r.wrap_boundary(SyntheticStore,'transact','Store.transact');r.wrap_boundary(module,'independent','T.independent');result=unittest.TestResult();Run('test_one').run(result)
                finally:r.restore()
                side=r.finish()
            self.assertTrue(result.wasSuccessful());self.assertEqual(r.errors,[],side);self.assertEqual(side['status'],'TRACE_CAPTURED_PENDING_SUFFICIENCY_REVIEW');self.assertEqual(invocations,['NO_DOMAIN_IO']);self.assertIs(SyntheticStore.__init__,old_constructor);self.assertIs(SyntheticStore.snapshot,old_snapshot);self.assertIs(SyntheticStore.transact,old_transact)
            profile=r.profile
            if attack=='cycle':
                # Change only this owned synthetic packet and its checksum, then
                # require structural graph rejection rather than hash rejection.
                pg=side['pages'][0];path=root/pg['name'];page=json.loads(path.read_text());event=next(e for e in page['events'] if e.get('causal') is not None);event['causal']['parent_call_ref']=event['causal']['call_ref'];body=p.encode(page);path.write_bytes(body);pg.update(bytes=len(body),sha256=c.sha(body));side['pages_bytes']=len(body)
                self.err('CAUSAL_LINK_AMBIGUOUS',p.validate_pages,c.Reader(base),'packet',side,profile=profile)
            else:
                verified=p.validate_pages(c.Reader(base),'packet',side,profile=profile);self.assertEqual(verified['status'],'PAGE_BINDINGS_VERIFIED');self.assertEqual(len(side['retained_oracles']),1);self.assertEqual(len(next(iter(side['domain_witness_groups'].values()))['witnesses']),2);self.observations.append(dict(full_synthetic_recorder=True,pages_verified=verified,independent_calls=1,original_return_identity=True))
    def direct_recorder(self):
        with owned() as (base,root,owner):
            tid=self.reg['parental_contract']['direct_selector']['test_id'];r=self.recorder(owner,tid);r.causal_inventory[tid]=dict(family='DRIVE',classification='CAUSAL_DOMAIN');r.snapshot_ids=set();r.bind_direct=lambda:r.causal.bind(Direct,SyntheticLab,synthetic_child)
            def run_direct(test):
                test.lab=SyntheticLab();test.lab.run_id=RID;expected=SyntheticDrive().snapshot();ctx=p.multiprocessing.context.SpawnContext();a,b=ctx.Pipe();proc=ctx.Process(target=synthetic_child,args=(None,RID,None,b))
                try:
                    proc.start();b.close();test.assertTrue(a.poll(10));test.assertEqual(expected,a.recv());proc.join(10);test.assertEqual(proc.exitcode,0)
                finally:
                    if proc.is_alive():proc.terminate();proc.join(5)
                    a.close();b.close();CHILDREN.append(dict(exitcode=proc.exitcode,role='OWN_NEW_SYNTHETIC_DI07_PRODUCER'));proc.close()
            Direct=type('Direct',(unittest.TestCase,),dict(__module__='dw_direct',runTest=run_direct,id=lambda self:tid))
            original_recv=p.multiprocessing.connection._ConnectionBase.recv;original_join=p.multiprocessing.process.BaseProcess.join
            def recv(obj):
                value=original_recv(obj);r.attempt(r.causal.message,obj,value);return value
            def join(obj,*args,**kwargs):
                value=original_join(obj,*args,**kwargs);r.attempt(r.causal.exit,obj,direct=True);return value
            r.install();r.wrap_return(SyntheticDrive,'snapshot');r.install_direct()
            try:
                with patch.object(p.multiprocessing.connection._ConnectionBase,'recv',recv),patch.object(p.multiprocessing.process.BaseProcess,'join',join):result=unittest.TestResult();Direct().run(result)
            finally:r.restore()
            side=r.finish();self.assertTrue(result.wasSuccessful());self.assertEqual(r.errors,[],side);self.assertEqual(side['status'],'TRACE_CAPTURED_PENDING_SUFFICIENCY_REVIEW');self.assertEqual(len(side['parental_registrations']),1);verified=p.validate_pages(c.Reader(base),'packet',side,profile=r.profile);self.assertEqual(verified['status'],'PAGE_BINDINGS_VERIFIED');self.observations.append(dict(DI07_style='NEW_SYNTHETIC_ONLY',pages_verified=verified))
