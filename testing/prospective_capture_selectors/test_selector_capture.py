# SPDX-License-Identifier: GPL-3.0-only
"""NS12: new synthetic inputs only; no historical tests or product imports."""
import contextlib
import copy
import json
import os
from pathlib import Path
import sys
import tempfile
import types
import unittest
from unittest.mock import patch
from testing.prospective_capture_selectors import capture as p,worker as w
c=p.c;ROOT=p.ROOT;ROOTS=[];CHILDREN=[]
RID='11111111-1111-4111-8111-111111111111';SID='22222222-2222-4222-8222-222222222222';CID='33333333-3333-4333-8333-333333333333';OTHER='44444444-4444-4444-8444-444444444444';HEX='a'*64

class SyntheticError(ValueError):pass

def proof(family='T',tick=None):return dict(schema=p.PROOF_SCHEMAS[family],run_id=RID,store_id=SID,ticket=CID,request_hash=HEX,creation_key=HEX,manifest_hash=HEX,status='EFFECT_CONFIRMED',remote_id=OTHER,applied_version=1,payload_hash='d'*64,retry_tick=tick,code='CONFIRMED')
def request():return dict(cid=CID,kind='EXECUTE',args={'ticket':CID},expected=None)
def receipt(family='T'):return dict(schema='d5.durable-receipt.v1',command_id=CID,request_sha256=p.store_request(request())['request_sha256'],before_seq=0,seq=1,before_state_sha256='b'*64,after_data_sha256='c'*64,historical=False,grants_execution_authority=False,quota_consumed=0,reservations_created=0,activation_allowed=False,result=proof(family))
def returned(family='T'):
    rec=receipt(family);return dict(head=dict(run_id=RID,store_id=SID,role='REMOTE',seq=1,commit_sha256=HEX),state={'receipts':{CID:rec}},chain=[dict(seq=1,command_id=CID,request_sha256=rec['request_sha256'],operation={k:request()[k] for k in ('kind','args','expected')},receipt={k:v for k,v in rec.items() if k!='historical'})])
def oracle(family='T'):
    row=dict(case='NS_SYNTHETIC',role='REMOTE',store_id=SID,seq=1,state_sha256=p.canonical_hash(returned(family)['state']),receipts=1)
    if family=='T':row.update(commit_sha256=HEX,tasks=0)
    else:row.update(head_sha256=HEX,entities=0,relations=0)
    return row

def context(family='T',**changes):return dict(p.selector_context('STORE',family,'REMOTE',RID,SID,'EXECUTE'),**{})|changes

class SyntheticStore:
    def __init__(self,path,run_id,store_id,role,reducer,genesis,*,hook=None):self.family=reducer;self.calls=0;self.last_return=None
    def snapshot(self):return returned(self.family)
    def transact(self,cid,kind,args,expected=None):self.calls+=1;self.last_return=receipt(self.family);return self.last_return

@contextlib.contextmanager
def owned():
    row=dict(ownership_verified=False,removed=False,sibling_preserved=False);ROOTS.append(row)
    with tempfile.TemporaryDirectory(prefix='i91-own-') as tmp:
        base=Path(tmp);root=base/'packet';root.mkdir();owner=c.OwnedRoot(root);sibling=base/'sibling';sibling.write_bytes(b'I91_SYNTHETIC')
        try:yield base,root,owner
        finally:owner.verify();row.update(ownership_verified=True,sibling_preserved=sibling.read_bytes()==b'I91_SYNTHETIC')
    row['removed']=not base.exists()

def forbidden():
    prefixes=('source_ingest','testing.D5','testing.durable_','testing.evidence_')
    suffixes=('.test_domain_capture','.run_domain_lab','.test_parental_capture','.run_parental_lab','.test_causal_capture','.run_causal_lab','.test_late_capture','.run_late_lab','.test_typed_capture','.run_typed_lab','.test_paged_capture','.run_paged_lab','.test_prospective_capture','.run_capture_lab')
    return sorted(n for n in sys.modules if n.startswith(prefixes) or n.endswith(suffixes))

class SelectorTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):cls.reg=p.read_registry();cls.spec=cls.reg['projection_schemas'];cls.meta=cls.spec['metadata_selectors'];cls.design=cls.reg['selector_contract']
    def setUp(self):self.observations=[]
    def check(self,value,label):self.assertTrue(value);self.observations.append(dict(check=label,status='PASS'))
    def err(self,code,fn,*args,**kwargs):
        with self.assertRaises(c.CaptureFault) as raised:fn(*args,**kwargs)
        self.assertEqual(raised.exception.code,code);self.observations.append(dict(expected=code,observed=raised.exception.code))
    def recorder(self,owner,tid='ns_synthetic.Run.test_one',sources=None,family='T'):
        entry=dict(id='SYNTHETIC_ONLY',expected_test_ids=[tid],expected_groups={'ns_synthetic':1},group_policies={'ns_synthetic':dict(domain_required=False,no_store_reason='SYNTHETIC_ONLY')},record_sources=sources or [],method_bindings={tid:dict(status='SOURCE_DERIVED_EXPECTATION',scope='SYNTHETIC_COMPONENT_ONLY')})
        reg=copy.deepcopy(self.reg);reg['snapshot_scopes']=[];reg['operand_scopes']=[];reg['inventory'].append(dict(test_id=tid,family=family,classification='CAUSAL_DOMAIN'))
        return p.Recorder(entry,owner,profile=reg,bindings=p.LateBindings([dict(id='builtins.dict',source=None)],c.Reader(ROOT)))
    def full_recorder(self,family,attack=False):
        with owned() as (base,root,owner):
            module=types.ModuleType('ns_synthetic_oracle');module.ORACLES=[];module.CURRENT_CASE='NS_SYNTHETIC';original_return=returned(family);calls=[]
            def independent(path):calls.append(path);module.ORACLES.append(oracle(family));return original_return
            module.independent=independent;tid='ns_synthetic.Run.test_one';r=self.recorder(owner,tid,[dict(module=module.__name__,field='ORACLES',raw_pointer=None)],family)
            def run_one(test):
                store=SyntheticStore(None,RID,SID,'REMOTE',family,None);store.snapshot();test.assertIs(store.transact(**request()),store.last_return);test.assertEqual(store.calls,1);test.assertIs(module.independent('NO_DOMAIN_IO'),original_return)
            Run=type('Run',(unittest.TestCase,),dict(__module__='ns_synthetic',test_one=run_one));originals=[SyntheticStore.__init__,SyntheticStore.snapshot,SyntheticStore.transact]
            with patch.dict(sys.modules,{module.__name__:module}):
                try:
                    r.install();r.constructor(SyntheticStore);r.wrap_return(SyntheticStore,'snapshot');r.wrap_boundary(SyntheticStore,'transact','Store.transact');r.wrap_boundary(module,'independent',family+'.independent');result=unittest.TestResult();Run('test_one').run(result)
                finally:r.restore()
                side=r.finish()
            self.assertTrue(result.wasSuccessful(),result.errors);self.assertEqual(r.errors,[],side);self.assertEqual(side['status'],'TRACE_CAPTURED_PENDING_SUFFICIENCY_REVIEW');self.assertEqual(calls,['NO_DOMAIN_IO']);self.assertEqual(originals,[SyntheticStore.__init__,SyntheticStore.snapshot,SyntheticStore.transact])
            verified=p.validate_pages(c.Reader(base),'packet',side,profile=r.profile);self.assertEqual(verified['status'],'PAGE_BINDINGS_VERIFIED');self.assertEqual(len(side['retained_oracles']),1);self.assertTrue(any(l['relation']=='COMMAND_RECEIPT_ORACLE_COMMIT' for l in side['causal_links'].values()))
            if attack:
                side['domain_witness_groups'][next(iter(side['domain_witness_groups']))]['role']='CLIENT';self.err('ORACLE_DOMAIN_IDENTITY_MISSING',p.validate_causal,side,r.profile)
            self.observations.append(dict(full_synthetic_recorder=True,family=family,reader=verified,original_return_identity=True,independent_calls=1,command_link_verified=True))
    def test_NS01(self):
        self.err('COMMAND_HEADER_INVALID',p.legacy_selectors,proof(),self.meta)
        for seal in ('D5-I88-integrity.json','D5-I89-integrity.json','D5-I90-integrity.json'):
            for n,h in json.loads((ROOT/'docs/validation'/seal).read_text())['artifacts'].items():self.assertEqual(c.sha((ROOT/n).read_bytes()),h)
        self.check(not self.design['implementation_authorized'],'historical I90 proposal unchanged; user approval recorded in I91')
    def test_NS02(self):
        for operation in ('EXECUTE','CLOSE'):
            raw=receipt();projected=p.store_receipt(raw,self.spec,context=context(operation=operation));self.assertIsNone(projected['result_metadata']['retry_tick']);self.assertEqual(projected['metadata_policy_ref'],p.NP01);self.assertEqual(projected['result_digest'],p.bounded_builtin(raw['result']));self.assertEqual(raw,receipt());p.validate_receipt_metadata(projected,self.spec,context(operation=operation))
        self.full_recorder('T')
    def test_NS03(self):
        selected,policy=p.scoped_selectors(proof('R'),self.meta,context('R'));self.assertEqual(policy,p.NP02);self.assertIsNone(selected['retry_tick']);self.err('COMMAND_HEADER_INVALID',p.scoped_selectors,proof('R'),self.meta,context('T'));self.full_recorder('R')
    def test_NS04(self):
        for family in ('T','R'):
            for tick in (0,1023):self.assertEqual(p.scoped_selectors(proof(family,tick),self.meta,context(family))[0]['retry_tick'],tick)
            for tick in (True,1.0,'0',1024,-1):self.err('COMMAND_HEADER_INVALID',p.scoped_selectors,proof(family,tick),self.meta,context(family))
    def test_NS05(self):
        for mutate in ('missing','extra','unknown'):
            value=proof()
            if mutate=='missing':del value['retry_tick']
            elif mutate=='extra':value['extra']=0
            else:value['schema']='UNKNOWN'
            self.err('COMMAND_HEADER_INVALID',p.scoped_selectors,value,self.meta,context())
        out,policy=p.scoped_selectors({'ticket':CID},self.meta,context());self.assertEqual(out,{'ticket':CID});self.assertEqual(policy,p.NP00);self.assertNotIn('retry_tick',out);self.assertIn('retry_tick',p.scoped_selectors(proof(),self.meta,context())[0])
    def test_NS06(self):
        for field in ('seq','version','ledger_version'):self.err('COMMAND_HEADER_INVALID',p.scoped_selectors,{field:None},self.meta,context())
        value=proof();value['applied_version']=None;self.err('COMMAND_HEADER_INVALID',p.scoped_selectors,value,self.meta,context());value=p.store_receipt(receipt(),self.spec,context=context());value['seq']=None;self.err('COMMAND_HEADER_INVALID',p.validate_receipt_metadata,value,self.spec,context())
    def test_NS07(self):
        contexts=[None,context(role='CLIENT'),context(role='DRIVE'),context(operation='MUTATE'),context(family='DRIVE'),context(run_id=OTHER),context(store_id=OTHER),context(origin='PAYLOAD')]
        for ctx in contexts:self.err('COMMAND_HEADER_INVALID',p.scoped_selectors,proof(),self.meta,ctx)
    def test_NS08(self):
        value=p.store_receipt(receipt(),self.spec,context=context());self.assertEqual(value['command_id'],CID);self.assertEqual(value['request_sha256'],p.store_request(request())['request_sha256']);self.assertEqual(value['seq'],1);self.assertIs(value['grants_execution_authority'],False)
        for field,bad in (('command_id','BAD'),('quota_consumed',1),('reservations_created',True),('activation_allowed',True)):
            forged=copy.deepcopy(value);forged[field]=bad;self.err('COMMAND_HEADER_INVALID',p.validate_receipt_metadata,forged,self.spec,context())
        # The reader still binds actual command identity to its original request.
        row=dict(authority='OBSERVED_PARENT_RETURN',outcome='RETURN',exception=None,observer_id='Store.transact',request=p.store_request(request()),output=dict(value,command_id=OTHER));self.err('REQUEST_HASH_CONFLICT',p.validate_call_header,row,self.spec)
    def test_NS09(self):
        contract=self.reg['parental_contract'];events=[];errors=[]
        for family in ('T','R'):
            e=p.DomainState(RID,p.LIMITS,self.spec,lambda n=1:None,lambda *a,**k:events.append(k),errors.append,contract=contract);e.begin(dict(test_frame_id='F1',test_id='NS_SYNTHETIC'),self)
            ctx=p.multiprocessing.context.SpawnContext();a,b=ctx.Pipe();proc=ctx.Process()
            try:
                key=e.register(proc,a,dict(run_id=RID,client_id=OTHER,remote_id=SID),'remote',{'ticket':CID},family=family);self.assertTrue(e.message(a,('OK',proof(family))));row=e.tables['protocol_instances'][key];header=row['observed_messages'][0]['header'];self.assertIsNone(header['receipt']);self.assertIsNone(header['command_id']);self.assertEqual(header['command_id_authority'],'CHILD_LOCAL_NOT_OBSERVED');self.assertEqual(header['selector_policy_ref'],p.NP01 if family=='T' else p.NP02);self.assertIsNone(header['selectors']['retry_tick']);p.validate_protocol(key,row,{'parental_registrations':{}},self.reg,p.LIMITS)
            finally:a.close();b.close();proc.close()
        self.check(not errors,'registered synthetic CP07/CP13; no child started, command receipt or inferred UUID5')
    def test_NS10(self):
        meta=p.scoped_selectors(proof(),self.meta,context())[0]
        for policy,selected,ctx in [('FORGED',meta,context()),(p.NP01,meta,context(role='CLIENT')),(p.NP02,meta,context()),(p.NP01,dict(meta,extra=0),context()),(p.NP00,meta,None)]:self.err('COMMAND_HEADER_INVALID',p.validate_selector_metadata,selected,policy,self.meta,ctx)
        self.full_recorder('T',attack=True)
    def test_NS11(self):
        self.assertEqual(self.reg['limits'],json.loads((ROOT/p.DOMAIN_REGISTRY).read_text())['limits'])
        with owned() as (base,root,owner):
            r=self.recorder(owner);r.active=dict(test_id='ns_synthetic.Run.test_one',test_frame_id='F1',event_count=0,owner_context_refs=[]);r.frame_summary=dict(operands_missing=False,returns_missing=False);r.causal.begin(r.active,self)
            store=SyntheticStore(None,RID,SID,'REMOTE','T',None);original=SyntheticStore.transact;r.wrap_boundary(SyntheticStore,'transact','Store.transact')
            try:self.assertIs(store.transact(**request()),store.last_return);self.assertEqual(store.calls,1);self.assertIn('COMMAND_HEADER_INVALID',r.errors)
            finally:r.restore();r.events.close()
            self.assertIs(SyntheticStore.transact,original);module=types.ModuleType('ns_exception');error=SyntheticError('SYNTHETIC');calls=[]
            def raising(path):calls.append(path);raise error
            module.independent=raising;r.causal.stacks.clear();r.causal_exception_types={'ns.SyntheticError':SyntheticError};r.wrap_boundary(module,'independent','T.independent')
            try:
                with self.assertRaises(SyntheticError) as raised:module.independent('NO_IO')
                self.assertIs(raised.exception,error);self.assertEqual(calls,['NO_IO'])
            finally:r.restore()
            self.assertIs(module.independent,raising);ledger=p.Ledger(RID,pid=123);ledger.at('TARGETS');ledger.fail('COMMAND_HEADER_INVALID');ledger.at('FINALIZE');ledger.fail('STALE_INPUTS');self.assertEqual(ledger.value()['phase'],'TARGETS');self.assertEqual(ledger.value()['code'],'SANITIZED_WORKER_ERROR');fd=owner.create('partial');writer=p.SideWriter(fd,RID,pid=123)
            def partial(fd,body):os.write(fd,body[:12]);raise OSError('SYNTHETIC')
            try:
                with patch.object(p,'write_all',side_effect=partial):
                    with self.assertRaises(OSError):writer.failure(ledger)
                self.assertFalse(writer.failure(ledger));self.assertEqual((root/'partial').stat().st_size,12)
            finally:os.close(fd)
            (root/'input').write_bytes(b'12345678');reader=c.Reader(base,{'read_bytes':12});reader.read('packet/input');self.err('READ_BUDGET',reader.read,'packet/input')
        self.check(True,'identity, first diagnostic, partial write, restoration and owned cleanup verified')
    def test_NS12(self):
        plan=p.plan(registry=self.reg);self.assertEqual(plan['status'],'NOT_RUN_I92_AUTHORIZATION_REQUIRED');self.assertFalse(plan['closure']);self.assertEqual(w.main(['P01','3','4','5','6',RID]),2);self.assertEqual(forbidden(),[])
        for n in (p.AUTHORITY,p.DESTINATION,p.LAUNCH_COPY):self.assertFalse((ROOT/n).exists())
        self.check(True,'I92 functional, IR03 and publication remain separate decisions')
