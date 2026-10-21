# SPDX-License-Identifier: GPL-3.0-only
import hashlib
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest
from source_ingest.preview import canonical, observe, save_preview
from source_ingest.compare import compare_previews, load_preview
from source_ingest.register import HEADERS, PROFILE

PROJECT = '00000000-0000-4000-8000-000000000001'
DOCUMENT = '00000000-0000-4000-8000-000000000002'
HEADER = '| ' + ' | '.join(HEADERS) + ' |\n|' + '---|' * 8 + '\n'
ROW = '| PT-01 | Example | `module` | Review only | PT-02 | OPEN | unverified | inert |\n'


class RegisterComparisonTest(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.fixture = Path(__file__).parent / 'fixtures'

    def capture(self, text, *, revision='local-1', project=PROJECT, document=DOCUMENT, profile=PROFILE):
        (self.root / 'register.md').write_text(text)
        value = observe(self.root, 'register.md', project, document, revision, profile)
        return save_preview(self.root / 'previews', value)[0], value

    def unsafe_artifact(self, payload):
        path = self.root / (hashlib.sha256(payload).hexdigest() + '.json')
        path.write_bytes(payload)
        return path

    def test_escaped_pipes_and_struck_row_preserve_raw_fields(self):
        _, value = self.capture(HEADER + ROW.replace('PT-01', '~~PT-01~~').replace('Example', r'A \| B'))
        row = value['proposals'][0]
        self.assertTrue(value['register']['comparison_eligible'])
        self.assertEqual('PT-01', row['source_key'])
        self.assertTrue(row['source_struck'])
        self.assertEqual('~~PT-01~~', row['fields']['id'])
        self.assertEqual(r'A \| B', row['fields']['item'])
        self.assertEqual('OPEN', row['fields']['status'])
        self.assertEqual('PT-02', row['fields']['blocked_on'])
        self.assertFalse(row['activation_allowed'])

    def test_duplicate_id_across_tables_blocks_all_comparison_and_retains_rows(self):
        before, _ = self.capture(HEADER + ROW)
        after, value = self.capture(HEADER + ROW + '\n## History\n\n' + HEADER + ROW.replace('PT-01', '~~PT-01~~'))
        self.assertEqual(2, len(value['proposals']))
        report = compare_previews(before, after)
        self.assertEqual('BLOCKED', report['state'])
        self.assertEqual([], report['changes'])
        self.assertIn('REGISTER_KEY_DUPLICATE', [d['code'] for d in report['diagnostics']])

    def test_unescaped_pipe_including_code_is_ambiguous_and_blocks(self):
        for text in ['A | B', '`A | B`', r'A \\| B']:
            with self.subTest(text=text):
                _, value = self.capture(HEADER + ROW.replace('Example', text))
                self.assertFalse(value['register']['comparison_eligible'])
                self.assertIn('REGISTER_ROW_WIDTH', [d['code'] for d in value['diagnostics']])

    def test_bad_header_separator_missing_final_pipe_and_invalid_id_block(self):
        for text in [HEADER.replace('Component(s)', 'Components') + ROW,
                     HEADER.replace('---', '--') + ROW,
                     HEADER + ROW.rstrip()[:-1] + '\n',
                     HEADER + ROW.replace('PT-01', '**PT-01**'),
                     HEADER + ROW.replace('PT-01', 'pt-01')]:
            with self.subTest(text=text):
                _, value = self.capture(text)
                self.assertFalse(value['register']['comparison_eligible'])

    def test_unknown_keyed_table_and_indented_or_html_input_blocks(self):
        for text in [HEADER + ROW + '\n| Key | Summary |\n|---|---|\n| PT-99 | hidden |\n',
                     '    ' + HEADER.replace('\n', '\n    ') + ROW,
                     '<!--\n' + HEADER + ROW + '-->\n',
                     HEADER + ROW + '\n' + HEADER.replace('ID', 'id') + ROW.replace('PT-01', 'pt-01')]:
            with self.subTest(text=text):
                _, value = self.capture(text)
                self.assertFalse(value['register']['comparison_eligible'])

    def test_fenced_table_never_becomes_candidates_and_other_tables_are_diagnostic(self):
        _, value = self.capture('```md\n' + HEADER + ROW + '```\n')
        self.assertEqual([], value['proposals'])
        self.assertFalse(value['register']['comparison_eligible'])
        _, value = self.capture('| Field | Value |\n|---|---|\n| note | raw |\n\n' + HEADER + ROW)
        self.assertTrue(value['register']['comparison_eligible'])
        self.assertIn('OTHER_TABLE_LINES_UNINTERPRETED', [d['code'] for d in value['diagnostics']])

    def test_difference_reports_change_move_addition_and_absence_without_deletion(self):
        before, old = self.capture((self.fixture / 'register-before.md').read_text())
        after, new = self.capture((self.fixture / 'register-after.md').read_text(), revision='local-2')
        report = compare_previews(before, after)
        changes = {r['source_key']: r for r in report['changes']}
        self.assertEqual('CHANGED', changes['PT-01']['change'])
        self.assertEqual(['id', 'status'], changes['PT-01']['changed_fields'])
        self.assertEqual('ABSENT_IN_OBSERVATION', changes['PT-02']['change'])
        self.assertEqual('UNCHANGED', changes['PT-03']['change'])
        self.assertTrue(changes['PT-03']['location_changed'])
        self.assertEqual('ADDED', changes['PT-04']['change'])
        self.assertEqual(old['proposals'][0]['source_identity_id'], new['proposals'][1]['source_identity_id'])
        self.assertNotEqual(old['proposals'][0]['candidate_id'], new['proposals'][1]['candidate_id'])
        self.assertTrue(all(not item['activation_allowed'] for item in report['changes']))
        self.assertFalse(report['activation_allowed'])

    def test_same_bytes_new_label_and_exact_repeat_are_unchanged(self):
        before, _ = self.capture(HEADER + ROW)
        after, _ = self.capture(HEADER + ROW, revision='local-2')
        report = compare_previews(before, after)
        self.assertEqual(['UNCHANGED'], [r['change'] for r in report['changes']])
        self.assertEqual(compare_previews(before, after), report)
        self.assertEqual(['UNCHANGED'], [r['change'] for r in compare_previews(before, before)['changes']])

    def test_empty_recognized_register_is_absence_but_no_register_blocks(self):
        before, _ = self.capture(HEADER + ROW)
        empty, _ = self.capture(HEADER)
        self.assertEqual('ABSENT_IN_OBSERVATION', compare_previews(before, empty)['changes'][0]['change'])
        missing, _ = self.capture('# No declared table\n')
        self.assertEqual('BLOCKED', compare_previews(before, missing)['state'])

    def test_project_document_and_profile_are_explicit_compatibility_boundaries(self):
        before, _ = self.capture(HEADER + ROW)
        for options in [{'project': '00000000-0000-4000-8000-000000000003'},
                        {'document': '00000000-0000-4000-8000-000000000003'}, {'profile': 'markdown-structure.v1'}]:
            after, _ = self.capture(HEADER + ROW, **options)
            with self.subTest(options=options), self.assertRaises(ValueError):
                compare_previews(before, after)

    def test_forged_fields_eligibility_and_snapshot_claims_fail_reconstruction(self):
        path, value = self.capture(HEADER + ROW)
        for mutate in [lambda v: v['proposals'][0]['fields'].update(status='DONE'),
                       lambda v: v.update(activation_allowed=True),
                       lambda v: v.update(content_sha256='0' * 64),
                       lambda v: v['register'].update(row_count=999)]:
            forged = json.loads(path.read_bytes())
            mutate(forged)
            candidate = self.unsafe_artifact(canonical(forged))
            with self.subTest(mutate=mutate), self.assertRaises(ValueError):
                load_preview(candidate)

    def test_register_row_limit_rejects_instead_of_truncating(self):
        with self.assertRaisesRegex(ValueError, 'row limits'):
            self.capture(HEADER + ROW * 2001)

    def test_forged_eligibility_cannot_unblock_duplicate_source_keys(self):
        _, value = self.capture(HEADER + ROW + ROW)
        value['register']['comparison_eligible'] = True
        with self.assertRaises(ValueError):
            load_preview(self.unsafe_artifact(canonical(value)))

    def test_filename_hash_extra_duplicate_json_keys_and_symlink_fail(self):
        path, value = self.capture(HEADER + ROW)
        payload = path.read_bytes()
        path.write_bytes(payload + b' ')
        with self.assertRaises(ValueError):
            load_preview(path)
        value['extra'] = 'not supported'
        with self.assertRaises(ValueError):
            load_preview(self.unsafe_artifact(canonical(value)))
        with self.assertRaises(ValueError):
            load_preview(self.unsafe_artifact(b'{"profile":"task-register.v1","profile":"task-register.v1"}\n'))
        link = self.root / ('f' * 64 + '.json')
        link.symlink_to(path)
        with self.assertRaises(OSError):
            load_preview(link)

    def test_reused_caller_label_is_diagnostic_not_revision_order(self):
        before, _ = self.capture(HEADER + ROW)
        after, _ = self.capture(HEADER + ROW.replace('OPEN', 'WATCH'))
        report = compare_previews(before, after)
        self.assertEqual('PREVIEW_ONLY', report['state'])
        self.assertEqual('CALLER_LABEL_REUSED_WITH_DIFFERENT_BYTES', report['diagnostics'][0]['code'])

    def test_cli_valid_and_blocked_exit_codes_save_reviewable_reports(self):
        before, _ = self.capture(HEADER + ROW)
        after, _ = self.capture(HEADER + ROW + ROW)
        command = [sys.executable, '-m', 'source_ingest.compare', '--before', str(before), '--store', str(self.root / 'comparisons')]
        for path, expected in [(before, 0), (after, 2)]:
            with self.subTest(expected=expected):
                result = subprocess.run(command + ['--after', str(path)], text=True, capture_output=True)
                self.assertEqual(expected, result.returncode, result.stderr)
                value = json.loads(result.stdout)
                self.assertTrue(Path(value['comparison']).exists())
                self.assertFalse(value['activation_allowed'])


if __name__ == '__main__':
    unittest.main()
