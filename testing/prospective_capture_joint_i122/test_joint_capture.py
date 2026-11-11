# SPDX-License-Identifier: GPL-3.0-only
"""Ten future synthetic atomicity components. Written, AST-inspected, NOT RUN."""
import threading
import unittest
from unittest.mock import patch
from . import capture as p
from .atomic import clone_metadata


class Owner:
    def __init__(self):self.calls=[];self.check=None;self.fail=False
    def create(self,name):
        if self.check:self.check()
        self.calls.append(name)
        if self.fail:raise OSError('synthetic write failure')
        return 99


class Reader:
    def read(self,name):raise AssertionError('no source read expected in kernel fixture')


def fixture():
    owner=Owner();bindings=p.LateBindings([dict(id='builtins.dict')],Reader())
    rec=p.Recorder(dict(id='P01'),owner,profile=dict(inventory=[],projection_schemas={},parental_contract={}),bindings=bindings)
    return rec,owner


class R2CandidateTests(unittest.TestCase):
    def test_01_quota_rejection_keeps_live_metadata(self):
        r,_=fixture();old=r.parent_snapshots;used=r.references
        def phase(s):s.parent_snapshots.append(dict(synthetic=True));s.reference(s.limits['refs'])
        with self.assertRaises(p.c.CaptureFault):r._atomic(phase)
        self.assertIs(r.parent_snapshots,old);self.assertEqual(r.parent_snapshots,[]);self.assertEqual(r.references,used)
    def test_02_frame_aliases_survive_commit(self):
        r,_=fixture();frame={};r.frames=[frame];r.active=frame;r._causal_data.frame=frame
        r._atomic(lambda s:s.active.update(synthetic=1))
        self.assertIs(r.frames[0],r.active);self.assertIs(r.active,r._causal_data.frame)
        self.assertEqual(frame,{});self.assertEqual(r.active,dict(synthetic=1))
    def test_03_original_guards_remain_opaque(self):
        r,_=fixture();original=dict(synthetic=1);values=[original]
        r.record_refs=[({},original)];r.record_baselines={('m','f'):(values,0,None)}
        r._causal_data.oracle_guards=[(original,{})];r.causal_sources={'m':(None,values,{})}
        self.assertIs(r._atomic(lambda s:s.record_refs[0][1]),original)
        self.assertIs(r.record_refs[0][1],original);self.assertIs(r.record_baselines[('m','f')][0],values)
    def test_04_no_copy_hooks_or_identity_merging(self):
        class Original:
            def __deepcopy__(self,memo):raise AssertionError('copy hook forbidden')
        a=Original();b=Original();row={'left':a,'right':b};same=[];row.update(x=same,y=same)
        out=clone_metadata(row,{},set())
        self.assertIs(out['left'],a);self.assertIs(out['right'],b);self.assertIs(out['x'],out['y']);self.assertIsNot(out['x'],same)
    def test_05_nested_reservations_share_the_same_budget(self):
        r,_=fixture();used=r.references
        def phase(s):s.reference(s.limits['refs']-used);s.reference()
        with self.assertRaises(p.c.CaptureFault):r._atomic(phase)
        self.assertEqual(r.references,used)
        # Both threads enter outside the lock; no barrier/wait is inside a phase.
        r,_=fixture();r.references=r.limits['refs']-1;gate=threading.Barrier(2);results=[]
        def actor():
            gate.wait()
            try:r._atomic(lambda s:s.reference());results.append('COMMIT')
            except p.c.CaptureFault:results.append('REJECT')
        threads=[threading.Thread(target=actor) for _ in range(2)]
        for t in threads:t.start()
        for t in threads:t.join(5);self.assertFalse(t.is_alive())
        self.assertEqual(sorted(results),['COMMIT','REJECT']);self.assertEqual(r.references,r.limits['refs'])
    def test_06_swallowed_validation_error_rejects_whole_draft(self):
        r,_=fixture();old=r.parent_outcomes
        def phase(s):s.parent_outcomes.append('draft');s.invalid('CAUSAL_FIELD_BUDGET')
        with self.assertRaises(p.c.CaptureFault):r._atomic(phase)
        self.assertIs(r.parent_outcomes,old);self.assertEqual(old,[])
        self.assertEqual(r.errors[0],'CAUSAL_FIELD_BUDGET')
    def test_07_page_io_occurs_after_unlock(self):
        r,owner=fixture();owner.check=lambda:self.assertFalse(r._state_lock._is_owned())
        def phase(s):s.events._writes.append(('event-0001.json',b'{}'))
        with patch.object(p,'write_all',side_effect=lambda fd,body:owner.check()),patch.object(p.os,'close'):
            r._atomic(phase)
        self.assertEqual(owner.calls,['event-0001.json']);self.assertEqual(r._pending_io,0)
    def test_08_io_failure_poisons_future_publication(self):
        r,owner=fixture();owner.fail=True
        with self.assertRaises(OSError):r._atomic(lambda s:s.events._writes.append(('event-0001.json',b'{}')))
        self.assertTrue(r._failed);self.assertEqual(r._pending_io,0)
        with self.assertRaises(p.c.CaptureFault):r._atomic(lambda s:s.reference())
    def test_09_original_return_and_exception_are_preserved(self):
        r,_=fixture();marker=object();calls=[]
        class Subject:
            def snapshot(self):calls.append(1);return marker
        r.wrap_return(Subject,'snapshot');r.invalid('REFERENCE_BUDGET')
        try:self.assertIs(Subject().snapshot(),marker);self.assertEqual(calls,[1])
        finally:r.restore()
        r,_=fixture();error=ValueError('synthetic');calls=[]
        class Failed:
            def snapshot(self):calls.append(1);raise error
        r.wrap_return(Failed,'snapshot')
        try:
            with self.assertRaises(ValueError) as caught:Failed().snapshot()
            self.assertIs(caught.exception,error);self.assertEqual(calls,[1])
        finally:r.restore()
    def test_10_finalize_preflight_creates_no_page_on_rejection(self):
        r,owner=fixture();r.references=r.limits['refs']
        r.events.chunks=[b'{}'];r.events.chunk_bytes=2;r.events.count=1
        with self.assertRaises(p.c.CaptureFault):r._atomic(lambda s:s.events.close(),seal=True)
        self.assertFalse(r.events.closed);self.assertEqual(r.events.manifest,[])
        self.assertEqual(r.events.chunks,[b'{}']);self.assertEqual(owner.calls,[])
