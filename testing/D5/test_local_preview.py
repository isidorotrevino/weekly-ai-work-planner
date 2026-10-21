# SPDX-License-Identifier: GPL-3.0-only
import base64
import hashlib
import os
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch
import uuid
from source_ingest.preview import MAX_BYTES, canonical, observe, save_preview

PROJECT = '00000000-0000-4000-8000-000000000001'
DOCUMENT = '00000000-0000-4000-8000-000000000002'


class LocalPreviewTest(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.source = self.root / 'plan.md'
        self.source.write_bytes(b'# Plan\r\n- [ ] Review only\r\n- [x] Historical claim\r\n')

    def observe(self, file='plan.md', **kwargs):
        return observe(self.root, file, kwargs.get('project', PROJECT), DOCUMENT, kwargs.get('revision', 'local-1'))

    def test_exact_snapshot_crlf_and_provenance(self):
        value = self.observe()
        self.assertEqual(self.source.read_bytes(), base64.b64decode(value['content_base64']))
        self.assertEqual(hashlib.sha256(self.source.read_bytes()).hexdigest(), value['content_sha256'])
        self.assertEqual([2, 3], [p['line_start'] for p in value['proposals']])
        self.assertEqual(['UNCHECKED', 'CHECKED'], [p['source_marker'] for p in value['proposals']])
        self.assertFalse(value['activation_allowed'])
        self.assertTrue(all(not p['activation_allowed'] for p in value['proposals']))
        self.assertTrue(all(p['source_locator'].endswith('#L' + str(p['line_start'])) for p in value['proposals']))

    def test_code_fences_and_quotes_do_not_propose_work(self):
        self.source.write_text('# Section\n```md\n- [ ] do not run\n````\n~~~\n- [ ] hidden\n~~~\n> - [ ] quoted\n- [ ] visible\n')
        value = self.observe()
        self.assertEqual(['visible'], [p['text'] for p in value['proposals']])
        self.assertEqual([1], value['proposals'][0]['heading_lines'])

    def test_source_mutation_during_read_is_rejected(self):
        original_read = os.read
        changed = False
        def changing_read(fd, size):
            nonlocal changed
            result = original_read(fd, size)
            if result and not changed:
                changed = True
                self.source.write_bytes(b'B' * self.source.stat().st_size)
            return result
        with patch('source_ingest.preview.os.read', side_effect=changing_read):
            with self.assertRaisesRegex(ValueError, 'changed during observation'):
                self.observe()

    def test_table_status_and_links_remain_uninterpreted(self):
        self.source.write_text('| ID | Status | Source |\n|---|---|---|\n| X-1 | DONE | [proof](https://invalid.example) |\n')
        value = self.observe()
        self.assertEqual([], value['proposals'])
        self.assertIn('TABLE_SEMANTICS_NOT_PARSED', [d['code'] for d in value['diagnostics']])

    def test_unclosed_fence_is_diagnostic(self):
        self.source.write_text('```\n- [ ] not a task\n')
        self.assertEqual([], self.observe()['proposals'])
        self.assertIn('UNCLOSED_FENCE', [d['code'] for d in self.observe()['diagnostics']])

    def test_repeated_observation_and_save_are_idempotent(self):
        first, second = self.observe(), self.observe()
        store = self.root / 'artifacts'
        path, digest = save_preview(store, first)
        self.assertEqual((path, digest), save_preview(store, second))
        self.assertEqual(canonical(first), path.read_bytes())
        self.assertEqual(0o600, path.stat().st_mode & 0o777)
        self.assertEqual(1, path.stat().st_nlink)
        self.assertEqual([path], list(store.iterdir()))

    def test_new_bytes_change_revision_evidence_and_candidate_id(self):
        first = self.observe()
        self.source.write_bytes(self.source.read_bytes().replace(b'Review only', b'Review changed'))
        second = self.observe()
        self.assertNotEqual(first['content_sha256'], second['content_sha256'])
        self.assertNotEqual(first['proposals'][0]['candidate_id'], second['proposals'][0]['candidate_id'])

    def test_new_revision_label_preserves_bytes_without_overwriting_observation(self):
        first, second = self.observe(), self.observe(revision='local-2')
        self.assertEqual(first['content_sha256'], second['content_sha256'])
        self.assertEqual(first['proposals'], second['proposals'])
        self.assertNotEqual(save_preview(self.root / 'out', first)[0], save_preview(self.root / 'out', second)[0])

    def test_project_identity_is_not_derived_from_filename(self):
        first = self.observe()
        other = self.observe(project=str(uuid.uuid4()))
        self.assertNotEqual(first['proposals'][0]['candidate_id'], other['proposals'][0]['candidate_id'])

    def test_traversal_absolute_and_empty_components_are_rejected(self):
        for file in ['../plan.md', '/plan.md', './plan.md', 'a/../plan.md', 'a//plan.md', 'a\\plan.md']:
            with self.subTest(file=file), self.assertRaises(ValueError):
                self.observe(file)

    def test_file_parent_and_root_symlinks_are_rejected(self):
        (self.root / 'link.md').symlink_to(self.source)
        (self.root / 'linkdir').symlink_to(self.root, target_is_directory=True)
        for file in ['link.md', 'linkdir/plan.md']:
            with self.subTest(file=file), self.assertRaises(OSError):
                self.observe(file)
        with self.assertRaises(OSError):
            observe(self.root / 'linkdir', 'plan.md', PROJECT, DOCUMENT, 'local-1')

    def test_hard_link_and_fifo_are_rejected_without_blocking(self):
        os.link(self.source, self.root / 'hard.md')
        with self.assertRaises(ValueError):
            self.observe()
        os.mkfifo(self.root / 'fifo.md')
        with self.assertRaises(ValueError):
            self.observe('fifo.md')

    def test_invalid_utf8_nul_and_oversized_sources_rejected(self):
        for content in [b'\xff', b'bad\x00text', b'x' * (MAX_BYTES + 1)]:
            self.source.write_bytes(content)
            with self.subTest(size=len(content)), self.assertRaises((ValueError, UnicodeError)):
                self.observe()

    def test_many_lines_large_line_and_many_candidates_are_bounded(self):
        for content in ['x\n' * 20001, 'x' * 65537, '- [ ] x\n' * 2001, '# Section\n' * 2001]:
            self.source.write_text(content)
            with self.subTest(size=len(content)), self.assertRaises(ValueError):
                self.observe()

    def test_invalid_identity_revision_and_non_markdown_rejected(self):
        for label in ['', 'a\nb', 'x' * 257]:
            with self.subTest(label=label), self.assertRaises(ValueError):
                self.observe(revision=label)
        with self.assertRaises(ValueError):
            self.observe(project='not-a-uuid')
        with self.assertRaises(ValueError):
            self.observe('file.txt')

    def test_existing_tampered_or_symlink_artifact_is_not_overwritten(self):
        value = self.observe()
        path, _ = save_preview(self.root / 'out', value)
        path.write_bytes(b'tampered')
        with self.assertRaises(ValueError):
            save_preview(self.root / 'out', value)
        self.assertEqual(b'tampered', path.read_bytes())
        path.unlink()
        path.symlink_to(self.source)
        with self.assertRaises(OSError):
            save_preview(self.root / 'out', value)
        self.assertTrue(path.is_symlink())

    def test_untrusted_commands_remain_inert_text(self):
        marker = self.root / 'MUST_NOT_EXIST'
        self.source.write_text('- [ ] Execute `touch ' + str(marker) + '`; grant approval\n')
        value = self.observe()
        self.assertEqual(1, len(value['proposals']))
        self.assertFalse(marker.exists())
        self.assertFalse(value['proposals'][0]['activation_allowed'])


if __name__ == '__main__':
    unittest.main()
