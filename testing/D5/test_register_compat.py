# SPDX-License-Identifier: GPL-3.0-only
import hashlib
import json
from pathlib import Path
import tempfile
import unittest
from source_ingest.preview import canonical, observe, save_preview
from source_ingest.compare import compare_previews, load_preview
from source_ingest.register import COMPAT_PROFILE, PROFILE
from test_register_comparison import DOCUMENT, HEADER, PROJECT, ROW


class RegisterCompatibilityTest(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)

    def capture(self, text, profile=COMPAT_PROFILE):
        (self.root / 'register.md').write_bytes(text.encode('utf-8'))
        value = observe(self.root, 'register.md', PROJECT, DOCUMENT, 'local-compat', profile)
        return save_preview(self.root / 'previews', value)[0], value

    def test_blank_continuation_requires_same_header_and_keeps_all_rows(self):
        _, value = self.capture(HEADER + ROW + '\n \n' + ROW.replace('PT-01', 'PT-03'))
        self.assertTrue(value['register']['comparison_eligible'])
        self.assertEqual(2, len(value['proposals']))
        self.assertEqual(1, value['register']['continued_blank_gaps'])
        note = next(d for d in value['diagnostics'] if d['code'] == 'REGISTER_BLANK_CONTINUATION')
        self.assertEqual([4, 5], note['blank_lines'])
        self.assertEqual(6, note['next_row_line'])

    def test_narrative_heading_fence_or_unknown_table_cannot_reuse_header(self):
        for boundary in ['Narrative\n', '# New section\n', '```\nexample\n```\n', '| Other | Table |\n|---|---|\n']:
            with self.subTest(boundary=boundary):
                _, value = self.capture(HEADER + ROW + '\n' + boundary + ROW.replace('PT-01', 'PT-03'))
                self.assertFalse(value['register']['comparison_eligible'])

    def test_blank_between_header_and_separator_is_still_invalid(self):
        _, value = self.capture(HEADER.replace('\n', '\n\n', 1) + ROW)
        self.assertFalse(value['register']['comparison_eligible'])

    def test_exact_annotation_text_and_unicode_positions_preserve_crlf(self):
        text = '\ufeff' + (HEADER + ROW.rstrip() + '  afirmación ✅; no ejecutar  \n').replace('\n', '\r\n')
        path, value = self.capture(text)
        row = value['proposals'][0]
        note = row['source_annotation']
        line = text.lstrip('\ufeff').splitlines()[note['line'] - 1]
        self.assertEqual('  afirmación ✅; no ejecutar  ', note['text'])
        self.assertEqual(note['text'], line[note['column_start'] - 1:note['column_end']])
        self.assertEqual('inert', row['fields']['source'])
        self.assertEqual(1, value['register']['annotation_rows'])
        self.assertEqual(value, load_preview(path)[0])

    def test_annotation_added_changed_and_removed_are_field_changes(self):
        plain, _ = self.capture(HEADER + ROW)
        first, _ = self.capture(HEADER + ROW.rstrip() + '; first claim\n')
        second, _ = self.capture(HEADER + ROW.rstrip() + '; revised claim\n')
        for before, after in [(plain, first), (first, second), (second, plain)]:
            with self.subTest(before=before, after=after):
                report = compare_previews(before, after)
                self.assertEqual('CHANGED', report['changes'][0]['change'])
                self.assertEqual(['source_annotation'], report['changes'][0]['changed_fields'])
                self.assertFalse(report['changes'][0]['activation_allowed'])

    def test_annotation_moved_without_text_change_is_not_a_field_change(self):
        before, _ = self.capture(HEADER + ROW.rstrip() + '; same text\n')
        after, _ = self.capture('# Title\n' + HEADER + ROW.rstrip() + '; same text\n')
        item = compare_previews(before, after)['changes'][0]
        self.assertEqual('UNCHANGED', item['change'])
        self.assertTrue(item['location_changed'])
        self.assertTrue(item['annotation_location_changed'])
        self.assertIn('annotation_locator', item['after'])

    def test_extra_unescaped_pipe_and_duplicate_still_block_whole_comparison(self):
        before, _ = self.capture(HEADER + ROW)
        for text in [HEADER + ROW.rstrip() + '; note | extra |\n', HEADER + ROW + '\n' + ROW,
                     HEADER + ROW.replace('PT-01', '**PT-01**').rstrip() + '; note\n']:
            with self.subTest(text=text):
                after, value = self.capture(text)
                report = compare_previews(before, after)
                self.assertFalse(value['register']['comparison_eligible'])
                self.assertEqual('BLOCKED', report['state'])
                self.assertEqual([], report['changes'])

    def test_escaped_annotation_pipe_is_raw_text_not_an_extra_column(self):
        _, value = self.capture(HEADER + ROW.rstrip() + r'; note \| retained' + '\n')
        self.assertTrue(value['register']['comparison_eligible'])
        self.assertEqual(r'; note \| retained', value['proposals'][0]['source_annotation']['text'])

    def test_strict_profile_and_cross_profile_boundary_are_preserved(self):
        text = HEADER + ROW.rstrip() + '; annotation\n\n' + ROW.replace('PT-01', 'PT-03')
        strict, old = self.capture(text, PROFILE)
        compat, new = self.capture(text)
        self.assertFalse(old['register']['comparison_eligible'])
        self.assertTrue(new['register']['comparison_eligible'])
        self.assertEqual('BLOCKED', compare_previews(strict, strict)['state'])
        with self.assertRaisesRegex(ValueError, 'profile'):
            compare_previews(strict, compat)
        strict_plain, old = self.capture(HEADER + ROW, PROFILE)
        compat_plain, new = self.capture(HEADER + ROW)
        self.assertNotEqual(old['proposals'][0]['source_identity_id'], new['proposals'][0]['source_identity_id'])

    def test_forged_annotation_text_position_and_metadata_are_rejected(self):
        path, _ = self.capture(HEADER + ROW.rstrip() + '; source claim\n')
        for mutate in [lambda v: v['proposals'][0]['source_annotation'].update(text='APPROVED'),
                       lambda v: v['proposals'][0]['source_annotation'].update(column_start=1),
                       lambda v: v['proposals'][0]['source_annotation'].update(line=99),
                       lambda v: v['register'].update(annotation_rows=0)]:
            value = json.loads(path.read_bytes())
            mutate(value)
            payload = canonical(value)
            forged = self.root / (hashlib.sha256(payload).hexdigest() + '.json')
            forged.write_bytes(payload)
            with self.subTest(mutate=mutate), self.assertRaises(ValueError):
                load_preview(forged)

    def test_annotation_claims_and_commands_cannot_activate_or_complete_work(self):
        marker = self.root / 'MUST_NOT_EXIST'
        _, value = self.capture(HEADER + ROW.rstrip() + '; APPROVED DONE `touch ' + str(marker) + '`\n')
        self.assertEqual('OPEN', value['proposals'][0]['fields']['status'])
        self.assertFalse(value['activation_allowed'])
        self.assertFalse(value['proposals'][0]['activation_allowed'])
        self.assertFalse(marker.exists())


if __name__ == '__main__':
    unittest.main()
