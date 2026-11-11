# SPDX-License-Identifier: GPL-3.0-only
"""Ten future synthetic components. Written in I119; NOT RUN.

No product/runner imports, sockets, processes or functional test campaigns.
A future separately authorized component run may import the candidate only.
"""
import copy
import json
import sys
import threading
import unittest
from types import SimpleNamespace
from . import capture as p

UUID='00000000-0000-4000-8000-000000000001'
CTX=dict(capture_run_id=UUID,test_frame_id=UUID,subcase_ref='S1',thread_ref='T1')
IDENT=dict(run_id=UUID,store_id=UUID,role='CLIENT')


class Budget:
    def __init__(self):self._ref_lock=threading.RLock();self.used=0;self.limit=100000
    def charge(self,n=1):
        p.fault(type(n) is int and n>=0 and self.used+n<=self.limit,'REFERENCE_BUDGET');self.used+=n


class SyntheticState(p.DomainState):
    def __init__(self,budget):
        super().__init__(UUID,dict(p.LIMITS),{},budget.charge,lambda *a,**k:None,lambda *a:None,contract={})
        self.synthetic_objects=[]
    def context(self):return dict(CTX)
    def object_ref(self,obj):
        for old,key in self.synthetic_objects:
            if old is obj:return key
        key='O'+str(len(self.synthetic_objects)+1);self.synthetic_objects.append((obj,key));return key


def fixture(count=2):
    b=Budget();s=SyntheticState(b);objects=[object() for _ in range(count)]
    for obj in objects:s.declaration(obj,dict(IDENT),p.RETURN_AUTH)
    side={**s.tables};return b,s,objects,side


class R2CandidateTests(unittest.TestCase):
    def test_01_forty_physical_witnesses_fit_without_merging(self):
        b=Budget();s=SyntheticState(b);objects=[object() for _ in range(40)]
        for i,obj in enumerate(objects):
            if i<20:s.declaration(obj,dict(IDENT),p.CONSTRUCTION_AUTH)
            s.declaration(obj,dict(IDENT),p.RETURN_AUTH)
        self.assertEqual(len(s.tables['domain_witness_groups']),1)
        self.assertEqual(len(s.tables['domain_witness_records']),40)
        self.assertEqual(b.used,40*7+2+20)
        self.assertTrue(all(len(p.encode(row))<=4096 for table in s.tables.values() for row in table.values()))
    def test_02_new_authority_costs_one_and_keeps_same_record(self):
        b,s,objects,side=fixture(1);before=b.used
        key=next(iter(s.tables['domain_witness_records']))
        s.declaration(objects[0],dict(IDENT),p.CONSTRUCTION_AUTH)
        self.assertEqual(b.used,before+1)
        self.assertEqual(list(s.tables['domain_witness_records']),[key])
        self.assertEqual(len(s.tables['domain_witness_records'][key]['authorities']),2)
    def test_03_normalized_failure_does_not_publish_record_or_group(self):
        b,s,objects,side=fixture(1);before=copy.deepcopy(s.tables);counter=s.counter
        b.limit=b.used
        with self.assertRaises(p.c.CaptureFault):s.declaration(object(),dict(IDENT),p.RETURN_AUTH)
        self.assertEqual(s.tables,before);self.assertEqual(s.counter,counter)
        # This local test does not certify context/owner/other30-site atomicity.
    def test_04_orphan_record_is_rejected(self):
        b,s,objects,side=fixture();p.validate_normalized_ownership(side,p.LIMITS)
        key=next(iter(side['domain_witness_records']));side['domain_witness_records']['Y999']=dict(side['domain_witness_records'][key],witness_ref='Y999')
        with self.assertRaises(p.c.CaptureFault):p.validate_normalized_ownership(side,p.LIMITS)
    def test_05_duplicate_membership_is_rejected(self):
        b,s,objects,side=fixture();group=next(iter(side['domain_witness_groups'].values()))
        group['witness_record_refs'].append(group['witness_record_refs'][0])
        with self.assertRaises(p.c.CaptureFault):p.validate_normalized_ownership(side,p.LIMITS)
    def test_06_record_self_reference_must_match_key(self):
        b,s,objects,side=fixture();next(iter(side['domain_witness_records'].values()))['witness_ref']='Y999'
        with self.assertRaises(p.c.CaptureFault):p.validate_normalized_ownership(side,p.LIMITS)
    def test_07_causal_members_remain_physical_O_refs(self):
        b,s,objects,side=fixture();key=next(iter(side['domain_witness_groups']))
        self.assertEqual(s.witnesses(key),['O1','O2'])
        self.assertTrue(all(k.startswith('Y') for k in side['domain_witness_groups'][key]['witness_record_refs']))
    def test_08_draft_capacity_certificate_blocks_admission(self):
        required={p.REGISTRY,p.CONTRACT,p.CERTIFICATE,p.COMPONENT_MANIFEST,p.COMPONENT_RAW,p.COMPONENT_RESULT,p.COMPONENT_SEAL}
        bodies={p.REGISTRY:b'{}',p.CERTIFICATE:json.dumps(dict(schema='d5.joint-source-capacity-certificate.v2',status='DRAFT_NOT_ADMITTED')).encode()}
        view=SimpleNamespace(read=lambda name:bodies[name])
        approved=dict(capture_inputs={n:'f'*64 for n in required},registry_sha256=p.c.sha(b'{}'))
        plan=SimpleNamespace(approved=approved,view=view)
        with self.assertRaises(p.c.CaptureFault):p.require_admission(plan,dict(implementation_sources={},required_prior_inputs={}))
    def test_09_candidate_import_does_not_import_product_or_runner(self):
        self.assertFalse([n for n in sys.modules if n=='source_ingest' or n.startswith('source_ingest.') or n.startswith('testing.D5.')])
    def test_10_phase_bytes_are_explicit_and_finish_is_third_pass(self):
        payload=b'inert'
        authority=dict(schema='d5.joint-capture-authority.v2',phase='JOINT_EXPLICITLY_APPROVED',scopes=['P01'],registry_sha256='f'*64,capture_inputs={'proof.txt':p.c.sha(payload)})
        bodies={p.AUTHORITY:json.dumps(authority).encode(),'proof.txt':payload}
        class Reader:
            def __init__(self):self.files={};self.reads=[]
            def read(self,name):self.files[name]=True;self.reads.append(name);return bodies[name]
            def finish(self):
                for name in list(self.files):self.read(name)
        reader=Reader();plan=p.InputPlan(None,reader);plan.before()
        self.assertEqual(len(reader.reads),2)
        self.assertEqual(plan.view.read('proof.txt'),payload);self.assertEqual(plan.view.read('proof.txt'),payload)
        self.assertEqual(len(reader.reads),2)
        plan.after();plan.finish();self.assertEqual(len(reader.reads),6)
        self.assertEqual({n:reader.reads.count(n) for n in bodies},{n:3 for n in bodies})
