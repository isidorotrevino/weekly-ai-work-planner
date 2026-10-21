# SPDX-License-Identifier: GPL-3.0-only
"""Adapter trust boundary without Docker; integration runs separately."""
import hashlib
import tempfile
import unittest
from unittest.mock import Mock

from source_ingest.postgres import LabClient, envelope, ingest_request, verify_payload
from source_ingest.preview import build_observation, canonical, save_preview

PROJECT = '00000000-0000-4000-8000-000000000001'
DOCUMENT = '00000000-0000-4000-8000-000000000002'
COMMAND = '00000000-0000-4000-8000-000000000003'


class AdapterBoundary(unittest.TestCase):
    def setUp(self):
        self.source = b'# Synthetic\n- [ ] diagnostic only\n'
        self.value = build_observation(self.source,'fixture.md',PROJECT,DOCUMENT,'fixture')
        self.artifact = canonical(self.value)
        self.request = envelope(COMMAND,'INGEST',PROJECT,DOCUMENT,profile=self.value['profile'],
                                content_sha256=self.value['content_sha256'],
                                preview_sha256=hashlib.sha256(self.artifact).hexdigest())
        self.client = LabClient.__new__(LabClient)
        self.client.query = Mock()

    def test_forged_semantics_never_reach_sql(self):
        altered = dict(self.value, proposals=[])
        artifact = canonical(altered)
        request = dict(self.request,preview_sha256=hashlib.sha256(artifact).hexdigest())
        with self.assertRaises(ValueError):
            self.client.submit(request,self.source,artifact)
        self.client.query.assert_not_called()

    def test_request_scope_never_overrides_verified_artifact(self):
        with self.assertRaises(ValueError):
            self.client.submit(dict(self.request,document_id=COMMAND),self.source,self.artifact)
        self.client.query.assert_not_called()

    def test_file_reconstruction_and_transport_safe_encoding(self):
        # Shell/SQL-looking text is preserved exclusively inside hex-encoded data.
        value = build_observation(self.source,'fixture.md',PROJECT,DOCUMENT,"x'); DROP SCHEMA d5; -- $(id)")
        with tempfile.TemporaryDirectory() as directory:
            path,_ = save_preview(directory,value)
            packet = ingest_request(COMMAND,path)
        self.client.submit(*packet)
        sql = self.client.query.call_args.args[0]
        self.assertNotIn('DROP SCHEMA',sql)
        self.assertNotIn('$(id)',sql)
        self.assertEqual(verify_payload(*packet[1:]),value)
