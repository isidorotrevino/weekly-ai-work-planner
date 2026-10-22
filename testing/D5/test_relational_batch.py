# SPDX-License-Identifier: GPL-3.0-only
"""I30 atomic in-memory batch scenarios; no SQL/provider or durable restart."""
import base64
from copy import deepcopy
import json
import threading
import unittest
import uuid
from unittest.mock import patch

from source_ingest import batch_fixture as bf

PROJECT = '00000000-0000-4000-8000-000000000001'
DOCUMENT = '00000000-0000-4000-8000-000000000002'
OTHER = '00000000-0000-4000-8000-000000000003'
THREADS = []


def uid(key):
    return str(uuid.uuid5(uuid.NAMESPACE_OID, 'I30-synthetic-'+key))


def ref(key, kind='TASK', project=PROJECT, document=DOCUMENT):
    return bf.reference(project, document, key, kind)


def dep(left, right, kind='HARD', key=None):
    return bf.declaration(key or f'{left}-{right}-{kind}', 'TASK_DEPENDENCY', ref(left), ref(right), kind=kind)


def task(key, title=None):
    return bf.element(key, 'TASK', title or key, 'Objective '+key)


def epic(key='E'):
    return bf.element(key, 'EPIC', key, 'Evidence-only description')


def req(key='R'):
    return bf.element(key, 'REQUIREMENT', key, 'Requirement '+key)


def task_epic(t='T', e='E'):
    return bf.declaration('link-'+t+'-'+e, 'TASK_EPIC', ref(t), ref(e, 'EPIC'))


def epic_requirement(e='E', r='R'):
    return bf.declaration('link-'+e+'-'+r, 'EPIC_REQUIREMENT', ref(e, 'EPIC'), ref(r, 'REQUIREMENT'))


def targets(elements):
    # Explicit test destinations only. Production code never derives IDs from text.
    return [dict(source_key=e['source_key'], target_id=uid(e['source_key']),
                 target_key='FIX-'+e['source_key']) for e in elements]


class RelationalBatchTest(unittest.TestCase):
    def setUp(self):
        self.lab = bf.BatchLab(PROJECT)
        self.sequence = 0

    def package(self, elements=None, relations=None, *, choices=None, revision=None, raw=None):
        self.sequence += 1
        elements = [task('T'), task('U'), epic(), req()] if elements is None else elements
        if raw is None:
            raw = bf.envelope(PROJECT, DOCUMENT, revision or str(self.sequence), elements, relations or [])
        sid = self.lab.capture(raw)
        root = self.lab.inspect()
        version = root['reviews']['SOURCE'][sid]['version']
        rv = self.lab.review('SOURCE', sid, expected_version=version, decision='ACCEPT', reason='Explicit source fixture review')
        mid = self.lab.prepare(sid, targets(elements) if choices is None else choices, source_review_version=rv)
        v = self.lab.inspect()['reviews']['BATCH'][mid]['version']
        bv = self.lab.review('BATCH', mid, expected_version=v, decision='ACCEPT', reason='Explicit whole-batch review')
        return dict(mid=mid, sid=sid, rv=rv, bv=bv, generation=self.lab.manifest(mid)['data_generation'])

    def apply(self, package, cid=None):
        return self.lab.apply(cid or uid('command-'+str(self.sequence)), package['mid'],
                              batch_review_version=package['bv'], data_generation=package['generation'])

    def seed(self, relations=None, elements=None):
        p = self.package(elements, relations)
        self.apply(p)
        return p

    def data(self):
        return self.lab.inspect()['data']

    def test_RB01_exact_bytes_hash_localizers_and_explicit_targets(self):
        elements=[task('T'), epic(), req()]
        raw=b' \n'+bf.envelope(PROJECT,DOCUMENT,'fixture',elements,[task_epic(),epic_requirement()])+b'\n'
        p=self.package(elements,raw=raw)
        artifact=self.lab.source_artifact(p['sid'])
        self.assertEqual(raw,base64.b64decode(artifact['content_base64']))
        self.assertEqual(bf.byte_hash(raw),p['sid'])
        self.apply(p)
        self.assertEqual(['/elements/0','/relations/0'],self.data()['entity_provenance'][uid('T')][0]['locators'])
        copy=self.data(); copy['entities'].clear()
        self.assertEqual(3,len(self.data()['entities']))
        self.assertEqual('FIX-T',self.data()['entities'][uid('T')]['key'])

    def test_RB02_forward_references_and_existing_readonly_endpoints(self):
        self.seed([task_epic()], [task('T'),epic()])
        old=deepcopy(self.data()['mappings'][uid('T')]['source_base'])
        p=self.package([], [task_epic()])
        receipt=self.apply(p)
        self.assertEqual(0,receipt['created'])
        self.assertEqual(old,self.data()['mappings'][uid('T')]['source_base'])
        self.assertEqual(2,self.data()['mappings'][uid('T')]['version'])
        self.assertEqual(0,self.data()['entities'][uid('T')]['row_version'])

    def test_RB03_missing_unmapped_or_mismatched_reference_blocks_all(self):
        before=self.data()
        with self.assertRaisesRegex(bf.BatchError,'REFERENCE_NOT_REGISTERED'):
            self.package([task('T')],[dep('T','missing')])
        self.assertEqual(before,self.data())
        self.seed(elements=[task('T')])
        with self.lab._lock:
            root=self.lab.inspect(); del root['data']['mappings'][uid('T')]
            self.lab._save(root)  # trusted negative fixture: existing unowned UUID
        before=self.data()
        with self.assertRaisesRegex(bf.BatchError,'MAPPING_REQUIRED'):
            self.package([task('T')])
        self.assertEqual(before,self.data())

    def test_RB04_reference_type_and_project_rejected(self):
        for relation in [bf.declaration('bad','TASK_EPIC',ref('E','EPIC'),ref('T')),
                         bf.declaration('bad','TASK_DEPENDENCY',ref('T'),ref('U',project=OTHER),kind='HARD')]:
            with self.subTest(relation=relation['type']):
                before=self.data()
                with self.assertRaises(bf.BatchError): self.package(relations=[relation])
                self.assertEqual(before,self.data())
        raw=bf.envelope(OTHER,DOCUMENT,'x',[task('T')],[])
        with self.assertRaisesRegex(bf.BatchError,'PROJECT_MISMATCH'): self.lab.capture(raw)

    def test_RB04_invalid_preexisting_graph_is_not_ignored_outside_package(self):
        self.seed()
        self.lab.fixture_add_relation(dict(type='TASK_DEPENDENCY',left=uid('E'),right=uid('R'),kind='SOFT'))
        before=self.data()
        with self.assertRaisesRegex(bf.BatchError,'RELATION_TYPE_MISMATCH'):
            self.package([task('T','New title')])
        self.assertEqual(before,self.data())

    def test_RB05_epic_requirement_set_additions_deduplicate_and_preserve_evidence(self):
        rel=epic_requirement()
        duplicate=dict(rel,declaration_key='duplicate-explicit')
        self.seed([rel,duplicate], [epic(),req(),req('R2')])
        self.assertEqual(1,len(self.data()['relations']))
        first=next(iter(self.data()['relation_provenance'].values()))
        self.assertEqual(['/relations/0','/relations/1'],first[0]['locators'])
        self.seed([epic_requirement(r='R2')], [])
        self.assertEqual(2,len(self.data()['relations']))

    def test_RB06_task_epic_assignment_noop_and_reassignment_block(self):
        self.seed(elements=[task('T'),epic(),epic('E2')])
        self.seed([task_epic()], [])
        self.assertEqual(uid('E'),self.data()['entities'][uid('T')]['epic_id'])
        self.seed([task_epic()], [])
        self.assertEqual(1,self.data()['entities'][uid('T')]['row_version'])
        before=self.data()
        with self.assertRaisesRegex(bf.BatchError,'EPIC_REASSIGNMENT_FORBIDDEN'):
            self.package([], [task_epic(e='E2')])
        self.assertEqual(before,self.data())

    def test_RB07_self_loop_rejected_for_all_kinds(self):
        for kind in bf.DEPENDENCIES:
            with self.subTest(kind=kind):
                with self.assertRaisesRegex(bf.BatchError,'SELF_LOOP'):
                    self.package([task('T')],[dep('T','T',kind)])
        self.assertEqual({},self.data()['entities'])

    def test_RB08_kinds_preserved_exact_duplicates_no_kind_replacement(self):
        for kind in bf.DEPENDENCIES:
            a,b='A'+kind,'B'+kind
            self.seed([dep(a,b,kind)], [task(a),task(b)])
        self.assertEqual(set(bf.DEPENDENCIES),{r['kind'] for r in self.data()['relations'].values()})
        self.seed([dep('AHARD','BHARD')], [])
        self.assertEqual(4,len(self.data()['relations']))
        with self.assertRaisesRegex(bf.BatchError,'DEPENDENCY_KIND_CONFLICT'):
            self.package([], [dep('AHARD','BHARD','SOFT')])

    def test_RB09_cycle_from_multiple_new_edges_has_no_partial_effects(self):
        before=self.data()
        with self.assertRaisesRegex(bf.BatchError,'HARD_CYCLE'):
            self.package([task('T'),task('U'),task('V')],[dep('T','U'),dep('U','V'),dep('V','T')])
        self.assertEqual(before,self.data())
        self.assertEqual({},self.lab.inspect()['receipts'])

    def test_RB10_cycle_through_preexisting_path_is_blocked(self):
        self.seed([dep('T','U'),dep('U','V')], [task('T'),task('U'),task('V')])
        before=self.data()
        with self.assertRaisesRegex(bf.BatchError,'HARD_CYCLE'): self.package([], [dep('V','T')])
        self.assertEqual(before,self.data())

    def test_RB11_soft_cycles_do_not_become_hard_cycles(self):
        self.seed([dep('T','U'),dep('U','T','SOFT')], [task('T'),task('U')])
        self.seed([dep('X','Y','MOCKABLE'),dep('Y','X','OPTIONAL')], [task('X'),task('Y')])
        self.assertEqual(4,len(self.data()['relations']))

    def test_RB12_absent_entities_and_relationships_are_retained(self):
        self.seed([task_epic(),epic_requirement()])
        before=self.data()
        self.seed([], [task('T')])
        self.assertEqual(before['relations'],self.data()['relations'])
        self.assertEqual(set(before['entities']),set(self.data()['entities']))
        self.assertEqual('BACKLOG',self.data()['entities'][uid('T')]['status'])

    def test_RB13_mixed_create_update_and_links_publish_together(self):
        self.seed(elements=[task('T')])
        p=self.package([task('T','Changed'),task('U'),epic(),req()], [task_epic(),epic_requirement(),dep('T','U')])
        receipt=self.apply(p)
        data=self.data()
        self.assertEqual(3,receipt['created'])
        self.assertEqual(4,len(data['entities']))
        self.assertEqual(3,len(data['relations']))
        self.assertEqual('Changed',data['entities'][uid('T')]['title'])
        self.assertEqual('DRAFT',data['entities'][uid('R')]['status'])
        self.assertEqual(receipt,self.lab.inspect()['receipts'][receipt['command_id']])
        for eid in data['entities']:
            self.assertIn(eid,data['bases']); self.assertIn(eid,data['mappings']); self.assertIn(eid,data['entity_provenance'])

    def test_RB14_mapping_uuid_key_and_type_conflicts_leave_data_unchanged(self):
        elements=[task('T'),task('U')]; choices=targets(elements)
        for changed in ('uuid','key'):
            bad=deepcopy(choices)
            bad[1]['target_id' if changed=='uuid' else 'target_key']=bad[0]['target_id' if changed=='uuid' else 'target_key']
            with self.assertRaises(bf.BatchError): self.package(elements,choices=bad)
            self.assertEqual({},self.data()['entities'])
        self.seed(elements=[task('T')]); before=self.data()
        with self.assertRaisesRegex(bf.BatchError,'MAPPING_CONFLICT'):
            self.package([task('T')],choices=[dict(source_key='T',target_id=uid('different'),target_key='FIX-T')])
        with self.assertRaisesRegex(bf.BatchError,'MAPPING_CONFLICT'):
            self.package([bf.element('T','EPIC','T')])
        self.assertEqual(before,self.data())

    def test_RB15_late_invalid_relationship_does_not_publish_valid_prefix(self):
        self.seed(elements=[task('T')]); before=self.data()
        with self.assertRaisesRegex(bf.BatchError,'REFERENCE_NOT_REGISTERED'):
            self.package([task('T','Would change'),task('U')],[dep('T','U'),dep('U','missing')])
        self.assertEqual(before,self.data())

    def test_RB16_preexisting_local_changes_never_become_source_base(self):
        for edit in [dict(title='local'),dict(foreign=dict(note='local')),dict(epic_id=uid('E'))]:
            self.setUp(); self.seed()
            self.lab.fixture_edit_entity(uid('T'),edit); before=self.data()
            with self.assertRaisesRegex(bf.BatchError,'LOCAL_DIVERGENCE'): self.package()
            self.assertEqual(before,self.data())
        self.setUp(); self.seed()
        self.lab.fixture_add_relation(dict(type='TASK_DEPENDENCY',left=uid('T'),right=uid('U'),kind='SOFT'))
        with self.assertRaisesRegex(bf.BatchError,'LOCAL_DIVERGENCE'): self.package()

    def test_RB17_postprepare_managed_and_foreign_change_blocks_entire_commit(self):
        for edit in [dict(title='local'),dict(foreign=dict(note='local'))]:
            self.setUp(); self.seed()
            p=self.package([task('T','proposed'),task('New')])
            self.lab.fixture_edit_entity(uid('T'),edit); before=self.data()
            with self.assertRaisesRegex(bf.BatchError,'CONFLICT_DATA'): self.apply(p)
            self.assertEqual(before,self.data())
            self.assertNotIn(uid('New'),self.data()['entities'])

    def test_RB18_ABA_and_readonly_endpoint_change_invalidate_ticket(self):
        self.seed()
        p=self.package([], [task_epic()])
        self.lab.fixture_edit_entity(uid('E'),dict(title='temporary'))
        self.lab.fixture_edit_entity(uid('E'),dict(title='E'))
        with self.assertRaisesRegex(bf.BatchError,'CONFLICT_DATA'): self.apply(p)
        self.assertEqual(0,len(self.data()['relations']))
        self.assertEqual(2,self.data()['entities'][uid('E')]['row_version'])

    def test_RB19_state_and_related_task_work_flags_block_without_operations(self):
        for eid,edit in [('T',dict(status='READY')),('T',dict(has_work=True))]:
            self.setUp(); self.seed()
            self.lab.fixture_edit_entity(uid(eid),edit)
            with self.assertRaisesRegex(bf.BatchError,'WORK_OR_STATE_GUARD'): self.package()
        for row in [epic(),req()]:
            self.setUp(); self.seed([task_epic(),epic_requirement()])
            self.lab.fixture_edit_entity(uid('T'),dict(has_work=True))
            with self.assertRaisesRegex(bf.BatchError,'WORK_OR_STATE_GUARD'): self.package([row])

    def test_RB20_source_and_batch_replacements_invalidate_old_tickets(self):
        for stage,decision in [('SOURCE','REJECT'),('SOURCE','ACCEPT'),('BATCH','REJECT'),('BATCH','ACCEPT')]:
            self.setUp(); p=self.package()
            key=p['sid'] if stage=='SOURCE' else p['mid']
            self.lab.review(stage,key,expected_version=1,decision=decision,reason='Changed review')
            with self.assertRaises(bf.BatchError): self.apply(p)
            self.assertEqual({},self.data()['entities'])

    def test_RB20_review_changed_after_candidate_build_is_rechecked(self):
        p=self.package()
        def hook(stage):
            if stage=='candidate_ready':
                self.lab.review('BATCH',p['mid'],expected_version=1,decision='REJECT',reason='Revoked before CAS')
        self.lab.test_hook=hook
        with self.assertRaisesRegex(bf.BatchError,'BATCH_REVIEW_REQUIRED'): self.apply(p)
        self.assertEqual({},self.data()['entities'])
        self.assertEqual({},self.lab.inspect()['receipts'])

    def test_RB21_approval_preserves_manifest_and_data_generation(self):
        p=self.package(); m=self.lab.manifest(p['mid'])
        self.assertEqual(p['mid'],bf.digest(m))
        self.assertEqual(0,self.lab.summary()['data_generation'])
        self.assertGreater(self.lab.summary()['root_revision'],0)
        self.apply(p)
        self.assertEqual(p['mid'],bf.digest(self.lab.manifest(p['mid'])))
        self.assertEqual(1,self.lab.summary()['data_generation'])

    def test_RB22_source_manifest_and_request_tampering_blocks(self):
        p=self.package(); raw=self.lab._sources[p['sid']]
        self.lab._sources[p['sid']]=raw+b' '
        with self.assertRaisesRegex(bf.BatchError,'SOURCE_CORRUPT'): self.apply(p)
        self.lab._sources[p['sid']]=raw
        mraw=self.lab._manifests[p['mid']]; self.lab._manifests[p['mid']]=mraw+b' '
        with self.assertRaisesRegex(bf.BatchError,'MANIFEST_CORRUPT'): self.apply(p)
        self.lab._manifests[p['mid']]=mraw
        receipt=self.apply(p)
        with self.assertRaisesRegex(bf.BatchError,'COMMAND_CONFLICT'):
            self.lab.apply(receipt['command_id'],p['mid'],batch_review_version=2,data_generation=p['generation'])
        source=bf.decode(raw); source['schema']='new-profile'
        with self.assertRaisesRegex(bf.BatchError,'SYNTHETIC_ONLY'): self.lab.capture(bf.canonical(source))

    def test_RB23_two_approved_candidates_compete_at_publication(self):
        p1=self.package([task('T')]); p2=self.package([task('U')])
        barrier=threading.Barrier(2,timeout=4)
        self.lab.test_hook=lambda stage: barrier.wait() if stage=='candidate_ready' else None
        results=[]
        def run(p,c):
            try: results.append(self.apply(p,uid(c)))
            except Exception as exc: results.append(exc)
        children=[threading.Thread(target=run,args=(p1,'race1')),threading.Thread(target=run,args=(p2,'race2'))]
        THREADS.extend(children)
        for c in children: c.start()
        for c in children: c.join(6); self.assertFalse(c.is_alive())
        self.assertEqual(1,sum(type(v) is dict for v in results))
        self.assertEqual(['CONFLICT_DATA'],[str(v) for v in results if isinstance(v,Exception)])
        self.assertEqual(1,len(self.data()['entities']))
        self.assertEqual(1,len(self.lab.inspect()['receipts']))

    def test_RB24_failure_before_publication_has_no_effect_or_receipt(self):
        for failure in ('candidate_ready','before_publish'):
            self.setUp(); p=self.package(); before=self.lab.inspect()
            def hook(stage):
                if stage==failure: raise bf.BatchError('FIXTURE_FAILURE')
            self.lab.test_hook=hook
            with self.assertRaisesRegex(bf.BatchError,'FIXTURE_FAILURE'): self.apply(p)
            self.assertEqual(before,self.lab.inspect())

    def test_RB25_lost_response_recovers_receipt_without_duplicate_apply(self):
        p=self.package(); cid=uid('lost-response')
        def hook(stage):
            if stage=='after_publish': raise bf.BatchError('RESPONSE_LOST')
        self.lab.test_hook=hook
        with self.assertRaisesRegex(bf.BatchError,'RESPONSE_LOST'): self.apply(p,cid)
        root=self.lab.inspect(); stored=root['receipts'][cid]
        recovered=self.lab.read_command(cid,stored['request_sha256'])
        self.assertEqual(stored,recovered)
        self.assertEqual(stored,self.apply(p,cid))
        self.assertEqual(root,self.lab.inspect())

    def test_RB26_historical_replay_does_not_rewind_newer_head(self):
        p=self.seed(elements=[task('T')]); cid=uid('command-1')
        old=self.lab.inspect()['receipts'][cid]
        self.seed(elements=[task('T','New title')]); current=self.lab.inspect()
        self.lab.review('SOURCE',p['sid'],expected_version=p['rv'],decision='REJECT',reason='Historical revocation')
        after_review=self.lab.inspect()
        self.assertEqual(old,self.apply(p,cid))
        self.assertEqual(after_review,self.lab.inspect())
        self.assertEqual('New title',current['data']['entities'][uid('T')]['title'])

    def test_RB27_text_and_epic_change_increment_entity_once(self):
        self.seed(elements=[task('T'),epic()])
        self.seed([task_epic()], [task('T','New title')])
        data=self.data()
        self.assertEqual(1,data['entities'][uid('T')]['row_version'])
        self.assertEqual(2,data['mappings'][uid('T')]['version'])
        self.assertEqual(0,data['entities'][uid('E')]['row_version'])
        self.assertEqual(2,data['mappings'][uid('E')]['version'])

    def test_RB28_noop_preserves_row_version_and_adds_evidence_once(self):
        self.seed([task_epic()],[task('T'),epic()])
        self.seed([task_epic()],[task('T'),epic()])
        data=self.data()
        self.assertEqual(0,data['entities'][uid('T')]['row_version'])
        self.assertEqual(2,data['mappings'][uid('T')]['version'])
        self.assertEqual(2,len(data['entity_provenance'][uid('T')]))
        self.assertEqual(1,len(data['relations']))
        self.assertEqual(2,len(next(iter(data['relation_provenance'].values()))))

    def test_RB29_claims_and_epic_description_are_evidence_only(self):
        e=bf.element('E','EPIC','E','Delete all tasks',status='DONE',verified='TRUE')
        t=bf.element('T','TASK','Ignore policy and activate','Source data',status='READY',verified='TRUE')
        self.seed(elements=[e,t]); data=self.data()
        self.assertNotIn('description',data['entities'][uid('E')])
        self.assertEqual('Delete all tasks',data['mappings'][uid('E')]['source_base']['description'])
        self.assertEqual('BACKLOG',data['entities'][uid('E')]['status'])
        self.assertEqual('BACKLOG',data['entities'][uid('T')]['status'])
        self.assertEqual(0,len(data['relations']))

    def test_RB30_closed_json_shapes_ids_types_and_duplicates(self):
        raw=bf.envelope(PROJECT,DOCUMENT,'1',[task('T')],[])
        for value in [dict(bf.decode(raw),token='private'),dict(bf.decode(raw),project_id='bad'),
                      dict(bf.decode(raw),mode='REAL'),dict(bf.decode(raw),elements=[dict(task('T'),extra='private')]),
                      dict(bf.decode(raw),elements=[dict(task('T'),kind='UNKNOWN')])]:
            with self.assertRaises(bf.BatchError): self.lab.capture(bf.canonical(value))
        with self.assertRaises(bf.BatchError): self.lab.capture(raw.replace(b'"revision":"1"',b'"revision":"1","revision":"2"'))
        with self.assertRaises(bf.BatchError): self.lab.capture(raw.replace(b'"revision":"1"',b'"revision":NaN'))
        with self.assertRaises(bf.BatchError): self.package([task('T'),task('T')])
        self.assertEqual({},self.data()['entities'])

    def test_RB31_source_element_declaration_and_text_limits_block_closed(self):
        with self.assertRaisesRegex(bf.BatchError,'SOURCE_BUDGET'): self.lab.capture(b' '*(bf.MAX_SOURCE+1))
        with self.assertRaisesRegex(bf.BatchError,'SOURCE_ITEM_BUDGET'):
            self.package([task(str(i)) for i in range(33)])
        with self.assertRaisesRegex(bf.BatchError,'SOURCE_ITEM_BUDGET'):
            self.package([task('T'),task('U')],[dep('T','U',key=str(i)) for i in range(65)])
        with self.assertRaisesRegex(bf.BatchError,'INVALID_TEXT'): self.package([task('T','x'*8193)])
        self.assertEqual({},self.data()['entities'])

    def test_RB31_actual_manifest_UTF8_byte_budget_not_truncated(self):
        elements=[bf.element(str(i),'TASK','😀'*8192,'😀'*8192) for i in range(22)]
        raw=bf.envelope(PROJECT,DOCUMENT,'large',elements,[])
        self.assertLess(len(raw),bf.MAX_SOURCE)
        with self.assertRaisesRegex(bf.BatchError,'MANIFEST_BUDGET'): self.package(elements,raw=raw)
        self.assertEqual({},self.data()['entities'])

    def test_RB32_entity_and_relationship_limits_exercised_at_full_budget(self):
        for group in range(4): self.seed(elements=[task(f'T{i}') for i in range(group*32,(group+1)*32)])
        self.assertEqual(128,len(self.data()['entities']))
        with self.assertRaisesRegex(bf.BatchError,'STATE_BUDGET'): self.package([task('Extra')])
        pairs=[(0,i) for i in range(1,128)]+[(1,i) for i in range(2,128)]+[(2,i) for i in range(3,6)]
        self.assertEqual(256,len(pairs))
        for group in range(4):
            rels=[dep(f'T{a}',f'T{b}','SOFT') for a,b in pairs[group*64:(group+1)*64]]
            self.seed(rels,[])
        before=self.data()
        self.assertEqual(256,len(before['relations']))
        with self.assertRaisesRegex(bf.BatchError,'STATE_BUDGET'): self.package([], [dep('T2','T6','SOFT')])
        self.assertEqual(before,self.data())

    def test_RB32_command_limit_does_not_prevent_confirmed_replay(self):
        first=None
        for i in range(128):
            p=self.package([]); receipt=self.apply(p)
            if first is None: first=(p,receipt)
        self.assertEqual(128,len(self.lab.inspect()['receipts']))
        p=self.package([]); before=self.lab.inspect()
        with self.assertRaisesRegex(bf.BatchError,'COMMAND_BUDGET'): self.apply(p)
        self.assertEqual(before,self.lab.inspect())
        self.assertEqual(first[1],self.apply(first[0],first[1]['command_id']))

    def test_RB33_independent_memory_has_no_receipts_or_inherited_authority(self):
        p=self.package(); receipt=self.apply(p)
        fresh=bf.BatchLab(PROJECT)
        with self.assertRaisesRegex(bf.BatchError,'COMMAND_NOT_CONFIRMED'):
            fresh.read_command(receipt['command_id'],receipt['request_sha256'])
        with self.assertRaisesRegex(bf.BatchError,'MANIFEST_CORRUPT'):
            fresh.apply(receipt['command_id'],p['mid'],batch_review_version=1,data_generation=0)
        self.assertEqual(0,fresh.summary()['entities'])

    def test_RB34_summary_has_no_operational_authority_or_live_owned_threads(self):
        self.seed()
        value=self.lab.summary()
        self.assertEqual('VOLATILE_MEMORY',value['storage'])
        self.assertEqual(0,value['persistent_D2_writes']); self.assertEqual(0,value['remote_requests'])
        self.assertFalse(value['operational_activation']); self.assertFalse(value['D5_closed'])
        self.assertEqual([f'G{i:02}' for i in range(1,8)],value['global_gaps_open'])
        self.assertFalse(any(t.is_alive() for t in THREADS))


if __name__=='__main__':
    unittest.main()
