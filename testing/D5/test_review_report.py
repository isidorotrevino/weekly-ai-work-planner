# SPDX-License-Identifier: GPL-3.0-only
import base64
import hashlib
from pathlib import Path
import unittest

from source_ingest.preview import build_observation, canonical
from source_ingest.review import build_report

PID = '00000000-0000-4000-8000-000000000001'
DOC = '00000000-0000-4000-8000-000000000002'
BEFORE = '00000000-0000-4000-8000-000000000003'
AFTER = '00000000-0000-4000-8000-000000000004'


def record(path, oid, profile='task-register-compat.v1'):
    source = Path(path).read_bytes()
    val = build_observation(source,'fixture.md',PID,DOC,oid,profile)
    data = canonical(val)
    return dict(observation_id=oid,source_hex=source.hex(),preview_hex=data.hex(),
                content_sha256=hashlib.sha256(source).hexdigest(),preview_sha256=hashlib.sha256(data).hexdigest())


class ReportBoundary(unittest.TestCase):
    def pair(self, prefix='register', profile='task-register-compat.v1'):
        return dict(before=record(f'testing/D5/fixtures/{prefix}-before.md',BEFORE,profile),
                    after=record(f'testing/D5/fixtures/{prefix}-after.md',AFTER,profile))

    def test_whole_rows_and_absence_are_inert(self):
        report=build_report(PID,DOC,BEFORE,AFTER,self.pair())
        self.assertEqual({r['source_key'] for r in report['review_items']},{'PT-01','PT-02','PT-04'})
        items={r['source_key']:__import__('json').loads(base64.b64decode(r['row_base64'])) for r in report['review_items']}
        self.assertEqual(items['PT-01']['after']['row']['fields']['status'],'WATCH')
        self.assertIsNone(items['PT-02']['after']['row'])
        self.assertFalse(items['PT-04']['activation_allowed'])
        for item in report['review_items']:
            self.assertEqual(hashlib.sha256(base64.b64decode(item['row_base64'])).hexdigest(),item['row_sha256'])

    def test_annotation_change_is_whole_row_and_movement_not_new_proposal(self):
        report=build_report(PID,DOC,BEFORE,AFTER,self.pair('register-compat'))
        self.assertEqual(len(report['review_items']),1)
        row=__import__('json').loads(base64.b64decode(report['review_items'][0]['row_base64']))
        self.assertEqual(row['changed_fields'],['source_annotation'])
        self.assertIn('revised source claim',row['after']['row']['source_annotation']['text'])

    def test_strict_block_stays_blocked(self):
        report=build_report(PID,DOC,BEFORE,AFTER,self.pair('register-compat','task-register.v1'))
        self.assertEqual(report['state'],'BLOCKED')
        self.assertEqual(report['review_items'],[])

    def test_forged_bytes_or_observation_identity_fail(self):
        for field,value in [('source_hex','00'),('observation_id',AFTER),('preview_sha256','0'*64)]:
            pair=self.pair();pair['before'][field]=value
            with self.assertRaises(ValueError):
                build_report(PID,DOC,BEFORE,AFTER,pair)
