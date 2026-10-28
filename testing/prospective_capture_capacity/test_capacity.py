# SPDX-License-Identifier: GPL-3.0-only
"""CB01-CB32: newly authored synthetic planner tests; no historical imports."""
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
from testing.prospective_capture_capacity import capacity as p
ROOT=p.ROOT;ROOTS=[];THREADS=[]

@contextlib.contextmanager
def owned():
    row=dict(ownership_verified=False,removed=False,sibling_preserved=False);ROOTS.append(row)
    with tempfile.TemporaryDirectory(prefix='i95-own-') as tmp:
        base=Path(tmp);root=base/'owned';root.mkdir();(root/'OWNER').write_text('I95_SYNTHETIC_OWNER');sibling=base/'sibling';sibling.write_bytes(b'I95_CONTROL')
        try:yield base,root
        finally:
            row['ownership_verified']=(root/'OWNER').read_text()=='I95_SYNTHETIC_OWNER';row['sibling_preserved']=sibling.read_bytes()==b'I95_CONTROL'
    row['removed']=not base.exists()

def forbidden():return sorted(n for n in sys.modules if n.startswith(('source_ingest','testing.D5','testing.prospective_capture.','testing.prospective_capture_')) and not n.startswith('testing.prospective_capture_capacity'))

def limits(**changes):
    out=dict(p.DEFAULT_LIMITS)
    for k,v in changes.items():assert k in out and type(v) is int and 0<=v<=out[k];out[k]=v
    return out

def base_files():return {'OWNER':36,'runner-raw.json':10,'sidecar.json':10,'context.json':10,'launch.json':10}
def model():return dict(scope='SYNTHETIC_MODEL',source_pins={'synthetic.py':'a'*64},inventory=['synthetic.Test.one','synthetic.Test.two'],charging_sites={'active.base':2,'active.child':1},unresolved=[])
def certificate(expected=None):
    e=model() if expected is None else expected
    return dict(schema=p.SCHEMA,source_pins=e['source_pins'],inventory_sha256=p.sha(p.encode(e['inventory'])),charging_sites=e['charging_sites'],multiplicity_bounds={'active.base':3,'active.child':2},proposed_numeric_limits=limits(),joint_resource_envelope=dict(refs=8,events_per_test=[1,1],events=2,files=base_files(),reads=[('synthetic/file',8),('synthetic/file',8)],operand_original=8,operand_auxiliary=8),unresolved=[],review_decision=dict(basis='PINNED_SOURCE_ENVELOPE',status='PLANNING_MODEL_ONLY'))

def exact_row(n):
    overhead=len(p.encode({'padding':''}));assert n>=overhead;return {'padding':'x'*(n-overhead)}

class CapacityTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):cls.manifest=p.read_manifest(p.Reader(ROOT,p.DEFAULT_LIMITS));cls.design=json.loads((ROOT/p.DESIGN).read_text())
    def setUp(self):self.observations=[]
    def check(self,value,label):self.assertTrue(value);self.observations.append(dict(check=label,status='PASS'))
    def err(self,code,fn,*args,**kwargs):
        with self.assertRaises(p.Fault) as raised:fn(*args,**kwargs)
        self.assertEqual(raised.exception.code,code);self.observations.append(dict(expected=code,observed=raised.exception.code))
    def test_CB01(self):
        for seal in ('D5-I86-integrity.json','D5-I89-integrity.json','D5-I92-integrity.json','D5-I93-integrity.json','D5-I94-integrity.json'):
            for n,h in json.loads((ROOT/'docs/validation'/seal).read_text())['artifacts'].items():self.assertEqual(p.sha((ROOT/n).read_bytes()),h)
        with owned() as (base,root):
            (root/'source').write_bytes(b'PINNED');r=p.Reader(base,limits());r.read('owned/source');(root/'source').write_bytes(b'CHANGED');self.err('STALE_INPUTS',r.finish)
        self.check(not self.design['implementation_authorized'],'historical I94 flags preserved; user I95 approval separate')
    def test_CB02(self):
        self.assertEqual(self.manifest['limits'],limits())
        for mode in ('missing','extra','renamed','hash'):
            with owned() as (base,root):
                source=ROOT/p.MANIFEST;dst=base/p.MANIFEST;dst.parent.mkdir(parents=True);m=copy.deepcopy(self.manifest)
                if mode=='missing':del m['limits']['refs']
                elif mode=='extra':m['limits']['other_refs']=1
                elif mode=='renamed':m['limits']['ref_limit']=m['limits'].pop('refs')
                else:m['contract_sha256']='0'*64
                dst.write_bytes(p.encode(m));contract=base/p.DESIGN;contract.write_bytes((ROOT/p.DESIGN).read_bytes());self.err('STALE_INPUTS' if mode=='hash' else 'STALE_AUTHORITY',p.read_manifest,p.Reader(base,limits()))
    def test_CB03(self):
        g=p.AtomicGuard(limits());g.commit(16383,{'rows':{'before':{'value':1}}});g.commit(1,{'rows':{'last':{'value':2}}});self.assertEqual(g.snapshot()['used'],16384);self.assertEqual(len(g.snapshot()['tables']['rows']),2);self.check(True,'exact16384 committed once without cap revision')
    def test_CB04(self):
        g=p.AtomicGuard(limits());g.commit(16384,{'rows':{'last':{'value':1}}});before=g.snapshot();self.err('REFERENCE_BUDGET',g.commit,1,{'rows':{'over':{'value':2}}});self.assertEqual(g.snapshot(),before)
    def test_CB05(self):
        g=p.AtomicGuard(limits(refs=5));g.commit(3,{'rows':{'initial':{}}});before=g.snapshot();self.err('REFERENCE_BUDGET',g.commit,1+len(['a','b']),{'rows':{'new':{'witness_refs':['a','b']}}});self.assertEqual(g.snapshot(),before);self.err('CAUSAL_FIELD_BUDGET',g.commit,1,{'rows':{'new':exact_row(4097)}});self.assertEqual(g.snapshot(),before)
    def test_CB06(self):
        class Hostile:
            def __int__(self):raise AssertionError('MUST_NOT_RUN')
        g=p.AtomicGuard(limits());before=g.snapshot()
        for n in (True,1.0,'1',-1,1<<64,Hostile()):self.err('REFERENCE_BUDGET',g.commit,n,{'rows':{'x':{}}});self.assertEqual(g.snapshot(),before)
        g.commit(0,{});self.assertEqual(g.snapshot(),before)
    def test_CB07(self):
        g=p.AtomicGuard(limits(refs=64));barrier=threading.Barrier(8);accepted=[];rejected=[];errors=[];lock=threading.Lock()
        def run(worker):
            try:
                barrier.wait(5)
                for j in range(16):
                    try:g.commit(1,{'rows':{f'{worker}-{j}':{}}});target=accepted
                    except p.Fault as ex:
                        if ex.code!='REFERENCE_BUDGET':raise
                        target=rejected
                    with lock:target.append((worker,j))
            except BaseException as ex:
                with lock:errors.append(type(ex).__name__)
        threads=[threading.Thread(target=run,args=(i,),name='I95_SYNTHETIC') for i in range(8)]
        for t in threads:t.start()
        for t in threads:t.join(10)
        THREADS.extend(dict(name=t.name,alive=t.is_alive()) for t in threads);self.assertFalse(errors);self.assertFalse(any(t.is_alive() for t in threads));self.assertEqual(len(accepted),64);self.assertEqual(len(rejected),64);self.assertEqual(g.snapshot()['used'],64);self.assertEqual(len(g.snapshot()['tables']['rows']),64)
        self.check(True,'8 own threads;64 successful unique reservations,64 rejects; one global committed ledger')
    def test_CB08(self):
        g=p.AtomicGuard(limits(refs=3))
        for i in range(3):g.commit(1,{f'table{i}':{f'row{i}':dict(frame=i,page=i,thread=i)}})
        before=g.snapshot();self.err('REFERENCE_BUDGET',g.commit,1,{'different':{'other':dict(frame=100,page=100,thread=100)}});self.assertEqual(g.snapshot(),before)
    def test_CB09(self):
        classes={'Base':dict(base=None,methods={'link':'base.link','owner':'base.owner'}),'Child':dict(base='Base',methods={'link':'child.link'}),'Top':dict(base='Child',methods={'retain':'top.retain'})};resolved=p.resolve_methods(classes,'Top');self.assertEqual(resolved,{'link':'child.link','owner':'base.owner','retain':'top.retain'});self.assertNotIn('base.link',resolved.values());classes['Base']['base']='Top';self.err('STALE_INPUTS',p.resolve_methods,classes,'Top')
    def test_CB10(self):
        self.assertEqual(p.evaluate(None,model(),limits())['status'],'NOT_ESTABLISHED');c=certificate();c['multiplicity_bounds']['active.child']=None;result=p.evaluate(c,model(),limits());self.assertEqual(result['status'],'NOT_ESTABLISHED');self.assertFalse(result['functional_release_authorized'])
        original=dict(model(),scope='ORIGINAL_P01',unresolved=['ORIGINAL_SOURCE_MULTIPLICITIES']);self.assertEqual(p.evaluate(c,original,limits())['status'],'NOT_ESTABLISHED')
    def test_CB11(self):
        for field,value in [('source_pins',{'synthetic.py':'b'*64}),('inventory_sha256',p.sha(p.encode(['synthetic.Test.one']))),('charging_sites',{'other':1})]:
            c=certificate();c[field]=value;self.err('STALE_INPUTS',p.evaluate,c,model(),limits())
        self.check(forbidden()==[],'reject before any product/runner import; no subset or aggregate package')
    def test_CB12(self):
        c=certificate();c['review_decision']=dict(basis='I92_PREFIX_13_OF_321_TIMES_MULTIPLIER',status='PLANNING_MODEL_ONLY');self.err('STALE_AUTHORITY',p.evaluate,c,model(),limits());c=certificate();c['proposed_numeric_limits']['refs']=65536;self.err('STALE_AUTHORITY',p.evaluate,c,model(),limits())
    def test_CB13(self):
        account=p.EventAccounting(limits())
        for _ in range(2048):account.accept('synthetic.test',24)
        self.err('EVENT_TEST_BUDGET',account.accept,'synthetic.test',24);self.assertEqual(account.count,2048)
        g=p.AtomicGuard(limits(events_test=2));g.commit(1,{'rows':{'a':{}}},{'test_id':'one'});g.commit(1,{'rows':{'b':{}}},{'test_id':'one'});before=g.snapshot();self.err('EVENT_TEST_BUDGET',g.commit,1,{'rows':{'c':{}}},{'test_id':'one'});self.assertEqual(g.snapshot(),before);self.assertEqual(len(before['events']),2)
    def test_CB14(self):
        account=p.EventAccounting(limits())
        for i in range(131072):account.accept(str(i//2048),24)
        self.err('EVENT_CAMPAIGN_BUDGET',account.accept,'new',24);self.assertEqual(account.count,131072);self.check(True,'131072 planning descriptors accepted,one over rejects; no functional event capture')
    def test_CB15(self):
        self.assertEqual(len(p.encode(p.checked_row(exact_row(4096),limits()))),4096);self.err('CAUSAL_FIELD_BUDGET',p.checked_row,exact_row(4097),limits());account=p.EventAccounting(limits());account.accept('one',4096);self.err('EVENT_SIZE_BUDGET',account.accept,'one',4097)
        row={'padding':'é'*2000};self.assertEqual(len(p.encode(row)),4014);self.assertEqual(p.checked_row(row,limits()),row);self.err('CAUSAL_FIELD_BUDGET',p.checked_row,{'padding':'é'*2042},limits())
    def test_CB16(self):
        planner=p.PagePlanner(limits());event=exact_row(4096)
        while planner.length(planner.current_count+1,planner.current_bytes+4096)<=2097152:planner.append(event)
        remaining=2097152-planner.length(planner.current_count+1,planner.current_bytes)
        self.assertGreaterEqual(remaining,14);planner.append(exact_row(remaining));self.assertEqual(planner.sizes(),[2097152]);planner.append({'last':True});self.assertEqual(len(planner.sizes()),2)
        self.assertEqual(p.page_sizes([2097152]*32,limits()),67108864);self.err('PAGE_COUNT_BUDGET',p.page_sizes,[1]*33,limits());self.err('PAGE_BYTES_BUDGET',p.page_sizes,[2097153],limits());self.err('PAGES_TOTAL_BUDGET',p.page_sizes,[100,100],limits(event_pages_total_bytes=199));self.check(True,'actual encoded page plan exact2MiB includes header/commas;32-page total boundary is size-model only')
    def test_CB17(self):
        for name,code in [('runner-raw.json','RAW_BUDGET'),('sidecar.json','SIDECAR_BUDGET'),('context.json','CONTEXT_BUDGET'),('launch.json','CONTEXT_BUDGET')]:
            files=base_files();files[name]=12582912;p.bundle_sizes(files,limits());files[name]+=1;self.err(code,p.bundle_sizes,files,limits())
    def test_CB18(self):
        p.package_total(117444608,37,limits());self.err('PACKAGE_BUDGET',p.package_total,117444609,37,limits());self.err('PACKAGE_SET_MISMATCH',p.package_total,1,38,limits());files=base_files();files.update({f'event-{i:04}.json':2097152 for i in range(1,33)});files.update({k:12582912 for k in files if k!='OWNER' and not k.startswith('event-')});self.assertEqual(p.bundle_sizes(files,limits()),117440548);self.assertEqual(117444608-117440548,4060);files['extra']=1;self.err('PACKAGE_SET_MISMATCH',p.bundle_sizes,files,limits());self.check(True,'independent package counter cap tested;valid all-maxima bundle has4060-byte headroom,not falsely claimed at exact package cap')
    def test_CB19(self):
        a=p.ReadAccounting(limits())
        for i in range(8):a.charge(str(i),16777216)
        self.assertEqual(a.unique,134217728);a.charge('0',16777216)
        for _ in range(7):a.charge('1',16777216)
        self.assertEqual(a.total,268435456);self.err('READ_BUDGET',a.charge,'1',16777216);self.err('UNIQUE_BUDGET',a.charge,'extra',1)
        with owned() as (base,root):
            (root/'a').write_bytes(b'12345678');r=p.Reader(base,limits(input_read_bytes=16));r.read('owned/a');r.finish();self.assertEqual(r.accounting.total,16);self.err('READ_BUDGET',r.read,'owned/a')
    def test_CB20(self):
        files=base_files();files.update({f'event-{i:04}.json':2097152 for i in range(1,33)});files.update({k:12582912 for k in files if k!='OWNER' and not k.startswith('event-')});a=p.ReadAccounting(limits(),'evidence');reads=list(files.items());a.plan(reads);a.plan(reads);self.err('READ_BUDGET',a.plan,reads);self.check(a.total<=268435456,'three maximum scans rejected under one evidence Reader ledger')
    def test_CB21(self):
        p.check_operand(16777200,16,limits());self.err('OPERAND_BUDGET',p.check_operand,16777200,17,limits());self.err('OPERAND_BUDGET',p.check_operand,16777217,0,limits());self.check(True,'source plus auxiliaries charged regardless of compact output descriptor')
    def test_CB22(self):
        value=0
        for _ in range(32):value=[value]
        p.builtin(value,limits());self.err('OPERAND_DEPTH',p.builtin,[value],limits());p.builtin('x'*4096,limits());self.err('OPERAND_BUDGET',p.builtin,'x'*4097,limits());p.size(4096,limits()['frames'],'FRAME_BUDGET');self.err('FRAME_BUDGET',p.size,4097,limits()['frames'],'FRAME_BUDGET')
    def test_CB23(self):
        source='for i in range(2,10,2):\n pass\nfor j in (1,2,3):\n pass\n';bounds=p.loop_bounds(source);self.assertEqual([x['bound'] for x in bounds],[4,3]);self.assertTrue(all(not x['transitive_bound_proven'] for x in bounds));self.check(True,'AST only;local bounds not full call closure/runtime evidence')
    def test_CB24(self):
        self.assertTrue(all(x['bound'] is None for x in p.loop_bounds('for x in data:\n pass\nwhile ready():\n pass\n')));self.assertIsNone(p.graph_bound('f',{'f':dict(local=1,calls=[('f',1)])}));self.assertIsNone(p.graph_bound('f',{'f':dict(local=1,calls=[('external',1)])}));self.assertIsNone(p.graph_bound('f',{'f':dict(local=None,calls=[])}));self.assertEqual(p.graph_bound('f',{'f':dict(local=2,calls=[('g',3)]),'g':dict(local=4,calls=[])}),14)
    def test_CB25(self):
        group=dict(context=dict(capture='c',frame='f',subcase='s',thread='t'),identity=dict(run='r',store='s',role='REMOTE'),witnesses=[dict(object_ref='O1',authorities=['CONSTRUCTION_NOT_HEAD']),dict(object_ref='O2',authorities=['OBSERVED_RETURN'])]);retained=p.validate_witness_group(group);self.assertEqual(retained,group);self.assertEqual(len(retained['witnesses']),2);self.assertIsNot(retained,group);forged=copy.deepcopy(group);forged['witnesses'].append(forged['witnesses'][0]);self.err('STALE_INPUTS',p.validate_witness_group,forged);self.check(True,'synthetic preservation model only;no physical-state identity or runtime domain validation claim')
    def test_CB26(self):
        additions={'rows':{'r':{'left_ref':'SAME','right_ref':'SAME'}}};self.assertEqual(p.reference_cost(additions),3);g=p.AtomicGuard(limits());self.err('REFERENCE_BUDGET',g.commit,2,additions);g.commit(3,additions);self.assertEqual(g.snapshot()['used'],3);self.assertEqual(g.snapshot()['tables']['rows']['r'],additions['rows']['r'])
    def test_CB27(self):
        g=p.AtomicGuard(limits(refs=1));calls=[];value={}
        def original():calls.append(1);return value
        def observe(out):self.assertIs(out,value);g.commit(0,{});return 2,{'rows':{'x':{}}},None
        self.assertIs(g.invoke(original,observe=observe),value);self.assertEqual(calls,[1]);self.assertTrue(g.should_stop);self.assertEqual(g.snapshot()['used'],0)
        error=ValueError('SYNTHETIC_ORIGINAL')
        def raising():calls.append(2);raise error
        with self.assertRaises(ValueError) as raised:g.invoke(raising)
        self.assertIs(raised.exception,error);self.assertEqual(calls,[1,2]);self.check(True,'original callable and observer both outside lock;identity preserved,latched,caller must stop between synthetic tests')
    def test_CB28(self):
        d=p.Diagnostic();d.at('TARGETS');d.fail('REFERENCE_BUDGET');d.at('FINALIZE');d.fail('RAW_BUDGET');self.assertEqual(d.value()['phase'],'TARGETS');self.assertEqual(d.value()['code'],'REFERENCE_BUDGET');self.assertLessEqual(len(p.encode(d.value())),4096);self.assertNotIn('traceback',d.value());d=p.Diagnostic();d.fail('UNRECOGNIZED_FREE_TEXT');self.assertEqual(d.value()['code'],'SANITIZED_WORKER_ERROR')
    def test_CB29(self):
        with owned() as (base,root):
            fd=os.open(root/'partial',os.O_WRONLY|os.O_CREAT|os.O_EXCL,0o600);w=p.OneShot(fd);d=p.Diagnostic();d.fail('REFERENCE_BUDGET')
            def partial(fd,body):os.write(fd,body[:12]);raise OSError('SYNTHETIC')
            try:
                with patch.object(p,'write_all',side_effect=partial):
                    with self.assertRaises(OSError):w.failure(d)
                self.assertFalse(w.failure(d));self.assertEqual((root/'partial').stat().st_size,12)
            finally:os.close(fd)
    def test_CB30(self):
        with owned() as (base,root):
            owner=types.ModuleType('i95_synthetic');g=p.AtomicGuard(limits())
            def original():return 'ORIGINAL'
            def wrapper():return 'WRAPPED'
            owner.method=wrapper;owner.method=lambda:'CHANGED';p.restore_binding(owner,'method',original,wrapper,g);self.assertIs(owner.method,original);self.assertIn('OBSERVER_IDENTITY_CHANGED',g.errors);self.assertEqual(g.diagnostic.value()['code'],'SANITIZED_WORKER_ERROR');self.assertEqual(owner.method(),'ORIGINAL')
        self.check(ROOTS[-1]['removed'] and ROOTS[-1]['ownership_verified'] and ROOTS[-1]['sibling_preserved'],'own root removed;OWNER and sibling verified')
    def test_CB31(self):
        result=p.evaluate(certificate(),model(),limits());self.assertEqual(result['status'],'CAPACITY_ESTABLISHED_SYNTHETIC_MODEL_ONLY');missing=['PENDING_CHILD_EXIT','ORACLE_VALUE_MISSING','REMOTE_RESULT_WITHOUT_STORE_RECEIPT','NULL_POLICY_REQUIRED'];gate=p.evidence_gate(result,missing);self.assertEqual(gate['missing'],missing);self.assertEqual(gate['evidence_status'],'MISSING_REQUIRED_EVIDENCE');self.assertFalse(gate['functional_release_authorized']);self.assertFalse(gate['closure'])
    def test_CB32(self):
        self.assertEqual(forbidden(),[]);self.assertEqual(limits()['refs'],16384);self.assertFalse(self.manifest['functional_execution_authorized']);self.assertFalse(hasattr(p,'launch'));self.assertFalse(hasattr(p,'worker'))
        for n in ('docs/validation/D5-I96-capture-authorization.json','docs/validation/D5-I96-P01','docs/validation/D5-I96-P01-launch.json'):self.assertFalse((ROOT/n).exists())
        self.check(True,'component only;original certificate unresolved,IR03/publication/global acceptance pending')
